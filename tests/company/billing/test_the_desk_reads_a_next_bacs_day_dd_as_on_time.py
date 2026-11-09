"""A direct debit due on a weekend or bank holiday is collected, on time, on the next working day, so
the collections desk must not open a missed-payment journey on it.

DEFECT this names: `CollectionsJourneyDesk.advance` dated a bill's miss from `missed_on(due)` and
closed `bill_paid_in_its_window` on the due date, so a DD due Saturday 13 Jan 2024 and collected
Monday 15 Jan opened a journey on Sunday 14 Jan: a false collections contact on a household that paid
on time (9 of 2,459 such bills on e50e7b8f68). The page counter was fixed on 0f9ebbad56; this is the
desk. Knowledge: `docs/market_research/payments_and_direct_debit_2026-10-25.md`, "The day a collection
lands".

One control over the partition: the next-working-day DD reads on time, while the same bill paid on
receipt Monday and a DD collected Wednesday both still open a journey. A desk that never opens one, or
always does, fails it.
"""
from __future__ import annotations

import datetime as dt

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.collections_journey import MISSED_PAYMENT
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from interface.contracts.payment_observable_seam import (
    COLLECTION_REQUEST_TYPE,
    CollectionRequest,
    PaymentRail,
)
from interface.contracts.wall_envelope import WallRequest

ISSUE = dt.date(2023, 12, 30)  # due Saturday 2024-01-13 on the 14-day terms
MONDAY = dt.date(2024, 1, 15)
WEDNESDAY = dt.date(2024, 1, 17)


def _opened(account: str, paid_on: dt.date, *, by_dd: bool) -> list:
    consumer = PaymentObservationConsumer(ledger_book=LedgerBook())
    ref = f"{account}::1"
    if by_dd:
        consumer.note_collection_request(WallRequest(
            correlation_id=ref, request_type=COLLECTION_REQUEST_TYPE, schema_version=1,
            as_of=dt.datetime.combine(ISSUE, dt.time(0, 0)),
            emitted_at=dt.datetime.combine(ISSUE, dt.time(0, 0)),
            payload=CollectionRequest(account_id=account, mandate_ref=f"MND-{account}",
                                      amount_gbp=100.0, rail=PaymentRail.BACS_DIRECT_DEBIT,
                                      requested_collection_date=ISSUE + dt.timedelta(days=14))))
    for kind, on in ((LedgerEventType.BILL_DEBIT, ISSUE), (LedgerEventType.PAYMENT_CREDIT, paid_on)):
        consumer.ledger_book.post(LedgerEvent(
            event_id=f"{kind.value}:{account}", account_id=account, event_type=kind,
            amount_gbp=100.0, valid_time=on,
            transaction_time=dt.datetime.combine(on, dt.time(0, 0)), invoice_ref=ref))
    consumer.advance_collections_journey(account, dt.date(2024, 3, 1))
    return [s["on"] for j in consumer.collections_journeys.journeys() for s in j["stages"]
            if s["stage"] == MISSED_PAYMENT]


def test_a_dd_due_on_a_saturday_and_collected_on_monday_opens_no_journey():
    late_dd = _opened("ACC-DD-WED", WEDNESDAY, by_dd=True)
    on_receipt = _opened("ACC-SC-MON", MONDAY, by_dd=False)
    # Both branches the rule leaves open are reachable before asserting the one it closes.
    assert late_dd == ["2024-01-16"], late_dd  # missed the day after Monday, its last day
    assert on_receipt == ["2024-01-14"], on_receipt
    assert _opened("ACC-DD-MON", MONDAY, by_dd=True) == []


def _reoffers(paid_on: dt.date, *, by_dd: bool) -> list:
    """PROS-2017-0233's record (`test_a_reoffer_follows_a_missed_bill_not_a_standing_arrear`): an
    October arrear stands, so the plan is on offer. Its December bill falls due Saturday 16 Dec 2017
    and is paid on `paid_on`."""
    from company.billing.collections_journey import PLAN_REOFFER_STEP
    bills = [(dt.date(2017, 9, 6), 28.33, dt.date(2017, 9, 20)), (dt.date(2017, 10, 2), 35.45, None),
             (dt.date(2017, 10, 31), 39.31, dt.date(2017, 11, 14)),
             (dt.date(2017, 12, 2), 51.31, paid_on), (dt.date(2018, 1, 5), 53.06, dt.date(2018, 1, 19))]
    consumer = PaymentObservationConsumer(ledger_book=LedgerBook())
    for n, (issued, gbp, paid) in enumerate(bills):
        if by_dd:
            consumer.collections_journeys.note_bill_collected_by_direct_debit(str(n))
        consumer.ledger_book.post(LedgerEvent(
            event_id=f"B{n}", account_id="A", event_type=LedgerEventType.BILL_DEBIT, amount_gbp=gbp,
            valid_time=issued, transaction_time=dt.datetime.combine(issued, dt.time(0, 0)),
            invoice_ref=str(n)))
        if paid is not None:
            consumer.ledger_book.post(LedgerEvent(
                event_id=f"P{n}", account_id="A", event_type=LedgerEventType.PAYMENT_CREDIT,
                amount_gbp=gbp, valid_time=paid,
                transaction_time=dt.datetime.combine(paid, dt.time(0, 0))))
    consumer.advance_collections_journey("A", dt.date(2018, 2, 1))
    return [s["on"] for j in consumer.collections_journeys.journeys() for s in j["stages"]
            if s["stage"] == PLAN_REOFFER_STEP]


def test_a_dd_bill_collected_on_the_next_working_day_draws_no_reoffer():
    """DEFECT: `bill_paid_in_its_window` closed on the due date, so a DD due Saturday and collected
    Monday read as "a further bill missed" and re-offered the plan. Partition first: paid on receipt
    that Monday it is a miss (re-offered the day after its due date), and a DD collected Wednesday is
    a miss too (re-offered the day after Monday, its last day to pay)."""
    monday, wednesday = dt.date(2017, 12, 18), dt.date(2017, 12, 20)
    assert _reoffers(monday, by_dd=False) == ["2017-12-17"]
    assert _reoffers(wednesday, by_dd=True) == ["2017-12-19"]
    assert _reoffers(monday, by_dd=True) == []
