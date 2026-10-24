"""Prepayment debt (a): a credit account moved to a meter for debt repays through top-ups (2026-10-24).

Knowledge: `docs/market_research/debt_realism_three_world_fidelity_gaps.md` s.2, part (a).

What each control names as its own defect:

  * `test_meter_moves_happen_and_do_not_happen` -- a route that moves everyone or no-one passes every
    other test here; the control run (take-up off) must move nobody and the switched-on run somebody
    while some accounts stay on credit.
  * `test_the_company_ledger_receives_what_the_meter_collected` -- the move recorded but the
    deductions never posted: the account would sit overdue and be dunned for debt a meter is repaying.
  * `test_recovery_is_the_published_weekly_mean_per_fuel_and_never_exceeds_the_debt` -- the rate
    swapped between fuels, or a last deduction that overshoots the debt.
  * `test_bills_after_the_move_are_paid_before_use` -- the account moved but still billed as credit:
    it would fail a DD on a meter.
  * `test_a_lump_for_a_bill_before_the_move_is_withdrawn` -- the same arrears repaid twice, by lump and meter.
"""
from __future__ import annotations

import datetime as dt
from datetime import date

import pytest

import simulation.payment_method_dynamics as pmd
from background.live_payment_triad import LivePaymentTriad
from simulation.plan_offer_response import HouseholdPlanBook


def _run(take_up: float) -> LivePaymentTriad:
    pmd.STRENGTHS = pmd.MethodStrengths(0.0, take_up)
    triad = LivePaymentTriad()
    for i in range(40):
        for m in range(1, 13):
            triad.record_period(customer_id=f"RESI{i:05d}", due_date=date(2020, m, 28),
                                amount_gbp=120.0, income_stress_value="high", segment="resi")
    triad.collections_journeys(date(2021, 12, 31))
    return triad


@pytest.fixture(autouse=True)
def _restore():
    saved = pmd.STRENGTHS
    yield
    pmd.STRENGTHS = saved


@pytest.fixture(scope="module")
def on_run():
    saved = pmd.STRENGTHS
    try:
        yield _run(1.0)
    finally:
        pmd.STRENGTHS = saved


def test_meter_moves_happen_and_do_not_happen(on_run):
    assert on_run._household_plans._meters, "no meter moved with take-up 1.0"
    assert len(on_run._household_plans._meters) < 40, "every account moved: the partition is one-sided"
    assert not _run(0.0)._household_plans._meters, "a meter moved with take-up off"


def test_the_company_ledger_receives_what_the_meter_collected(on_run):
    book = on_run._household_plans
    for account_id, (moved_on, debt) in book._meters.items():
        events = on_run._consumer.ledger_book.ledger(account_id).events()
        meter_cash = [e for e in events if ":meter:" in e.event_id]
        assert meter_cash, f"{account_id} moved on {moved_on} and no deduction reached its ledger"
        assert sum(e.amount_gbp for e in meter_cash) <= debt + 0.005


def test_recovery_is_the_published_weekly_mean_per_fuel_and_never_exceeds_the_debt():
    moved = date(2024, 1, 1)
    elec = pmd.meter_recoveries(100.0, moved, date(2024, 12, 31), "electricity")
    gas = pmd.meter_recoveries(100.0, moved, date(2024, 12, 31), "gas")
    assert elec[0] == {"due": "2024-01-08", "amount_gbp": 6.01}
    assert gas[0]["amount_gbp"] == 4.40
    for rows in (elec, gas):
        assert round(sum(r["amount_gbp"] for r in rows), 2) == 100.0
    assert len(elec) == 17 and elec[-1]["amount_gbp"] == pytest.approx(100 - 16 * 6.01)
    assert pmd.meter_recoveries(100.0, moved, moved + dt.timedelta(days=6)) == [], (
        "asking before the first top-up must see nothing")


def test_bills_after_the_move_are_paid_before_use():
    book = HouseholdPlanBook()
    book.record_meter("A", date(2020, 5, 1), 300.0)
    assert not book.on_meter("A", date(2020, 4, 30)) and book.on_meter("A", date(2020, 5, 28))
    assert not book.on_meter("B", date(2020, 5, 28))


def test_a_lump_for_a_bill_before_the_move_is_withdrawn():
    book = HouseholdPlanBook()
    book.record_meter("A", date(2020, 5, 1), 300.0)
    assert book.repays_through_plan("A", date(2020, 3, 28), date(2020, 7, 1))
    assert not book.repays_through_plan("A", date(2020, 5, 28), date(2020, 7, 1))
    assert not book.repays_through_plan("B", date(2020, 3, 28), date(2020, 7, 1))
