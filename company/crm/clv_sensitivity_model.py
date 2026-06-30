"""CLV Sensitivity Model (Phase DW).

Customer Lifetime Value (CLV) is the present value of all future cash flows
from a customer. For an energy supplier, CLV depends on:
- Annual margin per customer (revenue - cost to serve - bad debt)
- Churn rate (probability of leaving each year)
- Discount rate (cost of capital)
- Contract renewal probability and terms
- Cross-sell/upsell potential (dual fuel, EV tariff, SEG)

Sensitivity analysis asks: how does CLV change if one parameter moves?
This is essential for:
- Setting acquisition budgets (CAC < CLV/3 is a typical rule of thumb)
- Pricing retention offers (spend up to CLV delta)
- Segmenting customers by strategic value

Typical CLV formula: CLV = M × (R / (1 + D - R))
  where M = annual margin, R = retention rate (1 - churn), D = discount rate

This model runs CLV scenarios across a parameter grid to identify which
factors most change customer value — informing the company's strategy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


_BASE_DISCOUNT_RATE = 0.08          # 8% WACC / cost of capital
_BASE_CHURN_RATE = 0.18             # 18% annual churn (UK energy 2022-23)
_CAC_TO_CLV_FLOOR = 3.0            # CAC should not exceed CLV/3


@dataclass(frozen=True)
class CLVScenario:
    label: str
    annual_margin_gbp: float
    churn_rate: float
    discount_rate: float
    tenure_years: int = 5           # how many years to model

    @property
    def retention_rate(self) -> float:
        return 1.0 - self.churn_rate

    @property
    def clv_infinite_gbp(self) -> float:
        """Gordon Growth Model: CLV = M × R / (1 + D - R)."""
        denom = 1 + self.discount_rate - self.retention_rate
        if denom <= 0:
            return float("inf")
        return self.annual_margin_gbp * self.retention_rate / denom

    @property
    def clv_finite_gbp(self) -> float:
        """CLV over finite tenure: PV of each year's expected margin."""
        pv = 0.0
        survival = 1.0
        for t in range(1, self.tenure_years + 1):
            survival *= self.retention_rate
            pv += self.annual_margin_gbp * survival / (1 + self.discount_rate) ** t
        return pv

    @property
    def max_acquisition_cost_gbp(self) -> float:
        return self.clv_infinite_gbp / _CAC_TO_CLV_FLOOR

    @property
    def max_retention_spend_gbp(self) -> float:
        """How much to spend to retain: difference in CLV if churn avoided."""
        retained_clv = CLVScenario(
            label=self.label + "_retained",
            annual_margin_gbp=self.annual_margin_gbp,
            churn_rate=0.0,
            discount_rate=self.discount_rate,
        ).clv_finite_gbp
        return max(0.0, retained_clv - self.clv_finite_gbp)


class CLVSensitivityModel:
    """Runs CLV scenarios and identifies key value drivers."""

    def __init__(self) -> None:
        self._scenarios: Dict[str, CLVScenario] = {}

    def add_scenario(self, scenario: CLVScenario) -> CLVScenario:
        self._scenarios[scenario.label] = scenario
        return scenario

    def base_case(
        self,
        annual_margin_gbp: float = 200.0,
        label: str = "base",
    ) -> CLVScenario:
        return self.add_scenario(CLVScenario(
            label=label,
            annual_margin_gbp=annual_margin_gbp,
            churn_rate=_BASE_CHURN_RATE,
            discount_rate=_BASE_DISCOUNT_RATE,
        ))

    def run_churn_sensitivity(
        self,
        base: CLVScenario,
        churn_rates: List[float],
    ) -> List[CLVScenario]:
        scenarios = []
        for rate in churn_rates:
            s = CLVScenario(
                label=f"{base.label}_churn_{rate:.0%}",
                annual_margin_gbp=base.annual_margin_gbp,
                churn_rate=rate,
                discount_rate=base.discount_rate,
            )
            self.add_scenario(s)
            scenarios.append(s)
        return scenarios

    def run_margin_sensitivity(
        self,
        base: CLVScenario,
        margin_deltas: List[float],
    ) -> List[CLVScenario]:
        scenarios = []
        for delta in margin_deltas:
            s = CLVScenario(
                label=f"{base.label}_margin_{delta:+.0f}",
                annual_margin_gbp=base.annual_margin_gbp + delta,
                churn_rate=base.churn_rate,
                discount_rate=base.discount_rate,
            )
            self.add_scenario(s)
            scenarios.append(s)
        return scenarios

    def highest_clv(self) -> Optional[CLVScenario]:
        if not self._scenarios:
            return None
        return max(self._scenarios.values(), key=lambda s: s.clv_infinite_gbp)

    def lowest_clv(self) -> Optional[CLVScenario]:
        if not self._scenarios:
            return None
        return min(self._scenarios.values(), key=lambda s: s.clv_infinite_gbp)

    def scenarios_above_cac_floor(
        self, cac_gbp: float
    ) -> List[CLVScenario]:
        return [s for s in self._scenarios.values()
                if s.max_acquisition_cost_gbp >= cac_gbp]

    def clv_range_gbp(self) -> tuple:
        if not self._scenarios:
            return (0.0, 0.0)
        clvs = [s.clv_infinite_gbp for s in self._scenarios.values()
                if s.clv_infinite_gbp != float("inf")]
        return (min(clvs), max(clvs))

    def sensitivity_summary(self) -> str:
        n = len(self._scenarios)
        if n == 0:
            return "CLV Sensitivity Model: no scenarios loaded."
        lo, hi = self.clv_range_gbp()
        base = _BASE_CHURN_RATE
        return (
            f"CLV Sensitivity Model: {n} scenarios. "
            f"CLV range: £{lo:,.0f}–£{hi:,.0f}. "
            f"Base churn: {base:.0%}; discount: {_BASE_DISCOUNT_RATE:.0%}. "
            f"CAC floor: CLV/{_CAC_TO_CLV_FLOOR:.0f}."
        )
