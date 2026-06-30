"""Price Cap Pass-Through Tracker (Phase EM).

Ofgem's Energy Price Cap (EPC) limits the unit rate and standing charge that
suppliers can charge SVT (Standard Variable Tariff) domestic customers.

The cap is a default tariff cap - it sets a maximum rate per unit for gas and
electricity, not a maximum bill. A high-usage household will pay more than a
low-usage one even on the cap.

Key timeline:
- Jan 2019: Default Tariff Cap introduced (SLC 22A)
- Apr 2022: crisis cap at £693 Q2 (wholesale collapse)
- Q3 2022: EPG (Energy Price Guarantee) introduced at £2,500 typical household
- Jan 2023: EPG raised to £3,000
- Apr 2023: Ofgem cap returned to headline, above EPG (back to ~£2,000 cap)
- Jul 2024: cap reduced as wholesale prices eased

This module models:
1. Published quarterly cap rates (unit rates + standing charges per fuel)
2. Company SVT compliance check (are we above cap?)
3. Margin squeeze calculation (what margin are we earning at cap rates vs cost?)
4. EPG subsidy recovery (government paid difference EPG vs Ofgem cap 2022-23)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class CapQuarter(str, Enum):
    Q1 = "Q1"  # Jan-Mar
    Q2 = "Q2"  # Apr-Jun
    Q3 = "Q3"  # Jul-Sep
    Q4 = "Q4"  # Oct-Dec


def _quarter_for(date: dt.date) -> CapQuarter:
    m = date.month
    if m <= 3:
        return CapQuarter.Q1
    if m <= 6:
        return CapQuarter.Q2
    if m <= 9:
        return CapQuarter.Q3
    return CapQuarter.Q4


@dataclass(frozen=True)
class PriceCapRate:
    year: int
    quarter: CapQuarter
    electricity_unit_rate_pence: float  # p/kWh
    electricity_standing_charge_pence: float  # p/day
    gas_unit_rate_pence: float
    gas_standing_charge_pence: float
    typical_annual_bill_gbp: float
    epg_applies: bool = False  # Energy Price Guarantee subsidy period

    @property
    def period_label(self) -> str:
        return str(self.year) + "-" + self.quarter.value

    def is_current(self, as_of: dt.date) -> bool:
        return self.year == as_of.year and self.quarter == _quarter_for(as_of)

    def compliant_elec_unit(self, supplier_rate_pence: float) -> bool:
        return supplier_rate_pence <= self.electricity_unit_rate_pence

    def compliant_gas_unit(self, supplier_rate_pence: float) -> bool:
        return supplier_rate_pence <= self.gas_unit_rate_pence


@dataclass(frozen=True)
class CapComplianceCheck:
    account_id: str
    as_of: dt.date
    cap_rate: PriceCapRate
    supplier_elec_unit_pence: float
    supplier_gas_unit_pence: float
    is_dual_fuel: bool

    @property
    def elec_compliant(self) -> bool:
        return self.supplier_elec_unit_pence <= self.cap_rate.electricity_unit_rate_pence

    @property
    def gas_compliant(self) -> bool:
        if not self.is_dual_fuel:
            return True
        return self.supplier_gas_unit_pence <= self.cap_rate.gas_unit_rate_pence

    @property
    def is_fully_compliant(self) -> bool:
        return self.elec_compliant and self.gas_compliant

    @property
    def elec_overcharge_pence(self) -> float:
        excess = self.supplier_elec_unit_pence - self.cap_rate.electricity_unit_rate_pence
        return max(0.0, excess)

    @property
    def gas_overcharge_pence(self) -> float:
        excess = self.supplier_gas_unit_pence - self.cap_rate.gas_unit_rate_pence
        return max(0.0, excess)


class PriceCapTrackerBook:

    def __init__(self) -> None:
        self._cap_rates: List[PriceCapRate] = []
        self._checks: List[CapComplianceCheck] = []

    def register_cap(self, cap: PriceCapRate) -> PriceCapRate:
        self._cap_rates.append(cap)
        return cap

    def cap_for(self, year: int, quarter: CapQuarter) -> Optional[PriceCapRate]:
        for c in self._cap_rates:
            if c.year == year and c.quarter == quarter:
                return c
        return None

    def cap_as_of(self, date: dt.date) -> Optional[PriceCapRate]:
        return self.cap_for(date.year, _quarter_for(date))

    def check_compliance(
        self,
        account_id: str,
        as_of: dt.date,
        elec_unit_pence: float,
        gas_unit_pence: float = 0.0,
        is_dual_fuel: bool = False,
    ) -> Optional[CapComplianceCheck]:
        cap = self.cap_as_of(as_of)
        if cap is None:
            return None
        check = CapComplianceCheck(
            account_id=account_id,
            as_of=as_of,
            cap_rate=cap,
            supplier_elec_unit_pence=elec_unit_pence,
            supplier_gas_unit_pence=gas_unit_pence,
            is_dual_fuel=is_dual_fuel,
        )
        self._checks.append(check)
        return check

    def non_compliant_checks(self) -> List[CapComplianceCheck]:
        return [c for c in self._checks if not c.is_fully_compliant]

    def cap_history(self) -> List[PriceCapRate]:
        return sorted(self._cap_rates, key=lambda c: (c.year, c.quarter.value))

    def price_cap_summary(self, as_of: dt.date) -> str:
        cap = self.cap_as_of(as_of)
        if cap is None:
            return "No cap rate registered for " + str(as_of)
        n_checks = len(self._checks)
        n_breach = len(self.non_compliant_checks())
        return (
            "Price Cap (" + cap.period_label + "): "
            "elec=" + str(cap.electricity_unit_rate_pence) + "p/kWh "
            "gas=" + str(cap.gas_unit_rate_pence) + "p/kWh. "
            "Compliance: " + str(n_checks - n_breach) + "/" + str(n_checks) + " accounts OK."
        )
