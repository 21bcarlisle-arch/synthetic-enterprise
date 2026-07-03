"""I&C Demand Response Enrollment -- Phase NX.

Large I&C customers can sell interruptible load capacity into the UK Capacity
Market (CM) and NESO Demand Flexibility Service (DFS). Unlike residential
customers (who need EV/ASHP/battery), I&C participants sell process
flexibility (chillers, compressors, HVAC curtailment, interruptible loads).

Eligibility: I&C customers with EAC >= _IC_MIN_EAC_KWH participate via DSR
aggregators who pool sub-2 MW loads into CM-eligible units. Aggregators charge
a commission (_AGGREGATOR_FEE_PCT) on CM/DFS revenue.

CM clearing prices are from published T-4/T-3 auction results (NESO).
DFS: launched Oct 2022; payments ~£4.5/MWh for demand reduction events.

Epistemic: company observes I&C EAC from billing records. No SIM internals read.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

_IC_LOAD_FACTOR = 0.65           # typical industrial load factor (UK)
_IC_DSR_FRACTION = 0.10          # 10% of peak demand enrolled in DSR/CM
_AGGREGATOR_FEE_PCT = 0.20       # aggregator fee on gross CM/DFS revenue
_IC_MIN_EAC_KWH = 200_000        # minimum 200 MWh/yr for DSR aggregator eligibility

_DFS_LAUNCH_YEAR = 2022
_DFS_RATE_GBP_PER_MWH = 4.5     # NESO DFS average rate 2022-24
_DFS_EVENTS_PER_YR = 20          # ~20 winter dispatch events
_DFS_DURATION_HRS = 1.0          # 1-hour events

# T-4/T-3 CM delivery year clearing prices (£/kW/yr) by calendar year of Oct delivery start.
# Source: NESO auction results + capacity_market_levy_2016_2024.md.
_CM_DELIVERY_GBP_PER_KW_YR: Dict[int, float] = {
    2016: 15.0,
    2017: 10.0,
    2018: 19.40,
    2019: 18.00,
    2020: 22.50,
    2021: 8.40,
    2022: 6.44,
    2023: 15.97,
    2024: 18.00,
    2025: 18.00,
}


@dataclass(frozen=True)
class ICFlexibilityRecord:
    """Realized CM/DFS revenue for one I&C customer in one year."""

    customer_id: str
    year: int
    eac_kwh: float
    peak_demand_kw: float
    flex_kw: float
    cm_price_gbp_per_kw: float
    gross_cm_revenue_gbp: float
    gross_dfs_revenue_gbp: float
    aggregator_fee_gbp: float
    net_revenue_gbp: float


def _peak_demand_kw(eac_kwh: float) -> float:
    """Estimate peak demand from annual consumption."""
    return eac_kwh / (8760.0 * _IC_LOAD_FACTOR)


def _flex_kw(peak_kw: float) -> float:
    return round(peak_kw * _IC_DSR_FRACTION, 2)


def _gross_cm_revenue(flex_kw: float, year: int) -> float:
    price = _CM_DELIVERY_GBP_PER_KW_YR.get(year, _CM_DELIVERY_GBP_PER_KW_YR[2025])
    return round(flex_kw * price, 2)


def _gross_dfs_revenue(flex_kw: float, year: int) -> float:
    if year < _DFS_LAUNCH_YEAR:
        return 0.0
    # flex_kw * duration_hrs / 1000 = MWh per event; multiply by rate and events
    flex_mw = flex_kw / 1000.0
    return round(flex_mw * _DFS_DURATION_HRS * _DFS_RATE_GBP_PER_MWH * _DFS_EVENTS_PER_YR, 2)


class ICFlexibilityRevenueBook:
    """Computes realized CM/DFS revenue for enrolled I&C customers.

    Usage::

        book = ICFlexibilityRevenueBook()
        book.compute_year(2023, [("C_IC1", 1_998_631), ("C_IC3", 4_007_250)])
        print(book.total_revenue_all_years())
    """

    def __init__(self) -> None:
        self._records: List[ICFlexibilityRecord] = []

    def compute_year(
        self,
        year: int,
        ic_customers: List[tuple],  # list of (customer_id, eac_kwh)
    ) -> Dict[str, float]:
        """Compute net IC flexibility revenue for all eligible customers in one year."""
        revenue_by_cid: Dict[str, float] = {}

        for cid, eac_kwh in ic_customers:
            if eac_kwh < _IC_MIN_EAC_KWH:
                continue

            peak_kw = _peak_demand_kw(eac_kwh)
            fkw = _flex_kw(peak_kw)
            cm_price = _CM_DELIVERY_GBP_PER_KW_YR.get(year, _CM_DELIVERY_GBP_PER_KW_YR[2025])
            gross_cm = _gross_cm_revenue(fkw, year)
            gross_dfs = _gross_dfs_revenue(fkw, year)
            agg_fee = round((gross_cm + gross_dfs) * _AGGREGATOR_FEE_PCT, 2)
            net = round(gross_cm + gross_dfs - agg_fee, 2)

            record = ICFlexibilityRecord(
                customer_id=cid,
                year=year,
                eac_kwh=eac_kwh,
                peak_demand_kw=round(peak_kw, 2),
                flex_kw=fkw,
                cm_price_gbp_per_kw=cm_price,
                gross_cm_revenue_gbp=gross_cm,
                gross_dfs_revenue_gbp=gross_dfs,
                aggregator_fee_gbp=agg_fee,
                net_revenue_gbp=net,
            )
            self._records.append(record)
            revenue_by_cid[cid] = net

        return revenue_by_cid

    def records_for_year(self, year: int) -> List[ICFlexibilityRecord]:
        return [r for r in self._records if r.year == year]

    def total_revenue_for_year(self, year: int) -> float:
        return round(sum(r.net_revenue_gbp for r in self._records if r.year == year), 2)

    def total_revenue_all_years(self) -> float:
        return round(sum(r.net_revenue_gbp for r in self._records), 2)

    def flexibility_summary(self) -> dict:
        years_with_revenue = sorted({r.year for r in self._records})
        per_year = {}
        for yr in years_with_revenue:
            yr_recs = self.records_for_year(yr)
            per_year[yr] = {
                "total_net_gbp": self.total_revenue_for_year(yr),
                "enrolled_customers": len(yr_recs),
                "total_flex_kw": round(sum(r.flex_kw for r in yr_recs), 2),
            }
        return {
            "total_ic_flex_revenue_gbp": self.total_revenue_all_years(),
            "enrolled_customer_years": len(self._records),
            "years_with_revenue": years_with_revenue,
            "per_year": per_year,
        }
