from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PropertyType(str, Enum):
    DETACHED = 'detached'
    SEMI_DETACHED = 'semi_detached'
    TERRACED = 'terraced'
    FLAT = 'flat'
    BUNGALOW = 'bungalow'
    MOBILE_HOME = 'mobile_home'
    COMMERCIAL = 'commercial'


class TenureType(str, Enum):
    OWNER_OCCUPIED = 'owner_occupied'
    PRIVATE_RENTED = 'private_rented'
    SOCIAL_RENTED = 'social_rented'
    SHARED_OWNERSHIP = 'shared_ownership'


class EPCRating(str, Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'
    G = 'G'


_EPC_CONSUMPTION_MULTIPLIER: dict[str, float] = {
    'A': 0.60, 'B': 0.75, 'C': 0.90, 'D': 1.00,
    'E': 1.20, 'F': 1.45, 'G': 1.75,
}

_FLOOR_AREA_BASELINE_M2: dict[str, float] = {
    'detached': 130.0, 'semi_detached': 90.0, 'terraced': 75.0,
    'flat': 55.0, 'bungalow': 80.0, 'mobile_home': 45.0, 'commercial': 200.0,
}

UK_AVG_DOMESTIC_ELEC_KWH = 3100.0
UK_AVG_DOMESTIC_GAS_KWH = 12000.0

# Source string used when an attribute has never been discovered via any
# observable event -- it is a population-average assumption, not a ground-truth
# read (see company/crm/property_discovery.py). Belongs here, not in
# property_discovery.py, so Property's own default-provenance behaviour is
# self-contained and doesn't require the discovery module to be imported.
UNCONFIRMED_DEFAULT_SOURCE = 'unconfirmed_default'

# The physical attributes this belief layer tracks discovery confidence for.
# (has_gas is treated as known-at-signup-by-construction -- a customer always
# tells us what fuel(s) they want supplied -- so it is not part of this list.)
TRACKED_BELIEF_FIELDS = (
    'property_type', 'tenure', 'epc_rating', 'floor_area_m2',
    'bedrooms', 'occupants', 'has_solar_pv', 'electric_vehicle',
)


@dataclass(frozen=True)
class Property:
    """The company's BELIEF about a customer's home -- not a read of the
    sim-side ground-truth Property (saas/property_model.py). Every physical
    attribute below is a value the company currently BELIEVES to be true;
    `provenance` records, per attribute, how confident we are and how we
    came to believe it (self-disclosure, an EPC-certificate lookup, a tariff
    registration, an engineer visit, or -- absent any of those -- an
    unconfirmed population-average default). A belief may differ from
    reality; that imperfection is the point (real_world_twin: a real
    supplier only learns a property's true attributes via meter install/
    survey/customer disclosure). Never populate this from
    saas/property_model.py -- use company/crm/property_discovery.py's
    discovery functions instead.
    """
    uprn: str
    property_type: PropertyType
    tenure: TenureType
    epc_rating: EPCRating
    floor_area_m2: float
    bedrooms: int
    occupants: int
    has_gas: bool = True
    has_solar_pv: bool = False
    electric_vehicle: bool = False
    # attribute name -> {'source': str, 'confidence': float (0..1), 'as_of': date}
    # Excluded from equality/hash: two beliefs about the same physical facts
    # should compare equal regardless of how/when we came to hold them.
    provenance: dict = field(default_factory=dict, compare=False)

    def confidence_for(self, attribute: str) -> float:
        """0.0 (never discovered -- default assumption) to 1.0 (certain)."""
        return self.provenance.get(attribute, {}).get('confidence', 0.0)

    def source_for(self, attribute: str) -> str:
        return self.provenance.get(attribute, {}).get('source', UNCONFIRMED_DEFAULT_SOURCE)

    def as_of_for(self, attribute: str):
        return self.provenance.get(attribute, {}).get('as_of')

    def is_discovered(self, attribute: str) -> bool:
        """True once at least one observable discovery event has touched
        this attribute (as opposed to it still holding its unconfirmed
        default)."""
        return self.source_for(attribute) != UNCONFIRMED_DEFAULT_SOURCE

    @property
    def overall_confidence(self) -> float:
        """Mean discovery confidence across every tracked attribute -- a
        single 0..1 gauge of how well the company actually knows this home,
        as opposed to how much of it is still assumed."""
        values = [self.confidence_for(f) for f in TRACKED_BELIEF_FIELDS]
        return round(sum(values) / len(values), 3) if values else 0.0

    @property
    def consumption_multiplier(self) -> float:
        return _EPC_CONSUMPTION_MULTIPLIER[self.epc_rating.value]

    @property
    def estimated_annual_elec_kwh(self) -> float:
        area_factor = self.floor_area_m2 / _FLOOR_AREA_BASELINE_M2.get(
            self.property_type.value, 80.0
        )
        occupant_factor = max(1.0, self.occupants / 2.5)
        ev_uplift = 2500.0 if self.electric_vehicle else 0.0
        solar_offset = 2000.0 if self.has_solar_pv else 0.0
        base = UK_AVG_DOMESTIC_ELEC_KWH * area_factor * occupant_factor
        base *= self.consumption_multiplier
        return round(max(0.0, base + ev_uplift - solar_offset), 0)

    @property
    def estimated_annual_gas_kwh(self) -> float:
        if not self.has_gas:
            return 0.0
        area_factor = self.floor_area_m2 / _FLOOR_AREA_BASELINE_M2.get(
            self.property_type.value, 80.0
        )
        base = UK_AVG_DOMESTIC_GAS_KWH * area_factor
        base *= self.consumption_multiplier
        return round(max(0.0, base), 0)

    @property
    def is_fuel_poor(self) -> bool:
        return (
            self.epc_rating in (EPCRating.F, EPCRating.G)
            and self.tenure in (TenureType.PRIVATE_RENTED, TenureType.SOCIAL_RENTED)
        )

    @property
    def eco4_eligible(self) -> bool:
        return self.epc_rating.value in ('D', 'E', 'F', 'G')

    @property
    def psr_priority_property(self) -> bool:
        return self.epc_rating in (EPCRating.F, EPCRating.G)
