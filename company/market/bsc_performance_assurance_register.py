"""BSC Performance Assurance Register.

Elexon PA framework (BSC Section M): quarterly self-assessments by suppliers,
DAs, DCs, and MOPs against six data quality metrics. Elexon assigns STANDARD
(0 breaches), WATCH (1-2), or FORMAL_ACTION (3+) tier. Watch/Formal Action
triggers a Remedial Action Plan (RAP) within 20WD. Formal Action can result
in agent suspension -- settlement risk for all MPANs under that agent.

Connects to:
  - dadc_contract_register.py (Phase CV): who the DA/DC agents are
  - mop_appointment_register.py (Phase HJ): who the MOP agents are
  - bsc_settlement_dispute_register.py: disputes (distinct)
  - mpas_standing_data_correction_register.py: standing data quality (distinct)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


def _add_working_days(date: dt.date, days: int) -> dt.date:
    current = date
    added = 0
    while added < days:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


class PAAgentType(Enum):
    SUPPLIER = "SUPPLIER"
    DATA_AGGREGATOR = "DATA_AGGREGATOR"
    DATA_COLLECTOR = "DATA_COLLECTOR"
    METER_OPERATOR = "METER_OPERATOR"


class PAMetric(Enum):
    MISSING_READS = "MISSING_READS"
    LATE_DATA_FLOWS = "LATE_DATA_FLOWS"
    ERRONEOUS_READS = "ERRONEOUS_READS"
    UNRECONCILED_VOLUMES = "UNRECONCILED_VOLUMES"
    DATA_SUBSTITUTION_RATE = "DATA_SUBSTITUTION_RATE"
    FLOW_REJECTION_RATE = "FLOW_REJECTION_RATE"


class PAAssessmentTier(Enum):
    STANDARD = "STANDARD"
    WATCH = "WATCH"
    FORMAL_ACTION = "FORMAL_ACTION"


class PAStatus(Enum):
    OPEN = "OPEN"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    RAP_REQUIRED = "RAP_REQUIRED"
    RAP_IN_PROGRESS = "RAP_IN_PROGRESS"
    RAP_CLOSED = "RAP_CLOSED"


_METRIC_THRESHOLDS = {
    PAMetric.MISSING_READS: 97.0,
    PAMetric.LATE_DATA_FLOWS: 95.0,
    PAMetric.ERRONEOUS_READS: 99.0,
    PAMetric.UNRECONCILED_VOLUMES: 98.0,
    PAMetric.DATA_SUBSTITUTION_RATE: 95.0,
    PAMetric.FLOW_REJECTION_RATE: 97.0,
}


@dataclass(frozen=True)
class PAMetricScore:
    metric: PAMetric
    score_pct: float
    threshold_pct: float

    @property
    def is_breached(self) -> bool:
        return self.score_pct < self.threshold_pct

    @property
    def severity(self) -> str:
        if not self.is_breached:
            return "PASS"
        ratio = self.score_pct / self.threshold_pct
        if ratio < 0.5:
            return "HIGH"
        if ratio < 0.9:
            return "MEDIUM"
        return "LOW"


@dataclass(frozen=True)
class PAAssessmentRecord:
    assessment_id: str
    agent_type: PAAgentType
    agent_name: str
    quarter_year: int
    quarter_number: int
    assessment_date: dt.date
    metric_scores: Tuple[PAMetricScore, ...]
    status: PAStatus

    @property
    def quarter_label(self) -> str:
        return f"Q{self.quarter_number}/{self.quarter_year}"

    @property
    def breached_metrics(self) -> List[PAMetricScore]:
        return [m for m in self.metric_scores if m.is_breached]

    @property
    def tier(self) -> PAAssessmentTier:
        n = len(self.breached_metrics)
        if n == 0:
            return PAAssessmentTier.STANDARD
        if n <= 2:
            return PAAssessmentTier.WATCH
        return PAAssessmentTier.FORMAL_ACTION

    @property
    def rap_required(self) -> bool:
        return self.tier != PAAssessmentTier.STANDARD

    @property
    def rap_due_date(self) -> Optional[dt.date]:
        if not self.rap_required:
            return None
        return _add_working_days(self.assessment_date, 20)

    def is_rap_overdue(self, as_of: dt.date) -> bool:
        if not self.rap_required or self.status == PAStatus.RAP_CLOSED:
            return False
        due = self.rap_due_date
        return due is not None and as_of > due

    @property
    def overall_pass_rate_pct(self) -> float:
        if not self.metric_scores:
            return 0.0
        passed = sum(1 for m in self.metric_scores if not m.is_breached)
        return round(100.0 * passed / len(self.metric_scores), 1)

    @property
    def assessment_summary(self) -> str:
        return (
            f"{self.assessment_id} | {self.agent_name} ({self.agent_type.value}) "
            f"| {self.quarter_label} | {self.tier.value} | {self.status.value} "
            f"| {self.overall_pass_rate_pct}% metrics passed"
        )


class BSCPerformanceAssuranceRegister:
    """Quarterly BSC Section M Performance Assurance tracking."""

    def __init__(self) -> None:
        self._records: List[PAAssessmentRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"PA-{self._counter:05d}"

    def _get(self, assessment_id: str) -> PAAssessmentRecord:
        for r in self._records:
            if r.assessment_id == assessment_id:
                return r
        raise KeyError(f"Assessment not found: {assessment_id}")

    def _replace(self, updated: PAAssessmentRecord) -> None:
        self._records = [
            updated if r.assessment_id == updated.assessment_id else r
            for r in self._records
        ]

    def record_assessment(
        self,
        agent_type: PAAgentType,
        agent_name: str,
        quarter_year: int,
        quarter_number: int,
        assessment_date: dt.date,
        metric_scores: Tuple[PAMetricScore, ...],
    ) -> PAAssessmentRecord:
        if quarter_number not in (1, 2, 3, 4):
            raise ValueError(f"quarter_number must be 1-4, got {quarter_number}")
        record = PAAssessmentRecord(
            assessment_id=self._next_id(),
            agent_type=agent_type,
            agent_name=agent_name,
            quarter_year=quarter_year,
            quarter_number=quarter_number,
            assessment_date=assessment_date,
            metric_scores=metric_scores,
            status=PAStatus.OPEN,
        )
        self._records.append(record)
        return record

    def submit_assessment(self, assessment_id: str) -> PAAssessmentRecord:
        r = self._get(assessment_id)
        if r.status != PAStatus.OPEN:
            raise ValueError(f"Can only submit OPEN; {assessment_id} is {r.status.value}")
        updated = PAAssessmentRecord(
            assessment_id=r.assessment_id, agent_type=r.agent_type,
            agent_name=r.agent_name, quarter_year=r.quarter_year,
            quarter_number=r.quarter_number, assessment_date=r.assessment_date,
            metric_scores=r.metric_scores, status=PAStatus.SUBMITTED,
        )
        self._replace(updated)
        return updated

    def accept_assessment(self, assessment_id: str) -> PAAssessmentRecord:
        r = self._get(assessment_id)
        if r.status != PAStatus.SUBMITTED:
            raise ValueError(f"Can only accept SUBMITTED; {assessment_id} is {r.status.value}")
        new_status = PAStatus.RAP_REQUIRED if r.rap_required else PAStatus.ACCEPTED
        updated = PAAssessmentRecord(
            assessment_id=r.assessment_id, agent_type=r.agent_type,
            agent_name=r.agent_name, quarter_year=r.quarter_year,
            quarter_number=r.quarter_number, assessment_date=r.assessment_date,
            metric_scores=r.metric_scores, status=new_status,
        )
        self._replace(updated)
        return updated

    def raise_rap(self, assessment_id: str) -> PAAssessmentRecord:
        r = self._get(assessment_id)
        if r.status != PAStatus.RAP_REQUIRED:
            raise ValueError(f"Can only raise RAP for RAP_REQUIRED; {assessment_id} is {r.status.value}")
        updated = PAAssessmentRecord(
            assessment_id=r.assessment_id, agent_type=r.agent_type,
            agent_name=r.agent_name, quarter_year=r.quarter_year,
            quarter_number=r.quarter_number, assessment_date=r.assessment_date,
            metric_scores=r.metric_scores, status=PAStatus.RAP_IN_PROGRESS,
        )
        self._replace(updated)
        return updated

    def close_rap(self, assessment_id: str) -> PAAssessmentRecord:
        r = self._get(assessment_id)
        if r.status != PAStatus.RAP_IN_PROGRESS:
            raise ValueError(f"Can only close RAP_IN_PROGRESS; {assessment_id} is {r.status.value}")
        updated = PAAssessmentRecord(
            assessment_id=r.assessment_id, agent_type=r.agent_type,
            agent_name=r.agent_name, quarter_year=r.quarter_year,
            quarter_number=r.quarter_number, assessment_date=r.assessment_date,
            metric_scores=r.metric_scores, status=PAStatus.RAP_CLOSED,
        )
        self._replace(updated)
        return updated

    def assessments_for_agent(self, agent_name: str) -> List[PAAssessmentRecord]:
        return [r for r in self._records if r.agent_name == agent_name]

    def current_tier_for_agent(
        self, agent_name: str, as_of: dt.date
    ) -> Optional[PAAssessmentTier]:
        _TERMINAL = (
            PAStatus.ACCEPTED,
            PAStatus.RAP_REQUIRED,
            PAStatus.RAP_IN_PROGRESS,
            PAStatus.RAP_CLOSED,
        )
        accepted = [
            r for r in self._records
            if r.agent_name == agent_name
            and r.status in _TERMINAL
            and r.assessment_date <= as_of
        ]
        if not accepted:
            return None
        latest = max(accepted, key=lambda r: (r.quarter_year, r.quarter_number))
        return latest.tier

    @property
    def agents_on_watch(self) -> List[str]:
        seen: set = set()
        result = []
        for r in self._records:
            if (
                r.status in (PAStatus.RAP_REQUIRED, PAStatus.RAP_IN_PROGRESS)
                and r.tier == PAAssessmentTier.WATCH
                and r.agent_name not in seen
            ):
                seen.add(r.agent_name)
                result.append(r.agent_name)
        return result

    @property
    def agents_on_formal_action(self) -> List[str]:
        seen: set = set()
        result = []
        for r in self._records:
            if (
                r.status in (PAStatus.RAP_REQUIRED, PAStatus.RAP_IN_PROGRESS)
                and r.tier == PAAssessmentTier.FORMAL_ACTION
                and r.agent_name not in seen
            ):
                seen.add(r.agent_name)
                result.append(r.agent_name)
        return result

    def overdue_raps(self, as_of: dt.date) -> List[PAAssessmentRecord]:
        return [r for r in self._records if r.is_rap_overdue(as_of)]

    def quarterly_summary(self, year: int, quarter: int) -> dict:
        qr = [
            r for r in self._records
            if r.quarter_year == year and r.quarter_number == quarter
        ]
        return {
            "year": year,
            "quarter": quarter,
            "quarter_label": f"Q{quarter}/{year}",
            "total": len(qr),
            "standard_count": sum(1 for r in qr if r.tier == PAAssessmentTier.STANDARD),
            "watch_count": sum(1 for r in qr if r.tier == PAAssessmentTier.WATCH),
            "formal_action_count": sum(1 for r in qr if r.tier == PAAssessmentTier.FORMAL_ACTION),
        }

    @property
    def pa_register_summary(self) -> dict:
        return {
            "total_assessments": len(self._records),
            "agents_on_watch": self.agents_on_watch,
            "agents_on_formal_action": self.agents_on_formal_action,
            "standard_count": sum(1 for r in self._records if r.tier == PAAssessmentTier.STANDARD),
            "watch_count": sum(1 for r in self._records if r.tier == PAAssessmentTier.WATCH),
            "formal_action_count": sum(1 for r in self._records if r.tier == PAAssessmentTier.FORMAL_ACTION),
        }
