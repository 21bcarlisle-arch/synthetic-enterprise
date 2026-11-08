"""Settlement imbalance analytics: cash-out cost tracking, systematic bias detection."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ImbalanceDirection(str, Enum):
    LONG = 'long'   # More generation/purchased than consumed
    SHORT = 'short'  # Less generation/purchased than consumed
    FLAT = 'flat'


@dataclass(frozen=True)
class ImbalanceRecord:
    settlement_date: dt.date
    settlement_period: int
    commodity: str
    imbalance_mwh: float
    cash_out_price_gbp_per_mwh: float

    @property
    def direction(self) -> ImbalanceDirection:
        if self.imbalance_mwh > 0.01:
            return ImbalanceDirection.LONG
        elif self.imbalance_mwh < -0.01:
            return ImbalanceDirection.SHORT
        return ImbalanceDirection.FLAT

    @property
    def cash_out_cost_gbp(self) -> float:
        return round(abs(self.imbalance_mwh) * self.cash_out_price_gbp_per_mwh, 2)


class ImbalanceAnalytics:
    def __init__(self) -> None:
        self._records: List[ImbalanceRecord] = []

    def record(self, settlement_date: dt.date, period: int,
                 commodity: str, imbalance_mwh: float,
                 cash_out_price: float) -> ImbalanceRecord:
        rec = ImbalanceRecord(
            settlement_date=settlement_date, settlement_period=period,
            commodity=commodity, imbalance_mwh=imbalance_mwh,
            cash_out_price_gbp_per_mwh=cash_out_price,
        )
        self._records.append(rec)
        return rec

    def total_cash_out_gbp(self, year: int,
                             commodity: Optional[str] = None) -> float:
        records = [r for r in self._records if r.settlement_date.year == year]
        if commodity:
            records = [r for r in records if r.commodity == commodity]
        return round(sum(r.cash_out_cost_gbp for r in records), 2)

    def net_imbalance_mwh(self, year: int) -> float:
        return round(sum(
            r.imbalance_mwh for r in self._records
            if r.settlement_date.year == year
        ), 3)

    def systematic_bias(self, year: int) -> ImbalanceDirection:
        net = self.net_imbalance_mwh(year)
        if net > 0.01:
            return ImbalanceDirection.LONG
        elif net < -0.01:
            return ImbalanceDirection.SHORT
        return ImbalanceDirection.FLAT

    def worst_period(self, year: int) -> Optional[ImbalanceRecord]:
        yr_records = [r for r in self._records if r.settlement_date.year == year]
        if not yr_records:
            return None
        return max(yr_records, key=lambda r: r.cash_out_cost_gbp)

    def short_count(self, year: int) -> int:
        return sum(1 for r in self._records
                   if r.settlement_date.year == year
                   and r.direction == ImbalanceDirection.SHORT)

    def avg_cash_out_per_mwh(self, year: int) -> Optional[float]:
        records = [r for r in self._records if r.settlement_date.year == year]
        if not records:
            return None
        total_mwh = sum(abs(r.imbalance_mwh) for r in records)
        if total_mwh == 0:
            return 0.0
        total_cost = sum(r.cash_out_cost_gbp for r in records)
        return round(total_cost / total_mwh, 2)

    def imbalance_summary(self, year: int) -> dict:
        worst = self.worst_period(year)
        return {
            'year': year,
            'total_records': len([r for r in self._records
                                   if r.settlement_date.year == year]),
            'total_cash_out_gbp': self.total_cash_out_gbp(year),
            'net_imbalance_mwh': self.net_imbalance_mwh(year),
            'systematic_bias': self.systematic_bias(year).value,
            'short_periods': self.short_count(year),
            'worst_cost_gbp': worst.cash_out_cost_gbp if worst else 0.0,
        }
