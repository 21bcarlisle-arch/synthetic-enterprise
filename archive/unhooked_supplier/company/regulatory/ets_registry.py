"""UK Emissions Trading Scheme (UKETS) allowance registry: purchase, allocation, surrender."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


# UK ETS launched January 2021 post-Brexit, replacing EU ETS for UK participants.
# Power generators are 'installation operators'; energy suppliers are 'aircraft operators'
# only if they run aviation. Suppliers face ETS costs indirectly via wholesale power price.
# But direct compliance is needed if supplier owns generation assets.

_UKETS_PRICE_GBP_PER_TONNE: Dict[int, float] = {
    2021: 50.0,
    2022: 72.0,  # Peak Mar 2022 £80+
    2023: 65.0,
    2024: 45.0,
    2025: 50.0,
}

_FREE_ALLOCATION_TONNE_PER_MWH: Dict[str, float] = {
    'gas': 0.06,
    'coal': 0.0,   # Coal receives no free allocation
    'biomass': 0.01,
}


def get_ukets_price(year: int) -> float:
    if year in _UKETS_PRICE_GBP_PER_TONNE:
        return _UKETS_PRICE_GBP_PER_TONNE[year]
    return _UKETS_PRICE_GBP_PER_TONNE.get(
        max(k for k in _UKETS_PRICE_GBP_PER_TONNE if k <= year),
        50.0,
    )


class AllowanceSource(str, Enum):
    AUCTION = 'auction'
    FREE_ALLOCATION = 'free_allocation'
    SECONDARY_MARKET = 'secondary_market'
    FORWARD_PURCHASE = 'forward_purchase'


@dataclass(frozen=True)
class AllowancePurchase:
    purchase_id: str
    year: int
    purchase_date: dt.date
    tonnes_co2: float
    price_gbp_per_tonne: float
    source: AllowanceSource

    @property
    def total_cost_gbp(self) -> float:
        return round(self.tonnes_co2 * self.price_gbp_per_tonne, 2)


@dataclass(frozen=True)
class ComplianceObligation:
    compliance_year: int
    generation_mwh: float
    emission_factor_tonne_per_mwh: float
    free_allocation_tonnes: float = 0.0

    @property
    def gross_obligation_tonnes(self) -> float:
        return round(self.generation_mwh * self.emission_factor_tonne_per_mwh, 1)

    @property
    def net_obligation_tonnes(self) -> float:
        return max(0.0, round(self.gross_obligation_tonnes - self.free_allocation_tonnes, 1))


class ETSRegistry:
    def __init__(self) -> None:
        self._purchases: List[AllowancePurchase] = []
        self._surrenders: Dict[int, float] = {}  # year -> tonnes surrendered
        self._obligations: List[ComplianceObligation] = []

    def purchase(self, purchase_id: str, year: int, purchase_date: dt.date,
                   tonnes: float, price_gbp_per_tonne: float,
                   source: AllowanceSource) -> AllowancePurchase:
        p = AllowancePurchase(
            purchase_id=purchase_id, year=year, purchase_date=purchase_date,
            tonnes_co2=tonnes, price_gbp_per_tonne=price_gbp_per_tonne,
            source=source,
        )
        self._purchases.append(p)
        return p

    def record_obligation(self, compliance_year: int, generation_mwh: float,
                            emission_factor: float,
                            free_allocation: float = 0.0) -> ComplianceObligation:
        ob = ComplianceObligation(
            compliance_year=compliance_year, generation_mwh=generation_mwh,
            emission_factor_tonne_per_mwh=emission_factor,
            free_allocation_tonnes=free_allocation,
        )
        self._obligations.append(ob)
        return ob

    def surrender(self, year: int, tonnes: float) -> None:
        self._surrenders[year] = self._surrenders.get(year, 0.0) + tonnes

    def holding_tonnes(self, year: int) -> float:
        purchased = sum(p.tonnes_co2 for p in self._purchases if p.year == year)
        surrendered = self._surrenders.get(year, 0.0)
        return round(purchased - surrendered, 1)

    def total_spend_gbp(self, year: int) -> float:
        return round(sum(p.total_cost_gbp for p in self._purchases if p.year == year), 2)

    def compliance_position(self, year: int) -> Optional[dict]:
        obs = [o for o in self._obligations if o.compliance_year == year]
        if not obs:
            return None
        net_ob = sum(o.net_obligation_tonnes for o in obs)
        holding = self.holding_tonnes(year)
        return {
            'year': year,
            'net_obligation_tonnes': round(net_ob, 1),
            'holdings_tonnes': holding,
            'surplus_deficit_tonnes': round(holding - net_ob, 1),
            'is_compliant': holding >= net_ob,
            'total_spend_gbp': self.total_spend_gbp(year),
        }
