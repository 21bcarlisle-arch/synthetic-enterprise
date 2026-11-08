"""Interconnector cross-border price exposure: NEMO, BritNed, IFA1/2, VikingLink."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class Interconnector(str, Enum):
    IFA1 = 'IFA1'    # UK-France 2000 MW
    IFA2 = 'IFA2'    # UK-France 1000 MW (2021)
    BRITNED = 'BritNed'  # UK-Netherlands 1000 MW
    NEMO = 'NEMO'    # UK-Belgium 1000 MW
    NORTHSEALINK = 'NSL'  # UK-Norway 1400 MW (2021)
    VIKINGLINK = 'VikingLink'  # UK-Denmark 1400 MW (2024)
    ELECLINK = 'ElecLink'  # UK-France 1000 MW (2022)


class FlowDirection(str, Enum):
    IMPORT = 'import'
    EXPORT = 'export'
    CONSTRAINED = 'constrained'  # physical flow limits


_INTERCONNECTOR_CAPACITY_MW: Dict[Interconnector, int] = {
    Interconnector.IFA1: 2000,
    Interconnector.IFA2: 1000,
    Interconnector.BRITNED: 1000,
    Interconnector.NEMO: 1000,
    Interconnector.NORTHSEALINK: 1400,
    Interconnector.VIKINGLINK: 1400,
    Interconnector.ELECLINK: 1000,
}


@dataclass(frozen=True)
class InterconnectorObservation:
    interconnector: Interconnector
    observation_date: dt.date
    flow_mw: float
    gb_price_gbp_per_mwh: float
    foreign_price_gbp_per_mwh: float
    direction: FlowDirection

    @property
    def price_differential_gbp_per_mwh(self) -> float:
        return round(self.gb_price_gbp_per_mwh - self.foreign_price_gbp_per_mwh, 2)

    @property
    def capacity_mw(self) -> int:
        return _INTERCONNECTOR_CAPACITY_MW[self.interconnector]

    @property
    def utilisation_pct(self) -> float:
        if self.capacity_mw == 0:
            return 0.0
        return round(abs(self.flow_mw) / self.capacity_mw * 100, 1)


class InterconnectorPriceMonitor:
    def __init__(self) -> None:
        self._observations: List[InterconnectorObservation] = []

    def record(self, interconnector: Interconnector, date: dt.date,
                flow_mw: float, gb_price: float, foreign_price: float,
                direction: FlowDirection) -> InterconnectorObservation:
        obs = InterconnectorObservation(
            interconnector=interconnector, observation_date=date,
            flow_mw=flow_mw, gb_price_gbp_per_mwh=gb_price,
            foreign_price_gbp_per_mwh=foreign_price, direction=direction,
        )
        self._observations.append(obs)
        return obs

    def observations_for(self, interconnector: Interconnector) -> List[InterconnectorObservation]:
        return [o for o in self._observations if o.interconnector == interconnector]

    def avg_price_differential(self, interconnector: Interconnector) -> Optional[float]:
        obs = self.observations_for(interconnector)
        if not obs:
            return None
        return round(sum(o.price_differential_gbp_per_mwh for o in obs) / len(obs), 2)

    def highest_differential(self) -> Optional[InterconnectorObservation]:
        if not self._observations:
            return None
        return max(self._observations,
                    key=lambda o: abs(o.price_differential_gbp_per_mwh))

    def import_days(self, interconnector: Interconnector) -> int:
        return sum(1 for o in self.observations_for(interconnector)
                   if o.direction == FlowDirection.IMPORT)

    def total_import_mwh(self, interconnector: Interconnector) -> float:
        return round(sum(
            o.flow_mw * 24 for o in self.observations_for(interconnector)
            if o.direction == FlowDirection.IMPORT
        ), 1)

    def monitor_summary(self, date: dt.date) -> dict:
        year_obs = [o for o in self._observations if o.observation_date.year == date.year]
        return {
            'year': date.year,
            'observations': len(year_obs),
            'interconnectors_active': len(set(o.interconnector for o in year_obs)),
            'avg_gb_price': round(
                sum(o.gb_price_gbp_per_mwh for o in year_obs) / max(1, len(year_obs)), 2
            ),
        }
