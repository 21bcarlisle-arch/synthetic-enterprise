"""Customer Satisfaction Survey (CSS) tracker.

Ofgem's annual CSS survey asks domestic customers to rate their energy supplier
across 6 dimensions. Ofgem publishes league-table results; bottom-quartile
performance triggers "Enhanced Monitoring" and may lead to enforcement action.

Survey dimensions (each rated 1-10 by customer):
1. Overall satisfaction
2. Billing accuracy (bills match expectations)
3. Ease of contact (can reach the supplier when needed)
4. Complaint handling (resolved fairly and promptly)
5. Value for money (price seems fair vs alternatives)
6. Meter reading accuracy

Industry benchmarks (Ofgem CSS report, 2016-2024):
- Typical large supplier overall: 6.5-7.5 / 10
- Top-quartile threshold: ~7.8 / 10
- Bottom-quartile threshold: ~6.0 / 10
- 2022 crisis: overall satisfaction fell to 5.2 / 10 across all suppliers
  (Ofgem CSS 2022: highest volume of dissatisfied customers on record)
- Switching intent correlates strongly with value-for-money score

A CSS response is captured per customer per survey wave (annual). The book
aggregates to supplier-level scores for compliance reporting.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Dict, List, Optional


_TOP_QUARTILE_THRESHOLD = 7.8
_BOTTOM_QUARTILE_THRESHOLD = 6.0
_CRISIS_YEAR = 2022

# Historical industry average overall scores (for benchmarking)
_INDUSTRY_AVERAGE_OVERALL: dict[int, float] = {
    2016: 7.2, 2017: 7.3, 2018: 7.2, 2019: 7.1, 2020: 7.4,
    2021: 6.8, 2022: 5.2, 2023: 6.1, 2024: 6.9, 2025: 7.0,
}


class CSSPerformanceBand(str):
    TOP = "top_quartile"
    MID = "mid_field"
    BOTTOM = "bottom_quartile"


@dataclass(frozen=True)
class CSSResponse:
    customer_id: str
    survey_year: int
    survey_date: dt.date
    overall_score: float             # 1-10
    billing_accuracy: float          # 1-10
    ease_of_contact: float           # 1-10
    value_for_money: float           # 1-10
    meter_accuracy: float            # 1-10
    complaint_handling: Optional[float] = None  # 1-10; None if no complaint in year

    def __post_init__(self) -> None:
        for attr, val in [
            ("overall_score", self.overall_score),
            ("billing_accuracy", self.billing_accuracy),
            ("ease_of_contact", self.ease_of_contact),
            ("value_for_money", self.value_for_money),
            ("meter_accuracy", self.meter_accuracy),
        ]:
            if not (1.0 <= val <= 10.0):
                raise ValueError(f"{attr} must be 1-10, got {val}")
        if self.complaint_handling is not None and not (1.0 <= self.complaint_handling <= 10.0):
            raise ValueError(f"complaint_handling must be 1-10, got {self.complaint_handling}")

    @property
    def composite_score(self) -> float:
        """Weighted composite (overall 30%, others 14% each)."""
        scores = [
            self.overall_score * 0.30,
            self.billing_accuracy * 0.14,
            self.ease_of_contact * 0.14,
            self.value_for_money * 0.14,
            self.meter_accuracy * 0.14,
        ]
        if self.complaint_handling is not None:
            scores.append(self.complaint_handling * 0.14)
        return round(sum(scores) / sum([0.30, 0.14, 0.14, 0.14, 0.14,
                                        0.14 if self.complaint_handling is not None else 0.0]), 2)

    @property
    def would_recommend(self) -> bool:
        return self.overall_score >= 7.0


class CSSBook:
    """Aggregate CSS responses and produce Ofgem-compatible league-table metrics."""

    def __init__(self) -> None:
        self._responses: List[CSSResponse] = []

    def record_response(
        self,
        customer_id: str,
        survey_year: int,
        survey_date: dt.date,
        overall_score: float,
        billing_accuracy: float,
        ease_of_contact: float,
        value_for_money: float,
        meter_accuracy: float,
        complaint_handling: Optional[float] = None,
    ) -> CSSResponse:
        r = CSSResponse(
            customer_id=customer_id, survey_year=survey_year,
            survey_date=survey_date, overall_score=overall_score,
            billing_accuracy=billing_accuracy, ease_of_contact=ease_of_contact,
            value_for_money=value_for_money, meter_accuracy=meter_accuracy,
            complaint_handling=complaint_handling,
        )
        self._responses.append(r)
        return r

    def annual_responses(self, year: int) -> List[CSSResponse]:
        return [r for r in self._responses if r.survey_year == year]

    def avg_score(self, year: int, dimension: str = "overall_score") -> Optional[float]:
        responses = self.annual_responses(year)
        vals = [getattr(r, dimension) for r in responses
                if getattr(r, dimension) is not None]
        if not vals:
            return None
        return round(sum(vals) / len(vals), 2)

    def performance_band(self, year: int) -> str:
        avg = self.avg_score(year)
        if avg is None:
            return "unrated"
        if avg >= _TOP_QUARTILE_THRESHOLD:
            return CSSPerformanceBand.TOP
        if avg >= _BOTTOM_QUARTILE_THRESHOLD:
            return CSSPerformanceBand.MID
        return CSSPerformanceBand.BOTTOM

    def vs_industry_avg(self, year: int) -> Optional[float]:
        """Supplier overall avg minus industry average (positive = better than market)."""
        supplier_avg = self.avg_score(year)
        industry_avg = _INDUSTRY_AVERAGE_OVERALL.get(year)
        if supplier_avg is None or industry_avg is None:
            return None
        return round(supplier_avg - industry_avg, 2)

    def recommend_rate(self, year: int) -> Optional[float]:
        responses = self.annual_responses(year)
        if not responses:
            return None
        return round(sum(1 for r in responses if r.would_recommend) / len(responses), 3)

    def css_summary(self, year: int) -> dict:
        responses = self.annual_responses(year)
        return {
            "year": year,
            "responses": len(responses),
            "avg_overall": self.avg_score(year, "overall_score"),
            "avg_billing": self.avg_score(year, "billing_accuracy"),
            "avg_contact": self.avg_score(year, "ease_of_contact"),
            "avg_value": self.avg_score(year, "value_for_money"),
            "performance_band": self.performance_band(year),
            "vs_industry": self.vs_industry_avg(year),
            "recommend_rate": self.recommend_rate(year),
        }
