"""The retention guard offers only where the lower bound of its save rate's interval pays.

Defect named: the guard offers on a save rate it cannot tell from zero. On §15's holdout the
offered group lost 26 of 62 and the holdout 8 of 21, and every offer's money landed on a stayer
(M2: transfer). A point estimate floored at 0 says nothing about how wide the doubt is, and an
unlearned rate fell back to the standing guard, which offers. Knowledge: `docs/market_research/
a_save_offer_against_the_switching_rules_and_the_seam.md` §9f. Prereg §16.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect
import math

import pytest

import simulation.run_phase2b as run_phase2b
from company.crm.churn_desk import ENDING_TERM_FIXED
from company.crm.competitive_pressure import CompetitivePressureLedger, pressure_ledger_scope
from company.interfaces.growth_desk import (
    SAVE_RATE_INTERVAL_INCLUDES_ZERO,
    SAVE_RATE_LOWER_BOUND_DOES_NOT_PAY,
    SAVE_RATE_NOT_LEARNED,
    retention_value_at_save_rate_lower_bound,
)
from company.policy.decision_policy import CURRENT_POLICY, DecisionPolicy


def _ledger(held=None, offered=None):
    """A holdout ledger with 2017's closed groups as (n, lost)."""
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    ledger.arm_save_holdout()
    for tag, group, observe in (("H", held, ledger.observe_retention_holdout),
                                ("O", offered, ledger.observe_retention_offer)):
        if group is None:
            continue
        n, lost = group
        for i in range(n):
            acct = f"{tag}-{i}"
            ledger.observe_ending_term(2017, ENDING_TERM_FIXED, acct, 0.5)
            observe(2017, ENDING_TERM_FIXED, acct, 0.5)
            if i < lost:
                ledger.observe_competitive_loss(2017, account_id=acct)
    return ledger


def _decide(ledger, *, value=1000.0, cost=50.0, belief=0.5):
    with pressure_ledger_scope(ledger):
        return retention_value_at_save_rate_lower_bound(
            value, belief=belief, ending_term_type=ENDING_TERM_FIXED, renewal_year=2018,
            offer_cost=cost)


def test_the_whole_partition_is_reachable_and_each_part_decides_as_named():
    """The one control over the partition: an offer where the lower bound pays, none where the
    interval includes zero, none while the rate is unlearned, and none where the bound is above
    zero but too low to pay. Asserted reachable together, so a guard that refuses everything
    reds here."""
    pays = _decide(_ledger(held=(21, 15), offered=(62, 10)))
    includes_zero = _decide(_ledger(held=(21, 8), offered=(62, 26)))  # §15's own counts
    unlearned = _decide(_ledger(offered=(62, 26)))
    too_low = _decide(_ledger(held=(21, 15), offered=(62, 10)), cost=400.0)

    value, interval, refusal, _ = pays
    assert refusal is None and interval[1] > 0.0
    assert value == pytest.approx(0.5 * interval[1] * 1000.0) and value > 50.0
    assert includes_zero[0] is None and includes_zero[2] == SAVE_RATE_INTERVAL_INCLUDES_ZERO
    assert includes_zero[1][1] <= 0.0 < includes_zero[1][2]
    assert unlearned[0] is None and unlearned[1] is None
    assert unlearned[2] == SAVE_RATE_NOT_LEARNED and "(0 held out, 62 offered)" in unlearned[3]
    assert too_low[0] is None and too_low[2] == SAVE_RATE_LOWER_BOUND_DOES_NOT_PAY
    assert {pays[2], includes_zero[2], unlearned[2], too_low[2]} == {
        None, SAVE_RATE_INTERVAL_INCLUDES_ZERO, SAVE_RATE_NOT_LEARNED,
        SAVE_RATE_LOWER_BOUND_DOES_NOT_PAY}


def test_the_bound_is_the_lower_one_not_the_point():
    """A point that pays with a lower bound that does not must refuse: the guard reads the bound."""
    ledger = _ledger(held=(21, 15), offered=(62, 10))
    point, lower, _ = ledger.retention_save_rate_interval(ENDING_TERM_FIXED, 2018)[0]
    cost = 0.5 * 1000.0 * (point + lower) / 2  # between what the bound and the point would pay
    assert _decide(ledger, cost=cost)[2] == SAVE_RATE_LOWER_BOUND_DOES_NOT_PAY


def test_the_interval_is_katz_on_the_jeffreys_proportions():
    """Printed at §15's counts and by hand: Katz's log interval on o/h, 95%."""
    (point, lower, upper), why = _ledger(held=(21, 8), offered=(62, 26)).retention_save_rate_interval(
        ENDING_TERM_FIXED, 2018)
    h, o = 8.5 / 22, 26.5 / 63
    se = math.sqrt((1 - o) / (63 * o) + (1 - h) / (22 * h))
    assert point == pytest.approx(1 - o / h)
    assert lower == pytest.approx(1 - (o / h) * math.exp(1.959964 * se))
    assert upper == pytest.approx(1 - (o / h) * math.exp(-1.959964 * se))
    assert (round(point, 3), round(lower, 3), round(upper, 3)) == (-0.089, -0.986, 0.403)
    assert "holdout lost 8 of 21" in why and "95% interval" in why
    # More of the same evidence narrows it: the width is earned by the counts, not picked.
    wide = _ledger(held=(21, 15), offered=(62, 10)).retention_save_rate_interval(
        ENDING_TERM_FIXED, 2018)[0]
    narrow = _ledger(held=(210, 150), offered=(620, 100)).retention_save_rate_interval(
        ENDING_TERM_FIXED, 2018)[0]
    assert narrow[2] - narrow[1] < wide[2] - wide[1]


def test_no_interval_without_a_holdout():
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    interval, why = ledger.retention_save_rate_interval(ENDING_TERM_FIXED, 2018)
    assert interval is None and "no holdout" in why


def test_the_switch_is_off_on_the_standing_policy_and_refused_without_the_holdout():
    default = {f.name: f.default for f in dataclasses.fields(DecisionPolicy)}
    assert default["retention_offers_on_the_save_rate_lower_bound"] is False
    assert CURRENT_POLICY.retention_offers_on_the_save_rate_lower_bound is False
    alone = dataclasses.replace(CURRENT_POLICY, renewal_belief_by_ending_term=True,
                                retention_weighs_save_odds=True,
                                retention_offers_on_the_save_rate_lower_bound=True)
    with pytest.raises(ValueError, match="retention_save_rate_learned_against_holdout off"):
        run_phase2b._refuse_save_odds_with_no_ending_term(alone)
    run_phase2b._refuse_save_odds_with_no_ending_term(
        dataclasses.replace(alone, retention_save_rate_learned_against_holdout=True))


def test_the_run_loop_asks_the_bound_before_the_holdout_coin_and_the_offer():
    """Read from the run loop's syntax tree: the lower-bound door is asked ahead of the coin and of
    the offer's booking, so a refusal reaches the value test before anything is offered."""
    tree = ast.parse(inspect.getsource(run_phase2b))
    lines = {n.func.id: n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "id", None) in ("retention_value_at_save_rate_lower_bound",
                                                  "retention_save_holdout_draws",
                                                  "book_retention_offer")}
    assert lines["retention_value_at_save_rate_lower_bound"] < lines[
        "retention_save_holdout_draws"] < lines["book_retention_offer"]
