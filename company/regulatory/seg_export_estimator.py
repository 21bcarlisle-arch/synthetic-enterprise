"""SEG Export Estimator — Phase R.

Estimates solar electricity export for SEG-registered customers using
declared panel capacity and UK regional yield benchmarks.

The company observes solar capacity at SEG registration (MCS certificate
required — The Electricity Works (Miscellaneous Amendments) Regulations 2020).
Export is estimated from capacity × benchmark yield × export fraction; it is
true-up against smart export meter readings when available.

This matches real supplier practice: Octopus, Ovo, and British Gas all
estimate export for customers without smart export meters using MCS data
and SAP 10.2 yield tables, settling quarterly or annually.

Self-consumption fractions (BEIS 2022, UK Household Solar Report):
  - Standard (no battery): ~50% self-consumed, ~50% exported
  - With battery storage:  ~70% self-consumed, ~30% exported

SEG only applies from 2020-01-01 (The Smart Export Guarantee Order 2019).
Pre-2020 solar export was settled under FIT (fit_book.py, Phase 286).
"""
from __future__ import annotations

from dataclasses import dataclass

from company.regulatory.seg_book import SEGBook, SEGPayment

# UK average yield per kWp per year (SAP 10.2 / MCS performance data).
# Weighted average for England & Wales, accounting for inverter losses,
# shading, and degradation. South England ~950, North ~750; UK avg ~850.
# Source: BEIS Solar PV Deployment Statistics, SAP 10.2 Table H1.
ANNUAL_YIELD_KWH_PER_KWP: float = 850.0

# Self-consumption fraction — share of generation consumed on-site.
# Higher with battery storage (battery absorbs daytime surplus).
SELF_CONSUMPTION_STANDARD: float = 0.50  # no battery
SELF_CONSUMPTION_WITH_BATTERY: float = 0.70  # with home battery

# SEG active from 2020. Pre-2020 export settled under FIT.
SEG_START_YEAR: int = 2020


@dataclass(frozen=True)
class AnnualExportEstimate:
    customer_id: str
    year: int
    generation_kwh: float
    self_consumed_kwh: float
    exported_kwh: float
    seg_rate_p_per_kwh: float
    seg_payment_gbp: float


class SEGExportEstimator:
    """Estimates annual solar export and records SEG payments in a SEGBook.

    The estimator uses declared capacity (kWp from SEG contract) and the
    UK average yield benchmark to compute generation, then applies the
    standard self-consumption fraction to derive export.
    """

    def __init__(self, seg_book: SEGBook) -> None:
        self._seg_book = seg_book

    def annual_yield_kwh(self, capacity_kwp: float) -> float:
        """Gross annual generation estimate for a given system size."""
        return capacity_kwp * ANNUAL_YIELD_KWH_PER_KWP

    def self_consumption_fraction(self, has_battery: bool) -> float:
        return SELF_CONSUMPTION_WITH_BATTERY if has_battery else SELF_CONSUMPTION_STANDARD

    def export_fraction(self, has_battery: bool) -> float:
        return 1.0 - self.self_consumption_fraction(has_battery)

    def estimate_annual_export_kwh(
        self,
        capacity_kwp: float,
        has_battery: bool = False,
    ) -> float:
        """Estimate exported kWh for one year given panel capacity."""
        return self.annual_yield_kwh(capacity_kwp) * self.export_fraction(has_battery)

    def estimate_and_record(
        self,
        customer_id: str,
        capacity_kwp: float,
        year: int,
        has_battery: bool = False,
    ) -> AnnualExportEstimate:
        """Estimate export for a customer-year and record a SEGPayment.

        Returns the estimate. Raises ValueError if year < SEG_START_YEAR.
        """
        if year < SEG_START_YEAR:
            raise ValueError(
                f"SEG started {SEG_START_YEAR}; {year} export settled under FIT"
            )
        generation = self.annual_yield_kwh(capacity_kwp)
        sc_frac = self.self_consumption_fraction(has_battery)
        self_consumed = round(generation * sc_frac, 2)
        exported = round(generation * (1.0 - sc_frac), 2)
        rate = self._seg_book.seg_rate_for_year(year)
        payment_gbp = round(exported * rate / 100.0, 4)
        period_start = f"{year}-01-01"
        period_end = f"{year}-12-31"
        self._seg_book.record_payment(
            SEGPayment(
                customer_id=customer_id,
                period_start=period_start,
                period_end=period_end,
                export_kwh=exported,
                rate_p_per_kwh=rate,
            )
        )
        return AnnualExportEstimate(
            customer_id=customer_id,
            year=year,
            generation_kwh=round(generation, 2),
            self_consumed_kwh=self_consumed,
            exported_kwh=exported,
            seg_rate_p_per_kwh=rate,
            seg_payment_gbp=payment_gbp,
        )

    def portfolio_summary(self, estimates: list[AnnualExportEstimate]) -> dict:
        """Aggregate export and payment totals across all estimates."""
        if not estimates:
            return {
                "customer_count": 0,
                "total_generation_kwh": 0.0,
                "total_export_kwh": 0.0,
                "total_seg_cost_gbp": 0.0,
            }
        return {
            "customer_count": len({e.customer_id for e in estimates}),
            "total_generation_kwh": round(sum(e.generation_kwh for e in estimates), 2),
            "total_export_kwh": round(sum(e.exported_kwh for e in estimates), 2),
            "total_seg_cost_gbp": round(sum(e.seg_payment_gbp for e in estimates), 4),
        }
