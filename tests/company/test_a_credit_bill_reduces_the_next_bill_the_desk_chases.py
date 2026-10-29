"""A credit bill (negative bill) is a credit on the account, so the desk chases the next bill net of it.

The run posted max(0, ask) to the triad, so a credit bill left no trace and the desk's overdue
(the next bill unpaid) sat above what the household's page said was owed. PROS-2016-0098: a
-58.97 credit bill on 30 Apr 2017, then a 57.18 bill whose DD failed; the page showed 1.79 in credit.
"""
import datetime as dt

from company.billing.account_ledger import AccountLedger, LedgerEvent, LedgerEventType


def _ev(i, t, amt, day, ref=None):
    d = dt.date(2017, *day)
    return LedgerEvent(event_id=i, account_id="A", event_type=t, amount_gbp=amt,
                       valid_time=d, transaction_time=dt.datetime.combine(d, dt.time()),
                       invoice_ref=ref)


def test_a_credit_note_nets_against_the_next_bill_and_is_not_cash():
    book = AccountLedger("A")
    book.post(_ev("credit:1", LedgerEventType.ADJUSTMENT_CREDIT, 58.97, (4, 30)))
    book.post(_ev("bill:2", LedgerEventType.BILL_DEBIT, 57.18, (6, 1), "inv2"))
    res = book.allocate(as_of=dt.date(2017, 6, 2))
    assert res.total_undisputed_outstanding_gbp == 0.0
    # Not cash: nothing allocated, nothing unallocated, so the cash-conservation control is untouched.
    assert res.allocations == [] and res.unallocated_credit_gbp == 0.0
    # Control over the partition: a credit smaller than the bill leaves the rest owed.
    book2 = AccountLedger("A")
    book2.post(_ev("credit:1", LedgerEventType.ADJUSTMENT_CREDIT, 10.0, (4, 30)))
    book2.post(_ev("bill:2", LedgerEventType.BILL_DEBIT, 57.18, (6, 1), "inv2"))
    assert book2.allocate(as_of=dt.date(2017, 6, 2)).total_undisputed_outstanding_gbp == 47.18
