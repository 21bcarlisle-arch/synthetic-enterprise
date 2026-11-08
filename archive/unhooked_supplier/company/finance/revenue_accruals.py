"""Revenue accruals ledger: billed vs unbilled accrual for month-end close."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class RevenueType(str, Enum):
    COMMODITY = 'commodity'
    STANDING_CHARGE = 'standing_charge'
    EXIT_FEE = 'exit_fee'
    LATE_PAYMENT_FEE = 'late_payment_fee'
    RECONNECTION_FEE = 'reconnection_fee'


class RecognitionBasis(str, Enum):
    BILLED = 'billed'
    ACCRUED = 'accrued'


@dataclass(frozen=True)
class RevenueEntry:
    customer_id: str
    period_start: dt.date
    period_end: dt.date
    revenue_type: RevenueType
    basis: RecognitionBasis
    amount_gbp: float
    commodity: str

    @property
    def period_days(self) -> int:
        return max(1, (self.period_end - self.period_start).days + 1)

    @property
    def daily_revenue_gbp(self) -> float:
        return round(self.amount_gbp / self.period_days, 4)


class RevenueAccrualsLedger:
    def __init__(self) -> None:
        self._entries: List[RevenueEntry] = []

    def post(self, customer_id: str, period_start: dt.date, period_end: dt.date,
             revenue_type: RevenueType, basis: RecognitionBasis,
             amount_gbp: float, commodity: str = 'electricity') -> RevenueEntry:
        entry = RevenueEntry(
            customer_id=customer_id, period_start=period_start, period_end=period_end,
            revenue_type=revenue_type, basis=basis, amount_gbp=amount_gbp,
            commodity=commodity,
        )
        self._entries.append(entry)
        return entry

    def entries_in_period(self, period_start: dt.date, period_end: dt.date
                          ) -> List[RevenueEntry]:
        return [e for e in self._entries
                if e.period_start <= period_end and e.period_end >= period_start]

    def billed_revenue_gbp(self, period_start: dt.date, period_end: dt.date) -> float:
        return round(sum(e.amount_gbp for e in self.entries_in_period(period_start, period_end)
                         if e.basis == RecognitionBasis.BILLED), 2)

    def accrued_revenue_gbp(self, period_start: dt.date, period_end: dt.date) -> float:
        return round(sum(e.amount_gbp for e in self.entries_in_period(period_start, period_end)
                         if e.basis == RecognitionBasis.ACCRUED), 2)

    def total_revenue_gbp(self, period_start: dt.date, period_end: dt.date) -> float:
        return round(self.billed_revenue_gbp(period_start, period_end) +
                     self.accrued_revenue_gbp(period_start, period_end), 2)

    def by_type(self, period_start: dt.date, period_end: dt.date) -> dict:
        result: Dict[str, float] = {}
        for e in self.entries_in_period(period_start, period_end):
            k = e.revenue_type.value
            result[k] = round(result.get(k, 0.0) + e.amount_gbp, 2)
        return result

    def accrual_ratio(self, period_start: dt.date, period_end: dt.date) -> Optional[float]:
        total = self.total_revenue_gbp(period_start, period_end)
        if total == 0:
            return None
        return round(self.accrued_revenue_gbp(period_start, period_end) / total * 100, 1)

    def monthly_summary(self, year: int, month: int) -> dict:
        start = dt.date(year, month, 1)
        if month == 12:
            end = dt.date(year + 1, 1, 1) - dt.timedelta(days=1)
        else:
            end = dt.date(year, month + 1, 1) - dt.timedelta(days=1)
        return {
            'year': year, 'month': month,
            'billed_gbp': self.billed_revenue_gbp(start, end),
            'accrued_gbp': self.accrued_revenue_gbp(start, end),
            'total_gbp': self.total_revenue_gbp(start, end),
            'accrual_ratio_pct': self.accrual_ratio(start, end),
            'by_type': self.by_type(start, end),
        }
