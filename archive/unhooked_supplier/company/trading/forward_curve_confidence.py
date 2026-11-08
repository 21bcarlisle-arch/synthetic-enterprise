"""Forward Curve Confidence Band (Phase ET).

The company builds forward price curves for electricity and gas to:
- Price tariffs in advance
- Guide hedging decisions
- Stress-test profitability

But forward curves are not forecasts — they are market prices for future delivery.
As delivery approaches, the curve narrows (less uncertainty). The confidence band
quantifies how wide the plausible range is at each tenor.

Key inputs:
- Front-month: tight band (market liquidity, clear price discovery)
- Q+1 to Q+4: moderate band (seasonal patterns predictable)
- Season+: wide band (fundamentals dominate, less liquidity)
- 2+ years: very wide (macro uncertainty, weather normals only)

Confidence bands are used to:
1. Set tariff buffer margins (ensure profitability across band)
2. Determine maximum contract tenure the company will offer
3. Show the board scenario range on profitability projections
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TenorBand(str, Enum):
    FRONT_MONTH = "front_month"         # 0-1 months forward
    NEAR_QUARTER = "near_quarter"       # 1-6 months
    FAR_QUARTER = "far_quarter"         # 6-12 months
    NEAR_SEASONAL = "near_seasonal"     # 1-2 years
    FAR_SEASONAL = "far_seasonal"       # 2+ years


# Confidence intervals by tenor (pct of base price, 80% confidence interval)
_CONFIDENCE_INTERVAL_PCT = {
    TenorBand.FRONT_MONTH: 5.0,
    TenorBand.NEAR_QUARTER: 12.0,
    TenorBand.FAR_QUARTER: 20.0,
    TenorBand.NEAR_SEASONAL: 30.0,
    TenorBand.FAR_SEASONAL: 45.0,
}


def _tenor_band(months_forward: int) -> TenorBand:
    if months_forward <= 1:
        return TenorBand.FRONT_MONTH
    if months_forward <= 6:
        return TenorBand.NEAR_QUARTER
    if months_forward <= 12:
        return TenorBand.FAR_QUARTER
    if months_forward <= 24:
        return TenorBand.NEAR_SEASONAL
    return TenorBand.FAR_SEASONAL


@dataclass(frozen=True)
class ForwardCurvePoint:
    delivery_date: dt.date
    as_of_date: dt.date
    fuel: str
    mid_price_gbp_per_mwh: float
    source: str = "market"  # "market" or "extrapolated"

    @property
    def months_forward(self) -> int:
        delta = (self.delivery_date.year - self.as_of_date.year) * 12
        delta += self.delivery_date.month - self.as_of_date.month
        return max(0, delta)

    @property
    def tenor_band(self) -> TenorBand:
        return _tenor_band(self.months_forward)

    @property
    def confidence_interval_pct(self) -> float:
        return _CONFIDENCE_INTERVAL_PCT[self.tenor_band]

    @property
    def lower_band_gbp_per_mwh(self) -> float:
        return self.mid_price_gbp_per_mwh * (1 - self.confidence_interval_pct / 100)

    @property
    def upper_band_gbp_per_mwh(self) -> float:
        return self.mid_price_gbp_per_mwh * (1 + self.confidence_interval_pct / 100)

    @property
    def band_width_gbp_per_mwh(self) -> float:
        return self.upper_band_gbp_per_mwh - self.lower_band_gbp_per_mwh

    @property
    def is_extrapolated(self) -> bool:
        return self.source == "extrapolated"

    def point_summary(self) -> str:
        return (
            self.fuel + " " + str(self.delivery_date) + ": "
            "mid=" + str(round(self.mid_price_gbp_per_mwh, 2)) + " "
            "band=[" + str(round(self.lower_band_gbp_per_mwh, 2)) + "-"
            + str(round(self.upper_band_gbp_per_mwh, 2)) + "] "
            "(" + self.tenor_band.value + " ±" + str(self.confidence_interval_pct) + "%)"
        )


class ForwardCurveConfidenceBand:

    def __init__(self) -> None:
        self._points: List[ForwardCurvePoint] = []

    def add_point(self, point: ForwardCurvePoint) -> ForwardCurvePoint:
        self._points.append(point)
        return point

    def points_for_fuel(self, fuel: str) -> List[ForwardCurvePoint]:
        return sorted(
            [p for p in self._points if p.fuel == fuel],
            key=lambda p: p.delivery_date
        )

    def points_in_band(self, band: TenorBand) -> List[ForwardCurvePoint]:
        return [p for p in self._points if p.tenor_band == band]

    def extrapolated_points(self) -> List[ForwardCurvePoint]:
        return [p for p in self._points if p.is_extrapolated]

    def max_confidence_interval_pct(self, fuel: str) -> float:
        pts = self.points_for_fuel(fuel)
        if not pts:
            return 0.0
        return max(p.confidence_interval_pct for p in pts)

    def band_summary(self, as_of: dt.date) -> str:
        n = len(self._points)
        n_extrap = len(self.extrapolated_points())
        fuels = list(dict.fromkeys(p.fuel for p in self._points))
        return (
            "Forward Curve Confidence (" + str(as_of) + "): "
            + str(n) + " points across " + str(len(fuels)) + " fuel(s). "
            + str(n_extrap) + " extrapolated."
        )
