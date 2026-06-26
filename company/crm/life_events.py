from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class LifeEventType(str, Enum):
    BIRTH = 'birth'
    DEATH = 'death'
    MARRIAGE = 'marriage'
    DIVORCE = 'divorce'
    JOB_LOSS = 'job_loss'
    JOB_GAIN = 'job_gain'
    RETIREMENT = 'retirement'
    SERIOUS_ILLNESS = 'serious_illness'
    MOVE_IN = 'move_in'
    MOVE_OUT = 'move_out'
    BENEFIT_CHANGE = 'benefit_change'


_VULNERABILITY_EVENTS = {
    LifeEventType.JOB_LOSS,
    LifeEventType.SERIOUS_ILLNESS,
    LifeEventType.RETIREMENT,
    LifeEventType.DEATH,
    LifeEventType.DIVORCE,
    LifeEventType.BENEFIT_CHANGE,
}

_OCCUPANCY_CHANGE_EVENTS = {
    LifeEventType.BIRTH,
    LifeEventType.DEATH,
    LifeEventType.MOVE_IN,
    LifeEventType.MOVE_OUT,
    LifeEventType.MARRIAGE,
    LifeEventType.DIVORCE,
}


@dataclass
class LifeEvent:
    customer_id: str
    event_type: LifeEventType
    event_date: date
    notes: str = ''
    occupancy_delta: int = 0

    @property
    def triggers_vulnerability_review(self) -> bool:
        return self.event_type in _VULNERABILITY_EVENTS

    @property
    def triggers_occupancy_change(self) -> bool:
        return self.event_type in _OCCUPANCY_CHANGE_EVENTS

    @property
    def triggers_cot(self) -> bool:
        return self.event_type in (LifeEventType.MOVE_IN, LifeEventType.MOVE_OUT)

    @property
    def triggers_psr_review(self) -> bool:
        return self.event_type in {
            LifeEventType.SERIOUS_ILLNESS,
            LifeEventType.RETIREMENT,
            LifeEventType.DEATH,
        }


@dataclass
class LifeEventLog:
    _events: List[LifeEvent] = field(default_factory=list)

    def record(self, event: LifeEvent) -> LifeEvent:
        self._events.append(event)
        return event

    def events_for_customer(self, customer_id: str) -> List[LifeEvent]:
        return [e for e in self._events if e.customer_id == customer_id]

    def pending_vulnerability_reviews(self, since: date) -> List[LifeEvent]:
        return [
            e for e in self._events
            if e.triggers_vulnerability_review and e.event_date >= since
        ]

    def pending_cot_triggers(self, since: date) -> List[LifeEvent]:
        return [
            e for e in self._events
            if e.triggers_cot and e.event_date >= since
        ]

    def pending_psr_reviews(self, since: date) -> List[LifeEvent]:
        return [
            e for e in self._events
            if e.triggers_psr_review and e.event_date >= since
        ]

    def annual_summary(self, year: int) -> dict:
        year_events = [e for e in self._events if e.event_date.year == year]
        by_type: dict[str, int] = {}
        for e in year_events:
            by_type[e.event_type.value] = by_type.get(e.event_type.value, 0) + 1
        vulnerability_triggers = sum(1 for e in year_events if e.triggers_vulnerability_review)
        cot_triggers = sum(1 for e in year_events if e.triggers_cot)
        result = dict(
            year=year,
            total=len(year_events),
            vulnerability_triggers=vulnerability_triggers,
            cot_triggers=cot_triggers,
            by_type=by_type,
        )
        return result
