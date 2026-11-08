"""Power Purchase Agreement (PPA) book: long-term renewable offtake contracts."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class PPATechnology(str, Enum):
    ONSHORE_WIND = 'onshore_wind'
    OFFSHORE_WIND = 'offshore_wind'
    SOLAR = 'solar'
    HYDRO = 'hydro'
    BIOMASS = 'biomass'


class PPAPricingType(str, Enum):
    FIXED = 'fixed'
    INDEXED = 'indexed'    # e.g. % of baseload price
    FLOOR = 'floor'        # minimum price guaranteed


@dataclass(frozen=True)
class PPAContract:
    contract_id: str
    generator_id: str
    technology: PPATechnology
    start_date: dt.date
    end_date: dt.date
    capacity_mw: float
    annual_generation_mwh: float
    price_gbp_per_mwh: float
    pricing_type: PPAPricingType = PPAPricingType.FIXED
    floor_price_gbp_per_mwh: Optional[float] = None

    @property
    def term_years(self) -> float:
        return round((self.end_date - self.start_date).days / 365.25, 1)

    @property
    def annual_cost_gbp(self) -> float:
        return round(self.annual_generation_mwh * self.price_gbp_per_mwh, 2)

    def is_active(self, as_of: dt.date) -> bool:
        return self.start_date <= as_of <= self.end_date

    def effective_price(self, market_price: float) -> float:
        if self.pricing_type == PPAPricingType.FIXED:
            return self.price_gbp_per_mwh
        if self.pricing_type == PPAPricingType.FLOOR:
            return max(
                self.floor_price_gbp_per_mwh or self.price_gbp_per_mwh,
                market_price,
            )
        return market_price

    def vs_market_gbp(self, market_price: float) -> float:
        diff = self.price_gbp_per_mwh - market_price
        return round(self.annual_generation_mwh * diff, 2)


class PPABook:
    def __init__(self) -> None:
        self._contracts: List[PPAContract] = []

    def add_contract(self, contract_id: str, generator_id: str,
                       technology: PPATechnology,
                       start_date: dt.date, end_date: dt.date,
                       capacity_mw: float, annual_mwh: float,
                       price_gbp_per_mwh: float,
                       pricing_type: PPAPricingType = PPAPricingType.FIXED,
                       floor_price: Optional[float] = None) -> PPAContract:
        c = PPAContract(
            contract_id=contract_id, generator_id=generator_id,
            technology=technology, start_date=start_date, end_date=end_date,
            capacity_mw=capacity_mw, annual_generation_mwh=annual_mwh,
            price_gbp_per_mwh=price_gbp_per_mwh, pricing_type=pricing_type,
            floor_price_gbp_per_mwh=floor_price,
        )
        self._contracts.append(c)
        return c

    def active_contracts(self, as_of: dt.date) -> List[PPAContract]:
        return [c for c in self._contracts if c.is_active(as_of)]

    def total_contracted_mwh(self, as_of: dt.date) -> float:
        return sum(c.annual_generation_mwh for c in self.active_contracts(as_of))

    def total_annual_cost_gbp(self, as_of: dt.date) -> float:
        return round(sum(c.annual_cost_gbp for c in self.active_contracts(as_of)), 2)

    def total_vs_market_gbp(self, as_of: dt.date, market_price: float) -> float:
        return round(sum(
            c.vs_market_gbp(market_price) for c in self.active_contracts(as_of)
        ), 2)

    def ppa_summary(self, as_of: dt.date, market_price: float) -> dict:
        active = self.active_contracts(as_of)
        return {
            'active_ppas': len(active),
            'total_contracted_mwh': self.total_contracted_mwh(as_of),
            'total_annual_cost_gbp': self.total_annual_cost_gbp(as_of),
            'vs_market_gbp': self.total_vs_market_gbp(as_of, market_price),
            'renewable_share_mwh': self.total_contracted_mwh(as_of),
        }
