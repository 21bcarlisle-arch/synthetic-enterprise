"""Account Intelligence Report (Phase EI).

Synthesizes: ResentmentLedger + ThreeHorizonCLVTracker +
ActivationEnergyRegister + GlobalReputationIndex into per-account
action recommendations.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class RecommendedAction(str, Enum):
    IMMEDIATE_RETENTION = "immediate_retention"
    TARGETED_REPRICE = "targeted_reprice"
    PROACTIVE_SERVICE = "proactive_service"
    MONITOR = "monitor"
    MANAGE_EXIT = "manage_exit"
    UPSELL = "upsell"


class AccountIntelligenceRating(str, Enum):
    PREMIUM = "premium"
    STABLE = "stable"
    AT_RISK = "at_risk"
    BURNED = "burned"


@dataclass(frozen=True)
class AccountIntelligenceReport:
    account_id: str
    generated_at: dt.date
    resentment_score: float
    is_burned: bool
    h3_signal: Optional[str]
    switching_ae: float
    gri_multiplier: float
    max_retention_offer_gbp: float

    @property
    def rating(self) -> AccountIntelligenceRating:
        if self.is_burned:
            return AccountIntelligenceRating.BURNED
        if self.resentment_score > 35 or self.h3_signal in ("at_risk", "deteriorating"):
            return AccountIntelligenceRating.AT_RISK
        if self.h3_signal == "outperforming" and self.resentment_score < 10:
            return AccountIntelligenceRating.PREMIUM
        return AccountIntelligenceRating.STABLE

    @property
    def recommended_action(self) -> RecommendedAction:
        if self.is_burned:
            return RecommendedAction.MANAGE_EXIT
        if self.resentment_score > 40 and self.h3_signal == "at_risk":
            return RecommendedAction.IMMEDIATE_RETENTION
        if self.h3_signal == "at_risk":
            return RecommendedAction.TARGETED_REPRICE
        if self.resentment_score > 25:
            return RecommendedAction.PROACTIVE_SERVICE
        if self.h3_signal == "outperforming":
            return RecommendedAction.UPSELL
        return RecommendedAction.MONITOR

    @property
    def action_urgency_days(self) -> int:
        action = self.recommended_action
        if action == RecommendedAction.IMMEDIATE_RETENTION:
            return 1
        if action in (RecommendedAction.TARGETED_REPRICE, RecommendedAction.PROACTIVE_SERVICE):
            return 7
        if action == RecommendedAction.UPSELL:
            return 30
        return 90

    def intelligence_summary(self) -> str:
        return (
            "Account " + self.account_id + " (" + self.rating.value + "): "
            "resentment=" + str(round(self.resentment_score)) + ", "
            "H3=" + (self.h3_signal or "n/a") + ", "
            "action=" + self.recommended_action.value + " "
            "within " + str(self.action_urgency_days) + "d."
        )


class AccountIntelligenceEngine:

    @staticmethod
    def generate(
        account_id: str,
        as_of: dt.date,
        resentment_score: float,
        is_burned: bool,
        h3_signal: Optional[str],
        switching_ae: float,
        gri_multiplier: float,
        max_retention_offer_gbp: float,
    ) -> AccountIntelligenceReport:
        return AccountIntelligenceReport(
            account_id=account_id,
            generated_at=as_of,
            resentment_score=resentment_score,
            is_burned=is_burned,
            h3_signal=h3_signal,
            switching_ae=switching_ae,
            gri_multiplier=gri_multiplier,
            max_retention_offer_gbp=max_retention_offer_gbp,
        )

    @staticmethod
    def portfolio_action_counts(reports: List[AccountIntelligenceReport]) -> dict:
        counts: dict = {}
        for r in reports:
            a = r.recommended_action.value
            counts[a] = counts.get(a, 0) + 1
        return counts

    @staticmethod
    def immediate_actions(reports: List[AccountIntelligenceReport]) -> List[AccountIntelligenceReport]:
        return [r for r in reports if r.action_urgency_days <= 7]

    @staticmethod
    def premium_accounts(reports: List[AccountIntelligenceReport]) -> List[AccountIntelligenceReport]:
        return [r for r in reports if r.rating == AccountIntelligenceRating.PREMIUM]

    @staticmethod
    def portfolio_intelligence_summary(reports: List[AccountIntelligenceReport], as_of: dt.date) -> str:
        n = len(reports)
        n_premium = len(AccountIntelligenceEngine.premium_accounts(reports))
        n_immediate = len(AccountIntelligenceEngine.immediate_actions(reports))
        n_burned = sum(1 for r in reports if r.is_burned)
        return (
            "Portfolio Intelligence (" + str(as_of) + "): " + str(n) + " accounts. "
            "Premium: " + str(n_premium) + ". Immediate action: " + str(n_immediate) + ". "
            "Burned (irrecoverable): " + str(n_burned) + "."
        )
