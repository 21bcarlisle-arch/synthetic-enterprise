"""Property and asset model — Phase 4c-1 (physical simulation layer).

Phase 4c replaces flat consumption/billing assumptions with a physical and
behavioural model. This is the first sub-phase: give each residential
customer a physical property record — type, EPC rating, occupancy pattern,
heating system, and asset mix (EV/solar/smart meter) — that later sub-phases
(4c-2 weather-driven demand, 4c-4 bill clarity, 4c-5 payment behaviour) read
from.

Seeded from the existing `saas/customers.py` roster:
- `property_type`, `epc_rating`, `bedrooms` come directly from the resi
  electricity record (C1-C4).
- `heating_system` is `"gas_boiler"` if a matching dual-fuel gas record
  (`"{customer_id}g"`) exists in the roster, else `"electric_storage"` — all
  four current resi customers are dual-fuel, so all get gas boilers today.
- `occupancy_pattern` and `assets` are seed estimates (no real data yet) —
  see `OCCUPANCY_PATTERN_BY_CUSTOMER` and `ASSET_PROFILE_BY_CUSTOMER` below.
  These are placeholders pending the `customer-archetype-data-enrichment`
  background task (see `docs/instructions/background-tasks.md`), which will
  derive archetype-based occupancy/asset distributions from real EPC/Census/
  Ofgem data and should replace these per-customer constants in a future
  increment.

This module is pure: plain dicts in, plain dicts out. No imports from `sim/`.
"""
import random as _random

PROPERTY_TYPE_BY_HOME_TYPE = {
    "urban_flat": "flat",
    "suburban_semi": "semi",
    "tenement_flat": "flat",
    "rural_detached": "detached",
}

DEFAULT_PROPERTY_TYPE = "other"

# Seed estimates — one of single/family/elderly per current resi customer,
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

# Seed estimates — EV/solar/smart meter mix, chosen for asset-mix diversity
# pending real archetype data (e.g. rural detached properties are more
# likely to have driveway EV charging and roof space for solar).
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


def build_properties(customers: list[dict]) -> dict:
    """Build one physical-property record per resi electricity customer.

    `customers` is the `saas.customers.CUSTOMERS` roster (or a subset). Only
    records with `segment == "resi"` and `commodity == "electricity"` get a
    property (the dual-fuel gas records, e.g. "C1g", represent the same
    physical property's gas supply and are consulted only to determine
    `heating_system`; SME records are out of scope for this sub-phase).

    Returns a dict keyed by `customer_id`, each value:
      {customer_id, property_type, epc_rating, bedrooms, occupancy_pattern,
       heating_system, assets: {ev, solar, smart_meter}}
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
        properties[cid] = {
            "customer_id": cid,
            "property_type": PROPERTY_TYPE_BY_HOME_TYPE.get(c["home_type"], DEFAULT_PROPERTY_TYPE),
            "epc_rating": c["epc_rating"],
            "bedrooms": c["bedrooms"],
            "occupancy_pattern": OCCUPANCY_PATTERN_BY_CUSTOMER.get(cid, DEFAULT_OCCUPANCY_PATTERN),
            "heating_system": GAS_HEATING_SYSTEM if cid in gas_customer_ids else DEFAULT_HEATING_SYSTEM,
            "assets": dict(ASSET_PROFILE_BY_CUSTOMER.get(cid, DEFAULT_ASSETS)),
        }
    return properties


def get_smart_meter_status(customer_id: str, year: int, segment: str = "resi") -> bool:
    """Return True if customer has a smart meter by year-end.

    For known static customers, uses ASSET_PROFILE_BY_CUSTOMER directly
    (their initial status is authoritative).

    For acquired customers (not in the profile table), uses the smart meter
    rollout penetration rate for the segment and year with a deterministic
    RNG seeded by customer_id. The penetration rate is monotonically increasing,
    so once a customer crosses the threshold they keep their smart meter in all
    subsequent years.

    Phase 50: enables ToU eligibility gate in Phase 51 without changing billing.
    """
    if customer_id in ASSET_PROFILE_BY_CUSTOMER:
        return ASSET_PROFILE_BY_CUSTOMER[customer_id]["smart_meter"]

    from saas.smart_meter_rollout import get_penetration
    rng_roll = _random.Random(f"smart_meter_{customer_id}").random()
    penetration = get_penetration(year, segment)
    return rng_roll < penetration
