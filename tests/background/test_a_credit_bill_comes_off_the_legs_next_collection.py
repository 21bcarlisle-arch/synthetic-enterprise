"""A credit bill comes off the leg's next bill, so the household is asked, and pays, the rest.

The page nets a credit bill against the leg's next bill (`arrears_engine.resolved_settlement`,
SLC 31H.12). The triad collected the whole next bill, so the credit sat unused on the desk's ledger
until it absorbed a later unpaid bill. On the 209c3350ab book, SYN-2016-083's -28.53 credit bill of
Jul 2017 was netted by the page off the Aug 2017 bill (37.41 paid of 65.94). The desk took the same
28.53 off a Jan 2019 bill that the page still showed owed, and printed 89.80 overdue against the
page's 47.05.
"""
import datetime as dt

from background.live_payment_triad import LivePaymentTriad, _period_index_for, account_of


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
    # Both desks are told what the netted bill asked, so its 70.00 paid on the due date is not read
    # as a miss of its 100.00 face (N15 on b3ce2a4e73); the un-netted March bill asked its face.
    # Corrected 9 Nov 2026: this pinned the dict to [70.0]. The January credit bill asked nothing,
    # and is now recorded so (a nil ask is no sign of leaving level DD, `_shows_how_it_pays`).
    for consumer in (triad._consumer, triad._cf_consumer):
        cj = consumer.collections_journeys
        assert [cj.asked_of(f"CRED-0::{_period_index_for(m)}", 100.0) for m in ("2018-01", "2018-02", "2018-03")] == [
            0.0, 70.0, 100.0], cj._asked


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


def _level_leg_then_credit(credit):
    # Two level months collect 60.00 against 100.00 bills, so the leg leaves level DD owing an 80.00
    # scheme debit. Then a credit bill, then a bill of 100.00 paid on receipt.
    triad = LivePaymentTriad()
    for due, month in ((dt.date(2018, 2, 14), "2018-01"), (dt.date(2018, 3, 14), "2018-02")):
        triad.record_period(customer_id="CRED-0", due_date=due, bill_month=month, amount_gbp=100.0,
                            credit_gbp=0.0, income_stress_value="low",
                            level_collection={"amount_gbp": 60.0, "collection_date": due.isoformat()})
    _post(triad, "CRED-0", dt.date(2018, 4, 14), "2018-03", credit=credit)
    _post(triad, "CRED-0", dt.date(2018, 5, 14), "2018-04", amount=100.0)
    return triad


def test_a_credit_after_leaving_level_dd_meets_the_scheme_debit_before_it_waits_for_the_next_bill():
    # SYN-2016-549g on the 78f82e4242 book: a GBP -62.12 credit bill waited whole over a 53.98 scheme
    # debit, so the household was asked nothing on bills its own supplier then chased at face, and
    # the page netted the 53.98 the household never sent. SLC 27.16: a credit is only what exceeds
    # the charges due on the contract (payments_and_direct_debit_2026-10-25.md, "A credit bill after
    # leaving with the debit still owed").
    small, large = _level_leg_then_credit(30.0), _level_leg_then_credit(100.0)
    assert [_payments(t, "CRED-0")[:2] for t in (small, large)] == [
        [(dt.date(2018, 2, 14), 60.0), (dt.date(2018, 3, 14), 60.0)]] * 2, "both legs were level"
    # The whole partition is reachable on one leg: a credit inside the debit waits for nothing,
    # a credit beyond it waits for exactly the excess (100 - 80 = 20 comes off the next bill).
    assert (dt.date(2018, 5, 14), 100.0) in _payments(small, "CRED-0")
    assert (dt.date(2018, 5, 14), 80.0) in _payments(large, "CRED-0")
