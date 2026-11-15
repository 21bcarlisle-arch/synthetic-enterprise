"""A household that leaves level direct debit owing only what its account-wide closing statement asks
is dunned from that statement's due date, and from nothing else.

The branch this pins is the desk's account-wide statement opener (`level_leave_dates` plus
`CLOSING_STATEMENT_TERM_DAYS` in `CollectionsJourneyDesk.advance`). On the 2016 run it opens no
journey, and mutating its term to 0 changed nothing at 3c1bf2654. Of the ten 2016 leavers, five owed
nothing on the statement or had a leg statement (`leg_statement_asks`) that same day. The other five
had already opened a journey earlier that year, and the desk ignores an opener for an account it
already holds open (docs/staging/done/SEAT_FINDING_THE_ACCOUNT_WIDE_CLOSING_STATEMENT_OPENER_IS_
UNEXERCISED_ON_THE_2016_RUN_2026-11-15.md). The account branch is the sole opener when the last leg
leaves with NO scheme debit (its bills asked exactly what its collections did) and the debit is a
returned collection no journey held, the household being square when it came back.
`left_level_asks` puts that shortfall on the statement (SYN-2016-217, 9d7dcfc19c).

The fixture: electricity E, one leg, level at GBP 50 against bills of 30, 30 and 90, with GBP 10 of
credit paid in October. The 5 Dec collection is returned with the account square, so nothing opens.
E leaves on 31 Jan 2025 (its January bill, GBP 40, is on receipt and paid on its due date) owing GBP 40.
The statement falls due on 28 Feb.
"""
from __future__ import annotations

import datetime as dt

import company.billing.collections_journey as cj
from company.billing.account_ledger import AccountLedger, LedgerBook, LedgerEvent
from company.billing.account_ledger import LedgerEventType as T
from company.billing.arrears_engine import (
    CLOSING_STATEMENT_TERM_DAYS,
    LevelSchedule,
    leg_statement_asks,
    level_leave_dates,
    observed_cash_event_id,
)
from company.billing.payment_observation_consumer import PaymentObservationConsumer

D = dt.date
ACC = "ACC-ONE"
LEFT = D(2025, 1, 31)
DUE = LEFT + dt.timedelta(days=CLOSING_STATEMENT_TERM_DAYS)
RETURNED = D(2024, 12, 5)
_n = iter(range(10_000))


def _ev(kind, gbp, on, ref=None, event_id=None):
    return LedgerEvent(event_id or f"e{next(_n)}", ACC, kind, gbp, on,
                       dt.datetime.combine(on, dt.time()), ref)


def _cash(gbp, on, crossing):
    return _ev(T.PAYMENT_CREDIT, gbp, on, event_id=observed_cash_event_id(f"{crossing}:{next(_n)}"))


def _events(*, statement_paid_on=None):
    events = [_cash(10.0, D(2024, 10, 1), "E::0")]
    requests = []
    for n, (on, gbp, ask_on) in enumerate([(D(2024, 10, 31), 30.0, D(2024, 11, 5)),
                                           (D(2024, 11, 30), 30.0, RETURNED),
                                           (D(2024, 12, 31), 90.0, D(2025, 1, 5))], 1):
        events.append(_ev(T.BILL_DEBIT, gbp, on, f"E::{n}"))
        requests.append((ask_on, 50.0, f"E::{n}"))
        if ask_on != RETURNED:
            events.append(_cash(50.0, ask_on, f"E::{n}"))
    events.append(_ev(T.BILL_DEBIT, 40.0, LEFT, "E::4"))
    events.append(_cash(40.0, LEFT + dt.timedelta(days=14), "E::4"))
    if statement_paid_on is not None:
        events.append(_cash(40.0, statement_paid_on, "E::stmt"))
    return events, requests


def _journeys(**kw):
    events, requests = _events(**kw)
    c = PaymentObservationConsumer(ledger_book=LedgerBook())
    for e in events:
        c.ledger_book.post(e)
    c._level_requests[ACC] = sorted(requests)
    c._dd_failures[ACC] = [type("F", (), {"value_date": RETURNED})()]
    c.advance_collections_journey(ACC, D(2025, 4, 30))
    return c.collections_journeys.journeys()


def test_the_account_statement_is_the_only_obligation_left_unmet():
    """The premise: the leg asks nothing of its own, so only the account branch can open."""
    events, requests = _events()
    led = AccountLedger(ACC)
    for e in events:
        led.post(e)
    schedule = LevelSchedule(requests=tuple(sorted(requests)))
    assert level_leave_dates(led, schedule, D(2025, 4, 30)) == [LEFT]
    assert leg_statement_asks(led, schedule, D(2025, 4, 30)) == []


def test_an_unpaid_account_statement_opens_the_day_after_it_falls_due():
    """Both sides of the partition: unpaid opens, paid on its due date does not. Nothing opens on
    the returned collection, the household being square that day."""
    unpaid = _journeys()
    paid = _journeys(statement_paid_on=DUE)
    assert unpaid and not paid, (unpaid, paid)
    assert len(unpaid) == 1
    opened = unpaid[0]["stages"][0]
    assert (opened["stage"], opened["on"], opened["overdue_gbp"]) == (
        "missed_payment", (DUE + dt.timedelta(days=1)).isoformat(), 40.0)


def test_the_opener_is_read_from_the_statements_term(monkeypatch):
    """The mutation 3c1bf2654 could not fire on the run. At term 0 the desk looks on the day of
    leaving, when the statement is not yet due, and never again: the GBP 40 is never dunned."""
    monkeypatch.setattr(cj, "CLOSING_STATEMENT_TERM_DAYS", 0)
    assert _journeys() == []


def test_a_statement_paid_after_its_due_date_cures_the_journey():
    journeys = _journeys(statement_paid_on=DUE + dt.timedelta(days=7))
    assert journeys and journeys[0]["stages"][0]["on"] == (DUE + dt.timedelta(days=1)).isoformat()
    assert journeys[0]["exit"] == cj.CURED, journeys[0]["stages"]
