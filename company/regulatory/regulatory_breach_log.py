"""Regulatory Breach Log.

Central register for potential Standard Licence Condition (SLC) breaches.
Each company module that detects a compliance issue can record an entry.

Ofgem enforcement process:
1. Supplier self-report breach (SLC 27A, SLC 14 etc. have reporting obligations)
2. Ofgem reviews and opens investigation if material
3. Final orders / penalty up to 10% of turnover

Breach severity:
- POTENTIAL: not confirmed, under investigation
- CONFIRMED: breach occurred
- REMEDIATED: breach occurred but fixed and reported

Epistemic: the company knows about its own compliance issues
and is required to report material breaches to Ofgem.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum


class BreachSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"  # Systemic / affects many customers


class BreachStatus(str, Enum):
    POTENTIAL = "potential"
    CONFIRMED = "confirmed"
    REMEDIATED = "remediated"
    CLOSED = "closed"
    REPORTED_TO_OFGEM = "reported_to_ofgem"


class BreachSource(str, Enum):
    INTERNAL_AUDIT = "internal_audit"
    CUSTOMER_COMPLAINT = "customer_complaint"
    OFGEM_REQUEST = "ofgem_request"
    SELF_DETECTION = "self_detection"
    THIRD_PARTY = "third_party"


@dataclass(frozen=True)
class RegulatoryBreachRecord:
    breach_id: str
    slc_reference: str           # e.g. "SLC 14", "SLC 27A"
    description: str
    detected_date: date
    severity: BreachSeverity
    status: BreachStatus
    source: BreachSource
    accounts_affected: int = 0
    estimated_penalty_gbp: float = 0.0
    remediation_date: date | None = None

    @property
    def is_open(self) -> bool:
        return self.status in (BreachStatus.POTENTIAL, BreachStatus.CONFIRMED, BreachStatus.REPORTED_TO_OFGEM)

    @property
    def is_reportable(self) -> bool:
        return self.severity in (BreachSeverity.HIGH, BreachSeverity.CRITICAL)


class RegulatoryBreachLog:
    """Central breach register for regulatory compliance tracking."""

    def __init__(self) -> None:
        self._records: list[RegulatoryBreachRecord] = []

    def record(
        self,
        breach_id: str,
        slc_reference: str,
        description: str,
        detected_date: date,
        severity: BreachSeverity,
        source: BreachSource = BreachSource.SELF_DETECTION,
        accounts_affected: int = 0,
        estimated_penalty_gbp: float = 0.0,
    ) -> RegulatoryBreachRecord:
        record = RegulatoryBreachRecord(
            breach_id=breach_id,
            slc_reference=slc_reference,
            description=description,
            detected_date=detected_date,
            severity=severity,
            status=BreachStatus.POTENTIAL,
            source=source,
            accounts_affected=accounts_affected,
            estimated_penalty_gbp=estimated_penalty_gbp,
        )
        self._records.append(record)
        return record

    def confirm(self, breach_id: str) -> RegulatoryBreachRecord:
        return self._update_status(breach_id, BreachStatus.CONFIRMED)

    def report_to_ofgem(self, breach_id: str) -> RegulatoryBreachRecord:
        return self._update_status(breach_id, BreachStatus.REPORTED_TO_OFGEM)

    def remediate(self, breach_id: str, remediation_date: date) -> RegulatoryBreachRecord:
        old = next(r for r in self._records if r.breach_id == breach_id)
        updated = RegulatoryBreachRecord(
            breach_id=old.breach_id, slc_reference=old.slc_reference,
            description=old.description, detected_date=old.detected_date,
            severity=old.severity, status=BreachStatus.REMEDIATED,
            source=old.source, accounts_affected=old.accounts_affected,
            estimated_penalty_gbp=old.estimated_penalty_gbp,
            remediation_date=remediation_date,
        )
        self._records = [updated if r.breach_id == breach_id else r for r in self._records]
        return updated

    def _update_status(self, breach_id: str, new_status: BreachStatus) -> RegulatoryBreachRecord:
        old = next(r for r in self._records if r.breach_id == breach_id)
        updated = RegulatoryBreachRecord(
            breach_id=old.breach_id, slc_reference=old.slc_reference,
            description=old.description, detected_date=old.detected_date,
            severity=old.severity, status=new_status,
            source=old.source, accounts_affected=old.accounts_affected,
            estimated_penalty_gbp=old.estimated_penalty_gbp,
            remediation_date=old.remediation_date,
        )
        self._records = [updated if r.breach_id == breach_id else r for r in self._records]
        return updated

    @property
    def open_breaches(self) -> list[RegulatoryBreachRecord]:
        return [r for r in self._records if r.is_open]

    @property
    def critical_breaches(self) -> list[RegulatoryBreachRecord]:
        return [r for r in self._records if r.severity == BreachSeverity.CRITICAL]

    @property
    def reportable_breaches(self) -> list[RegulatoryBreachRecord]:
        return [r for r in self._records if r.is_reportable and r.is_open]

    @property
    def total_estimated_penalty_gbp(self) -> float:
        return sum(r.estimated_penalty_gbp for r in self.open_breaches)

    def by_slc(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for r in self._records:
            result[r.slc_reference] = result.get(r.slc_reference, 0) + 1
        return result

    def breach_summary(self) -> str:
        n_total = len(self._records)
        n_open = len(self.open_breaches)
        n_reportable = len(self.reportable_breaches)
        return (
            "Regulatory Breach Log (Ofgem SLC)\n"
            "Total: {:d} | Open: {:d} | Reportable (H/C): {:d}\n"
            "Total estimated penalty: £{:,.0f}".format(n_total, n_open, n_reportable, self.total_estimated_penalty_gbp)
        )
