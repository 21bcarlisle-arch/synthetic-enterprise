"""Billing Dispute Resolution Book (Phase FC).

When a customer disputes a charge on their bill, the supplier must follow
a formal dispute resolution process.

SLC 23 (Consumer standards): Suppliers must have effective complaint handling.
SLC 14: Billing accuracy obligations.

Dispute resolution stages:
1. RAISED: Customer notifies supplier of dispute
2. INVESTIGATING: Supplier reviews meter reads, tariff history, payments
3. CREDIT_ISSUED: Supplier agrees error; credit applied before resolution
4. RESOLVED_IN_CUSTOMER_FAVOUR: Charge corrected/waived
5. RESOLVED_IN_SUPPLIER_FAVOUR: Original charge confirmed as correct
6. REFERRED_TO_OMBUDSMAN: Customer disagrees with resolution

Key obligations:
- Acknowledge within 3 working days (SLC 18.7)
- Resolve or provide Final Response within 8 weeks (SLC 18.9)
- No disconnection while genuine dispute is unresolved
- Back-billing cap applies to disputed historic charges (SLC 31A)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class DisputeStatus(str, Enum):
    RAISED = "raised"
    INVESTIGATING = "investigating"
    CREDIT_ISSUED = "credit_issued"
    RESOLVED_IN_CUSTOMER_FAVOUR = "resolved_in_customer_favour"
    RESOLVED_IN_SUPPLIER_FAVOUR = "resolved_in_supplier_favour"
    REFERRED_TO_OMBUDSMAN = "referred_to_ombudsman"


class DisputeReason(str, Enum):
    ESTIMATED_BILL = "estimated_bill"
    TARIFF_ERROR = "tariff_error"
    METER_ERROR = "meter_error"
    BACK_BILLING = "back_billing"
    DIRECT_DEBIT_ERROR = "direct_debit_error"
    SWITCH_FINAL_BILL = "switch_final_bill"
    PAYMENT_NOT_CREDITED = "payment_not_credited"


_NO_DISCONNECT_STATUSES = frozenset({
    DisputeStatus.RAISED,
    DisputeStatus.INVESTIGATING,
    DisputeStatus.CREDIT_ISSUED,
})
_FINAL_RESPONSE_DEADLINE_DAYS = 56  # 8 weeks SLC 18.9


@dataclass(frozen=True)
class BillingDispute:
    dispute_id: str
    account_id: str
    raised_at: dt.date
    reason: DisputeReason
    disputed_amount_gbp: float
    status: DisputeStatus = DisputeStatus.RAISED
    credit_applied_gbp: float = 0.0
    resolved_at: Optional[dt.date] = None

    @property
    def is_open(self) -> bool:
        return self.status in (
            DisputeStatus.RAISED,
            DisputeStatus.INVESTIGATING,
            DisputeStatus.CREDIT_ISSUED,
        )

    @property
    def can_disconnect(self) -> bool:
        return self.status not in _NO_DISCONNECT_STATUSES

    @property
    def net_disputed_amount_gbp(self) -> float:
        return self.disputed_amount_gbp - self.credit_applied_gbp

    def is_final_response_overdue(self, as_of: dt.date) -> bool:
        if not self.is_open:
            return False
        return (as_of - self.raised_at).days > _FINAL_RESPONSE_DEADLINE_DAYS

    def dispute_summary(self) -> str:
        return (
            "BillingDispute " + self.dispute_id + " (" + self.account_id + "): "
            + self.reason.value + " GBP" + str(round(self.disputed_amount_gbp, 2))
            + " [" + self.status.value + "]"
        )


class BillingDisputeBook:

    def __init__(self) -> None:
        self._disputes: List[BillingDispute] = []
        self._next_id = 1

    def raise_dispute(
        self,
        account_id: str,
        reason: DisputeReason,
        disputed_amount_gbp: float,
        raised_at: dt.date,
    ) -> BillingDispute:
        did = "DISP-" + str(self._next_id).zfill(5)
        self._next_id += 1
        d = BillingDispute(
            dispute_id=did,
            account_id=account_id,
            raised_at=raised_at,
            reason=reason,
            disputed_amount_gbp=disputed_amount_gbp,
        )
        self._disputes.append(d)
        return d

    def update_dispute(
        self,
        dispute_id: str,
        new_status: DisputeStatus,
        as_of: dt.date,
        credit_applied_gbp: float = 0.0,
    ) -> Optional[BillingDispute]:
        for i, d in enumerate(self._disputes):
            if d.dispute_id == dispute_id:
                resolved_at = as_of if new_status in (
                    DisputeStatus.RESOLVED_IN_CUSTOMER_FAVOUR,
                    DisputeStatus.RESOLVED_IN_SUPPLIER_FAVOUR,
                    DisputeStatus.REFERRED_TO_OMBUDSMAN,
                ) else None
                updated = BillingDispute(
                    dispute_id=d.dispute_id,
                    account_id=d.account_id,
                    raised_at=d.raised_at,
                    reason=d.reason,
                    disputed_amount_gbp=d.disputed_amount_gbp,
                    status=new_status,
                    credit_applied_gbp=credit_applied_gbp,
                    resolved_at=resolved_at,
                )
                self._disputes[i] = updated
                return updated
        return None

    def open_disputes(self) -> List[BillingDispute]:
        return [d for d in self._disputes if d.is_open]

    def disputes_for_account(self, account_id: str) -> List[BillingDispute]:
        return [d for d in self._disputes if d.account_id == account_id]

    def overdue_final_responses(self, as_of: dt.date) -> List[BillingDispute]:
        return [d for d in self.open_disputes() if d.is_final_response_overdue(as_of)]

    def accounts_blocked_from_disconnection(self) -> List[str]:
        return list({d.account_id for d in self.open_disputes() if not d.can_disconnect})

    def total_disputed_amount_gbp(self) -> float:
        return sum(d.disputed_amount_gbp for d in self.open_disputes())

    def dispute_book_summary(self, as_of: dt.date) -> str:
        n_open = len(self.open_disputes())
        n_overdue = len(self.overdue_final_responses(as_of))
        total = self.total_disputed_amount_gbp()
        return (
            "Billing Disputes (" + str(as_of) + "): "
            + str(n_open) + " open. "
            "Overdue final responses: " + str(n_overdue) + ". "
            "Total disputed: GBP" + str(round(total, 0)) + "."
        )
