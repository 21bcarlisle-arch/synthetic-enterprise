"""Standard Licence Condition (SLC) compliance tracker.

Ofgem's Standard Licence Conditions define the obligations all licensed
energy suppliers must meet. This tracker aggregates compliance signals
from multiple company modules into a single compliance dashboard.

SLCs tracked:
- SLC 6: Bills must be issued on time and accurately
- SLC 14: Credit refunds within 10 working days
- SLC 21B: Account closure final bill within 42 days
- SLC 22: Renewal notice 42 days before expiry
- SLC 27: Debt management — 4-step process, no disconnection without process
- SLC 27A: Ability to pay assessment for vulnerable customers
- SLC 31A: Back-billing cap (12 months domestic)
- SLC 45: Smart meter rollout obligation

Company Duty: Ofgem Consumer Duty (2023) requires good customer outcomes
across all four pillars: Products, Price, Service, and Consumer Support.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SLCStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    BREACH_RISK = "BREACH_RISK"
    BREACHED = "BREACHED"
    NOT_APPLICABLE = "N/A"
    UNKNOWN = "UNKNOWN"


class SLCCategory(str, Enum):
    BILLING = "Billing"
    CREDIT = "Credit & Refunds"
    DEBT = "Debt Management"
    METERING = "Metering"
    RENEWAL = "Renewal"
    VULNERABILITY = "Vulnerability"
    SMART = "Smart Metering"


@dataclass(frozen=True)
class SLCObservation:
    slc_ref: str
    category: SLCCategory
    description: str
    status: SLCStatus
    breach_count: int = 0
    at_risk_count: int = 0
    notes: str = ""

    @property
    def is_compliant(self) -> bool:
        return self.status == SLCStatus.COMPLIANT

    @property
    def is_breached(self) -> bool:
        return self.status == SLCStatus.BREACHED

    @property
    def severity_score(self) -> int:
        """0=OK, 1=risk, 2=breached."""
        if self.status == SLCStatus.BREACHED:
            return 2
        if self.status == SLCStatus.BREACH_RISK:
            return 1
        return 0


class SLCComplianceTracker:
    """Consolidates SLC compliance observations into a portfolio-level dashboard."""

    def __init__(self) -> None:
        self._observations: dict[str, SLCObservation] = {}

    def record(
        self,
        slc_ref: str,
        category: SLCCategory,
        description: str,
        status: SLCStatus,
        breach_count: int = 0,
        at_risk_count: int = 0,
        notes: str = "",
    ) -> SLCObservation:
        obs = SLCObservation(
            slc_ref=slc_ref,
            category=category,
            description=description,
            status=status,
            breach_count=breach_count,
            at_risk_count=at_risk_count,
            notes=notes,
        )
        self._observations[slc_ref] = obs
        return obs

    def get(self, slc_ref: str) -> Optional[SLCObservation]:
        return self._observations.get(slc_ref)

    @property
    def all_observations(self) -> list[SLCObservation]:
        return sorted(self._observations.values(), key=lambda o: o.slc_ref)

    @property
    def breached(self) -> list[SLCObservation]:
        return [o for o in self._observations.values() if o.is_breached]

    @property
    def at_risk(self) -> list[SLCObservation]:
        return [o for o in self._observations.values() if o.status == SLCStatus.BREACH_RISK]

    @property
    def compliant(self) -> list[SLCObservation]:
        return [o for o in self._observations.values() if o.is_compliant]

    @property
    def total_breach_count(self) -> int:
        return sum(o.breach_count for o in self._observations.values())

    @property
    def total_at_risk_count(self) -> int:
        return sum(o.at_risk_count for o in self._observations.values())

    @property
    def overall_rag(self) -> str:
        if self.breached:
            return "RED"
        if self.at_risk:
            return "AMBER"
        return "GREEN"

    def by_category(self, category: SLCCategory) -> list[SLCObservation]:
        return [o for o in self._observations.values() if o.category == category]

    def highest_severity_slcs(self, n: int = 3) -> list[SLCObservation]:
        return sorted(
            self._observations.values(),
            key=lambda o: (o.severity_score, o.breach_count),
            reverse=True,
        )[:n]

    def compliance_summary(self) -> str:
        n_total = len(self._observations)
        n_compliant = len(self.compliant)
        n_risk = len(self.at_risk)
        n_breached = len(self.breached)
        lines = [
            "SLC Compliance Dashboard",
            "Overall RAG: {}".format(self.overall_rag),
            "Compliant: {}/{} | At Risk: {} | Breached: {}".format(
                n_compliant, n_total, n_risk, n_breached
            ),
            "Total breaches recorded: {}".format(self.total_breach_count),
        ]
        if self.breached:
            lines.append("BREACHED:")
            for o in self.breached:
                lines.append("  {} ({}): {} breach(es)".format(o.slc_ref, o.category.value, o.breach_count))
        if self.at_risk:
            lines.append("AT RISK:")
            for o in self.at_risk:
                lines.append("  {} ({}): {} at risk".format(o.slc_ref, o.category.value, o.at_risk_count))
        return chr(10).join(lines)
