"""After the last rung the collections desk still acts, and a live debt is written off only by a named rule.

The 19 Oct run showed a bill that drew its notices in 2019 and then nothing for five years
(`docs/staging/SEAT_FINDING_EXPLORES_CAST_FINDS_STANDARD_VARIABLE_BILLS_ABOVE_THE_CAP_AND_NO_MOVER_OR_TWO_RATE_HOME_2026-10-23.md`
s3). Knowledge: `docs/market_research/company_debt_management.md`, "After the last rung".

What each control names as its own defect:
  * `test_an_unpaid_live_debt_reaches_a_further_step_or_a_named_write_off_and_a_paid_one_neither`
    -- the desk goes silent past its top rung, writes a live debt off by no rule, or acts on an
    account that pays. The whole partition is asserted in ONE control before what any leg looks like.
  * `test_a_payment_inside_six_years_restarts_the_bar` -- the bar reads the bill's age alone, so a
    household still paying something has its debt released (Limitation Act s.29(5)).
  * `test_a_reoffer_with_no_offer_after_it_is_unlawful` -- the order check accepts a re-offer that
    made no offer.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.collections_journey import (
    ARRANGEMENT_OFFERED,
    PLAN_OFFER_STEP,
    PLAN_REOFFER_STEP,
    PREPAYMENT_OFFERED,
    PREPAYMENT_STEP,
    STATUTE_BAR_RULE,
    UNREACHED_EXITS,
    WRITE_OFF,
    UnlawfulJourneyOrderError,
    assert_journey_order_lawful,
    statute_barred_gbp,
)
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.crm.account_hierarchy import Segment

START = dt.date(2016, 1, 1)
THROUGH = dt.date(2023, 3, 1)


def _monthly(n_months):
    return [dt.date(START.year + (START.month - 1 + k) // 12, (START.month - 1 + k) % 12 + 1, 1)
            for k in range(n_months)]


def _walk(account, *, paid_months=(), pay_once_on=None):
    consumer = PaymentObservationConsumer(ledger_book=LedgerBook())
    for n, issued in enumerate(_monthly(86)):
        consumer.ledger_book.post(LedgerEvent(
            event_id=f"B:{account}:{n}", account_id=account, event_type=LedgerEventType.BILL_DEBIT,
            amount_gbp=50.0, valid_time=issued,
            transaction_time=dt.datetime.combine(issued, dt.time(0, 0)), invoice_ref=f"{n}"))
        if n in paid_months:
            paid = issued + dt.timedelta(days=10)
            consumer.ledger_book.post(LedgerEvent(
                event_id=f"P:{account}:{n}", account_id=account,
                event_type=LedgerEventType.PAYMENT_CREDIT, amount_gbp=50.0, valid_time=paid,
                transaction_time=dt.datetime.combine(paid, dt.time(0, 0)), invoice_ref=f"{n}"))
    if pay_once_on is not None:
        consumer.ledger_book.post(LedgerEvent(
            event_id=f"P1:{account}", account_id=account, event_type=LedgerEventType.PAYMENT_CREDIT,
            amount_gbp=10.0, valid_time=pay_once_on,
            transaction_time=dt.datetime.combine(pay_once_on, dt.time(0, 0)), invoice_ref=None))
    consumer.advance_collections_journey(account, THROUGH)
    journeys = consumer.collections_journeys.journeys()
    for j in journeys:
        assert_journey_order_lawful(j, Segment.RESIDENTIAL)
    stages = [s for j in journeys for s in j["stages"]]
    write_offs = [e for e in consumer.ledger_book.ledger(account).events()
                  if e.event_type == LedgerEventType.WRITE_OFF_CREDIT]
    return stages, write_offs


def test_an_unpaid_live_debt_reaches_a_further_step_or_a_named_write_off_and_a_paid_one_neither():
    unpaid, unpaid_wo = _walk("ACC-NEVER")
    paid, paid_wo = _walk("ACC-PAYS", paid_months=range(86))
    names = [s["stage"] for s in unpaid]

    reoffered = PLAN_REOFFER_STEP in names
    written_off = WRITE_OFF in names and bool(unpaid_wo)
    paid_reaches_neither = not paid and not paid_wo
    assert reoffered and written_off and paid_reaches_neither

    # The re-offer comes after the plan offer's own offer (from that rung up, since "One case, one
    # climb"), a re-offer stands past the top rung too, and each one makes an offer.
    first = names.index(PLAN_REOFFER_STEP)
    assert names.index(PLAN_OFFER_STEP) < names.index(ARRANGEMENT_OFFERED) < first
    assert PLAN_REOFFER_STEP in names[names.index(PREPAYMENT_OFFERED):]
    assert names[first + 1] == ARRANGEMENT_OFFERED
    # The write-off names its rule, falls six years after the first bill's due date, and posts that
    # bill to the ledger as STATUTE_BARRED, not the whole balance.
    wo = next(s for s in unpaid if s["stage"] == WRITE_OFF)
    assert wo["rule"] == STATUTE_BAR_RULE
    assert wo["on"] == "2022-01-15"
    assert wo["written_off_gbp"] == 50.0
    assert "statute_barred" in unpaid_wo[0].reason
    assert "write_off" not in UNREACHED_EXITS


def test_a_payment_inside_six_years_restarts_the_bar():
    stages, write_offs = _walk("ACC-ONCE", pay_once_on=dt.date(2020, 6, 1))
    assert WRITE_OFF not in [s["stage"] for s in stages] and not write_offs
    assert PLAN_REOFFER_STEP in [s["stage"] for s in stages]


def test_the_bar_reads_both_clocks():
    consumer = PaymentObservationConsumer(ledger_book=LedgerBook())
    ledger = consumer.ledger_book.ledger("ACC-B")
    ledger.post(LedgerEvent(event_id="b", account_id="ACC-B", event_type=LedgerEventType.BILL_DEBIT,
                            amount_gbp=80.0, valid_time=START,
                            transaction_time=dt.datetime.combine(START, dt.time(0, 0))))
    assert statute_barred_gbp(ledger, dt.date(2022, 1, 14)) == 0.0
    assert statute_barred_gbp(ledger, dt.date(2022, 1, 15)) == 80.0


def test_a_reoffer_with_no_offer_after_it_is_unlawful():
    journey = {"account_id": "A", "exit": None, "stages": [
        {"stage": "missed_payment", "on": "2016-01-16"},
        {"stage": PREPAYMENT_STEP, "on": "2016-04-14"},
        {"stage": PREPAYMENT_OFFERED, "on": "2016-04-14"},
        {"stage": PLAN_REOFFER_STEP, "on": "2016-05-16"},
    ]}
    with pytest.raises(UnlawfulJourneyOrderError, match=PLAN_REOFFER_STEP):
        assert_journey_order_lawful(journey, Segment.RESIDENTIAL)
