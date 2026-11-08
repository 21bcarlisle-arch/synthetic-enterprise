"""Phase JU: Coverage Depth Sprint XLIII -- 30 tests."""
import datetime as dt
import pytest
from company.market.dsr_book import DispatchResult, DSRBook


def _dsr():
    book = DSRBook()
    book.enroll("IC001", "1200011111", 2.0, dt.date(2021, 1, 1), payment_per_mwh_gbp=60.0)
    return book


def _dispatch(book, mw_req=2.0, mw_del=2.0, hours=1):
    start = dt.datetime(2022, 6, 1, 17, 0)
    end = start + dt.timedelta(hours=hours)
    return book.dispatch("IC001", mw_req, start, end, mw_del)


def test_dsr_event_id_dsr0001():
    assert _dispatch(_dsr()).event_id == "DSR-0001"


def test_dsr_event_ids_sequential():
    book = _dsr()
    e1 = _dispatch(book)
    e2 = _dispatch(book)
    assert e1.event_id == "DSR-0001" and e2.event_id == "DSR-0002"


def test_dsr_dispatch_95pct_is_delivered():
    ev = _dispatch(_dsr(), mw_req=2.0, mw_del=1.9)
    assert ev.delivery_rate == pytest.approx(95.0)
    assert ev.result == DispatchResult.DELIVERED


def test_dsr_dispatch_below_95pct_is_partial():
    ev = _dispatch(_dsr(), mw_req=2.0, mw_del=1.89)
    assert ev.result == DispatchResult.PARTIAL


def test_dsr_payment_calculated():
    ev = _dispatch(_dsr(), mw_req=2.0, mw_del=2.0, hours=2)
    assert ev.delivered_mwh == pytest.approx(4.0)
    assert ev.payment_gbp == pytest.approx(4.0 * 60.0)


def test_dsr_duration_hours_2h():
    assert _dispatch(_dsr(), hours=2).duration_hours == pytest.approx(2.0)


def test_dsr_delivered_mwh_3h():
    ev = _dispatch(_dsr(), mw_del=2.0, hours=3)
    assert ev.delivered_mwh == pytest.approx(6.0)


def test_dsr_events_for_customer_filter():
    book = DSRBook()
    book.enroll("IC001", "1200011111", 2.0, dt.date(2021, 1, 1))
    book.enroll("IC002", "1200022222", 1.5, dt.date(2021, 1, 1))
    s, e = dt.datetime(2022, 6, 1, 17, 0), dt.datetime(2022, 6, 1, 18, 0)
    book.dispatch("IC001", 2.0, s, e, 2.0)
    book.dispatch("IC002", 1.5, s, e, 1.5)
    book.dispatch("IC001", 2.0, s, e, 2.0)
    assert len(book.events_for_customer("IC001")) == 2
    assert len(book.events_for_customer("IC002")) == 1


def test_dsr_delivery_rate_year_none_empty():
    assert _dsr().delivery_rate_year(2023) is None


def test_dsr_delivery_rate_100_full():
    book = _dsr()
    _dispatch(book, mw_req=2.0, mw_del=2.0)
    assert book.delivery_rate_year(2022) == pytest.approx(100.0)


def _period():
    return dt.datetime(2022, 3, 1), dt.datetime(2022, 3, 31, 23, 59, 59)
