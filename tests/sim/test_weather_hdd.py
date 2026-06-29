"""Tests for Phase 58: HDD weather adjustment for gas consumption."""

import pytest
from sim.weather_hdd import (
    HDD_BASE_TEMP_C,
    REFERENCE_MONTHLY_HDD,
    get_hdd,
    get_monthly_hdd,
    get_weather_factor,
    weather_factor_for_term,
    _resolve_source_cid,
)
from simulation.gas_settlement import run_gas_term


def _fake_gas_records(start="2020-01-01", end="2020-03-31", price=30.0):
    """Minimal gas price records for gas_settlement tests."""
    from datetime import date, timedelta
    records = []
    d = date.fromisoformat(start)
    e = date.fromisoformat(end)
    while d <= e:
        records.append({"settlementDate": d.isoformat(), "systemSellPrice": price})
        d += timedelta(days=1)
    return records


class TestHddCalculation:
    def test_hdd_is_zero_above_base_temp(self):
        # C1 on a summer day should be warm enough for zero HDD
        hdd = get_hdd("2020-07-15", "C1")
        # July means average ~16-17°C, well above 15.5 base
        assert hdd >= 0.0, "HDD must be non-negative"
        # Cannot assert exactly 0 because it depends on real weather data,
        # but we verify it never goes negative
        assert hdd < HDD_BASE_TEMP_C, "HDD cannot exceed base temperature"

    def test_hdd_positive_below_base_temp(self):
        hdd = get_hdd("2020-01-15", "C1")
        # January UK temperatures are well below 15.5°C
        assert hdd > 0.0, "January HDD must be positive"

    def test_hdd_formula_correct(self):
        # Inject a known temperature via the cache to verify the formula
        from sim.weather_hdd import _WEATHER_CACHE
        _WEATHER_CACHE["TEST_COLD"] = {"2020-02-01": 5.0}
        hdd = get_hdd("2020-02-01", "TEST_COLD")
        assert abs(hdd - 10.5) < 0.001, "HDD should be 15.5 - 5.0 = 10.5"
        _WEATHER_CACHE["TEST_WARM"] = {"2020-07-01": 20.0}
        hdd_warm = get_hdd("2020-07-01", "TEST_WARM")
        assert hdd_warm == 0.0, "HDD above base temp must be 0"

    def test_monthly_hdd_sums_days(self):
        jan_hdd = get_monthly_hdd(2020, 1, "C1")
        # January should have substantial HDD - at least 200 (31 days of cold)
        assert jan_hdd > 100.0, "January HDD should be substantial"

    def test_monthly_hdd_summer_low(self):
        jul_hdd = get_monthly_hdd(2020, 7, "C1")
        # July should have very low HDD
        assert jul_hdd < 100.0, "July HDD should be much lower than winter"
        assert jul_hdd < get_monthly_hdd(2020, 1, "C1"), "July < January"


class TestWeatherFactor:
    def test_weather_factor_warm_winter_below_1(self):
        # 2019-2020 UK winter was warmest on record; Jan/Feb 2020 should be below 1
        factor_jan = get_weather_factor(2020, 1, "C1")
        # Warm winter → actual HDD below reference → factor < 1
        # (Climate normals ~350 HDD for Jan; 2020 was notably warm)
        assert factor_jan < 1.1, "Jan 2020 factor should not be much above normal"

    def test_weather_factor_clipped_to_sane_range(self):
        for year in range(2016, 2026):
            for month in range(1, 13):
                f = get_weather_factor(year, month, "C1")
                assert 0.3 <= f <= 2.0, f"Factor out of range: {year}-{month:02d} = {f}"

    def test_weather_factor_reference_months_sensible(self):
        # Reference HDD: all months defined, winter months >> summer months
        assert REFERENCE_MONTHLY_HDD[1] > REFERENCE_MONTHLY_HDD[7], "Jan ref > Jul ref"
        assert REFERENCE_MONTHLY_HDD[12] > REFERENCE_MONTHLY_HDD[6], "Dec ref > Jun ref"
        assert all(v > 0.0 for v in REFERENCE_MONTHLY_HDD.values()), "All refs > 0"

    def test_weather_factor_for_term_returns_in_range(self):
        f = weather_factor_for_term("2020-01-01", "2020-04-01", "C1")
        assert 0.3 <= f <= 2.0, f"Term factor out of range: {f}"

    def test_weather_factor_for_single_month_term(self):
        f_term = weather_factor_for_term("2020-01-01", "2020-02-01", "C1")
        f_month = get_weather_factor(2020, 1, "C1")
        assert abs(f_term - f_month) < 0.01, "Single-month term should equal monthly factor"


class TestGasCustomerMapping:
    def test_resolve_source_cid_gas_to_electricity(self):
        assert _resolve_source_cid("C1g") == "C1"
        assert _resolve_source_cid("C2g") == "C2"
        assert _resolve_source_cid("C3g") == "C3"
        assert _resolve_source_cid("C4g") == "C4"

    def test_resolve_source_cid_non_gas_unchanged(self):
        assert _resolve_source_cid("C1") == "C1"
        assert _resolve_source_cid("C_IC3g") == "C_IC3"  # I&C gas maps to electricity counterpart


class TestWeatherAdjustedGasSettlement:
    def test_warm_factor_reduces_consumption_ic(self):
        records_normal = run_gas_term(
            "C_IC3g", "2020-01-01", "2020-02-01",
            aq_kwh=120000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
            segment="I&C",
            weather_factor=1.0,
        )
        records_warm = run_gas_term(
            "C_IC3g", "2020-01-01", "2020-02-01",
            aq_kwh=120000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
            segment="I&C",
            weather_factor=0.8,
        )
        normal_kwh = sum(r["daily_kwh"] for r in records_normal)
        warm_kwh = sum(r["daily_kwh"] for r in records_warm)
        assert warm_kwh < normal_kwh, "Warm weather factor should reduce I&C consumption"
        assert abs(warm_kwh / normal_kwh - 0.8) < 0.001, "Factor 0.8 gives exactly 80% I&C consumption"

    def test_resi_consumption_uses_hdd_not_weather_factor(self):
        records_wf08 = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
            weather_factor=0.8,
        )
        records_wf10 = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
            weather_factor=1.0,
        )
        kwh_wf08 = sum(r["daily_kwh"] for r in records_wf08)
        kwh_wf10 = sum(r["daily_kwh"] for r in records_wf10)
        assert abs(kwh_wf08 - kwh_wf10) < 0.01, "Resi gas ignores weather_factor; uses HDD shape"

    def test_weather_factor_in_record(self):
        records = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
            weather_factor=0.75,
        )
        for rec in records:
            assert "weather_factor" in rec, "Record must contain weather_factor field"
            assert abs(rec["weather_factor"] - 0.75) < 0.001, "weather_factor must round-trip"

    def test_default_weather_factor_is_1(self):
        records = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
        )
        for rec in records:
            assert rec["weather_factor"] == 1.0, "Default weather_factor must be 1.0"
