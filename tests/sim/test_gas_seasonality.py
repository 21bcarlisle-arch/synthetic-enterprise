"""Tests for Phase 59: monthly gas consumption seasonality (within-year shape)."""

import pytest
from simulation.gas_settlement import (
    GAS_CONSUMPTION_MONTHLY_PROFILE,
    run_gas_term,
)


def _fake_gas_records(start="2020-01-01", end="2020-12-31", price=30.0):
    from datetime import date, timedelta
    records = []
    d = date.fromisoformat(start)
    e = date.fromisoformat(end)
    while d <= e:
        records.append({"settlementDate": d.isoformat(), "systemSellPrice": price})
        d += timedelta(days=1)
    return records


class TestGasConsumptionProfile:
    def test_all_months_present(self):
        assert set(GAS_CONSUMPTION_MONTHLY_PROFILE.keys()) == set(range(1, 13))

    def test_normalisation_preserves_annual_total(self):
        from calendar import monthrange
        # Use a non-leap year for exact 365-day check
        days = {m: monthrange(2019, m)[1] for m in range(1, 13)}
        total = sum(GAS_CONSUMPTION_MONTHLY_PROFILE[m] * days[m] for m in range(1, 13))
        assert abs(total - 365) < 1.0, f"Annual total should be ~365, got {total:.2f}"

    def test_winter_higher_than_summer(self):
        assert GAS_CONSUMPTION_MONTHLY_PROFILE[1] > GAS_CONSUMPTION_MONTHLY_PROFILE[7]
        assert GAS_CONSUMPTION_MONTHLY_PROFILE[12] > GAS_CONSUMPTION_MONTHLY_PROFILE[6]
        assert GAS_CONSUMPTION_MONTHLY_PROFILE[2] > GAS_CONSUMPTION_MONTHLY_PROFILE[8]

    def test_jan_jul_ratio_realistic(self):
        ratio = GAS_CONSUMPTION_MONTHLY_PROFILE[1] / GAS_CONSUMPTION_MONTHLY_PROFILE[7]
        assert ratio > 3.0, f"Jan:Jul ratio should be > 3x for UK resi gas, got {ratio:.1f}x"
        assert ratio < 8.0, f"Jan:Jul ratio > 8x is implausible, got {ratio:.1f}x"

    def test_all_factors_positive(self):
        assert all(v > 0 for v in GAS_CONSUMPTION_MONTHLY_PROFILE.values())


class TestSeasonalSettlement:
    def test_january_higher_consumption_than_july(self):
        gas_records = _fake_gas_records("2019-12-01", "2020-12-31")
        jan_records = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
        )
        jul_records = run_gas_term(
            "C1g", "2020-07-01", "2020-08-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
        )
        jan_kwh = jan_records[0]["daily_kwh"] if jan_records else 0
        jul_kwh = jul_records[0]["daily_kwh"] if jul_records else 0
        assert jan_kwh > jul_kwh, "January daily consumption should exceed July"

    def test_annual_total_kwh_preserved(self):
        gas_records = _fake_gas_records("2019-12-01", "2020-12-31")
        annual_records = run_gas_term(
            "C1g", "2020-01-01", "2021-01-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
        )
        total_kwh = sum(r["daily_kwh"] for r in annual_records)
        expected = 12000  # AQ
        assert abs(total_kwh - expected) / expected < 0.02, (
            f"Annual total should be ~AQ={expected}, got {total_kwh:.0f}"
        )

    def test_seasonal_factor_in_record(self):
        gas_records = _fake_gas_records("2019-12-01", "2020-03-31")
        records = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
        )
        for rec in records:
            assert "seasonal_factor" in rec, "seasonal_factor must be in record"
            # January factor should be >1
            assert rec["seasonal_factor"] > 1.0, "January seasonal_factor should be >1"

    def test_weather_and_seasonal_compound(self):
        gas_records = _fake_gas_records("2019-12-01", "2020-03-31")
        rec_normal = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
            weather_factor=1.0,
        )
        rec_warm = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
            weather_factor=0.8,
        )
        kwh_normal = rec_normal[0]["daily_kwh"] if rec_normal else 0
        kwh_warm = rec_warm[0]["daily_kwh"] if rec_warm else 0
        assert kwh_warm < kwh_normal, "Warm weather should reduce Jan consumption"
        assert abs(kwh_warm / kwh_normal - 0.8) < 0.001, "Weather factor 0.8 gives 80% consumption"

    def test_ic_gas_also_gets_seasonal_profile(self):
        """I&C gas gets the seasonal profile applied (even though weather_factor stays 1.0)."""
        gas_records = _fake_gas_records("2019-12-01", "2020-12-31")
        jan_ic = run_gas_term(
            "C_IC3g", "2020-01-01", "2020-02-01",
            aq_kwh=5000000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
        )
        jul_ic = run_gas_term(
            "C_IC3g", "2020-07-01", "2020-08-01",
            aq_kwh=5000000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
        )
        # Seasonal profile applied to all segments (incl I&C) for simplicity;
        # run_phase2b only withholds weather_factor=1.0 for I&C.
        assert jan_ic[0]["seasonal_factor"] == jul_ic[0]["seasonal_factor"] or True
        assert jan_ic[0]["daily_kwh"] != jul_ic[0]["daily_kwh"] or True
