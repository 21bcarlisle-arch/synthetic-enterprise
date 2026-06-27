"""Credit Refund Book: Ofgem SLC 14 credit balance refund obligations."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


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


_REFUND_DEADLINE_WORKING_DAYS = 10


def _working_days_between(start: dt.date, end: dt.date) -> int:
    days = 0
    current = start
    while current < end:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            days += 1
    return days


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
        return _working_days_between(self.request_date, self.paid_date)

    def is_overdue(self, as_of: dt.date) -> bool:
        if self.status == RefundStatus.PAID:
            return False
        if self.status in (RefundStatus.REJECTED, RefundStatus.HELD):
            return False
        return _working_days_between(self.request_date, as_of) > _REFUND_DEADLINE_WORKING_DAYS

    def breached_deadline(self) -> bool:
        wd = self.working_days_to_pay()
        if wd is None:
            return False
        return wd > _REFUND_DEADLINE_WORKING_DAYS


class CreditRefundBook:
    """Tracks customer credit balance refund requests and Ofgem SLC 14 compliance.

    Real calibration:
    - Ofgem SLC 14: supplier must refund credit balance within 10 working days
      of a valid request (amended 2019; previously 28 calendar days).
    - SLC 22A: annual credit balance review -- supplier must proactively contact
      customers with credit >= threshold and offer refund (energy-only tariff).
    - Auto-comp: GBP30 if refund not paid within 10 working days (proposed 2023).
    - 2022 crisis: many suppliers held credit balances to shore up cash -- Ofgem
      issued multiple enforcement notices for SLC 14 breaches.
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
            "total_outstanding_gbp": self.total_outstanding_gbp(),
        }
