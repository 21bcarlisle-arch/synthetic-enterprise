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


# --- Phase KB depth tests ---

def test_event_id_format():
    book = _book()
    start = dt.datetime(2022, 1, 10, 17, 0)
    end = dt.datetime(2022, 1, 10, 18, 0)
    ev = book.dispatch('IC001', 2.0, start, end, delivered_mw=2.0)
    assert ev.event_id == 'DSR-0001'


def test_event_id_sequential():
    book = _book()
    start = dt.datetime(2022, 1, 10, 17, 0)
    end = dt.datetime(2022, 1, 10, 18, 0)
    ev1 = book.dispatch('IC001', 2.0, start, end, delivered_mw=2.0)
    ev2 = book.dispatch('IC002', 1.5, start, end, delivered_mw=1.5)
    assert ev1.event_id == 'DSR-0001'
    assert ev2.event_id == 'DSR-0002'


def test_duration_hours_two_hour_dispatch():
    book = _book()
    start = dt.datetime(2022, 1, 10, 16, 0)
    end = dt.datetime(2022, 1, 10, 18, 0)
    ev = book.dispatch('IC001', 2.0, start, end, delivered_mw=2.0)
    assert ev.duration_hours == pytest.approx(2.0)


def test_delivered_mwh_2_5mw_3h():
    book = _book()
    start = dt.datetime(2022, 1, 10, 15, 0)
    end = dt.datetime(2022, 1, 10, 18, 0)
    ev = book.dispatch('IC001', 2.0, start, end, delivered_mw=2.5)
    assert ev.delivered_mwh == pytest.approx(7.5)


def test_events_for_customer_filters():
    book = _book()
    start = dt.datetime(2022, 1, 10, 17, 0)
    end = dt.datetime(2022, 1, 10, 18, 0)
    book.dispatch('IC001', 2.0, start, end, delivered_mw=2.0)
    book.dispatch('IC002', 1.5, start, end, delivered_mw=1.5)
    events = book.events_for_customer('IC001')
    assert len(events) == 1
    assert events[0].customer_id == 'IC001'


def test_delivery_rate_year_none_when_empty():
    book = _book()
    assert book.delivery_rate_year(2099) is None


def test_delivery_rate_partial_50_pct():
    book = _book()
    start = dt.datetime(2022, 1, 10, 17, 0)
    end = dt.datetime(2022, 1, 10, 18, 0)
    book.dispatch('IC001', 2.0, start, end, delivered_mw=1.0)
    assert book.delivery_rate_year(2022) == pytest.approx(50.0)


def test_payment_formula_3h_dispatch():
    book = _book()
    start = dt.datetime(2022, 1, 10, 15, 0)
    end = dt.datetime(2022, 1, 10, 18, 0)
    ev = book.dispatch('IC002', 1.5, start, end, delivered_mw=1.5)
    assert ev.payment_gbp == pytest.approx(247.5)


def test_annual_summary_year_filter():
    book = _book()
    start_22 = dt.datetime(2022, 1, 10, 17, 0)
    end_22 = dt.datetime(2022, 1, 10, 18, 0)
    start_23 = dt.datetime(2023, 1, 10, 17, 0)
    end_23 = dt.datetime(2023, 1, 10, 18, 0)
    book.dispatch('IC001', 2.0, start_22, end_22, delivered_mw=2.0)
    book.dispatch('IC001', 2.0, start_23, end_23, delivered_mw=2.0)
    s = book.annual_summary(2022)
    assert s['dispatch_events'] == 1


def test_delivered_at_exactly_95_pct():
    book = _book()
    start = dt.datetime(2022, 1, 10, 17, 0)
    end = dt.datetime(2022, 1, 10, 18, 0)
    ev = book.dispatch('IC001', 2.0, start, end, delivered_mw=1.9)
    assert ev.result == DispatchResult.DELIVERED
