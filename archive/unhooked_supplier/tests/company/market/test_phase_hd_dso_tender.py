"""Tests for DSO Flexibility Tender Register -- Phase HD."""
import datetime as dt
import pytest
from company.market.dso_flexibility_tender_register import (
    FlexibilityService, TenderStatus, BidStatus,
    DSOFlexibilityTenderRecord, DSOFlexibilityBid,
    DSOFlexibilityTenderRegister,
)

TODAY = dt.date(2024, 6, 10)
PERIOD_START = dt.date(2024, 10, 1)
PERIOD_END = dt.date(2025, 3, 31)
DNO = "National Grid Electricity Distribution"
GSP = "Exeter GSP"


def make_reg():
    return DSOFlexibilityTenderRegister()


def create_tender(reg=None, dno=DNO, service=FlexibilityService.PEAK_AVOIDANCE,
                  gsp=GSP, start=PERIOD_START, end=PERIOD_END, capacity=5.0):
    if reg is None:
        reg = make_reg()
    return reg, reg.create_tender(dno, service, gsp, start, end, capacity)


class TestDSOFlexibilityTenderRecord:
    def test_is_open_when_open(self):
        _, t = create_tender()
        assert t.is_open

    def test_is_open_when_closed(self):
        reg, t = create_tender()
        reg.close_tender(t.tender_id)
        closed = reg.open_tenders  # should be empty
        assert len(closed) == 0

    def test_is_not_awarded_when_open(self):
        _, t = create_tender()
        assert not t.is_awarded

    def test_is_awarded(self):
        reg, t = create_tender()
        reg.close_tender(t.tender_id)
        reg.award_tender(t.tender_id, 50000.0, TODAY)
        awarded = reg.awarded_tenders
        assert len(awarded) == 1 and awarded[0].is_awarded

    def test_contract_length_days(self):
        _, t = create_tender()
        expected = (PERIOD_END - PERIOD_START).days
        assert t.contract_length_days == expected

    def test_tender_summary_contains_id(self):
        _, t = create_tender()
        assert t.tender_id in t.tender_summary()

    def test_frozen(self):
        _, t = create_tender()
        with pytest.raises((AttributeError, TypeError)):
            t.dno_name = "other"


class TestDSOFlexibilityBid:
    def test_is_not_accepted_when_submitted(self):
        reg, t = create_tender()
        b = reg.submit_bid(t.tender_id, 2.0, 45000.0)
        assert not b.is_accepted

    def test_annual_revenue_zero_when_not_accepted(self):
        reg, t = create_tender()
        b = reg.submit_bid(t.tender_id, 2.0, 45000.0)
        assert b.annual_revenue_gbp == 0.0

    def test_annual_revenue_when_accepted(self):
        reg, t = create_tender()
        b = reg.submit_bid(t.tender_id, 2.0, 45000.0)
        accepted = reg.accept_bid(b.bid_id, 2.0)
        assert abs(accepted.annual_revenue_gbp - 90000.0) < 1e-9

    def test_frozen(self):
        reg, t = create_tender()
        b = reg.submit_bid(t.tender_id, 2.0, 45000.0)
        with pytest.raises((AttributeError, TypeError)):
            b.bid_id = "other"


class TestDSOFlexibilityTenderRegister:
    def setup_method(self):
        self.reg = make_reg()

    def _create(self, dno=DNO, service=FlexibilityService.PEAK_AVOIDANCE,
                gsp=GSP, start=PERIOD_START, end=PERIOD_END, capacity=5.0):
        return self.reg.create_tender(dno, service, gsp, start, end, capacity)

    def test_create_tender_returns_open(self):
        t = self._create()
        assert t.status == TenderStatus.OPEN

    def test_auto_id_prefix(self):
        t = self._create()
        assert t.tender_id.startswith("DSO-TEN-")

    def test_auto_id_increments(self):
        t1 = self._create()
        t2 = self._create(gsp="Bristol GSP")
        assert t1.tender_id != t2.tender_id

    def test_end_before_start_raises(self):
        with pytest.raises(ValueError):
            self._create(start=PERIOD_END, end=PERIOD_START)

    def test_zero_capacity_raises(self):
        with pytest.raises(ValueError):
            self._create(capacity=0.0)

    def test_negative_capacity_raises(self):
        with pytest.raises(ValueError):
            self._create(capacity=-1.0)

    def test_close_tender(self):
        t = self._create()
        closed = self.reg.close_tender(t.tender_id)
        assert closed.status == TenderStatus.CLOSED

    def test_close_non_open_raises(self):
        t = self._create()
        self.reg.close_tender(t.tender_id)
        with pytest.raises(ValueError):
            self.reg.close_tender(t.tender_id)

    def test_award_requires_closed(self):
        t = self._create()
        with pytest.raises(ValueError):
            self.reg.award_tender(t.tender_id, 50000.0, TODAY)

    def test_award_tender(self):
        t = self._create()
        self.reg.close_tender(t.tender_id)
        awarded = self.reg.award_tender(t.tender_id, 50000.0, TODAY)
        assert awarded.status == TenderStatus.AWARDED
        assert awarded.clearing_price_gbp_per_mw == 50000.0

    def test_negative_clearing_price_raises(self):
        t = self._create()
        self.reg.close_tender(t.tender_id)
        with pytest.raises(ValueError):
            self.reg.award_tender(t.tender_id, -1.0, TODAY)

    def test_cancel_tender(self):
        t = self._create()
        cancelled = self.reg.cancel_tender(t.tender_id, "Insufficient bids")
        assert cancelled.status == TenderStatus.CANCELLED
        assert "Insufficient" in cancelled.cancelled_reason

    def test_cancel_awarded_raises(self):
        t = self._create()
        self.reg.close_tender(t.tender_id)
        self.reg.award_tender(t.tender_id, 50000.0, TODAY)
        with pytest.raises(ValueError):
            self.reg.cancel_tender(t.tender_id, "too late")

    def test_submit_bid(self):
        t = self._create()
        b = self.reg.submit_bid(t.tender_id, 2.0, 45000.0)
        assert b.status == BidStatus.SUBMITTED

    def test_bid_auto_id_prefix(self):
        t = self._create()
        b = self.reg.submit_bid(t.tender_id, 2.0, 45000.0)
        assert b.bid_id.startswith("DSO-BID-")

    def test_bid_on_closed_tender_raises(self):
        t = self._create()
        self.reg.close_tender(t.tender_id)
        with pytest.raises(ValueError):
            self.reg.submit_bid(t.tender_id, 2.0, 45000.0)

    def test_zero_capacity_bid_raises(self):
        t = self._create()
        with pytest.raises(ValueError):
            self.reg.submit_bid(t.tender_id, 0.0, 45000.0)

    def test_accept_bid(self):
        t = self._create()
        b = self.reg.submit_bid(t.tender_id, 5.0, 45000.0)
        accepted = self.reg.accept_bid(b.bid_id, 5.0)
        assert accepted.status == BidStatus.ACCEPTED
        assert accepted.awarded_capacity_mw == 5.0

    def test_reject_bid(self):
        t = self._create()
        b = self.reg.submit_bid(t.tender_id, 5.0, 45000.0)
        rejected = self.reg.reject_bid(b.bid_id)
        assert rejected.status == BidStatus.REJECTED

    def test_withdraw_bid(self):
        t = self._create()
        b = self.reg.submit_bid(t.tender_id, 5.0, 45000.0)
        withdrawn = self.reg.withdraw_bid(b.bid_id)
        assert withdrawn.status == BidStatus.WITHDRAWN

    def test_open_tenders(self):
        t1 = self._create()
        self._create(gsp="Bristol GSP")
        self.reg.close_tender(t1.tender_id)
        assert len(self.reg.open_tenders) == 1

    def test_bids_for_tender(self):
        t1 = self._create()
        t2 = self._create(gsp="Bristol GSP")
        self.reg.submit_bid(t1.tender_id, 2.0, 45000.0)
        self.reg.submit_bid(t2.tender_id, 3.0, 40000.0)
        assert len(self.reg.bids_for_tender(t1.tender_id)) == 1

    def test_total_contracted_capacity_mw(self):
        t1 = self._create(capacity=5.0)
        t2 = self._create(gsp="Bristol GSP", capacity=3.0)
        b1 = self.reg.submit_bid(t1.tender_id, 5.0, 45000.0)
        b2 = self.reg.submit_bid(t2.tender_id, 3.0, 40000.0)
        self.reg.accept_bid(b1.bid_id, 5.0)
        self.reg.accept_bid(b2.bid_id, 3.0)
        assert abs(self.reg.total_contracted_capacity_mw - 8.0) < 1e-9

    def test_total_annual_revenue(self):
        t = self._create()
        b = self.reg.submit_bid(t.tender_id, 2.0, 50000.0)
        self.reg.accept_bid(b.bid_id, 2.0)
        assert abs(self.reg.total_annual_flexibility_revenue_gbp - 100000.0) < 1e-9

    def test_tenders_by_dno(self):
        self._create(dno=DNO)
        self._create(dno="Western Power Distribution", gsp="Plymouth GSP")
        assert len(self.reg.tenders_by_dno(DNO)) == 1

    def test_dso_tender_summary(self):
        self._create()
        s = self.reg.dso_tender_summary()
        assert "1 total" in s

    def test_empty_summary(self):
        s = self.reg.dso_tender_summary()
        assert "0 total" in s
