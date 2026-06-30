"""Tests for Phase FZ: Ofgem Redress Payment Register."""
import datetime as dt
import pytest
from company.regulatory.ofgem_redress_register import (
    RedressPaymentRecipient,
    RedressPaymentStatus,
    RedressPaymentRecord,
    OfgemRedressRegister,
    _PAYMENT_DEADLINE_DAYS_DEFAULT,
)

# ── helpers ──────────────────────────────────────────────────────────────────

AGREED = dt.date(2024, 1, 15)
DEADLINE = AGREED + dt.timedelta(days=_PAYMENT_DEADLINE_DAYS_DEFAULT)


def make_record(
    redress_id="RD-00001",
    agreed_date=None,
    recipient=RedressPaymentRecipient.NATIONAL_ENERGY_ACTION,
    amount=50_000.0,
    breach="SLC 27 billing failure",
    deadline=None,
    status=RedressPaymentStatus.AGREED,
    payment_date=None,
):
    agreed_date = agreed_date or AGREED
    deadline = deadline or DEADLINE
    return RedressPaymentRecord(
        redress_id=redress_id,
        agreed_date=agreed_date,
        recipient=recipient,
        amount_gbp=amount,
        related_breach_description=breach,
        payment_deadline=deadline,
        status=status,
        payment_date=payment_date,
    )


# ── RedressPaymentRecord ─────────────────────────────────────────────────────

class TestRedressPaymentRecord:

    def test_is_paid_when_paid(self):
        r = make_record(status=RedressPaymentStatus.PAID)
        assert r.is_paid

    def test_is_not_paid_when_agreed(self):
        r = make_record(status=RedressPaymentStatus.AGREED)
        assert not r.is_paid

    def test_is_overdue_property(self):
        r = make_record(status=RedressPaymentStatus.OVERDUE)
        assert r.is_overdue

    def test_is_overdue_as_of_before_deadline(self):
        r = make_record()
        assert not r.is_overdue_as_of(DEADLINE)

    def test_is_overdue_as_of_after_deadline(self):
        r = make_record()
        assert r.is_overdue_as_of(DEADLINE + dt.timedelta(days=1))

    def test_is_overdue_as_of_false_when_paid(self):
        r = make_record(status=RedressPaymentStatus.PAID)
        assert not r.is_overdue_as_of(dt.date(2030, 1, 1))

    def test_is_overdue_as_of_false_when_cancelled(self):
        r = make_record(status=RedressPaymentStatus.CANCELLED)
        assert not r.is_overdue_as_of(dt.date(2030, 1, 1))

    def test_record_summary_contains_amount_and_id(self):
        r = make_record(amount=25_000.0)
        s = r.record_summary()
        assert "RD-00001" in s
        assert "25,000.00" in s

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.amount_gbp = 99_999.0


# ── OfgemRedressRegister ─────────────────────────────────────────────────────

class TestOfgemRedressRegister:

    def setup_method(self):
        self.reg = OfgemRedressRegister()

    def test_record_redress_stored(self):
        r = self.reg.record_redress(
            AGREED, RedressPaymentRecipient.NATIONAL_ENERGY_ACTION, 50_000.0, "SLC breach"
        )
        assert r.amount_gbp == 50_000.0
        assert r.status == RedressPaymentStatus.AGREED

    def test_record_redress_auto_id(self):
        r1 = self.reg.record_redress(AGREED, RedressPaymentRecipient.CITIZENS_ADVICE, 10_000.0, "B1")
        r2 = self.reg.record_redress(AGREED, RedressPaymentRecipient.CITIZENS_ADVICE, 20_000.0, "B2")
        assert r1.redress_id != r2.redress_id

    def test_record_redress_deadline_computed(self):
        r = self.reg.record_redress(AGREED, RedressPaymentRecipient.ENERGY_SAVING_TRUST, 5_000.0, "B", deadline_days=60)
        assert r.payment_deadline == AGREED + dt.timedelta(days=60)

    def test_record_redress_zero_amount_raises(self):
        with pytest.raises(ValueError):
            self.reg.record_redress(AGREED, RedressPaymentRecipient.CITIZENS_ADVICE, 0.0, "B")

    def test_record_redress_negative_raises(self):
        with pytest.raises(ValueError):
            self.reg.record_redress(AGREED, RedressPaymentRecipient.CITIZENS_ADVICE, -1.0, "B")

    def test_mark_paid(self):
        r = self.reg.record_redress(AGREED, RedressPaymentRecipient.NATIONAL_ENERGY_ACTION, 50_000.0, "B")
        paid = self.reg.mark_paid(r.redress_id, dt.date(2024, 2, 1))
        assert paid.status == RedressPaymentStatus.PAID
        assert paid.payment_date == dt.date(2024, 2, 1)

    def test_mark_overdue(self):
        r = self.reg.record_redress(AGREED, RedressPaymentRecipient.CITIZENS_ADVICE, 30_000.0, "B")
        overdue = self.reg.mark_overdue(r.redress_id)
        assert overdue.status == RedressPaymentStatus.OVERDUE

    def test_cancel(self):
        r = self.reg.record_redress(AGREED, RedressPaymentRecipient.CITIZENS_ADVICE, 10_000.0, "B")
        cancelled = self.reg.cancel(r.redress_id)
        assert cancelled.status == RedressPaymentStatus.CANCELLED

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.mark_paid("RD-99999", dt.date(2024, 2, 1))

    def test_pending_payments(self):
        r1 = self.reg.record_redress(AGREED, RedressPaymentRecipient.NATIONAL_ENERGY_ACTION, 50_000.0, "B1")
        self.reg.record_redress(AGREED, RedressPaymentRecipient.CITIZENS_ADVICE, 20_000.0, "B2")
        self.reg.mark_paid(r1.redress_id, dt.date(2024, 2, 1))
        # only the unpaid, non-overdue one is pending
        pending = self.reg.pending_payments(DEADLINE - dt.timedelta(days=1))
        assert len(pending) == 1

    def test_overdue_payments(self):
        r1 = self.reg.record_redress(AGREED, RedressPaymentRecipient.NATIONAL_ENERGY_ACTION, 50_000.0, "B1")
        self.reg.record_redress(AGREED, RedressPaymentRecipient.CITIZENS_ADVICE, 20_000.0, "B2")
        self.reg.mark_paid(r1.redress_id, dt.date(2024, 2, 1))
        # after deadline: r2 is overdue
        overdue = self.reg.overdue_payments(DEADLINE + dt.timedelta(days=1))
        assert len(overdue) == 1

    def test_by_recipient(self):
        self.reg.record_redress(AGREED, RedressPaymentRecipient.NATIONAL_ENERGY_ACTION, 50_000.0, "B1")
        self.reg.record_redress(AGREED, RedressPaymentRecipient.CITIZENS_ADVICE, 20_000.0, "B2")
        nea = self.reg.by_recipient(RedressPaymentRecipient.NATIONAL_ENERGY_ACTION)
        assert len(nea) == 1 and nea[0].amount_gbp == 50_000.0

    def test_total_paid_gbp(self):
        r1 = self.reg.record_redress(AGREED, RedressPaymentRecipient.NATIONAL_ENERGY_ACTION, 50_000.0, "B1")
        self.reg.record_redress(AGREED, RedressPaymentRecipient.CITIZENS_ADVICE, 20_000.0, "B2")
        self.reg.mark_paid(r1.redress_id, dt.date(2024, 2, 1))
        assert abs(self.reg.total_paid_gbp() - 50_000.0) < 1e-9

    def test_total_outstanding_excludes_paid_and_cancelled(self):
        r1 = self.reg.record_redress(AGREED, RedressPaymentRecipient.NATIONAL_ENERGY_ACTION, 50_000.0, "B1")
        r2 = self.reg.record_redress(AGREED, RedressPaymentRecipient.CITIZENS_ADVICE, 20_000.0, "B2")
        r3 = self.reg.record_redress(AGREED, RedressPaymentRecipient.ENERGY_SAVING_TRUST, 10_000.0, "B3")
        self.reg.mark_paid(r1.redress_id, dt.date(2024, 2, 1))
        self.reg.cancel(r2.redress_id)
        outstanding = self.reg.total_outstanding_gbp(AGREED)
        assert abs(outstanding - 10_000.0) < 1e-9

    def test_all_paid_true(self):
        r = self.reg.record_redress(AGREED, RedressPaymentRecipient.NATIONAL_ENERGY_ACTION, 50_000.0, "B")
        self.reg.mark_paid(r.redress_id, dt.date(2024, 2, 1))
        assert self.reg.all_paid()

    def test_all_paid_false(self):
        self.reg.record_redress(AGREED, RedressPaymentRecipient.NATIONAL_ENERGY_ACTION, 50_000.0, "B")
        assert not self.reg.all_paid()

    def test_redress_register_summary(self):
        r = self.reg.record_redress(AGREED, RedressPaymentRecipient.NATIONAL_ENERGY_ACTION, 50_000.0, "B")
        self.reg.mark_paid(r.redress_id, dt.date(2024, 2, 1))
        s = self.reg.redress_register_summary(dt.date(2024, 3, 1))
        assert "1 orders" in s
        assert "1 paid" in s

    def test_empty_register_summary(self):
        s = self.reg.redress_register_summary(dt.date(2024, 1, 1))
        assert "0 orders" in s
