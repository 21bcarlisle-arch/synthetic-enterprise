from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class PortalAction(str, Enum):
    LOGIN = 'login'
    VIEW_BILL = 'view_bill'
    DOWNLOAD_BILL = 'download_bill'
    SUBMIT_METER_READ = 'submit_meter_read'
    CHANGE_DIRECT_DEBIT = 'change_direct_debit'
    UPDATE_CONTACT_DETAILS = 'update_contact_details'
    VIEW_TARIFF = 'view_tariff'
    INITIATE_SWITCH = 'initiate_switch'
    RAISE_COMPLAINT = 'raise_complaint'
    VIEW_CONSUMPTION = 'view_consumption'
    ENROL_PAPERLESS = 'enrol_paperless'


_SELF_SERVE_ACTIONS = {
    PortalAction.SUBMIT_METER_READ,
    PortalAction.CHANGE_DIRECT_DEBIT,
    PortalAction.UPDATE_CONTACT_DETAILS,
    PortalAction.ENROL_PAPERLESS,
}


@dataclass(frozen=True)
class PortalEvent:
    event_id: str
    customer_id: str
    action: PortalAction
    event_datetime: dt.datetime
    session_id: str

    @property
    def is_self_serve(self) -> bool:
        return self.action in _SELF_SERVE_ACTIONS


class PortalAnalytics:
    def __init__(self) -> None:
        self._events: list[PortalEvent] = []
        self._next_id = 1

    def record(self, customer_id: str, action: PortalAction,
               event_datetime: dt.datetime, session_id: str) -> PortalEvent:
        ev = PortalEvent(
            event_id=f'PE-{self._next_id:06d}',
            customer_id=customer_id, action=action,
            event_datetime=event_datetime, session_id=session_id,
        )
        self._next_id += 1
        self._events.append(ev)
        return ev

    def events_in_period(self, from_dt: dt.datetime, to_dt: dt.datetime,
                         action: Optional[PortalAction] = None) -> List[PortalEvent]:
        recs = [e for e in self._events if from_dt <= e.event_datetime <= to_dt]
        if action:
            recs = [e for e in recs if e.action == action]
        return recs

    def unique_users(self, from_dt: dt.datetime, to_dt: dt.datetime) -> int:
        evs = self.events_in_period(from_dt, to_dt)
        return len(set(e.customer_id for e in evs))

    def self_serve_rate(self, from_dt: dt.datetime, to_dt: dt.datetime) -> Optional[float]:
        evs = self.events_in_period(from_dt, to_dt)
        if not evs:
            return None
        self_serve = sum(1 for e in evs if e.is_self_serve)
        return round(self_serve / len(evs) * 100, 1)

    def action_counts(self, from_dt: dt.datetime, to_dt: dt.datetime) -> Dict[str, int]:
        evs = self.events_in_period(from_dt, to_dt)
        counts: Dict[str, int] = {}
        for e in evs:
            counts[e.action.value] = counts.get(e.action.value, 0) + 1
        return counts

    def monthly_summary(self, year: int, month: int) -> dict:
        first = dt.datetime(year, month, 1, 0, 0, 0)
        last_day = 28 if month == 2 else 30 if month in {4, 6, 9, 11} else 31
        last = dt.datetime(year, month, last_day, 23, 59, 59)
        evs = self.events_in_period(first, last)
        return {
            'year': year,
            'month': month,
            'total_events': len(evs),
            'unique_users': self.unique_users(first, last),
            'self_serve_rate_pct': self.self_serve_rate(first, last),
            'action_counts': self.action_counts(first, last),
        }
