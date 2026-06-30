"""Tests for Customer Profitability Scorecard (Phase FK)."""
import datetime as dt
import pytest
from company.crm.customer_profitability_scorecard import (
    ScorecardTier, CustomerProfitabilityScore,
    _TARGET_ANNUAL_MARGIN_GBP, _TARGET_CLV_GBP,
)

DATE = dt.date(2024, 6, 1)


def make_score(margin=150.0, tenure=5.0, clv=500.0, c2s=30.0, rev=500.0):
    return CustomerProfitabilityScore(
        account_id="C1", scored_at=DATE,
        annual_margin_gbp=margin, tenure_years=tenure,
        h3_clv_gbp=clv, cost_to_serve_gbp=c2s, annual_revenue_gbp=rev,
    )


class TestCustomerProfitabilityScore:
    def test_margin_score_at_target(self):
        s = make_score(margin=_TARGET_ANNUAL_MARGIN_GBP)
        assert s.margin_score == pytest.approx(25.0)

    def test_margin_score_capped(self):
        s = make_score(margin=_TARGET_ANNUAL_MARGIN_GBP * 2)
        assert s.margin_score == pytest.approx(25.0)

    def test_margin_score_zero(self):
        s = make_score(margin=0.0)
        assert s.margin_score == pytest.approx(0.0)

    def test_tenure_score_at_max(self):
        s = make_score(tenure=5.0)
        assert s.tenure_score == pytest.approx(25.0)

    def test_tenure_score_capped(self):
        s = make_score(tenure=10.0)
        assert s.tenure_score == pytest.approx(25.0)

    def test_clv_score_at_target(self):
        s = make_score(clv=_TARGET_CLV_GBP)
        assert s.clv_score == pytest.approx(25.0)

    def test_service_efficiency_perfect(self):
        s = make_score(c2s=0.0, rev=500.0)
        assert s.service_efficiency_score == pytest.approx(25.0)

    def test_service_efficiency_at_limit(self):
        s = make_score(c2s=500.0, rev=500.0)  # ratio = 1.0
        assert s.service_efficiency_score == pytest.approx(0.0)

    def test_total_score_perfect(self):
        s = make_score(margin=150.0, tenure=5.0, clv=500.0, c2s=0.0, rev=500.0)
        assert s.total_score == pytest.approx(100.0)

    def test_tier_platinum(self):
        s = make_score(margin=150.0, tenure=5.0, clv=500.0, c2s=0.0, rev=500.0)
        assert s.tier == ScorecardTier.PLATINUM

    def test_tier_loss_making(self):
        s = make_score(margin=0.0, tenure=0.0, clv=0.0, c2s=500.0, rev=500.0)
        assert s.tier == ScorecardTier.LOSS_MAKING

    def test_max_retention_budget_platinum(self):
        s = make_score(margin=150.0, tenure=5.0, clv=500.0, c2s=0.0, rev=500.0)
        assert s.max_retention_budget_gbp > 0

    def test_max_retention_budget_bronze(self):
        s = make_score(margin=10.0, tenure=1.0, clv=50.0, c2s=400.0, rev=500.0)
        assert s.max_retention_budget_gbp == 0.0

    def test_scorecard_summary(self):
        s = make_score()
        text = s.scorecard_summary()
        assert "Scorecard" in text
        assert "C1" in text
