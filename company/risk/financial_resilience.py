"""Financial Resilience Assessment (FRA): Ofgem mandatory quarterly framework post-2022."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class FRAStatus(str, Enum):
    RESILIENT = "resilient"       # >12 months liquidity, stress tests passed
    ADEQUATE = "adequate"         # 6-12 months, stress tests passed
    BORDERLINE = "borderline"     # 3-6 months or borderline stress
    INADEQUATE = "inadequate"     # <3 months or stress test failure


class FRATrigger(str, Enum):
    ROUTINE_QUARTERLY = "routine_quarterly"
    MARKET_STRESS_EVENT = "market_stress_event"   # triggered by e.g. NBP spike
    REGULATOR_DIRECTED = "regulator_directed"


_RESILIENT_MONTHS = 12
_ADEQUATE_MONTHS = 6
_BORDERLINE_MONTHS = 3


@dataclass(frozen=True)
class FRAAssessment:
    year: int
    quarter: int                        # 1-4
    assessment_date: dt.date
    trigger: FRATrigger
    treasury_gbp: float
    credit_facility_headroom_gbp: float
    monthly_fixed_costs_gbp: float      # monthly burn rate (non-wholesale)
    stress_test_passed: bool
    var_within_limit: bool
    net_wholesale_exposure_gbp: float   # open unhedged exposure

    @property
    def total_liquidity_gbp(self) -> float:
        return self.treasury_gbp + self.credit_facility_headroom_gbp

    @property
    def months_of_liquidity(self) -> Optional[float]:
        if self.monthly_fixed_costs_gbp <= 0:
            return None
        return round(self.total_liquidity_gbp / self.monthly_fixed_costs_gbp, 1)

    @property
    def status(self) -> FRAStatus:
        months = self.months_of_liquidity
        if months is None:
            return FRAStatus.BORDERLINE
        if not self.stress_test_passed or not self.var_within_limit:
            if months < _BORDERLINE_MONTHS:
                return FRAStatus.INADEQUATE
            return FRAStatus.BORDERLINE
        if months >= _RESILIENT_MONTHS:
            return FRAStatus.RESILIENT
        if months >= _ADEQUATE_MONTHS:
            return FRAStatus.ADEQUATE
        if months >= _BORDERLINE_MONTHS:
            return FRAStatus.BORDERLINE
        return FRAStatus.INADEQUATE

    @property
    def is_compliant(self) -> bool:
        return self.status != FRAStatus.INADEQUATE

    @property
    def period_label(self) -> str:
        return f"{self.year}Q{self.quarter}"


class FinancialResilienceBook:
    """Tracks quarterly FRA submissions.

    Real calibration:
    - Ofgem FRA Framework: introduced after 28 supplier failures in 2021-22 crisis
    - Quarterly mandatory; board sign-off required
    - Minimum requirement: demonstrate 12+ months of liquidity runway
    - Stress tests must be passed (see stress_test.py Ph303)
    - VaR must be within approved limits (see var_monitor.py Ph282)
    - Persistent INADEQUATE rating: Ofgem can direct remedial action or revoke licence
    - Key failure mode (Bulb, Avro, Igloo etc.): no formal resilience framework meant
      they did not know how close to insolvency they were until margin calls hit
    """

    def __init__(self) -> None:
        self._assessments: List[FRAAssessment] = []

    def record_assessment(self, assessment: FRAAssessment) -> FRAAssessment:
        self._assessments.append(assessment)
        return assessment

    def assessments_for_year(self, year: int) -> List[FRAAssessment]:
        return [a for a in self._assessments if a.year == year]

    def latest_assessment(self) -> Optional[FRAAssessment]:
        if not self._assessments:
            return None
        return sorted(self._assessments, key=lambda a: a.assessment_date)[-1]

    def inadequate_quarters(self) -> List[FRAAssessment]:
        return [a for a in self._assessments if a.status == FRAStatus.INADEQUATE]

    def borderline_or_worse(self) -> List[FRAAssessment]:
        return [a for a in self._assessments
                if a.status in (FRAStatus.BORDERLINE, FRAStatus.INADEQUATE)]

    def trend_is_deteriorating(self) -> bool:
        sorted_assessments = sorted(self._assessments, key=lambda a: a.assessment_date)
        if len(sorted_assessments) < 3:
            return False
        last_3 = sorted_assessments[-3:]
        statuses = [FRAStatus.RESILIENT, FRAStatus.ADEQUATE, FRAStatus.BORDERLINE, FRAStatus.INADEQUATE]
        indices = [statuses.index(a.status) for a in last_3]
        return indices[2] > indices[1] >= indices[0]

    def fra_summary(self) -> dict:
        assessments = sorted(self._assessments, key=lambda a: a.assessment_date)
        latest = self.latest_assessment()
        return {
            "total_assessments": len(self._assessments),
            "inadequate_quarters": len(self.inadequate_quarters()),
            "borderline_or_worse": len(self.borderline_or_worse()),
            "trend_deteriorating": self.trend_is_deteriorating(),
            "latest_status": latest.status.value if latest else None,
            "latest_liquidity_months": latest.months_of_liquidity if latest else None,
        }
