"""The WORLD's dwelling and household record for each supplied property (B12).

This module is the world side of the `B12_the_dwelling_is_the_worlds_and_the_
company_only_discovers_it` split, executed 2026-08-18 (KNIFE3 step 35). It exists
because `simulation/run_phase2b.py` used to reach across the epistemic wall into
`saas/property_model.py` for `build_properties` — the one live `owed` crossing under
B12. What a house physically IS (its type, its EPC band, its bedrooms, who lives in
it, what it is heated by, whether it has an EV or solar panels) is a fact about the
WORLD. The supplier discovers those facts; it does not author them.

WHAT MOVED HERE AND WHY IT IS NOT A `git mv`. `saas/property_model.py` has four
company-side importers, so the FILE cannot move (that would create `company -> sim`
edges in the other direction). But the crossing is not the file — it is one edge
whose payload is four names, and not one of those four importers imports any of
them (measured by AST closure, §3ac of the disposition register). The two sides
share exactly one name once the supplier's approximation subtree is excluded, so
the cut is a SPLIT along the ownership line, not a move.

WHAT DELIBERATELY DID NOT MOVE. `_derive_syn_property_fields` and its `_SYN_*` band
tables stay in `saas/property_model.py`. They are the SUPPLIER'S APPROXIMATION of a
dwelling it has not observed, derived from the observable `consumption_band`. B12
clause (ii) requires the world to draw its dwelling "with no call into any `saas.*`
approximation", so the world-side builder below has no such fallback at all: a drawn
customer with no world dwelling is an internal inconsistency in the world, and it
RAISES rather than guessing.

**THIS REVERSES A DELIBERATE CHOICE OF A PREVIOUS STEP, IN THOSE WORDS.** Step 31
(§3z) chose the `saas_approximation` fallback to be "deliberately silent-but-labelled
rather than" raising, pinned at `tests/simulation/
test_the_worlds_dwelling_is_drawn_not_believed.py`:299. That choice was correct while
ONE function served both sides — a shared builder cannot raise on the supplier's
behalf. The split is what makes the two behaviours separable: the world raises
because it must know its own draw, and the supplier keeps guessing because guessing
is its job. The labelled-fallback branch is not deleted; it stays saas-side where the
label means something.

THE ASSET TABLE'S OWNERSHIP, which §3ac left as the one open residual. It is ruled
WORLD-side and lives here. Whether a house has an EV, solar panels or a smart meter
is physical. The supplier's own knowledge of it is a different quantity that is
allowed to be wrong, and it is separately authored at
`saas.property_model.KNOWN_SMART_METER_BY_CUSTOMER` — the supplier's METER-FLEET
record, which a real supplier genuinely does hold because it installed the meters.
That record covers `smart_meter` ONLY, and smart-meter status is the one asset field
`company/crm/property_discovery.py` does NOT list in `_NEVER_KNOWN_AT_SIGNUP_FIELDS`
(`epc_rating`, `floor_area_m2`, `has_solar_pv`, `electric_vehicle` are the scored
discoveries). So the duplicated literal is confined to the single field that is not
a scored belief, which is why this is not B3's refused duplicate-the-constant move:
no belief the harness scores is made right by construction. Independence is proven by
mutation in both directions in
`tests/simulation/test_the_dwelling_record_is_the_worlds.py`, never by a test pinning
the two tables equal.

This module imports nothing from `saas/` or `company/` and must not.
"""
import random as _random

PROPERTY_TYPE_BY_HOME_TYPE = {
    "urban_flat": "flat",
    "suburban_semi": "semi",
    "tenement_flat": "flat",
    "rural_detached": "detached",
}

DEFAULT_PROPERTY_TYPE = "other"

# Seed estimates — one of single/family/elderly per authored resi customer,
# chosen for occupancy-pattern diversity pending real archetype data.
OCCUPANCY_PATTERN_BY_CUSTOMER = {
    "C1": "single",
    "C2": "family",
    "C3": "elderly",
    "C4": "family",
    "C7": "single",
    "C8": "family",
    "C9": "elderly",
}
DEFAULT_OCCUPANCY_PATTERN = "single"

# --- W2_13: people-count and composition -----------------------------------
# `occupancy_pattern` above is a 3-way CATEGORY. `simulation.demand_model`
# (W2_13) keys both its occupancy responses — volume and daytime shape — on a
# PEOPLE COUNT, with the category kept only as the fallback for a household
# whose headcount is unknown. So the dwelling record carries one.
#
# For the seven authored static customers the headcount is set explicitly and
# consistently with the authored `occupancy_pattern` (a "single" household of
# four people would be incoherent). These are SEED ESTIMATES of exactly the
# same status as the occupancy patterns beside them — no real data.
PEOPLE_COUNT_BY_CUSTOMER = {
    "C1": 1,  # single
    "C2": 4,  # family
    "C3": 2,  # elderly couple
    "C4": 3,  # family
    "C7": 1,  # single
    "C8": 4,  # family
    "C9": 1,  # elderly, living alone
}

# Every other customer (the acquired/SYN cohort) draws a headcount from the
# real population distribution: ONS Census 2021 table TS017 "Household size",
# England — 1p 30.1%, 2p 34.0%, 3p 16.0%, 4p 12.9%, 5+p 7.0% (mean 2.37
# persons/household), the same anchor `simulation.household_segments.
# OCCUPANCY_POPULATION_SHARE` and `simulation.demand_model.
# HOUSEHOLD_SIZE_POPULATION_SHARE` use. Held as a literal here rather than
# imported for the reason `demand_model` states over its own copy — so this
# builder cannot be silently re-levelled by an unrelated edit to the segment
# bands — and `tests/simulation/test_the_dwelling_record_is_the_worlds.py`
# asserts the copies agree.
HOUSEHOLD_SIZE_SHARE_ONS_TS017 = [(1, 0.301), (2, 0.340), (3, 0.160), (4, 0.129), (5, 0.070)]

# R10 GAP (a) — the adults/children split. NEED's consumption gradient is
# keyed on ADULTS ONLY and no located table cross-tabulates adults against
# children, so there is no anchor for how many children a household of a given
# size contains, nor for a child's marginal consumption. This module therefore
# does NOT fabricate a children distribution: `children_count` defaults to 0
# (an all-adult reading of the headcount, which is exactly the basis NEED
# publishes on) and the aggregate stays where NEED puts it. The MECHANISM for
# children exists and is exercised in `simulation.demand_model`
# (`child_adult_equivalence`, sampled per household from a range, never a
# point estimate) for callers that do know a composition — the gap is the
# population-level split, not the response.
DEFAULT_CHILDREN_COUNT = 0


def _derive_people_count(customer_id: str) -> int:
    """Deterministic per-customer household size for a customer with no
    authored headcount, drawn from the ONS TS017 distribution above.

    Same per-customer-deterministic convention as
    `simulation.household_segments`' archetype draws, under its OWN named key
    (`people_count_<id>`) so it cannot shift any other draw's sequence (C-S2).
    """
    roll = _random.Random(f"people_count_{customer_id}").random()
    cumulative = 0.0
    for size, share in HOUSEHOLD_SIZE_SHARE_ONS_TS017:
        cumulative += share
        if roll < cumulative:
            return size
    return HOUSEHOLD_SIZE_SHARE_ONS_TS017[-1][0]  # float-rounding fallback


# --- THE PHYSICAL ASSET MIX, ruled world-side 2026-08-18 (KNIFE3 step 35) ---
# Seed estimates — EV/solar/smart meter mix, chosen for asset-mix diversity
# pending real archetype data (e.g. rural detached properties are more likely
# to have driveway EV charging and roof space for solar).
#
# THIS IS THE TRUTH, not the supplier's record of it. `run_phase2b` reads it for
# world physics only (`simulation.demand_response.compute_shift_fraction`). The
# supplier's own meter-fleet knowledge is the separately-authored
# `saas.property_model.KNOWN_SMART_METER_BY_CUSTOMER`; the supplier has no
# authored knowledge of EV or solar at all and must discover those
# (`company/crm/property_discovery.py::_NEVER_KNOWN_AT_SIGNUP_FIELDS`).
ASSET_PROFILE_BY_CUSTOMER = {
    "C1": {"ev": False, "solar": False, "smart_meter": True},
    "C2": {"ev": True, "solar": False, "smart_meter": True},
    "C3": {"ev": False, "solar": False, "smart_meter": False},
    "C4": {"ev": True, "solar": True, "smart_meter": True},
    "C7": {"ev": True, "solar": False, "smart_meter": True},
    "C8": {"ev": False, "solar": False, "smart_meter": True},
    "C9": {"ev": False, "solar": False, "smart_meter": True},
}
DEFAULT_ASSETS = {"ev": False, "solar": False, "smart_meter": False}

GAS_HEATING_SYSTEM = "gas_boiler"
DEFAULT_HEATING_SYSTEM = "electric_storage"


# --- WHOSE DWELLING THE RECORD IS (B12) ------------------------------------
# Every dwelling record states which of these produced its physical fields, so a
# record can never be read as the world's ground truth without saying where it
# came from. The finding that forced this
# (WORKER_FINDING_THE_WORLDS_DWELLING_FOR_A_DRAWN_HOME_IS_THE_COMPANYS_OWN_ESTIMATE_
# 2026-08-17) was invisible precisely because the record did not carry its basis.
#
# The third basis that used to sit here, `saas_approximation`, is NOT part of the
# world's vocabulary and is deliberately absent — see the module docstring. It
# still exists on the supplier's side of the split, where it labels the
# supplier's own guess as the supplier's own guess.
BASIS_AUTHORED_ROSTER = "authored_roster"  # the hand-authored C1-C9 dwelling
BASIS_WORLD_DRAW = "world_draw"            # the world's published stock draw


class DwellingNotDrawn(KeyError):
    """A supplied customer has no dwelling on either basis the world recognises.

    Raised rather than approximated. The world knows every home it drew; a drawn
    customer missing from `dwellings` means the draw and the roster have come
    apart upstream, and silently substituting the SUPPLIER'S guess for the
    world's ground truth is the exact defect B12 exists to repair. Guessing here
    would be indistinguishable, downstream, from having known.
    """


def build_properties(customers: list[dict], dwellings: dict | None = None) -> dict:
    """Build one physical dwelling record per resi electricity customer.

    `dwellings` (B12) is `{customer_id: {property_type, epc_rating, bedrooms}}` —
    the WORLD's own dwelling for each drawn home, handed in by the world-side
    caller (`simulation.live_population.live_dwellings()`).

    Two bases, and no third. A customer carrying the authored roster's
    `home_type`/`epc_rating`/`bedrooms` gets those at basis `authored_roster`; a
    drawn (SYN-*) customer gets the world's drawn dwelling at basis `world_draw`.
    A drawn customer present in `customers` but absent from `dwellings` raises
    `DwellingNotDrawn` — the world does not fall back to the supplier's
    approximation, which is what this module was split out of `saas/` to stop.

    `customers` is the `saas.customers.CUSTOMERS` roster as published world-ward
    by `simulation.live_population.live_population()` (or a subset). Only records
    with `segment == "resi"` and `commodity == "electricity"` get a dwelling (the
    dual-fuel gas records, e.g. "C1g", represent the same physical property's gas
    supply and are consulted only to determine `heating_system`; SME records are
    out of scope for this sub-phase).

    Returns a dict keyed by `customer_id`, each value:
      {customer_id, property_type, epc_rating, bedrooms, dwelling_basis,
       occupancy_pattern, people_count, children_count, heating_system,
       assets: {ev, solar, smart_meter}}

    `people_count`/`children_count` (W2_13) are the primary key for
    `simulation.demand_model`'s occupancy volume and daytime-shape responses;
    `occupancy_pattern` is retained as the coarse shape fallback.
    """
    gas_customer_ids = {
        c["customer_id"][:-1]
        for c in customers
        if c.get("commodity") == "gas" and c["customer_id"].endswith("g")
    }

    properties = {}
    for c in customers:
        if c["segment"] != "resi" or c.get("commodity") != "electricity":
            continue
        cid = c["customer_id"]
        # The static roster carries `home_type`/`epc_rating`/`bedrooms`; the SYN
        # cohort (flag-on `live_population()`) does not. Branch on the presence of
        # `home_type` so the static path stays byte-identical to the pre-split
        # builder and a SYN dict is served by the world's own draw.
        if "home_type" in c:
            phys = {
                "property_type": PROPERTY_TYPE_BY_HOME_TYPE.get(c["home_type"], DEFAULT_PROPERTY_TYPE),
                "epc_rating": c["epc_rating"],
                "bedrooms": c["bedrooms"],
            }
            basis = BASIS_AUTHORED_ROSTER
        elif (dwellings or {}).get(cid):
            phys = dwellings[cid]
            basis = BASIS_WORLD_DRAW
        else:
            raise DwellingNotDrawn(
                f"{cid!r} is supplied but the world drew no dwelling for it, and it "
                f"carries no authored roster dwelling either. The world does not "
                f"approximate its own ground truth (B12); fix the draw upstream in "
                f"simulation.live_population.live_dwellings()."
            )
        properties[cid] = {
            "customer_id": cid,
            "property_type": phys["property_type"],
            "epc_rating": phys["epc_rating"],
            "bedrooms": phys["bedrooms"],
            "dwelling_basis": basis,
            "occupancy_pattern": OCCUPANCY_PATTERN_BY_CUSTOMER.get(cid, DEFAULT_OCCUPANCY_PATTERN),
            "people_count": PEOPLE_COUNT_BY_CUSTOMER.get(cid) or _derive_people_count(cid),
            "children_count": DEFAULT_CHILDREN_COUNT,
            "heating_system": GAS_HEATING_SYSTEM if cid in gas_customer_ids else DEFAULT_HEATING_SYSTEM,
            "assets": dict(ASSET_PROFILE_BY_CUSTOMER.get(cid, DEFAULT_ASSETS)),
        }
    return properties
