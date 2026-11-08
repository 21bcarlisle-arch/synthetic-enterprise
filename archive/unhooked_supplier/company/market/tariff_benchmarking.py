"""Tariff Benchmarking Register (Phase EZ).

The company monitors competitor tariff prices to:
1. Set competitive pricing (not too high = churn; not too low = margin squeeze)
2. Trigger repricing when the market moves significantly
3. Support the activation energy model (if competitor tariffs are lower,
   perceived saving = difference in annual bill)

Data sources (all publicly observable):
- Ofgem comparison tool (public API)
- uSwitch / Energyguide published tariff data
- BEIS DUKES quarterly domestic prices
- Competitor press releases and tariff notices

This module models a rolling snapshot of market tariff benchmarks,
enabling the company to track its relative price position.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class SupplierRank(str, Enum):
    CHEAPEST = "cheapest"       # company is cheapest in market
    BELOW_AVERAGE = "below_average"
    AVERAGE = "average"
    ABOVE_AVERAGE = "above_average"
    MOST_EXPENSIVE = "most_expensive"


class TariffType(str, Enum):
    SVT = "svt"             # Standard Variable
    FIXED_12M = "fixed_12m"
    FIXED_24M = "fixed_24m"
    GREEN = "green"
    TOU = "tou"             # Time-of-Use


@dataclass(frozen=True)
class CompetitorTariff:
    supplier_name: str
    tariff_type: TariffType
    snapshot_date: dt.date
    electricity_unit_rate_pence: float
    electricity_standing_charge_pence: float
    annual_bill_gbp_typical: float   # at 2,900 kWh/yr Ofgem typical consumption

    def annual_bill_at(self, consumption_kwh: float) -> float:
        unit_cost = consumption_kwh * self.electricity_unit_rate_pence / 100
        standing = 365 * self.electricity_standing_charge_pence / 100
        return unit_cost + standing


@dataclass(frozen=True)
class TariffBenchmarkSnapshot:
    snapshot_date: dt.date
    tariff_type: TariffType
    company_unit_rate_pence: float
    competitor_tariffs: tuple  # of CompetitorTariff

    @property
    def all_unit_rates(self) -> list:
        rates = [t.electricity_unit_rate_pence for t in self.competitor_tariffs]
        rates.append(self.company_unit_rate_pence)
        return sorted(rates)

    @property
    def market_avg_rate_pence(self) -> float:
        if not self.competitor_tariffs:
            return self.company_unit_rate_pence
        all_rates = [t.electricity_unit_rate_pence for t in self.competitor_tariffs]
        return sum(all_rates) / len(all_rates)

    @property
    def company_premium_pence(self) -> float:
        return self.company_unit_rate_pence - self.market_avg_rate_pence

    @property
    def is_above_market(self) -> bool:
        return self.company_unit_rate_pence > self.market_avg_rate_pence

    @property
    def supplier_rank(self) -> SupplierRank:
        n = len(self.competitor_tariffs)
        if n == 0:
            return SupplierRank.AVERAGE
        cheaper_count = sum(
            1 for t in self.competitor_tariffs
            if t.electricity_unit_rate_pence < self.company_unit_rate_pence
        )
        pct_cheaper = 100.0 * cheaper_count / n
        if pct_cheaper == 0:
            return SupplierRank.CHEAPEST
        if pct_cheaper <= 25:
            return SupplierRank.BELOW_AVERAGE
        if pct_cheaper <= 75:
            return SupplierRank.AVERAGE
        if pct_cheaper < 100:
            return SupplierRank.ABOVE_AVERAGE
        return SupplierRank.MOST_EXPENSIVE

    def benchmark_summary(self) -> str:
        return (
            "Tariff Benchmark (" + str(self.snapshot_date) + " " + self.tariff_type.value + "): "
            "company=" + str(round(self.company_unit_rate_pence, 2)) + "p "
            "market_avg=" + str(round(self.market_avg_rate_pence, 2)) + "p "
            "premium=" + str(round(self.company_premium_pence, 2)) + "p "
            "rank=" + self.supplier_rank.value
        )


class TariffBenchmarkingRegister:

    def __init__(self) -> None:
        self._snapshots: List[TariffBenchmarkSnapshot] = []

    def record(self, snapshot: TariffBenchmarkSnapshot) -> TariffBenchmarkSnapshot:
        self._snapshots.append(snapshot)
        return snapshot

    def latest_for(self, tariff_type: TariffType) -> Optional[TariffBenchmarkSnapshot]:
        matching = [s for s in self._snapshots if s.tariff_type == tariff_type]
        if not matching:
            return None
        return max(matching, key=lambda s: s.snapshot_date)

    def snapshots_above_market(self) -> List[TariffBenchmarkSnapshot]:
        return [s for s in self._snapshots if s.is_above_market]

    def avg_company_premium_pence(self) -> float:
        if not self._snapshots:
            return 0.0
        return sum(s.company_premium_pence for s in self._snapshots) / len(self._snapshots)

    def tariff_benchmark_summary(self, as_of: dt.date) -> str:
        n = len(self._snapshots)
        n_above = len(self.snapshots_above_market())
        avg_prem = self.avg_company_premium_pence()
        return (
            "Tariff Benchmarking (" + str(as_of) + "): "
            + str(n) + " snapshots. "
            "Above market: " + str(n_above) + ". "
            "Avg premium: " + str(round(avg_prem, 2)) + "p/kWh."
        )
