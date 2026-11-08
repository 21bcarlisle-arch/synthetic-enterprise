"""Customer Complaint Root Cause Analyser (Phase DS).

Ofgem Consumer Duty (2023) requires suppliers to:
- Identify and address root causes of customer complaints
- Track complaint patterns and trends
- Demonstrate that complaint learnings are fed back into product/process design
- Report complaint root causes to Ofgem on request

Standard Energy Ombudsman complaint categories:
- Billing: estimated readings, incorrect tariff, direct debit issues
- Transfer/switching: delays, erroneous transfers, loss of dual fuel discount
- Metering: inaccurate meter reads, smart meter installation delays
- Customer service: unresponsive, poor information, vulnerable not identified
- Disconnection/debt: improper process, vulnerable customer disconnected

Root cause analysis prevents systematic failures:
- One billing bug can generate hundreds of complaints
- Identifying the upstream cause is more efficient than resolving one-by-one
- Ofgem views systemic unresolved root causes as Consumer Duty failures

Epistemic note: the company observes its own complaint records. It cannot
see competitor complaint rates.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ComplaintCategory(str, Enum):
    BILLING = "billing"
    TARIFF_PRICING = "tariff_pricing"
    TRANSFER_SWITCHING = "transfer_switching"
    METERING = "metering"
    CUSTOMER_SERVICE = "customer_service"
    DISCONNECTION_DEBT = "disconnection_debt"
    SMART_METER = "smart_meter"
    DIRECT_DEBIT = "direct_debit"
    OTHER = "other"


class RootCauseStatus(str, Enum):
    OPEN = "open"                 # root cause identified, not yet fixed
    IN_REMEDIATION = "in_remediation"
    CLOSED = "closed"             # root cause fixed
    SYSTEMIC = "systemic"         # ongoing systemic issue, Ofgem-level concern
    MONITOR = "monitor"           # low volume, monitoring


class ImpactSeverity(str, Enum):
    LOW = "low"          # 1-5 customers affected
    MEDIUM = "medium"    # 6-50 customers
    HIGH = "high"        # 51-200 customers
    CRITICAL = "critical"  # 200+ or regulatory risk


_REMEDIATION_SLA_DAYS: Dict[str, int] = {
    ImpactSeverity.CRITICAL: 5,
    ImpactSeverity.HIGH: 14,
    ImpactSeverity.MEDIUM: 30,
    ImpactSeverity.LOW: 90,
}


@dataclass(frozen=True)
class ComplaintRootCause:
    rca_id: str
    category: ComplaintCategory
    description: str
    identified_date: dt.date
    severity: ImpactSeverity
    complaints_attributed: int
    estimated_customers_affected: int
    status: RootCauseStatus
    remediation_owner: str
    closed_date: Optional[dt.date] = None
    linked_slc: Optional[str] = None       # e.g. "SLC 6" for billing

    @property
    def remediation_sla_days(self) -> int:
        return _REMEDIATION_SLA_DAYS[self.severity]

    def is_overdue(self, as_of: dt.date) -> bool:
        if self.status == RootCauseStatus.CLOSED:
            return False
        target = self.identified_date + dt.timedelta(days=self.remediation_sla_days)
        return as_of > target

    @property
    def is_systemic(self) -> bool:
        return self.status == RootCauseStatus.SYSTEMIC

    @property
    def is_open(self) -> bool:
        return self.status in (RootCauseStatus.OPEN, RootCauseStatus.IN_REMEDIATION,
                               RootCauseStatus.SYSTEMIC)


class ComplaintRootCauseAnalyser:
    """Tracks complaint root causes and remediation progress."""

    def __init__(self) -> None:
        self._records: Dict[str, ComplaintRootCause] = {}
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"RCA-{self._seq:04d}"

    def identify(
        self,
        category: ComplaintCategory,
        description: str,
        identified_date: dt.date,
        severity: ImpactSeverity,
        complaints_attributed: int,
        estimated_customers_affected: int,
        remediation_owner: str,
        linked_slc: Optional[str] = None,
    ) -> ComplaintRootCause:
        rca_id = self._next_id()
        rec = ComplaintRootCause(
            rca_id=rca_id,
            category=category,
            description=description,
            identified_date=identified_date,
            severity=severity,
            complaints_attributed=complaints_attributed,
            estimated_customers_affected=estimated_customers_affected,
            status=RootCauseStatus.OPEN,
            remediation_owner=remediation_owner,
            linked_slc=linked_slc,
        )
        self._records[rca_id] = rec
        return rec

    def _update_status(self, rca_id: str, status: RootCauseStatus,
                       closed_date: Optional[dt.date] = None) -> ComplaintRootCause:
        rec = self._records[rca_id]
        updated = ComplaintRootCause(
            rca_id=rec.rca_id, category=rec.category, description=rec.description,
            identified_date=rec.identified_date, severity=rec.severity,
            complaints_attributed=rec.complaints_attributed,
            estimated_customers_affected=rec.estimated_customers_affected,
            status=status, remediation_owner=rec.remediation_owner,
            closed_date=closed_date, linked_slc=rec.linked_slc,
        )
        self._records[rca_id] = updated
        return updated

    def start_remediation(self, rca_id: str) -> ComplaintRootCause:
        return self._update_status(rca_id, RootCauseStatus.IN_REMEDIATION)

    def close(self, rca_id: str, closed_date: dt.date) -> ComplaintRootCause:
        return self._update_status(rca_id, RootCauseStatus.CLOSED, closed_date)

    def escalate_systemic(self, rca_id: str) -> ComplaintRootCause:
        return self._update_status(rca_id, RootCauseStatus.SYSTEMIC)

    def get(self, rca_id: str) -> Optional[ComplaintRootCause]:
        return self._records.get(rca_id)

    def open_rcas(self) -> List[ComplaintRootCause]:
        return [r for r in self._records.values() if r.is_open]

    def overdue_rcas(self, as_of: dt.date) -> List[ComplaintRootCause]:
        return [r for r in self._records.values() if r.is_overdue(as_of)]

    def systemic_issues(self) -> List[ComplaintRootCause]:
        return [r for r in self._records.values() if r.is_systemic]

    def by_category(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for r in self._records.values():
            out[r.category.value] = out.get(r.category.value, 0) + r.complaints_attributed
        return out

    def critical_open(self) -> List[ComplaintRootCause]:
        return [r for r in self.open_rcas()
                if r.severity == ImpactSeverity.CRITICAL]

    def total_complaints_attributed(self) -> int:
        return sum(r.complaints_attributed for r in self._records.values())

    def rca_summary(self) -> str:
        n_open = len(self.open_rcas())
        n_systemic = len(self.systemic_issues())
        n_critical = len(self.critical_open())
        total = self.total_complaints_attributed()
        return (
            f"Complaint Root Cause Analyser (Consumer Duty): "
            f"{len(self._records)} RCAs identified; "
            f"{n_open} open ({n_critical} critical); {n_systemic} systemic. "
            f"Total complaints attributed: {total}."
        )
