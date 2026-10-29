"""A leaver's debt is written off on ONE date: the company's own write-off, a year after the final bill.

The page wrote it off at the final bill's due date, the company's sweep a year after the final bill
and only once the run was over, and the desk at the six-year bar, so the desk chased a balance the
page said was nil (class a of INV_OVERDUE_WITHIN_PAGE_BALANCE, 723 steps on 112 households;
`docs/staging/SEAT_FINDING_THE_PAGE_PRINTS_MORE_OVERDUE_THAN_IT_SAYS_IS_OWED_ON_493_OF_752_HOUSEHOLDS_2026-10-28.md`).
Knowledge: `docs/market_research/debt_and_collections.md` s.7.3.

What each control names as its own defect:
  * `test_the_desk_writes_a_closed_balance_off_on_the_company_date_and_nothing_else` -- the desk
    chases a closed account past the company's write-off, writes off a live or paid-up account, or
    never takes the closed branch at all. The whole partition is one assertion.
  * `test_the_page_writes_a_leavers_debt_off_on_the_date_the_desk_does` -- the world's close
    write-off is dated by its own clock again, not the company's.
"""
from __future__ import annotations

import datetime as dt

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.arrears_engine import CLOSED_ACCOUNT_RULE, closed_account_write_off_date
from company.billing.collections_journey import WRITE_OFF
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from simulation.arrears_engine import (
    LEG_CLOSE,
    PAYMENT_TERMS_DAYS,
    balance_settlement_from_outcomes,
)

FIRST = dt.date(2017, 1, 1)
THROUGH = dt.date(2019, 6, 30)


def _monthly(n):
    return [dt.date(FIRST.year + (FIRST.month - 1 + k) // 12, (FIRST.month - 1 + k) % 12 + 1, 1)
            for k in range(n)]


def _walk(account, n_bills, *, paid=False):
    consumer = PaymentObservationConsumer(ledger_book=LedgerBook())
    for n, issued in enumerate(_monthly(n_bills)):
        consumer.ledger_book.post(LedgerEvent(
            event_id=f"B:{account}:{n}", account_id=account, event_type=LedgerEventType.BILL_DEBIT,
            amount_gbp=40.0, valid_time=issued,
            transaction_time=dt.datetime.combine(issued, dt.time(0, 0)), invoice_ref=f"{n}"))
        if paid:
            on = issued + dt.timedelta(days=10)
            consumer.ledger_book.post(LedgerEvent(
                event_id=f"P:{account}:{n}", account_id=account,
                event_type=LedgerEventType.PAYMENT_CREDIT, amount_gbp=40.0, valid_time=on,
                transaction_time=dt.datetime.combine(on, dt.time(0, 0)), invoice_ref=f"{n}"))
    consumer.advance_collections_journey(account, THROUGH)
    stages = [s for j in consumer.collections_journeys.journeys() for s in j["stages"]]
    write_offs = [e for e in consumer.ledger_book.ledger(account).events()
                  if e.event_type == LedgerEventType.WRITE_OFF_CREDIT]
    return stages, write_offs


def test_the_desk_writes_a_closed_balance_off_on_the_company_date_and_nothing_else():
    left, left_wo = _walk("ACC-LEFT", 6)                # billed Jan-Jun 2017, never paid, then gone
    live, live_wo = _walk("ACC-LIVE", 30)               # still billed to the walk's end, never paid
    paid_up, paid_wo = _walk("ACC-PAID", 6, paid=True)  # left, owing nothing

    company_date = closed_account_write_off_date(_monthly(6)[-1]).isoformat()
    closed = [s for s in left if s["stage"] == WRITE_OFF]
    assert (closed and closed[0]["rule"] == CLOSED_ACCOUNT_RULE
            and not [s for s in live if s.get("rule") == CLOSED_ACCOUNT_RULE] and not live_wo
            and not paid_up and not paid_wo)

    assert closed[0]["on"] == company_date == "2018-06-01"
    assert closed[0]["written_off_gbp"] == 240.0
    assert [(e.valid_time.isoformat(), e.amount_gbp) for e in left_wo] == [(company_date, 240.0)]
    assert "uneconomic_to_pursue" in left_wo[0].reason
    # Nothing is chased after the company has written the balance off.
    assert max(s["on"] for s in left) == company_date


def test_the_page_writes_a_leavers_debt_off_on_the_date_the_desk_does():
    due = [d + dt.timedelta(days=PAYMENT_TERMS_DAYS) for d in _monthly(6)]
    resolved = [{"customer_id": "C9", "period_end": d.isoformat(), "commodity": "electricity",
                 "amount_gbp": 40.0, "due_date": d, "method": "standard_credit",
                 "outcome": "failed", "days_late": 0} for d in due]
    written_off, _ = balance_settlement_from_outcomes(resolved, {"C9"})
    dates = {(w["leg"], w["date"]) for w in written_off.values()}
    assert dates == {(LEG_CLOSE, closed_account_write_off_date(_monthly(6)[-1]))}
