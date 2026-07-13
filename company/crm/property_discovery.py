"""Discovery mechanism for the company-side property belief layer (C2_discovery_through_interfaces).

The company can never read a customer's ground-truth property record --
that lives sim-side, in saas/property_model.py, on the far side of the
epistemic wall. Everything the company believes about a customer's home is
built up incrementally through OBSERVABLE events, each of which stamps the
touched attribute(s) with a source/confidence/as-of-date on the resulting
Property record (see property_model.Property.provenance):

  * self-disclosure at signup      -- what the customer tells us on the
                                       onboarding form (moderate confidence,
                                       unverified)
  * an EPC-certificate-register    -- the only observable way we learn a
    lookup                            real EPC rating
  * a tariff registration          -- the customer opts into an EV or
                                       solar-export tariff (a real
                                       commercial action we observe)
  * a meter-engineer site visit    -- a physical survey correcting floor
                                       area/occupancy

Undisclosed/unconfirmed attributes are filled from population-average
defaults with near-zero confidence and an explicit 'unconfirmed_default'
source -- NOT a read of the sim's ground truth. A belief built this way MAY
diverge from the customer's actual home; that imperfection is the point.

Epistemic-compliant: nothing in this module imports from sim/ or
simulation/, or from saas/property_model.py (the sim-side ground truth).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import replace
from typing import Optional

from company.crm.property_model import (
    EPCRating, Property, PropertyType, TenureType, UNCONFIRMED_DEFAULT_SOURCE,
)

# Confidence bands per discovery-event class (0.0-1.0). Deliberately not 1.0
# even for the most reliable sources -- self-disclosure can be wrong, EPC
# registers can be stale, an engineer visit is the closest to ground truth
# this company ever gets but is still an observation, not an oracle read.
SELF_DISCLOSURE_CONFIDENCE = 0.6
EPC_LOOKUP_CONFIDENCE = 0.95
TARIFF_REGISTRATION_CONFIDENCE = 0.9
ENGINEER_VISIT_CONFIDENCE = 0.98
DEFAULT_ASSUMPTION_CONFIDENCE = 0.1

SOURCE_SELF_DISCLOSED_SIGNUP = 'self_disclosed_signup'
SOURCE_EPC_CERTIFICATE_LOOKUP = 'epc_certificate_lookup'
SOURCE_TARIFF_REGISTRATION = 'tariff_registration'
SOURCE_ENGINEER_VISIT = 'engineer_visit'

# Population-average priors used to fill any attribute never disclosed or
# discovered -- these are UK-average assumptions, not a read of any specific
# customer's ground truth (same status as UK_AVG_DOMESTIC_ELEC_KWH already
# used elsewhere in property_model.py).
DEFAULT_PROPERTY_TYPE = PropertyType.SEMI_DETACHED
DEFAULT_TENURE = TenureType.OWNER_OCCUPIED
DEFAULT_EPC_RATING = EPCRating.D  # UK modal EPC band (Ofgem/EPC register distribution)
DEFAULT_FLOOR_AREA_M2 = 85.0
DEFAULT_BEDROOMS = 3
DEFAULT_OCCUPANTS = 2

_SIGNUP_DISCLOSABLE_FIELDS = ('property_type', 'tenure', 'bedrooms', 'occupants')
_NEVER_KNOWN_AT_SIGNUP_FIELDS = ('epc_rating', 'floor_area_m2', 'has_solar_pv', 'electric_vehicle')


def _stamped(source: str, confidence: float, as_of: dt.date) -> dict:
    return {'source': source, 'confidence': confidence, 'as_of': as_of}


def open_belief_from_signup(
    uprn: str,
    as_of: dt.date,
    *,
    property_type: Optional[PropertyType] = None,
    tenure: Optional[TenureType] = None,
    bedrooms: Optional[int] = None,
    occupants: Optional[int] = None,
    has_gas: bool = True,
) -> Property:
    """Open the company's FIRST belief about a home from the onboarding
    disclosure event. Any of property_type/tenure/bedrooms/occupants the
    customer did not state is filled from a population-average default at
    near-zero confidence, explicitly marked 'unconfirmed_default'.

    EPC rating, floor area, solar PV and EV are NEVER known at signup in
    reality (no customer states their own EPC band unprompted, and a
    company cannot see it without a register lookup) -- they always start
    as unconfirmed-default here, regardless of what is passed in.
    """
    resolved = {
        'property_type': property_type if property_type is not None else DEFAULT_PROPERTY_TYPE,
        'tenure': tenure if tenure is not None else DEFAULT_TENURE,
        'bedrooms': bedrooms if bedrooms is not None else DEFAULT_BEDROOMS,
        'occupants': occupants if occupants is not None else DEFAULT_OCCUPANTS,
    }
    disclosed = {
        'property_type': property_type is not None,
        'tenure': tenure is not None,
        'bedrooms': bedrooms is not None,
        'occupants': occupants is not None,
    }

    provenance: dict = {}
    for name in _SIGNUP_DISCLOSABLE_FIELDS:
        if disclosed[name]:
            provenance[name] = _stamped(SOURCE_SELF_DISCLOSED_SIGNUP, SELF_DISCLOSURE_CONFIDENCE, as_of)
        else:
            provenance[name] = _stamped(UNCONFIRMED_DEFAULT_SOURCE, DEFAULT_ASSUMPTION_CONFIDENCE, as_of)
    for name in _NEVER_KNOWN_AT_SIGNUP_FIELDS:
        provenance[name] = _stamped(UNCONFIRMED_DEFAULT_SOURCE, DEFAULT_ASSUMPTION_CONFIDENCE, as_of)

    return Property(
        uprn=uprn,
        property_type=resolved['property_type'],
        tenure=resolved['tenure'],
        epc_rating=DEFAULT_EPC_RATING,
        floor_area_m2=DEFAULT_FLOOR_AREA_M2,
        bedrooms=resolved['bedrooms'],
        occupants=resolved['occupants'],
        has_gas=has_gas,
        provenance=provenance,
    )


def apply_epc_lookup(prop: Property, epc_rating: EPCRating, as_of: dt.date) -> Property:
    """Record an EPC-certificate-register lookup -- the only observable way
    the company ever learns a real EPC rating."""
    updated = replace(prop, epc_rating=epc_rating)
    prov = dict(updated.provenance)
    prov['epc_rating'] = _stamped(SOURCE_EPC_CERTIFICATE_LOOKUP, EPC_LOOKUP_CONFIDENCE, as_of)
    return replace(updated, provenance=prov)


def apply_tariff_registration(
    prop: Property,
    as_of: dt.date,
    *,
    has_solar_pv: Optional[bool] = None,
    electric_vehicle: Optional[bool] = None,
) -> Property:
    """The customer registers for an EV or solar-export tariff -- an
    observable commercial action, not a meter/ground-truth read."""
    updates = {}
    if has_solar_pv is not None:
        updates['has_solar_pv'] = has_solar_pv
    if electric_vehicle is not None:
        updates['electric_vehicle'] = electric_vehicle
    if not updates:
        return prop
    updated = replace(prop, **updates)
    prov = dict(updated.provenance)
    for name in updates:
        prov[name] = _stamped(SOURCE_TARIFF_REGISTRATION, TARIFF_REGISTRATION_CONFIDENCE, as_of)
    return replace(updated, provenance=prov)


def apply_engineer_visit(
    prop: Property,
    as_of: dt.date,
    *,
    floor_area_m2: Optional[float] = None,
    bedrooms: Optional[int] = None,
    occupants: Optional[int] = None,
) -> Property:
    """A meter-engineer site visit corrects floor area / bedrooms /
    occupants -- the closest the company ever gets to ground truth, but
    still an observation with its own confidence, not an oracle read."""
    updates = {}
    if floor_area_m2 is not None:
        updates['floor_area_m2'] = floor_area_m2
    if bedrooms is not None:
        updates['bedrooms'] = bedrooms
    if occupants is not None:
        updates['occupants'] = occupants
    if not updates:
        return prop
    updated = replace(prop, **updates)
    prov = dict(updated.provenance)
    for name in updates:
        prov[name] = _stamped(SOURCE_ENGINEER_VISIT, ENGINEER_VISIT_CONFIDENCE, as_of)
    return replace(updated, provenance=prov)
