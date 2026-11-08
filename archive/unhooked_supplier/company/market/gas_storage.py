"""Gas storage position: seasonal injection, withdrawal, and storage optimisation."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class StorageFacility(str, Enum):
    ROUGH = 'rough'           # Depleted field -- mothballed 2017
    STUBLACH = 'stublach'     # Salt cavern, Cheshire
    HOLFORD = 'holford'       # Salt cavern, Cheshire
    HUMBLY_GROVE = 'humbly_grove'
    HORNSEA = 'hornsea'       # Depleted field


_STORAGE_CAPACITY_MCM: Dict[StorageFacility, float] = {
    StorageFacility.ROUGH: 3300.0,  # Historic. Mothballed May 2017
    StorageFacility.STUBLACH: 390.0,
    StorageFacility.HOLFORD: 40.0,
    StorageFacility.HUMBLY_GROVE: 320.0,
    StorageFacility.HORNSEA: 140.0,
}


class StorageOperation(str, Enum):
    INJECT = 'inject'
    WITHDRAW = 'withdraw'


@dataclass(frozen=True)
class StorageTransaction:
    facility: StorageFacility
    transaction_date: dt.date
    operation: StorageOperation
    volume_mcm: float
    price_gbp_per_therm: float

    @property
    def cost_gbp(self) -> float:
        therms_per_mcm = 3_412.14
        total_therms = self.volume_mcm * therms_per_mcm
        if self.operation == StorageOperation.INJECT:
            return round(total_therms * self.price_gbp_per_therm, 2)
        return round(-total_therms * self.price_gbp_per_therm, 2)

    @property
    def is_winter_operation(self) -> bool:
        return self.transaction_date.month in (10, 11, 12, 1, 2, 3)


@dataclass
class GasStorageBook:
    _transactions: List[StorageTransaction] = field(default_factory=list)
    _inventory_mcm: Dict[StorageFacility, float] = field(default_factory=dict)

    def inject(self, facility: StorageFacility, date: dt.date,
                 volume_mcm: float, price_gbp_per_therm: float) -> StorageTransaction:
        t = StorageTransaction(facility, date, StorageOperation.INJECT,
                                volume_mcm, price_gbp_per_therm)
        self._transactions.append(t)
        self._inventory_mcm[facility] = self._inventory_mcm.get(facility, 0.0) + volume_mcm
        return t

    def withdraw(self, facility: StorageFacility, date: dt.date,
                   volume_mcm: float, price_gbp_per_therm: float) -> StorageTransaction:
        t = StorageTransaction(facility, date, StorageOperation.WITHDRAW,
                                volume_mcm, price_gbp_per_therm)
        self._transactions.append(t)
        self._inventory_mcm[facility] = max(
            0.0, self._inventory_mcm.get(facility, 0.0) - volume_mcm
        )
        return t

    def inventory_mcm(self, facility: Optional[StorageFacility] = None) -> float:
        if facility:
            return self._inventory_mcm.get(facility, 0.0)
        return sum(self._inventory_mcm.values())

    def total_injected_mcm(self, year: int) -> float:
        return round(sum(
            t.volume_mcm for t in self._transactions
            if t.transaction_date.year == year
            and t.operation == StorageOperation.INJECT
        ), 2)

    def net_storage_cost_gbp(self, year: int) -> float:
        return round(sum(
            t.cost_gbp for t in self._transactions if t.transaction_date.year == year
        ), 2)

    def spread_gbp_per_therm(self, facility: StorageFacility,
                               year: int) -> Optional[float]:
        injects = [t for t in self._transactions
                    if t.facility == facility
                    and t.transaction_date.year == year
                    and t.operation == StorageOperation.INJECT]
        withdraws = [t for t in self._transactions
                      if t.facility == facility
                      and t.transaction_date.year == year
                      and t.operation == StorageOperation.WITHDRAW]
        if not injects or not withdraws:
            return None
        avg_inject = sum(t.price_gbp_per_therm for t in injects) / len(injects)
        avg_withdraw = sum(t.price_gbp_per_therm for t in withdraws) / len(withdraws)
        return round(avg_withdraw - avg_inject, 4)

    def storage_summary(self, year: int) -> dict:
        return {
            'year': year,
            'total_injected_mcm': self.total_injected_mcm(year),
            'total_inventory_mcm': self.inventory_mcm(),
            'net_storage_cost_gbp': self.net_storage_cost_gbp(year),
        }
