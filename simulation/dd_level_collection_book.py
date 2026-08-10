"""DD1 (atom ``DD_seasonal_cashflow_physics``) -- the LEVEL (fixed) direct-debit
collection made first-class: the standing monthly amount actually SIZES the
collection, landing on the customer's own staggered payment day.

The gap this closes. Two DD collection surfaces already existed, and NEITHER let
the standing monthly amount size a real collection record:

* ``simulation/dd_collection_book.py`` is VARIABLE DD: every ``DDPaymentAttempt``
  is sized by the raw bill (``total_amount_gbp``), and its own docstring says so
  explicitly -- the mandate's ``monthly_amount_gbp`` there is "an estimated
  reference level that never sizes or gates a collection". So under that book the
  household pays a different amount every month, tracking consumption.
* ``simulation/dd_balance_book.py`` (DD2) DOES compute the fixed standing level
  DD (``BalancePoint.collected_gbp``) -- but it consumes it only to carry a
  running credit/debit BALANCE. No collection RECORD is ever sized by it.

This module is the missing LEVEL-DD collection: under a level (fixed) DD -- the
UK domestic NORM -- the household pays the SAME fixed amount every month
regardless of that month's consumption, and that fixed amount is exactly the
standing level DD. Here that standing amount SIZES a first-class collection
record, and the collection lands on the customer's staggered payment day
(``staggered_payment_day`` / ``next_collection_on_day``, DD1's already-wired
day-of-month physics). Fixed and Variable DD coexist (the atom's own scope:
"payment-method first-class"); this is the Fixed-DD counterpart to
``dd_collection_book``'s Variable-DD raw-bill collections.

Consistency by construction, not by re-derivation. This function does NOT
recompute the standing level DD -- it READS ``DD2``'s already-built
``DDBalanceBook`` and sizes each collection from that month's
``BalancePoint.collected_gbp``. So the level-DD amount here is IDENTICALLY the
one DD2 carries and DD4a re-estimates -- the three artefacts cannot drift apart
because there is a single source of the number. (The alternative, copying the
year-on-year re-estimation chain into a third module, is exactly the silent
divergence the atom warns against.)

Safe-by-construction, mirroring ``dd_balance_book`` / ``dd_collection_book`` /
``dd_review_runner`` EXACTLY -- a new company-observable artefact where none
existed before, with NO existing number changed:

* It reads ONLY the DD2 balance book (itself built from company-observable bill
  fields) plus the pure per-customer ``staggered_payment_day`` digest. It mutates
  nothing, touches no ledger / treasury / cash-timing figure, and changes no
  published number.
* It draws NO RNG and is a pure, deterministic, idempotent function of the
  balance book (C-S2: replaying the same book reproduces an identical schedule).
  It is time-scale invariant (C-S5): it sizes one collection per billed period in
  issue order, not on any wall clock.
* The DD population and standing-DD chain are DD2's, so this stays mutually
  consistent with every DD2/DD3/DD4a/DD-H figure automatically.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

from simulation.dd_balance_book import DDBalanceBook
from simulation.dd_payment_day import staggered_payment_day

# How many per-customer collection schedules to carry on the serialised surface
# so a business page can render a REAL customer's fixed monthly collections (not
# a synthetic illustration). Deterministic pick: the first N ids, matching DD2.
_SAMPLE_SCHEDULE_CUSTOMERS = 6


def _window_index(month: str, anchor_month: str) -> int:
    """Whole 12-month window ``month`` falls in, counting from ``anchor_month``
    (both 'YYYY-MM'). Window 0 is the first billed year, 1 the second, etc."""
    ay, am = int(anchor_month[:4]), int(anchor_month[5:7])
    my, mm = int(month[:4]), int(month[5:7])
    return ((my - ay) * 12 + (mm - am)) // 12


@dataclass(frozen=True)
class LevelCollection:
    """One fixed level-DD collection: the standing amount sized it, not the
    month's bill."""

    collection_date: str   # 'YYYY-MM-DD' -- the staggered payment day in-month
    amount_gbp: float      # the FIXED standing level DD (== DD2's collected_gbp)
    payment_day: int       # the customer's staggered day-of-month (1-28)
    consumed_gbp: float    # that month's actual bill -- carried for contrast only


@dataclass
class DDLevelCollectionBook:
    """Per-customer fixed level-DD collection schedules + the portfolio totals
    they aggregate to."""

    # customer_id -> ordered list of LevelCollection
    schedules: dict = field(default_factory=dict)

    def _windows_fixed(self, cid: str) -> bool:
        """True iff, within every 12-month window, this customer's collections
        are all the SAME amount -- the defining property of a level DD (a
        bill-sized collection would vary month to month for a seasonal
        customer). The falsifiable DD1 invariant."""
        cols = self.schedules.get(cid, [])
        if not cols:
            return True
        anchor = cols[0].collection_date[:7]
        by_window: dict[int, set] = {}
        for c in cols:
            wi = _window_index(c.collection_date[:7], anchor)
            by_window.setdefault(wi, set()).add(round(c.amount_gbp, 2))
        return all(len(amounts) == 1 for amounts in by_window.values())

    def summary(self) -> dict:
        all_cols = [c for cols in self.schedules.values() for c in cols]
        if not all_cols:
            return {
                "n_customers": 0,
                "n_collections": 0,
                "total_level_collected_gbp": 0.0,
                "mean_monthly_level_dd_gbp": 0.0,
                "all_schedules_level_fixed": True,
            }
        total = sum(c.amount_gbp for c in all_cols)
        return {
            "n_customers": len(self.schedules),
            "n_collections": len(all_cols),
            "total_level_collected_gbp": round(total, 2),
            "mean_monthly_level_dd_gbp": round(total / len(all_cols), 2),
            # Every customer's collections are fixed within each year: the tell
            # that the standing amount -- not the bill -- sized every collection.
            "all_schedules_level_fixed": all(
                self._windows_fixed(cid) for cid in self.schedules
            ),
        }

    def serialise(self) -> dict:
        """JSON-safe form for the run-output surface (mirrors
        ``DDBalanceBook.serialise``): the summary plus a bounded set of real
        per-customer collection schedules a business page can render directly."""
        sample_ids = sorted(self.schedules)[:_SAMPLE_SCHEDULE_CUSTOMERS]
        return {
            "summary": self.summary(),
            "sample_schedules": {
                cid: [dataclasses.asdict(c) for c in self.schedules[cid]]
                for cid in sample_ids
            },
        }


def build_dd_level_collection_book(balance_book: DDBalanceBook) -> DDLevelCollectionBook:
    """Size a fixed level-DD collection for every billed month DD2 carries,
    landing it on the customer's staggered payment day.

    Pure, deterministic, idempotent: reads ``balance_book`` and the per-customer
    ``staggered_payment_day`` digest only, draws no RNG, mutates nothing. See the
    module docstring for the wall-clean basis and the by-construction consistency
    with ``dd_balance_book`` / ``dd_review_runner``.
    """
    book = DDLevelCollectionBook()
    for cid in sorted(balance_book.trajectories):
        points = balance_book.trajectories[cid]
        day = staggered_payment_day(cid)  # 1-28, deterministic per customer
        schedule: list[LevelCollection] = []
        for p in points:
            # p.month is 'YYYY-MM'; the staggered day (<=28) exists in every
            # month, so no short-month clamping is needed.
            schedule.append(LevelCollection(
                collection_date=f"{p.month}-{day:02d}",
                amount_gbp=p.collected_gbp,   # the FIXED standing level DD sizes it
                payment_day=day,
                consumed_gbp=p.consumed_gbp,
            ))
        book.schedules[cid] = schedule
    return book
