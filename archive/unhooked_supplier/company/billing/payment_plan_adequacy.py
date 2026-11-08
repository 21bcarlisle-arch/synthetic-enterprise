"""Payment plan adequacy: Ofgem Ability to Pay (ATP) compliance assessment."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ATPCompliance(str, Enum):
    AFFORDABLE = "affordable"       # plan <= 15% of disposable income
    BORDERLINE = "borderline"       # 15-25% of disposable income
    UNAFFORDABLE = "unaffordable"   # >25% of disposable income
    UNKNOWN = "unknown"             # insufficient income data


_AFFORDABLE_THRESHOLD_PCT = 15.0   # below this: plan is affordable
_BORDERLINE_THRESHOLD_PCT = 25.0   # above this: plan is unaffordable
_MIN_DISPOSABLE_GBP = 50.0         # floor: plans cannot leave <£50/month disposable


@dataclass(frozen=True)
class PaymentPlanAdequacyCheck:
    account_id: str
    assessment_date: dt.date
    monthly_plan_gbp: float
    estimated_monthly_income_gbp: Optional[float]
    monthly_essential_costs_gbp: Optional[float]
    is_vulnerable: bool = False

    @property
    def disposable_income_gbp(self) -> Optional[float]:
        if self.estimated_monthly_income_gbp is None or self.monthly_essential_costs_gbp is None:
            return None
        return max(0.0, self.estimated_monthly_income_gbp - self.monthly_essential_costs_gbp)

    @property
    def plan_as_pct_disposable(self) -> Optional[float]:
        d = self.disposable_income_gbp
        if d is None or d <= 0:
            return None
        return round(self.monthly_plan_gbp / d * 100, 1)

    @property
    def compliance(self) -> ATPCompliance:
        pct = self.plan_as_pct_disposable
        d = self.disposable_income_gbp
        if pct is None:
            return ATPCompliance.UNKNOWN
        if d is not None and (d - self.monthly_plan_gbp) < _MIN_DISPOSABLE_GBP:
            return ATPCompliance.UNAFFORDABLE
        if pct <= _AFFORDABLE_THRESHOLD_PCT:
            return ATPCompliance.AFFORDABLE
        if pct <= _BORDERLINE_THRESHOLD_PCT:
            return ATPCompliance.BORDERLINE
        return ATPCompliance.UNAFFORDABLE

    @property
    def is_compliant(self) -> bool:
        return self.compliance != ATPCompliance.UNAFFORDABLE


class PaymentPlanAdequacyBook:
    """Tracks ATP compliance of payment plans across the portfolio.

    Real calibration:
    - Ofgem ATP guidance: plan ideally <15% of discretionary income
    - 2022-23 crisis: energy bills tripled; 40% of customers on plans couldn't afford them
      (Citizens Advice survey 2023)
    - Unaffordable plans -> PPM installation request -> self-rationing -> fuel poverty
    - Vulnerable customers on unaffordable plans: immediate welfare referral required
    - Ofgem enforcement: suppliers must proactively review plans annually and after
      any significant bill increase (SLC 27A, Ability to Pay)
    """

    def __init__(self) -> None:
        self._checks: List[PaymentPlanAdequacyCheck] = []

    def record_check(self, check: PaymentPlanAdequacyCheck) -> PaymentPlanAdequacyCheck:
        self._checks.append(check)
        return check

    def checks_for(self, account_id: str) -> List[PaymentPlanAdequacyCheck]:
        return [c for c in self._checks if c.account_id == account_id]

    def latest_for(self, account_id: str) -> Optional[PaymentPlanAdequacyCheck]:
        matches = sorted(self.checks_for(account_id), key=lambda x: x.assessment_date)
        return matches[-1] if matches else None

    def non_compliant_plans(self) -> List[PaymentPlanAdequacyCheck]:
        return [c for c in self._checks if c.compliance == ATPCompliance.UNAFFORDABLE]

    def borderline_plans(self) -> List[PaymentPlanAdequacyCheck]:
        return [c for c in self._checks if c.compliance == ATPCompliance.BORDERLINE]

    def unknown_income_plans(self) -> List[PaymentPlanAdequacyCheck]:
        return [c for c in self._checks if c.compliance == ATPCompliance.UNKNOWN]

    def vulnerable_non_compliant(self) -> List[PaymentPlanAdequacyCheck]:
        return [c for c in self.non_compliant_plans() if c.is_vulnerable]

    def total_at_risk_gbp(self) -> float:
        return round(sum(c.monthly_plan_gbp for c in self.non_compliant_plans()), 2)

    def adequacy_summary(self) -> dict:
        from collections import Counter
        counts = Counter(c.compliance.value for c in self._checks)
        return {
            "total_checks": len(self._checks),
            "affordable": counts.get(ATPCompliance.AFFORDABLE.value, 0),
            "borderline": counts.get(ATPCompliance.BORDERLINE.value, 0),
            "unaffordable": counts.get(ATPCompliance.UNAFFORDABLE.value, 0),
            "unknown": counts.get(ATPCompliance.UNKNOWN.value, 0),
            "vulnerable_non_compliant": len(self.vulnerable_non_compliant()),
            "total_at_risk_gbp": self.total_at_risk_gbp(),
        }
