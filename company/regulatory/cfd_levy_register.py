"""Contract for Difference (CfD) Levy Register (Phase FJ).

Contracts for Difference (CfDs) are government-backed contracts between
low-carbon generators and the Low Carbon Contracts Company (LCCC).

How it works:
- CfD Strike Price: guaranteed price for each MWh generated (set at auction)
- Reference Price: actual market price
- If Strike > Reference: LCCC pays generator the difference (funded by supplier levy)
- If Reference > Strike: generator pays back the difference to LCCC

From the supplier's perspective:
- Pay CfD Supplier Obligation (levy) if CfD payments are flowing to generators
- Receive CfD Operational Levy refund if generators are paying back

The levy is collected quarterly by LCCC based on the supplier's electricity supply volume.

Observed data: LCCC publishes quarterly levy rates (p/MWh) which suppliers apply
to their metered supply volume. Reference prices and CfD settlement are public.

2023-24: offshore wind CfD strike prices ~£40-50/MWh; market was £60-90/MWh
-> generators paying back = suppliers receive negative levy (credit/refund)

This is a high-volatility levy that can swing from cost to credit in different
price environments.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class CFDLevyDirection(str, Enum):
    PAYMENT = "payment"     # supplier pays levy (strike > market)
    RECEIPT = "receipt"     # supplier receives refund (market > strike)


@dataclass(frozen=True)
class CFDLevyQuarter:
    year: int
    quarter: int             # 1-4
    levy_rate_pence_per_mwh: float   # can be negative if market > strike
    supplier_mwh_supplied: float

    @property
    def period_label(self) -> str:
        return str(self.year) + " Q" + str(self.quarter)

    @property
    def total_levy_gbp(self) -> float:
        return self.supplier_mwh_supplied * self.levy_rate_pence_per_mwh / 100

    @property
    def direction(self) -> CFDLevyDirection:
        if self.total_levy_gbp >= 0:
            return CFDLevyDirection.PAYMENT
        return CFDLevyDirection.RECEIPT

    @property
    def is_credit(self) -> bool:
        return self.total_levy_gbp < 0

    def levy_summary(self) -> str:
        return (
            "CfD Levy " + self.period_label + ": "
            + str(round(self.levy_rate_pence_per_mwh, 3)) + "p/MWh "
            "total=" + ("+" if not self.is_credit else "") + "GBP" + str(round(self.total_levy_gbp, 0))
            + " [" + self.direction.value + "]"
        )


class CFDLevyRegister:

    def __init__(self) -> None:
        self._quarters: List[CFDLevyQuarter] = []

    def record(self, quarter: CFDLevyQuarter) -> CFDLevyQuarter:
        self._quarters.append(quarter)
        return quarter

    def quarters_for_year(self, year: int) -> List[CFDLevyQuarter]:
        return [q for q in self._quarters if q.year == year]

    def total_levy_gbp(self, year: Optional[int] = None) -> float:
        quarters = self._quarters if year is None else self.quarters_for_year(year)
        return sum(q.total_levy_gbp for q in quarters)

    def credit_quarters(self) -> List[CFDLevyQuarter]:
        return [q for q in self._quarters if q.is_credit]

    def payment_quarters(self) -> List[CFDLevyQuarter]:
        return [q for q in self._quarters if not q.is_credit]

    def avg_levy_rate_pence_per_mwh(self) -> float:
        if not self._quarters:
            return 0.0
        return sum(q.levy_rate_pence_per_mwh for q in self._quarters) / len(self._quarters)

    def cfd_levy_summary(self) -> str:
        n = len(self._quarters)
        total = self.total_levy_gbp()
        n_credit = len(self.credit_quarters())
        return (
            "CfD Levy Register: " + str(n) + " quarters. "
            "Net levy: GBP" + str(round(total, 0)) + " "
            "(" + ("cost" if total >= 0 else "credit") + "). "
            "Credit quarters: " + str(n_credit) + "."
        )
