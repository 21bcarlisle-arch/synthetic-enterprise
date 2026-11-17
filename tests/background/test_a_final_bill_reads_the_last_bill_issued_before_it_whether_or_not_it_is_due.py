"""A level leaver's final bill reads every bill issued before it, due or not.

The defect this names (row 7 on the 18f201c5bf book, INV_OVERDUE_WITHIN_PAGE_BALANCE, 20 steps): the
world read the leg's balance at the final bill from bills already DUE, while it counted ALL the cash.
A last regular bill issued days before the final bill was not yet due, so it was left out. The level
cash that had met it was not left out. So the leg read in credit, and the final bill netted a credit
that did not exist: SYN-2016-471 was asked 4.75 of a 14.10 bill, and -523 and -546 were asked nothing.
The page printed the face as paid. The desk read the cash that crossed, so every step of each leaver's
journey printed the netted amount above the page's balance (desk's overdue less page's balance:
9.35, 25.28 and 6.73). SLC 27.17: the final bill states the one balance.

Shape, as SYN-2016-471's: level 40 a month; Jan bill 30, Feb bill 60 issued 28 Feb and due 14 Mar; the
household moves out on 6 Mar and its final bill of 25 is issued 7 Mar. The ledger owes 10 when the
final bill is issued (bills 90, cash 80). The due-only read saw a credit of 50.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

import background.live_payment_triad as lpt
import simulation.household_budget as household_budget
from background.live_payment_triad import LivePaymentTriad
from simulation.payment_behaviour_source import DIRECT_DEBIT


@pytest.fixture
def asked(monkeypatch):
    """Every amount the world presented, keyed by (leg, period index), every draw collected."""
    monkeypatch.setattr(household_budget, "BUDGET_DECIDES_PAYMENT", False)
    monkeypatch.setattr(lpt.early_contact, "EARLY_CONTACT_SHARE", 0.0)
    monkeypatch.setattr(lpt, "later_settlement_date", lambda event, segment="resi": None)
    monkeypatch.setattr(lpt, "FINAL_BILL_ASKS_THE_LEVEL_DEBIT", True)
    real = lpt.generate_payment_event
    seen: dict = {}

    def draw(cid, period_index, due, amount, stress, method, **kw):
        seen[(cid, period_index)] = amount
        ev = real(cid, period_index, due, amount, stress, method, **kw)
        return lpt.dataclasses.replace(ev, result="success", days_late=0,
                                       payment_date=due.isoformat(), dd_failure_reason=None)
    monkeypatch.setattr(lpt, "generate_payment_event", draw)
    return seen


def _leave_before_the_last_bill_is_due(cid):
    t = LivePaymentTriad()
    t._method_for = lambda c, fuel="electricity": DIRECT_DEBIT
    for month, due, end, face in (("2025-01", date(2025, 2, 14), "2025-01-31", 30.00),
                                  ("2025-02", date(2025, 3, 14), "2025-02-28", 60.00)):
        t.record_period(
            customer_id=cid, due_date=due, bill_month=month, period_end=end, amount_gbp=face,
            income_stress_value="low", segment="resi",
            level_collection={"month": month, "collection_date": f"{month}-05", "amount_gbp": 40.00})
    t.record_period(
        customer_id=cid, due_date=date(2025, 3, 21), bill_month="2025-03", period_end="2025-03-05",
        amount_gbp=25.00, income_stress_value="low", segment="resi", moved_out_on="2025-03-06",
        level_collection={"month": "2025-03", "collection_date": "2025-03-05", "amount_gbp": 40.00})
    return t, lpt._period_index_for("2025-03")


def test_the_final_bill_counts_the_last_bill_before_it_is_due(asked):
    """The first assertion is that the shape is reached: the final bill was issued before the Feb bill
    fell due, so a due-only read cannot see that bill."""
    t, final = _leave_before_the_last_bill_is_due("LVL-471")
    row = t.final_month_nets()["rows"][-1]
    assert date(2025, 3, 21) - timedelta(days=lpt.PAYMENT_TERMS_DAYS) < date(2025, 3, 14)
    assert row["ledger_balance_gbp"] == pytest.approx(10.00)
    assert row["credit_taken_gbp"] == pytest.approx(0.0)
    assert row["debit_asked_gbp"] == pytest.approx(10.00)
    assert asked[("LVL-471", final)] == pytest.approx(35.00)


def test_a_true_credit_is_still_netted_once(asked):
    """The other side of the same read: where the level cash really exceeds every bill issued, the final
    bill nets that credit, no more. Level 40 against bills of 30 and 30 leaves 20 in credit."""
    t = LivePaymentTriad()
    t._method_for = lambda c, fuel="electricity": DIRECT_DEBIT
    for month, due, end in (("2025-01", date(2025, 2, 14), "2025-01-31"),
                            ("2025-02", date(2025, 3, 14), "2025-02-28")):
        t.record_period(
            customer_id="LVL-CR", due_date=due, bill_month=month, period_end=end, amount_gbp=30.00,
            income_stress_value="low", segment="resi",
            level_collection={"month": month, "collection_date": f"{month}-05", "amount_gbp": 40.00})
    t.record_period(
        customer_id="LVL-CR", due_date=date(2025, 3, 21), bill_month="2025-03", period_end="2025-03-05",
        amount_gbp=25.00, income_stress_value="low", segment="resi", moved_out_on="2025-03-06",
        level_collection={"month": "2025-03", "collection_date": "2025-03-05", "amount_gbp": 40.00})
    row = t.final_month_nets()["rows"][-1]
    assert row["credit_taken_gbp"] == pytest.approx(20.00)
    assert asked[("LVL-CR", lpt._period_index_for("2025-03"))] == pytest.approx(5.00)
