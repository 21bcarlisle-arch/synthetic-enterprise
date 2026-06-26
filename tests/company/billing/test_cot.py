import pytest
from datetime import date
from company.billing.cot import COTBook, COTType, deemed_rate_gbp_per_kwh


@pytest.fixture
def book():
    return COTBook()


def test_record_move_out(book):
    ev = book.record_move_out("C1", "MPAN001", date(2022, 3, 1), 12500.0)
    assert ev.cot_type == COTType.MOVE_OUT
    assert ev.meter_read_kwh == 12500.0
    assert ev.customer_id == "C1"


def test_void_appears_after_move_out(book):
    book.record_move_out("C1", "MPAN001", date(2022, 3, 1), 12500.0)
    assert "MPAN001" in book.void_properties()


def test_record_move_in_clears_void(book):
    book.record_move_out("C1", "MPAN001", date(2022, 3, 1), 12500.0)
    book.record_move_in("C2", "MPAN001", date(2022, 4, 1), 12500.0)
    assert "MPAN001" not in book.void_properties()


def test_move_in_event_type(book):
    ev = book.record_move_in("C2", "MPAN001", date(2022, 4, 1), 12500.0)
    assert ev.cot_type == COTType.MOVE_IN
    assert ev.new_occupant_id == "C2"


def test_void_days(book):
    book.record_move_out("C1", "MPAN001", date(2022, 3, 1), 12500.0)
    assert book.void_days("MPAN001", date(2022, 3, 31)) == 30


def test_void_days_zero_if_not_void(book):
    assert book.void_days("MPAN999", date(2022, 3, 31)) == 0


def test_overdue_for_nomination(book):
    book.record_move_out("C1", "MPAN001", date(2022, 3, 1), 12500.0)
    # 29 days after move-out -> overdue (>28)
    assert "MPAN001" in book.overdue_for_nomination(date(2022, 3, 30))


def test_not_overdue_within_28_days(book):
    book.record_move_out("C1", "MPAN001", date(2022, 3, 1), 12500.0)
    # 28 days after move-out -> boundary, NOT overdue (>28 not >=28)
    assert "MPAN001" not in book.overdue_for_nomination(date(2022, 3, 29))


def test_move_in_removes_from_overdue(book):
    book.record_move_out("C1", "MPAN001", date(2022, 3, 1), 12500.0)
    book.record_move_in("C2", "MPAN001", date(2022, 4, 1), 12500.0)
    assert "MPAN001" not in book.overdue_for_nomination(date(2022, 5, 1))


def test_portfolio_summary(book):
    book.record_move_out("C1", "MPAN001", date(2022, 3, 1), 12500.0)
    book.record_move_out("C2", "MPAN002", date(2022, 3, 15), 8000.0)
    s = book.portfolio_summary(date(2022, 4, 1))
    assert s["total_voids"] == 2
    assert s["avg_void_days"] > 0
    assert s["total_events"] == 2


def test_deemed_rate_normal_year():
    # 2019: SVT 15.5p, +20% = 18.6p, cap=16p -> capped at 16p
    r = deemed_rate_gbp_per_kwh(date(2019, 6, 1))
    assert abs(r - 0.16) < 0.001


def test_deemed_rate_crisis_year():
    # 2022: SVT 28p, +20% = 33.6p, cap=34p -> deemed = 33.6p
    r = deemed_rate_gbp_per_kwh(date(2022, 6, 1))
    assert abs(r - 0.336) < 0.001


def test_events_for_meter_point(book):
    book.record_move_out("C1", "MPAN001", date(2022, 3, 1), 12500.0)
    book.record_move_in("C2", "MPAN001", date(2022, 4, 1), 12500.0)
    evs = book.events_for("MPAN001")
    assert len(evs) == 2
    types = {e.cot_type for e in evs}
    assert COTType.MOVE_OUT in types
    assert COTType.MOVE_IN in types
