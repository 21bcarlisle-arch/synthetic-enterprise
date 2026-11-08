from __future__ import annotations
import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class DayAheadDirection(str, Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True)
class DayAheadAuction:
    auction_id: str
    delivery_date: dt.date
    direction: DayAheadDirection
    volume_mwh: float
    bid_price_gbp_per_mwh: float
    cleared_price_gbp_per_mwh: float
    auctioned_at: dt.datetime

    @property
    def cost_gbp(self) -> float:
        value = self.volume_mwh * self.cleared_price_gbp_per_mwh
        return round(value if self.direction == DayAheadDirection.BUY else -value, 2)

    @property
    def vs_forward_spread_gbp_per_mwh(self) -> float:
        return round(self.cleared_price_gbp_per_mwh - self.bid_price_gbp_per_mwh, 2)

    @property
    def is_crisis_price(self) -> bool:
        return self.cleared_price_gbp_per_mwh > 300.0


class DayAheadBook:
    def __init__(self) -> None:
        self._auctions: List[DayAheadAuction] = []

    def submit_auction(self, auction_id: str, delivery_date: dt.date,
                       direction: DayAheadDirection, volume_mwh: float,
                       bid_price_gbp_per_mwh: float, cleared_price_gbp_per_mwh: float,
                       auctioned_at: dt.datetime) -> DayAheadAuction:
        if volume_mwh <= 0:
            raise ValueError("volume_mwh must be positive")
        if auctioned_at.date() >= delivery_date:
            raise ValueError("auctioned_at must be before delivery_date")
        auction = DayAheadAuction(auction_id=auction_id, delivery_date=delivery_date,
            direction=direction, volume_mwh=volume_mwh,
            bid_price_gbp_per_mwh=bid_price_gbp_per_mwh,
            cleared_price_gbp_per_mwh=cleared_price_gbp_per_mwh, auctioned_at=auctioned_at)
        self._auctions.append(auction)
        return auction

    def auctions_for_month(self, year: int, month: int) -> List[DayAheadAuction]:
        return [a for a in self._auctions
                if a.delivery_date.year == year and a.delivery_date.month == month]

    def net_position_mwh(self, delivery_date: dt.date) -> float:
        net = 0.0
        for a in self._auctions:
            if a.delivery_date == delivery_date:
                net += a.volume_mwh if a.direction == DayAheadDirection.BUY else -a.volume_mwh
        return round(net, 4)

    def total_volume_mwh(self, year: Optional[int] = None) -> float:
        auctions = [a for a in self._auctions if year is None or a.delivery_date.year == year]
        return round(sum(a.volume_mwh for a in auctions), 3)

    def total_cost_gbp(self, year: Optional[int] = None) -> float:
        auctions = [a for a in self._auctions if year is None or a.delivery_date.year == year]
        return round(sum(a.cost_gbp for a in auctions), 2)

    def average_clearing_price(self, year: Optional[int] = None) -> Optional[float]:
        auctions = [a for a in self._auctions if year is None or a.delivery_date.year == year]
        if not auctions:
            return None
        total_vol = sum(a.volume_mwh for a in auctions)
        if total_vol == 0:
            return None
        weighted = sum(a.cleared_price_gbp_per_mwh * a.volume_mwh for a in auctions)
        return round(weighted / total_vol, 2)

    def crisis_auctions(self, threshold: float = 300.0) -> List[DayAheadAuction]:
        return [a for a in self._auctions if a.cleared_price_gbp_per_mwh > threshold]

    def monthly_summary(self, year: int, month: int) -> dict:
        ma = self.auctions_for_month(year, month)
        buys = [a for a in ma if a.direction == DayAheadDirection.BUY]
        sells = [a for a in ma if a.direction == DayAheadDirection.SELL]
        bv = round(sum(a.volume_mwh for a in buys), 3)
        sv = round(sum(a.volume_mwh for a in sells), 3)
        tv = round(sum(a.volume_mwh for a in ma), 3)
        avg = round(sum(a.cleared_price_gbp_per_mwh * a.volume_mwh for a in ma) / tv, 2) if tv > 0 else None
        return {"month": f"{year:04d}-{month:02d}", "buy_volume_mwh": bv,
                "sell_volume_mwh": sv, "net_volume_mwh": round(bv - sv, 3),
                "total_cost_gbp": round(sum(a.cost_gbp for a in ma), 2),
                "avg_clearing_price": avg,
                "crisis_count": sum(1 for a in ma if a.is_crisis_price),
                "auction_count": len(ma)}

    def day_ahead_summary(self) -> dict:
        buys = [a for a in self._auctions if a.direction == DayAheadDirection.BUY]
        sells = [a for a in self._auctions if a.direction == DayAheadDirection.SELL]
        return {"total_auctions": len(self._auctions),
                "total_buy_volume_mwh": round(sum(a.volume_mwh for a in buys), 3),
                "total_sell_volume_mwh": round(sum(a.volume_mwh for a in sells), 3),
                "total_cost_gbp": self.total_cost_gbp(),
                "avg_clearing_price": self.average_clearing_price(),
                "crisis_auctions_count": len(self.crisis_auctions()),
                "years_active": sorted({a.delivery_date.year for a in self._auctions})}
