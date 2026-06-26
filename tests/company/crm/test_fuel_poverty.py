import pytest
from company.crm.fuel_poverty import (
    FuelPovertyBand, LIHCStatus, FuelPovertyAssessment, assess_fuel_poverty,
    _UK_MEDIAN_HOUSEHOLD_INCOME_GBP, _UK_MEDIAN_ENERGY_COST_GBP,
)


def test_not_fuel_poor_high_income():
    a = assess_fuel_poverty("C001", 80000.0, 2000.0)
    assert a.energy_spend_pct == pytest.approx(2.5)
    assert a.fuel_poverty_band == FuelPovertyBand.NOT_FUEL_POOR
    assert a.is_fuel_poor is False


def test_borderline_fuel_poor():
    a = assess_fuel_poverty("C002", 25000.0, 2200.0)
    assert a.energy_spend_pct == pytest.approx(8.8)
    assert a.fuel_poverty_band == FuelPovertyBand.BORDERLINE


def test_fuel_poor_above_10_pct():
    a = assess_fuel_poverty("C003", 18000.0, 2200.0)
    assert a.fuel_poverty_band == FuelPovertyBand.FUEL_POOR
    assert a.is_fuel_poor is True


def test_severely_fuel_poor_above_20_pct():
    a = assess_fuel_poverty("C004", 10000.0, 2500.0)
    assert a.energy_spend_pct > 20
    assert a.fuel_poverty_band == FuelPovertyBand.SEVERELY_FUEL_POOR


def test_lihc_low_income_high_cost():
    low_income = _UK_MEDIAN_HOUSEHOLD_INCOME_GBP * 0.50
    high_cost = _UK_MEDIAN_ENERGY_COST_GBP + 500
    a = assess_fuel_poverty("C005", low_income, high_cost)
    assert a.lihc_status != LIHCStatus.NOT_LIHC


def test_not_lihc_average_income():
    a = assess_fuel_poverty("C006", 45000.0, 1800.0)
    assert a.lihc_status == LIHCStatus.NOT_LIHC


def test_whd_eligible_if_lihc():
    low_income = _UK_MEDIAN_HOUSEHOLD_INCOME_GBP * 0.50
    a = assess_fuel_poverty("C007", low_income, _UK_MEDIAN_ENERGY_COST_GBP + 500)
    assert a.whd_eligible is True


def test_eco4_priority_if_fuel_poor():
    a = assess_fuel_poverty("C008", 15000.0, 3000.0)
    assert a.eco4_priority is True


def test_lihc_severe_very_high_spend_pct():
    low_income = _UK_MEDIAN_HOUSEHOLD_INCOME_GBP * 0.40
    a = assess_fuel_poverty("C009", low_income, low_income * 0.25)
    assert a.lihc_status == LIHCStatus.LIHC_SEVERE


def test_assessment_is_frozen():
    a = assess_fuel_poverty("C010", 20000.0, 2500.0)
    with pytest.raises(Exception):
        a.customer_id = "X"
