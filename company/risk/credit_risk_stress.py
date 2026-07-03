"""Credit risk stress for Ofgem FRA capital adequacy (Phase NR).

Post-2022 Ofgem FRA requires combined stress testing: market risk (price VaR) AND
credit risk (customer bad debt shock). This module models the credit side.

Empirical basis: Ofgem 2022 consumer vulnerability report — industry bad debt rose
from ~1% to ~2.5% of revenue during 2021-22 crisis (2.5x multiplier).
"""
from __future__ import annotations

from dataclasses import dataclass


CRISIS_BAD_DEBT_MULTIPLIER: float = 2.5   # Ofgem 2022 empirical: crisis = 2.5x normal
MATERIAL_THRESHOLD_PCT: float = 0.5       # incremental > 0.5% revenue = board-material


@dataclass(frozen=True)
class CreditRiskStress:
    current_provision_gbp: float
    stress_multiplier: float
    annual_revenue_gbp: float

    @property
    def stressed_provision_gbp(self) -> float:
        return self.current_provision_gbp * self.stress_multiplier

    @property
    def stress_incremental_gbp(self) -> float:
        """Additional capital consumed above current provision in a crisis."""
        return max(0.0, self.stressed_provision_gbp - self.current_provision_gbp)

    @property
    def is_material(self) -> bool:
        """True if incremental stress exceeds 0.5% of annual revenue."""
        if self.annual_revenue_gbp <= 0:
            return False
        return (self.stress_incremental_gbp / self.annual_revenue_gbp * 100) > MATERIAL_THRESHOLD_PCT

    def summary(self) -> dict:
        return {
            "current_provision_gbp": round(self.current_provision_gbp, 2),
            "stress_multiplier": self.stress_multiplier,
            "stressed_provision_gbp": round(self.stressed_provision_gbp, 2),
            "stress_incremental_gbp": round(self.stress_incremental_gbp, 2),
            "is_material": self.is_material,
        }


def build_credit_risk_stress(
    current_provision_gbp: float,
    annual_revenue_gbp: float,
    stress_multiplier: float = CRISIS_BAD_DEBT_MULTIPLIER,
) -> CreditRiskStress:
    return CreditRiskStress(
        current_provision_gbp=current_provision_gbp,
        stress_multiplier=stress_multiplier,
        annual_revenue_gbp=annual_revenue_gbp,
    )
