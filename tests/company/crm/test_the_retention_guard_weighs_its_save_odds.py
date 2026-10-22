"""The retention guard weighs its own save odds: belief x save rate x value protected, against cost.

Defect named: the save rate is learned but never reaches the offer decision (the guard keeps
offering every cut it sizes, prereg §7), or it is learned from P(stay | offered), which counts
every household that would have stayed anyway. Knowledge: `docs/market_research/
a_save_offer_against_the_switching_rules_and_the_seam.md` §9. Prereg §13.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect

import pytest

import simulation.run_phase2b as run_phase2b
from company.crm.churn_desk import ENDING_TERM_DEFAULT, ENDING_TERM_FIXED
from company.crm.competitive_pressure import CompetitivePressureLedger, pressure_ledger_scope
from company.interfaces.growth_desk import (
    book_retention_offer,
    retention_value_weighed_by_save_odds,
)
from company.policy.decision_policy import CURRENT_POLICY, DecisionPolicy


def _offers(ledger, kind, year, n, lost, belief=0.4):
    for i in range(n):
        acct = f"{kind}-{year}-{i}"
        ledger.observe_ending_term(year, kind, acct, belief)
        ledger.observe_retention_offer(year, kind, acct, belief)
        if i < lost:
            ledger.observe_competitive_loss(year, account_id=acct)


def _armed():
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    return ledger


def test_the_save_rate_is_one_minus_observed_over_expected_on_offered_accounts_only():
    ledger = _armed()
    _offers(ledger, ENDING_TERM_FIXED, 2017, 20, 2)  # belief 0.4 -> 8 expected, 2 lost
    # A loss from an account we never offered is not evidence about offers.
    ledger.observe_ending_term(2017, ENDING_TERM_FIXED, "NOT-OFFERED", 0.4)
    ledger.observe_competitive_loss(2017, account_id="NOT-OFFERED")
    rate, why = ledger.retention_save_rate(ENDING_TERM_FIXED, 2018)
    assert rate == pytest.approx(1.0 - ((2 + 0.5) / 21) / 0.4)
    assert "2 losses against 8.00 predicted on 20" in why


def test_only_closed_years_teach_and_a_new_roll_closes_the_old_offer():
    ledger = _armed()
    _offers(ledger, ENDING_TERM_FIXED, 2018, 10, 0)
    assert ledger.retention_save_rate(ENDING_TERM_FIXED, 2018)[0] is None
    # Offered in 2017, rolled again in 2018 with no offer, lost in 2018: not the offer's loss.
    ledger.observe_ending_term(2017, ENDING_TERM_FIXED, "R", 0.4)
    ledger.observe_retention_offer(2017, ENDING_TERM_FIXED, "R", 0.4)
    ledger.observe_ending_term(2018, ENDING_TERM_FIXED, "R", 0.4)
    ledger.observe_competitive_loss(2018, account_id="R")
    assert ledger.retention_offer_sums[(ENDING_TERM_FIXED, 2017)]["losses"] == 0


def test_the_save_rate_refuses_with_its_reason_and_never_reads_below_zero():
    unarmed = CompetitivePressureLedger()
    assert unarmed.retention_save_rate(ENDING_TERM_FIXED, 2019) == (
        None, "departures are not being reported to this ledger")
    ledger = _armed()
    _offers(ledger, ENDING_TERM_FIXED, 2017, 10, 9, belief=0.3)  # lost more than predicted
    assert ledger.retention_save_rate(ENDING_TERM_FIXED, 2018)[0] == 0.0
    rate, why = ledger.retention_save_rate(ENDING_TERM_DEFAULT, 2018)
    assert rate is None and "no closed retention offers" in why


def test_the_weighing_can_refuse_can_offer_and_can_fall_back():
    """One control over the whole partition: a guard that refuses everything, or weighs nothing,
    fails one of the three legs. Reds if the save rate stops reaching the value weighed."""
    cost = 10.0
    ledger = _armed()
    _offers(ledger, ENDING_TERM_FIXED, 2017, 40, 2, belief=0.5)   # high save rate
    _offers(ledger, ENDING_TERM_DEFAULT, 2017, 40, 30, belief=0.5)  # none saved
    with pressure_ledger_scope(ledger):
        offer, s_fix, _ = retention_value_weighed_by_save_odds(
            100.0, belief=0.5, ending_term_type=ENDING_TERM_FIXED, renewal_year=2018)
        refuse, s_def, _ = retention_value_weighed_by_save_odds(
            100.0, belief=0.5, ending_term_type=ENDING_TERM_DEFAULT, renewal_year=2018)
        fall_back, s_none, why = retention_value_weighed_by_save_odds(
            100.0, belief=0.5, ending_term_type=ENDING_TERM_FIXED, renewal_year=2017)
    assert offer == pytest.approx(0.5 * s_fix * 100.0) and offer > cost
    assert s_def == 0.0 and refuse < cost
    assert s_none is None and fall_back == 100.0 and "no closed" in why
    assert {offer > cost, refuse > cost} == {True, False}


def test_an_offer_booked_through_the_door_reaches_the_ledger():
    ledger = _armed()
    with pressure_ledger_scope(ledger):
        book_retention_offer(renewal_year=2017, ending_term_type=ENDING_TERM_FIXED,
                             account_id="D", belief=0.6)
    assert ledger.retention_offer_sums[(ENDING_TERM_FIXED, 2017)] == {"n": 1, "sp": 0.6, "losses": 0}


def test_the_run_loop_hands_the_weighed_value_to_the_offer_decision_and_books_the_offer():
    """The chain, read from the run loop's own syntax tree (a comment cannot satisfy it): the
    guard's `_value_protected` is reassigned from the weighing, and the offer is booked."""
    tree = ast.parse(inspect.getsource(run_phase2b))
    weighed = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)
               and isinstance(n.value, ast.Call)
               and getattr(n.value.func, "id", None) == "retention_value_weighed_by_save_odds"
               and isinstance(n.targets[0], ast.Tuple)
               and n.targets[0].elts[0].id == "_value_protected"]
    assert len(weighed) == 1
    booked = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
              and getattr(n.func, "id", None) == "book_retention_offer"]
    assert len(booked) == 1


def test_the_switch_is_off_on_the_standing_policy_and_refused_without_the_ending_term_type():
    default = {f.name: f.default for f in dataclasses.fields(DecisionPolicy)}
    assert default["retention_weighs_save_odds"] is False
    assert CURRENT_POLICY.retention_weighs_save_odds is False
    alone = dataclasses.replace(CURRENT_POLICY, retention_weighs_save_odds=True)
    with pytest.raises(ValueError, match="renewal_belief_by_ending_term off"):
        run_phase2b._refuse_save_odds_with_no_ending_term(alone)
    run_phase2b._refuse_save_odds_with_no_ending_term(
        dataclasses.replace(alone, renewal_belief_by_ending_term=True))
