from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class CustomerCLVRecord:
    customer_id: str
    acquisition_year: int
    channel: str
    segment: str
    clv_gbp: float
    annual_margin_gbp: float
    tenure_years: float


@dataclass(frozen=True)
class CohortSummary:
    key: str
    customer_count: int
    avg_clv_gbp: float
    median_clv_gbp: float
    total_clv_gbp: float
    avg_annual_margin_gbp: float
    avg_tenure_years: float
    profitable_pct: float

    @property
    def is_profitable_cohort(self) -> bool:
        return self.avg_clv_gbp > 0


def _cohort_summary(key: str, records: List[CustomerCLVRecord]) -> CohortSummary:
    n = len(records)
    if n == 0:
        return CohortSummary(key=key, customer_count=0, avg_clv_gbp=0.0,
                             median_clv_gbp=0.0, total_clv_gbp=0.0,
                             avg_annual_margin_gbp=0.0, avg_tenure_years=0.0,
                             profitable_pct=0.0)
    clvs = sorted(r.clv_gbp for r in records)
    mid = n // 2
    median = (clvs[mid - 1] + clvs[mid]) / 2 if n % 2 == 0 else clvs[mid]
    profitable = sum(1 for r in records if r.clv_gbp > 0)
    return CohortSummary(
        key=key,
        customer_count=n,
        avg_clv_gbp=round(sum(clvs) / n, 2),
        median_clv_gbp=round(median, 2),
        total_clv_gbp=round(sum(clvs), 2),
        avg_annual_margin_gbp=round(sum(r.annual_margin_gbp for r in records) / n, 2),
        avg_tenure_years=round(sum(r.tenure_years for r in records) / n, 2),
        profitable_pct=round(profitable / n * 100, 1),
    )


class CLVCohortBook:
    def __init__(self) -> None:
        self._records: List[CustomerCLVRecord] = []

    def add(self, customer_id: str, acquisition_year: int, channel: str,
            segment: str, clv_gbp: float, annual_margin_gbp: float,
            tenure_years: float) -> CustomerCLVRecord:
        r = CustomerCLVRecord(
            customer_id=customer_id, acquisition_year=acquisition_year,
            channel=channel, segment=segment, clv_gbp=clv_gbp,
            annual_margin_gbp=annual_margin_gbp, tenure_years=tenure_years,
        )
        self._records.append(r)
        return r

    def by_acquisition_year(self, year: int) -> CohortSummary:
        recs = [r for r in self._records if r.acquisition_year == year]
        return _cohort_summary(str(year), recs)

    def by_channel(self, channel: str) -> CohortSummary:
        recs = [r for r in self._records if r.channel == channel]
        return _cohort_summary(channel, recs)

    def by_segment(self, segment: str) -> CohortSummary:
        recs = [r for r in self._records if r.segment == segment]
        return _cohort_summary(segment, recs)

    def all_cohorts_by_year(self) -> Dict[int, CohortSummary]:
        years = sorted(set(r.acquisition_year for r in self._records))
        return {y: self.by_acquisition_year(y) for y in years}

    def best_cohort_by_year(self) -> Optional[CohortSummary]:
        cohorts = list(self.all_cohorts_by_year().values())
        if not cohorts:
            return None
        return max(cohorts, key=lambda c: c.avg_clv_gbp)

    def worst_cohort_by_year(self) -> Optional[CohortSummary]:
        cohorts = list(self.all_cohorts_by_year().values())
        if not cohorts:
            return None
        return min(cohorts, key=lambda c: c.avg_clv_gbp)

    def portfolio_summary(self) -> dict:
        n = len(self._records)
        if n == 0:
            return {'total_customers': 0}
        total_clv = sum(r.clv_gbp for r in self._records)
        return {
            'total_customers': n,
            'total_clv_gbp': round(total_clv, 2),
            'avg_clv_gbp': round(total_clv / n, 2),
            'profitable_pct': round(sum(1 for r in self._records if r.clv_gbp > 0) / n * 100, 1),
        }
