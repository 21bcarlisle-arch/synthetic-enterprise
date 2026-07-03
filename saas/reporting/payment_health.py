from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


_HIGH_CHURN_RISK_THRESHOLD = 0.30
_BAD_DEBT_RATE_AMBER = 0.0075  # 0.75% of revenue
_BAD_DEBT_RATE_RED = 0.0150    # 1.5% of revenue
_AT_RISK_PCT_RED = 60.0        # >60% of customers at high churn risk
_AT_RISK_PCT_AMBER = 30.0      # >30% of customers at high churn risk
_TREND_DETERIORATING_FACTOR = 1.20
_TREND_IMPROVING_FACTOR = 0.80


@dataclass(frozen=True)
class PaymentHealthSummary:
    year: int
    bad_debt_gbp: float
    revenue_gbp: float
    bad_debt_rate: float       # bad_debt_gbp / revenue_gbp
    at_risk_customer_count: int
    total_customer_count: int
    at_risk_pct: float         # at_risk / total * 100
    trend: Literal["IMPROVING", "STABLE", "DETERIORATING"]
    rag: Literal["GREEN", "AMBER", "RED"]


def _trend(current_rate: float, prior_rate: float | None) -> Literal["IMPROVING", "STABLE", "DETERIORATING"]:
    if prior_rate is None or prior_rate == 0:
        return "STABLE"
    if current_rate > prior_rate * _TREND_DETERIORATING_FACTOR:
        return "DETERIORATING"
    if current_rate < prior_rate * _TREND_IMPROVING_FACTOR:
        return "IMPROVING"
    return "STABLE"


def _rag(bad_debt_rate: float, at_risk_pct: float) -> Literal["GREEN", "AMBER", "RED"]:
    if bad_debt_rate > _BAD_DEBT_RATE_RED or at_risk_pct > _AT_RISK_PCT_RED:
        return "RED"
    if bad_debt_rate > _BAD_DEBT_RATE_AMBER or at_risk_pct > _AT_RISK_PCT_AMBER:
        return "AMBER"
    return "GREEN"


def _build_summary(yr_str: str, year_data: dict, prior_rate: float | None) -> PaymentHealthSummary:
    bad_debt = year_data.get("bad_debt_gbp", 0.0)
    revenue = year_data.get("revenue_gbp", 0.0)
    bad_debt_rate = bad_debt / revenue if revenue > 0 else 0.0

    churn_risk = year_data.get("churn_risk_by_account", {})
    total_customers = len(churn_risk)
    at_risk = sum(
        1 for v in churn_risk.values()
        if isinstance(v, (int, float)) and v > _HIGH_CHURN_RISK_THRESHOLD
    )
    at_risk_pct = at_risk / total_customers * 100 if total_customers > 0 else 0.0

    return PaymentHealthSummary(
        year=int(yr_str),
        bad_debt_gbp=bad_debt,
        revenue_gbp=revenue,
        bad_debt_rate=bad_debt_rate,
        at_risk_customer_count=at_risk,
        total_customer_count=total_customers,
        at_risk_pct=at_risk_pct,
        trend=_trend(bad_debt_rate, prior_rate),
        rag=_rag(bad_debt_rate, at_risk_pct),
    )


def build_payment_health_series(run_data: dict) -> list[PaymentHealthSummary]:
    years_raw = run_data.get("years", {})
    summaries = []
    prior_rate: float | None = None
    for yr_str in sorted(years_raw.keys()):
        summary = _build_summary(yr_str, years_raw[yr_str], prior_rate)
        summaries.append(summary)
        prior_rate = summary.bad_debt_rate
    return summaries
