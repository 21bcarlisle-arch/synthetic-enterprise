from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class BillingDisputeType(str, Enum):
    WRONG_TARIFF_APPLIED = 'wrong_tariff_applied'
    INCORRECT_UNIT_RATE = 'incorrect_unit_rate'
    MISSING_DISCOUNT = 'missing_discount'
    DUPLICATE_INVOICE = 'duplicate_invoice'
    DIRECT_DEBIT_ERROR = 'direct_debit_error'
    STANDING_CHARGE_ERROR = 'standing_charge_error'
    EXIT_FEE_DISPUTE = 'exit_fee_dispute'


class BillingDisputeStatus(str, Enum):
    OPEN = 'open'
    UNDER_REVIEW = 'under_review'
    RESOLVED_CREDIT = 'resolved_credit'
    RESOLVED_NO_CHANGE = 'resolved_no_change'
    ESCALATED = 'escalated'


@dataclass(frozen=True)
class BillingDispute:
    dispute_id: str
    customer_id: str
    invoice_reference: str
    dispute_type: BillingDisputeType
    disputed_amount_gbp: float
    opened_date: dt.date
    status: BillingDisputeStatus
    credit_applied_gbp: float = 0.0
    closed_date: Optional[dt.date] = None

    @property
    def is_open(self) -> bool:
        return self.status in (BillingDisputeStatus.OPEN, BillingDisputeStatus.UNDER_REVIEW)

    @property
    def days_to_resolution(self) -> Optional[int]:
        if self.closed_date is None:
            return None
        return (self.closed_date - self.opened_date).days


class BillingDisputeBook:
    def __init__(self) -> None:
        self._disputes: Dict[str, BillingDispute] = {}
        self._next_id = 1

    def raise_dispute(self, customer_id: str, invoice_reference: str,
                      dispute_type: BillingDisputeType, disputed_amount_gbp: float,
                      opened_date: dt.date) -> BillingDispute:
        dispute_id = f'BDR-{self._next_id:04d}'
        self._next_id += 1
        d = BillingDispute(
            dispute_id=dispute_id,
            customer_id=customer_id,
            invoice_reference=invoice_reference,
            dispute_type=dispute_type,
            disputed_amount_gbp=disputed_amount_gbp,
            opened_date=opened_date,
            status=BillingDisputeStatus.OPEN,
        )
        self._disputes[dispute_id] = d
        return d

    def update_status(self, dispute_id: str, new_status: BillingDisputeStatus) -> BillingDispute:
        d = self._disputes[dispute_id]
        self._disputes[dispute_id] = BillingDispute(
            dispute_id=d.dispute_id,
            customer_id=d.customer_id,
            invoice_reference=d.invoice_reference,
            dispute_type=d.dispute_type,
            disputed_amount_gbp=d.disputed_amount_gbp,
            opened_date=d.opened_date,
            status=new_status,
            credit_applied_gbp=d.credit_applied_gbp,
            closed_date=d.closed_date,
        )
        return self._disputes[dispute_id]

    def resolve_with_credit(self, dispute_id: str, credit_gbp: float,
                            closed_date: dt.date) -> BillingDispute:
        d = self._disputes[dispute_id]
        self._disputes[dispute_id] = BillingDispute(
            dispute_id=d.dispute_id,
            customer_id=d.customer_id,
            invoice_reference=d.invoice_reference,
            dispute_type=d.dispute_type,
            disputed_amount_gbp=d.disputed_amount_gbp,
            opened_date=d.opened_date,
            status=BillingDisputeStatus.RESOLVED_CREDIT,
            credit_applied_gbp=credit_gbp,
            closed_date=closed_date,
        )
        return self._disputes[dispute_id]

    def resolve_no_change(self, dispute_id: str, closed_date: dt.date) -> BillingDispute:
        d = self._disputes[dispute_id]
        self._disputes[dispute_id] = BillingDispute(
            dispute_id=d.dispute_id,
            customer_id=d.customer_id,
            invoice_reference=d.invoice_reference,
            dispute_type=d.dispute_type,
            disputed_amount_gbp=d.disputed_amount_gbp,
            opened_date=d.opened_date,
            status=BillingDisputeStatus.RESOLVED_NO_CHANGE,
            credit_applied_gbp=0.0,
            closed_date=closed_date,
        )
        return self._disputes[dispute_id]

    def open_disputes(self) -> List[BillingDispute]:
        return [d for d in self._disputes.values() if d.is_open]

    def disputes_for_customer(self, customer_id: str) -> List[BillingDispute]:
        return [d for d in self._disputes.values() if d.customer_id == customer_id]

    def total_credits_issued_gbp(self) -> float:
        return round(sum(d.credit_applied_gbp for d in self._disputes.values()), 2)

    def annual_summary(self) -> dict:
        all_d = list(self._disputes.values())
        closed = [d for d in all_d if not d.is_open]
        credited = [d for d in all_d if d.status == BillingDisputeStatus.RESOLVED_CREDIT]
        by_type: dict = {}
        for d in all_d:
            by_type[d.dispute_type.value] = by_type.get(d.dispute_type.value, 0) + 1
        avg_days = None
        days_list = [d.days_to_resolution for d in closed if d.days_to_resolution is not None]
        if days_list:
            avg_days = round(sum(days_list) / len(days_list), 1)
        return {
            'total_disputes': len(all_d),
            'open': len(self.open_disputes()),
            'resolved_credit': len(credited),
            'total_credits_issued_gbp': self.total_credits_issued_gbp(),
            'avg_days_to_resolution': avg_days,
            'by_type': by_type,
        }
