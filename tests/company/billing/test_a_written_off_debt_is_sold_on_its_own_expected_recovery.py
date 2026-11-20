"""KNIFE3, 2026-11-20: the sell-or-work choice on a written-off debt reads THAT debt's expected
recovery, learned from the company's own ledger (debt_and_collections.md s.7.7): cash received
against a written-off bill after its write-off, over the amount written off, resolved over the book's
own write-off-to-remittance lag, in cells cut by the bill's age at close. Each test names the defect
it catches."""
import datetime as dt
import inspect

from company.billing.account_ledger import LedgerBook, LedgerEvent
from company.billing.account_ledger import LedgerEventType as T
from company.billing.collections_journey import (
    expected_post_close_recovery,
    sells_written_off_debt,
)
from company.finance import cash_forecast_provision as cfp
from company.interfaces.collections_communication import (
    sells_written_off_debt as sells_through_the_door,
)

TT = dt.datetime(2020, 1, 1)
START = dt.date(2017, 1, 10)
CLOSE = START + dt.timedelta(days=30 * 23)        # the last bill
WRITE_OFF = CLOSE + dt.timedelta(days=365)
REMIT = WRITE_OFF + dt.timedelta(days=210)        # 575 d after close: outside any 365-d window
AS_OF = REMIT + dt.timedelta(days=30)
PUBLISHED_PRICES = (0.054, 0.070, 0.093)  # Lowell 2013 / register default / Arrow 2017, per GBP
AGED_BILL, YOUNG_BILL = 0, 22             # bill 0 is ~22 months past due at close; bill 22 is not


def _account(book, acct, unpaid_bill, share, customer_pays_after_close=0.0):
    """24 monthly bills of 60, all paid but `unpaid_bill`, which is written off at close +365 and
    earns `share` of itself from the agency 210 days later."""
    for k in range(24):
        day = START + dt.timedelta(days=30 * k)
        book.post(LedgerEvent(f"{acct}-b{k}", acct, T.BILL_DEBIT, 60.0, day, TT, invoice_ref=f"{acct}-{k}"))
        if k != unpaid_bill:
            book.post(LedgerEvent(f"{acct}-p{k}", acct, T.PAYMENT_CREDIT, 60.0, day + dt.timedelta(days=5),
                                  TT, remittance=(f"{acct}-{k}",)))
    if customer_pays_after_close:
        book.post(LedgerEvent(f"{acct}-c", acct, T.PAYMENT_CREDIT, customer_pays_after_close,
                              CLOSE + dt.timedelta(days=40), TT, remittance=(f"{acct}-{unpaid_bill}",)))
    book.post(LedgerEvent(f"{acct}-wo", acct, T.WRITE_OFF_CREDIT, 60.0 - customer_pays_after_close, WRITE_OFF,
                          TT, invoice_ref=f"{acct}-{unpaid_bill}", reason="closed account"))
    if share:
        book.post(LedgerEvent(f"{acct}-r", acct, T.PAYMENT_CREDIT, (60.0 - customer_pays_after_close) * share,
                              REMIT, TT, remittance=(f"{acct}-{unpaid_bill}",)))


def _book(aged_share, young_share, n=8, **kw):
    book = LedgerBook()
    for i in range(n):
        _account(book, f"AGED{i}", AGED_BILL, aged_share, **kw)
        _account(book, f"YOUNG{i}", YOUNG_BILL, young_share, **kw)
    return book


def _rates(book, as_of=AS_OF):
    return cfp.learn(book, as_of=as_of, payment_method_of=lambda a, d: "standard_credit")


def _expected(book, acct, rates):
    bill = AGED_BILL if acct.startswith("AGED") else YOUNG_BILL
    return expected_post_close_recovery(book.ledger(acct), CLOSE, rates,
                                        bill_on=START + dt.timedelta(days=30 * bill))


def test_one_book_at_one_published_price_sells_one_debt_and_works_another():
    # Catches: the per-debt branch never being taken -- a rule that still reads one book-wide figure
    # sells all or none at a given price. Both sides of the partition, in one book, at one price.
    book = _book(aged_share=0.063, young_share=0.122)
    rates = _rates(book)
    aged, young = _expected(book, "AGED0", rates), _expected(book, "YOUNG0", rates)
    assert young > rates.written_off_recovery > aged
    assert sells_written_off_debt(0.070, aged) and not sells_written_off_debt(0.070, young)


def test_the_agency_lag_is_learned_and_its_remittance_reached():
    # Catches: a window anchored on the last bill (365 d), which no remittance at close +575 d enters,
    # and a lag read from anything but the book's own write-off-to-cash gaps.
    rates = _rates(_book(0.063, 0.122))
    assert rates.remittance_lag_days == (REMIT - WRITE_OFF).days
    assert rates.written_off_debts == 16 and rates.written_off_recovered_gbp > 0
    # Before the agency has paid, no debt is resolved: a write-off is not read as a zero recovery.
    assert _rates(_book(0.063, 0.122), as_of=REMIT - dt.timedelta(days=1)).written_off_debts == 0


def test_customer_cash_before_write_off_is_not_recovery():
    # Catches: the old denominator -- recovery read as all cash after close over the closing
    # balance, so a customer who paid most of the final bill makes the agency look 10x better.
    rates = _rates(_book(0.063, 0.122, customer_pays_after_close=50.0))
    young = rates.written_off_recovery_for(cfp.PostCloseCell(False))
    assert abs(young - 0.122) < 0.01


def test_the_cell_is_the_bills_age_at_close():
    # Catches: a cell read off anything but the bill's own date and the last bill, or the cut moved
    # off Energy UK's 12 months past due.
    terms = dt.timedelta(days=cfp.PAYMENT_TERMS_DAYS)
    assert cfp.bill_cell(CLOSE - terms - dt.timedelta(days=366), CLOSE) == cfp.PostCloseCell(True)
    assert cfp.bill_cell(CLOSE - terms - dt.timedelta(days=365), CLOSE) == cfp.PostCloseCell(False)
    assert list(inspect.signature(cfp.bill_cell).parameters) == ["bill_on", "closed_on"]


def test_a_book_that_recovers_alike_gives_every_debt_the_same_figure():
    # Catches: an invented gradient -- the cells moving apart when the book's own outcomes do not.
    book = _book(0.10, 0.10)
    rates = _rates(book)
    assert abs(_expected(book, "AGED0", rates) - _expected(book, "YOUNG0", rates)) < 1e-9


def test_with_no_book_every_debt_expects_the_published_prior():
    # Catches: a per-debt figure appearing before the company has resolved a single write-off.
    book = _book(0.063, 0.122)
    assert _expected(book, "AGED0", None) == cfp.PRIOR_POST_CLOSE_RECOVERY
    assert _expected(book, "YOUNG0", _rates(book, as_of=WRITE_OFF)) == cfp.PRIOR_POST_CLOSE_RECOVERY
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


def test_an_account_with_an_aged_and_a_young_debt_credits_each_its_own_remittance():
    # Catches: cash after a write-off credited to every debt on the account rather than the one the
    # agency's remittance names -- the big accounts hold aged and young bills together, and pooling
    # them is what kept the replay's cells from separating.
    book = LedgerBook()
    for k in range(24):
        day = START + dt.timedelta(days=30 * k)
        book.post(LedgerEvent(f"M-b{k}", "M", T.BILL_DEBIT, 60.0, day, TT, invoice_ref=f"M-{k}"))
        if k not in (AGED_BILL, YOUNG_BILL):
            book.post(LedgerEvent(f"M-p{k}", "M", T.PAYMENT_CREDIT, 60.0, day, TT, remittance=(f"M-{k}",)))
    for bill, share in ((AGED_BILL, 0.05), (YOUNG_BILL, 0.20)):
        book.post(LedgerEvent(f"M-wo{bill}", "M", T.WRITE_OFF_CREDIT, 60.0, WRITE_OFF, TT,
                              invoice_ref=f"M-{bill}", reason="closed account"))
        book.post(LedgerEvent(f"M-r{bill}", "M", T.PAYMENT_CREDIT, 60.0 * share, REMIT, TT,
                              remittance=(f"M-{bill}",)))
    cells = _rates(book).written_off_by_cell
    assert abs(cells[cfp.PostCloseCell(True)][1] - 3.0) < 1e-9
    assert abs(cells[cfp.PostCloseCell(False)][1] - 12.0) < 1e-9


def test_a_remittance_above_the_debt_recovers_the_debt_and_no_more():
    # Catches: an overpaid or misallocated remittance read as recovering more than was written off.
    rates = _rates(_book(1.5, 1.5, n=1))
    assert rates.written_off_recovered_gbp == rates.written_off_gbp == 120.0
