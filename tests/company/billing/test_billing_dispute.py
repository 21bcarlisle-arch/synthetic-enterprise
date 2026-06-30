"""Tests for Billing Dispute Resolution Book (Phase FC)."""
import datetime as dt
import pytest
from company.billing.billing_dispute import (
    DisputeStatus, DisputeReason, BillingDispute, BillingDisputeBook,
)

DATE = dt.date(2024, 3, 1)
ACCT = "C1"


def make_dispute(amount=250.0, reason=DisputeReason.ESTIMATED_BILL,
                 status=DisputeStatus.RAISED, credit=0.0, date=DATE):
    return BillingDispute(
        dispute_id="DISP-00001", account_id=ACCT,
        raised_at=date, reason=reason,
        disputed_amount_gbp=amount, status=status, credit_applied_gbp=credit,
    )


class TestBillingDispute:
    def test_is_open_raised(self):
        assert make_dispute().is_open

    def test_is_open_investigating(self):
        assert make_dispute(status=DisputeStatus.INVESTIGATING).is_open

    def test_not_open_resolved(self):
        d = make_dispute(status=DisputeStatus.RESOLVED_IN_SUPPLIER_FAVOUR)
        assert not d.is_open

    def test_can_disconnect_resolved(self):
        d = make_dispute(status=DisputeStatus.RESOLVED_IN_SUPPLIER_FAVOUR)
        assert d.can_disconnect

    def test_cannot_disconnect_open(self):
        assert not make_dispute(status=DisputeStatus.INVESTIGATING).can_disconnect

    def test_net_disputed_amount(self):
        d = make_dispute(amount=300.0, credit=100.0)
        assert d.net_disputed_amount_gbp == pytest.approx(200.0)

    def test_final_response_overdue(self):
        d = make_dispute(date=dt.date(2023, 1, 1))
        assert d.is_final_response_overdue(DATE)

    def test_final_response_not_overdue(self):
        assert not make_dispute().is_final_response_overdue(DATE)

    def test_not_overdue_if_resolved(self):
        d = make_dispute(status=DisputeStatus.RESOLVED_IN_CUSTOMER_FAVOUR,
                         date=dt.date(2020, 1, 1))
        assert not d.is_final_response_overdue(DATE)

    def test_dispute_summary(self):
        s = make_dispute().dispute_summary()
        assert "DISP-00001" in s


class TestBillingDisputeBook:
    def test_raise_auto_id(self):
        book = BillingDisputeBook()
        d = book.raise_dispute(ACCT, DisputeReason.ESTIMATED_BILL, 100.0, DATE)
        assert d.dispute_id == "DISP-00001"

    def test_open_disputes(self):
        book = BillingDisputeBook()
        book.raise_dispute(ACCT, DisputeReason.ESTIMATED_BILL, 100.0, DATE)
        assert len(book.open_disputes()) == 1

    def test_update_to_resolved(self):
        book = BillingDisputeBook()
        d = book.raise_dispute(ACCT, DisputeReason.ESTIMATED_BILL, 100.0, DATE)
        updated = book.update_dispute(d.dispute_id,
                                      DisputeStatus.RESOLVED_IN_CUSTOMER_FAVOUR, DATE)
        assert not updated.is_open
        assert len(book.open_disputes()) == 0

    def test_overdue_final_responses(self):
        book = BillingDisputeBook()
        book.raise_dispute(ACCT, DisputeReason.ESTIMATED_BILL, 100.0, dt.date(2023, 1, 1))
        assert len(book.overdue_final_responses(DATE)) == 1

    def test_accounts_blocked_from_disconnection(self):
        book = BillingDisputeBook()
        book.raise_dispute(ACCT, DisputeReason.ESTIMATED_BILL, 100.0, DATE)
        blocked = book.accounts_blocked_from_disconnection()
        assert ACCT in blocked

    def test_total_disputed_amount(self):
        book = BillingDisputeBook()
        book.raise_dispute(ACCT, DisputeReason.TARIFF_ERROR, 200.0, DATE)
        assert book.total_disputed_amount_gbp() == pytest.approx(200.0)

    def test_dispute_book_summary(self):
        book = BillingDisputeBook()
        book.raise_dispute(ACCT, DisputeReason.METER_ERROR, 150.0, DATE)
        s = book.dispute_book_summary(DATE)
        assert "Billing Disputes" in s
