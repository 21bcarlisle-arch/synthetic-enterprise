"""Demand side response (DSR) event management: grid stress, customer curtailment."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class DSREventType(str, Enum):
    GRID_STRESS = 'grid_stress'
    FREQUENCY_RESPONSE = 'frequency_response'
    TRIAD_AVOIDANCE = 'triad_avoidance'
    CAPACITY_MARKET_DISPATCH = 'capacity_market_dispatch'
    VOLUNTARY = 'voluntary'


class CurtailmentStatus(str, Enum):
    NOTIFIED = 'notified'
    COMPLIED = 'complied'
    PARTIAL = 'partial'
    NON_COMPLIANT = 'non_compliant'
    EXEMPTED = 'exempted'


@dataclass
class DSREvent:
    event_id: str
    event_type: DSREventType
    start_datetime: dt.datetime
    end_datetime: dt.datetime
    target_mw_reduction: float
    notice_given_minutes: int

    @property
    def duration_hours(self) -> float:
        return (self.end_datetime - self.start_datetime).total_seconds() / 3600

    @property
    def target_mwh(self) -> float:
        return round(self.target_mw_reduction * self.duration_hours, 2)

    @property
    def is_short_notice(self) -> bool:
        return self.notice_given_minutes < 30


@dataclass
class CustomerCurtailment:
    customer_id: str
    event_id: str
    contracted_reduction_kw: float
    actual_reduction_kw: float
    status: CurtailmentStatus = CurtailmentStatus.NOTIFIED
    revenue_gbp: float = 0.0

    @property
    def compliance_pct(self) -> float:
        if self.contracted_reduction_kw <= 0:
            return 0.0
        return round(self.actual_reduction_kw / self.contracted_reduction_kw * 100, 1)


class DSRPortfolio:
    def __init__(self) -> None:
        self._events: List[DSREvent] = []
        self._curtailments: List[CustomerCurtailment] = []

    def create_event(self, event_id: str, event_type: DSREventType,
                       start: dt.datetime, end: dt.datetime,
                       target_mw: float, notice_minutes: int) -> DSREvent:
        ev = DSREvent(
            event_id=event_id, event_type=event_type,
            start_datetime=start, end_datetime=end,
            target_mw_reduction=target_mw, notice_given_minutes=notice_minutes,
        )
        self._events.append(ev)
        return ev

    def record_curtailment(self, customer_id: str, event_id: str,
                             contracted_kw: float, actual_kw: float,
                             revenue_gbp: float = 0.0) -> CustomerCurtailment:
        status = CurtailmentStatus.NOTIFIED
        if actual_kw >= contracted_kw * 0.95:
            status = CurtailmentStatus.COMPLIED
        elif actual_kw > 0:
            status = CurtailmentStatus.PARTIAL
        else:
            status = CurtailmentStatus.NON_COMPLIANT
        c = CustomerCurtailment(
            customer_id=customer_id, event_id=event_id,
            contracted_reduction_kw=contracted_kw, actual_reduction_kw=actual_kw,
            status=status, revenue_gbp=revenue_gbp,
        )
        self._curtailments.append(c)
        return c

    def total_mwh_delivered(self, event_id: str) -> float:
        ev = next((e for e in self._events if e.event_id == event_id), None)
        if not ev:
            return 0.0
        total_kw = sum(
            c.actual_reduction_kw for c in self._curtailments
            if c.event_id == event_id
        )
        return round(total_kw / 1000 * ev.duration_hours, 3)

    def compliance_rate_pct(self, event_id: str) -> Optional[float]:
        curtailments = [c for c in self._curtailments if c.event_id == event_id]
        if not curtailments:
            return None
        complied = sum(1 for c in curtailments if c.status == CurtailmentStatus.COMPLIED)
        return round(complied / len(curtailments) * 100, 1)

    def annual_revenue_gbp(self, year: int) -> float:
        return round(sum(
            c.revenue_gbp for c in self._curtailments
            if any(e.event_id == c.event_id and e.start_datetime.year == year
                   for e in self._events)
        ), 2)

    def dsr_summary(self, year: int) -> dict:
        yr_events = [e for e in self._events if e.start_datetime.year == year]
        return {
            'year': year,
            'events': len(yr_events),
            'total_target_mwh': round(sum(e.target_mwh for e in yr_events), 2),
            'annual_revenue_gbp': self.annual_revenue_gbp(year),
            'participating_customers': len(set(
                c.customer_id for c in self._curtailments
                if any(e.event_id == c.event_id and e.start_datetime.year == year
                       for e in self._events)
            )),
        }
