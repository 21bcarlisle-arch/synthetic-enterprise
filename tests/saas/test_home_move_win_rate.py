import pytest

from saas.home_move_win_rate import (
    BASE_WIN_PROBABILITY,
    MAX_WIN_PROBABILITY,
    MIN_WIN_PROBABILITY,
    PRICE_SENSITIVITY_BY_EPC,
    build_home_move_win_rates,
    home_move_win_probability,
)

CUSTOMERS = [
    {"customer_id": "C1", "segment": "resi", "epc_rating": "D"},
    {"customer_id": "C2", "segment": "resi", "epc_rating": "G"},
    {"customer_id": "C5", "segment": "SME", "epc_rating": "C"},
]

CHURN_RISK = {
    "C1": [
        {"renewal_period": "2017-01", "bill_shock_count": 1, "churn_probability": 0.08},
        {"renewal_period": "2018-01", "bill_shock_count": 0, "churn_probability": 0.05},
    ],
    "C2": [
        {"renewal_period": "2017-01", "bill_shock_count": 0, "churn_probability": 0.05},
    ],
    "C5": [],
}


def test_win_probability_at_market_average_price_equals_segment_baseline():
    assert home_move_win_probability("resi", "D", 0.0) == BASE_WIN_PROBABILITY["resi"]
    assert home_move_win_probability("SME", "C", 0.0) == BASE_WIN_PROBABILITY["SME"]


def test_higher_price_than_market_reduces_win_probability():
    base = home_move_win_probability("resi", "D", 0.0)
    higher_price = home_move_win_probability("resi", "D", 0.05)
    assert higher_price < base
    assert higher_price == pytest.approx(base - 0.05 * PRICE_SENSITIVITY_BY_EPC["D"])


def test_lower_price_than_market_increases_win_probability():
    base = home_move_win_probability("resi", "D", 0.0)
    lower_price = home_move_win_probability("resi", "D", -0.05)
    assert lower_price > base
    assert lower_price == pytest.approx(base + 0.05 * PRICE_SENSITIVITY_BY_EPC["D"])


def test_worse_epc_rating_is_more_price_sensitive():
    # Same price disadvantage; G-rated property's win probability drops
    # further than a C-rated property's, since PRICE_SENSITIVITY_BY_EPC["G"]
    # > PRICE_SENSITIVITY_BY_EPC["C"].
    drop_c = BASE_WIN_PROBABILITY["resi"] - home_move_win_probability("resi", "C", 0.05)
    drop_g = BASE_WIN_PROBABILITY["resi"] - home_move_win_probability("resi", "G", 0.05)
    assert drop_g > drop_c


def test_win_probability_clamped_to_bounds():
    assert home_move_win_probability("resi", "G", 1.0) == MIN_WIN_PROBABILITY
    assert home_move_win_probability("resi", "G", -1.0) == MAX_WIN_PROBABILITY


def test_unknown_segment_falls_back_to_resi_baseline():
    assert home_move_win_probability("unknown", "D", 0.0) == BASE_WIN_PROBABILITY["resi"]


def test_unknown_epc_rating_falls_back_to_sensitivity_one():
    assert home_move_win_probability("resi", "unknown", 0.05) == pytest.approx(
        BASE_WIN_PROBABILITY["resi"] - 0.05 * 1.0
    )


def test_empty_churn_risk_returns_empty_dict():
    assert build_home_move_win_rates({}, CUSTOMERS, 0.0) == {}


def test_account_with_no_renewals_maps_to_empty_list():
    result = build_home_move_win_rates(CHURN_RISK, CUSTOMERS, 0.0)
    assert result["C5"] == []


def test_build_home_move_win_rates_attaches_constant_win_probability_per_account():
    result = build_home_move_win_rates(CHURN_RISK, CUSTOMERS, 0.0)
    expected_win_probability = home_move_win_probability("resi", "D", 0.0)
    for renewal in result["C1"]:
        assert renewal["win_probability"] == expected_win_probability


def test_effective_retention_probability_formula():
    result = build_home_move_win_rates(CHURN_RISK, CUSTOMERS, 0.0)
    renewal = result["C1"][0]
    churn_p = renewal["churn_probability"]
    win_p = renewal["win_probability"]
    expected = (1 - churn_p) + churn_p * win_p
    assert renewal["effective_retention_probability"] == pytest.approx(expected)


def test_effective_retention_probability_equals_one_when_no_churn_risk():
    result = build_home_move_win_rates(
        {"C1": [{"renewal_period": "2017-01", "bill_shock_count": 0, "churn_probability": 0.0}]},
        CUSTOMERS,
        0.0,
    )
    assert result["C1"][0]["effective_retention_probability"] == pytest.approx(1.0)


def test_renewal_periods_preserved_in_order():
    result = build_home_move_win_rates(CHURN_RISK, CUSTOMERS, 0.0)
    periods = [r["renewal_period"] for r in result["C1"]]
    assert periods == ["2017-01", "2018-01"]


def test_unknown_billing_account_raises_key_error():
    with pytest.raises(KeyError):
        build_home_move_win_rates({"C99": []}, CUSTOMERS, 0.0)


from saas.home_move_win_rate import (
    MIN_WIN_PROBABILITY,
    MAX_WIN_PROBABILITY,
    BASE_WIN_PROBABILITY,
    PRICE_SENSITIVITY_BY_EPC,
)


def test_min_win_probability():
    assert MIN_WIN_PROBABILITY == pytest.approx(0.05)


def test_max_win_probability():
    assert MAX_WIN_PROBABILITY == pytest.approx(0.95)


def test_resi_base_win_probability():
    assert BASE_WIN_PROBABILITY["resi"] == pytest.approx(0.55)


def test_sme_base_win_probability():
    assert BASE_WIN_PROBABILITY["SME"] == pytest.approx(0.35)


def test_epc_g_most_price_sensitive():
    assert PRICE_SENSITIVITY_BY_EPC["G"] > PRICE_SENSITIVITY_BY_EPC["A"]


def test_epc_sensitivity_monotonic():
    ratings = ["A", "B", "C", "D", "E", "F", "G"]
    sensitivities = [PRICE_SENSITIVITY_BY_EPC[r] for r in ratings]
    assert sensitivities == sorted(sensitivities)
