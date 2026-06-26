import pytest
from datetime import date
from company.billing.meter_dispute import (
    DisputeType, DisputeStatus, MeterDispute, MeterDisputeBook,
)


@pytest.fixture
def book():
    return MeterDisputeBook()


@pytest.fixture
def sample_dispute(book):
    return book.open_dispute(
        customer_id="C001",
        bill_reference="BILL-2022-03",
        dispute_type=DisputeType.ESTIMATED_READ,
        billed_read_kwh=5000.0,
        claimed_read_kwh=4200.0,
        opened_date=date(2022, 3, 15),
    )


def test_open_dispute_creates_record(book, sample_dispute):
    assert sample_dispute.dispute_id == 1
    assert sample_dispute.customer_id == "C001"
    assert sample_dispute.status == DisputeStatus.OPEN


def test_disputed_kwh(sample_dispute):
    assert sample_dispute.disputed_kwh == pytest.approx(800.0)


def test_is_open_true_for_new_dispute(sample_dispute):
    assert sample_dispute.is_open is True


def test_update_status_to_under_review(book, sample_dispute):
    ok = book.update_status(sample_dispute.dispute_id, DisputeStatus.UNDER_REVIEW)
    assert ok is True
    assert sample_dispute.status == DisputeStatus.UNDER_REVIEW
    assert sample_dispute.is_open is True


def test_update_status_unknown_id_returns_false(book):
    result = book.update_status(999, DisputeStatus.UNDER_REVIEW)
    assert result is False


def test_resolve_accepted(book, sample_dispute):
    ok = book.resolve(
        sample_dispute.dispute_id,
        accepted=True,
        resolved_date=date(2022, 3, 25),
        credit_applied_gbp=48.50,
        notes="meter read confirmed lower",
    )
    assert ok is True
    assert sample_dispute.status == DisputeStatus.RESOLVED_ACCEPTED
    assert sample_dispute.credit_applied_gbp == pytest.approx(48.50)
    assert sample_dispute.is_open is False


def test_resolve_rejected(book, sample_dispute):
    book.resolve(
        sample_dispute.dispute_id,
        accepted=False,
        resolved_date=date(2022, 3, 25),
    )
    assert sample_dispute.status == DisputeStatus.RESOLVED_REJECTED
    assert sample_dispute.credit_applied_gbp == pytest.approx(0.0)
    assert sample_dispute.is_open is False


def test_outstanding_disputes_excludes_resolved(book, sample_dispute):
    book.open_dispute(
        "C002", "BILL-2022-04", DisputeType.METER_FAULT, 3000.0, 2800.0, date(2022, 4, 1)
    )
    book.resolve(sample_dispute.dispute_id, True, date(2022, 3, 25))
    outstanding = book.outstanding_disputes()
    assert len(outstanding) == 1
    assert outstanding[0].customer_id == "C002"


def test_disputes_for_customer(book, sample_dispute):
    book.open_dispute(
        "C002", "BILL-2022-05", DisputeType.ACTUAL_TOO_HIGH,
        8000.0, 6000.0, date(2022, 5, 1)
    )
    c1_disputes = book.disputes_for_customer("C001")
    assert len(c1_disputes) == 1


def test_annual_summary_no_disputes(book):
    summary = book.annual_summary(2020)
    assert summary["total"] == 0
    assert summary["total_credit_gbp"] == 0.0


def test_annual_summary_with_mixed_outcomes(book):
    book.open_dispute(
        "C001", "BILL-2022-01", DisputeType.ESTIMATED_READ,
        5000.0, 4200.0, date(2022, 1, 10)
    )
    book.open_dispute(
        "C002", "BILL-2022-02", DisputeType.PRIOR_READING_ERROR,
        3000.0, 2500.0, date(2022, 2, 5)
    )
    book.resolve(1, True, date(2022, 1, 20), credit_applied_gbp=35.0)
    book.resolve(2, False, date(2022, 2, 15))

    summary = book.annual_summary(2022)
    assert summary["total"] == 2
    assert summary["accepted"] == 1
    assert summary["rejected"] == 1
    assert summary["outstanding"] == 0
    assert summary["total_credit_gbp"] == pytest.approx(35.0)


def test_auto_increment_ids(book):
    d1 = book.open_dispute("C001", "B1", DisputeType.ESTIMATED_READ, 100.0, 90.0, date(2022, 1, 1))
    d2 = book.open_dispute("C001", "B2", DisputeType.METER_FAULT, 200.0, 180.0, date(2022, 2, 1))
    assert d1.dispute_id == 1
    assert d2.dispute_id == 2
