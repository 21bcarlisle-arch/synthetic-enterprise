"""A mover's bills on a DD leg are collected on their date or returned, like every other DD.

Two defects, both found as the "missed DD without a return" leg of
INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE on the 209c3350ab book (38 bills on 35 accounts, every
one a mover's):

* 21 were the bill BEFORE the final one. The triad asked the exit model with the bill's due date where
  it takes the period end, so a bill for the month before the move, due in the move month, was drawn
  as a final bill and could come back paid weeks late;
* 17 were the final bill itself: the exit model's PAID_LATE kept its lateness on a DD leg, so a DD was
  "collected" up to 77 days after its date with no return.

Knowledge: `docs/market_research/payments_and_direct_debit_2026-10-25.md`, "A DD is never late".
"""
from __future__ import annotations

from datetime import date

import simulation.arrears_engine as ae
import simulation.world_payment_truth as wpt
from background.live_payment_triad import LivePaymentTriad

STAMP = {"moved_out_on": "2022-06-20"}


def _exits(method):
    out = []
    for i in range(400):
        e = ae.mover_final_bill_outcome(STAMP, f"MV{i:04d}", "2022-06-19", "electricity", 150.0,
                                        method, "HIGH", 42)
        if e is not None and e[0] == "success":
            out.append(e[1])
    return out


def test_a_paid_final_bill_on_a_dd_leg_is_collected_on_its_date():
    """Defect: the exit model's PAID_LATE kept its days late on a DD leg."""
    receipt = _exits(ae.PAY_ON_RECEIPT_METHOD)
    # The late branch can be taken at all: a pay-on-receipt mover does pay a final bill late.
    assert any(d > 0 for d in receipt), receipt
    dd = _exits(ae.DD_METHOD)
    assert dd and all(d == 0 for d in dd), sorted(set(dd))
    # Only the date moves: the same households pay.
    assert len(dd) == len(receipt)


def test_the_bill_before_the_final_is_not_the_exit(monkeypatch):
    """Defect: the triad asked the exit model with the due date, so the May bill, due in June, of a
    household that left on 20 June was drawn as its final bill."""
    monkeypatch.setattr(wpt, "UNIFIED", True)
    seen = []
    real = ae.mover_final_bill_outcome

    def spy(behavioral, cid, period_end, *a, **k):
        out = real(behavioral, cid, period_end, *a, **k)
        seen.append((period_end, out is not None))
        return out

    monkeypatch.setattr("background.live_payment_triad.mover_final_bill_outcome", spy)
    triad = LivePaymentTriad()
    for i in range(20):
        cid = f"RESI{i:05d}"
        triad.record_period(customer_id=cid, due_date=date(2022, 6, 14), amount_gbp=90.0,
                            income_stress_value="moderate", segment="resi", bill_month="2022-05",
                            moved_out_on="2022-06-20")
        triad.record_period(customer_id=cid, due_date=date(2022, 7, 8), amount_gbp=40.0,
                            income_stress_value="moderate", segment="resi", bill_month="2022-06",
                            moved_out_on="2022-06-20")
    # Each bill is asked by its period end (none given here, so the month's last day or the last
    # supplied day): the May bill comes back None, and the final bill reaches the exit model (a
    # meter-paying household's comes back None too).
    assert {d for d, _ in seen} == {"2022-05-31", "2022-06-19"}, seen
    assert not any(hit for d, hit in seen if d == "2022-05-31"), seen
    assert any(hit for d, hit in seen if d == "2022-06-19"), seen
