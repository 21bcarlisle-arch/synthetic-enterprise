from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class DisputeType(str, Enum):
    ESTIMATED_READ = "estimated_read"
    ACTUAL_TOO_HIGH = "actual_too_high"
    METER_FAULT = "meter_fault"
    PRIOR_READING_ERROR = "prior_reading_error"


class DisputeStatus(str, Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED_ACCEPTED = "resolved_accepted"
    RESOLVED_REJECTED = "resolved_rejected"


@dataclass
class MeterDispute:
    dispute_id: int
    customer_id: str
    bill_reference: str
    dispute_type: DisputeType
    billed_read_kwh: float
    claimed_read_kwh: float
    opened_date: date
    status: DisputeStatus = DisputeStatus.OPEN
    resolved_date: Optional[date] = None
    resolution_notes: Optional[str] = None
    credit_applied_gbp: float = 0.0

    @property
    def disputed_kwh(self) -> float:
        return abs(self.billed_read_kwh - self.claimed_read_kwh)

    @property
    def is_open(self) -> bool:
        return self.status in (DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW)


@dataclass
class MeterDisputeBook:
    _disputes: List[MeterDispute] = field(default_factory=list)
    _next_id: int = field(default=1)

    def open_dispute(
        self,
        customer_id: str,
        bill_reference: str,
        dispute_type: DisputeType,
        billed_read_kwh: float,
        claimed_read_kwh: float,
        opened_date: date,
    ) -> MeterDispute:
        d = MeterDispute(
            dispute_id=self._next_id,
            customer_id=customer_id,
            bill_reference=bill_reference,
            dispute_type=dispute_type,
            billed_read_kwh=billed_read_kwh,
            claimed_read_kwh=claimed_read_kwh,
            opened_date=opened_date,
        )
        self._disputes.append(d)
        self._next_id += 1
        return d

    def update_status(self, dispute_id: int, status: DisputeStatus) -> bool:
        for d in self._disputes:
            if d.dispute_id == dispute_id:
                d.status = status
                return True
        return False

    def resolve(
        self,
        dispute_id: int,
        accepted: bool,
        resolved_date: date,
        credit_applied_gbp: float = 0.0,
        notes: Optional[str] = None,
    ) -> bool:
        for d in self._disputes:
            if d.dispute_id == dispute_id:
                d.status = (
                    DisputeStatus.RESOLVED_ACCEPTED if accepted
                    else DisputeStatus.RESOLVED_REJECTED
                )
                d.resolved_date = resolved_date
                d.credit_applied_gbp = credit_applied_gbp
                d.resolution_notes = notes
                return True
        return False

    def outstanding_disputes(self) -> List[MeterDispute]:
        return [d for d in self._disputes if d.is_open]

    def disputes_for_customer(self, customer_id: str) -> List[MeterDispute]:
        return [d for d in self._disputes if d.customer_id == customer_id]

    def annual_summary(self, year: int) -> dict:
        year_disputes = [d for d in self._disputes if d.opened_date.year == year]
        if not year_disputes:
            result = dict(year=year, total=0, accepted=0, rejected=0,
                          outstanding=0, total_credit_gbp=0.0)
            return result
        accepted = sum(
            1 for d in year_disputes if d.status == DisputeStatus.RESOLVED_ACCEPTED
        )
        rejected = sum(
            1 for d in year_disputes if d.status == DisputeStatus.RESOLVED_REJECTED
        )
        outstanding = sum(1 for d in year_disputes if d.is_open)
        credit = round(sum(d.credit_applied_gbp for d in year_disputes), 2)
        result = dict(year=year, total=len(year_disputes), accepted=accepted,
                      rejected=rejected, outstanding=outstanding, total_credit_gbp=credit)
        return result
