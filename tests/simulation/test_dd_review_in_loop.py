"""DD4b answers the review the household meets, asked in the loop (`simulation/dd_review_in_loop.py`).

Defects these name:
  * the in-loop review tells a different chain from the post-loop review over the same bills
    (a window boundary off by a month, the chain reset, a review told before its year is out);
  * the rare branch -- a material rise told mid-run -- cannot be reached at all;
  * the run loop answers one rise twice, at the renewal and at the review.

Mutations performed 2026-10-12: window bound //12 -> //13 (red), VAT not grossed up (red), a second
answer site in the loop (red). Taking the chain's LAST event in place of the one dated this month stays
green, and that is an equivalence, not a gap: the review is asked only at a window's first bill, and
the newest event then is always dated at that bill.
"""
from __future__ import annotations

import ast
from pathlib import Path

from company.interfaces.dd_review import annual_dd_review_view
from simulation.dd_review_in_loop import InLoopDDReview, reconcile
from simulation.dd_shock_response import DDShockStrengths, respond_to_told_amount
from simulation.price_cap_enforcement import DOMESTIC_VAT_RATE

ROOT = Path(__file__).resolve().parents[2]


def _months(start: str, n: int) -> list[str]:
    y, m = (int(p) for p in start.split("-"))
    out = []
    for i in range(n):
        t = y * 12 + (m - 1) + i
        out.append(f"{t // 12:04d}-{t % 12 + 1:02d}")
    return out


def _book(amounts_by_year: list[float], start: str = "2019-07") -> tuple[InLoopDDReview, list]:
    """One leg billed monthly; a year's monthly ex-VAT amount per element of `amounts_by_year`."""
    rv = InLoopDDReview(lambda cid: None)
    rv._opening["C1"] = 60.0  # the opening amount the door would have set
    for i, month in enumerate(_months(start, 12 * len(amounts_by_year))):
        rv.post("C1", month, amounts_by_year[i // 12])
    return rv, rv._bills["C1"]


def test_the_review_told_in_the_loop_is_the_post_loop_chain_month_for_month():
    rv, bills = _book([55.0, 60.0, 110.0, 70.0])
    post = annual_dd_review_view(bills, {"C1": 60.0})["events"]
    assert len(post) == 3
    assert rv.told == post
    assert reconcile(rv.told, post)["only_in_loop"] == 0


def test_a_material_rise_is_told_mid_run_and_answered_and_a_fall_is_not():
    rv, _ = _book([55.0, 60.0, 110.0, 70.0, 70.0])
    on = DDShockStrengths(0.0, 0.0, 1.0)
    answered = [respond_to_told_amount(
        household="H1", month=e["review_date"][:7], amount_in_force_gbp=e["current_dd_gbp"],
        new_amount_gbp=e["recommended_monthly_gbp"], stress="LOW", stays=True,
        already_cancelled=False, strengths=on) for e in rv.told]
    # The partition: window w is reviewed at the first bill of w+1. The year that ran at 110 a
    # month is told a material rise at 2022-07 and answered; the year after it is told a fall and
    # is not, nor is a small rise. Both branches are reached in one book.
    assert [a is not None for a in answered] == [False, False, True, False]
    assert answered[2]["review_month"] == "2022-07"
    assert rv.told[2]["recommended_monthly_gbp"] > 110.0 * (1 + DOMESTIC_VAT_RATE) - 1


def test_no_review_is_told_before_a_year_of_bills_or_without_an_opening_amount():
    rv, _ = _book([55.0])
    assert rv.told == []
    unopened = InLoopDDReview(lambda cid: None)
    for month in _months("2019-07", 30):
        assert unopened.post("C2", month, 80.0) is None


def test_the_run_loop_answers_dd4b_at_one_site_only():
    tree = ast.parse((ROOT / "simulation" / "run_phase2b.py").read_text())
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name)
             and n.func.id in {"respond_to_told_amount", "respond_to_dd_shock", "respond"}]
    assert [c.func.id for c in calls] == ["respond_to_told_amount"]
