"""Phase CM: Market Share Estimator tests."""
import pytest
from company.market.market_share_estimator import (
    MarketShareEstimator, MarketSegment, SegmentShareEstimate, MarketShareSnapshot
)


def _estimator_with_2022() -> MarketShareEstimator:
    e = MarketShareEstimator()
    e.record_year(2022, {
        MarketSegment.DOMESTIC: 9,        # small resi portfolio
        MarketSegment.SME: 0,
        MarketSegment.INDUSTRIAL_COMMERCIAL: 4,  # 4 I&C accounts
    })
    return e


def _two_year_estimator() -> MarketShareEstimator:
    e = MarketShareEstimator()
    e.record_year(2021, {MarketSegment.INDUSTRIAL_COMMERCIAL: 2})
    e.record_year(2022, {MarketSegment.INDUSTRIAL_COMMERCIAL: 4})
    return e


# 1. Market share calculation correct for I&C (28k market, 4 accounts)
def test_ic_share_pct():
    e = _estimator_with_2022()
    snap = e.snapshot_for_year(2022)
    ic = snap.estimate_for_segment(MarketSegment.INDUSTRIAL_COMMERCIAL)
    # 4 / 28,000 * 100 ≈ 0.01429%
    assert abs(ic.market_share_pct - 4/28000*100) < 0.0001


# 2. Blended share includes all segments
def test_blended_share_all_segments():
    e = _estimator_with_2022()
    snap = e.snapshot_for_year(2022)
    # total_own = 9+0+4=13; total_uk ~29M+1.7M+28k
    assert snap.blended_share_pct > 0
    assert snap.blended_share_pct < 0.001   # micro supplier


# 3. is_micro_supplier true for domestic (9 accounts / 29M market = micro)
def test_is_micro_supplier():
    e = _estimator_with_2022()
    snap = e.snapshot_for_year(2022)
    domestic = snap.estimate_for_segment(MarketSegment.DOMESTIC)
    assert domestic.is_micro_supplier


# 4. customers_needed_for_1pct
def test_customers_needed_1pct():
    e = _estimator_with_2022()
    snap = e.snapshot_for_year(2022)
    ic = snap.estimate_for_segment(MarketSegment.INDUSTRIAL_COMMERCIAL)
    # 1% of 28,000 = 280; need 280-4 = 276 more
    assert ic.customers_needed_for_1pct == 276


# 5. total_own_customers sums across segments
def test_total_own_customers():
    e = _estimator_with_2022()
    snap = e.snapshot_for_year(2022)
    assert snap.total_own_customers == 13   # 9+0+4


# 6. largest_segment returns highest share segment
def test_largest_segment():
    e = _estimator_with_2022()
    snap = e.snapshot_for_year(2022)
    # I&C: 4/28k = 0.0143% >> domestic 9/29M = 0.00003%
    assert snap.largest_segment.segment == MarketSegment.INDUSTRIAL_COMMERCIAL


# 7. growth_rate_pct calculates correctly
def test_growth_rate_pct():
    e = _two_year_estimator()
    rate = e.growth_rate_pct(2021, 2022)
    # 2 → 4 customers = 100% growth
    assert abs(rate - 100.0) < 0.01


# 8. growth_rate_pct returns None for missing year
def test_growth_rate_none_missing_year():
    e = _estimator_with_2022()
    rate = e.growth_rate_pct(2020, 2022)
    assert rate is None


# 9. share_trend returns year-keyed dict
def test_share_trend():
    e = _two_year_estimator()
    trend = e.share_trend()
    assert 2021 in trend and 2022 in trend
    assert trend[2022] > trend[2021]   # more customers in 2022


# 10. latest_snapshot returns most recent
def test_latest_snapshot():
    e = _two_year_estimator()
    assert e.latest_snapshot.year == 2022


# 11. market_overrides allow custom market size
def test_market_overrides():
    e = MarketShareEstimator()
    e.record_year(2022, {MarketSegment.INDUSTRIAL_COMMERCIAL: 5},
                  market_overrides={MarketSegment.INDUSTRIAL_COMMERCIAL: 50})
    snap = e.snapshot_for_year(2022)
    ic = snap.estimate_for_segment(MarketSegment.INDUSTRIAL_COMMERCIAL)
    assert abs(ic.market_share_pct - 10.0) < 0.01


# 12. market_summary contains key fields
def test_market_summary():
    e = _estimator_with_2022()
    summary = e.market_summary()
    assert "Market Share" in summary
    assert "2022" in summary
    assert "13" in summary   # total customers
