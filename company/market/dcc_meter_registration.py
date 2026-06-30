"""DCC Meter Registration Register (Phase GB).

When a SMETS2 smart meter is installed, it must be registered on the
Data Communications Company (DCC) communications network before remote
reads can begin.

DCC registration obligations (Smart Energy Code/SEC):
  - Installation must be reported to DCC within 10 working days
  - Registration must complete within 10 working days of installation
  - Failed registrations must be retried within 5 working days
  - Unregistered meters ("orphaned") after 90 days are a regulatory concern
  - Orphaned meters reported in quarterly SLC 21B returns to DESNZ

DCC operates the Home Area Network (HAN) and Wide Area Network (WAN)
infrastructure via Telefónica (North) and Arqiva (South).

The company can observe:
  - Which meters it has installed (its own installation records)
  - Which meters the DCC has confirmed as registered (DCC portal notifications)
  - Which meters remain unregistered after deadline

This module tracks per-meter DCC registration status for SLC 21B compliance.
SMETS1 meters do NOT go through DCC (legacy IHD/WAN) — only SMETS2.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_DCC_REGISTRATION_DEADLINE_DAYS = 10   # working days
_DCC_ORPHAN_THRESHOLD_DAYS = 90        # calendar days
_DCC_RETRY_DEADLINE_WORKING_DAYS = 5   # after a failed registration


def _add_working_days(start: dt.date, n: int) -> dt.date:
    """Return the date n working days after start (skips weekends only)."""
    current = start
    remaining = n
    while remaining > 0:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


class DCCRegistrationStatus(str, Enum):
    PENDING = "pending"              # installation reported; awaiting DCC confirmation
    REGISTERED = "registered"        # DCC confirmed; remote reads enabled
    FAILED = "failed"                # DCC rejected (e.g. comms fault, incorrect MPAN)
    ORPHANED = "orphaned"            # >90 calendar days, still unregistered
    DEREGISTERED = "deregistered"    # meter removed / customer left; explicitly closed


@dataclass(frozen=True)
class DCCRegistrationRecord:
    record_id: str                      # DCC-NNNNN
    mpan: str                           # 13-digit electricity meter point
    install_date: dt.date
    meter_serial: str
    status: DCCRegistrationStatus = DCCRegistrationStatus.PENDING
    registered_date: Optional[dt.date] = None
    failed_date: Optional[dt.date] = None
    retry_count: int = 0

    @property
    def registration_deadline(self) -> dt.date:
        return _add_working_days(self.install_date, _DCC_REGISTRATION_DEADLINE_DAYS)

    @property
    def is_registered(self) -> bool:
        return self.status == DCCRegistrationStatus.REGISTERED

    @property
    def is_pending(self) -> bool:
        return self.status == DCCRegistrationStatus.PENDING

    @property
    def is_failed(self) -> bool:
        return self.status == DCCRegistrationStatus.FAILED

    @property
    def is_orphaned(self) -> bool:
        return self.status == DCCRegistrationStatus.ORPHANED

    def is_overdue_as_of(self, as_of: dt.date) -> bool:
        if self.status not in (DCCRegistrationStatus.PENDING, DCCRegistrationStatus.FAILED):
            return False
        return as_of > self.registration_deadline

    def is_orphan_candidate_as_of(self, as_of: dt.date) -> bool:
        """Eligible to be marked orphaned: pending/failed for >90 calendar days."""
        if self.status not in (DCCRegistrationStatus.PENDING, DCCRegistrationStatus.FAILED):
            return False
        return (as_of - self.install_date).days > _DCC_ORPHAN_THRESHOLD_DAYS

    def days_since_install(self, as_of: dt.date) -> int:
        return (as_of - self.install_date).days

    def record_summary(self) -> str:
        return (
            f"DCC {self.record_id} MPAN={self.mpan} "
            f"({self.status.value}) installed={self.install_date} "
            f"deadline={self.registration_deadline} retries={self.retry_count}"
        )


class DCCMeterRegistrationRegister:

    def __init__(self) -> None:
        self._records: List[DCCRegistrationRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"DCC-{self._counter:05d}"

    def register_installation(
        self, mpan: str, install_date: dt.date, meter_serial: str
    ) -> DCCRegistrationRecord:
        record = DCCRegistrationRecord(
            record_id=self._next_id(),
            mpan=mpan,
            install_date=install_date,
            meter_serial=meter_serial,
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> DCCRegistrationRecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = DCCRegistrationRecord(
                    record_id=r.record_id,
                    mpan=r.mpan,
                    install_date=r.install_date,
                    meter_serial=r.meter_serial,
                    status=kwargs.get("status", r.status),
                    registered_date=kwargs.get("registered_date", r.registered_date),
                    failed_date=kwargs.get("failed_date", r.failed_date),
                    retry_count=kwargs.get("retry_count", r.retry_count),
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"DCC registration record {record_id} not found")

    def mark_registered(
        self, record_id: str, registered_date: dt.date
    ) -> DCCRegistrationRecord:
        return self._update(
            record_id,
            status=DCCRegistrationStatus.REGISTERED,
            registered_date=registered_date,
        )

    def mark_failed(
        self, record_id: str, failed_date: dt.date
    ) -> DCCRegistrationRecord:
        for r in self._records:
            if r.record_id == record_id:
                return self._update(
                    record_id,
                    status=DCCRegistrationStatus.FAILED,
                    failed_date=failed_date,
                    retry_count=r.retry_count + 1,
                )
        raise KeyError(f"DCC registration record {record_id} not found")

    def mark_orphaned(self, record_id: str) -> DCCRegistrationRecord:
        return self._update(record_id, status=DCCRegistrationStatus.ORPHANED)

    def deregister(self, record_id: str) -> DCCRegistrationRecord:
        return self._update(record_id, status=DCCRegistrationStatus.DEREGISTERED)

    def pending_registrations(self) -> List[DCCRegistrationRecord]:
        return [r for r in self._records if r.is_pending]

    def overdue_registrations(self, as_of: dt.date) -> List[DCCRegistrationRecord]:
        return [r for r in self._records if r.is_overdue_as_of(as_of)]

    def failed_registrations(self) -> List[DCCRegistrationRecord]:
        return [r for r in self._records if r.is_failed]

    def orphaned_meters(self) -> List[DCCRegistrationRecord]:
        return [r for r in self._records if r.is_orphaned]

    def orphan_candidates(self, as_of: dt.date) -> List[DCCRegistrationRecord]:
        return [r for r in self._records if r.is_orphan_candidate_as_of(as_of)]

    def registered_meters(self) -> List[DCCRegistrationRecord]:
        return [r for r in self._records if r.is_registered]

    def registration_rate_pct(self) -> Optional[float]:
        active = [
            r for r in self._records
            if r.status != DCCRegistrationStatus.DEREGISTERED
        ]
        if not active:
            return None
        n_registered = sum(1 for r in active if r.is_registered)
        return round(100.0 * n_registered / len(active), 2)

    def total_retry_count(self) -> int:
        return sum(r.retry_count for r in self._records)

    def dcc_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_reg = len(self.registered_meters())
        n_pend = len(self.pending_registrations())
        n_fail = len(self.failed_registrations())
        n_orp = len(self.orphaned_meters())
        n_overdue = len(self.overdue_registrations(as_of))
        rate = self.registration_rate_pct()
        rate_str = f"{rate:.1f}%" if rate is not None else "n/a"
        return (
            f"DCC Meter Registration ({as_of}): {n} installations, "
            f"{n_reg} registered ({rate_str}), {n_pend} pending, "
            f"{n_fail} failed, {n_orp} orphaned, {n_overdue} overdue."
        )
