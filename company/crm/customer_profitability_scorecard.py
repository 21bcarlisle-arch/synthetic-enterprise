"""Customer Profitability Scorecard (Phase FK).

Aggregates per-customer signals into a profitability score that the CRM
team uses to prioritize retention investment and cross-sell targeting.

Score components (each 0-25 points, total 0-100):
1. Margin contribution (0-25): net margin / target_margin, capped at 25
2. Tenure stability (0-25): years with company, capped at 5yr = 25pts
3. CLV potential (0-25): H3 CLV / target_CLV, capped at 25
4. Service cost burden (0-25): inverse of cost_to_serve/revenue; low cost = more points

Scorecard tiers:
- PLATINUM: 80-100 (retain at all costs, proactive upsell)
- GOLD: 60-79 (valuable; retain with standard offer)
- SILVER: 40-59 (average; monitor, opportunistic retention)
- BRONZE: 20-39 (below average; minimal retention spend)
- LOSS_MAKING: 0-19 (negative value; manage exit or fundamental reprice)

This module is a synthesis of Phase EI (AccountIntelligence), Phase J (margin),
Phase AD (churn risk), Phase EW (service tickets).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ScorecardTier(str, Enum):
    PLATINUM = "platinum"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    LOSS_MAKING = "loss_making"


_TIER_THRESHOLDS = {
    ScorecardTier.PLATINUM: 80,
    ScorecardTier.GOLD: 60,
    ScorecardTier.SILVER: 40,
    ScorecardTier.BRONZE: 20,
    ScorecardTier.LOSS_MAKING: 0,
}

_TARGET_ANNUAL_MARGIN_GBP = 150.0
_TARGET_CLV_GBP = 500.0
_MAX_TENURE_YEARS = 5
_PLATINUM_RETENTION_BUDGET_GBP = 200.0
_GOLD_RETENTION_BUDGET_GBP = 80.0


@dataclass(frozen=True)
class CustomerProfitabilityScore:
    account_id: str
    scored_at: dt.date
    annual_margin_gbp: float
    tenure_years: float
    h3_clv_gbp: float
    cost_to_serve_gbp: float
    annual_revenue_gbp: float

    @property
    def margin_score(self) -> float:
        if _TARGET_ANNUAL_MARGIN_GBP <= 0:
            return 0.0
        return min(25.0, 25.0 * self.annual_margin_gbp / _TARGET_ANNUAL_MARGIN_GBP)

    @property
    def tenure_score(self) -> float:
        return min(25.0, 25.0 * self.tenure_years / _MAX_TENURE_YEARS)

    @property
    def clv_score(self) -> float:
        if _TARGET_CLV_GBP <= 0:
            return 0.0
        return min(25.0, 25.0 * self.h3_clv_gbp / _TARGET_CLV_GBP)

    @property
    def service_efficiency_score(self) -> float:
        if self.annual_revenue_gbp <= 0:
            return 0.0
        cost_ratio = self.cost_to_serve_gbp / self.annual_revenue_gbp
        if cost_ratio >= 1.0:
            return 0.0
        return 25.0 * (1.0 - cost_ratio)

    @property
    def total_score(self) -> float:
        return (
            self.margin_score
            + self.tenure_score
            + self.clv_score
            + self.service_efficiency_score
        )

    @property
    def tier(self) -> ScorecardTier:
        score = self.total_score
        if score >= 80:
            return ScorecardTier.PLATINUM
        if score >= 60:
            return ScorecardTier.GOLD
        if score >= 40:
            return ScorecardTier.SILVER
        if score >= 20:
            return ScorecardTier.BRONZE
        return ScorecardTier.LOSS_MAKING

    @property
    def max_retention_budget_gbp(self) -> float:
        if self.tier == ScorecardTier.PLATINUM:
            return _PLATINUM_RETENTION_BUDGET_GBP
        if self.tier == ScorecardTier.GOLD:
            return _GOLD_RETENTION_BUDGET_GBP
        return 0.0

    def scorecard_summary(self) -> str:
        return (
            "Scorecard " + self.account_id + " [" + self.tier.value + "]: "
            + str(round(self.total_score, 1)) + "/100 "
            "(margin=" + str(round(self.margin_score, 1))
            + " tenure=" + str(round(self.tenure_score, 1))
            + " clv=" + str(round(self.clv_score, 1))
            + " efficiency=" + str(round(self.service_efficiency_score, 1)) + ")"
        )
