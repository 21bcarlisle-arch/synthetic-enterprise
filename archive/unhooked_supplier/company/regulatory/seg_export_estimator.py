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

# ONE NUMBER FOR THE WHOLE COUNTRY, AND WHAT IT COSTS. Until 2026-09-06 this constant was the
# estimator's entire geography: every household in the book, Penzance and Thurso alike, generated
# at the same rate. W1_25 measured the error that carries -- a 3.4% RMS in annual generation across
# the household-weighted population, which is the same order as the SEG rate spread the figure is
# used to value. The five bands below take it to 0.95%.
#
# Source: MCS-certified installations, 2025 fleet average, 882 kWh/kWp. That is the LEVEL anchor
# and it replaces 850, which cited "BEIS Solar PV Deployment Statistics, SAP 10.2 Table H1" for a
# figure neither of them states. Retained as the FALLBACK for a customer whose location is unknown,
# and `yield_kwh_per_kwp` says so by requiring the caller to pass None explicitly rather than
# defaulting into it.
ANNUAL_YIELD_KWH_PER_KWP: float = 882.0

# THE SHAPE IS DERIVED, THE LEVEL IS PUBLISHED, AND THE TWO ARE DIFFERENT KINDS OF THING.
#
# Shape: household-weighted clustering of Met Office HadUK-Grid annual sunshine duration over the
# 121,668 occupied 1 km cells (`tools/weather_cell_derivation.py`), converted to irradiation by the
# Angstrom-Prescott relation H/H0 = a + b(n/N) with Prescott's a=0.25, b=0.50 -- the method the UK's
# own gridded solar resource is built with. Level: scaled so the household-weighted mean is the MCS
# fleet average above.
#
# KEYED ON SUNSHINE HOURS, NOT ON LATITUDE, AND THAT IS A FINDING RATHER THAN A CONVENIENCE. The
# five bands overlap almost completely in latitude -- the sunniest spans 49.9-54.1 N and the dullest
# 50.6-60.8 N -- because Britain's sunshine is coastal and eastern as much as it is southern. A
# latitude lookup would look reasonable and be wrong for most of the country. The company can read
# a cell's annual sunshine from the published Met Office grid for any postcode, so this asks for the
# quantity that actually governs.
#
# THE PUBLISHED 750-1050 kWh/kWp RANGE IS NOT A CHECK ON THIS TABLE. That range is quoted for
# optimally tilted south-facing installations at the extremes; the MCS fleet average is over all
# orientations and tilts. Two different populations, so the derived 835-947 spread being narrower
# says nothing about either. Stated because the comparison is the obvious one to make and it does
# not hold.
SOLAR_BAND_CUTS_SUNSHINE_HOURS: tuple[float, ...] = (1400.6, 1512.6, 1603.2, 1727.2)
SOLAR_BAND_YIELD_KWH_PER_KWP: tuple[float, ...] = (834.8, 865.8, 887.9, 908.7, 946.6)
#: Share of GB households in each band, for anyone weighing whether a band is worth carrying.
SOLAR_BAND_HOUSEHOLD_SHARE: tuple[float, ...] = (0.162, 0.247, 0.298, 0.239, 0.054)


def yield_kwh_per_kwp(annual_sunshine_hours: float | None) -> float:
    """Annual yield per kWp for a location, from its published annual sunshine duration.

    `None` means the location is unknown and returns the national fleet average. It is REQUIRED
    rather than defaulted so that using the national figure is a decision a caller makes, not one
    it falls into -- the whole defect this table exists to close was a national figure nobody had
    to ask for.
    """
    if annual_sunshine_hours is None:
        return ANNUAL_YIELD_KWH_PER_KWP
    if annual_sunshine_hours <= 0.0:
        raise ValueError(f"annual sunshine duration must be positive, got {annual_sunshine_hours}")
    band = 0
    for cut in SOLAR_BAND_CUTS_SUNSHINE_HOURS:
        if annual_sunshine_hours < cut:
            break
        band += 1
    return SOLAR_BAND_YIELD_KWH_PER_KWP[band]

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

    def annual_yield_kwh(self, capacity_kwp: float,
                         annual_sunshine_hours: float | None = None) -> float:
        """Gross annual generation estimate for a given system size and location.

        `annual_sunshine_hours` defaults to None -- the national fleet average -- so every existing
        caller keeps working. That default is the one concession to compatibility here, and it is
        why `yield_kwh_per_kwp` refuses to hide the same choice: a caller that passes nothing gets
        the national figure and a 3.4% RMS error, exactly as it did before.
        """
        return capacity_kwp * yield_kwh_per_kwp(annual_sunshine_hours)

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
