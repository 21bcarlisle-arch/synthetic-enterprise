"""Capacity Market Revenue Register (Phase EX).

The Capacity Market (CM) is a UK government mechanism to ensure sufficient
dispatchable generation capacity. Suppliers don't directly participate in CM
auctions (that's for generators and DSR providers), but they:

1. Pay CM supplier obligations (a levy on their consumption MWh)
2. May receive CM revenue if they have registered demand-side response (DSR)
   or battery storage flexibility assets

From the company's perspective:
- CM Obligation: paid quarterly based on metered consumption
  Rate: ~GBP4-8/kW/yr (varies by auction year) = ~GBP0.50-1.00/MWh for typical customer
- CM Revenue: received if flexibility assets (batteries, DSR) are contracted
  Rate: ~GBP50-100/kW/yr for contracted flexible capacity

This module models:
- CM obligation payments (cost)
- CM revenue receipts from contracted flexibility (revenue)
- Net CM position (revenue offset against obligation)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class CMDirection(str, Enum):
    OBLIGATION = "obligation"   # company pays (consumer MWh-based levy)
    REVENUE = "revenue"         # company receives (DSR/battery contract)


@dataclass(frozen=True)
class CMTransaction:
    delivery_year: int          # 2016-2025
    direction: CMDirection
    asset_id: Optional[str]     # None for obligations; asset ID for CM revenue
    mwh_consumed: float         # for obligations
    contracted_kw: float        # for revenue contracts (0 if obligation)
    rate_gbp: float             # per MWh (obligation) or per kW/yr (revenue)

    @property
    def gross_amount_gbp(self) -> float:
        if self.direction == CMDirection.OBLIGATION:
            return self.mwh_consumed * self.rate_gbp
        return self.contracted_kw * self.rate_gbp

    @property
    def is_obligation(self) -> bool:
        return self.direction == CMDirection.OBLIGATION

    def transaction_summary(self) -> str:
        return (
            "CM " + self.direction.value + " " + str(self.delivery_year) + ": "
            "GBP" + str(round(self.gross_amount_gbp, 0))
        )


class CapacityMarketRegister:

    def __init__(self) -> None:
        self._transactions: List[CMTransaction] = []

    def record(self, txn: CMTransaction) -> CMTransaction:
        self._transactions.append(txn)
        return txn

    def transactions_for_year(self, year: int) -> List[CMTransaction]:
        return [t for t in self._transactions if t.delivery_year == year]

    def obligations_for_year(self, year: int) -> List[CMTransaction]:
        return [t for t in self.transactions_for_year(year) if t.is_obligation]

    def revenues_for_year(self, year: int) -> List[CMTransaction]:
        return [t for t in self.transactions_for_year(year) if not t.is_obligation]

    def total_obligation_gbp(self, year: Optional[int] = None) -> float:
        txns = self._transactions if year is None else self.transactions_for_year(year)
        return sum(t.gross_amount_gbp for t in txns if t.is_obligation)

    def total_revenue_gbp(self, year: Optional[int] = None) -> float:
        txns = self._transactions if year is None else self.transactions_for_year(year)
        return sum(t.gross_amount_gbp for t in txns if not t.is_obligation)

    def net_cm_position_gbp(self, year: Optional[int] = None) -> float:
        return self.total_revenue_gbp(year) - self.total_obligation_gbp(year)

    def contracted_kw_total(self) -> float:
        return sum(t.contracted_kw for t in self._transactions if not t.is_obligation)

    def cm_register_summary(self, year: Optional[int] = None) -> str:
        label = str(year) if year else "all years"
        obl = self.total_obligation_gbp(year)
        rev = self.total_revenue_gbp(year)
        net = self.net_cm_position_gbp(year)
        return (
            "Capacity Market (" + label + "): "
            "obligation=GBP" + str(round(obl)) + " "
            "revenue=GBP" + str(round(rev)) + " "
            "net=GBP" + str(round(net)) + "."
        )
