import pytest
from company.crm.channel_roi import (
    AcquisitionChannel, ChannelROIResult, compute_channel_roi, channel_roi_ranking
)


def test_compute_roi_price_comparison():
    r = compute_channel_roi(AcquisitionChannel.PRICE_COMPARISON, 120.0, 0.30)
    assert r.channel == AcquisitionChannel.PRICE_COMPARISON
    assert r.avg_cac_gbp == 65.0
    assert r.effective_churn_pct > r.base_churn_pct


def test_compute_roi_direct_web_lower_churn():
    r_pcw = compute_channel_roi(AcquisitionChannel.PRICE_COMPARISON, 120.0, 0.30)
    r_web = compute_channel_roi(AcquisitionChannel.DIRECT_WEB, 120.0, 0.30)
    assert r_web.effective_churn_pct < r_pcw.effective_churn_pct


def test_roi_is_profitable_flag():
    r = compute_channel_roi(AcquisitionChannel.EXISTING_CUSTOMER_REFERRAL, 200.0, 0.20)
    assert r.is_profitable


def test_roi_unprofitable_high_churn():
    r = compute_channel_roi(AcquisitionChannel.PRICE_COMPARISON, 30.0, 0.80)
    assert not r.is_profitable


def test_outbound_retention_lower_cac():
    r = compute_channel_roi(AcquisitionChannel.OUTBOUND_RETENTION, 150.0, 0.20)
    assert r.avg_cac_gbp == 12.0


def test_channel_roi_ranking_order():
    ranking = channel_roi_ranking(150.0, 0.25)
    assert len(ranking) == len(AcquisitionChannel)
    for i in range(len(ranking) - 1):
        assert ranking[i].roi_ratio >= ranking[i + 1].roi_ratio


def test_ranking_best_channel_is_not_pcw():
    ranking = channel_roi_ranking(150.0, 0.25)
    best = ranking[0]
    assert best.channel != AcquisitionChannel.PRICE_COMPARISON


def test_expected_tenure_from_churn():
    r = compute_channel_roi(AcquisitionChannel.DIRECT_WEB, 100.0, 0.25)
    effective = r.effective_churn_pct
    assert abs(r.expected_tenure_years - 1.0 / effective) < 0.01


def test_smart_meter_lowest_cac():
    r = compute_channel_roi(AcquisitionChannel.SMART_METER_INSTALL, 100.0, 0.20)
    assert r.avg_cac_gbp == 15.0
