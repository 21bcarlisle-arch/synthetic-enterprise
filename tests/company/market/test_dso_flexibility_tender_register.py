import datetime as dt
import pytest
from company.market.dso_flexibility_tender_register import (
    DSOFlexibilityTenderRegister, FlexibilityService, TenderStatus, BidStatus,
)

START = dt.date(2022, 6, 1)
END = dt.date(2023, 5, 31)


def _reg():
    r = DSOFlexibilityTenderRegister()
    r.create_tender("UK Power Networks", FlexibilityService.PEAK_AVOIDANCE, "GSP-EAST", START, END, 5.0)
    return r


def test_tender_id_prefix():
    reg = _reg()
    assert reg._tenders[0].tender_id.startswith("DSO-TEN-")


def test_status_default_open():
    reg = _reg()
    assert reg._tenders[0].status == TenderStatus.OPEN


def test_zero_capacity_raises():
    reg = DSOFlexibilityTenderRegister()
    with pytest.raises(ValueError):
        reg.create_tender("UK PN", FlexibilityService.VOLTAGE_SUPPORT, "GSP-X", START, END, 0.0)


def test_end_before_start_raises():
    reg = DSOFlexibilityTenderRegister()
    with pytest.raises(ValueError):
        reg.create_tender("UK PN", FlexibilityService.VOLTAGE_SUPPORT, "GSP-X", END, START, 5.0)


def test_submit_bid_id_prefix():
    reg = _reg()
    tid = reg._tenders[0].tender_id
    bid = reg.submit_bid(tid, 2.5, 1000.0)
    assert bid.bid_id.startswith("DSO-BID-")


def test_accept_bid_sets_capacity():
    reg = _reg()
    tid = reg._tenders[0].tender_id
    bid = reg.submit_bid(tid, 3.0, 900.0)
    updated = reg.accept_bid(bid.bid_id, 2.0)
    assert updated.awarded_capacity_mw == 2.0
    assert updated.status == BidStatus.ACCEPTED


def test_annual_revenue_for_accepted_bid():
    reg = _reg()
    tid = reg._tenders[0].tender_id
    bid = reg.submit_bid(tid, 3.0, 1000.0)
    accepted = reg.accept_bid(bid.bid_id, 2.0)
    assert accepted.annual_revenue_gbp == 2000.0


def test_close_then_award():
    reg = _reg()
    tid = reg._tenders[0].tender_id
    reg.close_tender(tid)
    updated = reg.award_tender(tid, 1200.0, dt.date(2022, 6, 15))
    assert updated.status == TenderStatus.AWARDED
    assert updated.clearing_price_gbp_per_mw == 1200.0


def test_cannot_bid_on_closed_tender():
    reg = _reg()
    tid = reg._tenders[0].tender_id
    reg.close_tender(tid)
    with pytest.raises(ValueError):
        reg.submit_bid(tid, 1.0, 500.0)


def test_total_contracted_capacity_sums_accepted():
    reg = _reg()
    tid = reg._tenders[0].tender_id
    bid = reg.submit_bid(tid, 3.0, 900.0)
    reg.accept_bid(bid.bid_id, 2.0)
    assert reg.total_contracted_capacity_mw == 2.0
