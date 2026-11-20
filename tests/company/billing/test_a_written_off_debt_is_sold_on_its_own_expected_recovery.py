"""KNIFE3, 2026-11-20: the sell-or-work choice on a written-off debt reads THAT debt's expected
recovery, learned from the company's own ledger (debt_and_collections.md s.7.7), not one book-wide
figure. Each test names the defect it catches."""
import datetime as dt
import inspect

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.collections_journey import (
    expected_post_close_recovery,
    sells_written_off_debt,
)
from company.finance import cash_forecast_provision as cfp
from company.interfaces.collections_communication import (
    sells_written_off_debt as sells_through_the_door,
)

TT = dt.datetime(2020, 1, 1)
START = dt.date(2018, 1, 10)
AS_OF = START + dt.timedelta(days=30 * 30)
PUBLISHED_PRICES = (0.054, 0.070, 0.093)  # Lowell 2013 / register default / Arrow 2017, per GBP


def _bill(book, acct, k, paid):
    day = START + dt.timedelta(days=30 * k)
    book.post(LedgerEvent(f"{acct}-b{k}", acct, LedgerEventType.BILL_DEBIT, 60.0, day, TT))
    if paid:
        book.post(LedgerEvent(f"{acct}-p{k}", acct, LedgerEventType.PAYMENT_CREDIT, 60.0,
                              day + dt.timedelta(days=5), TT))


def _book(recover_paying, recover_stopped, n=8):
    """PAYING accounts pay every bill but the final one; STOPPED accounts stop five months before
    closing. Each later pays back the given share of what it owed at close."""
    book = LedgerBook()
    after = START + dt.timedelta(days=30 * 11 + 120)
    for i in range(n):
        for k in range(12):
            _bill(book, f"PAYING{i}", k, k < 11)
            _bill(book, f"STOPPED{i}", k, k < 7)
        for acct, owed, share in ((f"PAYING{i}", 60.0, recover_paying),
                                  (f"STOPPED{i}", 300.0, recover_stopped)):
            if share:
                book.post(LedgerEvent(f"{acct}-r", acct, LedgerEventType.PAYMENT_CREDIT,
                                      owed * share, after, TT))
    return book


def _expected(book, acct, rates):
    led = book.ledger(acct)
    last = max(e.valid_time for e in led.events_through(AS_OF)
               if e.event_type == LedgerEventType.BILL_DEBIT)
    return expected_post_close_recovery(led, last, rates)


def _rates(book):
    return cfp.learn(book, as_of=AS_OF, payment_method_of=lambda a, d: "standard_credit")


def test_one_book_at_one_published_price_sells_one_debt_and_works_another():
    # Catches: the per-debt branch never being taken -- a rule that still reads one book-wide figure
    # sells all or none at a given price. Both sides of the partition, in one book, at one price.
    book = _book(recover_paying=0.30, recover_stopped=0.02)
    rates = _rates(book)
    paying, stopped = _expected(book, "PAYING0", rates), _expected(book, "STOPPED0", rates)
    assert paying > rates.post_close_recovery > stopped
    for price in PUBLISHED_PRICES:
        assert sells_written_off_debt(price, stopped) and not sells_written_off_debt(price, paying)


def test_the_cells_come_from_the_ledger_at_close():
    # Catches: a cell read off anything but the company's own bills and payments at the last bill.
    book = _book(0.0, 0.0)
    last = START + dt.timedelta(days=30 * 11)
    assert cfp.post_close_cell(book.ledger("PAYING0"), last) == cfp.PostCloseCell(0, False)
    stopped = cfp.post_close_cell(book.ledger("STOPPED0"), last)
    assert stopped.months_unpaid_at_close > 0 and stopped.carried_arrears
    assert list(inspect.signature(cfp.post_close_cell).parameters) == ["ledger", "closed_on"]


def test_a_book_that_recovers_alike_gives_every_debt_the_same_figure():
    # Catches: an invented gradient -- the cells moving apart when the book's own outcomes do not.
    book = _book(recover_paying=0.10, recover_stopped=0.10)
    rates = _rates(book)
    assert abs(_expected(book, "PAYING0", rates) - _expected(book, "STOPPED0", rates)) < 1e-9


def test_with_no_book_every_debt_expects_the_published_prior():
    # Catches: a per-debt figure appearing before the company has resolved a single close.
    book = _book(0.30, 0.02)
    assert _expected(book, "PAYING0", None) == cfp.PRIOR_POST_CLOSE_RECOVERY
    assert _expected(book, "STOPPED0", None) == cfp.PRIOR_POST_CLOSE_RECOVERY
    assert sells_written_off_debt(0.15) and not sells_written_off_debt(0.07)


def test_a_debt_in_sensitive_circumstances_is_never_sold():
    # Catches: the exclusion dropped (sold at a price that sells the same debt unflagged) and the
    # exclusion applied to everything (the unflagged debt not sold either).
    for price in (*PUBLISHED_PRICES, 0.5, 1.0):
        assert sells_written_off_debt(price, 0.0)
        assert not sells_written_off_debt(price, 0.0, sensitive=True)


def test_the_door_forwards_the_per_debt_figure_and_the_flag():
    # Catches: the door dropping the per-debt figure or the flag and answering the book-wide rule.
    for offer in (None, 0.05, 0.093, 0.5):
        for er in (None, 0.02, 0.30):
            for sensitive in (False, True):
                assert (sells_through_the_door(offer, er, sensitive=sensitive)
                        == sells_written_off_debt(offer, er, sensitive=sensitive))
