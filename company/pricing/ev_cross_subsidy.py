"""EV Customer Cross-Subsidy Register -- Phase U.

Identifies EV customers who generate significant margin cross-subsidy under
flat-rate tariffs (supplier buys cheap overnight wholesale, bills at flat rate).
Ranks them by cross-subsidy value for product strategy decisions.

Builds on Phase T (ToU Tariff Profitability Assessor). All inputs are
company-observable (billing history, CRM EV flag). Epistemic-compliant.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from company.pricing.tou_tariff_assessor import (
    DemandShapeClass,
    ToUTariffAssessorBook,
    WholesaleBandRates,
)


@dataclass(frozen=True)
class CrossSubsidyRecord:
    account_id: str
    year: int
    annual_kwh: float
    years_with_ev: int
    flat_margin_gbp: float
    tou_margin_gbp: float
    flat_rate_p_per_kwh: float

    @property
    def cross_subsidy_gbp(self) -> float:
        return round(self.flat_margin_gbp - self.tou_margin_gbp, 2)

    @property
    def is_at_risk(self) -> bool:
        return self.cross_subsidy_gbp > 0


class CrossSubsidyRegister:
    """Ranks EV customers by flat-tariff cross-subsidy value.

    Used to identify which EV customers the supplier should retain on
    flat tariff when ToU products are being marketed.
    """

    def __init__(self) -> None:
        self._records: list = []

    def record(
        self,
        account_id: str,
        year: int,
        annual_kwh: float,
        years_with_ev: int,
        flat_rate_p_per_kwh: float,
        wholesale_band_rates: WholesaleBandRates,
    ) -> CrossSubsidyRecord:
        """Compute and record cross-subsidy for one EV customer-year."""
        book = ToUTariffAssessorBook()
        cmp = book.assess(
            account_id=account_id,
            year=year,
            annual_kwh=annual_kwh,
            shape_class=DemandShapeClass.OVERNIGHT_HEAVY,
            flat_rate_p_per_kwh=flat_rate_p_per_kwh,
            wholesale_band_rates=wholesale_band_rates,
        )
        rec = CrossSubsidyRecord(
            account_id=account_id,
            year=year,
            annual_kwh=annual_kwh,
            years_with_ev=years_with_ev,
            flat_margin_gbp=cmp.flat_margin_gbp,
            tou_margin_gbp=cmp.tou_margin_gbp,
            flat_rate_p_per_kwh=flat_rate_p_per_kwh,
        )
        self._records.append(rec)
        return rec

    def records_for(self, account_id: str) -> list:
        return [r for r in self._records if r.account_id == account_id]

    def top_n_by_cross_subsidy(self, n: int, year: Optional[int] = None) -> list:
        records = self._for_year(year)
        return sorted(records, key=lambda r: r.cross_subsidy_gbp, reverse=True)[:n]

    def at_risk_if_tou_launched(
        self, threshold_gbp: float = 0.0, year: Optional[int] = None
    ) -> list:
        return [r for r in self._for_year(year) if r.cross_subsidy_gbp > threshold_gbp]

    def total_cross_subsidy_gbp(self, year: Optional[int] = None) -> float:
        return round(sum(r.cross_subsidy_gbp for r in self._for_year(year)), 2)

    def average_cross_subsidy_gbp(self, year: Optional[int] = None) -> float:
        records = self._for_year(year)
        if not records:
            return 0.0
        return round(self.total_cross_subsidy_gbp(year) / len(records), 2)

    def portfolio_summary(self, year: Optional[int] = None) -> dict:
        records = self._for_year(year)
        if not records:
            return {"ev_accounts": 0}
        top = self.top_n_by_cross_subsidy(1, year)
        return {
            "ev_accounts": len(records),
            "total_cross_subsidy_gbp": self.total_cross_subsidy_gbp(year),
            "average_cross_subsidy_gbp": self.average_cross_subsidy_gbp(year),
            "at_risk_count": len(self.at_risk_if_tou_launched(year=year)),
            "top_account_id": top[0].account_id if top else None,
        }

    def _for_year(self, year: Optional[int]) -> list:
        if year is None:
            return list(self._records)
        return [r for r in self._records if r.year == year]
