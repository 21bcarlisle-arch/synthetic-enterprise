"""Tests for Metering Data Exception Handler (Phase EY)."""
import datetime as dt
import pytest
from company.billing.metering_exception import (
    ReadType, ExceptionType, MeterRead, MeteringException, MeteringExceptionBook,
)

DATE = dt.date(2024, 1, 15)
MPAN = "1000000000001"


def make_read(rtype=ReadType.ACTUAL, val=5000.0, date=DATE):
    return MeterRead(mpan=MPAN, read_date=date, read_type=rtype,
                     read_value_kwh=val)


class TestMeterRead:
    def test_actual_is_actual(self):
        r = make_read(ReadType.ACTUAL)
        assert r.is_actual

    def test_smart_is_actual(self):
        r = make_read(ReadType.SMART_AMR)
        assert r.is_actual

    def test_estimated_is_estimated(self):
        r = make_read(ReadType.ESTIMATED)
        assert r.is_estimated

    def test_actual_is_not_estimated(self):
        r = make_read(ReadType.ACTUAL)
        assert not r.is_estimated


class TestMeteringException:
    def test_is_resolved_false(self):
        e = MeteringException("EXC-00001", MPAN, ExceptionType.NO_READ, DATE)
        assert not e.is_resolved

    def test_is_resolved_true(self):
        e = MeteringException("EXC-00001", MPAN, ExceptionType.NO_READ, DATE,
                              resolved_at=DATE + dt.timedelta(days=5))
        assert e.is_resolved

    def test_days_outstanding(self):
        e = MeteringException("EXC-00001", MPAN, ExceptionType.NO_READ, DATE)
        assert e.days_outstanding(DATE + dt.timedelta(days=10)) == 10

    def test_days_outstanding_when_resolved(self):
        e = MeteringException("EXC-00001", MPAN, ExceptionType.NO_READ, DATE,
                              resolved_at=DATE + dt.timedelta(days=3))
        assert e.days_outstanding(DATE + dt.timedelta(days=10)) == 0

    def test_exception_summary(self):
        e = MeteringException("EXC-00001", MPAN, ExceptionType.NO_READ, DATE)
        s = e.exception_summary()
        assert "EXC-00001" in s
        assert "no_read" in s


class TestMeteringExceptionBook:
    def test_record_read(self):
        book = MeteringExceptionBook()
        book.record_read(make_read())
        assert len(book.reads_for_mpan(MPAN)) == 1

    def test_consecutive_estimate_count(self):
        book = MeteringExceptionBook()
        book.record_read(make_read(ReadType.ACTUAL, date=dt.date(2024, 1, 1)))
        book.record_read(make_read(ReadType.ESTIMATED, date=dt.date(2024, 2, 1)))
        book.record_read(make_read(ReadType.ESTIMATED, date=dt.date(2024, 3, 1)))
        assert book.consecutive_estimate_count(MPAN) == 2

    def test_consecutive_count_resets_on_actual(self):
        book = MeteringExceptionBook()
        book.record_read(make_read(ReadType.ESTIMATED, date=dt.date(2024, 1, 1)))
        book.record_read(make_read(ReadType.ACTUAL, date=dt.date(2024, 2, 1)))
        assert book.consecutive_estimate_count(MPAN) == 0

    def test_raise_exception(self):
        book = MeteringExceptionBook()
        e = book.raise_exception(MPAN, ExceptionType.NO_READ, DATE)
        assert e.exception_id == "EXC-00001"
        assert len(book.open_exceptions()) == 1

    def test_resolve_exception(self):
        book = MeteringExceptionBook()
        e = book.raise_exception(MPAN, ExceptionType.NO_READ, DATE)
        resolved = book.resolve_exception(e.exception_id, DATE + dt.timedelta(days=5))
        assert resolved.is_resolved
        assert len(book.open_exceptions()) == 0

    def test_actual_read_pct(self):
        book = MeteringExceptionBook()
        book.record_read(make_read(ReadType.ACTUAL))
        book.record_read(make_read(ReadType.ESTIMATED))
        assert book.actual_read_pct() == pytest.approx(50.0)

    def test_actual_read_pct_empty(self):
        book = MeteringExceptionBook()
        assert book.actual_read_pct() == 100.0

    def test_metering_summary(self):
        book = MeteringExceptionBook()
        book.record_read(make_read())
        s = book.metering_summary(DATE)
        assert "Metering Exceptions" in s
