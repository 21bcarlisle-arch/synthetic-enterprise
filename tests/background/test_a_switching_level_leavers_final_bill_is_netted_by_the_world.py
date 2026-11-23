"""A level leaver that SWITCHES away has its final bill netted by the world, as a mover's is.

The defect this names (`docs/staging/SEAT_FINDING_A_SWITCHING_LEVEL_LEAVER_IS_REFUNDED_SHORT_BECAUSE_
THE_WORLD_NETS_THE_FINAL_BILL_FOR_MOVERS_ONLY_2026-11-23.md`): the triad's final-month branch was gated
on `moved_out_on`, which only a home move sets. A switch-away's final bill was collected at its face,
while the page netted it and the refund paid the netted closing: 149 legs refunded GBP 3,673.83 short
on 6a588a832f. The run already knows a closing leg's last month (`left`); it now tells the triad.
"""
from __future__ import annotations

from datetime import date

import pytest

import background.live_payment_triad as lpt
import tests.background.test_a_level_leavers_final_bill_asks_its_face_less_the_schedules_surplus as base
from background.live_payment_triad import LivePaymentTriad
from simulation.payment_behaviour_source import DIRECT_DEBIT

FINAL, SUMMER = base.FINAL, base.SUMMER
asked = base.asked


def _switch(cid, final_face, *, closing=True, on_level=True):
    """Three level months, then a final bill with no move date: the switch-away's shape."""
    t = LivePaymentTriad()
    t._method_for = lambda c, fuel="electricity": DIRECT_DEBIT
    for month, period_end, due, bill in SUMMER:
        t.record_period(
            customer_id=cid, due_date=due, bill_month=month, period_end=period_end,
            amount_gbp=bill, income_stress_value="low", segment="resi",
            level_collection={"month": month, "collection_date": f"{month}-05", "amount_gbp": 60.00}
            if on_level else None)
    # The runner passes no level row for a leg that left (`level_collection=None if left`).
    t.record_period(
        customer_id=cid, due_date=date(2025, 5, 14), bill_month="2025-04",
        period_end="2025-04-30", amount_gbp=final_face, income_stress_value="low",
        segment="resi", closing=closing, level_collection=None)
    return t


def test_the_branch_is_reachable_both_ways(asked):
    """The same switch-away, closing and not: only the closing bill is netted. Without the flag the
    bill keeps today's face, so the control can fail."""
    _switch("SW-ON", 120.00)
    _switch("SW-OFF", 120.00, closing=False)
    assert asked[("SW-ON", FINAL)] == pytest.approx(30.00)
    assert asked[("SW-OFF", FINAL)] == pytest.approx(120.00)


def test_a_switchers_surplus_that_covers_the_final_bill_presents_nothing(asked):
    t = _switch("SW-ALL", 50.00)
    assert asked[("SW-ALL", FINAL)] == pytest.approx(0.00)
    assert t._records[-1].result == "success"


def test_a_switchers_final_bill_is_recorded_beside_its_face(asked):
    nets = _switch("SW-PART", 120.00).final_month_nets()
    assert nets["legs"] == 1 and nets["netted_ledger_credit_legs"] == 1
    r = nets["rows"][0]
    assert r["bill_month"] == "2025-04" and r["ever_level"]
    assert r["ledger_balance_gbp"] == pytest.approx(-90.00)
    assert r["ask_gbp"] == pytest.approx(r["face_gbp"] - r["credit_taken_gbp"]) == pytest.approx(30.00)


def test_a_never_level_switcher_still_asks_its_face(asked):
    _switch("SW-FACE", 50.00, on_level=False)
    assert asked[("SW-FACE", FINAL)] == pytest.approx(50.00)


def test_a_switcher_carries_no_exit_draw(asked):
    """Closing is not a move: the mover's exit model stays keyed on `moved_out_on`, so no seed moves."""
    t = _switch("SW-EXIT", 120.00)
    assert not t._final_bill_part_share
    assert lpt.LivePaymentTriad().final_month_nets()["legs"] == 0
