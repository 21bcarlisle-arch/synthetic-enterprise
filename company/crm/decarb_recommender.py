from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Measure(str, Enum):
    CAVITY_WALL_INSULATION = 'cavity_wall_insulation'
    SOLID_WALL_INSULATION = 'solid_wall_insulation'
    LOFT_INSULATION = 'loft_insulation'
    HEAT_PUMP = 'heat_pump'
    SOLAR_PV = 'solar_pv'
    SMART_CONTROLS = 'smart_controls'
    DOUBLE_GLAZING = 'double_glazing'
    LED_LIGHTING = 'led_lighting'
    BATTERY_STORAGE = 'battery_storage'


class FundingScheme(str, Enum):
    ECO4 = 'eco4'
    BUS = 'bus'          # Boiler Upgrade Scheme
    SEG = 'seg'          # Smart Export Guarantee
    GHG = 'ghg'          # Great British Insulation Scheme
    SELF_FUNDED = 'self_funded'


_MEASURE_TYPICAL_ANNUAL_SAVINGS_GBP = {
    Measure.CAVITY_WALL_INSULATION: 155,
    Measure.SOLID_WALL_INSULATION: 490,
    Measure.LOFT_INSULATION: 150,
    Measure.HEAT_PUMP: 415,
    Measure.SOLAR_PV: 370,
    Measure.SMART_CONTROLS: 130,
    Measure.DOUBLE_GLAZING: 125,
    Measure.LED_LIGHTING: 75,
    Measure.BATTERY_STORAGE: 200,
}

_MEASURE_TYPICAL_COST_GBP = {
    Measure.CAVITY_WALL_INSULATION: 1_700,
    Measure.SOLID_WALL_INSULATION: 8_000,
    Measure.LOFT_INSULATION: 400,
    Measure.HEAT_PUMP: 12_000,
    Measure.SOLAR_PV: 5_500,
    Measure.SMART_CONTROLS: 250,
    Measure.DOUBLE_GLAZING: 5_000,
    Measure.LED_LIGHTING: 100,
    Measure.BATTERY_STORAGE: 4_500,
}


@dataclass(frozen=True)
class MeasureRecommendation:
    measure: Measure
    estimated_annual_savings_gbp: float
    estimated_cost_gbp: float
    funding_schemes: tuple
    priority: int

    @property
    def simple_payback_years(self) -> float:
        if self.estimated_annual_savings_gbp <= 0:
            return float('inf')
        return round(self.estimated_cost_gbp / self.estimated_annual_savings_gbp, 1)


@dataclass(frozen=True)
class DecarbonisationPlan:
    customer_id: str
    recommendations: tuple
    # How confident the company is in the BELIEF this plan was built on
    # (0..1), when the plan was derived from the discovered property belief
    # layer (company/crm/home_registry.py) rather than from caller-supplied
    # attributes. None when the plan was built from explicit attributes with
    # no attached belief-confidence. A low value here means the company is
    # recommending measures on a poorly-known home -- e.g. an EPC band that is
    # still an unconfirmed population-average default, not a real register
    # lookup -- and the recommendation should be treated as provisional.
    belief_confidence: Optional[float] = None

    @property
    def total_potential_savings_gbp(self) -> float:
        return sum(r.estimated_annual_savings_gbp for r in self.recommendations)

    @property
    def top_measure(self) -> Optional[MeasureRecommendation]:
        return self.recommendations[0] if self.recommendations else None

    @property
    def is_provisional_on_weak_belief(self) -> bool:
        """True when the plan rests on a belief the company barely knows.

        The company acts on what it has observed, at the confidence it has:
        below this threshold the recommendation is driven mostly by
        unconfirmed population-average defaults (see property_discovery.py),
        so it should be surfaced as 'we think, pending confirmation' rather
        than presented as settled."""
        return self.belief_confidence is not None and self.belief_confidence < 0.5

    def summary(self) -> dict:
        return {
            'customer_id': self.customer_id,
            'recommendation_count': len(self.recommendations),
            'total_potential_savings_gbp': round(self.total_potential_savings_gbp, 2),
            'top_measure': self.top_measure.measure.value if self.top_measure else None,
            'belief_confidence': self.belief_confidence,
            'provisional_on_weak_belief': self.is_provisional_on_weak_belief,
        }


def recommend_measures(
    customer_id: str,
    epc_rating: str,
    property_type: str,
    heating_system: str,
    has_solar: bool = False,
    is_fuel_poor: bool = False,
    eco4_eligible: bool = False,
    belief_confidence: Optional[float] = None,
) -> DecarbonisationPlan:
    recs: List[MeasureRecommendation] = []
    priority = 1

    if epc_rating in ('E', 'F', 'G'):
        if property_type in ('terraced', 'semi_detached', 'detached'):
            funding = ('eco4', 'ghg') if eco4_eligible else ('ghg', 'self_funded')
            recs.append(MeasureRecommendation(
                Measure.CAVITY_WALL_INSULATION,
                _MEASURE_TYPICAL_ANNUAL_SAVINGS_GBP[Measure.CAVITY_WALL_INSULATION],
                0 if eco4_eligible else _MEASURE_TYPICAL_COST_GBP[Measure.CAVITY_WALL_INSULATION],
                tuple(FundingScheme(s) for s in funding),
                priority,
            ))
            priority += 1
        else:
            funding = ('eco4',) if eco4_eligible else ('self_funded',)
            recs.append(MeasureRecommendation(
                Measure.SOLID_WALL_INSULATION,
                _MEASURE_TYPICAL_ANNUAL_SAVINGS_GBP[Measure.SOLID_WALL_INSULATION],
                0 if eco4_eligible else _MEASURE_TYPICAL_COST_GBP[Measure.SOLID_WALL_INSULATION],
                tuple(FundingScheme(s) for s in funding),
                priority,
            ))
            priority += 1

    if epc_rating in ('D', 'E', 'F', 'G'):
        recs.append(MeasureRecommendation(
            Measure.LOFT_INSULATION,
            _MEASURE_TYPICAL_ANNUAL_SAVINGS_GBP[Measure.LOFT_INSULATION],
            0 if eco4_eligible else _MEASURE_TYPICAL_COST_GBP[Measure.LOFT_INSULATION],
            (FundingScheme.ECO4,) if eco4_eligible else (FundingScheme.SELF_FUNDED,),
            priority,
        ))
        priority += 1

    if heating_system in ('gas_boiler', 'oil_boiler', 'storage_heater') and epc_rating in ('A', 'B', 'C', 'D'):
        recs.append(MeasureRecommendation(
            Measure.HEAT_PUMP,
            _MEASURE_TYPICAL_ANNUAL_SAVINGS_GBP[Measure.HEAT_PUMP],
            _MEASURE_TYPICAL_COST_GBP[Measure.HEAT_PUMP] - 7500,
            (FundingScheme.BUS,),
            priority,
        ))
        priority += 1

    if not has_solar:
        schemes = [FundingScheme.SEG]
        if not schemes:
            schemes = [FundingScheme.SELF_FUNDED]
        recs.append(MeasureRecommendation(
            Measure.SOLAR_PV,
            _MEASURE_TYPICAL_ANNUAL_SAVINGS_GBP[Measure.SOLAR_PV],
            _MEASURE_TYPICAL_COST_GBP[Measure.SOLAR_PV],
            (FundingScheme.SEG,),
            priority,
        ))
        priority += 1

    recs.append(MeasureRecommendation(
        Measure.SMART_CONTROLS,
        _MEASURE_TYPICAL_ANNUAL_SAVINGS_GBP[Measure.SMART_CONTROLS],
        _MEASURE_TYPICAL_COST_GBP[Measure.SMART_CONTROLS],
        (FundingScheme.SELF_FUNDED,),
        priority,
    ))

    return DecarbonisationPlan(
        customer_id=customer_id,
        recommendations=tuple(recs),
        belief_confidence=belief_confidence,
    )


# Coarse heating-system inference from the one fuel fact the belief layer
# tracks (has_gas). The belief layer does NOT carry a heating-system
# attribute, so this is an explicit assumption, not a discovered fact -- a
# gas-supplied home is assumed to run a gas boiler, an all-electric home a
# storage heater. A caller who has a better-observed heating system (e.g.
# from an engineer visit) should pass it explicitly.
def _assume_heating_system(has_gas: bool) -> str:
    return 'gas_boiler' if has_gas else 'storage_heater'


def recommend_from_registry(
    home_registry,
    account_id: str,
    heating_system: Optional[str] = None,
) -> DecarbonisationPlan:
    """Build a decarbonisation plan from the company's DISCOVERED belief
    about a customer's home, at the confidence the company actually holds --
    NOT from a direct read of sim-side ground truth.

    This is the epistemic wall in action: the recommender never touches
    saas/property_model.py. It reads only company/crm/home_registry.py's
    belief (get_profile / belief_confidence), which was itself built purely
    from observable discovery events (signup disclosure, EPC-register
    lookup, tariff registration, engineer visit -- see property_discovery.py).
    A belief may legitimately differ from the customer's real home; the plan
    carries the belief's overall confidence so a weakly-known home yields a
    plan flagged provisional (DecarbonisationPlan.is_provisional_on_weak_belief),
    exactly as a real supplier would treat a recommendation made off an
    assumed rather than a verified EPC band.
    """
    prop = home_registry.get_profile(account_id)
    belief = home_registry.belief_confidence(account_id)
    heating = heating_system if heating_system is not None else _assume_heating_system(prop.has_gas)
    return recommend_measures(
        customer_id=account_id,
        epc_rating=prop.epc_rating.value,
        property_type=prop.property_type.value,
        heating_system=heating,
        has_solar=prop.has_solar_pv,
        is_fuel_poor=prop.is_fuel_poor,
        eco4_eligible=prop.eco4_eligible,
        belief_confidence=belief['overall_confidence'],
    )
