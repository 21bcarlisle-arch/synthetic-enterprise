from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# TNUoS (Transmission Network Use of System) residual tariff £/kW/year by year
# Triad demand periods set annual capacity cost; values are representative national average
_TNUOS_RESIDUAL_P_PER_KWH: dict[int, float] = {
    2016: 0.68, 2017: 0.72, 2018: 0.76, 2019: 0.80,
    2020: 0.88, 2021: 0.92, 2022: 1.05, 2023: 1.18, 2024: 1.25, 2025: 1.32,
}

# TNUoS Triad-related locational charge (£/kW/year for Triad MW)
_TNUOS_TRIAD_ZONE_FACTOR: dict[str, float] = {
    "north": 1.20,   # Scotland/Northern — remote from demand
    "south": 0.85,   # South England — close to demand
    "midlands": 1.00,
    "london": 0.90,
}


class TriadStatus(str, Enum):
    TRIAD = "triad"
    NEAR_MISS = "near_miss"
    NORMAL = "normal"


@dataclass(frozen=True)
class TNUoSCharge:
    account_id: str
    charge_year: int
    consumption_kwh: float
    residual_rate_p_per_kwh: float
    triad_demand_kw: float
    triad_rate_gbp_per_kw: float
    zone: str = "midlands"

    @property
    def residual_charge_gbp(self) -> float:
        return round(self.consumption_kwh * self.residual_rate_p_per_kwh / 100, 2)

    @property
    def triad_charge_gbp(self) -> float:
        return round(self.triad_demand_kw * self.triad_rate_gbp_per_kw, 2)

    @property
    def total_charge_gbp(self) -> float:
        return round(self.residual_charge_gbp + self.triad_charge_gbp, 2)


@dataclass(frozen=True)
class TriadHalfHour:
    settlement_date: str
    settlement_period: int
    demand_kw: float
    status: TriadStatus


class TNUoSLedger:
    def __init__(self) -> None:
        self._charges: list[TNUoSCharge] = []
        self._triad_hhs: list[TriadHalfHour] = []

    @staticmethod
    def residual_rate_for_year(year: int) -> float:
        return _TNUOS_RESIDUAL_P_PER_KWH.get(year, 1.00)

    @staticmethod
    def zone_factor(zone: str) -> float:
        return _TNUOS_TRIAD_ZONE_FACTOR.get(zone.lower(), 1.00)

    def record_charge(self, charge: TNUoSCharge) -> TNUoSCharge:
        self._charges.append(charge)
        return charge

    def record_triad_hh(self, hh: TriadHalfHour) -> TriadHalfHour:
        self._triad_hhs.append(hh)
        return hh

    def charges_for_year(self, year: int) -> list[TNUoSCharge]:
        return [c for c in self._charges if c.charge_year == year]

    def total_charged_gbp(self, year: Optional[int] = None) -> float:
        charges = self.charges_for_year(year) if year else self._charges
        return round(sum(c.total_charge_gbp for c in charges), 2)

    def triad_half_hours(self, year: Optional[int] = None) -> list[TriadHalfHour]:
        if year:
            # Triad periods are in the settlement year Nov-Feb window
            return [h for h in self._triad_hhs
                    if h.settlement_date.startswith(str(year)) or
                    h.settlement_date.startswith(str(year - 1))]
        return list(self._triad_hhs)

    def confirmed_triads(self) -> list[TriadHalfHour]:
        return [h for h in self._triad_hhs if h.status == TriadStatus.TRIAD]

    def tnuos_summary(self, year: Optional[int] = None) -> dict:
        return {
            "total_accounts": len({c.account_id for c in self._charges}),
            "total_charged_gbp": self.total_charged_gbp(year),
            "confirmed_triads": len(self.confirmed_triads()),
        }
