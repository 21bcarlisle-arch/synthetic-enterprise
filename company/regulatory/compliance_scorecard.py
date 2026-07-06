"""Ofgem Market Compliance Scorecard.

A compliance function tracks all Standard Licence Condition (SLC) obligations
simultaneously, producing a consolidated RAG (Red/Amber/Green) status for each
area. This is what a Head of Compliance presents at the monthly Risk Committee
and what feeds into Ofgem's annual Compliance Reporting Return.

The 10 compliance domains correspond to the main SLC obligation clusters:
1. SLC 0-9: Licence conditions and governance
2. SLC 10-14: Customer relationship (billing, metering, switching)
3. SLC 15-19: Payment/debt management and PPM
4. SLC 20-24: Information and transparency
5. SLC 25-29: Complaints and dispute resolution
6. SLC 30-35: Vulnerable customers and Priority Services Register
7. SLC 36-40: Tariff design and price cap compliance
8. SLC 41-50: Renewables/environmental obligations (RO, CfD, EE)
9. SLC 51-60: Network connection and balancing
10. SFR / Financial resilience (post-2023 requirement)

RAG logic: any BREACH sets the domain RED; borderline metrics set AMBER.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class RAGStatus(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


class ComplianceDomain(str, Enum):
    GOVERNANCE = "governance"
    BILLING_METERING = "billing_metering"
    PAYMENT_DEBT = "payment_debt"
    INFORMATION_TRANSPARENCY = "information_transparency"
    COMPLAINTS = "complaints"
    VULNERABLE_CUSTOMERS = "vulnerable_customers"
    TARIFF_PRICE_CAP = "tariff_price_cap"
    ENVIRONMENTAL = "environmental"
    NETWORK_BALANCING = "network_balancing"
    FINANCIAL_RESILIENCE = "financial_resilience"


_DOMAIN_SLC_REF: dict[str, str] = {
    "governance": "SLC 0-9",
    "billing_metering": "SLC 10-14",
    "payment_debt": "SLC 15-19",
    "information_transparency": "SLC 20-24",
    "complaints": "SLC 25-29 / Ofgem Time to Fix rules",
    "vulnerable_customers": "SLC 30-35 / PSR",
    "tariff_price_cap": "SLC 36-40 / Default Tariff Cap",
    "environmental": "SLC 41-50 / RO, CfD, EE obligation",
    "network_balancing": "SLC 51-60 / BSC obligations",
    "financial_resilience": "SLC 4C / SFR Decision 2023",
}


@dataclass(frozen=True)
class ComplianceCheck:
    domain: ComplianceDomain
    check_date: dt.date
    status: RAGStatus
    metric_value: Optional[float] = None  # the KPI being assessed
    threshold: Optional[float] = None    # the regulatory threshold
    notes: str = ""

    @property
    def slc_reference(self) -> str:
        return _DOMAIN_SLC_REF.get(self.domain.value, "")

    @property
    def is_breach(self) -> bool:
        return self.status == RAGStatus.RED


@dataclass
class ComplianceScorecard:
    """Monthly consolidated compliance scorecard."""

    _checks: List[ComplianceCheck] = field(default_factory=list)

    def record_check(
        self,
        domain: ComplianceDomain,
        check_date: dt.date,
        status: RAGStatus,
        metric_value: Optional[float] = None,
        threshold: Optional[float] = None,
        notes: str = "",
    ) -> ComplianceCheck:
        check = ComplianceCheck(
            domain=domain, check_date=check_date, status=status,
            metric_value=metric_value, threshold=threshold, notes=notes,
        )
        self._checks.append(check)
        return check

    def latest_check(self, domain: ComplianceDomain) -> Optional[ComplianceCheck]:
        domain_checks = [c for c in self._checks if c.domain == domain]
        if not domain_checks:
            return None
        return sorted(domain_checks, key=lambda c: c.check_date)[-1]

    def latest_status(self, domain: ComplianceDomain) -> Optional[RAGStatus]:
        check = self.latest_check(domain)
        return check.status if check else None

    def overall_rag(self, as_of_date: dt.date) -> RAGStatus:
        """Worst RAG status across all domains as of date."""
        seen: dict[ComplianceDomain, ComplianceCheck] = {}
        for c in self._checks:
            if c.check_date <= as_of_date:
                if c.domain not in seen or c.check_date > seen[c.domain].check_date:
                    seen[c.domain] = c
        statuses = [c.status for c in seen.values()]
        if RAGStatus.RED in statuses:
            return RAGStatus.RED
        if RAGStatus.AMBER in statuses:
            return RAGStatus.AMBER
        return RAGStatus.GREEN

    def breaches(self, as_of_date: dt.date) -> List[ComplianceCheck]:
        """All RED domains as of date (latest check per domain)."""
        seen: dict[ComplianceDomain, ComplianceCheck] = {}
        for c in self._checks:
            if c.check_date <= as_of_date:
                if c.domain not in seen or c.check_date > seen[c.domain].check_date:
                    seen[c.domain] = c
        return [c for c in seen.values() if c.is_breach]

    def scorecard_summary(self, as_of_date: dt.date) -> dict:
        seen: dict[ComplianceDomain, ComplianceCheck] = {}
        for c in self._checks:
            if c.check_date <= as_of_date:
                if c.domain not in seen or c.check_date > seen[c.domain].check_date:
                    seen[c.domain] = c
        rag_counts = {s.value: 0 for s in RAGStatus}
        for c in seen.values():
            rag_counts[c.status.value] += 1
        return {
            "as_of_date": str(as_of_date),
            "overall_rag": self.overall_rag(as_of_date).value,
            "domains_checked": len(seen),
            "rag_counts": rag_counts,
            "breach_domains": [c.domain.value for c in self.breaches(as_of_date)],
        }
