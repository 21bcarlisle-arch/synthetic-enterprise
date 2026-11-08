"""Level DD step 2b: phase 2b asks the balance book for each level leg's collection as the month
posts (`simulation/dd_review_in_loop.InLoopLevelCollection`), and phase 4c hands the page that
schedule (`level_dd_schedule_from_the_loop`).

Defects these name:
  * the loop's schedule differs from the book the post-loop chain builds over the same bills: a
    window asked from the wrong anchor, an amount cached past its window, a step-up the loop
    cannot see, or a collection dated off the Bacs day or before supply;
  * the cache never refreshes, so every month collects the opening amount -- the control asserts
    the amount changes across windows before asserting the loop agrees (a guard that never moves
    would agree with a book that never moves);
  * phase 4c keeps the hindsight rebuild although the loop collected, or takes the loop's schedule
    while the dual-fuel offsets (which the loop does not ask) are on.

Mutations performed 2026-11-08: the window test in `collect` removed so the first ask is reused
for the run (red, the amounts-move leg); the cutoff one month early so month m's bill is not in
the book (red, every month None); `level_dd_schedule_from_the_loop` ignoring the offsets switch
(red); the supply start not passed to the collection dates (red).
"""
from __future__ import annotations

import calendar

from simulation.dd_balance_book import build_dd_balance_book
from simulation.dd_collection_book import StopNoticeBoard
from simulation.dd_level_collection_book import (
    build_dd_level_collection_book,
    level_dd_collections,
    supply_starts,
)
from simulation.dd_review_in_loop import InLoopLevelCollection, level_dd_schedule_from_the_loop
from simulation.run_phase4c_on_phase2b import build_monthly_bills

CID = "C1"


def _months(start: str, n: int) -> list[str]:
    y, m = (int(p) for p in start.split("-"))
    return [f"{(y * 12 + m - 1 + i) // 12:04d}-{(y * 12 + m - 1 + i) % 12 + 1:02d}" for i in range(n)]


def _rows(month: str, kwh: float, first_day: int = 1) -> list[dict]:
    y, m = int(month[:4]), int(month[5:7])
    days = calendar.monthrange(y, m)[1]
    return [{
        "customer_id": CID, "commodity": "electricity",
        "settlement_date": f"{y}-{m:02d}-{d:02d}", "settlement_period": 1,
        "consumption_kwh": kwh / days, "unit_rate_gbp_per_mwh": 250.0,
        "revenue_gbp": (kwh / days / 1000) * 250.0 + 0.5, "standing_charge_gbp": 0.5,
        "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0,
    } for d in range(first_day, days + 1)]


def _seasonal(i: int, month: str) -> float:
    # Winter-heavy and rising year on year, so the review moves the amount and a debit builds.
    return (520.0 if int(month[5:7]) in (11, 12, 1, 2, 3) else 180.0) * (1.0 + 0.25 * (i // 12))


def _run(n_months: int = 40, opening: float = 30.0):
    months = _months("2019-04", n_months)
    board = StopNoticeBoard(lambda _cid: [])
    loop = InLoopLevelCollection(board, lambda _cid: None)
    loop._opening[CID] = opening
    every: list[dict] = []
    for i, month in enumerate(months):
        rows = _rows(month, _seasonal(i, month), first_day=20 if i == 0 else 1)
        every.extend(rows)
        board.observe(rows)
        loop.collect(CID, month)
    bills = build_monthly_bills(every)
    book = build_dd_balance_book(bills, {CID: opening}, dd_spells={})
    rebuilt = level_dd_collections(build_dd_level_collection_book(book, supply_starts(bills)),
                                   lambda _cid: True)
    return loop, rebuilt


def test_the_loop_collects_the_amount_the_post_loop_book_sets_every_month():
    loop, rebuilt = _run()
    in_loop = loop.collected[CID]
    amounts = {r["amount_gbp"] for r in in_loop}
    # The branch exists to be taken: the amount must move across windows, or agreement proves nothing.
    assert len(amounts) >= 3, amounts
    assert len(in_loop) == len(rebuilt[CID]) == 40
    assert in_loop == rebuilt[CID]
    # Once a window, not once a month.
    assert loop.books_asked <= 5, loop.books_asked


def test_the_first_collection_waits_for_supply_and_lands_on_a_bacs_day():
    loop, _ = _run(n_months=3)
    # Supply starts Sat 20 Apr 2019, after the leg's payment day (the 14th): the mandate schedules
    # the first collection on the supply start, and Bacs collects it on Tue 23rd (Easter Monday 22nd).
    first = loop.collected[CID][0]
    assert first["scheduled_date"] == "2019-04-20"
    assert first["collection_date"] == "2019-04-23"


def test_phase_4c_reads_the_loop_schedule_and_keeps_the_rebuild_only_where_the_loop_cannot_ask():
    loop, rebuilt = _run(n_months=14)
    altered = {CID: [dict(r) for r in loop.collected[CID]]}
    altered[CID][-1]["amount_gbp"] += 1.0
    schedule, reconcile = level_dd_schedule_from_the_loop(altered, rebuilt, False)
    assert schedule == altered and reconcile["source"] == "in_loop"
    assert reconcile["differ"] == 1 and reconcile["matched"] == 13
    schedule, reconcile = level_dd_schedule_from_the_loop(altered, rebuilt, True)
    assert schedule == rebuilt and reconcile["source"] == "post_loop_rebuild"
    schedule, reconcile = level_dd_schedule_from_the_loop(None, rebuilt, False)
    assert schedule == rebuilt and reconcile["source"] == "post_loop_rebuild"
