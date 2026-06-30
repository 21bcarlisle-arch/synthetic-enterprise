"""Tests for Customer Segment Profitability Analysis (Phase ES)."""
import datetime as dt
import pytest
from company.finance.segment_profitability import (
    CustomerSegment, SegmentStrategy, SegmentProfitabilitySnapshot,
    SegmentProfitabilityBook,
)

DATE = dt.date(2024, 1, 15)


def make_snap(seg=CustomerSegment.DOMESTIC, n=1000, rev=500_000.0, cost=450_000.0,
              cac=50_000.0, churn=15.0, clv=300.0, date=DATE):
    return SegmentProfitabilitySnapshot(
        segment=seg, as_of=date, customer_count=n,
        total_annual_revenue_gbp=rev, total_annual_cost_gbp=cost,
        total_cac_spend_gbp=cac, avg_churn_rate_pct=churn, avg_clv_gbp=clv,
    )


class TestSegmentProfitabilitySnapshot:
    def test_total_annual_margin(self):
        s = make_snap(rev=500_000, cost=450_000)
        assert s.total_annual_margin_gbp == pytest.approx(50_000.0)

    def test_margin_pct(self):
        s = make_snap(rev=500_000, cost=450_000)
        assert s.margin_pct == pytest.approx(10.0)

    def test_margin_pct_zero_revenue(self):
        s = make_snap(rev=0, cost=0)
        assert s.margin_pct == 0.0

    def test_revenue_per_customer(self):
        s = make_snap(n=1000, rev=500_000)
        assert s.revenue_per_customer_gbp == pytest.approx(500.0)

    def test_margin_per_customer(self):
        s = make_snap(n=1000, rev=500_000, cost=450_000)
        assert s.margin_per_customer_gbp == pytest.approx(50.0)

    def test_strategy_exit_negative_margin(self):
        s = make_snap(rev=400_000, cost=500_000, clv=300.0, churn=15.0)
        assert s.strategy == SegmentStrategy.EXIT

    def test_strategy_exit_low_clv(self):
        s = make_snap(rev=500_000, cost=450_000, clv=30.0, churn=15.0)
        assert s.strategy == SegmentStrategy.EXIT

    def test_strategy_harvest_high_churn(self):
        s = make_snap(rev=500_000, cost=450_000, clv=300.0, churn=35.0)
        assert s.strategy == SegmentStrategy.HARVEST

    def test_strategy_harvest_low_margin_pct(self):
        s = make_snap(rev=500_000, cost=486_000, clv=300.0, churn=15.0)
        assert s.margin_pct < 3.0
        assert s.strategy == SegmentStrategy.HARVEST

    def test_strategy_grow(self):
        s = make_snap(rev=500_000, cost=400_000, clv=600.0, churn=10.0)
        assert s.strategy == SegmentStrategy.GROW

    def test_strategy_maintain(self):
        s = make_snap(rev=500_000, cost=450_000, clv=300.0, churn=15.0)
        assert s.strategy == SegmentStrategy.MAINTAIN

    def test_segment_summary(self):
        s = make_snap()
        summary = s.segment_summary()
        assert "domestic" in summary
        assert "strategy=" in summary


class TestSegmentProfitabilityBook:
    def test_record_and_latest(self):
        book = SegmentProfitabilityBook()
        book.record(make_snap())
        snap = book.latest_for(CustomerSegment.DOMESTIC)
        assert snap is not None

    def test_latest_returns_most_recent(self):
        book = SegmentProfitabilityBook()
        book.record(make_snap(date=dt.date(2024, 1, 1)))
        book.record(make_snap(date=dt.date(2024, 6, 1)))
        snap = book.latest_for(CustomerSegment.DOMESTIC)
        assert snap.as_of == dt.date(2024, 6, 1)

    def test_grow_segments(self):
        book = SegmentProfitabilityBook()
        book.record(make_snap(rev=500_000, cost=400_000, clv=600.0, churn=10.0))
        assert len(book.grow_segments()) == 1

    def test_exit_segments(self):
        book = SegmentProfitabilityBook()
        book.record(make_snap(rev=400_000, cost=500_000, clv=300.0))
        assert len(book.exit_segments()) == 1

    def test_total_portfolio_margin(self):
        book = SegmentProfitabilityBook()
        book.record(make_snap(seg=CustomerSegment.DOMESTIC, rev=500_000, cost=450_000))
        book.record(make_snap(seg=CustomerSegment.SME, rev=200_000, cost=180_000))
        total = book.total_portfolio_margin_gbp()
        assert total == pytest.approx(70_000.0)

    def test_portfolio_segment_summary(self):
        book = SegmentProfitabilityBook()
        book.record(make_snap())
        s = book.portfolio_segment_summary(DATE)
        assert "Segment Profitability" in s
