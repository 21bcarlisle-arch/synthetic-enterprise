from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ProfileClass(str, Enum):
    """Electricity settlement profile class (determines half-hourly shape)."""
    PC1 = "1"   # Domestic unrestricted
    PC2 = "2"   # Domestic Economy 7
    PC3 = "3"   # Non-domestic unrestricted (small)
    PC4 = "4"   # Non-domestic Economy 7
    PC5 = "5"   # Non-domestic MD <= 100kW (HH metered)
    PC6 = "6"   # Non-domestic MD > 100kW
    PC7 = "7"   # Non-domestic HH MD <= 100kW
    PC8 = "8"   # Non-domestic HH MD > 100kW (I&C)


class FuelType(str, Enum):
    ELECTRICITY = "electricity"
    GAS = "gas"


@dataclass(frozen=True)
class SupplyPointRecord:
    identifier: str  # MPAN (13 digits) or MPRN (10 digits)
    account_id: str
    fuel: FuelType
    profile_class: Optional[ProfileClass]  # electricity only
    supplier_start_date: str
    supplier_end_date: Optional[str] = None
    annual_quantity_kwh: float = 0.0  # AQ from DCUSA/xoserve

    @property
    def is_active(self) -> bool:
        return self.supplier_end_date is None

    @property
    def is_hh(self) -> bool:
        """Half-hourly metered — profile class 5-8."""
        return self.profile_class in (
            ProfileClass.PC5, ProfileClass.PC6, ProfileClass.PC7, ProfileClass.PC8
        )

    @property
    def is_domestic(self) -> bool:
        return self.profile_class in (ProfileClass.PC1, ProfileClass.PC2)


class SupplyPointRegister:
    def __init__(self) -> None:
        self._records: dict[str, SupplyPointRecord] = {}

    def register(self, record: SupplyPointRecord) -> SupplyPointRecord:
        self._records[record.identifier] = record
        return record

    def deregister(self, identifier: str, end_date: str) -> Optional[SupplyPointRecord]:
        from dataclasses import replace
        if identifier not in self._records:
            return None
        updated = replace(self._records[identifier], supplier_end_date=end_date)
        self._records[identifier] = updated
        return updated

    def get(self, identifier: str) -> Optional[SupplyPointRecord]:
        return self._records.get(identifier)

    def active_points(self, fuel: Optional[FuelType] = None) -> list[SupplyPointRecord]:
        active = [r for r in self._records.values() if r.is_active]
        return [r for r in active if r.fuel == fuel] if fuel else active

    def points_for_account(self, account_id: str) -> list[SupplyPointRecord]:
        return [r for r in self._records.values() if r.account_id == account_id]

    def hh_points(self) -> list[SupplyPointRecord]:
        return [r for r in self._records.values() if r.is_active and r.is_hh]

    def profile_class_breakdown(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for r in self._records.values():
            if r.is_active and r.profile_class:
                key = r.profile_class.value
                result[key] = result.get(key, 0) + 1
        return result

    def total_aq_kwh(self, fuel: Optional[FuelType] = None) -> float:
        pts = self.active_points(fuel)
        return round(sum(r.annual_quantity_kwh for r in pts), 2)

    def register_summary(self) -> dict:
        return {
            "total_registered": len(self._records),
            "active_electricity": len(self.active_points(FuelType.ELECTRICITY)),
            "active_gas": len(self.active_points(FuelType.GAS)),
            "hh_points": len(self.hh_points()),
            "total_aq_electricity_kwh": self.total_aq_kwh(FuelType.ELECTRICITY),
        }
