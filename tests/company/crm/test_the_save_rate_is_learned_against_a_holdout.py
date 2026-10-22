"""The save rate is learned against the company's own holdout, not against its belief.

Defect named: the held-out renewals' losses stop reaching `retention_save_rate`, so the rate reads
the offered accounts alone and a belief that under-reads its tail passes for a save rate (prereg
§13: the rate read 0.19 while the world kept 0 of 32). Knowledge: `docs/market_research/
a_save_offer_against_the_switching_rules_and_the_seam.md` §9e. Prereg §15.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect

import pytest

import simulation.run_phase2b as run_phase2b
from company.crm.churn_desk import ENDING_TERM_FIXED
from company.crm.competitive_pressure import (
    SAVE_HOLDOUT_SHARE,
    CompetitivePressureLedger,
    pressure_ledger_scope,
    save_holdout_draws,
    save_holdout_share,
)
from company.interfaces.growth_desk import book_retention_holdout, retention_save_holdout_draws
from company.policy.decision_policy import CURRENT_POLICY, DecisionPolicy


def _group(ledger, observe, tag, year, n, lost, belief=0.4):
    for i in range(n):
        acct = f"{tag}-{year}-{i}"
        ledger.observe_ending_term(year, ENDING_TERM_FIXED, acct, belief)
        observe(year, ENDING_TERM_FIXED, acct, belief)
        if i < lost:
            ledger.observe_competitive_loss(year, account_id=acct)


def _holdout_ledger():
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    ledger.arm_save_holdout()
    return ledger


def test_the_holdouts_losses_reach_the_save_rate():
    """The control the item names: the same offered group reads a different save rate as the
    holdout's losses change, and exactly (h - o) / h."""
    rates = {}
    for held_lost in (2, 8):
        ledger = _holdout_ledger()
        _group(ledger, ledger.observe_retention_offer, "O", 2017, 20, 4)
        _group(ledger, ledger.observe_retention_holdout, "H", 2017, 10, held_lost)
        rate, why = ledger.retention_save_rate(ENDING_TERM_FIXED, 2018)
        h, o = (held_lost + 0.5) / 11, (4 + 0.5) / 21
        assert rate == pytest.approx(max(0.0, (h - o) / h))
        assert f"holdout lost {held_lost} of 10" in why and "offered lost 4 of 20" in why
        rates[held_lost] = rate
    assert rates[8] > rates[2] > 0.0


def test_the_belief_no_longer_enters_once_the_holdout_is_armed():
    readings = set()
    for belief in (0.2, 0.7):
        ledger = _holdout_ledger()
        _group(ledger, ledger.observe_retention_offer, "O", 2017, 20, 4, belief)
        _group(ledger, ledger.observe_retention_holdout, "H", 2017, 10, 5, belief)
        readings.add(round(ledger.retention_save_rate(ENDING_TERM_FIXED, 2018)[0], 12))
    assert len(readings) == 1


def test_it_refuses_with_its_reason_until_both_groups_have_closed_renewals():
    ledger = _holdout_ledger()
    _group(ledger, ledger.observe_retention_offer, "O", 2017, 20, 4)
    rate, why = ledger.retention_save_rate(ENDING_TERM_FIXED, 2018)
    assert rate is None and "(0 held out, 20 offered)" in why
    _group(ledger, ledger.observe_retention_holdout, "H", 2018, 10, 9)
    assert ledger.retention_save_rate(ENDING_TERM_FIXED, 2018)[0] is None  # 2018 not closed
    assert ledger.retention_save_rate(ENDING_TERM_FIXED, 2019)[0] > 0.0
    # Offers that lose MORE than the holdout save nothing, never a negative rate.
    worse = _holdout_ledger()
    _group(worse, worse.observe_retention_offer, "O", 2017, 10, 9)
    _group(worse, worse.observe_retention_holdout, "H", 2017, 10, 1)
    assert worse.retention_save_rate(ENDING_TERM_FIXED, 2018)[0] == 0.0


def test_a_new_roll_closes_the_held_out_renewal():
    ledger = _holdout_ledger()
    ledger.observe_ending_term(2017, ENDING_TERM_FIXED, "R", 0.4)
    ledger.observe_retention_holdout(2017, ENDING_TERM_FIXED, "R", 0.4)
    ledger.observe_ending_term(2018, ENDING_TERM_FIXED, "R", 0.4)
    ledger.observe_competitive_loss(2018, account_id="R")
    assert ledger.retention_holdout_sums[(ENDING_TERM_FIXED, 2017)]["losses"] == 0


def test_the_doors_arm_the_ledger_and_book_the_holdout():
    ledger = CompetitivePressureLedger()
    with pressure_ledger_scope(ledger):
        retention_save_holdout_draws("A", "2017-03-01")
        book_retention_holdout(renewal_year=2017, ending_term_type=ENDING_TERM_FIXED,
                               account_id="A", belief=0.6)
    assert ledger.save_holdout_armed
    assert ledger.retention_holdout_sums[(ENDING_TERM_FIXED, 2017)] == {
        "n": 1, "sp": 0.6, "losses": 0}


def test_the_coin_can_hold_out_and_can_offer_at_about_the_derived_share():
    draws = [save_holdout_draws(f"ACC-{i}", "2017-06-01") for i in range(4000)]
    assert any(draws) and not all(draws)
    assert sum(draws) / len(draws) == pytest.approx(SAVE_HOLDOUT_SHARE, abs=0.03)
    assert draws == [save_holdout_draws(f"ACC-{i}", "2017-06-01") for i in range(4000)]


def test_the_share_is_derived_and_falls_back_to_the_even_split_when_a_year_cannot_resolve_it():
    # §9e's inputs give about 0.27; more offers need a smaller holdout; too few, the even split.
    assert SAVE_HOLDOUT_SHARE == pytest.approx(0.272, abs=0.002)
    assert save_holdout_share(300, 34 / 83, 0.83) < SAVE_HOLDOUT_SHARE < 0.5
    assert save_holdout_share(40, 34 / 83, 0.83) == 0.5


def test_the_run_loop_books_the_holdout_and_withholds_its_offer():
    """Read from the run loop's syntax tree: the holdout branch books through the door and sits
    ahead of the branch that makes the offer, so a held-out renewal is never also offered."""
    tree = ast.parse(inspect.getsource(run_phase2b))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "id", None) in ("book_retention_holdout",
                                                  "retention_save_holdout_draws",
                                                  "book_retention_offer")]
    lines = {n.func.id: n.lineno for n in calls}
    assert len(calls) == 3
    assert lines["retention_save_holdout_draws"] < lines["book_retention_holdout"] < lines[
        "book_retention_offer"]


def test_the_switch_is_off_on_the_standing_policy_and_refused_without_the_guard_it_feeds():
    default = {f.name: f.default for f in dataclasses.fields(DecisionPolicy)}
    assert default["retention_save_rate_learned_against_holdout"] is False
    assert CURRENT_POLICY.retention_save_rate_learned_against_holdout is False
    alone = dataclasses.replace(CURRENT_POLICY, renewal_belief_by_ending_term=True,
                                retention_save_rate_learned_against_holdout=True)
    with pytest.raises(ValueError, match="retention_weighs_save_odds off"):
        run_phase2b._refuse_save_odds_with_no_ending_term(alone)
    run_phase2b._refuse_save_odds_with_no_ending_term(
        dataclasses.replace(alone, retention_weighs_save_odds=True))
