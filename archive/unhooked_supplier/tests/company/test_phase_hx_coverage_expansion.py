# Increment 3: the legs of tests/company/test_phase_hx_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase HX: coverage expansion for acquisition_strategy_book, dual_fuel_bill, market_share_estimator."""
import datetime as dt
import pytest


# ===== market_share_estimator =====
from company.market.market_share_estimator import (
    MarketShareEstimator, MarketSegment, MarketShareSnapshot
)

class TestMarketShareEstimator:
    def test_record_year_creates_snapshot(self):
        est = MarketShareEstimator()
        snap = est.record_year(2023, {MarketSegment.DOMESTIC: 5000})
        assert isinstance(snap, MarketShareSnapshot)
        assert snap.year == 2023

    def test_total_own_customers(self):
        est = MarketShareEstimator()
        snap = est.record_year(2023, {
            MarketSegment.DOMESTIC: 5000, MarketSegment.SME: 200
        })
        assert snap.total_own_customers == 5200

    def test_blended_share_pct(self):
        est = MarketShareEstimator()
        # Use market_overrides to control denominator; set non-domestic to same as own count (0)
        snap = est.record_year(2023,
            {MarketSegment.DOMESTIC: 29_000},
            market_overrides={
                MarketSegment.DOMESTIC: 2_900_000,
                MarketSegment.SME: 0,
                MarketSegment.INDUSTRIAL_COMMERCIAL: 0,
            })
        # 29k / 2900k = 1.0%
        assert snap.blended_share_pct == pytest.approx(1.0, abs=0.01)

    def test_snapshot_for_year(self):
        est = MarketShareEstimator()
        est.record_year(2022, {MarketSegment.DOMESTIC: 3000})
        est.record_year(2023, {MarketSegment.DOMESTIC: 4000})
        snap = est.snapshot_for_year(2022)
        assert snap.total_own_customers == 3000

    def test_latest_snapshot_most_recent(self):
        est = MarketShareEstimator()
        est.record_year(2022, {MarketSegment.DOMESTIC: 3000})
        est.record_year(2023, {MarketSegment.DOMESTIC: 4000})
        assert est.latest_snapshot.year == 2023

    def test_growth_rate_pct(self):
        est = MarketShareEstimator()
        est.record_year(2022, {MarketSegment.DOMESTIC: 2000})
        est.record_year(2023, {MarketSegment.DOMESTIC: 2500})
        gr = est.growth_rate_pct(2022, 2023)
        assert gr == pytest.approx(25.0, rel=0.01)

    def test_is_micro_supplier(self):
        est = MarketShareEstimator()
        snap = est.record_year(2023, {MarketSegment.DOMESTIC: 100})  # tiny share
        resi = snap.estimate_for_segment(MarketSegment.DOMESTIC)
        assert resi.is_micro_supplier

    def test_largest_segment_by_share(self):
        est = MarketShareEstimator()
        snap = est.record_year(2023, {
            MarketSegment.DOMESTIC: 500,
            MarketSegment.SME: 1000,   # SME market is much smaller → higher share
        })
        assert snap.largest_segment is not None

    def test_share_trend_sorted_by_year(self):
        est = MarketShareEstimator()
        est.record_year(2022, {MarketSegment.DOMESTIC: 2000})
        est.record_year(2023, {MarketSegment.DOMESTIC: 3000})
        trend = est.share_trend()
        assert list(trend.keys()) == [2022, 2023]

    def test_market_summary_keys(self):
        est = MarketShareEstimator()
        est.record_year(2023, {MarketSegment.DOMESTIC: 5000})
        s = est.market_summary()
        assert "Market Share" in s and "customers" in s
