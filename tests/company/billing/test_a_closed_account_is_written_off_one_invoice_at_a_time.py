"""A closed account is written off one invoice at a time, so the per-debt learner can see each debt.

`cash_forecast_provision._written_off` drops a write-off with no `invoice_ref`: cash after it cannot be
told from cash for any other debt. Both of the company's closed-account write-offs (the month-end
sweep and the desk's) posted one balance-level write-off with no ref, so in-run the learner saw no
debt at all. Finding: `docs/staging/SEAT_FINDING_THE_HELD_PER_DEBT_SALE_RULE_LEARNS_A_WINDOW_THE_AGENCY_
NEVER_PAYS_INTO_2026-11-20.md`, "In-run successor". Knowledge: `docs/market_research/debt_and_collections.md`
s.7.7.
"""
import datetime as dt

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.arrears_engine import (
    CLOSED_ACCOUNT_RULE,
    closed_balance_write_offs,
    owed_by_invoice,
)
from company.finance.cash_forecast_provision import _written_off

ON = dt.date(2021, 3, 31)
T = LedgerEventType


def _at(day: dt.date) -> dt.datetime:
    return dt.datetime.combine(day, dt.time(0, 0))


def _book(*extra, refs=True):
    book = LedgerBook()
    for i, (gbp, day) in enumerate([(100.0, dt.date(2019, 12, 1)), (80.0, dt.date(2020, 1, 1)),
                                    (60.0, dt.date(2020, 2, 1))], start=1):
        book.post(LedgerEvent(f"b{i}", "A", T.BILL_DEBIT, gbp, day, _at(day),
                              invoice_ref=f"I{i}" if refs else None))
    for e in extra:
        book.post(e)
    return book


def _pay(eid, gbp, day, remittance=(), recorded=None):
    return LedgerEvent(eid, "A", T.PAYMENT_CREDIT, gbp, day, _at(recorded or day),
                       remittance=remittance)


def _swept(book):
    return [(e.invoice_ref, e.amount_gbp) for e in closed_balance_write_offs(book, ON, _at(ON))]


def test_each_open_invoice_is_written_off_under_its_own_ref_and_the_total_is_unchanged():
    """One control over the partition: ref'd pieces (newest first, cash earmarked to I2 respected)
    AND the no-ref remainder are both reached, and every piece sums to the balance.
    Defect: a sweep that drops the ref, or posts the balance as one lump."""
    earmarked = _book(_pay("p", 50.0, dt.date(2020, 1, 20), remittance=("I2",)))
    assert _swept(earmarked) == [("I3", 60.0), ("I2", 30.0), ("I1", 100.0)]
    assert earmarked.ledger("A").balance(ON) == 0.0
    no_refs = _book(refs=False)
    assert _swept(no_refs) == [(None, 240.0)]
    assert no_refs.ledger("A").balance(ON) == 0.0


def test_a_credit_note_comes_off_the_oldest_invoice_as_the_balance_takes_it():
    """Defect: the excess trimmed from the newest invoice, which would age the debt younger."""
    note = LedgerEvent("cn", "A", T.ADJUSTMENT_CREDIT, 20.0, dt.date(2020, 2, 20),
                       _at(dt.date(2020, 2, 20)))
    assert owed_by_invoice(_book(note).ledger("A"), ON, 220.0) == [
        ("I3", 60.0), ("I2", 80.0), ("I1", 80.0)]


def test_cash_recorded_after_the_sweep_does_not_move_the_split():
    """A payment dated before the sweep but recorded after it is not seen by the balance, so it must
    not be seen by the split either. Defect: the split read off the whole ledger, which here puts
    50 of the 240 on no invoice (hindsight the sweep on the day did not have)."""
    late = _pay("late", 50.0, dt.date(2020, 1, 20), remittance=("I2",),
                recorded=dt.date(2021, 6, 1))
    assert _swept(_book(late)) == [("I3", 60.0), ("I2", 80.0), ("I1", 100.0)]


def test_the_learner_reads_a_swept_debt_once_cash_is_earmarked_to_it():
    """The point of the ref: cash after the write-off against I1 is that debt's recovery.
    Defect: a write-off the learner cannot see (`_written_off` returns nothing)."""
    book = _book()
    closed_balance_write_offs(book, ON, _at(ON))
    paid = ON + dt.timedelta(days=210)
    book.post(_pay("dca", 12.2, paid, remittance=("I1",)))
    seen = {(round(gbp, 2), tuple(cash)) for _wo, gbp, _cell, cash in
            _written_off(book.ledger("A"), paid)}
    assert (100.0, ((paid, 12.2),)) in seen and len(seen) == 3


def test_the_desk_posts_its_closed_account_write_off_under_each_invoice_ref():
    """The desk's write-off goes through the consumer's `_post_desk_write_off`.
    Defect: the desk path dropping the ref the sweep carries."""
    from company.billing.payment_observation_consumer import PaymentObservationConsumer

    consumer = PaymentObservationConsumer.__new__(PaymentObservationConsumer)
    consumer.ledger_book = book = _book()
    consumer._post_desk_write_off("A", 60.0, ON, CLOSED_ACCOUNT_RULE, invoice_ref="I3")
    [w] = [e for e in book.ledger("A").events() if e.event_type == T.WRITE_OFF_CREDIT]
    assert (w.invoice_ref, w.amount_gbp) == ("I3", 60.0)


def test_the_desk_journey_hands_each_invoice_ref_to_the_ledger_seam():
    """The journey decides the write-off and hands it to the seam one invoice at a time.
    Defect: the journey posting the balance's pieces with no ref (the consumer test above cannot
    see that: it calls the seam directly)."""
    from company.billing.collections_journey import CollectionsJourneyDesk
    from company.crm.account_hierarchy import Segment

    calls = []
    desk = CollectionsJourneyDesk(
        view_at=lambda *a: {}, refuse_dunning_of_cleared_debt=lambda *a: None,
        post_write_off=lambda acct, gbp, on, rule, invoice_ref=None: calls.append(
            (invoice_ref, gbp, rule)))
    book = _book()
    assert desk._write_off_if_closed("A", Segment.RESIDENTIAL, book.ledger("A"), ON)
    assert calls == [("I3", 60.0, CLOSED_ACCOUNT_RULE), ("I2", 80.0, CLOSED_ACCOUNT_RULE),
                     ("I1", 100.0, CLOSED_ACCOUNT_RULE)]
