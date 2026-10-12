from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional


class DDAction(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"


# Variance beyond ±5% triggers a DD adjustment. The DUTY is Ofgem SLC 27.15 (set
# and revise the DD on "the best and most current information available"); the
# ±5% is NOT in the licence -- there is no SLC 27B, and SLC 27.13-27.16 name no
# numeric trigger. It is a widely used supplier review band, so it stands here as
# a MODELLING CONVENTION, not a licence requirement.
# Source: docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md
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


def _recommended_monthly_at_rates(
    *,
    annual_kwh: float,
    days: int,
    unit_rate_per_mwh_ex_vat: float,
    standing_charge_per_day_ex_vat: float,
    billed_adjustments: float = 0.0,
) -> float:
    """The completed year's consumption priced at the rates in force from the review date, grossed
    for VAT, plus any catch-up billed in the year, rounded as `_recommended_monthly` rounds.
    Published through `company.interfaces.dd_review_outcome.reviewed_monthly_amount_at_rates`."""
    from company.compliance.domain_invariants import vat_rate_for_segment
    ex_vat = annual_kwh / 1000.0 * unit_rate_per_mwh_ex_vat + days * standing_charge_per_day_ex_vat
    return _recommended_monthly(ex_vat * (1.0 + vat_rate_for_segment("resi")) + billed_adjustments)


#: How the annual review sizes next year's debit. `last_year_spend` resets it to what the completed
#: year cost at the prices it was billed at. `consumption_at_rates_in_force` prices that year's
#: billed kWh and days at the rates on the first bill of the year being set (SLC 27.15, "most
#: current information"). The two agree when prices are flat. Moved here from
#: `simulation/dd_balance_book.py` (2026-10-12): which rule the review applies is the supplier's
#: review policy; the world chooses only which policy arm a run is on.
REVIEW_RULES = ("last_year_spend", "consumption_at_rates_in_force")
DEFAULT_REVIEW_RULE = "last_year_spend"


def bill_days(b) -> int:
    """Days a bill covers, as printed on it (`days_in_period`), else from its period dates."""
    if b.get("days_in_period"):
        return int(b["days_in_period"])
    end = date.fromisoformat(b["period_end"][:10])
    start = date.fromisoformat(b["period_start"][:10]) if b.get("period_start") else end.replace(day=1)
    return (end - start).days + 1


def reviewed_standing(rule: str, completed: list, first_of_new) -> float:
    """The standing monthly debit the review after `completed` (one window's bills) sets.

    Where the rates in force cannot be read off the window's first bill (no such bill, or a bill
    without the rate fields), the review falls back to last year's spend: there is nothing more
    current to price at.
    """
    if rule not in REVIEW_RULES:
        raise ValueError(f"unknown DD review rule {rule!r}; expected one of {REVIEW_RULES}")
    spend = sum(float(b["total_amount_gbp"]) for b in completed)
    if rule == "last_year_spend" or first_of_new is None:
        return _recommended_monthly(spend)
    unit = first_of_new.get("average_unit_rate_gbp_per_mwh")
    sc = first_of_new.get("standing_charge_gbp_per_day")
    if not unit or sc is None or any(b.get("total_consumption_kwh") is None for b in completed):
        return _recommended_monthly(spend)
    return _recommended_monthly_at_rates(
        annual_kwh=sum(float(b["total_consumption_kwh"]) for b in completed),
        days=sum(bill_days(b) for b in completed),
        unit_rate_per_mwh_ex_vat=float(unit),
        standing_charge_per_day_ex_vat=float(sc),
        billed_adjustments=sum(float(b.get("catchup_adjustment_gbp") or 0.0)
                                   for b in completed if b.get("catchup_applied")),
    )


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
