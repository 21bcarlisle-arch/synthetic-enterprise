"""Consumer Duty Annual Board Report Register (Phase FW).

Under FCA Consumer Duty (effective 31 July 2023; adopted by Ofgem via
SLC alignment for energy retail), firms must produce a formal Annual
Board Report reviewing consumer outcomes. For energy suppliers:

- Board must approve and sign off the report annually
- Four mandatory outcomes must be assessed: Products and Services,
  Price and Value, Consumer Understanding, Consumer Support
- Key metrics, targets, year-on-year trends, and forward commitments
  are documented
- Ofgem can request the report on 5 working days' notice (Licence Fitness)

First mandatory report year: 2023/24 (board sign-off by 31 Jul 2024).
Subsequent years: by 31 Jul each year covering the prior 12 months.

Distinct from quarterly ConsumerDutyRegister (Phase EF) assessments:
this module models the formal annual board document, board approval,
and multi-year improvement trajectory.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from company.compliance.consumer_duty import DutyOutcome, OutcomeRAG


_FIRST_REPORT_YEAR = 2023          # first mandatory annual report covers 2023/24
_BOARD_REPORT_DEADLINE_MONTH = 7   # July each year (31 Jul)
_BOARD_REPORT_DEADLINE_DAY = 31
_OFGEM_NOTICE_WORKING_DAYS = 5     # WD notice to produce report for Ofgem


@dataclass(frozen=True)
class DutyOutcomeSummary:
    outcome: DutyOutcome
    key_metric_name: str
    key_metric_value: float   # actual this year
    target_value: float       # board-set target
    prior_year_value: Optional[float]  # None for first year
    remediation_count: int    # improvement actions completed this year
    forward_commitment_count: int  # committed improvement actions next year

    @property
    def rag(self) -> OutcomeRAG:
        if self.key_metric_value >= self.target_value:
            return OutcomeRAG.GREEN
        if self.key_metric_value >= self.target_value * 0.90:
            return OutcomeRAG.AMBER
        return OutcomeRAG.RED

    @property
    def is_improving(self) -> bool:
        if self.prior_year_value is None:
            return True
        return self.key_metric_value >= self.prior_year_value

    @property
    def improvement_delta(self) -> Optional[float]:
        if self.prior_year_value is None:
            return None
        return self.key_metric_value - self.prior_year_value

    def outcome_summary(self) -> str:
        trend = "↑" if self.is_improving else "↓"
        return (
            f"[{self.outcome.value}] {self.rag.value.upper()} "
            f"{self.key_metric_name}={self.key_metric_value:.1f} "
            f"(target {self.target_value:.1f}) {trend} "
            f"| {self.remediation_count} remediation(s)"
        )


@dataclass(frozen=True)
class ConsumerDutyAnnualReport:
    year: int                        # calendar year the report covers
    outcomes: Tuple[DutyOutcomeSummary, ...]   # must cover all 4 DutyOutcomes
    board_approved: bool = False
    approval_date: Optional[dt.date] = None

    @property
    def report_deadline(self) -> dt.date:
        return dt.date(self.year + 1, _BOARD_REPORT_DEADLINE_MONTH, _BOARD_REPORT_DEADLINE_DAY)

    @property
    def is_overdue(self) -> bool:
        if self.board_approved:
            return False
        return dt.date.today() > self.report_deadline

    def is_overdue_as_of(self, as_of: dt.date) -> bool:
        if self.board_approved:
            return False
        return as_of > self.report_deadline

    @property
    def overall_rag(self) -> OutcomeRAG:
        rags = [o.rag for o in self.outcomes]
        if OutcomeRAG.RED in rags:
            return OutcomeRAG.RED
        if OutcomeRAG.AMBER in rags:
            return OutcomeRAG.AMBER
        return OutcomeRAG.GREEN

    @property
    def red_outcomes_count(self) -> int:
        return sum(1 for o in self.outcomes if o.rag == OutcomeRAG.RED)

    @property
    def all_outcomes_improving(self) -> bool:
        return all(o.is_improving for o in self.outcomes)

    @property
    def total_remediations(self) -> int:
        return sum(o.remediation_count for o in self.outcomes)

    @property
    def total_forward_commitments(self) -> int:
        return sum(o.forward_commitment_count for o in self.outcomes)

    def get_outcome(self, outcome: DutyOutcome) -> Optional[DutyOutcomeSummary]:
        for o in self.outcomes:
            if o.outcome == outcome:
                return o
        return None

    def report_summary(self) -> str:
        approved_str = f"(approved {self.approval_date})" if self.board_approved else "(PENDING)"
        return (
            f"Consumer Duty Annual Board Report {self.year} {approved_str}: "
            f"Overall {self.overall_rag.value.upper()}. "
            f"{self.red_outcomes_count} red outcomes. "
            f"{self.total_remediations} remediations, "
            f"{self.total_forward_commitments} commitments forward."
        )


class ConsumerDutyBoardRegister:

    def __init__(self) -> None:
        self._reports: Dict[int, ConsumerDutyAnnualReport] = {}

    def add_report(
        self,
        year: int,
        outcomes: Tuple[DutyOutcomeSummary, ...],
    ) -> ConsumerDutyAnnualReport:
        if year < _FIRST_REPORT_YEAR:
            raise ValueError(
                f"Consumer Duty Annual Board Report not required before {_FIRST_REPORT_YEAR}; "
                f"got year={year}"
            )
        report = ConsumerDutyAnnualReport(year=year, outcomes=outcomes)
        self._reports[year] = report
        return report

    def approve_report(self, year: int, approval_date: dt.date) -> ConsumerDutyAnnualReport:
        if year not in self._reports:
            raise KeyError(f"No report recorded for year {year}")
        old = self._reports[year]
        approved = ConsumerDutyAnnualReport(
            year=old.year,
            outcomes=old.outcomes,
            board_approved=True,
            approval_date=approval_date,
        )
        self._reports[year] = approved
        return approved

    def report_for_year(self, year: int) -> Optional[ConsumerDutyAnnualReport]:
        return self._reports.get(year)

    def unapproved_reports(self) -> List[ConsumerDutyAnnualReport]:
        return [r for r in self._reports.values() if not r.board_approved]

    def overdue_reports(self, as_of: dt.date) -> List[ConsumerDutyAnnualReport]:
        return [r for r in self._reports.values() if r.is_overdue_as_of(as_of)]

    def red_years(self) -> List[int]:
        return [
            year for year, r in self._reports.items()
            if r.overall_rag == OutcomeRAG.RED
        ]

    def outcome_trend(
        self, outcome: DutyOutcome
    ) -> List[Tuple[int, Optional[float]]]:
        result = []
        for year in sorted(self._reports):
            os_ = self._reports[year].get_outcome(outcome)
            result.append((year, os_.key_metric_value if os_ else None))
        return result

    def all_years_approved(self) -> bool:
        return all(r.board_approved for r in self._reports.values())

    def board_register_summary(self, as_of: dt.date) -> str:
        n = len(self._reports)
        n_approved = sum(1 for r in self._reports.values() if r.board_approved)
        n_overdue = len(self.overdue_reports(as_of))
        n_red = len(self.red_years())
        return (
            f"Consumer Duty Board Register ({as_of}): {n} annual reports "
            f"({n_approved} approved, {n_overdue} overdue). "
            f"{n_red} red year(s)."
        )
