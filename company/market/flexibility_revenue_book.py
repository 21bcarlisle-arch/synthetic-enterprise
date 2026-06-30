"""Flexibility Revenue Book -- Phase AF.

Realizes annual DSR and Capacity Market revenue from enrolling customers
with flexible assets (EV, ASHP, battery) in NESO Demand Flexibility
Service and the Capacity Market.

Epistemic: asset flags come from company CRM records (observable).
No simulation internals read.

CM: operational since 2014; T-4 clearing ~75/kW/yr (2023).
DFS: launched October 2022 by NESO; ~20 winter dispatch events/yr.

Phasing:
- 2016-2021: CM revenue only
- 2022+: CM + DFS revenue
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict, List

from company.market.flexibility_potential import (
    _estimate_capacity_revenue,
    _estimate_dfs_revenue,
    _estimate_flex_kw,
)

_DFS_LAUNCH_YEAR = 2022


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
            cm_rev = round(_estimate_capacity_revenue(flex_kw), 2)
            dfs_rev = round(_estimate_dfs_revenue(flex_kw), 2) if dfs_active else 0.0
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
