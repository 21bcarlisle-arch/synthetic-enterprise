from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class AgentPerformancePeriod:
    agent_id: str
    period_start: dt.date
    period_end: dt.date
    calls_handled: int
    total_handle_time_seconds: int
    first_contact_resolutions: int
    escalations: int
    complaints_raised: int
    avg_csat: Optional[float]

    @property
    def avg_handle_time_seconds(self) -> Optional[float]:
        if self.calls_handled == 0:
            return None
        return round(self.total_handle_time_seconds / self.calls_handled, 1)

    @property
    def first_contact_resolution_rate(self) -> Optional[float]:
        if self.calls_handled == 0:
            return None
        return round(self.first_contact_resolutions / self.calls_handled * 100, 1)

    @property
    def escalation_rate(self) -> Optional[float]:
        if self.calls_handled == 0:
            return None
        return round(self.escalations / self.calls_handled * 100, 1)

    @property
    def complaint_rate(self) -> Optional[float]:
        if self.calls_handled == 0:
            return None
        return round(self.complaints_raised / self.calls_handled * 100, 1)


@dataclass(frozen=True)
class ContactCentreMetrics:
    period_start: dt.date
    period_end: dt.date
    total_calls: int
    answered_within_sla_seconds: int
    abandoned_calls: int
    total_handle_time_seconds: int
    agents_on_duty: int

    @property
    def abandonment_rate(self) -> float:
        offered = self.total_calls + self.abandoned_calls
        if offered == 0:
            return 0.0
        return round(self.abandoned_calls / offered * 100, 1)

    @property
    def avg_handle_time_seconds(self) -> Optional[float]:
        if self.total_calls == 0:
            return None
        return round(self.total_handle_time_seconds / self.total_calls, 1)

    @property
    def sla_answer_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return round(self.answered_within_sla_seconds / self.total_calls * 100, 1)

    @property
    def calls_per_agent(self) -> Optional[float]:
        if self.agents_on_duty == 0:
            return None
        return round(self.total_calls / self.agents_on_duty, 1)

    def summary(self) -> dict:
        return {
            'period_start': str(self.period_start),
            'period_end': str(self.period_end),
            'total_calls': self.total_calls,
            'abandonment_rate': self.abandonment_rate,
            'sla_answer_rate': self.sla_answer_rate,
            'avg_handle_time_seconds': self.avg_handle_time_seconds,
            'calls_per_agent': self.calls_per_agent,
        }
