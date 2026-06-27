import datetime as dt
import pytest
from company.market.mhhs_tracker import (
    MHHSMilestoneRecord, MHHSMilestone, MHHSMilestoneStatus,
    MHHSReadinessSnapshot, MHHSReadinessTracker,
)


def make_milestone(milestone=MHHSMilestone.DCC_CONNECTIVITY,
                   target=dt.date(2024, 6, 30),
                   status=MHHSMilestoneStatus.IN_PROGRESS,
                   completed=None):
    return MHHSMilestoneRecord(
        milestone=milestone, target_date=target,
        status=status, completion_date=completed,
    )


def make_snapshot(date=dt.date(2024, 6, 30), hh_pct=45.0, smets2_pct=80.0,
                  migrated=5000, total_nhh=10000):
    return MHHSReadinessSnapshot(
        snapshot_date=date,
        pct_customers_hh_settled=hh_pct,
        pct_smets2_dcc_connected=smets2_pct,
        nhh_profiles_migrated=migrated,
        total_nhh_customers=total_nhh,
    )


class TestMHHSMilestoneRecord:
    def test_is_overdue_false_complete(self):
        m = make_milestone(status=MHHSMilestoneStatus.COMPLETE)
        assert m.is_overdue(dt.date(2025, 1, 1)) is False

    def test_is_overdue_false_within_target(self):
        m = make_milestone(target=dt.date(2024, 12, 31))
        assert m.is_overdue(dt.date(2024, 12, 1)) is False

    def test_is_overdue_true_past_target(self):
        m = make_milestone(target=dt.date(2024, 6, 30))
        assert m.is_overdue(dt.date(2024, 8, 1)) is True

    def test_is_overdue_false_failed(self):
        m = make_milestone(status=MHHSMilestoneStatus.FAILED)
        assert m.is_overdue(dt.date(2025, 1, 1)) is False

    def test_days_to_target(self):
        m = make_milestone(target=dt.date(2024, 12, 31))
        assert m.days_to_target(dt.date(2024, 12, 1)) == 30

    def test_frozen(self):
        m = make_milestone()
        with pytest.raises((AttributeError, TypeError)):
            m.status = MHHSMilestoneStatus.COMPLETE


class TestMHHSReadinessSnapshot:
    def test_migration_completion_pct(self):
        s = make_snapshot(migrated=5000, total_nhh=10000)
        assert s.migration_completion_pct == 50.0

    def test_migration_completion_zero_nhh(self):
        s = make_snapshot(migrated=0, total_nhh=0)
        assert s.migration_completion_pct == 100.0

    def test_is_on_track_before_golive(self):
        s = make_snapshot(date=dt.date(2024, 6, 1), migrated=9000, total_nhh=10000)
        assert isinstance(s.is_on_track, bool)


class TestMHHSReadinessTracker:
    def test_record_milestone(self):
        tracker = MHHSReadinessTracker()
        m = make_milestone()
        tracker.record_milestone(m)
        assert m in tracker.complete_milestones() or m.milestone in (
            mm.milestone for mm in tracker._milestones.values())

    def test_update_milestone_status(self):
        tracker = MHHSReadinessTracker()
        tracker.record_milestone(make_milestone(milestone=MHHSMilestone.DCC_CONNECTIVITY))
        result = tracker.update_milestone(MHHSMilestone.DCC_CONNECTIVITY,
                                          MHHSMilestoneStatus.COMPLETE,
                                          dt.date(2024, 5, 31))
        assert result.status == MHHSMilestoneStatus.COMPLETE
        assert result.completion_date == dt.date(2024, 5, 31)

    def test_update_raises_not_found(self):
        tracker = MHHSReadinessTracker()
        with pytest.raises(ValueError):
            tracker.update_milestone(MHHSMilestone.DCC_CONNECTIVITY,
                                     MHHSMilestoneStatus.COMPLETE)

    def test_record_snapshot(self):
        tracker = MHHSReadinessTracker()
        tracker.record_snapshot(make_snapshot())
        assert tracker.latest_snapshot() is not None

    def test_latest_snapshot_most_recent(self):
        tracker = MHHSReadinessTracker()
        tracker.record_snapshot(make_snapshot(date=dt.date(2024, 1, 1)))
        tracker.record_snapshot(make_snapshot(date=dt.date(2024, 6, 1)))
        assert tracker.latest_snapshot().snapshot_date == dt.date(2024, 6, 1)

    def test_overdue_milestones(self):
        tracker = MHHSReadinessTracker()
        tracker.record_milestone(make_milestone(
            milestone=MHHSMilestone.DCC_CONNECTIVITY,
            target=dt.date(2024, 6, 30)))
        assert len(tracker.overdue_milestones(dt.date(2024, 8, 1))) == 1
        assert len(tracker.overdue_milestones(dt.date(2024, 5, 1))) == 0

    def test_complete_milestones(self):
        tracker = MHHSReadinessTracker()
        tracker.record_milestone(make_milestone(
            milestone=MHHSMilestone.DCC_CONNECTIVITY,
            status=MHHSMilestoneStatus.COMPLETE))
        tracker.record_milestone(make_milestone(
            milestone=MHHSMilestone.HH_DATA_INGESTION,
            status=MHHSMilestoneStatus.IN_PROGRESS))
        assert len(tracker.complete_milestones()) == 1

    def test_at_risk_milestones(self):
        tracker = MHHSReadinessTracker()
        tracker.record_milestone(make_milestone(
            milestone=MHHSMilestone.DCC_CONNECTIVITY,
            status=MHHSMilestoneStatus.AT_RISK))
        assert len(tracker.at_risk_milestones()) == 1

    def test_readiness_rag_green(self):
        tracker = MHHSReadinessTracker()
        tracker.record_milestone(make_milestone(
            milestone=MHHSMilestone.DCC_CONNECTIVITY,
            target=dt.date(2025, 12, 31),
            status=MHHSMilestoneStatus.IN_PROGRESS))
        assert tracker.readiness_rag(dt.date(2025, 1, 1)) == "GREEN"

    def test_readiness_rag_red_overdue(self):
        tracker = MHHSReadinessTracker()
        tracker.record_milestone(make_milestone(
            milestone=MHHSMilestone.DCC_CONNECTIVITY,
            target=dt.date(2024, 6, 30),
            status=MHHSMilestoneStatus.IN_PROGRESS))
        assert tracker.readiness_rag(dt.date(2024, 8, 1)) == "RED"

    def test_readiness_rag_amber_at_risk(self):
        tracker = MHHSReadinessTracker()
        tracker.record_milestone(make_milestone(
            milestone=MHHSMilestone.DCC_CONNECTIVITY,
            target=dt.date(2025, 12, 31),
            status=MHHSMilestoneStatus.AT_RISK))
        assert tracker.readiness_rag(dt.date(2025, 1, 1)) == "AMBER"

    def test_mhhs_summary_keys(self):
        tracker = MHHSReadinessTracker()
        s = tracker.mhhs_summary(dt.date(2024, 6, 1))
        for k in ("total_milestones", "complete", "overdue", "at_risk",
                  "readiness_rag", "hh_settled_pct"):
            assert k in s

    def test_mhhs_summary_no_snapshot(self):
        tracker = MHHSReadinessTracker()
        s = tracker.mhhs_summary(dt.date(2024, 6, 1))
        assert s["hh_settled_pct"] == 0.0
