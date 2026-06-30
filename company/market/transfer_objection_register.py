"""Transfer Objection Register (Phase GO).

When a customer initiates a switch to a new supplier, the losing
supplier can raise an objection under the Central Switching Service
(CSS) rules. CSS launched June 2023; objection window = 5 WD.

Valid objection grounds (CSS Rules Section 14):
  UNPAID_DEBT: customer has a debt balance >£0 for supply owed to
    the losing supplier; the debt does NOT transfer; the switch still
    proceeds but the objection is noted for debt recovery
  METER_DISPUTE: there is an active disputed meter read that has not
    been resolved; prevents finalising the exit read
  CONTRACT_DISPUTE: existing contract has not been legally resolved;
    e.g., the customer claims the contract is invalid
  COOLING_OFF: customer is still within the 14-day cooling-off period
    for a previous contract with the losing supplier
  REGULATORY_RESTRICTION: e.g., disconnection process in progress

Invalid objection grounds:
  Raising an objection purely to delay/block switching is a breach
  of SLC 14 and Ofgem has issued enforcement notices for this.

Key rule: debt alone does NOT block a switch (SLC 14.5); the switch
proceeds, debt follows the customer, supplier must pursue separately.

Connects to: css_performance_register.py (overall CSS performance),
erroneous_transfer.py (wrongful transfers).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_OBJECTION_WINDOW_WD = 5


def _add_wd(start: dt.date, n: int) -> dt.date:
    cur = start
    added = 0
    while added < n:
        cur += dt.timedelta(days=1)
        if cur.weekday() < 5:
            added += 1
    return cur


class ObjectionGround(str, Enum):
    UNPAID_DEBT = "unpaid_debt"
    METER_DISPUTE = "meter_dispute"
    CONTRACT_DISPUTE = "contract_dispute"
    COOLING_OFF = "cooling_off"
    REGULATORY_RESTRICTION = "regulatory_restriction"


class ObjectionStatus(str, Enum):
    RAISED = "raised"
    VALID = "valid"
    INVALID = "invalid"
    RESOLVED = "resolved"
    WITHDRAWN = "withdrawn"


_OPEN = frozenset({ObjectionStatus.RAISED, ObjectionStatus.VALID})


@dataclass(frozen=True)
class TransferObjectionRecord:
    objection_id: str
    mpan: str
    switch_ref: str
    objection_date: dt.date
    ground: ObjectionGround
    status: ObjectionStatus = ObjectionStatus.RAISED
    resolution_date: Optional[dt.date] = None
    notes: str = ""

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    @property
    def objection_deadline(self) -> dt.date:
        return _add_wd(self.objection_date, _OBJECTION_WINDOW_WD)

    def resolution_days(self, as_of: dt.date) -> int:
        end = self.resolution_date if self.resolution_date is not None else as_of
        return (end - self.objection_date).days

    def objection_summary(self) -> str:
        return (
            "OBJ " + self.objection_id + " mpan=" + self.mpan
            + " switch=" + self.switch_ref
            + " ground=" + self.ground.value
            + " [" + self.status.value + "]"
        )


class TransferObjectionRegister:

    def __init__(self) -> None:
        self._records: List[TransferObjectionRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "OBJ-" + str(self._counter).zfill(5)

    def raise_objection(
        self, mpan: str, switch_ref: str, objection_date: dt.date,
        ground: ObjectionGround, notes: str = "",
    ) -> TransferObjectionRecord:
        record = TransferObjectionRecord(
            objection_id=self._next_id(),
            mpan=mpan, switch_ref=switch_ref,
            objection_date=objection_date,
            ground=ground, notes=notes,
        )
        self._records.append(record)
        return record

    def _update(self, objection_id: str, **kwargs) -> TransferObjectionRecord:
        for i, r in enumerate(self._records):
            if r.objection_id == objection_id:
                updated = TransferObjectionRecord(
                    objection_id=r.objection_id,
                    mpan=r.mpan, switch_ref=r.switch_ref,
                    objection_date=r.objection_date,
                    ground=r.ground,
                    status=kwargs.get("status", r.status),
                    resolution_date=kwargs.get("resolution_date", r.resolution_date),
                    notes=kwargs.get("notes", r.notes),
                )
                self._records[i] = updated
                return updated
        raise KeyError("Objection " + objection_id + " not found")

    def mark_valid(self, objection_id: str) -> TransferObjectionRecord:
        return self._update(objection_id, status=ObjectionStatus.VALID)

    def mark_invalid(self, objection_id: str) -> TransferObjectionRecord:
        return self._update(objection_id, status=ObjectionStatus.INVALID)

    def resolve(self, objection_id: str, resolution_date: dt.date) -> TransferObjectionRecord:
        return self._update(objection_id, status=ObjectionStatus.RESOLVED,
                           resolution_date=resolution_date)

    def withdraw(self, objection_id: str) -> TransferObjectionRecord:
        return self._update(objection_id, status=ObjectionStatus.WITHDRAWN)

    def open_objections(self) -> List[TransferObjectionRecord]:
        return [r for r in self._records if r.is_open]

    def invalid_objections(self) -> List[TransferObjectionRecord]:
        return [r for r in self._records if r.status == ObjectionStatus.INVALID]

    def by_ground(self, ground: ObjectionGround) -> List[TransferObjectionRecord]:
        return [r for r in self._records if r.ground == ground]

    def by_switch(self, switch_ref: str) -> List[TransferObjectionRecord]:
        return [r for r in self._records if r.switch_ref == switch_ref]

    def average_resolution_days(self, as_of: dt.date) -> Optional[float]:
        resolved = [r for r in self._records
                    if r.status in (ObjectionStatus.RESOLVED, ObjectionStatus.INVALID,
                                   ObjectionStatus.WITHDRAWN)]
        if not resolved:
            return None
        return round(sum(r.resolution_days(as_of) for r in resolved) / len(resolved), 1)

    def invalid_rate_pct(self) -> Optional[float]:
        terminal = [r for r in self._records
                    if r.status not in (ObjectionStatus.RAISED, ObjectionStatus.VALID)]
        if not terminal:
            return None
        invalid = sum(1 for r in terminal if r.status == ObjectionStatus.INVALID)
        return round(invalid / len(terminal) * 100, 1)

    def objection_register_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_open = len(self.open_objections())
        n_invalid = len(self.invalid_objections())
        return (
            "Transfer Objection Register (" + str(as_of) + "): "
            + str(n) + " objections ("
            + str(n_open) + " open, "
            + str(n_invalid) + " invalid)."
        )
