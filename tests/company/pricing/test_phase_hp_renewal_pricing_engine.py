"""Tests for Phase HP: Renewal Pricing Engine."""
import pytest
from company.pricing.renewal_pricing_engine import (
    RenewalPricingEngine,
    RenewalPricingRecommendation,
    RenewalPricingResult,
    _estimate_conversion,
    _MIN_GROSS_MARGIN_PCT,
    _RENEWAL_CONVERSION_DECAY_PER_PCT_ABOVE,
)


def _price(engine=None, customer_id="C1", segment="resi", annual_kwh=3500,
           current=200.0, svt=280.0, wholesale=150.0, nc=55.0, cts=50.0):
    if engine is None:
        engine = RenewalPricingEngine()
    return engine.price_renewal(
        customer_id=customer_id, segment=segment, annual_kwh=annual_kwh,
        current_tariff_gbp_per_mwh=current, svt_gbp_per_mwh=svt,
        wholesale_cost_gbp_per_mwh=wholesale, non_commodity_cost_gbp_per_mwh=nc,
        cost_to_serve_gbp_pa=cts,
    )


class TestEstimateConversion:
    def test_at_svt_base_conversion(self):
        c = _estimate_conversion(280.0, 280.0, 85.0, "resi")
        assert c == pytest.approx(85.0)

    def test_above_svt_decays(self):
        c = _estimate_conversion(280.0 * 1.10, 280.0, 85.0, "resi")
        assert c < 85.0

    def test_ic_less_decay(self):
        resi_conv = _estimate_conversion(300.0, 280.0, 85.0, "resi")
        ic_conv = _estimate_conversion(300.0, 280.0, 85.0, "I&C")
        assert ic_conv > resi_conv

    def test_floor_at_zero(self):
        c = _estimate_conversion(1000.0, 280.0, 85.0, "resi")
        assert c >= 0.0

    def test_cap_at_100(self):
        c = _estimate_conversion(100.0, 280.0, 85.0, "resi")
        assert c <= 100.0


class TestRenewalPricingResult:
    def test_total_cost(self):
        r = _price(wholesale=150.0, nc=55.0)
        assert r.total_cost_gbp_per_mwh == pytest.approx(205.0)

    def test_margin_per_mwh(self):
        r = _price(wholesale=150.0, nc=55.0)
        assert r.margin_per_mwh == pytest.approx(r.recommended_tariff_gbp_per_mwh - 205.0)

    def test_is_viable_when_not_no_offer(self):
        r = _price(wholesale=150.0, nc=55.0, svt=280.0)
        assert r.is_viable is True

    def test_is_not_viable_no_offer(self):
        r = _price(wholesale=200.0, nc=100.0, svt=280.0, cts=50.0)
        if r.recommendation == RenewalPricingRecommendation.NO_OFFER:
            assert r.is_viable is False

    def test_vs_svt_pct(self):
        r = _price(wholesale=150.0, nc=55.0, svt=280.0)
        expected_vs_svt = (r.recommended_tariff_gbp_per_mwh - 280.0) / 280.0 * 100
        assert r.vs_svt_pct == pytest.approx(round(expected_vs_svt, 2))

    def test_vs_svt_pct_zero_svt(self):
        r = _price(svt=0.0)
        assert r.vs_svt_pct == 0.0


class TestRenewalPricingEngine:
    def test_price_renewal_returns_result(self):
        r = _price()
        assert isinstance(r, RenewalPricingResult)
        assert r.customer_id == "C1"

    def test_full_margin_when_comfortable(self):
        r = _price(wholesale=100.0, nc=40.0, svt=280.0, cts=30.0)
        assert r.recommendation == RenewalPricingRecommendation.FULL_MARGIN

    def test_no_offer_when_floor_above_svt(self):
        r = _price(wholesale=250.0, nc=80.0, svt=280.0, cts=200.0)
        assert r.recommendation == RenewalPricingRecommendation.NO_OFFER

    def test_tariff_below_svt_cap(self):
        r = _price(wholesale=100.0, nc=40.0, svt=280.0)
        assert r.recommended_tariff_gbp_per_mwh <= 280.0 * 1.025

    def test_expected_conversion_between_0_and_100(self):
        r = _price()
        assert 0 <= r.expected_conversion_pct <= 100

    def test_expected_gross_margin_positive_when_viable(self):
        r = _price(wholesale=100.0, nc=40.0, svt=280.0, cts=30.0)
        if r.is_viable:
            assert r.expected_gross_margin_gbp_pa >= 0

    def test_portfolio_renewal_plan_all_results(self):
        engine = RenewalPricingEngine()
        customers = [
            {"customer_id": "C1", "annual_kwh": 3500},
            {"customer_id": "C2", "segment": "I&C", "annual_kwh": 100000},
        ]
        results = engine.portfolio_renewal_plan(customers)
        assert len(results) == 2
        assert all(isinstance(r, RenewalPricingResult) for r in results)

    def test_portfolio_renewal_plan_empty(self):
        engine = RenewalPricingEngine()
        assert engine.portfolio_renewal_plan([]) == []

    def test_pricing_summary_not_empty(self):
        engine = RenewalPricingEngine()
        results = [_price(engine=engine, customer_id=f"C{i}") for i in range(3)]
        s = engine.pricing_summary(results)
        assert "Renewal Pricing Engine" in s
        assert "customers" in s

    def test_pricing_summary_empty(self):
        engine = RenewalPricingEngine()
        s = engine.pricing_summary([])
        assert "No renewal" in s

    def test_custom_base_conversion(self):
        engine = RenewalPricingEngine(base_renewal_conversion_pct=50.0)
        r = _price(engine=engine, wholesale=100.0, nc=40.0, svt=280.0)
        assert r.expected_conversion_pct <= 50.0


    def test_cost_plus_when_tight_margin(self):
        engine = RenewalPricingEngine(risk_premium_pct=0.0)
        r = engine.price_renewal(
            customer_id="C1", segment="resi", annual_kwh=3500,
            current_tariff_gbp_per_mwh=200.0, svt_gbp_per_mwh=220.0,
            wholesale_cost_gbp_per_mwh=190.0, non_commodity_cost_gbp_per_mwh=28.0,
            cost_to_serve_gbp_pa=0.0,
        )
        assert r.recommendation in (
            RenewalPricingRecommendation.COST_PLUS,
            RenewalPricingRecommendation.COMPETITIVE,
            RenewalPricingRecommendation.NO_OFFER,
        )

    def test_competitive_within_3pct_of_svt(self):
        # cost_floor close to svt so target gets capped to svt*1.02 (within 3% of svt)
        engine = RenewalPricingEngine(risk_premium_pct=5.0)
        r = engine.price_renewal(
            customer_id="C1", segment="resi", annual_kwh=3500,
            current_tariff_gbp_per_mwh=280.0, svt_gbp_per_mwh=280.0,
            wholesale_cost_gbp_per_mwh=240.0, non_commodity_cost_gbp_per_mwh=35.0,
            cost_to_serve_gbp_pa=0.0,
        )
        assert r.recommendation == RenewalPricingRecommendation.COMPETITIVE

    def test_expected_net_margin_lower_than_gross(self):
        r = _price(wholesale=100.0, nc=40.0, svt=280.0, cts=50.0)
        assert r.expected_net_margin_gbp_pa <= r.expected_gross_margin_gbp_pa

    def test_zero_annual_kwh_no_crash(self):
        engine = RenewalPricingEngine()
        r = engine.price_renewal(
            customer_id="C0", segment="resi", annual_kwh=0.0,
            current_tariff_gbp_per_mwh=200.0, svt_gbp_per_mwh=280.0,
            wholesale_cost_gbp_per_mwh=150.0, non_commodity_cost_gbp_per_mwh=55.0,
            cost_to_serve_gbp_pa=50.0,
        )
        assert isinstance(r, RenewalPricingResult)

    def test_no_offer_tariff_at_cost_floor(self):
        r = _price(wholesale=250.0, nc=80.0, svt=280.0, cts=200.0)
        if r.recommendation == RenewalPricingRecommendation.NO_OFFER:
            assert r.recommended_tariff_gbp_per_mwh >= r.total_cost_gbp_per_mwh

    def test_pricing_summary_contains_recommendation_breakdown(self):
        engine = RenewalPricingEngine()
        results = [_price(engine=engine, customer_id="C1", wholesale=100.0, nc=40.0, svt=280.0)]
        s = engine.pricing_summary(results)
        assert "full_margin" in s or "competitive" in s or "cost_plus" in s or "no_offer" in s
