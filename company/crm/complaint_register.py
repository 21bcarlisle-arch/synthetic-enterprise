"""Complaint handling register: SLC 27 compliance, 8-week clock, Ombudsman referrals."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


RESOLUTION_DEADLINE_DAYS = 56  # 8 calendar weeks per SLC 27
OMBUDSMAN_ELIGIBLE_DAYS = 8 * 7  # customer can refer after 8 weeks


class ComplaintCategory(str, Enum):
    BILLING = 'billing'
    METER_READS = 'meter_reads'
    SUPPLY_FAILURE = 'supply_failure'
    SWITCH = 'switch'
    DEBT_COLLECTION = 'debt_collection'
    CUSTOMER_SERVICE = 'customer_service'
    SMART_METER = 'smart_meter'
    TARIFF = 'tariff'


class ComplaintStatus(str, Enum):
    OPEN = 'open'
    UNDER_INVESTIGATION = 'under_investigation'
    AWAITING_CUSTOMER = 'awaiting_customer'
    RESOLVED = 'resolved'
    UPHELD = 'upheld'
    NOT_UPHELD = 'not_upheld'
    OMBUDSMAN_REFERRED = 'ombudsman_referred'


@dataclass
class Complaint:
    complaint_id: str
    customer_id: str
    received_date: dt.date
    category: ComplaintCategory
    description: str
    status: ComplaintStatus = ComplaintStatus.OPEN
    resolution_date: Optional[dt.date] = None
    goodwill_payment_gbp: float = 0.0
    is_vulnerable: bool = False

    def deadline(self) -> dt.date:
        return self.received_date + dt.timedelta(days=RESOLUTION_DEADLINE_DAYS)

    def days_open(self, as_of: dt.date) -> int:
        end = self.resolution_date if self.resolution_date else as_of
        return (end - self.received_date).days

    def is_overdue(self, as_of: dt.date) -> bool:
        if self.status in (ComplaintStatus.RESOLVED, ComplaintStatus.UPHELD,
                            ComplaintStatus.NOT_UPHELD, ComplaintStatus.OMBUDSMAN_REFERRED):
            return False
        return (as_of - self.received_date).days > RESOLUTION_DEADLINE_DAYS

    def is_ombudsman_eligible(self, as_of: dt.date) -> bool:
        return (as_of - self.received_date).days >= OMBUDSMAN_ELIGIBLE_DAYS

    def resolve(self, resolution_date: dt.date, upheld: bool,
                  goodwill_gbp: float = 0.0) -> None:
        self.resolution_date = resolution_date
        self.status = ComplaintStatus.UPHELD if upheld else ComplaintStatus.NOT_UPHELD
        self.goodwill_payment_gbp = goodwill_gbp

    def refer_to_ombudsman(self, referral_date: dt.date) -> None:
        self.status = ComplaintStatus.OMBUDSMAN_REFERRED
        self.resolution_date = referral_date


class ComplaintRegister:
    def __init__(self) -> None:
        self._complaints: List[Complaint] = []

    def raise_complaint(self, complaint_id: str, customer_id: str,
                          received_date: dt.date, category: ComplaintCategory,
                          description: str = '', is_vulnerable: bool = False) -> Complaint:
        c = Complaint(
            complaint_id=complaint_id, customer_id=customer_id,
            received_date=received_date, category=category,
            description=description, is_vulnerable=is_vulnerable,
        )
        self._complaints.append(c)
        return c

    def get(self, complaint_id: str) -> Optional[Complaint]:
        return next((c for c in self._complaints if c.complaint_id == complaint_id), None)

    def open_complaints(self) -> List[Complaint]:
        return [c for c in self._complaints if c.status in (
            ComplaintStatus.OPEN, ComplaintStatus.UNDER_INVESTIGATION,
            ComplaintStatus.AWAITING_CUSTOMER
        )]

    def overdue_complaints(self, as_of: dt.date) -> List[Complaint]:
        return [c for c in self.open_complaints() if c.is_overdue(as_of)]

    def complaints_per_100_customers(self, customer_count: int,
                                       year: int) -> float:
        if customer_count == 0:
            return 0.0
        count = len([c for c in self._complaints
                      if c.received_date.year == year])
        return round(count / customer_count * 100, 2)

    def upheld_rate_pct(self, year: int) -> Optional[float]:
        resolved = [c for c in self._complaints
                    if c.received_date.year == year
                    and c.status in (ComplaintStatus.UPHELD, ComplaintStatus.NOT_UPHELD)]
        if not resolved:
            return None
        upheld = sum(1 for c in resolved if c.status == ComplaintStatus.UPHELD)
        return round(upheld / len(resolved) * 100, 1)

    def total_goodwill_gbp(self, year: int) -> float:
        return round(sum(
            c.goodwill_payment_gbp for c in self._complaints
            if c.received_date.year == year
        ), 2)

    def complaints_summary(self, as_of: dt.date, customer_count: int) -> dict:
        year = as_of.year
        by_cat: Dict[str, int] = {}
        for c in self._complaints:
            if c.received_date.year == year:
                k = c.category.value
                by_cat[k] = by_cat.get(k, 0) + 1
        return {
            'year': year,
            'open': len(self.open_complaints()),
            'overdue': len(self.overdue_complaints(as_of)),
            'per_100_customers': self.complaints_per_100_customers(customer_count, year),
            'upheld_rate_pct': self.upheld_rate_pct(year),
            'total_goodwill_gbp': self.total_goodwill_gbp(year),
            'by_category': by_cat,
        }
