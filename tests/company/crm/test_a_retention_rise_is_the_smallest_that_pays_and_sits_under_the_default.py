"""C35's second shape of share: a monthly rise on the renewal fix, the smallest that brings our side
to zero, capped by the headroom under the published default.

Inputs are §4's constructed cases (`docs/market_research/a_retention_price_that_shares_the_value_an_action_creates.md`),
not estimates of the world. Mutations observed on 2026-10-17, each applied in place and reverted:

  * the cap check removed (`if rise > headroom` before the search)  -> 2 red, the cap tests
  * the search starts at zero AND the loop drops its held arm       -> 3 red, the shed test among them
  * the household floor removed (`kept < 0.0` never true)           -> 2 red, the household tests
  * the slope arm dropped from the search loop                      -> 3 red, the smallest-rise test among them

Starting at zero alone leaves the shed test green, and that is an equivalence: the loop's held arm
is a second leg of the same guard. It reds only the cap tests, because the refusal then names the
search, not the cap.
"""
from __future__ import annotations

import dataclasses

import pytest

from company.crm.next_best_action import (
    AccountState,
    Action,
    ActionEstimate,
    RenewalTerms,
    RetentionRise,
    decide,
    price_retention_rise,
    value_change,
)
from company.policy.decision_policy import CURRENT_POLICY

H = 48
T = Action.TARIFF_ADVICE
ON = dataclasses.replace(CURRENT_POLICY, name="rise_on", next_best_action_shares_by_retention_rise=True)


def advice(gives_up, hazard_cut):
    return ActionEstimate(T, gives_up * 12.0, -gives_up, -hazard_cut)


def terms(headroom_gbp_per_month, annual_mwh=3.6):
    return RenewalTerms(100.0, 100.0 + headroom_gbp_per_month * 12.0 / annual_mwh, annual_mwh)


def state(margin, hazard, renewal=None, estimates=()):
    return AccountState("a", margin, hazard, 0, tuple(estimates), renewal=renewal)


def ours(s, e, rise, slope):
    return value_change(s, ActionEstimate(e.action, e.customer_benefit_gbp_per_year,
                                          e.margin_change_gbp_per_month + rise,
                                          e.hazard_change_per_month + slope * rise), H)


def test_the_rise_is_the_smallest_penny_that_clears_both_arms():
    # §4 row (5, 0.5%, 2, 0.1pt): 1.89 with the hazard held, 2.28 with the published slope.
    s, e = state(5.0, 0.005), advice(2.0, 0.001)
    rise, why = price_retention_rise(s, e, terms(50.0), H)
    assert why == "" and rise.rise_gbp_per_month == pytest.approx(2.28)
    assert ours(s, e, 2.28, 0.0015) >= 0.0 and ours(s, e, 2.28, 0.0) >= 0.0
    assert ours(s, e, 2.27, 0.0015) < 0.0
    assert rise.value_change_gbp == pytest.approx(ours(s, e, 2.28, 0.0015))


def test_a_rise_above_the_headroom_under_the_default_is_refused():
    # §4 row (5, 3%, 3, 0.3pt) needs 2.73 held; a stayer declines a fix dearer than the default.
    s, e = state(5.0, 0.03), advice(3.0, 0.003)
    assert price_retention_rise(s, e, terms(3.5), H)[0] is not None
    rise, why = price_retention_rise(s, e, terms(2.0), H)
    assert rise is None and "above the headroom under the default" in why


def test_a_rise_that_pays_only_by_shedding_a_loss_making_account_is_not_a_share():
    # Margin below zero: a dearer price drives the account away, which flatters our side at a
    # smaller rise than the one that pays on the months it stays.
    s, e = state(-1.0, 0.04), advice(0.5, 0.0)
    assert ours(s, e, 0.3, 0.0015 * 40) >= 0.0  # the shedding route exists at a steep slope
    rise, _ = price_retention_rise(s, e, terms(50.0), H, slope_per_gbp_year=0.0015 * 40)
    assert rise is not None and rise.rise_gbp_per_month >= 0.5
    assert ours(s, e, rise.rise_gbp_per_month, 0.0) >= 0.0


def test_a_rise_that_takes_more_than_the_advice_gives_is_refused():
    # §4 row (15, 0.5%, 3, 0.3pt): the rise needed with the slope takes more than the advice saves.
    rise, why = price_retention_rise(state(15.0, 0.005), advice(3.0, 0.003), terms(50.0), H)
    assert rise is None and "more than the advice gives the household" in why


def test_no_published_default_fails_closed_and_says_why():
    t = RenewalTerms(100.0, None, 3.6)
    rise, why = price_retention_rise(state(5.0, 0.005), advice(2.0, 0.001), t, H)
    assert rise is None and "no published default" in why


def _book():
    cases = [(5.0, 0.005, 2.0, 0.001, 50.0), (5.0, 0.03, 3.0, 0.003, 2.0),
             (15.0, 0.005, 3.0, 0.003, 50.0), (0.7, 0.04, 2.0, 0.003, 3.0),
             (30.0, 0.005, 2.0, 0.001, 50.0)]
    return [AccountState(f"a{i}", m, h, 0, (advice(g, c),), renewal=terms(room))
            for i, (m, h, g, c, room) in enumerate(cases)]


def test_off_the_switch_changes_no_decision():
    for s in _book():
        bare = dataclasses.replace(s, renewal=None)
        off = decide(s, H)
        assert off == decide(s, H, policy=CURRENT_POLICY) == decide(bare, H, policy=ON)
        assert off.action is Action.NOTHING


def test_on_the_switch_takes_a_rise_and_refuses_one_on_the_cap():
    decisions = [decide(s, H, policy=ON) for s in _book()]
    taken = [d for d in decisions if isinstance(d.share, RetentionRise)]
    assert taken and all(d.action is T and d.value_change_gbp >= 0.0
                         and d.customer_benefit_gbp_per_year >= 0.0 for d in taken)
    refusals = [why for d in decisions for _, why in d.unscored]
    assert any("above the headroom" in w for w in refusals)
    assert any("more than the advice gives" in w for w in refusals)
