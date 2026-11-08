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


def test_deferral_id_sequential():
    book = PaymentDeferralBook()
    d1 = book.create('C001', DeferralReason.FINANCIAL_HARDSHIP, 200.0,
                     D(2022, 1, 1), D(2022, 7, 1), 33.0)
    d2 = book.create('C002', DeferralReason.JOB_LOSS, 300.0,
                     D(2022, 1, 1), D(2022, 7, 1), 50.0)
    assert d1.deferral_id == 'DEF-0001'
    assert d2.deferral_id == 'DEF-0002'


def test_outstanding_capped_at_zero_on_overpayment():
    book = PaymentDeferralBook()
    d = book.create('C001', DeferralReason.ILLNESS, 100.0, D(2022, 1, 1), D(2022, 6, 1), 100.0)
    book.record_repayment(d.deferral_id, 150.0)
    assert d.outstanding_gbp == 0.0
    assert d.status == DeferralStatus.COMPLETED


def test_deferrals_for_customer():
    book = PaymentDeferralBook()
    book.create('C_A', DeferralReason.FINANCIAL_HARDSHIP, 200.0,
                D(2022, 1, 1), D(2022, 7, 1), 33.0)
    book.create('C_B', DeferralReason.JOB_LOSS, 300.0,
                D(2022, 1, 1), D(2022, 7, 1), 50.0)
    book.create('C_A', DeferralReason.BEREAVEMENT, 150.0,
                D(2022, 3, 1), D(2022, 9, 1), 25.0)
    result = book.deferrals_for_customer('C_A')
    assert len(result) == 2
    assert all(d.customer_id == 'C_A' for d in result)


def test_total_outstanding_excludes_completed():
    book = PaymentDeferralBook()
    d1 = book.create('C001', DeferralReason.FINANCIAL_HARDSHIP, 200.0,
                     D(2022, 1, 1), D(2022, 7, 1), 33.0)
    d2 = book.create('C002', DeferralReason.JOB_LOSS, 300.0,
                     D(2022, 1, 1), D(2022, 7, 1), 50.0)
    book.record_repayment(d2.deferral_id, 300.0)
    assert book.total_deferred_outstanding_gbp() == pytest.approx(200.0)


def test_total_outstanding_excludes_defaulted():
    book = PaymentDeferralBook()
    d1 = book.create('C001', DeferralReason.FINANCIAL_HARDSHIP, 200.0,
                     D(2022, 1, 1), D(2022, 7, 1), 33.0)
    d2 = book.create('C002', DeferralReason.BENEFIT_DELAY, 400.0,
                     D(2022, 1, 1), D(2022, 7, 1), 67.0)
    book.mark_defaulted(d2.deferral_id)
    assert book.total_deferred_outstanding_gbp() == pytest.approx(200.0)


def test_overdue_excludes_completed():
    book = PaymentDeferralBook()
    d = book.create('C001', DeferralReason.COVID_19, 100.0,
                    D(2020, 4, 1), D(2020, 6, 1), 100.0)
    book.record_repayment(d.deferral_id, 100.0)
    assert d.status == DeferralStatus.COMPLETED
    assert len(book.overdue_deferrals(D(2020, 7, 1))) == 0


def test_defaulted_not_in_active_deferrals():
    book = PaymentDeferralBook()
    d = book.create('C001', DeferralReason.JOB_LOSS, 500.0,
                    D(2022, 1, 1), D(2022, 6, 1), 80.0)
    book.mark_defaulted(d.deferral_id)
    assert len(book.active_deferrals()) == 0


def test_annual_summary_by_reason_multiple():
    book = PaymentDeferralBook()
    book.create('C001', DeferralReason.FINANCIAL_HARDSHIP, 200.0,
                D(2022, 1, 1), D(2022, 7, 1), 33.0)
    book.create('C002', DeferralReason.FINANCIAL_HARDSHIP, 300.0,
                D(2022, 1, 1), D(2022, 7, 1), 50.0)
    book.create('C003', DeferralReason.ILLNESS, 150.0,
                D(2022, 1, 1), D(2022, 6, 1), 25.0)
    s = book.annual_summary()
    assert s['by_reason']['financial_hardship'] == 2
    assert s['by_reason']['illness'] == 1


def test_annual_summary_completed_count():
    book = PaymentDeferralBook()
    d = book.create('C001', DeferralReason.BEREAVEMENT, 100.0,
                    D(2022, 1, 1), D(2022, 4, 1), 100.0)
    book.record_repayment(d.deferral_id, 100.0)
    s = book.annual_summary()
    assert s['completed'] == 1
    assert s['active'] == 0


def test_cancelled_not_active():
    book = PaymentDeferralBook()
    d = book.create('C001', DeferralReason.BENEFIT_DELAY, 300.0,
                    D(2022, 1, 1), D(2022, 7, 1), 50.0)
    book.cancel(d.deferral_id)
    assert len(book.active_deferrals()) == 0
    s = book.annual_summary()
    assert s['active'] == 0
