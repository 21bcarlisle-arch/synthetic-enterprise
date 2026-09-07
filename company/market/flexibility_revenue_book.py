"""Flexibility Revenue Book -- Phase AF.

Realizes annual DSR and Capacity Market revenue from enrolling customers
with flexible assets (EV, ASHP, battery) in NESO Demand Flexibility
Service and the Capacity Market.

Epistemic: asset flags come from company CRM records (observable).
No simulation internals read.

CM: THE DOMESTIC CM LEG IS REFUSED, and this book's phasing changed with it. A household cannot
hold a Capacity Market agreement -- the minimum CMU is 1 MW against a whole flexible house of
3.0-15.4 kW -- so `flexibility_potential._estimate_capacity_revenue` returns `None` and this book
books nothing for it. The docstring here previously read "T-4 clearing ~75/kW/yr (2023)": the 75
was the T-1 clearing price for delivery year 2022/23, which cleared at the price cap, and it was
neither a T-4 nor 2023 nor anything a household could earn. See
`capacity_market_published_record`.
DFS: launched October 2022 by NESO. Event count and rate are published per winter and read
from `dfs_published_record` -- 22 events in 2022/23 (of which only 2 were called by system
conditions; the other 20 were calendar-scheduled tests) and 44 in 2024/25.

Phasing:
- 2016-2021: NO domestic flexibility revenue at all. This used to read "CM revenue only", and
  that whole leg was the refused one -- so every pre-DFS year in this book now books zero, which
  is the honest reading of a household that held no agreement in a market it could not enter.
- 2022+: DFS revenue only, per the published winter record.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict, List

from company.market import dfs_published_record
from company.market.flexibility_potential import (
    _estimate_capacity_revenue,
    _estimate_dfs_revenue,
    _estimate_flex_kw,
)

_DFS_LAUNCH_YEAR = dfs_published_record.FIRST_WINTER


@dataclass(frozen=True)
class FlexibilityRevenueRecord:
    """Realized flexibility revenue for one customer in one year."""

    customer_id: str
    year: int
    has_ev: bool
    has_ashp: bool
    has_battery: bool
    flex_kw: float
    capacity_market_revenue_gbp: float
    dfs_revenue_gbp: float
    total_revenue_gbp: float
    dfs_established: bool = True
    """False means the winter is not in the published record, so the DFS leg is 0.0 for want of
    evidence rather than because the service paid nothing. 2023/24 is the live case."""


class FlexibilityRevenueBook:
    """Realizes annual DSR/CM revenue from the portfolio.

    Usage::

        book = FlexibilityRevenueBook()
        by_cid = book.compute_year(2024, household_register, ["C1", "C2", "C3"])
        print(book.total_revenue_for_year(2024))
    """

    def __init__(self) -> None:
        self._records: List[FlexibilityRevenueRecord] = []

    def compute_year(
        self,
        year: int,
        household_register,
        customer_ids: List[str],
    ) -> Dict[str, float]:
        """Compute realized flexibility revenue for all customers in a given year.

        Returns cid->total_revenue_gbp for customers with flexible assets.
        DFS revenue only from 2022 onwards (DFS launch year).
        CM revenue from 2016 onwards (CM active since 2014).
        """
        year_end_str = str(dt.date(year, 12, 31))
        dfs_active = year >= _DFS_LAUNCH_YEAR
        revenue_by_cid: Dict[str, float] = {}

        for cid in customer_ids:
            assets = household_register.dynamic_assets(cid, year_end_str)
            has_ev = bool(assets.get("ev", False))
            has_ashp = bool(assets.get("ashp", False))
            has_battery = bool(assets.get("battery", False))

            if not (has_ev or has_ashp or has_battery):
                continue

            flex_kw = _estimate_flex_kw(has_ev, has_ashp, has_battery)
            # `None` is a refusal with a reason, not a missing measurement: a household holds no
            # CM agreement, so this zero is structural and established. It is a DIFFERENT zero
            # from the DFS one below, which means "the service ran and we cannot say what it
            # paid" -- the two flags on the record are what keep them apart.
            cm_raw = _estimate_capacity_revenue(flex_kw)
            cm_rev = 0.0 if cm_raw is None else round(cm_raw, 2)
            dfs_raw = _estimate_dfs_revenue(flex_kw, year) if dfs_active else 0.0
            # None means the winter ran and the published record does not establish what it paid.
            # Booked as 0.0 with the flag beside it, never silently as "the service paid nothing".
            dfs_rev = 0.0 if dfs_raw is None else round(dfs_raw, 2)
            total = round(cm_rev + dfs_rev, 2)

            self._records.append(
                FlexibilityRevenueRecord(
                    customer_id=cid,
                    year=year,
                    has_ev=has_ev,
                    has_ashp=has_ashp,
                    has_battery=has_battery,
                    flex_kw=flex_kw,
                    capacity_market_revenue_gbp=cm_rev,
                    dfs_revenue_gbp=dfs_rev,
                    total_revenue_gbp=total,
                    dfs_established=(dfs_raw is not None),
                )
            )
            revenue_by_cid[cid] = total

        return revenue_by_cid

    def records_for_year(self, year: int) -> List[FlexibilityRevenueRecord]:
        return [r for r in self._records if r.year == year]

    def total_revenue_for_year(self, year: int) -> float:
        return round(sum(r.total_revenue_gbp for r in self._records if r.year == year), 2)

    def total_cm_revenue(self) -> float:
        return round(sum(r.capacity_market_revenue_gbp for r in self._records), 2)

    def total_dfs_revenue(self) -> float:
        return round(sum(r.dfs_revenue_gbp for r in self._records), 2)

    def total_revenue_all_years(self) -> float:
        return round(sum(r.total_revenue_gbp for r in self._records), 2)

    def flexibility_summary(self) -> dict:
        years_with_revenue = sorted({r.year for r in self._records})
        per_year = {}
        for yr in years_with_revenue:
            yr_recs = self.records_for_year(yr)
            per_year[yr] = {
                "total_gbp": self.total_revenue_for_year(yr),
                "cm_gbp": round(sum(r.capacity_market_revenue_gbp for r in yr_recs), 2),
                "dfs_gbp": round(sum(r.dfs_revenue_gbp for r in yr_recs), 2),
                "enrolled_customers": len(yr_recs),
            }
        peak_yr_rev = max(
            (self.total_revenue_for_year(y) for y in years_with_revenue),
            default=0.0,
        )
        return {
            "total_flexibility_revenue_gbp": self.total_revenue_all_years(),
            "total_cm_revenue_gbp": self.total_cm_revenue(),
            "total_dfs_revenue_gbp": self.total_dfs_revenue(),
            "years_with_revenue": years_with_revenue,
            "peak_year_revenue_gbp": peak_yr_rev,
            "enrolled_customer_years": len(self._records),
            "per_year": per_year,
        }
