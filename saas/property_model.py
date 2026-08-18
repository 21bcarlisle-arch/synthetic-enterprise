"""The SUPPLIER's derivations about a customer's dwelling — Phase 4c-1.

**SPLIT 2026-08-18 (KNIFE3 step 35, B12).** This module used to hold BOTH the
world's dwelling ground truth and the supplier's approximation of it, and
`simulation/run_phase2b.py` imported `build_properties` across the epistemic wall
to get the former. That was the one live `owed` crossing under
`B12_the_dwelling_is_the_worlds_and_the_company_only_discovers_it`. The world's half
now lives at `simulation/dwelling_records.py`, which owns `build_properties`, the
physical asset mix, occupancy/headcount, heating system and the dwelling-basis
vocabulary. That module's docstring records the split and its two residual rulings.

WHAT STAYED, and it is the whole of what this module is now for: the SUPPLIER'S OWN
READING of a dwelling it has not observed. A drawn (`SYN-*`) customer carries the
observable `consumption_band` and nothing else, so the supplier infers
`property_type`/`epc_rating`/`bedrooms` from it. That inference is ALLOWED TO BE
WRONG — the gap between it and the world's drawn dwelling is exactly what the coupled
triad scores. It is labelled `saas_approximation` wherever it is recorded so it can
never again be read as ground truth.

The file did not move, and could not: it has four company-side importers
(`saas/home_move_win_rate.py`, `saas/customers.py` x3), so a `git mv` would create
`company -> sim` edges in the other direction. It did not need to. Not one of those
four importers reads any of the four names `run_phase2b` imported, which is why the
cut is a split along the ownership line rather than a move — measured by AST closure
in §3ac of `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`.

Seeded from the existing `saas/customers.py` roster. This module is pure: plain dicts
in, plain dicts out. **No imports from `sim/` or `simulation/`** — in particular it
must NOT import the world's dwelling record to check its own guess against, which
would make the supplier right by construction.
"""
import random as _random

# --- SYN-shape property derivation (generator_draw_wiring, remaining build #1) ---
# The synthetically-drawn acquisition cohort (`simulation.population_draw.
# SyntheticCustomer.to_customer_dict()`) that `live_population()` appends when the
# director-reserved `SE_DRAW_POPULATION=1` flag is on does NOT carry the static
# roster's `home_type`/`epc_rating`/`bedrooms` fields — it carries the OBSERVABLE
# `consumption_band` (LOW/MEDIUM/HIGH) instead. The supplier derives the physical
# fields from that observable. This is a genuine derivation (not a `.get()`
# default): a real supplier without an EPC-register lookup would infer dwelling
# size/type from consumption, exactly this shape.
#
# R10 SIMPLIFICATION (honest gap, NOT ground truth): `consumption_band` is a coarse
# 3-way observable, so the derived `property_type`/`bedrooms` are a low-fidelity
# archetype, and `epc_rating` falls back to the UK domestic MODAL band "D" (no
# per-property EPC observable exists for a SYN customer — a real supplier would query
# the EPC register; that lookup is not modelled). These are saas-side approximations
# labelled as such, never claimed as the customer's real property.
_SYN_BEDROOMS_BY_BAND = {"LOW": 2, "MEDIUM": 3, "HIGH": 4}
_SYN_PROPERTY_TYPE_BY_BAND = {"LOW": "flat", "MEDIUM": "semi", "HIGH": "detached"}
_SYN_DEFAULT_BEDROOMS = 3          # MEDIUM-equivalent when band is missing/unknown
_SYN_DEFAULT_PROPERTY_TYPE = "semi"
_SYN_MODAL_EPC_RATING = "D"        # UK domestic modal EPC band; honest population default

# The SAME derivation expressed in the roster's `home_type` vocabulary, for the one
# caller that needs a `home_type` rather than a `property_type`:
# `saas.customers.make_acquired_customer()`, which clones a predecessor's dwelling
# fields when a home move is won on a drawn property. Kept beside the property-type
# map, not near its caller, because the two MUST agree -- `simulation.
# dwelling_records.PROPERTY_TYPE_BY_HOME_TYPE[_SYN_HOME_TYPE_BY_BAND[band]] ==
# _SYN_PROPERTY_TYPE_BY_BAND[band]` for every band, so a drawn customer and its
# home-move successor describe the same dwelling. That identity is asserted in
# tests/saas/test_property_model.py rather than trusted. The join runs through the
# WORLD's home-type map because that is the vocabulary the roster is authored in;
# the assertion lives in a test, which may read both sides, and not in either module.
_SYN_HOME_TYPE_BY_BAND = {
    "LOW": "urban_flat",
    "MEDIUM": "suburban_semi",
    "HIGH": "rural_detached",
}
_SYN_DEFAULT_HOME_TYPE = "suburban_semi"   # MEDIUM-equivalent, matches the default above

# The one basis label that is the SUPPLIER'S. Its two siblings — `authored_roster`
# and `world_draw` — are the world's and live in `simulation/dwelling_records.py`;
# they are deliberately not re-exported here, because a supplier that could stamp
# a record `world_draw` could launder its own guess into ground truth, which is the
# defect B12 exists to repair.
BASIS_SAAS_APPROXIMATION = "saas_approximation"  # the supplier's own guess


def _epc_rating_of(c: dict) -> str:
    """The customer's `epc_rating`, derived from the observable for a drawn record.

    Sibling of `_home_type_of`. Same reason it exists: the static roster authors
    `epc_rating`, a drawn (SYN-*) record does not carry it, and every site that
    reads it must get the SAME answer or two parts of the company will describe
    one customer's dwelling differently.
    """
    if "epc_rating" in c:
        return c["epc_rating"]
    return _derive_syn_property_fields(c)["epc_rating"]


def _home_type_of(c: dict) -> str:
    """The customer's `home_type`, derived from the observable for a drawn record.

    The static roster authors `home_type`; a drawn (SYN-*) record carries
    `consumption_band` instead. One accessor so that every caller needing a
    home_type gets the SAME answer -- `make_acquired_customer()` and the phase-3a
    shock diagnostic previously each read `c["home_type"]` directly, which is a
    KeyError the moment the population draw is activated.
    """
    if "home_type" in c:
        return c["home_type"]
    return _SYN_HOME_TYPE_BY_BAND.get(c.get("consumption_band"), _SYN_DEFAULT_HOME_TYPE)


def _derive_syn_property_fields(c: dict) -> dict:
    """Derive `property_type`/`epc_rating`/`bedrooms` for a SYN-shaped customer.

    Reads only the OBSERVABLE `consumption_band`; returns saas-side approximations
    (see the R10 note above). Pure and deterministic (no RNG) — C-S2 replay-safe.

    This is the branch B12 clause (ii) forbids the world to call, and after the
    2026-08-18 split it no longer can: the world's builder raises
    `simulation.dwelling_records.DwellingNotDrawn` where it used to land here.
    Records built from this function are stamped `BASIS_SAAS_APPROXIMATION` by
    whoever records them.
    """
    band = c.get("consumption_band")
    return {
        "property_type": _SYN_PROPERTY_TYPE_BY_BAND.get(band, _SYN_DEFAULT_PROPERTY_TYPE),
        "epc_rating": _SYN_MODAL_EPC_RATING,
        "bedrooms": _SYN_BEDROOMS_BY_BAND.get(band, _SYN_DEFAULT_BEDROOMS),
    }


# --- THE SUPPLIER'S METER-FLEET RECORD (B12 residual, ruled 2026-08-18) ------
# §3ac left one open question: who owns the per-customer asset table. It is ruled
# WORLD-side (`simulation.dwelling_records.ASSET_PROFILE_BY_CUSTOMER`) because
# whether a house has an EV, solar panels or a smart meter is physical.
#
# What stays here is a DIFFERENT quantity: the supplier's own record of WHICH
# METERS IT HAS INSTALLED. A real supplier genuinely holds that — it commissioned
# the fleet — which is why `smart_meter` is the one asset field
# `company/crm/property_discovery.py` does NOT list in
# `_NEVER_KNOWN_AT_SIGNUP_FIELDS` (`epc_rating`, `floor_area_m2`, `has_solar_pv`,
# `electric_vehicle` are the scored discoveries). The supplier has NO authored
# knowledge of EV or solar and must discover those through events.
#
# WHY THIS IS NOT B3's REFUSED DUPLICATE-THE-CONSTANT MOVE. The seven booleans
# below also appear world-side, so the two agree today. B3 refuses duplication
# when it makes a SCORED belief right by construction — and smart-meter status is
# precisely the field that is not scored, because it is not discovered. The
# duplication is confined to it: nothing the harness scores is settled by a literal
# copied onto both sides. The two tables are separately authored and are allowed to
# drift; a drift would mean the supplier's fleet record is wrong about a real
# meter, which is a defect the model should be able to express. Independence is
# proven by mutation in BOTH directions in
# `tests/simulation/test_the_dwelling_record_is_the_worlds.py` — never by a test
# pinning the two equal (B3's and B7's recorded refusal).
KNOWN_SMART_METER_BY_CUSTOMER = {
    "C1": True,
    "C2": True,
    "C3": False,
    "C4": True,
    "C7": True,
    "C8": True,
    "C9": True,
}


def get_smart_meter_status(customer_id: str, year: int, segment: str = "resi") -> bool:
    """Return True if customer has a smart meter by year-end.

    For known static customers, uses the supplier's own meter-fleet record
    KNOWN_SMART_METER_BY_CUSTOMER directly (the supplier commissioned those
    installations, so its record of them is authoritative FOR THE SUPPLIER).

    For acquired customers (not in the fleet record), uses the smart meter
    rollout penetration rate for the segment and year with a deterministic
    RNG seeded by customer_id. The penetration rate is monotonically increasing,
    so once a customer crosses the threshold they keep their smart meter in all
    subsequent years.

    Phase 50: enables ToU eligibility gate in Phase 51 without changing billing.
    """
    if customer_id in KNOWN_SMART_METER_BY_CUSTOMER:
        return KNOWN_SMART_METER_BY_CUSTOMER[customer_id]

    from saas.smart_meter_rollout import get_penetration
    rng_roll = _random.Random(f"smart_meter_{customer_id}").random()
    penetration = get_penetration(year, segment)
    return rng_roll < penetration
