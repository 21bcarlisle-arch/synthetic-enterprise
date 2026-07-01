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


# --- Phase MN depth tests ---

def test_account_id_stored():
    s = make_score()
    assert s.account_id == 'C1'


def test_scored_at_stored():
    s = make_score()
    assert s.scored_at == DATE


def test_scorecard_tier_count():
    from company.crm.customer_profitability_scorecard import ScorecardTier
    assert len(list(ScorecardTier)) == 5


def test_tier_gold():
    # margin=25, tenure=12.5, clv=12.5, service=12.5 → 62.5 GOLD
    s = CustomerProfitabilityScore(
        account_id='C1', scored_at=DATE,
        annual_margin_gbp=150.0, tenure_years=2.5,
        h3_clv_gbp=250.0, cost_to_serve_gbp=250.0, annual_revenue_gbp=500.0,
    )
    assert s.tier == ScorecardTier.GOLD


def test_tier_silver():
    # margin=12.5, tenure=10, clv=7.5, service=15 → 45 SILVER
    s = CustomerProfitabilityScore(
        account_id='C1', scored_at=DATE,
        annual_margin_gbp=75.0, tenure_years=2.0,
        h3_clv_gbp=150.0, cost_to_serve_gbp=200.0, annual_revenue_gbp=500.0,
    )
    assert s.tier == ScorecardTier.SILVER


def test_tier_bronze():
    # margin=10, tenure=7.5, clv=5, service=2.5 → 25 BRONZE
    s = CustomerProfitabilityScore(
        account_id='C1', scored_at=DATE,
        annual_margin_gbp=60.0, tenure_years=1.5,
        h3_clv_gbp=100.0, cost_to_serve_gbp=450.0, annual_revenue_gbp=500.0,
    )
    assert s.tier == ScorecardTier.BRONZE


def test_max_retention_budget_gold():
    from company.crm.customer_profitability_scorecard import _GOLD_RETENTION_BUDGET_GBP
    s = CustomerProfitabilityScore(
        account_id='C1', scored_at=DATE,
        annual_margin_gbp=150.0, tenure_years=2.5,
        h3_clv_gbp=250.0, cost_to_serve_gbp=250.0, annual_revenue_gbp=500.0,
    )
    assert s.tier == ScorecardTier.GOLD
    assert s.max_retention_budget_gbp == pytest.approx(_GOLD_RETENTION_BUDGET_GBP)


def test_service_efficiency_zero_revenue():
    s = make_score(c2s=100.0, rev=0.0)
    assert s.service_efficiency_score == pytest.approx(0.0)


def test_clv_score_half_target():
    s = make_score(clv=_TARGET_CLV_GBP / 2)
    assert s.clv_score == pytest.approx(12.5)


def test_tenure_score_partial():
    s = make_score(tenure=2.5)
    assert s.tenure_score == pytest.approx(12.5)
