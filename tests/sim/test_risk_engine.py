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
