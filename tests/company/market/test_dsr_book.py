import datetime as dt
import pytest
from company.market.dsr_book import (
    DSRStatus, DispatchResult, DSRParticipant, DispatchEvent, DSRBook
)


def _book():
    book = DSRBook()
    book.enroll('IC001', '1200011111', 2.0, dt.date(2021, 1, 1), payment_per_mwh_gbp=60.0)
    book.enroll('IC002', '1200022222', 1.5, dt.date(2021, 6, 1), payment_per_mwh_gbp=55.0)
    return book


def test_enroll_participant():
    book = _book()
    assert len(book._participants) == 2
    assert book._participants['IC001'].status == DSRStatus.ACTIVE


def test_total_contracted_mw():
    book = _book()
    assert book.total_contracted_mw() == pytest.approx(3.5)


def test_dispatch_full_delivery():
    book = _book()
    start = dt.datetime(2022, 1, 10, 17, 0)
    end = dt.datetime(2022, 1, 10, 18, 0)
    ev = book.dispatch('IC001', requested_mw=2.0, dispatch_start=start,
                       dispatch_end=end, delivered_mw=2.0)
    assert ev.result == DispatchResult.DELIVERED
    assert ev.delivered_mwh == pytest.approx(2.0)
    assert ev.payment_gbp == pytest.approx(120.0)


def test_dispatch_partial():
    book = _book()
    start = dt.datetime(2022, 1, 10, 17, 0)
    end = dt.datetime(2022, 1, 10, 18, 0)
    ev = book.dispatch('IC001', requested_mw=2.0, dispatch_start=start,
                       dispatch_end=end, delivered_mw=1.0)
    assert ev.result == DispatchResult.PARTIAL
    assert ev.delivery_rate == pytest.approx(50.0)


def test_dispatch_non_delivery():
    book = _book()
    start = dt.datetime(2022, 1, 10, 17, 0)
    end = dt.datetime(2022, 1, 10, 18, 0)
    ev = book.dispatch('IC001', requested_mw=2.0, dispatch_start=start,
                       dispatch_end=end, delivered_mw=0.0)
    assert ev.result == DispatchResult.NON_DELIVERY


def test_total_payments_gbp():
    book = _book()
    start = dt.datetime(2022, 6, 1, 16, 0)
    end = dt.datetime(2022, 6, 1, 18, 0)
    book.dispatch('IC001', requested_mw=2.0, dispatch_start=start,
                  dispatch_end=end, delivered_mw=2.0)
    book.dispatch('IC002', requested_mw=1.5, dispatch_start=start,
                  dispatch_end=end, delivered_mw=1.5)
    total = book.total_payments_gbp(2022)
    assert total == pytest.approx(60*4 + 55*3)


def test_annual_summary():
    book = _book()
    start = dt.datetime(2022, 2, 1, 17, 0)
    end = dt.datetime(2022, 2, 1, 18, 0)
    book.dispatch('IC001', requested_mw=2.0, dispatch_start=start,
                  dispatch_end=end, delivered_mw=2.0)
    s = book.annual_summary(2022)
    assert s['dispatch_events'] == 1
    assert s['full_deliveries'] == 1
    assert 'total_payments_gbp' in s
    assert 'active_participants' in s
