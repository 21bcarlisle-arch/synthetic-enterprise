"""Tests for C3: Payment processing and debt aging (Phase 67)."""

import pytest
from company.billing.invoice import create_invoice, create_schema, get_invoice
from company.billing.payments import (
    age_debt,
    debt_aging_summary,
    reconcile_payment,
    reconcile_payments,
)


@pytest.fixture
def db(tmp_path):
    return tmp_path / 'invoices.db'


def _bill(customer_id='C1', period_end='2016-01-31', amount=100.0):
    return {
        'customer_id': customer_id,
        'period_start': '2016-01-01',
        'period_end': period_end,
        'total_amount_gbp': amount,
        'total_consumption_kwh': 1500.0,
        'clarity_score': 0.85,
        'bill_shock_pct': None,
    }


def _payment(customer_id='C1', period_end='2016-01-31', amount=105.0):
    return {
        'event_type': 'payment_received_event',
        'customer_id': customer_id,
        'bill_period_end': period_end,
        'amount_gbp': amount,
    }


def test_reconcile_marks_paid_when_full_payment(db):
    num = create_invoice(_bill(), db)
    result = reconcile_payment(_payment(), db)
    assert result == 'paid'
    assert get_invoice(num, db)['payment_status'] == 'paid'


def test_reconcile_marks_partial_when_underpaid(db):
    num = create_invoice(_bill(), db)
    result = reconcile_payment(_payment(amount=50.0), db)
    assert result == 'partially_paid'
    assert get_invoice(num, db)['payment_status'] == 'partially_paid'


def test_reconcile_no_match_for_unknown_period(db):
    create_schema(db)
    result = reconcile_payment(_payment(period_end='2099-12-31'), db)
    assert result == 'no_match'


def test_reconcile_payments_counts_outcomes(db):
    create_invoice(_bill(period_end='2016-01-31'), db)
    create_invoice(_bill(period_end='2016-02-29'), db)
    events = [
        _payment(period_end='2016-01-31', amount=105.0),
        _payment(period_end='2016-02-29', amount=50.0),
        _payment(period_end='2099-12-31'),
    ]
    counts = reconcile_payments(events, db)
    assert counts['paid'] == 1
    assert counts['partially_paid'] == 1
    assert counts['no_match'] == 1


def test_reconcile_payments_skips_non_payment_events(db):
    create_invoice(_bill(), db)
    events = [
        {'event_type': 'billing_event', 'customer_id': 'C1',
         'bill_period_end': '2016-01-31', 'amount_gbp': 100.0},
        _payment(),
    ]
    counts = reconcile_payments(events, db)
    assert counts['paid'] == 1


def test_reconcile_idempotent_on_paid_invoice(db):
    create_invoice(_bill(), db)
    reconcile_payment(_payment(), db)
    result = reconcile_payment(_payment(), db)
    assert result == 'paid'


def test_age_debt_flags_overdue_as_bad_debt(db):
    num = create_invoice(_bill(period_end='2016-01-31'), db)
    result = age_debt(db, '2016-07-01')
    bad = [r for r in result if r['invoice_number'] == num]
    assert bad and bad[0]['new_status'] == 'bad_debt'
    assert get_invoice(num, db)['payment_status'] == 'bad_debt'


def test_age_debt_current_invoice_stays_unpaid(db):
    num = create_invoice(_bill(period_end='2016-01-31'), db)
    result = age_debt(db, '2016-02-10')
    found = [r for r in result if r['invoice_number'] == num]
    assert found and found[0]['new_status'] == 'unpaid'
    assert get_invoice(num, db)['payment_status'] == 'unpaid'


def test_debt_aging_summary_buckets(db):
    create_invoice(_bill(period_end='2016-01-31', amount=100.0), db)
    create_invoice(_bill(period_end='2015-01-31', amount=200.0), db)
    summary = debt_aging_summary(db, '2016-06-01')
    assert summary['current']['count'] >= 0
    assert 'bad_debt' in summary
    assert summary['bad_debt']['count'] >= 1


def test_debt_aging_empty_db_returns_zeros(db):
    create_schema(db)
    summary = debt_aging_summary(db, '2016-01-01')
    for bucket in ('current', 'late', 'overdue', 'bad_debt'):
        assert bucket in summary
        assert summary[bucket]['count'] == 0
        assert summary[bucket]['amount_gbp'] == 0.0


# --- Phase KY depth tests ---

def test_bad_debt_days_constant():
    from company.billing.payments import BAD_DEBT_DAYS
    assert BAD_DEBT_DAYS == 90


def test_reconcile_returns_string(db):
    event = {
        "event_type": "payment_received_event",
        "customer_id": "C001",
        "bill_period_end": "2022-03-31",
        "amount_gbp": 0.0,
    }
    result = reconcile_payment(event, db)
    assert isinstance(result, str)


def test_reconcile_no_match_returns_no_match(db):
    event = {
        "event_type": "payment_received_event",
        "customer_id": "UNKNOWN",
        "bill_period_end": "2099-01-31",
        "amount_gbp": 100.0,
    }
    assert reconcile_payment(event, db) == "no_match"


def test_reconcile_payments_returns_dict(db):
    result = reconcile_payments([], db)
    assert isinstance(result, dict)


def test_reconcile_payments_has_no_match_key(db):
    result = reconcile_payments([], db)
    assert "no_match" in result


def test_reconcile_payments_has_paid_key(db):
    result = reconcile_payments([], db)
    assert "paid" in result


def test_reconcile_payments_empty_events_all_zero(db):
    result = reconcile_payments([], db)
    assert result["paid"] == 0 and result["no_match"] == 0


def test_age_debt_returns_list(db):
    result = age_debt(db, "2022-06-01")
    assert isinstance(result, list)


def test_debt_aging_summary_returns_dict(db):
    result = debt_aging_summary(db, "2022-06-01")
    assert isinstance(result, dict)


def test_debt_aging_summary_has_current_key(db):
    result = debt_aging_summary(db, "2022-06-01")
    assert "current" in result
