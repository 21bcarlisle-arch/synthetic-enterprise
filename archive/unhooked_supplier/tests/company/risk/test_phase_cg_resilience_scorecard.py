"""Phase CG: Supplier Resilience Scorecard tests."""
import pytest
from company.risk.supplier_resilience_scorecard import (
    SupplierResilienceScorecard, PillarRAG, ResiliencePillar
)


def _green_scorecard():
    sc = SupplierResilienceScorecard()
    sc.assess_liquidity(cash_gbp=6_000_000, monthly_supply_cost_gbp=400_000)  # 15 months GREEN
    sc.assess_hedge_coverage(hedge_fraction_pct=80.0)                          # GREEN
    sc.assess_credit_quality(bad_debt_gbp=10_000, revenue_gbp=1_500_000)      # 0.67% GREEN
    sc.assess_concentration(max_single_customer_revenue_gbp=200_000, total_revenue_gbp=1_500_000)  # 13.3% GREEN
    sc.assess_stress_resilience(net_margin_gbp=500_000, stressed_net_margin_gbp=600_000)           # 1.2x GREEN
    return sc


# 1. All-green scorecard overall RAG is GREEN
def test_all_green():
    sc = _green_scorecard()
    assert sc.overall_rag == PillarRAG.GREEN


# 2. Any RED pillar makes overall RED
def test_one_red_makes_overall_red():
    sc = SupplierResilienceScorecard()
    sc.assess_hedge_coverage(30.0)  # RED (below 40%)
    assert sc.overall_rag == PillarRAG.RED


# 3. Liquidity: 6 months = AMBER
def test_liquidity_amber():
    sc = SupplierResilienceScorecard()
    score = sc.assess_liquidity(cash_gbp=600_000, monthly_supply_cost_gbp=100_000)  # 6 months
    assert score.rag == PillarRAG.AMBER


# 4. Liquidity: 3 months = RED
def test_liquidity_red():
    sc = SupplierResilienceScorecard()
    score = sc.assess_liquidity(cash_gbp=300_000, monthly_supply_cost_gbp=100_000)  # 3 months
    assert score.rag == PillarRAG.RED


# 5. Hedge coverage 45% = AMBER
def test_hedge_amber():
    sc = SupplierResilienceScorecard()
    score = sc.assess_hedge_coverage(45.0)
    assert score.rag == PillarRAG.AMBER


# 6. Bad debt 3% = RED
def test_bad_debt_red():
    sc = SupplierResilienceScorecard()
    score = sc.assess_credit_quality(bad_debt_gbp=30_000, revenue_gbp=1_000_000)  # 3%
    assert score.rag == PillarRAG.RED


# 7. Concentration 30% = AMBER
def test_concentration_amber():
    sc = SupplierResilienceScorecard()
    score = sc.assess_concentration(300_000, 1_000_000)
    assert score.rag == PillarRAG.AMBER


# 8. Stress resilience negative = RED
def test_stress_resilience_red():
    sc = SupplierResilienceScorecard()
    score = sc.assess_stress_resilience(500_000, -100_000)  # stressed = negative
    assert score.rag == PillarRAG.RED


# 9. Composite score all-green = 3.0
def test_composite_score_all_green():
    sc = _green_scorecard()
    assert abs(sc.composite_score - 3.0) < 0.01


# 10. red_pillars returns RED pillars only
def test_red_pillars():
    sc = SupplierResilienceScorecard()
    sc.assess_hedge_coverage(30.0)  # RED
    sc.assess_liquidity(cash_gbp=6_000_000, monthly_supply_cost_gbp=300_000)  # GREEN
    red = sc.red_pillars()
    assert len(red) == 1
    assert red[0].pillar == ResiliencePillar.HEDGE_COVERAGE


# 11. scorecard_summary contains pillar names
def test_scorecard_summary():
    sc = _green_scorecard()
    summary = sc.scorecard_summary()
    assert "Liquidity" in summary
    assert "Composite score" in summary
    assert "Overall RAG" in summary


# 12. score_value mapping: GREEN=3, AMBER=2, RED=1
def test_score_values():
    sc = SupplierResilienceScorecard()
    g = sc.assess_hedge_coverage(80.0)   # GREEN
    sc2 = SupplierResilienceScorecard()
    a = sc2.assess_hedge_coverage(50.0)  # AMBER
    sc3 = SupplierResilienceScorecard()
    r = sc3.assess_hedge_coverage(20.0)  # RED
    assert g.score_value == 3
    assert a.score_value == 2
    assert r.score_value == 1


# --- Phase MD depth tests ---

def test_pillar_stored():
    sc = SupplierResilienceScorecard()
    score = sc.assess_liquidity(6_000_000, 400_000)
    assert score.pillar == ResiliencePillar.LIQUIDITY


def test_rag_stored():
    sc = SupplierResilienceScorecard()
    score = sc.assess_liquidity(6_000_000, 400_000)
    assert score.rag == PillarRAG.GREEN


def test_value_stored():
    sc = SupplierResilienceScorecard()
    score = sc.assess_liquidity(6_000_000, 400_000)
    assert score.value == pytest.approx(15.0)


def test_threshold_green_stored():
    sc = SupplierResilienceScorecard()
    score = sc.assess_liquidity(6_000_000, 400_000)
    assert score.threshold_green == pytest.approx(12.0)


def test_threshold_amber_stored():
    sc = SupplierResilienceScorecard()
    score = sc.assess_liquidity(6_000_000, 400_000)
    assert score.threshold_amber == pytest.approx(6.0)


def test_description_non_empty():
    sc = SupplierResilienceScorecard()
    score = sc.assess_liquidity(6_000_000, 400_000)
    assert len(score.description) > 0


def test_score_value_green_equals_3():
    sc = SupplierResilienceScorecard()
    score = sc.assess_liquidity(6_000_000, 400_000)
    assert score.score_value == 3


def test_score_value_amber_equals_2():
    sc = SupplierResilienceScorecard()
    score = sc.assess_liquidity(3_000_000, 400_000)
    assert score.rag == PillarRAG.AMBER
    assert score.score_value == 2


def test_resilience_pillar_has_5_members():
    assert len(list(ResiliencePillar)) == 5


def test_assess_liquidity_returns_pillar_score():
    from company.risk.supplier_resilience_scorecard import PillarScore
    sc = SupplierResilienceScorecard()
    result = sc.assess_liquidity(6_000_000, 400_000)
    assert isinstance(result, PillarScore)
