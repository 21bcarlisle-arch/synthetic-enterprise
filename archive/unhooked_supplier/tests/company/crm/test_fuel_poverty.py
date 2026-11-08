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


# --- Phase LA depth tests ---

def test_customer_id_stored():
    a = FuelPovertyAssessment('C_LA', 30_000.0, 2_500.0)
    assert a.customer_id == 'C_LA'


def test_income_stored():
    a = FuelPovertyAssessment('C1', 25_000.0, 2_000.0)
    assert a.gross_annual_income_gbp == pytest.approx(25_000.0)


def test_energy_cost_stored():
    a = FuelPovertyAssessment('C1', 25_000.0, 3_000.0)
    assert a.estimated_annual_energy_cost_gbp == pytest.approx(3_000.0)


def test_energy_spend_pct_formula():
    a = FuelPovertyAssessment('C1', 20_000.0, 2_000.0)
    assert a.energy_spend_pct == pytest.approx(10.0)


def test_is_fuel_poor_bool():
    a = FuelPovertyAssessment('C1', 20_000.0, 2_500.0)
    assert isinstance(a.is_fuel_poor, bool)


def test_whd_eligible_bool():
    a = FuelPovertyAssessment('C1', 20_000.0, 2_500.0)
    assert isinstance(a.whd_eligible, bool)


def test_eco4_priority_bool():
    a = FuelPovertyAssessment('C1', 20_000.0, 2_500.0)
    assert isinstance(a.eco4_priority, bool)


def test_median_income_constant_is_positive():
    assert _UK_MEDIAN_HOUSEHOLD_INCOME_GBP > 0


def test_median_energy_cost_constant_is_positive():
    assert _UK_MEDIAN_ENERGY_COST_GBP > 0


def test_assess_fuel_poverty_returns_assessment():
    result = assess_fuel_poverty('C1', 20_000.0, 2_500.0)
    assert isinstance(result, FuelPovertyAssessment)
