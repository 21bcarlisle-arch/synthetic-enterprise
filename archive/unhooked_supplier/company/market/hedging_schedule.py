"""Commodity hedging schedule: forward delivery vs open position by month."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class HedgeTenor(str, Enum):
    MONTH_AHEAD = 'month_ahead'
    QUARTER_AHEAD = 'quarter_ahead'
    SEASON_AHEAD = 'season_ahead'
    YEAR_AHEAD = 'year_ahead'


class Commodity(str, Enum):
    ELECTRICITY = 'electricity'
    GAS = 'gas'


@dataclass(frozen=True)
class ForwardContractDelivery:
    contract_id: str
    commodity: Commodity
    delivery_month: dt.date
    volume_mwh: float
    contracted_price_gbp_per_mwh: float
    tenor: HedgeTenor
    traded_date: dt.date

    @property
    def contract_value_gbp(self) -> float:
        return round(self.volume_mwh * self.contracted_price_gbp_per_mwh, 2)


@dataclass
class DeliveryMonthPosition:
    delivery_month: dt.date
    commodity: Commodity
    forecast_mwh: float
    _contracts: List[ForwardContractDelivery] = field(default_factory=list)

    @property
    def hedged_mwh(self) -> float:
        return round(sum(c.volume_mwh for c in self._contracts), 2)

    @property
    def open_position_mwh(self) -> float:
        return round(self.forecast_mwh - self.hedged_mwh, 2)

    @property
    def hedge_ratio_pct(self) -> float:
        if self.forecast_mwh == 0:
            return 0.0
        return round(self.hedged_mwh / self.forecast_mwh * 100, 1)

    @property
    def is_over_hedged(self) -> bool:
        return self.hedged_mwh > self.forecast_mwh

    @property
    def avg_contracted_price(self) -> Optional[float]:
        if not self._contracts:
            return None
        total_vol = sum(c.volume_mwh for c in self._contracts)
        if total_vol == 0:
            return None
        return round(
            sum(c.volume_mwh * c.contracted_price_gbp_per_mwh for c in self._contracts) / total_vol, 2
        )


class HedgingSchedule:
    def __init__(self) -> None:
        self._positions: Dict[tuple, DeliveryMonthPosition] = {}
        self._next_id = 1

    def set_forecast(self, delivery_month: dt.date, commodity: Commodity,
                      forecast_mwh: float) -> DeliveryMonthPosition:
        key = (delivery_month, commodity)
        pos = DeliveryMonthPosition(delivery_month=delivery_month, commodity=commodity,
                                     forecast_mwh=forecast_mwh)
        self._positions[key] = pos
        return pos

    def add_contract(self, delivery_month: dt.date, commodity: Commodity,
                      volume_mwh: float, price_gbp_per_mwh: float,
                      tenor: HedgeTenor, traded_date: dt.date) -> ForwardContractDelivery:
        key = (delivery_month, commodity)
        if key not in self._positions:
            raise KeyError(f'No forecast for {delivery_month}/{commodity.value}')
        contract = ForwardContractDelivery(
            contract_id=f'FWD-{self._next_id:04d}',
            commodity=commodity, delivery_month=delivery_month,
            volume_mwh=volume_mwh, contracted_price_gbp_per_mwh=price_gbp_per_mwh,
            tenor=tenor, traded_date=traded_date,
        )
        self._next_id += 1
        self._positions[key]._contracts.append(contract)
        return contract

    def get_position(self, delivery_month: dt.date, commodity: Commodity
                      ) -> Optional[DeliveryMonthPosition]:
        return self._positions.get((delivery_month, commodity))

    def over_hedged_months(self, commodity: Commodity) -> List[dt.date]:
        return [pos.delivery_month for pos in self._positions.values()
                if pos.commodity == commodity and pos.is_over_hedged]

    def portfolio_hedge_ratio(self, commodity: Commodity) -> Optional[float]:
        positions = [p for p in self._positions.values() if p.commodity == commodity]
        total_forecast = sum(p.forecast_mwh for p in positions)
        if total_forecast == 0:
            return None
        total_hedged = sum(p.hedged_mwh for p in positions)
        return round(total_hedged / total_forecast * 100, 1)

    def schedule_summary(self, commodity: Commodity) -> dict:
        positions = sorted(
            [p for p in self._positions.values() if p.commodity == commodity],
            key=lambda p: p.delivery_month,
        )
        return {
            'commodity': commodity.value,
            'months': len(positions),
            'total_forecast_mwh': round(sum(p.forecast_mwh for p in positions), 2),
            'total_hedged_mwh': round(sum(p.hedged_mwh for p in positions), 2),
            'portfolio_hedge_ratio_pct': self.portfolio_hedge_ratio(commodity),
            'over_hedged_count': len([p for p in positions if p.is_over_hedged]),
        }
