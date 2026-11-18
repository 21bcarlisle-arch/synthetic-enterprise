"""N29, home_moves.md s.8.8e choice 30: the close set-off reads the other fuel's debt on the refund
day, a bill issued by then and collected after it included.

The defect this catches: the set-off read the debt leg's balance after every payment the run would
ever make, so a final bill its direct debit collected days after the refund counted as paid and was
not set off. On run_output_8a300fa561, 23 refunds (GBP 483.51) were paid while the same household
owed that money on its other fuel. With `later_cash` ignored, the first test reads no set-off.
"""
from __future__ import annotations

import datetime as dt

from simulation.arrears_engine import balance_settlement_from_outcomes, bill_due_date
from simulation.credit_refund_events import generate_credit_refund_log, set_offs_from_refund_log


def _final_bill(cid: str, period_end: str, amount: float, days_late: int) -> dict:
    return {"customer_id": cid, "period_end": period_end, "commodity": "gas",
            "due_date": bill_due_date(cid, period_end), "outcome": "success",
            "amount_gbp": amount, "days_late": days_late, "method": "direct_debit"}


def _close(debt_leg_days_late: int):
    """H1 closes 100 in credit; H1g's 60 final bill is collected `debt_leg_days_late` after due."""
    rows = [_final_bill("H1g", "2023-06-10", 60.0, debt_leg_days_late)]
    closing: dict[str, float] = {}
    later: dict = {}
    balance_settlement_from_outcomes(rows, {"H1g"}, closing, later_cash_out=later)
    closing["H1"] = -100.0
    bills = [{"customer_id": "H1", "period_end": "2023-06-10"}, rows[0]]
    log = generate_credit_refund_log(bills, {}, closing, later_cash=later)
    return rows, closing, later, {e["customer_id"]: e for e in log}


def test_both_sides_of_the_refund_day_occur():
    """The partition first: one debt bill is still unpaid on the refund day, the other is paid
    before it. Without both, the tests below prove nothing."""
    _, _, later, log = _close(10)
    refund_day = dt.date.fromisoformat(log["H1"]["paid_date"])
    issued, paid, _ = later["H1g"][0]
    assert issued <= refund_day < paid
    _, _, later, log = _close(-30)
    assert later["H1g"][0][1] <= dt.date.fromisoformat(log["H1"]["paid_date"])


def test_a_final_bill_collected_after_the_refund_is_set_off():
    _, closing, _, log = _close(10)
    assert closing["H1g"] == 0.0, "the closing balance reads the bill as paid"
    assert log["H1"]["set_off_gbp"] == 60.0 and log["H1"]["set_off_against"] == "H1g"
    assert log["H1"]["credit_amount_gbp"] == 40.0


def test_a_bill_paid_before_the_refund_day_is_not_set_off():
    _, _, _, log = _close(-30)
    assert log["H1"]["set_off_gbp"] == 0.0 and log["H1"]["credit_amount_gbp"] == 100.0


def test_the_set_off_bill_asks_only_the_rest_and_the_debt_leg_closes_square():
    """The collection after the refund takes the bill less the set-off (SLC 31H.12), so the
    household is not refunded on one fuel and debited the same money on the other."""
    rows, _, _, log = _close(10)
    closing: dict[str, float] = {}
    later: dict = {}
    written, credited = balance_settlement_from_outcomes(
        rows, {"H1g"}, closing, set_offs=set_offs_from_refund_log(list(log.values())),
        later_cash_out=later)
    met = credited[("H1g", "2023-06-10", "gas")]
    assert [(c["kind"], c["amount_gbp"], c["credit_period_end"]) for c in met] == [("set_off", 60.0, "H1")]
    assert "H1g" not in later, "the bill asked nothing once the set-off met it"
    assert written == {}
    assert closing["H1g"] == 0.0, "closing_out stays the balance at close before the set-off"



def test_a_bill_collected_on_the_refund_day_does_not_draw_the_set_off():
    """The set-off meets the debt at the END of the refund day, after that day's collections. This
    level leg owes a 20 shortfall, not a bill: sorted before the day's payments, the final bill
    collected that day (after the last level collection, so at its face) drew the set-off, and the
    shortfall stayed owed (SYN-2016-047g 131.29, -234 4.62 on the N29 replay)."""
    from simulation.arrears_engine import paid_on

    rows = [{"customer_id": "PART", "period_end": f"2020-{m:02d}-28", "commodity": "electricity",
             "amount_gbp": 50.0, "due_date": dt.date(2020, m, 28) + dt.timedelta(days=14),
             "method": "direct_debit", "outcome": "success", "days_late": 0} for m in (1, 2, 3)]
    level = {"PART": [{"month": f"2020-{m:02d}", "collection_date": f"2020-{m + 1:02d}-01",
                       "amount_gbp": 40.0} for m in (1, 2)]}
    day = paid_on(rows[-1]["due_date"], 0, "direct_debit")
    log = [{"customer_id": "PARTg", "paid_date": day.isoformat(), "set_off_gbp": 20.0,
            "set_off_against": "PART"}]
    closing: dict[str, float] = {}
    _, credited = balance_settlement_from_outcomes(
        rows, {"PART"}, closing, level_dd_collections=level, set_offs=set_offs_from_refund_log(log))
    assert closing["PART"] == 20.0, "the shortfall the set-off is for"
    assert not any(c["kind"] == "set_off" for v in credited.values() for c in v), \
        "the bill collected on the refund day drew the set-off"
