"""Tests for Phase 60: I&C gas flat seasonal consumption profile."""

import pytest
from simulation.gas_settlement import (
    GAS_CONSUMPTION_MONTHLY_PROFILE,
    GAS_IC_CONSUMPTION_MONTHLY_PROFILE,
    run_gas_term,
)


def _fake_gas_records(start="2019-12-01", end="2020-12-31", price=40.0):
    from datetime import date, timedelta
    records = []
    d = date.fromisoformat(start)
    e = date.fromisoformat(end)
    while d <= e:
        records.append({"settlementDate": d.isoformat(), "systemSellPrice": price})
        d += timedelta(days=1)
    return records


class TestIcGasProfile:
    def test_all_months_present(self):
        assert set(GAS_IC_CONSUMPTION_MONTHLY_PROFILE.keys()) == set(range(1, 13))

    def test_ic_normalisation_non_leap_year(self):
        from calendar import monthrange
        days = {m: monthrange(2019, m)[1] for m in range(1, 13)}
        total = sum(GAS_IC_CONSUMPTION_MONTHLY_PROFILE[m] * days[m] for m in range(1, 13))
        assert abs(total - 365) < 1.0, f"IC annual total should be ~365, got {total:.2f}"

    def test_ic_profile_much_flatter_than_resi(self):
        resi_jan = GAS_CONSUMPTION_MONTHLY_PROFILE[1]
        resi_jul = GAS_CONSUMPTION_MONTHLY_PROFILE[7]
        ic_jan = GAS_IC_CONSUMPTION_MONTHLY_PROFILE[1]
        ic_jul = GAS_IC_CONSUMPTION_MONTHLY_PROFILE[7]
        resi_ratio = resi_jan / resi_jul
        ic_ratio = ic_jan / ic_jul
        assert ic_ratio < resi_ratio / 2, (
            f"I&C profile should be much flatter than resi. "
            f"resi={resi_ratio:.1f}x, I&C={ic_ratio:.1f}x"
        )

    def test_ic_jan_jul_ratio_below_2(self):
        ratio = GAS_IC_CONSUMPTION_MONTHLY_PROFILE[1] / GAS_IC_CONSUMPTION_MONTHLY_PROFILE[7]
        assert 1.0 < ratio < 2.0, f"I&C Jan:Jul ratio should be 1.0-2.0x, got {ratio:.2f}x"

    def test_all_ic_factors_positive(self):
        assert all(v > 0 for v in GAS_IC_CONSUMPTION_MONTHLY_PROFILE.values())


class TestSegmentProfileSelection:
    def test_resi_uses_resi_profile(self):
        gas_records = _fake_gas_records()
        recs = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
            segment="resi",
        )
        # Resi Jan factor ~1.88 → daily_kwh >> AQ/365
        expected_factor = GAS_CONSUMPTION_MONTHLY_PROFILE[1]
        actual_factor = recs[0]["seasonal_factor"]
        assert abs(actual_factor - expected_factor) < 0.001, (
            f"Resi should use resi profile. Expected {expected_factor}, got {actual_factor}"
        )

    def test_ic_uses_ic_profile(self):
        gas_records = _fake_gas_records()
        recs = run_gas_term(
            "C_IC3g", "2020-01-01", "2020-02-01",
            aq_kwh=5000000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
            segment="I&C",
        )
        expected_factor = GAS_IC_CONSUMPTION_MONTHLY_PROFILE[1]
        actual_factor = recs[0]["seasonal_factor"]
        assert abs(actual_factor - expected_factor) < 0.001, (
            f"I&C should use IC profile. Expected {expected_factor}, got {actual_factor}"
        )

    def test_ic_jan_consumption_not_5x_jul(self):
        gas_records = _fake_gas_records()
        jan_recs = run_gas_term(
            "C_IC3g", "2020-01-01", "2020-02-01",
            aq_kwh=5000000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
            segment="I&C",
        )
        jul_recs = run_gas_term(
            "C_IC3g", "2020-07-01", "2020-08-01",
            aq_kwh=5000000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=gas_records,
            segment="I&C",
        )
        ratio = jan_recs[0]["daily_kwh"] / jul_recs[0]["daily_kwh"]
        assert ratio < 2.0, f"I&C gas Jan:Jul kwh ratio should be <2, got {ratio:.2f}"
        assert ratio > 1.0, "I&C gas has slight winter uplift"
