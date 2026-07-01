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


# --- Phase JZ depth tests ---

from company.crm.channel_roi import AcquisitionChannel, ChannelAcquisition, _BASE_CAC_GBP


def test_channel_acquisition_avg_cac():
    acq = ChannelAcquisition(AcquisitionChannel.DIRECT_WEB, 2022, 4, 112.0)
    import pytest
    assert acq.avg_cac_gbp == pytest.approx(28.0)


def test_channel_acquisition_avg_cac_zero_customers():
    acq = ChannelAcquisition(AcquisitionChannel.DIRECT_WEB, 2022, 0, 0.0)
    import pytest
    assert acq.avg_cac_gbp == pytest.approx(0.0)


def test_effective_churn_capped_at_1():
    r = compute_channel_roi(AcquisitionChannel.PRICE_COMPARISON, 100.0, 0.90)
    import pytest
    assert r.effective_churn_pct == pytest.approx(1.0)
    assert r.expected_tenure_years == pytest.approx(1.0)


def test_zero_base_churn_gives_tenure_20():
    r = compute_channel_roi(AcquisitionChannel.DIRECT_WEB, 100.0, 0.0)
    import pytest
    assert r.expected_tenure_years == pytest.approx(20.0)


def test_partner_referral_cac():
    r = compute_channel_roi(AcquisitionChannel.PARTNER_REFERRAL, 150.0, 0.25)
    import pytest
    assert r.avg_cac_gbp == pytest.approx(35.0)


def test_telesales_highest_cac():
    r = compute_channel_roi(AcquisitionChannel.TELESALES, 150.0, 0.25)
    import pytest
    assert r.avg_cac_gbp == pytest.approx(90.0)


def test_is_profitable_at_exactly_1():
    import pytest
    from company.crm.channel_roi import ChannelROIResult
    r = ChannelROIResult(
        channel=AcquisitionChannel.DIRECT_WEB,
        avg_cac_gbp=100.0,
        avg_annual_margin_gbp=50.0,
        base_churn_pct=0.25,
        effective_churn_pct=0.25,
        expected_tenure_years=4.0,
        roi_ratio=1.0,
    )
    assert r.is_profitable is True


def test_is_not_profitable_below_1():
    import pytest
    from company.crm.channel_roi import ChannelROIResult
    r = ChannelROIResult(
        channel=AcquisitionChannel.PRICE_COMPARISON,
        avg_cac_gbp=65.0,
        avg_annual_margin_gbp=20.0,
        base_churn_pct=0.80,
        effective_churn_pct=1.0,
        expected_tenure_years=1.0,
        roi_ratio=0.3,
    )
    assert r.is_profitable is False


def test_direct_web_effective_churn_less_than_base():
    r = compute_channel_roi(AcquisitionChannel.DIRECT_WEB, 120.0, 0.30)
    assert r.effective_churn_pct < r.base_churn_pct


def test_existing_referral_lowest_effective_churn():
    base = 0.20
    r_ecr = compute_channel_roi(AcquisitionChannel.EXISTING_CUSTOMER_REFERRAL, 100.0, base)
    r_smi = compute_channel_roi(AcquisitionChannel.SMART_METER_INSTALL, 100.0, base)
    assert r_ecr.effective_churn_pct < r_smi.effective_churn_pct
