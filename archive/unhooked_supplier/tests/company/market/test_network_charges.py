import pytest
"""Phase 122: Network Use of System (UoS) charges tests."""

from company.market.network_charges import (
    get_duos_rate, get_tnuos_rate, network_cost_per_mwh, annual_network_cost,
)


def test_duos_resi_2024():
    rate = get_duos_rate(2024, "resi")
    assert rate == 3.3


def test_duos_sme_higher_than_resi():
    resi = get_duos_rate(2024, "resi")
    sme = get_duos_rate(2024, "sme")
    assert sme > resi


def test_duos_ic_lower_than_resi():
    resi = get_duos_rate(2024, "resi")
    ic = get_duos_rate(2024, "ic")
    assert ic < resi


def test_duos_segment_alias_domestic():
    rate = get_duos_rate(2024, "domestic")
    assert rate == get_duos_rate(2024, "resi")


def test_duos_rises_over_time():
    r2016 = get_duos_rate(2016, "resi")
    r2025 = get_duos_rate(2025, "resi")
    assert r2025 > r2016


def test_tnuos_rate_2024():
    rate = get_tnuos_rate(2024)
    assert rate == 0.67


def test_network_cost_structure():
    result = network_cost_per_mwh(2024, "resi")
    assert "duos_p_per_kwh" in result
    assert "tnuos_p_per_kwh" in result
    assert "total_gbp_per_mwh" in result


def test_network_cost_gbp_per_mwh_conversion():
    result = network_cost_per_mwh(2024, "resi")
    expected = (result["duos_p_per_kwh"] + result["tnuos_p_per_kwh"]) * 10
    assert abs(result["total_gbp_per_mwh"] - expected) < 0.01


def test_annual_network_cost_scales():
    cost1 = annual_network_cost(2024, "resi", 1.0)
    cost2 = annual_network_cost(2024, "resi", 2.0)
    assert abs(cost2 - cost1 * 2) < 0.01


def test_annual_cost_positive():
    cost = annual_network_cost(2024, "sme", 100.0)
    assert cost > 0

import pytest

# --- Phase LB depth tests ---

def test_duos_resi_2022():
    rate = get_duos_rate(2022, 'resi')
    assert rate == pytest.approx(3.0)


def test_duos_sme_2022():
    rate = get_duos_rate(2022, 'sme')
    assert rate == pytest.approx(3.9)


def test_duos_ic_2022():
    rate = get_duos_rate(2022, 'ic')
    assert rate == pytest.approx(2.0)


def test_tnuos_rate_is_float():
    rate = get_tnuos_rate(2022)
    assert isinstance(rate, float)


def test_tnuos_rate_2022():
    rate = get_tnuos_rate(2022)
    assert rate == pytest.approx(0.62)


def test_network_cost_year_stored():
    result = network_cost_per_mwh(2022, 'resi')
    assert result['year'] == 2022


def test_network_cost_segment_stored():
    result = network_cost_per_mwh(2022, 'sme')
    assert result['segment'] == 'sme'


def test_network_cost_total_is_sum():
    result = network_cost_per_mwh(2022, 'resi')
    assert result['total_p_per_kwh'] == pytest.approx(result['duos_p_per_kwh'] + result['tnuos_p_per_kwh'])


def test_annual_cost_is_float():
    result = annual_network_cost(2022, 'resi', 10.0)
    assert isinstance(result, float)


def test_annual_cost_zero_zero_mwh():
    result = annual_network_cost(2022, 'resi', 0.0)
    assert result == pytest.approx(0.0)
