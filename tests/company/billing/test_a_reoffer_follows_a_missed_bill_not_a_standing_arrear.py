"""A re-offer says "a further bill missed", so a bill must have been missed (N15).

PROS-2017-0233 on 0a6391d186: one DD returned on the £35.45 September bill, then every later bill
collected in full on its due date, and the desk re-offered the plan the day after each one, worded
as a miss. The desk keyed the re-offer to the calendar (the day after ANY bill's due date) and never
asked whether that bill was paid. Knowledge: `docs/market_research/company_debt_management.md`,
"A further bill missed".

What the control names as its own defect:
  * `test_a_bill_paid_on_its_due_date_draws_no_reoffer_and_a_missed_one_does` -- the desk re-offers
    after a bill paid in full on its due date while an older arrear stands. The partition is asserted
    first: the same account re-offers when a later bill IS missed, so a desk that never re-offers fails.
  * `test_a_bill_a_credit_bill_paid_down_is_judged_on_what_it_asked` -- the desk judges a bill on its
    face, so one a credit bill paid down reads missed when the household paid every penny it was asked
    (7 of the 11 re-offers the blind row found on b3ce2a4e73, e.g. PROS-2021-0236g's £20.21 gas bill
    asked £0.00). Partition first: the same bill's ask left unpaid still re-offers.
"""
from __future__ import annotations

import datetime as dt

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.collections_journey import (
    PLAN_REOFFER_STEP,
    assert_journey_order_lawful,
    bill_paid_in_its_window,
)
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.crm.account_hierarchy import Segment

# PROS-2017-0233's record: (issued, GBP, paid on the due date?)
BILLS = [(dt.date(2017, 9, 6), 28.33, True), (dt.date(2017, 10, 2), 35.45, False),
         (dt.date(2017, 10, 31), 39.31, True), (dt.date(2017, 12, 2), 51.31, True),
         (dt.date(2018, 1, 5), 53.06, True)]
THROUGH = dt.date(2018, 2, 1)


def _reoffers(bills, asked=None, paid_gbp=None):
    """`asked`: invoice_ref -> what a netted bill asked, told to the desk; `paid_gbp`: invoice_ref ->
    what the household paid on the due date, where not the face."""
    consumer = PaymentObservationConsumer(ledger_book=LedgerBook())
    for ref, gbp in (asked or {}).items():
        consumer.collections_journeys.note_bill_asked(ref, gbp)
    for n, (issued, gbp, paid) in enumerate(bills):
        consumer.ledger_book.post(LedgerEvent(
            event_id=f"B{n}", account_id="A", event_type=LedgerEventType.BILL_DEBIT, amount_gbp=gbp,
            valid_time=issued, transaction_time=dt.datetime.combine(issued, dt.time(0, 0)),
            invoice_ref=str(n)))
        if paid:
            due = issued + dt.timedelta(days=14)
            consumer.ledger_book.post(LedgerEvent(
                event_id=f"P{n}", account_id="A", event_type=LedgerEventType.PAYMENT_CREDIT,
                amount_gbp=(paid_gbp or {}).get(str(n), gbp), valid_time=due, transaction_time=dt.datetime.combine(due, dt.time(0, 0))))
    consumer.advance_collections_journey("A", THROUGH)
    journeys = consumer.collections_journeys.journeys()
    for j in journeys:
        assert_journey_order_lawful(j, Segment.RESIDENTIAL)
    return [s["on"] for j in journeys for s in j["stages"] if s["stage"] == PLAN_REOFFER_STEP]


def test_a_bill_paid_on_its_due_date_draws_no_reoffer_and_a_missed_one_does():
    # The partition first: miss the December bill too, and the day after its due date re-offers.
    missed_december = [b if b[0] != dt.date(2017, 12, 2) else (b[0], b[1], False) for b in BILLS]
    assert _reoffers(missed_december) == ["2017-12-17"]
    # The record: the arrear stands, every later bill is paid on its date, and no miss is claimed.
    assert _reoffers(BILLS) == []


def test_the_window_counts_cash_from_issue_to_due_inclusive():
    issued = dt.date(2017, 10, 31)
    on_due = [(dt.date(2017, 11, 14), 39.31)]
    assert bill_paid_in_its_window(on_due, issued, 39.31)
    assert not bill_paid_in_its_window([(dt.date(2017, 11, 15), 39.31)], issued, 39.31)
    assert not bill_paid_in_its_window([(dt.date(2017, 10, 30), 39.31)], issued, 39.31)
    assert not bill_paid_in_its_window([(dt.date(2017, 11, 14), 20.0)], issued, 39.31)


def test_a_bill_a_credit_bill_paid_down_is_judged_on_what_it_asked():
    # The December £51.31 bill had £20.00 of an earlier credit bill netted off it, so it asked £31.31
    # and the household paid exactly that on its due date. The arrear from October still stands.
    paid_ask = {"3": 31.31}
    # Partition first: told nothing about the netting, the desk reads £31.31 against £51.31 and
    # re-offers -- the defect, and proof the branch can be taken.
    assert _reoffers(BILLS, paid_gbp=paid_ask) == ["2017-12-17"]
    # Told what the bill asked, a household that paid it is not told it missed it.
    assert _reoffers(BILLS, asked={"3": 31.31}, paid_gbp=paid_ask) == []
    # And a netted bill whose ask went unpaid is still a further bill missed.
    assert _reoffers(BILLS, asked={"3": 31.31}, paid_gbp={"3": 0.0}) == ["2017-12-17"]
