"""Vulnerable Customer Register (Phase FA).

Ofgem Consumer Duty (2023) requires suppliers to identify vulnerable customers
and ensure they receive fair outcomes. This module models the vulnerability
assessment and tracking regime.

Vulnerability dimensions (Ofgem 2022 Vulnerability Guidance):
1. Financial vulnerability: debt, fuel poverty, income shock
2. Health vulnerability: medical equipment, cognitive impairment
3. Life events: bereavement, domestic abuse, job loss (temporary)
4. Age-related: under 5 children, over 70 adults
5. Communication needs: language barriers, disability

Key obligations:
- SLC 26B: Priority Services Register (medical/elderly) - already Phase CR
- Consumer Duty: ALL vulnerable customers must receive fair outcomes
- Smart meter priority (BEIS): vulnerable customers should be offered smart
  meters first (they benefit most from avoiding estimated bills)
- Prepayment meter ban (2023): vulnerable customers cannot be force-fitted

This register covers the broader vulnerability population beyond PSR.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class VulnerabilityType(str, Enum):
    FINANCIAL = "financial"
    HEALTH_MEDICAL = "health_medical"
    LIFE_EVENT = "life_event"
    AGE_RELATED = "age_related"
    COMMUNICATION = "communication"
    MENTAL_HEALTH = "mental_health"


class VulnerabilityRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"      # immediate risk of harm if service interrupted


_PPM_VULNERABLE_BAN = True    # Cannot force-fit PPM for vulnerable customers (2023)


@dataclass(frozen=True)
class VulnerabilityRecord:
    account_id: str
    vulnerability_types: tuple      # of VulnerabilityType
    risk_level: VulnerabilityRisk
    identified_at: dt.date
    review_due_date: dt.date
    notes: str = ""
    is_active: bool = True

    @property
    def is_ppm_restricted(self) -> bool:
        return _PPM_VULNERABLE_BAN and self.is_active

    @property
    def has_multiple_vulnerabilities(self) -> bool:
        return len(self.vulnerability_types) > 1

    def is_review_overdue(self, as_of: dt.date) -> bool:
        if not self.is_active:
            return False
        return as_of > self.review_due_date

    def vulnerability_summary(self) -> str:
        types_str = ",".join(v.value for v in self.vulnerability_types)
        return (
            "VCR " + self.account_id + " [" + self.risk_level.value + "]: "
            + types_str
        )


class VulnerableCustomerRegister:

    def __init__(self) -> None:
        self._records: List[VulnerabilityRecord] = []

    def register(self, record: VulnerabilityRecord) -> VulnerabilityRecord:
        self._records.append(record)
        return record

    def active_records(self) -> List[VulnerabilityRecord]:
        return [r for r in self._records if r.is_active]

    def by_risk_level(self, risk: VulnerabilityRisk) -> List[VulnerabilityRecord]:
        return [r for r in self.active_records() if r.risk_level == risk]

    def critical_accounts(self) -> List[VulnerabilityRecord]:
        return self.by_risk_level(VulnerabilityRisk.CRITICAL)

    def ppm_restricted_accounts(self) -> List[VulnerabilityRecord]:
        return [r for r in self.active_records() if r.is_ppm_restricted]

    def overdue_reviews(self, as_of: dt.date) -> List[VulnerabilityRecord]:
        return [r for r in self.active_records() if r.is_review_overdue(as_of)]

    def multi_vulnerability_accounts(self) -> List[VulnerabilityRecord]:
        return [r for r in self.active_records() if r.has_multiple_vulnerabilities]

    def vulnerability_rate_pct(self, total_customers: int) -> float:
        if total_customers == 0:
            return 0.0
        return 100.0 * len(self.active_records()) / total_customers

    def vcr_summary(self, as_of: dt.date, total_customers: int = 0) -> str:
        n = len(self.active_records())
        n_critical = len(self.critical_accounts())
        n_overdue = len(self.overdue_reviews(as_of))
        rate = self.vulnerability_rate_pct(total_customers)
        portfolio_str = "(" + str(round(rate, 1)) + "% of portfolio). " if total_customers else ". "
        return (
            "VCR (" + str(as_of) + "): "
            + str(n) + " vulnerable customers "
            + portfolio_str
            + "Critical: " + str(n_critical) + ". "
            + "Overdue reviews: " + str(n_overdue) + "."
        )
