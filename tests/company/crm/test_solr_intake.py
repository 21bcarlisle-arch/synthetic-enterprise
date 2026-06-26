import datetime as dt
import pytest
from company.crm.solr_intake import (
    SoLRIntakeStatus, SoLRBatch, SoLRCustomer, SoLRBook
)


def _book():
    book = SoLRBook('SUPPLIER_A')
    book.register_batch('BATCH001', 'GreenStar Energy',
                        dt.date(2021, 11, 1), 1500, 0.0)
    return book


def test_register_batch():
    book = _book()
    b = book._batches['BATCH001']
    assert b.failed_supplier == 'GreenStar Energy'
    assert b.customer_count == 1500


def test_deemed_tariff_above_cap():
    book = SoLRBook('SUPPLIER_A')
    batch = book.register_batch('B2', 'MegaEnergy', dt.date(2022, 9, 1), 800, 15.0)
    assert batch.is_priced_above_cap is True


def test_add_customer_initial_status():
    book = _book()
    c = book.add_customer('C001', 'BATCH001', '1200011111', 'residential')
    assert c.status == SoLRIntakeStatus.NOTIFIED


def test_mark_contacted():
    book = _book()
    book.add_customer('C001', 'BATCH001', '1200011111', 'residential')
    c = book.mark_contacted('C001', dt.date(2021, 11, 5))
    assert c.status == SoLRIntakeStatus.CONTACTED
    assert c.contacted_date == dt.date(2021, 11, 5)


def test_mark_onboarded():
    book = _book()
    book.add_customer('C001', 'BATCH001', '1200011111', 'residential')
    book.mark_contacted('C001', dt.date(2021, 11, 5))
    c = book.mark_onboarded('C001', dt.date(2021, 11, 10))
    assert c.is_retained is True


def test_retention_rate():
    book = _book()
    book.add_customer('C001', 'BATCH001', '1200011111', 'residential')
    book.add_customer('C002', 'BATCH001', '1200022222', 'residential')
    book.add_customer('C003', 'BATCH001', '1200033333', 'residential')
    book.mark_contacted('C001', dt.date(2021, 11, 5))
    book.mark_onboarded('C001', dt.date(2021, 11, 10))
    book.mark_switched_away('C002', dt.date(2021, 11, 20))
    assert book.retention_rate('BATCH001') == pytest.approx(33.3)


def test_contact_rate():
    book = _book()
    book.add_customer('C001', 'BATCH001', '1200011111', 'residential')
    book.add_customer('C002', 'BATCH001', '1200022222', 'residential')
    book.mark_contacted('C001', dt.date(2021, 11, 5))
    assert book.contact_rate('BATCH001') == pytest.approx(50.0)


def test_batch_summary_keys():
    book = _book()
    book.add_customer('C001', 'BATCH001', '1200011111', 'residential')
    s = book.batch_summary('BATCH001')
    assert 'retention_rate_pct' in s
    assert 'contact_rate_pct' in s
    assert 'by_status' in s
    assert 'actual_customers_received' in s
