"""A household leaving with both fuels is answered once, on both legs (fuel page §8a).

The defect kept visible with the switch off: of a dual household's two loss notices the company
answers one, sized on that fuel alone, against a gap Ofgem measures on the dual-fuel bill.

Inputs are the published 2019-Q2 record (`published_default_rate_ex_vat`, `published_best_deal_gap
_share`): electricity 176.8 and gas 39.4 GBP/MWh ex VAT, gap 0.298. The renewals, floors and volumes
are illustrative, at the scale of the live book's median legs (3 and 11.5 MWh).

Named mutation: in `household_save_rates`, `headroom >= 0.0` -> `all(match[leg.supply_point_id] >=
leg.cost_floor for leg in legs)` (the per-leg floor). Run 2026-10-18: it turns
`test_on_one_leg_may_sit_under_its_floor_when_the_household_keeps_a_margin` and the partition
control red (2 failed, 9 passed), and was restored.
"""
from __future__ import annotations

import dataclasses

import pytest

from company.crm.save_offer import (
    SaveLeg,
    household_save_rates,
    price_match_save_rate,
    save_rates_for_decision,
)
from company.policy.decision_policy import CURRENT_POLICY

GAP = 0.298
ON = dataclasses.replace(CURRENT_POLICY, save_offer_decides_per_household=True)


def _legs(elec_floor: float = 115.0, gas_floor: float = 30.0) -> tuple[SaveLeg, SaveLeg]:
    return (SaveLeg("X", 165.0, 176.8, elec_floor, 3.0),
            SaveLeg("Xg", 36.0, 39.4, gas_floor, 11.5))


def test_the_switch_stands_off_on_the_standing_policy():
    assert CURRENT_POLICY.save_offer_decides_per_household is False


def test_the_partition_off_answers_one_notice_on_answers_both_and_every_branch_is_reachable():
    """One control over the whole partition: off answers the decision leg only; on answers both;
    and on reaches each of its three answers (matched, floored, none)."""
    off = save_rates_for_decision(_legs(), GAP, CURRENT_POLICY)
    on = save_rates_for_decision(_legs(), GAP, ON)
    _, matched = household_save_rates(_legs(), GAP)
    _, floored = household_save_rates(_legs(elec_floor=140.0), GAP)
    none, nothing = household_save_rates(_legs(), 0.0)
    assert set(off) == {"X"} and set(on) == {"X", "Xg"}
    assert matched.startswith("matched") and floored.startswith("floored") and none is None, (
        matched, floored, nothing)


def test_off_is_the_per_leg_price_match_exactly():
    """Off is today's answer, byte for byte, across floors either side of the match."""
    for floor in (100.0, 124.0, 124.2, 140.0, 170.0):
        legs = _legs(elec_floor=floor)
        expected = price_match_save_rate(165.0, 176.8, GAP, floor)
        assert save_rates_for_decision(legs, GAP, CURRENT_POLICY) == (
            {} if expected is None else {"X": expected})
        assert save_rates_for_decision(legs, GAP, None) == save_rates_for_decision(
            legs, GAP, CURRENT_POLICY)


def test_on_one_leg_may_sit_under_its_floor_when_the_household_keeps_a_margin():
    rates, reason = household_save_rates(_legs(), GAP)
    assert rates == pytest.approx({"X": 176.8 * (1 - GAP), "Xg": 39.4 * (1 - GAP)}), reason
    assert rates["Xg"] < 30.0  # under gas's own floor, carried by electricity's margin
    margin = 3.0 * (rates["X"] - 115.0) + 11.5 * (rates["Xg"] - 30.0)
    assert margin >= 0.0


def test_on_where_the_household_would_lose_each_leg_falls_back_to_its_own_floor():
    rates, reason = household_save_rates(_legs(elec_floor=140.0), GAP)
    assert rates == {"X": 140.0, "Xg": 30.0}, reason
    assert "loses GBP" in reason


def test_on_no_leg_is_offered_more_than_its_renewal_and_a_leg_at_the_market_is_left_alone():
    legs = (SaveLeg("X", 120.0, 176.8, 100.0, 3.0), SaveLeg("Xg", 36.0, 39.4, 20.0, 11.5))
    rates, _ = household_save_rates(legs, GAP)
    assert set(rates) == {"Xg"}  # electricity's renewal already beats the market's best deal


@pytest.mark.parametrize("field", ["renewal_unit_rate", "published_default_rate", "cost_floor",
                                   "annual_mwh"])
def test_on_an_unknown_leg_refuses_the_household_and_names_the_point(field):
    legs = list(_legs())
    legs[1] = dataclasses.replace(legs[1], **{field: None})
    rates, reason = household_save_rates(legs, GAP)
    assert rates is None and "Xg" in reason


def test_on_a_market_with_nothing_cheaper_offers_nothing():
    for gap in (None, 0.0, -0.01):
        assert household_save_rates(_legs(), gap)[0] is None
        assert save_rates_for_decision(_legs(), gap, ON) == {}
