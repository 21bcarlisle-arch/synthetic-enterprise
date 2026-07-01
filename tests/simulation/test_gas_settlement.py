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


from datetime import date, timedelta
from simulation.gas_settlement import run_gas_term


def _gas_records(start_date, end_date, price=50.0):
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    records = []
    current = start
    while current < end:
        records.append({"settlementDate": current.isoformat(), "systemSellPrice": price})
        current += timedelta(days=1)
    return records


def test_run_gas_term_single_day():
    records = _gas_records("2022-01-01", "2022-01-10")
    result = run_gas_term(
        customer_id="C1",
        term_start="2022-01-01",
        term_end="2022-01-02",
        aq_kwh=12000,
        unit_rate_gbp_mwh=80.0,
        hedge_fraction=0.5,
        forward_price=70.0,
        monthly_cost_of_capital_gbp=5.0,
        gas_price_records=records,
    )
    assert len(result) == 1


def test_run_gas_term_end_date_exclusive():
    records = _gas_records("2022-01-01", "2022-01-10")
    result = run_gas_term(
        customer_id="C1",
        term_start="2022-01-01",
        term_end="2022-01-01",
        aq_kwh=12000,
        unit_rate_gbp_mwh=80.0,
        hedge_fraction=0.5,
        forward_price=70.0,
        monthly_cost_of_capital_gbp=5.0,
        gas_price_records=records,
    )
    assert len(result) == 0


def test_run_gas_term_all_keys_present():
    records = _gas_records("2022-01-01", "2022-01-10")
    result = run_gas_term(
        customer_id="C1",
        term_start="2022-01-01",
        term_end="2022-01-02",
        aq_kwh=12000,
        unit_rate_gbp_mwh=80.0,
        hedge_fraction=0.5,
        forward_price=70.0,
        monthly_cost_of_capital_gbp=5.0,
        gas_price_records=records,
    )
    r = result[0]
    for key in ("customer_id", "settlement_date", "commodity", "daily_kwh",
                "revenue_gbp", "wholesale_cost_gbp", "margin_gbp",
                "net_margin_gbp", "capital_cost_gbp", "hedge_fraction"):
        assert key in r


def test_run_gas_term_hedge_fraction_zero_uses_spot():
    spot = 100.0
    records = _gas_records("2022-01-01", "2022-01-10", price=spot)
    result = run_gas_term(
        customer_id="C1",
        term_start="2022-01-01",
        term_end="2022-01-02",
        aq_kwh=12000,
        unit_rate_gbp_mwh=80.0,
        hedge_fraction=0.0,
        forward_price=50.0,
        monthly_cost_of_capital_gbp=0.0,
        gas_price_records=records,
    )
    r = result[0]
    # With hedge_fraction=0, all cost is at spot
    # spot_price * daily_mwh
    expected_cost = spot * (r["daily_kwh"] / 1000.0)
    assert abs(r["wholesale_cost_gbp"] - expected_cost) < 1e-3


def test_run_gas_term_commodity_is_gas():
    records = _gas_records("2022-01-01", "2022-01-10")
    result = run_gas_term(
        customer_id="C1",
        term_start="2022-01-01",
        term_end="2022-01-03",
        aq_kwh=12000,
        unit_rate_gbp_mwh=80.0,
        hedge_fraction=0.5,
        forward_price=70.0,
        monthly_cost_of_capital_gbp=0.0,
        gas_price_records=records,
    )
    for r in result:
        assert r["commodity"] == "gas"
