import pytest
from datetime import date
from company.regulatory.gsop import GSOPBook, GSOPPayment, GSOPType, _add_working_days


@pytest.fixture
def book():
    return GSOPBook()


def test_record_trigger_creates_payment(book):
    p = book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    assert p.customer_id == "C1"
    assert p.gsop_type == GSOPType.MISSED_APPOINTMENT
    assert p.amount_gbp == 30.0
    assert p.paid_date is None


def test_payment_due_date_is_future(book):
    p = book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    assert p.payment_due_date > date(2022, 3, 1)


def test_erroneous_transfer_has_20_working_day_window(book):
    p = book.record_trigger("C1", GSOPType.ERRONEOUS_TRANSFER, date(2022, 3, 1))
    # 20 working days from 2022-03-01 (Tuesday)
    assert (p.payment_due_date - date(2022, 3, 1)).days >= 20


def test_pay_marks_payment_as_paid(book):
    p = book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    ok = book.pay(p.payment_id, date(2022, 3, 5))
    assert ok
    assert p.is_paid
    assert p.paid_date == date(2022, 3, 5)


def test_pay_returns_false_for_unknown_id(book):
    assert book.pay(999, date(2022, 3, 5)) is False


def test_overdue_returns_unpaid_past_due(book):
    p = book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    overdue_list = book.overdue(date(2022, 4, 1))
    assert p in overdue_list


def test_overdue_excludes_paid(book):
    p = book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    book.pay(p.payment_id, date(2022, 3, 5))
    assert book.overdue(date(2022, 4, 1)) == []


def test_total_liability_all_years(book):
    book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    book.record_trigger("C2", GSOPType.ERRONEOUS_TRANSFER, date(2022, 6, 1))
    assert book.total_liability_gbp() == 60.0


def test_total_liability_by_year(book):
    book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, date(2021, 3, 1))
    book.record_trigger("C2", GSOPType.ERRONEOUS_TRANSFER, date(2022, 6, 1))
    assert book.total_liability_gbp(year=2022) == 30.0
    assert book.total_liability_gbp(year=2021) == 30.0


def test_annual_report_structure(book):
    book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    p2 = book.record_trigger("C2", GSOPType.ERRONEOUS_TRANSFER, date(2022, 6, 1))
    book.pay(p2.payment_id, date(2022, 6, 20))
    r = book.annual_report(2022)
    assert r["year"] == 2022
    assert r["total_triggers"] == 2
    assert r["total_paid"] == 1
    assert r["total_liability_gbp"] == 60.0
    assert r["by_type"]["missed_appointment"] == 1
    assert r["by_type"]["erroneous_transfer"] == 1


def test_annual_report_empty_year(book):
    r = book.annual_report(2020)
    assert r["total_triggers"] == 0
    assert r["auto_pay_rate_pct"] == 100.0


def test_add_working_days_skips_weekends():
    # 2022-03-01 is a Tuesday; +5 working days = 2022-03-08 (Tuesday)
    result = _add_working_days(date(2022, 3, 1), 5)
    assert result == date(2022, 3, 8)
    assert result.weekday() == 1  # Tuesday


# --- Phase MA depth tests ---

def test_payment_id_is_1_for_first(book):
    p = book.record_trigger('C1', GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    assert p.payment_id == 1


def test_payment_customer_id_stored(book):
    p = book.record_trigger('CUST-MA', GSOPType.ERRONEOUS_TRANSFER, date(2022, 3, 1))
    assert p.customer_id == 'CUST-MA'


def test_gsop_type_stored(book):
    p = book.record_trigger('C1', GSOPType.WRONGFUL_DISCONNECT, date(2022, 3, 1))
    assert p.gsop_type == GSOPType.WRONGFUL_DISCONNECT


def test_trigger_date_stored(book):
    d = date(2022, 5, 10)
    p = book.record_trigger('C1', GSOPType.FINAL_BILL_DELAY, d)
    assert p.trigger_date == d


def test_amount_gbp_stored(book):
    p = book.record_trigger('C1', GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    assert p.amount_gbp == pytest.approx(30.0)


def test_paid_date_none_before_pay(book):
    p = book.record_trigger('C1', GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    assert p.paid_date is None


def test_is_paid_false_before_pay(book):
    p = book.record_trigger('C1', GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    assert p.is_paid is False


def test_sequential_payment_ids(book):
    p1 = book.record_trigger('C1', GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    p2 = book.record_trigger('C2', GSOPType.ERRONEOUS_TRANSFER, date(2022, 3, 2))
    assert p1.payment_id == 1
    assert p2.payment_id == 2


def test_record_trigger_returns_gsop_payment(book):
    result = book.record_trigger('C1', GSOPType.MISSED_APPOINTMENT, date(2022, 3, 1))
    assert isinstance(result, GSOPPayment)


def test_gsop_type_has_5_members():
    assert len(list(GSOPType)) == 5
