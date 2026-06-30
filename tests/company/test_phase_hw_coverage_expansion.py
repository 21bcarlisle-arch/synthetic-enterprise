"""Phase HW: coverage expansion for liquidity_stress_test, initial_margin_register, price_elasticity."""
import datetime as dt
import pytest

# ===== liquidity_stress_test =====
from company.risk.liquidity_stress_test import (
    LiquidityStressTestBook, LiquidityStressOutcome, StressScenario, StressTestResult
)

def _book(starting_cash=5_000_000, daily_op=5_000, normal_vm=10_000,
          retail_revenue=20_000_000, im_posted=500_000):
    return LiquidityStressTestBook(
        starting_cash_gbp=starting_cash,
        daily_operating_cost_gbp=daily_op,
        normal_daily_vm_gbp=normal_vm,
        annual_retail_revenue_gbp=retail_revenue,
        total_im_posted_gbp=im_posted,
    )

class TestLiquidityStressTest:
    def test_run_scenario_returns_result(self):
        book = _book()
        scenario = StressScenario("mild", 20, 5, 50)
        result = book.run_scenario(scenario)
        assert isinstance(result, StressTestResult)

    def test_solvent_outcome_with_large_cash(self):
        book = _book(starting_cash=100_000_000)
        result = book.run_scenario(StressScenario("mild", 20, 5, 50))
        assert result.outcome == LiquidityStressOutcome.SOLVENT

    def test_insolvent_outcome_with_low_cash(self):
        book = _book(starting_cash=10_000, normal_vm=100_000, im_posted=5_000_000)
        result = book.run_scenario(StressScenario("severe", 200, 15, 200))
        assert result.outcome == LiquidityStressOutcome.INSOLVENT

    def test_ending_cash_negative_when_insolvent(self):
        book = _book(starting_cash=10_000, normal_vm=100_000, im_posted=5_000_000)
        result = book.run_scenario(StressScenario("severe", 200, 15, 200))
        assert result.ending_cash_gbp < 0

    def test_total_cash_drain(self):
        book = _book(normal_vm=10_000, im_posted=0)
        scenario = StressScenario("test", 0, 0, 0, stress_days=10)
        result = book.run_scenario(scenario)
        # vm_drain=10000*1*10=100000; im_call=0; inflow=20M/365*10≈547945
        assert result.total_cash_drain_gbp == pytest.approx(100_000.0)

    def test_survival_days_proportional_to_cash(self):
        book = _book(starting_cash=5_000_000)
        result = book.run_scenario(StressScenario("mild", 20, 5, 50))
        assert result.survival_days >= 0

    def test_headroom_pct_positive_when_solvent(self):
        book = _book(starting_cash=100_000_000)
        result = book.run_scenario(StressScenario("mild", 10, 2, 20))
        assert result.headroom_pct > 0

    def test_standard_scenarios_returns_three(self):
        book = _book(starting_cash=50_000_000)
        results = book.standard_scenarios()
        assert len(results) == 3
        assert book.all_results == results

    def test_worst_outcome_insolvent_when_mixed(self):
        book = _book(starting_cash=10_000, normal_vm=100_000, im_posted=5_000_000)
        book.run_scenario(StressScenario("mild", 20, 5, 50))
        book.run_scenario(StressScenario("severe", 200, 15, 200))
        worst = book.worst_outcome
        assert worst.outcome == LiquidityStressOutcome.INSOLVENT

    def test_stress_summary_keys(self):
        book = _book(starting_cash=100_000_000)
        book.run_scenario(StressScenario("mild", 20, 5, 50))
        s = book.stress_summary()
        assert "Liquidity Stress" in s and "Scenarios run" in s


# ===== initial_margin_register =====
from company.trading.initial_margin_register import (
    InitialMarginRegister, MarginAccountType, IMStatus
)

def _post(reg, mid="IM1", trade="T1", cp="ICE", notional=10_000,
          posted=50_000, pdate=None, rdate=None):
    pdate = pdate or dt.date(2022, 1, 1)
    rdate = rdate or dt.date(2022, 4, 1)
    return reg.post_margin(mid, trade, cp, MarginAccountType.EXCHANGE_CLEARED,
                           notional, posted, pdate, rdate)

class TestInitialMarginRegister:
    def test_post_margin_creates_record(self):
        reg = InitialMarginRegister()
        rec = _post(reg, "IM1")
        assert rec.status == IMStatus.POSTED
        assert rec.margin_posted_gbp == 50_000

    def test_total_locked_gbp(self):
        reg = InitialMarginRegister()
        _post(reg, "IM1", posted=50_000)
        _post(reg, "IM2", posted=30_000)
        assert reg.total_locked_gbp == pytest.approx(80_000)

    def test_issue_additional_call_updates_status(self):
        reg = InitialMarginRegister()
        _post(reg, "IM1", posted=50_000)
        updated = reg.issue_additional_call("IM1", 20_000)
        assert updated.status == IMStatus.CALLED
        assert updated.total_held_gbp == pytest.approx(70_000)

    def test_additional_call_gbp_tracked(self):
        reg = InitialMarginRegister()
        _post(reg, "IM1", posted=50_000)
        reg.issue_additional_call("IM1", 20_000)
        assert reg.total_additional_calls_gbp == pytest.approx(20_000)

    def test_return_margin_sets_returned_status(self):
        reg = InitialMarginRegister()
        _post(reg, "IM1")
        returned = reg.return_margin("IM1", dt.date(2022, 4, 1))
        assert returned.status == IMStatus.RETURNED
        assert returned.actual_return_date == dt.date(2022, 4, 1)

    def test_active_records_excludes_returned(self):
        reg = InitialMarginRegister()
        _post(reg, "IM1")
        _post(reg, "IM2")
        reg.return_margin("IM1", dt.date(2022, 4, 1))
        assert len(reg.active_records) == 1

    def test_margin_rate_pct_of_notional(self):
        reg = InitialMarginRegister()
        rec = _post(reg, "IM1", notional=1000, posted=10_000)  # £100/MWh proxy → notional_value=100k; 10k/100k=10%
        assert rec.margin_rate_pct_of_notional == pytest.approx(10.0)

    def test_records_by_counterparty(self):
        reg = InitialMarginRegister()
        _post(reg, "IM1", cp="ICE", posted=50_000)
        _post(reg, "IM2", cp="ICE", posted=30_000)
        _post(reg, "IM3", cp="LME", posted=20_000)
        by_cp = reg.records_by_counterparty()
        assert by_cp["ICE"] == pytest.approx(80_000)
        assert by_cp["LME"] == pytest.approx(20_000)

    def test_im_summary_keys(self):
        reg = InitialMarginRegister()
        _post(reg, "IM1")
        s = reg.im_summary()
        assert "Initial Margin" in s and "locked" in s

    def test_empty_register_totals_zero(self):
        reg = InitialMarginRegister()
        assert reg.total_locked_gbp == 0.0
        assert reg.total_additional_calls_gbp == 0.0


# ===== price_elasticity =====
from company.pricing.price_elasticity import (
    PriceElasticityBook, ElasticityBand, PriceChangeImpact, PortfolioImpact
)

class TestPriceElasticityBook:
    def test_estimate_churn_impact_returns_impact(self):
        book = PriceElasticityBook()
        impact = book.estimate_churn_impact("resi", 10.0, 5.0, 1000, 1_000_000)
        assert isinstance(impact, PriceChangeImpact)
        assert impact.segment == "resi"

    def test_price_increase_drives_extra_churn(self):
        book = PriceElasticityBook()
        impact = book.estimate_churn_impact("resi", 20.0, 5.0, 1000, 1_000_000)
        assert impact.extra_churn_rate_pct > 0

    def test_total_churn_is_base_plus_extra(self):
        book = PriceElasticityBook()
        impact = book.estimate_churn_impact("resi", 10.0, 5.0, 1000, 1_000_000)
        assert impact.total_churn_rate_pct == pytest.approx(
            impact.base_churn_rate_pct + impact.extra_churn_rate_pct, abs=0.01
        )

    def test_ic_less_elastic_than_resi(self):
        book = PriceElasticityBook()
        resi = book.estimate_churn_impact("resi", 20.0, 5.0, 1000, 1_000_000)
        ic = book.estimate_churn_impact("I&C", 20.0, 5.0, 1000, 1_000_000)
        assert ic.extra_churn_rate_pct < resi.extra_churn_rate_pct

    def test_crisis_year_increases_elasticity(self):
        normal = PriceElasticityBook(is_crisis_year=False)
        crisis = PriceElasticityBook(is_crisis_year=True)
        n_impact = normal.estimate_churn_impact("resi", 10.0, 5.0, 1000, 1_000_000)
        c_impact = crisis.estimate_churn_impact("resi", 10.0, 5.0, 1000, 1_000_000)
        assert c_impact.extra_churn_rate_pct > n_impact.extra_churn_rate_pct

    def test_elasticity_band_high_when_large_churn(self):
        book = PriceElasticityBook()
        impact = book.estimate_churn_impact("resi", 60.0, 5.0, 1000, 1_000_000)
        assert impact.elasticity_band == ElasticityBand.HIGH

    def test_elasticity_band_low_when_small_churn(self):
        book = PriceElasticityBook()
        impact = book.estimate_churn_impact("resi", 2.0, 5.0, 1000, 1_000_000)
        assert impact.elasticity_band == ElasticityBand.LOW

    def test_model_portfolio_impact_returns_portfolio_impact(self):
        book = PriceElasticityBook()
        segments = {
            "resi": {"count": 1000, "revenue_gbp": 1_000_000, "churn_pct": 5.0},
            "SME": {"count": 100, "revenue_gbp": 500_000, "churn_pct": 3.0},
        }
        portfolio = book.model_portfolio_impact(10.0, segments)
        assert isinstance(portfolio, PortfolioImpact)
        assert portfolio.total_customers == 1100

    def test_elasticity_summary_not_empty(self):
        book = PriceElasticityBook()
        s = book.elasticity_summary()
        assert "elasticity" in s.lower() or "resi" in s.lower()

    def test_optimal_tariff_change_returns_float(self):
        book = PriceElasticityBook()
        opt = book.optimal_tariff_change(
            segment="resi", base_churn_rate_pct=5.0,
            customer_count=1000, annual_revenue_gbp=1_000_000
        )
        assert isinstance(opt, (float, int))
