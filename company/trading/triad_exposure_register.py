"""Triad Exposure Register (Phase FG).

Electricity 'Triads' are the 3 highest demand half-hours in the UK grid,
occurring between November and February (with at least 10 days between each).
National Grid (NESO) announces the Triads each March after the Triad season ends.

TNUoS (Transmission Network Use of System) charges are based on a supplier's
demand during the Triad half-hours. High demand during Triads = large TNUoS bills.

Triad charging formula (simplified):
  TNUoS charge = (customer MW demand during each Triad ÷ 2) * TNUoS tariff (£/kW/yr)
  TNUoS tariff: ~£70-100/kW/yr for residential Zone 14 (South East England)

Why this matters:
- TNUoS is a pass-through cost (supplier cannot avoid it)
- But suppliers who warn customers (ToU, I&C) to reduce demand during Triad
  events can reduce their collective exposure
- 2022-23: TNUoS rates soared due to reinforcement costs; big I&C customers
  subscribe to 'Triad warning' services to avoid charges

Observability:
- Historical Triads are published by NESO post-season
- The supplier can observe its own settlement data (Elexon)
- I&C customers often use consultants/aggregators for Triad management
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TriadSeason(str, Enum):
    Y2016_17 = "2016-17"
    Y2017_18 = "2017-18"
    Y2018_19 = "2018-19"
    Y2019_20 = "2019-20"
    Y2020_21 = "2020-21"
    Y2021_22 = "2021-22"
    Y2022_23 = "2022-23"
    Y2023_24 = "2023-24"
    Y2024_25 = "2024-25"


class CustomerExposureClass(str, Enum):
    HIGH = "high"       # significant demand during Triads
    MANAGED = "managed" # demand reduced by customer action
    LOW = "low"         # inherently low demand during Triads


@dataclass(frozen=True)
class TriadObservation:
    season: TriadSeason
    triad_number: int               # 1, 2, or 3
    settlement_date: dt.date
    settlement_period: int          # HH period 1-48
    national_demand_gw: float       # grid total demand at this period

    @property
    def is_valid(self) -> bool:
        return 1 <= self.triad_number <= 3 and 1 <= self.settlement_period <= 48


@dataclass(frozen=True)
class CustomerTriadExposure:
    account_id: str
    season: TriadSeason
    demand_mw_triad_1: float
    demand_mw_triad_2: float
    demand_mw_triad_3: float
    tnu_os_tariff_gbp_per_kw: float = 80.0   # typical residential Zone 14
    exposure_class: CustomerExposureClass = CustomerExposureClass.HIGH

    @property
    def avg_demand_mw(self) -> float:
        return (self.demand_mw_triad_1 + self.demand_mw_triad_2 + self.demand_mw_triad_3) / 3

    @property
    def tnu_os_charge_gbp(self) -> float:
        return self.avg_demand_mw * 1000 * self.tnu_os_tariff_gbp_per_kw

    def exposure_summary(self) -> str:
        return (
            "TriadExposure " + self.account_id + " " + self.season.value + ": "
            "avg=" + str(round(self.avg_demand_mw * 1000, 1)) + "kW "
            "TNUoS=GBP" + str(round(self.tnu_os_charge_gbp, 0))
        )


class TriadExposureRegister:

    def __init__(self) -> None:
        self._observations: List[TriadObservation] = []
        self._exposures: List[CustomerTriadExposure] = []

    def record_triad(self, obs: TriadObservation) -> TriadObservation:
        self._observations.append(obs)
        return obs

    def record_customer_exposure(self, exp: CustomerTriadExposure) -> CustomerTriadExposure:
        self._exposures.append(exp)
        return exp

    def triads_for_season(self, season: TriadSeason) -> List[TriadObservation]:
        return sorted(
            [o for o in self._observations if o.season == season],
            key=lambda o: o.triad_number,
        )

    def exposures_for_season(self, season: TriadSeason) -> List[CustomerTriadExposure]:
        return [e for e in self._exposures if e.season == season]

    def total_tnu_os_charge_gbp(self, season: TriadSeason) -> float:
        return sum(e.tnu_os_charge_gbp for e in self.exposures_for_season(season))

    def high_exposure_accounts(self, season: TriadSeason) -> List[CustomerTriadExposure]:
        return [
            e for e in self.exposures_for_season(season)
            if e.exposure_class == CustomerExposureClass.HIGH
        ]

    def triad_register_summary(self, season: TriadSeason) -> str:
        n_obs = len(self.triads_for_season(season))
        n_cust = len(self.exposures_for_season(season))
        total = self.total_tnu_os_charge_gbp(season)
        return (
            "Triad Register " + season.value + ": "
            + str(n_obs) + " Triads observed. "
            + str(n_cust) + " customer exposures. "
            "Total TNUoS: GBP" + str(round(total, 0)) + "."
        )
