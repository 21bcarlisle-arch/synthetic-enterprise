from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class SwitchDirection(str, Enum):
    GAIN = 'gain'
    LOSS = 'loss'


class SwitchStatus(str, Enum):
    INITIATED = 'initiated'
    COMPLETED = 'completed'
    OBJECTED = 'objected'
    CANCELLED = 'cancelled'
    ERRONEOUS = 'erroneous'


@dataclass(frozen=True)
class SwitchEvent:
    event_id: str
    mpan: str
    customer_id: Optional[str]
    direction: SwitchDirection
    losing_supplier: str
    gaining_supplier: str
    initiation_date: dt.date
    completion_date: Optional[dt.date] = None
    status: SwitchStatus = SwitchStatus.INITIATED
    erroneous_transfer: bool = False

    @property
    def days_to_complete(self) -> Optional[int]:
        if self.completion_date is None:
            return None
        return (self.completion_date - self.initiation_date).days

    @property
    def is_completed(self) -> bool:
        return self.status == SwitchStatus.COMPLETED


class SwitchAnalytics:
    def __init__(self, our_supplier_id: str) -> None:
        self._supplier_id = our_supplier_id
        self._events: list[SwitchEvent] = []
        self._next_id = 1

    def record(self, mpan: str, customer_id: Optional[str], direction: SwitchDirection,
               losing_supplier: str, gaining_supplier: str,
               initiation_date: dt.date) -> SwitchEvent:
        event_id = f'SW-{self._next_id:05d}'
        self._next_id += 1
        ev = SwitchEvent(
            event_id=event_id, mpan=mpan, customer_id=customer_id,
            direction=direction, losing_supplier=losing_supplier,
            gaining_supplier=gaining_supplier, initiation_date=initiation_date,
        )
        self._events.append(ev)
        return ev

    def _replace_event(self, event_id: str, **kwargs):
        for i, ev in enumerate(self._events):
            if ev.event_id == event_id:
                old = ev
                updated = SwitchEvent(
                    event_id=old.event_id, mpan=old.mpan, customer_id=old.customer_id,
                    direction=old.direction, losing_supplier=old.losing_supplier,
                    gaining_supplier=old.gaining_supplier,
                    initiation_date=old.initiation_date,
                    completion_date=kwargs.get('completion_date', old.completion_date),
                    status=kwargs.get('status', old.status),
                    erroneous_transfer=kwargs.get('erroneous_transfer', old.erroneous_transfer),
                )
                self._events[i] = updated
                return updated
        raise KeyError(event_id)

    def complete(self, event_id: str, completion_date: dt.date) -> SwitchEvent:
        return self._replace_event(event_id, status=SwitchStatus.COMPLETED,
                                   completion_date=completion_date)

    def mark_erroneous(self, event_id: str) -> SwitchEvent:
        return self._replace_event(event_id, status=SwitchStatus.ERRONEOUS,
                                   erroneous_transfer=True)

    def object(self, event_id: str) -> SwitchEvent:
        return self._replace_event(event_id, status=SwitchStatus.OBJECTED)

    def gains_in_year(self, year: int) -> List[SwitchEvent]:
        return [e for e in self._events
                if e.direction == SwitchDirection.GAIN
                and e.initiation_date.year == year]

    def losses_in_year(self, year: int) -> List[SwitchEvent]:
        return [e for e in self._events
                if e.direction == SwitchDirection.LOSS
                and e.initiation_date.year == year]

    def erroneous_transfers_in_year(self, year: int) -> List[SwitchEvent]:
        return [e for e in self._events
                if e.erroneous_transfer and e.initiation_date.year == year]

    def avg_days_to_complete(self, year: int) -> Optional[float]:
        completed = [e.days_to_complete for e in self._events
                     if e.is_completed and e.completion_date is not None
                     and e.initiation_date.year == year
                     and e.days_to_complete is not None]
        if not completed:
            return None
        return round(sum(completed) / len(completed), 1)

    def net_customer_change(self, year: int) -> int:
        return len(self.gains_in_year(year)) - len(self.losses_in_year(year))

    def annual_summary(self, year: int) -> dict:
        gains = self.gains_in_year(year)
        losses = self.losses_in_year(year)
        return {
            'year': year,
            'gains': len(gains),
            'losses': len(losses),
            'net': len(gains) - len(losses),
            'erroneous_transfers': len(self.erroneous_transfers_in_year(year)),
            'avg_days_to_complete': self.avg_days_to_complete(year),
        }
