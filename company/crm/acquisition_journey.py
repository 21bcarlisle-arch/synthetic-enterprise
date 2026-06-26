from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional


class AcquisitionStage(str, Enum):
    QUOTE_REQUESTED = "quote_requested"
    APPLICATION_SUBMITTED = "application_submitted"
    CREDIT_CHECK = "credit_check"
    CREDIT_APPROVED = "credit_approved"
    CREDIT_DECLINED = "credit_declined"
    SIGNED_UP = "signed_up"
    FIRST_BILL_SENT = "first_bill_sent"
    ONBOARDED = "onboarded"


_SUCCESS_PATH = [
    AcquisitionStage.QUOTE_REQUESTED,
    AcquisitionStage.APPLICATION_SUBMITTED,
    AcquisitionStage.CREDIT_CHECK,
    AcquisitionStage.CREDIT_APPROVED,
    AcquisitionStage.SIGNED_UP,
    AcquisitionStage.FIRST_BILL_SENT,
    AcquisitionStage.ONBOARDED,
]

_TERMINAL_STAGES = {AcquisitionStage.CREDIT_DECLINED, AcquisitionStage.ONBOARDED}


@dataclass
class AcquisitionJourney:
    customer_id: str
    channel: str
    stage_dates: Dict[AcquisitionStage, date] = field(default_factory=dict)

    def advance(self, stage: AcquisitionStage, as_of: date) -> None:
        self.stage_dates[stage] = as_of

    @property
    def current_stage(self) -> Optional[AcquisitionStage]:
        if not self.stage_dates:
            return None
        return max(self.stage_dates, key=lambda s: self.stage_dates[s])

    @property
    def is_complete(self) -> bool:
        cs = self.current_stage
        return cs is not None and cs in _TERMINAL_STAGES

    @property
    def converted(self) -> bool:
        return AcquisitionStage.ONBOARDED in self.stage_dates

    def days_to_stage(self, stage: AcquisitionStage) -> Optional[int]:
        start = self.stage_dates.get(AcquisitionStage.QUOTE_REQUESTED)
        end = self.stage_dates.get(stage)
        if start is None or end is None:
            return None
        return (end - start).days


@dataclass
class AcquisitionFunnel:
    _journeys: List[AcquisitionJourney] = field(default_factory=list)

    def start_journey(self, customer_id: str, channel: str, quote_date: date) -> AcquisitionJourney:
        j = AcquisitionJourney(customer_id=customer_id, channel=channel)
        j.advance(AcquisitionStage.QUOTE_REQUESTED, quote_date)
        self._journeys.append(j)
        return j

    def advance(self, customer_id: str, stage: AcquisitionStage, as_of: date) -> bool:
        for j in self._journeys:
            if j.customer_id == customer_id:
                j.advance(stage, as_of)
                return True
        return False

    def conversion_rate(self, from_stage: AcquisitionStage, to_stage: AcquisitionStage) -> float:
        with_from = [j for j in self._journeys if from_stage in j.stage_dates]
        if not with_from:
            return 0.0
        with_to = sum(1 for j in with_from if to_stage in j.stage_dates)
        return with_to / len(with_from)

    def drop_off_at(self, stage: AcquisitionStage) -> List[AcquisitionJourney]:
        return [
            j for j in self._journeys
            if j.current_stage == stage and not j.is_complete
        ]

    def channel_summary(self, channel: str) -> dict:
        ch = [j for j in self._journeys if j.channel == channel]
        if not ch:
            result = dict(channel=channel, total=0, converted=0, conversion_rate=0.0)
            return result
        converted = sum(1 for j in ch if j.converted)
        result = dict(
            channel=channel,
            total=len(ch),
            converted=converted,
            conversion_rate=round(converted / len(ch), 4),
        )
        return result
