"""Tests for Complaint Root Cause Analyser (Phase DS)."""
import datetime as dt
import pytest
from company.crm.complaint_root_cause_analyser import (
    ComplaintCategory, RootCauseStatus, ImpactSeverity,
    ComplaintRootCause, ComplaintRootCauseAnalyser,
    _REMEDIATION_SLA_DAYS,
)


@pytest.fixture
def analyser():
    return ComplaintRootCauseAnalyser()


DATE = dt.date(2024, 3, 1)


def identify(analyser, category=ComplaintCategory.BILLING, severity=ImpactSeverity.MEDIUM,
             attributed=10, customers=25, owner="Billing Team", slc=None):
    return analyser.identify(
        category=category,
        description="Test root cause",
        identified_date=DATE,
        severity=severity,
        complaints_attributed=attributed,
        estimated_customers_affected=customers,
        remediation_owner=owner,
        linked_slc=slc,
    )


class TestComplaintRootCause:
    def test_created_open(self, analyser):
        rec = identify(analyser)
        assert rec.status == RootCauseStatus.OPEN
        assert rec.is_open

    def test_sla_days_medium(self, analyser):
        rec = identify(analyser, severity=ImpactSeverity.MEDIUM)
        assert rec.remediation_sla_days == 30

    def test_sla_days_critical(self, analyser):
        rec = identify(analyser, severity=ImpactSeverity.CRITICAL)
        assert rec.remediation_sla_days == 5

    def test_overdue_medium_31_days(self, analyser):
        rec = identify(analyser, severity=ImpactSeverity.MEDIUM)
        as_of = DATE + dt.timedelta(days=31)
        assert rec.is_overdue(as_of)

    def test_not_overdue_within_sla(self, analyser):
        rec = identify(analyser, severity=ImpactSeverity.MEDIUM)
        as_of = DATE + dt.timedelta(days=25)
        assert not rec.is_overdue(as_of)

    def test_closed_not_overdue(self, analyser):
        rec = identify(analyser, severity=ImpactSeverity.CRITICAL)
        analyser.close(rec.rca_id, DATE + dt.timedelta(days=3))
        closed = analyser.get(rec.rca_id)
        as_of = DATE + dt.timedelta(days=100)
        assert not closed.is_overdue(as_of)

    def test_is_systemic(self, analyser):
        rec = identify(analyser)
        analyser.escalate_systemic(rec.rca_id)
        updated = analyser.get(rec.rca_id)
        assert updated.is_systemic
        assert updated.is_open  # systemic = still open

    def test_linked_slc(self, analyser):
        rec = identify(analyser, slc="SLC 6")
        assert rec.linked_slc == "SLC 6"

    def test_in_remediation_is_open(self, analyser):
        rec = identify(analyser)
        analyser.start_remediation(rec.rca_id)
        updated = analyser.get(rec.rca_id)
        assert updated.is_open
        assert updated.status == RootCauseStatus.IN_REMEDIATION


class TestComplaintRootCauseAnalyser:
    def test_sequential_ids(self, analyser):
        r1 = identify(analyser)
        r2 = identify(analyser)
        assert r1.rca_id != r2.rca_id

    def test_open_rcas(self, analyser):
        r1 = identify(analyser)
        r2 = identify(analyser)
        analyser.close(r1.rca_id, DATE + dt.timedelta(days=10))
        assert len(analyser.open_rcas()) == 1

    def test_overdue_rcas(self, analyser):
        r1 = identify(analyser, severity=ImpactSeverity.MEDIUM)  # 30d SLA
        identify(analyser, severity=ImpactSeverity.LOW)            # 90d SLA
        as_of = DATE + dt.timedelta(days=35)  # medium overdue, low not
        overdue = analyser.overdue_rcas(as_of)
        assert len(overdue) == 1

    def test_systemic_issues(self, analyser):
        r1 = identify(analyser)
        analyser.escalate_systemic(r1.rca_id)
        identify(analyser)
        assert len(analyser.systemic_issues()) == 1

    def test_by_category(self, analyser):
        identify(analyser, category=ComplaintCategory.BILLING, attributed=5)
        identify(analyser, category=ComplaintCategory.BILLING, attributed=3)
        identify(analyser, category=ComplaintCategory.METERING, attributed=2)
        by_cat = analyser.by_category()
        assert by_cat[ComplaintCategory.BILLING.value] == 8
        assert by_cat[ComplaintCategory.METERING.value] == 2

    def test_critical_open(self, analyser):
        identify(analyser, severity=ImpactSeverity.CRITICAL)
        identify(analyser, severity=ImpactSeverity.MEDIUM)
        assert len(analyser.critical_open()) == 1

    def test_total_complaints_attributed(self, analyser):
        identify(analyser, attributed=5)
        identify(analyser, attributed=8)
        assert analyser.total_complaints_attributed() == 13

    def test_sla_constants(self):
        assert _REMEDIATION_SLA_DAYS[ImpactSeverity.CRITICAL] == 5
        assert _REMEDIATION_SLA_DAYS[ImpactSeverity.HIGH] == 14
        assert _REMEDIATION_SLA_DAYS[ImpactSeverity.MEDIUM] == 30
        assert _REMEDIATION_SLA_DAYS[ImpactSeverity.LOW] == 90

    def test_rca_summary(self, analyser):
        identify(analyser)
        s = analyser.rca_summary()
        assert "Root Cause Analyser" in s
        assert "Consumer Duty" in s

    def test_empty_analyser_summary(self, analyser):
        s = analyser.rca_summary()
        assert "0 RCAs" in s
