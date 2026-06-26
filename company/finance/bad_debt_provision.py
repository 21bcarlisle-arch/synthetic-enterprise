"""Bad debt provisioning: forward-looking provision based on arrears aging."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class AgingBucket(str, Enum):
    CURRENT = 'current'
    DAYS_30 = '31_60_days'
    DAYS_60 = '61_90_days'
    DAYS_90 = '91_180_days'
    DAYS_180_PLUS = '180_plus_days'


_PROVISION_RATES = {
    AgingBucket.CURRENT: 0.005,
    AgingBucket.DAYS_30: 0.05,
    AgingBucket.DAYS_60: 0.20,
    AgingBucket.DAYS_90: 0.50,
    AgingBucket.DAYS_180_PLUS: 0.90,
}


def classify_age(days_outstanding: int) -> AgingBucket:
    if days_outstanding <= 30:
        return AgingBucket.CURRENT
    if days_outstanding <= 60:
        return AgingBucket.DAYS_30
    if days_outstanding <= 90:
        return AgingBucket.DAYS_60
    if days_outstanding <= 180:
        return AgingBucket.DAYS_90
    return AgingBucket.DAYS_180_PLUS


@dataclass(frozen=True)
class ArrearsLedgerItem:
    customer_id: str
    outstanding_gbp: float
    days_outstanding: int
    is_vulnerable: bool = False

    @property
    def aging_bucket(self) -> AgingBucket:
        return classify_age(self.days_outstanding)

    @property
    def provision_rate(self) -> float:
        return _PROVISION_RATES[self.aging_bucket]

    @property
    def provision_gbp(self) -> float:
        return round(self.outstanding_gbp * self.provision_rate, 2)


@dataclass(frozen=True)
class BadDebtProvision:
    as_of: dt.date
    items: tuple

    @property
    def total_arrears_gbp(self) -> float:
        return round(sum(i.outstanding_gbp for i in self.items), 2)

    @property
    def total_provision_gbp(self) -> float:
        return round(sum(i.provision_gbp for i in self.items), 2)

    @property
    def provision_coverage_pct(self) -> float:
        if self.total_arrears_gbp == 0:
            return 0.0
        return round(self.total_provision_gbp / self.total_arrears_gbp * 100, 1)

    def by_bucket(self) -> dict:
        buckets: dict = {}
        for i in self.items:
            b = i.aging_bucket.value
            if b not in buckets:
                buckets[b] = {'count': 0, 'arrears_gbp': 0.0, 'provision_gbp': 0.0}
            buckets[b]['count'] += 1
            buckets[b]['arrears_gbp'] = round(buckets[b]['arrears_gbp'] + i.outstanding_gbp, 2)
            buckets[b]['provision_gbp'] = round(buckets[b]['provision_gbp'] + i.provision_gbp, 2)
        return buckets

    def vulnerable_provision_gbp(self) -> float:
        return round(sum(i.provision_gbp for i in self.items if i.is_vulnerable), 2)

    def summary(self) -> dict:
        return {
            'as_of': self.as_of.isoformat(),
            'total_customers': len(self.items),
            'total_arrears_gbp': self.total_arrears_gbp,
            'total_provision_gbp': self.total_provision_gbp,
            'provision_coverage_pct': self.provision_coverage_pct,
            'vulnerable_provision_gbp': self.vulnerable_provision_gbp(),
            'by_bucket': self.by_bucket(),
        }


def build_provision(as_of: dt.date, items: List[ArrearsLedgerItem]) -> BadDebtProvision:
    return BadDebtProvision(as_of=as_of, items=tuple(items))
