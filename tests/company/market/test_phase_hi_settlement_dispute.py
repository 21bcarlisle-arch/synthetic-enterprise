"""Tests for BSC Settlement Dispute Register -- Phase HI."""
import datetime as dt
import pytest
from company.market.bsc_settlement_dispute_register import (
    DisputeGround, SQStatus, SettlementDisputeRecord, BSCSettlementDisputeRegister,
)

TODAY = dt.date(2024, 6, 10)
SDATE = dt.date(2022, 1, 15)
RUN = "R2"
GROUND = DisputeGround.METER_READ_ERROR


def make_reg():
    return BSCSettlementDisputeRegister()


def raise_sq(reg=None, settlement_date=SDATE, run_type=RUN, ground=GROUND,
             error_gwh=0.5, impact_gbp=12500.0, raised_date=TODAY):
    if reg is None:
        reg = make_reg()
    return reg, reg.raise_dispute(settlement_date, run_type, ground, error_gwh, impact_gbp, raised_date)


class TestSettlementDisputeRecord:
    def test_raised_status(self):
        _, rec = raise_sq()
        assert rec.status == SQStatus.RAISED

    def test_is_open_when_raised(self):
        _, rec = raise_sq()
        assert rec.is_open

    def test_is_not_upheld_when_raised(self):
        _, rec = raise_sq()
        assert not rec.is_upheld

    def test_saa_response_due_none_before_investigation(self):
        _, rec = raise_sq()
        assert rec.saa_response_due is None

    def test_saa_response_due_after_investigation_started(self):
        reg, rec = raise_sq()
        inv = reg.start_investigation(rec.dispute_id, TODAY)
        assert inv.saa_response_due is not None
        # 40 working days from TODAY = approx 56+ calendar days
        assert inv.saa_response_due > TODAY + dt.timedelta(days=50)

    def test_is_saa_overdue_false_when_just_started(self):
        reg, rec = raise_sq()
        reg.start_investigation(rec.dispute_id, TODAY)
        updated = reg.all_records[0]
        assert not updated.is_saa_response_overdue(TODAY + dt.timedelta(days=5))

    def test_is_saa_overdue_true_past_deadline(self):
        reg, rec = raise_sq()
        reg.start_investigation(rec.dispute_id, TODAY)
        updated = reg.all_records[0]
        assert updated.is_saa_response_overdue(TODAY + dt.timedelta(days=90))

    def test_dispute_summary_contains_id(self):
        _, rec = raise_sq()
        assert rec.dispute_id in rec.dispute_summary()

    def test_frozen(self):
        _, rec = raise_sq()
        with pytest.raises((AttributeError, TypeError)):
            rec.status = SQStatus.UPHELD


class TestBSCSettlementDisputeRegister:
    def setup_method(self):
        self.reg = make_reg()

    def _raise(self, error_gwh=0.5, impact_gbp=12500.0, ground=GROUND):
        return self.reg.raise_dispute(SDATE, RUN, ground, error_gwh, impact_gbp, TODAY)

    def test_auto_id_prefix(self):
        rec = self._raise()
        assert rec.dispute_id.startswith("SQ-")

    def test_auto_id_increments(self):
        r1 = self._raise()
        r2 = self._raise()
        assert r1.dispute_id != r2.dispute_id

    def test_zero_error_raises(self):
        with pytest.raises(ValueError):
            self._raise(error_gwh=0.0)

    def test_negative_impact_raises(self):
        with pytest.raises(ValueError):
            self._raise(impact_gbp=-1.0)

    def test_start_investigation(self):
        rec = self._raise()
        inv = self.reg.start_investigation(rec.dispute_id, TODAY)
        assert inv.status == SQStatus.UNDER_INVESTIGATION

    def test_start_investigation_non_raised_raises(self):
        rec = self._raise()
        self.reg.start_investigation(rec.dispute_id, TODAY)
        with pytest.raises(ValueError):
            self.reg.start_investigation(rec.dispute_id, TODAY)

    def test_uphold(self):
        rec = self._raise()
        self.reg.start_investigation(rec.dispute_id, TODAY)
        upheld = self.reg.uphold(rec.dispute_id, TODAY + dt.timedelta(days=50), 10000.0)
        assert upheld.status == SQStatus.UPHELD
        assert upheld.recovery_amount_gbp == 10000.0

    def test_uphold_negative_recovery_raises(self):
        rec = self._raise()
        self.reg.start_investigation(rec.dispute_id, TODAY)
        with pytest.raises(ValueError):
            self.reg.uphold(rec.dispute_id, TODAY, -1.0)

    def test_reject(self):
        rec = self._raise()
        self.reg.start_investigation(rec.dispute_id, TODAY)
        rejected = self.reg.reject(rec.dispute_id, TODAY + dt.timedelta(days=40))
        assert rejected.status == SQStatus.REJECTED

    def test_appeal_after_rejection(self):
        rec = self._raise()
        self.reg.start_investigation(rec.dispute_id, TODAY)
        self.reg.reject(rec.dispute_id, TODAY + dt.timedelta(days=40))
        appealed = self.reg.appeal(rec.dispute_id, TODAY + dt.timedelta(days=50))
        assert appealed.status == SQStatus.APPEALED

    def test_appeal_not_rejected_raises(self):
        rec = self._raise()
        with pytest.raises(ValueError):
            self.reg.appeal(rec.dispute_id, TODAY)

    def test_uphold_appeal(self):
        rec = self._raise()
        self.reg.start_investigation(rec.dispute_id, TODAY)
        self.reg.reject(rec.dispute_id, TODAY + dt.timedelta(days=40))
        self.reg.appeal(rec.dispute_id, TODAY + dt.timedelta(days=50))
        result = self.reg.uphold_appeal(rec.dispute_id, TODAY + dt.timedelta(days=70), 8000.0)
        assert result.status == SQStatus.APPEAL_UPHELD

    def test_reject_appeal(self):
        rec = self._raise()
        self.reg.start_investigation(rec.dispute_id, TODAY)
        self.reg.reject(rec.dispute_id, TODAY + dt.timedelta(days=40))
        self.reg.appeal(rec.dispute_id, TODAY + dt.timedelta(days=50))
        result = self.reg.reject_appeal(rec.dispute_id, TODAY + dt.timedelta(days=70))
        assert result.status == SQStatus.APPEAL_REJECTED

    def test_withdraw_from_open(self):
        rec = self._raise()
        withdrawn = self.reg.withdraw(rec.dispute_id)
        assert withdrawn.status == SQStatus.WITHDRAWN

    def test_withdraw_terminal_raises(self):
        rec = self._raise()
        self.reg.start_investigation(rec.dispute_id, TODAY)
        self.reg.uphold(rec.dispute_id, TODAY + dt.timedelta(days=40), 5000.0)
        with pytest.raises(ValueError):
            self.reg.withdraw(rec.dispute_id)

    def test_open_disputes(self):
        r1 = self._raise()
        r2 = self._raise()
        self.reg.start_investigation(r1.dispute_id, TODAY)
        self.reg.uphold(r1.dispute_id, TODAY + dt.timedelta(days=40), 5000.0)
        assert len(self.reg.open_disputes) == 1

    def test_upheld_disputes(self):
        rec = self._raise()
        self.reg.start_investigation(rec.dispute_id, TODAY)
        self.reg.uphold(rec.dispute_id, TODAY + dt.timedelta(days=40), 5000.0)
        assert len(self.reg.upheld_disputes) == 1

    def test_overdue_saa_responses(self):
        rec = self._raise()
        self.reg.start_investigation(rec.dispute_id, TODAY)
        # 40WD in future should NOT show as overdue
        assert len(self.reg.overdue_saa_responses(TODAY + dt.timedelta(days=20))) == 0
        # 90 cal days later should show as overdue
        assert len(self.reg.overdue_saa_responses(TODAY + dt.timedelta(days=90))) == 1

    def test_total_financial_impact_open_only(self):
        r1 = self._raise(impact_gbp=10000.0)
        r2 = self._raise(impact_gbp=5000.0)
        self.reg.start_investigation(r1.dispute_id, TODAY)
        self.reg.uphold(r1.dispute_id, TODAY + dt.timedelta(days=40), 10000.0)
        # r1 upheld (not open), r2 still open
        assert abs(self.reg.total_financial_impact_gbp - 5000.0) < 0.01

    def test_total_recovered_gbp(self):
        r1 = self._raise()
        self.reg.start_investigation(r1.dispute_id, TODAY)
        self.reg.uphold(r1.dispute_id, TODAY + dt.timedelta(days=40), 8000.0)
        assert abs(self.reg.total_recovered_gbp - 8000.0) < 0.01

    def test_uphold_rate_pct(self):
        r1 = self._raise()
        r2 = self._raise()
        self.reg.start_investigation(r1.dispute_id, TODAY)
        self.reg.uphold(r1.dispute_id, TODAY + dt.timedelta(days=40), 5000.0)
        self.reg.start_investigation(r2.dispute_id, TODAY)
        self.reg.reject(r2.dispute_id, TODAY + dt.timedelta(days=40))
        rate = self.reg.uphold_rate_pct()
        assert rate is not None
        assert abs(rate - 50.0) < 0.01

    def test_uphold_rate_none_when_no_decided(self):
        self._raise()
        assert self.reg.uphold_rate_pct() is None

    def test_dispute_register_summary(self):
        self._raise()
        s = self.reg.dispute_register_summary()
        assert "1 total" in s

    def test_empty_summary(self):
        assert "0 total" in self.reg.dispute_register_summary()
