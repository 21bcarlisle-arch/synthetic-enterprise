"""Phase MU Coverage Depth Sprint CXIX.

Targets three sim/ modules that had only 4 tests each:
  sim/hedging_strategy  — constants, boundary conditions, reasoning text
  sim/risk_engine       — constants, formula, VaR pipeline, assess_term_risk
  sim/weather_price_sensitivity — constants, HDD boundary, multiplier trigger

10 tests per module, 30 total.
"""

import pytest

from sim.hedging_strategy import (
    EVOLUTION_STEP,
    MARGIN_TOLERANCE_GBP,
    MIN_HEDGE_FLOOR,
    evolve_hedge_fraction,
)
from sim.risk_engine import (
    SIGMA_STRESSED_POST_REFORM,
    SIGMA_STRESSED_PRE_REFORM,
    WACC,
    Z_SCORE_90_CONFIDENCE,
    assess_term_risk,
    calculate_active_collateral,
    calculate_sigma_recent,
    calculate_var,
    get_sigma_stressed,
)
from sim.weather_price_sensitivity import (
    BASELINE_HEATING_DEGREE_DAYS,
    COLD_SPELL_HDD_THRESHOLD,
    COLD_SPELL_PRICE_MULTIPLIER,
    average_heating_degree_days,
    weather_sensitivity_multiplier,
)

# ---------------------------------------------------------------------------
# Fixtures for risk_engine tests
# ---------------------------------------------------------------------------

_RECORDS_2021 = [
    {"settlementDate": f"2021-{m:02d}-15", "systemSellPrice": 100.0}
    for m in range(1, 13)
]
_RECORDS_2022 = [
    {"settlementDate": f"2022-{m:02d}-15", "systemSellPrice": 100.0}
    for m in range(1, 13)
]


# ---------------------------------------------------------------------------
# sim/hedging_strategy -- 10 tests
# ---------------------------------------------------------------------------


def test_hedging_evolution_step_constant():
    assert EVOLUTION_STEP == pytest.approx(0.1)


def test_hedging_margin_tolerance_constant():
    assert MARGIN_TOLERANCE_GBP == pytest.approx(5.0)


def test_hedging_hold_at_positive_tolerance_boundary():
    # difference == +MARGIN_TOLERANCE_GBP is NOT strictly > threshold -> hold
    current = 0.90
    naked = 50.0
    actual = naked + MARGIN_TOLERANCE_GBP  # difference == 5.0 exactly
    new_hf, _ = evolve_hedge_fraction(current, naked, actual)
    assert new_hf == pytest.approx(current)


def test_hedging_hold_at_negative_tolerance_boundary():
    # difference == -MARGIN_TOLERANCE_GBP is NOT strictly < -threshold -> hold
    current = 0.90
    naked = 50.0
    actual = naked - MARGIN_TOLERANCE_GBP  # difference == -5.0 exactly
    new_hf, _ = evolve_hedge_fraction(current, naked, actual)
    assert new_hf == pytest.approx(current)


def test_hedging_evolve_up_from_floor_by_one_step():
    new_hf, _ = evolve_hedge_fraction(
        MIN_HEDGE_FLOOR, naked_margin_gbp=50.0, actual_margin_gbp=100.0
    )
    assert new_hf == pytest.approx(MIN_HEDGE_FLOOR + EVOLUTION_STEP)


def test_hedging_evolve_up_capped_at_full_hedge():
    # 0.95 + 0.1 = 1.05 -> capped at 1.0
    new_hf, _ = evolve_hedge_fraction(0.95, naked_margin_gbp=50.0, actual_margin_gbp=100.0)
    assert new_hf == pytest.approx(1.0)


def test_hedging_evolve_down_from_above_floor():
    # 0.95 - 0.1 = 0.85 == MIN_HEDGE_FLOOR (floor is not breached)
    new_hf, _ = evolve_hedge_fraction(0.95, naked_margin_gbp=100.0, actual_margin_gbp=50.0)
    assert new_hf == pytest.approx(MIN_HEDGE_FLOOR)


def test_hedging_evolve_down_at_floor_stays_floored():
    # Already at floor; decrease clamped to floor
    new_hf, reasoning = evolve_hedge_fraction(
        MIN_HEDGE_FLOOR, naked_margin_gbp=200.0, actual_margin_gbp=50.0
    )
    assert new_hf == pytest.approx(MIN_HEDGE_FLOOR)
    assert "mandate floor" in reasoning.lower()


def test_hedging_raise_reasoning_contains_actual_values():
    actual, naked = 100.0, 50.0
    _, reasoning = evolve_hedge_fraction(MIN_HEDGE_FLOOR, naked, actual)
    assert "100" in reasoning and "50" in reasoning


def test_hedging_hold_reasoning_describes_noise():
    # Difference = 3.0 < 5.0 -> hold; reasoning should flag it as noise/tolerance
    _, reasoning = evolve_hedge_fraction(0.90, naked_margin_gbp=50.0, actual_margin_gbp=53.0)
    assert "noise" in reasoning.lower() or "tolerance" in reasoning.lower()


# ---------------------------------------------------------------------------
# sim/risk_engine -- 10 tests
# ---------------------------------------------------------------------------


def test_risk_z_score_constant():
    assert Z_SCORE_90_CONFIDENCE == pytest.approx(1.645)


def test_risk_wacc_constant():
    assert WACC == pytest.approx(0.10)


def test_risk_calculate_sigma_recent_returns_nonneg_float():
    sigma = calculate_sigma_recent("2022-06-01", _RECORDS_2021)
    assert isinstance(sigma, float)
    assert sigma >= 0.0


def test_risk_calculate_sigma_recent_bootstrap_fallback():
    # Records start at reference_date -> backward window empty -> forward bootstrap
    records = [
        {"settlementDate": f"2021-{m:02d}-15", "systemSellPrice": 80.0 + m}
        for m in range(1, 13)
    ]
    sigma = calculate_sigma_recent("2021-01-15", records)
    assert isinstance(sigma, float)
    assert sigma >= 0.0


def test_risk_calculate_sigma_recent_raises_no_records():
    # Records in 2015 are outside both backward and forward windows of 2025-01-01
    records = [{"settlementDate": "2015-06-01", "systemSellPrice": 50.0}]
    with pytest.raises(ValueError):
        calculate_sigma_recent("2025-01-01", records)


def test_risk_calculate_var_exact_formula():
    sigma = 1.0
    volume_kwh = 1000.0  # = 1 MWh
    price = 10.0
    expected = Z_SCORE_90_CONFIDENCE * sigma * (volume_kwh / 1000.0) * price
    assert calculate_var(sigma, volume_kwh, price) == pytest.approx(expected)


def test_risk_get_sigma_stressed_exact_boundary():
    assert get_sigma_stressed("2022-12-31") == pytest.approx(SIGMA_STRESSED_PRE_REFORM)
    assert get_sigma_stressed("2023-01-01") == pytest.approx(SIGMA_STRESSED_POST_REFORM)


def test_risk_calculate_active_collateral_picks_max():
    assert calculate_active_collateral(100.0, 200.0) == pytest.approx(200.0)
    assert calculate_active_collateral(300.0, 150.0) == pytest.approx(300.0)


def test_risk_assess_term_risk_returns_all_keys():
    result = assess_term_risk("2022-01-01", 1000.0, 100.0, _RECORDS_2021)
    assert set(result.keys()) == {
        "sigma_recent",
        "sigma_stressed",
        "var_current_gbp",
        "var_stressed_gbp",
        "active_collateral_gbp",
        "monthly_cost_of_capital_gbp",
    }


def test_risk_assess_term_risk_post_reform_higher_cost():
    # Post-2023 stressed floor (1.50) >> pre-reform (0.50); with flat prices
    # sigma_recent = 0 -> stressed VaR binds; post-reform must yield higher cost.
    result_pre = assess_term_risk("2022-01-01", 1000.0, 100.0, _RECORDS_2021)
    result_post = assess_term_risk("2023-06-01", 1000.0, 100.0, _RECORDS_2022)
    assert result_post["monthly_cost_of_capital_gbp"] > result_pre["monthly_cost_of_capital_gbp"]


# ---------------------------------------------------------------------------
# sim/weather_price_sensitivity -- 10 tests
# ---------------------------------------------------------------------------


def test_weather_cold_spell_threshold_constant():
    assert COLD_SPELL_HDD_THRESHOLD == pytest.approx(8.0)


def test_weather_baseline_hdd_constant():
    assert BASELINE_HEATING_DEGREE_DAYS == pytest.approx(5.5)


def test_weather_cold_spell_multiplier_constant():
    assert COLD_SPELL_PRICE_MULTIPLIER == pytest.approx(1.10)


def test_weather_avg_hdd_at_heating_base_is_zero():
    # HEATING_BASE_TEMP_C = 15.5; HDD = max(0, 15.5 - 15.5) = 0.0
    assert average_heating_degree_days([15.5]) == pytest.approx(0.0)


def test_weather_avg_hdd_above_base_clamped_to_zero():
    # 20.0 > 15.5 -> HDD = max(0, 15.5 - 20.0) = 0.0
    assert average_heating_degree_days([20.0]) == pytest.approx(0.0)


def test_weather_avg_hdd_negative_temp():
    # -4.5 -> HDD = max(0, 15.5 - (-4.5)) = 20.0
    assert average_heating_degree_days([-4.5]) == pytest.approx(20.0)


def test_weather_multiplier_boundary_exactly_at_threshold():
    # temp = 7.5 -> HDD = 15.5 - 7.5 = 8.0; 8.0 is NOT strictly > 8.0 -> returns 1.0
    assert weather_sensitivity_multiplier([7.5]) == pytest.approx(1.0)


def test_weather_multiplier_just_above_threshold():
    # temp = 7.4 -> HDD = 15.5 - 7.4 = 8.1 > 8.0 -> applies multiplier
    assert weather_sensitivity_multiplier([7.4]) == pytest.approx(COLD_SPELL_PRICE_MULTIPLIER)


def test_weather_multiplier_very_cold_list():
    # temps = [-10.0] -> HDD = 25.5, well above threshold
    assert weather_sensitivity_multiplier([-10.0]) == pytest.approx(COLD_SPELL_PRICE_MULTIPLIER)


def test_weather_avg_hdd_known_mix():
    # temps [15.5, 10.5, 5.5] -> HDD [0, 5, 10] -> mean = 5.0
    assert average_heating_degree_days([15.5, 10.5, 5.5]) == pytest.approx(5.0)
