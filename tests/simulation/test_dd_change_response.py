"""DD4c -- a household told a new DD amount, or offered a date nearer payday (2026-10-12).

What each control names as its own defect:

  * `test_the_shipped_world_answers_no_date_offer` -- the date response switched on by default.
  * `test_a_date_offer_reaches_both_answers_and_only_a_stretched_mismatched_household_takes_it`
    -- the partition first (takes it, does not); then a LOW-stress household helped, or every
    stretched one, or a share far from the published mismatch.
  * `test_a_moved_date_lowers_failures_from_its_month_on_and_compounds_with_a_shock` -- the effect
    drawn and never reaching a collection, starting early, ending after a year like a shock's, or
    swallowed by a concurrent shock's uplift.
  * `test_a_told_amount_is_a_shock_only_above_the_one_material_rise` -- a second meaning of
    "shocked", or a fall answered as if it were a rise.
"""
from __future__ import annotations

import pytest

import simulation.dd_shock_response as dsr
from simulation.dd_shock_response import (
    PAYDAY_MISMATCH_SHARE_LOW_INCOME,
    DateChangeStrength,
    DDShockStrengths,
    bill_effect,
    respond_to_date_offer,
    respond_to_told_amount,
)
from simulation.experienced_bill_shock import MATERIAL_RISE_FRACTION

HIGH = DateChangeStrength.at("high")


def test_the_shipped_world_answers_no_date_offer():
    assert dsr.DATE_CHANGE.off and DateChangeStrength.at("default").off
    assert not any(respond_to_date_offer(household=f"H{i}", month="2020-04", stress="high")
                   for i in range(300))


def test_a_date_offer_reaches_both_answers_and_only_a_stretched_mismatched_household_takes_it():
    rows = [respond_to_date_offer(household=f"H{i}", month="2020-04", stress="moderate",
                                  strength=HIGH) for i in range(3000)]
    assert any(rows) and not all(rows)
    share = sum(r is not None for r in rows) / len(rows)
    assert abs(share - PAYDAY_MISMATCH_SHARE_LOW_INCOME) < 0.04, share
    assert not any(respond_to_date_offer(household=f"H{i}", month="2020-04", stress="low",
                                         strength=HIGH) for i in range(500))


def test_a_moved_date_lowers_failures_from_its_month_on_and_compounds_with_a_shock():
    row = next(r for i in range(100) if (r := respond_to_date_offer(
        household=f"H{i}", month="2020-04", stress="high", strength=HIGH)))
    assert bill_effect([row], "2020-03").failure_multiplier == 1.0
    assert bill_effect([row], "2020-04").failure_multiplier == pytest.approx(1 - 0.36)
    assert bill_effect([row], "2024-04").failure_multiplier == pytest.approx(1 - 0.36)
    shock = {"household": "H", "review_month": "2020-06", "cancelled_month": None,
             "failure_multiplier": 4.0}
    assert bill_effect([row, shock], "2020-07").failure_multiplier == pytest.approx(4.0 * 0.64)


def test_a_told_amount_is_a_shock_only_above_the_one_material_rise():
    on = DDShockStrengths(cancel_share=0.0, failure_uplift=1.0, complaint_share=0.0)
    def told(new):
        return respond_to_told_amount(household="H", month="2020-04", amount_in_force_gbp=100.0,
                                      new_amount_gbp=new, stress="low", stays=True,
                                      already_cancelled=False, strengths=on)
    assert told(100.0 * (1 + MATERIAL_RISE_FRACTION) + 1)["failure_multiplier"] == 2.0
    assert told(100.0 * (1 + MATERIAL_RISE_FRACTION)) is None
    assert told(60.0) is None
