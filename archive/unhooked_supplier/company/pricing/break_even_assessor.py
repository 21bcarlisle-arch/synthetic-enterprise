"""Break-Even Tariff Assessor.

For each customer, computes the minimum unit rate (break-even rate) that recovers
all costs (wholesale + levies + operating). Compares this against the Ofgem price
cap for the period. If break-even > cap, the customer is structurally constrained:
the company cannot price profitably within the regulatory ceiling.

Connects Phase 294 (cost-to-serve) with Phase 295 (Ofgem price cap) to surface
which customers are net-negative by structural constraint vs. by tariff choice.

All inputs are company-observable. Epistemic-compliant.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BreakEvenAssessment:
    """Break-even tariff analysis for one customer account."""
    account_id: str
    year: int
    fuel: str  # "electricity" or "gas"
    consumption_kwh: float
    total_cost_p_per_kwh: float      # wholesale + levies + operating (p/kWh)
    minimum_margin_p_per_kwh: float  # minimum viable margin (default 0.5p/kWh)
    cap_p_per_kwh: Optional[float]   # Ofgem price cap unit rate (p/kWh); None if uncapped

    @property
    def break_even_p_per_kwh(self) -> float:
        """Minimum unit rate to cover all costs plus minimum margin."""
        return round(self.total_cost_p_per_kwh + self.minimum_margin_p_per_kwh, 4)

    @property
    def is_cap_constrained(self) -> bool:
        """True if Ofgem price cap is below the break-even unit rate."""
        if self.cap_p_per_kwh is None:
            return False
        return self.cap_p_per_kwh < self.break_even_p_per_kwh

    @property
    def headroom_p_per_kwh(self) -> Optional[float]:
        """Gap between price cap and break-even (negative = structurally constrained)."""
        if self.cap_p_per_kwh is None:
            return None
        return round(self.cap_p_per_kwh - self.break_even_p_per_kwh, 4)

    @property
    def uncovered_loss_gbp(self) -> float:
        """Annual loss from cap constraint (0 if not constrained)."""
        if not self.is_cap_constrained:
            return 0.0
        shortfall_p = self.break_even_p_per_kwh - (self.cap_p_per_kwh or 0.0)
        return round(shortfall_p * self.consumption_kwh / 100.0, 2)

    @property
    def minimum_viable_tariff_gbp_pa(self) -> float:
        """Annual revenue needed to break even (consumption × break-even rate)."""
        return round(self.break_even_p_per_kwh * self.consumption_kwh / 100.0, 2)


class BreakEvenAssessorBook:
    """Register of break-even tariff assessments.

    Records one assessment per (account_id, year, fuel). Surfaces structurally
    constrained accounts — those where the Ofgem price cap prevents profitable pricing.
    """

    def __init__(self) -> None:
        self._assessments: list[BreakEvenAssessment] = []

    def record(self, assessment: BreakEvenAssessment) -> BreakEvenAssessment:
        self._assessments.append(assessment)
        return assessment

    def latest_for(
        self, account_id: str, fuel: str = "electricity"
    ) -> Optional[BreakEvenAssessment]:
        matches = [a for a in self._assessments
                   if a.account_id == account_id and a.fuel == fuel]
        return max(matches, key=lambda a: a.year) if matches else None

    def cap_constrained(self, year: Optional[int] = None) -> list[BreakEvenAssessment]:
        records = self._for_year(year)
        return [a for a in records if a.is_cap_constrained]

    def total_uncovered_loss_gbp(self, year: Optional[int] = None) -> float:
        records = self._for_year(year)
        return round(sum(a.uncovered_loss_gbp for a in records), 2)

    def cap_constrained_rate_pct(self, year: Optional[int] = None) -> float:
        records = self._for_year(year)
        if not records:
            return 0.0
        constrained = sum(1 for a in records if a.is_cap_constrained)
        return round(constrained / len(records) * 100, 2)

    def assessor_summary(self, year: Optional[int] = None) -> dict:
        records = self._for_year(year)
        if not records:
            return {"accounts_assessed": 0}
        constrained = [a for a in records if a.is_cap_constrained]
        total_loss = self.total_uncovered_loss_gbp(year)
        return {
            "accounts_assessed": len(records),
            "cap_constrained_count": len(constrained),
            "cap_constrained_rate_pct": self.cap_constrained_rate_pct(year),
            "total_uncovered_loss_gbp": total_loss,
        }

    def _for_year(self, year: Optional[int]) -> list[BreakEvenAssessment]:
        if year is None:
            return list(self._assessments)
        return [a for a in self._assessments if a.year == year]
