"""A credit valued on a day the collections desk had already walked through is counted, with the
dunning steps such credits cleared after issue over every dunning step issued.

The desk is promised a ledger complete to each walk's end (`CollectionsJourneyDesk.advance`). On
book 61118 that promise broke for ACC-SYN-2016-239 and stopped a run; e09f1640a stopped the crash by
judging each step when issued, which made the late credit silent. These controls keep it countable.

  * `test_a_credit_behind_the_walk_is_recorded_and_one_ahead_of_it_is_not` -- the whole partition in
    one control: the same consumer takes one credit behind its walk and one ahead of it, and only
    the first is a row. Named defects: the detector never fires (no row), or fires on every credit
    (two rows, a "rate" of 100% that would read as a finding).
  * `test_the_cleared_step_count_carries_its_denominator` -- the published count is the steps a
    late credit cleared over the dunning steps issued, never a bare count.
"""
from __future__ import annotations

import datetime as dt

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.payment_observation_consumer import PaymentObservationConsumer

ACCOUNT = "ACC-BEHIND"
ISSUE = dt.date(2024, 1, 1)  # due 01-15, missed 01-16, reminder 01-22, reminder_2 01-29
REMINDER_2 = dt.date(2024, 1, 29)
WALKED = dt.date(2024, 1, 30)


def _consumer_walked_past_reminder_2():
    consumer = PaymentObservationConsumer(ledger_book=LedgerBook())
    consumer.ledger_book.post(LedgerEvent(
        event_id="bill:1", account_id=ACCOUNT, event_type=LedgerEventType.BILL_DEBIT,
        amount_gbp=100.0, valid_time=ISSUE, transaction_time=dt.datetime(2024, 1, 1),
        invoice_ref=f"{ACCOUNT}::1"))
    consumer.advance_collections_journey(ACCOUNT, WALKED)
    return consumer


def _pay(consumer, gbp, value_date, ref):
    consumer._post_cash(account_id=ACCOUNT, amount_gbp=gbp, value_date=value_date,
                        observed_at=dt.datetime(2024, 2, 2), correlation_id=ref,
                        remittance_ref=None)


def test_a_credit_behind_the_walk_is_recorded_and_one_ahead_of_it_is_not():
    consumer = _consumer_walked_past_reminder_2()
    _pay(consumer, 10.0, WALKED + dt.timedelta(days=1), "ahead")
    _pay(consumer, 112.53, REMINDER_2, "behind")
    _pay(consumer, 112.53, REMINDER_2, "behind")  # the same response again: one ledger event
    _pay(consumer, 1.0, WALKED, "on-the-last-day")  # the walk's end is inclusive
    assert consumer.credits_behind_the_walk == [
        {"account_id": ACCOUNT, "value_date": REMINDER_2.isoformat(),
         "walked_through": WALKED.isoformat(), "amount_gbp": 112.53, "correlation_id": "behind"},
        {"account_id": ACCOUNT, "value_date": WALKED.isoformat(),
         "walked_through": WALKED.isoformat(), "amount_gbp": 1.0,
         "correlation_id": "on-the-last-day"}]


def test_the_cleared_step_count_carries_its_denominator():
    consumer = _consumer_walked_past_reminder_2()
    _pay(consumer, 122.53, REMINDER_2, "behind")
    consumer.advance_collections_journey(ACCOUNT, dt.date(2024, 3, 1))
    record = consumer.collections_journeys.late_credit_record()
    assert record["steps_cleared_after_issue"] == 1
    assert record["accounts"] == 1
    # reminder (01-22) and reminder_2 (01-29) were issued; the cure is not a dunning step.
    assert record["dunning_steps_issued"] == 2
