"""Renewables Obligation (RO) compliance ledger: ROCs, buyout, mutualisation."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ROCTechnology(str, Enum):
    ONSHORE_WIND = 'onshore_wind'
    OFFSHORE_WIND = 'offshore_wind'
    SOLAR_PV = 'solar_pv'
    HYDRO = 'hydro'
    ANAEROBIC_DIGESTION = 'anaerobic_digestion'
    BIOMASS = 'biomass'
    LANDFILL_GAS = 'landfill_gas'


_BUYOUT_PRICE_GBP_PER_ROC: Dict[int, float] = {
    2016: 44.33,
    2017: 46.20,
    2018: 47.22,
    2019: 48.78,
    2020: 50.05,
    2021: 50.80,
    2022: 54.35,
    2023: 60.28,
    2024: 62.10,
    2025: 63.80,
}

_RO_LEVEL_ROC_PER_MWH: Dict[int, float] = {
    2016: 0.341,
    2017: 0.328,
    2018: 0.310,
    2019: 0.295,
    2020: 0.279,
    2021: 0.272,
    2022: 0.259,
    2023: 0.246,
    2024: 0.234,
    2025: 0.223,
}


def get_buyout_price(year: int) -> float:
    return _BUYOUT_PRICE_GBP_PER_ROC.get(year, 63.80)


def get_ro_level(year: int) -> float:
    return _RO_LEVEL_ROC_PER_MWH.get(year, 0.223)


@dataclass(frozen=True)
class ROCPurchase:
    purchase_id: str
    technology: ROCTechnology
    rocs: float
    price_gbp_per_roc: float
    purchase_date: dt.date

    @property
    def total_cost_gbp(self) -> float:
        return round(self.rocs * self.price_gbp_per_roc, 2)


@dataclass
class ROCompliancePeriod:
    year: int
    supplied_mwh: float
    rocs_surrendered: float = 0.0
    buyout_rocs: float = 0.0

    @property
    def obligation_rocs(self) -> float:
        return round(self.supplied_mwh * get_ro_level(self.year), 1)

    @property
    def shortfall_rocs(self) -> float:
        return max(0.0, self.obligation_rocs - self.rocs_surrendered)

    @property
    def buyout_cost_gbp(self) -> float:
        return round(self.shortfall_rocs * get_buyout_price(self.year), 2)

    @property
    def compliance_pct(self) -> float:
        if self.obligation_rocs == 0:
            return 100.0
        return round(self.rocs_surrendered / self.obligation_rocs * 100, 1)

    @property
    def is_compliant(self) -> bool:
        return self.shortfall_rocs <= 0.01


class ROCLedger:
    def __init__(self) -> None:
        self._purchases: List[ROCPurchase] = []
        self._periods: Dict[int, ROCompliancePeriod] = {}
        self._purchase_counter = 0

    def buy_rocs(self, technology: ROCTechnology, rocs: float,
                   price_gbp_per_roc: float,
                   purchase_date: dt.date) -> ROCPurchase:
        self._purchase_counter += 1
        p = ROCPurchase(
            purchase_id=f'ROC-{self._purchase_counter:04d}',
            technology=technology, rocs=rocs,
            price_gbp_per_roc=price_gbp_per_roc,
            purchase_date=purchase_date,
        )
        self._purchases.append(p)
        return p

    def open_period(self, year: int, supplied_mwh: float) -> ROCompliancePeriod:
        p = ROCompliancePeriod(year=year, supplied_mwh=supplied_mwh)
        self._periods[year] = p
        return p

    def surrender_rocs(self, year: int, rocs: float) -> None:
        if year not in self._periods:
            raise KeyError(f'No compliance period open for {year}')
        self._periods[year].rocs_surrendered += rocs

    def get_period(self, year: int) -> Optional[ROCompliancePeriod]:
        return self._periods.get(year)

    def total_roc_spend_gbp(self, year: int) -> float:
        return round(sum(
            p.total_cost_gbp for p in self._purchases
            if p.purchase_date.year == year
        ), 2)

    def roc_summary(self, year: int) -> dict:
        period = self._periods.get(year)
        return {
            'year': year,
            'buyout_price_gbp': get_buyout_price(year),
            'ro_level_roc_per_mwh': get_ro_level(year),
            'obligation_rocs': period.obligation_rocs if period else None,
            'rocs_surrendered': period.rocs_surrendered if period else 0.0,
            'compliance_pct': period.compliance_pct if period else None,
            'buyout_cost_gbp': period.buyout_cost_gbp if period else 0.0,
            'roc_spend_gbp': self.total_roc_spend_gbp(year),
        }
