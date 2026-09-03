"""R15 proofs for the A/B runner — the tool that produces the value cycle's headline.

This file did not exist until 2026-08-26, which is its own finding: `tools/run_value_cycle_ab.py`
produces the single number the whole thesis is scored on (net −£93,555, enterprise value
−£118,252 at the time of writing) and had no test of any kind. Two of its controls already carry
a documented incident in their docstrings; neither had a proof that it fires.

WHAT IS PROVEN HERE, and why each control exists:

  `churn_roster_diff`   — added because aggregates could not answer the question the 12:35Z run
                          raised. That run reported the arm giving up £123,006 of gross margin on
                          a NET +3 churns: £41,000 each, on a domestic book averaging ~£420 of
                          whole-life margin. Either a handful of large accounts carry the delta or
                          the churn count is not the mechanism, and the artefact could not tell
                          those apart. FAIL-OPEN is the killer pattern here: an absent roster
                          reported as "no accounts differ" would be the most reassuring wrong
                          answer this artefact could carry.

                          IT ANSWERED, AND THE ANSWER WAS NEITHER GUESS. The value arm loses
                          C1_2, C3, C6 and C7 and SAVES PROS-2019-0003 — four and one, which the
                          net "+3" had hidden — and not one of the five I&C accounts, refuting
                          the large-account hypothesis this diff was built to test. Their
                          whole-life revenue under the control totals ~£69,000, less than the
                          delta, and an account that churns early earns even less of that. So
                          the churns are not the mechanism either, which is what `margin_movers`
                          below exists to pursue.

  `margin_movers`       — where the delta comes from account by account, with the CONCENTRATION
                          of the absolute movement. A delta spread across 200 customers supports
                          a portfolio claim; a delta carried by three is a case study wearing a
                          portfolio's clothes, and the two must not read the same.

  `realised_metrics`    — its `figure()` RAISES on a missing key, because `.get(key, 0.0)` once
                          reported £0 revenue for BOTH arms, identically, so the delta was a clean
                          zero and nothing looked wrong (R15 FAIL-SILENT, recorded in its own
                          docstring). That control is proven here rather than trusted.

THREE LOOKUP FAULTS WERE FOUND BY A CONTROL BEHAVING WELL, and that is the part worth keeping.
Each live run returned every value as `null`, and each blank named the next fault:

  1. read from `phase2b.per_customer_lifetime`; the published artefact carries it at the TOP level;
  2. keyed by CUSTOMER (`C1`, `C1g`) where `churned_billing_accounts` is keyed by BILLING ACCOUNT
     (`C1`, `C1_2`), so the two never met;
  3. and then the real one — `per_customer_lifetime` IS NOT IN THE RUN AT ALL. It is built by
     `saas/reporting/annual_report.py`, so it exists in the published artefact and never in the
     in-memory result an experiment holds. The source is now the world's own settled records,
     which is what that reporting layer aggregates from and what a harness should have been
     reading anyway.

Had any of those defaulted to 0.0, the artefact would have said four real customers were worth
nothing — a number a reader would have believed, three separate times. Every fault has its own
test, and `margin_basis` is published beside the figures so the two bases cannot be read as one
(R14).
"""

import copy
import json

import pytest

from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH
from simulation.live_population import served_segments
from tools import run_value_cycle_ab as rvca
from tools.run_value_cycle_ab import (
    CLOCK_DEFINITIONS,
    REPORTED_BASIS,
    SETTLED_BASIS,
    _concordance,
    belief_vs_outcome,
    book_at_run,
    book_identity,
    bound_attribution,
    churn_roster_diff,
    churn_volume_attribution,
    clock_audit,
    concordance_null_spread,
    gross_to_net_bridge,
    margin_movers,
    method_skill,
    realised_metrics,
)


def _arm(churned, lifetimes=None, *, lifetimes_at_top_level=True, **phase2b):
    """The smallest run-result shape these two functions read.

    `per_customer_lifetime` really does sit at the phase4c result's TOP level while
    `churned_billing_accounts` sits under `phase2b`, so the default here mirrors the
    live artefact rather than the tidier shape it would be easy to assume.
    """
    result = {"phase2b": dict(phase2b)}
    if churned is not None:
        result["phase2b"]["churned_billing_accounts"] = churned
    if lifetimes_at_top_level:
        result["per_customer_lifetime"] = lifetimes or {}
    else:
        result["phase2b"]["per_customer_lifetime"] = lifetimes or {}
    return result


def _life(value, segment="resi"):
    return {"segment": segment, "net_margin_after_cost_to_serve_gbp": value}


# ---------------------------------------------------------------------------
# churn_roster_diff — the accounts behind the delta
# ---------------------------------------------------------------------------

def test_the_diff_names_the_accounts_each_arm_lost_alone():
    control = _arm(["A", "B"], {"B": _life(120.0)})
    value = _arm(["A", "C"], {"C": _life(340.0)})
    diff = churn_roster_diff(control, value)

    assert diff["available"] is True
    assert [r["account"] for r in diff["only_in_value_arm"]] == ["C"]
    assert [r["account"] for r in diff["only_in_control_arm"]] == ["B"]
    assert diff["churned_under_both"] == 1


def test_the_diff_surfaces_a_single_large_account_carrying_the_delta():
    """The question the 12:35Z run could not answer. One I&C account is worth ~500x a
    domestic one here, so a delta that looks like a portfolio result may be one decision."""
    control = _arm(["A"], {})
    value = _arm(["A", "IC-1"], {"IC-1": _life(-221_491.0, segment="I&C")})
    diff = churn_roster_diff(control, value)

    assert diff["largest_single_difference_gbp"] == pytest.approx(221_491.0)
    assert diff["only_in_value_arm"][0]["segment"] == "I&C"


def test_the_diff_stays_quiet_when_both_arms_lost_the_same_accounts():
    """The partner. A diff that always reports a difference names nothing."""
    diff = churn_roster_diff(_arm(["A", "B"]), _arm(["B", "A"]))
    assert diff["only_in_value_arm"] == []
    assert diff["only_in_control_arm"] == []
    assert diff["largest_single_difference_gbp"] == 0.0
    assert diff["churned_under_both"] == 2


def test_an_arm_that_SAVES_an_account_is_reported_not_netted_away():
    """Three lost and two saved is a different animal from three lost, and the net
    count hides the difference — which is exactly what `realised_delta.churned_accounts`
    does on its own."""
    control = _arm(["S1", "S2"], {"S1": _life(400.0), "S2": _life(500.0)})
    value = _arm(["L1", "L2", "L3"],
                 {f"L{i}": _life(100.0) for i in (1, 2, 3)})
    diff = churn_roster_diff(control, value)

    assert len(diff["only_in_value_arm"]) == 3
    assert len(diff["only_in_control_arm"]) == 2
    assert diff["only_in_control_arm_realised_gbp"] == pytest.approx(900.0)
    assert diff["only_in_value_arm_realised_gbp"] == pytest.approx(300.0)


@pytest.mark.parametrize("control_roster, value_roster", [
    (None, ["A"]),
    (["A"], None),
    (None, None),
    ("A,B", ["A"]),          # a string is not a roster
    (["A"], {"A": True}),    # nor is a dict
])
def test_a_missing_or_malformed_roster_is_unavailable_not_empty(control_roster, value_roster):
    """FAIL-OPEN, the killer pattern for this control. "No accounts differ" and "I could
    not find the roster" must never render as the same artefact."""
    diff = churn_roster_diff(_arm(control_roster), _arm(value_roster))
    assert diff["available"] is False
    assert diff["reason"]
    assert "only_in_value_arm" not in diff


def test_an_account_with_no_lifetime_row_reports_none_not_zero():
    """A silent 0.0 would understate the delta and read as a worthless customer. The
    account still appears — it churned — but its value is a declared blank."""
    diff = churn_roster_diff(_arm([]), _arm(["GHOST"], {}))
    row = diff["only_in_value_arm"][0]
    assert row["account"] == "GHOST"
    assert row["realised_lifetime_margin_gbp"] is None
    assert row["segment"] is None


def test_the_totals_sum_only_the_figures_that_exist():
    """A None must not poison the total into an exception, and must not be counted as 0
    either — the total is over what is known, beside a row that shows what is not."""
    value = _arm(["K", "UNKNOWN"], {"K": _life(250.0)})
    diff = churn_roster_diff(_arm([]), value)
    assert diff["only_in_value_arm_realised_gbp"] == pytest.approx(250.0)
    assert any(r["realised_lifetime_margin_gbp"] is None
               for r in diff["only_in_value_arm"])


def test_an_all_blank_input_reports_unavailable_rather_than_zero():
    """THE NULL CONTROL for the aggregation, and the defect the 13:58Z run showed.

    Five accounts were named, every `realised_lifetime_margin_gbp` was null, and all
    three totals read 0.0 — a verdict no run could move, R15's fourth shape. That run
    was superseded by 14:25Z before it was ever committed, so no artefact in origin
    records the fault and this test is the only thing that now holds it down. It is the
    reassuring wrong answer specifically: `reading` sends the reader to divide
    `largest_single_difference_gbp` into the headline delta, and a fabricated 0.0
    divides to "no concentration", i.e. "the loss is a portfolio property" — the one
    conclusion this artefact exists to be capable of refusing.
    """
    diff = churn_roster_diff(_arm(["KEPT"], {}), _arm(["GONE"], {}))

    assert [r["account"] for r in diff["only_in_value_arm"]] == ["GONE"]
    assert diff["only_in_value_arm_realised_gbp"] is None
    assert diff["only_in_control_arm_realised_gbp"] is None
    assert diff["largest_single_difference_gbp"] is None
    assert diff["realised_coverage"]["only_in_value_arm"] == {"accounts": 1, "valued": 0}


def test_an_empty_roster_side_still_totals_an_honest_zero():
    """The partner to the null control, and the reason it is not simply "null when in
    doubt". Nothing differing on a side really is 0.0 there — a control that answered
    "unavailable" to every question would be as constant as the one it replaced."""
    diff = churn_roster_diff(_arm([]), _arm(["K"], {"K": _life(250.0)}))

    assert diff["only_in_control_arm"] == []
    assert diff["only_in_control_arm_realised_gbp"] == 0.0
    assert diff["only_in_value_arm_realised_gbp"] == pytest.approx(250.0)
    assert diff["largest_single_difference_gbp"] == pytest.approx(250.0)


def test_a_partially_valued_side_publishes_that_its_total_is_a_floor():
    """A sum over two of five accounts is a FLOOR, and a floor that does not say so is
    read as a measurement. The total stays a real number — it is known — but
    `realised_coverage` is what stops it being divided into the headline as if complete."""
    value = _arm(["K", "UNKNOWN"], {"K": _life(250.0)})
    diff = churn_roster_diff(_arm([]), value)

    assert diff["only_in_value_arm_realised_gbp"] == pytest.approx(250.0)
    assert diff["realised_coverage"]["only_in_value_arm"] == {"accounts": 2, "valued": 1}


def test_a_non_string_entry_in_the_roster_is_dropped_not_crashed():
    diff = churn_roster_diff(_arm([]), _arm(["A", None, 7, "B"]))
    assert sorted(r["account"] for r in diff["only_in_value_arm"]) == ["A", "B"]


def test_each_arms_values_come_from_its_own_run():
    """An account the control lost is valued from the CONTROL's book. Reading both sides
    out of one arm's `per_customer_lifetime` would price a counterfactual with the wrong
    world's numbers."""
    control = _arm(["ONLY-CONTROL"], {"ONLY-CONTROL": _life(777.0)})
    value = _arm([], {"ONLY-CONTROL": _life(-999.0)})   # same id, different world
    diff = churn_roster_diff(control, value)
    assert diff["only_in_control_arm"][0]["realised_lifetime_margin_gbp"] == (
        pytest.approx(777.0))


def test_the_lifetime_lookup_reads_the_top_level_where_the_artefact_actually_puts_it():
    """FOUND LIVE (2026-08-26). The first version read `phase2b.per_customer_lifetime`;
    the phase4c result carries it at the TOP level, so every account came back blank.
    The control did its job — it declared the blanks instead of rendering 0.0 — but the
    blank was a lookup bug, and a reader would have concluded those customers were
    worthless rather than unlooked-up."""
    value = _arm(["C3"], {"C3": _life(597.68)}, lifetimes_at_top_level=True)
    row = churn_roster_diff(_arm([]), value)["only_in_value_arm"][0]
    assert row["realised_lifetime_margin_gbp"] == pytest.approx(597.68)
    assert row["segment"] == "resi"


def test_the_lifetime_lookup_still_finds_it_under_phase2b():
    """Both shapes are accepted, so a producer that moves the field does not silently
    blank the column."""
    value = _arm(["C3"], {"C3": _life(597.68)}, lifetimes_at_top_level=False)
    row = churn_roster_diff(_arm([]), value)["only_in_value_arm"][0]
    assert row["realised_lifetime_margin_gbp"] == pytest.approx(597.68)


def test_dual_fuel_legs_are_summed_into_the_billing_account_the_roster_names():
    """SECOND MISMATCH, same live run. `per_customer_lifetime` is keyed by CUSTOMER
    (`C1`, `C1g`) and `churned_billing_accounts` by BILLING ACCOUNT (`C1`). A dual-fuel
    household bills once, so the legs sum — using the same helper `saas.clv_model`
    uses, so the two cannot drift into different ideas of one account."""
    value = _arm(["C1"], {"C1": _life(162.52), "C1g": _life(80.00)})
    row = churn_roster_diff(_arm([]), value)["only_in_value_arm"][0]
    assert row["realised_lifetime_margin_gbp"] == pytest.approx(242.52)


def test_a_billing_account_with_no_customer_row_behind_it_stays_a_declared_blank():
    """`C1_2` is a real secondary billing account the household register does not
    carry, so it genuinely has no lifetime figure. It must still appear — it churned —
    and its value must be null, not zero."""
    diff = churn_roster_diff(_arm([]), _arm(["C1_2"], {"C1": _life(162.52)}))
    row = diff["only_in_value_arm"][0]
    assert row["account"] == "C1_2"
    assert row["realised_lifetime_margin_gbp"] is None


# ---------------------------------------------------------------------------
# the source of realised margin, and the basis it is stated on (R14)
# ---------------------------------------------------------------------------

def _record(customer_id, net, segment="resi"):
    return {"customer_id": customer_id, "net_margin_gbp": net, "segment": segment}


def _records_arm(records, churned=None):
    """An arm shaped like the LIVE in-memory result: settled records, no
    `per_customer_lifetime` anywhere, because the reporting layer builds that."""
    result = {"phase2b": {"all_records": records}}
    if churned is not None:
        result["phase2b"]["churned_billing_accounts"] = churned
    return result


def test_realised_margin_falls_back_to_the_worlds_own_settled_records():
    """FOUND LIVE, third lookup (2026-08-26). `per_customer_lifetime` is not in the run
    at ALL — `saas/reporting/annual_report.py` builds it — so an A/B holding the in-memory
    result can never find it. The settled records are what that reporting layer itself
    aggregates from, and they are what a harness should be reading anyway: what happened,
    not a renderer's derivation of it."""
    control = _records_arm([_record("C6", 500.0, "SME")])
    value = _records_arm([_record("C6", 80.0, "SME")])
    movers = margin_movers(control, value)

    assert movers["available"] is True
    assert movers["margin_basis"] == SETTLED_BASIS
    assert movers["biggest_movers"][0]["delta_gbp"] == pytest.approx(-420.0)
    assert movers["biggest_movers"][0]["segment"] == "SME"


def test_the_reported_basis_is_preferred_when_the_artefact_supplies_it():
    """An artefact-driven caller has the richer after-cost-to-serve figure, so it wins —
    and the basis says which one a reader is looking at rather than leaving them to infer
    it from a key name (R14)."""
    control = _arm(None, {"C6": _life(500.0, "SME")})
    value = _arm(None, {"C6": _life(80.0, "SME")})
    movers = margin_movers(control, value)
    assert movers["margin_basis"] == REPORTED_BASIS


def test_the_two_bases_are_never_silently_mixed_in_one_number():
    """The bases differ by the whole cost-to-serve stack, so a comparison that took one
    arm from each would report a difference that is an accounting change, not a decision."""
    assert SETTLED_BASIS != REPORTED_BASIS
    assert "BEFORE cost-to-serve" in SETTLED_BASIS
    assert "after cost-to-serve as well" in REPORTED_BASIS


def test_dual_fuel_legs_are_summed_from_the_settled_records_too():
    """The same billing-account folding on the records path — otherwise the fallback
    quietly counts a dual-fuel household twice."""
    control = _records_arm([_record("C1", 100.0), _record("C1g", 50.0)])
    value = _records_arm([_record("C1", 100.0), _record("C1g", -50.0)])
    movers = margin_movers(control, value)
    assert movers["accounts_compared"] == 1
    assert movers["biggest_movers"][0]["account"] == "C1"
    assert movers["biggest_movers"][0]["delta_gbp"] == pytest.approx(-100.0)


def test_the_churn_roster_publishes_its_basis_as_well():
    """The roster's value column is the same figure on the same basis, so it carries the
    same label — a reader comparing the two rows must not have to assume they agree."""
    diff = churn_roster_diff(_records_arm([], []),
                             _records_arm([_record("C6", 80.0, "SME")], ["C6"]))
    assert diff["margin_basis"] == SETTLED_BASIS
    assert diff["only_in_value_arm"][0]["realised_lifetime_margin_gbp"] == pytest.approx(80.0)


def test_records_that_are_not_dicts_or_carry_no_customer_are_skipped():
    """A malformed record must not crash a ten-year experiment at the reporting step."""
    control = _records_arm([_record("A", 10.0)])
    value = _records_arm([_record("A", 5.0), None, "junk", {"net_margin_gbp": 1.0}])
    movers = margin_movers(control, value)
    assert movers["accounts_compared"] == 1
    assert movers["biggest_movers"][0]["delta_gbp"] == pytest.approx(-5.0)


# ---------------------------------------------------------------------------
# margin_movers — where the delta actually comes from
# ---------------------------------------------------------------------------

def test_concentration_reports_one_when_a_single_account_is_the_headline():
    """The claim this number exists to stop: a delta carried by one customer read as a
    portfolio result. Concentration near 1.0 means case study, not portfolio."""
    control = _arm(None, {"A": _life(100.0), "B": _life(200.0), "C": _life(50.0)})
    value = _arm(None, {"A": _life(100.0), "B": _life(-800.0), "C": _life(50.0)})
    movers = margin_movers(control, value, top=1)

    assert movers["available"] is True
    assert movers["accounts_that_moved"] == 1
    assert movers["concentration_top_n_share_of_absolute_movement"] == pytest.approx(1.0)
    assert movers["biggest_movers"][0]["account"] == "B"
    assert movers["biggest_movers"][0]["delta_gbp"] == pytest.approx(-1000.0)


def test_concentration_reports_low_when_the_delta_is_spread_across_the_book():
    """The partner. A concentration metric that always says 1.0 cannot support a
    portfolio claim, only refuse one."""
    control = _arm(None, {f"A{i}": _life(100.0) for i in range(40)})
    value = _arm(None, {f"A{i}": _life(90.0) for i in range(40)})
    movers = margin_movers(control, value, top=4)

    assert movers["accounts_that_moved"] == 40
    assert movers["concentration_top_n_share_of_absolute_movement"] == pytest.approx(0.1)


def test_movers_are_ranked_by_absolute_movement_not_signed():
    """A large GAIN matters as much as a large loss for reading concentration; ranking
    on the signed delta would bury the account that saved the arm."""
    control = _arm(None, {"UP": _life(0.0), "DOWN": _life(500.0), "FLAT": _life(10.0)})
    value = _arm(None, {"UP": _life(900.0), "DOWN": _life(100.0), "FLAT": _life(10.0)})
    ranked = [r["account"] for r in margin_movers(control, value)["biggest_movers"]]
    assert ranked[:2] == ["UP", "DOWN"]


def test_an_account_present_in_only_one_arm_still_moves():
    """A customer the value arm never acquired, or one it drove out before any
    settlement, must not vanish from the comparison by having no row on one side."""
    movers = margin_movers(_arm(None, {"GONE": _life(300.0)}), _arm(None, {}))
    assert movers["accounts_that_moved"] == 1
    assert movers["biggest_movers"][0]["delta_gbp"] == pytest.approx(-300.0)


def test_dual_fuel_legs_are_summed_before_the_comparison():
    """The same billing-account key space the churn roster uses — a household whose gas
    leg moved and whose electricity leg did not has moved once, not twice."""
    control = _arm(None, {"C1": _life(100.0), "C1g": _life(50.0)})
    value = _arm(None, {"C1": _life(100.0), "C1g": _life(-50.0)})
    movers = margin_movers(control, value)
    assert movers["accounts_compared"] == 1
    assert movers["biggest_movers"][0]["account"] == "C1"
    assert movers["biggest_movers"][0]["delta_gbp"] == pytest.approx(-100.0)


def test_movers_is_unavailable_with_a_named_reason_when_neither_arm_published():
    """FAIL-OPEN. No book must not read as "nothing moved", which is the most
    reassuring wrong answer this row could give."""
    movers = margin_movers(_arm(None, {}), _arm(None, {}))
    assert movers["available"] is False
    assert movers["reason"]
    assert "biggest_movers" not in movers


def test_movers_stays_quiet_when_the_two_arms_produced_the_same_book():
    """If the writer were a no-op this must report zero movement, or the row cannot
    distinguish a working arm from a broken one."""
    book = {"A": _life(100.0), "B": _life(200.0)}
    movers = margin_movers(_arm(None, dict(book)), _arm(None, dict(book)))
    assert movers["accounts_that_moved"] == 0
    assert movers["total_absolute_movement_gbp"] == 0.0
    assert movers["concentration_top_n_share_of_absolute_movement"] is None


# ---------------------------------------------------------------------------
# realised_metrics — the fail-silent this file's docstring records
# ---------------------------------------------------------------------------

def _full_arm(**overrides):
    """THREE DISTINCT VALUES PER FIGURE, and that is the whole point.

    A fixture whose `all_records` summed to the same `total_net` the run's summary carries could
    not see which of the two `realised_metrics` reports — the balanced-fixture pattern, and the
    exact blindness that let the live artefact publish GBP 113,282.62 and GBP 153,244.79 for one
    arm for two days.

    Since 2026-08-28 there are THREE places a net margin can be read from, not two, because
    `simulation/settlement_clocks.refresh_settlement_scalars` now re-derives the bare scalars
    from the mutated rows and preserves the settlement loop's fold under `provisioned_*`. So
    the fixture carries three distinct values for each figure — rows 1,200 / 3.00 / 1,450, bare
    scalars 1,000 / 10.00 / 1,250, provisioned 900 / 12.00 / 1,150 — and every assertion below
    lands away from all the others. In a REAL refreshed run the bare scalars equal the rows;
    holding them apart here is what gives the test the power to say which one was read, which
    a faithful-but-balanced fixture would not have.
    """
    phase2b = {
        "total_net": 1_000.0, "total_gross": 5_000.0, "total_bad_debt": 10.0,
        "total_capital": 40.0,
        "final_treasury": 1_250.0, "churned_billing_accounts": ["A"],
        # What the settlement loop froze, preserved by the refresh. Distinct from BOTH the rows
        # and the bare scalars, so a block that reported either under a `provisioned_` label
        # would fail rather than coincide.
        "provisioned_total_net": 900.0,
        "provisioned_total_bad_debt": 12.0,
        "provisioned_final_treasury": 1_150.0,
        "value_arm_log": [{}, {}],
        "all_records": [
            {"net_margin_gbp": 700.0, "bad_debt_gbp": 2.0,
             "treasury_cash_balance_gbp": 1_400.0},
            {"net_margin_gbp": 500.0, "bad_debt_gbp": 1.0,
             "treasury_cash_balance_gbp": 1_450.0},
        ],
    }
    phase2b.update(overrides)
    return {"phase2b": phase2b,
            "enterprise_value": {"portfolio": {"enterprise_value_gbp": 900.0,
                                               "account_count": 12}}}


def test_realised_metrics_reports_what_the_world_did():
    metrics = realised_metrics(_full_arm())
    assert metrics["total_net_gbp"] == 1_200.0
    assert metrics["total_gross_margin_gbp"] == 5_000.0
    assert metrics["churned_accounts"] == 1
    assert metrics["renewals_priced_by_the_arm"] == 2


def test_the_net_margin_is_summed_from_the_rows_not_read_off_the_frozen_summary():
    """THE DEFECT, 2026-08-28. `run_phase4c_on_phase2b` mutates `all_records` in place —
    `apply_emergent_bad_debt` replaces the flat-rate provision with the arrears model's realised
    write-offs and `apply_debt_recovery` credits back the DCA proceeds — while
    `run_phase2b`'s `total_net`/`total_bad_debt`/`final_treasury` stay frozen at the values they
    had before. Reading those scalars published a superseded net margin beside the bridge's
    live one, GBP 39,962.17 apart, under a label claiming both came from the settled records.

    This asserts the FIGURES, not the wiring: the rows win, and the superseded read survives
    under its own name so the next reader can tell the two apart."""
    metrics = realised_metrics(_full_arm())

    assert metrics["total_net_gbp"] == 1_200.0
    assert metrics["total_bad_debt_gbp"] == 3.0
    assert metrics["final_treasury_gbp"] == 1_450.0
    # THE PROVISIONED FIGURES COME FROM THE `provisioned_` NAMES, not from the bare scalars
    # (2026-08-28, second pass). The bare names are re-derived from the mutated rows by
    # `refresh_settlement_scalars`, so reading them under a provisioned label would publish a
    # realised figure on a provisioned clock — a new instance of the class this block documents.
    # The fixture's 900 / 12.00 / 1,150 are away from both the rows and the bare scalars, so
    # only the right read passes.
    assert metrics["provisioned_net_gbp"] == 900.0
    assert metrics["provisioned_bad_debt_gbp"] == 12.0
    assert metrics["provisioned_final_treasury_gbp"] == 1_150.0
    # Every published figure carries its clock, in the block, where the JSON reader is (R14).
    assert metrics["clocks"]["total_net_gbp"] == "settled-realised"
    assert metrics["clocks"]["provisioned_net_gbp"] == "settled-provisioned"


def test_an_arm_with_no_rows_refuses_rather_than_falling_back_to_the_frozen_scalars():
    """R15 FAIL-OPEN. The scalars are still there when the rows are not, so the cheap failure
    mode is to quietly report the superseded figure under the realised label — which is the
    original defect wearing the repair's clothes."""
    arm = _full_arm()
    del arm["phase2b"]["all_records"]
    with pytest.raises(ValueError, match="all_records"):
        realised_metrics(arm)


@pytest.mark.parametrize("missing", ["total_gross", "total_capital",
                                     "provisioned_total_net", "provisioned_total_bad_debt",
                                     "provisioned_final_treasury"])
def test_a_missing_figure_raises_rather_than_reporting_zero(missing):
    """R15 FAIL-SILENT, and it has already happened once: `.get(key, 0.0)` reported £0
    revenue for BOTH arms, identically, so the delta was a clean zero and nothing looked
    wrong. A metric that cannot find its own figure has to say so."""
    arm = _full_arm()
    del arm["phase2b"][missing]
    with pytest.raises(KeyError, match=missing):
        realised_metrics(arm)


# ---------------------------------------------------------------------------
# clock_audit — the control, and the four mutations that must red it (R15)
# ---------------------------------------------------------------------------

def _clocked_artefact():
    """A three-arm artefact shaped like the live one, on the repaired labels.

    The arm blocks come from `realised_metrics` itself rather than being hand-written, so the
    numbers the control reconciles are the ones the publisher really emits; the bridge and the
    verdict are given the ROWS figure (1,200) because that is what the repaired chain puts
    there. The level arm is present so the audit has three arms to place, as the published
    three-arm run does."""
    arm = realised_metrics(_full_arm())
    return {
        "clock_definitions": dict(CLOCK_DEFINITIONS),
        "control_arm": copy.deepcopy(arm),
        "value_arm": copy.deepcopy(arm),
        "level_arm": copy.deepcopy(arm),
        "gross_to_net_bridge": {
            "clock": "settled-realised",
            "control_arm": {"net_margin_gbp": 1_200.0},
            "value_arm": {"net_margin_gbp": 1_200.0},
        },
        "level_vs_selection": {
            "clock": "settled-realised",
            "control_net_gbp": 1_200.0,
            "value_arm_net_gbp": 1_200.0,
            "level_arm_net_gbp": 1_200.0,
        },
    }


def test_the_clock_audit_passes_the_repaired_artefact():
    """THE NULL RUNG. A control whose PASS branch is unreachable reports a constant verdict, so
    the honest artefact has to be shown passing before any mutation below means anything."""
    audit = clock_audit(_clocked_artefact())

    assert audit["passes"] is True, audit["failures"]
    assert audit["arms_checked"] == ["control_arm", "level_arm", "value_arm"]
    assert audit["clocks_in_use"] == ["settled-provisioned", "settled-realised"]
    # Two per arm block, plus the bridge's two, plus the verdict's three.
    assert audit["figures_checked"] == 11


def test_relabelling_the_superseded_figure_as_realised_fires_the_control():
    """THE MUTATION THE DOORBELL NAMES, and the cheapest way to make this control go quiet:
    leave both figures published and call them the same clock. Two disagreeing net margins then
    sit on one clock for one arm, which is the defect verbatim."""
    artefact = _clocked_artefact()
    artefact["control_arm"]["clocks"]["provisioned_net_gbp"] = "settled-realised"

    audit = clock_audit(artefact)

    assert audit["passes"] is False
    assert any("ONE clock" in f and "control_arm" in f for f in audit["failures"])


def test_a_net_margin_published_with_no_clock_at_all_fires_the_control():
    """The pre-repair state of the file: figures published, nothing saying which clock."""
    artefact = _clocked_artefact()
    del artefact["value_arm"]["clocks"]["total_net_gbp"]

    audit = clock_audit(artefact)

    assert audit["passes"] is False
    assert any("NO declared clock" in f for f in audit["failures"])


def test_a_clock_the_artefact_never_defines_fires_the_control():
    """A label is not a clock. `banked` is the specific invented name this world does not have,
    and inventing it was the likeliest wrong answer to the defect this control closes."""
    artefact = _clocked_artefact()
    artefact["gross_to_net_bridge"]["clock"] = "banked"

    audit = clock_audit(artefact)

    assert audit["passes"] is False
    assert any("does not define" in f for f in audit["failures"])


def test_two_blocks_on_one_clock_that_disagree_fire_the_control():
    """The original defect's arithmetic, on the labels the repair leaves behind: the bridge and
    the arm block both claim `settled-realised`, so they must agree to the penny."""
    artefact = _clocked_artefact()
    artefact["gross_to_net_bridge"]["control_arm"]["net_margin_gbp"] = 113_282.62

    audit = clock_audit(artefact)

    assert audit["passes"] is False
    assert any("113,282.62" in f for f in audit["failures"])


@pytest.mark.parametrize("strip", ["clock_definitions", "arms"])
def test_the_audit_fails_closed_when_it_has_nothing_to_compare(strip):
    """R15 FAIL-OPEN, the pattern that kills a control like this: an artefact it cannot read at
    all must not report PASS. An audit with nothing to compare is a failed audit."""
    artefact = _clocked_artefact()
    if strip == "clock_definitions":
        del artefact["clock_definitions"]
    else:
        for key in ("control_arm", "value_arm", "level_arm",
                    "gross_to_net_bridge", "level_vs_selection"):
            del artefact[key]

    audit = clock_audit(artefact)

    assert audit["passes"] is False


def test_the_expected_value_the_arm_maximises_is_not_among_the_metrics():
    """Scoring the arm on its own objective would make the comparison circular. The
    absence is deliberate and stated in the docstring, so it is asserted here."""
    metrics = realised_metrics(_full_arm(expected_value_gbp=9_999.0))
    assert not any("expected_value" in key for key in metrics)


# ---------------------------------------------------------------------------
# belief_vs_outcome — inference, or a profitable miscalibration?
# ---------------------------------------------------------------------------

def _decision(account, believed, term="2020-01-01", margin=10.0, **extra):
    return {"customer_id": account, "term_start": term,
            "believed_p_retain": believed,
            "chosen_margin_gbp_per_mwh": margin, **extra}


def _event(account, event_type, term="2020-01-01"):
    return {"customer_id": account, "event_date": term, "event_type": event_type}


def _arm_with(log, events):
    return {"phase2b": {"value_arm_log": log, "customer_events": events}}


def test_a_belief_that_ranks_perfectly_scores_auc_one():
    """The upper end. If this did not reach 1.0 the statistic could not report skill."""
    log = [_decision(f"A{i}", p) for i, p in enumerate([0.95, 0.9, 0.85, 0.2, 0.15, 0.1])]
    events = [_event(f"A{i}", t) for i, t in enumerate(["renewed"] * 3 + ["churned"] * 3)]
    result = belief_vs_outcome(_arm_with(log, events))
    assert result["available"] is True
    assert result["discrimination_auc"] == pytest.approx(1.0)
    assert result["priced_and_scored"] == 6


def test_a_belief_carrying_NO_information_scores_exactly_a_half():
    """THE RESULT THAT WOULD FALSIFY THE THESIS while the P&L still improved, so it must be
    unmistakable rather than approximately a half. Ties count a half each, so a constant
    belief cannot score 1.0 or 0.0 by an accident of sort order."""
    log = [_decision(f"A{i}", 0.5) for i in range(6)]
    events = [_event(f"A{i}", t) for i, t in enumerate(["renewed"] * 3 + ["churned"] * 3)]
    assert belief_vs_outcome(_arm_with(log, events))["discrimination_auc"] == pytest.approx(0.5)


def test_a_belief_that_ranks_BACKWARDS_scores_below_a_half():
    """Anti-skill has to be distinguishable from no skill: an arm acting on an inverted
    belief is worse than one acting on a coin, and 0.5 would hide that."""
    log = [_decision(f"A{i}", p) for i, p in enumerate([0.1, 0.15, 0.2, 0.85, 0.9, 0.95])]
    events = [_event(f"A{i}", t) for i, t in enumerate(["renewed"] * 3 + ["churned"] * 3)]
    assert belief_vs_outcome(_arm_with(log, events))["discrimination_auc"] == pytest.approx(0.0)


def test_calibration_error_names_its_direction():
    """Believing customers are stickier than they are is a different defect from the
    reverse, and the sign is the whole message."""
    log = [_decision(f"A{i}", 0.9) for i in range(10)]
    events = [_event(f"A{i}", t) for i, t in enumerate(["renewed"] * 5 + ["churned"] * 5)]
    result = belief_vs_outcome(_arm_with(log, events))
    assert result["mean_believed_p_retain"] == pytest.approx(0.9)
    assert result["realised_retention_rate"] == pytest.approx(0.5)
    assert result["calibration_error"] == pytest.approx(0.4)


def test_calibration_and_discrimination_are_independent():
    """A model can be uniformly wrong about the LEVEL and still rank correctly — which is
    real information and a repairable defect. If these two moved together the measurement
    could not tell 'wrong scale' from 'no signal', which is the distinction it exists for."""
    log = [_decision(f"A{i}", p) for i, p in enumerate([0.99, 0.98, 0.97, 0.96, 0.95, 0.94])]
    events = [_event(f"A{i}", t) for i, t in enumerate(["renewed"] * 3 + ["churned"] * 3)]
    result = belief_vs_outcome(_arm_with(log, events))
    assert result["discrimination_auc"] == pytest.approx(1.0)
    assert result["calibration_error"] > 0.4


def test_the_outcome_side_is_a_TALLY_not_a_second_probability():
    """R15 INDEPENDENCE. A run publishing a contradictory probability field must not move
    the realised side — the same defect `simulation/customer_events.py` records having paid
    for once, when comparing two probabilities produced a spurious error pattern."""
    log = [_decision(f"A{i}", 0.5) for i in range(4)]
    events = [dict(_event(f"A{i}", t), realized_churn_probability=0.99,
                   company_churn_estimate=0.99)
              for i, t in enumerate(["renewed"] * 2 + ["churned"] * 2)]
    assert belief_vs_outcome(_arm_with(log, events))["realised_retention_rate"] == (
        pytest.approx(0.5))


def test_a_decision_is_scored_against_ITS_OWN_renewal_not_any_other():
    """An account renews many times and only one of those decisions is the one being
    scored. Keying on the account alone would grade a 2020 decision against a 2024 outcome."""
    log = [_decision("A", 0.9, term="2020-01-01"), _decision("A", 0.2, term="2024-01-01")]
    events = [_event("A", "renewed", "2020-01-01"), _event("A", "churned", "2024-01-01")]
    result = belief_vs_outcome(_arm_with(log, events))
    assert result["discrimination_auc"] == pytest.approx(1.0)
    assert result["priced_and_scored"] == 2


def test_declined_renewals_are_not_scored_as_decisions():
    """A decline is a decision NOT to price; scoring it would grade a belief the arm never
    formed and move the denominator."""
    log = [_decision("A", 0.9), {"customer_id": "B", "term_start": "2020-01-01",
                                 "declined": True, "reason": "no lawful offer"}]
    events = [_event("A", "renewed"), _event("B", "churned")]
    assert belief_vs_outcome(_arm_with(log, events))["priced_and_scored"] == 1


def test_an_unmatched_decision_is_COUNTED_not_dropped():
    """A silently moving denominator makes a calibration figure unreadable."""
    log = [_decision("A", 0.9), _decision("GHOST", 0.9)]
    result = belief_vs_outcome(_arm_with(log, [_event("A", "renewed")]))
    assert result["priced_and_scored"] == 1
    assert result["unmatched_decisions"] == 1


def test_the_auc_is_none_rather_than_invented_when_one_side_is_empty():
    """FAIL-OPEN. With no churn there is nothing to rank against, and 1.0 would read as
    perfect skill on a population that could not disagree."""
    log = [_decision(f"A{i}", 0.9) for i in range(3)]
    result = belief_vs_outcome(_arm_with(log, [_event(f"A{i}", "renewed") for i in range(3)]))
    assert result["discrimination_auc"] is None
    assert result["auc_population"] == {"retained": 3, "left": 0}


@pytest.mark.parametrize("phase2b", [
    {},
    {"value_arm_log": [], "customer_events": [{"x": 1}]},
    {"value_arm_log": [{"customer_id": "A"}], "customer_events": []},
])
def test_belief_vs_outcome_is_unavailable_with_a_named_reason(phase2b):
    """FAIL-OPEN. 'The arm priced nothing' and 'I cannot score it' must not both render as
    a clean absence."""
    result = belief_vs_outcome({"phase2b": phase2b})
    assert result["available"] is False
    assert result["reason"]


def test_coverage_is_published_so_the_statistics_cannot_be_read_as_the_whole_book():
    """The first live run scored 28 of 58 decisions. Calibration and AUC over half a
    population are still worth having and are NOT the same claim as over all of it, so the
    share is a published field rather than something a reader must divide out."""
    log = [_decision("A", 0.9), _decision("GHOST1", 0.9), _decision("GHOST2", 0.9)]
    result = belief_vs_outcome(_arm_with(log, [_event("A", "renewed")]))
    assert result["scored_share_of_priced"] == pytest.approx(1 / 3)
    assert "scored_share_of_priced" in result["reading"]


def test_full_coverage_reports_one_rather_than_being_omitted():
    """A field that only appears when it is bad is a field a reader learns to ignore."""
    log = [_decision("A", 0.9), _decision("B", 0.2)]
    events = [_event("A", "renewed"), _event("B", "churned")]
    assert belief_vs_outcome(_arm_with(log, events))["scored_share_of_priced"] == 1.0


def test_the_unmatched_decisions_are_sampled_and_dated_not_merely_counted():
    """A bare count is not much better than a silent drop. The first live run reported 30
    of 58 unmatched and nothing in the artefact could say why, so the next reader gets a
    sample, a per-year distribution and a stated hypothesis."""
    log = [_decision("A", 0.9),
           _decision("G", 0.9, term="2023-05-01"),
           _decision("H", 0.5, term="2023-09-01")]
    result = belief_vs_outcome(_arm_with(log, [_event("A", "renewed")]))
    assert result["unmatched_by_year"] == {"2023": 2}
    assert {r["account"] for r in result["unmatched_sample"]} == {"G", "H"}
    assert "rolled NO" in result["unmatched_meaning"]


def test_an_unmatched_decision_is_excluded_rather_than_counted_as_retained():
    """Scoring a belief about retention against a renewal where leaving was impossible
    would flatter the arm — the realised rate must not absorb them."""
    log = [_decision("A", 0.9), _decision("B", 0.9)]
    result = belief_vs_outcome(_arm_with(log, [_event("A", "churned")]))
    assert result["priced_and_scored"] == 1
    assert result["realised_retention_rate"] == 0.0


# ---------------------------------------------------------------------------
# method_skill — A48, does the arm's own price rank JOINT value created?
# ---------------------------------------------------------------------------
#
# The mission (director, 2026-08-28): "the enterprise value is the automated method for finding
# those customers, not the book itself." Every headline the project publishes is about the BOOK,
# and until this landed nothing measured the METHOD. Frame:
# `docs/design/A48_MEASURING_THE_METHOD_FRAME.md`.
#
# THE KILLER PATTERNS THIS SECTION IS AIMED AT, named before the tests:
#
#   FAIL-OPEN   — a statistic that returns the null (0.5) when it has no population would report
#                 "no skill" for "nothing measured", and a reader cannot tell those apart. It
#                 must return None.
#   FAIL-OPEN   — a decision whose net margin never resolved, scored at zero, puts a coverage
#                 gap into the outcome and the rank statistic reads it as a real ranking.
#   TAUTOLOGY   — the constant-signal null must run through the SAME code path as the estimate.
#                 A null asserted as 0.5 by a separate branch proves nothing about the estimator.
#
# THE TERM BOUNDARY IS THE OTHER SUBJECT HERE. `A47`'s view groups by calendar YEAR; a priced
# term is 365 days from an arbitrary start, so a customer-year mixes two decisions. The test
# below mutates a settled row across the term boundary and requires the answer to MOVE — under
# a year grouping it would not, which is exactly the defect the FRAME named rather than deferred.

_CAP_2022 = 283.4          # published Ofgem electricity cap unit rate, £/MWh, 2022
_GAS_CAP_2022 = 73.7       # ...and the GAS one. Not the same number, and that is the point.
_TERM = "2022-01-01"
_IN_TERM = "2022-06-01"


def _a48_settled(account, *, paid_gbp, net_gbp, mwh=10.0, on=_IN_TERM, commodity="electricity"):
    """One settled row, shaped as `simulation/settlement_daily.fold_to_days` leaves them."""
    return {"customer_id": account, "settlement_date": on, "commodity": commodity,
            "consumption_kwh": mwh * 1000.0, "revenue_gbp": paid_gbp,
            "margin_gbp": net_gbp, "net_margin_gbp": net_gbp}


def _a48_priced(account, margin, term=_TERM):
    return {"customer_id": account, "term_start": term,
            "chosen_margin_gbp_per_mwh": margin, "believed_p_retain": 0.9}


def _a48_run(log, records):
    return {"phase2b": {"value_arm_log": log, "all_records": records}}


def _a48_rising():
    """Four accounts whose joint value rises with the margin the arm chose for them.

    Paid is held constant so the household's saving is identical across accounts; the net
    margin rises with the chosen margin, which is the relationship a working method would
    produce. Concordance must be 1.0.
    """
    log = [_a48_priced(f"A{i}", 1.0 + i) for i in range(4)]
    records = [_a48_settled(f"A{i}", paid_gbp=2000.0, net_gbp=100.0 * (i + 1)) for i in range(4)]
    return log, records


def test_a_signal_that_ranks_joint_value_perfectly_scores_one():
    """The upper end. If this did not reach 1.0 the statistic could not report skill at all."""
    result = method_skill(_a48_run(*_a48_rising()))
    assert result["available"] is True
    assert result["concordance"] == pytest.approx(1.0)
    assert result["decisions_scored"] == 4
    assert result["accounts"] == 4


def test_a_method_that_prices_highest_where_it_destroys_the_relationship_scores_below_a_half():
    """THE DIRECTOR'S OWN CASE, and the one worth being able to see: the arm ranks
    confidently and uses the ranking to EXTRACT. Its most expensive decisions are the ones
    where the household kept least, so joint value falls as the price rises. A book-only
    headline cannot distinguish this from skill; this figure can."""
    log = [_a48_priced(f"A{i}", 1.0 + i) for i in range(4)]
    # Paid RISES with the chosen margin, so the household's saving — and the joint value —
    # falls exactly where the arm was most confident.
    records = [_a48_settled(f"A{i}", paid_gbp=1000.0 + 400.0 * i, net_gbp=100.0) for i in range(4)]
    result = method_skill(_a48_run(log, records))
    assert result["concordance"] == pytest.approx(0.0)


def test_a_constant_signal_scores_exactly_a_half():
    """THE RESULT THAT SAYS THE METHOD HAS NO SKILL, so it must be unmistakable rather than
    approximately a half. Signal ties count a half each, so a constant price cannot score 1.0
    or 0.0 by an accident of sort order."""
    log = [_a48_priced(f"A{i}", 2.0) for i in range(4)]
    records = [_a48_settled(f"A{i}", paid_gbp=2000.0, net_gbp=100.0 * (i + 1)) for i in range(4)]
    assert method_skill(_a48_run(log, records))["concordance"] == pytest.approx(0.5)


def test_the_published_null_runs_through_the_same_path_and_is_exactly_a_half():
    """ANTI-TAUTOLOGY. The flat-rules arm's `value_arm_log` is empty by construction, so the
    null cannot be read off a control run — it is constructed by replacing the signal with the
    flat rule's constant and running the SAME estimator over the SAME outcomes. Asserting it
    from a separate branch would prove nothing about the estimator, so this pins that the
    published null sits beside a NON-null estimate rather than replacing it."""
    result = method_skill(_a48_run(*_a48_rising()))
    assert result["null_constant_signal_concordance"] == pytest.approx(0.5)
    assert result["concordance"] != pytest.approx(0.5)


def test_nothing_to_rank_reports_none_rather_than_the_null():
    """FAIL-OPEN, the killer for this control. "The method has no skill" and "there was nothing
    to measure" must never read the same. One identical outcome across every decision leaves no
    comparable pair, and 0.5 there would be the most reassuring wrong answer available."""
    log = [_a48_priced(f"A{i}", 1.0 + i) for i in range(3)]
    records = [_a48_settled(f"A{i}", paid_gbp=2000.0, net_gbp=100.0) for i in range(3)]
    result = method_skill(_a48_run(log, records))
    assert result["concordance"] is None
    assert result["available"] is False
    assert "ranked" in result["reason"]
    assert result["pairs_tied_on_outcome"] == 3


def test_a_decision_with_no_net_margin_is_excluded_and_counted_never_valued_at_zero():
    """The gross line must never silently stand in for the net (R14, and the defect recorded
    against `saas/cost_to_serve.py` where a contribution margin wearing a net margin's name
    valued the entire book). A decision the outcome cannot reach leaves the population and
    says so."""
    log, records = _a48_rising()
    records[0] = dict(records[0], net_margin_gbp=None)
    result = method_skill(_a48_run(log, records))
    assert result["decisions_scored"] == 3
    assert result["decisions_the_outcome_could_not_reach"] == 1


def test_settled_pounds_outside_the_priced_term_never_reach_the_decision():
    """THE TERM BOUNDARY, and the reason `A47`'s year grouping could not be reused.

    MUTATION: move one account's settled row 400 days past its term start — still the same
    CALENDAR grouping would place it against a customer-year, but it belongs to no priced term.
    It must be excluded and counted, and the decision must drop out of the population. If the
    grouping had stayed calendar-year this row would still be scored and the assertion below
    would fail.
    """
    log, records = _a48_rising()
    records[0] = dict(records[0], settlement_date="2023-02-05")
    result = method_skill(_a48_run(log, records))
    assert result["decisions_scored"] == 3
    assert result["settled_rows_outside_every_priced_term"] == 1


def test_both_fuel_legs_fold_onto_the_billing_account_the_decision_priced():
    """The arm prices one renewal for account `C1`; the settled book carries `C1` and `C1g` as
    two fuel legs. Scoring them as two customers would put half an account's pounds against a
    whole account's price.

    EACH LEG IS VALUED AT ITS OWN FUEL'S PUBLISHED RATE, and the arithmetic below is written
    out with both rates rather than one, because valuing gas volumes at the electricity tariff
    overstates the counterfactual roughly four-fold in our favour — the defect
    `tests/company/analytics/test_household_value_share.py::test_gas_volumes_are_never_valued_
    at_the_electricity_tariff` exists to make impossible, arriving here through the fold.
    """
    log = [_a48_priced("C1", 1.0), _a48_priced("D1", 4.0)]
    records = [
        _a48_settled("C1", paid_gbp=2000.0, net_gbp=50.0),
        _a48_settled("C1g", paid_gbp=2000.0, net_gbp=50.0, commodity="gas"),
        _a48_settled("D1", paid_gbp=2000.0, net_gbp=400.0),
    ]
    result = method_skill(_a48_run(log, records))
    assert result["decisions_scored"] == 2
    assert result["accounts"] == 2
    scored = {row["account"]: row for row in result["scored_sample"]}
    # C1's two legs summed: one decision, both legs' pounds behind it, each at its own rate.
    counterfactual = (_CAP_2022 + _GAS_CAP_2022) * 10.0
    assert scored["C1"]["joint_value_ratio"] == pytest.approx(
        (counterfactual - 4000.0 + 100.0) / counterfactual)


def test_method_skill_is_unavailable_with_a_named_reason_rather_than_a_number():
    """Three ways this figure cannot exist, each named. An artefact carrying a bare null here
    would be read as a measurement that came out empty."""
    assert method_skill({"phase2b": {}})["reason"] == (
        "the value arm priced nothing in this run")
    assert "no settlement records" in method_skill(
        _a48_run([_a48_priced("A", 1.0)], []))["reason"]
    assert "declined every renewal" in method_skill(
        {"phase2b": {"value_arm_log": [{"customer_id": "A", "declined": True}],
                     "all_records": [_a48_settled("A", paid_gbp=1.0, net_gbp=1.0)]}})["reason"]


def test_the_bound_and_the_basis_travel_with_the_number():
    """R14 and the FRAME's section 5: the resolution wall is stated BEFORE the figure, not
    discovered by a reader afterwards, and the clock is on the artefact."""
    result = method_skill(_a48_run(*_a48_rising()))
    assert "settled clock" in result["basis"]
    assert "confidence interval" in result["bound"]
    assert "A46" in result["bound"]


# ---------------------------------------------------------------------------
# method_skill.drop_out — the funnel from what the arm PRICED to what is SCORED
# ---------------------------------------------------------------------------
#
# THE DEFECT THESE EXIST FOR (2026-08-30). The live artefact published
# `method_skill.decisions_scored: 6` and `decision_shape.priced: 20` — two counts of one
# subject, on one page, with a single lumped `decisions_the_outcome_could_not_reach: 14`
# between them and no statement of what the 14 were. A reader could not tell whether the
# sample was small because a join failed (ours to widen, today, for free) or because the
# world settled no outcome behind those prices (not widenable at any effort). That
# distinction is the ONLY currently available lever on the 0.133–0.867 null interval, and it
# was unreadable.


def test_the_funnel_from_priced_to_scored_reconciles_or_refuses_to_read_itself():
    """THE CONTROL THAT CAN FAIL, and the reason the class table is a table.

    MUTATION: hand `_skill_drop_out` a drop-out that does not account for every logged
    decision — exactly what a new `continue` added to the scoring loop without a matching
    reason key would produce. The block must say so and WITHHOLD its verdict, because a
    funnel that reads as an account of the gap while being one is worse than no funnel.
    """
    good = rvca._skill_drop_out(4, 3, {"the_priced_term_carried_no_settled_row": 1})
    assert good["reconciles"] is True
    assert "priced decisions" in good["reading"]

    short = rvca._skill_drop_out(4, 3, {})
    assert short["reconciles"] is False
    assert "DOES NOT ADD UP" in short["reading"]
    # AND THE VERDICT IS GONE, not merely accompanied by a warning.
    assert "eligibility the concordance genuinely needs" not in short["reading"]


def test_every_drop_reason_is_reachable_from_the_scoring_loop_and_carries_a_class():
    """R15's parametrised-registry trap, avoided: the membership is pinned LITERALLY here, so
    deleting a reason from `SKILL_DROP_REASONS` leaves this test rather than both sides of it.
    A key with no branch is a reason that can never be reported; a branch with no key is a
    silent drop — and `_skill_drop_out` counts only the keys, so the second one is what would
    break the reconciliation above.
    """
    assert set(rvca.SKILL_DROP_REASONS) == {
        "declined",
        "signal_not_a_number",
        "account_has_no_settled_row_anywhere",
        "the_priced_term_carried_no_settled_row",
        "no_published_counterfactual_rate_for_the_term",
        "a_settled_row_carried_no_net_margin",
        "counterfactual_not_positive",
    }
    for reason, (klass, means) in rvca.SKILL_DROP_REASONS.items():
        assert klass in rvca.SKILL_DROP_CLASSES, reason
        assert len(means) > 40, reason


def test_a_priced_account_the_settled_book_never_carries_is_a_join_not_an_eligibility_rule():
    """THE DISTINCTION THE WHOLE BLOCK EXISTS TO PUBLISH, in the direction that indicts us.

    The arm prices an account the settled records have no row for under any key. That is the
    arm and the world failing to MEET — a defect we can fix — and it must never be reported
    as the concordance declining to score a decision.
    """
    log, records = _a48_rising()
    result = method_skill(_a48_run(log + [_a48_priced("GHOST", 9.0)], records))
    drop = result["drop_out"]
    assert drop["dropped_by_reason"]["account_has_no_settled_row_anywhere"] == 1
    assert drop["dropped_by_class"]["join"] == 1
    assert drop["dropped_by_class"]["eligibility"] == 0
    assert "could be widened here with no world change" in drop["reading"]


def test_an_accounts_only_priced_term_going_empty_is_the_term_boundary_not_a_failed_join():
    """THE MISCLASSIFICATION THIS TEST WAS WRITTEN AFTER MAKING (2026-08-30, in the draft).

    The first cut split "a failed join" from "the term boundary" by asking whether the account
    appeared anywhere in the VALUED VIEW. But the valued view is keyed by account-TERM, so an
    account whose only priced term happens to carry no settled row disappears from it entirely
    and read as a failed join. Every single-term account in the book would have been counted
    as a defect of ours, inflating exactly the number that argues the sample can be widened.

    MUTATION: move the account's only settled row 400 days past its term, so the account still
    settles but no priced term of its own contains anything. The verdict must be eligibility.
    """
    log, records = _a48_rising()
    records[0] = dict(records[0], settlement_date="2023-02-05")
    drop = method_skill(_a48_run(log, records))["drop_out"]
    assert drop["dropped_by_reason"]["the_priced_term_carried_no_settled_row"] == 1
    assert drop["dropped_by_reason"]["account_has_no_settled_row_anywhere"] == 0
    assert drop["dropped_by_class"]["join"] == 0
    assert drop["dropped_by_class"]["eligibility"] == 1


def test_a_missing_net_margin_and_a_missing_counterfactual_are_not_the_same_finding():
    """These were one `blind` flag, so the drop-out could only ever say "the outcome could not
    reach it". They are different things and only one of them is ours: a term with no published
    default-tariff rate is a gap in the series WE sourced (coverage), a term whose settled row
    supplies no net margin is the view refusing to let the gross stand in (eligibility, R14).

    MUTATION: the same account-term, broken each way in turn. The two must not land in one bin.
    """
    log, records = _a48_rising()
    no_net = method_skill(_a48_run(log, [dict(records[0], net_margin_gbp=None)] + records[1:]))
    assert no_net["drop_out"]["dropped_by_reason"]["a_settled_row_carried_no_net_margin"] == 1
    assert no_net["drop_out"]["dropped_by_class"]["coverage"] == 0

    # No published rate reaches this row's own date and fuel, and this is the REAL gap rather
    # than an invented one: the counterfactual falls back to a pre-2019 SVT series that exists
    # for electricity and not for gas, so a gas-only account settling in 2016 has no published
    # default tariff to be measured against. `published_default_tariff(date(2016, 6, 1), "gas")`
    # is None at HEAD. (An unrecognised FUEL would not do: `ofgem_price_cap` raises on one
    # rather than returning None, which is the fail-closed behaviour and not this branch.)
    no_rate = method_skill(_a48_run(
        [_a48_priced("A0", 1.0, term="2016-01-01")] + log[1:],
        [_a48_settled("A0", paid_gbp=2000.0, net_gbp=100.0,
                      on="2016-06-01", commodity="gas")] + records[1:]))
    assert (no_rate["drop_out"]["dropped_by_reason"]
            ["no_published_counterfactual_rate_for_the_term"]) == 1
    assert no_rate["drop_out"]["dropped_by_class"]["coverage"] == 1
    assert no_rate["drop_out"]["dropped_by_class"]["eligibility"] == 0


def test_a_decline_never_enters_the_priced_population_it_is_reported_against():
    """A decline is a decision and is counted, but the funnel's subject is why the PRICED
    population shrank. Counting declines as drop-outs from it would overstate the shrinkage
    and put a decision the arm never priced into the denominator of a coverage claim.
    """
    log, records = _a48_rising()
    drop = method_skill(_a48_run(
        log + [{"customer_id": "Z9", "term_start": _TERM, "declined": True}],
        records))["drop_out"]
    assert drop["decisions_the_arm_logged"] == 5
    assert drop["priced_decisions"] == 4
    assert drop["decisions_scored"] == 4
    assert drop["dropped_by_reason"]["declined"] == 1
    assert sum(drop["dropped_by_class"].values()) == 0
    assert "no join to widen" in drop["reading"]


def test_the_verdict_moves_with_the_counts_rather_than_being_a_constant():
    """R15: a reading that says the same thing whatever the funnel holds is not a reading.

    The same book, one decision broken two different ways, must produce two different
    verdicts — and the all-eligibility one must say the sample CANNOT be widened from this
    book, which is the answer that costs us the argument for a bigger n.
    """
    log, records = _a48_rising()
    records[0] = dict(records[0], settlement_date="2023-02-05")
    eligibility_only = method_skill(_a48_run(log, records))["drop_out"]["reading"]
    joined = method_skill(_a48_run(
        log + [_a48_priced("GHOST", 9.0)], records))["drop_out"]["reading"]
    assert "CANNOT BE WIDENED FROM THIS BOOK" in eligibility_only
    assert "CANNOT BE WIDENED FROM THIS BOOK" not in joined
    assert eligibility_only != joined


def test_the_lumped_count_the_funnel_replaces_still_agrees_with_it():
    """RECONCILIATION BETWEEN THE TWO PUBLISHED FIELDS, not "the answer is N".

    `decisions_the_outcome_could_not_reach` is the figure this artefact carried before the
    funnel existed and consumers still read it. It must equal the funnel's own drop-out less
    declines, forever — if the two ever disagree, one of them is counting a different subject
    and the page would carry both.
    """
    log, records = _a48_rising()
    records[0] = dict(records[0], net_margin_gbp=None)
    records[1] = dict(records[1], settlement_date="2023-02-05")
    result = method_skill(_a48_run(
        log + [{"customer_id": "Z9", "term_start": _TERM, "declined": True}], records))
    drop = result["drop_out"]
    assert result["decisions_the_outcome_could_not_reach"] == (
        drop["decisions_dropped"] - drop["dropped_by_reason"]["declined"])
    assert result["decisions_the_outcome_could_not_reach"] == 2


# ---------------------------------------------------------------------------
# gross_to_net_bridge — the £30,924 that was "observed and unexplained"
# ---------------------------------------------------------------------------
#
# THE DEFECT THESE TESTS EXIST FOR (2026-08-26): the A/B published gross margin FALLING by
# £14,151 while net margin ROSE by £16,773, could attribute £2,591 of the £30,924 gap to bad
# debt, and recorded the rest as unexplained with volume-lost-to-churn offered as an INFERRED
# candidate. Nothing was wrong with the run. The instrument published gross, bad debt and net
# and nothing in between — three of the five lines — so the two largest terms had nowhere to
# appear. These tests hold the bridge to the property that makes it an attribution rather than
# a story: it closes, and when it cannot close it says so instead of absorbing the difference.

def _ledger(rows, churned=(), account_count=12):
    return {"phase2b": {"all_records": list(rows),
                        "churned_billing_accounts": list(churned)},
            "enterprise_value": {"portfolio": {"account_count": account_count}}}


def _elec(customer="C1", *, gross, policy=0.0, network=0.0, capital=0.0, bad_debt=0.0,
          volume=1_000.0, extra=0.0):
    """One electricity row whose net obeys the world's own identity.

    `extra` is a deduction the row really suffers and the bridge has no line for — the
    shape of a cost line added to the world and never added here.
    """
    return {"customer_id": customer, "margin_gbp": gross, "policy_cost_gbp": policy,
            "network_cost_gbp": network, "capital_cost_gbp": capital,
            "bad_debt_gbp": bad_debt, "consumption_kwh": volume,
            "revenue_gbp": gross * 2, "wholesale_cost_gbp": gross,
            "net_margin_gbp": gross - policy - network - capital - bad_debt - extra}


def _gas(customer="C1g", *, gross, policy=0.0, network=0.0, capital=0.0, volume=500.0):
    """A gas row. It books the same economic lines under DIFFERENT KEYS, which is the
    reason `GROSS_TO_NET_LINES` maps a list of fields onto one bridge line."""
    return {"customer_id": customer, "commodity": "gas", "margin_gbp": gross,
            "gas_policy_cost_gbp": policy, "gas_network_cost_gbp": network,
            "capital_cost_gbp": capital, "consumption_kwh": volume,
            "revenue_gbp": gross * 2, "wholesale_cost_gbp": gross,
            "net_margin_gbp": gross - policy - network - capital}


def test_the_bridge_names_the_line_that_moved_and_closes_on_the_net_delta():
    """The whole point: a net delta with a mechanism attached, in named lines with figures."""
    control = _ledger([_elec(gross=5_000.0, policy=100.0, network=200.0,
                             capital=3_000.0, bad_debt=400.0)])
    value = _ledger([_elec(gross=4_800.0, policy=95.0, network=190.0,
                           capital=2_000.0, bad_debt=350.0)])
    bridge = gross_to_net_bridge(control, value)

    assert bridge["reconstruction_closes"] is True
    assert bridge["net_delta_gbp"] == pytest.approx(865.0)
    assert bridge["largest_contribution"] == "capital_cost_gbp"
    contributions = bridge["net_delta_contribution_gbp"]
    assert contributions["capital_cost_gbp"] == pytest.approx(1_000.0)
    assert contributions["gross_margin_gbp"] == pytest.approx(-200.0)
    assert contributions["bad_debt_gbp"] == pytest.approx(50.0)


def test_a_cost_line_the_bridge_does_not_know_about_stops_it_closing():
    """R15 — THE MUTATION THIS CONTROL MUST SURVIVE. `extra` is a real deduction with no
    bridge line, exactly the shape of a cost added to the world and never added here. The
    bridge must refuse to close rather than quietly enlarge one of the lines it does carry:
    an attribution that always adds up is not an attribution, it is arithmetic laundering.

    This is also why the residual is NOT one of the contributions. With it in the sum,
    `reconstructed` reduces to `net_delta` for any set of lines including the empty one, and
    `reconstruction_closes` would be a constant True — the first draft did exactly that."""
    control = _ledger([_elec(gross=5_000.0, capital=1_000.0)])
    value = _ledger([_elec(gross=5_000.0, capital=1_000.0, extra=250.0)])
    bridge = gross_to_net_bridge(control, value)

    assert bridge["reconstruction_closes"] is False
    assert bridge["reconstruction_error_gbp"] == pytest.approx(250.0)
    assert bridge["unexplained_residual_delta_gbp"] == pytest.approx(-250.0)
    assert bridge["value_arm"]["unexplained_residual_gbp"] == pytest.approx(-250.0)


def test_gas_and_electricity_book_the_same_line_under_different_keys_and_are_summed_as_one():
    """Reporting `policy_cost_gbp` alone would show a dual-fuel book's levies as the
    electricity leg's only — half a line, indistinguishable from a small one."""
    control = _ledger([_elec(gross=1_000.0, policy=50.0),
                       _gas(gross=200.0, policy=30.0)])
    value = _ledger([_elec(gross=1_000.0, policy=10.0),
                     _gas(gross=200.0, policy=5.0)])
    bridge = gross_to_net_bridge(control, value)

    assert bridge["control_arm"]["policy_and_levies_gbp"] == pytest.approx(80.0)
    assert bridge["value_arm"]["policy_and_levies_gbp"] == pytest.approx(15.0)
    assert bridge["net_delta_contribution_gbp"]["policy_and_levies_gbp"] == pytest.approx(65.0)
    assert bridge["reconstruction_closes"] is True


def test_gross_falling_while_net_rises_is_reported_as_two_signed_terms_not_one_puzzle():
    """The literal 2026-08-26 shape, at scale: gross down, net up. Both signs survive into
    the output, because a decomposition that only reports the winning line is a headline."""
    control = _ledger([_elec(gross=433_174.76, capital=320_502.33, bad_debt=32_984.26)])
    value = _ledger([_elec(gross=419_023.25, capital=292_168.64, bad_debt=30_393.17)])
    bridge = gross_to_net_bridge(control, value)

    contributions = bridge["net_delta_contribution_gbp"]
    assert contributions["gross_margin_gbp"] < 0
    assert contributions["capital_cost_gbp"] > 0
    assert bridge["net_delta_gbp"] > 0
    assert bridge["reconstruction_closes"] is True


def test_an_arm_with_no_ledger_raises_rather_than_bridging_a_row_of_zeroes():
    """R15 FAIL-OPEN, the pattern `realised_metrics` already refuses at the top level: a
    zero-filled bridge is indistinguishable from a run where every deduction was zero."""
    with pytest.raises(ValueError, match="all_records"):
        gross_to_net_bridge(_ledger([]), _ledger([_elec(gross=1.0)]))


def test_the_bridge_states_the_clock_it_is_measured_on():
    """R14 — no financial figure without its basis, and this publishes five of them."""
    bridge = gross_to_net_bridge(_ledger([_elec(gross=1.0)]), _ledger([_elec(gross=2.0)]))
    assert "SETTLED" in bridge["basis"]
    assert set(bridge["line_definitions"]) == {
        "policy_and_levies_gbp", "network_gbp", "capital_cost_gbp", "bad_debt_gbp"}


# ---------------------------------------------------------------------------
# churn_volume_attribution — a candidate that is allowed to come back negative
# ---------------------------------------------------------------------------

def test_the_churn_candidate_is_confirmed_when_the_lost_accounts_carry_the_gross_fall():
    control = _ledger([_elec("C1", gross=1_000.0), _elec("C2", gross=500.0)])
    value = _ledger([_elec("C1", gross=1_000.0)], churned=["C2"])
    attribution = churn_volume_attribution(control, value)

    assert attribution["differentially_churned_accounts"] == ["C2"]
    assert attribution["gross_delta_gbp"] == pytest.approx(-500.0)
    assert attribution["share_of_gross_delta"] == pytest.approx(1.0)


def test_the_churn_candidate_is_RULED_OUT_when_the_fall_sits_with_everyone_else():
    """The result this function exists to be able to return. `volume lost to the two extra
    churned accounts` was offered as an inferred explanation; measuring it has to be able to
    come back saying no, or measuring it adds nothing over asserting it."""
    control = _ledger([_elec("C1", gross=1_000.0), _elec("C2", gross=10.0)])
    value = _ledger([_elec("C1", gross=600.0)], churned=["C2"])
    attribution = churn_volume_attribution(control, value)

    assert attribution["gross_delta_gbp"] == pytest.approx(-410.0)
    assert attribution["share_of_gross_delta"] == pytest.approx(10.0 / 410.0)
    assert attribution["share_of_gross_delta"] < 0.05


def test_accounts_that_churned_under_BOTH_arms_are_not_differential():
    """A departure both arms suffered explains no delta between them."""
    control = _ledger([_elec("C1", gross=1_000.0)], churned=["C9"])
    value = _ledger([_elec("C1", gross=900.0)], churned=["C9"])
    attribution = churn_volume_attribution(control, value)

    assert attribution["differentially_churned_accounts"] == []
    assert attribution["gross_delta_from_differentially_churned_gbp"] == 0.0


def test_a_dual_fuel_households_two_legs_are_one_churned_billing_account():
    """`_billing_account_id` folds `C1g` into `C1`; splitting the ledger by raw customer id
    would leave the gas leg in `everyone_else` while its own household churned."""
    control = _ledger([_elec("C1", gross=1_000.0), _gas("C1g", gross=200.0)])
    value = _ledger([], churned=["C1"])
    attribution = churn_volume_attribution(control, value)

    assert attribution["control_arm"]["differentially_churned"]["gross_gbp"] == pytest.approx(
        1_200.0)
    assert attribution["control_arm"]["everyone_else"]["gross_gbp"] == 0.0


# ---------------------------------------------------------------------------
# book_identity — WORKER_FINDING_THE_AB_ARTEFACT_CANNOT_NAME_THE_BOOK_IT_RAN_ON
# ---------------------------------------------------------------------------

def test_the_artefact_can_name_its_own_book():
    """Two readings three days apart were each correct about a book the company no longer
    had, and the only way to tell was to compare a commit timestamp to a run timestamp by
    hand. The run now says which book it ran on, in its own output."""
    identity = book_identity(_ledger(
        [_elec("C1", gross=1.0), _gas("C1g", gross=1.0), _elec("C2", gross=1.0)],
        account_count=2), book_at_run())

    assert identity["billing_accounts_settled_in_window"] == 2
    assert identity["served_segments"] == list(served_segments())
    assert identity["with_an_electricity_leg"] == 2
    assert identity["with_a_gas_leg"] == 1
    assert identity["dual_fuel"] == 1
    assert identity["dual_fuel_share_of_accounts"] == pytest.approx(0.5)
    assert identity["accounts_at_end_of_window"] == 2


def test_an_electricity_only_book_is_reported_as_one_rather_than_left_to_inference():
    """The single-fuel book the superseded reading ran on. It must be visibly 0% dual fuel,
    not silently absent — that absence is the whole defect."""
    identity = book_identity(_ledger([_elec("C1", gross=1.0), _elec("C2", gross=1.0)]))
    assert identity["dual_fuel"] == 0
    assert identity["dual_fuel_share_of_accounts"] == 0.0
    assert identity["with_a_gas_leg"] == 0


def test_an_empty_book_reports_an_unavailable_share_rather_than_a_flattering_zero():
    identity = book_identity(_ledger([]))
    assert identity["billing_accounts_settled_in_window"] == 0
    assert identity["dual_fuel_share_of_accounts"] is None


def test_the_book_names_the_segments_it_was_allowed_to_serve(monkeypatch):
    """The population is a FREE VARIABLE of the run — resolved from the curriculum file — and
    until this landed the record of the run did not capture it. A run on the wrong segments
    produced a clean, complete, plausible artefact and no control could fire, which is R15
    FAIL-OPEN one level above R14's clock rule.

    Read from `served_segments()` rather than restated, so the artefact cannot claim a book
    the population was not built from. Monkeypatching the env override is the cheapest proof
    that it is genuinely read per call and not frozen at import."""
    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi")
    identity = book_identity(_ledger([_elec("C1", gross=1.0)]), book_at_run())
    assert identity["served_segments"] == ["resi"]

    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi,SME")
    assert book_identity(
        _ledger([_elec("C1", gross=1.0)]), book_at_run())["served_segments"] == ["resi", "SME"]


def test_an_overridden_book_and_a_curriculum_book_are_DIFFERENT_CLAIMS(monkeypatch):
    """A measurement someone asked for and what the company actually serves are not the same
    statement even when they resolve to the same segments — the finding asked for the override
    recorded separately for that reason. Recording only the resolved list loses which of the
    two a reader is looking at."""
    monkeypatch.delenv("SE_SERVED_SEGMENTS", raising=False)
    from_curriculum = book_at_run()
    assert from_curriculum["resolved_from"] == "curriculum"
    assert from_curriculum["override_env"] is None

    # The override deliberately set to the SAME list the curriculum resolves to. A control that
    # inferred the source from the segments could not tell these two apart — which is the whole
    # point of carrying the raw string.
    monkeypatch.setenv("SE_SERVED_SEGMENTS", ",".join(from_curriculum["served_segments"]))
    overridden = book_at_run()
    assert overridden["served_segments"] == from_curriculum["served_segments"]
    assert overridden["resolved_from"] == "SE_SERVED_SEGMENTS"
    assert overridden["override_env"] == ",".join(from_curriculum["served_segments"])


def test_a_book_the_caller_never_recorded_is_UNAVAILABLE_not_todays_curriculum(monkeypatch):
    """FAIL CLOSED. The tempting repair is to resolve the segments here when the caller passed
    none — and that reports the book at the moment the artefact was assembled, for an arm that
    may have run on a different one. It is also what makes the cross-arm control a tautology:
    every arm gets the same answer from the same call."""
    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi")
    identity = book_identity(_ledger([_elec("C1", gross=1.0)]))

    assert identity["served_segments"] is None
    assert identity["served_segments_resolved_from"] is None
    assert "not known" in identity["served_segments_unavailable_because"]
    # The rest of the block still measures — an unknown population does not void the counts.
    assert identity["billing_accounts_settled_in_window"] == 1


def test_the_arm_reports_the_book_IT_ran_on_and_not_the_one_live_at_assembly(monkeypatch):
    """TAUTOLOGY guard, and the reason the snapshot is taken per arm. The env here says one
    thing and the arm's own record says another; the arm's record must win, or an artefact
    assembled after a curriculum edit relabels every arm with the second book."""
    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi,SME,I&C")
    at_run = {"served_segments": ["resi"], "resolved_from": "curriculum", "override_env": None}

    identity = book_identity(_ledger([_elec("C1", gross=1.0)]), at_run)

    assert identity["served_segments"] == ["resi"]
    assert identity["served_segments_unavailable_because"] is None


# ---------------------------------------------------------------------------
# same_book_across_arms — the population axis of `arm_identity`
# ---------------------------------------------------------------------------

def _book(segments):
    return {"served_segments": list(segments), "resolved_from": "curriculum",
            "override_env": None}


def test_two_arms_on_ONE_book_pass_and_the_verdict_names_the_book():
    out = rvca.same_book_across_arms(
        {"control_arm": _book(["resi", "SME"]), "value_arm": _book(["resi", "SME"])})

    assert out["same_book"] is True
    assert out["arms_compared"] == ["control_arm", "value_arm"]
    assert out["distinct_books"] == [["resi", "SME"]]
    assert out["arms_with_no_recorded_book"] == []


def test_two_arms_on_TWO_books_fail_and_both_books_are_on_the_surface():
    """The defect itself: three readings from this tool on one day, on three books, each
    artefact clean and none of them able to say which. A verdict with no per-arm list would
    tell a reader something is wrong without telling them what."""
    out = rvca.same_book_across_arms(
        {"control_arm": _book(["resi", "SME"]), "value_arm": _book(["resi"])})

    assert out["same_book"] is False
    assert out["distinct_books"] == [["resi"], ["resi", "SME"]]
    assert out["served_segments_by_arm"]["value_arm"] == ["resi"]


def test_a_book_the_same_arms_reached_two_WAYS_is_still_one_book():
    """The other half of the mutation. Compared on the RESOLVED segments, so an env-overridden
    arm and a curriculum arm that serve the same list agree — and the difference the verdict
    ignores is published beside it rather than dropped."""
    overridden = {"served_segments": ["resi", "SME"], "resolved_from": "SE_SERVED_SEGMENTS",
                  "override_env": "resi,SME"}
    out = rvca.same_book_across_arms(
        {"control_arm": _book(["resi", "SME"]), "value_arm": overridden})

    assert out["same_book"] is True
    assert out["resolved_from_by_arm"] == {
        "control_arm": "curriculum", "value_arm": "SE_SERVED_SEGMENTS"}


def test_ONE_arm_cannot_agree_with_itself_so_the_verdict_is_CANNOT_TELL():
    """A pass branch reached by having nothing to compare is not a pass. `True` here would be
    the whole control's fail-open shape: a run that recorded one arm reads as checked."""
    out = rvca.same_book_across_arms({"control_arm": _book(["resi", "SME"])})

    assert out["same_book"] is None
    assert out["arms_compared"] == ["control_arm"]


def test_an_arm_that_recorded_NO_book_makes_the_verdict_CANNOT_TELL_not_TRUE():
    """An unmeasured population is not a matching one — the two recorded arms agreeing must
    not vote down an arm nobody observed."""
    out = rvca.same_book_across_arms(
        {"control_arm": _book(["resi", "SME"]), "value_arm": _book(["resi", "SME"]),
         "level_arm": {}})

    assert out["same_book"] is None
    assert out["arms_with_no_recorded_book"] == ["level_arm"]
    assert out["arms_compared"] == ["control_arm", "value_arm"]


# ---------------------------------------------------------------------------
# bound_attribution — who chose the price, the customer or a bound
# ---------------------------------------------------------------------------
#
# "The advantage must come from INFERENCE, never ACCESS" fails just as completely when the
# advantage comes from a BOUND: a margin pinned to the lawful ceiling is a margin the arm did
# not choose. `decision_shape` counted `ceiling_bound` honestly and left it among fourteen other
# integers, so an artefact in which the price cap set half the arm's answers read exactly like
# one in which it set none of them. This section is the sentence that block could not say, and
# these tests are what stop it becoming a constant.

def _priced(account, *, margin=30.0, ceiling=False, support=False, side="auto",
            term="2020-01-01"):
    return {"customer_id": account, "term_start": term,
            "chosen_margin_gbp_per_mwh": margin,
            "ceiling_bound": ceiling, "extrapolation_bound": support,
            "endpoint_side": ("ceiling" if ceiling else None) if side == "auto" else side}


def _arm_priced(log, lifetimes):
    return {"phase2b": {"value_arm_log": log},
            "per_customer_lifetime": {k: _life(v) for k, v in lifetimes.items()}}


FLAT = {"A": 100.0, "B": 100.0, "C": 100.0, "D": 100.0}


def test_an_arm_whose_answers_were_all_its_own_says_THE_CUSTOMER():
    """The PASS branch, and it has to be reachable or the verdict is a constant reporting
    itself as a measurement (R15's fourth shape)."""
    value = _arm_priced([_priced(a) for a in "ABCD"], dict(FLAT, A=200.0))

    out = bound_attribution(_arm_priced([], FLAT), value)

    assert out["decided_by"] == "the customer"
    assert out["decided_by_the_lawful_ceiling"] == 0
    assert out["decided_by_the_model_support_bound"] == 0
    assert out["chosen_freely"] == 4
    assert out["share_of_priced_decided_by_a_bound"] == 0.0
    assert "decided by the customer" in out["headline"]


def test_an_arm_the_price_cap_decided_says_A_BOUND_and_names_which_one():
    """The measured state on 2026-08-26: 20 of 42 priced renewals at the lawful ceiling. The
    headline must say the cap chose them, not that the arm did."""
    log = [_priced("A", ceiling=True), _priced("B", ceiling=True),
           _priced("C"), _priced("D")]

    out = bound_attribution(_arm_priced([], FLAT), _arm_priced(log, FLAT))

    assert out["decided_by"] == "a bound"
    assert out["decided_by_the_lawful_ceiling"] == 2
    assert out["share_of_priced_decided_by_a_bound"] == 0.5
    assert "2 by the lawful price cap" in out["headline"]
    assert "0 by the frontier" in out["headline"]


def test_the_two_bounds_are_counted_APART_and_never_twice():
    """The ceiling is an external law a real supplier really has; the support bound is this
    company's own ignorance. Reporting them as one number makes those read the same, and a
    decision both bounds reached must not be counted twice."""
    log = [_priced("A", ceiling=True, support=True), _priced("B", support=True),
           _priced("C"), _priced("D")]

    out = bound_attribution(_arm_priced([], FLAT), _arm_priced(log, FLAT))

    assert out["decided_by_the_lawful_ceiling"] == 1
    assert out["decided_by_the_model_support_bound"] == 1
    assert out["chosen_freely"] == 2
    assert (out["decided_by_the_lawful_ceiling"] + out["decided_by_the_model_support_bound"]
            + out["chosen_freely"]) == out["priced"]


def test_a_bound_that_decided_FEW_answers_but_ALL_THE_MONEY_still_says_A_BOUND():
    """THE MUTATION THAT MATTERS. A count-only attribution is blind to exactly the case this
    artefact keeps producing: `margin_movers` has reported 99.4% of the absolute movement on
    fifteen accounts. One capped renewal on the account carrying the delta IS the headline, and
    a section that only counted decisions would call it a footnote."""
    log = [_priced("A", ceiling=True), _priced("B"), _priced("C"), _priced("D")]
    value = _arm_priced(log, dict(FLAT, A=1000.0, B=110.0, C=110.0, D=110.0))

    out = bound_attribution(_arm_priced([], FLAT), value)

    assert out["share_of_priced_decided_by_a_bound"] == 0.25       # a minority of ANSWERS
    money = out["realised_margin_movement"]
    assert money["share_of_absolute_movement_on_those_accounts"] > 0.9
    assert money["net_delta_gbp_on_those_accounts"] == pytest.approx(900.0)
    assert money["net_delta_gbp_elsewhere"] == pytest.approx(30.0)
    assert out["decided_by"] == "a bound"


def test_a_bound_that_decided_few_answers_and_little_money_says_MIXED():
    """The third branch, and it must not collapse into either neighbour: a minority bound is
    neither 'the customer chose' nor 'a bound chose', and saying so is the honest answer."""
    log = [_priced("A", ceiling=True), _priced("B"), _priced("C"), _priced("D")]
    value = _arm_priced(log, dict(FLAT, A=110.0, B=1000.0, C=110.0, D=110.0))

    out = bound_attribution(_arm_priced([], FLAT), value)

    assert out["realised_margin_movement"][
        "share_of_absolute_movement_on_those_accounts"] < 0.05
    assert out["decided_by"] == "mixed"
    assert "decided by mixed" in out["headline"]


def test_the_median_margin_is_split_by_WHO_DECIDED_IT():
    """The diagnostic the whole section exists to expose: if the ceiling-decided median sits
    well above the freely-chosen one, the arm wanted more than the law allows on exactly the
    customers it was stopped on, and the cap — not the churn belief — held the price down."""
    log = [_priced("A", margin=180.0, ceiling=True), _priced("B", margin=190.0, ceiling=True),
           _priced("C", margin=20.0), _priced("D", margin=24.0)]

    medians = bound_attribution(_arm_priced([], FLAT),
                                _arm_priced(log, FLAT))["median_margin_gbp_per_mwh"]

    assert medians["decided_by_the_lawful_ceiling"] == 190.0
    assert medians["chosen_freely"] == 24.0
    assert medians["decided_by_the_model_support_bound"] is None
    assert medians["control"] == TARGET_MARGIN_GBP_PER_MWH


def test_a_ceiling_bound_answer_that_did_NOT_sit_at_the_ceiling_is_visible():
    """A cross-check between two fields computed independently inside `decide_margin`:
    `ceiling_bound` is the shadow score (what it would have chosen with the cap lifted),
    `endpoint_side` is where the winner actually sat. They must agree; a divergence is a defect
    in the search rather than a caveat here, and it has to be countable to be noticed."""
    log = [_priced("A", ceiling=True, side="ceiling"), _priced("B", ceiling=True, side=None)]

    out = bound_attribution(_arm_priced([], FLAT), _arm_priced(log, FLAT))

    assert out["decided_by_the_lawful_ceiling"] == 2
    assert out["ceiling_bound_and_sat_at_that_end"] == 1


def test_declines_are_not_counted_as_answers_a_bound_decided():
    """A decline is a decision and `decision_shape` counts it — but it is not a PRICE, and
    folding it in here would dilute the share of answers a bound chose."""
    log = [_priced("A", ceiling=True), _priced("B", ceiling=True),
           {"customer_id": "C", "declined": True, "reason": "no lawful predictable offer"}]

    out = bound_attribution(_arm_priced([], FLAT), _arm_priced(log, FLAT))

    assert out["priced"] == 2
    assert out["share_of_priced_decided_by_a_bound"] == 1.0


def test_the_control_arm_is_UNAVAILABLE_with_a_reason_rather_than_a_flattering_zero():
    """An arm that priced nothing has no answers to attribute. Reporting `decided_by: the
    customer` there would be a control arm claiming the thesis."""
    out = bound_attribution(_arm_priced([], FLAT), _arm_priced([], FLAT))

    assert out["available"] is False
    assert "priced no renewal" in out["why_not"]
    assert "decided_by" not in out


def test_the_headline_is_COMPUTED_and_moves_with_the_run():
    """A stored sentence describes whichever run wrote it. This one is rebuilt from the counts
    every time, so it cannot outlive them."""
    few = bound_attribution(_arm_priced([], FLAT),
                            _arm_priced([_priced("A", ceiling=True)] + [_priced(a) for a in "BCD"],
                                        FLAT))["headline"]
    many = bound_attribution(_arm_priced([], FLAT),
                             _arm_priced([_priced(a, ceiling=True) for a in "ABCD"],
                                         FLAT))["headline"]

    assert "1 of 4 priced renewals (25%)" in few
    assert "4 of 4 priced renewals (100%)" in many
    assert few != many


def test_the_section_refuses_to_recommend_moving_the_ceiling():
    """R12/R13 in the artefact's own words. The one repair this finding must never propose is
    the one that makes the number go away, and the artefact is where a later reader looks."""
    out = bound_attribution(_arm_priced([], FLAT),
                            _arm_priced([_priced("A", ceiling=True)], FLAT))

    assert out["what_would_change_this"].startswith("NOT moving the ceiling")
    assert "cite a published source" in out["what_would_change_this"]
    assert "blind to what it does to this delta" in out["what_would_change_this"]


# ---------------------------------------------------------------------------
# cross_section_reconciliation — why the two artefacts' endpoint counts differ
# ---------------------------------------------------------------------------

SHAPE = {"priced": 42, "declined": 8, "endpoint_bound": 20, "endpoint_at_ceiling": 20,
         "endpoint_at_floor": 0, "extrapolation_bound": 2}


def _arms_artefact(tmp_path, monkeypatch, payload):
    path = tmp_path / "value_based_pricing_arms.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(rvca, "ARMS_ARTEFACT", path)
    return path


def test_the_two_populations_are_NAMED_rather_than_left_to_be_inferred(tmp_path, monkeypatch):
    """The reading that prompted this, on 2026-08-26: interior optima on 255 of 263 accounts
    against 20 of 42 priced renewals at the ceiling, taken as contradicting each other. They are
    two questions put to one module over different populations under different bounds, and both
    answers are correct."""
    _arms_artefact(tmp_path, monkeypatch, {
        "endpoint_bound": 19, "endpoint_at_ceiling": 1, "endpoint_at_floor": 18,
        "extrapolation_bound": 0,
        "population": {"unit": "one renewal decision per ACCOUNT, taken at a single moment",
                       "as_of_year": 2025, "decisions": 397, "distinct_accounts": 397,
                       "priced_under_a_lawful_ceiling": 0, "lawful_ceiling_passed": False,
                       "what_endpoint_at_ceiling_means": "the top of the candidate grid"},
    })

    out = rvca.cross_section_reconciliation(SHAPE)

    assert out["available"] is True
    assert out["cross_section"]["decisions"] == 397
    assert out["cross_section"]["lawful_ceiling_passed"] is False
    assert out["this_run"]["decisions"] == 42
    assert out["this_run"]["lawful_ceiling_passed"] is True
    differences = {d["difference"] for d in out["the_three_differences"]}
    assert differences == {"population", "ceiling", "conditions"}
    measured = " ".join(d["measured"] for d in out["the_three_differences"])
    assert "397" in measured and "42" in measured and "2025" in measured


def test_a_low_ceiling_count_taken_without_a_ceiling_is_not_read_as_evidence(tmp_path,
                                                                            monkeypatch):
    """The specific misreading. Where no ceiling is passed `ceiling_bound` cannot fire at all,
    so the cross-section's near-zero count is not evidence that the cap does not bind."""
    _arms_artefact(tmp_path, monkeypatch, {
        "endpoint_at_ceiling": 1,
        "population": {"decisions": 397, "distinct_accounts": 397, "as_of_year": 2025,
                       "priced_under_a_lawful_ceiling": 0, "lawful_ceiling_passed": False,
                       "unit": "per ACCOUNT", "what_endpoint_at_ceiling_means": "grid top"},
    })

    ceiling = [d for d in rvca.cross_section_reconciliation(SHAPE)["the_three_differences"]
               if d["difference"] == "ceiling"][0]

    assert "priced 0 of 397" in ceiling["measured"]
    assert "not evidence that the cap does not bind" in ceiling["measured"]


def test_a_STALE_arms_artefact_is_refused_rather_than_reconciled_against(tmp_path, monkeypatch):
    """FAIL-LOUD, not fail-open. An artefact predating the `population` block does not say which
    ceiling its counts were taken under — reconciling against it would assume the very thing the
    two files were read as disagreeing about."""
    _arms_artefact(tmp_path, monkeypatch, {"endpoint_at_ceiling": 1, "accounts_priced": 397})

    out = rvca.cross_section_reconciliation(SHAPE)

    assert out["available"] is False
    assert "predates the `population` block" in out["why_not"]
    assert "couple_value_based_pricing" in out["why_not"]


def test_a_MISSING_arms_artefact_says_so_instead_of_omitting_the_section(tmp_path, monkeypatch):
    monkeypatch.setattr(rvca, "ARMS_ARTEFACT", tmp_path / "nothing.json")

    out = rvca.cross_section_reconciliation(SHAPE)

    assert out["available"] is False
    assert "has not been generated" in out["why_not"]


def test_an_UNREADABLE_arms_artefact_is_a_failed_check_not_a_passed_one(tmp_path, monkeypatch):
    """R15 FAIL-SILENT: a checker that cannot run has not passed."""
    path = tmp_path / "value_based_pricing_arms.json"
    path.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(rvca, "ARMS_ARTEFACT", path)

    out = rvca.cross_section_reconciliation(SHAPE)

    assert out["available"] is False
    assert "unreadable" in out["why_not"]


def test_the_reconciliation_does_not_claim_to_settle_the_customer_level_question(tmp_path,
                                                                                monkeypatch):
    """Both figures being explicable is not both being flattering. Interior on the cross-section
    and ceiling-bound here are consistent AND both say the optimum lies above what the company
    may lawfully charge."""
    _arms_artefact(tmp_path, monkeypatch, {
        "population": {"decisions": 397, "distinct_accounts": 397, "as_of_year": 2025,
                       "priced_under_a_lawful_ceiling": 0, "lawful_ceiling_passed": False,
                       "unit": "per ACCOUNT", "what_endpoint_at_ceiling_means": "grid top"}})

    out = rvca.cross_section_reconciliation(SHAPE)

    assert "open either way" in out["what_this_does_NOT_reconcile"]
    assert "bound_attribution.what_would_change_this" in out["what_this_does_NOT_reconcile"]


# ── A48: how wide is the null? ────────────────────────────────────────────────────────────────
#
# The point null (a constant signal scores exactly 0.5) proves the estimator is not broken. It
# says NOTHING about whether an observed value is distinguishable from a random signal at the
# sample size actually available. The first live reading was 0.6136 on 12 decisions -- a value a
# random signal reaches about one time in six.
#
# THE FIRST VERSION USED KENDALL'S UNTIED CLOSED FORM AND REFUSED ON TIES, and its first live
# application refused: the arm priced 25 renewals at 24 distinct margins, so a tied signal pair is
# the NORMAL case. A bound that refuses on the data it was built for is not a bound. It permutes
# the observed signal values now, which reproduces the tie structure by construction.

def _rising(n=12, tie=False):
    """n points whose signal ranks the outcome perfectly; optionally with one tied signal pair."""
    pts = [(float(i), float(i)) for i in range(n)]
    if tie:
        pts[1] = (pts[0][0], pts[1][1])
    return pts


def _shuffled_signal(n=12, seed=7):
    import random as _r
    rng = _r.Random(seed)
    signals = list(range(n))
    rng.shuffle(signals)
    return [(float(s), float(i)) for i, s in enumerate(signals)]


def test_the_permuted_null_matches_the_closed_form_when_there_are_no_ties():
    """INDEPENDENCE (R15). Kendall's untied null gives sd = sqrt(2(2n+5)/(9n(n-1)))/2 = 0.1105 at
    n=12. The published spread is a permutation, a completely different method, so agreeing with
    the closed form on the case the closed form covers is what stops it being one unverified
    reading.

    Fires on: permuting the wrong thing (outcomes instead of signals), too few draws, or a
    concordance that is not the statistic the null is drawn for.
    """
    import math

    pts = _shuffled_signal()
    observed, _, _ = _concordance(pts)
    out = concordance_null_spread(pts, observed)
    closed = math.sqrt(2.0 * (2.0 * 12 + 5.0) / (9.0 * 12 * 11)) / 2.0
    assert out["available"] is True
    assert out["null_mean"] == pytest.approx(0.5, abs=0.01), "the null is not centred on 0.5"
    assert out["null_sd"] == pytest.approx(closed, abs=0.01), (
        "permuted sd {:.4f} disagrees with the closed form {:.4f}".format(out["null_sd"], closed))


def test_a_TIED_signal_gets_a_spread_instead_of_a_refusal():
    """THE DEFECT THE LIVE RUN FOUND. The closed-form version refused here, and this is the
    ordinary case: 24 distinct margins across 25 priced renewals.

    Fires on: reverting to a formula that cannot take ties, which withholds the figure forever on
    the only data it will ever see.
    """
    pts = _rising(tie=True)
    observed, _, _ = _concordance(pts)
    out = concordance_null_spread(pts, observed)
    assert out["available"] is True, out.get("reason")
    assert out["signal_ties_in_the_observed_data"] == 1
    assert 0.0 < out["null_sd"] < 0.5


def test_the_null_is_deterministic():
    """A seeded permutation must give the same artefact twice, or a re-run differs from its own
    record for a reason no reader could tell from a real change."""
    pts = _rising(tie=True)
    observed, _, _ = _concordance(pts)
    first = concordance_null_spread(pts, observed)
    second = concordance_null_spread(pts, observed)
    assert first["null_sd"] == second["null_sd"]
    assert first["null_95_interval"] == second["null_95_interval"]
    assert first["p_two_sided"] == second["p_two_sided"]


def test_too_few_decisions_refuse_rather_than_returning_a_wide_interval():
    """Fires on: returning an interval for two points, which has no sampling distribution and
    would render as a very tolerant result rather than as no result."""
    for n in (0, 1, 2):
        out = concordance_null_spread(_rising(n) if n else [], 0.9)
        assert out["available"] is False
        assert "no sampling distribution" in out["reason"]


def test_one_outcome_for_every_decision_is_undefined_not_wide():
    """FAIL-OPEN killer at the degenerate end. If every decision shares an outcome, no permutation
    of the signal can rank anything -- and a very wide interval would read as a tolerant result
    rather than as no result at all."""
    out = concordance_null_spread([(float(i), 1.0) for i in range(12)], 0.5)
    assert out["available"] is False
    assert "no permutation of the signal can rank anything" in out["reason"]


def test_the_spread_can_also_say_DISTINGUISHABLE():
    """The control must fire in BOTH directions, or it is a machine for calling every result null.
    A perfectly ranking signal on 12 points is far outside the null."""
    pts = _rising()
    observed, _, _ = _concordance(pts)
    out = concordance_null_spread(pts, observed)
    assert observed == pytest.approx(1.0)
    assert out["observed_inside_the_null_interval"] is False
    assert out["p_two_sided"] < 0.01
    assert "OUTSIDE the interval" in out["reading"]


def test_the_null_narrows_as_decisions_accumulate():
    """The bound is a statement about sample size, so it must respond to sample size."""
    sds = []
    for n in (12, 40, 120):
        pts = _shuffled_signal(n, seed=n)
        observed, _, _ = _concordance(pts)
        sds.append(concordance_null_spread(pts, observed, draws=4000)["null_sd"])
    assert sds[0] > sds[1] > sds[2]


# ── the artefact carries the code that made it, resolved at PROCESS START ─────────────────────


def test_the_producing_commit_is_bound_at_import_not_at_assembly():
    """THE MECHANISM, and the only property that distinguishes this from a `git rev-parse` at the
    write site -- which is what both previous repairs amounted to and what both of them missed.

    A run takes an hour and fifty minutes; this tree lands population changes about every forty.
    So a sha read at ASSEMBLY names the tree the artefact was WRITTEN by, which is precisely the
    tree that did NOT draw its book. Python binds a module's code at import, so the import-time
    constant is the only moment in the process that answers the question actually being asked.

    Fires on: calling `current_head()` inside `producing_commit()`. The head is moved AFTER
    import here -- exactly what a concurrent lane landing a commit mid-run does -- and the stamp
    must not follow it.

    THE PATCH IS ON `rvca.current_head`, NOT ON `background.boot_sha.current_head`, and the first
    draft of this test got that wrong and passed against the mutation. `run_value_cycle_ab` does
    `from background.boot_sha import current_head`, so it holds its OWN reference; rebinding the
    name in the defining module leaves the caller's copy untouched and the control sees nothing.
    A control that cannot observe its own mutation is the tautology R15 names, and this one was
    established by running the mutation rather than by reading the code.
    """
    bound_at_import = rvca.PRODUCING_COMMIT
    original = rvca.current_head
    try:
        rvca.current_head = lambda: "d" * 40              # the tree moves under the run
        stamp = rvca.producing_commit()
    finally:
        rvca.current_head = original

    assert stamp["commit"] == bound_at_import, (
        "the stamp followed the tree instead of the process -- it is being resolved at assembly, "
        "which names the code that WROTE the artefact rather than the code that made its numbers")
    assert stamp["commit"] != "d" * 40


def test_every_artefact_this_runner_writes_carries_the_same_stamp():
    """One shape, one answer. A consumer meets `producing_commit.commit` or its absence, never
    three spellings of the same fact.

    Fires on: stamping one artefact and not the others; on a per-call resolution that could give
    two artefacts of one process two different shas.
    """
    assert rvca.producing_commit() == rvca.producing_commit()
    assert set(rvca.producing_commit()) >= {
        "commit", "resolved_at", "resolved_when", "unavailable_because"}


def test_a_run_that_cannot_reach_git_states_the_absence_rather_than_a_placeholder():
    """FAIL-CLOSED. `commit: None` WITH the reason -- never "", never "unknown", never the
    assembly tree's sha.

    A consumer that cannot tell "no commit" from "some commit" is the fail-open shape this field
    replaces, and a wrong sha is worse here than an admitted absence: the whole use of the field
    is to let a reader tell the producing tree from the publishing one.

    Fires on: defaulting the constant to `""`; on dropping `unavailable_because`.
    """
    original = rvca.PRODUCING_COMMIT
    try:
        rvca.PRODUCING_COMMIT = None
        stamp = rvca.producing_commit()
    finally:
        rvca.PRODUCING_COMMIT = original

    assert stamp["commit"] is None
    assert stamp["unavailable_because"]
    assert "cannot name the code" in stamp["unavailable_because"]
    # AND THE HEALTHY CASE STILL SAYS NOTHING, so `unavailable_because` is a signal and not decor.
    if original:
        assert rvca.producing_commit()["unavailable_because"] is None


# ─────────────────────────────────────────────────────────────────────────────────────────────
# ONE WORLD ACROSS EVERY LEG, OR NO DECOMPOSITION
#
# THE DEFECT (filed as `c30b98048`, 2026-08-31): "the bound that decided 'cannot resolve' was
# measured in another world, and the new one is wider". A variance measured over one departure
# level is not a component of a variance measured over another, so legs from two worlds do not
# partition anything and their ratio is not a reconciliation -- it is two unrelated numbers
# divided. `decompose_floor` already refuses legs that do not name their own HALF; this is the
# same refusal for the world, and it is the stronger of the two.
#
# R15 -- the mutations, each run and reverted:
#   * drop the `unstamped` check -> `test_legs_that_cannot_name_their_world_are_refused` reds.
#     Every floor artefact on disk today is unstamped, so this is the live branch.
#   * compare `len(set(...)) > 1` on a set built from `.get("digest", "same")` -> the same test
#     reds, because a default collapses two unknowns into one agreement.


def _floor_leg(mode, values, world="w-live"):
    leg = {"redraw_scope": {"mode": mode},
           "seeds": [{"seed": 11111 + i, "selection_gbp": v} for i, v in enumerate(values)]}
    if world is not None:
        leg["world_identity"] = {"digest": world, "unavailable_because": None}
    return leg


def _three_arm_leg(world="w-live"):
    leg = {
        "level_vs_selection": {"selection_gbp": 1500.0},
        "renewal_funnel": {"value_arm": {"priced": 20, "renewals_the_world_offered": 1369}},
    }
    if world is not None:
        leg["world_identity"] = {"digest": world, "unavailable_because": None}
    return leg


def test_legs_that_cannot_name_their_world_are_refused():
    """An unstamped leg must not be assumed to share the others' world.

    Unknown provenance on a bound reads as fine unless something says otherwise (FAIL-SILENT),
    and every floor artefact written before 2026-09-03 is in exactly this state -- so this is the
    live branch, not an edge case.

    Fires on: dropping the check, or defaulting a missing digest to a shared sentinel.
    """
    split = rvca.decompose_floor(
        _floor_leg("all", [1.0, 2.0, 3.0], world=None),
        _floor_leg("only", [1.0, 2.0, 3.5]),
        _floor_leg("except", [1.0, 1.1, 1.2]),
        _three_arm_leg())
    assert split["available"] is False
    assert "do not say which world they ran in" in split["why_not"]
    assert "undecomposed" in split["why_not"], split["why_not"]


def test_legs_from_two_worlds_do_not_partition_one_call_stream():
    """A reconciliation across two worlds is two unrelated numbers divided.

    Fires on: comparing anything other than the legs' world digests, or reporting the ratio
    anyway with a caveat -- a caveat under a published ratio is not a refusal.
    """
    split = rvca.decompose_floor(
        _floor_leg("all", [1.0, 2.0, 3.0]),
        _floor_leg("only", [1.0, 2.0, 3.5], world="w-OLD"),
        _floor_leg("except", [1.0, 1.1, 1.2]),
        _three_arm_leg())
    assert split["available"] is False
    assert "different worlds" in split["why_not"]
    assert "w-OLD" in split["why_not"] and "w-live" in split["why_not"]


def test_one_world_across_every_leg_decomposes_and_is_stamped():
    """THE PASS BRANCH, driven explicitly so the refusal above is a reading and not a constant.

    The composed artefact carries the world its legs AGREED on -- not the world of the process
    that assembled it, which ran nothing and whose level may differ from the one every figure
    was measured over.

    Fires on: refusing legs that do share a world; or stamping the decomposition at write time.
    """
    split = rvca.decompose_floor(
        _floor_leg("all", [1.0, 2.0, 3.0]),
        _floor_leg("only", [1.0, 2.0, 3.5]),
        _floor_leg("except", [1.0, 1.1, 1.2]),
        _three_arm_leg())
    assert split["available"] is True, split.get("why_not")
    assert split["world_identity"]["digest"] == "w-live"
    assert sorted(split["world_identity"]["agreed_across_legs"]) == [
        "except", "only", "three_arm", "undecomposed"]


# ---------------------------------------------------------------------------
# A REFUSED FLOOR RUN LEAVES THE REFUSAL WHERE THE FLOOR WOULD HAVE BEEN
#
# `floor_run_headroom_refusal` was landed on 2026-09-03 because the undecomposed leg was
# OOM-killed at 1h 09m and wrote nothing. The filed reason was not the lost hour: it was that "an
# absent artefact reads exactly like a run still in progress". The refusal removed the OOM as a
# CAUSE of that absence and left the absence itself -- `print(...); return 2` writes no file. These
# legs are driven through `main()` on purpose. A refusal wired into the helper and not into the
# entry point is this repo's filed FAIL-OPEN shape, and asserting on `floor_refusal_artefact`
# alone would pass while `main` still returned 2 in silence.
# ---------------------------------------------------------------------------


def _refuse_floor(monkeypatch, reason="no headroom on this guest"):
    """Force the refusal branch without needing a machine that is actually short of memory."""
    monkeypatch.setattr(rvca, "floor_run_headroom_refusal", lambda *a, **k: reason)
    monkeypatch.setattr(rvca, "noise_floor", _never_runs)


def _never_runs(*args, **kwargs):
    raise AssertionError("the floor run must not start once the headroom check has refused it")


def test_a_REFUSED_floor_run_writes_the_refusal_where_the_artefact_would_have_been(
        tmp_path, monkeypatch):
    """The defect: refused and still-running are the same thing on disk.

    Fires on: `main` returning 2 without writing; on writing somewhere other than `--out`, which
    would leave the path the next session looks at still absent.
    """
    out = tmp_path / "value_cycle_ab_s1_noise_floor_20260903.json"
    _refuse_floor(monkeypatch)

    rc = rvca.main(["--level-arm", "--noise-floor-seeds", "11111,22222,33333",
                    "--redraw-mode", "all", "--out", str(out)])

    assert rc == 2
    assert out.exists(), "the refusal left the path absent, which reads as a run still in progress"
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["available"] is False
    assert written[rvca.FLOOR_REFUSAL_MARKER] is True
    assert "no headroom on this guest" in written["why_not"], (
        "the refusal must carry the reason it refused, not merely that it did")


def test_the_refusal_carries_NO_generated_at_so_nothing_reads_it_as_a_fresh_floor(
        tmp_path, monkeypatch):
    """`generated_at` is what every consumer keys freshness off.

    A refusal stamped with it would be the NEWEST artefact on disk and the most misleading, because
    nothing was measured. Fires on: adding `generated_at` to the refusal artefact.
    """
    out = tmp_path / "floor.json"
    _refuse_floor(monkeypatch)
    rvca.main(["--noise-floor-seeds", "11111", "--out", str(out)])

    written = json.loads(out.read_text(encoding="utf-8"))
    assert "generated_at" not in written
    assert written["refused_at"], "the refusal still has to say WHEN it refused"


def test_a_refusal_NEVER_overwrites_a_floor_run_that_succeeded(tmp_path, monkeypatch):
    """These legs are re-run at the same `--out` across worlds.

    A refused re-run that clobbered the good floor would fail the page closed for a reason that has
    nothing to do with the figures -- the overwrite class already filed against this repo's capture
    tooling. Fires on: writing the refusal unconditionally.
    """
    out = tmp_path / "floor.json"
    real = {"generated_at": "2026-09-03T12:00:00Z",
            "selection_gbp_spread": {"stdev": 3776.27, "n": 3}}
    out.write_text(json.dumps(real), encoding="utf-8")
    _refuse_floor(monkeypatch)

    assert rvca.main(["--noise-floor-seeds", "11111", "--out", str(out)]) == 2
    assert json.loads(out.read_text(encoding="utf-8")) == real, (
        "a refusal replaced a measured floor with its own excuse")


def test_a_refusal_MAY_replace_an_earlier_refusal(tmp_path, monkeypatch):
    """THE PASS BRANCH, so the no-clobber leg above is a reading and not a constant verdict.

    Fires on: a guard keyed to the path existing at all, which would make the first refusal
    permanent and every later one silent.
    """
    out = tmp_path / "floor.json"
    out.write_text(json.dumps(rvca.floor_refusal_artefact("an earlier refusal")),
                   encoding="utf-8")
    _refuse_floor(monkeypatch, reason="the reason this time")

    rvca.main(["--noise-floor-seeds", "11111", "--out", str(out)])

    assert "the reason this time" in json.loads(out.read_text(encoding="utf-8"))["why_not"]


def test_an_artefact_that_cannot_be_read_is_not_overwritten(tmp_path, monkeypatch):
    """Fail closed: if we cannot SHOW it is a refusal, it may be a measurement.

    Fires on: treating an unparseable file as clobberable, which is the flattering assumption.
    """
    out = tmp_path / "floor.json"
    out.write_text("{not json", encoding="utf-8")
    _refuse_floor(monkeypatch)

    rvca.main(["--noise-floor-seeds", "11111", "--out", str(out)])

    assert out.read_text(encoding="utf-8") == "{not json"


def test_the_refusal_artefact_is_refused_by_the_decomposition_rather_than_split(tmp_path,
                                                                               monkeypatch):
    """The refusal must not become a leg. It names a world, so the world check alone passes it.

    Fires on: a refusal shaped so `decompose_floor` reads it as a floor with a zero spread, which
    would publish a decomposition off a run that never happened.
    """
    monkeypatch.setattr(rvca, "world_identity", lambda: {"digest": "w-live"})
    refusal = rvca.floor_refusal_artefact("no headroom")

    split = rvca.decompose_floor(refusal, _floor_leg("only", [1.0, 2.0, 3.5]),
                                 _floor_leg("except", [1.0, 1.1, 1.2]), _three_arm_leg())

    assert split["available"] is False
    assert split["why_not"]
