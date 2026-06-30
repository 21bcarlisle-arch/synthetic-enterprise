"""Standing Charge Fairness Assessor (Phase FP).

Standing charges (daily pence/day) are fixed per-customer costs regardless
of consumption. They've been controversial because:

1. Low-usage customers (fuel poor, students, away homes) pay a higher share
   of their bill as standing charges vs consumption
2. In the 2022-23 crisis, Ofgem capped unit rates but standing charges rose
   significantly (some suppliers: 50p/day+ = £182/yr just for connection)
3. Ofgem has asked suppliers to justify standing charge levels as part of
   Consumer Duty obligations (fair outcomes for vulnerable customers)

OFGEM Price Cap (2023 Q3): electricity standing charge ~53p/day, gas ~29p/day
Pre-crisis (2021): electricity ~25p/day, gas ~25p/day

Key fairness metrics:
- Standing charge as % of total bill (should not dominate for standard consumers)
- Cross-subsidy: high-usage customers effectively subsidise network costs for
  low-usage customers when standing charges are below cost-recovery level
- Prepayment meter premium: historically ~£100/yr extra (PPM scandal 2023)

From regulatory/consumer_duty perspective:
- SLC 22A: bills must be clear; standing charges prominently shown
- Consumer Duty: fair pricing; vulnerable customers must not be disadvantaged
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List


class SCFairnessRating(str, Enum):
    FAIR = "fair"               # within Ofgem reasonable range
    BORDERLINE = "borderline"   # approaching concern
    UNFAIR = "unfair"           # Ofgem likely to challenge
    EXCESSIVE = "excessive"     # well above Ofgem cap


class ConsumerImpactLevel(str, Enum):
    LOW = "low"         # standing charge < 20% of typical bill
    MEDIUM = "medium"   # 20-35%
    HIGH = "high"       # 35-50%
    CRITICAL = "critical"  # >50%: standing charges dominate bill


_OFGEM_SC_CAP_ELEC_PENCE_PER_DAY = 61.0    # Q3 2024
_OFGEM_SC_CAP_GAS_PENCE_PER_DAY = 31.0
_TYPICAL_ELEC_KWH = 2900.0                  # Ofgem typical household
_TYPICAL_GAS_KWH = 11500.0


@dataclass(frozen=True)
class StandingChargeAssessment:
    tariff_id: str
    is_electricity: bool
    standing_charge_pence_per_day: float
    unit_rate_pence_per_kwh: float

    @property
    def annual_sc_gbp(self) -> float:
        return 365 * self.standing_charge_pence_per_day / 100

    @property
    def typical_annual_unit_cost_gbp(self) -> float:
        consumption = _TYPICAL_ELEC_KWH if self.is_electricity else _TYPICAL_GAS_KWH
        return consumption * self.unit_rate_pence_per_kwh / 100

    @property
    def typical_annual_bill_gbp(self) -> float:
        return self.annual_sc_gbp + self.typical_annual_unit_cost_gbp

    @property
    def sc_pct_of_typical_bill(self) -> float:
        if self.typical_annual_bill_gbp <= 0:
            return 0.0
        return 100.0 * self.annual_sc_gbp / self.typical_annual_bill_gbp

    @property
    def cap_reference(self) -> float:
        return _OFGEM_SC_CAP_ELEC_PENCE_PER_DAY if self.is_electricity \
            else _OFGEM_SC_CAP_GAS_PENCE_PER_DAY

    @property
    def fairness_rating(self) -> SCFairnessRating:
        pct_over_cap = 100.0 * (self.standing_charge_pence_per_day - self.cap_reference) / self.cap_reference
        if pct_over_cap > 30:
            return SCFairnessRating.EXCESSIVE
        if pct_over_cap > 10:
            return SCFairnessRating.UNFAIR
        if pct_over_cap > -10:
            return SCFairnessRating.BORDERLINE
        return SCFairnessRating.FAIR

    @property
    def consumer_impact(self) -> ConsumerImpactLevel:
        pct = self.sc_pct_of_typical_bill
        if pct > 50:
            return ConsumerImpactLevel.CRITICAL
        if pct > 35:
            return ConsumerImpactLevel.HIGH
        if pct > 20:
            return ConsumerImpactLevel.MEDIUM
        return ConsumerImpactLevel.LOW

    def assessment_summary(self) -> str:
        fuel = "electricity" if self.is_electricity else "gas"
        return (
            "SCAssessment " + self.tariff_id + " (" + fuel + "): "
            + str(round(self.standing_charge_pence_per_day, 1)) + "p/day "
            "annual=GBP" + str(round(self.annual_sc_gbp, 0)) + " "
            "[" + self.fairness_rating.value + "] "
            "impact=" + self.consumer_impact.value
        )


class StandingChargeAssessor:

    def __init__(self) -> None:
        self._assessments: List[StandingChargeAssessment] = []

    def assess(self, a: StandingChargeAssessment) -> StandingChargeAssessment:
        self._assessments.append(a)
        return a

    def unfair_or_worse(self) -> List[StandingChargeAssessment]:
        bad = {SCFairnessRating.UNFAIR, SCFairnessRating.EXCESSIVE}
        return [a for a in self._assessments if a.fairness_rating in bad]

    def high_impact_assessments(self) -> List[StandingChargeAssessment]:
        bad = {ConsumerImpactLevel.HIGH, ConsumerImpactLevel.CRITICAL}
        return [a for a in self._assessments if a.consumer_impact in bad]

    def max_annual_sc_gbp(self) -> float:
        if not self._assessments:
            return 0.0
        return max(a.annual_sc_gbp for a in self._assessments)

    def sc_assessor_summary(self) -> str:
        n = len(self._assessments)
        n_unfair = len(self.unfair_or_worse())
        n_impact = len(self.high_impact_assessments())
        return (
            "Standing Charge Assessor: " + str(n) + " tariffs assessed. "
            "Unfair/excessive: " + str(n_unfair) + ". "
            "High consumer impact: " + str(n_impact) + "."
        )
