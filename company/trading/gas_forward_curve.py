"""Wholesale Gas Forward Curve (Phase FR).

NBP (National Balancing Point) gas is traded in p/therm on the ICE exchange.
The gas forward curve provides future price expectations needed for:
1. Gas purchasing decisions (hedge or buy spot?)
2. Gas customer tariff setting (cost pass-through)
3. Gas-to-power spread analysis (when is gas-fired generation economic?)
4. Risk management: gas book VaR

Typical curve structure:
- DA (Day-Ahead): most liquid, most accurate
- Balance of Month: current month remaining
- Seasons: Summer (Apr-Sep) / Winter (Oct-Mar)
- Cal+1, Cal+2: next year, year after

Seasonality: Winter gas always priced at a premium to Summer (storage premium).
Typical winter/summer spread: 10-30% pre-crisis; up to 100%+ during crisis.

All NBP prices are publicly available via ICE/Platts/ICIS market reports.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class GasTenorBand(str, Enum):
    DAY_AHEAD = "day_ahead"
    BALANCE_OF_MONTH = "balance_of_month"
    FRONT_MONTH = "front_month"
    SUMMER = "summer"     # Apr-Sep
    WINTER = "winter"     # Oct-Mar
    CAL_PLUS_1 = "cal_plus_1"
    CAL_PLUS_2 = "cal_plus_2"


_GAS_CONFIDENCE_INTERVAL_PCT: Dict[GasTenorBand, float] = {
    GasTenorBand.DAY_AHEAD: 3.0,
    GasTenorBand.BALANCE_OF_MONTH: 5.0,
    GasTenorBand.FRONT_MONTH: 8.0,
    GasTenorBand.SUMMER: 18.0,
    GasTenorBand.WINTER: 22.0,
    GasTenorBand.CAL_PLUS_1: 35.0,
    GasTenorBand.CAL_PLUS_2: 50.0,
}

_THERMS_PER_MWH = 1.0 / 29.307


@dataclass(frozen=True)
class GasForwardPoint:
    curve_date: dt.date
    tenor_band: GasTenorBand
    mid_price_pence_per_therm: float

    @property
    def mid_price_gbp_per_mwh(self) -> float:
        return self.mid_price_pence_per_therm * _THERMS_PER_MWH * 100

    @property
    def confidence_interval_pct(self) -> float:
        return _GAS_CONFIDENCE_INTERVAL_PCT[self.tenor_band]

    @property
    def lower_band_pence(self) -> float:
        return self.mid_price_pence_per_therm * (1.0 - self.confidence_interval_pct / 100)

    @property
    def upper_band_pence(self) -> float:
        return self.mid_price_pence_per_therm * (1.0 + self.confidence_interval_pct / 100)

    @property
    def is_crisis_price(self) -> bool:
        return self.mid_price_pence_per_therm > 200.0

    def point_summary(self) -> str:
        return (
            "GasForward " + str(self.curve_date) + " " + self.tenor_band.value + ": "
            + str(round(self.mid_price_pence_per_therm, 1)) + "p/therm "
            "(" + str(round(self.mid_price_gbp_per_mwh, 2)) + " GBP/MWh) "
            "CI=±" + str(self.confidence_interval_pct) + "%"
            + (" CRISIS" if self.is_crisis_price else "")
        )


class GasForwardCurve:

    def __init__(self) -> None:
        self._points: List[GasForwardPoint] = []

    def add_point(self, point: GasForwardPoint) -> GasForwardPoint:
        self._points.append(point)
        return point

    def points_for_date(self, curve_date: dt.date) -> List[GasForwardPoint]:
        return sorted(
            [p for p in self._points if p.curve_date == curve_date],
            key=lambda p: list(GasTenorBand).index(p.tenor_band),
        )

    def latest_da_price_pence(self) -> Optional[float]:
        da_points = [p for p in self._points if p.tenor_band == GasTenorBand.DAY_AHEAD]
        if not da_points:
            return None
        return max(da_points, key=lambda p: p.curve_date).mid_price_pence_per_therm

    def winter_summer_spread(self, curve_date: dt.date) -> Optional[float]:
        day_points = {p.tenor_band: p for p in self.points_for_date(curve_date)}
        if GasTenorBand.WINTER in day_points and GasTenorBand.SUMMER in day_points:
            return (day_points[GasTenorBand.WINTER].mid_price_pence_per_therm
                    - day_points[GasTenorBand.SUMMER].mid_price_pence_per_therm)
        return None

    def crisis_points(self) -> List[GasForwardPoint]:
        return [p for p in self._points if p.is_crisis_price]

    def gas_curve_summary(self, curve_date: dt.date) -> str:
        n = len(self.points_for_date(curve_date))
        da = self.latest_da_price_pence()
        spread = self.winter_summer_spread(curve_date)
        return (
            "Gas Forward Curve (" + str(curve_date) + "): "
            + str(n) + " points. "
            + ("DA=" + str(round(da, 1)) + "p/therm. " if da else "")
            + ("W/S spread=" + str(round(spread, 1)) + "p. " if spread else "")
        )
