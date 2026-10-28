"""A month inside the unnamed occupier's window stays the occupier's when the deemed account's EBSS
credit paid it.

The world books each window row's energy as `occupier_debt_gbp`, net of the credit, so a month the
credit wholly paid carries debt 0 on every row. Bill assembly took the share as debt over revenue, so
that month read as share 0, and the arrears engine asked the named payer for the whole bill
(OCC-bec72a04dec8, Dec 2022 to Feb 2023; 14 bills, GBP 1,160 on the 1691ec0ecd book). The payer was
then asked for days the government's credit had already paid.
"""
import simulation.arrears_engine as ae
from simulation.run_phase4c_on_phase2b import build_monthly_bills
from tests.simulation.test_run_phase4c_on_phase2b import make_record


def _month(cid, window_days, days=31, kwh=10.0, credit_per_row=None):
    """Dec 2022, the first `window_days` days inside the window. Each window row's debt is its
    revenue less what the credit paid of it, as `occupier_scheme_credit` books it."""
    rows = []
    for d in range(1, days + 1):
        r = make_record(cid, "2022-12-%02d" % d, kwh)
        if d <= window_days:
            paid = r["revenue_gbp"] if credit_per_row is None else min(credit_per_row, r["revenue_gbp"])
            r["occupier_scheme_credit_gbp"] = paid
            r["occupier_debt_gbp"] = r["revenue_gbp"] - paid
        rows.append(r)
    rows[0]["occupier_scheme_month_credit_gbp"] = 67.0
    return rows


def _bill(rows):
    (bill,) = [b for b in build_monthly_bills(rows) if b["period_end"].startswith("2022-12")]
    return bill


def test_the_partition_holds_both_a_whole_and_a_part_window_month():
    """Control: the whole-window month's debt is 0, so the old debt-over-revenue reading is 0."""
    whole, part = _month("C1", 31), _month("C1", 15)
    assert sum(r["occupier_debt_gbp"] for r in whole if "occupier_debt_gbp" in r) == 0.0
    assert any("occupier_debt_gbp" in r for r in part) and any(
        "occupier_debt_gbp" not in r for r in part)


def test_a_window_month_the_credit_paid_is_wholly_the_occupiers():
    bill = _bill(_month("C1", 31))
    assert bill.get("occupier_share") == 1.0, bill.get("occupier_share")


def test_the_credit_does_not_shrink_a_part_window_months_share():
    bill = _bill(_month("C1", 15, credit_per_row=0.5))
    assert abs(bill["occupier_share"] - 15 / 31) < 1e-9, bill["occupier_share"]


def test_no_payer_is_asked_for_a_window_month_the_credit_paid():
    bill = _bill(_month("C1", 31))
    rows = ae._resolve_bills([bill], {}, 42)
    assert not rows, rows
