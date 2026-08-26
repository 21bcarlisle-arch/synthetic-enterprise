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

from tools.run_value_cycle_ab import (
    REPORTED_BASIS,
    SETTLED_BASIS,
    churn_roster_diff,
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
                                     "final_treasury"])
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
