"""CfD (Contracts for Difference) levy tracker.

UK suppliers pay a per-MWh electricity levy to the Low Carbon Contracts Company
(LCCC) to fund CfD payments to renewable generators. The quarterly levy rate
reflects whether CfD generators are earning above or below their strike price.

Key market dynamics:
- 2016-2020: levy positive (£1-6/MWh), renewables earning below market.
- 2021-2022: electricity prices surpassed most CfD strike prices -> generators
  repay excess to LCCC -> levy rate turned NEGATIVE in Q4 2022 (suppliers
  received a credit, reducing their bills).
- 2023-2025: prices normalised, levy returned to low positive (~£1-3/MWh).

Levy applies only to electricity; gas supply is not subject to CfD levy.
Source: LCCC quarterly settlement notices (public domain).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class LevyDirection(str, Enum):
    POSITIVE = "positive"   # supplier pays levy to LCCC
    NEGATIVE = "negative"   # LCCC credits supplier (generators repaying)
    ZERO = "zero"           # net-zero quarter


# Historical CfD levy rates (£/MWh) by year and quarter (Q1-Q4).
# Negative values = supplier credit (2022 Q3-Q4 / 2023 Q1 crisis reversal).
# Source: LCCC public settlement data, simplified to quarterly averages.
_LEVY_RATES_GBP_PER_MWH: Dict[int, Dict[int, float]] = {
    2016: {1: 2.5, 2: 2.7, 3: 2.9, 4: 3.1},
    2017: {1: 3.2, 2: 3.5, 3: 3.4, 4: 3.6},
    2018: {1: 3.7, 2: 3.9, 3: 4.0, 4: 4.2},
    2019: {1: 4.3, 2: 4.6, 3: 4.8, 4: 5.1},
    2020: {1: 5.2, 2: 4.8, 3: 4.9, 4: 5.0},
    2021: {1: 5.3, 2: 4.5, 3: 2.8, 4: 1.2},  # prices rising -> levy shrinking
    2022: {1: 0.5, 2: -1.8, 3: -8.5, 4: -12.3},  # crisis: generators pay back
    2023: {1: -6.2, 2: 1.4, 3: 2.1, 4: 2.6},     # normalising
    2024: {1: 2.4, 2: 2.3, 3: 2.2, 4: 2.4},
    2025: {1: 2.5, 2: 2.6, 3: 2.7, 4: 2.8},
}

_LEVY_FALLBACK_GBP_PER_MWH = 3.0


def _quarter(month: int) -> int:
    return (month - 1) // 3 + 1


def get_levy_rate(year: int, quarter: int) -> float:
    """Return CfD levy rate (£/MWh) for given year/quarter. Negative = credit."""
    return _LEVY_RATES_GBP_PER_MWH.get(year, {}).get(quarter, _LEVY_FALLBACK_GBP_PER_MWH)


@dataclass(frozen=True)
class CfDLevyCharge:
    account_id: str
    charge_date: dt.date
    year: int
    quarter: int
    consumption_mwh: float
    rate_gbp_per_mwh: float

    @property
    def levy_gbp(self) -> float:
        return round(self.consumption_mwh * self.rate_gbp_per_mwh, 2)

    @property
    def direction(self) -> LevyDirection:
        if self.rate_gbp_per_mwh > 0:
            return LevyDirection.POSITIVE
        if self.rate_gbp_per_mwh < 0:
            return LevyDirection.NEGATIVE
        return LevyDirection.ZERO

    @property
    def is_credit(self) -> bool:
        return self.direction == LevyDirection.NEGATIVE


class CfDLevyBook:
    """Record CfD levy charges across accounts and periods."""

    def __init__(self) -> None:
        self._charges: List[CfDLevyCharge] = []

    def record_charge(self, account_id: str, charge_date: dt.date,
                      consumption_mwh: float) -> CfDLevyCharge:
        """Record a CfD levy charge for a given settlement period."""
        year = charge_date.year
        quarter = _quarter(charge_date.month)
        rate = get_levy_rate(year, quarter)
        charge = CfDLevyCharge(
            account_id=account_id,
            charge_date=charge_date,
            year=year,
            quarter=quarter,
            consumption_mwh=consumption_mwh,
            rate_gbp_per_mwh=rate,
        )
        self._charges.append(charge)
        return charge

    def charges_for_account(self, account_id: str) -> List[CfDLevyCharge]:
        return [c for c in self._charges if c.account_id == account_id]

    def annual_levy_gbp(self, year: int, account_id: Optional[str] = None) -> float:
        charges = [c for c in self._charges if c.year == year]
        if account_id:
            charges = [c for c in charges if c.account_id == account_id]
        return round(sum(c.levy_gbp for c in charges), 2)

    def quarterly_levy_gbp(self, year: int, quarter: int) -> float:
        charges = [c for c in self._charges if c.year == year and c.quarter == quarter]
        return round(sum(c.levy_gbp for c in charges), 2)

    def total_credit_quarters(self, account_id: Optional[str] = None) -> int:
        """Count quarters where the levy was negative (supplier received credit)."""
        seen: set[tuple[int, int]] = set()
        result = 0
        for c in self._charges:
            if account_id and c.account_id != account_id:
                continue
            key = (c.year, c.quarter)
            if key not in seen:
                seen.add(key)
                if c.is_credit:
                    result += 1
        return result

    def levy_summary(self, year: int) -> dict:
        year_charges = [c for c in self._charges if c.year == year]
        annual_total = round(sum(c.levy_gbp for c in year_charges), 2)
        credit_quarters = sum(
            1 for q in range(1, 5)
            if get_levy_rate(year, q) < 0
        )
        return {
            "year": year,
            "total_levy_gbp": annual_total,
            "is_net_credit": annual_total < 0,
            "credit_quarters": credit_quarters,
            "accounts_charged": len({c.account_id for c in year_charges}),
            "total_mwh": round(sum(c.consumption_mwh for c in year_charges), 3),
        }
