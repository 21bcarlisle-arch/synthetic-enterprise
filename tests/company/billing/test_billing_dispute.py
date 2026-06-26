import datetime as dt
import pytest
from company.billing.billing_dispute import (
    BillingDisputeType, BillingDisputeStatus, BillingDispute, BillingDisputeBook
)

D = dt.date


def test_raise_dispute():
    book = BillingDisputeBook()
    d = book.raise_dispute('C001', 'INV-001', BillingDisputeType.WRONG_TARIFF_APPLIED, 75.0, D(2023, 5, 1))
    assert d.status == BillingDisputeStatus.OPEN
    assert d.is_open


def test_resolve_with_credit():
    book = BillingDisputeBook()
    d = book.raise_dispute('C002', 'INV-002', BillingDisputeType.INCORRECT_UNIT_RATE, 120.0, D(2023, 5, 1))
    resolved = book.resolve_with_credit(d.dispute_id, 120.0, D(2023, 5, 20))
    assert resolved.status == BillingDisputeStatus.RESOLVED_CREDIT
    assert resolved.credit_applied_gbp == 120.0
    assert not resolved.is_open


def test_resolve_no_change():
    book = BillingDisputeBook()
    d = book.raise_dispute('C003', 'INV-003', BillingDisputeType.EXIT_FEE_DISPUTE, 50.0, D(2023, 5, 1))
    resolved = book.resolve_no_change(d.dispute_id, D(2023, 5, 15))
    assert resolved.status == BillingDisputeStatus.RESOLVED_NO_CHANGE
    assert resolved.credit_applied_gbp == 0.0


def test_days_to_resolution():
    book = BillingDisputeBook()
    d = book.raise_dispute('C004', 'INV-004', BillingDisputeType.DUPLICATE_INVOICE, 200.0, D(2023, 5, 1))
    resolved = book.resolve_with_credit(d.dispute_id, 200.0, D(2023, 5, 11))
    assert resolved.days_to_resolution == 10


def test_open_disputes():
    book = BillingDisputeBook()
    d1 = book.raise_dispute('C005', 'INV-005', BillingDisputeType.MISSING_DISCOUNT, 30.0, D(2023, 5, 1))
    d2 = book.raise_dispute('C006', 'INV-006', BillingDisputeType.DIRECT_DEBIT_ERROR, 80.0, D(2023, 5, 1))
    book.resolve_no_change(d1.dispute_id, D(2023, 5, 14))
    assert len(book.open_disputes()) == 1


def test_total_credits_issued():
    book = BillingDisputeBook()
    d1 = book.raise_dispute('C007', 'INV-007', BillingDisputeType.WRONG_TARIFF_APPLIED, 100.0, D(2023, 5, 1))
    d2 = book.raise_dispute('C008', 'INV-008', BillingDisputeType.INCORRECT_UNIT_RATE, 50.0, D(2023, 5, 1))
    book.resolve_with_credit(d1.dispute_id, 100.0, D(2023, 5, 15))
    book.resolve_with_credit(d2.dispute_id, 50.0, D(2023, 5, 18))
    assert book.total_credits_issued_gbp() == pytest.approx(150.0)


def test_disputes_for_customer():
    book = BillingDisputeBook()
    book.raise_dispute('C009', 'INV-009', BillingDisputeType.STANDING_CHARGE_ERROR, 25.0, D(2023, 5, 1))
    book.raise_dispute('C009', 'INV-010', BillingDisputeType.DUPLICATE_INVOICE, 150.0, D(2023, 6, 1))
    assert len(book.disputes_for_customer('C009')) == 2


def test_annual_summary():
    book = BillingDisputeBook()
    d1 = book.raise_dispute('C010', 'INV-011', BillingDisputeType.WRONG_TARIFF_APPLIED, 80.0, D(2023, 5, 1))
    d2 = book.raise_dispute('C011', 'INV-012', BillingDisputeType.EXIT_FEE_DISPUTE, 60.0, D(2023, 5, 1))
    book.resolve_with_credit(d1.dispute_id, 80.0, D(2023, 5, 20))
    s = book.annual_summary()
    assert s['total_disputes'] == 2
    assert s['resolved_credit'] == 1
    assert s['total_credits_issued_gbp'] == pytest.approx(80.0)
    assert s['avg_days_to_resolution'] is not None
