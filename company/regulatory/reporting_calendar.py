"""Regulatory reporting calendar: submission deadlines and overdue detection."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ReportingFrequency(str, Enum):
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    ANNUAL = 'annual'
    AD_HOC = 'ad_hoc'


class DeadlineStatus(str, Enum):
    PENDING = 'pending'
    SUBMITTED = 'submitted'
    OVERDUE = 'overdue'
    WAIVED = 'waived'


@dataclass(frozen=True)
class RegulatoryDeadline:
    deadline_id: str
    name: str
    regulator: str
    frequency: ReportingFrequency
    due_date: dt.date
    submitted_date: Optional[dt.date] = None
    notes: str = ''

    def status(self, as_of: dt.date) -> DeadlineStatus:
        if self.submitted_date is not None:
            return DeadlineStatus.SUBMITTED
        if as_of > self.due_date:
            return DeadlineStatus.OVERDUE
        return DeadlineStatus.PENDING

    @property
    def is_submitted(self) -> bool:
        return self.submitted_date is not None

    def days_until_due(self, as_of: dt.date) -> int:
        return (self.due_date - as_of).days


class RegulatoryCalendar:
    def __init__(self) -> None:
        self._deadlines: List[RegulatoryDeadline] = []
        self._submitted: dict[str, dt.date] = {}

    def add_deadline(self, deadline_id: str, name: str, regulator: str,
                      frequency: ReportingFrequency, due_date: dt.date,
                      notes: str = '') -> RegulatoryDeadline:
        dl = RegulatoryDeadline(
            deadline_id=deadline_id, name=name, regulator=regulator,
            frequency=frequency, due_date=due_date, notes=notes,
        )
        self._deadlines.append(dl)
        return dl

    def mark_submitted(self, deadline_id: str, submitted_date: dt.date) -> RegulatoryDeadline:
        idx = next(i for i, d in enumerate(self._deadlines) if d.deadline_id == deadline_id)
        old = self._deadlines[idx]
        new = RegulatoryDeadline(
            deadline_id=old.deadline_id, name=old.name, regulator=old.regulator,
            frequency=old.frequency, due_date=old.due_date,
            submitted_date=submitted_date, notes=old.notes,
        )
        self._deadlines[idx] = new
        return new

    def overdue(self, as_of: dt.date) -> List[RegulatoryDeadline]:
        return [d for d in self._deadlines if d.status(as_of) == DeadlineStatus.OVERDUE]

    def due_within_days(self, as_of: dt.date, days: int) -> List[RegulatoryDeadline]:
        return [d for d in self._deadlines
                if d.status(as_of) == DeadlineStatus.PENDING
                and 0 <= d.days_until_due(as_of) <= days]

    def by_regulator(self, regulator: str) -> List[RegulatoryDeadline]:
        return [d for d in self._deadlines if d.regulator == regulator]

    def calendar_summary(self, as_of: dt.date) -> dict:
        submitted = sum(1 for d in self._deadlines if d.status(as_of) == DeadlineStatus.SUBMITTED)
        pending = sum(1 for d in self._deadlines if d.status(as_of) == DeadlineStatus.PENDING)
        overdue = sum(1 for d in self._deadlines if d.status(as_of) == DeadlineStatus.OVERDUE)
        return {
            'as_of': as_of.isoformat(),
            'total': len(self._deadlines),
            'submitted': submitted,
            'pending': pending,
            'overdue': overdue,
            'due_within_14_days': len(self.due_within_days(as_of, 14)),
        }
