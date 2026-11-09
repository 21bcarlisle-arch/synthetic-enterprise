"""A level direct debit leg whose month asks nothing has not left level DD.

The defect this names: `arrears_engine.on_level_dd` read a leg as on level only while its latest bill
was one a level collection paid for. In a month the Energy Bills Support Scheme credit covered the
whole bill, or the level amount was GBP 0, nothing is presented, so that bill is paid by no level
collection, and the leg read as having left. It was then dunned on its bills until the next level
bill was issued. On the 505df564e3 page ledger, 6 accounts that went on collecting level read as
having left this way, on 359 account-days, all in Nov 2022 to Apr 2023. K8: `docs/market_research/payments_and_direct_debit_
2026-10-25.md`, "A month the level schedule asks nothing of is not a departure".

The fixture is one leg on a GBP 50 level amount. Sep and Oct bills are level-paid. November's bill is
covered whole by the scheme credit, so the in-run ledger posts it at GBP 0. December's level amount
is GBP 0, so its GBP 40 bill asks nothing. January is level-paid again.
"""
from __future__ import annotations

import datetime as dt

from company.billing.account_ledger import LedgerBook, LedgerEvent
from company.billing.account_ledger import LedgerEventType as T
from company.billing.arrears_engine import level_leave_dates, on_level_dd
from company.billing.payment_observation_consumer import PaymentObservationConsumer

D = dt.date
ACC = "ACC-NIL"


def _ev(kind, gbp, on, n):
    return LedgerEvent(f"{kind.value}:{ACC}:{n}", ACC, kind, gbp, on, dt.datetime.combine(on, dt.time()),
                       f"{ACC}::{n}")


def _consumer(*, leave_in_february: bool):
    """The fixture leg. With `leave_in_february`, February's GBP 70 bill is presented to nobody: the
    household has left, and the bill asks its face."""
    c = PaymentObservationConsumer(ledger_book=LedgerBook())
    bills = [(D(2022, 9, 30), 45.0, 1), (D(2022, 10, 31), 55.0, 2), (D(2022, 11, 30), 0.0, 3),
             (D(2022, 12, 31), 40.0, 4), (D(2023, 1, 31), 65.0, 5)]
    if leave_in_february:
        bills.append((D(2023, 2, 28), 70.0, 6))
    for on, gbp, n in bills:
        c.ledger_book.post(_ev(T.BILL_DEBIT, gbp, on, n))
    c.collections_journeys.note_bill_asked(f"{ACC}::4", 0.0)  # the level amount was GBP 0
    requests = [(D(2022, 9, 20), 50.0, f"{ACC}::1"), (D(2022, 10, 20), 50.0, f"{ACC}::2"),
                (D(2023, 1, 20), 50.0, f"{ACC}::5")]
    for n, (on, gbp, _ref) in enumerate(requests, 10):
        c.ledger_book.post(_ev(T.PAYMENT_CREDIT, gbp, on, n))
    c._level_requests[ACC] = requests
    return c


def test_a_nil_month_keeps_the_leg_on_level_and_a_billed_month_off_it_still_reads_as_leaving():
    """The partition, both branches first: a predicate that always reads level passes the first half,
    and the one this replaces reads the nil months as leaving."""
    stays, leaves = _consumer(leave_in_february=False), _consumer(leave_in_february=True)
    s_led, s_sched = stays.ledger_book.ledger(ACC), stays.level_schedule_of(ACC)
    l_led, l_sched = leaves.ledger_book.ledger(ACC), leaves.level_schedule_of(ACC)
    nil_days = [D(2022, 11, 30), D(2022, 12, 15), D(2022, 12, 31), D(2023, 1, 19)]
    assert all(on_level_dd(s_led, s_sched, d) for d in nil_days), [
        d for d in nil_days if not on_level_dd(s_led, s_sched, d)]
    assert not on_level_dd(l_led, l_sched, D(2023, 3, 1))
    assert level_leave_dates(s_led, s_sched, D(2023, 3, 31)) == []
    assert level_leave_dates(l_led, l_sched, D(2023, 3, 31)) == [D(2023, 2, 28)]


def test_a_nil_month_on_a_level_leg_opens_no_journey():
    """What the reading is for: the desk walks a still-level leg on its schedule, which every
    collection met, so nothing is owed and nothing opens. Read as a leaver, the GBP 40 December bill
    asked nothing and the leg was dunned on its bills."""
    c = _consumer(leave_in_february=False)
    c.advance_collections_journey(ACC, D(2023, 3, 31))
    assert c.collections_journeys.journeys() == []
