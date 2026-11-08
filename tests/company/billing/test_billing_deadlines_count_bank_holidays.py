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


from company.billing.credit_refund import CreditRefundRecord, RefundTrigger
from company.billing.energy_theft_book import TheftCase, TheftCaseStatus, TheftType

D = dt.date


def _refund(start):
    return lambda as_of: CreditRefundRecord("A", start, RefundTrigger.CUSTOMER_REQUEST,
                                            50.0).is_overdue(as_of)






def _theft(start):
    return lambda as_of: TheftCase("T", "A", "MPAN", start, TheftType.BYPASSED_METER, 100.0,
                                   status=TheftCaseStatus.CONFIRMED, confirmed_date=start
                                   ).is_dno_notification_overdue(as_of, 2)








def test_the_refund_read_out_counts_the_same_clock():
    """`working_days_to_pay` is what the credit-refund door publishes to the world's log."""
    rec = CreditRefundRecord("A", D(2024, 12, 20), RefundTrigger.CUSTOMER_REQUEST, 50.0,
                             paid_date=D(2025, 1, 7))
    assert rec.working_days_to_pay() == 9
    assert rec.breached_deadline() is False
