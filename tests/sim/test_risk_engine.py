from sim.risk_engine import (
    SIGMA_STRESSED_POST_REFORM,
    SIGMA_STRESSED_PRE_REFORM,
    calculate_active_collateral,
    calculate_monthly_cost_of_capital,
    calculate_var,
    compute_net_margin,
    get_sigma_stressed,
    is_administration_triggered,
)


def test_var_increases_with_naked_volume():
    sigma = 1.0
    forward_price_gbp_per_mwh = 10.0
    smaller_volume = 1000
    larger_volume = 5000

    var_smaller = calculate_var(sigma, smaller_volume, forward_price_gbp_per_mwh)
    var_larger = calculate_var(sigma, larger_volume, forward_price_gbp_per_mwh)

    assert var_larger > var_smaller


def test_stressed_var_floor_binds_post_2023():
    sigma_pre_reform = get_sigma_stressed("2022-12-31")
    sigma_post_reform = get_sigma_stressed("2023-01-01")

    assert sigma_pre_reform == SIGMA_STRESSED_PRE_REFORM
    assert sigma_post_reform == SIGMA_STRESSED_POST_REFORM
    assert sigma_post_reform > sigma_pre_reform

    naked_volume_kwh = 1000
    forward_price_gbp_per_mwh = 10.0

    # A "current conditions" view calmer than the post-2023 regulatory floor —
    # the floor must still bind regardless.
    sigma_recent = 0.20
    var_current = calculate_var(sigma_recent, naked_volume_kwh, forward_price_gbp_per_mwh)
    var_stressed = calculate_var(sigma_post_reform, naked_volume_kwh, forward_price_gbp_per_mwh)

    assert var_stressed > var_current
    assert calculate_active_collateral(var_current, var_stressed) == var_stressed


def test_coc_deducted_from_net_margin():
    gross_margin_gbp = 100.0
    capital_cost_gbp = 15.0

    net_margin = compute_net_margin(gross_margin_gbp, capital_cost_gbp)
    assert net_margin == 85.0

    active_collateral_gbp = 1000.0
    monthly_cost_of_capital_gbp = calculate_monthly_cost_of_capital(active_collateral_gbp)

    computed_net_margin = compute_net_margin(500.0, monthly_cost_of_capital_gbp)
    assert computed_net_margin == 500.0 - monthly_cost_of_capital_gbp


def test_administration_triggers_at_zero_treasury():
    assert is_administration_triggered(0) is True
    assert is_administration_triggered(-50.0) is True
    assert is_administration_triggered(100.0) is False


from sim.risk_engine import (
    Z_SCORE_90_CONFIDENCE,
    WACC,
    SIGMA_STRESSED_PRE_REFORM,
    SIGMA_STRESSED_POST_REFORM,
    REGULATORY_REGIME_CHANGE_DATE,
    calculate_var,
    calculate_active_collateral,
    calculate_monthly_cost_of_capital,
)


def test_z_score_90_confidence():
    assert Z_SCORE_90_CONFIDENCE == 1.645


def test_wacc_is_10_percent():
    assert WACC == 0.10


def test_sigma_stressed_post_higher_than_pre():
    assert SIGMA_STRESSED_POST_REFORM > SIGMA_STRESSED_PRE_REFORM


def test_var_formula_matches_z_sigma_price_volume():
    sigma = 0.50
    volume_kwh = 2000.0
    price = 100.0
    result = calculate_var(sigma, volume_kwh, price)
    expected = Z_SCORE_90_CONFIDENCE * sigma * price * (volume_kwh / 1000.0)
    assert abs(result - expected) < 1e-6


def test_active_collateral_is_max_of_current_and_stressed():
    assert calculate_active_collateral(100.0, 200.0) == 200.0
    assert calculate_active_collateral(300.0, 200.0) == 300.0


def test_monthly_cost_of_capital_formula():
    collateral = 12000.0
    expected = collateral * WACC / 12
    assert abs(calculate_monthly_cost_of_capital(collateral) - expected) < 1e-6


def test_sigma_recent_raises_on_empty_records():
    from sim.risk_engine import calculate_sigma_recent
    import pytest
    with pytest.raises((ValueError, ZeroDivisionError, IndexError, Exception)):
        calculate_sigma_recent("2022-01-01", [])


def test_regulatory_regime_change_date_2023():
    assert REGULATORY_REGIME_CHANGE_DATE == "2023-01-01"


def test_stressed_var_higher_post_reform():
    from sim.risk_engine import get_sigma_stressed
    s_pre = get_sigma_stressed("2022-12-31")
    s_post = get_sigma_stressed("2023-01-01")
    var_pre = calculate_var(s_pre, 1000.0, 50.0)
    var_post = calculate_var(s_post, 1000.0, 50.0)
    assert var_post > var_pre
