import pytest
from company.risk.stress_test import (
    StressScenario, StressAssumption, StressResult, StressTestBook,
)


def make_book():
    return StressTestBook(credit_facility_gbp=5_000_000.0)


def test_stress_result_is_frozen():
    book = make_book()
    r = book.run_stress(StressScenario.MARKET_SPIKE, 3_000_000, 100_000)
    with pytest.raises((AttributeError, TypeError)):
        r.survives = True  # type: ignore


def test_survives_true_when_treasury_positive():
    book = make_book()
    r = book.run_stress(StressScenario.MARKET_SPIKE, 10_000_000, 50_000, weekly_burn_gbp=10_000)
    assert r.survives is True
    assert r.stressed_treasury_gbp > 0


def test_survives_false_when_treasury_negative():
    book = make_book()
    r = book.run_stress(StressScenario.COMBINED_CRISIS, 500_000, 200_000, weekly_burn_gbp=80_000)
    assert r.survives is False
    assert r.stressed_treasury_gbp < 0


def test_drawdown_pct_correct():
    book = make_book()
    r = book.run_stress(StressScenario.MARKET_SPIKE, 2_000_000, 50_000, weekly_burn_gbp=20_000)
    expected = (r.treasury_drawdown_gbp / 2_000_000) * 100.0
    assert abs(r.drawdown_pct - expected) < 0.001


def test_drawdown_pct_zero_treasury():
    book = make_book()
    assumption = StressAssumption.default_for(StressScenario.CREDIT_DEFAULT)
    assumption2 = StressAssumption(
        scenario=StressScenario.CREDIT_DEFAULT,
        price_multiplier_elec=1.0, price_multiplier_gas=1.0,
        demand_uplift_pct=0.0, margin_call_gbp=0.0,
        counterparty_default_gbp=0.0, duration_weeks=1,
    )
    r = book.run_stress(StressScenario.CREDIT_DEFAULT, 0.0, 0.0, weekly_burn_gbp=0.0, assumption=assumption2)
    assert r.drawdown_pct == 0.0


def test_severity_rag_green_small_drawdown():
    book = make_book()
    r = book.run_stress(StressScenario.MARKET_SPIKE, 100_000_000, 100_000, weekly_burn_gbp=5_000)
    assert r.severity_rag == "GREEN"
    assert r.drawdown_pct < 10.0


def test_severity_rag_red_when_fails():
    book = make_book()
    r = book.run_stress(StressScenario.COMBINED_CRISIS, 100_000, 50_000, weekly_burn_gbp=50_000)
    assert r.severity_rag == "RED"
    assert not r.survives


def test_is_severe_below_250k():
    book = make_book()
    r = book.run_stress(StressScenario.COMBINED_CRISIS, 100_000, 50_000, weekly_burn_gbp=50_000)
    assert r.is_severe is True


def test_combined_crisis_higher_drawdown_than_market_spike():
    book = make_book()
    treasury = 5_000_000
    var = 200_000
    burn = 40_000
    r_market = book.run_stress(StressScenario.MARKET_SPIKE, treasury, var, burn)
    r_combined = book.run_stress(StressScenario.COMBINED_CRISIS, treasury, var, burn)
    assert r_combined.treasury_drawdown_gbp > r_market.treasury_drawdown_gbp


def test_margin_calls_triggered_reflects_assumption():
    book = make_book()
    r = book.run_stress(StressScenario.LIQUIDITY_CRISIS, 3_000_000, 100_000)
    assert r.margin_calls_triggered_gbp == 500_000.0


def test_worst_case_returns_highest_drawdown():
    book = make_book()
    book.run_stress(StressScenario.MARKET_SPIKE, 2_000_000, 80_000, weekly_burn_gbp=20_000)
    book.run_stress(StressScenario.CREDIT_DEFAULT, 2_000_000, 80_000, weekly_burn_gbp=20_000)
    book.run_stress(StressScenario.COMBINED_CRISIS, 2_000_000, 80_000, weekly_burn_gbp=20_000)
    worst = book.worst_case()
    assert worst is not None
    assert worst.scenario == StressScenario.COMBINED_CRISIS


def test_worst_case_empty_book():
    book = make_book()
    assert book.worst_case() is None


def test_scenarios_survived_and_failed():
    book = make_book()
    book.run_stress(StressScenario.MARKET_SPIKE, 20_000_000, 50_000, weekly_burn_gbp=5_000)
    book.run_stress(StressScenario.COMBINED_CRISIS, 50_000, 50_000, weekly_burn_gbp=50_000)
    survived = [s.value for s in book.scenarios_survived()]
    failed = [s.value for s in book.scenarios_failed()]
    assert "market_spike" in survived
    assert "combined_crisis" in failed


def test_probability_weighted_loss():
    book = make_book()
    r1 = book.run_stress(StressScenario.MARKET_SPIKE, 2_000_000, 100_000, 30_000)
    r2 = book.run_stress(StressScenario.CREDIT_DEFAULT, 2_000_000, 100_000, 30_000)
    probs = {StressScenario.MARKET_SPIKE: 0.3, StressScenario.CREDIT_DEFAULT: 0.1}
    expected = r1.treasury_drawdown_gbp * 0.3 + r2.treasury_drawdown_gbp * 0.1
    result = book.probability_weighted_loss_gbp(probs)
    assert abs(result - expected) < 0.01


def test_stress_summary_keys():
    book = make_book()
    book.run_stress(StressScenario.MARKET_SPIKE, 3_000_000, 100_000)
    s = book.stress_summary()
    required = {
        "total_runs", "scenarios_run", "scenarios_survived",
        "scenarios_failed", "worst_case_scenario", "worst_case_drawdown_gbp",
        "worst_case_rag", "red_count", "credit_facility_gbp",
    }
    assert required.issubset(s.keys())


def test_stress_summary_empty_book():
    book = make_book()
    s = book.stress_summary()
    assert s["total_runs"] == 0
    assert s["worst_case_scenario"] is None


def test_results_for_scenario_filters_correctly():
    book = make_book()
    book.run_stress(StressScenario.MARKET_SPIKE, 2_000_000, 50_000)
    book.run_stress(StressScenario.CREDIT_DEFAULT, 2_000_000, 50_000)
    book.run_stress(StressScenario.MARKET_SPIKE, 2_000_000, 50_000)
    results = book.results_for_scenario(StressScenario.MARKET_SPIKE)
    assert len(results) == 2
    assert all(r.scenario == StressScenario.MARKET_SPIKE for r in results)


def test_peak_var_reflects_price_factor():
    book = make_book()
    var = 100_000.0
    r = book.run_stress(StressScenario.MARKET_SPIKE, 5_000_000, var, 20_000)
    elec = 5.0
    gas = 4.0
    expected_var = var * ((elec + gas) / 2.0)
    assert abs(r.peak_var_gbp - expected_var) < 0.01


def test_weeks_to_cash_concern_none_when_surviving():
    book = make_book()
    r = book.run_stress(StressScenario.MARKET_SPIKE, 50_000_000, 50_000, 10_000)
    assert r.weeks_to_cash_concern is None


def test_weeks_to_cash_concern_set_when_failing():
    book = make_book()
    r = book.run_stress(StressScenario.COMBINED_CRISIS, 100_000, 50_000, 80_000)
    assert not r.survives
    assert r.weeks_to_cash_concern is not None
    assert isinstance(r.weeks_to_cash_concern, int)
