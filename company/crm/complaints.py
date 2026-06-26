from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import List, Optional

OMBUDSMAN_ESCALATION_DAYS = 56  # 8 weeks per Ofgem SLC 2.7


class ComplaintCategory(str, Enum):
    BILLING = "billing"
    METERING = "metering"
    SUPPLY_INTERRUPTION = "supply_interruption"
    SWITCHING = "switching"
    CUSTOMER_SERVICE = "customer_service"
    DEBT_HANDLING = "debt_handling"
    PPM = "ppm"
    OTHER = "other"


class ComplaintStatus(str, Enum):
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    RESOLVED = "resolved"
    DEADLOCKED = "deadlocked"          # supplier cannot resolve; eligble for Ombudsman
    ESCALATED_TO_OMBUDSMAN = "escalated_to_ombudsman"
    OMBUDSMAN_CLOSED = "ombudsman_closed"


@dataclass
class Complaint:
    complaint_id: int
    customer_id: str
    category: ComplaintCategory
    opened_date: date
    description: str
    status: ComplaintStatus = ComplaintStatus.OPEN
    resolved_date: Optional[date] = None
    resolution_summary: Optional[str] = None
    redress_gbp: float = 0.0
    escalated_date: Optional[date] = None

    @property
    def is_open(self) -> bool:
        return self.status in (
            ComplaintStatus.OPEN,
            ComplaintStatus.UNDER_INVESTIGATION,
        )

    def days_open(self, as_of: date) -> int:
        end = self.resolved_date or as_of
        return (end - self.opened_date).days

    def eligible_for_ombudsman(self, as_of: date) -> bool:
        if not self.is_open:
            return False
        return self.days_open(as_of) >= OMBUDSMAN_ESCALATION_DAYS


@dataclass
class ComplaintBook:
    _complaints: List[Complaint] = field(default_factory=list)
    _next_id: int = field(default=1)

    def raise_complaint(
        self,
        customer_id: str,
        category: ComplaintCategory,
        opened_date: date,
        description: str = "",
    ) -> Complaint:
        c = Complaint(
            complaint_id=self._next_id,
            customer_id=customer_id,
            category=category,
            opened_date=opened_date,
            description=description,
        )
        self._complaints.append(c)
        self._next_id += 1
        return c

    def update_status(self, complaint_id: int, status: ComplaintStatus) -> bool:
        for c in self._complaints:
            if c.complaint_id == complaint_id:
                c.status = status
                return True
        return False

    def resolve(
        self,
        complaint_id: int,
        resolved_date: date,
        resolution_summary: str = "",
        redress_gbp: float = 0.0,
    ) -> bool:
        for c in self._complaints:
            if c.complaint_id == complaint_id:
                c.status = ComplaintStatus.RESOLVED
                c.resolved_date = resolved_date
                c.resolution_summary = resolution_summary
                c.redress_gbp = redress_gbp
                return True
        return False

    def escalate_to_ombudsman(self, complaint_id: int, as_of: date) -> bool:
        for c in self._complaints:
            if c.complaint_id == complaint_id and c.eligible_for_ombudsman(as_of):
                c.status = ComplaintStatus.ESCALATED_TO_OMBUDSMAN
                c.escalated_date = as_of
                return True
        return False

    def overdue_for_ombudsman(self, as_of: date) -> List[Complaint]:
        return [c for c in self._complaints if c.eligible_for_ombudsman(as_of)]

    def complaints_for_customer(self, customer_id: str) -> List[Complaint]:
        return [c for c in self._complaints if c.customer_id == customer_id]

    def annual_summary(self, year: int) -> dict:
        year_complaints = [c for c in self._complaints if c.opened_date.year == year]
        if not year_complaints:
            result = dict(year=year, total=0, resolved=0, escalated=0,
                          outstanding=0, total_redress_gbp=0.0,
                          by_category=dict())
            return result
        resolved = sum(1 for c in year_complaints if c.status == ComplaintStatus.RESOLVED)
        escalated = sum(
            1 for c in year_complaints
            if c.status == ComplaintStatus.ESCALATED_TO_OMBUDSMAN
        )
        outstanding = sum(1 for c in year_complaints if c.is_open)
        redress = round(sum(c.redress_gbp for c in year_complaints), 2)
        by_cat = {}
        for c in year_complaints:
            by_cat[c.category.value] = by_cat.get(c.category.value, 0) + 1
        result = dict(
            year=year,
            total=len(year_complaints),
            resolved=resolved,
            escalated=escalated,
            outstanding=outstanding,
            total_redress_gbp=redress,
            by_category=by_cat,
        )
        return result
