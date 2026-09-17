"""Is the book a spread of distinct half-hourly shapes, or rescaled copies of one profile?

REUSE: tools/book_shape_spread.py
CLASS: CUSTOM
INDEX: searched "shape", "profile", "spread", "diversity", "rescale", "peak share".
       `tools/demand_vector_coverage.py` measures how many households reproduce a DISTRIBUTION of
       annual quantities; it says nothing about the shape of a day. `simulation/demand_model.
       build_demand_shape` is the LEGACY provider this measures against. `tools/couple_fabric.py`
       compares belief to truth, not household to household. Nothing measured shape diversity.

WHY THIS EXISTS
---------------
Director, setting the phase-one test: *"look across the book and see a credible spread of those,
not a set of rescaled copies of one profile."*

That is a precise, falsifiable property and it needs the level removed to test. Two households can
differ by a factor of three in annual kWh and still have the SAME SHAPE -- which is exactly what a
rescaled national profile produces, and exactly what looks like variety until you normalise.

So every premise-day is divided by its own total. What is left is the shape alone. If the book is
rescaled copies, the normalised profiles are identical and the pairwise distance is zero however
different the totals look.

THE COMPARISON IS AGAINST THE THING IT REPLACES
------------------------------------------------
The legacy provider takes one published Profile Class 1 curve and scales it per customer per day.
Under normalisation its households collapse onto each other -- and the director found that himself
before this existed: *"I don't believe single and family households have the same daily electricity
shape... 'identical to four decimals' is the tell."* The fabric path has to beat that, and by how
much is the measurement rather than the claim.
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

PERIODS_PER_DAY = 48

#: The premises whose cells have a real daily weather archive today.
ARCHIVE_CELLS = ("C1", "C2", "C3", "C4")


def _varied_households():
    """A spread of real fabric and people, not a spread of scale factors.

    Deliberately crossing the things that should move a SHAPE rather than a level: fabric era and
    insulation (how fast the house loses heat, so how long the boiler runs), property type (how
    much of it there is), and bedrooms (which drives the occupancy prior, so the base load and the
    hot-water draw).
    """
    sys.path.insert(0, str(PROJECT / "tests" / "simulation"))
    from test_premise_trace import make_household

    from simulation.household import BuildEra, InsulationLevel, PropertyType

    cases = []
    for era in (BuildEra.PRE_1919, BuildEra.ERA_1965_1980, BuildEra.POST_2000):
        for insulation in (InsulationLevel.POOR, InsulationLevel.PARTIAL, InsulationLevel.FULL):
            for ptype, beds in ((PropertyType.FLAT, 1),
                                (PropertyType.SEMI_DETACHED, 3),
                                (PropertyType.DETACHED, 5)):
                cases.append({
                    "label": f"{era.name}/{insulation.name}/{ptype.name}{beds}",
                    "household": make_household(
                        property_type=ptype, build_era=era,
                        insulation=insulation, bedrooms=beds),
                })
    return cases


def _normalised_daily(series: list[float]) -> list[float]:
    """A day's 48 half-hours as SHARES of that day. The level is divided out on purpose."""
    total = sum(series)
    if total <= 0:
        return [0.0] * PERIODS_PER_DAY
    return [v / total for v in series]


def _mean_abs_difference(a: list[float], b: list[float]) -> float:
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def spread(profiles: dict[str, list[float]]) -> dict:
    """Pairwise shape distances over a set of normalised profiles.

    ONE COPY, used by both arms of both measurements (2026-09-17). `measure` and `measure_book`
    each carried their own, which is two implementations of the statistic the whole tool exists to
    report -- and the two arms of a comparison computing their distance differently is the
    quietest way to publish a ratio that is not a quantity.

    THE STATISTIC THAT ANSWERS THE QUESTION IS `closest_pair`, not the mean. "Rescaled copies of
    one profile" is not a claim about the AVERAGE distance -- it is the claim that some pair is the
    SAME shape. A mean can look healthy while the closest pair is a duplicate, which is exactly
    what the legacy path does: its single and family households are identical to four decimal
    places and its elderly one is not, so the average hides the collapse.
    """
    keys = sorted(profiles)
    pairs = list(itertools.combinations(keys, 2))
    if not pairs:
        return {"n_profiles": len(keys), "n_pairs": 0}
    dists = [_mean_abs_difference(profiles[a], profiles[b]) for a, b in pairs]
    order = sorted(dists)
    closest = min(range(len(pairs)), key=lambda i: dists[i])
    return {
        "n_profiles": len(keys),
        "n_pairs": len(pairs),
        "mean_abs_share_difference": round(sum(dists) / len(dists), 6),
        "median": round(order[len(order) // 2], 6),
        "p10": round(order[int(0.10 * len(order))], 6),
        "p90": round(order[int(0.90 * len(order))], 6),
        "closest_pair": [pairs[closest][0], pairs[closest][1]],
        "closest_pair_distance": round(dists[closest], 8),
        "identical_pairs": sum(1 for d in dists if d < 1e-9),
        "near_identical_pairs": sum(1 for d in dists if d < 1e-4),
    }


def measure(year: int = 2022, month: int = 1, seed: int = 42) -> dict:
    """Shape diversity across fabric x cell, for the fabric path and the legacy one."""
    import simulation.premise_trace as pt

    start, end = dt.date(year, month, 1), dt.date(year, month, 28)
    cases = _varied_households()

    fabric_gas: dict[str, list[float]] = {}
    fabric_elec: dict[str, list[float]] = {}
    for cell in ARCHIVE_CELLS:
        weather = pt.load_trace_weather(cell, start=start, end=end)
        if not weather:
            continue
        for case in cases:
            key = f"{cell}:{case['label']}"
            trace = pt.generate_premise_trace(
                premise_id=key, household=case["household"], weather=weather,
                seed=seed, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
            gas = [0.0] * PERIODS_PER_DAY
            elec = [0.0] * PERIODS_PER_DAY
            for day in trace.days:
                for period in range(PERIODS_PER_DAY):
                    gas[period] += day.gas_kwh[period]
                    elec[period] += day.electricity_kwh[period]
            fabric_gas[key] = _normalised_daily(gas)
            fabric_elec[key] = _normalised_daily(elec)

    # --- the legacy provider, measured the same way ------------------------------------------
    legacy = {}
    try:
        from sim.profile_class_1 import load_pc1_shape
        from simulation import demand_model as dm

        base = load_pc1_shape(f"{year}-{month:02d}-15")
        for pattern in ("single", "family", "elderly"):
            for people in (1, 3, 5):
                prop = {"heating_system": "gas_boiler", "occupancy_pattern": pattern,
                        "assets": {}, "people_count": people}
                shape = dm.build_demand_shape(list(base), 8.0, "electricity", prop)
                legacy[f"{pattern}{people}"] = _normalised_daily(list(shape))
    except Exception as exc:  # noqa: BLE001 -- reported, not hidden
        legacy = {}
        legacy_error = str(exc)[:160]
    else:
        legacy_error = None

    return {
        "window": f"{start}..{end}",
        "cells": list(ARCHIVE_CELLS),
        "fabric_path": {
            "gas": spread(fabric_gas),
            "electricity": spread(fabric_elec),
        },
        "legacy_path": {
            "electricity": spread(legacy) if legacy else {"n_profiles": 0},
            "error": legacy_error,
        },
    }


def measure_book(year: int = 2022, month: int = 1, seed: int = 42,
                 limit: int | None = None, progress=lambda _m: None) -> dict:
    """The same question asked of THE BOOK, rather than of a designed panel.

    WHY THIS IS A SEPARATE MEASUREMENT AND NOT A BIGGER `measure` (2026-09-17).
    `measure` crosses 27 constructed households with the four legacy archive sites. That was the
    right instrument while the archive WAS four sites: it asks whether the fabric path CAN produce
    a spread, holding the population fixed and varying the things that should move a shape.

    It cannot answer the director's question, which is about the book. Its households are built by
    `make_household` to span era x insulation x property type, so the spread it finds is the spread
    someone designed into it. The book's households are drawn, its premises sit in 149 real cells
    rather than 4, and its composition is whatever the campaign won. **A panel can prove the
    mechanism works and still say nothing about whether the book is a spread or a stack of
    copies.** Both are kept: the panel is the capability, this is the fact.

    ONE VARIABLE AGAINST THE LEGACY ARM. Each premise is measured twice over the same window with
    the same household and the same cell -- once on the shipped fabric path, once on the legacy
    provider it replaced. The premises, not just the counts, are held fixed, so the comparison is
    not two populations wearing one number (`legacy_path` in `measure` compares nine constructed
    occupancy/headcount combinations, which is a different set from its fabric arm).
    """
    from sim.profile_class_1 import load_pc1_shape
    from simulation.demand_model import build_demand_shape
    from simulation.dwelling_records import build_properties
    from simulation.fabric_demand_path import WeatherWorldSource, build_fabric_series_for_site
    from simulation.household_demand import HouseholdDemandRegister
    from simulation.live_population import live_drawn_households, live_dwellings, live_population
    from simulation.run_phase2b import DEFAULT_PROPERTY

    start, end = dt.date(year, month, 1), dt.date(year, month, 28)
    customers = [c for c in live_population() if c["commodity"] == "electricity"]
    if limit is not None:
        customers = customers[:limit]
    register = HouseholdDemandRegister(customers, drawn_households=live_drawn_households())
    source = WeatherWorldSource.load()
    # THE LEGACY ARM'S REAL INPUTS. A first draft of this built the property dict inline from
    # `customer.get("occupancy_pattern", "family")` and `customer.get("people_count", 3)` -- keys
    # the live customer records DO NOT CARRY. Every premise therefore got the identical dict, and
    # the legacy arm reported all 45 pairs identical at distance exactly 0.0. That reading was
    # this harness repeating one input, not a measurement of the legacy provider, and it happened
    # to point the way the hypothesis wanted. `build_properties` is what the runner itself feeds
    # `build_demand_shape`, so the legacy arm is now the legacy path rather than a caricature.
    properties = build_properties(customers, dwellings=live_dwellings())

    fabric_elec: dict[str, list[float]] = {}
    legacy_elec: dict[str, list[float]] = {}
    cells_seen: set[str] = set()
    refused: dict[str, int] = {}
    base = load_pc1_shape(f"{year}-{month:02d}-15")

    for customer in customers:
        cid = str(customer["customer_id"])
        cell = source.site_for(customer)
        if not source.available(cell):
            refused[cell if cell.startswith("no ") else "cell incomplete"] = \
                refused.get(cell if cell.startswith("no ") else "cell incomplete", 0) + 1
            continue
        household = register.household_at_date(cid, start.isoformat())
        if household is None:
            refused["no household record"] = refused.get("no household record", 0) + 1
            continue
        try:
            series = build_fabric_series_for_site(
                customer_id=cid,
                household_at_date=lambda d, _c=cid: register.household_at_date(_c, d),
                weather_site=cell, latitude_deg=customer["location"]["lat"],
                start=start, end=end, seed=seed,
                weather_days_for=source.days,
            )
        except Exception as exc:  # noqa: BLE001 -- counted by its MESSAGE, never skipped silently
            # The type alone is not a cause. A first draft reported `{'ValueError': 2}`, which
            # names the class of two premises nobody can act on; the message says which two and
            # why, and 213 identical sentences was the exact defect this whole run was about.
            cause = f"{type(exc).__name__}: {str(exc)[:90]}"
            refused[cause] = refused.get(cause, 0) + 1
            continue
        cells_seen.add(cell)
        elec = [0.0] * PERIODS_PER_DAY
        for periods in series.gross_electricity_kwh.values():
            for period, value in enumerate(periods):
                elec[period] += value
        fabric_elec[f"{cell}:{cid}"] = _normalised_daily(elec)

        # THE LEGACY ARM, ON THE SAME PREMISE, with the property record the RUNNER would have
        # handed it. A premise with no record falls to the runner's own DEFAULT_PROPERTY rather
        # than being dropped: dropping it would silently shrink the legacy arm's population below
        # the fabric arm's and make the two spreads incomparable.
        prop = properties.get(cid) or dict(DEFAULT_PROPERTY)
        legacy_elec[f"{cell}:{cid}"] = _normalised_daily(
            list(build_demand_shape(list(base), 8.0, "electricity", prop)))
        progress(f"  {len(fabric_elec)} priced")

    return {
        "window": f"{start}..{end}",
        "book_electricity_customers": len(customers),
        "priced": len(fabric_elec),
        "distinct_cells": len(cells_seen),
        "not_priced": refused,
        "fabric_path": {"electricity": spread(fabric_elec)},
        "legacy_path": {"electricity": spread(legacy_elec)},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--year", type=int, default=2022)
    ap.add_argument("--month", type=int, default=1)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--book", action="store_true",
                    help="measure THE BOOK's real premises in their own cells, not the panel")
    ap.add_argument("--limit", type=int, default=None, help="with --book, price at most N premises")
    args = ap.parse_args(argv)

    if args.book:
        result = measure_book(args.year, args.month, limit=args.limit)
        if args.json:
            print(json.dumps(result, indent=1))
            return 0
        fe = result["fabric_path"]["electricity"]
        le = result["legacy_path"]["electricity"]
        print(f"window {result['window']} -- THE BOOK")
        print(f"  {result['priced']} of {result['book_electricity_customers']} electricity "
              f"premises priced, across {result['distinct_cells']} distinct cells")
        if result["not_priced"]:
            print(f"  not priced: {result['not_priced']}")
        print("\nMEAN ABSOLUTE DIFFERENCE IN HALF-HOURLY SHARE (the level divided out)")
        print(f"  fabric path   {fe.get('mean_abs_share_difference')}  over "
              f"{fe.get('n_pairs')} pairs, {fe.get('identical_pairs')} identical")
        print(f"  legacy path   {le.get('mean_abs_share_difference')}  over "
              f"{le.get('n_pairs')} pairs, {le.get('identical_pairs')} identical")
        print("\nCLOSEST PAIR -- the test of 'rescaled copies', which an average cannot see")
        for name, s in (("fabric", fe), ("legacy", le)):
            if s.get("closest_pair"):
                print(f"  {name:8s} {s['closest_pair_distance']:.8f}  "
                      f"{s['closest_pair'][0]} vs {s['closest_pair'][1]}")
                print(f"           near-identical pairs (<1e-4): {s['near_identical_pairs']}"
                      f" of {s['n_pairs']}")
        return 0

    result = measure(args.year, args.month)
    if args.json:
        print(json.dumps(result, indent=1))
        return 0
    fg, fe = result["fabric_path"]["gas"], result["fabric_path"]["electricity"]
    lg = result["legacy_path"]["electricity"]
    print(f"window {result['window']}, cells {','.join(result['cells'])}\n")
    print("MEAN ABSOLUTE DIFFERENCE IN HALF-HOURLY SHARE (the level divided out)")
    print(f"  fabric path, gas          {fg.get('mean_abs_share_difference')}  "
          f"over {fg.get('n_pairs')} pairs, {fg.get('identical_pairs')} identical")
    print(f"  fabric path, electricity  {fe.get('mean_abs_share_difference')}  "
          f"over {fe.get('n_pairs')} pairs, {fe.get('identical_pairs')} identical")
    print(f"  legacy path, electricity  {lg.get('mean_abs_share_difference')}  "
          f"over {lg.get('n_pairs')} pairs, {lg.get('identical_pairs')} identical")
    print("\nCLOSEST PAIR — the test of 'rescaled copies', which an average cannot see")
    for name, s in (("fabric gas", fg), ("fabric elec", fe), ("legacy elec", lg)):
        if s.get("closest_pair"):
            print(f"  {name:12s} {s['closest_pair_distance']:.8f}  "
                  f"{s['closest_pair'][0]} vs {s['closest_pair'][1]}")
            print(f"               near-identical pairs (<1e-4): {s['near_identical_pairs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
