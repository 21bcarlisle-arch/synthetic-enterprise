"""Wholesale Energy Market Interconnect Quality Register (Phase DP).

UK interconnectors are cross-border electricity cables connecting Great Britain
to France (IFA/IFA2), Belgium (Nemo), Netherlands (BritNed), Norway (NSL),
Denmark (Viking Link), and Ireland (Moyle/EWIC).

Interconnectors are treated as settlement units on the BSC with their own BM
unit IDs. A supplier trading on the interconnector must track:
- Physical flow direction (import/export)
- Settlement exposure at prevailing imbalance prices
- Net position contribution to NOP calculation
- Arbitrage opportunity versus day-ahead price differentials

From the company perspective (SIM/company seam): the company sees interconnect
as affecting price feed, not as a controllable asset.
This register tracks GB-continental price arbitrage signals and interconnect
capacity utilisation as observable market data.

Epistemic: company reads Elexon BM unit data and interconnect capacity from
NESO published data. Cannot see future flows.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class InterconnectorID(str, Enum):
    IFA = "IFA"         # GB-France 2000 MW (1985)
    IFA2 = "IFA2"       # GB-France 1000 MW (2021)
    NEMO = "NEMO"       # GB-Belgium 1000 MW (2019)
    BRITNED = "BRITNED" # GB-Netherlands 1000 MW (2011)
    NSL = "NSL"         # GB-Norway 1400 MW (2021) = North Sea Link
    MOYLE = "MOYLE"     # GB-Ireland 500 MW (2002)
    EWIC = "EWIC"       # GB-Ireland 500 MW (2012)
    VIKING = "VIKING"   # GB-Denmark 1400 MW (2023)


_CAPACITY_MW: Dict[str, float] = {
    InterconnectorID.IFA: 2000,
    InterconnectorID.IFA2: 1000,
    InterconnectorID.NEMO: 1000,
    InterconnectorID.BRITNED: 1000,
    InterconnectorID.NSL: 1400,
    InterconnectorID.MOYLE: 500,
    InterconnectorID.EWIC: 500,
    InterconnectorID.VIKING: 1400,
}

_COMMISSIONED_YEAR: Dict[str, int] = {
    InterconnectorID.IFA: 1985,
    InterconnectorID.IFA2: 2021,
    InterconnectorID.NEMO: 2019,
    InterconnectorID.BRITNED: 2011,
    InterconnectorID.NSL: 2021,
    InterconnectorID.MOYLE: 2002,
    InterconnectorID.EWIC: 2012,
    InterconnectorID.VIKING: 2023,
}


class FlowDirection(str, Enum):
    IMPORT = "import"   # power flowing into GB
    EXPORT = "export"   # power flowing out of GB
    ZERO = "zero"       # no flow


@dataclass(frozen=True)
class InterconnectorObservation:
    interconnector: InterconnectorID
    settlement_date: dt.date
    settlement_period: int           # 1-48
    flow_mw: float                   # positive = import, negative = export
    gb_price_gbp_per_mwh: float     # observed GB price
    continental_price_gbp_per_mwh: float  # continental counterpart

    @property
    def direction(self) -> FlowDirection:
        if self.flow_mw > 5:
            return FlowDirection.IMPORT
        if self.flow_mw < -5:
            return FlowDirection.EXPORT
        return FlowDirection.ZERO

    @property
    def utilisation_pct(self) -> float:
        capacity = _CAPACITY_MW.get(self.interconnector, 0)
        if capacity <= 0:
            return 0.0
        return abs(self.flow_mw) / capacity * 100

    @property
    def price_differential_gbp(self) -> float:
        return self.gb_price_gbp_per_mwh - self.continental_price_gbp_per_mwh

    @property
    def is_arbitrage_aligned(self) -> bool:
        """Imports should occur when continental is cheaper; exports when GB is cheaper."""
        if self.direction == FlowDirection.IMPORT:
            return self.continental_price_gbp_per_mwh < self.gb_price_gbp_per_mwh
        if self.direction == FlowDirection.EXPORT:
            return self.gb_price_gbp_per_mwh < self.continental_price_gbp_per_mwh
        return True


class InterconnectorMonitorRegister:
    """Tracks observable interconnector flow and price data."""

    def __init__(self) -> None:
        self._observations: List[InterconnectorObservation] = []

    @staticmethod
    def total_gb_import_capacity_mw() -> float:
        return sum(_CAPACITY_MW.values())

    @staticmethod
    def commissioned_year(interconnector: InterconnectorID) -> int:
        return _COMMISSIONED_YEAR[interconnector]

    def record(
        self,
        interconnector: InterconnectorID,
        settlement_date: dt.date,
        settlement_period: int,
        flow_mw: float,
        gb_price: float,
        continental_price: float,
    ) -> InterconnectorObservation:
        obs = InterconnectorObservation(
            interconnector=interconnector,
            settlement_date=settlement_date,
            settlement_period=settlement_period,
            flow_mw=flow_mw,
            gb_price_gbp_per_mwh=gb_price,
            continental_price_gbp_per_mwh=continental_price,
        )
        self._observations.append(obs)
        return obs

    def observations_for(
        self, interconnector: InterconnectorID, date: Optional[dt.date] = None
    ) -> List[InterconnectorObservation]:
        obs = [o for o in self._observations if o.interconnector == interconnector]
        if date:
            obs = [o for o in obs if o.settlement_date == date]
        return obs

    def imports(self) -> List[InterconnectorObservation]:
        return [o for o in self._observations if o.direction == FlowDirection.IMPORT]

    def exports(self) -> List[InterconnectorObservation]:
        return [o for o in self._observations if o.direction == FlowDirection.EXPORT]

    def non_arbitrage_aligned(self) -> List[InterconnectorObservation]:
        return [o for o in self._observations if not o.is_arbitrage_aligned]

    def avg_gb_price(self) -> float:
        if not self._observations:
            return 0.0
        return sum(o.gb_price_gbp_per_mwh for o in self._observations) / len(self._observations)

    def high_utilisation(self, threshold_pct: float = 80.0) -> List[InterconnectorObservation]:
        return [o for o in self._observations if o.utilisation_pct >= threshold_pct]

    def interconnector_summary(self) -> str:
        n = len(self._observations)
        total_cap = self.total_gb_import_capacity_mw()
        return (
            f"Interconnector Monitor: {n} observations. "
            f"Total GB interconnect capacity: {total_cap:,.0f} MW. "
            f"Interconnects: {len(InterconnectorID)}."
        )
