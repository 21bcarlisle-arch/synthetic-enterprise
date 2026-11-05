"""An ask of GBP 0 presents no collection, so it cannot be returned, and a settlement other money
has cleared is not sent.

A credit bill, or a bill a waiting credit paid in full, asks nothing. The triad still drew an
outcome for it. On the fd91027799 book, 29 credit-bill months and 5 fully credited bills came back
"failed", and 4 of the bills also had a settlement queued (PROS-2016-0020g INV9316, SYN-2016-291
May 2023). The household is told its balance, and it repays that balance, never more
(debt_and_collections.md s.7.3).
"""
import datetime as dt

from background.live_payment_triad import LivePaymentTriad, account_of


def _payments(triad, cid):
    return [(e.valid_time, e.amount_gbp) for e in triad._ledger_book.ledger(account_of(cid)).events()
            if e.event_type.name == "PAYMENT_CREDIT" and e.amount_gbp > 0]


def _post(triad, cid, due, month, amount=0.0, credit=0.0):
    return triad.record_period(customer_id=cid, due_date=due, bill_month=month, amount_gbp=amount,
                               credit_gbp=credit, income_stress_value="low")


def test_a_bill_a_waiting_credit_paid_is_not_presented_and_cannot_fail():
    # "CRED-42"'s seeded Feb 2018 DD fails (the control below shows the draw), so this asks whether
    # an ask of nothing can still come back returned.
    control = LivePaymentTriad()
    assert _post(control, "CRED-42", dt.date(2018, 3, 14), "2018-02", amount=100.0)["result"] \
        == "DD_FAILED"
    triad = LivePaymentTriad()
    presented = []
    triad._consumer.note_collection_request = presented.append
    _post(triad, "CRED-42", dt.date(2018, 2, 14), "2018-01", credit=100.0)
    record = _post(triad, "CRED-42", dt.date(2018, 3, 14), "2018-02", amount=100.0)
    assert record["result"] != "DD_FAILED"
    assert [r.result for r in triad.records] == ["success", "success"]
    assert all(r.settled_on is None for r in triad.records)
    # Nothing was presented, and nothing crossed for either month.
    assert presented == []
    assert triad._hand_overs == []
    assert triad._n_nil_asks == 2


def test_a_settlement_carries_only_what_a_credit_left_open():
    # Feb's DD fails and the world settles it on 28 Mar. A 30.00 credit bill issued between
    # them clears part of it, so the household settles the 70.00 it is told is left.
    triad = LivePaymentTriad()
    _post(triad, "CRED-42", dt.date(2018, 2, 14), "2018-01", amount=50.0)
    _post(triad, "CRED-42", dt.date(2018, 3, 14), "2018-02", amount=100.0)
    assert triad.records[-1].settled_on == dt.date(2018, 3, 28)
    _post(triad, "CRED-42", dt.date(2018, 3, 20), "2018-03", credit=30.0)
    triad.collections_journeys(dt.date(2018, 6, 30))
    assert (dt.date(2018, 3, 28), 70.0) in _payments(triad, "CRED-42")
    assert triad.later_settlements()["cut_to_balance"] == 1
    # A credit that clears the whole bill leaves nothing to settle, so no cash is sent.
    cleared = LivePaymentTriad()
    _post(cleared, "CRED-42", dt.date(2018, 2, 14), "2018-01", amount=50.0)
    _post(cleared, "CRED-42", dt.date(2018, 3, 14), "2018-02", amount=100.0)
    _post(cleared, "CRED-42", dt.date(2018, 3, 20), "2018-03", credit=130.0)
    cleared.collections_journeys(dt.date(2018, 6, 30))
    assert not any(on == dt.date(2018, 3, 28) for on, _ in _payments(cleared, "CRED-42"))
    assert cleared.later_settlements()["already_cleared"] == 1
