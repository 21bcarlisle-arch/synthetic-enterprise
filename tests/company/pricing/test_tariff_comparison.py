"""Tests for Portal Phase 2: tariff comparison (Phase 77)."""

import pytest
from company.pricing.tariff_comparison import (
    STANDING_CHARGE_IC_P_PER_DAY,
    STANDING_CHARGE_RESI_P_PER_DAY,
    annual_cost_gbp,
    compare_tariffs,
    unit_rate_from_forward,
)


class _MockSI:
    """Minimal mock sim_interface that returns predictable forward prices."""
    def get_forward_price(self, fuel, delivery_date, term_months=12):
        return 100.0 + term_months  # longer term = slightly higher price


def test_unit_rate_from_forward_basic():
    rate = unit_rate_from_forward(100.0, markup_pct=0.0, vat_rate=0.0)
    assert rate == pytest.approx(10.0)  # £100/MWh = 10p/kWh


def test_unit_rate_includes_markup():
    rate = unit_rate_from_forward(100.0, markup_pct=10.0, vat_rate=0.0)
    assert rate == pytest.approx(11.0)


def test_unit_rate_includes_vat():
    rate = unit_rate_from_forward(100.0, markup_pct=0.0, vat_rate=0.05)
    assert rate == pytest.approx(10.5)


def test_annual_cost_gbp():
    cost = annual_cost_gbp(unit_rate_p=10.0, standing_charge_p=50.0, eac_kwh=3500.0)
    energy = 10.0 / 100 * 3500
    sc = 50.0 / 100 * 365
    assert cost == pytest.approx(energy + sc)


def test_compare_tariffs_returns_three_options():
    options = compare_tariffs(3500.0, _MockSI(), "2025-01-01", "resi")
    assert len(options) == 3


def test_compare_tariffs_sorted_by_cost():
    options = compare_tariffs(3500.0, _MockSI(), "2025-01-01", "resi")
    costs = [o["estimated_annual_cost_gbp"] for o in options]
    assert costs == sorted(costs)


def test_compare_tariffs_required_fields():
    options = compare_tariffs(3500.0, _MockSI(), "2025-01-01", "resi")
    required = {"name", "term_months", "forward_gbp_per_mwh", "unit_rate_p_per_kwh",
                "standing_charge_p_per_day", "estimated_annual_cost_gbp"}
    for opt in options:
        assert set(opt.keys()) == required


def test_ic_segment_has_zero_standing_charge():
    options = compare_tariffs(100_000.0, _MockSI(), "2025-01-01", "ic")
    for opt in options:
        assert opt["standing_charge_p_per_day"] == STANDING_CHARGE_IC_P_PER_DAY


def test_resi_segment_has_standing_charge():
    options = compare_tariffs(3500.0, _MockSI(), "2025-01-01", "resi")
    for opt in options:
        assert opt["standing_charge_p_per_day"] == STANDING_CHARGE_RESI_P_PER_DAY


def test_sme_segment_standing_charge():
    from company.pricing.tariff_comparison import STANDING_CHARGE_SME_P_PER_DAY
    options = compare_tariffs(25000.0, _MockSI(), "2025-01-01", "sme")
    for opt in options:
        assert opt["standing_charge_p_per_day"] == STANDING_CHARGE_SME_P_PER_DAY


def test_unit_rate_markup_and_vat_combined():
    rate = unit_rate_from_forward(100.0, markup_pct=10.0, vat_rate=0.05)
    expected = 100.0 / 1000.0 * 1.10 * 1.05 * 100.0
    assert rate == pytest.approx(expected, rel=0.001)


def test_annual_cost_zero_standing_charge():
    cost = annual_cost_gbp(10.0, 0.0, 3500.0)
    assert cost == pytest.approx(350.0)


def test_compare_has_fixed_1yr_option():
    options = compare_tariffs(3500.0, _MockSI(), "2025-01-01", "resi")
    names = [o["name"] for o in options]
    assert "Fixed 1 Year" in names


def test_unit_rate_200_gbp_per_mwh():
    rate = unit_rate_from_forward(200.0, markup_pct=0.0, vat_rate=0.0)
    assert rate == pytest.approx(20.0)


def test_business_vat_higher_than_domestic():
    resi_rate = unit_rate_from_forward(100.0, markup_pct=0.0, vat_rate=0.05)
    sme_rate = unit_rate_from_forward(100.0, markup_pct=0.0, vat_rate=0.20)
    assert sme_rate > resi_rate


def test_annual_cost_proportional_to_eac():
    cost_low = annual_cost_gbp(10.0, 0.0, 3000.0)
    cost_high = annual_cost_gbp(10.0, 0.0, 6000.0)
    assert cost_high == pytest.approx(cost_low * 2.0)


def test_compare_tariffs_variable_option_present():
    options = compare_tariffs(3500.0, _MockSI(), "2025-01-01", "resi")
    names = [o["name"] for o in options]
    assert "Variable SVT" in names


def test_compare_tariffs_forward_price_in_result():
    options = compare_tariffs(3500.0, _MockSI(), "2025-01-01", "resi")
    for opt in options:
        assert opt["forward_gbp_per_mwh"] > 0


def test_compare_tariffs_unit_rate_positive():
    options = compare_tariffs(3500.0, _MockSI(), "2025-01-01", "resi")
    for opt in options:
        assert opt["unit_rate_p_per_kwh"] > 0
