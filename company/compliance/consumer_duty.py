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
    # R15 (KL-5 fix, 2026-07-13): "no assessment performed" is a distinct
    # governance state, NOT green. Under FCA Consumer Duty an un-assessed
    # outcome is a governance failure, not compliance -- an empty register
    # must never read GREEN (that was a FAIL-SILENT: absence read as clean).
    NOT_ASSESSED = "not_assessed"


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

    def is_assessed(self) -> bool:
        """True iff at least one of the four Consumer-Duty outcomes has ever
        been assessed. Surfaces/daemons should treat False as a flag (an
        un-assessed register is a governance gap), never as compliance."""
        return any(self.latest_for_outcome(o) is not None for o in DutyOutcome)

    def needs_attention(self) -> bool:
        """The board/daemon flag: True when the register is NOT solidly GREEN --
        i.e. RED, AMBER, or NOT_ASSESSED. A convenience wrapper so callers do
        not accidentally treat NOT_ASSESSED as GREEN."""
        return self.overall_rag() != OutcomeRAG.GREEN

    def overall_rag(self) -> OutcomeRAG:
        latest = [self.latest_for_outcome(o) for o in DutyOutcome]
        active = [a for a in latest if a is not None]
        # R15 (KL-5 fix): an empty register (no outcome ever assessed) is a
        # governance failure, NOT compliant. Return the distinct NOT_ASSESSED
        # state rather than defaulting silently to GREEN.
        if not active:
            return OutcomeRAG.NOT_ASSESSED
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
            "assessed": self.is_assessed(),
            "needs_attention": self.needs_attention(),
            "red_outcomes": len(self.red_outcomes()),
            "outcomes": result,
        }
