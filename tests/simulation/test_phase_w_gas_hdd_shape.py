"""Tests for Phase W: Gas Boiler Daily HDD Shape.

Resi/SME gas now uses a daily HDD-weighted consumption shape:
  70% space heating (scales with daily HDD / annual reference HDD)
  30% DHW + cooking (flat year-round)
This mirrors Phase I for ASHP electricity and replaces the monthly-profile
x term-level weather_factor approach for residential and SME gas customers.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from sim.weather_hdd import REFERENCE_MONTHLY_HDD
from simulation.gas_settlement import (
    _GAS_BOILER_HEATING_FRACTION,
    _HDD_REF_ANNUAL,
    GAS_IC_CONSUMPTION_MONTHLY_PROFILE,
    run_gas_term,
)


def _fake_gas_records(start: str, end: str, price: float = 30.0) -> list[dict]:
    records = []
    d = date.fromisoformat(start)
    e = date.fromisoformat(end)
    while d <= e:
        records.append({"settlementDate": d.isoformat(), "systemSellPrice": price})
        d += timedelta(days=1)
    return records


def _run_one_month(month_start: str, aq: int = 12000, segment: str = "resi") -> list[dict]:
    d = date.fromisoformat(month_start)
    next_month = date(d.year + (d.month // 12), (d.month % 12) + 1, 1)
    gas_records = _fake_gas_records("2015-12-01", next_month.isoformat())
    return run_gas_term(
        "NO_WEATHER_FILE_CID",  # no weather CSV -> reference HDD fallback
        month_start,
        next_month.isoformat(),
        aq_kwh=aq,
        unit_rate_gbp_mwh=30.0,
        hedge_fraction=0.0,
        forward_price=30.0,
        monthly_cost_of_capital_gbp=1.0,
        gas_price_records=gas_records,
        segment=segment,
    )


class TestHDDConstants:
    def test_heating_fraction_calibrated(self):
        assert 0.82 <= _GAS_BOILER_HEATING_FRACTION <= 0.87  # DESNZ ET 4.1/4.2 fit, 2016-25

    def test_hdd_ref_annual_positive(self):
        assert _HDD_REF_ANNUAL > 1000

    def test_hdd_ref_annual_matches_sum(self):
        assert abs(_HDD_REF_ANNUAL - sum(REFERENCE_MONTHLY_HDD.values())) < 0.01


class TestResiGasHDDShape:
    def test_january_higher_than_july_reference_hdd(self):
        jan = _run_one_month("2020-01-01")
        jul = _run_one_month("2020-07-01")
        jan_avg = sum(r["daily_kwh"] for r in jan) / len(jan) if jan else 0
        jul_avg = sum(r["daily_kwh"] for r in jul) / len(jul) if jul else 0
        assert jan_avg > jul_avg, "January average should exceed July for resi gas"

    def test_jan_jul_ratio_realistic(self):
        jan = _run_one_month("2020-01-01")
        jul = _run_one_month("2020-07-01")
        jan_avg = sum(r["daily_kwh"] for r in jan) / len(jan)
        jul_avg = sum(r["daily_kwh"] for r in jul) / len(jul)
        ratio = jan_avg / jul_avg
        assert 3.0 < ratio < 10.0, f"Jan:Jul ratio {ratio:.2f}x should be 3-10x for UK resi"

    def test_dhw_floor_summer(self):
        # July consumption should be near-flat (mostly DHW; space heating ~0)
        # DHW floor = AQ * (1 - FRAC) / 365
        jul = _run_one_month("2020-07-01", aq=12000)
        if not jul:
            return
        dhw_floor = 12000 * (1.0 - _GAS_BOILER_HEATING_FRACTION) / 365.0
        # July average daily should be close to DHW floor (small space heating residual)
        jul_avg = sum(r["daily_kwh"] for r in jul) / len(jul)
        assert jul_avg >= dhw_floor * 0.9, "July must include DHW floor component"
        assert jul_avg < dhw_floor * 3.0, "July should not be much above DHW floor"

    def test_annual_total_conserved_reference_hdd(self):
        # With no actual weather data (reference HDD), annual total should equal AQ within 2%.
        aq = 12000
        gas_records = _fake_gas_records("2019-12-01", "2021-01-02")
        records = run_gas_term(
            "NO_WEATHER_FILE_CID", "2020-01-01", "2021-01-01",
            aq_kwh=aq, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
        )
        total = sum(r["daily_kwh"] for r in records)
        assert abs(total - aq) / aq < 0.02, f"Annual total {total:.0f} should be ~{aq}"

    def test_weather_factor_ignored_for_resi(self):
        # weather_factor=0.5 vs 1.0 should produce identical output for resi
        gas_records = _fake_gas_records("2019-12-01", "2020-02-01")
        r1 = run_gas_term(
            "NO_WEATHER_FILE_CID", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
            weather_factor=0.5,
        )
        r2 = run_gas_term(
            "NO_WEATHER_FILE_CID", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
            weather_factor=1.0,
        )
        if r1 and r2:
            assert abs(r1[0]["daily_kwh"] - r2[0]["daily_kwh"]) < 0.0001, (
                "weather_factor must not affect resi/SME gas in Phase W"
            )

    def test_seasonal_factor_in_record(self):
        jan = _run_one_month("2020-01-01")
        for rec in jan:
            assert "seasonal_factor" in rec
            assert rec["seasonal_factor"] > 0

    def test_seasonal_factor_january_above_one(self):
        jan = _run_one_month("2020-01-01")
        if jan:
            assert jan[0]["seasonal_factor"] > 1.0, "January seasonal_factor > 1 (winter peak)"

    def test_seasonal_factor_july_below_one(self):
        jul = _run_one_month("2020-07-01")
        if jul:
            assert jul[0]["seasonal_factor"] < 1.0, "July seasonal_factor < 1 (summer trough)"


class TestICGasUnchanged:
    def test_ic_gas_uses_monthly_profile_not_hdd(self):
        jan = _run_one_month("2020-01-01", segment="I&C")
        if not jan:
            return
        # I&C uses GAS_IC_CONSUMPTION_MONTHLY_PROFILE; seasonal_factor should match
        expected_factor = GAS_IC_CONSUMPTION_MONTHLY_PROFILE[1]
        assert abs(jan[0]["seasonal_factor"] - expected_factor) < 0.001

    def test_ic_gas_weather_factor_still_applies(self):
        gas_records = _fake_gas_records("2019-12-01", "2020-02-01")
        r_wf = run_gas_term(
            "NO_WEATHER_FILE_CID", "2020-01-01", "2020-02-01",
            aq_kwh=5_000_000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
            segment="I&C",
            weather_factor=0.8,
        )
        r_normal = run_gas_term(
            "NO_WEATHER_FILE_CID", "2020-01-01", "2020-02-01",
            aq_kwh=5_000_000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
            segment="I&C",
            weather_factor=1.0,
        )
        if r_wf and r_normal:
            assert r_wf[0]["daily_kwh"] < r_normal[0]["daily_kwh"], (
                "I&C weather_factor=0.8 should reduce consumption vs 1.0"
            )


def test_the_fraction_and_the_reference_year_reproduce_the_published_normal_gas_year():
    """Defect caught: the heating fraction moved without REFERENCE_MONTHLY_HDD (or the reverse).

    The two calibrate as a pair: 0.85 on the pre-2026-11-20 table gave Jan:Jul 10.6, and 0.70 on the
    re-based table gives 4.3. DESNZ ET 4.1/4.2 domestic, normalised to 1991-2020 weather, gives 7.15-7.47
    over 2023-25 (docs/market_research/the_domestic_gas_year_heats_on_about_85_percent_not_70_2026-11-19.md s.5).
    """
    import calendar

    f = _GAS_BOILER_HEATING_FRACTION
    annual = sum(REFERENCE_MONTHLY_HDD.values())

    def month_share(m: int) -> float:
        days = 28.25 if m == 2 else calendar.monthrange(2019, m)[1]
        return f * REFERENCE_MONTHLY_HDD[m] / annual + (1.0 - f) * days / 365.25

    assert 7.15 <= month_share(1) / month_share(7) <= 7.47
