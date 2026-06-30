"""Phase BA: Price Elasticity Estimator tests."""
import pytest
from company.pricing.price_elasticity import (
    PriceElasticityBook, ElasticityBand, PortfolioImpact,
    _PRICE_ELASTICITY_BY_SEGMENT, _CRISIS_ELASTICITY_MULTIPLIER,
)


def _book(crisis=False):
    return PriceElasticityBook(is_crisis_year=crisis)


def _resi_impact(tariff_change_pct=10.0, base_churn=25.0, count=100, rev=50000.0):
    return _book().estimate_churn_impact("resi", tariff_change_pct, base_churn, count, rev)


# 1. Positive tariff change increases churn
def test_price_increase_increases_churn():
    imp = _resi_impact(tariff_change_pct=10.0, base_churn=25.0)
    assert imp.total_churn_rate_pct > 25.0


# 2. Zero tariff change = base churn only
def test_zero_change_no_extra_churn():
    imp = _resi_impact(tariff_change_pct=0.0, base_churn=25.0)
    assert imp.extra_churn_rate_pct == 0.0
    assert imp.total_churn_rate_pct == 25.0


# 3. I&C less elastic than resi
def test_ic_less_elastic_than_resi():
    book = _book()
    resi_imp = book.estimate_churn_impact("resi", 10.0, 20.0, 10, 100000.0)
    ic_imp = book.estimate_churn_impact("I&C", 10.0, 20.0, 10, 100000.0)
    assert resi_imp.extra_churn_rate_pct > ic_imp.extra_churn_rate_pct


# 4. Crisis year multiplies elasticity
def test_crisis_year_higher_elasticity():
    normal = _book(crisis=False).estimate_churn_impact("resi", 10.0, 25.0, 100, 50000.0)
    crisis = _book(crisis=True).estimate_churn_impact("resi", 10.0, 25.0, 100, 50000.0)
    assert crisis.extra_churn_rate_pct > normal.extra_churn_rate_pct


# 5. Crisis elasticity exactly 1.5× normal
def test_crisis_multiplier_exact():
    normal = _book(crisis=False).estimate_churn_impact("resi", 10.0, 20.0, 100, 50000.0)
    crisis = _book(crisis=True).estimate_churn_impact("resi", 10.0, 20.0, 100, 50000.0)
    ratio = crisis.extra_churn_rate_pct / normal.extra_churn_rate_pct
    assert abs(ratio - _CRISIS_ELASTICITY_MULTIPLIER) < 0.01


# 6. is_viable when retained revenue >= pre-change revenue
def test_viable_small_increase():
    # I&C: low base churn + low elasticity → 3% increase is viable with enough customers
    imp = _book().estimate_churn_impact("I&C", 3.0, 2.0, 200, 1_000_000.0)
    assert imp.is_viable  # I&C: 2% base churn, 200 customers, 3% increase


# 7. Large price spike not viable for resi
def test_large_increase_not_viable_resi():
    imp = _book().estimate_churn_impact("resi", 25.0, 25.0, 100, 50000.0)
    assert not imp.is_viable


# 8. elasticity_band property
def test_elasticity_band_low():
    imp = _book().estimate_churn_impact("I&C", 5.0, 5.0, 10, 500000.0)
    assert imp.elasticity_band == ElasticityBand.LOW


# 9. model_portfolio_impact sums segments
def test_portfolio_impact_sums():
    book = _book()
    segs = {
        "resi": {"churn_pct": 25.0, "count": 80, "revenue_gbp": 40000.0},
        "I&C": {"churn_pct": 8.0, "count": 4, "revenue_gbp": 500000.0},
    }
    port = book.model_portfolio_impact(5.0, segs)
    assert port.total_customers == 84
    assert port.total_retained_revenue_gbp > 0
    assert port.pre_change_revenue_gbp == pytest.approx(540000.0, abs=0.1)


# 10. optimal_tariff_change returns float in search range
def test_optimal_tariff_change_in_range():
    book = _book()
    opt = book.optimal_tariff_change("resi", 25.0, 100, 50000.0)
    assert -10.0 <= opt <= 30.0


# 11. Optimal for I&C allows higher increase
def test_ic_optimal_higher_than_resi():
    book = _book()
    resi_opt = book.optimal_tariff_change("resi", 20.0, 100, 50000.0)
    ic_opt = book.optimal_tariff_change("I&C", 8.0, 4, 1_000_000.0)
    assert ic_opt >= resi_opt


# 12. retention_rate_pct on portfolio
def test_portfolio_retention_rate():
    book = _book()
    segs = {"resi": {"churn_pct": 0.0, "count": 100, "revenue_gbp": 50000.0}}
    port = book.model_portfolio_impact(0.0, segs)
    # zero churn → 100% retention
    assert port.retention_rate_pct == 100.0


# 13. revenue_delta_gbp shows positive for viable change
def test_revenue_delta_positive_for_viable():
    imp = _book().estimate_churn_impact("I&C", 5.0, 5.0, 10, 1_000_000.0)
    if imp.is_viable:
        assert imp.revenue_delta_gbp > 0


# 14. elasticity_summary contains all segments
def test_elasticity_summary_all_segments():
    summary = _book().elasticity_summary()
    for seg in _PRICE_ELASTICITY_BY_SEGMENT:
        assert seg in summary


# 15. Crisis summary note present
def test_crisis_summary_note():
    summary = _book(crisis=True).elasticity_summary()
    assert "CRISIS" in summary
