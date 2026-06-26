from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional


class DDAction(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"


# Variance beyond ±5% triggers a DD adjustment under Ofgem SLC 27B
_VARIANCE_THRESHOLD_PCT = 5.0


@dataclass(frozen=True)
class DDReviewResult:
    customer_id: str
    review_date: date
    current_dd_gbp: float          # monthly DD amount
    actual_annual_spend_gbp: float # actual spend over 12 months
    recommended_monthly_gbp: float # rounded to nearest pound
    variance_pct: float            # (actual - implied_annual) / implied_annual * 100
    action: DDAction


def _recommended_monthly(actual_annual: float) -> float:
    """Round up to nearest pound for DD amount."""
    monthly = actual_annual / 12.0
    return round(monthly + 0.5)   # ceiling-round to pound


def review(
    customer_id: str,
    review_date: date,
    current_dd_gbp: float,
    actual_annual_spend_gbp: float,
) -> DDReviewResult:
    """Compute the ADDR outcome for a single customer."""
    implied_annual = current_dd_gbp * 12.0
    if implied_annual == 0:
        variance_pct = 0.0
    else:
        variance_pct = (actual_annual_spend_gbp - implied_annual) / implied_annual * 100.0
    recommended = _recommended_monthly(actual_annual_spend_gbp)
    if variance_pct > _VARIANCE_THRESHOLD_PCT:
        action = DDAction.INCREASE
    elif variance_pct < -_VARIANCE_THRESHOLD_PCT:
        action = DDAction.DECREASE
    else:
        action = DDAction.MAINTAIN
    return DDReviewResult(
        customer_id=customer_id,
        review_date=review_date,
        current_dd_gbp=current_dd_gbp,
        actual_annual_spend_gbp=actual_annual_spend_gbp,
        recommended_monthly_gbp=recommended,
        variance_pct=round(variance_pct, 1),
        action=action,
    )


@dataclass
class DDReviewBook:
    """Tracks annual direct debit review outcomes across the portfolio."""

    _reviews: List[DDReviewResult] = field(default_factory=list)

    def record(self, result: DDReviewResult) -> None:
        self._reviews.append(result)

    def run_review(
        self,
        customer_id: str,
        review_date: date,
        current_dd_gbp: float,
        actual_annual_spend_gbp: float,
    ) -> DDReviewResult:
        result = review(customer_id, review_date, current_dd_gbp, actual_annual_spend_gbp)
        self._reviews.append(result)
        return result

    def latest_review(self, customer_id: str) -> Optional[DDReviewResult]:
        matches = [r for r in self._reviews if r.customer_id == customer_id]
        return max(matches, key=lambda r: r.review_date) if matches else None

    def overdue_for_review(
        self,
        as_of: date,
        last_review_dates: Dict[str, date],
        months: int = 12,
    ) -> List[str]:
        """Customer IDs whose last review was >months months ago."""
        overdue = []
        for cid, last in last_review_dates.items():
            months_elapsed = (as_of.year - last.year) * 12 + (as_of.month - last.month)
            if months_elapsed > months:
                overdue.append(cid)
        return overdue

    def summary(self) -> dict:
        n = len(self._reviews)
        if n == 0:
            return {
                "total_reviews": 0,
                "increase_count": 0,
                "decrease_count": 0,
                "maintain_count": 0,
                "avg_variance_pct": 0.0,
            }
        return {
            "total_reviews": n,
            "increase_count": sum(1 for r in self._reviews if r.action == DDAction.INCREASE),
            "decrease_count": sum(1 for r in self._reviews if r.action == DDAction.DECREASE),
            "maintain_count": sum(1 for r in self._reviews if r.action == DDAction.MAINTAIN),
            "avg_variance_pct": round(
                sum(r.variance_pct for r in self._reviews) / n, 1
            ),
        }
