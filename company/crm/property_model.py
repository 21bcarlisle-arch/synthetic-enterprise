from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PropertyType(str, Enum):
    DETACHED = 'detached'
    SEMI_DETACHED = 'semi_detached'
    TERRACED = 'terraced'
    FLAT = 'flat'
    BUNGALOW = 'bungalow'
    MOBILE_HOME = 'mobile_home'
    COMMERCIAL = 'commercial'


class TenureType(str, Enum):
    OWNER_OCCUPIED = 'owner_occupied'
    PRIVATE_RENTED = 'private_rented'
    SOCIAL_RENTED = 'social_rented'
    SHARED_OWNERSHIP = 'shared_ownership'


class EPCRating(str, Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'
    G = 'G'


_EPC_CONSUMPTION_MULTIPLIER: dict[str, float] = {
    'A': 0.60, 'B': 0.75, 'C': 0.90, 'D': 1.00,
    'E': 1.20, 'F': 1.45, 'G': 1.75,
}

_FLOOR_AREA_BASELINE_M2: dict[str, float] = {
    'detached': 130.0, 'semi_detached': 90.0, 'terraced': 75.0,
    'flat': 55.0, 'bungalow': 80.0, 'mobile_home': 45.0, 'commercial': 200.0,
}

UK_AVG_DOMESTIC_ELEC_KWH = 3100.0
UK_AVG_DOMESTIC_GAS_KWH = 12000.0


@dataclass(frozen=True)
class Property:
    uprn: str
    property_type: PropertyType
    tenure: TenureType
    epc_rating: EPCRating
    floor_area_m2: float
    bedrooms: int
    occupants: int
    has_gas: bool = True
    has_solar_pv: bool = False
    electric_vehicle: bool = False

    @property
    def consumption_multiplier(self) -> float:
        return _EPC_CONSUMPTION_MULTIPLIER[self.epc_rating.value]

    @property
    def estimated_annual_elec_kwh(self) -> float:
        area_factor = self.floor_area_m2 / _FLOOR_AREA_BASELINE_M2.get(
            self.property_type.value, 80.0
        )
        occupant_factor = max(1.0, self.occupants / 2.5)
        ev_uplift = 2500.0 if self.electric_vehicle else 0.0
        solar_offset = 2000.0 if self.has_solar_pv else 0.0
        base = UK_AVG_DOMESTIC_ELEC_KWH * area_factor * occupant_factor
        base *= self.consumption_multiplier
        return round(max(0.0, base + ev_uplift - solar_offset), 0)

    @property
    def estimated_annual_gas_kwh(self) -> float:
        if not self.has_gas:
            return 0.0
        area_factor = self.floor_area_m2 / _FLOOR_AREA_BASELINE_M2.get(
            self.property_type.value, 80.0
        )
        base = UK_AVG_DOMESTIC_GAS_KWH * area_factor
        base *= self.consumption_multiplier
        return round(max(0.0, base), 0)

    @property
    def is_fuel_poor(self) -> bool:
        return (
            self.epc_rating in (EPCRating.F, EPCRating.G)
            and self.tenure in (TenureType.PRIVATE_RENTED, TenureType.SOCIAL_RENTED)
        )

    @property
    def eco4_eligible(self) -> bool:
        return self.epc_rating.value in ('D', 'E', 'F', 'G')

    @property
    def psr_priority_property(self) -> bool:
        return self.epc_rating in (EPCRating.F, EPCRating.G)
