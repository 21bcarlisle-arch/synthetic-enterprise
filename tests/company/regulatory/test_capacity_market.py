"""Phase 121: Capacity Market obligation tests."""
import pytest
from company.regulatory.capacity_market import (
    compute_cm_obligation, cm_charge_per_mwh, _CM_OBLIGATION_RATE_BY_YEAR,
)


def test_obligation_structure():
    result = compute_cm_obligation(2024, 10_000_000)
    assert result.year == 2024
    assert result.obligation_kw > 0
    assert result.annual_charge_gbp > 0


def test_annual_charge_scales_with_demand():
    r1 = compute_cm_obligation(2024, 1_000_000)
    r2 = compute_cm_obligation(2024, 2_000_000)
    assert r2.annual_charge_gbp > r1.annual_charge_gbp


def test_delivered_when_firm_capacity_meets_obligation():
    result = compute_cm_obligation(2024, 1_000_000, firm_capacity_kw=999_999)
    assert result.delivery_status == "DELIVERED"
    assert result.penalty_gbp == 0.0


def test_failed_when_no_firm_capacity():
    result = compute_cm_obligation(2024, 10_000_000, firm_capacity_kw=0)
    assert result.delivery_status == "FAILED"


def test_penalty_zero_when_delivered():
    result = compute_cm_obligation(2024, 1_000_000, firm_capacity_kw=999_999)
    assert result.penalty_gbp == 0.0


def test_crisis_year_higher_rate():
    rate_2022 = _CM_OBLIGATION_RATE_BY_YEAR[2022]
    rate_2021 = _CM_OBLIGATION_RATE_BY_YEAR[2021]
    assert rate_2022 > rate_2021


def test_cm_charge_per_mwh_positive():
    charge = cm_charge_per_mwh(2024, 5_000_000)
    assert charge > 0


def test_cm_charge_per_mwh_zero_demand():
    charge = cm_charge_per_mwh(2024, 0)
    assert charge == 0.0


def test_derating_factor_reduces_obligation():
    result = compute_cm_obligation(2024, 1_000_000)
    # obligation_kw should be 92% of gross peak
    peak_mw = (1_000_000 / 8760.0) * 1.8
    gross_kw = peak_mw * 1000
    expected = gross_kw * 0.92
    assert abs(result.obligation_kw - expected) < 10


def test_shortfall_when_partial():
    result = compute_cm_obligation(2024, 10_000_000, firm_capacity_kw=1)
    assert result.shortfall_kw > 0


# --- Phase JX depth tests ---

def test_partial_delivery_status():
    # demand 87600 MWh -> obligation ~16560 kw; shortfall 1060 < 10% -> PARTIAL
    result = compute_cm_obligation(2024, 87_600, firm_capacity_kw=15_500)
    assert result.delivery_status == 'PARTIAL'


def test_cm_charge_2022_higher_than_2021():
    charge_2022 = cm_charge_per_mwh(2022, 5_000_000)
    charge_2021 = cm_charge_per_mwh(2021, 5_000_000)
    assert charge_2022 > charge_2021


def test_cm_obligation_2021_rate():
    assert _CM_OBLIGATION_RATE_BY_YEAR[2021] == pytest.approx(0.77)


def test_cm_obligation_unknown_year_uses_2025_rate():
    r_unknown = compute_cm_obligation(9999, 1_000_000)
    r_2025 = compute_cm_obligation(2025, 1_000_000)
    assert r_unknown.clearing_price_gbp_per_kw == r_2025.clearing_price_gbp_per_kw


def test_penalty_formula():
    # demand 87600 -> obligation ~16560 kw; firm=0 -> shortfall=16560; rate=65 (2024)
    # penalty = round((16560/1000) * (65/8), 2) = round(134.55, 2)
    result = compute_cm_obligation(2024, 87_600, firm_capacity_kw=0)
    expected = round((result.shortfall_kw / 1000.0) * (65.0 / 8), 2)
    assert result.penalty_gbp == pytest.approx(expected)
