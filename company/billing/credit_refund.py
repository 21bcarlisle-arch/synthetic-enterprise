"""Credit Refund Book: the credit-balance refund a leaver is owed, GSoP 2015 reg 6D.

Reg 6D (inserted by SI 2019/218, in force 1 May 2019): "within 10 working days of issuing a
customer's final bill, or if applicable, corrected final bill, refund any outstanding credit
balance". Until 2026-10-25 this module called it "SLC 14", the wrong locus
(`docs/market_research/home_moves.md` s.8.8, correction of 24 Oct). The
deadline is the same, so no figure moved with the label.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from company.compliance.working_days import add_working_days, working_days_between
from company.regulatory.gsop import standard_payment_gbp


class RefundTrigger(str, Enum):
    CUSTOMER_REQUEST = "customer_request"
    ACCOUNT_CLOSURE = "account_closure"
    ANNUAL_CREDIT_REVIEW = "annual_credit_review"   # SLC 22A annual review
    DECEASED_ESTATE = "deceased_estate"


class RefundStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"   # e.g. disputed balance; remains open
    HELD = "held"           # held pending final bill (closure only)


#: GSoP 2015 reg 6D(3), SI 2019/218 reg 3: 10 working days from the final bill's issue
#: (`docs/market_research/home_moves.md` s.8.8).
_REFUND_DEADLINE_WORKING_DAYS = 10

#: SI 2019/218 reg 1(1): the instrument, and reg 6D with it, came into force on 1 May 2019
#: (legislation.gov.uk/uksi/2019/218/made, read 2026-10-25). A refund due before then is not a
#: guaranteed standard and owes no payment, however late.
REG_6D_IN_FORCE = dt.date(2019, 5, 1)


def refund_due_date(final_bill_issued: dt.date) -> dt.date:
    """The last working day reg 6D allows: the 10th after the final bill's issue."""
    return add_working_days(final_bill_issued, _REFUND_DEADLINE_WORKING_DAYS)


def scheduled_refund_date(final_bill_issued: dt.date) -> dt.date:
    """When this company pays a closure refund: on the deadline itself.

    The choice of day inside the window is the company's, and no published source gives a
    supplier's typical lag (GAP, home_moves.md s.8.8). The deadline is the one day the rule fixes,
    and paying on it holds the customer's money longest, the direction that errs against the thesis
    (F11). It counts on the company's bank-holiday calendar, so the date is never late by its own
    rule. Until 2026-10-25 the world drew this lag instead, 10% of it 11 to 25 working days.
    """
    return refund_due_date(final_bill_issued)


@dataclass(frozen=True)
class CreditRefundRecord:
    account_id: str
    request_date: dt.date
    trigger: RefundTrigger
    credit_amount_gbp: float
    status: RefundStatus = RefundStatus.PENDING
    approved_date: Optional[dt.date] = None
    paid_date: Optional[dt.date] = None

    def working_days_to_pay(self) -> Optional[int]:
        if self.paid_date is None:
            return None
        return working_days_between(self.request_date, self.paid_date)

    def is_overdue(self, as_of: dt.date) -> bool:
        if self.status == RefundStatus.PAID:
            return False
        if self.status in (RefundStatus.REJECTED, RefundStatus.HELD):
            return False
        return working_days_between(self.request_date, as_of) > _REFUND_DEADLINE_WORKING_DAYS

    def reg_6d_binds(self) -> bool:
        return refund_due_date(self.request_date) >= REG_6D_IN_FORCE

    def breached_deadline(self) -> bool:
        """Paid after the reg 6D deadline, on a refund the standard bound."""
        wd = self.working_days_to_pay()
        if wd is None or not self.reg_6d_binds():
            return False
        return wd > _REFUND_DEADLINE_WORKING_DAYS

    def reg_6d_payment(self) -> float:
        """The guaranteed-standard payment a late refund owes: the rate in force the day it failed."""
        if not self.breached_deadline():
            return 0.0
        failed_on = refund_due_date(self.request_date) + dt.timedelta(days=1)
        return standard_payment_gbp(failed_on)


class CreditRefundBook:
    """Tracks customer credit balance refunds against GSoP reg 6D.

    - Reg 6D: a leaver's credit is refunded within 10 working days of the final bill's issue, or
      of a corrected final bill. `request_date` is that issue date for an account closure.
    - A late one owes the standard payment, £30 and £40 for failures from 2 January 2025
      (`company/regulatory/gsop.py`), and none before reg 6D came into force.
    - SLC 22A: annual credit balance review -- supplier must proactively contact
      customers with credit >= threshold and offer refund (energy-only tariff).
    """

    def __init__(self) -> None:
        self._records: List[CreditRefundRecord] = []

    def raise_refund(self, record: CreditRefundRecord) -> CreditRefundRecord:
        self._records.append(record)
        return record

    def _update(self, account_id: str, **kwargs) -> CreditRefundRecord:
        import dataclasses
        for i, r in enumerate(self._records):
            if r.account_id == account_id and r.status not in (
                RefundStatus.PAID, RefundStatus.REJECTED
            ):
                updated = dataclasses.replace(r, **kwargs)
                self._records[i] = updated
                return updated
        raise ValueError(f"No open refund for {account_id}")

    def approve(self, account_id: str, approved_date: dt.date) -> CreditRefundRecord:
        return self._update(account_id, status=RefundStatus.APPROVED,
                            approved_date=approved_date)

    def pay(self, account_id: str, paid_date: dt.date) -> CreditRefundRecord:
        return self._update(account_id, status=RefundStatus.PAID, paid_date=paid_date)

    def reject(self, account_id: str) -> CreditRefundRecord:
        return self._update(account_id, status=RefundStatus.REJECTED)

    def hold(self, account_id: str) -> CreditRefundRecord:
        return self._update(account_id, status=RefundStatus.HELD)

    def pending_refunds(self) -> List[CreditRefundRecord]:
        return [r for r in self._records
                if r.status in (RefundStatus.PENDING, RefundStatus.APPROVED)]

    def overdue_refunds(self, as_of: dt.date) -> List[CreditRefundRecord]:
        return [r for r in self._records if r.is_overdue(as_of)]

    def deadline_breaches(self) -> List[CreditRefundRecord]:
        return [r for r in self._records if r.breached_deadline()]

    def total_outstanding_gbp(self) -> float:
        return round(sum(
            r.credit_amount_gbp for r in self._records
            if r.status in (RefundStatus.PENDING, RefundStatus.APPROVED)
        ), 2)

    def refund_summary(self) -> dict:
        total = len(self._records)
        paid = [r for r in self._records if r.status == RefundStatus.PAID]
        return {
            "total_refunds": total,
            "paid": len(paid),
            "pending": len(self.pending_refunds()),
            "deadline_breaches": len(self.deadline_breaches()),
            "compensation_gbp": round(sum(r.reg_6d_payment() for r in self._records), 2),
            "total_outstanding_gbp": self.total_outstanding_gbp(),
        }
