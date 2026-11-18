"""The 0.30 churn-belief cutoff is skipped where the save-odds weighing carries the belief.

Defect named: a renewal under the fixed cutoff never reaches the value test, so a policy that
weighs belief x save rate x value protected still loses every offer a lower-level belief moves
under 0.30 (`THE_VALUE_TEST_REDESIGN.md` §12c: 9 of 10 value-arm flips). Knowledge:
`docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md` §11.
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
    CONSIDERED_ON_THE_SAVE_ODDS,
    CONSIDERED_OVER_THE_BELIEF_THRESHOLD,
    NOT_CONSIDERED_UNDER_THE_BELIEF_THRESHOLD,
    retention_considers_the_renewal,
)
from company.policy.decision_policy import CURRENT_POLICY, DecisionPolicy


def _learned_fix_ledger():
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    for i in range(40):
        acct = f"F-{i}"
        ledger.observe_ending_term(2017, ENDING_TERM_FIXED, acct, 0.5)
        ledger.observe_retention_offer(2017, ENDING_TERM_FIXED, acct, 0.5)
        if i < 2:
            ledger.observe_competitive_loss(2017, account_id=acct)
    return ledger


def _considers(belief, skip, kind=ENDING_TERM_FIXED, year=2018):
    return retention_considers_the_renewal(belief, threshold=0.30, skip_threshold=skip,
                                           ending_term_type=kind, renewal_year=year)


def test_every_branch_of_the_selection_can_be_taken():
    """One control over the whole partition. Reds if the switch stops letting an under-cutoff
    renewal through on a learned rate, if it lets one through on an unlearned rate (the weighing
    then carries no belief), or if the cutoff stops admitting what is over it."""
    with pressure_ledger_scope(_learned_fix_ledger()):
        over = _considers(0.36, skip=False)
        under_off = _considers(0.12, skip=False)
        under_on_learned = _considers(0.12, skip=True)
        under_on_unlearned_type = _considers(0.12, skip=True, kind=ENDING_TERM_DEFAULT)
        under_on_unclosed_year = _considers(0.12, skip=True, year=2017)
    assert over == (True, CONSIDERED_OVER_THE_BELIEF_THRESHOLD)
    assert under_off == (False, NOT_CONSIDERED_UNDER_THE_BELIEF_THRESHOLD)
    assert under_on_learned == (True, CONSIDERED_ON_THE_SAVE_ODDS)
    for refused, why in (under_on_unlearned_type, under_on_unclosed_year):
        assert refused is False and why.startswith(NOT_CONSIDERED_UNDER_THE_BELIEF_THRESHOLD + ": ")
        assert "no closed" in why
    assert _considers(0.12, skip=True)[0] is False  # no ledger in scope names itself too
    assert "no pressure ledger" in _considers(0.12, skip=True)[1]


def test_the_run_loop_gates_the_offer_on_the_selection_not_on_a_bare_threshold():
    """Read from the run loop's syntax tree: no `> RETENTION_THRESHOLD` comparison is left, and the
    selection is called with the policy's switch."""
    tree = ast.parse(inspect.getsource(run_phase2b))
    bare = [n for n in ast.walk(tree) if isinstance(n, ast.Compare)
            and any(getattr(c, "id", None) == "RETENTION_THRESHOLD" for c in n.comparators)]
    assert bare == []
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "id", None) == "retention_considers_the_renewal"]
    assert len(calls) == 1
    skip = {k.arg: k.value for k in calls[0].keywords}["skip_threshold"]
    assert getattr(skip, "attr", None) == "retention_skips_the_belief_threshold_when_save_odds_weigh"


def test_the_switch_is_off_on_the_standing_policy_and_refused_without_the_weighing():
    field = "retention_skips_the_belief_threshold_when_save_odds_weigh"
    assert {f.name: f.default for f in dataclasses.fields(DecisionPolicy)}[field] is False
    assert getattr(CURRENT_POLICY, field) is False
    alone = dataclasses.replace(CURRENT_POLICY, renewal_belief_by_ending_term=True, **{field: True})
    with pytest.raises(ValueError, match="retention_weighs_save_odds off"):
        run_phase2b._refuse_save_odds_with_no_ending_term(alone)
    run_phase2b._refuse_save_odds_with_no_ending_term(
        dataclasses.replace(alone, retention_weighs_save_odds=True))
