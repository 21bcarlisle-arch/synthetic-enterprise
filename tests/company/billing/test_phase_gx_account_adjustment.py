import datetime as dt
import pytest
from company.billing.account_adjustment_register import (
    AdjustmentType, AdjustmentDirection, AdjustmentStatus, AccountAdjustmentRecord,
    AccountAdjustmentRegister, approval_tier_required,
    _AUTO_APPROVE_LIMIT, _TEAM_LEADER_LIMIT, _MANAGEMENT_LIMIT,
)

ACCOUNT = "ACC-001"
RAISED = dt.date(2024, 5, 1)
AS_OF = dt.date(2024, 6, 1)


def make_record(amount=50.0, direction=AdjustmentDirection.CREDIT,
                status=AdjustmentStatus.APPROVED):
    return AccountAdjustmentRecord(
        record_id="ADJ-000001", account_id=ACCOUNT,
        adjustment_type=AdjustmentType.GOODWILL,
        direction=direction, amount_gbp=amount,
        reason="Service failure", raised_date=RAISED, status=status)


class TestApprovalTier:
    def test_auto_at_limit(self):
        assert approval_tier_required(_AUTO_APPROVE_LIMIT) == "auto"
    def test_team_leader_above_auto(self):
        assert approval_tier_required(_AUTO_APPROVE_LIMIT + 1) == "team_leader"
    def test_management_above_team_leader(self):
        assert approval_tier_required(_TEAM_LEADER_LIMIT + 1) == "management"
    def test_director_above_management(self):
        assert approval_tier_required(_MANAGEMENT_LIMIT + 1) == "director"


class TestAccountAdjustmentRecord:
    def test_is_open_pending(self):
        assert make_record(status=AdjustmentStatus.PENDING_APPROVAL).is_open
    def test_is_open_approved(self):
        assert make_record(status=AdjustmentStatus.APPROVED).is_open
    def test_is_not_open_applied(self):
        assert not make_record(status=AdjustmentStatus.APPLIED).is_open
    def test_approval_tier_credit(self):
        r = make_record(amount=50.0)
        assert r.approval_tier == "team_leader"
    def test_net_amount_credit(self):
        r = make_record(amount=50.0, direction=AdjustmentDirection.CREDIT)
        assert abs(r.net_amount_gbp - (-50.0)) < 1e-9
    def test_net_amount_debit(self):
        r = make_record(amount=50.0, direction=AdjustmentDirection.DEBIT)
        assert abs(r.net_amount_gbp - 50.0) < 1e-9
    def test_adjustment_summary_credit(self):
        s = make_record().adjustment_summary()
        assert "ADJ-000001" in s and ACCOUNT in s and "-GBP" in s
    def test_adjustment_summary_debit(self):
        s = make_record(direction=AdjustmentDirection.DEBIT).adjustment_summary()
        assert "+GBP" in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.amount_gbp = 999.0


class TestAccountAdjustmentRegister:
    def setup_method(self):
        self.reg = AccountAdjustmentRegister()

    def test_raise_adjustment_small_auto_approved(self):
        r = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, _AUTO_APPROVE_LIMIT, "Small goodwill", RAISED)
        assert r.status == AdjustmentStatus.APPROVED and r.approved_by == "auto"

    def test_raise_adjustment_large_pending(self):
        r = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 200.0, "Large goodwill", RAISED)
        assert r.status == AdjustmentStatus.PENDING_APPROVAL

    def test_zero_amount_raises(self):
        with pytest.raises(ValueError):
            self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
                AdjustmentDirection.CREDIT, 0.0, "Zero", RAISED)

    def test_auto_id_increments(self):
        r1 = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 20.0, "R1", RAISED)
        r2 = self.reg.raise_adjustment("ACC-002", AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 20.0, "R2", RAISED)
        assert r1.record_id != r2.record_id

    def test_approve(self):
        r = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 200.0, "Large goodwill", RAISED)
        approved = self.reg.approve(r.record_id, "Manager Jane")
        assert approved.status == AdjustmentStatus.APPROVED
        assert approved.approved_by == "Manager Jane"

    def test_apply(self):
        r = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 20.0, "Small", RAISED)
        applied = self.reg.apply(r.record_id, AS_OF)
        assert applied.status == AdjustmentStatus.APPLIED
        assert applied.applied_date == AS_OF

    def test_reject(self):
        r = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 200.0, "Large", RAISED)
        rejected = self.reg.reject(r.record_id, "Not justified")
        assert rejected.status == AdjustmentStatus.REJECTED
        assert "Not justified" in rejected.rejection_reason

    def test_reverse(self):
        r = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 20.0, "Applied in error", RAISED)
        self.reg.apply(r.record_id, AS_OF)
        rev = self.reg.reverse(r.record_id)
        assert rev.status == AdjustmentStatus.REVERSED

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.approve("ADJ-999999", "Boss")

    def test_pending_approval(self):
        r = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 200.0, "Large", RAISED)
        self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 20.0, "Small auto", RAISED)
        assert len(self.reg.pending_approval()) == 1

    def test_adjustments_for_account(self):
        self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 20.0, "R1", RAISED)
        self.reg.raise_adjustment("ACC-002", AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 20.0, "R2", RAISED)
        assert len(self.reg.adjustments_for_account(ACCOUNT)) == 1

    def test_by_type(self):
        self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 20.0, "R1", RAISED)
        self.reg.raise_adjustment(ACCOUNT, AdjustmentType.COMPLAINT_REMEDY,
            AdjustmentDirection.CREDIT, 30.0, "R2", RAISED)
        assert len(self.reg.by_type(AdjustmentType.GOODWILL)) == 1

    def test_total_credits_applied_gbp(self):
        r1 = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 20.0, "R1", RAISED)
        self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 30.0, "R2", RAISED)
        self.reg.apply(r1.record_id, AS_OF)
        assert abs(self.reg.total_credits_applied_gbp() - 20.0) < 1e-9

    def test_total_debits_applied_gbp(self):
        r1 = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.DATA_ERROR_CORRECTION,
            AdjustmentDirection.DEBIT, 50.0, "Undercharge", RAISED)
        self.reg.apply(r1.record_id, AS_OF)
        assert abs(self.reg.total_debits_applied_gbp() - 50.0) < 1e-9

    def test_goodwill_spend_gbp(self):
        r1 = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 20.0, "Goodwill", RAISED)
        r2 = self.reg.raise_adjustment(ACCOUNT, AdjustmentType.COMPLAINT_REMEDY,
            AdjustmentDirection.CREDIT, 30.0, "Remedy", RAISED)
        self.reg.apply(r1.record_id, AS_OF)
        self.reg.apply(r2.record_id, AS_OF)
        assert abs(self.reg.goodwill_spend_gbp() - 20.0) < 1e-9

    def test_adjustment_summary(self):
        self.reg.raise_adjustment(ACCOUNT, AdjustmentType.GOODWILL,
            AdjustmentDirection.CREDIT, 200.0, "Large", RAISED)
        s = self.reg.adjustment_summary()
        assert "1 adjustments" in s and "1 pending" in s
