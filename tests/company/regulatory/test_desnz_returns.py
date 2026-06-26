"""Phase 133: DESNZ supplier data returns tests."""

from company.regulatory.desnz_returns import (
    SupplierDataReturn, FuelPovertyDeclaration, CarbonIntensityReturn,
    estimate_fuel_poor_customers,
)


def _sdr():
    return SupplierDataReturn(
        reference_month="2024-03",
        electricity_customers=10_000,
        gas_customers=8_000,
        dual_fuel_customers=6_000,
        smart_meter_customers=7_500,
        prepayment_meter_customers=1_200,
        fixed_tariff_customers=8_000,
        variable_tariff_customers=2_000,
    )


def test_total_customers():
    sdr = _sdr()
    assert sdr.total_customers == 12_000  # 10k+8k-6k dual fuel


def test_smart_meter_pct():
    sdr = _sdr()
    assert sdr.smart_meter_pct == pytest.approx(62.5, abs=0.1)


def test_sdr_submission_default_false():
    sdr = _sdr()
    assert sdr.submitted is False


def test_fuel_poverty_rate():
    fp = FuelPovertyDeclaration(2024, 10_000, 1_500)
    assert fp.fuel_poverty_rate_pct == 15.0


def test_fuel_poverty_estimate_high_bill():
    count = estimate_fuel_poor_customers(10_000, 4_000)  # £4k bill >> threshold
    assert count > 0
    assert count < 10_000


def test_fuel_poverty_estimate_low_bill():
    # Bill below threshold — zero fuel poor
    count = estimate_fuel_poor_customers(10_000, 1_000)  # £1k << £2.5k threshold
    assert count == 0


def test_carbon_intensity_calculation():
    r = CarbonIntensityReturn(
        declaration_year=2024,
        total_kwh_supplied=1_000_000,
        renewable_kwh=400_000,
        nuclear_kwh=200_000,
        gas_kwh=300_000,
        coal_kwh=50_000,
        other_kwh=50_000,
    )
    assert r.co2_intensity_g_per_kwh > 0
    assert r.renewable_pct == 40.0


def test_pure_renewable_low_carbon():
    r = CarbonIntensityReturn(2024, 1_000_000, 1_000_000, 0, 0, 0, 0)
    assert r.co2_intensity_g_per_kwh == 15.0
    assert r.renewable_pct == 100.0


def test_carbon_zero_if_no_supply():
    r = CarbonIntensityReturn(2024, 0, 0, 0, 0, 0, 0)
    assert r.co2_intensity_g_per_kwh == 0.0


import pytest
