import pytest
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


def test_obligation_not_found():
    t = _tracker()
    assert t.obligation("nonexistent_obligation") is None


def test_submissions_for_filter():
    t = _tracker()
    t.record_submission(ObligationSubmission("price_cap_compliance", "2024-M01", "2024-02-10", "2024-02-15"))
    t.record_submission(ObligationSubmission("complaint_report", "2024-Q1", "2024-04-25", "2024-04-30"))
    subs = t.submissions_for("price_cap_compliance")
    assert len(subs) == 1
    assert subs[0].obligation_name == "price_cap_compliance"


def test_submissions_for_empty():
    t = _tracker()
    assert t.submissions_for("billing_accuracy_audit") == []


def test_penalty_multiple_late():
    t = _tracker()
    t.record_submission(ObligationSubmission("annual_business_report", "2024", "2025-04-01", "2025-03-31"))
    t.record_submission(ObligationSubmission("complaint_report", "2024-Q1", "2024-05-05", "2024-04-30"))
    # annual_business_report: £10M; complaint_report: £500k
    assert t.total_potential_penalty_gbp() == pytest.approx(10_500_000)


def test_on_time_rate_all_on_time():
    t = _tracker()
    t.record_submission(ObligationSubmission("price_cap_compliance", "2024-M01", "2024-02-10", "2024-02-15"))
    t.record_submission(ObligationSubmission("price_cap_compliance", "2024-M02", "2024-03-10", "2024-03-15"))
    assert t.on_time_rate_pct() == 100.0


def test_submission_on_exact_deadline_is_on_time():
    t = _tracker()
    sub = ObligationSubmission(
        obligation_name="price_cap_compliance",
        reference_period="2024-M03",
        submission_date="2024-04-15",
        deadline_date="2024-04-15",
    )
    t.record_submission(sub)
    assert sub.is_on_time is True
    assert sub.days_late == 0


def test_annual_business_report_max_penalty():
    t = _tracker()
    ob = t.obligation("annual_business_report")
    assert ob.max_penalty_gbp == 10_000_000


def test_summary_includes_potential_penalty():
    t = _tracker()
    t.record_submission(ObligationSubmission("annual_business_report", "2024", "2025-04-01", "2025-03-31"))
    s = t.summary()
    assert "potential_penalty_gbp" in s
    assert s["potential_penalty_gbp"] == 10_000_000


def test_all_obligation_names_present():
    t = _tracker()
    names = {ob.name for ob in t.all_obligations()}
    for expected in ("price_cap_compliance", "billing_accuracy_audit", "complaint_report",
                     "annual_business_report", "smart_meter_progress", "debt_difficulty_report"):
        assert expected in names


def test_no_penalty_when_all_on_time():
    t = _tracker()
    t.record_submission(ObligationSubmission("complaint_report", "2024-Q1", "2024-04-25", "2024-04-30"))
    assert t.total_potential_penalty_gbp() == 0.0
