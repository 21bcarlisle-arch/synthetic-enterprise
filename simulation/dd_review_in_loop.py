"""The supplier's annual DD review, asked IN THE LOOP, so the household is told its new amount the
month the review is taken and can answer it before its next collection is drawn.

WHY THIS EXISTS (`docs/staging/WORLD_FREEZE_DD_SHOCK_SAVE_AND_MOVER_AT_THEIR_RANGE_ENDS_2026-10-12.md`
s1). The review ran only after the loop (`run_phase4c_on_phase2b`, over the finished bills), where no
payment is drawn, so DD4b could answer a rise only at a RENEWAL: on 200 founders it saw 10 of the
world's 299 material rises and none of the 122 in 2022-23. Over 7m real SVT direct debits rose in
2022 by review of a default-tariff household's DD, not at a renewal (`what_bill_shock_is.md`).

WHAT IS ASKED, AND OF WHOM. The review is the supplier's: this module asks the company's own door
(`company.interfaces.dd_review.annual_dd_review_view`, the one the post-loop review uses) over the
leg's bills posted so far, and is told an amount. None of the desk's rule crosses. The review is
causal by construction -- window w is reviewed at the first bill of window w+1, from window w's
bills only -- so asking it as the bills arrive gives the post-loop chain's events at the month they
fall, provided the bills are the same.

THE BILLS ARE THE SUPPLIER'S OWN, THE SAME ONES THE POST-LOOP CHAIN BILLS
(`docs/staging/done/SEAT_FINDING_THE_IN_LOOP_DD_REVIEW_IS_TOLD_TRUE_CONSUMPTION_NOT_THE_SUPPLIERS_
ESTIMATED_BILLS_2026-10-13.md`, remedy; knowledge pass
`docs/market_research/a_suppliers_annual_dd_review_is_sized_from_its_own_issued_bills_not_true_
consumption_2026-10-13.md`). This used to gross up the loop's own settled revenue at true meter kWh --
a figure no real supplier holds where a read is estimated. It now calls the SAME assembly door the
post-loop chain calls (`simulation.run_phase4c_on_phase2b.build_monthly_bills`, the world's wrapper
over `company.billing.monthly_bill_assembly.assemble_monthly_bills` and
`simulation.meter_reads.SimulatedReadFeed`), restricted to this leg's own settled rows observed so
far. `SimulatedReadFeed.read_for` seeds its RNG on `(customer_id, period_end)` alone
(`simulation/meter_reads.py`), so a bill assembled here from a subset of rows is byte-identical to the
one the post-loop chain assembles later from the complete history -- there is no second estimate to
agree with, only one assembly asked twice. `churned_ids` is deliberately never passed: whether this
leg will churn is not yet knowable to a chain running causally inside the leg's own history, so no
bill here is ever forced to a final-read resolution the way the post-loop chain's genuinely-last bill
can be -- the honest asymmetry of asking mid-run rather than after the fact.

THE MOVE-IN ATTRIBUTION (the SEAT_FINDING's second named cause: a mover's first window dropping the
owner's void and unnamed-occupier months the post-loop bills include) is resolved by construction, not
by a separate rule: both chains now attribute a leg's rows through the one assembly call that decides
it, so there is nothing left for two attributions to disagree about.

The opening amount -- what the supplier set at sign-up -- is asked through the same door as the
post-loop review (`_opening_dd_by_customer`), from the leg's registration and its first settled month.
A leg with no opening amount is never reviewed here either, exactly as there.

WHERE THE TOLD EVENT IS LOOKED FOR (`docs/market_research/a_supplier_does_not_review_the_direct_debit_
at_an_accounts_final_bill_2026-10-13.md`). The post-loop review is dated at the first bill of the new
window, and that bill ends either at month-end or, in the run's last month, at the run's last settled
day, where the horizon cuts it short. `post` looks at exactly those two dates. A leaver's final bill
ends on its own last day. The post-loop chain reviews no closed account there, and the loop must not
tell one either, including a leaver whose last day happens to be a month-end. The loop knows it is
looking at a final bill because a leg's last month is posted only by the run-end flush, once all its
rows are in. If its last settled day falls in that month and before the run's end, the leg has left
supply.
"""
from __future__ import annotations

from datetime import date
from typing import Callable, Mapping, Optional


def _month_end(month: str) -> str:
    year, mon = (int(p) for p in month.split("-"))
    nxt = date(year + (mon == 12), mon % 12 + 1, 1)
    return date.fromordinal(nxt.toordinal() - 1).isoformat()


def _months_between(a: str, b: str) -> int:
    return (int(b[:4]) - int(a[:4])) * 12 + (int(b[5:7]) - int(a[5:7]))


class InLoopDDReview:
    """Per leg: the settled rows observed so far and its first settled month's rows. `post` returns
    the review event told THIS month (the company's serialised event), or None."""

    def __init__(self, customer_of: Callable[[str], Optional[dict]], run_end: Optional[str] = None):
        self._customer_of = customer_of
        self._run_end = run_end
        self._rows: dict[str, list[dict]] = {}
        self._first_month_rows: dict[str, list[dict]] = {}
        self._first_month: dict[str, str] = {}
        self._last_window: dict[str, int] = {}
        self._last_day: dict[str, str] = {}
        self._opening: dict[str, Optional[float]] = {}
        self.told: list[dict] = []

    def observe(self, rows) -> None:
        """The committed daily rows: kept in full per leg, so a window close can re-ask the
        supplier's own assembly door over this leg's whole history, same as the post-loop chain
        does over the whole run's. Each leg's first settled month is additionally kept apart --
        all the opening amount reads (`sold_unit_rate`, `sold_standing_charge`)."""
        for r in rows:
            cid = r.get("customer_id")
            month = r["settlement_date"][:7]
            self._rows.setdefault(cid, []).append(r)
            day = r["settlement_date"][:10]
            if day > self._last_day.get(cid, ""):
                self._last_day[cid] = day
            first = self._first_month.setdefault(cid, month)
            if month == first:
                self._first_month_rows.setdefault(cid, []).append(r)

    def _opening_of(self, cid: str) -> Optional[float]:
        if cid not in self._opening:
            from simulation.run_phase4c_on_phase2b import _opening_dd_by_customer
            customer = self._customer_of(cid)
            self._opening[cid] = (None if customer is None else _opening_dd_by_customer(
                [customer], self._first_month_rows.get(cid, [])).get(cid))
        return self._opening[cid]

    def post(self, cid: str, month: str) -> Optional[dict]:
        first = self._first_month.get(cid)
        if first is None:
            return None
        window = _months_between(first, month) // 12
        starts_a_window = window != self._last_window.get(cid, 0)
        self._last_window[cid] = window
        if not starts_a_window:
            return None
        last = self._last_day[cid]
        if self._run_end is not None and last[:7] == month and last < self._run_end:
            return None
        opening = self._opening_of(cid)
        if opening is None:
            return None
        from simulation.run_phase4c_on_phase2b import build_monthly_bills
        bills = build_monthly_bills(self._rows.get(cid, []))
        from company.interfaces.dd_review import annual_dd_review_view
        period_end = _month_end(month)
        if self._run_end is not None and self._run_end[:7] == month:
            period_end = min(period_end, self._run_end)
        events = annual_dd_review_view(bills, {cid: opening})["events"]
        told = next((e for e in events if e["review_date"] == period_end), None)
        if told is not None:
            self.told.append(told)
        return told


def reconcile(told: list[dict], post_loop_events: list[dict]) -> dict:
    """How the reviews told in the loop compare with the post-loop review's, keyed on (customer,
    review month): matched, only-in-loop, only-post-loop, and the material-rise agreement on the
    matched ones (rise over 15%, the census's reading)."""
    def key(e):
        return (e["customer_id"], e["review_date"][:7])

    def rise(e):
        cur = e["current_dd_gbp"]
        return (e["recommended_monthly_gbp"] - cur) / cur if cur else 0.0

    a = {key(e): e for e in told}
    b = {key(e): e for e in post_loop_events}
    both = sorted(set(a) & set(b))
    return {
        "in_loop": len(a), "post_loop": len(b), "matched": len(both),
        "only_in_loop": len(set(a) - set(b)), "only_post_loop": len(set(b) - set(a)),
        "material_in_loop": sum(1 for e in a.values() if rise(e) > 0.15),
        "material_post_loop": sum(1 for e in b.values() if rise(e) > 0.15),
        "material_agree_on_matched": sum(1 for k in both if (rise(a[k]) > 0.15) == (rise(b[k]) > 0.15)),
        "max_abs_rise_gap_on_matched": round(max((abs(rise(a[k]) - rise(b[k])) for k in both),
                                                 default=0.0), 4),
    }


class InLoopLevelCollection:
    """Step 2b of the level-DD finding (`docs/staging/SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_
    DUNNED_PER_BILL_SO_ITS_PAGE_PRINTS_OVERDUE_WHILE_IN_CREDIT_2026-11-07.md`): the level amount a
    household's bank pays THIS month, asked of the balance book (`build_dd_balance_book`) over the
    leg's bills and DD spells known so far, as the month posts.

    The post-loop schedule (`run_phase4c_on_phase2b`, `build_dd_level_collection_book`) rebuilt it
    after the run from every bill. Step 2a (ee0982734c) made the book causal, so a book over the
    bills to month m gives month m the amount the full book gives it; asked here, phase 2b and the
    page collect one schedule, and nothing in it is sized from a bill not yet issued.

    ASKED ONCE A WINDOW. The book's standing amount is set at the first DD bill of each 12-month
    window (anchored on the leg's first DD bill) and its step-up is taken then too, so it is fixed
    for the window: a later month of the window reads the amount asked at its first. A new window,
    a first ask, or a leg billed as one that left asks the book again.

    The bills are the stop board's (`StopNoticeBoard.bills_before`): the same assembly, rebilled for
    N14 as the published run is, before the pre-bill gate, because phase 4c builds its book over
    those. The spells are the rails' over the issued bills (`supplier_dd_spells`), as
    `dd_spells_from_run` reads them post-run. Not asked: the closed set (a final bill's bar moves
    no collected amount) and the dual-fuel offsets (`offsets_dual_fuel_legs`; off by default, and a
    run with it on keeps the post-loop rebuild -- `level_dd_schedule_from_the_loop` refuses it)."""

    def __init__(self, board, customer_of: Callable[[str], Optional[dict]]):
        self._board = board
        self._customer_of = customer_of
        # The leg's first supplied day, as `supply_starts` reads it post-run: its earliest bill's start.
        self._supply_start: dict[str, date] = {}
        self._opening: dict[str, Optional[float]] = {}
        # leg -> (anchor month, window index, standing amount)
        self._window: dict[str, tuple[str, int, float]] = {}
        self.collected: dict[str, list[dict]] = {}
        self.books_asked = 0

    def _opening_of(self, cid: str) -> Optional[float]:
        if cid not in self._opening:
            from simulation.run_phase4c_on_phase2b import _opening_dd_by_customer
            customer = self._customer_of(cid)
            rows = self._board.records_of(cid)
            first = min((r["settlement_date"][:7] for r in rows), default=None)
            self._opening[cid] = (None if customer is None or first is None else
                                  _opening_dd_by_customer(
                                      [customer], [r for r in rows
                                                   if r["settlement_date"][:7] == first]).get(cid))
        return self._opening[cid]

    def _ask_book(self, cid: str, month: str, left: bool) -> Optional[tuple[str, int, float]]:
        from simulation.dd_balance_book import build_dd_balance_book
        from simulation.dd_collection_book import supplier_dd_spells
        opening = self._opening_of(cid)
        if opening is None:
            return None
        y, m = int(month[:4]), int(month[5:7])
        cutoff = f"{y + m // 12:04d}-{m % 12 + 1:02d}-01"
        bills = self._board.bills_before(cid, cutoff, churned=left)
        spells = supplier_dd_spells(self._board.issued_bills_before(cid, cutoff, churned=left),
                                    self._board._behavioral(cid))
        self.books_asked += 1
        if bills and cid not in self._supply_start:
            from simulation.dd_level_collection_book import supply_starts
            self._supply_start.update(supply_starts([b for b in bills if b["customer_id"] == cid]))
        points = build_dd_balance_book(bills, {cid: opening}, dd_spells=spells).trajectories.get(cid)
        point = next((p for p in reversed(points or []) if p.month == month), None)
        if point is None:
            return None
        return points[0].month, _months_between(points[0].month, month) // 12, point.collected_gbp

    def collect(self, cid: str, month: str, left: bool = False) -> Optional[dict]:
        """`{month, scheduled_date, collection_date, amount_gbp}` for the leg's level collection
        paying for `month`, or None: no opening amount, or no DD bill for the month in the book."""
        from simulation.dd_level_collection_book import level_collection_dates
        from simulation.dd_payment_day import staggered_payment_day
        known = self._window.get(cid)
        if (known is None or left
                or _months_between(known[0], month) // 12 != known[1]):
            known = self._ask_book(cid, month, left)
            if known is None:
                return None
            self._window[cid] = known
        scheduled, collected = level_collection_dates(month, staggered_payment_day(cid),
                                                      self._supply_start.get(cid))
        row = {"month": month, "scheduled_date": scheduled.isoformat(),
               "collection_date": collected.isoformat(), "amount_gbp": known[2]}
        self.collected.setdefault(cid, []).append(row)
        return row


def level_dd_schedule_from_the_loop(in_loop: Mapping[str, list[dict]] | None,
                                    rebuilt: Mapping[str, list[dict]],
                                    offsets_dual_fuel_legs: bool) -> tuple[dict, dict]:
    """The level schedule phase 4c hands the page and the books, and how it compares with the
    post-loop rebuild: `(schedule, reconcile)`.

    The schedule is the loop's (`InLoopLevelCollection.collected`) for the households the world put
    on a level amount, which is what phase 2b collected. A run with no loop schedule, or with the
    dual-fuel offsets on (which the loop does not ask), keeps the rebuild, and says so."""
    def key_rows(schedule):
        return {(cid, r["month"]): r for cid, rows in schedule.items() for r in rows}

    if in_loop is None or offsets_dual_fuel_legs:
        return dict(rebuilt), {"source": "post_loop_rebuild",
                               "why": ("no loop schedule in the run" if in_loop is None else
                                       "dual-fuel offsets on: the loop does not ask them")}
    loop_rows, post_rows = key_rows(in_loop), key_rows(rebuilt)
    both = set(loop_rows) & set(post_rows)
    moved = [k for k in both
             if abs(loop_rows[k]["amount_gbp"] - post_rows[k]["amount_gbp"]) > 0.005
             or loop_rows[k]["collection_date"] != post_rows[k]["collection_date"]]
    return (dict(in_loop),
            {"source": "in_loop",
             "months_in_loop": len(loop_rows), "months_post_loop": len(post_rows),
             "matched": len(both) - len(moved), "differ": len(moved),
             "only_in_loop": len(set(loop_rows) - set(post_rows)),
             "only_post_loop": len(set(post_rows) - set(loop_rows)),
             "differ_sample": [{"customer_id": k[0], "month": k[1],
                                "in_loop_gbp": loop_rows[k]["amount_gbp"],
                                "post_loop_gbp": post_rows[k]["amount_gbp"]}
                               for k in sorted(moved)[:20]]})
