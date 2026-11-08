"""Supplier Fitness and Propriety Assessment Register.

Post-2022 Ofgem Market Review: new Licence Condition 30A requires
energy suppliers to ensure their directors and senior managers are
'fit and proper' to hold those positions.

Fit and proper criteria (Ofgem guidance, June 2022):
1. Honesty and integrity: no criminal convictions for dishonesty/fraud
2. Financial soundness: no bankruptcy/disqualification/insolvency
3. Competence: relevant energy industry experience
4. Conflicts of interest: declared and managed

Applies to:
- Licensed board directors
- Senior managers with significant influence (SMCR-style)
- Proposed major shareholders (>20% ownership)

Ofgem can require removal of a person who fails the assessment.

This register tracks assessments, expiry dates (annual review), and
flags any unresolved fit-and-proper concerns as regulatory risk.

Epistemic: the company knows who its directors are and their
self-declared fitness information. Ofgem decisions are observable.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum


class FitnessOutcome(str, Enum):
    FIT = "fit"
    FIT_WITH_CONDITIONS = "fit_with_conditions"
    UNDER_REVIEW = "under_review"
    NOT_FIT = "not_fit"


class FitnessRole(str, Enum):
    EXECUTIVE_DIRECTOR = "executive_director"
    NON_EXECUTIVE_DIRECTOR = "non_executive_director"
    SENIOR_MANAGER = "senior_manager"
    MAJOR_SHAREHOLDER = "major_shareholder"


class FitnessConcernCategory(str, Enum):
    CRIMINAL_CONVICTION = "criminal_conviction"
    BANKRUPTCY = "bankruptcy"
    DISQUALIFICATION = "disqualification"
    CONFLICT_OF_INTEREST = "conflict_of_interest"
    COMPETENCE_GAP = "competence_gap"
    PRIOR_SUPPLIER_FAILURE = "prior_supplier_failure"


_REVIEW_INTERVAL_DAYS = 365


@dataclass(frozen=True)
class FitnessAssessment:
    person_id: str
    name: str
    role: FitnessRole
    assessment_date: date
    outcome: FitnessOutcome
    conditions: tuple[str, ...] = ()
    concerns: tuple[FitnessConcernCategory, ...] = ()

    @property
    def review_due_date(self) -> date:
        return self.assessment_date + timedelta(days=_REVIEW_INTERVAL_DAYS)

    def is_review_overdue(self, as_of: date) -> bool:
        return as_of > self.review_due_date

    @property
    def is_fit(self) -> bool:
        return self.outcome in (FitnessOutcome.FIT, FitnessOutcome.FIT_WITH_CONDITIONS)

    @property
    def has_concerns(self) -> bool:
        return len(self.concerns) > 0


class SupplierFitnessRegister:
    """Tracks fit-and-proper assessments for senior persons."""

    def __init__(self) -> None:
        self._assessments: dict[str, FitnessAssessment] = {}

    def assess(
        self,
        person_id: str,
        name: str,
        role: FitnessRole,
        assessment_date: date,
        outcome: FitnessOutcome,
        conditions: tuple[str, ...] = (),
        concerns: tuple[FitnessConcernCategory, ...] = (),
    ) -> FitnessAssessment:
        record = FitnessAssessment(
            person_id=person_id, name=name, role=role,
            assessment_date=assessment_date, outcome=outcome,
            conditions=conditions, concerns=concerns,
        )
        self._assessments[person_id] = record
        return record

    def get(self, person_id: str) -> FitnessAssessment | None:
        return self._assessments.get(person_id)

    def not_fit_persons(self) -> list[FitnessAssessment]:
        return [a for a in self._assessments.values() if not a.is_fit]

    def overdue_reviews(self, as_of: date) -> list[FitnessAssessment]:
        return [a for a in self._assessments.values() if a.is_review_overdue(as_of)]

    def persons_with_concerns(self) -> list[FitnessAssessment]:
        return [a for a in self._assessments.values() if a.has_concerns]

    def prior_supplier_failure_risk(self) -> list[FitnessAssessment]:
        return [a for a in self._assessments.values()
                if FitnessConcernCategory.PRIOR_SUPPLIER_FAILURE in a.concerns]

    @property
    def all_fit(self) -> bool:
        return all(a.is_fit for a in self._assessments.values())

    def fitness_summary(self, as_of: date) -> str:
        n = len(self._assessments)
        n_not_fit = len(self.not_fit_persons())
        n_overdue = len(self.overdue_reviews(as_of))
        return (
            "Supplier Fitness Register (Ofgem LC 30A)\n"
            "Senior persons: {:d} | Not fit: {:d} | Overdue review: {:d}\n"
            "All fit: {}".format(n, n_not_fit, n_overdue, self.all_fit)
        )
