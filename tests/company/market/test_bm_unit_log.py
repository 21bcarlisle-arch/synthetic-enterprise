import datetime as dt
import pytest
from company.market.bm_unit_log import (
    BMActionType, BMDispatchStatus, BMOffer, BMDispatch, BMUnitLog
)


SUBMIT_T = dt.datetime(2022, 1, 3, 9, 0)
DISPATCH_T = dt.datetime(2022, 1, 3, 11, 0)
SETTLE_DATE = dt.date(2022, 1, 3)


def _make_log() -> BMUnitLog:
    return BMUnitLog('BM-FLEX-001', 50.0)


def test_offered_mwh():
    log = _make_log()
    offer = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 10.0, 200.0, SUBMIT_T)
    assert offer.offered_mwh == pytest.approx(5.0)


def test_is_expensive():
    log = _make_log()
    cheap = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 10.0, 200.0, SUBMIT_T)
    pricy = log.submit_offer(SETTLE_DATE, 23, BMActionType.OFFER, 10.0, 600.0, SUBMIT_T)
    assert not cheap.is_expensive
    assert pricy.is_expensive


def test_full_dispatch_status():
    log = _make_log()
    offer = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 10.0, 200.0, SUBMIT_T)
    d = log.record_dispatch(offer, 10.0, DISPATCH_T)
    assert d.status == BMDispatchStatus.DISPATCHED


def test_part_dispatch_status():
    log = _make_log()
    offer = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 10.0, 200.0, SUBMIT_T)
    d = log.record_dispatch(offer, 5.0, DISPATCH_T)
    assert d.status == BMDispatchStatus.PART_DISPATCHED


def test_dispatch_revenue():
    log = _make_log()
    offer = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 10.0, 200.0, SUBMIT_T)
    d = log.record_dispatch(offer, 10.0, DISPATCH_T)
    assert d.revenue_gbp == pytest.approx(5.0 * 200.0)


def test_utilisation_pct():
    log = _make_log()
    offer = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 20.0, 150.0, SUBMIT_T)
    d = log.record_dispatch(offer, 15.0, DISPATCH_T)
    assert d.utilisation_pct == pytest.approx(75.0)


def test_total_revenue():
    log = _make_log()
    for sp in [22, 23, 24]:
        offer = log.submit_offer(SETTLE_DATE, sp, BMActionType.OFFER, 10.0, 200.0, SUBMIT_T)
        log.record_dispatch(offer, 10.0, DISPATCH_T)
    assert log.total_revenue_gbp(2022) == pytest.approx(3 * 5.0 * 200.0)


def test_avg_dispatch_price():
    log = _make_log()
    for price in [100.0, 200.0, 300.0]:
        offer = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 10.0, price, SUBMIT_T)
        log.record_dispatch(offer, 10.0, DISPATCH_T)
    avg = log.avg_dispatch_price(2022)
    assert avg == pytest.approx(200.0)


def test_bm_summary():
    log = _make_log()
    offer = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 10.0, 200.0, SUBMIT_T)
    log.record_dispatch(offer, 10.0, DISPATCH_T)
    s = log.bm_summary(2022)
    assert s['dispatches'] == 1
    assert s['total_revenue_gbp'] == pytest.approx(5.0 * 200.0)


def test_avg_dispatch_price_none_when_no_dispatches():
    log = _make_log()
    assert log.avg_dispatch_price(2022) is None


def test_total_revenue_year_filter():
    log = _make_log()
    # Dispatch in 2021
    offer_2021 = log.submit_offer(dt.date(2021, 12, 1), 22, BMActionType.OFFER, 10.0, 200.0, SUBMIT_T)
    log.record_dispatch(offer_2021, 10.0, DISPATCH_T)
    # Dispatch in 2022
    offer_2022 = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 10.0, 300.0, SUBMIT_T)
    log.record_dispatch(offer_2022, 10.0, DISPATCH_T)
    assert log.total_revenue_gbp(2022) == pytest.approx(5.0 * 300.0)
    assert log.total_revenue_gbp(2021) == pytest.approx(5.0 * 200.0)


def test_dispatch_count_year_filter():
    log = _make_log()
    offer_2021 = log.submit_offer(dt.date(2021, 6, 1), 10, BMActionType.OFFER, 10.0, 100.0, SUBMIT_T)
    log.record_dispatch(offer_2021, 10.0, DISPATCH_T)
    offer_2022 = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 10.0, 200.0, SUBMIT_T)
    log.record_dispatch(offer_2022, 10.0, DISPATCH_T)
    assert log.dispatch_count(2022) == 1
    assert log.dispatch_count(2021) == 1


def test_is_expensive_at_exactly_500():
    log = _make_log()
    offer = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 10.0, 500.0, SUBMIT_T)
    assert not offer.is_expensive  # > 500, not >= 500


def test_utilisation_pct_zero_when_no_offered():
    offer = BMOffer('BM001', SETTLE_DATE, 22, BMActionType.OFFER, 0.0, 200.0, SUBMIT_T)
    d = BMDispatch(offer, 0.0, DISPATCH_T)
    assert d.utilisation_pct == pytest.approx(0.0)


def test_dispatched_mwh_property():
    log = _make_log()
    offer = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 20.0, 200.0, SUBMIT_T)
    d = log.record_dispatch(offer, 20.0, DISPATCH_T)
    assert d.dispatched_mwh == pytest.approx(10.0)


def test_bm_summary_bmu_id():
    log = _make_log()
    s = log.bm_summary(2022)
    assert s['bmu_id'] == 'BM-FLEX-001'


def test_bm_summary_offers_submitted():
    log = _make_log()
    log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 10.0, 200.0, SUBMIT_T)
    log.submit_offer(SETTLE_DATE, 23, BMActionType.BID, 5.0, 150.0, SUBMIT_T)
    s = log.bm_summary(2022)
    assert s['offers_submitted'] == 2


def test_part_dispatch_boundary():
    log = _make_log()
    offer = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 100.0, 200.0, SUBMIT_T)
    # 98.9% < 99% threshold → PART_DISPATCHED
    d = log.record_dispatch(offer, 98.9, DISPATCH_T)
    assert d.status == BMDispatchStatus.PART_DISPATCHED


def test_revenue_is_dispatched_mwh_times_price():
    log = _make_log()
    offer = log.submit_offer(SETTLE_DATE, 22, BMActionType.OFFER, 8.0, 250.0, SUBMIT_T)
    d = log.record_dispatch(offer, 8.0, DISPATCH_T)
    # dispatched_mwh = 8 * 0.5 = 4.0; revenue = 4.0 * 250 = 1000.0
    assert d.revenue_gbp == pytest.approx(1000.0)
