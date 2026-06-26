import datetime as dt
import pytest
from company.billing.payment_deferral import (
    DeferralStatus, DeferralReason, PaymentDeferral, PaymentDeferralBook
)

D = dt.date


def test_create_deferral():
    book = PaymentDeferralBook()
    d = book.create('C001', DeferralReason.FINANCIAL_HARDSHIP, 600.0,
                    D(2022, 1, 1), D(2022, 7, 1), 100.0)
    assert d.status == DeferralStatus.ACTIVE
    assert d.outstanding_gbp == 600.0
    assert d.deferral_days == 181


def test_record_repayment_partial():
    book = PaymentDeferralBook()
    d = book.create('C002', DeferralReason.JOB_LOSS, 300.0, D(2022, 1, 1), D(2022, 7, 1), 50.0)
    book.record_repayment(d.deferral_id, 100.0)
    assert d.outstanding_gbp == pytest.approx(200.0)
    assert d.status == DeferralStatus.ACTIVE


def test_record_repayment_completes_deferral():
    book = PaymentDeferralBook()
    d = book.create('C003', DeferralReason.ILLNESS, 200.0, D(2022, 1, 1), D(2022, 4, 1), 200.0)
    book.record_repayment(d.deferral_id, 200.0)
    assert d.status == DeferralStatus.COMPLETED
    assert d.outstanding_gbp == 0.0


def test_mark_defaulted():
    book = PaymentDeferralBook()
    d = book.create('C004', DeferralReason.BENEFIT_DELAY, 500.0, D(2022, 1, 1), D(2022, 6, 1), 80.0)
    book.mark_defaulted(d.deferral_id)
    assert d.status == DeferralStatus.DEFAULTED


def test_cancel_deferral():
    book = PaymentDeferralBook()
    d = book.create('C005', DeferralReason.COVID_19, 400.0, D(2020, 4, 1), D(2020, 10, 1), 67.0)
    book.cancel(d.deferral_id)
    assert d.status == DeferralStatus.CANCELLED


def test_active_deferrals():
    book = PaymentDeferralBook()
    d1 = book.create('C006', DeferralReason.JOB_LOSS, 200.0, D(2022, 1, 1), D(2022, 7, 1), 33.0)
    d2 = book.create('C007', DeferralReason.ILLNESS, 100.0, D(2022, 1, 1), D(2022, 4, 1), 100.0)
    book.record_repayment(d2.deferral_id, 100.0)
    active = book.active_deferrals()
    assert len(active) == 1
    assert active[0].customer_id == 'C006'


def test_overdue_deferrals():
    book = PaymentDeferralBook()
    d = book.create('C008', DeferralReason.FINANCIAL_HARDSHIP, 300.0, D(2022, 1, 1), D(2022, 3, 1), 100.0)
    assert len(book.overdue_deferrals(D(2022, 4, 1))) == 1
    assert len(book.overdue_deferrals(D(2022, 2, 1))) == 0


def test_total_deferred_outstanding():
    book = PaymentDeferralBook()
    book.create('C009', DeferralReason.FINANCIAL_HARDSHIP, 200.0, D(2022, 1, 1), D(2022, 7, 1), 33.0)
    book.create('C010', DeferralReason.JOB_LOSS, 300.0, D(2022, 1, 1), D(2022, 7, 1), 50.0)
    assert book.total_deferred_outstanding_gbp() == pytest.approx(500.0)


def test_annual_summary():
    book = PaymentDeferralBook()
    book.create('C011', DeferralReason.FINANCIAL_HARDSHIP, 200.0, D(2022, 1, 1), D(2022, 7, 1), 33.0)
    d2 = book.create('C012', DeferralReason.JOB_LOSS, 300.0, D(2022, 1, 1), D(2022, 7, 1), 50.0)
    book.mark_defaulted(d2.deferral_id)
    s = book.annual_summary()
    assert s['total_deferrals'] == 2
    assert s['active'] == 1
    assert s['defaulted'] == 1
    assert 'financial_hardship' in s['by_reason']
