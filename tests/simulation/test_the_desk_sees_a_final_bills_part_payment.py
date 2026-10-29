"""The collections desk sees the part of a mover's final bill the household paid.

The defect this names: the triad decided a mover's final bill as failed with `part_paid` paid
(`arrears_engine.mover_final_bill_outcome`), kept the part for the world's truth, which the page
prints as a payment received, and crossed only the failure to the desk. The desk chased the whole
bill: on the 209c3350ab book, 148 collections steps on 18 households printed an overdue figure above
the page by exactly the part paid (INV_OVERDUE_WITHIN_PAGE_BALANCE), and the close write-off took
the whole bill.
"""
from __future__ import annotations

from datetime import date

import simulation.arrears_engine as ae
import simulation.world_payment_truth as wpt
from background.live_payment_triad import LivePaymentTriad


def test_the_desk_owes_the_bill_less_the_part_paid(monkeypatch):
    monkeypatch.setattr(wpt, "UNIFIED", True)
    triad = LivePaymentTriad()
    outcomes = set()
    for i in range(200):
        cid = f"RESI{i:05d}"
        triad.record_period(customer_id=cid, due_date=date(2020, 3, 28), amount_gbp=90.0,
                            income_stress_value="moderate", segment="resi",
                            moved_out_on="2020-03-15")
        method = wpt.engine_method(triad._method_for(cid))
        exit_ = ae.mover_final_bill_outcome({"moved_out_on": "2020-03-15"}, cid, "2020-03-28",
                                            "electricity", 90.0, method, "MODERATE", 42)
        if exit_ is None:
            continue
        outcome, _late, part = exit_
        kind = "paid" if outcome == "success" else "part" if part > 0 else "none"
        outcomes.add(kind)
        owed = triad._ledger_book.ledger(triad.records[-1].account_id).balance(date(2021, 12, 31))
        want = 0.0 if kind == "paid" else round(90.0 - part, 2)
        assert abs(owed - want) < 0.005, (cid, kind, part, owed)
    # The partition first: a final bill paid, part paid and not paid at all all occur here.
    assert outcomes == {"paid", "part", "none"}, outcomes
