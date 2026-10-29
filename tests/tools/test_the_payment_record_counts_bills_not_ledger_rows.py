"""The second cold read's N3 (2026-10-28): "34 payments, 4 returned, 42 missed" on a 50-bill account.
The counter counted ledger rows and arrears cases, not bills. On the 1a02c46116 book, 631 of 1,125
accounts with collections due breached INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE. Under the
row's definitions, each bill past its due date counts as paid (a payment on it by that date) or
missed, never both and never neither. A return is one attempt on a bill. A one-off payment on no
bill due is no collection. A prepayment statement is never due.

The third cold read (2026-10-29): SYN-2016-356 printed "4 of 4 bills paid, 0 returned, 0 missed" at
its own "Missed a payment" moment, because the record waited 30 days past the due date and the desk
did not. Both now read `collections_journey.bill_missed`."""
import datetime as dt

from company.billing.collections_journey import missed_on
from tools.generate_explore_cast import payment_record


def _bill(n, due, doc="bill"):
    return {"invoice_number": n, "due_date": due, "document_type": doc}


def _pay(n, on, kind="payment_received", method="direct_debit"):
    return {"type": kind, "invoice_number": n, "date": on, "method": method}


BILLS = [_bill(1, "2020-01-20"), _bill(2, "2020-02-20"), _bill(3, "2020-03-20"),
         _bill(4, "2020-06-20"),                       # past due on 2020-07-01, unpaid
         _bill(5, "2020-01-25", doc="prepayment_statement")]
LEDGER = [_pay(1, "2020-01-20"),
          _pay(2, "2020-02-20", "payment_failed"), _pay(2, "2020-03-01"),   # returned, re-presented
          _pay(2, "2020-03-05"),                                          # a second payment on it
          _pay(3, "2020-05-30"),                                          # paid, but after its due date
          _pay(None, "2020-04-01", method="standard_credit")]            # one-off, on no bill


def test_each_bill_due_is_paid_or_missed_and_a_return_is_an_attempt():
    rec = payment_record(LEDGER, BILLS, "2020-07-01")
    assert (rec["due"], rec["payments"], rec["returned"], rec["missed"]) == (4, 1, 1, 3), rec
    assert rec["payments"] + rec["missed"] == rec["due"]


def test_a_missed_direct_debit_bill_is_counted_beside_its_returns():
    rec = payment_record([_pay(1, "2020-01-20", "payment_failed")], BILLS[:1], "2020-07-01")
    assert (rec["missed"], rec["missed_dd"], rec["returned"]) == (1, 1, 1), rec


def test_the_record_counts_a_bill_missed_on_the_day_the_desk_opens_its_journey():
    """SYN-2016-356's shape: a pay-on-receipt bill unpaid at its due date and paid ten days later. On
    the desk's "Missed a payment" day the record shows it missed, and the day before it is not yet
    due, so the partition has both sides. Red on origin: "1 of 1 bills paid, 0 missed" would have
    waited 30 days. A late payment never un-misses the bill."""
    bill, due = [_bill(1, "2016-10-28")], dt.date(2016, 10, 28)
    led = [_pay(1, "2016-11-07", method="standard_credit")]
    opened = missed_on(due).isoformat()
    assert payment_record([], bill, (due).isoformat())["due"] == 0
    rec = payment_record([], bill, opened)
    assert (rec["due"], rec["payments"], rec["missed"]) == (1, 0, 1), rec
    assert payment_record(led, bill, "2017-01-01")["missed"] == 1
    assert payment_record([_pay(1, "2016-10-28", method="standard_credit")], bill, opened)["missed"] == 0


def test_a_return_shows_on_the_day_it_happens():
    """A DD returned on its due date shows beside the "Direct debit returned" moment that day, before
    its bill is missable (three such stories on the 209c3350ab book printed "0 returned")."""
    rec = payment_record([_pay(1, "2020-01-20", "payment_failed")], BILLS[:1], "2020-01-20")
    assert (rec["due"], rec["returned"]) == (0, 1), rec
