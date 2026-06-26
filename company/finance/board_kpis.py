from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class KPIStatus(str, Enum):
    GREEN = 'green'
    AMBER = 'amber'
    RED = 'red'


@dataclass(frozen=True)
class KPIValue:
    name: str
    value: float
    unit: str
    target: float
    lower_is_better: bool = False

    @property
    def vs_target_pct(self) -> float:
        if self.target == 0:
            return 0.0
        return round((self.value - self.target) / abs(self.target) * 100, 1)

    @property
    def status(self) -> KPIStatus:
        diff = self.vs_target_pct
        if self.lower_is_better:
            diff = -diff
        if diff >= -5:
            return KPIStatus.GREEN
        if diff >= -20:
            return KPIStatus.AMBER
        return KPIStatus.RED


@dataclass(frozen=True)
class BoardKPIDashboard:
    year: int
    quarter: int
    kpis: tuple

    @property
    def green_count(self) -> int:
        return sum(1 for k in self.kpis if k.status == KPIStatus.GREEN)

    @property
    def amber_count(self) -> int:
        return sum(1 for k in self.kpis if k.status == KPIStatus.AMBER)

    @property
    def red_count(self) -> int:
        return sum(1 for k in self.kpis if k.status == KPIStatus.RED)

    @property
    def overall_status(self) -> KPIStatus:
        if self.red_count > 0:
            return KPIStatus.RED
        if self.amber_count > 0:
            return KPIStatus.AMBER
        return KPIStatus.GREEN

    def get_kpi(self, name: str) -> Optional[KPIValue]:
        return next((k for k in self.kpis if k.name == name), None)

    def summary(self) -> dict:
        return {
            'year': self.year,
            'quarter': self.quarter,
            'total_kpis': len(self.kpis),
            'green': self.green_count,
            'amber': self.amber_count,
            'red': self.red_count,
            'overall_status': self.overall_status.value,
            'kpis': [
                {
                    'name': k.name,
                    'value': k.value,
                    'unit': k.unit,
                    'target': k.target,
                    'status': k.status.value,
                }
                for k in self.kpis
            ],
        }


def build_board_dashboard(
    year: int,
    quarter: int,
    customer_count: int, customer_target: int,
    gross_margin_pct: float, gm_target_pct: float,
    ebitda_margin_pct: float, ebitda_target_pct: float,
    bad_debt_pct: float, bad_debt_target_pct: float,
    complaint_resolution_days: float, crt_target_days: float,
    csat_score: float, csat_target: float,
    gsop_compliance_pct: float, gsop_target_pct: float,
) -> BoardKPIDashboard:
    kpis = [
        KPIValue('Customer count', customer_count, 'accounts', customer_target),
        KPIValue('Gross margin', gross_margin_pct, '%', gm_target_pct),
        KPIValue('EBITDA margin', ebitda_margin_pct, '%', ebitda_target_pct),
        KPIValue('Bad debt rate', bad_debt_pct, '%', bad_debt_target_pct, lower_is_better=True),
        KPIValue('Complaint resolution days', complaint_resolution_days, 'days', crt_target_days, lower_is_better=True),
        KPIValue('CSAT score', csat_score, '/5', csat_target),
        KPIValue('GSOP compliance', gsop_compliance_pct, '%', gsop_target_pct),
    ]
    return BoardKPIDashboard(year=year, quarter=quarter, kpis=tuple(kpis))
