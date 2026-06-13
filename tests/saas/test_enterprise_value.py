import pytest

from saas.clv_model import build_clv
from saas.enterprise_value import (
    adjust_churn_risk_for_home_move,
    build_enterprise_value,
    effective_churn_probability,
)
from saas.home_move_win_rate import build_home_move_win_rates

CUSTOMERS = [
    {"customer_id": "C1", "segment": "resi", "epc_rating": "D"},
    {"customer_id": "C2", "segment": "resi", "epc_rating": "D"},
    {"customer_id": "C3", "segment": "resi", "epc_rating": "D"},
]

CHURN_RISK = {
    "C1": [
        {"renewal_period": "2017-01", "bill_shock_count": 1, "churn_probability": 0.08},
        {"renewal_period": "2018-01", "bill_shock_count": 0, "churn_probability": 0.05},
        {"renewal_period": "2019-01", "bill_shock_count": 2, "churn_probability": 0.11},
    ],
    "C2": [
        {"renewal_period": "2017-01", "bill_shock_count": 0, "churn_probability": 0.05},
        {"renewal_period": "2018-01", "bill_shock_count": 0, "churn_probability": 0.05},
    ],
    "C3": [],
}

COST_TO_SERVE = {
    "by_customer": {
        "C1": {"cost_to_serve_gbp": 100.0, "margin_gbp": 500.0, "net_margin_gbp": 400.0},
        "C1g": {"cost_to_serve_gbp": 50.0, "margin_gbp": 200.0, "net_margin_gbp": 150.0},
        "C2": {"cost_to_serve_gbp": 80.0, "margin_gbp": 300.0, "net_margin_gbp": 220.0},
    }
}


def test_effective_churn_probability_is_product_of_churn_and_loss():
    assert effective_churn_probability(0.1, 0.6) == pytest.approx(0.1 * 0.4)


def test_effective_churn_probability_zero_when_win_probability_is_one():
    assert effective_churn_probability(0.5, 1.0) == 0.0


def test_effective_churn_probability_equals_churn_when_win_probability_is_zero():
    assert effective_churn_probability(0.5, 0.0) == 0.5


def test_adjust_churn_risk_reduces_churn_probability():
    win_rates = build_home_move_win_rates(CHURN_RISK, CUSTOMERS, price_differential_pct=0.0)
    adjusted = adjust_churn_risk_for_home_move(CHURN_RISK, win_rates)

    for account_id in ("C1", "C2"):
        for raw, adj in zip(CHURN_RISK[account_id], adjusted[account_id]):
            assert adj["churn_probability"] < raw["churn_probability"]
            assert adj["renewal_period"] == raw["renewal_period"]
            assert adj["bill_shock_count"] == raw["bill_shock_count"]


def test_adjust_churn_risk_preserves_accounts_with_no_renewals():
    win_rates = build_home_move_win_rates(CHURN_RISK, CUSTOMERS, 0.0)
    adjusted = adjust_churn_risk_for_home_move(CHURN_RISK, win_rates)
    assert adjusted["C3"] == []


def test_build_enterprise_value_excludes_accounts_with_no_renewals():
    result = build_enterprise_value(CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, n_draws=50)
    assert set(result["by_customer"].keys()) == {"C1", "C2"}
    assert result["portfolio"]["account_count"] == 2


def test_build_enterprise_value_portfolio_total_matches_sum_of_accounts():
    result = build_enterprise_value(CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, n_draws=50)
    total = sum(entry["clv_gbp"] for entry in result["by_customer"].values())
    assert result["portfolio"]["enterprise_value_gbp"] == pytest.approx(total)


def test_home_move_win_back_increases_clv_versus_raw_churn():
    # Lower effective churn (thanks to win-back potential) -> longer expected
    # lifetime -> higher CLV than clv_model's raw-churn projection.
    raw_clv = build_clv(CHURN_RISK, COST_TO_SERVE, n_draws=50)
    result = build_enterprise_value(CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, n_draws=50)

    for account_id in ("C1", "C2"):
        assert result["by_customer"][account_id]["clv_gbp"] >= raw_clv[account_id]["clv_gbp"]


def test_higher_price_differential_reduces_enterprise_value():
    # A price disadvantage lowers win_probability, raising effective churn,
    # which should not increase enterprise value relative to price parity.
    at_parity = build_enterprise_value(CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, n_draws=50)
    overpriced = build_enterprise_value(CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.1, n_draws=50)

    assert overpriced["portfolio"]["enterprise_value_gbp"] <= at_parity["portfolio"]["enterprise_value_gbp"]


def test_build_enterprise_value_empty_churn_risk_returns_empty():
    result = build_enterprise_value({"C1": []}, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, n_draws=50)
    assert result["by_customer"] == {}
    assert result["portfolio"] == {"enterprise_value_gbp": 0.0, "account_count": 0}
