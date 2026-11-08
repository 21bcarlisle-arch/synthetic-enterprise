"""Metering services: Meter Operator (MOP) and Data Collector (DC) contracts."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class MeteringServiceType(str, Enum):
    MOP = 'mop'   # Meter Operator
    DC = 'dc'     # Data Collector
    DA = 'da'     # Data Aggregator
    MAM = 'mam'   # Meter Asset Manager


class MeterType(str, Enum):
    CREDIT = 'credit'
    PREPAYMENT = 'prepayment'
    SMART = 'smart'  # SMETS2
    HH = 'hh'        # Half-hourly


class ServiceCallType(str, Enum):
    METER_READ = 'meter_read'
    METER_INSTALL = 'meter_install'
    METER_EXCHANGE = 'meter_exchange'
    METER_REMOVAL = 'meter_removal'
    FAULT_REPAIR = 'fault_repair'
    SMART_COMMISSIONING = 'smart_commissioning'


_MOP_RATE_GBP_PER_METER_PER_YEAR: Dict[MeterType, float] = {
    MeterType.CREDIT: 18.0,
    MeterType.PREPAYMENT: 22.0,
    MeterType.SMART: 28.0,
    MeterType.HH: 45.0,
}

_DC_RATE_GBP_PER_METER_PER_YEAR: Dict[MeterType, float] = {
    MeterType.CREDIT: 12.0,
    MeterType.PREPAYMENT: 14.0,
    MeterType.SMART: 16.0,
    MeterType.HH: 30.0,
}


@dataclass(frozen=True)
class MeteringContract:
    provider_id: str
    service_type: MeteringServiceType
    meter_type: MeterType
    start_date: dt.date
    end_date: Optional[dt.date]
    mpan: str

    @property
    def annual_cost_gbp(self) -> float:
        if self.service_type == MeteringServiceType.MOP:
            return _MOP_RATE_GBP_PER_METER_PER_YEAR.get(self.meter_type, 20.0)
        if self.service_type == MeteringServiceType.DC:
            return _DC_RATE_GBP_PER_METER_PER_YEAR.get(self.meter_type, 12.0)
        return 10.0

    def is_active(self, as_of: dt.date) -> bool:
        if as_of < self.start_date:
            return False
        if self.end_date and as_of > self.end_date:
            return False
        return True

    def cost_for_period_gbp(self, from_date: dt.date, to_date: dt.date) -> float:
        days = (to_date - from_date).days
        return round(self.annual_cost_gbp / 365 * days, 2)


@dataclass(frozen=True)
class ServiceCall:
    call_id: str
    mpan: str
    call_type: ServiceCallType
    call_date: dt.date
    cost_gbp: float
    completed: bool = True


class MeteringContractManager:
    def __init__(self) -> None:
        self._contracts: List[MeteringContract] = []
        self._service_calls: List[ServiceCall] = []
        self._call_counter = 0

    def register_contract(self, provider_id: str, service_type: MeteringServiceType,
                            meter_type: MeterType, mpan: str,
                            start_date: dt.date,
                            end_date: Optional[dt.date] = None) -> MeteringContract:
        c = MeteringContract(
            provider_id=provider_id, service_type=service_type,
            meter_type=meter_type, start_date=start_date,
            end_date=end_date, mpan=mpan,
        )
        self._contracts.append(c)
        return c

    def log_service_call(self, mpan: str, call_type: ServiceCallType,
                           call_date: dt.date, cost_gbp: float,
                           completed: bool = True) -> ServiceCall:
        self._call_counter += 1
        sc = ServiceCall(
            call_id=f'SC-{self._call_counter:04d}',
            mpan=mpan, call_type=call_type, call_date=call_date,
            cost_gbp=cost_gbp, completed=completed,
        )
        self._service_calls.append(sc)
        return sc

    def active_contracts(self, as_of: dt.date,
                           service_type: Optional[MeteringServiceType] = None
                           ) -> List[MeteringContract]:
        return [c for c in self._contracts if c.is_active(as_of)
                 and (service_type is None or c.service_type == service_type)]

    def annual_contract_cost_gbp(self, year: int) -> float:
        as_of = dt.date(year, 12, 31)
        return round(sum(
            c.annual_cost_gbp for c in self.active_contracts(as_of)
        ), 2)

    def service_call_cost_gbp(self, year: int) -> float:
        return round(sum(
            sc.cost_gbp for sc in self._service_calls if sc.call_date.year == year
        ), 2)

    def metering_summary(self, year: int) -> dict:
        as_of = dt.date(year, 12, 31)
        return {
            'year': year,
            'active_contracts': len(self.active_contracts(as_of)),
            'annual_contract_cost_gbp': self.annual_contract_cost_gbp(year),
            'service_call_cost_gbp': self.service_call_cost_gbp(year),
        }
