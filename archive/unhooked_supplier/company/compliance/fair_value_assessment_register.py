"""Consumer Duty Fair Value Assessment Register (Phase GP).

FCA/Ofgem Consumer Duty (July 2023) requires suppliers to assess
that each product/tariff type delivers fair value to customers.

Fair value framework (Consumer Duty 2.4.1):
  - Benefit received must be proportionate to price paid
  - Must consider the impact on vulnerable customers specifically
  - Annual assessment required for each product category
  - Board must receive and approve the fair value assessment
  - Ofgem may request evidence of assessment at any time
  - Products found to offer poor value must be reviewed within 30 days

Fair value metrics:
  - Revenue per customer vs cost to serve per customer
  - Margin as % of revenue (industry benchmark: 3-8% for domestic)
  - Comparison with market median price (TCR benchmark)
  - Complaint rate, NPS, satisfaction scores
  - Exit rate (high exit = price rejection by customers)

Distinct from consumer_duty.py (general Consumer Duty obligations)
and ofgem_scorecard.py (Ofgem performance metrics). This module
tracks the formal annual fair value assessment for each tariff.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_REVIEW_CYCLE_MONTHS = 12
_POOR_VALUE_REVIEW_DAYS = 30


class ProductCategory(str, Enum):
    STANDARD_VARIABLE = "standard_variable"
    FIXED_TERM = "fixed_term"
    PREPAYMENT = "prepayment"
    TIME_OF_USE = "time_of_use"
    DEEMED = "deemed"
    GREEN_TARIFF = "green_tariff"


class FairValueOutcome(str, Enum):
    FAIR_VALUE = "fair_value"
    FAIR_VALUE_WITH_CAVEATS = "fair_value_with_caveats"
    POOR_VALUE = "poor_value"
    UNDER_REVIEW = "under_review"
    WITHDRAWN = "withdrawn"


_POOR = frozenset({FairValueOutcome.POOR_VALUE})


@dataclass(frozen=True)
class FairValueAssessmentRecord:
    record_id: str
    product_id: str
    product_category: ProductCategory
    assessment_date: dt.date
    outcome: FairValueOutcome
    cost_to_serve_gbp_pa: float
    revenue_per_customer_gbp_pa: float
    customer_count: int
    board_approved_date: Optional[dt.date] = None
    notes: str = ""

    @property
    def margin_per_customer_gbp(self) -> float:
        return round(self.revenue_per_customer_gbp_pa - self.cost_to_serve_gbp_pa, 2)

    @property
    def margin_pct(self) -> float:
        if self.revenue_per_customer_gbp_pa == 0:
            return 0.0
        return round(self.margin_per_customer_gbp / self.revenue_per_customer_gbp_pa * 100, 2)

    @property
    def is_poor_value(self) -> bool:
        return self.outcome == FairValueOutcome.POOR_VALUE

    @property
    def is_board_approved(self) -> bool:
        return self.board_approved_date is not None

    def is_overdue_review(self, as_of: dt.date) -> bool:
        months_since = (
            (as_of.year - self.assessment_date.year) * 12
            + (as_of.month - self.assessment_date.month)
        )
        return months_since >= _REVIEW_CYCLE_MONTHS

    def poor_value_review_due(self) -> Optional[dt.date]:
        if not self.is_poor_value:
            return None
        return self.assessment_date + dt.timedelta(days=_POOR_VALUE_REVIEW_DAYS)

    def assessment_summary(self) -> str:
        return (
            "FVA " + self.record_id + " product=" + self.product_id
            + " [" + self.product_category.value + "]"
            + " margin=" + str(self.margin_pct) + "%"
            + " [" + self.outcome.value + "]"
        )


class FairValueAssessmentRegister:

    def __init__(self) -> None:
        self._records: List[FairValueAssessmentRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "FVA-" + str(self._counter).zfill(5)

    def create_assessment(
        self,
        product_id: str,
        product_category: ProductCategory,
        assessment_date: dt.date,
        outcome: FairValueOutcome,
        cost_to_serve_gbp_pa: float,
        revenue_per_customer_gbp_pa: float,
        customer_count: int,
        notes: str = "",
    ) -> FairValueAssessmentRecord:
        if cost_to_serve_gbp_pa < 0 or revenue_per_customer_gbp_pa < 0:
            raise ValueError("cost and revenue must be non-negative")
        if customer_count < 0:
            raise ValueError("customer_count must be non-negative")
        record = FairValueAssessmentRecord(
            record_id=self._next_id(),
            product_id=product_id, product_category=product_category,
            assessment_date=assessment_date, outcome=outcome,
            cost_to_serve_gbp_pa=cost_to_serve_gbp_pa,
            revenue_per_customer_gbp_pa=revenue_per_customer_gbp_pa,
            customer_count=customer_count, notes=notes,
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> FairValueAssessmentRecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = FairValueAssessmentRecord(
                    record_id=r.record_id, product_id=r.product_id,
                    product_category=r.product_category,
                    assessment_date=r.assessment_date,
                    outcome=kwargs.get("outcome", r.outcome),
                    cost_to_serve_gbp_pa=r.cost_to_serve_gbp_pa,
                    revenue_per_customer_gbp_pa=r.revenue_per_customer_gbp_pa,
                    customer_count=r.customer_count,
                    board_approved_date=kwargs.get("board_approved_date", r.board_approved_date),
                    notes=kwargs.get("notes", r.notes),
                )
                self._records[i] = updated
                return updated
        raise KeyError("FVA record " + record_id + " not found")

    def approve(self, record_id: str, board_approved_date: dt.date) -> FairValueAssessmentRecord:
        return self._update(record_id, board_approved_date=board_approved_date)

    def update_outcome(self, record_id: str, outcome: FairValueOutcome) -> FairValueAssessmentRecord:
        return self._update(record_id, outcome=outcome)

    def poor_value_products(self) -> List[FairValueAssessmentRecord]:
        return [r for r in self._records if r.is_poor_value]

    def overdue_reviews(self, as_of: dt.date) -> List[FairValueAssessmentRecord]:
        return [r for r in self._records if r.is_overdue_review(as_of)]

    def unapproved_assessments(self) -> List[FairValueAssessmentRecord]:
        return [r for r in self._records if not r.is_board_approved]

    def by_category(self, category: ProductCategory) -> List[FairValueAssessmentRecord]:
        return [r for r in self._records if r.product_category == category]

    def total_customers_assessed(self) -> int:
        return sum(r.customer_count for r in self._records)

    def fair_value_compliance_rate_pct(self) -> Optional[float]:
        if not self._records:
            return None
        fair = sum(1 for r in self._records if not r.is_poor_value)
        return round(fair / len(self._records) * 100, 1)

    def fva_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_poor = len(self.poor_value_products())
        n_overdue = len(self.overdue_reviews(as_of))
        n_unapproved = len(self.unapproved_assessments())
        return (
            "Fair Value Assessment Register (" + str(as_of) + "): "
            + str(n) + " assessments ("
            + str(n_poor) + " poor value, "
            + str(n_overdue) + " overdue, "
            + str(n_unapproved) + " unapproved)."
        )
