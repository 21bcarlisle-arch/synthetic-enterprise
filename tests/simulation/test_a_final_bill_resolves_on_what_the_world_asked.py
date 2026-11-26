"""A mover's final bill resolves on what the world ASKED (its face less the credit it netted, plus
the scheme's debit beside it), never on its face (SEAT_PREREG_THE_PAGE_RESOLVES_A_FINAL_BILL_ON_THE_
WORLDS_ASK_2026-11-26.md).

Defects this file exists to catch:
  * the page pays a level leg's final bill at its face and refunds the credit the world had netted
    (SYN-2016-244: 52.26 paid, 26.71 refunded, where the world asked 25.55);
  * the part a gone household paid is a share of the face, so it can exceed the ask
    (OCC-cede70b10116g: 57.23 part-paid of a 3.61 ask);
  * a part above the charges is taken off the face, opening a negative case (PROS-2016-0370g).
"""
from datetime import date, timedelta
from types import SimpleNamespace

import simulation.arrears_engine as ae
import simulation.world_payment_truth as wpt
from tests.simulation.test_world_payment_truth import MONTHS, _book, _truth


def _final(**told):
    truth = _truth(failed=(), months=MONTHS)
    truth["outcomes"][MONTHS[-1][:7]].update(told)
    bills, behavioral, _ = _book(truth)
    return next(r for r in ae._resolve_bills(bills, behavioral, 42)
                if r["period_end"] == MONTHS[-1] and r["outcome"] != "repayment")


def test_a_part_share_is_of_the_ask_and_a_part_above_the_charges_paid_the_debit():
    face = _final(result="failed")["amount_gbp"]
    netted = _final(result="failed", part_share=0.5, credit_taken_gbp=face - 10.0)
    assert netted["part_paid_gbp"] == 5.0 and netted["debit_paid_gbp"] == 0.0
    # Share of face + 2 x face: 1.5 x face paid, so the charges are met and half a face of debit.
    over = _final(result="failed", part_share=0.5, debit_asked_gbp=2 * face)
    assert over["amount_gbp"] == 0.0 and over["part_paid_gbp"] == face
    assert abs(over["debit_paid_gbp"] - 0.5 * face) < 0.011
    # The world's own cash, when the book carries it, wins over the share.
    cash = _final(result="failed", part_share=0.5, part_paid_gbp=3.0)
    assert cash["part_paid_gbp"] == 3.0 and cash["amount_gbp"] == round(face - 3.0, 2)


def test_the_payment_truth_carries_the_credit_and_the_part_cash_onto_the_final_month():
    month = wpt.bill_month_of(5)
    rec = SimpleNamespace(customer_id="L", period_index=5, result="failed", days_late=0,
                          payment_method="direct_debit", account_id="A", due_date=date(2020, 6, 1),
                          settled_on=None)
    triad = SimpleNamespace(
        records=[rec], _final_bill_part_share={}, _crossed_settlements=[],
        _household_plans=SimpleNamespace(_terms={}),
        _final_month_nets=[{"leg": "L", "bill_month": month, "debit_asked_gbp": 0.0,
                            "credit_taken_gbp": 26.71, "part_paid_gbp": 1.75}])
    told = wpt.build(triad, date(2025, 6, 30))["L"]["outcomes"][month]
    assert told["credit_taken_gbp"] == 26.71 and told["part_paid_gbp"] == 1.75
    assert "debit_asked_gbp" not in told


def _row(month, outcome, amount, method="direct_debit", **extra):
    pe = f"2020-{month:02d}-28"
    return {"customer_id": "L", "period_end": pe, "commodity": "electricity", "amount_gbp": amount,
            "due_date": date.fromisoformat(pe) + timedelta(days=14), "method": method,
            "outcome": outcome, "days_late": 0, **extra}


def _close(credit_taken):
    """A level leg whose only level collection came back, and whose settlement of it left 20 over,
    paying a 30 final on receipt. No level collection succeeded, so the close's own netting of a
    level surplus (which needs one) cannot reach it: SYN-2016-244's shape."""
    level = {"L": [{"month": "2020-01", "collection_date": "2020-01-19", "amount_gbp": 50.0}]}
    rows = [_row(1, "failed", 50.0), _row(2, "success", 50.0, method="standard_credit"),
            {**_row(3, "repayment", 70.0, method=None), "due_date": date(2020, 3, 20),
             "repayment_kind": "settlement", "settles_month": "2020-01"},
            _row(5, "success", 30.0, method="standard_credit", credit_taken_gbp=credit_taken)]
    closing = {}
    _, credited = ae.balance_settlement_from_outcomes(rows, {"L"}, closing,
                                                      level_dd_collections=level)
    final = credited.get(("L", "2020-05-28", "electricity"), [])
    return closing["L"], round(sum(c["amount_gbp"] for c in final if c["kind"] == "credit"), 2)


def test_a_level_legs_final_bill_nets_the_credit_the_world_took_and_only_then():
    # Both sides of the branch: held to the close and refunded without the world's word, netted
    # against the final bill as credit with it.
    assert _close(0.0) == (-20.0, 0.0)
    assert _close(20.0) == (0.0, 20.0)
