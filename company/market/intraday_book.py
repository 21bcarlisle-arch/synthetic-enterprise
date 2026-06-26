"""Intraday electricity trading book.

UK suppliers trade on the N2EX intraday continuous market to balance their
position before gate closure (1 hour before each 30-minute settlement period).
The goal: arrive at gate closure with a flat book (no open imbalance), as any
remaining position goes to Elexon's Balancing Mechanism at potentially punitive
cashout prices.

Typical intraday volumes:
- Suppliers trade 5-30% of their portfolio daily on intraday
- Trade sizes: 0.1-5 MW blocks (N2EX minimum 0.1 MW)
- Price discovery: continuous limit order book
- 2022 crisis: intraday prices hit £4,000+/MWh in winter peaks

Intraday P&L = sum of (sell_price - buy_price) × volume across all round trips.
A supplier with good forecasting buys short positions cheaply and sells long
positions profitably. Poor forecasting = large exposure at cashout.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class TradeDirection(str, Enum):
    BUY = "buy"    # buying power = covering a short position
    SELL = "sell"  # selling power = unwinding a long position


class TradeReason(str, Enum):
    POSITION_BALANCING = "position_balancing"   # routine flat-book management
    DEMAND_FORECAST_REVISION = "demand_forecast_revision"  # actual demand differs
    GENERATION_SHORTFALL = "generation_shortfall"  # PPA/wind under-delivery
    EMERGENCY_COVER = "emergency_cover"            # crisis trade (expensive)
    OPTIMISATION = "optimisation"                  # opportunistic spread trade


@dataclass(frozen=True)
class IntradayTrade:
    trade_id: str
    settlement_date: dt.date
    settlement_period: int       # 1-48 (each = 30 min)
    direction: TradeDirection
    volume_mw: float             # block size in MW
    price_gbp_per_mwh: float
    traded_at: dt.datetime       # timestamp of execution
    reason: TradeReason = TradeReason.POSITION_BALANCING

    @property
    def volume_mwh(self) -> float:
        return round(self.volume_mw * 0.5, 4)   # 30-min period = 0.5 hours

    @property
    def trade_value_gbp(self) -> float:
        """Positive = cost (buy), negative = revenue (sell)."""
        value = self.volume_mwh * self.price_gbp_per_mwh
        return round(value if self.direction == TradeDirection.BUY else -value, 2)

    @property
    def is_crisis_price(self) -> bool:
        """True when traded above £500/MWh (crisis-level intraday)."""
        return self.price_gbp_per_mwh > 500.0


class IntradayBook:
    """Log and analyse intraday electricity trades."""

    def __init__(self) -> None:
        self._trades: List[IntradayTrade] = []

    def record_trade(
        self,
        trade_id: str,
        settlement_date: dt.date,
        settlement_period: int,
        direction: TradeDirection,
        volume_mw: float,
        price_gbp_per_mwh: float,
        traded_at: dt.datetime,
        reason: TradeReason = TradeReason.POSITION_BALANCING,
    ) -> IntradayTrade:
        if not (1 <= settlement_period <= 48):
            raise ValueError(f"settlement_period must be 1-48, got {settlement_period}")
        trade = IntradayTrade(
            trade_id=trade_id,
            settlement_date=settlement_date,
            settlement_period=settlement_period,
            direction=direction,
            volume_mw=volume_mw,
            price_gbp_per_mwh=price_gbp_per_mwh,
            traded_at=traded_at,
            reason=reason,
        )
        self._trades.append(trade)
        return trade

    def trades_for_date(self, settlement_date: dt.date) -> List[IntradayTrade]:
        return [t for t in self._trades if t.settlement_date == settlement_date]

    def net_position_mwh(self, settlement_date: dt.date,
                          settlement_period: Optional[int] = None) -> float:
        """Net position: positive = net long (sold more than bought), negative = net short."""
        trades = self.trades_for_date(settlement_date)
        if settlement_period is not None:
            trades = [t for t in trades if t.settlement_period == settlement_period]
        net = 0.0
        for t in trades:
            if t.direction == TradeDirection.SELL:
                net += t.volume_mwh
            else:
                net -= t.volume_mwh
        return round(net, 4)

    def daily_pnl_gbp(self, settlement_date: dt.date) -> float:
        """Daily intraday P&L (negative = net cost, positive = net profit)."""
        return round(sum(-t.trade_value_gbp for t in self.trades_for_date(settlement_date)), 2)

    def crisis_trades(self, threshold_gbp_per_mwh: float = 500.0) -> List[IntradayTrade]:
        return [t for t in self._trades if t.price_gbp_per_mwh > threshold_gbp_per_mwh]

    def average_buy_price(self, settlement_date: dt.date) -> Optional[float]:
        buys = [t for t in self.trades_for_date(settlement_date)
                if t.direction == TradeDirection.BUY]
        if not buys:
            return None
        total_cost = sum(t.trade_value_gbp for t in buys)
        total_mwh = sum(t.volume_mwh for t in buys)
        return round(total_cost / total_mwh, 2) if total_mwh else None

    def intraday_summary(self, settlement_date: dt.date) -> dict:
        day_trades = self.trades_for_date(settlement_date)
        buys = [t for t in day_trades if t.direction == TradeDirection.BUY]
        sells = [t for t in day_trades if t.direction == TradeDirection.SELL]
        return {
            "settlement_date": str(settlement_date),
            "total_trades": len(day_trades),
            "buy_trades": len(buys),
            "sell_trades": len(sells),
            "buy_volume_mwh": round(sum(t.volume_mwh for t in buys), 3),
            "sell_volume_mwh": round(sum(t.volume_mwh for t in sells), 3),
            "net_position_mwh": self.net_position_mwh(settlement_date),
            "daily_pnl_gbp": self.daily_pnl_gbp(settlement_date),
            "crisis_trades": len([t for t in day_trades if t.is_crisis_price]),
        }
