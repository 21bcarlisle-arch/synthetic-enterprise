"""INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL (seventh cold read, N15): the desk's "a further bill missed"
needs a bill, due since the previous plan offer, that was not paid between its issue and due dates.

Defect this catches: the desk re-offered the plan on the day after any bill's due date without asking
whether it was paid (0a6391d186: OCC-17ff099218d5 re-offered on 16 Nov 2020 after its gas bill was
collected in full on 15 Nov). Mutations, each reds this file: the window opened at the account's start
(one early miss then licenses every re-offer); cash read across both legs or outside issue..due; a
credit netted on the bill's payment not counted; the gas leg's bills not joined to the household's journey;
the bill's own `credit_applied_gbp` read as landed (b3ce2a4e73: SYN-2016-066's returned DD, settled by a
credit bill four months later); cash posted against an older bill counted (PROS-2020-0016); a payment
naming no bill not counted. From 2026-11-11 (068b5e3cc8 / e1587ec5b, 19 re-offers the day after a
returned level instalment, e.g. SYN-2016-549 gas re-offered 25 Dec 2018 after its 24 Dec instalment was
returned): a returned level instalment in the window is a further missed scheduled payment (SLC 27.5B);
a successful one is not; a re-presentation of an instalment first returned before the previous offer
is the same payment, not a further miss.
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


PAID = "every bill and level instalment due since the previous offer paid"
NOTHING_DUE = "no bill or level instalment due since the previous offer"


def test_every_leg_of_the_row_can_be_taken():
    assert _grade([_pay(2, "2020-03-15")]) == (1, [PAID])                # paid on its due date
    assert _grade([]) == (1, [])                                         # never paid: a true miss
    assert _grade([_pay(2, "2020-03-20")]) == (1, [])                    # paid after its due date
    assert _grade([_pay(2, "2020-03-15", outcome="failed")]) == (1, [])  # a returned collection
    assert _grade([_pay(2, "2020-03-15", amount=30.0)]) == (1, [])       # paid short
    assert _grade([], gas_bill=_bill(2, "2020-02-01", "2020-02-15")) == (1, [NOTHING_DUE])


def test_a_miss_before_the_previous_offer_does_not_make_the_reoffer_true():
    """The January miss is what the 1 Mar offer answered; it is no FURTHER bill."""
    assert _grade([_pay(2, "2020-03-15")], old_miss=True) == (1, [PAID])


def _credited(on, outcome="success", n=2):
    """The ledger's shape for a bill an earlier credit paid down: the credit rides on the bill's payment."""
    return dict(_pay(n, on, amount=0.0, outcome=outcome), credit_applied_gbp=40.0)


def test_a_bill_paid_by_credit_or_by_scheme_credit_is_paid():
    netted = _bill(2, "2020-03-01", "2020-03-15", credit_applied_gbp=40.0)
    assert _grade([_credited("2020-03-15")], gas_bill=netted) == (1, [PAID])
    paid = {"invoice_number": 2, "payment_date": "2020-03-15", "amount_gbp": 0.0, "method": "direct_debit",
            "outcome": "success", "scheme_credit_gbp": 40.0}
    assert _grade([paid]) == (1, [PAID])


def test_a_returned_collection_later_settled_by_a_credit_bill_is_still_missed():
    """b3ce2a4e73, SYN-2016-066: the 16 Feb 2022 DD was returned; a credit bill of 30 Jun settled it, and
    the export's credit_applied_gbp on the February bill is that June credit. Not paid by its due date."""
    settled_later = _bill(2, "2020-03-01", "2020-03-15", credit_applied_gbp=40.0)
    assert _grade([_pay(2, "2020-03-15", outcome="failed")], gas_bill=settled_later) == (1, [])
    assert _grade([], gas_bill=settled_later) == (1, [])
    assert _grade([_credited("2020-03-20")], gas_bill=settled_later) == (1, [])   # netted after its due date


def test_cash_posted_against_an_older_bill_does_not_pay_this_one():
    """b3ce2a4e73, PROS-2020-0016: the April bill's late £19.37 and its £67 EBSS landed in the May bill's
    window; the May bill was paid 37 days late. The payment names its bill; a payment naming none counts."""
    older = dict(_pay(3, "2020-03-10", amount=0.0), scheme_credit_gbp=40.0)
    assert _grade([_pay(3, "2020-03-10"), older]) == (1, [])
    assert _grade([_pay(None, "2020-03-10")]) == (1, [PAID])


def test_a_book_read_without_the_bill_record_is_unbounded_and_never_clean():
    accts = _household([])
    raw = {a.cid: {"customer_id": a.cid, "billing_account_id": "H", "segment": "resi", "periods": [],
                   "payments": [], "events": {"collections_journeys": list(a.journeys)}} for a in accts}
    assert runner.run([{"id": ROW}], raw)[0]["status"] == "NOT_IN_EXPORT"
    t = runner.ev_reoffer_follows_a_missed_bill(None, [runner.Account(c, r) for c, r in raw.items()])
    assert (t.checked, t.unbounded) == (0, 1)


# ── A returned level instalment is a missed scheduled payment (2026-11-11) ──────────────────────

def _instalment(n, on, outcome="failed", amount=40.0, **kw):
    return dict(_pay(n, on, amount=amount, outcome=outcome), level_dd=True, **kw)


#: The gas bill fell due before the 1 Mar offer, so no bill falls in the window: only the instalment can.
_EARLY = _bill(2, "2020-02-01", "2020-02-15")


def test_a_reoffer_the_day_after_a_returned_level_instalment_passes():
    """Defect: the row read only bills by due date, so the 19 re-offers that followed a returned level
    instalment (SYN-2016-549 gas, 24 Dec 2018 returned, re-offered 25 Dec) read as breaches."""
    paid_bill = [_pay(2, "2020-02-15")]
    assert _grade(paid_bill + [_instalment(5, "2020-03-15")], gas_bill=_EARLY) == (1, [])
    assert _grade(paid_bill + [_instalment(5, "2020-03-01")], gas_bill=_EARLY) == (1, [])   # on P: inclusive
    assert _grade(paid_bill + [_instalment(5, "2020-03-16")], gas_bill=_EARLY) == (1, [])   # on E: inclusive
    assert _grade(paid_bill + [_instalment(5, "2020-02-28")], gas_bill=_EARLY) == (1, [NOTHING_DUE])


def test_a_level_instalment_that_was_collected_does_not_save_the_reoffer():
    """Defect: any level record in the window read as a miss, the outcome not tested."""
    assert _grade([_pay(2, "2020-02-15"), _instalment(5, "2020-03-15", outcome="success")],
                  gas_bill=_EARLY) == (1, [PAID])


def test_a_failed_representation_of_an_instalment_first_returned_before_the_offer_does_not_save_it():
    """Defect: a re-presentation counted as a further miss. The 20 Feb instalment was returned before the
    1 Mar offer, which answered it; its re-presentation on 5 Mar failing is the same scheduled payment."""
    pays = [_pay(2, "2020-02-15"), _instalment(5, "2020-02-20"), _instalment(5, "2020-03-05")]
    assert _grade(pays, gas_bill=_EARLY) == (1, [NOTHING_DUE])        # it fell due on 20 Feb, before P
    fresh = pays + [_instalment(6, "2020-03-10")]                     # a different instalment: a further miss
    assert _grade(fresh, gas_bill=_EARLY) == (1, [])
    later = [_pay(2, "2020-02-15"), _instalment(5, "2020-01-20"), _instalment(5, "2020-03-05")]
    assert _grade(later, gas_bill=_EARLY) == (1, [])                  # past 30 days: not a re-presentation


def test_a_failed_instalment_paid_in_full_is_not_missed_and_one_paid_short_is():
    """A failed collection's paid part: what the instalment asked, short by more than half a penny."""
    whole = [_pay(2, "2020-02-15"), _instalment(5, "2020-03-15", part_paid_gbp=40.0)]
    assert _grade(whole, gas_bill=_EARLY) == (1, [PAID])
    short = [_pay(2, "2020-02-15"), _instalment(5, "2020-03-15", part_paid_gbp=20.0)]
    assert _grade(short, gas_bill=_EARLY) == (1, [])


def test_the_instalment_clause_leaves_the_breach_branch_reachable():
    """Control over the whole partition: pass, every-paid breach and nothing-due breach all still fire
    with the instalment clause in place."""
    assert _grade([_pay(2, "2020-02-15"), _instalment(5, "2020-03-15")], gas_bill=_EARLY)[1] == []
    assert _grade([_pay(2, "2020-03-15"), _instalment(5, "2020-03-10", outcome="success")])[1] == [PAID]
    assert _grade([_pay(2, "2020-02-15")], gas_bill=_EARLY)[1] == [NOTHING_DUE]
