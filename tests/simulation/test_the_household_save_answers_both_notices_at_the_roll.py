"""The run's save site answers a dual household's two Invitations with one decision (fuel page §8a,
"Where the run answers both notices"; step 1b of the dual-fuel finding).

Defect guarded: `DecisionPolicy.save_offer_decides_per_household` had no run consumer, so switching it
on changed no byte, and the gas point's Invitation was filed and never read.

Inputs are the published 2024-Q2 record (`published_default_rate_ex_vat`, `published_best_deal_gap_
share`): electricity 233.3 and gas 57.5 GBP/MWh ex VAT, gap 0.089. Forwards, locked costs and volumes
are illustrative. The gas floor sits just above the gas match, so on answers gas only because the
household's summed headroom carries it.

No run on the short window can show this branch deciding: no Invitation reaches the company before
CSS, and the per-fuel default is unpublished before 2019 (prereg S1). This control is that evidence.

Mutations, run 2026-10-19, each red: held-notice filter dropped (1), riding leg never built (2), door
ignores the switch (1), default-tariff riding leg admitted (1), decision leg's own Invitation not
required (1). kWh passed as MWh stays green and is an EQUIVALENCE: both legs scale together and the
household rule reads only the sign of the summed headroom.
"""
from __future__ import annotations

import dataclasses

import pytest

import simulation.run_phase2b as run
from company.crm.cos_process import CoSRegister
from company.crm.save_offer import price_match_save_rate
from company.interfaces.save_offer import published_best_deal_gap_share, request_household_save
from company.policy.decision_policy import CURRENT_POLICY
from simulation.registration_loss_feed import RegistrationLossFeed

DAY = "2024-04-01"
ON = dataclasses.replace(CURRENT_POLICY, save_offer_decides_per_household=True)
ELEC = {"acquisition_date": DAY, "tariff_type": "fixed", "unit_rate_gbp_per_mwh": 240.0,
        "forward_price_gbp_per_mwh": 110.0, "company_forward_price_gbp_per_mwh": 110.0,
        "locked_policy_cost_gbp_per_mwh": 30.0, "locked_network_cost_gbp_per_mwh": 40.0}
GAS = {"acquisition_date": DAY, "tariff_type": "fixed", "unit_rate_gbp_per_mwh": 62.0,
       "forward_price_gbp_per_mwh": 40.0, "company_forward_price_gbp_per_mwh": 40.0,
       "locked_policy_cost_gbp_per_mwh": 3.0, "locked_network_cost_gbp_per_mwh": 8.0}


@pytest.fixture(autouse=True)
def _company_volume(monkeypatch):
    """The company's own annual volume for the riding point, which the run reads from its register
    reads; the read itself is not what is under test here."""
    monkeypatch.setattr(run, "_company_volume_reading",
                        lambda point, start, settled, fuel: {"kwh": 11_500.0})


def _held(points, day=DAY) -> CoSRegister:
    register = CoSRegister(holds={"H1", "H1g"}.__contains__)
    for wire in RegistrationLossFeed().wire_pending_notices_for_departure(points, day):
        assert register.receive_loss_wire(wire)
    return register


def _decide(policy, *, points=(("H1", "electricity"), ("H1g", "gas")), held=None, gas=GAS):
    legs = run._household_save_legs(
        "H1", "electricity", ELEC, DAY, ELEC["unit_rate_gbp_per_mwh"], 110.0, 3_000.0,
        list(points), {"H1": [ELEC]}, {"H1g": [gas]}, settled=None)
    register = _held(list(points) if held is None else held)
    rates, _vulnerable = request_household_save(
        register, legs, DAY, published_best_deal_gap_share(DAY), policy)
    return rates


def test_on_reaches_a_decision_that_answers_both_points_then_off_answers_one():
    """Asserted first, because the rare branch must be reachable before what it does is graded."""
    on = _decide(ON)
    assert set(on) == {"H1", "H1g"}, on
    off = _decide(CURRENT_POLICY)
    gap = published_best_deal_gap_share(DAY)
    floor = run._price_match_inputs(ELEC, "electricity", DAY, 110.0)["cost_floor"]
    assert off == {"H1": price_match_save_rate(240.0, run.published_default_rate_ex_vat(
        "electricity", DAY), gap, floor)}


def test_the_riding_leg_is_answered_under_its_own_floor_only_because_the_household_carries_it():
    on = _decide(ON)
    gas_floor = run._price_match_inputs(GAS, "gas", DAY, 40.0)["cost_floor"]
    assert on["H1g"] < gas_floor < GAS["unit_rate_gbp_per_mwh"], (on, gas_floor)


def test_a_single_fuel_household_is_decided_on_one_offer():
    assert set(_decide(ON, points=(("H1", "electricity"),))) == {"H1"}


def test_a_leg_whose_invitation_is_not_held_is_not_answered_and_without_the_roll_legs_none_is():
    assert set(_decide(ON, held=[("H1", "electricity")])) == {"H1"}
    assert _decide(ON, held=[("H1g", "gas")]) == {}


def test_before_css_no_invitation_arrives_so_nothing_is_decided():
    """Prereg S1's reason, held as a property: the short window cannot decide a save."""
    assert RegistrationLossFeed().wire_pending_notices_for_departure(
        [("H1", "electricity"), ("H1g", "gas")], "2017-03-01") == []


def test_a_riding_leg_on_the_default_tariff_is_not_a_fixed_offer_to_save_from():
    assert set(_decide(ON, gas={**GAS, "tariff_type": "svt"})) == {"H1"}
