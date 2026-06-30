"""Wholesale Gas Market Monitor (Phase FF).

The company buys gas on the wholesale market (NBP - National Balancing Point,
UK's gas pricing hub) to supply its gas customers.

Key metrics:
- Day-Ahead (DA) and Within-Day (WD) spot prices (p/therm, converted to £/MWh)
- Gas-to-power spread: gas price vs power price (signals when gas power is economic)
- Seasonal storage premium: winter vs summer gas prices
- Gas price in £/MWh (1 therm = 29.307 kWh for unit conversions)

Price dynamics (publicly observable via NESO/Elexon/Ofgem market data):
- Normal: 50-80p/therm (£17-27/MWh) pre-2021
- Crisis: 400-800p/therm (£136-273/MWh) 2021-2022
- Post-crisis: 100-150p/therm (£34-51/MWh) 2023+

The company trades NBP to supply its own gas book, not for proprietary trading.
It monitors its weighted average purchase price (WAPP) vs the prevailing market
to assess whether to hedge forward or buy spot.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class GasMarketSession(str, Enum):
    DAY_AHEAD = "day_ahead"
    WITHIN_DAY = "within_day"
    MONTH_AHEAD = "month_ahead"
    QUARTER_AHEAD = "quarter_ahead"
    SEASON_AHEAD = "season_ahead"


_THERMS_PER_MWH = 1.0 / 29.307


@dataclass(frozen=True)
class GasMarketSnapshot:
    settlement_date: dt.date
    session: GasMarketSession
    price_pence_per_therm: float
    volume_therm: float = 0.0

    @property
    def price_gbp_per_mwh(self) -> float:
        return self.price_pence_per_therm * _THERMS_PER_MWH * 100

    @property
    def is_crisis_price(self) -> bool:
        return self.price_pence_per_therm > 250.0

    @property
    def is_below_normal_range(self) -> bool:
        return self.price_pence_per_therm < 30.0

    def snapshot_summary(self) -> str:
        return (
            "GasMarket " + str(self.settlement_date) + " " + self.session.value + ": "
            + str(round(self.price_pence_per_therm, 1)) + "p/therm "
            + "(" + str(round(self.price_gbp_per_mwh, 2)) + " GBP/MWh)"
            + (" CRISIS" if self.is_crisis_price else "")
        )


@dataclass(frozen=True)
class GasPurchaseRecord:
    purchase_date: dt.date
    session: GasMarketSession
    volume_therm: float
    price_pence_per_therm: float

    @property
    def total_cost_gbp(self) -> float:
        return self.volume_therm * self.price_pence_per_therm / 100


class GasMarketMonitor:

    def __init__(self) -> None:
        self._snapshots: List[GasMarketSnapshot] = []
        self._purchases: List[GasPurchaseRecord] = []

    def record_price(self, snapshot: GasMarketSnapshot) -> GasMarketSnapshot:
        self._snapshots.append(snapshot)
        return snapshot

    def record_purchase(self, purchase: GasPurchaseRecord) -> GasPurchaseRecord:
        self._purchases.append(purchase)
        return purchase

    def latest_price(self, session: GasMarketSession) -> Optional[GasMarketSnapshot]:
        matching = [s for s in self._snapshots if s.session == session]
        if not matching:
            return None
        return max(matching, key=lambda s: s.settlement_date)

    def prices_in_range(
        self, start: dt.date, end: dt.date
    ) -> List[GasMarketSnapshot]:
        return [s for s in self._snapshots if start <= s.settlement_date <= end]

    def avg_price_pence_per_therm(
        self, session: Optional[GasMarketSession] = None
    ) -> float:
        snaps = self._snapshots
        if session:
            snaps = [s for s in snaps if s.session == session]
        if not snaps:
            return 0.0
        return sum(s.price_pence_per_therm for s in snaps) / len(snaps)

    def crisis_periods(self) -> List[GasMarketSnapshot]:
        return [s for s in self._snapshots if s.is_crisis_price]

    def wapp_pence_per_therm(self) -> float:
        total_cost = sum(p.total_cost_gbp for p in self._purchases)
        total_vol = sum(p.volume_therm for p in self._purchases)
        if total_vol == 0:
            return 0.0
        return total_cost * 100 / total_vol

    def total_purchases_therm(self) -> float:
        return sum(p.volume_therm for p in self._purchases)

    def gas_market_summary(self) -> str:
        n = len(self._snapshots)
        n_crisis = len(self.crisis_periods())
        wapp = self.wapp_pence_per_therm()
        return (
            "Gas Market Monitor: " + str(n) + " price records. "
            "Crisis periods: " + str(n_crisis) + ". "
            "WAPP: " + str(round(wapp, 1)) + "p/therm."
        )
