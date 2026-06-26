"""Phase 137: Ofgem reporting obligations tracker tests."""

from company.regulatory.ofgem_obligations import (
    ObligationSubmission, OfgemObligationsTracker,
)


def _tracker():
    t = OfgemObligationsTracker()
    return t


def test_obligations_loaded():
    t = _tracker()
    assert len(t.all_obligations()) == 6


def test_obligation_lookup():
    t = _tracker()
    ob = t.obligation("complaint_report")
    assert ob is not None
    assert ob.slc_ref == "SLC 14C"
    assert ob.frequency == "quarterly"


def test_on_time_submission():
    t = _tracker()
    sub = ObligationSubmission(
        obligation_name="price_cap_compliance",
        reference_period="2024-M01",
        submission_date="2024-02-10",
        deadline_date="2024-02-15",
    )
    t.record_submission(sub)
    assert sub.is_on_time is True
    assert sub.days_late == 0


def test_late_submission():
    t = _tracker()
    sub = ObligationSubmission(
        obligation_name="complaint_report",
        reference_period="2024-Q1",
        submission_date="2024-05-05",
        deadline_date="2024-04-30",
    )
    t.record_submission(sub)
    assert sub.is_on_time is False
    assert sub.days_late == 5


def test_late_submissions_filter():
    t = _tracker()
    t.record_submission(ObligationSubmission("price_cap_compliance", "2024-M01", "2024-02-10", "2024-02-15"))
    t.record_submission(ObligationSubmission("complaint_report", "2024-Q1", "2024-05-05", "2024-04-30"))
    assert len(t.late_submissions()) == 1


def test_on_time_rate():
    t = _tracker()
    t.record_submission(ObligationSubmission("price_cap_compliance", "2024-M01", "2024-02-10", "2024-02-15"))
    t.record_submission(ObligationSubmission("complaint_report", "2024-Q1", "2024-05-05", "2024-04-30"))
    assert t.on_time_rate_pct() == 50.0


def test_penalty_accrues_for_late():
    t = _tracker()
    t.record_submission(ObligationSubmission("annual_business_report", "2024", "2025-04-01", "2025-03-31"))
    penalty = t.total_potential_penalty_gbp()
    assert penalty == 10_000_000


def test_summary_structure():
    t = _tracker()
    s = t.summary()
    for k in ("obligations_count", "total_submissions", "late_submissions", "on_time_rate_pct"):
        assert k in s


def test_empty_tracker_100pct_on_time():
    t = _tracker()
    assert t.on_time_rate_pct() == 100.0
    assert t.total_potential_penalty_gbp() == 0.0
