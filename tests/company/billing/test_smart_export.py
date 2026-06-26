import pytest
from datetime import date
from company.billing.smart_export import (
    SEGAccount, SEGBook, seg_rate_ppm, seg_valid_rate, _SEG_MIN_RATE_PPM,
)


def test_seg_rate_2022_crisis():
    assert seg_rate_ppm(2022) == pytest.approx(15.0)


def test_seg_valid_rate_above_minimum():
    assert seg_valid_rate(5.0) is True


def test_seg_valid_rate_below_minimum():
    assert seg_valid_rate(0.5) is False


@pytest.fixture
def book():
    return SEGBook()


@pytest.fixture
def account(book):
    return book.register(
        "C001", "MPAN_001", "SEG_Standard",
        rate_ppm=7.0, registered_date=date(2022, 4, 1)
    )


def test_register_creates_account(account):
    assert account.customer_id == "C001"
    assert account.rate_ppm == pytest.approx(7.0)


def test_register_rejects_zero_rate(book):
    with pytest.raises(ValueError):
        book.register("C002", "MPAN_002", "SEG_Cheap", 0.0, date(2022, 1, 1))


def test_record_export_accumulates(book, account):
    book.record_export("C001", "2022-05", 100.0)
    book.record_export("C001", "2022-05", 50.0)
    assert account.export_readings["2022-05"] == pytest.approx(150.0)


def test_record_export_unknown_customer_returns_false(book):
    result = book.record_export("UNKNOWN", "2022-05", 100.0)
    assert result is False


def test_payment_for_period(account):
    account.record_export("2022-06", 200.0)
    expected = 200.0 * 7.0 / 10000
    assert account.payment_for_period("2022-06") == pytest.approx(expected, abs=0.01)


def test_total_export_kwh(account):
    account.record_export("2022-04", 80.0)
    account.record_export("2022-05", 120.0)
    assert account.total_export_kwh() == pytest.approx(200.0)


def test_annual_summary(book, account):
    book.record_export("C001", "2022-04", 100.0)
    book.record_export("C001", "2022-07", 200.0)
    summary = account.annual_summary(2022)
    assert summary["export_kwh"] == pytest.approx(300.0)
    assert summary["rate_ppm"] == pytest.approx(7.0)
    assert summary["payment_gbp"] == pytest.approx(300.0 * 7.0 / 10000, abs=0.01)


def test_portfolio_summary_empty(book):
    summary = book.portfolio_summary(2022)
    assert summary["total_accounts"] == 0
    assert summary["total_payments_gbp"] == 0.0


def test_portfolio_summary_with_accounts(book):
    a1 = book.register("C001", "M1", "SEG_A", 7.0, date(2022, 1, 1))
    a2 = book.register("C002", "M2", "SEG_B", 10.0, date(2022, 1, 1))
    book.record_export("C001", "2022-06", 500.0)
    book.record_export("C002", "2022-06", 300.0)
    summary = book.portfolio_summary(2022)
    assert summary["total_accounts"] == 2
    assert summary["total_export_kwh"] == pytest.approx(800.0)
