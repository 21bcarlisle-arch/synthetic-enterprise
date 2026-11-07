"""INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE, Leg A only.

f874c6836 landed the row with no evaluator, so the runner's disposition test was red on trunk. The
evaluator and this test were written on 5 Nov beside two household-page rows, and left uncommitted on
the shared tree when the host went down. They landed alone on 7 Nov to clear the red; the page rows
did not. The defect it names: a book whose direct debits collect the bill each month while its
households are meant to pay a level amount (0.963 on 4669d77ddd).
"""
from __future__ import annotations

from tools import domain_invariant_runner as runner


def _grade(inv_id, *accounts):
    r = runner.run([{"id": inv_id}], {a["customer_id"]: a for a in accounts})[0]
    return (r["status"], sorted(b["side"] for b in r.get("breach_examples") or ()),
            sorted(f["side"] for f in r.get("flag_examples") or ()))


def _dd_account(cid, amounts, bills):
    return {"customer_id": cid, "segment": "resi", "payments": [],
            "periods": [{"period_start": "2020-01-01", "period_end": "2020-12-31", "commodity": "electricity"}],
            "bill_record": {
                "invoices": [{"invoice_number": n, "period_start": "2020-%02d-01" % n, "period_end": "2020-%02d-28" % n,
                              "total_amount_gbp": b} for n, b in enumerate(bills, 1)],
                "payments": [{"invoice_number": n, "payment_date": "2020-%02d-15" % n, "amount_gbp": a,
                              "method": "direct_debit", "outcome": "success"} for n, a in enumerate(amounts, 1)]}}


def test_leg_a_of_the_dd_row_is_reachable_and_says_the_other_legs_are_unbuilt():
    i = "INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE"
    bills = [50.0, 61.0, 47.0, 70.0, 55.0, 64.0]

    def book(amounts, n=10):
        return [_dd_account("D%d" % k, amounts, bills) for k in range(n)]
    assert _grade(i, *book(bills))[:2] == ("BREACHED", ["Leg A"])
    # A level amount: never the bill, so Leg A passes, and the row still says what it did not grade.
    assert _grade(i, *book([60.0] * 6)) == ("FLAGGED", [], ["Legs B and C not built"])
    assert _grade(i, *book(bills, n=9))[0] == "UNREACHED"
