"""Wholesale gas OTC trading book (NBP market).

UK gas suppliers procure their gas supply via OTC (over-the-counter) trades on
the National Balancing Point (NBP) virtual gas market. These trades settle via
ICE or broker platforms. The NBP is the principal UK gas pricing benchmark.

Gas OTC trade types:
- Day-ahead: for next-gas-day delivery (most liquid, closest to spot)
- Month-ahead (M+1): next calendar month
- Season-ahead (Win/Sum): seasonal products (most liquidity for hedging)
- Within-day: same-day balancing (most expensive; reflects system balance)

Gas price units: pence per therm (p/th). 1 therm = 29.3 kWh.
At peak crisis (Aug 2022): NBP hit 600+ p/th vs 50-70 p/th normal range.

Positions track: the supplier's net purchased volume vs supply obligation.
A LONG position means more gas bought than needed (risk: prices fall).
A SHORT position means less gas bought than needed (risk: prices rise).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class GasTenor(str, Enum):
    WITHIN_DAY = "within_day"
    DAY_AHEAD = "day_ahead"
    MONTH_AHEAD = "month_ahead"
    SEASON_AHEAD = "season_ahead"


class GasTradeDirection(str, Enum):
    BUY = "buy"     # procuring gas (physical buy or financial long)
    SELL = "sell"   # selling gas (unwinding long or shorting)


class Season(str, Enum):
    SUMMER = "summer"   # Apr-Sep
    WINTER = "winter"   # Oct-Mar


_CRISIS_THRESHOLD_P_TH = 200.0   # above this = crisis-level pricing


def _season_from_month(month: int) -> Season:
    return Season.WINTER if month in (10, 11, 12, 1, 2, 3) else Season.SUMMER


@dataclass(frozen=True)
class GasOTCTrade:
    trade_id: str
    trade_date: dt.date
    delivery_date: dt.date    # start of delivery period
    tenor: GasTenor
    direction: GasTradeDirection
    volume_therms: float
    price_p_per_therm: float  # pence per therm

    @property
    def volume_mwh(self) -> float:
        return round(self.volume_therms * 0.02931, 3)   # 1 therm = 29.31 kWh

    @property
    def trade_value_gbp(self) -> float:
        value = self.volume_therms * self.price_p_per_therm / 100.0
        return round(value if self.direction == GasTradeDirection.BUY else -value, 2)

    @property
    def is_crisis_price(self) -> bool:
        return self.price_p_per_therm > _CRISIS_THRESHOLD_P_TH

    @property
    def delivery_season(self) -> Season:
        return _season_from_month(self.delivery_date.month)


class GasOTCBook:
    """Track wholesale gas OTC trades and net position."""

    def __init__(self) -> None:
        self._trades: List[GasOTCTrade] = []

    def record_trade(
        self,
        trade_id: str,
        trade_date: dt.date,
        delivery_date: dt.date,
        tenor: GasTenor,
        direction: GasTradeDirection,
        volume_therms: float,
        price_p_per_therm: float,
    ) -> GasOTCTrade:
        trade = GasOTCTrade(
            trade_id=trade_id, trade_date=trade_date, delivery_date=delivery_date,
            tenor=tenor, direction=direction, volume_therms=volume_therms,
            price_p_per_therm=price_p_per_therm,
        )
        self._trades.append(trade)
        return trade

    def trades_by_delivery_month(self, year: int, month: int) -> List[GasOTCTrade]:
        return [t for t in self._trades
                if t.delivery_date.year == year and t.delivery_date.month == month]

    def net_position_therms(
        self, delivery_date: dt.date, tenor: Optional[GasTenor] = None
    ) -> float:
        """Net long position in therms for given delivery date (positive = long)."""
        trades = [t for t in self._trades if t.delivery_date == delivery_date]
        if tenor:
            trades = [t for t in trades if t.tenor == tenor]
        net = 0.0
        for t in trades:
            if t.direction == GasTradeDirection.BUY:
                net += t.volume_therms
            else:
                net -= t.volume_therms
        return round(net, 2)

    def average_buy_price_p_th(
        self, year: int, month: int
    ) -> Optional[float]:
        """Volume-weighted average buy price for a delivery month."""
        buys = [t for t in self.trades_by_delivery_month(year, month)
                if t.direction == GasTradeDirection.BUY]
        if not buys:
            return None
        total_cost = sum(t.volume_therms * t.price_p_per_therm for t in buys)
        total_vol = sum(t.volume_therms for t in buys)
        return round(total_cost / total_vol, 2) if total_vol else None

    def crisis_trades(self) -> List[GasOTCTrade]:
        return [t for t in self._trades if t.is_crisis_price]

    def seasonal_exposure_therms(self, year: int) -> dict[str, float]:
        """Net long position (therms) by summer/winter for given delivery year."""
        exposure: dict[str, float] = {"summer": 0.0, "winter": 0.0}
        for t in self._trades:
            if t.delivery_date.year == year:
                season = t.delivery_season.value
                delta = t.volume_therms if t.direction == GasTradeDirection.BUY else -t.volume_therms
                exposure[season] = round(exposure[season] + delta, 2)
        return exposure

    def gas_book_summary(self, year: int) -> dict:
        year_trades = [t for t in self._trades if t.trade_date.year == year]
        buys = [t for t in year_trades if t.direction == GasTradeDirection.BUY]
        sells = [t for t in year_trades if t.direction == GasTradeDirection.SELL]
        crisis = [t for t in year_trades if t.is_crisis_price]
        return {
            "year": year,
            "total_trades": len(year_trades),
            "buy_volume_therms": round(sum(t.volume_therms for t in buys), 0),
            "sell_volume_therms": round(sum(t.volume_therms for t in sells), 0),
            "crisis_price_trades": len(crisis),
            "seasonal_exposure": self.seasonal_exposure_therms(year),
        }
