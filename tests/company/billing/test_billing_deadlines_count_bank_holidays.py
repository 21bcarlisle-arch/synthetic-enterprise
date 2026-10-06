"""The billing-side regulatory clocks count bank holidays out (atom SP2_1, Pass 2 billing batch).

Subject: the four billing modules that each carried a private, weekend-only
`_working_days_between` until 2026-10-03 -- `credit_refund`, `dd_indemnity`, `deemed_contract`,
`energy_theft_book` -- and now count on `company.compliance.working_days`.

EACH CASE IS A PAIR, and the pair is the control. Over a bank-holiday span the deadline must
NOT read as breached (the weekend-only loop said it was); a few working days later, with no
holiday in the way, it MUST read as breached. The second leg is what stops a verdict wired to
`False` from passing the first.

The dates are real England-and-Wales bank holidays from the committed calendar
(`company/compliance/working_days.py`, sourced from the GDS feed): Christmas Day and Boxing Day
2023 and 2024, New Year's Day 2025, Good Friday 29 March and Easter Monday 1 April 2024.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.credit_refund import CreditRefundRecord, RefundTrigger
from company.billing.dd_indemnity import DDIndemnityClaim, DDIndemnityReason
from company.billing.deemed_contract import DeemedContractRecord, DeemedSupplyReason
from company.billing.energy_theft_book import TheftCase, TheftCaseStatus, TheftType
from company.compliance.working_days import bank_holidays

D = dt.date


def _refund(start):
    return lambda as_of: CreditRefundRecord("A", start, RefundTrigger.CUSTOMER_REQUEST,
                                            50.0).is_overdue(as_of)


def _indemnity(start):
    return lambda as_of: DDIndemnityClaim("C", "A", start, start, 50.0,
                                          DDIndemnityReason.AMOUNT_INCORRECT
                                          ).is_investigation_overdue(as_of)


def _deemed(start):
    return lambda as_of: DeemedContractRecord("A", "MPAN", start, DeemedSupplyReason.NEW_TENANT
                                              ).is_notification_overdue(as_of)


def _theft(start):
    return lambda as_of: TheftCase("T", "A", "MPAN", start, TheftType.BYPASSED_METER, 100.0,
                                   status=TheftCaseStatus.CONFIRMED, confirmed_date=start
                                   ).is_dno_notification_overdue(as_of, 2)


# (verdict at a date, start, a date across the holiday that is NOT yet late, a date that IS)
CASES = [
    # SLC 14 refund, 10 working days: Fri 20 Dec 2024 -> Tue 7 Jan 2025 is 9 working days
    # (25, 26 Dec and 1 Jan out); the weekend-only loop counted 12 and called it a breach.
    ("credit_refund", _refund, D(2024, 12, 20), D(2025, 1, 7), D(2025, 1, 9)),
    ("dd_indemnity", _indemnity, D(2024, 12, 20), D(2025, 1, 7), D(2025, 1, 9)),
    # 5 working days across Easter 2024: Thu 28 Mar -> Fri 5 Apr is 4, not 6.
    ("deemed_contract", _deemed, D(2024, 3, 28), D(2024, 4, 5), D(2024, 4, 9)),
    # 2 working days across Christmas 2023: Fri 22 Dec -> Wed 27 Dec is 1, not 3. The 2 is passed
    # in by `_theft`: the module's own DNO deadline is unsourced and None since 2026-10-06.
    ("energy_theft_book", _theft, D(2023, 12, 22), D(2023, 12, 27), D(2023, 12, 29)),
]


def test_every_span_really_crosses_a_committed_bank_holiday():
    """The fixture's premise, checked against the calendar rather than asserted in a comment:
    a span with no holiday in it would make the pair below prove nothing about holidays."""
    hols = bank_holidays()
    for name, _, start, not_late, _late in CASES:
        crossed = [h for h in hols if start < h <= not_late]
        assert crossed, f"{name}: no bank holiday in ({start}, {not_late}]"


@pytest.mark.parametrize("name,make,start,not_late,late", CASES, ids=[c[0] for c in CASES])
def test_the_deadline_does_not_run_through_a_bank_holiday_but_does_fire_after(
        name, make, start, not_late, late):
    overdue = make(start)
    assert overdue(late) is True, f"{name}: the clock can never breach -- the pair proves nothing"
    assert overdue(not_late) is False, (
        f"{name}: {start} -> {not_late} read as breached; a bank holiday was counted as a "
        "working day (the pre-2026-10-03 weekend-only loop)"
    )


def test_the_refund_read_out_counts_the_same_clock():
    """`working_days_to_pay` is what the credit-refund door publishes to the world's log."""
    rec = CreditRefundRecord("A", D(2024, 12, 20), RefundTrigger.CUSTOMER_REQUEST, 50.0,
                             paid_date=D(2025, 1, 7))
    assert rec.working_days_to_pay() == 9
    assert rec.breached_deadline() is False
