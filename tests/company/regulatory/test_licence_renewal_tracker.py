"""Tests for Supplier Licence Renewal Tracker (Phase EP)."""
import datetime as dt
import pytest
from company.regulatory.licence_renewal_tracker import (
    LicenceType, ComplianceMilestoneType, ComplianceMilestone,
    LicenceRecord, SupplierLicenceRenewalTracker,
)

DATE = dt.date(2024, 1, 15)


def make_milestone(mtype=ComplianceMilestoneType.SLC_SELF_REPORT,
                   due=None, submitted=None):
    due = due or dt.date(2024, 1, 10)
    return ComplianceMilestone(
        milestone_type=mtype,
        due_date=due,
        submitted_date=submitted,
    )


class TestComplianceMilestone:
    def test_is_submitted_true(self):
        m = make_milestone(submitted=dt.date(2024, 1, 8))
        assert m.is_submitted

    def test_is_submitted_false(self):
        m = make_milestone()
        assert not m.is_submitted

    def test_is_overdue_past_due(self):
        m = make_milestone(due=dt.date(2024, 1, 10))
        assert m.is_overdue(dt.date(2024, 1, 15))

    def test_is_overdue_not_past(self):
        m = make_milestone(due=dt.date(2024, 2, 1))
        assert not m.is_overdue(dt.date(2024, 1, 15))

    def test_is_overdue_false_when_submitted(self):
        m = make_milestone(due=dt.date(2024, 1, 10), submitted=dt.date(2024, 1, 20))
        assert not m.is_overdue(dt.date(2024, 1, 25))

    def test_days_overdue(self):
        m = make_milestone(due=dt.date(2024, 1, 10))
        assert m.days_overdue(dt.date(2024, 1, 15)) == 5

    def test_days_overdue_zero_when_not(self):
        m = make_milestone(due=dt.date(2024, 2, 1))
        assert m.days_overdue(dt.date(2024, 1, 15)) == 0

    def test_is_late_submission_true(self):
        m = make_milestone(due=dt.date(2024, 1, 10), submitted=dt.date(2024, 1, 15))
        assert m.is_late_submission()

    def test_is_late_submission_false_on_time(self):
        m = make_milestone(due=dt.date(2024, 1, 10), submitted=dt.date(2024, 1, 8))
        assert not m.is_late_submission()

    def test_is_late_submission_false_not_submitted(self):
        m = make_milestone()
        assert not m.is_late_submission()


class TestLicenceRenewalTracker:
    def test_register_licence(self):
        tracker = SupplierLicenceRenewalTracker()
        lic = LicenceRecord(
            licence_type=LicenceType.ELECTRICITY_SUPPLY,
            licence_number="ES-12345",
            granted_date=dt.date(2019, 1, 1),
        )
        tracker.register_licence(lic)
        assert tracker.total_licences() == 1

    def test_add_and_retrieve_milestone(self):
        tracker = SupplierLicenceRenewalTracker()
        m = make_milestone(due=dt.date(2024, 1, 10))
        tracker.add_milestone(m)
        overdue = tracker.overdue_milestones(dt.date(2024, 1, 20))
        assert len(overdue) == 1

    def test_overdue_excludes_submitted(self):
        tracker = SupplierLicenceRenewalTracker()
        m = make_milestone(due=dt.date(2024, 1, 10), submitted=dt.date(2024, 1, 20))
        tracker.add_milestone(m)
        assert len(tracker.overdue_milestones(dt.date(2024, 1, 25))) == 0

    def test_submit_milestone(self):
        tracker = SupplierLicenceRenewalTracker()
        tracker.add_milestone(make_milestone(due=dt.date(2024, 1, 10)))
        result = tracker.submit_milestone(
            ComplianceMilestoneType.SLC_SELF_REPORT,
            dt.date(2024, 1, 10),
            dt.date(2024, 1, 9),
        )
        assert result is not None
        assert result.is_submitted

    def test_upcoming_milestones(self):
        tracker = SupplierLicenceRenewalTracker()
        tracker.add_milestone(make_milestone(due=dt.date(2024, 2, 1)))  # in window
        tracker.add_milestone(make_milestone(due=dt.date(2024, 4, 1)))  # outside window
        upcoming = tracker.upcoming_milestones(dt.date(2024, 1, 15), within_days=30)
        assert len(upcoming) == 1

    def test_late_submissions(self):
        tracker = SupplierLicenceRenewalTracker()
        late = make_milestone(due=dt.date(2024, 1, 10), submitted=dt.date(2024, 1, 20))
        on_time = make_milestone(due=dt.date(2024, 2, 1), submitted=dt.date(2024, 1, 30))
        tracker.add_milestone(late)
        tracker.add_milestone(on_time)
        assert len(tracker.late_submissions()) == 1

    def test_licence_compliance_summary(self):
        tracker = SupplierLicenceRenewalTracker()
        lic = LicenceRecord(LicenceType.ELECTRICITY_SUPPLY, "ES-001", dt.date(2019,1,1))
        tracker.register_licence(lic)
        s = tracker.licence_compliance_summary(DATE)
        assert "Licence Compliance" in s
