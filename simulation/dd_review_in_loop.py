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
(`docs/staging/SEAT_FINDING_THE_IN_LOOP_DD_REVIEW_IS_TOLD_TRUE_CONSUMPTION_NOT_THE_SUPPLIERS_
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
"""
from __future__ import annotations

from datetime import date
from typing import Callable, Optional


def _month_end(month: str) -> str:
    year, mon = (int(p) for p in month.split("-"))
    nxt = date(year + (mon == 12), mon % 12 + 1, 1)
    return date.fromordinal(nxt.toordinal() - 1).isoformat()


def _months_between(a: str, b: str) -> int:
    return (int(b[:4]) - int(a[:4])) * 12 + (int(b[5:7]) - int(a[5:7]))


class InLoopDDReview:
    """Per leg: the settled rows observed so far and its first settled month's rows. `post` returns
    the review event told THIS month (the company's serialised event), or None."""

    def __init__(self, customer_of: Callable[[str], Optional[dict]]):
        self._customer_of = customer_of
        self._rows: dict[str, list[dict]] = {}
        self._first_month_rows: dict[str, list[dict]] = {}
        self._first_month: dict[str, str] = {}
        self._last_window: dict[str, int] = {}
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
        opening = self._opening_of(cid)
        if opening is None:
            return None
        from simulation.run_phase4c_on_phase2b import build_monthly_bills
        bills = build_monthly_bills(self._rows.get(cid, []))
        from company.interfaces.dd_review import annual_dd_review_view
        period_end = _month_end(month)
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
