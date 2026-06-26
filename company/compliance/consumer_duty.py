from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DutyOutcome(str, Enum):
    PRODUCTS_AND_SERVICES = "products_and_services"
    PRICE_AND_VALUE = "price_and_value"
    CONSUMER_UNDERSTANDING = "consumer_understanding"
    CONSUMER_SUPPORT = "consumer_support"


class OutcomeRAG(str, Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


@dataclass(frozen=True)
class OutcomeAssessment:
    outcome: DutyOutcome
    assessment_date: str
    rag: OutcomeRAG
    metric_value: float
    metric_name: str
    narrative: str
    evidence_ref: str = ""

    @property
    def is_compliant(self) -> bool:
        return self.rag in (OutcomeRAG.GREEN, OutcomeRAG.AMBER)


class ConsumerDutyRegister:
    IMPLEMENTATION_DATE = "2023-07-31"

    def __init__(self) -> None:
        self._assessments: list[OutcomeAssessment] = []

    def record_assessment(self, assessment: OutcomeAssessment) -> OutcomeAssessment:
        self._assessments.append(assessment)
        return assessment

    def assessments_for_outcome(self, outcome: DutyOutcome) -> list[OutcomeAssessment]:
        return [a for a in self._assessments if a.outcome == outcome]

    def latest_for_outcome(self, outcome: DutyOutcome) -> Optional[OutcomeAssessment]:
        recs = self.assessments_for_outcome(outcome)
        return max(recs, key=lambda a: a.assessment_date) if recs else None

    def red_outcomes(self) -> list[OutcomeAssessment]:
        return [a for a in self._assessments if a.rag == OutcomeRAG.RED]

    def overall_rag(self) -> OutcomeRAG:
        latest = [self.latest_for_outcome(o) for o in DutyOutcome]
        active = [a for a in latest if a is not None]
        if not active:
            return OutcomeRAG.GREEN
        if any(a.rag == OutcomeRAG.RED for a in active):
            return OutcomeRAG.RED
        if any(a.rag == OutcomeRAG.AMBER for a in active):
            return OutcomeRAG.AMBER
        return OutcomeRAG.GREEN

    def outcomes_summary(self) -> dict:
        result = {}
        for outcome in DutyOutcome:
            latest = self.latest_for_outcome(outcome)
            result[outcome.value] = {
                "rag": latest.rag.value if latest else None,
                "metric_name": latest.metric_name if latest else None,
                "metric_value": latest.metric_value if latest else None,
                "narrative": latest.narrative if latest else None,
                "assessment_date": latest.assessment_date if latest else None,
                "assessments_count": len(self.assessments_for_outcome(outcome)),
            }
        return {
            "overall_rag": self.overall_rag().value,
            "red_outcomes": len(self.red_outcomes()),
            "outcomes": result,
        }
