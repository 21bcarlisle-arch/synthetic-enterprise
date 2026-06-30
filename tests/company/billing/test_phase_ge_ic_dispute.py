"""Tests for Phase GE: I&C Invoice Dispute Register."""
import datetime as dt
import pytest
from company.billing.ic_invoice_dispute_register import (
    ICDisputeType, ICResolutionMethod, ICDisputeStatus,
    ICInvoiceDisputeRecord, ICInvoiceDisputeRegister,
)

RAISED = dt.date(2024, 1, 15)
ACCT = "IC-001"
INV = "INV-2024-001"
AS_OF = dt.date(2024, 6, 30)

def make_record(status=ICDisputeStatus.RAISED, dtype=ICDisputeType.VOLUME, amount=50000.0):
    return ICInvoiceDisputeRecord(
        dispute_id="ICDISP-00001", account_id=ACCT,
        raised_date=RAISED, invoice_ref=INV,
        disputed_amount_gbp=amount, dispute_type=dtype, status=status)

class TestICInvoiceDisputeRecord:
    def test_is_open_when_raised(self):
        r = make_record(ICDisputeStatus.RAISED)
        assert r.is_open
    def test_is_open_under_review(self):
        r = make_record(ICDisputeStatus.UNDER_REVIEW)
        assert r.is_open
    def test_is_open_audit_commissioned(self):
        r = make_record(ICDisputeStatus.AUDIT_COMMISSIONED)
        assert r.is_open
    def test_not_open_when_escalated(self):
        r = make_record(ICDisputeStatus.ESCALATED_GEMA)
        assert not r.is_open
    def test_is_escalated_gema(self):
        r = make_record(ICDisputeStatus.ESCALATED_GEMA)
        assert r.is_escalated
    def test_is_escalated_court(self):
        r = make_record(ICDisputeStatus.ESCALATED_COURT)
        assert r.is_escalated
    def test_is_resolved_resolved(self):
        r = make_record(ICDisputeStatus.RESOLVED)
        assert r.is_resolved
    def test_is_resolved_agreed_settlement(self):
        r = make_record(ICDisputeStatus.AGREED_SETTLEMENT)
        assert r.is_resolved
    def test_is_resolved_withdrawn(self):
        r = make_record(ICDisputeStatus.WITHDRAWN)
        assert r.is_resolved
    def test_requires_external_resolution_audit(self):
        r = make_record(ICDisputeStatus.AUDIT_COMMISSIONED)
        assert r.requires_external_resolution
    def test_days_open_no_resolved_date(self):
        r = make_record()
        assert r.days_open(RAISED + dt.timedelta(30)) == 30
    def test_days_open_with_resolved_date(self):
        r = ICInvoiceDisputeRecord("X", ACCT, RAISED, INV, 50000.0,
            ICDisputeType.VOLUME, ICDisputeStatus.RESOLVED, None,
            resolved_date=RAISED + dt.timedelta(45))
        assert r.days_open(AS_OF) == 45
    def test_dispute_summary_string(self):
        r = make_record()
        assert "ICDISP-00001" in r.dispute_summary()
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.disputed_amount_gbp = 999.0

class TestICInvoiceDisputeRegister:
    def setup_method(self):
        self.reg = ICInvoiceDisputeRegister()
    def test_raise_dispute_stored(self):
        r = self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        assert r.is_open
    def test_raise_dispute_auto_id(self):
        r1 = self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        r2 = self.reg.raise_dispute(ACCT, RAISED, "INV-002", 20000.0, ICDisputeType.PRICING)
        assert r1.dispute_id != r2.dispute_id
    def test_raise_dispute_zero_amount_raises(self):
        with pytest.raises(ValueError):
            self.reg.raise_dispute(ACCT, RAISED, INV, 0.0, ICDisputeType.VOLUME)
    def test_commence_review(self):
        r = self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        rev = self.reg.commence_review(r.dispute_id)
        assert rev.status == ICDisputeStatus.UNDER_REVIEW
    def test_commission_audit(self):
        r = self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.METER_ACCURACY)
        aud = self.reg.commission_audit(r.dispute_id)
        assert aud.status == ICDisputeStatus.AUDIT_COMMISSIONED
        assert aud.resolution_method == ICResolutionMethod.INDEPENDENT_METER_AUDIT
    def test_resolve(self):
        r = self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        res = self.reg.resolve(r.dispute_id, AS_OF, ICResolutionMethod.SUPPLIER_REVIEW, 5000.0)
        assert res.is_resolved and res.credit_issued_gbp == 5000.0
    def test_agree_settlement(self):
        r = self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.PRICING)
        settled = self.reg.agree_settlement(r.dispute_id, AS_OF, 25000.0)
        assert settled.status == ICDisputeStatus.AGREED_SETTLEMENT
        assert settled.credit_issued_gbp == 25000.0
    def test_escalate_gema(self):
        r = self.reg.raise_dispute(ACCT, RAISED, INV, 500000.0, ICDisputeType.CONTRACT_BREACH)
        esc = self.reg.escalate_gema(r.dispute_id)
        assert esc.is_escalated and esc.resolution_method == ICResolutionMethod.GEMA_ARBITRATION
    def test_escalate_court(self):
        r = self.reg.raise_dispute(ACCT, RAISED, INV, 1000000.0, ICDisputeType.CONTRACT_BREACH)
        court = self.reg.escalate_court(r.dispute_id)
        assert court.status == ICDisputeStatus.ESCALATED_COURT
    def test_withdraw(self):
        r = self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        wd = self.reg.withdraw(r.dispute_id)
        assert wd.status == ICDisputeStatus.WITHDRAWN
    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.commence_review("ICDISP-99999")
    def test_open_disputes(self):
        r1 = self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        r2 = self.reg.raise_dispute(ACCT, RAISED, "INV-2", 20000.0, ICDisputeType.PRICING)
        self.reg.withdraw(r1.dispute_id)
        assert len(self.reg.open_disputes()) == 1
    def test_escalated_disputes(self):
        r = self.reg.raise_dispute(ACCT, RAISED, INV, 500000.0, ICDisputeType.CONTRACT_BREACH)
        self.reg.escalate_gema(r.dispute_id)
        assert len(self.reg.escalated_disputes()) == 1
    def test_disputes_for_account(self):
        self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        self.reg.raise_dispute("IC-002", RAISED, "INV-X", 30000.0, ICDisputeType.PRICING)
        assert len(self.reg.disputes_for_account(ACCT)) == 1
    def test_by_type(self):
        self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        self.reg.raise_dispute(ACCT, RAISED, "INV-2", 20000.0, ICDisputeType.PRICING)
        assert len(self.reg.by_type(ICDisputeType.VOLUME)) == 1
    def test_total_disputed_gbp_open_and_escalated(self):
        r1 = self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        r2 = self.reg.raise_dispute("IC-002", RAISED, "INV-2", 30000.0, ICDisputeType.PRICING)
        self.reg.escalate_gema(r2.dispute_id)
        self.reg.raise_dispute("IC-003", RAISED, "INV-3", 20000.0, ICDisputeType.SETTLEMENT_ERROR)
        r3_id = self.reg._records[-1].dispute_id
        self.reg.withdraw(r3_id)
        total = self.reg.total_disputed_gbp()
        assert abs(total - 80000.0) < 1e-6
    def test_total_credits_issued(self):
        r = self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        self.reg.resolve(r.dispute_id, AS_OF, ICResolutionMethod.SUPPLIER_REVIEW, 5000.0)
        assert abs(self.reg.total_credits_issued_gbp() - 5000.0) < 1e-6
    def test_long_running_disputes(self):
        self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        long = self.reg.long_running_disputes(RAISED + dt.timedelta(91))
        assert len(long) == 1
        not_long = self.reg.long_running_disputes(RAISED + dt.timedelta(89))
        assert len(not_long) == 0
    def test_dispute_register_summary(self):
        r = self.reg.raise_dispute(ACCT, RAISED, INV, 50000.0, ICDisputeType.VOLUME)
        s = self.reg.dispute_register_summary(AS_OF)
        assert "1 disputes" in s and "1 open" in s
    def test_empty_summary(self):
        s = self.reg.dispute_register_summary(AS_OF)
        assert "0 disputes" in s
