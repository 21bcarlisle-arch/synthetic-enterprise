"""Wholesale Market Position Monthly Report (Phase DV).

A monthly board/management pack item for a UK energy supplier:
tracks the evolution of the wholesale hedging position vs. retail load.
Shows whether the company is long (over-hedged), short (under-hedged),
or near-flat in each delivery period.

Key metrics:
- Hedge fraction (% of retail load that is hedged)
- Net open position (NOP) in MWh and £
- Mark-to-market (MtM) P&L on open hedges
- Realised vs. budget variance on commodity cost
- Weighted average purchase price (WAPP) vs. current market price

This report runs monthly, aggregated by delivery month.
Epistemic: data comes from forward book (observable) + retail load forecast
(company estimate). Cannot read SIM settlement internals.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class HedgePosture(str, Enum):
    OVER_HEDGED = "over_hedged"        # forwards > retail load
    NEAR_FLAT = "near_flat"            # within ±5%
    UNDER_HEDGED = "under_hedged"      # forwards < retail load


class PositionRAG(str, Enum):
    GREEN = "GREEN"    # hedge fraction ≥70%
    AMBER = "AMBER"    # 40-70%
    RED = "RED"        # <40% (exposed)


_OVER_HEDGE_THRESHOLD_PCT = 5.0       # >5% over = over-hedged
_NEAR_FLAT_BAND_PCT = 5.0
_GREEN_HEDGE_FLOOR = 70.0             # ≥70% hedged
_AMBER_HEDGE_FLOOR = 40.0             # 40-70% = AMBER
_MtM_LOSS_FLAG_GBP = 50000.0         # flag MtM losses >£50k


@dataclass(frozen=True)
class DeliveryMonthPosition:
    delivery_month: dt.date             # first day of delivery month
    retail_load_mwh: float
    hedged_volume_mwh: float
    wapp_gbp_per_mwh: float             # weighted avg purchase price
    current_market_price_gbp_per_mwh: float
    fuel: str                           # ELECTRICITY or GAS

    @property
    def hedge_fraction_pct(self) -> float:
        if self.retail_load_mwh <= 0:
            return 0.0
        return self.hedged_volume_mwh / self.retail_load_mwh * 100

    @property
    def nop_mwh(self) -> float:
        return self.hedged_volume_mwh - self.retail_load_mwh

    @property
    def posture(self) -> HedgePosture:
        pct = self.hedge_fraction_pct
        if pct > 100 + _OVER_HEDGE_THRESHOLD_PCT:
            return HedgePosture.OVER_HEDGED
        if pct < 100 - _NEAR_FLAT_BAND_PCT:
            return HedgePosture.UNDER_HEDGED
        return HedgePosture.NEAR_FLAT

    @property
    def rag(self) -> PositionRAG:
        pct = self.hedge_fraction_pct
        if pct >= _GREEN_HEDGE_FLOOR:
            return PositionRAG.GREEN
        if pct >= _AMBER_HEDGE_FLOOR:
            return PositionRAG.AMBER
        return PositionRAG.RED

    @property
    def mtm_gbp(self) -> float:
        return (self.current_market_price_gbp_per_mwh - self.wapp_gbp_per_mwh) * self.hedged_volume_mwh

    @property
    def is_mtm_loss(self) -> bool:
        return self.mtm_gbp < 0

    @property
    def commodity_cost_gbp(self) -> float:
        return self.wapp_gbp_per_mwh * self.hedged_volume_mwh


class WholesalePositionReport:
    """Monthly wholesale position report aggregating delivery periods."""

    def __init__(self, report_month: dt.date, prepared_by: str = "") -> None:
        self.report_month = report_month
        self.prepared_by = prepared_by
        self._positions: List[DeliveryMonthPosition] = []

    def add_position(self, position: DeliveryMonthPosition) -> None:
        self._positions.append(position)

    def positions(self, fuel: Optional[str] = None) -> List[DeliveryMonthPosition]:
        if fuel:
            return [p for p in self._positions if p.fuel == fuel]
        return list(self._positions)

    def red_positions(self) -> List[DeliveryMonthPosition]:
        return [p for p in self._positions if p.rag == PositionRAG.RED]

    def over_hedged_positions(self) -> List[DeliveryMonthPosition]:
        return [p for p in self._positions if p.posture == HedgePosture.OVER_HEDGED]

    def total_mtm_gbp(self, fuel: Optional[str] = None) -> float:
        return sum(p.mtm_gbp for p in self.positions(fuel))

    def portfolio_hedge_fraction_pct(self, fuel: Optional[str] = None) -> float:
        pos = self.positions(fuel)
        total_load = sum(p.retail_load_mwh for p in pos)
        total_hedged = sum(p.hedged_volume_mwh for p in pos)
        if total_load <= 0:
            return 0.0
        return total_hedged / total_load * 100

    def largest_nop_position(self) -> Optional[DeliveryMonthPosition]:
        if not self._positions:
            return None
        return max(self._positions, key=lambda p: abs(p.nop_mwh))

    def report_summary(self) -> str:
        n = len(self._positions)
        n_red = len(self.red_positions())
        hedge_pct = self.portfolio_hedge_fraction_pct()
        mtm = self.total_mtm_gbp()
        mtm_sign = "profit" if mtm >= 0 else "loss"
        return (
            f"Wholesale Position Report ({self.report_month.strftime('%b %Y')}): "
            f"{n} delivery months. Portfolio hedge: {hedge_pct:.1f}%. "
            f"RED positions: {n_red}. MtM: £{abs(mtm):,.0f} {mtm_sign}."
        )
