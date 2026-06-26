from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class HouseholdType(str, Enum):
    SINGLE_OCCUPANT = 'single_occupant'
    COUPLE_NO_CHILDREN = 'couple_no_children'
    FAMILY_WITH_CHILDREN = 'family_with_children'
    RETIRED_COUPLE = 'retired_couple'
    RETIRED_SINGLE = 'retired_single'
    STUDENT_HOUSEHOLD = 'student_household'
    WORK_FROM_HOME = 'work_from_home'


class HeatingSystem(str, Enum):
    GAS_BOILER = 'gas_boiler'
    HEAT_PUMP = 'heat_pump'
    STORAGE_HEATER = 'storage_heater'
    DISTRICT_HEATING = 'district_heating'
    OIL_BOILER = 'oil_boiler'
    SOLID_FUEL = 'solid_fuel'
    NO_CENTRAL_HEATING = 'no_central_heating'


_PEAK_LOAD_FACTOR: dict[str, float] = {
    'single_occupant': 0.85,
    'couple_no_children': 1.00,
    'family_with_children': 1.35,
    'retired_couple': 1.20,
    'retired_single': 0.90,
    'student_household': 0.75,
    'work_from_home': 1.15,
}

_DAY_CONSUMPTION_PCT: dict[str, float] = {
    'single_occupant': 0.55,
    'couple_no_children': 0.50,
    'family_with_children': 0.45,
    'retired_couple': 0.72,
    'retired_single': 0.70,
    'student_household': 0.40,
    'work_from_home': 0.68,
}


@dataclass(frozen=True)
class HouseholdBehaviourProfile:
    household_type: HouseholdType
    heating_system: HeatingSystem
    occupants: int
    has_electric_cooking: bool = False
    wfh_days_per_week: int = 0

    @property
    def peak_load_factor(self) -> float:
        base = _PEAK_LOAD_FACTOR.get(self.household_type.value, 1.0)
        wfh_boost = 0.08 if self.wfh_days_per_week >= 3 else 0.0
        return round(base + wfh_boost, 2)

    @property
    def daytime_consumption_pct(self) -> float:
        base = _DAY_CONSUMPTION_PCT.get(self.household_type.value, 0.50)
        wfh_boost = 0.10 if self.wfh_days_per_week >= 3 else 0.0
        return round(min(0.85, base + wfh_boost), 2)

    @property
    def evening_consumption_pct(self) -> float:
        return round(1.0 - self.daytime_consumption_pct, 2)

    @property
    def tou_price_sensitivity(self) -> str:
        if self.household_type in (
            HouseholdType.RETIRED_COUPLE, HouseholdType.RETIRED_SINGLE
        ):
            return 'low'
        if self.household_type in (
            HouseholdType.WORK_FROM_HOME, HouseholdType.SINGLE_OCCUPANT
        ):
            return 'high'
        return 'medium'

    @property
    def smart_meter_benefit_score(self) -> float:
        sensitivity_map = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
        sensitivity = sensitivity_map.get(self.tou_price_sensitivity, 0.6)
        evening_heavy = self.evening_consumption_pct > 0.55
        return round(sensitivity * (1.3 if evening_heavy else 1.0), 2)

    @property
    def heat_pump_eligible(self) -> bool:
        return self.heating_system != HeatingSystem.HEAT_PUMP
