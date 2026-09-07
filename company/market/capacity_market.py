"""Capacity Market participation: CM unit registration, auction, and obligations.

CLEARING PRICES ARE NOT CONSTANTS HERE. They are published per delivery year and per auction and
read from `capacity_market_published_record`, which loads the regulation commons. This module used
to carry `_CM_CLEARING_PRICE_GBP_PER_KW_PER_YEAR`, one of THREE homes for one publication.

THE DEFECT THAT TABLE CARRIED, and it is why the parameter below is now named for what it is: the
table was keyed by the year the AUCTION WAS HELD, while `get_cm_price` named its parameter
`delivery_year`. A T-4 auction procures four years ahead, so the two keys are four years apart and
nothing said so. `get_cm_price(2023)` returned GBP63.00 -- the price the 2023 auction set for
delivery year 2026/27 -- to a caller asking about delivery year 2023/24, whose T-4 cleared at
GBP15.97. That is 3.9x, silently, and the value was not wrong: the KEY was.

Two further entries were invented rather than mis-keyed. `2022: 75.00  # Crisis year spike` was
the T-1 clearing price for delivery year 2022/23, which cleared at the price CAP -- a censored
observation, not a market spike, and the same figure `flexibility_potential` was multiplying by a
household's rated power. `2021: 0.0  # No T4 cleared in some years` asserted that no T-4 cleared;
the T-4 for delivery year 2021/22 cleared at GBP8.40/kW, the cheapest of the whole record, so the
comment described the opposite of what happened and a zero stood where a real price belonged.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from company.market import capacity_market_published_record


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


def get_cm_price(
    delivery_year: int, auction: AuctionType = AuctionType.T4
) -> Optional[float]:
    """Published clearing price (GBP/kW/yr of DE-RATED capacity) for a DELIVERY year.

    `delivery_year` is the calendar year the Oct-Sep delivery year OPENS in -- 2022 is DY 2022/23 --
    and NOT the year the auction was held. The table this replaced used the latter under this
    parameter's name; see the module docstring.

    `auction` defaults to T-4 because that is the bulk procurement, but it is a real argument: the
    T-1 for DY 2022/23 cleared at 11.6x the T-3 for the same delivery year, so which auction is
    meant is a question with a 11.6x answer and not a detail.

    Returns `None` where the record does not establish a price, and there is NO INVENTED DEFAULT.
    The deleted lookup ended `.get(delivery_year, 50.0)`, so every year outside its ten keys --
    including every year of the run window it did not cover -- silently priced at GBP50/kW, a
    figure no auction ever cleared at.
    """
    return capacity_market_published_record.clearing_price_gbp_per_kw_year(
        delivery_year, "T-4" if auction is AuctionType.T4 else "T-1")


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
        price = clearing_price
        if price is None:
            # Priced at the auction this obligation is actually IN. The deleted lookup took no
            # auction argument, so a T-1 obligation was priced off the T-4 table -- for DY 2022/23
            # that is GBP6.44 against a real GBP75.00.
            price = get_cm_price(delivery_year, auction_type)
        if price is None:
            raise ValueError(
                f"no published {auction_type.value.upper()} clearing price for delivery year "
                f"{delivery_year}: {capacity_market_published_record.delivery_year(delivery_year)}"
                ". Pass `clearing_price` explicitly if this obligation's price is known from "
                "elsewhere; there is no default, because the default this replaced was GBP50/kW "
                "and no auction ever cleared there."
            )
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
            # T-4, named: a summary that printed "the" clearing price for a delivery year with two
            # auctions was already choosing, and choosing silently.
            'clearing_price_gbp_per_kw_t4': get_cm_price(delivery_year, AuctionType.T4),
            'clearing_price_gbp_per_kw_t1': get_cm_price(delivery_year, AuctionType.T1),
            'obligations': len(obs),
            'total_derated_kw': self.total_derated_kw(delivery_year),
            'total_revenue_gbp': self.total_revenue_gbp(delivery_year),
        }
