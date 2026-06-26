from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class MPRNStatus(str, Enum):
    REGISTERED = 'registered'
    DEREGISTERED = 'deregistered'
    PENDING_REGISTRATION = 'pending_registration'
    PENDING_SWITCH = 'pending_switch'
    DISCONNECTED = 'disconnected'
    OBJECTED = 'objected'


class GasConsumptionBand(str, Enum):
    DOMESTIC = 'domestic'
    SMALL_NON_DOMESTIC = 'small_non_domestic'
    MEDIUM_NON_DOMESTIC = 'medium_non_domestic'
    LARGE_NON_DOMESTIC = 'large_non_domestic'


_BAND_AQ_THRESHOLD_KWH = {
    GasConsumptionBand.DOMESTIC: 73_200.0,
    GasConsumptionBand.SMALL_NON_DOMESTIC: 293_000.0,
    GasConsumptionBand.MEDIUM_NON_DOMESTIC: 732_000.0,
}


def classify_gas_band(annual_quantity_kwh: float) -> GasConsumptionBand:
    if annual_quantity_kwh <= _BAND_AQ_THRESHOLD_KWH[GasConsumptionBand.DOMESTIC]:
        return GasConsumptionBand.DOMESTIC
    if annual_quantity_kwh <= _BAND_AQ_THRESHOLD_KWH[GasConsumptionBand.SMALL_NON_DOMESTIC]:
        return GasConsumptionBand.SMALL_NON_DOMESTIC
    if annual_quantity_kwh <= _BAND_AQ_THRESHOLD_KWH[GasConsumptionBand.MEDIUM_NON_DOMESTIC]:
        return GasConsumptionBand.MEDIUM_NON_DOMESTIC
    return GasConsumptionBand.LARGE_NON_DOMESTIC


@dataclass(frozen=True)
class MPRNRecord:
    mprn: str
    status: MPRNStatus
    annual_quantity_kwh: float
    registered_date: dt.date
    current_supplier_id: str
    deregistered_date: Optional[dt.date] = None
    pending_switch_date: Optional[dt.date] = None

    @property
    def consumption_band(self) -> GasConsumptionBand:
        return classify_gas_band(self.annual_quantity_kwh)

    @property
    def is_active(self) -> bool:
        return self.status not in {MPRNStatus.DEREGISTERED, MPRNStatus.DISCONNECTED}


class MPRNRegister:
    def __init__(self) -> None:
        self._records: dict[str, MPRNRecord] = {}

    def register(self, mprn: str, annual_quantity_kwh: float,
                 registered_date: dt.date, supplier_id: str) -> MPRNRecord:
        record = MPRNRecord(
            mprn=mprn, status=MPRNStatus.REGISTERED,
            annual_quantity_kwh=annual_quantity_kwh,
            registered_date=registered_date, current_supplier_id=supplier_id,
        )
        self._records[mprn] = record
        return record

    def initiate_switch(self, mprn: str, switch_date: dt.date) -> MPRNRecord:
        old = self._records[mprn]
        updated = MPRNRecord(
            mprn=old.mprn, status=MPRNStatus.PENDING_SWITCH,
            annual_quantity_kwh=old.annual_quantity_kwh,
            registered_date=old.registered_date, current_supplier_id=old.current_supplier_id,
            pending_switch_date=switch_date,
        )
        self._records[mprn] = updated
        return updated

    def complete_switch(self, mprn: str, new_supplier_id: str,
                        switch_date: dt.date) -> MPRNRecord:
        old = self._records[mprn]
        updated = MPRNRecord(
            mprn=old.mprn, status=MPRNStatus.REGISTERED,
            annual_quantity_kwh=old.annual_quantity_kwh,
            registered_date=switch_date, current_supplier_id=new_supplier_id,
        )
        self._records[mprn] = updated
        return updated

    def deregister(self, mprn: str, deregistered_date: dt.date) -> MPRNRecord:
        old = self._records[mprn]
        updated = MPRNRecord(
            mprn=old.mprn, status=MPRNStatus.DEREGISTERED,
            annual_quantity_kwh=old.annual_quantity_kwh,
            registered_date=old.registered_date, current_supplier_id=old.current_supplier_id,
            deregistered_date=deregistered_date,
        )
        self._records[mprn] = updated
        return updated

    def get(self, mprn: str) -> Optional[MPRNRecord]:
        return self._records.get(mprn)

    def active_mprns(self) -> List[MPRNRecord]:
        return [r for r in self._records.values() if r.is_active]

    def by_band(self, band: GasConsumptionBand) -> List[MPRNRecord]:
        return [r for r in self._records.values() if r.is_active and r.consumption_band == band]

    def portfolio_summary(self) -> dict:
        active = self.active_mprns()
        return {
            'total_active': len(active),
            'pending_switches': sum(1 for r in active if r.status == MPRNStatus.PENDING_SWITCH),
            'total_aq_kwh': round(sum(r.annual_quantity_kwh for r in active), 0),
            'by_band': {b.value: len(self.by_band(b)) for b in GasConsumptionBand},
        }
