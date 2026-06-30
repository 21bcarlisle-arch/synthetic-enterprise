"""Switching Friction Cost-Benefit Analyser (Phase EJ)."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List


class RetentionDecision(str, Enum):
    RETAIN_WITH_OFFER = "retain_with_offer"
    RETAIN_PASSIVELY = "retain_passively"
    LET_GO = "let_go"
    REFER_TO_COMMITTEE = "refer_to_committee"


_PASSIVE_RETENTION_AE_FLOOR = 90.0
_RETENTION_OFFER_MIN_ROI = 1.5
_BORDERLINE_MARGIN_PCT = 20.0


@dataclass(frozen=True)
class SwitchingCostBenefitAnalysis:
    account_id: str
    analysed_at: dt.date
    remaining_contract_years: float
    annual_margin_gbp: float
    current_switching_ae: float
    perceived_saving_gbp: float
    retention_offer_gbp: float
    replacement_cac_gbp: float
    discount_rate: float = 0.08

    @property
    def future_clv_if_retained_gbp(self) -> float:
        survival = (1 / (1 + self.discount_rate)) ** self.remaining_contract_years
        return self.annual_margin_gbp * self.remaining_contract_years * survival

    @property
    def net_benefit_of_offer_gbp(self) -> float:
        return self.future_clv_if_retained_gbp - self.retention_offer_gbp

    @property
    def offer_roi(self) -> float:
        if self.retention_offer_gbp <= 0:
            return float("inf")
        return self.future_clv_if_retained_gbp / self.retention_offer_gbp

    @property
    def is_customer_likely_to_switch(self) -> bool:
        return self.perceived_saving_gbp >= self.current_switching_ae

    @property
    def passive_friction_retains(self) -> bool:
        return self.current_switching_ae > _PASSIVE_RETENTION_AE_FLOOR

    @property
    def decision(self) -> RetentionDecision:
        if not self.is_customer_likely_to_switch:
            return RetentionDecision.RETAIN_PASSIVELY
        if self.passive_friction_retains:
            return RetentionDecision.RETAIN_PASSIVELY
        roi = self.offer_roi
        clv = self.future_clv_if_retained_gbp
        threshold = _RETENTION_OFFER_MIN_ROI
        border = abs(roi - threshold) / threshold
        if border < _BORDERLINE_MARGIN_PCT / 100:
            return RetentionDecision.REFER_TO_COMMITTEE
        if roi >= threshold and clv > self.replacement_cac_gbp:
            return RetentionDecision.RETAIN_WITH_OFFER
        return RetentionDecision.LET_GO

    def analysis_summary(self) -> str:
        return (
            "CBA(" + self.account_id + "): "
            "CLV=GBP" + str(round(self.future_clv_if_retained_gbp)) +
            " offer=GBP" + str(round(self.retention_offer_gbp)) +
            " ROI=" + str(round(self.offer_roi, 1)) + "x" +
            " -> " + self.decision.value
        )


class SwitchingCBABook:

    def __init__(self) -> None:
        self._analyses: List[SwitchingCostBenefitAnalysis] = []

    def analyse(self, analysis: SwitchingCostBenefitAnalysis) -> SwitchingCostBenefitAnalysis:
        self._analyses.append(analysis)
        return analysis

    def analyses_for(self, account_id: str) -> List[SwitchingCostBenefitAnalysis]:
        return [a for a in self._analyses if a.account_id == account_id]

    def retain_with_offer(self) -> List[SwitchingCostBenefitAnalysis]:
        return [a for a in self._analyses if a.decision == RetentionDecision.RETAIN_WITH_OFFER]

    def let_go(self) -> List[SwitchingCostBenefitAnalysis]:
        return [a for a in self._analyses if a.decision == RetentionDecision.LET_GO]

    def refer_to_committee(self) -> List[SwitchingCostBenefitAnalysis]:
        return [a for a in self._analyses if a.decision == RetentionDecision.REFER_TO_COMMITTEE]

    def total_retention_spend_gbp(self) -> float:
        return sum(a.retention_offer_gbp for a in self.retain_with_offer())

    def total_clv_at_stake_gbp(self) -> float:
        active = [a for a in self._analyses if a.is_customer_likely_to_switch]
        return sum(a.future_clv_if_retained_gbp for a in active)

    def portfolio_summary(self, as_of: dt.date) -> str:
        n = len(self._analyses)
        n_offer = len(self.retain_with_offer())
        n_let = len(self.let_go())
        n_ref = len(self.refer_to_committee())
        n_passive = n - n_offer - n_let - n_ref
        return (
            "Switching CBA (" + str(as_of) + "): " + str(n) + " analyses. "
            "Retain-offer=" + str(n_offer) + " let-go=" + str(n_let) +
            " committee=" + str(n_ref) + " passive=" + str(n_passive) + "."
        )
