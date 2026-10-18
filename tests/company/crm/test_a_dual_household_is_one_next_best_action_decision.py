"""A dual-fuel household reaching C35 on one renewal date is one decision, not two.

The defect this guards: decided per leg, a household is charged one rise on each fuel against one
advice benefit, and each leg reports the household as keeping some of it while the two rises
together take more than the advice gives
(`docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md`
§8). The legs below are the published probe's medians (electricity GBP 1.17 a month on 3.03 MWh,
gas GBP 1.85 on 11.5 MWh) and the C35 page's first advice effect.

NAMED MUTATION: in `household_state`, replace `sum(leg.monthly_margin_gbp for leg in legs)` with
`first.monthly_margin_gbp`. Then `test_on_the_household_is_charged_one_rise_it_can_afford` goes red,
because the merged decision prices one leg and its rise no longer matches the household's.
"""
from __future__ import annotations

import dataclasses

import pytest

from company.crm.next_best_action import (
    AccountState,
    Action,
    ActionEstimate,
    HouseholdRenewalTerms,
    RenewalTerms,
    decide,
    states_for_decision,
)
from company.policy.decision_policy import CURRENT_POLICY

H = 48
HAZARD = 0.01
ADVICE = (ActionEstimate(Action.TARIFF_ADVICE, 24.0, -2.0, -0.001),)
RISE_ON = dataclasses.replace(CURRENT_POLICY, next_best_action_shares_by_retention_rise=True)
PER_HOUSEHOLD = dataclasses.replace(RISE_ON, next_best_action_decides_per_household=True)
ELEC = AccountState("C1", 1.17, HAZARD, 0, ADVICE, (), RenewalTerms(200.0, 215.0, 3.03))
GAS = AccountState("C1", 1.85, HAZARD, 0, ADVICE, (), RenewalTerms(50.0, 55.0, 11.5))
SINGLE = AccountState("C5", 1.17, HAZARD, 0, ADVICE, (), RenewalTerms(200.0, 215.0, 3.03))


def _rises(states, policy):
    return [decide(s, H, policy).share for s in states_for_decision(states, policy)]


def test_the_switch_is_off_on_every_standing_policy_and_off_returns_the_legs_untouched():
    assert CURRENT_POLICY.next_best_action_decides_per_household is False
    legs = [ELEC, GAS, SINGLE]
    assert states_for_decision(legs, RISE_ON) == legs
    assert all(a is b for a, b in zip(states_for_decision(legs, RISE_ON), legs))
    assert states_for_decision(legs, None) == legs


def test_both_branches_are_reachable_and_they_disagree():
    """The partition first: a dual household decides twice off and once on, a single leg once both ways."""
    off, on = _rises([ELEC, GAS, SINGLE], RISE_ON), _rises([ELEC, GAS, SINGLE], PER_HOUSEHOLD)
    assert len(off) == 3 and len(on) == 2 and all(r is not None for r in off + on)


def test_off_the_household_pays_two_rises_for_one_benefit():
    """The defect, kept visible: each leg's rise is affordable alone and the pair is not."""
    first, second = _rises([ELEC, GAS], RISE_ON)
    benefit = ADVICE[0].customer_benefit_gbp_per_year * H / 12.0
    assert first.customer_benefit_kept_gbp > 0.0 and second.customer_benefit_kept_gbp > 0.0
    paid = (benefit - first.customer_benefit_kept_gbp) + (benefit - second.customer_benefit_kept_gbp)
    assert paid > benefit


def test_on_the_household_is_charged_one_rise_it_can_afford():
    (rise,) = _rises([ELEC, GAS], PER_HOUSEHOLD)
    assert rise.rise_gbp_per_month == pytest.approx(2.15)
    assert 0.0 < rise.customer_benefit_kept_gbp < ADVICE[0].customer_benefit_gbp_per_year * H / 12.0
    assert rise.headroom_gbp_per_month == pytest.approx((15.0 * 3.03 + 5.0 * 11.5) / 12.0)


def test_the_merged_headroom_is_unknown_if_either_legs_is():
    no_default = dataclasses.replace(GAS, renewal=RenewalTerms(50.0, None, 11.5))
    (merged,) = states_for_decision([ELEC, no_default], PER_HOUSEHOLD)
    assert isinstance(merged.renewal, HouseholdRenewalTerms)
    assert merged.renewal.headroom_gbp_per_month() is None
    decision = decide(merged, H, PER_HOUSEHOLD)
    assert decision.share is None and any("headroom" in why for _, why in decision.unscored)


@pytest.mark.parametrize("other, reason", [
    (dataclasses.replace(GAS, monthly_departure_hazard=0.02), "two departure hazards"),
    (dataclasses.replace(GAS, estimates=()), "different action estimates"),
    (dataclasses.replace(GAS, renewal=None), "one leg renews and another does not"),
])
def test_legs_that_are_not_one_decision_are_refused_with_the_reason(other, reason):
    with pytest.raises(ValueError, match=reason):
        states_for_decision([ELEC, other], PER_HOUSEHOLD)
