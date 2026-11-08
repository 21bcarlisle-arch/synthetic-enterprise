from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class HedgeOutcome(str, Enum):
    PROFITABLE = 'profitable'     # hedge bought below delivery price
    NEUTRAL = 'neutral'           # within 5% of spot
    COSTLY = 'costly'             # hedge price above delivery spot


@dataclass(frozen=True)
class HedgeDelivery:
    trade_id: str
    commodity: str
    delivery_year: int
    volume_mwh: float
    contracted_price_gbp_per_mwh: float
    spot_price_at_delivery_gbp_per_mwh: float

    @property
    def price_differential_gbp_per_mwh(self) -> float:
        return round(self.spot_price_at_delivery_gbp_per_mwh - self.contracted_price_gbp_per_mwh, 4)

    @property
    def pnl_gbp(self) -> float:
        return round(self.price_differential_gbp_per_mwh * self.volume_mwh, 2)

    @property
    def outcome(self) -> HedgeOutcome:
        diff_pct = abs(self.price_differential_gbp_per_mwh / self.spot_price_at_delivery_gbp_per_mwh * 100)
        if diff_pct <= 5.0:
            return HedgeOutcome.NEUTRAL
        return HedgeOutcome.PROFITABLE if self.pnl_gbp > 0 else HedgeOutcome.COSTLY

    @property
    def hedge_effectiveness_pct(self) -> float:
        if self.spot_price_at_delivery_gbp_per_mwh <= 0:
            return 0.0
        return round(self.price_differential_gbp_per_mwh / self.spot_price_at_delivery_gbp_per_mwh * 100, 2)


class HedgePerformanceBook:
    def __init__(self) -> None:
        self._deliveries: Dict[str, HedgeDelivery] = {}

    def record_delivery(self, trade_id: str, commodity: str, delivery_year: int,
                        volume_mwh: float, contracted_price: float,
                        spot_price: float) -> HedgeDelivery:
        d = HedgeDelivery(
            trade_id=trade_id,
            commodity=commodity,
            delivery_year=delivery_year,
            volume_mwh=volume_mwh,
            contracted_price_gbp_per_mwh=contracted_price,
            spot_price_at_delivery_gbp_per_mwh=spot_price,
        )
        self._deliveries[trade_id] = d
        return d

    def total_pnl_gbp(self, year: Optional[int] = None) -> float:
        deliveries = self._deliveries.values()
        if year is not None:
            deliveries = [d for d in deliveries if d.delivery_year == year]
        return round(sum(d.pnl_gbp for d in deliveries), 2)

    def profitable_trades(self) -> List[HedgeDelivery]:
        return [d for d in self._deliveries.values() if d.outcome == HedgeOutcome.PROFITABLE]

    def costly_trades(self) -> List[HedgeDelivery]:
        return [d for d in self._deliveries.values() if d.outcome == HedgeOutcome.COSTLY]

    def avg_effectiveness_pct(self, year: Optional[int] = None) -> Optional[float]:
        deliveries = list(self._deliveries.values())
        if year is not None:
            deliveries = [d for d in deliveries if d.delivery_year == year]
        if not deliveries:
            return None
        return round(sum(d.hedge_effectiveness_pct for d in deliveries) / len(deliveries), 2)

    def annual_summary(self, year: int) -> dict:
        year_d = [d for d in self._deliveries.values() if d.delivery_year == year]
        if not year_d:
            return {'year': year, 'trade_count': 0}
        profitable = [d for d in year_d if d.outcome == HedgeOutcome.PROFITABLE]
        costly = [d for d in year_d if d.outcome == HedgeOutcome.COSTLY]
        return {
            'year': year,
            'trade_count': len(year_d),
            'total_pnl_gbp': self.total_pnl_gbp(year),
            'profitable_trades': len(profitable),
            'costly_trades': len(costly),
            'avg_effectiveness_pct': self.avg_effectiveness_pct(year),
        }
