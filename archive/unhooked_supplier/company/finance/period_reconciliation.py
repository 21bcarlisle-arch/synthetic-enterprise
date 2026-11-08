"""Period-end financial reconciliation: revenue-cost matching, settlement variances."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ReconciliationStatus(str, Enum):
    OPEN = 'open'
    RECONCILED = 'reconciled'
    DISPUTED = 'disputed'
    WRITTEN_OFF = 'written_off'


class VarianceType(str, Enum):
    REVENUE_SHORTFALL = 'revenue_shortfall'
    COST_OVERRUN = 'cost_overrun'
    SETTLEMENT_DIFFERENCE = 'settlement_difference'
    ACCRUAL_REVERSAL = 'accrual_reversal'
    METER_READ_ERROR = 'meter_read_error'


@dataclass(frozen=True)
class ReconciliationVariance:
    variance_id: str
    period: dt.date
    variance_type: VarianceType
    amount_gbp: float
    description: str

    @property
    def is_adverse(self) -> bool:
        return self.amount_gbp < 0

    @property
    def abs_amount_gbp(self) -> float:
        return abs(self.amount_gbp)


@dataclass
class PeriodReconciliation:
    period_id: str
    period_start: dt.date
    period_end: dt.date
    billed_revenue_gbp: float
    accrued_revenue_gbp: float
    wholesale_cost_gbp: float
    network_cost_gbp: float
    policy_cost_gbp: float
    operating_cost_gbp: float
    status: ReconciliationStatus = ReconciliationStatus.OPEN
    variances: List[ReconciliationVariance] = None

    def __post_init__(self):
        if self.variances is None:
            self.variances = []

    @property
    def total_revenue_gbp(self) -> float:
        return round(self.billed_revenue_gbp + self.accrued_revenue_gbp, 2)

    @property
    def total_cost_gbp(self) -> float:
        return round(
            self.wholesale_cost_gbp + self.network_cost_gbp
            + self.policy_cost_gbp + self.operating_cost_gbp, 2
        )

    @property
    def gross_margin_gbp(self) -> float:
        return round(self.total_revenue_gbp - self.total_cost_gbp, 2)

    @property
    def total_variance_gbp(self) -> float:
        return round(sum(v.amount_gbp for v in self.variances), 2)

    @property
    def adjusted_margin_gbp(self) -> float:
        return round(self.gross_margin_gbp + self.total_variance_gbp, 2)

    def add_variance(self, variance_id: str, variance_type: VarianceType,
                       amount_gbp: float, description: str) -> ReconciliationVariance:
        v = ReconciliationVariance(
            variance_id=variance_id, period=self.period_start,
            variance_type=variance_type, amount_gbp=amount_gbp,
            description=description,
        )
        self.variances.append(v)
        return v

    def close(self) -> None:
        self.status = ReconciliationStatus.RECONCILED


class ReconciliationLedger:
    def __init__(self) -> None:
        self._periods: List[PeriodReconciliation] = []

    def open_period(self, period_id: str, period_start: dt.date, period_end: dt.date,
                      billed_revenue_gbp: float, accrued_revenue_gbp: float,
                      wholesale_cost_gbp: float, network_cost_gbp: float,
                      policy_cost_gbp: float, operating_cost_gbp: float
                      ) -> PeriodReconciliation:
        p = PeriodReconciliation(
            period_id=period_id, period_start=period_start, period_end=period_end,
            billed_revenue_gbp=billed_revenue_gbp,
            accrued_revenue_gbp=accrued_revenue_gbp,
            wholesale_cost_gbp=wholesale_cost_gbp,
            network_cost_gbp=network_cost_gbp,
            policy_cost_gbp=policy_cost_gbp,
            operating_cost_gbp=operating_cost_gbp,
        )
        self._periods.append(p)
        return p

    def get(self, period_id: str) -> Optional[PeriodReconciliation]:
        return next((p for p in self._periods if p.period_id == period_id), None)

    def open_periods(self) -> List[PeriodReconciliation]:
        return [p for p in self._periods if p.status == ReconciliationStatus.OPEN]

    def annual_gross_margin_gbp(self, year: int) -> float:
        return round(sum(
            p.adjusted_margin_gbp for p in self._periods
            if p.period_start.year == year
        ), 2)

    def variances_by_type(self, year: int) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for p in self._periods:
            if p.period_start.year != year:
                continue
            for v in p.variances:
                k = v.variance_type.value
                result[k] = round(result.get(k, 0.0) + v.amount_gbp, 2)
        return result

    def reconciliation_summary(self, year: int) -> dict:
        yr = [p for p in self._periods if p.period_start.year == year]
        return {
            'year': year,
            'periods': len(yr),
            'open': len([p for p in yr if p.status == ReconciliationStatus.OPEN]),
            'annual_gross_margin_gbp': self.annual_gross_margin_gbp(year),
            'total_variances_gbp': round(sum(p.total_variance_gbp for p in yr), 2),
            'variances_by_type': self.variances_by_type(year),
        }
