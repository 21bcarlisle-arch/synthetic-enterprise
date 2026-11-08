"""Tests for Phase GD: Direct Debit Mandate Register."""
import datetime as dt
import pytest
from company.billing.dd_mandate_register import (
    DDMandateStatus,
    DDMandateRecord,
    DDMandateRegister,
    _MAX_PAYMENT_DAY,
)

# ── helpers ──────────────────────────────────────────────────────────────────

SETUP = dt.date(2024, 3, 1)
ACCT = "ACC-001"


# ── DDMandateRecord ──────────────────────────────────────────────────────────

class TestDDMandateRecord:

    def test_is_active_default(self):
        r = DDMandateRecord("DDM-00001", ACCT, SETUP, 15, 100.0)
        assert r.is_active

    def test_is_active_reinstated(self):
        r = DDMandateRecord("DDM-00001", ACCT, SETUP, 15, 100.0, DDMandateStatus.REINSTATED)
        assert r.is_active

    def test_is_suspended(self):
        r = DDMandateRecord("DDM-00001", ACCT, SETUP, 15, 100.0, DDMandateStatus.SUSPENDED)
        assert r.is_suspended and not r.is_active

    def test_is_failed(self):
        r = DDMandateRecord("DDM-00001", ACCT, SETUP, 15, 100.0, DDMandateStatus.FAILED)
        assert r.is_failed

    def test_is_cancelled(self):
        r = DDMandateRecord("DDM-00001", ACCT, SETUP, 15, 100.0, DDMandateStatus.CANCELLED)
        assert r.is_cancelled

    def test_is_collectable_when_active(self):
        r = DDMandateRecord("DDM-00001", ACCT, SETUP, 15, 100.0)
        assert r.is_collectable

    def test_not_collectable_when_suspended(self):
        r = DDMandateRecord("DDM-00001", ACCT, SETUP, 15, 100.0, DDMandateStatus.SUSPENDED)
        assert not r.is_collectable

    def test_next_collection_due_active(self):
        r = DDMandateRecord("DDM-00001", ACCT, SETUP, 15, 100.0)
        assert r.next_collection_due == 15

    def test_next_collection_due_none_when_suspended(self):
        r = DDMandateRecord("DDM-00001", ACCT, SETUP, 15, 100.0, DDMandateStatus.SUSPENDED)
        assert r.next_collection_due is None

    def test_mandate_summary_string(self):
        r = DDMandateRecord("DDM-00001", ACCT, SETUP, 15, 100.0)
        s = r.mandate_summary()
        assert "DDM-00001" in s and ACCT in s

    def test_frozen(self):
        r = DDMandateRecord("DDM-00001", ACCT, SETUP, 15, 100.0)
        with pytest.raises((AttributeError, TypeError)):
            r.amount_gbp = 999.0


# ── DDMandateRegister ────────────────────────────────────────────────────────

class TestDDMandateRegister:

    def setup_method(self):
        self.reg = DDMandateRegister()

    def test_setup_mandate_stored(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        assert r.payment_day == 15 and r.amount_gbp == 100.0

    def test_setup_mandate_auto_ref(self):
        r1 = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        r2 = self.reg.setup_mandate("ACC-002", 1, 80.0, SETUP)
        assert r1.mandate_ref != r2.mandate_ref

    def test_setup_mandate_invalid_day_raises(self):
        with pytest.raises(ValueError):
            self.reg.setup_mandate(ACCT, 0, 100.0, SETUP)
        with pytest.raises(ValueError):
            self.reg.setup_mandate(ACCT, 29, 100.0, SETUP)

    def test_setup_mandate_day_28_valid(self):
        r = self.reg.setup_mandate(ACCT, _MAX_PAYMENT_DAY, 100.0, SETUP)
        assert r.payment_day == _MAX_PAYMENT_DAY

    def test_setup_mandate_zero_amount_raises(self):
        with pytest.raises(ValueError):
            self.reg.setup_mandate(ACCT, 15, 0.0, SETUP)

    def test_update_amount(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        updated = self.reg.update_amount(r.mandate_ref, 150.0, dt.date(2024, 4, 1))
        assert updated.amount_gbp == 150.0

    def test_update_amount_zero_raises(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        with pytest.raises(ValueError):
            self.reg.update_amount(r.mandate_ref, 0.0, dt.date(2024, 4, 1))

    def test_suspend(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        susp = self.reg.suspend(r.mandate_ref, dt.date(2024, 4, 1))
        assert susp.is_suspended

    def test_reinstate(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        self.reg.suspend(r.mandate_ref, dt.date(2024, 4, 1))
        reinstated = self.reg.reinstate(r.mandate_ref, dt.date(2024, 5, 1))
        assert reinstated.is_active

    def test_cancel(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        cancelled = self.reg.cancel(r.mandate_ref, dt.date(2024, 4, 1))
        assert cancelled.is_cancelled
        assert cancelled.cancellation_date == dt.date(2024, 4, 1)

    def test_record_failure_first_fails(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        failed = self.reg.record_failure(r.mandate_ref, dt.date(2024, 4, 1))
        assert failed.is_failed and failed.failed_count == 1

    def test_record_failure_second_cancels(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        self.reg.record_failure(r.mandate_ref, dt.date(2024, 4, 1))
        cancelled = self.reg.record_failure(r.mandate_ref, dt.date(2024, 4, 5))
        assert cancelled.is_cancelled and cancelled.failed_count == 2

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.cancel("DDM-99999", dt.date(2024, 4, 1))

    def test_active_mandates(self):
        r1 = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        self.reg.setup_mandate("ACC-002", 1, 80.0, SETUP)
        self.reg.cancel(r1.mandate_ref, dt.date(2024, 4, 1))
        assert len(self.reg.active_mandates()) == 1

    def test_failed_mandates(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        self.reg.record_failure(r.mandate_ref, dt.date(2024, 4, 1))
        assert len(self.reg.failed_mandates()) == 1

    def test_cancelled_mandates(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        self.reg.cancel(r.mandate_ref, dt.date(2024, 4, 1))
        assert len(self.reg.cancelled_mandates()) == 1

    def test_mandate_for_account_returns_active(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        result = self.reg.mandate_for_account(ACCT)
        assert result is not None and result.mandate_ref == r.mandate_ref

    def test_mandate_for_account_none_if_unknown(self):
        assert self.reg.mandate_for_account("UNKNOWN") is None

    def test_total_monthly_collection(self):
        r1 = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        self.reg.setup_mandate("ACC-002", 1, 80.0, SETUP)
        self.reg.cancel(r1.mandate_ref, dt.date(2024, 4, 1))
        assert abs(self.reg.total_monthly_collection_gbp() - 80.0) < 1e-9

    def test_accounts_without_active_mandate(self):
        self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        result = self.reg.accounts_without_active_mandate([ACCT, "ACC-002"])
        assert result == ["ACC-002"]

    def test_dd_mandate_summary(self):
        r = self.reg.setup_mandate(ACCT, 15, 100.0, SETUP)
        s = self.reg.dd_mandate_summary()
        assert "1 mandates" in s and "1 active" in s

    def test_empty_summary(self):
        s = self.reg.dd_mandate_summary()
        assert "0 mandates" in s
