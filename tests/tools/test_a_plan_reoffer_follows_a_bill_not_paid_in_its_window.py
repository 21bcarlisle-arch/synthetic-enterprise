"""INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL (seventh cold read, N15): the desk's "a further bill missed"
needs a bill, due since the previous plan offer, that was not paid between its issue and due dates.

Defect this catches: the desk re-offered the plan on the day after any bill's due date without asking
whether it was paid (0a6391d186: OCC-17ff099218d5 re-offered on 16 Nov 2020 after its gas bill was
collected in full on 15 Nov). Mutations, each reds this file: the window opened at the account's start
(one early miss then licenses every re-offer); cash read across both legs or outside issue..due; a
credit applied to the bill not counted; the gas leg's bills not joined to the household's journey.
"""
from __future__ import annotations

from tools import domain_invariant_runner as runner

ROW = "INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL"


def _leg(cid, bills, payments):
    return {"customer_id": cid, "billing_account_id": "H", "segment": "resi", "periods": [], "payments": [],
            "bill_record": {"invoices": bills, "payments": payments}}


def _bill(n, issued, due, total=40.0, **kw):
    return dict({"invoice_number": n, "document_type": "bill", "issue_date": issued, "due_date": due,
                 "total_amount_gbp": total}, **kw)


def _pay(n, on, amount=40.0, outcome="success", method="direct_debit"):
    return {"invoice_number": n, "payment_date": on, "amount_gbp": amount, "method": method, "outcome": outcome}


def _household(gas_payments, *, gas_bill=None, old_miss=False):
    """An electricity leg carrying the journey (offer 1 Mar, re-offer 16 Mar 2020) and a gas leg whose
    bill fell due on 15 Mar. With `old_miss`, a January electricity bill was never paid."""
    journey = {"journey_exit": None, "events": [
        {"event": "missed_payment", "event_date": "2020-01-16"},
        {"event": "repayment_plan_offer", "event_date": "2020-03-01"},
        {"event": "repayment_plan_reoffer", "event_date": "2020-03-16"}]}
    elec = _leg("H", [_bill(1, "2020-01-01", "2020-01-15")], [] if old_miss else [_pay(1, "2020-01-15")])
    elec["events"] = {"collections_journeys": [journey]}
    gas = _leg("Hg", [gas_bill or _bill(2, "2020-03-01", "2020-03-15")], gas_payments)
    gas["events"] = {"collections_journeys": [journey]}                 # each leg carries the same list
    return [runner.Account(c, r) for c, r in (("H", elec), ("Hg", gas))]


def _grade(*a, **kw):
    t = runner.ev_reoffer_follows_a_missed_bill(None, _household(*a, **kw))
    return t.checked, [b["side"] for b in t.breaches]


PAID = "every bill due since the previous offer paid in its window"


def test_every_leg_of_the_row_can_be_taken():
    assert _grade([_pay(2, "2020-03-15")]) == (1, [PAID])                # paid on its due date
    assert _grade([]) == (1, [])                                         # never paid: a true miss
    assert _grade([_pay(2, "2020-03-20")]) == (1, [])                    # paid after its due date
    assert _grade([_pay(2, "2020-03-15", outcome="failed")]) == (1, [])  # a returned collection
    assert _grade([_pay(2, "2020-03-15", amount=30.0)]) == (1, [])       # paid short
    assert _grade([], gas_bill=_bill(2, "2020-02-01", "2020-02-15")) == (1, [
        "no bill due since the previous offer"])


def test_a_miss_before_the_previous_offer_does_not_make_the_reoffer_true():
    """The January miss is what the 1 Mar offer answered; it is no FURTHER bill."""
    assert _grade([_pay(2, "2020-03-15")], old_miss=True) == (1, [PAID])


def test_a_bill_paid_by_credit_or_by_scheme_credit_is_paid():
    assert _grade([], gas_bill=_bill(2, "2020-03-01", "2020-03-15", credit_applied_gbp=40.0)) == (1, [PAID])
    paid = {"invoice_number": 2, "payment_date": "2020-03-15", "amount_gbp": 0.0, "method": "direct_debit",
            "outcome": "success", "scheme_credit_gbp": 40.0}
    assert _grade([paid]) == (1, [PAID])


def test_a_book_read_without_the_bill_record_is_unbounded_and_never_clean():
    accts = _household([])
    raw = {a.cid: {"customer_id": a.cid, "billing_account_id": "H", "segment": "resi", "periods": [],
                   "payments": [], "events": {"collections_journeys": list(a.journeys)}} for a in accts}
    assert runner.run([{"id": ROW}], raw)[0]["status"] == "NOT_IN_EXPORT"
    t = runner.ev_reoffer_follows_a_missed_bill(None, [runner.Account(c, r) for c, r in raw.items()])
    assert (t.checked, t.unbounded) == (0, 1)
