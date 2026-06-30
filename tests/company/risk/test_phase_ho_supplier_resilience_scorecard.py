"""Tests for Phase HO: Supplier Resilience Scorecard."""
import pytest
from company.risk.supplier_resilience_scorecard import (
    PillarRAG,
    PillarScore,
    ResiliencePillar,
    SupplierResilienceScorecard,
    _BAD_DEBT_AMBER_PCT,
    _HEDGE_GREEN_PCT,
    _LIQUIDITY_GREEN_MONTHS,
)


def _green_scorecard():
    sc = SupplierResilienceScorecard()
    sc.assess_liquidity(1_200_000, 90_000)
    sc.assess_hedge_coverage(80.0)
    sc.assess_credit_quality(5_000, 600_000)
    sc.assess_concentration(80_000, 600_000)
    sc.assess_stress_resilience(200_000, 210_000)
    return sc


class TestPillarScore:
    def test_score_value_green(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_hedge_coverage(80.0)
        assert s.score_value == 3

    def test_score_value_amber(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_hedge_coverage(55.0)
        assert s.score_value == 2

    def test_score_value_red(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_hedge_coverage(10.0)
        assert s.score_value == 1


class TestLiquidity:
    def test_green_above_12months(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_liquidity(1_200_000, 90_000)
        assert s.rag == PillarRAG.GREEN

    def test_amber_6_to_12_months(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_liquidity(600_000, 90_000)
        assert s.rag == PillarRAG.AMBER

    def test_red_below_6_months(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_liquidity(200_000, 90_000)
        assert s.rag == PillarRAG.RED

    def test_zero_cost_green(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_liquidity(100_000, 0)
        assert s.rag == PillarRAG.GREEN


class TestHedgeCoverage:
    def test_green(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_hedge_coverage(75.0)
        assert s.rag == PillarRAG.GREEN
        assert s.pillar == ResiliencePillar.HEDGE_COVERAGE

    def test_amber(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_hedge_coverage(55.0)
        assert s.rag == PillarRAG.AMBER

    def test_red(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_hedge_coverage(30.0)
        assert s.rag == PillarRAG.RED


class TestCreditQuality:
    def test_green(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_credit_quality(5_000, 600_000)
        assert s.rag == PillarRAG.GREEN

    def test_amber(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_credit_quality(12_000, 600_000)
        assert s.rag == PillarRAG.AMBER

    def test_red(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_credit_quality(20_000, 600_000)
        assert s.rag == PillarRAG.RED

    def test_zero_revenue(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_credit_quality(0, 0)
        assert s.value == pytest.approx(0.0)
        assert s.rag == PillarRAG.GREEN


class TestConcentration:
    def test_green(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_concentration(100_000, 600_000)
        assert s.rag == PillarRAG.GREEN

    def test_amber(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_concentration(150_000, 600_000)
        assert s.rag == PillarRAG.AMBER

    def test_red(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_concentration(250_000, 600_000)
        assert s.rag == PillarRAG.RED


class TestStressResilience:
    def test_green_survives(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_stress_resilience(200_000, 210_000)
        assert s.rag == PillarRAG.GREEN

    def test_amber_partial(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_stress_resilience(200_000, 120_000)
        assert s.rag == PillarRAG.AMBER

    def test_red_fails(self):
        sc = SupplierResilienceScorecard()
        s = sc.assess_stress_resilience(200_000, 50_000)
        assert s.rag == PillarRAG.RED


class TestScorecardAggregate:
    def test_overall_rag_green(self):
        sc = _green_scorecard()
        assert sc.overall_rag == PillarRAG.GREEN

    def test_overall_rag_red_when_any_red(self):
        sc = SupplierResilienceScorecard()
        sc.assess_hedge_coverage(10.0)
        sc.assess_credit_quality(5_000, 600_000)
        assert sc.overall_rag == PillarRAG.RED

    def test_overall_rag_red_when_empty(self):
        sc = SupplierResilienceScorecard()
        assert sc.overall_rag == PillarRAG.RED

    def test_composite_score_all_green(self):
        sc = _green_scorecard()
        assert sc.composite_score == pytest.approx(3.0)

    def test_composite_score_empty(self):
        sc = SupplierResilienceScorecard()
        assert sc.composite_score == 0.0

    def test_red_pillars(self):
        sc = SupplierResilienceScorecard()
        sc.assess_hedge_coverage(10.0)
        sc.assess_liquidity(1_200_000, 90_000)
        reds = sc.red_pillars()
        assert len(reds) == 1
        assert reds[0].pillar == ResiliencePillar.HEDGE_COVERAGE

    def test_scores_returns_all(self):
        sc = _green_scorecard()
        assert len(sc.scores) == 5

    def test_scorecard_summary_not_empty(self):
        sc = _green_scorecard()
        s = sc.scorecard_summary()
        assert "Resilience" in s
        assert "GREEN" in s

