"""Supplier of Last Resort (SoLR) exposure: competitor failure, customer transfer pricing."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class SoLREventStatus(str, Enum):
    ANNOUNCED = 'announced'
    ACTIVE = 'active'
    CUSTOMERS_TRANSFERRED = 'customers_transferred'
    COMPLETED = 'completed'


_SOLR_LEVY_HISTORY_GBP_PER_MWH: Dict[int, float] = {
    2016: 0.5,
    2017: 0.5,
    2018: 1.2,
    2019: 1.5,
    2020: 2.0,
    2021: 4.14,
    2022: 10.0,  # Bulb SAR + BSC shortfall recovery peak
    2023: 6.5,
    2024: 3.0,
    2025: 2.5,
}


def get_solr_levy_gbp_per_mwh(year: int) -> float:
    if year in _SOLR_LEVY_HISTORY_GBP_PER_MWH:
        return _SOLR_LEVY_HISTORY_GBP_PER_MWH[year]
    return _SOLR_LEVY_HISTORY_GBP_PER_MWH.get(
        max(k for k in _SOLR_LEVY_HISTORY_GBP_PER_MWH if k <= year),
        2.5,
    )


@dataclass
class SoLREvent:
    event_id: str
    failed_supplier: str
    announcement_date: dt.date
    customer_count_transferred: int
    avg_annual_kwh_per_customer: float
    status: SoLREventStatus = SoLREventStatus.ANNOUNCED
    transfer_date: Optional[dt.date] = None
    appointed_solr: Optional[str] = None
    legacy_credit_gbp: float = 0.0

    @property
    def total_annual_kwh(self) -> float:
        return self.customer_count_transferred * self.avg_annual_kwh_per_customer

    @property
    def total_annual_mwh(self) -> float:
        return self.total_annual_kwh / 1000

    def levy_cost_gbp(self, year: int) -> float:
        rate = get_solr_levy_gbp_per_mwh(year)
        return round(self.total_annual_mwh * rate, 2)


@dataclass(frozen=True)
class SoLRAcquisitionPrice:
    event_id: str
    offered_unit_rate_pence: float
    offered_standing_pence: float
    acquisition_premium_pct: float

    @property
    def is_above_svt(self) -> bool:
        return self.acquisition_premium_pct > 0


class SoLRBook:
    def __init__(self) -> None:
        self._events: List[SoLREvent] = []

    def record_event(self, event_id: str, failed_supplier: str,
                       announcement_date: dt.date, customer_count: int,
                       avg_annual_kwh: float, legacy_credit_gbp: float = 0.0) -> SoLREvent:
        ev = SoLREvent(
            event_id=event_id, failed_supplier=failed_supplier,
            announcement_date=announcement_date,
            customer_count_transferred=customer_count,
            avg_annual_kwh_per_customer=avg_annual_kwh,
            legacy_credit_gbp=legacy_credit_gbp,
        )
        self._events.append(ev)
        return ev

    def get(self, event_id: str) -> Optional[SoLREvent]:
        return next((e for e in self._events if e.event_id == event_id), None)

    def complete_transfer(self, event_id: str, transfer_date: dt.date,
                            appointed_solr: str) -> None:
        ev = self.get(event_id)
        if ev:
            ev.transfer_date = transfer_date
            ev.appointed_solr = appointed_solr
            ev.status = SoLREventStatus.CUSTOMERS_TRANSFERRED

    def annual_levy_cost_gbp(self, year: int) -> float:
        return round(sum(e.levy_cost_gbp(year) for e in self._events), 2)

    def total_legacy_credit_gbp(self) -> float:
        return round(sum(e.legacy_credit_gbp for e in self._events), 2)

    def events_summary(self, year: int) -> dict:
        yr_events = [e for e in self._events
                      if e.announcement_date.year == year]
        return {
            'year': year,
            'events_count': len(yr_events),
            'customers_affected': sum(e.customer_count_transferred for e in yr_events),
            'annual_levy_gbp': self.annual_levy_cost_gbp(year),
            'total_legacy_credit_gbp': self.total_legacy_credit_gbp(),
            'levy_rate_gbp_per_mwh': get_solr_levy_gbp_per_mwh(year),
        }
