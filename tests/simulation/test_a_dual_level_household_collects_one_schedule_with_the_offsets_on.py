"""A dual-fuel level-DD household collects ONE schedule with the dual-fuel offsets on: the amount the
world presents and the desk dunns against (`InLoopLevelCollection`, phase 2b) is the amount the page
collects (`level_dd_schedule_from_the_loop`, phase 4c), and both carry the offsets the post-loop
book sets (`build_dd_balance_book(offsets_dual_fuel_legs=True)`).

Defects these name:
  * the page takes the post-loop rebuild (with offsets) while the world presents the loop's
    schedule (without): on the e50e7b8f68 book, 80 INV_OVERDUE_WITHIN_PAGE_BALANCE and 71
    INV_OVERDUE_WITHIN_BALANCE, level households told they were overdue while their page was in
    credit (SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL_..._2026-11-07.md);
  * the loop asks the book over one leg only, so a debit leg's review is stepped up by the whole
    balance the other leg's credit covers;
  * phase 2b posts a household's legs term by term, so at the electricity leg's review the gas leg
    has not billed past it, and the book reads the gas supply as gone and offers no offset;
  * the stop board answers a leg's bills from a cache taken before that leg's term posted.

The offsets branch must be TAKEN before agreement means anything: the fixture's review has an
offset, and the electricity amount with offsets differs from the amount without.

Mutations performed 2026-11-09, each red here: the loop not passing the offsets switch to the book;
the other leg's bills left out of the ask; `still_supplied` ignored; the board's cache not dropped
on observe; `level_dd_schedule_from_the_loop` keeping the rebuild with offsets on.
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

ELEC, GAS = "C1", "C1g"
OPENING = {ELEC: 30.0, GAS: 120.0}
N_MONTHS, TERM = 30, 12


def _months(start: str, n: int) -> list[str]:
    y, m = (int(p) for p in start.split("-"))
    return [f"{(y * 12 + m - 1 + i) // 12:04d}-{(y * 12 + m - 1 + i) % 12 + 1:02d}" for i in range(n)]


def _rows(cid: str, fuel: str, month: str, kwh: float) -> list[dict]:
    y, m = int(month[:4]), int(month[5:7])
    days = calendar.monthrange(y, m)[1]
    return [{
        "customer_id": cid, "commodity": fuel,
        "settlement_date": f"{y}-{m:02d}-{d:02d}", "settlement_period": 1,
        "consumption_kwh": kwh / days, "unit_rate_gbp_per_mwh": 250.0,
        "revenue_gbp": (kwh / days / 1000) * 250.0 + 0.5, "standing_charge_gbp": 0.5,
        "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0,
    } for d in range(1, days + 1)]


def _kwh(cid: str, i: int, month: str) -> float:
    # Electricity winter-heavy and rising, opened low: a debit builds. Gas flat, opened high: a credit.
    if cid == GAS:
        return 120.0
    return (520.0 if int(month[5:7]) in (11, 12, 1, 2, 3) else 180.0) * (1.0 + 0.25 * (i // 12))


def _fuel(cid: str) -> str:
    return "gas" if cid == GAS else "electricity"


def _post_term_by_term(offsets: bool, **kwargs) -> InLoopLevelCollection:
    """As phase 2b posts: terms by start date, the electricity leg's term before the gas leg's of the
    same start; a leg with a term still to post is still supplied."""
    months = _months("2021-04", N_MONTHS)
    board = StopNoticeBoard(lambda _cid: [])
    pending: dict[str, int] = {ELEC: 0, GAS: 0}
    terms = [months[i:i + TERM] for i in range(0, N_MONTHS, TERM)]
    if kwargs.get("still_supplied", True) is True:
        kwargs["still_supplied"] = lambda leg: pending.get(leg, 0) > 0
    loop = InLoopLevelCollection(board, lambda _cid: None, offsets_dual_fuel_legs=offsets, **kwargs)
    loop._opening.update(OPENING)
    for k, term in enumerate(terms):
        for cid in (ELEC, GAS):
            pending[cid] = len(terms) - k - 1
            for month in term:
                board.observe(_rows(cid, _fuel(cid), month, _kwh(cid, months.index(month), month)))
                loop.collect(cid, month)
    return loop


def _post_loop(offsets: bool):
    months = _months("2021-04", N_MONTHS)
    every = [r for cid in (ELEC, GAS) for i, m in enumerate(months)
             for r in _rows(cid, _fuel(cid), m, _kwh(cid, i, m))]
    bills = build_monthly_bills(every)
    book = build_dd_balance_book(bills, OPENING, dd_spells={}, offsets_dual_fuel_legs=offsets)
    schedule = level_dd_collections(build_dd_level_collection_book(book, supply_starts(bills)),
                                    lambda _cid: True)
    return book, schedule


def test_with_the_offsets_on_the_desk_and_the_page_collect_one_schedule_carrying_the_offset():
    book, rebuilt = _post_loop(offsets=True)
    _, without = _post_loop(offsets=False)
    # The branch is taken: an offset is set at a review, and it moves the electricity amount.
    assert book.dual_fuel_offsets, "the fixture must set an offset, or agreement proves nothing"
    assert any(a["amount_gbp"] != b["amount_gbp"] for a, b in zip(rebuilt[ELEC], without[ELEC]))

    loop = _post_term_by_term(offsets=True)
    assert loop.collected[ELEC] == rebuilt[ELEC]
    assert loop.collected[GAS] == rebuilt[GAS]

    page, reconcile = level_dd_schedule_from_the_loop(loop.collected, rebuilt)
    assert page == loop.collected, "the page must collect what the world presented"
    assert reconcile["source"] == "in_loop"
    assert reconcile["differ"] == 0 and reconcile["only_in_loop"] == reconcile["only_post_loop"] == 0


def test_without_still_supplied_the_first_posted_leg_misses_its_offset():
    """The partition control for `still_supplied`: the term order alone hides the gas supply."""
    _, rebuilt = _post_loop(offsets=True)
    loop = _post_term_by_term(offsets=True, still_supplied=None)
    assert loop.collected[ELEC] != rebuilt[ELEC]


def test_with_the_offsets_off_the_loop_is_what_it_was():
    """Off, the ask is over one leg exactly as before: the dual household's schedule equals the
    offsets-off book's, and a loop built without the new arguments collects the same rows."""
    _, without = _post_loop(offsets=False)
    off = _post_term_by_term(offsets=False)
    assert off.collected == {ELEC: without[ELEC], GAS: without[GAS]}

    months = _months("2021-04", N_MONTHS)
    board = StopNoticeBoard(lambda _cid: [])
    legacy = InLoopLevelCollection(board, lambda _cid: None)
    legacy._opening.update(OPENING)
    for k in range(0, N_MONTHS, TERM):
        for cid in (ELEC, GAS):
            for month in months[k:k + TERM]:
                board.observe(_rows(cid, _fuel(cid), month, _kwh(cid, months.index(month), month)))
                legacy.collect(cid, month)
    assert legacy.collected == off.collected


def test_the_board_answers_a_leg_asked_before_its_rows_arrived_from_the_rows():
    board = StopNoticeBoard(lambda _cid: [])
    assert board.bills_before(GAS, "2021-05-01") == []
    board.observe(_rows(GAS, "gas", "2021-04", 120.0))
    assert [b["period_end"] for b in board.bills_before(GAS, "2021-05-01")] == ["2021-04-30"]


def test_a_leg_asked_by_its_sibling_before_its_first_term_still_collects_its_own_level_amount(monkeypatch):
    """The fixtures above seed `_opening`, so they never reach `_opening_of`. Through it, the
    electricity leg's offsets ask read the gas leg's opening before the gas term had posted, the
    None was cached, and the gas leg collected no level amount for the rest of the run: 291 dual
    gas legs on the b9ad453df0 book (459 households in the loop's schedule, 766 in the rebuild's).
    Offsets off never asks the sibling, so it is the partition control: both legs collect."""
    import simulation.run_phase4c_on_phase2b as phase4c

    monkeypatch.setattr(phase4c, "_opening_dd_by_customer",
                        lambda customers, _rows: {customers[0]["customer_id"]:
                                                  OPENING[customers[0]["customer_id"]]})
    _, rebuilt = _post_loop(offsets=True)
    collected = {}
    for offsets in (False, True):
        months = _months("2021-04", N_MONTHS)
        board = StopNoticeBoard(lambda _cid: [])
        pending: dict[str, int] = {}
        loop = InLoopLevelCollection(board, lambda cid: {"customer_id": cid},
                                     offsets_dual_fuel_legs=offsets,
                                     still_supplied=lambda leg: pending.get(leg, 0) > 0)
        terms = [months[i:i + TERM] for i in range(0, N_MONTHS, TERM)]
        for k, term in enumerate(terms):
            for cid in (ELEC, GAS):
                pending[cid] = len(terms) - k - 1
                for month in term:
                    board.observe(_rows(cid, _fuel(cid), month, _kwh(cid, months.index(month), month)))
                    loop.collect(cid, month)
        collected[offsets] = loop.collected
    assert len(collected[False].get(GAS, [])) == N_MONTHS, "the partition control: offsets off collects gas"
    assert collected[True].get(GAS) == rebuilt[GAS]
    assert collected[True][ELEC] == rebuilt[ELEC]
