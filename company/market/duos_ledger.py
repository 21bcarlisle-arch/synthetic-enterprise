from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# DUoS rates p/kWh vary by DNO area and voltage level; representative values
_DUOS_UNIT_RATE_P_PER_KWH: dict[int, float] = {
    2016: 1.85, 2017: 1.92, 2018: 1.98, 2019: 2.05,
    2020: 2.12, 2021: 2.20, 2022: 2.35, 2023: 2.48, 2024: 2.60, 2025: 2.75,
}


class DNOArea(str, Enum):
    NORTHERN = "northern"
    YORKSHIRE = "yorkshire"
    EAST_MIDLANDS = "east_midlands"
    WEST_MIDLANDS = "west_midlands"
    SOUTH_WESTERN = "south_western"
    SOUTHERN = "southern"
    EASTERN = "eastern"
    LONDON = "london"
    SOUTH_EASTERN = "south_eastern"
    MERSEYRAIL = "merseyrail"
    NORTH_WESTERN = "north_western"
    EAST_OF_SCOTLAND = "east_of_scotland"
    HYDRO = "hydro"
    SOUTH_WALES = "south_wales"


class VoltageLevel(str, Enum):
    HIGH = "hv"       # HV: 11kV – typically I&C
    LOW = "lv"        # LV: 230V – residential and small business


@dataclass(frozen=True)
class DUoSCharge:
    account_id: str
    charge_period: str  # YYYY-MM
    dno_area: DNOArea
    voltage_level: VoltageLevel
    consumption_kwh: float
    unit_rate_p_per_kwh: float
    standing_charge_gbp: float = 0.0

    @property
    def unit_charge_gbp(self) -> float:
        return round(self.consumption_kwh * self.unit_rate_p_per_kwh / 100, 2)

    @property
    def total_charge_gbp(self) -> float:
        return round(self.unit_charge_gbp + self.standing_charge_gbp, 2)

    @property
    def is_hv(self) -> bool:
        return self.voltage_level == VoltageLevel.HIGH


class DUoSLedger:
    def __init__(self) -> None:
        self._charges: list[DUoSCharge] = []

    def record_charge(self, charge: DUoSCharge) -> DUoSCharge:
        self._charges.append(charge)
        return charge

    @staticmethod
    def unit_rate_for_year(year: int, voltage: VoltageLevel = VoltageLevel.LOW) -> float:
        base = _DUOS_UNIT_RATE_P_PER_KWH.get(year, 2.50)
        # HV customers pay ~40% less (direct network connection, fewer distribution losses)
        return round(base * 0.6 if voltage == VoltageLevel.HIGH else base, 4)

    def charges_for_account(self, account_id: str) -> list[DUoSCharge]:
        return [c for c in self._charges if c.account_id == account_id]

    def total_charged_gbp(self, year: Optional[int] = None) -> float:
        charges = (
            [c for c in self._charges if c.charge_period.startswith(str(year))]
            if year else self._charges
        )
        return round(sum(c.total_charge_gbp for c in charges), 2)

    def annual_unit_cost_p_per_kwh(self, year: int) -> float:
        period_charges = [c for c in self._charges if c.charge_period.startswith(str(year))]
        total_kwh = sum(c.consumption_kwh for c in period_charges)
        total_gbp = sum(c.total_charge_gbp for c in period_charges)
        return round(total_gbp / total_kwh * 100, 4) if total_kwh > 0 else 0.0

    def hv_customer_count(self) -> int:
        return len({c.account_id for c in self._charges if c.is_hv})

    def duos_summary(self, year: Optional[int] = None) -> dict:
        return {
            "total_charges": len(self._charges),
            "total_charged_gbp": self.total_charged_gbp(year),
            "hv_customers": self.hv_customer_count(),
            "annual_unit_cost_p_per_kwh": self.annual_unit_cost_p_per_kwh(year) if year else None,
        }
