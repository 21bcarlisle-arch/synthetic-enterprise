import datetime as dt
import pytest
from company.billing.credit_refund import (
    CreditRefundRecord, CreditRefundBook, RefundTrigger, RefundStatus,
)


def make_record(account_id="A1", request=dt.date(2023, 1, 2),
                trigger=RefundTrigger.CUSTOMER_REQUEST, amount=150.0,
                status=RefundStatus.PENDING, approved=None, paid=None):
    return CreditRefundRecord(
        account_id=account_id, request_date=request, trigger=trigger,
        credit_amount_gbp=amount, status=status,
        approved_date=approved, paid_date=paid,
    )


class TestCreditRefundRecord:
    def test_working_days_to_pay_none_if_not_paid(self):
        r = make_record()
        assert r.working_days_to_pay() is None

    def test_working_days_to_pay_counts_weekdays(self):
        # Mon 2 Jan -> Mon 16 Jan = 10 working days
        r = make_record(request=dt.date(2023, 1, 2), paid=dt.date(2023, 1, 16),
                        status=RefundStatus.PAID)
        assert r.working_days_to_pay() == 10

    def test_working_days_skips_weekend(self):
        # Fri 6 Jan -> Mon 9 Jan = 1 working day
        r = make_record(request=dt.date(2023, 1, 6), paid=dt.date(2023, 1, 9),
                        status=RefundStatus.PAID)
        assert r.working_days_to_pay() == 1

    def test_is_overdue_false_if_paid(self):
        r = make_record(status=RefundStatus.PAID, paid=dt.date(2023, 1, 16))
        assert r.is_overdue(dt.date(2023, 2, 1)) is False

    def test_is_overdue_false_within_deadline(self):
        r = make_record(request=dt.date(2023, 1, 2))
        assert r.is_overdue(dt.date(2023, 1, 12)) is False

    def test_is_overdue_true_after_deadline(self):
        r = make_record(request=dt.date(2023, 1, 2))
        assert r.is_overdue(dt.date(2023, 1, 20)) is True

    def test_is_overdue_false_when_held(self):
        r = make_record(status=RefundStatus.HELD)
        assert r.is_overdue(dt.date(2023, 2, 1)) is False

    def test_is_overdue_false_when_rejected(self):
        r = make_record(status=RefundStatus.REJECTED)
        assert r.is_overdue(dt.date(2023, 2, 1)) is False

    def test_breached_deadline_true(self):
        r = make_record(request=dt.date(2023, 1, 2), paid=dt.date(2023, 1, 23),
                        status=RefundStatus.PAID)
        assert r.breached_deadline() is True

    def test_breached_deadline_false_on_time(self):
        r = make_record(request=dt.date(2023, 1, 2), paid=dt.date(2023, 1, 16),
                        status=RefundStatus.PAID)
        assert r.breached_deadline() is False

    def test_breached_deadline_false_not_paid(self):
        r = make_record()
        assert r.breached_deadline() is False

    def test_trigger_closure(self):
        r = make_record(trigger=RefundTrigger.ACCOUNT_CLOSURE)
        assert r.trigger == RefundTrigger.ACCOUNT_CLOSURE

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.credit_amount_gbp = 0


class TestCreditRefundBook:
    def test_raise_and_retrieve(self):
        book = CreditRefundBook()
        r = make_record()
        book.raise_refund(r)
        assert r in book.pending_refunds()

    def test_approve(self):
        book = CreditRefundBook()
        book.raise_refund(make_record(account_id="A1"))
        result = book.approve("A1", dt.date(2023, 1, 5))
        assert result.status == RefundStatus.APPROVED
        assert result.approved_date == dt.date(2023, 1, 5)

    def test_pay(self):
        book = CreditRefundBook()
        book.raise_refund(make_record(account_id="A1"))
        result = book.pay("A1", dt.date(2023, 1, 10))
        assert result.status == RefundStatus.PAID
        assert result.paid_date == dt.date(2023, 1, 10)

    def test_reject(self):
        book = CreditRefundBook()
        book.raise_refund(make_record(account_id="A1"))
        result = book.reject("A1")
        assert result.status == RefundStatus.REJECTED

    def test_hold(self):
        book = CreditRefundBook()
        book.raise_refund(make_record(account_id="A1"))
        result = book.hold("A1")
        assert result.status == RefundStatus.HELD

    def test_pending_excludes_paid(self):
        book = CreditRefundBook()
        book.raise_refund(make_record(account_id="A1"))
        book.pay("A1", dt.date(2023, 1, 10))
        assert len(book.pending_refunds()) == 0

    def test_overdue_refunds(self):
        book = CreditRefundBook()
        book.raise_refund(make_record(account_id="A1", request=dt.date(2023, 1, 2)))
        assert len(book.overdue_refunds(dt.date(2023, 1, 20))) == 1
        assert len(book.overdue_refunds(dt.date(2023, 1, 5))) == 0

    def test_deadline_breaches(self):
        book = CreditRefundBook()
        book.raise_refund(make_record(account_id="A1", request=dt.date(2023, 1, 2)))
        book.pay("A1", dt.date(2023, 1, 23))
        assert len(book.deadline_breaches()) == 1

    def test_no_breach_when_on_time(self):
        book = CreditRefundBook()
        book.raise_refund(make_record(account_id="A1", request=dt.date(2023, 1, 2)))
        book.pay("A1", dt.date(2023, 1, 13))
        assert len(book.deadline_breaches()) == 0

    def test_total_outstanding(self):
        book = CreditRefundBook()
        book.raise_refund(make_record(account_id="A1", amount=100.0))
        book.raise_refund(make_record(account_id="A2", amount=50.0))
        assert book.total_outstanding_gbp() == 150.0

    def test_total_outstanding_excludes_paid(self):
        book = CreditRefundBook()
        book.raise_refund(make_record(account_id="A1", amount=100.0))
        book.raise_refund(make_record(account_id="A2", amount=50.0))
        book.pay("A1", dt.date(2023, 1, 10))
        assert book.total_outstanding_gbp() == 50.0

    def test_summary_keys(self):
        book = CreditRefundBook()
        book.raise_refund(make_record())
        s = book.refund_summary()
        for k in ("total_refunds", "paid", "pending", "deadline_breaches",
                  "total_outstanding_gbp"):
            assert k in s

    def test_update_raises_on_missing(self):
        book = CreditRefundBook()
        with pytest.raises(ValueError):
            book.approve("NOTFOUND", dt.date(2023, 1, 5))
