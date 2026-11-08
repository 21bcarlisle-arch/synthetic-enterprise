"""Tests for SLC Compliance Tracker (Phase DN)."""
import pytest
from company.regulatory.slc_compliance_tracker import (
    SLCStatus, SLCCategory, SLCObservation, SLCComplianceTracker,
)


@pytest.fixture
def tracker():
    return SLCComplianceTracker()


def add_slc(tracker, ref="SLC 14", cat=SLCCategory.CREDIT,
            status=SLCStatus.COMPLIANT, breach_count=0, at_risk_count=0):
    return tracker.record(
        slc_ref=ref,
        category=cat,
        description=f"Test SLC {ref}",
        status=status,
        breach_count=breach_count,
        at_risk_count=at_risk_count,
    )


class TestSLCObservation:
    def test_compliant(self, tracker):
        obs = add_slc(tracker, status=SLCStatus.COMPLIANT)
        assert obs.is_compliant
        assert not obs.is_breached
        assert obs.severity_score == 0

    def test_at_risk(self, tracker):
        obs = add_slc(tracker, status=SLCStatus.BREACH_RISK)
        assert not obs.is_compliant
        assert not obs.is_breached
        assert obs.severity_score == 1

    def test_breached(self, tracker):
        obs = add_slc(tracker, status=SLCStatus.BREACHED)
        assert obs.is_breached
        assert not obs.is_compliant
        assert obs.severity_score == 2

    def test_not_applicable_zero_severity(self, tracker):
        obs = add_slc(tracker, status=SLCStatus.NOT_APPLICABLE)
        assert obs.severity_score == 0


class TestSLCComplianceTracker:
    def test_record_and_get(self, tracker):
        add_slc(tracker, "SLC 14")
        obs = tracker.get("SLC 14")
        assert obs is not None
        assert obs.slc_ref == "SLC 14"

    def test_get_missing_returns_none(self, tracker):
        assert tracker.get("MISSING") is None

    def test_overwrite_record(self, tracker):
        add_slc(tracker, "SLC 14", status=SLCStatus.COMPLIANT)
        add_slc(tracker, "SLC 14", status=SLCStatus.BREACHED)
        assert tracker.get("SLC 14").status == SLCStatus.BREACHED

    def test_breached_list(self, tracker):
        add_slc(tracker, "SLC 14", status=SLCStatus.BREACHED)
        add_slc(tracker, "SLC 22", status=SLCStatus.COMPLIANT)
        assert len(tracker.breached) == 1
        assert tracker.breached[0].slc_ref == "SLC 14"

    def test_at_risk_list(self, tracker):
        add_slc(tracker, "SLC 27", status=SLCStatus.BREACH_RISK)
        add_slc(tracker, "SLC 14", status=SLCStatus.COMPLIANT)
        assert len(tracker.at_risk) == 1

    def test_compliant_list(self, tracker):
        add_slc(tracker, "SLC 6", status=SLCStatus.COMPLIANT)
        add_slc(tracker, "SLC 14", status=SLCStatus.BREACHED)
        assert len(tracker.compliant) == 1

    def test_total_breach_count(self, tracker):
        add_slc(tracker, "SLC 6", status=SLCStatus.BREACHED, breach_count=3)
        add_slc(tracker, "SLC 14", status=SLCStatus.BREACHED, breach_count=2)
        assert tracker.total_breach_count == 5

    def test_total_at_risk_count(self, tracker):
        add_slc(tracker, "SLC 27", status=SLCStatus.BREACH_RISK, at_risk_count=4)
        assert tracker.total_at_risk_count == 4

    def test_overall_rag_green(self, tracker):
        add_slc(tracker, "SLC 14", status=SLCStatus.COMPLIANT)
        assert tracker.overall_rag == "GREEN"

    def test_overall_rag_amber(self, tracker):
        add_slc(tracker, "SLC 14", status=SLCStatus.COMPLIANT)
        add_slc(tracker, "SLC 27", status=SLCStatus.BREACH_RISK)
        assert tracker.overall_rag == "AMBER"

    def test_overall_rag_red(self, tracker):
        add_slc(tracker, "SLC 14", status=SLCStatus.BREACHED)
        assert tracker.overall_rag == "RED"

    def test_by_category(self, tracker):
        add_slc(tracker, "SLC 14", cat=SLCCategory.CREDIT)
        add_slc(tracker, "SLC 6", cat=SLCCategory.BILLING)
        add_slc(tracker, "SLC 21B", cat=SLCCategory.BILLING)
        billing = tracker.by_category(SLCCategory.BILLING)
        assert len(billing) == 2

    def test_highest_severity_order(self, tracker):
        add_slc(tracker, "SLC 6", status=SLCStatus.COMPLIANT)
        add_slc(tracker, "SLC 14", status=SLCStatus.BREACH_RISK, at_risk_count=2)
        add_slc(tracker, "SLC 27", status=SLCStatus.BREACHED, breach_count=5)
        top = tracker.highest_severity_slcs(n=2)
        assert top[0].slc_ref == "SLC 27"
        assert top[1].slc_ref == "SLC 14"

    def test_all_observations_sorted(self, tracker):
        add_slc(tracker, "SLC 45")
        add_slc(tracker, "SLC 14")
        refs = [o.slc_ref for o in tracker.all_observations]
        assert refs == sorted(refs)

    def test_compliance_summary_string(self, tracker):
        add_slc(tracker, "SLC 14", status=SLCStatus.COMPLIANT)
        add_slc(tracker, "SLC 27", status=SLCStatus.BREACHED, breach_count=2)
        s = tracker.compliance_summary()
        assert "SLC Compliance Dashboard" in s
        assert "RED" in s

    def test_empty_tracker_green(self, tracker):
        assert tracker.overall_rag == "GREEN"

    def test_all_observations_empty(self, tracker):
        assert tracker.all_observations == []
