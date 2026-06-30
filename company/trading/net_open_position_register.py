"""Net open position register — tracks hedged vs unhedged retail commitment.

A UK energy supplier's net open position is:
  NOP = retail commitment (MWh) - forward purchase (MWh)

A negative NOP (retail > forwards) = long retail, short market = bearish risk.
A positive NOP (forwards > retail) = overhedged = wasteful capital deployment.

Ofgem's FRA framework uses NOP as a key risk metric. During 2022, suppliers
with large long-retail / short-market positions faced catastrophic losses
when wholesale prices spiked.

UK market convention: NOP is computed per delivery period (monthly/quarterly)
and aggregated across all settlement locations (zones/nodes for gas,
half-hourly settlement for electricity).

Epistemic constraint: the company reads its own trade blotter (forward positions)
and customer register (estimated retail commitment). It does NOT read the sim's
forward curve or settlement internals.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ExposureDirection(str, Enum):
    LONG_RETAIL = "long_retail"     # More retail than hedges: bear market risk
    OVERHEDGED = "overhedged"       # More hedges than retail: forward mark-to-market risk
    FLAT = "flat"                   # Within tolerance


class NOPSeverity(str, Enum):
    GREEN = "GREEN"    # NOP within policy limits
    AMBER = "AMBER"    # NOP approaching limits
    RED = "RED"        # NOP breaches policy limits


_FLAT_TOLERANCE_PCT = 5.0   # ±5% = FLAT
_AMBER_THRESHOLD_PCT = 20.0  # >20% exposure = AMBER
_RED_THRESHOLD_PCT = 40.0    # >40% exposure = RED


@dataclass(frozen=True)
class DeliveryPeriodPosition:
    delivery_year: int
    delivery_quarter: int   # 1-4
    commodity: str          # "electricity" or "gas"
    retail_commitment_mwh: float
    forward_position_mwh: float

    @property
    def net_open_position_mwh(self) -> float:
        """Positive = overhedged; negative = long retail (underhedged)."""
        return self.forward_position_mwh - self.retail_commitment_mwh

    @property
    def nop_pct_of_retail(self) -> float:
        """NOP as % of retail commitment. Negative = underhedged."""
        if self.retail_commitment_mwh == 0:
            return 0.0
        return self.net_open_position_mwh / self.retail_commitment_mwh * 100

    @property
    def hedge_fraction_pct(self) -> float:
        """Forward position as % of retail commitment."""
        if self.retail_commitment_mwh == 0:
            return 0.0
        return self.forward_position_mwh / self.retail_commitment_mwh * 100

    @property
    def direction(self) -> ExposureDirection:
        abs_pct = abs(self.nop_pct_of_retail)
        if abs_pct <= _FLAT_TOLERANCE_PCT:
            return ExposureDirection.FLAT
        if self.net_open_position_mwh < 0:
            return ExposureDirection.LONG_RETAIL
        return ExposureDirection.OVERHEDGED

    @property
    def severity(self) -> NOPSeverity:
        abs_pct = abs(self.nop_pct_of_retail)
        if abs_pct >= _RED_THRESHOLD_PCT:
            return NOPSeverity.RED
        if abs_pct >= _AMBER_THRESHOLD_PCT:
            return NOPSeverity.AMBER
        return NOPSeverity.GREEN


class NetOpenPositionRegister:
    """Tracks NOP across all delivery periods and commodities."""

    def __init__(self) -> None:
        self._positions: list[DeliveryPeriodPosition] = []

    def record(
        self,
        delivery_year: int,
        delivery_quarter: int,
        commodity: str,
        retail_commitment_mwh: float,
        forward_position_mwh: float,
    ) -> DeliveryPeriodPosition:
        pos = DeliveryPeriodPosition(
            delivery_year=delivery_year,
            delivery_quarter=delivery_quarter,
            commodity=commodity,
            retail_commitment_mwh=retail_commitment_mwh,
            forward_position_mwh=forward_position_mwh,
        )
        self._positions.append(pos)
        return pos

    @property
    def all_positions(self) -> list[DeliveryPeriodPosition]:
        return sorted(self._positions, key=lambda p: (p.delivery_year, p.delivery_quarter, p.commodity))

    def positions_for_year(self, year: int) -> list[DeliveryPeriodPosition]:
        return [p for p in self._positions if p.delivery_year == year]

    def positions_for_commodity(self, commodity: str) -> list[DeliveryPeriodPosition]:
        return [p for p in self._positions if p.commodity == commodity]

    @property
    def red_positions(self) -> list[DeliveryPeriodPosition]:
        return [p for p in self._positions if p.severity == NOPSeverity.RED]

    @property
    def long_retail_positions(self) -> list[DeliveryPeriodPosition]:
        return [p for p in self._positions if p.direction == ExposureDirection.LONG_RETAIL]

    @property
    def overhedged_positions(self) -> list[DeliveryPeriodPosition]:
        return [p for p in self._positions if p.direction == ExposureDirection.OVERHEDGED]

    def aggregate_for_year(self, year: int) -> dict[str, float]:
        """Total retail commitment, forwards, NOP for the year."""
        positions = self.positions_for_year(year)
        return {
            "retail_mwh": sum(p.retail_commitment_mwh for p in positions),
            "forward_mwh": sum(p.forward_position_mwh for p in positions),
            "nop_mwh": sum(p.net_open_position_mwh for p in positions),
            "n_periods": len(positions),
        }

    def nop_summary(self) -> str:
        n = len(self._positions)
        red = len(self.red_positions)
        long_retail = len(self.long_retail_positions)
        overhedged = len(self.overhedged_positions)
        lines = [
            "Net Open Position Register",
            "Periods: {:d} | RED: {:d}".format(n, red),
            "Long retail (underhedged): {:d} | Overhedged: {:d}".format(long_retail, overhedged),
        ]
        return chr(10).join(lines)
