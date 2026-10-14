"""DD4b answers the review the household meets, asked in the loop (`simulation/dd_review_in_loop.py`).

Defects these name:
  * the in-loop review tells a different chain from the post-loop review over the same bills
    (a window boundary off by a month, the chain reset, a review told before its year is out);
  * the in-loop review was fed the loop's own settled revenue at TRUE meter kWh, where a real
    supplier reviewing a household with estimated reads holds only its own issued bills
    (`docs/staging/done/SEAT_FINDING_THE_IN_LOOP_DD_REVIEW_IS_TOLD_TRUE_CONSUMPTION_NOT_THE_SUPPLIERS_
    ESTIMATED_BILLS_2026-10-13.md`) -- fixed by asking the SAME assembly door
    (`simulation.run_phase4c_on_phase2b.build_monthly_bills`) the post-loop chain asks, restricted
    to the leg's own rows observed so far, so there is one assembly computing bill content and
    move-in attribution alike, not two;
  * the rare branch -- a material rise told mid-run -- cannot be reached at all;
  * the run loop answers one rise twice, at the renewal and at the review.

Mutations performed 2026-10-12: window bound //12 -> //13 (red), VAT not grossed up (red), a second
answer site in the loop (red). Taking the chain's LAST event in place of the one dated this month stays
green, and that is an equivalence, not a gap: the review is asked only at a window's first bill, and
the newest event then is always dated at that bill.

Mutations performed 2026-10-13 for the final-bill rule: the loop's closure guard off, the run-end
lookup off, the runner's guard off, the guard widened to drop every year of a closed account, the door
dropping `closed_ids`, the post-loop caller dropping `churned_ids` (all red).
"""
from __future__ import annotations

import ast
import calendar
from pathlib import Path

from company.interfaces.dd_review import annual_dd_review_view
from simulation.dd_review_in_loop import InLoopDDReview, reconcile
from simulation.dd_shock_response import DDShockStrengths, respond_to_told_amount
from simulation.run_phase4c_on_phase2b import build_monthly_bills

ROOT = Path(__file__).resolve().parents[2]


def _months(start: str, n: int) -> list[str]:
    y, m = (int(p) for p in start.split("-"))
    out = []
    for i in range(n):
        t = y * 12 + (m - 1) + i
        out.append(f"{t // 12:04d}-{t % 12 + 1:02d}")
    return out


def _month_rows(cid: str, year: int, month: int, kwh: float,
                 unit_rate: float = 150.0, sc_per_day: float = 0.50) -> list[dict]:
    """Real settlement rows, the shape `assemble_monthly_bills` actually reads -- same fixture
    pattern as `tests/company/billing/test_billing_accuracy.py`."""
    days = calendar.monthrange(year, month)[1]
    return [{
        "customer_id": cid,
        "settlement_date": f"{year}-{month:02d}-{d:02d}",
        "settlement_period": 1,
        "consumption_kwh": kwh / days,
        "unit_rate_gbp_per_mwh": unit_rate,
        "revenue_gbp": (kwh / days / 1000) * unit_rate + sc_per_day,
        "standing_charge_gbp": sc_per_day,
        "wholesale_cost_gbp": 0.0,
        "margin_gbp": 0.0,
    } for d in range(1, days + 1)]


def _rows_for(cid: str, start: str, n_months: int, kwh_of_month) -> list[dict]:
    out = []
    for i, month in enumerate(_months(start, n_months)):
        y, m = (int(p) for p in month.split("-"))
        out.extend(_month_rows(cid, y, m, kwh_of_month(i)))
    return out


def _fed_in_loop(cid: str, rows: list[dict], start: str, n_months: int, opening: float):
    """Feeds `rows` through `InLoopDDReview` one month of settled rows at a time, the same
    granularity `simulation/run_phase2b.py` observes (per term) and reviews (per month) at."""
    rv = InLoopDDReview(lambda _cid: None)
    rv._opening[cid] = opening
    for month in _months(start, n_months):
        rv.observe([r for r in rows if r["settlement_date"][:7] == month])
        rv.post(cid, month)
    return rv


def test_the_review_told_in_the_loop_is_the_post_loop_chains_bills_to_the_penny():
    # Two flat years, a year at 3x consumption (an unmissable material rise), two flat years after
    # (the fall the material rise's own review resets the standing DD against).
    def kwh(i):
        return 900.0 if i // 12 == 2 else 300.0

    rows = _rows_for("C1", "2019-07", 60, kwh)
    rv = _fed_in_loop("C1", rows, "2019-07", 60, opening=60.0)
    post = annual_dd_review_view(build_monthly_bills(rows), {"C1": 60.0})["events"]
    assert len(post) == 4
    assert rv.told == post
    assert reconcile(rv.told, post) == {
        "in_loop": 4, "post_loop": 4, "matched": 4, "only_in_loop": 0, "only_post_loop": 0,
        "material_in_loop": 1, "material_post_loop": 1, "material_agree_on_matched": 4,
        "max_abs_rise_gap_on_matched": 0.0,
    }


def test_a_material_rise_is_told_mid_run_and_answered_and_a_fall_is_not():
    def kwh(i):
        return 900.0 if i // 12 == 2 else 300.0

    rows = _rows_for("C1", "2019-07", 60, kwh)
    rv = _fed_in_loop("C1", rows, "2019-07", 60, opening=60.0)
    on = DDShockStrengths(0.0, 0.0, 1.0)
    answered = [respond_to_told_amount(
        household="H1", month=e["review_date"][:7], amount_in_force_gbp=e["current_dd_gbp"],
        new_amount_gbp=e["recommended_monthly_gbp"], stress="LOW", stays=True,
        already_cancelled=False, strengths=on) for e in rv.told]
    # The partition: window w is reviewed at the first bill of w+1. The year that ran at 3x
    # consumption is told a material rise at the next window's open and answered; the year after
    # it is told a fall (and a small opening-year rise) and is not. Both branches reached in one
    # book, same as the pre-fix test this replaces.
    assert [a is not None for a in answered] == [False, False, True, False]
    assert answered[2]["review_month"] == rv.told[2]["review_date"][:7]
    assert rv.told[2]["action"] == "increase" and rv.told[2]["large_increase"]
    assert rv.told[3]["action"] == "decrease"


def test_no_review_is_told_before_a_year_of_bills():
    rows = _rows_for("C1", "2019-07", 6, lambda i: 300.0)
    rv = _fed_in_loop("C1", rows, "2019-07", 6, opening=60.0)
    assert rv.told == []


def test_no_review_is_told_without_an_opening_amount():
    rows = _rows_for("C2", "2019-07", 30, lambda i: 300.0)
    unopened = InLoopDDReview(lambda _cid: None)  # customer_of -> None, so _opening_of -> None
    for month in _months("2019-07", 30):
        unopened.observe([r for r in rows if r["settlement_date"][:7] == month])
        assert unopened.post("C2", month) is None
    assert unopened.told == []


def test_the_run_loop_answers_dd4b_at_one_site_only():
    tree = ast.parse((ROOT / "simulation" / "run_phase2b.py").read_text())
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name)
             and n.func.id in {"respond_to_told_amount", "respond_to_dd_shock", "respond"}]
    assert [c.func.id for c in calls] == ["respond_to_told_amount"]


def _fed_as_the_loop_feeds(legs: dict[str, list[dict]], opening: float, run_end: str):
    """The order `simulation/run_phase2b.py` keeps: month M of a leg is posted once a later month's
    row has been observed, and every leg's last month is posted by the run-end flush."""
    rv = InLoopDDReview(lambda _cid: None, run_end=run_end)
    for cid in legs:
        rv._opening[cid] = opening
    months = sorted({r["settlement_date"][:7] for rows in legs.values() for r in rows})
    open_month: dict[str, str] = {}
    for month in months:
        batch = [r for rows in legs.values() for r in rows if r["settlement_date"][:7] == month]
        rv.observe(batch)
        for cid in sorted({r["customer_id"] for r in batch}):
            if open_month.get(cid, month) != month:
                rv.post(cid, open_month[cid])
            open_month[cid] = month
    for cid, month in open_month.items():
        rv.post(cid, month)
    return rv


def test_a_leavers_final_bill_is_not_reviewed_and_the_run_end_stub_is():
    # `docs/market_research/a_supplier_does_not_review_the_direct_debit_at_an_accounts_final_bill_
    # 2026-10-13.md`. Three legs, one partition. C1 (stays) opens 2023-03 and runs to the run end, so it is
    # told a review at a mid-run month-end (2024-03-31). C2 (leaves) opens on the same day and leaves on
    # 2024-03-31, a month-end, so its final bill is the first bill of its second year: no review in
    # either chain. C3 (stub) opens 2024-06, so its second year starts with the run's own cut-short
    # bill (2025-06-07), and that review is told.
    run_end = "2025-06-07"
    stub_last = [r for r in _month_rows("C3", 2025, 6, 300.0) if r["settlement_date"] <= run_end]
    legs = {
        "C1": _rows_for("C1", "2023-03", 27, lambda i: 300.0) + [
            dict(r, customer_id="C1") for r in stub_last],
        "C2": _rows_for("C2", "2023-03", 13, lambda i: 300.0),
        "C3": _rows_for("C3", "2024-06", 12, lambda i: 300.0) + stub_last,
    }
    rv = _fed_as_the_loop_feeds(legs, 60.0, run_end)
    told = {(e["customer_id"], e["review_date"]) for e in rv.told}
    assert told == {("C1", "2024-03-31"), ("C1", "2025-03-31"), ("C3", run_end)}

    all_rows = [r for rows in legs.values() for r in rows]
    post = annual_dd_review_view(build_monthly_bills(all_rows, {"C2"}),
                                 {c: 60.0 for c in legs}, {"C2"})["events"]
    assert {(e["customer_id"], e["review_date"]) for e in post} == told
    # The same bills with no closure named review C2 at its final bill: the guard is what
    # drops it, not an absent window.
    unclosed = annual_dd_review_view(build_monthly_bills(all_rows, {"C2"}),
                                     {c: 60.0 for c in legs})["events"]
    assert ("C2", "2024-03-31") in {(e["customer_id"], e["review_date"]) for e in unclosed}


def test_both_production_callers_hand_over_what_the_final_bill_rule_reads():
    # The rule above reaches the run only if the post-loop review is given the closed accounts and
    # the in-loop review is given the run's end. Without them both guards are silently off.
    def calls(path: str, name: str):
        tree = ast.parse((ROOT / "simulation" / path).read_text())
        return [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name) and n.func.id == name]

    [post] = calls("run_phase4c_on_phase2b.py", "annual_dd_review_view")
    assert len(post.args) + len(post.keywords) == 3
    [loop] = calls("run_phase2b.py", "InLoopDDReview")
    assert [k.arg for k in loop.keywords] == ["run_end"]
