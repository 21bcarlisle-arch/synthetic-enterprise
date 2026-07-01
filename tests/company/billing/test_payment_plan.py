import pytest
from datetime import date
from company.billing.payment_plan import PaymentPlan, PaymentPlanBook, PaymentPlanStatus


@pytest.fixture
def book():
    return PaymentPlanBook()


def test_create_plan(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    assert p.customer_id == "C1"
    assert p.original_debt_gbp == 600.0
    assert p.installment_gbp == 100.0
    assert p.status == PaymentPlanStatus.ACTIVE


def test_expected_months(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    assert p.expected_months == 6


def test_expected_months_rounds_up(book):
    p = book.create_plan("C1", 650.0, 100.0, date(2022, 1, 1))
    assert p.expected_months == 7


def test_record_payment_reduces_remaining_debt(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    book.record_payment(p.plan_id, date(2022, 2, 1))
    assert p.total_paid_gbp == 100.0
    assert p.remaining_debt_gbp == 500.0


def test_plan_completes_on_final_payment(book):
    p = book.create_plan("C1", 200.0, 100.0, date(2022, 1, 1))
    book.record_payment(p.plan_id, date(2022, 2, 1))
    book.record_payment(p.plan_id, date(2022, 3, 1))
    assert p.status == PaymentPlanStatus.COMPLETED
    assert p.remaining_debt_gbp == 0.0


def test_record_payment_returns_false_if_not_found(book):
    assert book.record_payment(999, date(2022, 2, 1)) is False


def test_record_missed_increments_count(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    book.record_missed(p.plan_id)
    assert p.missed_payments == 1
    assert p.status == PaymentPlanStatus.ACTIVE  # not yet defaulted


def test_plan_defaults_after_threshold_misses(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    book.record_missed(p.plan_id)
    book.record_missed(p.plan_id)
    assert p.status == PaymentPlanStatus.DEFAULTED


def test_cancel_plan(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    ok = book.cancel_plan(p.plan_id)
    assert ok
    assert p.status == PaymentPlanStatus.CANCELLED


def test_active_plans(book):
    p1 = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    p2 = book.create_plan("C2", 400.0, 50.0, date(2022, 1, 1))
    book.cancel_plan(p1.plan_id)
    active = book.active_plans()
    assert p2 in active
    assert p1 not in active


def test_defaulted_plans(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    book.record_missed(p.plan_id)
    book.record_missed(p.plan_id)
    assert p in book.defaulted_plans()


def test_portfolio_summary(book):
    book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    book.create_plan("C2", 400.0, 50.0, date(2022, 1, 1))
    s = book.portfolio_summary()
    assert s["total_plans"] == 2
    assert s["active"] == 2
    assert s["avg_original_debt_gbp"] == 500.0


# --- Phase LP depth tests ---

def test_plan_id_stored(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    assert p.plan_id == 1


def test_start_date_stored(book):
    d = date(2022, 6, 15)
    p = book.create_plan("C1", 600.0, 100.0, d)
    assert p.start_date == d


def test_status_default_active(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    assert p.status == PaymentPlanStatus.ACTIVE


def test_payments_made_default_zero(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    assert p.payments_made == 0


def test_total_paid_default_zero(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    assert p.total_paid_gbp == pytest.approx(0.0)


def test_missed_payments_default_zero(book):
    p = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    assert p.missed_payments == 0


def test_sequential_plan_ids(book):
    p1 = book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    p2 = book.create_plan("C2", 400.0, 50.0, date(2022, 1, 1))
    assert p1.plan_id == 1
    assert p2.plan_id == 2


def test_plans_for_customer(book):
    book.create_plan("C1", 600.0, 100.0, date(2022, 1, 1))
    book.create_plan("C1", 300.0, 50.0, date(2022, 2, 1))
    book.create_plan("C2", 200.0, 40.0, date(2022, 1, 1))
    assert len(book.plans_for_customer("C1")) == 2


def test_record_missed_returns_none_unknown_id(book):
    result = book.record_missed(999)
    assert result is None


def test_portfolio_summary_empty(book):
    s = book.portfolio_summary()
    assert s["total_plans"] == 0
    assert s["active"] == 0
    assert s["avg_original_debt_gbp"] == 0.0
