"""Dual-Fuel Account Consolidator — unified gas + electricity view.

UK dual-fuel customers have separate MPAN (electricity) and MPRN (gas) supply
points but are managed under a single customer account. This module provides the
consolidated account view that billing, CRM, and customer-facing systems need.

A real supplier bills gas and electricity separately (different settlement regimes:
BSC for electricity, UNC for gas) but the customer sees one account, one bill,
one direct debit.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class FuelType(str, Enum):
    ELECTRICITY = "electricity"
    GAS = "gas"


@dataclass(frozen=True)
class FuelLeg:
    """One fuel supply leg on a customer account."""
    account_id: str
    fuel: FuelType
    supply_point_ref: str        # MPAN (electricity) or MPRN (gas)
    tariff_name: str
    unit_rate_pence: float       # p/kWh
    standing_charge_pence: float # p/day
    estimated_annual_kwh: float  # EAC (elec) or AQ (gas)
    active: bool = True

    @property
    def estimated_annual_cost_gbp(self) -> float:
        unit_cost = (self.estimated_annual_kwh * self.unit_rate_pence) / 100.0
        standing = (365 * self.standing_charge_pence) / 100.0
        return round(unit_cost + standing, 2)


@dataclass(frozen=True)
class DualFuelAccount:
    """Consolidated view of all fuel legs for a single account."""
    account_id: str
    electricity_leg: Optional[FuelLeg]
    gas_leg: Optional[FuelLeg]

    @property
    def is_dual_fuel(self) -> bool:
        return self.electricity_leg is not None and self.gas_leg is not None

    @property
    def is_electricity_only(self) -> bool:
        return self.electricity_leg is not None and self.gas_leg is None

    @property
    def is_gas_only(self) -> bool:
        return self.gas_leg is not None and self.electricity_leg is None

    @property
    def has_any_supply(self) -> bool:
        return self.electricity_leg is not None or self.gas_leg is not None

    @property
    def combined_annual_cost_gbp(self) -> float:
        total = 0.0
        if self.electricity_leg and self.electricity_leg.active:
            total += self.electricity_leg.estimated_annual_cost_gbp
        if self.gas_leg and self.gas_leg.active:
            total += self.gas_leg.estimated_annual_cost_gbp
        return round(total, 2)

    @property
    def active_fuels(self) -> list[str]:
        fuels = []
        if self.electricity_leg and self.electricity_leg.active:
            fuels.append("electricity")
        if self.gas_leg and self.gas_leg.active:
            fuels.append("gas")
        return fuels


class DualFuelAccountBook:
    """Manages consolidated gas/electricity account views.

    Electricity and gas are registered as separate legs; the book provides
    a unified DualFuelAccount view for any account_id.
    """

    def __init__(self) -> None:
        self._electricity: dict[str, FuelLeg] = {}
        self._gas: dict[str, FuelLeg] = {}

    def register_electricity_leg(self, leg: FuelLeg) -> FuelLeg:
        if leg.fuel != FuelType.ELECTRICITY:
            raise ValueError("Expected electricity FuelLeg")
        self._electricity[leg.account_id] = leg
        return leg

    def register_gas_leg(self, leg: FuelLeg) -> FuelLeg:
        if leg.fuel != FuelType.GAS:
            raise ValueError("Expected gas FuelLeg")
        self._gas[leg.account_id] = leg
        return leg

    def get_account(self, account_id: str) -> Optional[DualFuelAccount]:
        elec = self._electricity.get(account_id)
        gas = self._gas.get(account_id)
        if elec is None and gas is None:
            return None
        return DualFuelAccount(account_id=account_id, electricity_leg=elec, gas_leg=gas)

    def all_accounts(self) -> list[DualFuelAccount]:
        all_ids = set(self._electricity) | set(self._gas)
        return [self.get_account(aid) for aid in sorted(all_ids)]  # type: ignore[misc]

    def dual_fuel_accounts(self) -> list[DualFuelAccount]:
        return [a for a in self.all_accounts() if a.is_dual_fuel]

    def electricity_only(self) -> list[DualFuelAccount]:
        return [a for a in self.all_accounts() if a.is_electricity_only]

    def gas_only(self) -> list[DualFuelAccount]:
        return [a for a in self.all_accounts() if a.is_gas_only]

    def total_combined_annual_cost_gbp(self) -> float:
        return round(sum(a.combined_annual_cost_gbp for a in self.all_accounts()), 2)

    def dual_fuel_summary(self) -> dict:
        accounts = self.all_accounts()
        return {
            "total_accounts": len(accounts),
            "dual_fuel": len(self.dual_fuel_accounts()),
            "electricity_only": len(self.electricity_only()),
            "gas_only": len(self.gas_only()),
            "combined_annual_cost_gbp": self.total_combined_annual_cost_gbp(),
        }
