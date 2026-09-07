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

  5. THE ARM IS HANDED LESS THAN THE ARM NEEDS (added 2026-08-26). `decide_margin` takes twenty
     company observables and this adapter used to pass six, letting the rest default. That is the
     defect the first ten-year A/B measured without naming: 36 of 66 answers sat on a bound, 27
     were clamped by the cap afterwards, and the median chosen margin was GBP 100.50/MWh against a
     regulated EBIT allowance of GBP 3.73-8.54. Two defaults did it. The billed `revenue_gbp`
     INCLUDES the standing charge, so `revenue / volume` is an ALL-IN rate being compared against
     a commodity-only offer -- GBP 55/MWh of phantom headroom on a small domestic account, spent
     before the churn model saw any rise. And no ceiling reached the search, so the cap landed
     afterwards as a clamp, which `decide_margin` refuses in its own body and which made
     `ceiling_bound` structurally unable to fire on the one path a live run uses.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from company.crm import customer_profitability as cp  # noqa: E402
from company.policy.decision_policy import (  # noqa: E402
    CURRENT_POLICY,
    VALUE_ARM_POLICY,
    policy_scope,
)
from company.pricing import renewal_rate_chain as chain  # noqa: E402
from company.pricing import value_based_renewal as vbr  # noqa: E402
from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date  # noqa: E402
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH  # noqa: E402

# THE WORLD'S OWN ID GRAMMAR, imported here and nowhere in `company/`. This file is a test and
# may read both sides; the arm may not, and the point of the control below is precisely that
# the company's billing grouping and the world's supply-point ids are two different things.
from simulation.household import GAS_LEG_ID_SUFFIX  # noqa: E402


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
    # GAS WAS THIS ROW UNTIL 2026-09-07 and is now an arm the writer prices; the
    # stage it left behind still exists and still needs a subject, so the subject
    # is a fuel outside `UPLIFTABLE_COMMODITIES` rather than one inside it.
    (dict(commodity="hydrogen"), "not priced by this arm"),
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
    observed = vbr.observed_account_state("C1", "2021-01-01", _settled(), "resi", "electricity")
    assert observed["eac_kwh"] == pytest.approx(250.0 * 12)
    # A record older than the window is outside it, and a record after the term start is
    # invisible: the point-in-time blindfold, asserted rather than assumed.
    older = _settled(year=2018) + _settled(year=2020)
    assert vbr.observed_account_state("C1", "2021-01-01", older, "resi", "electricity")["eac_kwh"] == (
        pytest.approx(250.0 * 12))
    future = _settled(year=2020) + _settled(year=2022)
    assert vbr.observed_account_state("C1", "2021-01-01", future, "resi", "electricity")["eac_kwh"] == (
        pytest.approx(250.0 * 12))


# ── 5. "no offer" is an ANSWER, and a live chain must be able to hear it ────────────────────

def test_a_renewal_the_arm_CANNOT_LAWFULLY_PRICE_leaves_the_rate_alone_and_says_why():
    """THE DEFECT THE FIRST TEN-YEAR A/B DIED ON, reproduced.

    `decide_margin` RAISES `MarginDecisionUnavailable` when no candidate margin survives both the
    price cap and the churn model's support bound (+83.1% of the current rate, the largest
    single-step domestic move Ofgem has published). Its own message insists that is "a real
    answer -- there is no offer here this company can both lawfully make and honestly predict --
    and not a default", and as a REPORT that is right. As a WRITER inside a live pricing chain it
    killed the run: `C_IC3`, 2021, base rate GBP 251.45.

    The 2016-2018 window never reached a rate high enough to produce one, which is exactly what a
    short window hides -- so this fixture forces the condition rather than waiting for a year
    that happens to contain it.

    THE OUTCOME IS THE CONTROL'S, AND THE RECORD IS NOT. The rate is untouched, because a
    supplier that cannot form a defensible view charges what it already charges. But a decline
    and a never-looked-at must not read the same in the run output, so it lands in
    `value_arm_entries` with `declined: True` and the refusal in full.
    """
    # THE CONDITION IS BASE > CURRENT x 1.831, AND IT IS RECONSTRUCTED FROM THE REAL REFUSAL
    # rather than guessed: `C_IC3` reported a support bound of GBP 193.1 at "83.1% above the
    # current rate" against a base of GBP 251.45, so its realised current rate was ~GBP 105.5 and
    # the STRUCK rate alone had already overshot what the churn model has evidence for. A cheap
    # account meeting an expensive term -- 2021 wholesale -- not an expensive customer.
    cheap = _settled(kwh_per_month=250.0, revenue_per_month=26.25)   # ~GBP 105/MWh realised
    observed = vbr.observed_account_state("C1", "2021-01-01", cheap, "SME", "electricity")
    assert observed["current_rate_gbp_per_mwh"] * 1.831 < 251.45, (
        "fixture no longer reproduces the incident -- the support bound reaches the base rate, "
        "so the arm can price this and the refusal below would never fire")
    with policy_scope(VALUE_ARM_POLICY):
        result = _drive(settled_records=cheap, struck_unit_rate_gbp_per_mwh=251.45)

    assert result.unit_rate_gbp_per_mwh == pytest.approx(251.45), (
        "a renewal the arm cannot price must come out at the rate the chain struck")
    assert not [c for c in result.components if c["cause"] == "value_arm"], (
        "the arm declined, so it must not appear as a writer that moved the rate")
    assert len(result.value_arm_entries) == 1
    entry = result.value_arm_entries[0]
    assert entry["declined"] is True
    assert "no lawful, predictable offer" in entry["reason"]
    assert "support bound" in entry["reason"], (
        "the refusal must carry decide_margin's own words -- a reason that says only 'declined' "
        "cannot tell a cap refusal from a support-bound refusal, and they are different findings")


def test_a_DECLINE_and_a_NEVER_LOOKED_are_not_the_same_row():
    """The R15 fail-silent guard on the split above, stated as the property that matters.

    An ineligible renewal (gas, flex, acquisition term) writes NOTHING; a declined one writes a
    row. Collapsing the two would make a book the arm walked past indistinguishable from a book
    it examined and refused, and the A/B's `declined_share_of_renewals_seen` would silently read
    zero for both.
    """
    with policy_scope(VALUE_ARM_POLICY):
        ineligible = _drive(commodity="gas")
        declined = _drive(settled_records=_settled(kwh_per_month=250.0, revenue_per_month=26.25),
                          struck_unit_rate_gbp_per_mwh=251.45)
    assert ineligible.value_arm_entries == []
    assert len(declined.value_arm_entries) == 1 and declined.value_arm_entries[0]["declined"]


# ── 5. the arm is handed what the arm needs ─────────────────────────────────────────────────
#
# Every test below is a MUTATION on `observed_account_state` / `renewal_margin_uplift`: revert the
# 2026-08-26 change it names and the test reds. They are grouped here because they share one
# subject -- the information the chain gives the decision -- and one finding,
# WORKER_FINDING_VALUE_ARM_CHOOSES_A_BOUND_NOT_A_CUSTOMER.

STANDING_CHARGE_GBP_PER_DAY = 0.27
DAYS_PER_ROW = 10


def _settled_with_standing_charge(account: str = "C1", *, year: int = 2020,
                                  commodity_rate: float = 120.0,
                                  annual_kwh: float = 1779.0) -> list[dict]:
    """A year of a SMALL DOMESTIC account's book, billed the way the world really bills it.

    `revenue_gbp` carries the commodity leg AND the standing charge, because that is what
    `simulation/hedged_settlement.py` stamps -- `revenue_gbp = settled[...] + sc_per_period`. The
    size is the point: 1,779 kWh a year at GBP 0.27/day means the standing charge is GBP 97 of a
    GBP 311 bill, so an all-in GBP/MWh overstates the commodity rate by nearly half.
    """
    rows = []
    kwh_per_row = annual_kwh / 36.0
    for m in range(1, 13):
        for d in (5, 15, 25):
            rows.append({
                "customer_id": account,
                "commodity": "electricity",
                "settlement_date": f"{year}-{m:02d}-{d:02d}",
                "consumption_kwh": kwh_per_row,
                "revenue_gbp": (kwh_per_row / 1000.0) * commodity_rate
                + STANDING_CHARGE_GBP_PER_DAY * DAYS_PER_ROW,
                "standing_charge_gbp": STANDING_CHARGE_GBP_PER_DAY * DAYS_PER_ROW,
                "settlement_periods_folded": 48 * DAYS_PER_ROW,
            })
    return rows


def test_the_arm_prices_against_the_COMMODITY_rate_not_the_ALL_IN_billed_one():
    """MUTATION 5a — the rate the churn model is asked about must be the same KIND of number as
    the offer it is compared against.

    `base_rate_gbp_per_mwh + margin` is a commodity unit rate with no standing charge in it. If
    `current_rate_gbp_per_mwh` is billed-revenue-over-volume it is not, and the difference is
    read by the model as headroom the supplier does not have. Restore
    `revenue / (kwh / 1000.0)` and this reds on the first assertion.
    """
    records = _settled_with_standing_charge()
    observed = vbr.observed_account_state("C1", "2021-01-01", records, "resi", "electricity")

    all_in = (sum(r["revenue_gbp"] for r in records)
              / (sum(r["consumption_kwh"] for r in records) / 1000.0))
    assert observed["current_rate_gbp_per_mwh"] == pytest.approx(120.0, abs=0.01), (
        "the arm's 'current rate' is not this account's commodity rate -- it is carrying the "
        f"standing charge, which on this account is worth {all_in - 120.0:.0f} GBP/MWh of "
        "headroom the supplier has not actually got"
    )
    # The NULL CONTROL, and it is what makes the assertion above a measurement rather than a
    # restatement: on a fixture where the standing charge were negligible the two numbers would
    # agree and this test could not tell the mechanisms apart.
    assert all_in - observed["current_rate_gbp_per_mwh"] > 40.0, (
        "this fixture cannot see the defect it is written for -- the all-in and commodity rates "
        "are too close for the choice between them to move any decision"
    )


def test_forgetting_the_STANDING_CHARGE_makes_the_chain_arm_OVER_PRICE():
    """MUTATION 5b — the CONSEQUENCE, priced. `expected_value_gbp`'s docstring already measures
    this on the decision (80.00 -> 60.00 GBP/MWh, because fixed revenue is only earned from a
    customer who STAYS, so forgetting it makes losing them look cheap). This asserts the chain
    path actually gets the corrected answer and not the inflated one.

    Both arms of the comparison are run here rather than asserted against a literal, so the test
    measures the mechanism rather than today's number.
    """
    records = _settled_with_standing_charge()
    observed = vbr.observed_account_state("C1", "2021-01-01", records, "resi", "electricity")
    base = 120.0 - TARGET_MARGIN_GBP_PER_MWH
    common = dict(customer_id="C1", arm=vbr.VALUE_BASED, base_rate_gbp_per_mwh=base,
                  eac_kwh=observed["eac_kwh"], tenure_years=observed["tenure_years"],
                  cost_to_serve_gbp_per_year=observed["cost_to_serve_gbp_per_year"],
                  segment="resi", renewal_year=2021)

    all_in = (sum(r["revenue_gbp"] for r in records)
              / (sum(r["consumption_kwh"] for r in records) / 1000.0))
    forgetful = vbr.decide_margin(current_rate_gbp_per_mwh=all_in, **common)
    corrected = vbr.decide_margin(
        current_rate_gbp_per_mwh=observed["current_rate_gbp_per_mwh"],
        annual_revenue_gbp=observed["annual_revenue_gbp"],
        fixed_revenue_gbp_per_year=observed["fixed_revenue_gbp_per_year"],
        expected_periods=observed["expected_periods"],
        **common)

    assert corrected.margin_gbp_per_mwh < forgetful.margin_gbp_per_mwh - 50.0, (
        "the corrected arm is not pricing materially below the forgetful one, so either the "
        "standing charge is not reaching the decision or it no longer moves it: measured "
        f"{corrected.margin_gbp_per_mwh:.2f} against {forgetful.margin_gbp_per_mwh:.2f} GBP/MWh"
    )


def test_the_arm_prices_a_renewal_at_its_OBSERVED_lifetime_not_the_no_evidence_fallback():
    """MUTATION 5c — `FALLBACK_LIFETIME_PERIODS` is written for an account that has given NO
    evidence, and the chain applied it to every account including ones with years of settled
    history in the records it was handed.

    A uniform scalar on EV, so it never moved the CHOICE -- which is exactly why it survived: the
    only thing it corrupted was every published `believed_expected_value_gbp`, and nothing
    compared those to anything until the A/B did.
    """
    records = (_settled_with_standing_charge(year=2018)
               + _settled_with_standing_charge(year=2019)
               + _settled_with_standing_charge(year=2020))
    observed = vbr.observed_account_state("C1", "2021-01-01", records, "resi", "electricity")
    assert observed["tenure_years"] > 2.9
    assert observed["expected_periods"] > vbr.FALLBACK_LIFETIME_PERIODS, (
        "a three-year account is still being priced at the one-period fallback meant for an "
        "account with no history at all"
    )
    assert observed["expected_periods"] <= vbr.MAX_EXPECTED_PERIODS, (
        "observed tenure is buying an unbounded lifetime -- the CLV horizon must still cap it")


def test_the_STANDING_CHARGE_FALLBACK_counts_DAYS_and_not_SETTLEMENT_ROWS():
    """MUTATION 5d — the fail-open that the fallback path invites. There are 48 settlement periods
    in a day and the tariff rate is per DAY, so a fallback that sums a per-day rate over records
    overstates the standing charge by up to 48x -- which would swamp the whole bill and send every
    answer to the floor. Only reachable for a generator that stamps no `standing_charge_gbp`, which
    is why it is tested rather than trusted.
    """
    records = _settled_with_standing_charge()
    for row in records:
        row.pop("standing_charge_gbp")
    observed = vbr.observed_account_state("C1", "2021-01-01", records, "resi", "electricity")

    days = len({r["settlement_date"] for r in records})
    assert observed["fixed_revenue_gbp_per_year"] == pytest.approx(
        days * STANDING_CHARGE_GBP_PER_DAY, rel=1e-6), (
        "the fallback standing charge is not days x the per-day rate -- if it is counting rows "
        "or periods it is inflating this account's fixed revenue by up to 48x"
    )
    assert observed["fixed_revenue_gbp_per_year"] < observed["annual_revenue_gbp"], (
        "the fallback standing charge exceeds the whole bill, which is the 48x shape")


def test_the_CAP_is_INSIDE_the_search_and_never_a_CLAMP_on_a_renewal_the_arm_PRICED():
    """MUTATION 5e — the ORDER, which `decide_margin` refuses in its own body: "Scoring a candidate
    the company may not lawfully offer and then clamping the winner would report an expected value
    nobody can earn, and would make the arm look better than the supplier it describes."

    The invariant is exact rather than statistical. The arm's `lawful` filter keeps only margins
    where `base + m <= cap`, and the chain's post-arm rate IS `base + m`, so a renewal the arm
    priced can never afterwards be clamped. A `price_cap` component on a PRICED renewal therefore
    means the ceiling stopped being threaded, or the arm's read of it and writer 4's have come
    apart. Drop `max_offered_rate_gbp_per_mwh` from the adapter call and this reds three ways.

    THE BASE RATE IS DERIVED FROM THE CAP, not written down, and that is a repair rather than a
    convenience (2026-08-31). It was `120.0`, and at that rate the ceiling bound only because the
    company's 2021 switching belief was WRONG -- `market_conditions` asserted a multiplier of 0.57
    against a published record implying 1.27, so the arm believed almost nobody would leave in
    2021 and chased a margin the cap then had to stop. Correcting that belief onto the record
    (10 of 10 years inside the published band) made the arm price 13 GBP/MWh below the ceiling
    and this leg went red -- a control keyed to today's answer going red because the code became
    more honest, which is the shape this project has repaired repeatedly. Struck two pounds under
    the cap, the unbounded optimum exceeds the ceiling for ANY churn belief that leaves a positive
    margin, so the flag's ability to fire no longer rides on a company belief being mistaken.
    """
    cap = get_cap_unit_rate_for_date("electricity", date(2021, 6, 1))
    domestic = dict(is_domestic=True, tariff_type="fixed", term_start="2021-06-01",
                    struck_unit_rate_gbp_per_mwh=cap - 2.0,
                    settled_records=_settled_with_standing_charge())
    with policy_scope(VALUE_ARM_POLICY):
        result = _drive(**domestic)

    priced = [e for e in result.value_arm_entries if not e.get("declined")]
    assert priced, "the fixture no longer exercises a priced domestic renewal"
    entry = priced[0]

    assert not [c for c in result.components if c["cause"] == "price_cap"], (
        "the cap clamped a rate the arm had already chosen -- it is landing AFTER the search "
        "again, so the belief recorded on this renewal is a belief about a price the customer "
        "was never charged"
    )
    assert entry["unit_rate_contracted"] == pytest.approx(entry["unit_rate_after"], abs=1e-6)
    assert entry["ceiling_bound"] is True, (
        "the cap decided this price and the record does not say so -- `ceiling_bound` is "
        "computed as `max_offered_rate_gbp_per_mwh is not None and ...`, so an adapter that "
        "passes no ceiling makes this flag STRUCTURALLY unable to fire (R15 fail-silent)"
    )


def test_the_arm_NEVER_ASKS_for_a_rate_above_the_cap_it_was_given():
    """The population-level form of the invariant above, across the shapes a domestic renewal
    takes. Either the arm prices under the cap, or it declines -- there is no third outcome in
    which it asks for an unlawful rate and is rescued by writer 4.
    """
    from datetime import date as _date

    from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date

    for struck in (80.0, 120.0, 160.0, 185.0):
        with policy_scope(VALUE_ARM_POLICY):
            result = _drive(is_domestic=True, tariff_type="fixed", term_start="2021-06-01",
                            struck_unit_rate_gbp_per_mwh=struck,
                            settled_records=_settled_with_standing_charge(
                                commodity_rate=struck))
        cap = get_cap_unit_rate_for_date("electricity", _date(2021, 6, 1))
        for entry in result.value_arm_entries:
            if entry.get("declined"):
                continue
            assert entry["unit_rate_after"] <= cap + 1e-6, (
                f"struck at {struck}: the arm asked for {entry['unit_rate_after']:.2f} GBP/MWh "
                f"against a cap of {cap:.2f} -- an unlawful offer that only writer 4 stops"
            )


# ── gas is priced as gas, not as electricity wearing a label ────────────────────────────────
#
# `UPLIFTABLE_COMMODITIES` admitted gas on 2026-09-07, closing the largest exclusion this
# company's own code owned: 346 of 1,953 offered renewals against 120 the arm priced.
#
# WIDENING A GATE IS THE EASY HALF AND THE UNSAFE ONE. Four inputs behind it are
# commodity-specific, and each has an electricity answer sitting where a missing gas answer
# would go: the record filter (which leg's book), the churn curve (`fuel`), the cost-to-serve
# cadence (gas settles daily, electricity half-hourly), and the standing-charge table. A gate
# that admits gas while any of those keeps its electricity literal returns a NUMBER, not an
# error -- and on a book that is 87 dual-fuel of 164 accounts the account really does have an
# electricity leg to read, so the wrong answer is populated and plausible.
#
# Every control below is written to fail if one of those four reverts to the literal. None of
# them asserts a particular gas price: they assert that the gas answer and the electricity
# answer are DIFFERENT and that the difference comes from the gas inputs.


def _dual_fuel_book(account: str = "C1", *, year: int = 2020) -> list[dict]:
    """One account, two legs, DELIBERATELY DIFFERENT SIZES, UNDER THE WORLD'S OWN TWO IDS.

    The sizes are what make the record filter falsifiable. Equal legs would let a filter that
    reads the wrong book return the right EAC, and the control would go green on the defect.

    THE GAS LEG IS FILED UNDER `<account>g` AND UNTIL 2026-09-07 THIS FIXTURE FILED IT UNDER
    `<account>`, which is not a shape the world ever produces. `simulation/hedged_settlement.py`
    and `simulation/gas_settlement.py` stamp `customer_id` with the SUPPLY POINT, and
    `simulation/run_phase2b.py` calls the chain with `household_of(cid)` — so on every real
    renewal the two ids differ by exactly the suffix this fixture used not to carry. With the
    ids collapsed, the four commodity controls below were green while not one of the 337 gas
    renewals in a live run could reach its own book (`no_observed_history`, 179 of them). The
    fixture was the only reason that was invisible; the ids are the world's now.
    """
    elec = _settled(account, year=year, kwh_per_month=250.0, revenue_per_month=45.0)
    gas = [
        {
            # The GAS LEG's own supply point, not the billing account it bills under.
            "customer_id": f"{account}g",
            "commodity": "gas",
            "settlement_date": f"{year}-{m:02d}-15",
            "term_start": f"{year}-01-01",
            "consumption_kwh": 900.0,
            # A REAL DOMESTIC GAS LEVEL, and it is load-bearing rather than dressing.
            # Gas unit rates are roughly a third of electricity's, and so is the gas cap:
            # GBP 33.40/MWh at 2021-06 against GBP 190-odd for electricity. A gas book
            # written at electricity levels makes the arm DECLINE every gas renewal for
            # want of a lawful margin -- which is the arm behaving correctly and the
            # fixture testing nothing.
            "revenue_gbp": 32.0,
            "net_margin_gbp": 1.0,
            "margin_gbp": 5.0,
            # Gas settles DAILY, so a gas record folds a day and not 48 half-hours. The value
            # is the fixture's half of the cadence the cost model switches on.
            "settlement_periods_folded": 1,
        }
        for m in range(1, 13)
    ]
    return elec + gas


#: WHICH SUPPLY POINT THE WORLD FILES EACH LEG'S SETTLED ROWS UNDER, keyed by commodity, and
#: taken from the world's own grammar rather than a literal `"g"` written here: a copy of the
#: suffix in this file would keep agreeing with the arm after the roster changed it, which is a
#: control keyed to today's answer. A commodity admitted to `UPLIFTABLE_COMMODITIES` without an
#: entry here FAILS the control below rather than quietly taking the electricity branch.
_WORLD_LEG_ID = {
    "electricity": lambda account: account,
    "gas": lambda account: account + GAS_LEG_ID_SUFFIX,
}


def test_every_commodity_the_arm_prices_can_reach_its_own_book_under_the_billing_account():
    """THE CLASS, NOT THE GAS INSTANCE: the arm is called under one id and the book is filed
    under another, and every commodity it admits has to survive that.

    THE DEFECT THIS EXISTS FOR (2026-09-07). `simulation/run_phase2b.py` calls the chain with
    `household_of(cid)` — the BILLING ACCOUNT — while both settlement writers stamp rows with
    the SUPPLY POINT. For electricity the two ids are the same string and nothing shows. For
    gas they differ by a suffix, so `observed_account_state` matched nothing and returned
    `None`: 179 of the 337 gas renewals refused at `no_observed_history`, `priced` unmoved at
    94, accounts unmoved at 66 — a widened gate that bought zero decisions and that no renewal
    count could distinguish from a win.

    KEYED TO THE PROPERTY: it asserts a renewal can REACH its own book, never what the book
    then says. A gas leg the arm declines for want of a lawful margin passes this — that is the
    arm working — and a gas leg it cannot see does not, whatever the cap does afterwards.
    """
    missing = set(vbr.UPLIFTABLE_COMMODITIES) - set(_WORLD_LEG_ID)
    assert not missing, (
        f"the arm now prices {sorted(missing)} and this control does not know which supply "
        f"point the world files that leg under — add it to `_WORLD_LEG_ID` rather than "
        f"letting the commodity go unchecked"
    )

    book = _dual_fuel_book()
    for commodity in sorted(vbr.UPLIFTABLE_COMMODITIES):
        leg_id = _WORLD_LEG_ID[commodity]("C1")
        # THE FILTER, asked under the id the chain is really called with.
        observed = vbr.observed_account_state("C1", "2021-01-01", book, "resi", commodity)
        assert observed is not None, (
            f"{commodity}: settled as {leg_id!r}, asked for as 'C1', and the arm cannot see it"
        )
        assert observed["eac_kwh"] > 0.0

        # AND THE WHOLE CHAIN, because the id is chosen there and not in the adapter. The two
        # ids are passed as the world passes them: the leg as `customer_id`, the household's
        # billing account as `billing_account`.
        with policy_scope(VALUE_ARM_POLICY):
            result = _drive(
                customer_id=leg_id,
                billing_account="C1",
                commodity=commodity,
                tariff_type="fixed",
                struck_unit_rate_gbp_per_mwh=(
                    200.0 if commodity == "electricity" else 60.0),
                settled_records=book,
            )
        stages = [e["stage"] for e in result.arm_funnel_entries]
        assert stages and vbr.STAGE_NO_OBSERVED_HISTORY not in stages, (
            f"{commodity}: the chain refused this renewal for want of a book it settled "
            f"itself — stages {stages}"
        )


def _dual_fuel_book_net_negative(account: str = "C1", *, year: int = 2020) -> list[dict]:
    """The same two legs under the same two ids, with BOTH prior terms NET-NEGATIVE.

    Writer 3 returns 0.0 for an account it judges profitable AND for an account whose book it
    cannot see, so a control over the reach needs a book on which the policy MUST fire —
    otherwise green says nothing. Derived from `_dual_fuel_book` rather than written out again,
    so the supply-point ids stay the world's and this fixture cannot drift away from the one
    the value arm's controls are keyed to.
    """
    return [
        {**r, "net_margin_gbp": -abs(float(r["net_margin_gbp"])) - 1.0}
        for r in _dual_fuel_book(account, year=year)
    ]


def test_every_commodity_writer_3_reprices_can_reach_the_book_it_settled_itself():
    """WRITER 3, THE SAME CLASS ONE WRITER EARLIER — and it survived the value arm's fix.

    THE DEFECT THIS EXISTS FOR (2026-09-07). `renewal_rate_chain` calls
    `renewal_unit_rate_uplift(account_id=billing_account, …)` — `household_of(cid)`, the BILLING
    ACCOUNT — while both settlement writers stamp rows with the SUPPLY POINT.
    `estimate_prior_term_net_margin` matched them with `==`, so every gas renewal resolved to
    `None` and `compute_profitability_uplift` returned 0.0. That is also its answer for "this
    account is profitable", so the supplier's own policy of repricing net-negative accounts was
    structurally unreachable on half the book and no run output could say so.

    KEYED TO THE PROPERTY, not to the uplift: it asserts a renewal the chain reprices can REACH
    the book it settled itself. What the policy then decides is the policy's business — the
    fixture is net-negative on both legs precisely so that 0.0 can only mean "cannot see it".

    THE SAME `_WORLD_LEG_ID` MAP as the value arm's control, and the completeness leg is read
    off `customer_profitability.UPLIFTABLE_COMMODITIES` — the module that OWNS writer 3's gate,
    not the seam that re-exports it — so a third commodity admitted to either gate fails here
    rather than quietly taking the electricity branch.
    """
    missing = set(cp.UPLIFTABLE_COMMODITIES) - set(_WORLD_LEG_ID)
    assert not missing, (
        f"writer 3 now reprices {sorted(missing)} and this control does not know which supply "
        f"point the world files that leg under — add it to `_WORLD_LEG_ID` rather than letting "
        f"the commodity go unchecked"
    )
    # THE TWO IDS REALLY DIFFER on at least one admitted commodity, or nothing below can tell a
    # billing-account match from string equality and the whole control is vacuous.
    assert len({_WORLD_LEG_ID[c]("C1") for c in cp.UPLIFTABLE_COMMODITIES}) > 1, (
        "every commodity writer 3 admits is filed under the billing account itself, so the "
        "defect this control guards cannot arise on this book — widen the fixture rather than "
        "deleting the control"
    )

    book = _dual_fuel_book_net_negative()
    for commodity in sorted(cp.UPLIFTABLE_COMMODITIES):
        leg_id = _WORLD_LEG_ID[commodity]("C1")

        # THE FIXTURE CAN PRODUCE AN UPLIFT AT ALL, established from the ROWS and not from the
        # function under test: each leg's prior term is genuinely net-negative and genuinely
        # carries enough records for the policy to form a view.
        rows = [r for r in book
                if r["customer_id"] == leg_id and r["commodity"] == commodity]
        assert len(rows) >= cp.MIN_RECORDS_FOR_JUDGEMENT
        assert sum(r["net_margin_gbp"] for r in rows) < 0.0

        # THE FILTER, asked under the id the chain is really called with.
        assert cp.estimate_prior_term_net_margin(
            "C1", "2021-01-01", book, commodity) is not None, (
            f"{commodity}: settled as {leg_id!r}, asked for as 'C1', and writer 3 cannot see "
            f"the book this supplier settled itself"
        )

        # AND THE WHOLE CHAIN, because the id is chosen there and not in the writer. The two
        # ids are passed as the world passes them: the leg as `customer_id`, the household's
        # billing account as `billing_account`.
        result = _drive(
            customer_id=leg_id,
            billing_account="C1",
            commodity=commodity,
            tariff_type="fixed",
            term_index=2,
            term_start="2021-01-01",
            struck_unit_rate_gbp_per_mwh=(200.0 if commodity == "electricity" else 60.0),
            settled_records=book,
        )
        assert result.profitability_uplift_entries, (
            f"{commodity}: a net-negative prior term the supplier settled itself, and writer 3 "
            f"logged nothing — 0.0 here is indistinguishable from 'this account is profitable'"
        )
        assert result.profitability_uplift_entries[0]["uplift_gbp_per_mwh"] > 0.0


def test_a_gas_renewal_reads_the_gas_leg_and_not_the_electricity_one():
    """THE RECORD FILTER. Reverting it to the electricity literal returns the elec leg's EAC.

    3,000 kWh (12 x 250) against 10,800 kWh (12 x 900): the two legs cannot be confused for
    one another, and neither can be reached by summing both.
    """
    book = _dual_fuel_book()
    gas = vbr.observed_account_state("C1", "2021-01-01", book, "resi", "gas")
    elec = vbr.observed_account_state("C1", "2021-01-01", book, "resi", "electricity")
    assert gas["eac_kwh"] == pytest.approx(900.0 * 12)
    assert elec["eac_kwh"] == pytest.approx(250.0 * 12)
    assert gas["eac_kwh"] != elec["eac_kwh"]
    # NOT THE SUM EITHER. A filter deleted outright — rather than reverted — would pass both
    # assertions above only if it happened to match one leg; this closes the third outcome.
    assert gas["eac_kwh"] != pytest.approx((900.0 + 250.0) * 12)


def test_a_gas_renewal_is_costed_on_the_gas_cadence_and_the_gas_standing_charge():
    """COST-TO-SERVE and the STANDING CHARGE, each against its own table.

    Both are asserted against `saas` directly rather than against a number written here: a
    constant copied into this file would keep agreeing with the arm after the table moved,
    which is a control keyed to today's answer instead of to the property.
    """
    from saas.cost_to_serve import cost_to_serve_for_period
    from saas.non_commodity import standing_charge_rate

    book = _dual_fuel_book()
    gas = vbr.observed_account_state("C1", "2021-01-01", book, "resi", "gas")

    expected_cts = sum(
        cost_to_serve_for_period("resi", 32.0, "gas", periods=1) for _ in range(12))
    assert gas["cost_to_serve_gbp_per_year"] == pytest.approx(expected_cts)
    # And it is NOT what the electricity cadence would have charged on the same records.
    assert gas["cost_to_serve_gbp_per_year"] != pytest.approx(
        sum(cost_to_serve_for_period("resi", 32.0, "electricity", periods=1) for _ in range(12)))

    # The gas standing charge, from the gas table. These records carry no stamped
    # `standing_charge_gbp`, so the fallback path is the one under test -- 12 distinct
    # settlement dates at the gas resi rate.
    assert gas["fixed_revenue_gbp_per_year"] == pytest.approx(
        12 * standing_charge_rate("gas", "resi"))
    assert standing_charge_rate("gas", "resi") != standing_charge_rate("electricity", "resi"), (
        "the two tables agree, so this control can no longer tell them apart -- give it a "
        "different discriminator rather than deleting it"
    )


def test_the_gas_renewal_is_priced_by_the_gas_churn_curve():
    """THE `fuel` ARGUMENT. `estimate_churn_probability` branches on it, and the gas branch
    carries its own base rate and its own rate sensitivity for a stickier product.

    Asserted as a DIFFERENCE between the two fuels at identical inputs, so it fails if the
    adapter stops passing `fuel` (both sides collapse onto the electricity curve and become
    equal), and it does not encode either curve's constants here.
    """
    from company.crm.churn_model import estimate_churn_probability

    kwargs = dict(old_rate_gbp_per_mwh=120.0, new_rate_gbp_per_mwh=180.0,
                  tenure_years=3.0, annual_consumption_kwh=10800.0, segment="resi")
    assert estimate_churn_probability(fuel="gas", **kwargs) != pytest.approx(
        estimate_churn_probability(fuel="electricity", **kwargs)), (
        "the two fuels' churn curves have converged, so passing `fuel` can no longer change "
        "an answer and the control below proves nothing"
    )

    book = _dual_fuel_book()
    with policy_scope(VALUE_ARM_POLICY):
        gas = vbr.renewal_margin_uplift(
            account_id="C1", commodity="gas", tariff_type="fixed", term_index=2,
            term_start="2021-01-01", locked_unit_rate=40.0, settled_records=book,
            is_domestic=False, arm=vbr.VALUE_BASED)
    assert gas.decision is not None, f"the arm refused a gas renewal it admits: {gas!r}"
    # The gas leg is the one that was priced: the arm's own record of how big this customer is
    # must be the gas leg's EAC, and there is no route to that number from the electricity leg.
    assert gas.decision.eac_mwh == pytest.approx(900.0 * 12 / 1000.0)


def test_the_adapter_SPENDS_the_fuel_rather_than_merely_having_one(monkeypatch):
    """THE CALLER, not the helper -- and this control exists because the obvious one failed.

    `test_the_gas_renewal_is_priced_by_the_gas_churn_curve` above asserts that the two fuels'
    curves differ and that the gas leg's EAC reached the decision. Both are true of an adapter
    that never passes `fuel` at all: the first calls `estimate_churn_probability` directly and
    the second is answered by the record filter. Deleting `fuel=commodity` from the
    `decide_margin` call left all of it green -- a control keyed to the helper surviving a
    mutation of the caller, which is the shape this repo has been caught by before.

    So this one reads the CALL. It fails if the argument is dropped, and it fails if the
    argument is passed as a literal, which is the same defect the seam's control 3 guards one
    writer along.
    """
    seen: list[dict] = []
    real = vbr.decide_margin

    def spy(**kwargs):
        seen.append(kwargs)
        return real(**kwargs)

    monkeypatch.setattr(vbr, "decide_margin", spy)
    book = _dual_fuel_book()
    for commodity, rate in (("gas", 40.0), ("electricity", 200.0)):
        with policy_scope(VALUE_ARM_POLICY):
            vbr.renewal_margin_uplift(
                account_id="C1", commodity=commodity, tariff_type="fixed", term_index=2,
                term_start="2021-01-01", locked_unit_rate=rate, settled_records=book,
                is_domestic=False, arm=vbr.VALUE_BASED)

    assert len(seen) == 2, f"the arm did not reach the decision on both fuels: {seen!r}"
    assert [call.get("fuel") for call in seen] == ["gas", "electricity"], (
        "the adapter did not hand `decide_margin` the renewal's own fuel. Left to its default, "
        "every gas renewal this arm now prices is answered by the ELECTRICITY churn curve -- a "
        "wrong number that looks exactly like a right one"
    )


def test_the_gas_renewal_decides_under_the_GAS_cap_and_not_the_electricity_one():
    """The lawful ceiling is a fact about the fuel. A gas renewal decided under the electricity
    cap is deciding under a bound that does not bind it, and `decide_margin` refuses the
    post-hoc version of that error explicitly.
    """
    from datetime import date as _date

    from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date

    gas_cap = get_cap_unit_rate_for_date("gas", _date(2021, 6, 1))
    elec_cap = get_cap_unit_rate_for_date("electricity", _date(2021, 6, 1))
    assert gas_cap is not None and elec_cap is not None
    assert gas_cap != pytest.approx(elec_cap), (
        "the two caps agree on this date, so this control cannot tell which one the chain "
        "read -- move the date rather than deleting the control"
    )

    book = _dual_fuel_book(year=2020)
    with policy_scope(VALUE_ARM_POLICY):
        result = _drive(commodity="gas", is_domestic=True, tariff_type="fixed",
                        term_start="2021-06-01", struck_unit_rate_gbp_per_mwh=28.0,
                        settled_records=book)
    priced = [e for e in result.value_arm_entries if not e.get("declined")]
    assert priced, f"the chain priced no gas renewal: {result.value_arm_entries!r}"
    for entry in priced:
        assert entry["unit_rate_after"] <= gas_cap + 1e-6, (
            f"the arm asked {entry['unit_rate_after']:.2f} GBP/MWh for a gas renewal against a "
            f"gas cap of {gas_cap:.2f} -- it decided under the wrong fuel's ceiling"
        )


def test_a_fuel_this_supplier_does_not_sell_is_REFUSED_rather_than_priced_as_electricity():
    """The gate still gates, and the fallback under it no longer answers.

    `standing_charge_rate` returned the ELECTRICITY table for any unrecognised commodity until
    2026-09-07, silently. That was unreachable while the gate admitted electricity only; the
    gate is wider now, so the fallback is what stands between a mistyped fuel and a published
    rate priced off the wrong book. It raises, and this asserts both halves.
    """
    from saas.non_commodity import standing_charge_rate

    uplift = vbr.renewal_margin_uplift(
        account_id="C1", commodity="hydrogen", tariff_type="fixed", term_index=2,
        term_start="2021-01-01", locked_unit_rate=200.0, settled_records=_dual_fuel_book(),
        is_domestic=True, arm=vbr.VALUE_BASED)
    assert uplift.not_run_stage == vbr.STAGE_NOT_THE_ARMS_COMMODITY
    assert uplift.uplift_gbp_per_mwh == 0.0

    with pytest.raises(ValueError, match="hydrogen"):
        standing_charge_rate("hydrogen", "resi")
