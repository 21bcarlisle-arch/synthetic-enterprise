from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class PositionDirection(str, Enum):
    LONG = 'long'    # hedged more than forecast
    SHORT = 'short'  # hedged less than forecast
    FLAT = 'flat'    # within tolerance


class CommodityType(str, Enum):
    ELECTRICITY = 'electricity'
    GAS = 'gas'


_FLAT_TOLERANCE_PCT = 5.0


@dataclass(frozen=True)
class EnergyPosition:
    commodity: CommodityType
    year: int
    forecast_customer_load_mwh: float
    hedged_mwh: float
    hedge_ratio_pct: float

    @property
    def net_position_mwh(self) -> float:
        return round(self.hedged_mwh - self.forecast_customer_load_mwh, 2)

    @property
    def direction(self) -> PositionDirection:
        ratio = self.hedge_ratio_pct
        if ratio < (100.0 - _FLAT_TOLERANCE_PCT):
            return PositionDirection.SHORT
        if ratio > (100.0 + _FLAT_TOLERANCE_PCT):
            return PositionDirection.LONG
        return PositionDirection.FLAT

    @property
    def is_within_policy(self) -> bool:
        return self.direction == PositionDirection.FLAT


@dataclass(frozen=True)
class PortfolioEnergyPosition:
    year: int
    electricity: EnergyPosition
    gas: EnergyPosition

    @property
    def is_fully_hedged(self) -> bool:
        return (
            self.electricity.direction == PositionDirection.FLAT and
            self.gas.direction == PositionDirection.FLAT
        )

    def summary(self) -> dict:
        return {
            'year': self.year,
            'electricity_forecast_mwh': self.electricity.forecast_customer_load_mwh,
            'electricity_hedged_mwh': self.electricity.hedged_mwh,
            'electricity_direction': self.electricity.direction.value,
            'electricity_net_mwh': self.electricity.net_position_mwh,
            'gas_forecast_mwh': self.gas.forecast_customer_load_mwh,
            'gas_hedged_mwh': self.gas.hedged_mwh,
            'gas_direction': self.gas.direction.value,
            'gas_net_mwh': self.gas.net_position_mwh,
            'is_fully_hedged': self.is_fully_hedged,
        }


def compute_energy_position(
    commodity: CommodityType,
    year: int,
    forecast_customer_load_mwh: float,
    hedged_mwh: float,
) -> EnergyPosition:
    hedge_ratio = round(hedged_mwh / forecast_customer_load_mwh * 100, 2) if forecast_customer_load_mwh > 0 else 0.0
    return EnergyPosition(
        commodity=commodity,
        year=year,
        forecast_customer_load_mwh=forecast_customer_load_mwh,
        hedged_mwh=hedged_mwh,
        hedge_ratio_pct=hedge_ratio,
    )
