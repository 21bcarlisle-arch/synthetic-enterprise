"""Debt Age Analysis Register (Phase FO).

Accounts receivable aged analysis: classifies outstanding debts by how
long they've been overdue. Used for:
1. Bad debt provisioning (IFRS 9 Expected Credit Loss model)
2. Prioritizing collection actions
3. Regulatory reporting to Ofgem (debt levels)

Standard aging buckets (UK energy supplier practice):
- CURRENT: 0-30 days (just billed; not yet overdue)
- DAYS_31_60: 31-60 days overdue
- DAYS_61_90: 61-90 days overdue  
- DAYS_91_180: 91-180 days overdue
- OVER_180: >180 days overdue (high write-off risk)

ECL provision rates (based on UK energy debt recovery experience):
- CURRENT: 2% (some customers always slow)
- 31-60d: 5%
- 61-90d: 15%
- 91-180d: 40%
- >180d: 80%

SLC 27A requires suppliers to identify and offer payment plans to indebted
domestic customers before escalating to debt agencies.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List


class DebtAgeBucket(str, Enum):
    CURRENT = "current"         # 0-30 days
    DAYS_31_60 = "31_60"
    DAYS_61_90 = "61_90"
    DAYS_91_180 = "91_180"
    OVER_180 = "over_180"


_PROVISION_RATE: dict = {
    DebtAgeBucket.CURRENT: 0.02,
    DebtAgeBucket.DAYS_31_60: 0.05,
    DebtAgeBucket.DAYS_61_90: 0.15,
    DebtAgeBucket.DAYS_91_180: 0.40,
    DebtAgeBucket.OVER_180: 0.80,
}


def _age_bucket(days_overdue: int) -> DebtAgeBucket:
    if days_overdue <= 30:
        return DebtAgeBucket.CURRENT
    if days_overdue <= 60:
        return DebtAgeBucket.DAYS_31_60
    if days_overdue <= 90:
        return DebtAgeBucket.DAYS_61_90
    if days_overdue <= 180:
        return DebtAgeBucket.DAYS_91_180
    return DebtAgeBucket.OVER_180


@dataclass(frozen=True)
class AgedDebt:
    account_id: str
    invoice_date: dt.date
    outstanding_gbp: float
    is_domestic: bool = True

    def age_bucket(self, as_of: dt.date) -> DebtAgeBucket:
        days = (as_of - self.invoice_date).days
        return _age_bucket(days)

    def days_overdue(self, as_of: dt.date) -> int:
        return max(0, (as_of - self.invoice_date).days)

    def ecl_provision_gbp(self, as_of: dt.date) -> float:
        rate = _PROVISION_RATE[self.age_bucket(as_of)]
        return self.outstanding_gbp * rate

    def debt_summary(self, as_of: dt.date) -> str:
        return (
            "AgedDebt " + self.account_id + ": "
            "GBP" + str(round(self.outstanding_gbp, 2)) + " "
            "[" + self.age_bucket(as_of).value + " bucket] "
            "ECL=GBP" + str(round(self.ecl_provision_gbp(as_of), 2))
        )


class DebtAgeAnalysisRegister:

    def __init__(self) -> None:
        self._debts: List[AgedDebt] = []

    def record(self, debt: AgedDebt) -> AgedDebt:
        self._debts.append(debt)
        return debt

    def debts_in_bucket(self, bucket: DebtAgeBucket, as_of: dt.date) -> List[AgedDebt]:
        return [d for d in self._debts if d.age_bucket(as_of) == bucket]

    def total_in_bucket_gbp(self, bucket: DebtAgeBucket, as_of: dt.date) -> float:
        return sum(d.outstanding_gbp for d in self.debts_in_bucket(bucket, as_of))

    def total_ecl_provision_gbp(self, as_of: dt.date) -> float:
        return sum(d.ecl_provision_gbp(as_of) for d in self._debts)

    def total_outstanding_gbp(self) -> float:
        return sum(d.outstanding_gbp for d in self._debts)

    def high_risk_debts(self, as_of: dt.date) -> List[AgedDebt]:
        high_risk = {DebtAgeBucket.DAYS_91_180, DebtAgeBucket.OVER_180}
        return [d for d in self._debts if d.age_bucket(as_of) in high_risk]

    def debt_age_summary(self, as_of: dt.date) -> str:
        n = len(self._debts)
        total = self.total_outstanding_gbp()
        ecl = self.total_ecl_provision_gbp(as_of)
        pct_provisioned = 100.0 * ecl / total if total else 0.0
        return (
            "Debt Age Analysis (" + str(as_of) + "): "
            + str(n) + " debts. "
            "Total: GBP" + str(round(total, 0)) + ". "
            "ECL provision: GBP" + str(round(ecl, 0)) + " "
            "(" + str(round(pct_provisioned, 1)) + "%)."
        )
