"""Tests for Phase GG: PPM Emergency Credit Register."""
import datetime as dt
import pytest
from company.billing.ppm_emergency_credit_register import (
    EmergencyCreditType, EmergencyCreditStatus, PPMEmergencyCreditRecord,
    PPMEmergencyCreditRegister, _DEFAULT_EMERGENCY_CREDIT_GBP, _SELF_DISCONNECT_WELFARE_CHECK_DAYS,
)

ISSUED = dt.date(2024, 1, 15)
ACCT = "PPM-001"
AS_OF = dt.date(2024, 4, 30)

def make_record(status=EmergencyCreditStatus.ACTIVE, amount=5.0, repaid=0.0):
    return PPMEmergencyCreditRecord(
        record_id="PPME-00001", account_id=ACCT, issued_date=ISSUED,
        credit_type=EmergencyCreditType.EMERGENCY, amount_gbp=amount,
        repayment_rate_pct=50.0, status=status, amount_repaid_gbp=repaid)

class TestPPMEmergencyCreditRecord:
    def test_is_active_default(self):
        r = make_record()
        assert r.is_active
    def test_is_fully_repaid(self):
        r = make_record(EmergencyCreditStatus.REPAID)
        assert r.is_fully_repaid
    def test_outstanding_gbp_no_repayment(self):
        r = make_record(amount=5.0, repaid=0.0)
        assert abs(r.outstanding_gbp - 5.0) < 1e-9
    def test_outstanding_gbp_partial_repayment(self):
        r = make_record(amount=5.0, repaid=2.0)
        assert abs(r.outstanding_gbp - 3.0) < 1e-9
    def test_outstanding_gbp_fully_repaid(self):
        r = make_record(amount=5.0, repaid=5.0)
        assert r.outstanding_gbp == 0.0
    def test_outstanding_clamps_to_zero(self):
        r = make_record(amount=5.0, repaid=10.0)
        assert r.outstanding_gbp == 0.0
    def test_days_outstanding_no_repaid_date(self):
        r = make_record()
        assert r.days_outstanding(ISSUED + dt.timedelta(10)) == 10
    def test_days_outstanding_with_repaid_date(self):
        r = PPMEmergencyCreditRecord(
            record_id="X", account_id=ACCT, issued_date=ISSUED,
            credit_type=EmergencyCreditType.EMERGENCY, amount_gbp=5.0,
            repayment_rate_pct=50.0, status=EmergencyCreditStatus.REPAID,
            repaid_date=ISSUED + dt.timedelta(14))
        assert r.days_outstanding(AS_OF) == 14
    def test_welfare_check_due_after_28d(self):
        r = make_record()
        assert r.is_welfare_check_due(ISSUED + dt.timedelta(_SELF_DISCONNECT_WELFARE_CHECK_DAYS))
    def test_welfare_check_not_due_before_28d(self):
        r = make_record()
        assert not r.is_welfare_check_due(ISSUED + dt.timedelta(_SELF_DISCONNECT_WELFARE_CHECK_DAYS - 1))
    def test_welfare_check_not_due_when_repaid(self):
        r = make_record(EmergencyCreditStatus.REPAID)
        assert not r.is_welfare_check_due(ISSUED + dt.timedelta(100))
    def test_record_summary_string(self):
        r = make_record()
        assert "PPME-00001" in r.record_summary()
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.amount_gbp = 99.0

class TestPPMEmergencyCreditRegister:
    def setup_method(self):
        self.reg = PPMEmergencyCreditRegister()
    def test_issue_credit_stored(self):
        r = self.reg.issue_credit(ACCT, ISSUED)
        assert r.is_active and r.amount_gbp == _DEFAULT_EMERGENCY_CREDIT_GBP
    def test_issue_credit_auto_id(self):
        r1 = self.reg.issue_credit(ACCT, ISSUED)
        r2 = self.reg.issue_credit("PPM-002", ISSUED)
        assert r1.record_id != r2.record_id
    def test_issue_credit_zero_raises(self):
        with pytest.raises(ValueError):
            self.reg.issue_credit(ACCT, ISSUED, amount_gbp=0.0)
    def test_issue_credit_invalid_repayment_rate_raises(self):
        with pytest.raises(ValueError):
            self.reg.issue_credit(ACCT, ISSUED, repayment_rate_pct=0.0)
    def test_record_partial_repayment(self):
        r = self.reg.issue_credit(ACCT, ISSUED, amount_gbp=5.0)
        updated = self.reg.record_partial_repayment(r.record_id, 3.0)
        assert abs(updated.amount_repaid_gbp - 3.0) < 1e-9 and updated.is_active
    def test_record_partial_repayment_full_repayment_marks_repaid(self):
        r = self.reg.issue_credit(ACCT, ISSUED, amount_gbp=5.0)
        done = self.reg.record_partial_repayment(r.record_id, 5.0)
        assert done.is_fully_repaid
    def test_record_partial_repayment_caps_at_amount(self):
        r = self.reg.issue_credit(ACCT, ISSUED, amount_gbp=5.0)
        done = self.reg.record_partial_repayment(r.record_id, 99.0)
        assert abs(done.amount_repaid_gbp - 5.0) < 1e-9
    def test_mark_written_off(self):
        r = self.reg.issue_credit(ACCT, ISSUED)
        wo = self.reg.mark_written_off(r.record_id)
        assert wo.status == EmergencyCreditStatus.WRITTEN_OFF
    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.mark_written_off("PPME-99999")
    def test_active_credit_for_account(self):
        r1 = self.reg.issue_credit(ACCT, ISSUED)
        r2 = self.reg.issue_credit("PPM-002", ISSUED)
        self.reg.record_partial_repayment(r2.record_id, 5.0)
        active = self.reg.active_credit_for(ACCT)
        assert len(active) == 1 and active[0].record_id == r1.record_id
    def test_welfare_check_due(self):
        self.reg.issue_credit(ACCT, ISSUED)
        due = self.reg.welfare_check_due(ISSUED + dt.timedelta(_SELF_DISCONNECT_WELFARE_CHECK_DAYS))
        assert len(due) == 1
    def test_total_outstanding_gbp(self):
        r1 = self.reg.issue_credit(ACCT, ISSUED, amount_gbp=5.0)
        r2 = self.reg.issue_credit("PPM-002", ISSUED, amount_gbp=10.0)
        self.reg.record_partial_repayment(r1.record_id, 5.0)  # repaid
        assert abs(self.reg.total_outstanding_gbp() - 10.0) < 1e-9
    def test_total_written_off_gbp(self):
        r = self.reg.issue_credit(ACCT, ISSUED, amount_gbp=5.0)
        self.reg.mark_written_off(r.record_id)
        assert abs(self.reg.total_written_off_gbp() - 5.0) < 1e-9
    def test_accounts_with_active_credit(self):
        self.reg.issue_credit(ACCT, ISSUED)
        self.reg.issue_credit("PPM-002", ISSUED)
        assert len(self.reg.accounts_with_active_credit()) == 2
    def test_written_off_records(self):
        r = self.reg.issue_credit(ACCT, ISSUED)
        self.reg.mark_written_off(r.record_id)
        assert len(self.reg.written_off_records()) == 1
    def test_emergency_credit_summary(self):
        self.reg.issue_credit(ACCT, ISSUED)
        s = self.reg.emergency_credit_summary(AS_OF)
        assert "1 records" in s and "1 active" in s
    def test_empty_summary(self):
        s = self.reg.emergency_credit_summary(AS_OF)
        assert "0 records" in s
