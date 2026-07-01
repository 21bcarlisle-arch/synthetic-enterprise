"""Tests for company/risk/liquidity_stress_test.py (Sprint CLIII)."""
import pytest

from company.risk.liquidity_stress_test import (
    LiquidityStressTestBook,
    LiquidityStressOutcome,
    StressScenario,
)


def _book(cash=5_000_000.0, daily_op=10_000.0, normal_vm=50_000.0,
          annual_revenue=3_000_000.0, total_im=500_000.0):
    return LiquidityStressTestBook(
        starting_cash_gbp=cash,
        daily_operating_cost_gbp=daily_op,
        normal_daily_vm_gbp=normal_vm,
        annual_retail_revenue_gbp=annual_revenue,
        total_im_posted_gbp=total_im,
    )


def test_run_scenario_returns_result():
    book = _book()
    scenario = StressScenario("test", 20.0, 5.0, 50.0, 30)
    result = book.run_scenario(scenario)
    assert result.scenario.name == "test"


def test_starting_cash_in_result():
    book = _book(cash=1_000_000.0)
    result = book.run_scenario(StressScenario("t", 10.0, 0.0, 0.0, 1))
    assert result.starting_cash_gbp == 1_000_000.0


def test_is_severe_above_50pct_shock():
    scenario = StressScenario("severe", 55.0, 10.0, 100.0)
    assert scenario.is_severe is True


def test_not_severe_below_threshold():
    scenario = StressScenario("mild", 20.0, 5.0, 50.0)
    assert scenario.is_severe is False


def test_total_cash_drain_sums():
    book = _book()
    result = book.run_scenario(StressScenario("t", 100.0, 5.0, 200.0, 30))
    assert abs(result.total_cash_drain_gbp - (result.vm_drain_gbp + result.im_additional_call_gbp)) < 0.01


def test_standard_scenarios_returns_three():
    book = _book()
    results = book.standard_scenarios()
    assert len(results) == 3


def test_worst_outcome_not_none_after_run():
    book = _book()
    book.run_scenario(StressScenario("t", 10.0, 0.0, 0.0, 1))
    assert book.worst_outcome is not None


def test_severe_scenario_insolvent_low_cash():
    book = _book(cash=100_000.0, normal_vm=50_000.0, total_im=1_000_000.0)
    result = book.run_scenario(StressScenario("severe", 200.0, 15.0, 200.0, 30))
    assert result.outcome in (LiquidityStressOutcome.CRITICAL, LiquidityStressOutcome.INSOLVENT)


def test_headroom_pct_positive_solvent():
    book = _book(cash=100_000_000.0)
    result = book.run_scenario(StressScenario("mild", 10.0, 0.0, 0.0, 1))
    assert result.headroom_pct > 0.0


def test_survival_days_infinite_when_zero_daily_cost():
    book = _book(daily_op=0.0)
    result = book.run_scenario(StressScenario("t", 10.0, 0.0, 0.0, 1))
    import math
    assert math.isinf(result.survival_days)
