"""Running answers to the questions the term loop asks of the settled book.

WHY THIS EXISTS — MEASURED, 2026-08-24, director's question "what actually holds 9-12GB during
a run, and does that footprint scale with accounts, with years, or both?"

`simulation/run_phase2b.py` accumulates every settlement record of the whole run in one list,
`all_records` — one dict per customer per day per settlement period, 17,520 per customer-year.
Measured at 1,202 bytes retained per record (deep walk and `tracemalloc` agree to 0.6%), which
is ~1,410 with the four keys the run adds after settlement. So:

    peak footprint ≈ customer-years × 17,520 × 1.4 kB

and the axis is neither accounts nor years but their PRODUCT — a customer-year costs the same
24 MB whichever way you get there. At the engine's 600-customer-year ceiling that is ~15 GB,
which is the 14.2 GB the OOM killer took fourteen times on 2026-08-24. At the director's target
of 200 residential accounts over the ten-year window it is **~49 GB**, more than the host has:
not a budget question, and not one more RAM can answer.

THE SECOND COST, AND THE ONE THAT GREW FASTEST. Two helpers filtered that whole list by
`customer_id` from INSIDE the term loop — `_company_eac_estimate` and
`_derive_eac_from_settlement`. Measured over two horizons:

    end-2017   30.2 customer-years    23.0s    3.0s in scans (13%)     56M records visited
    end-2019  109.0 customer-years   134.1s   41.9s in scans (31%)    870M records visited

Fitting those: scan time scales as customer-years^**2.05** while the rest of the run scales as
^1.19 and peak RSS as ^0.87. The scans are the only quadratic term in the run, and the engine's
ceiling is set from wall clock, so they are a large part of what that ceiling is protecting.

WHAT THIS IS
------------
A FOLD, not a store. Every consumer of `all_records` this project has — 26 read sites across
`run_phase2b`, the annual report, the segment report and five company doors — is a single pass
that accumulates. Not one needs random access to a row. So the records do not need keeping at
all: what the callers actually want is a handful of running totals, and those are about 200 kB.

That is why this is not backed by `docs/observability/projections.sqlite`, which was the obvious
candidate. That store is deliberately built from COMMITTED truth via `git cat-file blob HEAD:`,
rebuilt from scratch each time, and its own charter says it is never a source of truth and never
feeds a published figure. Writing a run's working state into it would break all three properties
to solve a problem that turns out not to need a store.

EXACTNESS IS THE WHOLE CONTRACT. This must answer what a scan of the list would have answered,
to the byte, or it is a behaviour change wearing a performance fix. Two rules make that
checkable rather than hoped for:

  * FED AT ONE PLACE ONLY — the same line that extends the list. `_company_eac_estimate` is
    called from inside the settlement loop, where the CURRENT term's records are not yet in the
    list; a fold fed any earlier would see records the list did not and would quietly widen the
    point-in-time window the blindfold depends on.
  * SAME PREDICATES — a record with `consumption_kwh is None` is skipped here exactly as the
    list comprehensions skip it, and the date window is half-open `[start, end)` exactly as
    `_company_eac_estimate`'s is.

`tests/simulation/test_settlement_fold.py` asserts the equality directly, by running both
implementations over the same records.
"""
from __future__ import annotations

from datetime import date


class SettlementFold:
    """Per-customer running totals over the settled book, in place of keeping the book."""

    def __init__(self) -> None:
        # cid -> {iso date: kwh}. Day granularity, not month, because the window
        # `_company_eac_estimate` asks for ends on an arbitrary term-start date and a monthly
        # bucket would have to guess how much of the boundary month falls inside it. A decade
        # of dates for a book of 200 is ~730k floats — still nothing beside 49 GB.
        self._kwh_by_date: dict[str, dict[str, float]] = {}
        self._kwh_total: dict[str, float] = {}
        self._first_date: dict[str, str] = {}
        self._last_date: dict[str, str] = {}
        self._records = 0

    # ── feeding ──────────────────────────────────────────────────────────────────────────

    def add(self, records) -> None:
        """Consume one term's settled records. Call this where the list is extended, and
        NOWHERE else — see EXACTNESS above."""
        for rec in records:
            kwh = rec.get("consumption_kwh")
            if kwh is None:
                # Matches the list comprehensions this replaces, which both filter
                # `consumption_kwh is not None`. A period with no consumption figure is not a
                # period of zero consumption, and counting it as one would drag every mean down.
                continue
            cid = rec.get("customer_id")
            day = rec.get("settlement_date")
            if cid is None or not day:
                continue
            self._records += 1
            by_date = self._kwh_by_date.setdefault(cid, {})
            by_date[day] = by_date.get(day, 0.0) + kwh
            self._kwh_total[cid] = self._kwh_total.get(cid, 0.0) + kwh
            first = self._first_date.get(cid)
            if first is None or day < first:
                self._first_date[cid] = day
            last = self._last_date.get(cid)
            if last is None or day > last:
                self._last_date[cid] = day

    # ── the two questions the term loop asks ────────────────────────────────────────────

    def consumption_kwh_between(self, cid: str, start_iso: str, end_iso: str) -> float:
        """Σ kWh for `cid` over the half-open window [start_iso, end_iso).

        ISO dates compare lexicographically in calendar order, so this needs no parsing. It
        walks the customer's own days rather than the whole book: ~3,650 string compares in
        place of a scan of every record every other customer ever settled.
        """
        by_date = self._kwh_by_date.get(cid)
        if not by_date:
            return 0.0
        return sum(v for d, v in by_date.items() if start_iso <= d < end_iso)

    def total_consumption_kwh(self, cid: str) -> float:
        return self._kwh_total.get(cid, 0.0)

    def span_days(self, cid: str) -> int:
        """Days from this customer's first settled day to its last, inclusive — 0 if none.

        Inclusive because the function this replaces computes `(max - min).days + 1`, and an
        off-by-one here moves a published annualised consumption figure.
        """
        first, last = self._first_date.get(cid), self._last_date.get(cid)
        if not first or not last:
            return 0
        return (date.fromisoformat(last) - date.fromisoformat(first)).days + 1

    def has_records(self, cid: str) -> bool:
        return cid in self._kwh_total

    @property
    def record_count(self) -> int:
        return self._records
