"""A household leaving level direct debit is dunned on what each supply leg owes, not on one pool.

On the 78f82e4242 book the desk opened two journeys inside the closing statement's term
(INV_OVERDUE_WITHIN_BALANCE; SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL_..._2026-11-07.md):
SYN-2016-007 was dunned GBP 9.20 the day after paying its electricity final bill, and SYN-2016-496
GBP 45.48, 61 days, from electricity bills its standing credit had paid. Each account's gas leg had
left level DD with a scheme debit. `left_level_asks` met every bill from one account-wide pool, oldest
first, so the gas debit landed on the electricity leg's newer, paid, on-receipt bills, and those aged
from their own due dates. The scheme's debit is owed on the closing statement
(payments_and_direct_debit_2026-10-25.md, "Leaving level direct debit with a debit").

Here, gas G is level at GBP 20 against bills of 20 and 60, then leaves on a GBP 5 final bill on
10 Dec; electricity E pays two GBP 30 bills by their own direct debits.
"""
from __future__ import annotations

import datetime as dt

from company.billing.account_ledger import AccountLedger, LedgerEvent
from company.billing.account_ledger import LedgerEventType as T
from company.billing.arrears_engine import (
    CLOSING_STATEMENT_TERM_DAYS,
    LevelSchedule,
    age_left_level,
    cash_leg,
    left_level_asks,
    observed_cash_event_id,
)

D = dt.date
TS = dt.datetime(2020, 1, 1)
LEFT = D(2019, 12, 10)
ON = D(2019, 12, 11)


def _bill(ref, on, gbp):
    return LedgerEvent("b" + ref, "ACC", T.BILL_DEBIT, gbp, on, TS, invoice_ref=ref)


def _cash(correlation_id, on, gbp):
    return LedgerEvent(observed_cash_event_id(correlation_id), "ACC", T.PAYMENT_CREDIT, gbp, on, TS)


def _ledger(e2_collected=True, extra=()):
    led = AccountLedger("ACC")
    events = [
        _bill("G::1", D(2019, 10, 1), 20.0), _cash("G::1", D(2019, 9, 25), 20.0),
        _bill("G::2", D(2019, 11, 1), 60.0), _cash("G::2", D(2019, 10, 25), 20.0),
        _bill("G::3", LEFT, 5.0),
        _bill("E::1", D(2019, 10, 5), 30.0), _cash("E::1", D(2019, 10, 19), 30.0),
        _bill("E::2", D(2019, 11, 5), 30.0),
        *extra,
    ]
    if e2_collected:
        events.append(_cash("E::2", D(2019, 11, 19), 30.0))
    for e in events:
        led.post(e)
    schedule = LevelSchedule(requests=((D(2019, 9, 25), 20.0, "G::1"), (D(2019, 10, 25), 20.0, "G::2")))
    return led, schedule


def _overdue(led, schedule, on=ON):
    left = left_level_asks(led, schedule, on)
    assert left is not None and left.left == LEFT
    return round(sum(i.outstanding_gbp for i in age_left_level(led, left, on) if i.days_overdue > 0), 2)


def test_a_paid_on_receipt_bill_is_not_overdue_and_an_unpaid_one_is():
    """The partition first: the same account, its second electricity bill collected or returned."""
    paid, returned = _overdue(*_ledger()), _overdue(*_ledger(e2_collected=False))
    assert (paid, returned) == (0.0, 30.0), (
        "a leaver's own-leg bill paid by its own collection must not be dunned for the other leg's "
        f"scheme debit, and one whose collection failed must be (paid {paid}, returned {returned})")


def test_the_scheme_debit_is_owed_on_the_closing_statement():
    led, schedule = _ledger()
    left = left_level_asks(led, schedule, ON)
    due = LEFT + dt.timedelta(days=CLOSING_STATEMENT_TERM_DAYS)
    assert (due, 40.0) in left.asks, left.asks
    # and past its term it is overdue, beside the unpaid GBP 5 final bill due 24 Dec
    assert _overdue(led, schedule, due + dt.timedelta(days=1)) == 45.0


def test_a_legs_surplus_and_unnamed_cash_meet_the_other_legs_debit():
    """A leg in credit nets against the account: what is left of each leg's own cash, and cash that
    names no leg (a plan instalment), go to what remains, oldest first."""
    plan = LedgerEvent("plan:1", "ACC", T.PAYMENT_CREDIT, 15.0, D(2019, 12, 1), TS)
    surplus = _cash("E::1b", D(2019, 11, 25), 10.0)
    led, schedule = _ledger(extra=(plan, surplus))
    assert (cash_leg(plan), cash_leg(surplus)) == (None, "E")
    left = left_level_asks(led, schedule, ON)
    assert (LEFT + dt.timedelta(days=CLOSING_STATEMENT_TERM_DAYS), 15.0) in left.asks, left.asks
