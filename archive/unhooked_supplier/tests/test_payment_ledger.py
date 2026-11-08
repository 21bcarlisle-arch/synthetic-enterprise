"""Tests for payment_ledger.py -- PaymentLedger and PaymentRecord."""
import pytest
from company.billing.payment_ledger import (
    PaymentLedger,
    PaymentRecord,
    PaymentMethodType,
    PaymentOutcome,
)


def _rec(payment_id, account_id, amount, method, outcome, inv_nums=()):
    return PaymentRecord(
        payment_id=payment_id,
        account_id=account_id,
        payment_date="2023-01-28",
        amount_gbp=amount,
        method=method,
        outcome=outcome,
        reference=f"REF-{payment_id}",
        invoice_numbers=tuple(inv_nums),
    )


def _dd_success(payment_id, account_id, amount, inv_nums=()):
    return _rec(payment_id, account_id, amount, PaymentMethodType.DIRECT_DEBIT, PaymentOutcome.SUCCESS, inv_nums)

def _dd_failed(payment_id, account_id, amount):
    return _rec(payment_id, account_id, amount, PaymentMethodType.DIRECT_DEBIT, PaymentOutcome.FAILED)


# --- PaymentMethodType ---

def test_direct_debit_is_automated():
    assert PaymentMethodType.DIRECT_DEBIT.is_automated is True

def test_prepayment_is_automated():
    assert PaymentMethodType.PREPAYMENT_METER.is_automated is True

def test_bacs_not_automated():
    assert PaymentMethodType.BACS.is_automated is False

def test_method_customer_label():
    assert PaymentMethodType.DIRECT_DEBIT.customer_label == "Direct Debit"
    assert PaymentMethodType.BACS.customer_label == "BACS Transfer"


# --- PaymentOutcome ---

def test_success_is_terminal():
    assert PaymentOutcome.SUCCESS.is_terminal is True

def test_pending_not_terminal():
    assert PaymentOutcome.PENDING.is_terminal is False

def test_outcome_customer_label():
    assert PaymentOutcome.FAILED.customer_label == "Failed"


# --- PaymentRecord ---

def test_record_is_successful():
    r = _dd_success("P1", "C1", 134.50, (1, 2))
    assert r.is_successful is True
    assert r.is_failed is False

def test_record_is_failed():
    r = _dd_failed("P2", "C1", 134.50)
    assert r.is_failed is True
    assert r.is_successful is False

def test_record_invoice_numbers_tuple():
    r = _dd_success("P1", "C1", 100.0, (7, 8))
    assert 7 in r.invoice_numbers
    assert 9 not in r.invoice_numbers


# --- PaymentLedger ---

def test_ledger_record_and_retrieve():
    ledger = PaymentLedger()
    r = _dd_success("P1", "C1", 134.50)
    ledger.record(r)
    recs = ledger.payments_for_account("C1")
    assert len(recs) == 1
    assert recs[0].payment_id == "P1"

def test_ledger_successful_total():
    ledger = PaymentLedger()
    ledger.record(_dd_success("P1", "C1", 50.0))
    ledger.record(_dd_success("P2", "C1", 80.0))
    ledger.record(_dd_failed("P3", "C1", 30.0))
    assert ledger.successful_total_gbp("C1") == pytest.approx(130.0)

def test_ledger_failed_payments():
    ledger = PaymentLedger()
    ledger.record(_dd_success("P1", "C1", 50.0))
    ledger.record(_dd_failed("P2", "C1", 30.0))
    assert len(ledger.failed_payments("C1")) == 1

def test_ledger_summary_in_credit():
    ledger = PaymentLedger()
    ledger.record(_dd_success("P1", "C1", 150.0))
    summary = ledger.ledger_summary("C1", total_billed_gbp=134.50)
    assert summary["in_credit"] is True
    assert summary["balance_gbp"] == pytest.approx(15.50, abs=0.01)
    assert summary["amount_owing_gbp"] == 0.0

def test_ledger_summary_amount_owing():
    ledger = PaymentLedger()
    ledger.record(_dd_success("P1", "C1", 100.0))
    summary = ledger.ledger_summary("C1", total_billed_gbp=134.50)
    assert summary["in_credit"] is False
    assert summary["amount_owing_gbp"] == pytest.approx(34.50, abs=0.01)

def test_ledger_method_breakdown():
    ledger = PaymentLedger()
    ledger.record(_dd_success("P1", "C1", 50.0))
    ledger.record(_dd_failed("P2", "C1", 50.0))
    ledger.record(_rec("P3", "C1", 50.0, PaymentMethodType.BACS, PaymentOutcome.SUCCESS))
    breakdown = ledger.payment_method_breakdown("C1")
    assert "direct_debit" in breakdown
    assert breakdown["direct_debit"]["success"] == 1
    assert breakdown["direct_debit"]["failed"] == 1
    assert "bacs" in breakdown

def test_ledger_portfolio_summary():
    ledger = PaymentLedger()
    ledger.record(_dd_success("P1", "C1", 100.0))
    ledger.record(_dd_failed("P2", "C2", 50.0))
    summary = ledger.portfolio_summary()
    assert summary["total_payment_count"] == 2
    assert summary["successful_gbp"] == pytest.approx(100.0)
    assert summary["failed_gbp"] == pytest.approx(50.0)
    assert summary["failure_rate_pct"] == pytest.approx(50.0)

def test_ledger_all_accounts():
    ledger = PaymentLedger()
    ledger.record(_dd_success("P1", "C1", 100.0))
    ledger.record(_dd_success("P2", "C2", 80.0))
    assert set(ledger.all_accounts()) == {"C1", "C2"}

def test_ledger_payments_by_date_sorted():
    ledger = PaymentLedger()
    r1 = PaymentRecord("P2", "C1", "2023-02-01", 50.0,
                       PaymentMethodType.DIRECT_DEBIT, PaymentOutcome.SUCCESS, "REF", ())
    r2 = PaymentRecord("P1", "C1", "2023-01-01", 50.0,
                       PaymentMethodType.DIRECT_DEBIT, PaymentOutcome.SUCCESS, "REF", ())
    ledger.record(r1)
    ledger.record(r2)
    by_date = ledger.payments_by_date("C1")
    assert by_date[0].payment_date < by_date[1].payment_date

def test_ledger_isolation_between_accounts():
    ledger = PaymentLedger()
    ledger.record(_dd_success("P1", "C1", 100.0))
    ledger.record(_dd_success("P2", "C2", 200.0))
    assert ledger.successful_total_gbp("C1") == pytest.approx(100.0)
    assert ledger.successful_total_gbp("C2") == pytest.approx(200.0)
