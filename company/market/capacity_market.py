"""Capacity Market participation: CM unit registration, auction, and obligations."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class CMUnitType(str, Enum):
    CCGT = 'ccgt'                # Combined-cycle gas turbine
    OCGT = 'ocgt'                # Open-cycle (peaker)
    BATTERY = 'battery'
    DEMAND_RESPONSE = 'demand_response'
    INTERCONNECTOR = 'interconnector'
    PUMP_STORAGE = 'pump_storage'


class AuctionType(str, Enum):
    T4 = 't4'  # 4 years ahead
    T1 = 't1'  # 1 year ahead


_CM_CLEARING_PRICE_GBP_PER_KW_PER_YEAR: Dict[int, float] = {
    2016: 18.00,
    2017: 22.50,
    2018: 8.40,
    2019: 15.97,
    2020: 6.44,
    2021: 0.0,   # No T4 cleared in some years
    2022: 75.00,  # Crisis year spike
    2023: 63.00,
    2024: 55.00,
    2025: 60.00,
}


def get_cm_price(delivery_year: int) -> float:
    return _CM_CLEARING_PRICE_GBP_PER_KW_PER_YEAR.get(delivery_year, 50.0)


@dataclass(frozen=True)
class CMUnit:
    unit_id: str
    unit_type: CMUnitType
    derated_capacity_kw: float
    registered_date: dt.date


@dataclass
class CMObligation:
    unit: CMUnit
    delivery_year: int
    auction_type: AuctionType
    clearing_price_gbp_per_kw: float
    is_prequalified: bool = True
    penalties_gbp: float = 0.0

    @property
    def annual_revenue_gbp(self) -> float:
        return round(
            self.unit.derated_capacity_kw * self.clearing_price_gbp_per_kw, 2
        )

    @property
    def net_revenue_gbp(self) -> float:
        return round(self.annual_revenue_gbp - self.penalties_gbp, 2)

    def apply_penalty(self, penalty_gbp: float) -> None:
        self.penalties_gbp += penalty_gbp


class CapacityMarketBook:
    def __init__(self) -> None:
        self._units: List[CMUnit] = []
        self._obligations: List[CMObligation] = []

    def register_unit(self, unit_id: str, unit_type: CMUnitType,
                        derated_kw: float,
                        registered_date: dt.date) -> CMUnit:
        u = CMUnit(
            unit_id=unit_id, unit_type=unit_type,
            derated_capacity_kw=derated_kw, registered_date=registered_date,
        )
        self._units.append(u)
        return u

    def add_obligation(self, unit: CMUnit, delivery_year: int,
                         auction_type: AuctionType,
                         clearing_price: Optional[float] = None
                         ) -> CMObligation:
        price = clearing_price if clearing_price is not None else get_cm_price(delivery_year)
        o = CMObligation(
            unit=unit, delivery_year=delivery_year,
            auction_type=auction_type, clearing_price_gbp_per_kw=price,
        )
        self._obligations.append(o)
        return o

    def obligations_for_year(self, delivery_year: int) -> List[CMObligation]:
        return [o for o in self._obligations if o.delivery_year == delivery_year]

    def total_revenue_gbp(self, delivery_year: int) -> float:
        return round(sum(
            o.annual_revenue_gbp for o in self.obligations_for_year(delivery_year)
        ), 2)

    def total_derated_kw(self, delivery_year: int) -> float:
        return sum(
            o.unit.derated_capacity_kw for o in self.obligations_for_year(delivery_year)
        )

    def cm_summary(self, delivery_year: int) -> dict:
        obs = self.obligations_for_year(delivery_year)
        return {
            'delivery_year': delivery_year,
            'clearing_price_gbp_per_kw': get_cm_price(delivery_year),
            'obligations': len(obs),
            'total_derated_kw': self.total_derated_kw(delivery_year),
            'total_revenue_gbp': self.total_revenue_gbp(delivery_year),
        }
