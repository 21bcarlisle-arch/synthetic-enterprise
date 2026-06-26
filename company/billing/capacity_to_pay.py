"""Capacity-to-Pay (CtP) affordability assessment for customers in arrears."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class AffordabilityOutcome(str, Enum):
    CAN_PAY_IN_FULL = 'can_pay_in_full'
    CAN_PAY_PARTIAL = 'can_pay_partial'
    CANNOT_PAY = 'cannot_pay'
    FUEL_POVERTY = 'fuel_poverty'


class RecommendedAction(str, Enum):
    STANDARD_PLAN = 'standard_plan'
    EXTENDED_PLAN = 'extended_plan'
    MINIMUM_PLAN = 'minimum_plan'
    PPM_CONVERSION = 'ppm_conversion'
    DEBT_ADVICE_REFERRAL = 'debt_advice_referral'
    WRITE_OFF_CONSIDERATION = 'write_off_consideration'


_STANDARD_PLAN_MONTHS = 12
_EXTENDED_PLAN_MONTHS = 24
_MINIMUM_PAYMENT_GBP = 5.0


@dataclass(frozen=True)
class CtPAssessment:
    customer_id: str
    assessment_date: dt.date
    monthly_income_gbp: float
    monthly_essential_outgoings_gbp: float
    total_debt_gbp: float
    is_vulnerable: bool = False

    @property
    def disposable_income_gbp(self) -> float:
        return max(0.0, self.monthly_income_gbp - self.monthly_essential_outgoings_gbp)

    @property
    def energy_share_of_income_pct(self) -> Optional[float]:
        if self.monthly_income_gbp <= 0:
            return None
        return round(self.total_debt_gbp / (self.monthly_income_gbp * 12) * 100, 1)

    @property
    def affordable_monthly_repayment_gbp(self) -> float:
        return round(min(self.disposable_income_gbp * 0.10, self.total_debt_gbp), 2)

    @property
    def outcome(self) -> AffordabilityOutcome:
        esi = self.energy_share_of_income_pct
        if esi is not None and esi >= 10.0:
            return AffordabilityOutcome.FUEL_POVERTY
        if self.affordable_monthly_repayment_gbp <= 0:
            return AffordabilityOutcome.CANNOT_PAY
        if self.affordable_monthly_repayment_gbp * _STANDARD_PLAN_MONTHS >= self.total_debt_gbp:
            return AffordabilityOutcome.CAN_PAY_IN_FULL
        return AffordabilityOutcome.CAN_PAY_PARTIAL

    @property
    def recommended_action(self) -> RecommendedAction:
        out = self.outcome
        if out == AffordabilityOutcome.FUEL_POVERTY:
            return (RecommendedAction.PPM_CONVERSION if self.is_vulnerable
                    else RecommendedAction.DEBT_ADVICE_REFERRAL)
        if out == AffordabilityOutcome.CANNOT_PAY:
            return RecommendedAction.WRITE_OFF_CONSIDERATION
        if out == AffordabilityOutcome.CAN_PAY_PARTIAL:
            repayment_months = (self.total_debt_gbp /
                                max(self.affordable_monthly_repayment_gbp, _MINIMUM_PAYMENT_GBP))
            if repayment_months <= _EXTENDED_PLAN_MONTHS:
                return RecommendedAction.EXTENDED_PLAN
            return RecommendedAction.MINIMUM_PLAN
        return RecommendedAction.STANDARD_PLAN

    @property
    def estimated_plan_months(self) -> Optional[int]:
        repayment = max(self.affordable_monthly_repayment_gbp, _MINIMUM_PAYMENT_GBP)
        if repayment <= 0 or self.outcome == AffordabilityOutcome.CANNOT_PAY:
            return None
        return round(self.total_debt_gbp / repayment)

    def summary(self) -> dict:
        return {
            'customer_id': self.customer_id,
            'assessment_date': self.assessment_date.isoformat(),
            'disposable_income_gbp': self.disposable_income_gbp,
            'affordable_monthly_repayment_gbp': self.affordable_monthly_repayment_gbp,
            'outcome': self.outcome.value,
            'recommended_action': self.recommended_action.value,
            'estimated_plan_months': self.estimated_plan_months,
            'energy_share_of_income_pct': self.energy_share_of_income_pct,
        }
