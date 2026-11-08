"""Phase CK: Liquidity Stress Test Book tests."""
import pytest
from company.risk.liquidity_stress_test import (
    LiquidityStressTestBook, StressScenario,
    StressTestResult, LiquidityStressOutcome
)


def _healthy_book() -> LiquidityStressTestBook:
    """Supplier with £5M cash, £500k/day revenue, manageable IM."""
    return LiquidityStressTestBook(
        starting_cash_gbp=5_000_000,
        daily_operating_cost_gbp=3_000,
        normal_daily_vm_gbp=1_000,
        annual_retail_revenue_gbp=10_000_000,
        total_im_posted_gbp=200_000,
    )


def _tight_book() -> LiquidityStressTestBook:
    """Supplier with minimal cash reserves."""
    return LiquidityStressTestBook(
        starting_cash_gbp=100_000,
        daily_operating_cost_gbp=5_000,
        normal_daily_vm_gbp=10_000,
        annual_retail_revenue_gbp=2_000_000,
        total_im_posted_gbp=500_000,
    )


# 1. Mild scenario returns SOLVENT for healthy book
def test_mild_scenario_solvent():
    book = _healthy_book()
    result = book.run_scenario(StressScenario("mild", 20, 5, 50))
    assert result.outcome == LiquidityStressOutcome.SOLVENT


# 2. Severe 2022 scenario drives tight book insolvent
def test_severe_insolvent():
    book = _tight_book()
    result = book.run_scenario(StressScenario("severe_2022", 200, 15, 200))
    assert result.outcome == LiquidityStressOutcome.INSOLVENT


# 3. Ending cash decreases with higher price shock
def test_higher_shock_lower_cash():
    book = _healthy_book()
    mild = book.run_scenario(StressScenario("mild", 20, 5, 50))
    severe = book.run_scenario(StressScenario("severe", 200, 5, 200))
    assert severe.ending_cash_gbp < mild.ending_cash_gbp


# 4. total_cash_drain includes VM + IM
def test_total_drain_includes_both():
    book = _tight_book()
    result = book.run_scenario(StressScenario("test", 50, 0, 100))
    assert result.total_cash_drain_gbp > 0
    assert result.vm_drain_gbp > 0
    assert result.im_additional_call_gbp > 0


# 5. survival_days proportional to ending cash
def test_survival_days_positive():
    book = _healthy_book()
    result = book.run_scenario(StressScenario("mild", 20, 5, 50))
    assert result.survival_days > 0


# 6. headroom_pct negative when insolvent
def test_headroom_pct_negative():
    book = _tight_book()
    result = book.run_scenario(StressScenario("extreme", 200, 0, 200))
    assert result.headroom_pct < 0


# 7. standard_scenarios returns 3 results
def test_standard_scenarios_count():
    book = _healthy_book()
    results = book.standard_scenarios()
    assert len(results) == 3


# 8. standard_scenarios escalates: mild < moderate < severe
def test_standard_scenarios_escalate():
    book = _tight_book()
    results = book.standard_scenarios()
    cashes = [r.ending_cash_gbp for r in results]
    assert cashes[0] > cashes[1] > cashes[2]


# 9. worst_outcome returns most severe
def test_worst_outcome():
    book = _tight_book()
    book.standard_scenarios()
    worst = book.worst_outcome
    assert worst.scenario.name == "severe_2022"


# 10. is_severe flag for extreme scenarios
def test_is_severe_flag():
    mild = StressScenario("mild", 20, 5, 50)
    severe = StressScenario("severe", 50, 5, 150)
    assert not mild.is_severe
    assert severe.is_severe


# 11. all_results accumulates across runs
def test_all_results_accumulates():
    book = _healthy_book()
    book.run_scenario(StressScenario("s1", 10, 0, 20))
    book.run_scenario(StressScenario("s2", 20, 0, 40))
    assert len(book.all_results) == 2


# 12. stress_summary contains key fields
def test_stress_summary():
    book = _tight_book()
    book.standard_scenarios()
    summary = book.stress_summary()
    assert "Liquidity Stress" in summary
    assert "severe_2022" in summary
    assert "Insolvent" in summary or "insolvent" in summary


# --- Phase MD depth tests ---

def test_scenario_name_stored():
    s = StressScenario('Test', 20.0, 10.0, 50.0)
    assert s.name == 'Test'


def test_price_shock_stored():
    s = StressScenario('Test', 30.0, 10.0, 100.0)
    assert s.wholesale_price_shock_pct == pytest.approx(30.0)


def test_volume_shock_stored():
    s = StressScenario('Test', 20.0, 15.0, 50.0)
    assert s.volume_shock_pct == pytest.approx(15.0)


def test_im_shock_stored():
    s = StressScenario('Test', 20.0, 10.0, 200.0)
    assert s.initial_margin_shock_pct == pytest.approx(200.0)


def test_stress_days_default_30():
    s = StressScenario('Test', 20.0, 10.0, 50.0)
    assert s.stress_days == 30


def test_is_severe_false_low_shock():
    s = StressScenario('mild', 20.0, 5.0, 50.0)
    assert s.is_severe is False


def test_is_severe_true_high_price_shock():
    s = StressScenario('severe', 60.0, 5.0, 50.0)
    assert s.is_severe is True


def test_starting_cash_stored():
    book = _healthy_book()
    result = book.run_scenario(StressScenario('mild', 20, 5, 50))
    assert result.starting_cash_gbp == pytest.approx(5_000_000)


def test_total_drain_is_sum():
    book = _healthy_book()
    result = book.run_scenario(StressScenario('mild', 20, 5, 50))
    expected = result.vm_drain_gbp + result.im_additional_call_gbp
    assert result.total_cash_drain_gbp == pytest.approx(expected)


def test_run_scenario_returns_stress_test_result():
    book = _healthy_book()
    result = book.run_scenario(StressScenario('mild', 20, 5, 50))
    assert isinstance(result, StressTestResult)
