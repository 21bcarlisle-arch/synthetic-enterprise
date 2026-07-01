"""Tests for simulation/gas_settlement.py constants and pure helpers."""

import pytest

from simulation.gas_settlement import (
    GAS_CONSUMPTION_MONTHLY_PROFILE,
    GAS_IC_CONSUMPTION_MONTHLY_PROFILE,
    GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH,
    _GAS_BOILER_HEATING_FRACTION,
    _daily_consumption_kwh,
)


def test_daily_consumption_365_days():
    assert _daily_consumption_kwh(36500) == pytest.approx(100.0)


def test_daily_consumption_typical_resi():
    # 12000 kWh/yr ÷ 365 days
    assert _daily_consumption_kwh(12000) == pytest.approx(12000 / 365.0)


def test_daily_consumption_zero():
    assert _daily_consumption_kwh(0) == pytest.approx(0.0)


def test_monthly_profile_all_twelve_months():
    assert set(GAS_CONSUMPTION_MONTHLY_PROFILE.keys()) == set(range(1, 13))


def test_monthly_profile_jan_is_highest():
    assert GAS_CONSUMPTION_MONTHLY_PROFILE[1] == max(GAS_CONSUMPTION_MONTHLY_PROFILE.values())


def test_monthly_profile_july_is_lowest():
    assert GAS_CONSUMPTION_MONTHLY_PROFILE[7] == min(GAS_CONSUMPTION_MONTHLY_PROFILE.values())


def test_ic_profile_all_twelve_months():
    assert set(GAS_IC_CONSUMPTION_MONTHLY_PROFILE.keys()) == set(range(1, 13))


def test_ic_profile_feb_is_peak():
    # I&C: Feb (mid-winter building heat) peaks slightly above Jan
    assert GAS_IC_CONSUMPTION_MONTHLY_PROFILE[2] == max(GAS_IC_CONSUMPTION_MONTHLY_PROFILE.values())


def test_ic_profile_flat_vs_resi():
    # I&C jan:jul ratio much smaller than resi (process heat is flatter)
    resi_ratio = GAS_CONSUMPTION_MONTHLY_PROFILE[1] / GAS_CONSUMPTION_MONTHLY_PROFILE[7]
    ic_ratio = GAS_IC_CONSUMPTION_MONTHLY_PROFILE[1] / GAS_IC_CONSUMPTION_MONTHLY_PROFILE[7]
    assert ic_ratio < resi_ratio


def test_pass_through_fee_positive():
    assert GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH > 0


def test_boiler_heating_fraction_seventy_pct():
    assert _GAS_BOILER_HEATING_FRACTION == pytest.approx(0.70)
