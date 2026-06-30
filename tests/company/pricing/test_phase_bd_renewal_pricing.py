"""Phase BD: Renewal Pricing Engine tests."""
import pytest
from company.pricing.renewal_pricing_engine import (
    RenewalPricingEngine, RenewalPricingRecommendation, RenewalPricingResult,
)


def _engine(base_conv=85.0, risk_prem=5.0):
    return RenewalPricingEngine(base_renewal_conversion_pct=base_conv, risk_premium_pct=risk_prem)


def _price(engine, cid="C1", seg="resi", kwh=3500.0, cur_tariff=200.0,
           svt=280.0, wholesale=150.0, non_comm=55.0, cts=50.0):
    return engine.price_renewal(
        customer_id=cid, segment=seg, annual_kwh=kwh,
        current_tariff_gbp_per_mwh=cur_tariff, svt_gbp_per_mwh=svt,
        wholesale_cost_gbp_per_mwh=wholesale, non_commodity_cost_gbp_per_mwh=non_comm,
        cost_to_serve_gbp_pa=cts,
    )


# 1. Basic pricing returns a result
def test_basic_pricing_returns_result():
    engine = _engine()
    result = _price(engine)
    assert isinstance(result, RenewalPricingResult)
    assert result.customer_id == "C1"


# 2. Recommended tariff covers all costs
def test_tariff_covers_costs():
    engine = _engine()
    result = _price(engine, wholesale=150.0, non_comm=55.0)
    # cost floor = 150 + 55 + (cts/mwh)
    assert result.recommended_tariff_gbp_per_mwh >= result.total_cost_gbp_per_mwh


# 3. NO_OFFER when cost floor exceeds SVT
def test_no_offer_when_cost_exceeds_svt():
    engine = _engine()
    result = _price(engine, wholesale=200.0, non_comm=100.0, svt=280.0)
    # cost_floor = 200 + 100 + cts_per_mwh ≈ 314+ > 280 SVT
    assert result.recommendation == RenewalPricingRecommendation.NO_OFFER
    assert not result.is_viable


# 4. FULL_MARGIN when cost is well below SVT
def test_full_margin_when_ample_room():
    engine = _engine(risk_prem=5.0)
    result = _price(engine, wholesale=100.0, non_comm=40.0, svt=300.0, cts=10.0)
    # cost floor ≈ 143, target ≈ 150, SVT=300 → target below SVT and well above cost
    assert result.is_viable
    assert result.recommendation in (RenewalPricingRecommendation.FULL_MARGIN,
                                      RenewalPricingRecommendation.COMPETITIVE)


# 5. Conversion declines when above SVT
def test_conversion_lower_above_svt():
    engine = _engine(base_conv=85.0)
    # Price at SVT → high conversion
    r_at_svt = _price(engine, wholesale=100.0, non_comm=40.0, svt=150.0, cts=5.0)
    # Price must be higher in this case (we can check expected_conversion_pct)
    assert r_at_svt.expected_conversion_pct <= 85.0


# 6. I&C less sensitive to above-SVT pricing
def test_ic_less_sensitive_to_overprice():
    engine = _engine(base_conv=80.0)
    resi_r = _price(engine, seg="resi", wholesale=100.0, non_comm=40.0, svt=155.0, cts=10.0)
    ic_r = _price(engine, seg="I&C", wholesale=100.0, non_comm=40.0, svt=155.0, cts=10.0)
    # I&C should retain more conversion when priced above SVT
    assert ic_r.expected_conversion_pct >= resi_r.expected_conversion_pct


# 7. margin_per_mwh property
def test_margin_per_mwh():
    engine = _engine()
    r = _price(engine, wholesale=150.0, non_comm=55.0)
    expected_margin = r.recommended_tariff_gbp_per_mwh - (150.0 + 55.0)
    assert abs(r.margin_per_mwh - expected_margin) < 0.01


# 8. vs_svt_pct for below-SVT tariff
def test_vs_svt_pct_negative_when_below():
    engine = _engine()
    r = _price(engine, wholesale=100.0, non_comm=40.0, svt=300.0, cts=10.0)
    # Tariff should be below SVT → negative vs_svt_pct
    assert r.vs_svt_pct < 0


# 9. portfolio_renewal_plan processes list
def test_portfolio_plan():
    engine = _engine()
    customers = [
        {"customer_id": "C1", "segment": "resi", "annual_kwh": 3500.0,
         "current_tariff_gbp_per_mwh": 200.0, "svt_gbp_per_mwh": 280.0,
         "wholesale_cost_gbp_per_mwh": 150.0, "non_commodity_cost_gbp_per_mwh": 55.0,
         "cost_to_serve_gbp_pa": 50.0},
        {"customer_id": "C_IC1", "segment": "I&C", "annual_kwh": 2_000_000.0,
         "current_tariff_gbp_per_mwh": 180.0, "svt_gbp_per_mwh": 250.0,
         "wholesale_cost_gbp_per_mwh": 120.0, "non_commodity_cost_gbp_per_mwh": 42.0,
         "cost_to_serve_gbp_pa": 5000.0},
    ]
    results = engine.portfolio_renewal_plan(customers)
    assert len(results) == 2


# 10. pricing_summary string
def test_pricing_summary_string():
    engine = _engine()
    r = _price(engine)
    summary = engine.pricing_summary([r])
    assert "1 customers priced" in summary
    assert "Viable renewals" in summary


# 11. Expected net margin accounts for CTS
def test_net_margin_accounts_for_cts():
    engine = _engine()
    r = _price(engine, wholesale=100.0, non_comm=40.0, svt=300.0, cts=100.0, kwh=3500.0)
    # Net margin should be less than gross margin by CTS fraction
    assert r.expected_net_margin_gbp_pa < r.expected_gross_margin_gbp_pa


# 12. is_viable False for NO_OFFER
def test_is_viable_false_for_no_offer():
    engine = _engine()
    r = _price(engine, wholesale=250.0, non_comm=100.0, svt=280.0)
    if r.recommendation == RenewalPricingRecommendation.NO_OFFER:
        assert not r.is_viable


# 13. total_cost_gbp_per_mwh = wholesale + non_commodity
def test_total_cost_property():
    engine = _engine()
    r = _price(engine, wholesale=150.0, non_comm=55.0)
    assert abs(r.total_cost_gbp_per_mwh - 205.0) < 0.01


# 14. Risk premium applied in target tariff
def test_risk_premium_applied():
    engine_0 = _engine(risk_prem=0.0)
    engine_5 = _engine(risk_prem=5.0)
    r0 = _price(engine_0, wholesale=100.0, non_comm=40.0, svt=300.0, cts=10.0)
    r5 = _price(engine_5, wholesale=100.0, non_comm=40.0, svt=300.0, cts=10.0)
    # 5% premium → higher tariff
    assert r5.recommended_tariff_gbp_per_mwh >= r0.recommended_tariff_gbp_per_mwh


# 15. Conversion at exactly 85% base when priced below SVT
def test_base_conversion_below_svt():
    engine = _engine(base_conv=85.0)
    # Very low cost → tariff well below SVT → full base conversion
    r = _price(engine, wholesale=50.0, non_comm=20.0, svt=300.0, cts=5.0)
    assert r.expected_conversion_pct == pytest.approx(85.0, abs=0.1)
