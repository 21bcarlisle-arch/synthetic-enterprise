"""Seasonal demand forecast: portfolio-level load profile for hedging decisions."""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class Season(str, Enum):
    WINTER = 'winter'  # Nov-Mar
    SUMMER = 'summer'  # Apr-Oct


class DemandScenario(str, Enum):
    BASE = 'base'
    HIGH = 'high'
    LOW = 'low'


_SEASONAL_INDEX: Dict[int, float] = {
    1: 1.35, 2: 1.25, 3: 1.10,
    4: 0.90, 5: 0.85, 6: 0.80,
    7: 0.80, 8: 0.80, 9: 0.85,
    10: 0.95, 11: 1.15, 12: 1.30,
}

_SCENARIO_MULTIPLIER: Dict[DemandScenario, float] = {
    DemandScenario.BASE: 1.0,
    DemandScenario.HIGH: 1.15,
    DemandScenario.LOW: 0.85,
}


def get_season(month: int) -> Season:
    return Season.WINTER if month in (11, 12, 1, 2, 3) else Season.SUMMER


@dataclass(frozen=True)
class MonthlyDemandForecast:
    year: int
    month: int
    commodity: str
    base_mwh: float
    scenario: DemandScenario = DemandScenario.BASE

    @property
    def season(self) -> Season:
        return get_season(self.month)

    @property
    def seasonal_index(self) -> float:
        return _SEASONAL_INDEX.get(self.month, 1.0)

    @property
    def forecast_mwh(self) -> float:
        return round(
            self.base_mwh
            * self.seasonal_index
            * _SCENARIO_MULTIPLIER[self.scenario],
            1
        )


class SeasonalDemandModel:
    def __init__(self) -> None:
        self._forecasts: List[MonthlyDemandForecast] = []

    def set_monthly_forecast(self, year: int, month: int, commodity: str,
                               base_mwh: float,
                               scenario: DemandScenario = DemandScenario.BASE
                               ) -> MonthlyDemandForecast:
        f = MonthlyDemandForecast(
            year=year, month=month, commodity=commodity,
            base_mwh=base_mwh, scenario=scenario,
        )
        self._forecasts.append(f)
        return f

    def get_month(self, year: int, month: int,
                    commodity: str) -> Optional[MonthlyDemandForecast]:
        return next(
            (f for f in self._forecasts
             if f.year == year and f.month == month
             and f.commodity == commodity),
            None,
        )

    def annual_demand_mwh(self, year: int, commodity: str) -> float:
        return round(sum(
            f.forecast_mwh for f in self._forecasts
            if f.year == year and f.commodity == commodity
        ), 1)

    def seasonal_demand_mwh(self, year: int, commodity: str, season: Season) -> float:
        return round(sum(
            f.forecast_mwh for f in self._forecasts
            if f.year == year and f.commodity == commodity
            and f.season == season
        ), 1)

    def peak_month(self, year: int, commodity: str) -> Optional[MonthlyDemandForecast]:
        months = [f for f in self._forecasts
                   if f.year == year and f.commodity == commodity]
        if not months:
            return None
        return max(months, key=lambda f: f.forecast_mwh)

    def winter_summer_ratio(self, year: int, commodity: str) -> Optional[float]:
        winter = self.seasonal_demand_mwh(year, commodity, Season.WINTER)
        summer = self.seasonal_demand_mwh(year, commodity, Season.SUMMER)
        if summer == 0:
            return None
        return round(winter / summer, 2)

    def demand_summary(self, year: int) -> dict:
        commodities = list(set(f.commodity for f in self._forecasts
                               if f.year == year))
        return {
            'year': year,
            'total_months': len([f for f in self._forecasts if f.year == year]),
            'by_commodity': {c: self.annual_demand_mwh(year, c) for c in commodities},
            'winter_summer_ratio': {
                c: self.winter_summer_ratio(year, c) for c in commodities
            },
        }
