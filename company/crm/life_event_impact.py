from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from company.crm.life_events import LifeEvent, LifeEventType


class ImpactSeverity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


_SEVERITY: dict[LifeEventType, ImpactSeverity] = {
    LifeEventType.BIRTH: ImpactSeverity.LOW,
    LifeEventType.DEATH: ImpactSeverity.HIGH,
    LifeEventType.MARRIAGE: ImpactSeverity.LOW,
    LifeEventType.DIVORCE: ImpactSeverity.MODERATE,
    LifeEventType.JOB_LOSS: ImpactSeverity.HIGH,
    LifeEventType.JOB_GAIN: ImpactSeverity.LOW,
    LifeEventType.RETIREMENT: ImpactSeverity.MODERATE,
    LifeEventType.SERIOUS_ILLNESS: ImpactSeverity.CRITICAL,
    LifeEventType.MOVE_IN: ImpactSeverity.MODERATE,
    LifeEventType.MOVE_OUT: ImpactSeverity.MODERATE,
    LifeEventType.BENEFIT_CHANGE: ImpactSeverity.MODERATE,
}

_CONSUMPTION_DELTA_PCT: dict[LifeEventType, float] = {
    LifeEventType.BIRTH: 8.0,
    LifeEventType.DEATH: -8.0,
    LifeEventType.MARRIAGE: 5.0,
    LifeEventType.DIVORCE: -5.0,
    LifeEventType.JOB_LOSS: 15.0,
    LifeEventType.JOB_GAIN: -10.0,
    LifeEventType.RETIREMENT: 12.0,
    LifeEventType.SERIOUS_ILLNESS: 10.0,
    LifeEventType.MOVE_IN: 0.0,
    LifeEventType.MOVE_OUT: 0.0,
    LifeEventType.BENEFIT_CHANGE: 5.0,
}

_PSR_EVENTS = frozenset([
    LifeEventType.SERIOUS_ILLNESS,
    LifeEventType.RETIREMENT,
    LifeEventType.DEATH,
])

_VULNERABILITY_EVENTS = frozenset([
    LifeEventType.JOB_LOSS,
    LifeEventType.SERIOUS_ILLNESS,
    LifeEventType.DIVORCE,
    LifeEventType.BENEFIT_CHANGE,
    LifeEventType.DEATH,
    LifeEventType.RETIREMENT,
])

_ACTIONS: dict[LifeEventType, list[str]] = {
    LifeEventType.BIRTH: ["Reassess annual consumption estimate", "Offer EE advice"],
    LifeEventType.DEATH: ["PSR review if bereaved household", "Arrange welfare call", "Review payment arrangement"],
    LifeEventType.MARRIAGE: ["Reassess consumption", "Offer joint account review"],
    LifeEventType.DIVORCE: ["Update account holder", "Offer tariff review", "Assess vulnerability status"],
    LifeEventType.JOB_LOSS: ["Offer payment plan", "Refer to fuel poverty support", "Reassess consumption (+15% home time)"],
    LifeEventType.JOB_GAIN: ["Reassess consumption estimate"],
    LifeEventType.RETIREMENT: ["PSR review (elderly threshold)", "Offer EE advice", "Reassess consumption (+12%)"],
    LifeEventType.SERIOUS_ILLNESS: ["PSR registration", "Arrange welfare call", "Review disconnection protection"],
    LifeEventType.MOVE_IN: ["COT process", "Reassess meter read", "New customer assessment"],
    LifeEventType.MOVE_OUT: ["COT process", "Final read & bill"],
    LifeEventType.BENEFIT_CHANGE: ["Warm Home Discount eligibility check", "Payment plan review", "Fuel poverty assessment"],
}


@dataclass(frozen=True)
class LifeEventImpact:
    event: LifeEvent
    severity: ImpactSeverity
    expected_consumption_delta_pct: float
    triggers_psr_review: bool
    vulnerability_flag: bool
    recommended_actions: tuple[str, ...]

    @property
    def is_urgent(self) -> bool:
        return self.severity in (ImpactSeverity.HIGH, ImpactSeverity.CRITICAL)

    def to_dict(self) -> dict:
        return {
            "customer_id": self.event.customer_id,
            "event_type": self.event.event_type.value,
            "event_date": str(self.event.event_date),
            "severity": self.severity.value,
            "consumption_delta_pct": self.expected_consumption_delta_pct,
            "triggers_psr_review": self.triggers_psr_review,
            "vulnerability_flag": self.vulnerability_flag,
            "recommended_actions": list(self.recommended_actions),
            "is_urgent": self.is_urgent,
        }


class LifeEventImpactAssessor:
    def assess(self, event: LifeEvent) -> LifeEventImpact:
        et = event.event_type
        return LifeEventImpact(
            event=event,
            severity=_SEVERITY.get(et, ImpactSeverity.LOW),
            expected_consumption_delta_pct=_CONSUMPTION_DELTA_PCT.get(et, 0.0),
            triggers_psr_review=et in _PSR_EVENTS,
            vulnerability_flag=et in _VULNERABILITY_EVENTS,
            recommended_actions=tuple(_ACTIONS.get(et, [])),
        )

    def batch_assess(self, events: list[LifeEvent]) -> list[LifeEventImpact]:
        return [self.assess(e) for e in events]

    def urgent_impacts(self, events: list[LifeEvent]) -> list[LifeEventImpact]:
        return [i for i in self.batch_assess(events) if i.is_urgent]

    def psr_candidates(self, events: list[LifeEvent]) -> list[LifeEventImpact]:
        return [i for i in self.batch_assess(events) if i.triggers_psr_review]

    def summary(self, events: list[LifeEvent]) -> dict:
        impacts = self.batch_assess(events)
        by_severity: dict[str, int] = {}
        for i in impacts:
            by_severity[i.severity.value] = by_severity.get(i.severity.value, 0) + 1
        return {
            "total_events": len(impacts),
            "urgent_count": sum(1 for i in impacts if i.is_urgent),
            "psr_candidates": sum(1 for i in impacts if i.triggers_psr_review),
            "vulnerability_flags": sum(1 for i in impacts if i.vulnerability_flag),
            "by_severity": by_severity,
        }
