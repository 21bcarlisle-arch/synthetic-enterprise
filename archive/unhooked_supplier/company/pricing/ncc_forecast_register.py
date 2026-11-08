"""Non-Commodity Cost (NCC) Forecast Register (Phase GW).

Non-commodity costs (NCCs) are levies and network charges that suppliers
pass through to customers alongside the commodity (gas/electricity) cost.
They represent ~40-50% of a domestic customer's total electricity bill.

NCC components (approximate 2024 proportions of domestic electricity bill):
  BSUOS: Balancing Services Use of System; operator BSC; ~5% of bill
  TNUOS: Transmission network charge; NGET; ~12% of bill (triad-exposed)
  DUOS: Distribution Use of System; DNO; ~18% of bill
  CM: Capacity Market levy; NESO; ~3% of bill
  CFD: Contracts for Difference levy; LCCC; ~1-2% of bill
  RO: Renewables Obligation; Ofgem; ~7% of bill
  FIT: Feed-in Tariff; Ofgem; ~1% of bill (legacy)
  GGL: Green Gas Levy; Ofgem; small and growing
  WHD: Warm Home Discount levy; Ofgem; ~£10/customer flat
  CCL: Climate Change Levy; HMRC; excluded for CCA holders

Gas NCCs are simpler: principally TNUoS (gas transmission), UNC transport,
and Green Gas Levy. Gas has no ROC/CfD/CM/FiT equivalent.

A supplier must forecast these costs for each forthcoming tariff period
to set a tariff that covers them. Under-estimation led to many 2021-22
failures (NCC errors of 30-50% in one quarter).

Distinct from: bsuos_ledger.py (actuals), tnuos_ledger.py (actuals),
duos_ledger.py (actuals). This register tracks FORECASTS used for pricing.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

_PENCE_PER_KWH = "p/kWh"
_POUNDS_PER_CUSTOMER = "GBP/customer/year"


class NCCComponent(str, Enum):
    BSUOS = "bsuos"
    TNUOS = "tnuos"
    DUOS = "duos"
    CM = "capacity_market"
    CFD = "cfd_levy"
    RO = "renewables_obligation"
    FIT = "fit_levy"
    GGL = "green_gas_levy"
    WHD = "whd_levy"
    CCL = "ccl"
    OTHER = "other"


class Fuel(str, Enum):
    ELECTRICITY = "electricity"
    GAS = "gas"


_GAS_APPLICABLE = frozenset({NCCComponent.TNUOS, NCCComponent.GGL, NCCComponent.OTHER})
_ELECTRICITY_ONLY = frozenset({
    NCCComponent.BSUOS, NCCComponent.CM, NCCComponent.CFD,
    NCCComponent.RO, NCCComponent.FIT,
})


@dataclass(frozen=True)
class NCCForecastRecord:
    record_id: str
    period_start: dt.date
    period_end: dt.date
    component: NCCComponent
    fuel: Fuel
    unit_rate: float
    unit_label: str
    source: str = ""
    forecast_date: Optional[dt.date] = None
    notes: str = ""

    @property
    def period_months(self) -> int:
        return (
            (self.period_end.year - self.period_start.year) * 12
            + (self.period_end.month - self.period_start.month)
        )

    def is_applicable_for_fuel(self) -> bool:
        if self.fuel == Fuel.GAS and self.component in _ELECTRICITY_ONLY:
            return False
        return True

    def annual_cost_per_customer_gbp(self, annual_kwh: float = 3100.0) -> float:
        if self.unit_label == _PENCE_PER_KWH:
            return round(annual_kwh * self.unit_rate / 100.0, 2)
        if self.unit_label == _POUNDS_PER_CUSTOMER:
            return round(self.unit_rate, 2)
        return 0.0

    def ncc_summary(self) -> str:
        return (
            "NCC " + self.record_id + " [" + self.fuel.value + "/" + self.component.value + "]"
            + " period=" + str(self.period_start) + "→" + str(self.period_end)
            + " rate=" + str(self.unit_rate) + " " + self.unit_label
        )


class NCCForecastRegister:

    def __init__(self) -> None:
        self._records: List[NCCForecastRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "NCC-FC-" + str(self._counter).zfill(5)

    def add_forecast(
        self,
        period_start: dt.date,
        period_end: dt.date,
        component: NCCComponent,
        fuel: Fuel,
        unit_rate: float,
        unit_label: str,
        source: str = "",
        forecast_date: Optional[dt.date] = None,
        notes: str = "",
    ) -> NCCForecastRecord:
        if period_end <= period_start:
            raise ValueError("period_end must be after period_start")
        if unit_rate < 0:
            raise ValueError("unit_rate must be non-negative")
        record = NCCForecastRecord(
            record_id=self._next_id(), period_start=period_start, period_end=period_end,
            component=component, fuel=fuel, unit_rate=unit_rate, unit_label=unit_label,
            source=source, forecast_date=forecast_date, notes=notes,
        )
        self._records.append(record)
        return record

    def forecasts_for_period(self, period_start: dt.date, fuel: Fuel) -> List[NCCForecastRecord]:
        return [r for r in self._records if r.period_start == period_start and r.fuel == fuel]

    def by_component(self, component: NCCComponent) -> List[NCCForecastRecord]:
        return [r for r in self._records if r.component == component]

    def total_ncc_pence_per_kwh(
        self, period_start: dt.date, fuel: Fuel,
    ) -> float:
        total = 0.0
        for r in self.forecasts_for_period(period_start, fuel):
            if r.unit_label == _PENCE_PER_KWH:
                total += r.unit_rate
        return round(total, 4)

    def total_annual_ncc_per_customer_gbp(
        self, period_start: dt.date, fuel: Fuel, annual_kwh: float = 3100.0,
    ) -> float:
        return round(
            sum(
                r.annual_cost_per_customer_gbp(annual_kwh)
                for r in self.forecasts_for_period(period_start, fuel)
            ),
            2,
        )

    def components_without_forecast(
        self, period_start: dt.date, fuel: Fuel,
    ) -> List[NCCComponent]:
        covered = {r.component for r in self.forecasts_for_period(period_start, fuel)}
        if fuel == Fuel.GAS:
            expected = _GAS_APPLICABLE
        else:
            expected = set(NCCComponent) - {NCCComponent.GGL}
        return [c for c in expected if c not in covered]

    def distinct_periods(self) -> List[dt.date]:
        return list(dict.fromkeys(r.period_start for r in self._records))

    def ncc_forecast_summary(self, period_start: dt.date, fuel: Fuel) -> str:
        n = len(self.forecasts_for_period(period_start, fuel))
        total_p_kwh = self.total_ncc_pence_per_kwh(period_start, fuel)
        return (
            "NCC Forecast [" + fuel.value + " " + str(period_start) + "]: "
            + str(n) + " components. "
            + str(total_p_kwh) + "p/kWh total NCC."
        )
