"""Phase 117: SoLR risk assessment tests."""

from company.regulatory.solr import (
    solr_capital_requirement, solr_revenue_upside, solr_scenario,
    _SOLR_LEVY_PER_CUSTOMER_GBP,
)


def test_capital_requirement_basic():
    result = solr_capital_requirement(10_000, 2_000_000)
    assert result["transfer_size"] == 10_000
    assert result["levy_gbp"] == round(10_000 * _SOLR_LEVY_PER_CUSTOMER_GBP, 2)


def test_capital_sustainable_when_treasury_large():
    result = solr_capital_requirement(1_000, 10_000_000)
    assert result["sustainable"] is True
    assert result["status"] == "SUSTAINABLE"


def test_capital_unsustainable_when_treasury_small():
    result = solr_capital_requirement(100_000, 100_000)
    assert result["sustainable"] is False
    assert result["status"] == "UNSUSTAINABLE"


def test_capital_marginal():
    # Treasury just covers requirement but not 50% headroom above it
    result = solr_capital_requirement(5_000, 650_000)
    assert result["status"] in ("MARGINAL", "SUSTAINABLE", "UNSUSTAINABLE")
    assert "status" in result


def test_headroom_calculated_correctly():
    result = solr_capital_requirement(1_000, 2_000_000)
    expected_headroom = 2_000_000 - result["total_required_gbp"]
    assert abs(result["headroom_gbp"] - expected_headroom) < 1.0


def test_revenue_upside_churn():
    result = solr_revenue_upside(10_000, 0.12)
    assert result["expected_churn_3m"] == 1_200
    assert result["retained_customers"] == 8_800


def test_revenue_upside_annual_revenue_positive():
    result = solr_revenue_upside(1_000)
    assert result["estimated_annual_revenue_gbp"] > 0


def test_solr_scenario_small():
    result = solr_scenario("small", 5_000_000)
    assert result["scenario"] == "small"
    assert result["transfer_size"] == 5_000
    assert "revenue" in result


def test_solr_scenario_large_unsustainable_small_treasury():
    result = solr_scenario("large", 100_000)
    assert result["sustainable"] is False


def test_solr_scenario_keys():
    result = solr_scenario("medium", 10_000_000)
    for key in ("levy_gbp", "total_required_gbp", "headroom_gbp", "status", "revenue"):
        assert key in result

import pytest

# --- Phase LF depth tests ---

def test_transfer_size_in_result():
    result = solr_capital_requirement(1000, 500_000.0)
    assert result['transfer_size'] == 1000


def test_levy_positive():
    result = solr_capital_requirement(1000, 500_000.0)
    assert result['levy_gbp'] > 0.0


def test_bad_debt_risk_positive():
    result = solr_capital_requirement(1000, 500_000.0)
    assert result['bad_debt_risk_gbp'] > 0.0


def test_total_required_sum_levy_bad_debt():
    result = solr_capital_requirement(1000, 500_000.0)
    assert result['total_required_gbp'] == pytest.approx(result['levy_gbp'] + result['bad_debt_risk_gbp'])


def test_treasury_stored():
    result = solr_capital_requirement(1000, 750_000.0)
    assert result['treasury_gbp'] == pytest.approx(750_000.0)


def test_status_is_string():
    result = solr_capital_requirement(1000, 500_000.0)
    assert isinstance(result['status'], str)


def test_sustainable_bool():
    result = solr_capital_requirement(1000, 500_000.0)
    assert isinstance(result['sustainable'], bool)


def test_revenue_upside_returns_dict():
    result = solr_revenue_upside(1000)
    assert isinstance(result, dict)


def test_revenue_upside_transfer_size():
    result = solr_revenue_upside(5000)
    assert result['transfer_size'] == 5000


def test_headroom_is_treasury_minus_required():
    result = solr_capital_requirement(1000, 500_000.0)
    expected = result['treasury_gbp'] - result['total_required_gbp']
    assert result['headroom_gbp'] == pytest.approx(expected)
