"""Global Reputation Index (Phase EB).

The CTO Architecture Guidance mandates the GRI as a first-class behavioral
physics entity. High GRI = Activation Energy multiplier > 1 (customers forgive
minor friction). Low GRI = multiplier < 1 (portfolio-wide churn acceleration).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ReputationBand(str, Enum):
    STRONG = "strong"          # GRI >= 70
    ADEQUATE = "adequate"      # 50 <= GRI < 70
    WEAK = "weak"              # 30 <= GRI < 50
    CRISIS = "crisis"          # GRI < 30


class ReputationEventType(str, Enum):
    COMPLAINT_RESOLVED_ON_TIME = "complaint_resolved_on_time"
    COMPLAINT_RESOLVED_LATE = "complaint_resolved_late"
    COMPLAINT_UPHELD_AT_OMBUDSMAN = "complaint_upheld_at_ombudsman"
    OFGEM_ENFORCEMENT_ACTION = "ofgem_enforcement_action"
    SLC_BREACH_PUBLISHED = "slc_breach_published"
    EXCEPTIONAL_SERVICE = "exceptional_service"
    TARIFF_TRANSPARENCY_AWARD = "tariff_transparency_award"
    PRICE_GOUGING_ALLEGATION = "price_gouging_allegation"
    SUCCESSFUL_DEBT_RESOLUTION = "successful_debt_resolution"


_GRI_IMPACT: Dict[ReputationEventType, float] = {
    ReputationEventType.COMPLAINT_RESOLVED_ON_TIME: +0.5,
    ReputationEventType.COMPLAINT_RESOLVED_LATE: -1.0,
    ReputationEventType.COMPLAINT_UPHELD_AT_OMBUDSMAN: -3.0,
    ReputationEventType.OFGEM_ENFORCEMENT_ACTION: -12.0,
    ReputationEventType.SLC_BREACH_PUBLISHED: -5.0,
    ReputationEventType.EXCEPTIONAL_SERVICE: +2.0,
    ReputationEventType.TARIFF_TRANSPARENCY_AWARD: +4.0,
    ReputationEventType.PRICE_GOUGING_ALLEGATION: -8.0,
    ReputationEventType.SUCCESSFUL_DEBT_RESOLUTION: +1.0,
}

_GRI_BASELINE = 50.0
_GRI_MIN = 0.0
_GRI_MAX = 100.0

_ACTIVATION_ENERGY_MULTIPLIER: Dict[ReputationBand, float] = {
    ReputationBand.STRONG: 1.3,
    ReputationBand.ADEQUATE: 1.0,
    ReputationBand.WEAK: 0.7,
    ReputationBand.CRISIS: 0.5,
}


@dataclass(frozen=True)
class ReputationEvent:
    event_type: ReputationEventType
    occurred_at: dt.date
    gri_delta: float
    description: str = ""


class GlobalReputationIndex:
    """Portfolio-level reputation score that amplifies or dampens churn risk."""

    def __init__(self, starting_gri: float = _GRI_BASELINE) -> None:
        self._starting_gri = starting_gri
        self._events: List[ReputationEvent] = []

    def record(
        self,
        event_type: ReputationEventType,
        occurred_at: dt.date,
        description: str = "",
        amplifier: float = 1.0,
    ) -> ReputationEvent:
        base_delta = _GRI_IMPACT[event_type]
        event = ReputationEvent(
            event_type=event_type,
            occurred_at=occurred_at,
            gri_delta=base_delta * amplifier,
            description=description,
        )
        self._events.append(event)
        return event

    def score(self, as_of: dt.date) -> float:
        gri = self._starting_gri
        for event in sorted(self._events, key=lambda e: e.occurred_at):
            if event.occurred_at > as_of:
                break
            gri += event.gri_delta
            gri = max(_GRI_MIN, min(_GRI_MAX, gri))
        return gri

    def band(self, as_of: dt.date) -> ReputationBand:
        s = self.score(as_of)
        if s >= 70:
            return ReputationBand.STRONG
        if s >= 50:
            return ReputationBand.ADEQUATE
        if s >= 30:
            return ReputationBand.WEAK
        return ReputationBand.CRISIS

    def activation_energy_multiplier(self, as_of: dt.date) -> float:
        return _ACTIVATION_ENERGY_MULTIPLIER[self.band(as_of)]

    def events_in_period(
        self, start: dt.date, end: dt.date
    ) -> List[ReputationEvent]:
        return [e for e in self._events if start <= e.occurred_at <= end]

    def worst_event_in_period(
        self, start: dt.date, end: dt.date
    ) -> Optional[ReputationEvent]:
        events = self.events_in_period(start, end)
        if not events:
            return None
        return min(events, key=lambda e: e.gri_delta)

    def trend(self, months: int, as_of: dt.date) -> str:
        total_m = as_of.year * 12 + as_of.month - months
        y, m = divmod(total_m, 12)
        if m == 0:
            y -= 1
            m = 12
        try:
            prior = dt.date(y, m, as_of.day)
        except ValueError:
            prior = dt.date(y, m, 28)
        start_score = self.score(prior)
        end_score = self.score(as_of)
        delta = end_score - start_score
        if delta > 2:
            return "improving"
        if delta < -2:
            return "declining"
        return "stable"

    def gri_summary(self, as_of: dt.date) -> str:
        s = self.score(as_of)
        b = self.band(as_of)
        ae = self.activation_energy_multiplier(as_of)
        n = len(self._events)
        return (
            f"Global Reputation Index: {s:.1f}/100 ({b.value}). "
            f"Activation Energy multiplier: x{ae:.1f}. "
            f"{n} reputation events recorded."
        )
