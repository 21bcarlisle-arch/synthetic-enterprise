"""Change of Tenancy (CoT) Register (Phase GK).

When a property changes occupant (tenant moves in/moves out, property
sold, landlord re-occupying), the energy supply must transfer.
Debt is associated with the person not the property (SLC 27/SLC 12.2).
New tenant gets a fresh deemed contract supply from day 1 of possession.
Cannot withhold supply due to previous tenant debt.
Abandonment: 3 contact attempts over 28 days with no response.
"""
from __future__ import annotations
import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_COT_READ_DAYS = 10
_MPAS_NOTIFY_DAYS = 2
_ABANDON_ATTEMPTS = 3
_ABANDON_DAYS = 28


def _add_working_days(start: dt.date, n: int) -> dt.date:
    current = start
    added = 0
    while added < n:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


class CoTType(str, Enum):
    NEW_TENANT = "new_tenant"
    NEW_OWNER = "new_owner"
    LANDLORD_RETURNING = "landlord_returning"
    EMPTY_PROPERTY = "empty_property"
    VOID_PERIOD = "void_period"


class CoTStatus(str, Enum):
    NOTIFIED = "notified"
    SUPPLY_TAKEN = "supply_taken"
    SUPPLY_DECLINED = "supply_declined"
    ABANDONED = "abandoned"
    CLOSED = "closed"


_OPEN = frozenset({CoTStatus.NOTIFIED, CoTStatus.SUPPLY_TAKEN})
_TERMINAL = frozenset({CoTStatus.SUPPLY_DECLINED, CoTStatus.ABANDONED, CoTStatus.CLOSED})


@dataclass(frozen=True)
class CoTRecord:
    cot_id: str
    mpan: str
    entry_date: dt.date
    cot_type: CoTType
    status: CoTStatus = CoTStatus.NOTIFIED
    account_id: Optional[str] = None
    entry_meter_read: Optional[float] = None
    contact_attempts: int = 0
    supply_start_date: Optional[dt.date] = None
    closed_date: Optional[dt.date] = None

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    @property
    def is_terminal(self) -> bool:
        return self.status in _TERMINAL

    @property
    def mpas_notification_due(self) -> dt.date:
        return _add_working_days(self.entry_date, _MPAS_NOTIFY_DAYS)

    @property
    def read_submission_due(self) -> dt.date:
        return _add_working_days(self.entry_date, _COT_READ_DAYS)

    def is_abandon_candidate(self, as_of: dt.date) -> bool:
        return (
            self.status == CoTStatus.NOTIFIED
            and self.contact_attempts >= _ABANDON_ATTEMPTS
            and (as_of - self.entry_date).days >= _ABANDON_DAYS
        )

    def cot_summary(self) -> str:
        acct = self.account_id or "unassigned"
        return (
            "CoT " + self.cot_id + " mpan=" + self.mpan
            + " [" + self.cot_type.value + "]"
            + " entry=" + str(self.entry_date)
            + " acct=" + acct
            + " [" + self.status.value + "]"
        )


class ChangeOfTenancyRegister:

    def __init__(self) -> None:
        self._records: List[CoTRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "COT-" + str(self._counter).zfill(5)

    def notify_cot(
        self,
        mpan: str,
        entry_date: dt.date,
        cot_type: CoTType = CoTType.NEW_TENANT,
        entry_meter_read: Optional[float] = None,
    ) -> CoTRecord:
        record = CoTRecord(
            cot_id=self._next_id(),
            mpan=mpan,
            entry_date=entry_date,
            cot_type=cot_type,
            entry_meter_read=entry_meter_read,
        )
        self._records.append(record)
        return record

    def _update(self, cot_id: str, **kwargs) -> CoTRecord:
        for i, r in enumerate(self._records):
            if r.cot_id == cot_id:
                updated = CoTRecord(
                    cot_id=r.cot_id, mpan=r.mpan, entry_date=r.entry_date,
                    cot_type=r.cot_type,
                    status=kwargs.get("status", r.status),
                    account_id=kwargs.get("account_id", r.account_id),
                    entry_meter_read=kwargs.get("entry_meter_read", r.entry_meter_read),
                    contact_attempts=kwargs.get("contact_attempts", r.contact_attempts),
                    supply_start_date=kwargs.get("supply_start_date", r.supply_start_date),
                    closed_date=kwargs.get("closed_date", r.closed_date),
                )
                self._records[i] = updated
                return updated
        raise KeyError("CoT record " + cot_id + " not found")

    def accept_supply(self, cot_id: str, account_id: str, supply_start_date: dt.date) -> CoTRecord:
        return self._update(cot_id, status=CoTStatus.SUPPLY_TAKEN,
                           account_id=account_id, supply_start_date=supply_start_date)

    def decline_supply(self, cot_id: str) -> CoTRecord:
        return self._update(cot_id, status=CoTStatus.SUPPLY_DECLINED)

    def log_contact_attempt(self, cot_id: str) -> CoTRecord:
        for r in self._records:
            if r.cot_id == cot_id:
                return self._update(cot_id, contact_attempts=r.contact_attempts + 1)
        raise KeyError("CoT record " + cot_id + " not found")

    def mark_abandoned(self, cot_id: str) -> CoTRecord:
        return self._update(cot_id, status=CoTStatus.ABANDONED)

    def close(self, cot_id: str, closed_date: dt.date) -> CoTRecord:
        return self._update(cot_id, status=CoTStatus.CLOSED, closed_date=closed_date)

    def open_cots(self) -> List[CoTRecord]:
        return [r for r in self._records if r.is_open]

    def abandon_candidates(self, as_of: dt.date) -> List[CoTRecord]:
        return [r for r in self._records if r.is_abandon_candidate(as_of)]

    def history_for_mpan(self, mpan: str) -> List[CoTRecord]:
        return [r for r in self._records if r.mpan == mpan]

    def active_supply_for_mpan(self, mpan: str) -> Optional[CoTRecord]:
        taken = [r for r in self._records if r.mpan == mpan and r.status == CoTStatus.SUPPLY_TAKEN]
        return max(taken, key=lambda r: r.entry_date) if taken else None

    def by_type(self, cot_type: CoTType) -> List[CoTRecord]:
        return [r for r in self._records if r.cot_type == cot_type]

    def conversion_rate_pct(self) -> Optional[float]:
        taken = sum(1 for r in self._records if r.status == CoTStatus.SUPPLY_TAKEN)
        terminal = sum(1 for r in self._records if r.is_terminal)
        if terminal == 0:
            return None
        return round(taken / (taken + terminal) * 100, 1)

    def cot_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_open = len(self.open_cots())
        n_abandon = len(self.abandon_candidates(as_of))
        cr = self.conversion_rate_pct()
        cr_str = (str(cr) + "%") if cr is not None else "n/a"
        return (
            "CoT Register (" + str(as_of) + "): " + str(n) + " CoTs ("
            + str(n_open) + " open, " + str(n_abandon) + " abandon candidates). "
            + "Conversion: " + cr_str + "."
        )
