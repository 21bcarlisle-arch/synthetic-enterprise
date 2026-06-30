"""Tests for Renewal Notice Register (Phase DQ)."""
import datetime as dt
import pytest
from company.crm.renewal_notice_register import (
    NoticeOutcome, RenewalNoticeRecord, RenewalNoticeRegister,
    _NOTICE_MIN_DAYS, _NOTICE_MAX_DAYS,
)


@pytest.fixture
def reg():
    return RenewalNoticeRegister()


EXPIRY = dt.date(2024, 12, 31)
ROLLOVER = "SVT Dec24"


def add(reg, account_id="C1", expiry=EXPIRY, exit_fee=0.0):
    return reg.register_contract(
        account_id=account_id,
        contract_expiry_date=expiry,
        rollover_tariff_name=ROLLOVER,
        rollover_unit_rate_pence=32.5,
        rollover_standing_charge_pence=55.0,
        exit_fee_gbp=exit_fee,
    )


class TestRenewalNoticeRecord:
    def test_pending_initially(self, reg):
        rec = add(reg)
        assert rec.outcome == NoticeOutcome.PENDING
        assert rec.days_before_expiry is None

    def test_sent_on_time(self, reg):
        add(reg)
        # Send exactly 45 days before expiry
        sent = EXPIRY - dt.timedelta(days=45)
        rec = reg.record_notice_sent("C1", sent)
        assert rec.outcome == NoticeOutcome.SENT_ON_TIME
        assert rec.days_before_expiry == 45

    def test_sent_late(self, reg):
        add(reg)
        sent = EXPIRY - dt.timedelta(days=30)
        rec = reg.record_notice_sent("C1", sent)
        assert rec.outcome == NoticeOutcome.SENT_LATE
        assert rec.is_breach

    def test_sent_early(self, reg):
        add(reg)
        sent = EXPIRY - dt.timedelta(days=60)
        rec = reg.record_notice_sent("C1", sent)
        assert rec.outcome == NoticeOutcome.SENT_EARLY
        assert not rec.is_breach  # early is compliant

    def test_boundary_exactly_42(self, reg):
        add(reg)
        sent = EXPIRY - dt.timedelta(days=42)
        rec = reg.record_notice_sent("C1", sent)
        assert rec.outcome == NoticeOutcome.SENT_ON_TIME

    def test_boundary_exactly_49(self, reg):
        add(reg)
        sent = EXPIRY - dt.timedelta(days=49)
        rec = reg.record_notice_sent("C1", sent)
        assert rec.outcome == NoticeOutcome.SENT_ON_TIME

    def test_is_compliant_not_required(self, reg):
        add(reg)
        reg.mark_not_required("C1")
        assert reg.get("C1").is_compliant

    def test_failed_is_breach(self, reg):
        add(reg)
        reg.mark_failed("C1")
        rec = reg.get("C1")
        assert rec.is_breach
        assert not rec.is_compliant

    def test_notice_due_window(self, reg):
        rec = add(reg)
        earliest, latest = rec.notice_due_window()
        assert earliest == EXPIRY - dt.timedelta(days=49)
        assert latest == EXPIRY - dt.timedelta(days=42)

    def test_exit_fee_stored(self, reg):
        rec = add(reg, exit_fee=50.0)
        assert rec.exit_fee_gbp == pytest.approx(50.0)


class TestRenewalNoticeRegisterQueries:
    def test_pending_list(self, reg):
        add(reg, "C1")
        add(reg, "C2")
        assert len(reg.pending()) == 2

    def test_breaches_list(self, reg):
        add(reg, "C1")
        add(reg, "C2")
        reg.mark_failed("C1")
        reg.record_notice_sent("C2", EXPIRY - dt.timedelta(days=30))
        assert len(reg.breaches()) == 2

    def test_due_for_notice(self, reg):
        # Expiry Dec 31; earliest notice = Nov 12 (49 days before)
        add(reg, "C1", expiry=EXPIRY)
        # as_of = Nov 15 = inside window
        as_of = dt.date(2024, 11, 15)
        due = reg.due_for_notice(as_of)
        assert len(due) == 1

    def test_not_due_before_window(self, reg):
        add(reg, "C1", expiry=EXPIRY)
        # as_of = Oct 1 = before earliest notice date
        as_of = dt.date(2024, 10, 1)
        assert reg.due_for_notice(as_of) == []

    def test_overdue_notice(self, reg):
        add(reg, "C1", expiry=EXPIRY)
        # as_of = Dec 1 = after latest notice date (Nov 19)
        as_of = dt.date(2024, 12, 1)
        overdue = reg.overdue_notice(as_of)
        assert len(overdue) == 1

    def test_compliance_rate_all_compliant(self, reg):
        add(reg, "C1")
        reg.record_notice_sent("C1", EXPIRY - dt.timedelta(days=45))
        assert reg.compliance_rate() == pytest.approx(1.0)

    def test_compliance_rate_empty(self, reg):
        assert reg.compliance_rate() == pytest.approx(1.0)

    def test_constants(self):
        assert _NOTICE_MIN_DAYS == 42
        assert _NOTICE_MAX_DAYS == 49

    def test_summary_string(self, reg):
        add(reg)
        s = reg.notice_register_summary()
        assert "Renewal Notice Register" in s
        assert "SLC 22" in s
