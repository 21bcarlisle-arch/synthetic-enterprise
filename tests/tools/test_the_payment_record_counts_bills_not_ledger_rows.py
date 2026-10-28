"""The second cold read's N3 (2026-10-28): "34 payments, 4 returned, 42 missed" on a 50-bill account.
The counter counted ledger rows and arrears cases, not bills. On the 1a02c46116 book, 631 of 1,125
accounts with collections due breached INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE. Under the
row's definitions, each bill whose due date and 30-day window have passed counts as paid (a payment
on it inside the window) or missed (none), never both and never neither. A return is one attempt
on a bill. A one-off payment on no bill due is no collection. A prepayment statement is never due."""
from tools.generate_explore_cast import payment_record


def _bill(n, due, doc="bill"):
    return {"invoice_number": n, "due_date": due, "document_type": doc}


def _pay(n, on, kind="payment_received", method="direct_debit"):
    return {"type": kind, "invoice_number": n, "date": on, "method": method}


BILLS = [_bill(1, "2020-01-20"), _bill(2, "2020-02-20"), _bill(3, "2020-03-20"),
         _bill(4, "2020-06-20"),                       # not yet due past its window on 2020-07-01
         _bill(5, "2020-01-25", doc="prepayment_statement")]
LEDGER = [_pay(1, "2020-01-20"),
          _pay(2, "2020-02-20", "payment_failed"), _pay(2, "2020-03-01"),   # returned, re-presented
          _pay(2, "2020-03-05"),                                          # a second payment on it
          _pay(3, "2020-05-30"),                                          # paid, but after its window
          _pay(None, "2020-04-01", method="standard_credit")]            # one-off, on no bill


def test_each_bill_due_is_paid_or_missed_and_a_return_is_an_attempt():
    rec = payment_record(LEDGER, BILLS, "2020-07-01")
    assert (rec["due"], rec["payments"], rec["returned"], rec["missed"]) == (3, 2, 1, 1), rec
    assert rec["payments"] + rec["missed"] == rec["due"]


def test_a_missed_direct_debit_bill_is_counted_beside_its_returns():
    rec = payment_record([_pay(1, "2020-01-20", "payment_failed")], BILLS[:1], "2020-07-01")
    assert (rec["missed"], rec["missed_dd"], rec["returned"]) == (1, 1, 1), rec
