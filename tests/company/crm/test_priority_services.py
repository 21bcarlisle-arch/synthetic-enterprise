import pytest
from datetime import date, timedelta
from company.crm.priority_services import PSRBook, PSREntry, PSRNeed


@pytest.fixture
def book():
    return PSRBook()


def test_register_customer(book):
    e = book.register("C1", [PSRNeed.LARGE_PRINT_BILLS], date(2022, 1, 1))
    assert e.customer_id == "C1"
    assert PSRNeed.LARGE_PRINT_BILLS in e.needs
    assert book.is_registered("C1")


def test_register_with_nominee(book):
    e = book.register(
        "C1", [PSRNeed.NOMINEE_BILLING], date(2022, 1, 1),
        nominee_name="Jane Smith", nominee_contact="07700900123"
    )
    assert e.nominee_name == "Jane Smith"
    assert e.nominee_contact == "07700900123"


def test_review_due_date_is_one_year_later(book):
    e = book.register("C1", [PSRNeed.BRAILLE_BILLS], date(2022, 1, 1))
    assert e.review_due_date == date(2023, 1, 1)


def test_is_not_due_for_review_before_year(book):
    e = book.register("C1", [PSRNeed.BRAILLE_BILLS], date(2022, 1, 1))
    assert not e.is_due_for_review(date(2022, 12, 31))


def test_is_due_for_review_after_year(book):
    e = book.register("C1", [PSRNeed.BRAILLE_BILLS], date(2022, 1, 1))
    assert e.is_due_for_review(date(2023, 1, 1))


def test_update_needs(book):
    book.register("C1", [PSRNeed.LARGE_PRINT_BILLS], date(2022, 1, 1))
    ok = book.update_needs("C1", [PSRNeed.BRAILLE_BILLS, PSRNeed.AUDIO_BILLS])
    assert ok
    assert PSRNeed.BRAILLE_BILLS in book.get("C1").needs
    assert PSRNeed.LARGE_PRINT_BILLS not in book.get("C1").needs


def test_update_needs_unknown_customer(book):
    assert book.update_needs("NOBODY", [PSRNeed.HEARING_IMPAIRED]) is False


def test_medically_dependent_customers(book):
    book.register("C1", [PSRNeed.MEDICALLY_DEPENDENT], date(2022, 1, 1))
    book.register("C2", [PSRNeed.LARGE_PRINT_BILLS], date(2022, 1, 1))
    med = book.medically_dependent_customers()
    assert "C1" in med
    assert "C2" not in med


def test_due_for_review(book):
    book.register("C1", [PSRNeed.BRAILLE_BILLS], date(2022, 1, 1))
    due = book.due_for_review(date(2023, 2, 1))
    assert any(e.customer_id == "C1" for e in due)


def test_not_registered_returns_false(book):
    assert not book.is_registered("UNKNOWN")


def test_get_returns_none_if_not_registered(book):
    assert book.get("NOBODY") is None


def test_portfolio_summary(book):
    book.register("C1", [PSRNeed.MEDICALLY_DEPENDENT, PSRNeed.LARGE_PRINT_BILLS], date(2022, 1, 1))
    book.register("C2", [PSRNeed.NOMINEE_BILLING], date(2022, 1, 1),
                  nominee_name="Bob Jones", nominee_contact="01234567890")
    s = book.portfolio_summary()
    assert s["total_registered"] == 2
    assert s["medically_dependent"] == 1
    assert s["with_nominee"] == 1
    assert s["need_breakdown"]["medically_dependent"] == 1
    assert s["need_breakdown"]["nominee_billing"] == 1
