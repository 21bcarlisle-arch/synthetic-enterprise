"""Tests for Portfolio Profitability Dashboard (Phase EG)."""
import datetime as dt
import pytest
from company.finance.portfolio_dashboard import (
    PortfolioHealthStatus, SegmentSummary,
    PortfolioProfitabilitySnapshot,
)


DATE = dt.date(2024, 6, 30)


def make_segment(name="domestic", count=100, margin=20_000.0, churn=15.0):
    return SegmentSummary(
        segment=name,
        customer_count=count,
        total_annual_margin_gbp=margin,
        avg_annual_margin_gbp=margin / count if count else 0,
        churn_rate_pct=churn,
    )


def make_snapshot(segments=None, gri=55.0, resolution=87.0, smart=75.0, hedge=80.0):
    if segments is None:
        segments = (make_segment(),)
    return PortfolioProfitabilitySnapshot(
        snapshot_date=DATE,
        supplier_name="TestEnergy",
        segments=segments,
        gri_score=gri,
        complaint_resolution_pct=resolution,
        smart_meter_pct=smart,
        hedge_fraction_pct=hedge,
    )


class TestSegmentSummary:
    def test_revenue_at_risk(self):
        s = make_segment(margin=100_000.0, churn=20.0)
        assert s.revenue_at_risk_gbp == pytest.approx(20_000.0)

    def test_avg_clv_positive(self):
        s = make_segment(count=1, margin=200.0, churn=18.0)
        assert s.avg_clv_gbp > 0


class TestPortfolioProfitabilitySnapshot:
    def test_total_customers(self):
        snap = make_snapshot(segments=(
            make_segment("domestic", count=80),
            make_segment("sme", count=20),
        ))
        assert snap.total_customers == 100

    def test_total_annual_margin(self):
        snap = make_snapshot(segments=(
            make_segment("domestic", count=80, margin=16_000),
            make_segment("sme", count=20, margin=4_000),
        ))
        assert snap.total_annual_margin_gbp == pytest.approx(20_000.0)

    def test_avg_annual_margin(self):
        snap = make_snapshot(segments=(make_segment(count=100, margin=20_000),))
        assert snap.avg_annual_margin_gbp == pytest.approx(200.0)

    def test_portfolio_churn_weighted(self):
        snap = make_snapshot(segments=(
            make_segment("dom", count=80, churn=15.0),
            make_segment("sme", count=20, churn=10.0),
        ))
        expected = (80 * 15 + 20 * 10) / 100
        assert snap.portfolio_churn_rate_pct == pytest.approx(expected)

    def test_revenue_at_risk(self):
        snap = make_snapshot(segments=(make_segment(margin=100_000, churn=20.0),))
        assert snap.total_revenue_at_risk_gbp == pytest.approx(20_000.0)

    def test_health_strong(self):
        snap = make_snapshot(segments=(make_segment(churn=8.0),), gri=65.0)
        assert snap.health_status == PortfolioHealthStatus.STRONG

    def test_health_critical(self):
        snap = make_snapshot(segments=(make_segment(churn=35.0),), gri=20.0)
        assert snap.health_status == PortfolioHealthStatus.CRITICAL

    def test_segment_lookup(self):
        snap = make_snapshot(segments=(
            make_segment("domestic"),
            make_segment("sme"),
        ))
        assert snap.segment("domestic") is not None
        assert snap.segment("MISSING") is None

    def test_concentration_risk(self):
        snap = make_snapshot(segments=(
            make_segment("dom", margin=80_000),
            make_segment("sme", margin=10_000),
            make_segment("ic", margin=5_000),
            make_segment("x", margin=3_000),
            make_segment("y", margin=2_000),
        ))
        cr = snap.concentration_risk_pct
        assert 0 < cr <= 100

    def test_dashboard_summary(self):
        snap = make_snapshot()
        s = snap.dashboard_summary()
        assert "Portfolio Dashboard" in s
        assert str(DATE.year) in s
