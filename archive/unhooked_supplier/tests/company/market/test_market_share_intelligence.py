"""Tests for Market Share Intelligence (Phase EK)."""
import datetime as dt
import pytest
from company.market.market_share_intelligence import (
    MarketSegment, SupplierTier, MarketShareSnapshot,
    MarketShareIntelligenceBook, _TOTAL_DOMESTIC_SUPPLY_POINTS,
)

DATE1 = dt.date(2023, 3, 31)
DATE2 = dt.date(2023, 6, 30)


def make_snap(own=10000, total=None, prior=None, segment=MarketSegment.DOMESTIC, date=DATE1):
    return MarketShareSnapshot(
        segment=segment,
        period_end=date,
        own_supply_points=own,
        total_market_supply_points=_TOTAL_DOMESTIC_SUPPLY_POINTS if total is None else total,
        prior_period_own=prior,
    )


class TestMarketShareSnapshot:
    def test_market_share_pct(self):
        s = make_snap(own=285000, total=28_500_000)
        assert s.market_share_pct == pytest.approx(1.0, rel=0.001)

    def test_market_share_zero_total(self):
        s = make_snap(own=100, total=0)
        assert s.market_share_pct == 0.0

    def test_above_reporting_floor(self):
        s = make_snap(own=285001, total=28_500_000)
        assert s.is_above_reporting_floor

    def test_below_reporting_floor(self):
        s = make_snap(own=100, total=28_500_000)
        assert not s.is_above_reporting_floor

    def test_tier_big_six(self):
        s = make_snap(own=1_500_000, total=28_500_000)
        assert s.supplier_tier == SupplierTier.BIG_SIX

    def test_tier_challenger(self):
        s = make_snap(own=285000, total=28_500_000)
        assert s.supplier_tier == SupplierTier.CHALLENGER

    def test_tier_micro(self):
        s = make_snap(own=1000, total=28_500_000)
        assert s.supplier_tier == SupplierTier.MICRO

    def test_growth_pct(self):
        s = make_snap(own=11000, prior=10000)
        assert s.period_growth_pct == pytest.approx(10.0)

    def test_growth_pct_none_when_no_prior(self):
        s = make_snap(prior=None)
        assert s.period_growth_pct is None

    def test_hhi_contribution(self):
        s = make_snap(own=285000, total=28_500_000)
        # 1% share -> (1^2)/10000 = 0.0001
        assert s.hhi_contribution == pytest.approx(0.0001, rel=0.01)

    def test_snapshot_summary(self):
        s = make_snap(own=285000, total=28_500_000)
        summary = s.snapshot_summary()
        assert "domestic" in summary
        assert "%" in summary


class TestMarketShareIntelligenceBook:
    def test_record_and_retrieve(self):
        book = MarketShareIntelligenceBook()
        book.record(make_snap())
        assert len(book.snapshots_for(MarketSegment.DOMESTIC)) == 1

    def test_latest_for(self):
        book = MarketShareIntelligenceBook()
        book.record(make_snap(own=10000, date=DATE1))
        book.record(make_snap(own=12000, date=DATE2))
        latest = book.latest_for(MarketSegment.DOMESTIC)
        assert latest.own_supply_points == 12000

    def test_latest_for_none_when_empty(self):
        book = MarketShareIntelligenceBook()
        assert book.latest_for(MarketSegment.DOMESTIC) is None

    def test_share_trend_growing(self):
        book = MarketShareIntelligenceBook()
        # Need >0.05% delta: from 1.0% to 1.1%
        book.record(make_snap(own=285000, date=DATE1))
        book.record(make_snap(own=302000, date=DATE2))
        assert book.share_trend(MarketSegment.DOMESTIC) == "growing"

    def test_share_trend_insufficient(self):
        book = MarketShareIntelligenceBook()
        book.record(make_snap())
        assert book.share_trend(MarketSegment.DOMESTIC) == "insufficient_data"

    def test_current_tier(self):
        book = MarketShareIntelligenceBook()
        book.record(make_snap(own=285000, total=28_500_000))
        assert book.current_tier(MarketSegment.DOMESTIC) == SupplierTier.CHALLENGER

    def test_intelligence_summary_contains_pct(self):
        book = MarketShareIntelligenceBook()
        book.record(make_snap())
        s = book.intelligence_summary(MarketSegment.DOMESTIC)
        assert "Market Intelligence" in s

    def test_intelligence_summary_empty(self):
        book = MarketShareIntelligenceBook()
        s = book.intelligence_summary(MarketSegment.DOMESTIC)
        assert "No market share data" in s
