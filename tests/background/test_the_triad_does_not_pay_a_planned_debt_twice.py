"""EP4 -- a household that agreed a repayment plan repays those arrears through it, not as a lump too.

What each control names as its own defect:

  * `test_a_plan_replaces_the_lump_and_no_lump_crosses_for_a_planned_bill` -- the world's later
    lump settlement crosses for a bill an agreed plan already covers, so the company is paid the
    same arrears twice; or the withdrawal fires on everything (the lump route closed for all).
    Both partitions -- lumps crossed, lumps withdrawn -- are asserted reachable first, on monthly
    and quarterly bills. Quarterly is the cadence where a lump is due before the ordinary walk has
    decided the offer, so it is what the hold is for.
  * `test_the_published_basis_withdraws_nothing` -- with no sourced take-up rate the world agrees
    nothing, so the change must move no lump.
  * `test_the_world_book_counts_only_a_plan_agreed_between_the_bill_and_the_lump` -- the book's
    window is open at either end.
"""
from __future__ import annotations

import dataclasses
import functools
from datetime import date

import pytest

import simulation.plan_offer_response as por
from background.live_payment_triad import LivePaymentTriad

_SOURCED = dataclasses.replace(por.PUBLISHED_BASIS, take_up_rate=1.0, instalment_keep_rate=1.0,
                               monthly_instalment_gbp=25.0)


def _run(months, customers=40) -> LivePaymentTriad:
    triad = LivePaymentTriad()
    for i in range(customers):
        for m in months:
            triad.record_period(customer_id=f"RESI{i:05d}", due_date=date(2020, m, 28),
                                amount_gbp=120.0, income_stress_value="high", segment="resi")
    triad.collections_journeys(date(2021, 12, 31))
    return triad


@pytest.fixture
def sourced(monkeypatch):
    """Every household agrees and keeps every plan: the injected basis, never the published one."""
    monkeypatch.setattr(por, "answer_plan_offer",
                        functools.partial(por.answer_plan_offer, basis=_SOURCED))
    monkeypatch.setattr(por, "plan_instalments",
                        functools.partial(por.plan_instalments, basis=_SOURCED))


@pytest.mark.parametrize("months", [range(1, 13), (1, 4, 7, 10)], ids=["monthly", "quarterly"])
def test_a_plan_replaces_the_lump_and_no_lump_crosses_for_a_planned_bill(sourced, months):
    triad = _run(months)
    assert triad.settlements_delivered > 0 and triad.settlements_withdrawn > 0, (
        "both partitions must be reachable: some lumps cross, some a plan replaces")
    assert triad.settlements_crossed_despite_a_plan == 0, (
        "a lump crossed for a bill an agreed plan was already repaying -- the arrears paid twice")
    assert triad.later_settlements() == {
        "delivered": triad.settlements_delivered, "withdrawn": triad.settlements_withdrawn,
        "crossed_despite_a_plan": 0}, "the summary the run publishes drops or renames a counter"


def test_the_published_basis_withdraws_nothing():
    triad = _run(range(1, 7), customers=15)
    assert triad.settlements_delivered > 0
    assert triad.settlements_withdrawn == 0 and triad.settlements_crossed_despite_a_plan == 0


def test_the_world_book_counts_only_a_plan_agreed_between_the_bill_and_the_lump():
    book = por.HouseholdPlanBook()
    book.record("A", date(2020, 2, 25))
    assert book.repays_through_plan("A", date(2020, 1, 28), date(2020, 5, 25))
    assert not book.repays_through_plan("A", date(2020, 2, 25), date(2020, 5, 25)), (
        "a bill falling due on the agreement day was not in the debt agreed")
    assert not book.repays_through_plan("A", date(2020, 1, 28), date(2020, 2, 25)), (
        "a lump on the agreement day was paid before the plan replaced it")
    assert not book.repays_through_plan("B", date(2020, 1, 28), date(2020, 5, 25))
    assert por.answer_plan_offer("A", date(2020, 3, 1), 50.0, agreements=book).accepted is None
    por.answer_plan_offer("C", date(2020, 3, 1), 50.0, basis=_SOURCED, agreements=book)
    assert book.repays_through_plan("C", date(2020, 1, 28), date(2020, 5, 25)), (
        "a yes was not recorded on the world's book")
