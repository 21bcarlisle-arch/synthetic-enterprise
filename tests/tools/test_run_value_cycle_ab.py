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

import pytest

from simulation.live_population import served_segments
from tools.run_value_cycle_ab import (
    REPORTED_BASIS,
    SETTLED_BASIS,
    belief_vs_outcome,
    book_identity,
    churn_roster_diff,
    churn_volume_attribution,
    gross_to_net_bridge,
    margin_movers,
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
    phase2b = {
        "total_net": 1_000.0, "total_gross": 5_000.0, "total_bad_debt": 10.0,
        "total_capital": 40.0,
        "final_treasury": 1_250.0, "churned_billing_accounts": ["A"],
        "value_arm_log": [{}, {}],
    }
    phase2b.update(overrides)
    return {"phase2b": phase2b,
            "enterprise_value": {"portfolio": {"enterprise_value_gbp": 900.0,
                                               "account_count": 12}}}


def test_realised_metrics_reports_what_the_world_did():
    metrics = realised_metrics(_full_arm())
    assert metrics["total_net_gbp"] == 1_000.0
    assert metrics["total_gross_margin_gbp"] == 5_000.0
    assert metrics["churned_accounts"] == 1
    assert metrics["renewals_priced_by_the_arm"] == 2


@pytest.mark.parametrize("missing", ["total_net", "total_gross", "total_bad_debt",
                                     "total_capital", "final_treasury"])
def test_a_missing_figure_raises_rather_than_reporting_zero(missing):
    """R15 FAIL-SILENT, and it has already happened once: `.get(key, 0.0)` reported £0
    revenue for BOTH arms, identically, so the delta was a clean zero and nothing looked
    wrong. A metric that cannot find its own figure has to say so."""
    arm = _full_arm()
    del arm["phase2b"][missing]
    with pytest.raises(KeyError, match=missing):
        realised_metrics(arm)


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
        account_count=2))

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
    """The population is a FREE VARIABLE of the run — resolved from the curriculum file at
    import time — and until this landed the record of the run did not capture it. A run on
    the wrong segments produced a clean, complete, plausible artefact and no control could
    fire, which is R15 FAIL-OPEN one level above R14's clock rule.

    Read from `served_segments()` rather than restated, so the artefact cannot claim a book
    the population was not built from. Monkeypatching the env override is the cheapest proof
    that it is genuinely read per call and not frozen at import."""
    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi")
    identity = book_identity(_ledger([_elec("C1", gross=1.0)]))
    assert identity["served_segments"] == ["resi"]

    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi,SME")
    assert book_identity(_ledger([_elec("C1", gross=1.0)]))["served_segments"] == ["resi", "SME"]
