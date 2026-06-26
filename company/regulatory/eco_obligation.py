from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

_ECO_OBLIGATION_COST_PER_MWH: dict[str, float] = {
    "ECO2": 3.20, "ECO3": 4.50, "ECO4": 6.80,
}
_ECO_PHASE_YEARS: dict[str, tuple[int, int]] = {
    "ECO2": (2015, 2018),
    "ECO3": (2018, 2022),
    "ECO4": (2022, 2026),
}


class ECOPhase(str, Enum):
    ECO2 = "ECO2"
    ECO3 = "ECO3"
    ECO4 = "ECO4"


class MeasureCategory(str, Enum):
    INSULATION = "insulation"
    HEATING = "heating"
    SMART_CONTROLS = "smart_controls"
    RENEWABLES = "renewables"


@dataclass(frozen=True)
class ECODelivery:
    delivery_id: str
    phase: ECOPhase
    delivery_year: int
    customer_id: str
    category: MeasureCategory
    co2_saved_tonnes: float
    cost_gbp: float
    is_fuel_poor: bool

    @property
    def cost_per_tonne_co2(self) -> float:
        return round(self.cost_gbp / self.co2_saved_tonnes, 2) if self.co2_saved_tonnes > 0 else 0.0


class ECOObligationBook:
    def __init__(self, annual_electricity_supplied_mwh: float = 50_000.0) -> None:
        self._deliveries: list[ECODelivery] = []
        self.annual_electricity_supplied_mwh = annual_electricity_supplied_mwh

    def record_delivery(self, delivery: ECODelivery) -> ECODelivery:
        self._deliveries.append(delivery)
        return delivery

    def deliveries_for_phase(self, phase: ECOPhase) -> list[ECODelivery]:
        return [d for d in self._deliveries if d.phase == phase]

    def deliveries_for_year(self, year: int) -> list[ECODelivery]:
        return [d for d in self._deliveries if d.delivery_year == year]

    def total_co2_saved_tonnes(self, phase: Optional[ECOPhase] = None) -> float:
        dels = self.deliveries_for_phase(phase) if phase else self._deliveries
        return round(sum(d.co2_saved_tonnes for d in dels), 2)

    def total_cost_gbp(self, phase: Optional[ECOPhase] = None) -> float:
        dels = self.deliveries_for_phase(phase) if phase else self._deliveries
        return round(sum(d.cost_gbp for d in dels), 2)

    def estimated_annual_obligation_gbp(self, phase: ECOPhase) -> float:
        rate = _ECO_OBLIGATION_COST_PER_MWH.get(phase.value, 5.0)
        return round(self.annual_electricity_supplied_mwh * rate, 2)

    def fuel_poor_delivery_pct(self) -> float:
        if not self._deliveries:
            return 0.0
        return round(sum(1 for d in self._deliveries if d.is_fuel_poor) / len(self._deliveries) * 100, 2)

    def eco_summary(self) -> dict:
        return {
            "total_deliveries": len(self._deliveries),
            "total_co2_saved_tonnes": self.total_co2_saved_tonnes(),
            "total_cost_gbp": self.total_cost_gbp(),
            "fuel_poor_delivery_pct": self.fuel_poor_delivery_pct(),
            "eco4_estimated_annual_gbp": self.estimated_annual_obligation_gbp(ECOPhase.ECO4),
        }
