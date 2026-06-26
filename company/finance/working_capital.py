"""Working capital daily cash position: inflows, outflows, headroom monitoring."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class CashFlowType(str, Enum):
    CUSTOMER_COLLECTIONS = 'customer_collections'
    WHOLESALE_SETTLEMENT = 'wholesale_settlement'
    NETWORK_CHARGES = 'network_charges'
    PAYROLL = 'payroll'
    VAT_PAYMENT = 'vat_payment'
    CREDIT_FACILITY_DRAWDOWN = 'credit_facility_drawdown'
    CREDIT_FACILITY_REPAYMENT = 'credit_facility_repayment'
    DSR_REVENUE = 'dsr_revenue'
    REGO_PURCHASE = 'rego_purchase'


class CashFlowDirection(str, Enum):
    INFLOW = 'inflow'
    OUTFLOW = 'outflow'


@dataclass(frozen=True)
class CashFlowEntry:
    entry_date: dt.date
    flow_type: CashFlowType
    direction: CashFlowDirection
    amount_gbp: float
    reference: str = ''

    @property
    def signed_amount(self) -> float:
        if self.direction == CashFlowDirection.INFLOW:
            return self.amount_gbp
        return -self.amount_gbp


@dataclass
class DailyCashPosition:
    as_of_date: dt.date
    opening_balance_gbp: float
    entries: List[CashFlowEntry] = None

    def __post_init__(self):
        if self.entries is None:
            self.entries = []

    @property
    def net_cash_flow_gbp(self) -> float:
        return round(sum(e.signed_amount for e in self.entries), 2)

    @property
    def closing_balance_gbp(self) -> float:
        return round(self.opening_balance_gbp + self.net_cash_flow_gbp, 2)

    @property
    def total_inflows_gbp(self) -> float:
        return round(sum(e.amount_gbp for e in self.entries
                          if e.direction == CashFlowDirection.INFLOW), 2)

    @property
    def total_outflows_gbp(self) -> float:
        return round(sum(e.amount_gbp for e in self.entries
                          if e.direction == CashFlowDirection.OUTFLOW), 2)


class WorkingCapitalMonitor:
    def __init__(self, opening_balance_gbp: float) -> None:
        self._balance = opening_balance_gbp
        self._positions: List[DailyCashPosition] = []
        self._minimum_operating_balance_gbp = 50_000.0

    def set_minimum_balance(self, amount_gbp: float) -> None:
        self._minimum_operating_balance_gbp = amount_gbp

    def post_day(self, date: dt.date,
                   entries: List[tuple]) -> DailyCashPosition:
        pos = DailyCashPosition(
            as_of_date=date,
            opening_balance_gbp=self._balance,
        )
        for flow_type, direction, amount, ref in entries:
            entry = CashFlowEntry(
                entry_date=date, flow_type=flow_type,
                direction=direction, amount_gbp=amount, reference=ref,
            )
            pos.entries.append(entry)
        self._balance = pos.closing_balance_gbp
        self._positions.append(pos)
        return pos

    def current_balance(self) -> float:
        return self._balance

    def is_below_minimum(self) -> bool:
        return self._balance < self._minimum_operating_balance_gbp

    def headroom_gbp(self) -> float:
        return round(self._balance - self._minimum_operating_balance_gbp, 2)

    def positions_in_period(self, start: dt.date, end: dt.date) -> List[DailyCashPosition]:
        return [p for p in self._positions
                if start <= p.as_of_date <= end]

    def lowest_balance_in_period(self, start: dt.date, end: dt.date) -> Optional[float]:
        positions = self.positions_in_period(start, end)
        if not positions:
            return None
        return min(p.closing_balance_gbp for p in positions)

    def total_inflows_gbp(self, start: dt.date, end: dt.date) -> float:
        return round(sum(
            p.total_inflows_gbp for p in self.positions_in_period(start, end)
        ), 2)

    def cash_summary(self, start: dt.date, end: dt.date) -> dict:
        positions = self.positions_in_period(start, end)
        return {
            'period_start': start.isoformat(),
            'period_end': end.isoformat(),
            'days': len(positions),
            'current_balance_gbp': self._balance,
            'headroom_gbp': self.headroom_gbp(),
            'is_below_minimum': self.is_below_minimum(),
            'total_inflows_gbp': self.total_inflows_gbp(start, end),
            'lowest_balance_gbp': self.lowest_balance_in_period(start, end),
        }
