"""SoLR Levy Reconciliation Register (Phase ER).

When a supplier fails and Ofgem designates a Supplier of Last Resort (SoLR),
the costs incurred by the SoLR are recovered through:

1. SoLR Levy: a levy on all remaining suppliers, applied via BSC settlement
   - Levied on MWh consumed during the SoLR period
   - Calculated as shortfall / total market MWh in period

2. Mutualisation: unpaid BSC charges from the failed supplier are spread
   across all participants via BSC market (Elexon administers)

3. Customer credit transfer: failed supplier may have net credit customer balances
   - These must be honoured by the SoLR (government backstops this)

This module models:
- Company's obligation to pay SoLR levies when other suppliers fail
- Mutualisation charges from Elexon settlement
- Accrual of expected levy exposure based on market observations

2021-22: 28 supplier failures; ~£3bn SoLR levy distributed across survivors.
Octopus, E.ON, OVO, British Gas acted as SoLR for multiple failed suppliers.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class LevyType(str, Enum):
    SOLR_LEVY = "solr_levy"                  # SoLR failure recovery
    BSC_MUTUALISATION = "bsc_mutualisation"  # unpaid BSC charges
    CUSTOMER_CREDIT_TRANSFER = "credit_transfer"  # customer credit honours


@dataclass(frozen=True)
class SoLRLevyCharge:
    levy_type: LevyType
    failed_supplier_name: str
    levy_date: dt.date
    company_mwh_in_period: float
    levy_rate_gbp_per_mwh: float
    total_market_mwh: float
    company_share_fraction: float  # company_mwh / total_market_mwh

    @property
    def company_levy_gbp(self) -> float:
        return self.company_mwh_in_period * self.levy_rate_gbp_per_mwh

    @property
    def market_total_levy_gbp(self) -> float:
        return self.total_market_mwh * self.levy_rate_gbp_per_mwh

    @property
    def is_significant(self) -> bool:
        return self.company_levy_gbp > 10_000.0

    def levy_summary(self) -> str:
        return (
            "SoLR Levy (" + self.failed_supplier_name + ", " + str(self.levy_date) + "): "
            "type=" + self.levy_type.value + " "
            "rate=GBP" + str(round(self.levy_rate_gbp_per_mwh, 4)) + "/MWh "
            "company_mwh=" + str(round(self.company_mwh_in_period, 1)) + " "
            "company_charge=GBP" + str(round(self.company_levy_gbp, 0))
        )


class SoLRLevyRegister:

    def __init__(self) -> None:
        self._charges: List[SoLRLevyCharge] = []

    def record(self, charge: SoLRLevyCharge) -> SoLRLevyCharge:
        self._charges.append(charge)
        return charge

    def charges_for_year(self, year: int) -> List[SoLRLevyCharge]:
        return [c for c in self._charges if c.levy_date.year == year]

    def solr_levies(self) -> List[SoLRLevyCharge]:
        return [c for c in self._charges if c.levy_type == LevyType.SOLR_LEVY]

    def mutualisation_charges(self) -> List[SoLRLevyCharge]:
        return [c for c in self._charges if c.levy_type == LevyType.BSC_MUTUALISATION]

    def significant_levies(self) -> List[SoLRLevyCharge]:
        return [c for c in self._charges if c.is_significant]

    def total_levy_paid_gbp(self, year: Optional[int] = None) -> float:
        charges = self.charges_for_year(year) if year else self._charges
        return sum(c.company_levy_gbp for c in charges)

    def total_market_loss_recovered_gbp(self) -> float:
        return sum(c.market_total_levy_gbp for c in self._charges)

    def unique_failed_suppliers(self) -> list:
        return list(dict.fromkeys(c.failed_supplier_name for c in self._charges))

    def levy_register_summary(self, as_of: dt.date) -> str:
        n = len(self._charges)
        n_sig = len(self.significant_levies())
        total = self.total_levy_paid_gbp()
        n_failed = len(self.unique_failed_suppliers())
        return (
            "SoLR Levy Register (" + str(as_of) + "): "
            + str(n) + " levy charges from " + str(n_failed) + " failed suppliers. "
            + str(n_sig) + " significant. "
            "Total paid: GBP" + str(round(total)) + "."
        )
