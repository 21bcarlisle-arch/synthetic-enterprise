import pytest
from datetime import date
from company.crm.complaints import (
    ComplaintCategory, ComplaintStatus, Complaint, ComplaintBook,
    OMBUDSMAN_ESCALATION_DAYS,
)


@pytest.fixture
def book():
    return ComplaintBook()


@pytest.fixture
def billing_complaint(book):
    return book.raise_complaint(
        customer_id="C001",
        category=ComplaintCategory.BILLING,
        opened_date=date(2022, 1, 10),
        description="Overcharged in January",
    )


def test_raise_complaint_creates_open_record(billing_complaint):
    assert billing_complaint.complaint_id == 1
    assert billing_complaint.status == ComplaintStatus.OPEN
    assert billing_complaint.is_open is True


def test_days_open_no_resolution(billing_complaint):
    as_of = date(2022, 2, 10)
    assert billing_complaint.days_open(as_of) == 31


def test_days_open_resolved(book, billing_complaint):
    book.resolve(billing_complaint.complaint_id, date(2022, 1, 20))
    assert billing_complaint.days_open(date(2022, 3, 1)) == 10


def test_not_eligible_for_ombudsman_below_threshold(billing_complaint):
    as_of = date(2022, 2, 28)
    assert billing_complaint.eligible_for_ombudsman(as_of) is False


def test_eligible_for_ombudsman_at_threshold(billing_complaint):
    as_of = date(2022, 3, 7)
    assert billing_complaint.days_open(as_of) == 56
    assert billing_complaint.eligible_for_ombudsman(as_of) is True


def test_resolved_complaint_not_eligible_for_ombudsman(book, billing_complaint):
    book.resolve(billing_complaint.complaint_id, date(2022, 2, 1))
    as_of = date(2022, 5, 1)
    assert billing_complaint.eligible_for_ombudsman(as_of) is False


def test_resolve_sets_fields(book, billing_complaint):
    ok = book.resolve(
        billing_complaint.complaint_id,
        resolved_date=date(2022, 1, 25),
        resolution_summary="Credit issued",
        redress_gbp=45.0,
    )
    assert ok is True
    assert billing_complaint.status == ComplaintStatus.RESOLVED
    assert billing_complaint.redress_gbp == pytest.approx(45.0)
    assert billing_complaint.is_open is False


def test_escalate_to_ombudsman(book, billing_complaint):
    as_of = date(2022, 3, 10)
    ok = book.escalate_to_ombudsman(billing_complaint.complaint_id, as_of)
    assert ok is True
    assert billing_complaint.status == ComplaintStatus.ESCALATED_TO_OMBUDSMAN
    assert billing_complaint.escalated_date == as_of


def test_escalate_fails_if_not_eligible(book, billing_complaint):
    as_of = date(2022, 1, 20)
    ok = book.escalate_to_ombudsman(billing_complaint.complaint_id, as_of)
    assert ok is False


def test_overdue_for_ombudsman(book):
    book.raise_complaint("C001", ComplaintCategory.BILLING, date(2022, 1, 1), "")
    book.raise_complaint("C002", ComplaintCategory.METERING, date(2022, 2, 28), "")
    as_of = date(2022, 3, 15)
    overdue = book.overdue_for_ombudsman(as_of)
    assert len(overdue) == 1
    assert overdue[0].customer_id == "C001"


def test_annual_summary_empty(book):
    summary = book.annual_summary(2020)
    assert summary["total"] == 0
    assert summary["total_redress_gbp"] == 0.0


def test_annual_summary_with_data(book):
    book.raise_complaint("C001", ComplaintCategory.BILLING, date(2022, 1, 10), "")
    book.raise_complaint("C002", ComplaintCategory.SWITCHING, date(2022, 3, 5), "")
    book.raise_complaint("C003", ComplaintCategory.PPM, date(2022, 6, 1), "")
    book.resolve(1, date(2022, 1, 30), "Credit applied", redress_gbp=50.0)
    book.resolve(2, date(2022, 3, 20))
    summary = book.annual_summary(2022)
    assert summary["total"] == 3
    assert summary["resolved"] == 2
    assert summary["outstanding"] == 1
    assert summary["total_redress_gbp"] == pytest.approx(50.0)
    assert summary["by_category"]["billing"] == 1
    assert summary["by_category"]["ppm"] == 1


# --- Phase LR depth tests ---

def test_complaint_id_stored(billing_complaint):
    assert billing_complaint.complaint_id == 1


def test_customer_id_stored(billing_complaint):
    assert billing_complaint.customer_id == "C001"


def test_category_stored(billing_complaint):
    assert billing_complaint.category == ComplaintCategory.BILLING


def test_opened_date_stored(billing_complaint):
    assert billing_complaint.opened_date == date(2022, 1, 10)


def test_description_stored(billing_complaint):
    assert billing_complaint.description == "Overcharged in January"


def test_redress_default_zero(billing_complaint):
    assert billing_complaint.redress_gbp == pytest.approx(0.0)


def test_resolved_date_default_none(billing_complaint):
    assert billing_complaint.resolved_date is None


def test_resolution_summary_default_none(billing_complaint):
    assert billing_complaint.resolution_summary is None


def test_escalated_date_default_none(billing_complaint):
    assert billing_complaint.escalated_date is None


def test_ombudsman_escalation_days_constant():
    assert OMBUDSMAN_ESCALATION_DAYS == 56
