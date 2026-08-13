"""Customer cohort — identities, geography, and home characteristics.

Defines the four resi customer profiles as plain data: a single source of
truth for later phases (pricing, hedging, weather correlation) to read from,
rather than each owning its own copy of who these customers are.

The module includes:
- A constant `CUSTOMERS` which is a list of four customer dictionaries.
- Accessor functions to retrieve customer data by ID or segment.
- A function to transform customer data into the format required by the settlement pipeline.

Each customer dictionary has the following keys:
- "customer_id": A unique identifier for the customer.
- "acquisition_date": The date the customer was acquired.
- "location": A nested dictionary containing latitude, longitude, and region.
- "home_type": A string describing the type of home.
- "bedrooms": The number of bedrooms in the home.
- "epc_rating": The Energy Performance Certificate rating.
- "eac_kwh": Estimated annual consumption in kilowatt-hours. This field may be `None` for future smart-meter customers.
- "commodity": The type of energy commodity (e.g., electricity). This is included to support potential expansion to gas in the future.
- "contract_type": The type of contract the customer has.
- "segment": The market segment the customer belongs to.

The module adheres to the "pure, seam-safe" pattern, ensuring that it contains only data and accessor functions without any imports from other simulation modules, I/O operations, or network calls. This separation helps maintain clear boundaries between different parts of the system.
"""

CUSTOMERS = [
    {
        "customer_id": "C1",
        "acquisition_date": "2016-01-01",
        "location": {"lat": 51.5074, "lon": -0.1278, "region": "London"},
        "home_type": "urban_flat",
        "bedrooms": 2,
        "epc_rating": "D",
        "eac_kwh": 2500,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C2",
        "acquisition_date": "2016-04-01",
        "location": {"lat": 53.4808, "lon": -2.2426, "region": "Manchester"},
        "home_type": "suburban_semi",
        "bedrooms": 3,
        "epc_rating": "D",
        "eac_kwh": 3500,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C3",
        "acquisition_date": "2016-07-01",
        "location": {"lat": 55.8642, "lon": -4.2518, "region": "Glasgow"},
        "home_type": "tenement_flat",
        "bedrooms": 2,
        "epc_rating": "E",
        "eac_kwh": 3200,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C4",
        "acquisition_date": "2016-10-01",
        "location": {"lat": 51.8330, "lon": -1.8433, "region": "Cotswolds"},
        "home_type": "rural_detached",
        "bedrooms": 4,
        "epc_rating": "E",
        "eac_kwh": 5500,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C5",
        "acquisition_date": "2016-01-01",
        "location": {"lat": 51.5074, "lon": -0.1278, "region": "London"},
        "home_type": "small_office",
        "bedrooms": None,
        "epc_rating": "C",
        "eac_kwh": 15000,
        "profile_class": 3,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "SME",
    },
    {
        "customer_id": "C6",
        "acquisition_date": "2016-04-01",
        "location": {"lat": 53.4808, "lon": -2.2426, "region": "Manchester"},
        "home_type": "warehouse_unit",
        "bedrooms": None,
        "epc_rating": "D",
        "eac_kwh": 45000,
        "profile_class": 3,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "SME",
    },
    # Phase 6a: HH (half-hourly metered, smart meter) resi electricity
    # customers. eac_kwh is None -- these customers have no static
    # "estimated annual consumption"; settlement reads real half-hourly
    # meter data (sim/hh_data/{customer_id}.csv, see
    # simulation/hh_consumption.py) and an effective EAC for hedging-volume
    # sizing is derived from that data instead.
    {
        "customer_id": "C7",
        "acquisition_date": "2016-01-01",
        "location": {"lat": 51.5074, "lon": -0.1278, "region": "London"},
        "home_type": "urban_flat",
        "bedrooms": 1,
        "epc_rating": "C",
        "eac_kwh": None,
        "metering": "HH",
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C8",
        "acquisition_date": "2016-04-01",
        "location": {"lat": 53.4808, "lon": -2.2426, "region": "Manchester"},
        "home_type": "suburban_semi",
        "bedrooms": 3,
        "epc_rating": "C",
        "eac_kwh": None,
        "metering": "HH",
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C9",
        "acquisition_date": "2016-07-01",
        "location": {"lat": 55.8642, "lon": -4.2518, "region": "Glasgow"},
        "home_type": "tenement_flat",
        "bedrooms": 2,
        "epc_rating": "D",
        "eac_kwh": None,
        "metering": "HH",
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    # Phase 24a: I&C electricity customer — 2 GWh/year, HH metered.
    # Phase 26a: industrial warehouse HH profile (Mon-Fri core hours, low weekends,
    # temperature-insensitive). Replaces C7 residential shape used in Phase 24a.
    # Phase 40c: deemed_gap_days=30 — 30-day out-of-contract window each renewal.
    # eac_kwh=None because settlement reads sim/hh_data/C_IC1.csv (~2 GWh/year).
    {
        "customer_id": "C_IC1",
        "acquisition_date": "2017-01-01",
        "location": {"lat": 52.4862, "lon": -1.8904, "region": "Birmingham"},
        "home_type": "warehouse_unit",
        "bedrooms": None,
        "epc_rating": "C",
        "eac_kwh": None,
        "metering": "HH",
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "I&C",
        "deemed_gap_days": 30,
    },
    # Phase 27a: second I&C customer — commercial office building, 1 GWh/year.
    # Temperature-sensitive: summer A/C peak (+15% Jun-Aug), business-hours load
    # (08:00-18:00 Mon-Fri), graduated Saturday (30%), minimal Sunday (8%).
    # Phase 40c: deemed_gap_days=30 — 30-day out-of-contract window each renewal.
    {
        "customer_id": "C_IC2",
        "acquisition_date": "2018-01-01",
        "location": {"lat": 52.4862, "lon": -1.8904, "region": "Birmingham"},
        "home_type": "office_building",
        "bedrooms": None,
        "epc_rating": "C",
        "eac_kwh": None,
        "metering": "HH",
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "I&C",
        "deemed_gap_days": 30,
    },
    # Phase 40a: I&C pass-through electricity customer — 4 GWh/year continuous-process
    # chemical plant, Teesside. Pass-through tariff: wholesale+margin locked at term start;
    # network and policy costs billed at actual rates each settlement period.
    # eac_kwh=None because settlement reads sim/hh_data/C_IC3.csv (~4 GWh/year).
    {
        "customer_id": "C_IC3",
        "acquisition_date": "2019-01-01",
        "location": {"lat": 54.5973, "lon": -1.1049, "region": "Teesside"},
        "home_type": "chemical_plant",
        "bedrooms": None,
        "epc_rating": "E",
        "eac_kwh": None,
        "metering": "HH",
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "I&C",
        "tariff_type": "pass_through",
    },
    # Phase 41a: flex/trading tariff — supermarket chain, 3 GWh/year electricity.
    # Flex: no locked unit rate. Customer calls volume weekly at day-ahead reference
    # price (7-day rolling spot average). Supplier earns a fixed trading markup only.
    # No capital cost (supplier hedges weekly at reference price).
    # eac_kwh=None because settlement reads sim/hh_data/C_IC4.csv (~3 GWh/year).
    {
        "customer_id": "C_IC4",
        "acquisition_date": "2020-01-01",
        "location": {"lat": 53.4808, "lon": -2.2426, "region": "Manchester"},
        "home_type": "supermarket",
        "bedrooms": None,
        "epc_rating": "C",
        "eac_kwh": None,
        "metering": "HH",
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "I&C",
        "tariff_type": "flex",
    },
    # Phase 40b: C_IC3 gas leg — 5 GWh industrial gas, Teesside, pass-through.
    # I&C gas: pays gas CCL (not resi-exempt); GGL applies from Nov 2021.
    {
        "customer_id": "C_IC3g",
        "acquisition_date": "2019-01-01",
        "location": {"lat": 54.5973, "lon": -1.1049, "region": "Teesside"},
        "home_type": "chemical_plant",
        "bedrooms": None,
        "epc_rating": "E",
        "aq_kwh": 5_000_000,
        "commodity": "gas",
        "segment": "I&C",
        "tariff_type": "pass_through",
        "contract_type": "fixed_1yr",
    },
    # Phase 2b: gas dual-fuel records for C1-C4 resi customers
    {
        "customer_id": "C1g",
        "acquisition_date": "2016-01-01",
        "location": {"lat": 51.5074, "lon": -0.1278, "region": "London"},
        "home_type": "urban_flat",
        "bedrooms": 2,
        "epc_rating": "D",
        "aq_kwh": 12000,
        "cv_factor": 39.5,
        "cf": 1.02264,
        "commodity": "gas",
        "contract_type": "fixed_1yr",
        "segment": "resi",
        "data_regime": "historical",
    },
    {
        "customer_id": "C2g",
        "acquisition_date": "2016-04-01",
        "location": {"lat": 53.4808, "lon": -2.2426, "region": "Manchester"},
        "home_type": "suburban_semi",
        "bedrooms": 3,
        "epc_rating": "D",
        "aq_kwh": 15000,
        "cv_factor": 39.5,
        "cf": 1.02264,
        "commodity": "gas",
        "contract_type": "fixed_1yr",
        "segment": "resi",
        "data_regime": "historical",
    },
    {
        "customer_id": "C3g",
        "acquisition_date": "2016-07-01",
        "location": {"lat": 55.8642, "lon": -4.2518, "region": "Glasgow"},
        "home_type": "tenement_flat",
        "bedrooms": 2,
        "epc_rating": "E",
        "aq_kwh": 14000,
        "cv_factor": 39.5,
        "cf": 1.02264,
        "commodity": "gas",
        "contract_type": "fixed_1yr",
        "segment": "resi",
        "data_regime": "historical",
    },
    {
        "customer_id": "C4g",
        "acquisition_date": "2016-10-01",
        "location": {"lat": 51.8330, "lon": -1.8433, "region": "Cotswolds"},
        "home_type": "rural_detached",
        "bedrooms": 4,
        "epc_rating": "E",
        "aq_kwh": 22000,
        "cv_factor": 39.5,
        "cf": 1.02264,
        "commodity": "gas",
        "contract_type": "fixed_1yr",
        "segment": "resi",
        "data_regime": "historical",
    },
]


def _stamp_known_smart_meter_status(customers: list[dict]) -> None:
    """Stamp `smart_meter` from saas.property_model.ASSET_PROFILE_BY_CUSTOMER
    onto any record that doesn't already carry its own smart_meter/metering
    flag. Gas dual-fuel twins (e.g. "C1g") inherit their electricity
    sibling's status -- same physical property, one meter-fleet decision
    (property_model.py's own docstring: gas records represent "the same
    physical property's gas supply").

    Fixes a real cross-module drift (Rich-flagged 2026-07-09): C1-C4's
    literal entries above carried no smart_meter key at all, so
    simulation.meter_reads.meter_type_for_customer() silently defaulted
    every one of them to "traditional" (no smart-meter read behaviour
    anywhere downstream -- meter-read log, bills, portal) even though
    property_model.py's asset profile -- already used elsewhere for
    EV/solar/smart-meter household physics -- said C1 was smart. One
    customer_id, one physical property: this stamps every known customer at
    once rather than patching C1 alone.
    """
    from saas.property_model import ASSET_PROFILE_BY_CUSTOMER
    for customer in customers:
        if "smart_meter" in customer or "metering" in customer:
            continue
        cid = customer["customer_id"]
        base_id = cid[:-1] if cid.endswith("g") else cid
        profile = ASSET_PROFILE_BY_CUSTOMER.get(base_id)
        if profile is not None:
            customer["smart_meter"] = profile["smart_meter"]


_stamp_known_smart_meter_status(CUSTOMERS)


# Phase 7e: successor customers activated when an original account churns and
# we win the home-mover competition. Same property as the predecessor; electricity
# only (gas successors deferred). `acquisition_date` matches the predecessor so
# the term schedule aligns — but actual settlement starts at the churn date.
SUCCESSOR_CUSTOMERS: list[dict] = [
    {
        "customer_id": "C1_2",
        "successor_of": "C1",
        "acquisition_date": "2016-01-01",
        "location": {"lat": 51.5074, "lon": -0.1278, "region": "London"},
        "home_type": "urban_flat",
        "bedrooms": 2,
        "epc_rating": "D",
        "eac_kwh": 2500,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C2_2",
        "successor_of": "C2",
        "acquisition_date": "2016-04-01",
        "location": {"lat": 53.4808, "lon": -2.2426, "region": "Manchester"},
        "home_type": "suburban_semi",
        "bedrooms": 3,
        "epc_rating": "D",
        "eac_kwh": 3500,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C3_2",
        "successor_of": "C3",
        "acquisition_date": "2016-07-01",
        "location": {"lat": 55.8642, "lon": -4.2518, "region": "Glasgow"},
        "home_type": "tenement_flat",
        "bedrooms": 2,
        "epc_rating": "E",
        "eac_kwh": 3200,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C4_2",
        "successor_of": "C4",
        "acquisition_date": "2016-10-01",
        "location": {"lat": 51.8330, "lon": -1.8433, "region": "Cotswolds"},
        "home_type": "rural_detached",
        "bedrooms": 4,
        "epc_rating": "E",
        "eac_kwh": 5500,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C5_2",
        "successor_of": "C5",
        "acquisition_date": "2016-01-01",
        "location": {"lat": 51.5074, "lon": -0.1278, "region": "London"},
        "home_type": "small_office",
        "bedrooms": None,
        "epc_rating": "C",
        "eac_kwh": 15000,
        "profile_class": 3,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "SME",
    },
    {
        "customer_id": "C6_2",
        "successor_of": "C6",
        "acquisition_date": "2016-04-01",
        "location": {"lat": 53.4808, "lon": -2.2426, "region": "Manchester"},
        "home_type": "warehouse_unit",
        "bedrooms": None,
        "epc_rating": "D",
        "eac_kwh": 45000,
        "profile_class": 3,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "SME",
    },
]


# Phase 8a: runtime accumulator for dynamically acquired customers.
# Populated by run_phase2b.main() when a fresh market acquisition wins.
# Never pre-defined — entries are appended at runtime, not at import time.
# Use _clear_acquired_customers() between test runs to avoid cross-test state.
ACQUIRED_CUSTOMERS: list[dict] = []


def _clear_acquired_customers() -> None:
    """Clear the runtime acquisition accumulator. Use in test teardown."""
    ACQUIRED_CUSTOMERS.clear()


# generator_draw_wiring ACTIVATION (2026-08-13, director console: "activate the
# population draw and wire the entrypoints"). A FOURTH registration book, kept
# separate from the three above on purpose.
#
# WHY A SEPARATE LIST, AND NOT AN APPEND TO EITHER EXISTING ONE:
#   - `CUSTOMERS` is the hand-authored 2016-2020 starting roster. Appending here
#     would change what `registered_supply_points()` returns, so the flag-OFF
#     path would stop being byte-identical and every consumer of the static
#     roster would silently move. The seam's whole contract is that OFF changes
#     nothing.
#   - `ACQUIRED_CUSTOMERS` is the run's OWN fresh-market wins, and it is what
#     acquisition-cost accounting counts (`COST_PER_ACQUISITION`). A drawn
#     customer was not won by this run's sales effort, so charging CPA for it
#     would be granting the company a book AND billing it for one. The drawn
#     dicts carry `acquisition_type: "synthetic_draw"` precisely so the two
#     never merge.
#
# WHAT IT IS: the meter points the curriculum says this supplier registered over
# 2021-2025 (W2_2 Profile B trickle, lambda=1.0/yr). Registration is a published
# industry act, so the book knowing about them is exactly right -- what must NOT
# happen is the company reading the SIM's hidden cohort, and it cannot: these are
# saas-shaped observable dicts, `to_customer_dict()` omits the ground-truth
# `cohort` by construction.
#
# DIRECTION: this list is written by the SIM side pushing registrations IN through
# `company.interfaces.supply_book.register_drawn_points()`. Nothing here imports
# `simulation.*` -- the company never pulls from the generator.
DRAWN_CUSTOMERS: list[dict] = []


def _register_drawn_customers(points: list[dict]) -> list[dict]:
    """Register drawn supply points, idempotently by `customer_id`.

    Idempotent because the activation runs once per process but entrypoints bind
    the book at import time in any order -- a second call must not double the
    book. Returns the points actually added (empty on a repeat call).
    """
    known = {c["customer_id"] for c in DRAWN_CUSTOMERS}
    added = [p for p in points if p["customer_id"] not in known]
    DRAWN_CUSTOMERS.extend(added)
    return added


def _clear_drawn_customers() -> None:
    """Clear the drawn-registration book. Use in test teardown."""
    DRAWN_CUSTOMERS.clear()


def make_acquired_customer(
    customer_id: str,
    predecessor: dict,
    acquisition_date: str,
) -> dict:
    """Build a fresh-market acquisition customer record cloned from a predecessor's
    property profile. Electricity only (no gas leg in Phase 8a).

    Phase 50: stamps smart_meter based on rollout penetration at acquisition year.
    """
    from saas.property_model import get_smart_meter_status
    import random as _random
    acq_year = int(acquisition_date[:4])
    segment = predecessor.get("segment", "resi")
    has_smart_meter = get_smart_meter_status(customer_id, acq_year, segment)
    # A DRAWN (SYN-*) predecessor carries `consumption_band` instead of the static
    # roster's `home_type`/`epc_rating`/`bedrooms` (generator_draw_wiring
    # activation). Branch on `home_type` exactly as `property_model.build_properties`
    # does, so the static path stays byte-identical and winning the home move on a
    # drawn property derives the dwelling fields from the observable rather than
    # raising KeyError. Local import: same cycle-avoidance as `get_smart_meter_status`
    # above.
    if "home_type" in predecessor:
        _home_type = predecessor["home_type"]
        _epc_rating = predecessor["epc_rating"]
        _bedrooms = predecessor.get("bedrooms")
    else:
        from saas.property_model import _derive_syn_property_fields, _home_type_of
        _phys = _derive_syn_property_fields(predecessor)
        _home_type = _home_type_of(predecessor)
        _epc_rating = _phys["epc_rating"]
        _bedrooms = _phys["bedrooms"]
    return {
        "customer_id": customer_id,
        "successor_of": predecessor["customer_id"],
        "acquisition_type": "fresh_market",
        "acquisition_date": acquisition_date,
        "location": predecessor["location"],
        "home_type": _home_type,
        "bedrooms": _bedrooms,
        "epc_rating": _epc_rating,
        "eac_kwh": predecessor.get("eac_kwh", 3200),
        "commodity": "electricity",
        "contract_type": predecessor.get("contract_type", "fixed_1yr"),
        "segment": segment,
        "smart_meter": has_smart_meter,
        **({"profile_class": predecessor["profile_class"]} if "profile_class" in predecessor else {}),
    }


def get_customer(customer_id: str) -> dict | None:
    """
    Retrieve a customer record by customer ID.

    :param customer_id: The unique identifier for the customer.
    :return: The customer dictionary if found, otherwise None.
    """
    # DRAWN_CUSTOMERS last: it is empty unless the population draw is activated,
    # so the flag-OFF lookup is the same three books in the same order as before.
    # It has to be searched at all because an activated run ITERATES the drawn
    # points (via `live_population()`) and then looks them back up by id -- a
    # book you can iterate but not resolve is what made a home-move win hand
    # `None` to `make_acquired_customer()`.
    all_customers = CUSTOMERS + SUCCESSOR_CUSTOMERS + ACQUIRED_CUSTOMERS + DRAWN_CUSTOMERS
    return next((customer for customer in all_customers if customer["customer_id"] == customer_id), None)


def get_customers_for_segment(segment: str) -> list[dict]:
    """
    Retrieve all customer records that match a given segment.

    :param segment: The market segment to filter by.
    :return: A list of customer dictionaries matching the segment, in the order they appear in CUSTOMERS.
    """
    return [customer for customer in CUSTOMERS if customer["segment"] == segment]


def customer_to_settlement_input(customer: dict) -> dict:
    """
    Transform a customer record into the minimal format required by the settlement pipeline.

    :param customer: The customer dictionary to transform.
    :return: A dictionary containing only "customer_id" and "acquisition_date".
    """
    return {
        "customer_id": customer["customer_id"],
        "acquisition_date": customer["acquisition_date"]
    }
