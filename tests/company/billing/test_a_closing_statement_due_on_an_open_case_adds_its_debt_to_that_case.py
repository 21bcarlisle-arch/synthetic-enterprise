"""A closing statement that falls due while the account's collections journey is open adds its GBP to
that case, and holds it open until paid.

The desk ignores an opener for an account it holds open (`CollectionsJourneyDesk.advance`), so when a
leaver's statement falls due on an open case, the open case is the only thing that can carry that
debt. On the 2016 run, four leavers had a case open on their statement's due date. For three of
them the statement asked nothing new: the shortfall stayed on the request the case was already
dunning. SYN-2016-012's case took the statement's GBP 10.57 on the day after it fell due
(docs/staging/done/SEAT_FINDING_A_CLOSING_STATEMENT_DUE_ON_AN_OPEN_JOURNEY_2026-11-15.md).

The case carries a debt in two places, and both are pinned. The first is what it reads as owed: the
view the desk steps on counts the statement's GBP as overdue from the day after its due date. The
second is what holds it open: it may not cure while the statement is unpaid.

The fixture: electricity E, one leg, level at GBP 50 against bills of 60, 60 and 90. The 5 Dec
collection is returned with the account in debt, so a journey opens on 6 Dec, dunning the GBP 50
shortfall. E leaves on 31 Jan 2025 with that journey open, so the shortfall stays owed from its
request (`left_level_asks`, `dunned_at`). The rest of the scheme debit, GBP 60, goes on the closing
statement due 28 Feb. The January on-receipt bill (GBP 40, due 14 Feb) is paid on its due date.
"""
from __future__ import annotations

import datetime as dt

import company.billing.arrears_engine as ae
import company.billing.collections_journey as cj
from company.billing.account_ledger import LedgerBook, LedgerEvent
from company.billing.account_ledger import LedgerEventType as T
from company.billing.arrears_engine import CLOSING_STATEMENT_TERM_DAYS, observed_cash_event_id
from company.billing.payment_observation_consumer import PaymentObservationConsumer

D = dt.date
ACC = "ACC-ONE"
LEFT = D(2025, 1, 31)
DUE = LEFT + dt.timedelta(days=CLOSING_STATEMENT_TERM_DAYS)
AFTER = DUE + dt.timedelta(days=1)
RETURNED = D(2024, 12, 5)
OPENED = RETURNED + dt.timedelta(days=1)
SHORTFALL, STATEMENT = 50.0, 60.0
_n = iter(range(10_000))


def _ev(kind, gbp, on, ref=None, event_id=None):
    return LedgerEvent(event_id or f"e{next(_n)}", ACC, kind, gbp, on,
                       dt.datetime.combine(on, dt.time()), ref)


def _cash(gbp, on, crossing):
    return _ev(T.PAYMENT_CREDIT, gbp, on, event_id=observed_cash_event_id(f"{crossing}:{next(_n)}"))


def _desk(*payments):
    """The desk walked to 30 Apr 2025, and the overdue GBP of every view it stepped on."""
    events, requests = [], []
    for n, (on, gbp, ask_on) in enumerate([(D(2024, 10, 31), 60.0, D(2024, 11, 5)),
                                           (D(2024, 11, 30), 60.0, RETURNED),
                                           (D(2024, 12, 31), 90.0, D(2025, 1, 5))], 1):
        events.append(_ev(T.BILL_DEBIT, gbp, on, f"E::{n}"))
        requests.append((ask_on, 50.0, f"E::{n}"))
        if ask_on != RETURNED:
            events.append(_cash(50.0, ask_on, f"E::{n}"))
    events.append(_ev(T.BILL_DEBIT, 40.0, LEFT, "E::4"))
    events.append(_cash(40.0, LEFT + dt.timedelta(days=14), "E::4"))
    events += [_cash(gbp, on, "E::pay") for gbp, on in payments]
    c = PaymentObservationConsumer(ledger_book=LedgerBook())
    for e in events:
        c.ledger_book.post(e)
    c._level_requests[ACC] = sorted(requests)
    c._dd_failures[ACC] = [type("F", (), {"value_date": RETURNED})()]
    seen = {}
    view_at = c.collections_journeys._view_at

    def _seen(account_id, segment, on):
        view = view_at(account_id, segment, on)
        seen[on] = view.get("undisputed_overdue_gbp")
        return view
    c.collections_journeys._view_at = _seen
    c.advance_collections_journey(ACC, D(2025, 4, 30))
    return c.collections_journeys.journeys(), seen


def test_the_statement_falls_due_on_an_open_case():
    """The premise: one journey, opened on the returned collection, still open past the statement.
    No second journey opens on the statement, since the desk ignores an opener for an open account."""
    journeys, _seen = _desk()
    assert len(journeys) == 1, [j["stages"][0] for j in journeys]
    assert journeys[0]["stages"][0]["on"] == OPENED.isoformat()
    assert journeys[0]["exit"] is None


def test_the_case_reads_the_statement_as_overdue_from_the_day_after_it_falls_due():
    """The desk steps on the statement's due date and the day after. The GBP 60 is not yet overdue
    on the due date and is overdue the day after, on top of the shortfall."""
    _journeys, seen = _desk()
    assert DUE in seen and AFTER in seen, sorted(seen)
    assert (seen[DUE], seen[AFTER]) == (SHORTFALL, SHORTFALL + STATEMENT)


def test_paying_the_shortfall_alone_after_the_statement_falls_due_does_not_cure_the_case():
    """Both sides: the shortfall alone leaves the statement owed and the case open; paying both
    cures it that day."""
    paid = D(2025, 3, 10)
    part, seen = _desk((SHORTFALL, paid))
    whole, _ = _desk((SHORTFALL + STATEMENT, paid))
    assert len(part) == 1 and part[0]["exit"] is None, part[0]["stages"]
    assert seen[paid] == STATEMENT
    assert len(whole) == 1 and whole[0]["exit"] == cj.CURED, whole[0]["stages"]
    assert whole[0]["stages"][-1]["on"] == paid.isoformat()


def test_a_case_cured_before_the_statement_falls_due_leaves_the_statement_to_open_its_own():
    """The other side of the partition: when the shortfall is paid before the statement is due, the
    case cures, and the unpaid statement opens a second case the day after it falls due."""
    journeys, _seen = _desk((SHORTFALL, D(2025, 2, 20)))
    assert [j["exit"] for j in journeys] == [cj.CURED, None], [j["stages"] for j in journeys]
    opened = journeys[1]["stages"][0]
    assert (opened["on"], opened["overdue_gbp"]) == (AFTER.isoformat(), STATEMENT)


def test_the_debt_is_read_from_the_statements_own_due_date(monkeypatch):
    """A mutation of the statement's term in the ledger's demand (`left_level_asks`) moves the day the
    case reads the GBP 60 as overdue, so the control reads the statement and not today's answer."""
    monkeypatch.setattr(ae, "CLOSING_STATEMENT_TERM_DAYS", CLOSING_STATEMENT_TERM_DAYS + 30)
    _journeys, seen = _desk()
    assert seen.get(AFTER) == SHORTFALL
