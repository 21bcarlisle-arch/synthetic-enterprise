"""Phase 140: MOA charge management tests."""

from company.billing.moa_charges import (
    get_moa_annual_charge, get_moa_daily_charge, calculate_moa_charges, moa_portfolio_cost
)


def test_trad_meter_2016_rate():
    assert get_moa_annual_charge("TRAD", 2016) == 12.0


def test_amr_meter_2024_rate():
    assert get_moa_annual_charge("AMR", 2024) == 85.0


def test_smets2_higher_than_trad():
    s2 = get_moa_annual_charge("SMETS2", 2022)
    trad = get_moa_annual_charge("TRAD", 2022)
    assert s2 > trad


def test_interpolation_between_years():
    rate_2018 = get_moa_annual_charge("TRAD", 2018)
    rate_2020 = get_moa_annual_charge("TRAD", 2020)
    rate_2019 = get_moa_annual_charge("TRAD", 2019)
    assert rate_2018 <= rate_2019 <= rate_2020


def test_daily_charge_is_annual_over_365():
    annual = get_moa_annual_charge("SMETS2", 2024)
    daily = get_moa_daily_charge("SMETS2", 2024)
    assert abs(daily * 365 - annual) < 0.01


def test_unknown_meter_type_defaults():
    rate = get_moa_annual_charge("UNKNOWN_TYPE", 2024)
    assert rate == 14.0


def test_calculate_moa_charges_single():
    mps = [{"mpan_or_mprn": "1000000000001", "meter_type": "TRAD", "days_in_period": 365}]
    lines = calculate_moa_charges(mps, 2024)
    assert len(lines) == 1
    assert lines[0].charge_gbp == pytest.approx(16.0, abs=0.1)


def test_portfolio_cost_multiple_meters():
    mps = [
        {"mpan_or_mprn": "M001", "meter_type": "TRAD", "days_in_period": 365},
        {"mpan_or_mprn": "M002", "meter_type": "SMETS2", "days_in_period": 365},
    ]
    total = moa_portfolio_cost(mps, 2024)
    assert total == pytest.approx(16.0 + 28.0, abs=0.5)


def test_partial_year_charge():
    mps = [{"mpan_or_mprn": "M001", "meter_type": "TRAD", "days_in_period": 182}]
    lines = calculate_moa_charges(mps, 2024)
    assert lines[0].charge_gbp < 16.0


import pytest


# --- Phase KV depth tests ---

def test_mpan_stored_on_invoice_line():
    lines = calculate_moa_charges([{"mpan_or_mprn": "MP001", "meter_type": "TRAD"}], 2022)
    assert lines[0].mpan_or_mprn == "MP001"


def test_meter_type_stored_on_invoice_line():
    lines = calculate_moa_charges([{"mpan_or_mprn": "MP001", "meter_type": "SMETS2"}], 2022)
    assert lines[0].meter_type == "SMETS2"


def test_year_stored_on_invoice_line():
    lines = calculate_moa_charges([{"mpan_or_mprn": "MP001", "meter_type": "TRAD"}], 2020)
    assert lines[0].year == 2020


def test_days_in_period_default_365():
    lines = calculate_moa_charges([{"mpan_or_mprn": "MP001", "meter_type": "TRAD"}], 2022)
    assert lines[0].days_in_period == 365


def test_charge_gbp_proportional_to_days():
    full = calculate_moa_charges([{"mpan_or_mprn": "MP001", "meter_type": "TRAD", "days_in_period": 365}], 2022)
    half = calculate_moa_charges([{"mpan_or_mprn": "MP001", "meter_type": "TRAD", "days_in_period": 182}], 2022)
    assert full[0].charge_gbp > half[0].charge_gbp


def test_smets1_annual_charge_2022():
    rate = get_moa_annual_charge("SMETS1", 2022)
    assert rate == pytest.approx(24.0)


def test_ppm_higher_than_trad():
    assert get_moa_annual_charge("PPM", 2022) > get_moa_annual_charge("TRAD", 2022)


def test_amr_highest_rate():
    amr = get_moa_annual_charge("AMR", 2022)
    smets2 = get_moa_annual_charge("SMETS2", 2022)
    assert amr > smets2


def test_portfolio_cost_zero_empty():
    assert moa_portfolio_cost([], 2022) == pytest.approx(0.0)


def test_daily_charge_is_float():
    result = get_moa_daily_charge("TRAD", 2022)
    assert isinstance(result, float)
