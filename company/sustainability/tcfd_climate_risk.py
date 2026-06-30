"""TCFD Climate Risk Financial Assessment (Phase DX).

The Task Force on Climate-related Financial Disclosures (TCFD) framework,
adopted by UK FCA and Ofgem, requires energy companies to assess two risk types:

PHYSICAL RISKS:
- Acute: extreme weather (storms, floods) damaging infrastructure
  → higher bad debt from billing disputes / outages
  → increased customer support costs
- Chronic: rising mean temperatures → reduced gas demand (heating)
  → reduced seasonal peak demand that tariffs are priced around

TRANSITION RISKS:
- Policy: carbon pricing, efficiency standards, green levies increasing
  → cost pressure on Scope 3 gas procurement
- Market: EV adoption reduces standard domestic electricity demand
  → increases cross-subsidy exposure on flat tariffs
- Technology: smart meter rollout accelerates switching
  → higher churn rate, lower portfolio stability

This assessment quantifies the GBP impact under 1.5°C, 2°C, and 4°C scenarios
for a 2025-2030 horizon, consistent with IPCC AR6 and NPC / UKCP18.

Epistemic: observations only — company cannot see forward curve construction,
only current prices and its own cost structure.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ClimatScenario(str, Enum):
    ORDERLY_1_5C = "orderly_1.5c"          # Paris-aligned, fast transition
    DISORDERLY_2C = "disorderly_2c"        # delayed action, abrupt transition
    HOT_HOUSE_4C = "hot_house_4c"          # minimal action, physical risks dominant


class RiskHorizon(str, Enum):
    SHORT = "short"     # 0-2 years
    MEDIUM = "medium"   # 2-5 years
    LONG = "long"       # 5+ years


class RiskType(str, Enum):
    PHYSICAL_ACUTE = "physical_acute"
    PHYSICAL_CHRONIC = "physical_chronic"
    TRANSITION_POLICY = "transition_policy"
    TRANSITION_MARKET = "transition_market"
    TRANSITION_TECHNOLOGY = "transition_technology"


_SCENARIO_TEMP_RISE = {
    ClimatScenario.ORDERLY_1_5C: 1.5,
    ClimatScenario.DISORDERLY_2C: 2.0,
    ClimatScenario.HOT_HOUSE_4C: 4.0,
}

_CARBON_PRICE_2030_GBP_PER_TCO2 = {
    ClimatScenario.ORDERLY_1_5C: 150.0,
    ClimatScenario.DISORDERLY_2C: 80.0,
    ClimatScenario.HOT_HOUSE_4C: 30.0,
}

_EXPECTED_GAS_DEMAND_REDUCTION_PCT = {
    ClimatScenario.ORDERLY_1_5C: 35.0,
    ClimatScenario.DISORDERLY_2C: 15.0,
    ClimatScenario.HOT_HOUSE_4C: 8.0,
}

_CHURN_UPLIFT_PCT = {
    ClimatScenario.ORDERLY_1_5C: 3.0,
    ClimatScenario.DISORDERLY_2C: 5.0,
    ClimatScenario.HOT_HOUSE_4C: 1.0,
}


@dataclass(frozen=True)
class ClimateRiskExposure:
    risk_type: RiskType
    scenario: ClimatScenario
    horizon: RiskHorizon
    description: str
    gross_exposure_gbp: float
    mitigation_gbp: float
    probability_pct: float

    @property
    def net_exposure_gbp(self) -> float:
        return self.gross_exposure_gbp - self.mitigation_gbp

    @property
    def risk_adjusted_exposure_gbp(self) -> float:
        return self.net_exposure_gbp * self.probability_pct / 100

    @property
    def is_material(self) -> bool:
        return self.risk_adjusted_exposure_gbp > 10_000.0


class TCFDClimateRiskAssessment:
    """TCFD-aligned climate risk financial assessment for a UK energy supplier."""

    def __init__(
        self,
        assessment_year: int,
        annual_gas_revenue_gbp: float,
        annual_gas_procurement_tco2: float,
        customer_count: int,
        average_annual_margin_gbp: float = 200.0,
    ) -> None:
        self.assessment_year = assessment_year
        self.annual_gas_revenue_gbp = annual_gas_revenue_gbp
        self.annual_gas_procurement_tco2 = annual_gas_procurement_tco2
        self.customer_count = customer_count
        self.average_annual_margin_gbp = average_annual_margin_gbp
        self._exposures: List[ClimateRiskExposure] = []

    def _add(self, exposure: ClimateRiskExposure) -> None:
        self._exposures.append(exposure)

    def run_scenario(self, scenario: ClimatScenario) -> List[ClimateRiskExposure]:
        """Quantify all risk types under given scenario. Returns list of exposures."""
        exposures = []

        # 1. Physical acute: extreme weather → billing disputes / bad debt
        acute_gross = self.customer_count * 25.0 * _SCENARIO_TEMP_RISE[scenario] / 1.5
        acute = ClimateRiskExposure(
            risk_type=RiskType.PHYSICAL_ACUTE,
            scenario=scenario,
            horizon=RiskHorizon.SHORT,
            description="Extreme weather events → increased bad debt and dispute handling costs",
            gross_exposure_gbp=acute_gross,
            mitigation_gbp=acute_gross * 0.2,
            probability_pct=40.0,
        )
        self._add(acute)
        exposures.append(acute)

        # 2. Physical chronic: lower heating demand → gas revenue reduction
        demand_reduction_pct = _EXPECTED_GAS_DEMAND_REDUCTION_PCT[scenario]
        chronic_gross = self.annual_gas_revenue_gbp * demand_reduction_pct / 100
        chronic = ClimateRiskExposure(
            risk_type=RiskType.PHYSICAL_CHRONIC,
            scenario=scenario,
            horizon=RiskHorizon.LONG,
            description=f"Rising temperatures → {demand_reduction_pct:.0f}% gas demand reduction by 2030",
            gross_exposure_gbp=chronic_gross,
            mitigation_gbp=chronic_gross * 0.1,
            probability_pct=70.0,
        )
        self._add(chronic)
        exposures.append(chronic)

        # 3. Transition policy: carbon price applied to Scope 3 gas procurement
        carbon_price = _CARBON_PRICE_2030_GBP_PER_TCO2[scenario]
        policy_gross = self.annual_gas_procurement_tco2 * carbon_price
        policy = ClimateRiskExposure(
            risk_type=RiskType.TRANSITION_POLICY,
            scenario=scenario,
            horizon=RiskHorizon.MEDIUM,
            description=f"Carbon price at £{carbon_price:.0f}/tCO₂ on gas procurement Scope 3",
            gross_exposure_gbp=policy_gross,
            mitigation_gbp=policy_gross * 0.15,
            probability_pct=60.0,
        )
        self._add(policy)
        exposures.append(policy)

        # 4. Transition market: EV uptake shifts load shape, increases cross-subsidy
        ev_cross_subsidy = self.customer_count * 50.0 * _SCENARIO_TEMP_RISE[scenario] / 2.0
        market = ClimateRiskExposure(
            risk_type=RiskType.TRANSITION_MARKET,
            scenario=scenario,
            horizon=RiskHorizon.MEDIUM,
            description="EV adoption increases flat-tariff cross-subsidy exposure",
            gross_exposure_gbp=ev_cross_subsidy,
            mitigation_gbp=ev_cross_subsidy * 0.3,
            probability_pct=55.0,
        )
        self._add(market)
        exposures.append(market)

        # 5. Transition technology: smart meter churn uplift
        churn_uplift = _CHURN_UPLIFT_PCT[scenario]
        lost_margin = (self.customer_count * churn_uplift / 100) * self.average_annual_margin_gbp
        tech = ClimateRiskExposure(
            risk_type=RiskType.TRANSITION_TECHNOLOGY,
            scenario=scenario,
            horizon=RiskHorizon.SHORT,
            description=f"Smart meter + switching platform → +{churn_uplift:.0f}% churn",
            gross_exposure_gbp=lost_margin,
            mitigation_gbp=lost_margin * 0.25,
            probability_pct=50.0,
        )
        self._add(tech)
        exposures.append(tech)

        return exposures

    def exposures(
        self,
        scenario: Optional[ClimatScenario] = None,
        risk_type: Optional[RiskType] = None,
    ) -> List[ClimateRiskExposure]:
        result = self._exposures
        if scenario:
            result = [e for e in result if e.scenario == scenario]
        if risk_type:
            result = [e for e in result if e.risk_type == risk_type]
        return result

    def material_exposures(self) -> List[ClimateRiskExposure]:
        return [e for e in self._exposures if e.is_material]

    def total_risk_adjusted_exposure_gbp(
        self, scenario: Optional[ClimatScenario] = None
    ) -> float:
        return sum(e.risk_adjusted_exposure_gbp for e in self.exposures(scenario))

    def worst_scenario(self) -> Optional[ClimatScenario]:
        if not self._exposures:
            return None
        return max(
            set(e.scenario for e in self._exposures),
            key=lambda s: self.total_risk_adjusted_exposure_gbp(s),
        )

    def tcfd_summary(self) -> str:
        n = len(self._exposures)
        n_material = len(self.material_exposures())
        total = self.total_risk_adjusted_exposure_gbp()
        worst = self.worst_scenario()
        worst_str = worst.value if worst else "n/a"
        return (
            f"TCFD Climate Risk ({self.assessment_year}): "
            f"{n} exposures across {len(set(e.scenario for e in self._exposures))} scenarios. "
            f"Material: {n_material}. Total risk-adjusted: £{total:,.0f}. "
            f"Worst scenario: {worst_str}."
        )
