"""A supply leg that leaves level direct debit while the account's other leg stays on it owes its scheme's
debit on its own closing statement, and the desk's cure needs that statement met.

The defect this names: `on_level_dd` keeps a mixed account on the schedule while any leg is level, and
`level_shortfall` asked only the schedule's requests and the bills no collection paid. The leaver's
scheme debit was asked by nothing, so the desk cured over it. SYN-2016-536 on 78f82e4242 was cured on
16 Feb 2023 while its gas leg owed GBP 132.02, a closing statement the page prints included. The
account statement (`left_level_asks`) waits for the last level leg to leave, so it was dated from the
account's leaving, not the leg's (SYN-2016-345). K8: `docs/market_research/payments_and_direct_debit_
2026-10-25.md`, "The debit a leaver owes is its leg's" and "Leaving level direct debit with a debit".

The fixture: gas G is level at GBP 60 against bills of 70, 110 and 140, so it leaves on 31 Jan 2025
with GBP 140 of scheme debit. Its January on-receipt bill (GBP 150) is paid on its due date. Its
statement falls due on 28 Feb. Electricity E stays level at GBP 50. Its 5 Dec collection is returned,
which opens the journey, and the household makes it good on 1 Mar.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_ledger import AccountLedger, LedgerBook, LedgerEvent
from company.billing.account_ledger import LedgerEventType as T
from company.billing.arrears_engine import (
    CLOSING_STATEMENT_TERM_DAYS,
    LevelSchedule,
    left_level_asks,
    leg_leave_dates,
    leg_statement_asks,
    level_shortfall,
    observed_cash_event_id,
)
from company.billing.collections_journey import CURED
from company.billing.payment_observation_consumer import PaymentObservationConsumer

D = dt.date
ACC = "ACC-MIX"
LEFT = D(2025, 1, 31)
DUE = LEFT + dt.timedelta(days=CLOSING_STATEMENT_TERM_DAYS)
MADE_GOOD = D(2025, 3, 1)
_n = iter(range(10_000))


def _ev(kind, gbp, on, ref=None, event_id=None):
    return LedgerEvent(event_id or f"e{next(_n)}", ACC, kind, gbp, on,
                       dt.datetime.combine(on, dt.time()), ref)


def _cash(gbp, on, crossing):
    """Cash this company observed on `crossing`, whose reference names the leg it was paid to."""
    return _ev(T.PAYMENT_CREDIT, gbp, on, event_id=observed_cash_event_id(f"{crossing}:{next(_n)}"))


def _events(*, statement_paid_on=None, g2_returned=False, g_credit_note=0.0, e_leaves=False,
            g4_paid=True, e_returned=True):
    """The fixture's events and level requests. `e_leaves` puts E on receipt from 28 Feb."""
    events, requests = [], []
    for n, (on, gbp, ask_on) in enumerate([(D(2024, 10, 31), 70.0, D(2024, 11, 5)),
                                           (D(2024, 11, 30), 110.0, D(2024, 12, 5)),
                                           (D(2024, 12, 31), 140.0, D(2025, 1, 5))], 1):
        events.append(_ev(T.BILL_DEBIT, gbp, on, f"G::{n}"))
        requests.append((ask_on, 60.0, f"G::{n}"))
        if not (g2_returned and n == 2):
            events.append(_cash(60.0, ask_on, f"G::{n}"))
    events.append(_ev(T.BILL_DEBIT, 150.0, LEFT, "G::4"))
    if g4_paid:
        events.append(_cash(150.0, D(2025, 2, 14), "G::4"))
    if g_credit_note:
        events.append(_ev(T.ADJUSTMENT_CREDIT, g_credit_note, D(2024, 11, 30), event_id="credit:G:2"))
    e_months = [D(2024, 10, 31), D(2024, 11, 30), D(2024, 12, 31), D(2025, 1, 31), D(2025, 2, 28)]
    for n, on in enumerate(e_months, 1):
        events.append(_ev(T.BILL_DEBIT, 50.0, on, f"E::{n}"))
        ask_on = D(on.year + on.month // 12, on.month % 12 + 1, 5)
        if e_leaves and n == len(e_months):
            continue  # its last bill is not collected by the schedule: E leaves on 28 Feb
        requests.append((ask_on, 50.0, f"E::{n}"))
        if ask_on != D(2024, 12, 5) or not e_returned:
            events.append(_cash(50.0, ask_on, f"E::{n}"))
    if e_returned:
        events.append(_cash(50.0, MADE_GOOD, "E::2"))  # E's returned instalment, made good
    if statement_paid_on is not None:
        events.append(_cash(140.0, statement_paid_on, "G::stmt"))
    return events, requests


def _schedule(**kw):
    """The ledger and the schedule `PaymentObservationConsumer.level_schedule_of` would build: a bill no
    level collection paid for is asked on its own due date, 14 days after issue."""
    events, requests = _events(**kw)
    led = AccountLedger(ACC)
    for e in events:
        led.post(e)
    level_refs = {ref for _d, _g, ref in requests}
    other = tuple((e.valid_time + dt.timedelta(days=14), e.amount_gbp) for e in events
                  if e.event_type == T.BILL_DEBIT and e.invoice_ref not in level_refs)
    return led, LevelSchedule(requests=tuple(sorted(requests)), other_asks=other)


def _journeys(**kw):
    events, requests = _events(**kw)
    c = PaymentObservationConsumer(ledger_book=LedgerBook())
    for e in events:
        c.ledger_book.post(e)
    c._level_requests[ACC] = sorted(requests)
    if kw.get("e_returned", True):
        c._dd_failures[ACC] = [type("F", (), {"value_date": D(2024, 12, 5)})()]
    c.advance_collections_journey(ACC, D(2025, 4, 30))
    return c.collections_journeys.journeys()


def _path(j):
    return [(s["stage"], s["on"], s["overdue_gbp"]) for s in j["stages"]]


def test_an_unpaid_leg_statement_opens_a_journey_and_holds_it_until_it_is_met():
    """The partition, both branches first. E pays every instalment. Before this build the unpaid
    statement opened nothing: no ask held the gas scheme's debit while E stayed level."""
    unpaid = _journeys(e_returned=False)
    paid_late = _journeys(e_returned=False, statement_paid_on=D(2025, 3, 20))
    paid_on_time = _journeys(e_returned=False, statement_paid_on=DUE)
    assert unpaid and paid_late and not paid_on_time, (unpaid, paid_late, paid_on_time)
    opened = unpaid[0]["stages"][0]
    assert (opened["on"], opened["overdue_gbp"]) == ((DUE + dt.timedelta(days=1)).isoformat(), 140.0)
    assert unpaid[0]["exit"] != CURED, _path(unpaid[0])
    assert paid_late[0]["exit"] == CURED and paid_late[0]["stages"][-1]["on"] == "2025-03-20", (
        _path(paid_late[0]))


def test_cash_paying_the_other_legs_bill_on_its_due_date_does_not_cure_a_missed_instalment():
    """SYN-2016-536's day, 16 Feb 2023. E's 5 Dec instalment is returned and made good on 1 Mar. G
    pays its January bill on its due date, 14 Feb, and its statement on its due date. Before this
    build the 14 Feb cash, counted before the bill it paid was asked, met E's missed request: the
    journey cured on 14 Feb and a second opened on 15 Feb over the same GBP 50."""
    journeys = _journeys(statement_paid_on=DUE)
    assert len(journeys) == 1, [_path(j) for j in journeys]
    assert journeys[0]["exit"] == CURED and journeys[0]["stages"][-1]["on"] == MADE_GOOD.isoformat(), (
        _path(journeys[0]))


def test_the_statement_is_the_legs_scheme_debit_due_from_its_own_leaving():
    led, schedule = _schedule(e_returned=False)
    one = leg_leave_dates(led, schedule, D(2025, 3, 31))
    assert set(one) == {"G"} and one["G"].left == LEFT and one["G"].scheme_debit_gbp == 140.0, one
    assert leg_statement_asks(led, schedule, D(2025, 3, 31)) == [(DUE, 140.0)]
    # Nothing is asked before its due date; from that day it is, and overdue the day after.
    assert level_shortfall(led, schedule, DUE - dt.timedelta(days=1)) is None
    on_due, after = (level_shortfall(led, schedule, d) for d in (DUE, DUE + dt.timedelta(days=1)))
    assert on_due is not None and (on_due.outstanding_gbp, on_due.days_overdue) == (140.0, 0), on_due
    assert after is not None and (after.outstanding_gbp, after.due_date) == (140.0, DUE), after


def test_a_returned_request_is_counted_once_not_again_on_the_statement():
    """The schedule already asks a returned instalment, so the statement is the debit beyond it."""
    led, schedule = _schedule(g2_returned=True)
    assert leg_statement_asks(led, schedule, D(2025, 3, 31)) == [(DUE, 140.0)]
    assert level_shortfall(led, schedule, MADE_GOOD).outstanding_gbp == 200.0


def test_the_legs_own_credit_note_comes_off_its_statement():
    led, schedule = _schedule(g_credit_note=25.0)
    assert leg_statement_asks(led, schedule, D(2025, 3, 31)) == [(DUE, 115.0)]


def test_a_leg_leaving_with_the_account_is_the_account_statements_and_dated_from_its_own_leaving():
    """When E leaves too, the account statement takes over (no leg statement on top), and G's part of
    it stays due from G's own leaving, not the account's (SYN-2016-345). G's January bill is unpaid,
    so G's own cash leaves the remainder on its last level-paid bill, which is the statement's."""
    led, schedule = _schedule(e_leaves=True, g4_paid=False)
    assert leg_statement_asks(led, schedule, D(2025, 4, 30)) == [(DUE, 140.0)]
    left = left_level_asks(led, schedule, D(2025, 4, 30))
    assert left is not None and left.left == D(2025, 2, 28), left
    g_part = [gbp for due, gbp in left.asks if due == DUE]
    assert g_part == [pytest.approx(140.0)], left.asks
    assert all(due != D(2025, 2, 28) + dt.timedelta(days=CLOSING_STATEMENT_TERM_DAYS)
               or gbp < 140.0 for due, gbp in left.asks), left.asks
