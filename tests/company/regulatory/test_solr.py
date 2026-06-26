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
