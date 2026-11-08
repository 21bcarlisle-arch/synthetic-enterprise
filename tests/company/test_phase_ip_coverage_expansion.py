"""Phase IP: deeper coverage for credit_scoring, switching_report, channel_roi."""
import datetime as dt
import pytest


# ===== channel_roi =====
from company.crm.channel_roi import (
    compute_channel_roi, channel_roi_ranking, AcquisitionChannel
)


class TestChannelROI:
    def test_effective_churn_multiplied_by_factor(self):
        r = compute_channel_roi(AcquisitionChannel.PRICE_COMPARISON, 150.0, 0.1)
        # churn_factor=1.45 → effective=0.1*1.45=0.145
        assert r.effective_churn_pct == pytest.approx(0.145)

    def test_expected_tenure_years(self):
        r = compute_channel_roi(AcquisitionChannel.DIRECT_WEB, 150.0, 0.1)
        # factor=0.85 → effective=0.085 → tenure=1/0.085≈11.76
        assert r.expected_tenure_years == pytest.approx(1/0.085, abs=0.1)

    def test_is_profitable_when_roi_above_1(self):
        # High margin, low CAC channel should be profitable
        r = compute_channel_roi(AcquisitionChannel.SMART_METER_INSTALL, 300.0, 0.1)
        assert r.is_profitable

    def test_price_comparison_highest_churn_factor(self):
        r = compute_channel_roi(AcquisitionChannel.PRICE_COMPARISON, 150.0, 0.10)
        r2 = compute_channel_roi(AcquisitionChannel.DIRECT_WEB, 150.0, 0.10)
        assert r.effective_churn_pct > r2.effective_churn_pct

    def test_referral_low_churn_factor(self):
        r = compute_channel_roi(AcquisitionChannel.EXISTING_CUSTOMER_REFERRAL, 150.0, 0.10)
        # factor=0.65 → effective=0.065
        assert r.effective_churn_pct == pytest.approx(0.065)

    def test_roi_ratio_positive_when_profitable_margin(self):
        r = compute_channel_roi(AcquisitionChannel.OUTBOUND_RETENTION, 100.0, 0.15)
        assert r.roi_ratio > 0

    def test_channel_roi_ranking_sorted_descending(self):
        ranking = channel_roi_ranking(200.0, 0.10)
        ratios = [r.roi_ratio for r in ranking]
        assert ratios == sorted(ratios, reverse=True)

    def test_channel_roi_ranking_all_channels(self):
        ranking = channel_roi_ranking(150.0, 0.10)
        assert len(ranking) == len(AcquisitionChannel)

    def test_cac_from_lookup(self):
        r = compute_channel_roi(AcquisitionChannel.TELESALES, 200.0, 0.10)
        assert r.avg_cac_gbp == pytest.approx(90.0)

    def test_smart_meter_lowest_cac(self):
        r = compute_channel_roi(AcquisitionChannel.SMART_METER_INSTALL, 200.0, 0.10)
        r2 = compute_channel_roi(AcquisitionChannel.TELESALES, 200.0, 0.10)
        assert r.avg_cac_gbp < r2.avg_cac_gbp
