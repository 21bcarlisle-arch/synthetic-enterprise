"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/billing/credit_refund.py — the Ofgem SLC 14 credit-balance refund
book (customer money held by the supplier, and the 10-working-day deadline for
giving it back).

All dates are literals. `is_overdue` takes `as_of` explicitly, so every path here
is time-independent — there is no wall-clock dependency to work around.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.credit_refund import (
    CreditRefundBook,
    CreditRefundRecord,
    RefundStatus,
    RefundTrigger,
    _working_days_between,
)

MON_1_JAN_2024 = dt.date(2024, 1, 1)   # a Monday
FRI_5_JAN_2024 = dt.date(2024, 1, 5)
MON_8_JAN_2024 = dt.date(2024, 1, 8)


def rec(account_id="A1", request_date=MON_1_JAN_2024, amount=120.0,
        trigger=RefundTrigger.CUSTOMER_REQUEST, **kw):
    return CreditRefundRecord(
        account_id=account_id,
        request_date=request_date,
        trigger=trigger,
        credit_amount_gbp=amount,
        **kw,
    )


# ---------------------------------------------------------------------------
# _working_days_between: the counting convention
# ---------------------------------------------------------------------------


def test_working_days_excludes_the_start_day_and_includes_the_end_day():
    """The loop advances BEFORE testing, so the start date is never counted and
    the end date is. Mon 1 Jan -> Mon 8 Jan is 5 working days, not 6."""
    assert _working_days_between(MON_1_JAN_2024, MON_8_JAN_2024) == 5
    assert _working_days_between(FRI_5_JAN_2024, MON_8_JAN_2024) == 1


def test_working_days_same_day_is_zero():
    assert _working_days_between(MON_1_JAN_2024, MON_1_JAN_2024) == 0


def test_working_days_skips_weekends_only_not_bank_holidays():
    """SURPRISE (unit class): 1 Jan 2024 was a bank holiday and Good Friday /
    Easter Monday are working days here. Only Sat/Sun are excluded, so the
    modelled SLC 14 clock runs FASTER than the real one over a holiday week and
    will report a breach the real rule would not."""
    # Thu 28 Mar 2024 -> Tue 2 Apr 2024 spans Good Friday and Easter Monday.
    assert _working_days_between(dt.date(2024, 3, 28), dt.date(2024, 4, 2)) == 3


def test_working_days_with_end_before_start_silently_returns_zero():
    """SURPRISE (boundary class): the `while current < end` loop simply never runs
    for an inverted range, so a transposed pair reports 0 working days rather than
    raising. Downstream, that reads as "paid instantly"."""
    assert _working_days_between(MON_8_JAN_2024, MON_1_JAN_2024) == 0


# ---------------------------------------------------------------------------
# CreditRefundRecord
# ---------------------------------------------------------------------------


def test_working_days_to_pay_is_none_until_paid():
    assert rec().working_days_to_pay() is None
    assert rec(paid_date=MON_8_JAN_2024).working_days_to_pay() == 5


def test_breached_deadline_is_false_while_unpaid_however_old():
    """SURPRISE (boundary class): `breached_deadline` reads only `paid_date`, so a
    refund that has NEVER been paid returns False forever. The breach register
    (`deadline_breaches`) therefore counts only refunds that were eventually paid
    late — never the ones still being sat on, which are the worse case."""
    ancient = rec(request_date=dt.date(2020, 1, 1))
    assert ancient.working_days_to_pay() is None
    assert ancient.breached_deadline() is False


def test_breached_deadline_boundary_is_strictly_more_than_ten_working_days():
    on_time = rec(request_date=MON_1_JAN_2024, paid_date=dt.date(2024, 1, 15))
    assert on_time.working_days_to_pay() == 10
    assert on_time.breached_deadline() is False
    late = rec(request_date=MON_1_JAN_2024, paid_date=dt.date(2024, 1, 16))
    assert late.working_days_to_pay() == 11
    assert late.breached_deadline() is True


def test_is_overdue_true_once_past_ten_working_days_while_pending():
    r = rec(request_date=MON_1_JAN_2024)
    assert r.is_overdue(dt.date(2024, 1, 15)) is False   # exactly 10
    assert r.is_overdue(dt.date(2024, 1, 16)) is True    # 11


def test_is_overdue_false_once_paid():
    r = rec(status=RefundStatus.PAID, paid_date=dt.date(2024, 1, 3))
    assert r.is_overdue(dt.date(2030, 1, 1)) is False


@pytest.mark.parametrize("status", [RefundStatus.REJECTED, RefundStatus.HELD])
def test_is_overdue_false_forever_for_rejected_and_held(status):
    """SURPRISE (boundary class, money-relevant): HELD and REJECTED suppress the
    overdue test unconditionally and with no expiry. Moving a refund to HELD stops
    the SLC 14 clock permanently — the exact behaviour the module's own docstring
    describes suppliers being fined for in 2022."""
    r = rec(status=status)
    assert r.is_overdue(dt.date(2099, 1, 1)) is False


# ---------------------------------------------------------------------------
# CreditRefundBook state transitions
# ---------------------------------------------------------------------------


def test_raise_approve_pay_happy_path():
    book = CreditRefundBook()
    book.raise_refund(rec())
    assert book.approve("A1", dt.date(2024, 1, 3)).status == RefundStatus.APPROVED
    paid = book.pay("A1", dt.date(2024, 1, 8))
    assert paid.status == RefundStatus.PAID
    assert paid.paid_date == dt.date(2024, 1, 8)
    assert book.pending_refunds() == []


def test_update_targets_the_first_open_refund_not_a_named_one():
    """SURPRISE (boundary class, money-relevant): records carry no refund id, and
    `_update` matches on account_id alone, taking the FIRST open record. With two
    open refunds on one account, `approve("A1")` silently approves the older £120
    one; there is no way to address the £80 one."""
    book = CreditRefundBook()
    book.raise_refund(rec(amount=120.0, request_date=MON_1_JAN_2024))
    book.raise_refund(rec(amount=80.0, request_date=dt.date(2024, 2, 1)))
    approved = book.approve("A1", dt.date(2024, 3, 1))
    assert approved.credit_amount_gbp == 120.0
    assert [r.status for r in book._records] == [RefundStatus.APPROVED, RefundStatus.PENDING]


def test_update_on_an_unknown_or_closed_account_raises():
    book = CreditRefundBook()
    with pytest.raises(ValueError, match="No open refund"):
        book.pay("NOPE", MON_8_JAN_2024)
    book.raise_refund(rec())
    book.reject("A1")
    with pytest.raises(ValueError, match="No open refund"):
        book.pay("A1", MON_8_JAN_2024)  # REJECTED is terminal


def test_held_is_not_terminal_and_can_still_be_paid():
    """HELD is skipped by the overdue test but NOT by `_update`'s open-record
    filter, so a held refund can still be paid later."""
    book = CreditRefundBook()
    book.raise_refund(rec(account_id="H1", amount=500.0))
    book.hold("H1")
    assert book.pay("H1", dt.date(2025, 1, 2)).status == RefundStatus.PAID


# ---------------------------------------------------------------------------
# Book-level registers and totals
# ---------------------------------------------------------------------------


def test_held_refund_disappears_from_both_the_overdue_register_and_the_liability():
    """SURPRISE (boundary class, money-relevant): a HELD refund is excluded from
    `overdue_refunds` AND from `total_outstanding_gbp` (which counts only PENDING
    and APPROVED). £500 genuinely owed back to the customer shows as £0 outstanding
    and raises no breach, indefinitely."""
    book = CreditRefundBook()
    book.raise_refund(rec(account_id="H1", amount=500.0))
    book.hold("H1")
    assert book.overdue_refunds(dt.date(2025, 1, 1)) == []
    assert book.total_outstanding_gbp() == 0
    assert book.deadline_breaches() == []


def test_rejected_refund_also_drops_out_of_outstanding_despite_remaining_open():
    """The RefundStatus.REJECTED comment says the balance "remains open", but the
    outstanding total counts only PENDING/APPROVED, so it contributes nothing."""
    book = CreditRefundBook()
    book.raise_refund(rec(account_id="R1", amount=90.0))
    book.reject("R1")
    assert book.total_outstanding_gbp() == 0


def test_total_outstanding_counts_pending_and_approved():
    book = CreditRefundBook()
    book.raise_refund(rec(account_id="A1", amount=120.0))
    book.raise_refund(rec(account_id="A2", amount=80.5))
    book.approve("A2", dt.date(2024, 1, 3))
    assert book.total_outstanding_gbp() == 200.5


def test_overdue_register_picks_up_a_stale_pending_refund():
    book = CreditRefundBook()
    book.raise_refund(rec(account_id="A1", request_date=MON_1_JAN_2024))
    assert [r.account_id for r in book.overdue_refunds(dt.date(2024, 2, 1))] == ["A1"]


def test_refund_summary_shape():
    book = CreditRefundBook()
    book.raise_refund(rec(account_id="A1", amount=120.0))
    book.raise_refund(rec(account_id="A2", amount=80.0))
    book.pay("A2", dt.date(2024, 2, 1))  # 22 working days -> a breach
    assert book.refund_summary() == {
        "total_refunds": 2,
        "paid": 1,
        "pending": 1,
        "deadline_breaches": 1,
        "total_outstanding_gbp": 120.0,
    }


def test_empty_book_summary():
    assert CreditRefundBook().refund_summary() == {
        "total_refunds": 0,
        "paid": 0,
        "pending": 0,
        "deadline_breaches": 0,
        "total_outstanding_gbp": 0,
    }


@pytest.mark.parametrize("trigger", list(RefundTrigger))
def test_trigger_does_not_change_the_deadline_treatment(trigger):
    """Every trigger — including ACCOUNT_CLOSURE and DECEASED_ESTATE, which in
    practice run to different timescales — shares the same 10-working-day test."""
    r = rec(trigger=trigger, request_date=MON_1_JAN_2024)
    assert r.is_overdue(dt.date(2024, 1, 16)) is True
