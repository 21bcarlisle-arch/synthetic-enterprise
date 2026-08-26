"""The value arm as WRITER 3b of the renewal rate chain — R15 proof.

WHAT THIS WIRING IS FOR (`docs/design/THE_VALUE_CYCLE_REALISED_AB.md`). The thesis is that a
supplier deciding customer-by-customer on what it can infer beats a flat rule through better
prediction and nothing else. `company/pricing/value_based_renewal.decide_margin` is the decision
and it was built on 2026-08-25; until this wiring it had no caller but a harness tool, so nothing
the company DID was ever different. The honest comparison is REALISED — the same book, the same
world, run once per arm — and that needs the arm to actually price a renewal.

THE FOUR THINGS THAT CAN GO WRONG HERE, and each has a mutation below rather than an assertion:

  1. THE CONTROL STOPS BEING THE CONTROL. If the writer is not a strict no-op under
     `flat_rules`, the A/B compares two code paths rather than one variable and every delta is
     uninterpretable. Pinned against the pre-cut transcription the seam test already carries.
  2. THE FLAT RULE IS CHARGED TWICE. `decide_margin` returns a MARGIN and the rate handed to the
     chain already contains `TARGET_MARGIN_GBP_PER_MWH`, so a writer that adds the margin
     outright silently double-charges every account by £2/MWh. That is a plausible, small,
     invisible error and it is the one this file is most worried about.
  3. THE CAP STOPS BINDING. Run unbounded against the real book this arm chose margins between
     £60 and £200/MWh against a flat £2. Placed after writer 4 it would publish a rate the
     supplier is not allowed to charge — a compliance breach produced by a pricing improvement.
  4. THE ARM FIRES WHEN NOBODY ASKED. It reads the run's ACTIVE POLICY rather than an argument,
     so a leaked scope would turn every ordinary run into the experiment.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from company.policy.decision_policy import (  # noqa: E402
    CURRENT_POLICY,
    VALUE_ARM_POLICY,
    policy_scope,
)
from company.pricing import renewal_rate_chain as chain  # noqa: E402
from company.pricing import value_based_renewal as vbr  # noqa: E402
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH  # noqa: E402


def _settled(account: str = "C1", *, year: int = 2020,
             kwh_per_month: float = 250.0, revenue_per_month: float = 45.0) -> list[dict]:
    """Twelve months of the account's own settled book, inside the arm's observation window.

    Deliberately a WHOLE year: the arm's EAC is the rolling twelve months before the term start,
    the same window the churn estimate uses, and a partial year would understate the account and
    make every figure below a property of the fixture rather than of the arm.
    """
    return [
        {
            "customer_id": account,
            "commodity": "electricity",
            "settlement_date": f"{year}-{m:02d}-15",
            "term_start": f"{year}-01-01",
            "consumption_kwh": kwh_per_month,
            "revenue_gbp": revenue_per_month,
            "net_margin_gbp": 1.0,
            "margin_gbp": 5.0,
            "settlement_periods_folded": 48,
        }
        for m in range(1, 13)
    ]


REFERENCE = dict(
    customer_id="C1",
    billing_account="C1",
    commodity="electricity",
    term_start="2021-01-01",
    tariff_type="fixed",
    term_index=2,
    struck_unit_rate_gbp_per_mwh=200.0,
    portfolio_margin_rates=[],
    prior_term_margin_gbp=None,
    prior_term_revenue_gbp=0.0,
    is_domestic=False,          # SME: keeps writer 4 out of the way except where it is the subject
    settled_records=_settled(),
)


def _drive(**over):
    return chain.decide_renewal_rate(**{**REFERENCE, **over})


# ── 1. the control is a strict no-op ────────────────────────────────────────────────────────

def test_the_control_arm_is_byte_identical_to_no_writer_at_all():
    """Under `flat_rules` the chain must produce exactly what it produced before this writer.

    Not "approximately the same rate" — the same rate, no `value_arm` component, and an EMPTY
    `value_arm_entries`. An empty list and a list of flat-margin choices are different facts, and
    a reader of a run output has to be able to tell which arm produced it.
    """
    with policy_scope(CURRENT_POLICY):
        result = _drive()
    assert result.unit_rate_gbp_per_mwh == REFERENCE["struck_unit_rate_gbp_per_mwh"]
    assert result.value_arm_entries == []
    assert not [c for c in result.components if c["cause"] == "value_arm"]


def test_the_control_arm_does_not_even_look_at_the_book(monkeypatch):
    """The no-op is EARLY, before any derivation. A control that computed the arm's answer and
    then discarded it would still be a no-op on the rate while costing a full grid search per
    renewal on every ordinary run — 263 accounts x 10 years of terms — and nothing would say so.
    """
    called = []
    monkeypatch.setattr(vbr, "observed_account_state",
                        lambda *a, **k: called.append(a) or None)
    with policy_scope(CURRENT_POLICY):
        _drive()
    assert called == [], "the control arm derived observables it had already decided not to use"


# ── 2. the value arm moves the rate, and by a DELTA ─────────────────────────────────────────

def test_the_value_arm_prices_the_account_and_says_what_it_believed():
    with policy_scope(VALUE_ARM_POLICY):
        result = _drive()
    assert result.unit_rate_gbp_per_mwh != REFERENCE["struck_unit_rate_gbp_per_mwh"]
    assert len(result.value_arm_entries) == 1
    entry = result.value_arm_entries[0]
    assert entry["arm"] == vbr.VALUE_BASED
    # The belief is carried and LABELLED as a belief, because the realised A/B is the only thing
    # that can say whether acting on it was right.
    assert 0.0 <= entry["believed_p_retain"] <= 1.0
    assert "believed_expected_value_gbp" in entry
    assert [c["cause"] for c in result.components].count("value_arm") == 1


def test_the_uplift_is_a_DELTA_against_the_flat_rule_and_not_the_margin_itself():
    """MUTATION 2 — the double-charge, which is small, plausible and invisible.

    The struck rate already carries `TARGET_MARGIN_GBP_PER_MWH`. The arm returns a MARGIN. So the
    correct move is `chosen - flat`, and the wrong one — `chosen` — overcharges every account on
    the book by exactly £2/MWh while every other assertion in this file still passes.
    """
    with policy_scope(VALUE_ARM_POLICY):
        result = _drive()
    entry = result.value_arm_entries[0]
    correct = entry["chosen_margin_gbp_per_mwh"] - TARGET_MARGIN_GBP_PER_MWH
    assert entry["uplift_gbp_per_mwh"] == pytest.approx(correct, abs=1e-6)

    wrong = entry["chosen_margin_gbp_per_mwh"]
    assert entry["uplift_gbp_per_mwh"] != pytest.approx(wrong, abs=1e-6), (
        "the writer added the whole margin, so the flat rule is being charged twice -- "
        "and the fixture cannot tell the two apart, so this assertion proves nothing"
    )
    # The rate that came out IS the base plus the arm's own answer, not the base plus both.
    base = REFERENCE["struck_unit_rate_gbp_per_mwh"] - TARGET_MARGIN_GBP_PER_MWH
    assert result.unit_rate_gbp_per_mwh == pytest.approx(
        base + entry["chosen_margin_gbp_per_mwh"], abs=1e-6)


# ── 3. the cap still binds, which is the whole argument for the placement ───────────────────

def test_the_DOMESTIC_PRICE_CAP_still_clamps_what_the_value_arm_added():
    """MUTATION 3 — placement. Writer 3b sits BEFORE writer 4 so the cap clamps it.

    Proven by comparing against the arm's own unclamped answer rather than against a literal: the
    contracted rate must be strictly BELOW what the arm asked for, and a `price_cap` component
    must say so. Move this writer after the cap and the contracted rate becomes the arm's answer,
    which is a rate this supplier is not permitted to charge.
    """
    with policy_scope(VALUE_ARM_POLICY):
        capped = _drive(is_domestic=True, term_start="2021-06-01")
        uncapped = _drive(is_domestic=False, term_start="2021-06-01")

    asked = uncapped.value_arm_entries[0]["unit_rate_after"]
    assert capped.unit_rate_gbp_per_mwh < asked, (
        "the cap did not bind on a rate the arm pushed above it -- writer 3b is on the wrong "
        "side of writer 4, so the arm can publish an unlawful rate"
    )
    assert [c for c in capped.components if c["cause"] == "price_cap"], (
        "the rate was clamped but no component says the cap did it")


# ── 4. the arm fires only when the run asked for it ─────────────────────────────────────────

def test_the_arm_reads_the_RUNS_policy_and_not_a_module_default():
    """Outside the scope, nothing. Inside it, the arm. Both directions, because a writer that
    always fired would pass every test above and turn every ordinary run into the experiment."""
    outside = _drive()
    with policy_scope(VALUE_ARM_POLICY):
        inside = _drive()
    assert outside.value_arm_entries == []
    assert inside.value_arm_entries != []
    after = _drive()
    assert after.value_arm_entries == [], "the scope leaked into the run that followed it"


# ── the states that are states, not errors ─────────────────────────────────────────────────

@pytest.mark.parametrize("over,reason_fragment", [
    (dict(settled_records=[]), "nothing settled"),
    (dict(term_index=0), "acquisition term"),
    (dict(commodity="gas"), "not priced by this arm"),
    (dict(tariff_type="flex"), "no locked margin"),
    (dict(struck_unit_rate_gbp_per_mwh=None), "no locked rate"),
])
def test_a_renewal_this_arm_cannot_price_is_left_alone_WITH_A_REASON(over, reason_fragment):
    """Each of these returns 0.0, and each says WHY.

    A bare 0.0 cannot be told apart from "the arm ran and chose the flat margin", which is R15's
    fail-silent pattern with the company's pricing in it: a run where the arm silently declined
    to price 200 of 263 accounts would look identical to one where it priced them all and agreed
    with the control.
    """
    with policy_scope(VALUE_ARM_POLICY):
        result = _drive(**over)
    assert result.value_arm_entries == []
    uplift = vbr.renewal_margin_uplift(
        account_id="C1", commodity=over.get("commodity", "electricity"),
        tariff_type=over.get("tariff_type", "fixed"),
        term_index=over.get("term_index", 2), term_start="2021-01-01",
        locked_unit_rate=over.get("struck_unit_rate_gbp_per_mwh", 200.0),
        settled_records=over.get("settled_records", _settled()),
        is_domestic=False, arm=vbr.VALUE_BASED)
    assert uplift.uplift_gbp_per_mwh == 0.0
    assert reason_fragment in (uplift.not_run_reason or "")


# ── the wall ────────────────────────────────────────────────────────────────────────────────

def test_the_adapter_cannot_reach_the_worlds_truth():
    """The arm's advantage must be INFERENCE, never ACCESS. `decide_margin` already refuses a
    parameter that could carry the world's churn probability; this asserts the adapter that feeds
    it did not open a back door by importing one."""
    source = (ROOT / "company" / "pricing" / "value_based_renewal.py").read_text(encoding="utf-8")
    for forbidden in ("from simulation", "import simulation", "from sim.", "import sim\n"):
        assert forbidden not in source, (
            f"{forbidden!r} appears in the value arm -- the company would be reading the world's "
            "own answer, and the whole comparison would be meaningless")


def test_the_observation_window_is_the_one_the_churn_estimate_uses():
    """The arm's objective multiplies `p_retain` by `eac_mwh`. `p_retain` is estimated against an
    EAC from a rolling twelve months (`run_phase2b._company_eac_estimate`). If this adapter used
    a different span, the arm's own objective would be internally inconsistent about how big the
    customer is and nothing would report it."""
    assert vbr.OBSERVATION_WINDOW_YEARS == 1
    observed = vbr.observed_account_state("C1", "2021-01-01", _settled(), "resi")
    assert observed["eac_kwh"] == pytest.approx(250.0 * 12)
    # A record older than the window is outside it, and a record after the term start is
    # invisible: the point-in-time blindfold, asserted rather than assumed.
    older = _settled(year=2018) + _settled(year=2020)
    assert vbr.observed_account_state("C1", "2021-01-01", older, "resi")["eac_kwh"] == (
        pytest.approx(250.0 * 12))
    future = _settled(year=2020) + _settled(year=2022)
    assert vbr.observed_account_state("C1", "2021-01-01", future, "resi")["eac_kwh"] == (
        pytest.approx(250.0 * 12))
