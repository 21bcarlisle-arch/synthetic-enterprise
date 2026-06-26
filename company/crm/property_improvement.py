"""Property improvement event tracker.

When domestic customers install energy efficiency measures, their EPC rating
improves, energy consumption drops, and fuel poverty risk decreases. This
module tracks individual improvement events and the resulting property upgrade.

UK energy efficiency schemes that fund improvements:
- ECO4 (Great British Insulation Scheme): cavity/solid wall insulation, boiler
  replacement for fuel-poor households.
- Boiler Upgrade Scheme (BUS): heat pump replacement (£7,500 grant 2022-2025).
- Home Upgrade Grant (HUG2): off-gas-grid homes, LA-administered.
- Smart Export Guarantee (SEG): solar PV installation.

Each measure has a defined annual energy saving (kWh) and typical cost
calibrated to BEIS/DESNZ domestic improvements data 2016-2025.

The EPC rating improvement from D→C, for example, reduces typical annual
electricity consumption by ~10% and gas by ~15% (insulation effects dominate).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class MeasureType(str, Enum):
    CAVITY_WALL_INSULATION = "cavity_wall_insulation"
    SOLID_WALL_INSULATION = "solid_wall_insulation"
    LOFT_INSULATION = "loft_insulation"
    HEAT_PUMP_AIR_SOURCE = "heat_pump_air_source"
    HEAT_PUMP_GROUND_SOURCE = "heat_pump_ground_source"
    SOLAR_PV = "solar_pv"
    SMART_METER = "smart_meter"
    BOILER_REPLACEMENT = "boiler_replacement"
    DOUBLE_GLAZING = "double_glazing"
    DRAUGHT_PROOFING = "draught_proofing"


class FundingScheme(str, Enum):
    ECO4 = "ECO4"
    BUS = "BUS"                  # Boiler Upgrade Scheme
    HUG2 = "HUG2"               # Home Upgrade Grant 2
    SEG = "SEG"                  # Smart Export Guarantee
    PRIVATE = "private"          # self-funded
    GBIS = "GBIS"                # Great British Insulation Scheme


# Annual energy saving estimates (kWh/yr) and EPC points (0-100 scale)
_MEASURE_SAVINGS: dict[str, tuple[float, float, int]] = {
    # (elec_saving_kwh, gas_saving_kwh, epc_points)
    "cavity_wall_insulation":  (0.0,    1800.0, 10),
    "solid_wall_insulation":   (0.0,    2800.0, 15),
    "loft_insulation":         (0.0,    900.0,  8),
    "heat_pump_air_source":    (0.0,    8000.0, 20),  # replaces gas boiler
    "heat_pump_ground_source": (0.0,    10000.0, 25),
    "solar_pv":                (2000.0, 0.0,    12),  # generation offset
    "smart_meter":             (150.0,  200.0,  3),
    "boiler_replacement":      (0.0,    1200.0, 8),
    "double_glazing":          (0.0,    600.0,  5),
    "draught_proofing":        (0.0,    150.0,  2),
}

# Typical grant values (£) by scheme and measure
_GRANT_VALUES: dict[tuple[str, str], float] = {
    ("ECO4", "cavity_wall_insulation"): 2500.0,
    ("ECO4", "solid_wall_insulation"): 8000.0,
    ("ECO4", "loft_insulation"): 900.0,
    ("BUS", "heat_pump_air_source"): 7500.0,
    ("BUS", "heat_pump_ground_source"): 7500.0,
    ("HUG2", "solid_wall_insulation"): 10000.0,
    ("HUG2", "heat_pump_air_source"): 10000.0,
    ("GBIS", "cavity_wall_insulation"): 1500.0,
    ("GBIS", "loft_insulation"): 600.0,
}


@dataclass(frozen=True)
class PropertyImprovement:
    customer_id: str
    uprn: str
    measure: MeasureType
    installation_date: dt.date
    funding_scheme: FundingScheme
    cost_gbp: float                  # total cost before grant
    epc_before: str                  # A-G
    epc_after: str                   # A-G

    @property
    def grant_gbp(self) -> float:
        key = (self.funding_scheme.value, self.measure.value)
        return _GRANT_VALUES.get(key, 0.0)

    @property
    def customer_cost_gbp(self) -> float:
        return round(max(0.0, self.cost_gbp - self.grant_gbp), 2)

    @property
    def annual_elec_saving_kwh(self) -> float:
        return _MEASURE_SAVINGS.get(self.measure.value, (0.0, 0.0, 0))[0]

    @property
    def annual_gas_saving_kwh(self) -> float:
        return _MEASURE_SAVINGS.get(self.measure.value, (0.0, 0.0, 0))[1]

    @property
    def epc_points_gained(self) -> int:
        return _MEASURE_SAVINGS.get(self.measure.value, (0.0, 0.0, 0))[2]

    @property
    def simple_payback_years(self) -> Optional[float]:
        """Years to recoup customer cost at average UK energy price (£0.28/kWh elec, £0.07/kWh gas)."""
        total_saving = (self.annual_elec_saving_kwh * 0.28
                        + self.annual_gas_saving_kwh * 0.07)
        if total_saving <= 0 or self.customer_cost_gbp <= 0:
            return None
        return round(self.customer_cost_gbp / total_saving, 1)


class PropertyImprovementBook:
    """Track property improvement events across the customer portfolio."""

    def __init__(self) -> None:
        self._improvements: List[PropertyImprovement] = []

    def record_improvement(
        self,
        customer_id: str,
        uprn: str,
        measure: MeasureType,
        installation_date: dt.date,
        funding_scheme: FundingScheme,
        cost_gbp: float,
        epc_before: str,
        epc_after: str,
    ) -> PropertyImprovement:
        imp = PropertyImprovement(
            customer_id=customer_id, uprn=uprn, measure=measure,
            installation_date=installation_date, funding_scheme=funding_scheme,
            cost_gbp=cost_gbp, epc_before=epc_before, epc_after=epc_after,
        )
        self._improvements.append(imp)
        return imp

    def for_customer(self, customer_id: str) -> List[PropertyImprovement]:
        return [i for i in self._improvements if i.customer_id == customer_id]

    def annual_improvements(self, year: int) -> List[PropertyImprovement]:
        return [i for i in self._improvements if i.installation_date.year == year]

    def total_grant_gbp(self, year: Optional[int] = None) -> float:
        imps = self.annual_improvements(year) if year else self._improvements
        return round(sum(i.grant_gbp for i in imps), 2)

    def customers_upgraded_epc(self, year: int, to_rating: str) -> List[str]:
        """Customer IDs whose EPC reached at least `to_rating` in this year."""
        _order = list("ABCDEFG")
        return [
            i.customer_id for i in self.annual_improvements(year)
            if _order.index(i.epc_after) <= _order.index(to_rating)
        ]

    def improvement_summary(self, year: int) -> dict:
        year_imps = self.annual_improvements(year)
        total_elec = sum(i.annual_elec_saving_kwh for i in year_imps)
        total_gas = sum(i.annual_gas_saving_kwh for i in year_imps)
        by_scheme: dict[str, int] = {}
        for i in year_imps:
            by_scheme[i.funding_scheme.value] = by_scheme.get(i.funding_scheme.value, 0) + 1
        return {
            "year": year,
            "total_measures": len(year_imps),
            "unique_customers": len({i.customer_id for i in year_imps}),
            "total_grant_gbp": self.total_grant_gbp(year),
            "annual_elec_saving_kwh": round(total_elec, 0),
            "annual_gas_saving_kwh": round(total_gas, 0),
            "by_funding_scheme": by_scheme,
        }
