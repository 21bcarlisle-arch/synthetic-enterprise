"""Flexible asset dispatch: battery/pump storage for BM and triad avoidance."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class AssetType(str, Enum):
    BATTERY_STORAGE = 'battery_storage'
    PUMP_STORAGE = 'pump_storage'
    FLYWHEEL = 'flywheel'
    DEMAND_RESPONSE = 'demand_response'


class DispatchMode(str, Enum):
    CHARGE = 'charge'
    DISCHARGE = 'discharge'
    STANDBY = 'standby'


@dataclass(frozen=True)
class AssetDispatchInterval:
    settlement_date: dt.date
    settlement_period: int
    mode: DispatchMode
    power_mw: float
    price_achieved_gbp_per_mwh: float

    @property
    def energy_mwh(self) -> float:
        return round(self.power_mw * 0.5, 3)

    @property
    def revenue_gbp(self) -> float:
        if self.mode == DispatchMode.CHARGE:
            return round(-self.energy_mwh * self.price_achieved_gbp_per_mwh, 2)
        if self.mode == DispatchMode.DISCHARGE:
            return round(self.energy_mwh * self.price_achieved_gbp_per_mwh, 2)
        return 0.0

    @property
    def is_evening_peak(self) -> bool:
        return 33 <= self.settlement_period <= 40


@dataclass
class FlexibleAsset:
    asset_id: str
    asset_type: AssetType
    capacity_mw: float
    storage_mwh: float
    roundtrip_efficiency_pct: float = 85.0
    current_soc_mwh: float = 0.0
    dispatch_history: List[AssetDispatchInterval] = field(default_factory=list)

    @property
    def soc_pct(self) -> float:
        return round(self.current_soc_mwh / self.storage_mwh * 100, 1)

    @property
    def can_charge(self) -> bool:
        return self.current_soc_mwh < self.storage_mwh * 0.99

    @property
    def can_discharge(self) -> bool:
        return self.current_soc_mwh > 0.01

    def dispatch(self, settlement_date: dt.date, period: int,
                   mode: DispatchMode, power_mw: float,
                   price_gbp_per_mwh: float) -> AssetDispatchInterval:
        interval = AssetDispatchInterval(
            settlement_date=settlement_date, settlement_period=period,
            mode=mode, power_mw=power_mw,
            price_achieved_gbp_per_mwh=price_gbp_per_mwh,
        )
        energy = interval.energy_mwh
        if mode == DispatchMode.CHARGE:
            effective_energy = energy * self.roundtrip_efficiency_pct / 100
            self.current_soc_mwh = min(
                self.storage_mwh,
                self.current_soc_mwh + effective_energy,
            )
        elif mode == DispatchMode.DISCHARGE:
            self.current_soc_mwh = max(0.0, self.current_soc_mwh - energy)
        self.dispatch_history.append(interval)
        return interval

    def total_revenue_gbp(self, year: int) -> float:
        return round(sum(
            i.revenue_gbp for i in self.dispatch_history
            if i.settlement_date.year == year
        ), 2)

    def cycles_in_year(self, year: int) -> float:
        discharge_mwh = sum(
            i.energy_mwh for i in self.dispatch_history
            if i.settlement_date.year == year and i.mode == DispatchMode.DISCHARGE
        )
        if self.storage_mwh == 0:
            return 0.0
        return round(discharge_mwh / self.storage_mwh, 1)

    def asset_summary(self, year: int) -> dict:
        return {
            'asset_id': self.asset_id,
            'asset_type': self.asset_type.value,
            'capacity_mw': self.capacity_mw,
            'storage_mwh': self.storage_mwh,
            'current_soc_pct': self.soc_pct,
            'total_revenue_gbp': self.total_revenue_gbp(year),
            'cycles_in_year': self.cycles_in_year(year),
        }
