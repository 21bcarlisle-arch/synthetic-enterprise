import pytest
from saas.clv_model import (
    _annuity_factor,
    DISCOUNT_RATE_ANNUAL,
    FALLBACK_PRIOR_PSEUDO_COUNT,
    MAX_PROJECTION_PERIODS,
    build_clv,
    build_shifted_beta_geo_data,
    fit_theta_prior_from_churn_probabilities,
)

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


def test_build_shifted_beta_geo_data_excludes_accounts_with_no_renewals():
    data = build_shifted_beta_geo_data(CHURN_RISK)
    ids = set(data["customer_id"])
    assert ids == {"C1", "C2"}


def test_build_shifted_beta_geo_data_is_all_censored():
    data = build_shifted_beta_geo_data(CHURN_RISK)
    row = data[data["customer_id"] == "C1"].iloc[0]
    assert row["t_churn"] == row["T"] == 3


def test_fit_theta_prior_method_of_moments():
    alpha, beta = fit_theta_prior_from_churn_probabilities(CHURN_RISK)
    assert alpha > 0
    assert beta > 0
    # mean of Beta(alpha, beta) should match the mean churn probability
    thetas = [0.08, 0.05, 0.11, 0.05, 0.05]
    expected_mean = sum(thetas) / len(thetas)
    assert abs(alpha / (alpha + beta) - expected_mean) < 1e-9


def test_fit_theta_prior_falls_back_when_variance_is_degenerate():
    uniform_risk = {
        "C1": [{"renewal_period": "2017-01", "bill_shock_count": 0, "churn_probability": 0.05}],
    }
    alpha, beta = fit_theta_prior_from_churn_probabilities(uniform_risk)
    assert alpha + beta == FALLBACK_PRIOR_PSEUDO_COUNT
    assert abs(alpha / (alpha + beta) - 0.05) < 1e-9


def test_build_clv_excludes_accounts_with_no_renewals():
    result = build_clv(CHURN_RISK, COST_TO_SERVE, n_draws=50)
    assert set(result.keys()) == {"C1", "C2"}


def test_build_clv_combines_dual_fuel_net_margin():
    result = build_clv(CHURN_RISK, COST_TO_SERVE, n_draws=50)
    # C1's net margin combines C1 (400.0) and C1g (150.0) over 3 renewal periods
    assert abs(result["C1"]["avg_annual_net_margin_gbp"] - (400.0 + 150.0) / 3) < 1e-9


def test_build_clv_positive_lifetime_and_value():
    result = build_clv(CHURN_RISK, COST_TO_SERVE, n_draws=50)
    for account_id, entry in result.items():
        assert entry["expected_lifetime_periods"] > 0
        assert entry["clv_gbp"] > 0
        # CLV should be less than an undiscounted perpetuity proxy: avg margin
        # times expected lifetime (the annuity factor discounts future periods)
        assert entry["clv_gbp"] < entry["avg_annual_net_margin_gbp"] * entry["expected_lifetime_periods"]


def test_build_clv_empty_churn_risk_returns_empty():
    assert build_clv({"C1": []}, COST_TO_SERVE, n_draws=50) == {}


def test_discount_rate_is_positive():
    assert 0 < DISCOUNT_RATE_ANNUAL < 1


def test_annuity_factor_zero_periods():
    assert _annuity_factor(0, 0.10) == pytest.approx(0.0)


def test_annuity_factor_one_period():
    assert _annuity_factor(1, 0.10) == pytest.approx(1 / 1.1)


def test_annuity_factor_two_periods():
    expected = 1 / 1.1 + 1 / 1.21
    assert _annuity_factor(2, 0.10) == pytest.approx(expected)


def test_annuity_factor_fractional():
    expected = 0.5 / 1.1
    assert _annuity_factor(0.5, 0.10) == pytest.approx(expected)


def test_annuity_factor_one_and_half():
    expected = 1 / 1.1 + 0.5 / 1.21
    assert _annuity_factor(1.5, 0.10) == pytest.approx(expected)


def test_annuity_factor_zero_rate_equals_periods():
    assert _annuity_factor(3, 0.0) == pytest.approx(3.0)


def test_clv_constants():
    assert DISCOUNT_RATE_ANNUAL == pytest.approx(0.10)
    assert MAX_PROJECTION_PERIODS == 50  # noqa: E501
