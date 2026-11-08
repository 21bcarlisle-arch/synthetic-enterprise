"""Corporation tax provision: UK CT rates 2016-2025 and annual provision calculation."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


# UK Corporation Tax main rate by financial year start (April)
# Source: HMRC; small company rates excluded (modelled as single-rate for simplicity)
_CT_RATE_BY_YEAR: Dict[int, float] = {
    2016: 0.20,  # Budget 2015: 20% -> 19% from April 2017
    2017: 0.19,
    2018: 0.19,
    2019: 0.19,
    2020: 0.19,
    2021: 0.19,
    2022: 0.19,  # Autumn 2021 Budget: freeze at 19% for 2022, rise to 25% from April 2023
    2023: 0.25,  # Finance Act 2021: 25% from 1 April 2023 (profits >GBP250k)
    2024: 0.25,
    2025: 0.25,
}


def _ct_rate_for_year(accounting_year: int) -> float:
    """Return the main CT rate for a calendar accounting year.
    UK financial year runs Apr-Mar; use the start of the calendar year as proxy."""
    return _CT_RATE_BY_YEAR.get(accounting_year, _CT_RATE_BY_YEAR[2025])


@dataclass(frozen=True)
class TaxProvision:
    accounting_year: int
    profit_before_tax_gbp: float
    ct_rate: float
    loss_relief_gbp: float = 0.0   # losses brought forward offset against this year

    @property
    def taxable_profit_gbp(self) -> float:
        return max(0.0, self.profit_before_tax_gbp - self.loss_relief_gbp)

    @property
    def current_tax_gbp(self) -> float:
        return round(self.taxable_profit_gbp * self.ct_rate, 2)

    @property
    def profit_after_tax_gbp(self) -> float:
        return round(self.profit_before_tax_gbp - self.current_tax_gbp, 2)

    @property
    def effective_rate_pct(self) -> float:
        if self.profit_before_tax_gbp <= 0:
            return 0.0
        return round(self.current_tax_gbp / self.profit_before_tax_gbp * 100, 1)

    @property
    def is_loss_year(self) -> bool:
        return self.profit_before_tax_gbp < 0


class CorporationTaxBook:
    """Annual CT provision tracker.

    Real data:
    - UK CT rate: 19% from April 2017 to March 2023; 25% from April 2023
    - Energy Profits Levy (EPL): applies to oil/gas PRODUCERS only; not energy suppliers
    - Loss relief: trading losses can be carried forward indefinitely or back 1 year
    - April 2023 change was the biggest CT rate rise since 1974
    - For a profitable energy supplier earning GBP1M net: additional GBP60k/yr from 2023
    - Small profits rate (profits <= GBP50k): 19% maintained; tapering to GBP250k
    """

    def __init__(self) -> None:
        self._provisions: Dict[int, TaxProvision] = {}
        self._accumulated_losses: float = 0.0

    def provision_for_year(
        self,
        accounting_year: int,
        profit_before_tax_gbp: float,
        use_loss_relief: bool = True,
    ) -> TaxProvision:
        rate = _ct_rate_for_year(accounting_year)
        relief = 0.0
        if use_loss_relief and self._accumulated_losses > 0 and profit_before_tax_gbp > 0:
            relief = min(self._accumulated_losses, profit_before_tax_gbp)

        provision = TaxProvision(
            accounting_year=accounting_year,
            profit_before_tax_gbp=profit_before_tax_gbp,
            ct_rate=rate,
            loss_relief_gbp=relief,
        )
        self._provisions[accounting_year] = provision

        # Update accumulated losses
        if profit_before_tax_gbp < 0:
            self._accumulated_losses += abs(profit_before_tax_gbp)
        elif relief > 0:
            self._accumulated_losses -= relief

        return provision

    def provision(self, accounting_year: int) -> Optional[TaxProvision]:
        return self._provisions.get(accounting_year)

    def total_tax_paid_gbp(self) -> float:
        return round(sum(p.current_tax_gbp for p in self._provisions.values()), 2)

    def loss_years(self) -> List[TaxProvision]:
        return [p for p in self._provisions.values() if p.is_loss_year]

    def accumulated_losses_gbp(self) -> float:
        return self._accumulated_losses

    def tax_summary(self) -> dict:
        provisions = sorted(self._provisions.values(), key=lambda p: p.accounting_year)
        return {
            "years_filed": len(self._provisions),
            "total_tax_paid_gbp": self.total_tax_paid_gbp(),
            "accumulated_losses_gbp": self.accumulated_losses_gbp(),
            "loss_years": len(self.loss_years()),
            "by_year": [
                {
                    "year": p.accounting_year,
                    "pbt_gbp": p.profit_before_tax_gbp,
                    "ct_rate_pct": p.ct_rate * 100,
                    "current_tax_gbp": p.current_tax_gbp,
                    "pat_gbp": p.profit_after_tax_gbp,
                    "effective_rate_pct": p.effective_rate_pct,
                }
                for p in provisions
            ],
        }
