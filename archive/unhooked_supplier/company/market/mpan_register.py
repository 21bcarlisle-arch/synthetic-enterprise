from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class MPANStatus(str, Enum):
    REGISTERED = 'registered'
    DEREGISTERED = 'deregistered'
    PENDING_REGISTRATION = 'pending_registration'
    PENDING_SWITCH = 'pending_switch'
    ENERGISED = 'energised'
    DE_ENERGISED = 'de_energised'
    OBJECTED = 'objected'


class ProfileClass(int, Enum):
    PC1 = 1
    PC2 = 2
    PC3 = 3
    PC4 = 4
    PC5 = 5
    PC6 = 6
    PC7 = 7
    PC8 = 8


_PC_DESCRIPTIONS = {
    ProfileClass.PC1: 'Domestic Unrestricted',
    ProfileClass.PC2: 'Domestic Economy 7',
    ProfileClass.PC3: 'Non-Domestic Unrestricted',
    ProfileClass.PC4: 'Non-Domestic Economy 7',
    ProfileClass.PC5: 'Non-Domestic (MD <=100kW, settled HH)',
    ProfileClass.PC6: 'Non-Domestic (MD 100-500kW)',
    ProfileClass.PC7: 'Non-Domestic (MD 500kW-1MW)',
    ProfileClass.PC8: 'Non-Domestic (MD >1MW)',
}


@dataclass(frozen=True)
class MPANRecord:
    mpan: str
    status: MPANStatus
    profile_class: ProfileClass
    measurement_class: str
    registered_date: dt.date
    current_supplier_id: str
    deregistered_date: Optional[dt.date] = None
    pending_switch_date: Optional[dt.date] = None

    @property
    def is_active(self) -> bool:
        return self.status not in {MPANStatus.DEREGISTERED, MPANStatus.DE_ENERGISED}

    @property
    def profile_class_description(self) -> str:
        return _PC_DESCRIPTIONS.get(self.profile_class, 'Unknown')


class MPANRegister:
    def __init__(self) -> None:
        self._records: dict[str, MPANRecord] = {}

    def register(self, mpan: str, profile_class: ProfileClass, measurement_class: str,
                 registered_date: dt.date, supplier_id: str) -> MPANRecord:
        record = MPANRecord(
            mpan=mpan, status=MPANStatus.REGISTERED,
            profile_class=profile_class, measurement_class=measurement_class,
            registered_date=registered_date, current_supplier_id=supplier_id,
        )
        self._records[mpan] = record
        return record

    def initiate_switch(self, mpan: str, switch_date: dt.date) -> MPANRecord:
        old = self._records[mpan]
        updated = MPANRecord(
            mpan=old.mpan, status=MPANStatus.PENDING_SWITCH,
            profile_class=old.profile_class, measurement_class=old.measurement_class,
            registered_date=old.registered_date, current_supplier_id=old.current_supplier_id,
            pending_switch_date=switch_date,
        )
        self._records[mpan] = updated
        return updated

    def complete_switch(self, mpan: str, new_supplier_id: str, switch_date: dt.date) -> MPANRecord:
        old = self._records[mpan]
        updated = MPANRecord(
            mpan=old.mpan, status=MPANStatus.REGISTERED,
            profile_class=old.profile_class, measurement_class=old.measurement_class,
            registered_date=switch_date, current_supplier_id=new_supplier_id,
        )
        self._records[mpan] = updated
        return updated

    def object_to_switch(self, mpan: str) -> MPANRecord:
        old = self._records[mpan]
        updated = MPANRecord(
            mpan=old.mpan, status=MPANStatus.OBJECTED,
            profile_class=old.profile_class, measurement_class=old.measurement_class,
            registered_date=old.registered_date, current_supplier_id=old.current_supplier_id,
        )
        self._records[mpan] = updated
        return updated

    def deregister(self, mpan: str, deregistered_date: dt.date) -> MPANRecord:
        old = self._records[mpan]
        updated = MPANRecord(
            mpan=old.mpan, status=MPANStatus.DEREGISTERED,
            profile_class=old.profile_class, measurement_class=old.measurement_class,
            registered_date=old.registered_date, current_supplier_id=old.current_supplier_id,
            deregistered_date=deregistered_date,
        )
        self._records[mpan] = updated
        return updated

    def get(self, mpan: str) -> Optional[MPANRecord]:
        return self._records.get(mpan)

    def active_mpans(self) -> List[MPANRecord]:
        return [r for r in self._records.values() if r.is_active]

    def pending_switches(self) -> List[MPANRecord]:
        return [r for r in self._records.values() if r.status == MPANStatus.PENDING_SWITCH]

    def by_profile_class(self, pc: ProfileClass) -> List[MPANRecord]:
        return [r for r in self._records.values() if r.profile_class == pc and r.is_active]

    def portfolio_summary(self) -> dict:
        active = self.active_mpans()
        return {
            'total_active': len(active),
            'pending_switches': len(self.pending_switches()),
            'by_profile_class': {
                pc.name: len(self.by_profile_class(pc)) for pc in ProfileClass
            },
        }
