"""Tests for Wholesale Trading Mandate Register -- Phase HH."""
import datetime as dt
import pytest
from company.trading.wholesale_trading_mandate_register import (
    TradingInstrument, AuthorizationLevel, MandateStatus,
    TradingMandateRecord, WholesaleTradingMandateRegister,
)

TODAY = dt.date(2024, 6, 10)
VALID_FROM = dt.date(2024, 1, 1)
VALID_TO = dt.date(2024, 12, 31)
APPROVER = "Risk Committee"


def make_reg():
    return WholesaleTradingMandateRegister()


def submit(reg=None, instrument=TradingInstrument.PHYSICAL_ELECTRICITY_FORWARD,
           tenor=365, notional=10_000_000.0, position=50000.0,
           auth=AuthorizationLevel.TRADER_AUTONOMOUS,
           valid_from=VALID_FROM, valid_to=VALID_TO):
    if reg is None:
        reg = make_reg()
    return reg, reg.submit_mandate(instrument, tenor, notional, position, auth, valid_from, valid_to)


class TestTradingMandateRecord:
    def test_is_not_approved_when_draft(self):
        _, rec = submit()
        assert not rec.is_approved

    def test_is_approved_when_active(self):
        reg, rec = submit()
        approved = reg.approve_mandate(rec.mandate_id, APPROVER, TODAY)
        assert approved.is_approved

    def test_is_active_when_active_and_in_range(self):
        reg, rec = submit()
        reg.approve_mandate(rec.mandate_id, APPROVER, TODAY)
        result = reg.active_mandates(TODAY)[0]
        assert result.is_active_as_of(TODAY)

    def test_is_not_active_before_valid_from(self):
        _, rec = submit()
        assert not rec.is_active_as_of(dt.date(2023, 12, 31))

    def test_is_not_active_after_valid_to(self):
        reg, rec = submit()
        reg.approve_mandate(rec.mandate_id, APPROVER, TODAY)
        result = reg.all_records[0]
        assert not result.is_active_as_of(dt.date(2025, 1, 1))

    def test_is_expired_after_valid_to(self):
        _, rec = submit()
        assert rec.is_expired_as_of(dt.date(2025, 1, 1))

    def test_days_remaining_within_period(self):
        _, rec = submit(valid_from=TODAY, valid_to=TODAY + dt.timedelta(days=30))
        assert rec.days_remaining(TODAY) == 30

    def test_days_remaining_zero_when_expired(self):
        _, rec = submit()
        assert rec.days_remaining(dt.date(2025, 1, 1)) == 0

    def test_mandate_summary_contains_id(self):
        _, rec = submit()
        assert rec.mandate_id in rec.mandate_summary()

    def test_frozen(self):
        _, rec = submit()
        with pytest.raises((AttributeError, TypeError)):
            rec.status = MandateStatus.ACTIVE


class TestWholesaleTradingMandateRegister:
    def setup_method(self):
        self.reg = make_reg()

    def _submit(self, instrument=TradingInstrument.PHYSICAL_ELECTRICITY_FORWARD,
                tenor=365, notional=10_000_000.0, position=50000.0,
                auth=AuthorizationLevel.TRADER_AUTONOMOUS,
                valid_from=VALID_FROM, valid_to=VALID_TO):
        return self.reg.submit_mandate(instrument, tenor, notional, position, auth, valid_from, valid_to)

    def test_submit_returns_draft(self):
        rec = self._submit()
        assert rec.status == MandateStatus.DRAFT

    def test_auto_id_prefix(self):
        rec = self._submit()
        assert rec.mandate_id.startswith("MANDATE-")

    def test_auto_id_increments(self):
        r1 = self._submit()
        r2 = self._submit(instrument=TradingInstrument.PHYSICAL_GAS_FORWARD)
        assert r1.mandate_id != r2.mandate_id

    def test_valid_to_before_from_raises(self):
        with pytest.raises(ValueError):
            self._submit(valid_from=VALID_TO, valid_to=VALID_FROM)

    def test_zero_tenor_raises(self):
        with pytest.raises(ValueError):
            self._submit(tenor=0)

    def test_zero_notional_raises(self):
        with pytest.raises(ValueError):
            self._submit(notional=0.0)

    def test_zero_position_raises(self):
        with pytest.raises(ValueError):
            self._submit(position=0.0)

    def test_approve_mandate(self):
        rec = self._submit()
        approved = self.reg.approve_mandate(rec.mandate_id, APPROVER, TODAY)
        assert approved.status == MandateStatus.ACTIVE
        assert approved.approved_by == APPROVER

    def test_approve_non_draft_raises(self):
        rec = self._submit()
        self.reg.approve_mandate(rec.mandate_id, APPROVER, TODAY)
        with pytest.raises(ValueError):
            self.reg.approve_mandate(rec.mandate_id, APPROVER, TODAY)

    def test_suspend_active(self):
        rec = self._submit()
        self.reg.approve_mandate(rec.mandate_id, APPROVER, TODAY)
        suspended = self.reg.suspend(rec.mandate_id)
        assert suspended.status == MandateStatus.SUSPENDED

    def test_suspend_draft_raises(self):
        rec = self._submit()
        with pytest.raises(ValueError):
            self.reg.suspend(rec.mandate_id)

    def test_reinstate_suspended(self):
        rec = self._submit()
        self.reg.approve_mandate(rec.mandate_id, APPROVER, TODAY)
        self.reg.suspend(rec.mandate_id)
        reinstated = self.reg.reinstate(rec.mandate_id)
        assert reinstated.status == MandateStatus.ACTIVE

    def test_reinstate_active_raises(self):
        rec = self._submit()
        self.reg.approve_mandate(rec.mandate_id, APPROVER, TODAY)
        with pytest.raises(ValueError):
            self.reg.reinstate(rec.mandate_id)

    def test_expire_mandate(self):
        rec = self._submit()
        expired = self.reg.expire(rec.mandate_id)
        assert expired.status == MandateStatus.EXPIRED

    def test_supersede_mandate(self):
        rec = self._submit()
        superseded = self.reg.supersede(rec.mandate_id)
        assert superseded.status == MandateStatus.SUPERSEDED

    def test_active_mandates(self):
        r1 = self._submit()
        r2 = self._submit(instrument=TradingInstrument.PHYSICAL_GAS_FORWARD)
        self.reg.approve_mandate(r1.mandate_id, APPROVER, TODAY)
        active = self.reg.active_mandates(TODAY)
        assert len(active) == 1

    def test_instruments_authorized(self):
        r1 = self._submit(instrument=TradingInstrument.PHYSICAL_ELECTRICITY_FORWARD)
        r2 = self._submit(instrument=TradingInstrument.PHYSICAL_GAS_FORWARD)
        self.reg.approve_mandate(r1.mandate_id, APPROVER, TODAY)
        authorized = self.reg.instruments_authorized(TODAY)
        assert TradingInstrument.PHYSICAL_ELECTRICITY_FORWARD in authorized
        assert TradingInstrument.PHYSICAL_GAS_FORWARD not in authorized

    def test_mandate_for_instrument_found(self):
        rec = self._submit()
        self.reg.approve_mandate(rec.mandate_id, APPROVER, TODAY)
        found = self.reg.mandate_for_instrument(
            TradingInstrument.PHYSICAL_ELECTRICITY_FORWARD, TODAY
        )
        assert found is not None

    def test_mandate_for_instrument_none_when_no_active(self):
        self._submit()  # not approved
        found = self.reg.mandate_for_instrument(
            TradingInstrument.PHYSICAL_ELECTRICITY_FORWARD, TODAY
        )
        assert found is None

    def test_expiring_within(self):
        rec = self._submit(valid_to=TODAY + dt.timedelta(days=25))
        self.reg.approve_mandate(rec.mandate_id, APPROVER, TODAY)
        expiring = self.reg.expiring_within(TODAY, 30)
        assert len(expiring) == 1

    def test_draft_mandates(self):
        self._submit()
        self._submit(instrument=TradingInstrument.PHYSICAL_GAS_FORWARD)
        assert len(self.reg.draft_mandates()) == 2

    def test_total_authorized_notional(self):
        r1 = self._submit(notional=5_000_000.0)
        r2 = self._submit(instrument=TradingInstrument.PHYSICAL_GAS_FORWARD, notional=3_000_000.0)
        self.reg.approve_mandate(r1.mandate_id, APPROVER, TODAY)
        self.reg.approve_mandate(r2.mandate_id, APPROVER, TODAY)
        assert abs(self.reg.total_authorized_notional_gbp(TODAY) - 8_000_000.0) < 1.0

    def test_mandate_register_summary(self):
        self._submit()
        s = self.reg.mandate_register_summary(TODAY)
        assert "1 total" in s

    def test_empty_summary(self):
        s = self.reg.mandate_register_summary(TODAY)
        assert "0 total" in s
