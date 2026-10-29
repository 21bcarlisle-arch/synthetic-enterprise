"""A credit bill comes off the leg's next bill, so the household is asked, and pays, the rest.

The page nets a credit bill against the leg's next bill (`arrears_engine.resolved_settlement`,
SLC 31H.12). The triad collected the whole next bill, so the credit sat unused on the desk's ledger
until it absorbed a later unpaid bill. On the 209c3350ab book, SYN-2016-083's -28.53 credit bill of
Jul 2017 was netted by the page off the Aug 2017 bill (37.41 paid of 65.94). The desk took the same
28.53 off a Jan 2019 bill that the page still showed owed, and printed 89.80 overdue against the
page's 47.05.
"""
import datetime as dt

from background.live_payment_triad import LivePaymentTriad, account_of


def _payments(triad, cid):
    return [(e.valid_time, e.amount_gbp) for e in triad._ledger_book.ledger(account_of(cid)).events()
            if e.event_type.name == "PAYMENT_CREDIT" and e.amount_gbp > 0]


def _post(triad, cid, due, month, amount=0.0, credit=0.0):
    return triad.record_period(customer_id=cid, due_date=due, bill_month=month, amount_gbp=amount,
                               credit_gbp=credit, income_stress_value="low")


def test_the_next_paid_bill_is_collected_net_of_the_credit_and_no_credit_is_left_on_the_desk():
    # "CRED-0" is a draw, not a label: its seeded payments in these months all succeed.
    triad = LivePaymentTriad()
    _post(triad, "CRED-0", dt.date(2018, 2, 14), "2018-01", credit=30.0)
    _post(triad, "CRED-0", dt.date(2018, 3, 14), "2018-02", amount=100.0)
    _post(triad, "CRED-0", dt.date(2018, 4, 14), "2018-03", amount=100.0)
    assert _payments(triad, "CRED-0") == [(dt.date(2018, 3, 14), 70.0), (dt.date(2018, 4, 14), 100.0)]
    # No credit is left on the desk to absorb a later unpaid bill the page still shows owed.
    events = triad._ledger_book.ledger(account_of("CRED-0")).events()
    assert round(sum(e.amount_gbp * (1 if e.event_type.name == "BILL_DEBIT" else -1)
                     for e in events), 2) == 0.0


def test_a_credit_waits_only_when_nothing_on_the_leg_is_unpaid():
    # The other side of the partition. "CRED-42"'s seeded Feb 2018 DD fails and is settled on
    # 28 Mar. A credit issued on 6 Mar meets that open bill, which the page nets first and the
    # desk's ledger nets oldest-first, so it is not held for the next bill as well.
    triad = LivePaymentTriad()
    _post(triad, "CRED-42", dt.date(2018, 2, 14), "2018-01", amount=50.0)
    assert _post(triad, "CRED-42", dt.date(2018, 3, 14), "2018-02", amount=100.0)["result"] == "DD_FAILED"
    _post(triad, "CRED-42", dt.date(2018, 3, 20), "2018-03", credit=30.0)
    _post(triad, "CRED-42", dt.date(2018, 5, 14), "2018-04", amount=100.0)
    assert (dt.date(2018, 5, 14), 100.0) in _payments(triad, "CRED-42")
    # ...and the same credit issued after the settlement is held, and nets the next bill.
    later = LivePaymentTriad()
    _post(later, "CRED-42", dt.date(2018, 2, 14), "2018-01", amount=50.0)
    _post(later, "CRED-42", dt.date(2018, 3, 14), "2018-02", amount=100.0)
    _post(later, "CRED-42", dt.date(2018, 4, 14), "2018-03", credit=30.0)
    _post(later, "CRED-42", dt.date(2018, 5, 14), "2018-04", amount=100.0)
    assert (dt.date(2018, 5, 14), 70.0) in _payments(later, "CRED-42")
