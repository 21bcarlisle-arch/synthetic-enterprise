"""Customer Account Adjustment Register (Phase GX).

Account adjustments are one-off credits or debits applied to customer
accounts outside of the standard billing workflow. They arise from:
- Goodwill payments (complaint remedy, service failure)
- Back-billing corrections (SLC 14.4: max 12 months backdated billing)
- Erroneous charge reversals
- Missed discount applications
- Data error corrections
- Regulatory redress payments (Ofgem-mandated remedies)

Approval framework:
  <= GBP25: auto-approved (front-line agent authority)
  GBP26-GBP100: team leader approval
  GBP101-GBP500: management approval
  > GBP500: director approval required

Accounting treatment:
  Credit adjustments: reduce revenue (Adj-Type CR) or increase liability
  Debit adjustments: increase revenue (Adj-Type DR) or reduce liability
  All adjustments flow through double-entry ledger when applied

Consumer Duty (2023): goodwill payments must be proportionate to harm;
over-reliance on goodwill (instead of fixing root cause) is a Consumer
Duty failure indicator.

Distinct from: billing_dispute.py (formal billing disputes with SLC 18.9),
back_billing.py (SLC 14.4 back-billing limits), payment_ledger.py.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_AUTO_APPROVE_LIMIT = 25.0
_TEAM_LEADER_LIMIT = 100.0
_MANAGEMENT_LIMIT = 500.0


class AdjustmentType(str, Enum):
    GOODWILL = "goodwill"
    BACK_BILLING_CREDIT = "back_billing_credit"
    ERRONEOUS_CHARGE_REVERSAL = "erroneous_charge_reversal"
    MISSED_DISCOUNT = "missed_discount"
    COMPLAINT_REMEDY = "complaint_remedy"
    DATA_ERROR_CORRECTION = "data_error_correction"
    REGULATORY_REDRESS = "regulatory_redress"
    DEBT_WRITE_OFF = "debt_write_off"


class AdjustmentDirection(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class AdjustmentStatus(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"
    REVERSED = "reversed"


_OPEN = frozenset({AdjustmentStatus.PENDING_APPROVAL, AdjustmentStatus.APPROVED})


def approval_tier_required(amount_gbp: float) -> str:
    if amount_gbp <= _AUTO_APPROVE_LIMIT:
        return "auto"
    if amount_gbp <= _TEAM_LEADER_LIMIT:
        return "team_leader"
    if amount_gbp <= _MANAGEMENT_LIMIT:
        return "management"
    return "director"


@dataclass(frozen=True)
class AccountAdjustmentRecord:
    record_id: str
    account_id: str
    adjustment_type: AdjustmentType
    direction: AdjustmentDirection
    amount_gbp: float
    reason: str
    raised_date: dt.date
    status: AdjustmentStatus = AdjustmentStatus.PENDING_APPROVAL
    approved_by: str = ""
    applied_date: Optional[dt.date] = None
    rejection_reason: str = ""

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    @property
    def approval_tier(self) -> str:
        return approval_tier_required(self.amount_gbp)

    @property
    def net_amount_gbp(self) -> float:
        return -self.amount_gbp if self.direction == AdjustmentDirection.CREDIT else self.amount_gbp

    def adjustment_summary(self) -> str:
        dir_sign = "-" if self.direction == AdjustmentDirection.CREDIT else "+"
        return (
            "Adj " + self.record_id + " account=" + self.account_id
            + " " + dir_sign + "GBP" + str(round(self.amount_gbp, 2))
            + " [" + self.adjustment_type.value + "/" + self.status.value + "]"
        )


class AccountAdjustmentRegister:

    def __init__(self) -> None:
        self._records: List[AccountAdjustmentRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "ADJ-" + str(self._counter).zfill(6)

    def raise_adjustment(
        self,
        account_id: str,
        adjustment_type: AdjustmentType,
        direction: AdjustmentDirection,
        amount_gbp: float,
        reason: str,
        raised_date: dt.date,
    ) -> AccountAdjustmentRecord:
        if amount_gbp <= 0:
            raise ValueError("amount_gbp must be positive")
        tier = approval_tier_required(amount_gbp)
        initial_status = (
            AdjustmentStatus.APPROVED if tier == "auto"
            else AdjustmentStatus.PENDING_APPROVAL
        )
        record = AccountAdjustmentRecord(
            record_id=self._next_id(),
            account_id=account_id, adjustment_type=adjustment_type,
            direction=direction, amount_gbp=amount_gbp, reason=reason,
            raised_date=raised_date, status=initial_status,
            approved_by="auto" if tier == "auto" else "",
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> AccountAdjustmentRecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = AccountAdjustmentRecord(
                    record_id=r.record_id, account_id=r.account_id,
                    adjustment_type=r.adjustment_type, direction=r.direction,
                    amount_gbp=r.amount_gbp, reason=r.reason, raised_date=r.raised_date,
                    status=kwargs.get("status", r.status),
                    approved_by=kwargs.get("approved_by", r.approved_by),
                    applied_date=kwargs.get("applied_date", r.applied_date),
                    rejection_reason=kwargs.get("rejection_reason", r.rejection_reason),
                )
                self._records[i] = updated
                return updated
        raise KeyError("Adjustment " + record_id + " not found")

    def approve(self, record_id: str, approved_by: str) -> AccountAdjustmentRecord:
        return self._update(record_id, status=AdjustmentStatus.APPROVED,
                            approved_by=approved_by)

    def apply(self, record_id: str, applied_date: dt.date) -> AccountAdjustmentRecord:
        return self._update(record_id, status=AdjustmentStatus.APPLIED,
                            applied_date=applied_date)

    def reject(self, record_id: str, rejection_reason: str) -> AccountAdjustmentRecord:
        return self._update(record_id, status=AdjustmentStatus.REJECTED,
                            rejection_reason=rejection_reason)

    def reverse(self, record_id: str) -> AccountAdjustmentRecord:
        return self._update(record_id, status=AdjustmentStatus.REVERSED)

    def pending_approval(self) -> List[AccountAdjustmentRecord]:
        return [r for r in self._records if r.status == AdjustmentStatus.PENDING_APPROVAL]

    def adjustments_for_account(self, account_id: str) -> List[AccountAdjustmentRecord]:
        return [r for r in self._records if r.account_id == account_id]

    def by_type(self, adjustment_type: AdjustmentType) -> List[AccountAdjustmentRecord]:
        return [r for r in self._records if r.adjustment_type == adjustment_type]

    def total_credits_applied_gbp(self) -> float:
        return sum(
            r.amount_gbp for r in self._records
            if r.status == AdjustmentStatus.APPLIED
            and r.direction == AdjustmentDirection.CREDIT
        )

    def total_debits_applied_gbp(self) -> float:
        return sum(
            r.amount_gbp for r in self._records
            if r.status == AdjustmentStatus.APPLIED
            and r.direction == AdjustmentDirection.DEBIT
        )

    def goodwill_spend_gbp(self) -> float:
        return sum(
            r.amount_gbp for r in self._records
            if r.adjustment_type == AdjustmentType.GOODWILL
            and r.status == AdjustmentStatus.APPLIED
        )

    def adjustment_summary(self) -> str:
        n = len(self._records)
        n_pending = len(self.pending_approval())
        credits = round(self.total_credits_applied_gbp(), 2)
        goodwill = round(self.goodwill_spend_gbp(), 2)
        return (
            "Adjustment Register: "
            + str(n) + " adjustments ("
            + str(n_pending) + " pending approval). "
            + "Credits applied: GBP" + str(credits) + ". "
            + "Goodwill: GBP" + str(goodwill) + "."
        )
