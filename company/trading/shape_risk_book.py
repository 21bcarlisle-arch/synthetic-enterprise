"""Wholesale Shape Risk Book (Phase EO).

Shape risk is the risk that actual customer demand profile differs from the
market shape used when buying wholesale energy. UK electricity is traded as:

1. Baseload: flat 24/7 (MW)
2. Peak: 07:00-19:00 weekdays (hours 1-12 of working day)
3. Off-peak: all other hours

A supplier who buys baseload but has customers with heavily peaking demand
is exposed to the peak/off-peak spread. In high-demand periods (cold mornings),
buying peaking power to fill the shape gap is expensive.

Similarly in gas: winter vs summer shape risk (seasonality mismatch).

This module models:
- Shape mismatch between purchased profile and customer demand profile
- Peak surplus/deficit in MW
- Financial exposure from shape mismatch at market spreads
- Weather-correlated shape events (cold spells drive demand spikes)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ShapeType(str, Enum):
    BASELOAD = "baseload"     # flat 24/7
    PEAK = "peak"             # 07:00-19:00 weekdays
    OFF_PEAK = "off_peak"     # all other hours
    CUSTOM = "custom"         # bespoke shape


class ShapeExposureDirection(str, Enum):
    LONG_PEAK = "long_peak"   # have more than needed during peak
    SHORT_PEAK = "short_peak" # need more than bought during peak
    BALANCED = "balanced"


_PEAK_DURATION_HOURS = 12.0    # 07:00-19:00 = 12 hours
_OFFPEAK_DURATION_HOURS = 12.0
_SHAPE_BALANCE_TOLERANCE_MW = 5.0  # ±5 MW considered balanced


@dataclass(frozen=True)
class ShapePosition:
    delivery_month: str   # YYYY-MM
    fuel: str             # "electricity" or "gas"
    purchased_baseload_mw: float
    expected_peak_mw: float      # customer demand during peak
    expected_offpeak_mw: float   # customer demand during off-peak
    peak_spread_gbp_per_mwh: float    # market peak premium over baseload
    offpeak_spread_gbp_per_mwh: float  # negative: off-peak discount

    @property
    def peak_surplus_mw(self) -> float:
        return self.purchased_baseload_mw - self.expected_peak_mw

    @property
    def offpeak_surplus_mw(self) -> float:
        return self.purchased_baseload_mw - self.expected_offpeak_mw

    @property
    def direction(self) -> ShapeExposureDirection:
        surplus = self.peak_surplus_mw
        if abs(surplus) <= _SHAPE_BALANCE_TOLERANCE_MW:
            return ShapeExposureDirection.BALANCED
        return ShapeExposureDirection.LONG_PEAK if surplus > 0 else ShapeExposureDirection.SHORT_PEAK

    @property
    def peak_financial_exposure_gbp(self) -> float:
        hours_in_month = 20 * _PEAK_DURATION_HOURS  # ~20 trading days/month
        mwh_delta = self.peak_surplus_mw * hours_in_month
        return mwh_delta * self.peak_spread_gbp_per_mwh

    @property
    def net_shape_pnl_gbp(self) -> float:
        hours_in_month_peak = 20 * _PEAK_DURATION_HOURS
        hours_in_month_offpeak = 20 * _OFFPEAK_DURATION_HOURS + 8 * 24  # weekends
        peak_pnl = self.peak_surplus_mw * hours_in_month_peak * self.peak_spread_gbp_per_mwh
        offpeak_pnl = self.offpeak_surplus_mw * hours_in_month_offpeak * self.offpeak_spread_gbp_per_mwh
        return peak_pnl + offpeak_pnl

    def position_summary(self) -> str:
        return (
            self.delivery_month + " " + self.fuel + ": "
            "baseload=" + str(round(self.purchased_baseload_mw, 1)) + "MW "
            "peak_surplus=" + str(round(self.peak_surplus_mw, 1)) + "MW "
            "net_shape_pnl=GBP" + str(round(self.net_shape_pnl_gbp))
        )


class ShapeRiskBook:

    def __init__(self) -> None:
        self._positions: List[ShapePosition] = []

    def record(self, position: ShapePosition) -> ShapePosition:
        self._positions.append(position)
        return position

    def positions_for_month(self, delivery_month: str) -> List[ShapePosition]:
        return [p for p in self._positions if p.delivery_month == delivery_month]

    def short_peak_positions(self) -> List[ShapePosition]:
        return [p for p in self._positions if p.direction == ShapeExposureDirection.SHORT_PEAK]

    def long_peak_positions(self) -> List[ShapePosition]:
        return [p for p in self._positions if p.direction == ShapeExposureDirection.LONG_PEAK]

    def total_net_shape_pnl_gbp(self) -> float:
        return sum(p.net_shape_pnl_gbp for p in self._positions)

    def worst_short_peak_position(self) -> Optional[ShapePosition]:
        short = self.short_peak_positions()
        if not short:
            return None
        return min(short, key=lambda p: p.peak_surplus_mw)

    def shape_risk_summary(self) -> str:
        n = len(self._positions)
        n_short = len(self.short_peak_positions())
        n_long = len(self.long_peak_positions())
        total_pnl = self.total_net_shape_pnl_gbp()
        return (
            "Shape Risk Book: " + str(n) + " positions. "
            "Short-peak: " + str(n_short) + " Long-peak: " + str(n_long) + ". "
            "Total shape P&L: GBP" + str(round(total_pnl)) + "."
        )
