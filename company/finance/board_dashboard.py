"""Integrated board KPI dashboard: the monthly view an energy supplier board reviews."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class KPIStatus(str, Enum):
    GREEN = 'green'
    AMBER = 'amber'
    RED = 'red'
    NOT_SET = 'not_set'


@dataclass(frozen=True)
class KPIMetric:
    name: str
    value: float
    target: float
    unit: str
    lower_is_better: bool = False

    @property
    def vs_target_pct(self) -> float:
        if self.target == 0:
            return 0.0
        return round((self.value - self.target) / abs(self.target) * 100, 1)

    @property
    def status(self) -> KPIStatus:
        pct = self.vs_target_pct
        if self.lower_is_better:
            if pct <= 0:
                return KPIStatus.GREEN
            elif pct <= 10:
                return KPIStatus.AMBER
            return KPIStatus.RED
        else:
            if pct >= 0:
                return KPIStatus.GREEN
            elif pct >= -10:
                return KPIStatus.AMBER
            return KPIStatus.RED

    @property
    def is_on_target(self) -> bool:
        return self.status == KPIStatus.GREEN


@dataclass
class BoardDashboard:
    period: dt.date
    customer_count: int
    net_margin_gbp: float
    gross_margin_gbp: float
    treasury_gbp: float
    enterprise_value_gbp: float
    churn_rate_pct: float
    complaints_per_100: float
    bad_debt_ratio_pct: float
    cash_runway_weeks: float
    hedge_ratio_pct: float
    tests_passing: int = 0

    def kpis(self, targets: dict) -> List[KPIMetric]:
        return [
            KPIMetric('Customer Count', self.customer_count,
                       targets.get('customer_count', self.customer_count), 'customers'),
            KPIMetric('Net Margin', self.net_margin_gbp,
                       targets.get('net_margin_gbp', 0), '£'),
            KPIMetric('Gross Margin', self.gross_margin_gbp,
                       targets.get('gross_margin_gbp', 0), '£'),
            KPIMetric('Treasury', self.treasury_gbp,
                       targets.get('treasury_gbp', 100_000), '£'),
            KPIMetric('Enterprise Value', self.enterprise_value_gbp,
                       targets.get('enterprise_value_gbp', 0), '£'),
            KPIMetric('Churn Rate', self.churn_rate_pct,
                       targets.get('churn_rate_pct', 3.0), '%', lower_is_better=True),
            KPIMetric('Complaints/100', self.complaints_per_100,
                       targets.get('complaints_per_100', 2.0), '/100', lower_is_better=True),
            KPIMetric('Bad Debt Ratio', self.bad_debt_ratio_pct,
                       targets.get('bad_debt_ratio_pct', 2.0), '%', lower_is_better=True),
            KPIMetric('Cash Runway', self.cash_runway_weeks,
                       targets.get('cash_runway_weeks', 8.0), 'weeks'),
            KPIMetric('Hedge Ratio', self.hedge_ratio_pct,
                       targets.get('hedge_ratio_pct', 70.0), '%'),
        ]

    def rag_summary(self, targets: dict) -> dict:
        kpis = self.kpis(targets)
        return {
            'period': self.period.isoformat(),
            'green': len([k for k in kpis if k.status == KPIStatus.GREEN]),
            'amber': len([k for k in kpis if k.status == KPIStatus.AMBER]),
            'red': len([k for k in kpis if k.status == KPIStatus.RED]),
            'overall': ('GREEN' if all(k.status != KPIStatus.RED for k in kpis) else 'RED'),
            'at_risk_metrics': [k.name for k in kpis if k.status != KPIStatus.GREEN],
        }
