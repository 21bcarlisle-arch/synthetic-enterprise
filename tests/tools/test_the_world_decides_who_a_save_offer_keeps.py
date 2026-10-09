"""The save-offer shapes graded on the coin-drawn set. One control per way it can mislead:

  1. a save is decided by a coin of ours or a fixed save probability, not by the world's own roll
     on the world's own curve -- so a published save rate would be an INPUT, not a check;
  2. the reactive save pays its cut on a household that would have stayed anyway;
  3. a zero cut "saves" someone, so the implied rate is a property of the arithmetic, not the cut;
  4. the sensitivity changes the world it claims only to rescale.
"""
from __future__ import annotations

import pytest

from simulation import coin_drawn_decision_set as cds
from tools.grade_save_offer_shapes import grade_shapes, world_save_rate

SMALL = dict(start_year=2016, end_year=2020, acquisitions_per_year=30.0)
CUT = 7.5


@pytest.fixture(scope="module")
def probed():
    return cds.build_decision_set(42, cut_gbp_per_mwh=0.0, probe_cuts=(0.0, CUT, 30.0), **SMALL).rows


def _row(p0: float, pc: float, roll: float, opened_on=None) -> dict:
    return {"account": "HLD-t", "decision_date": "2020-01-01", "arm": "holdout",
            "offer_unit_rate": 200.0, "stayed": roll <= p0, "payment_method": "direct_debit",
            "monthly_bills": [50.0] * 12, "billed_kwh": 3000.0, "opened_on": opened_on,
            "acquisition_route": None, "days_on_default": None, "ever_actively_renewed": None,
            "p_stay_holdout": p0, "p_stay_at_cut": {CUT: pc}, "roll": roll}


def test_a_save_is_the_worlds_own_stay_at_the_cut_price_on_the_same_roll(probed):
    """Defect 1. For every household leaving at the default, `saved_on_loss_notice` must agree with
    the world's OWN renewal outcome re-asked at the cut. An independent coin or a fixed save
    probability disagrees on some leaver; both branches (saved, not saved) must be reached."""
    leavers = [r for r in probed if not r["stayed"]]
    outcomes = []
    for r in leavers:
        for cut in (CUT, 30.0):
            world_stays = r["stays_at_cut"][cut]
            if world_stays is None or abs(r["roll"] - r["p_stay_at_cut"][cut]) < 1e-9:
                continue
            ours = cds.saved_on_loss_notice(r["roll"], r["p_stay_holdout"], r["p_stay_at_cut"][cut])
            assert ours == world_stays, (r["account"], r["decision_date"], cut)
            outcomes.append(ours)
    assert True in outcomes and False in outcomes, "a branch of the save is unreachable"


def test_the_reactive_save_never_pays_a_household_that_would_have_stayed():
    """Defect 2. A certain stayer (P0 = Pc = 1) costs C nothing and costs A the whole cut; and on
    a mix, C pays exactly on the moved share Pc - P0, never on P0."""
    stayer = grade_shapes([_row(1.0, 1.0, 0.5)], cut=CUT, stay_share=0.8, margin_share=0.14)
    assert stayer["C_reactive"]["paid_share"] == 0.0
    assert stayer["C_reactive"]["household_saving"] == 0.0
    assert stayer["A_blanket"]["paid_share"] == 1.0
    mix = grade_shapes([_row(0.6, 0.7, 0.65), _row(0.9, 0.92, 0.1)], cut=CUT, stay_share=0.8,
                       margin_share=0.14)
    assert mix["C_reactive"]["paid_share"] == pytest.approx((0.1 + 0.02) / 2)
    assert not cds.saved_on_loss_notice(0.3, 0.6, 0.9), "a roll below P0 was never leaving"


def test_a_zero_cut_saves_nobody(probed):
    """Defect 3. Re-asked at a cut of 0 the world returns P0, so the implied save rate is 0 -- from
    the world, not from a short-circuit."""
    assert all(r["p_stay_at_cut"][0.0] == r["p_stay_holdout"] for r in probed)
    zero = world_save_rate(probed, 0.0)
    assert zero["implied_save_rate"] == 0.0 and zero["saved_rolled"] == 0
    assert world_save_rate(probed, CUT)["implied_save_rate"] > 0.0
    assert cds.implied_save_rate(0.7, 0.7) == 0.0


def test_the_sensitivity_rescales_the_worlds_effect_and_k_one_is_the_world(probed):
    """Defect 4. k = 1 must reproduce the world's own rate and k = 0 must save nobody, so a target
    rate is reached by scaling the world's response, not by replacing it."""
    world = world_save_rate(probed, CUT)
    assert world_save_rate(probed, CUT, k=1.0) == world
    half = world_save_rate(probed, CUT, k=0.5)["implied_save_rate"]
    assert half == pytest.approx(world["implied_save_rate"] / 2)
    assert world_save_rate(probed, CUT, k=0.0)["saved_rolled"] == 0
