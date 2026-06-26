from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class DSRStatus(str, Enum):
    ENROLLED = 'enrolled'
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    WITHDRAWN = 'withdrawn'


class DispatchResult(str, Enum):
    DELIVERED = 'delivered'
    PARTIAL = 'partial'
    NON_DELIVERY = 'non_delivery'
    CANCELLED = 'cancelled'


@dataclass(frozen=True)
class DSRParticipant:
    customer_id: str
    mpan: str
    contracted_mw: float
    enrolled_date: dt.date
    status: DSRStatus = DSRStatus.ENROLLED
    payment_per_mwh_gbp: float = 0.0


@dataclass(frozen=True)
class DispatchEvent:
    event_id: str
    customer_id: str
    requested_mw: float
    delivered_mw: float
    dispatch_start: dt.datetime
    dispatch_end: dt.datetime
    result: DispatchResult
    payment_gbp: float

    @property
    def duration_hours(self) -> float:
        delta = self.dispatch_end - self.dispatch_start
        return round(delta.total_seconds() / 3600, 2)

    @property
    def delivered_mwh(self) -> float:
        return round(self.delivered_mw * self.duration_hours, 3)

    @property
    def delivery_rate(self) -> float:
        if self.requested_mw <= 0:
            return 0.0
        return round(self.delivered_mw / self.requested_mw * 100, 1)


class DSRBook:
    def __init__(self) -> None:
        self._participants: dict[str, DSRParticipant] = {}
        self._events: list[DispatchEvent] = []
        self._next_event = 1

    def enroll(self, customer_id: str, mpan: str, contracted_mw: float,
               enrolled_date: dt.date, payment_per_mwh_gbp: float = 50.0) -> DSRParticipant:
        p = DSRParticipant(
            customer_id=customer_id, mpan=mpan, contracted_mw=contracted_mw,
            enrolled_date=enrolled_date, status=DSRStatus.ACTIVE,
            payment_per_mwh_gbp=payment_per_mwh_gbp,
        )
        self._participants[customer_id] = p
        return p

    def dispatch(self, customer_id: str, requested_mw: float,
                 dispatch_start: dt.datetime, dispatch_end: dt.datetime,
                 delivered_mw: float) -> DispatchEvent:
        p = self._participants[customer_id]
        if p.status != DSRStatus.ACTIVE:
            raise ValueError(f'Customer {customer_id} is not active in DSR programme')
        duration_hours = (dispatch_end - dispatch_start).total_seconds() / 3600
        delivered_mwh = delivered_mw * duration_hours
        payment = round(delivered_mwh * p.payment_per_mwh_gbp, 2)
        result = DispatchResult.NON_DELIVERY
        if delivered_mw >= requested_mw * 0.95:
            result = DispatchResult.DELIVERED
        elif delivered_mw > 0:
            result = DispatchResult.PARTIAL
        event_id = f'DSR-{self._next_event:04d}'
        self._next_event += 1
        ev = DispatchEvent(
            event_id=event_id, customer_id=customer_id,
            requested_mw=requested_mw, delivered_mw=delivered_mw,
            dispatch_start=dispatch_start, dispatch_end=dispatch_end,
            result=result, payment_gbp=payment,
        )
        self._events.append(ev)
        return ev

    def events_for_customer(self, customer_id: str) -> List[DispatchEvent]:
        return [e for e in self._events if e.customer_id == customer_id]

    def total_contracted_mw(self) -> float:
        return round(
            sum(p.contracted_mw for p in self._participants.values()
                if p.status == DSRStatus.ACTIVE), 2)

    def total_payments_gbp(self, year: int) -> float:
        return round(sum(e.payment_gbp for e in self._events
                         if e.dispatch_start.year == year), 2)

    def delivery_rate_year(self, year: int) -> Optional[float]:
        year_events = [e for e in self._events
                       if e.dispatch_start.year == year
                       and e.result != DispatchResult.CANCELLED]
        if not year_events:
            return None
        return round(sum(e.delivery_rate for e in year_events) / len(year_events), 1)

    def annual_summary(self, year: int) -> dict:
        year_events = [e for e in self._events if e.dispatch_start.year == year]
        delivered = sum(1 for e in year_events if e.result == DispatchResult.DELIVERED)
        return {
            'year': year,
            'dispatch_events': len(year_events),
            'full_deliveries': delivered,
            'total_payments_gbp': self.total_payments_gbp(year),
            'avg_delivery_rate_pct': self.delivery_rate_year(year),
            'active_participants': sum(1 for p in self._participants.values()
                                      if p.status == DSRStatus.ACTIVE),
        }
