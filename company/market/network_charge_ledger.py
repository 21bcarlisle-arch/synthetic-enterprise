"""Network charge pass-through ledger: TNUoS, DUoS, BSUoS tracking."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class NetworkChargeType(str, Enum):
    TNUOS = 'tnuos'
    DUOS = 'duos'
    BSUOS = 'bsuos'
    CMSUOS = 'cmsuos'
    METERING = 'metering'


@dataclass(frozen=True)
class NetworkChargeRate:
    year: int
    charge_type: NetworkChargeType
    commodity: str
    rate_gbp_per_mwh: float
    notes: str = ''


@dataclass(frozen=True)
class NetworkChargeRecord:
    customer_id: str
    mpan: str
    period_start: dt.date
    period_end: dt.date
    charge_type: NetworkChargeType
    consumption_mwh: float
    rate_gbp_per_mwh: float

    @property
    def charge_gbp(self) -> float:
        return round(self.consumption_mwh * self.rate_gbp_per_mwh, 2)


class NetworkChargeLedger:
    def __init__(self) -> None:
        self._rates: List[NetworkChargeRate] = []
        self._records: List[NetworkChargeRecord] = []

    def set_rate(self, year: int, charge_type: NetworkChargeType,
                  commodity: str, rate_gbp_per_mwh: float,
                  notes: str = '') -> NetworkChargeRate:
        rate = NetworkChargeRate(
            year=year, charge_type=charge_type, commodity=commodity,
            rate_gbp_per_mwh=rate_gbp_per_mwh, notes=notes,
        )
        self._rates.append(rate)
        return rate

    def get_rate(self, year: int, charge_type: NetworkChargeType,
                  commodity: str) -> Optional[float]:
        matches = [r for r in self._rates
                   if r.year == year and r.charge_type == charge_type
                   and r.commodity == commodity]
        if not matches:
            return None
        return matches[-1].rate_gbp_per_mwh

    def post_charge(self, customer_id: str, mpan: str,
                     period_start: dt.date, period_end: dt.date,
                     charge_type: NetworkChargeType, consumption_mwh: float,
                     rate_gbp_per_mwh: float) -> NetworkChargeRecord:
        rec = NetworkChargeRecord(
            customer_id=customer_id, mpan=mpan,
            period_start=period_start, period_end=period_end,
            charge_type=charge_type, consumption_mwh=consumption_mwh,
            rate_gbp_per_mwh=rate_gbp_per_mwh,
        )
        self._records.append(rec)
        return rec

    def total_charges_gbp(self, customer_id: str,
                           period_start: dt.date, period_end: dt.date) -> float:
        return round(sum(
            r.charge_gbp for r in self._records
            if r.customer_id == customer_id
            and r.period_start <= period_end and r.period_end >= period_start
        ), 2)

    def charges_by_type(self, year: int) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for r in self._records:
            if r.period_start.year <= year <= r.period_end.year:
                k = r.charge_type.value
                result[k] = round(result.get(k, 0.0) + r.charge_gbp, 2)
        return result

    def portfolio_total_gbp(self, year: int) -> float:
        return round(sum(v for v in self.charges_by_type(year).values()), 2)

    def annual_summary(self, year: int) -> dict:
        return {
            'year': year,
            'total_gbp': self.portfolio_total_gbp(year),
            'by_type': self.charges_by_type(year),
            'record_count': len([r for r in self._records
                                  if r.period_start.year <= year <= r.period_end.year]),
        }
