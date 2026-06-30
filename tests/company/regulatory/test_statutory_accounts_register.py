"""Tests for Statutory Annual Accounts Register (Phase DJ)."""
import datetime as dt
import pytest
from company.regulatory.statutory_accounts_register import (
    AccountsType, FilingStatus, DisclosureFlag, StatutoryAccountsRecord,
    StatutoryAccountsRegister, _FILING_DEADLINE_MONTHS,
)


@pytest.fixture
def reg():
    return StatutoryAccountsRegister()


FYE = dt.date(2023, 12, 31)  # Financial year end


class TestStatutoryAccountsRecord:
    def test_record_created(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0)
        assert rec.financial_year_end == FYE
        assert rec.accounts_type == AccountsType.SMALL
        assert rec.status == FilingStatus.DRAFT

    def test_filing_deadline_9_months(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0)
        assert rec.filing_deadline == dt.date(2024, 9, 30)

    def test_filing_deadline_march_year_end(self, reg):
        rec = reg.record_year(dt.date(2023, 3, 31), revenue_gbp=1_500_000.0)
        assert rec.filing_deadline == dt.date(2023, 12, 31)

    def test_not_overdue_before_deadline(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0)
        before = dt.date(2024, 9, 29)
        assert not rec.is_overdue(before)

    def test_overdue_after_deadline(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0)
        after = dt.date(2024, 10, 1)
        assert rec.is_overdue(after)

    def test_submitted_not_overdue(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0,
                              status=FilingStatus.SUBMITTED,
                              submitted_date=dt.date(2024, 9, 1))
        assert not rec.is_overdue(dt.date(2025, 1, 1))

    def test_accepted_not_overdue(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0,
                              status=FilingStatus.ACCEPTED)
        assert not rec.is_overdue(dt.date(2025, 6, 1))

    def test_days_overdue(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0)
        # Deadline is 2024-09-30; 31 days later
        as_of = dt.date(2024, 10, 31)
        assert rec.days_overdue(as_of) == 31

    def test_days_overdue_zero_if_not_overdue(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0)
        assert rec.days_overdue(dt.date(2024, 8, 1)) == 0

    def test_late_penalty_30_days(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0)
        # 10 days overdue → up to 30 days bracket
        as_of = dt.date(2024, 10, 10)
        assert rec.late_penalty_gbp(as_of) == 150.0

    def test_late_penalty_escalates(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0)
        # 100 days overdue → 90-180 day bracket
        as_of = rec.filing_deadline + dt.timedelta(days=100)
        assert rec.late_penalty_gbp(as_of) == 750.0

    def test_no_penalty_if_not_overdue(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0)
        assert rec.late_penalty_gbp(dt.date(2024, 9, 1)) == 0.0

    def test_classify_micro(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=500_000.0)
        assert rec.accounts_type == AccountsType.MICRO

    def test_classify_medium(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=15_000_000.0)
        assert rec.accounts_type == AccountsType.MEDIUM

    def test_classify_large(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=40_000_000.0)
        assert rec.accounts_type == AccountsType.LARGE

    def test_requires_audit_medium(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=15_000_000.0)
        assert rec.requires_audit

    def test_no_audit_for_small(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0)
        assert not rec.requires_audit

    def test_has_disclosure_secr(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0,
                              disclosures=(DisclosureFlag.SECR,))
        assert rec.has_disclosure(DisclosureFlag.SECR)
        assert not rec.has_disclosure(DisclosureFlag.TCFD)

    def test_is_filed_submitted(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0,
                              status=FilingStatus.SUBMITTED)
        assert rec.is_filed

    def test_not_filed_draft(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0)
        assert not rec.is_filed

    def test_ch_reference_stored(self, reg):
        rec = reg.record_year(FYE, revenue_gbp=1_500_000.0,
                              ch_reference="CH-2024-001234")
        assert rec.ch_reference == "CH-2024-001234"


class TestStatutoryAccountsRegisterQueries:
    def test_overdue_list(self, reg):
        reg.record_year(FYE, revenue_gbp=1_500_000.0)
        overdue = reg.overdue(dt.date(2025, 1, 1))
        assert len(overdue) == 1

    def test_overdue_excludes_submitted(self, reg):
        reg.record_year(FYE, revenue_gbp=1_500_000.0,
                        status=FilingStatus.SUBMITTED)
        assert reg.overdue(dt.date(2025, 1, 1)) == []

    def test_total_penalty_exposure(self, reg):
        reg.record_year(dt.date(2022, 12, 31), revenue_gbp=1_500_000.0)
        penalty = reg.total_penalty_exposure_gbp(dt.date(2024, 1, 1))
        assert penalty > 0

    def test_filed_list(self, reg):
        reg.record_year(dt.date(2022, 12, 31), revenue_gbp=1_500_000.0,
                        status=FilingStatus.ACCEPTED)
        reg.record_year(FYE, revenue_gbp=1_500_000.0)
        assert len(reg.filed()) == 1

    def test_by_status(self, reg):
        reg.record_year(dt.date(2022, 12, 31), revenue_gbp=1_500_000.0,
                        status=FilingStatus.ACCEPTED)
        reg.record_year(FYE, revenue_gbp=1_500_000.0)
        by_s = reg.by_status()
        assert by_s[FilingStatus.ACCEPTED.value] == 1
        assert by_s[FilingStatus.DRAFT.value] == 1

    def test_requiring_audit(self, reg):
        reg.record_year(FYE, revenue_gbp=40_000_000.0)  # large
        reg.record_year(dt.date(2022, 12, 31), revenue_gbp=1_500_000.0)  # small
        assert len(reg.requiring_audit()) == 1

    def test_classify_static(self):
        assert StatutoryAccountsRegister.classify(500_000) == AccountsType.MICRO
        assert StatutoryAccountsRegister.classify(5_000_000) == AccountsType.SMALL
        assert StatutoryAccountsRegister.classify(15_000_000) == AccountsType.MEDIUM
        assert StatutoryAccountsRegister.classify(50_000_000) == AccountsType.LARGE

    def test_statutory_accounts_summary(self, reg):
        reg.record_year(FYE, revenue_gbp=1_500_000.0,
                        status=FilingStatus.ACCEPTED)
        s = reg.statutory_accounts_summary()
        assert "Statutory Accounts Register" in s
        assert "1 filed" in s

    def test_deadline_constant(self):
        assert _FILING_DEADLINE_MONTHS == 9
