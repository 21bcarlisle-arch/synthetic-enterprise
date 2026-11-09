"""A household that leaves level direct debit with a debit is sent one closing statement, due 28 days
later, and is dunned on that debit only if the statement goes unpaid.

The defect this names: once d8264b525e walked a left-level account on its bills, the debit its scheme
had not yet recovered was aged from the due dates of the level-paid bills it sat on. No one had asked
for those as debts, so the household opened a journey weeks overdue the day its first on-receipt bill
fell due, and could reach the plan-offer rung over money it was never asked for. The K8 entry is
`docs/market_research/payments_and_direct_debit_2026-10-25.md`, "Leaving level direct debit with a
debit".

The fixture is a winter leg on a GBP 60 level amount. October to December are level-paid (GBP 320 of
bills, GBP 180 collected), so it leaves level on 31 Jan 2025 with GBP 140 of scheme debit. January's
on-receipt bill (GBP 150, due 14 Feb) is collected on its due date. The closing statement is due on
28 Feb.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent
from company.billing.account_ledger import LedgerEventType as T
from company.billing.arrears_engine import CLOSING_STATEMENT_TERM_DAYS, dunning_path
from company.billing.collections_journey import MISSED_PAYMENT, PLAN_OFFER_STEP
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.crm.account_hierarchy import Segment

D = dt.date
LEFT = D(2025, 1, 31)
STATEMENT_DUE = LEFT + dt.timedelta(days=CLOSING_STATEMENT_TERM_DAYS)


def _ev(kind, account, gbp, on, n):
    return LedgerEvent(f"{kind.value}:{account}:{n}", account, kind, gbp, on,
                       dt.datetime.combine(on, dt.time()), f"{account}::{n}")


def _leaver(name, *, pay_january=True, returned=None, later=(), credit_note=None):
    """The fixture account, its journeys walked to 30 Jun 2025. `returned` is a level collection date
    the bank returned; `later` is extra `(date, GBP)` cash; `credit_note` a GBP credit on 1 Oct 2024."""
    account = f"ACC-{name}"
    c = PaymentObservationConsumer(ledger_book=LedgerBook())
    if credit_note is not None:
        c.ledger_book.post(_ev(T.ADJUSTMENT_CREDIT, account, credit_note, D(2024, 10, 1), 9))
    for n, (on, gbp) in enumerate([(D(2024, 10, 31), 70.0), (D(2024, 11, 30), 110.0),
                                   (D(2024, 12, 31), 140.0), (LEFT, 150.0)], 1):
        c.ledger_book.post(_ev(T.BILL_DEBIT, account, gbp, on, n))
    requests = []
    for n, on in enumerate([D(2024, 11, 5), D(2024, 12, 5), D(2025, 1, 5)], 1):
        requests.append((on, 60.0, f"{account}::{n}"))
        if on != returned:
            c.ledger_book.post(_ev(T.PAYMENT_CREDIT, account, 60.0, on, 10 + n))
    c._level_requests[account] = requests
    if returned is not None:
        c._dd_failures[account] = [type("F", (), {"value_date": returned})()]
    if pay_january:
        c.ledger_book.post(_ev(T.PAYMENT_CREDIT, account, 150.0, D(2025, 2, 14), 20))
    for n, (on, gbp) in enumerate(later, 30):
        c.ledger_book.post(_ev(T.PAYMENT_CREDIT, account, gbp, on, n))
    c.advance_collections_journey(account, D(2025, 6, 30))
    return c.collections_journeys.journeys()


def test_an_unpaid_closing_statement_opens_and_one_paid_inside_its_term_never_does():
    """The partition, both branches first: a desk that never opens passes the paid leg, and one that
    ages the scheme's bills from their own due dates opens on the paid leg (15 Feb, 32 days
    overdue, before this build)."""
    unpaid = _leaver("UNPAID")
    paid = _leaver("PAID", later=[(D(2025, 2, 20), 140.0)])
    paid_on_the_due_date = _leaver("PAID-ON-DUE", later=[(STATEMENT_DUE, 140.0)])
    assert unpaid and not paid and not paid_on_the_due_date, (unpaid, paid, paid_on_the_due_date)

    stages = unpaid[0]["stages"]
    # The debt clock starts at the statement's due date: the journey opens the day after it...
    assert stages[0]["stage"] == MISSED_PAYMENT
    assert stages[0]["on"] == (STATEMENT_DUE + dt.timedelta(days=1)).isoformat(), stages[0]
    # ...at the statement's amount, not the balance aged from the December bill...
    assert stages[0]["overdue_gbp"] == pytest.approx(140.0) and stages[0]["days_overdue"] == 1
    # ...and climbs from the first rung, never starting on the plan offer.
    first_rung = next(s for s in stages if s["stage"] != MISSED_PAYMENT)
    assert first_rung["stage"] == dunning_path(Segment.RESIDENTIAL)[0].action, first_rung
    assert first_rung["stage"] != PLAN_OFFER_STEP
    offer = next(s for s in stages if s["stage"] == PLAN_OFFER_STEP)
    assert D.fromisoformat(offer["on"]) >= STATEMENT_DUE + dt.timedelta(days=28), offer


def test_a_missed_on_receipt_bill_is_still_dunned_on_its_own_due_date():
    """The statement re-dates only the scheme's bills. January's bill, issued the day the household
    left, is an ordinary bill: missed, it opens on 15 Feb at its own GBP 150, with the statement's
    GBP 140 not yet due and so not printed overdue until 1 Mar."""
    journeys = _leaver("JAN-MISSED", pay_january=False)
    stages = journeys[0]["stages"]
    assert stages[0]["on"] == "2025-02-15" and stages[0]["overdue_gbp"] == pytest.approx(150.0)
    after = [s for s in stages if D.fromisoformat(s["on"]) > STATEMENT_DUE]
    assert after and after[0]["overdue_gbp"] == pytest.approx(290.0), after


def test_an_instalment_missed_before_leaving_is_not_forgiven_by_the_statement():
    """January's GBP 60 level collection is returned on 5 Jan and never made good. The journey that
    opened on 6 Jan must not cure on the day the household leaves just because the statement that
    re-dates its scheme debit is not yet due: the missed GBP 60 stays owed from 5 Jan."""
    journeys = _leaver("RETURNED", returned=D(2025, 1, 5))
    assert journeys and journeys[0]["stages"][0]["on"] == "2025-01-06", journeys
    cured = [s["on"] for j in journeys for s in j["stages"] if s["stage"] == "cured"]
    assert cured == [], cured


def test_a_return_no_journey_held_goes_on_the_statement_not_back_to_its_request():
    """The other side of the test above. December's collection comes back on 5 Dec while a credit note
    keeps the account square, so nothing is dunned. On leaving it still reads GBP 60 short of its
    schedule. That shortfall was never pursued, so it is demanded on the statement with the rest of
    the GBP 80 debit: the journey opens on 1 Mar at GBP 80. Dated back to 5 Dec instead, January's
    payment would meet it first and January's bill would open on 15 Feb (SYN-2016-217 on 9d7dcfc19c:
    first contact 130 days overdue, on the prepayment rung)."""
    journeys = _leaver("NEVER-DUNNED", returned=D(2024, 12, 5), credit_note=120.0)
    assert journeys, "the unpaid statement must open a journey, or the date below proves nothing"
    first = journeys[0]["stages"][0]
    assert first["on"] == (STATEMENT_DUE + dt.timedelta(days=1)).isoformat(), first
    assert first["overdue_gbp"] == pytest.approx(80.0) and first["days_overdue"] == 1, first
