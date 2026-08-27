"""EP13: the BIOMASS ORACLE BOUND — how much any outage model could possibly buy.

REUSE: tools/ep13_biomass_oracle_bound.py
CLASS: CUSTOM
INDEX: searched "oracle", "bound", "biomass", "outage", "upper bound", "counterfactual",
       "treatment". `tools/generate_grid_intensity_feed.py` is the nearest organ and this is
       deliberately NOT part of it: that module PUBLISHES and this one may not, because the
       treatment it measures is one the published feed is forbidden to use. Keeping them in
       separate files is what makes `test_the_oracle_cannot_reach_the_published_feed` a
       structural check rather than a promise. Every input is loaded through
       `generate_grid_intensity_feed.fuel_mix` and `sim/elexon_fuel_outturn.py` rather than
       re-read here, so the measurement runs against the caches the feed itself runs against.

WHY THIS EXISTS
---------------
`docs/design/maturity_map.yaml` named EP13's next gap, on 2026-08-26, as an OUTAGE MODEL: the
biomass fleet's low readings are outages rather than dispatch, so the residual can only explain
2.6-33.5% of its variance and a tidier percentile will not help.

Before building one, measure its CEILING. An outage model is an APPROXIMATION to knowing what the
biomass fleet was actually able to do in each half hour. So hand the dispatch that knowledge
EXACTLY — the metered half-hourly outturn, pinned, no freedom left — and see how far the gap to
NESO's published series closes. Whatever the oracle cannot buy, no approximation to it can buy.

THIS TREATMENT MAY NEVER BE PUBLISHED, and that is the whole reason the bound is worth taking
this way. NESO prices biomass at 120 gCO2/kWh, so a metered biomass reading is an emissions term
and handing it across the wall makes this NESO's arithmetic with a different cache — the
condition `sim/elexon_fuel_outturn.py` states and tests for nuclear and NPSHYD, which biomass
fails. An illegal treatment is still a legitimate BOUND, because a bound is a fact about what is
knowable and not a route to a number. `test_the_oracle_cannot_reach_the_published_feed` is what
keeps that distinction structural.

THE THREE TREATMENTS, one process, identical caches:

  flat      biomass held at `MUST_RUN_BIOMASS_MW` (2,400 MW) every half hour.
            THIS IS THE PUBLISHED SERIES — `BIOMASS_DISPATCH_WIRED` is False.
  envelope  the built-but-OFF annual envelope: the fleet's demonstrated maximum and minimum
            that year, with the dispatch choosing where inside it to sit.
  oracle    biomass pinned to its ACTUAL published half-hourly outturn.

TWO CONTROLS, both computed on every run and both mutation-proven in the test file, because the
two ways this measurement could report a comfortable falsehood are exactly opposite:

  1. `flat` MUST reproduce the shipped `build_shape` on every shape diagnostic. If the
     measurement route differs from the publishing route, the comparison is between two
     codepaths rather than between two treatments. (The two renormalisation divisors are
     excluded BY NAME: `build_shape` hands `compare_shapes` a series already normalised to 1.0
     and this route hands it raw t/MWh, so those two differ by construction and nothing else is
     allowed to.)
  2. The oracle MUST BITE. A treatment that changed no rate would report "perfect knowledge does
     not help" while actually reporting "perfect knowledge was never applied", and the shape
     diagnostics cannot tell those apart (R15 fail-silent).
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Mapping

from sim import grid_carbon_intensity as gci
from sim import neso_carbon_intensity as neso

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_DIR / "docs" / "observability" / "ep13_biomass_oracle_bound.json"

TREATMENTS = ("flat", "envelope", "oracle")

#: The two keys `compare_shapes` returns that differ between the measurement route and the
#: publishing route FOR A REASON THAT IS NOT A DEFECT, and the only two control 1 may skip.
_DIVISOR_KEYS = frozenset(
    {"reconstructed_renormalisation_divisor", "published_renormalisation_divisor"}
)


def treatment_rates(
    treatment: str,
    *,
    demand_by_period: Mapping[tuple[str, int], float],
    renewables_by_period: Mapping[tuple[str, int], float],
    imports_by_period: Mapping[tuple[str, int], tuple[float, float]],
    coal_capacity_by_year: Mapping[int, float],
    thermal_floor_by_year: Mapping[int, float],
    zero_carbon_must_run_by_period: Mapping[tuple[str, int], float],
    biomass_envelope_by_year: Mapping[int, Mapping[str, float]],
    biomass_mw_by_period: Mapping[tuple[str, int], float],
) -> dict[tuple[str, int], float]:
    """{(date, period): ABSOLUTE t/MWh} under one biomass treatment.

    Absolute and un-normalised, and that is deliberate rather than a shortcut: `compare_shapes`
    renormalises whatever it is handed to a demand-weighted mean over the half hours the two
    series share, so a per-year scalar here would be divided straight back out. Skipping the
    normalisation keeps this function's only difference from `build_shape` the ONE parameter
    under test, which is what makes control 1 meaningful.

    The oracle sets `biomass_floor_mw == biomass_capacity_mw == the metered half hour`, which
    leaves `emissions_rate_t_per_mwh`'s clamp no freedom: biomass is exactly what GB's fleet
    produced. A half hour with NO biomass reading falls back to the flat block rather than to
    zero — an absent reading is not a fleet that stopped (R15 fail-open), and it is the same
    call `build_shape` makes for an absent nuclear reading one layer down.
    """
    if treatment not in TREATMENTS:
        raise ValueError(f"unknown treatment {treatment!r}; expected one of {TREATMENTS}")
    out: dict[tuple[str, int], float] = {}
    for key, demand_mw in demand_by_period.items():
        renewable_mw = renewables_by_period.get(key)
        if renewable_mw is None or not demand_mw or float(demand_mw) <= 0.0:
            continue
        year = int(key[0][:4])
        import_mw, import_rate = imports_by_period.get(key, (0.0, 0.0))
        zero_carbon_mw = zero_carbon_must_run_by_period.get(key)
        if treatment == "flat":
            capacity = floor = None
        elif treatment == "envelope":
            envelope = biomass_envelope_by_year.get(year)
            capacity = None if envelope is None else float(envelope["capacity_mw"])
            floor = None if envelope is None else float(envelope["floor_mw"])
        else:
            actual = biomass_mw_by_period.get(key)
            capacity = floor = None if actual is None else float(actual)
        try:
            out[key] = gci.emissions_rate_t_per_mwh(
                float(demand_mw),
                float(renewable_mw),
                year,
                import_mw=float(import_mw),
                import_rate_t_per_mwh=float(import_rate),
                coal_capacity_mw=float(coal_capacity_by_year.get(year, 0.0)),
                thermal_floor_mw=float(thermal_floor_by_year.get(year, 0.0)),
                zero_carbon_must_run_mw=(
                    None if zero_carbon_mw is None else float(zero_carbon_mw)
                ),
                biomass_capacity_mw=capacity,
                biomass_floor_mw=floor,
            )
        except (gci.ShapeUnavailable, ValueError, KeyError):
            continue
    return out


def route_agreement(
    measured_flat: Mapping[str, float | None],
    shipped: Mapping[str, float | None],
) -> float:
    """CONTROL 1, as a number: the largest disagreement between the two routes' diagnostics.

    Returned rather than asserted, so the run PUBLISHES how well its own control held instead
    of a caller having to take a passing test's word for it in a different process.
    """
    return max(
        abs((measured_flat.get(k) or 0.0) - (shipped.get(k) or 0.0))
        for k in shipped
        if k not in _DIVISOR_KEYS
    )


def treatment_bite(
    baseline: Mapping[tuple[str, int], float],
    treated: Mapping[tuple[str, int], float],
) -> dict[str, float]:
    """CONTROL 2, as numbers: how hard a treatment actually moved the emissions rate.

    A `share_of_half_hours_moved` of zero means the treatment was never applied, whatever the
    shape diagnostics went on to say about it.
    """
    common = [k for k in baseline if k in treated]
    if not common:
        raise ValueError("the two rate series share no half hour, so no bite can be measured")
    mean_baseline = sum(baseline[k] for k in common) / len(common)
    if mean_baseline <= 0.0:
        raise ValueError("the baseline series has a non-positive mean, so bite has no scale")
    changes = [abs(treated[k] - baseline[k]) for k in common]
    return {
        "half_hours": float(len(common)),
        "mean_abs_rate_change_pct": 100.0 * (sum(changes) / len(changes)) / mean_baseline,
        "max_abs_rate_change_pct": 100.0 * max(changes) / mean_baseline,
        "share_of_half_hours_moved": sum(
            1 for k in common if abs(treated[k] - baseline[k]) > 0.01 * baseline[k]
        )
        / len(common),
    }


def _published_feed_source() -> str:
    return (PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text(encoding="utf-8")


def oracle_is_unreachable_from(source: str) -> bool:
    """True when nothing in `source` imports this module — an AST walk, not a substring search.

    A substring search would be satisfied by this module's own name appearing in a comment, and
    would be defeated by an import written any way but the one it looked for. The walk asks the
    parser instead.
    """
    tree = ast.parse(source)
    mine = Path(__file__).stem
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[-1] == mine for alias in node.names):
                return False
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[-1] == mine:
                return False
            if any(alias.name == mine for alias in node.names):
                return False
    return True


def measure() -> dict:
    """The bound, over every year the two series share. Loads the real caches."""
    from sim import elexon_fuel_outturn as fuel
    from tools.generate_grid_intensity_feed import (
        AGWS_CACHE,
        DEMAND_CACHE,
        aggregate_demand,
        aggregate_renewable_generation,
        fuel_mix,
    )

    demand = aggregate_demand(json.loads(Path(DEMAND_CACHE).read_text(encoding="utf-8")))
    renewables = aggregate_renewable_generation(
        json.loads(Path(AGWS_CACHE).read_text(encoding="utf-8"))
    )
    (imports, coal_capacity, _coverage, thermal_floors, must_run, _mrc, envelope) = fuel_mix()
    thermal_floor = {y: r["floor_mw"] for y, r in thermal_floors.items()}
    biomass_mw = fuel.biomass_by_period(fuel.load_cached_biomass())
    published = neso.actual_by_period(neso.to_settlement_periods(neso.load_cached()))

    inputs = dict(
        demand_by_period=demand,
        renewables_by_period=renewables,
        imports_by_period=imports,
        coal_capacity_by_year=coal_capacity,
        thermal_floor_by_year=thermal_floor,
        zero_carbon_must_run_by_period=must_run,
        biomass_envelope_by_year=envelope,
        biomass_mw_by_period=biomass_mw,
    )
    rates = {name: treatment_rates(name, **inputs) for name in TREATMENTS}
    shipped = gci.build_shape(
        demand,
        renewables,
        imports_by_period=imports,
        coal_capacity_by_year=coal_capacity,
        thermal_floor_by_year=thermal_floor,
        zero_carbon_must_run_by_period=must_run,
        biomass_envelope_by_year=None,
    )

    years = sorted({k[0][:4] for k in published} & {k[0][:4] for k in rates["flat"]})
    rows: dict[str, dict] = {}
    for year in years:
        try:
            reference = neso.compare_shapes(shipped, published, demand, year)
        except neso.NesoIntensityUnavailable:
            continue
        row: dict[str, object] = {"shipped_build_shape": reference}
        for name in TREATMENTS:
            row[name] = neso.compare_shapes(rates[name], published, demand, year)
        row["control_route_agreement"] = route_agreement(row["flat"], reference)
        row["control_oracle_bite"] = treatment_bite(
            {k: v for k, v in rates["flat"].items() if k[0][:4] == year},
            {k: v for k, v in rates["oracle"].items() if k[0][:4] == year},
        )
        rows[year] = row
    return {
        "measured_from": "sim/cache (Elexon FUELHH + demand + AGWS, NESO Carbon Intensity)",
        "basis": neso.PUBLISHED_BASIS,
        "treatments": {
            "flat": f"biomass held at {gci.MUST_RUN_BIOMASS_MW:.0f} MW -- THE PUBLISHED SERIES",
            "envelope": "the annual demonstrated envelope (built, BIOMASS_DISPATCH_WIRED False)",
            "oracle": "biomass pinned to its metered half-hourly outturn -- NOT PUBLISHABLE",
        },
        "oracle_reaches_the_published_feed": not oracle_is_unreachable_from(
            _published_feed_source()
        ),
        "years": rows,
    }


def main(argv: list[str] | None = None) -> int:
    data = measure()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    for year, row in sorted(data["years"].items()):
        print(
            f"{year} n={int(row['flat']['half_hours']):6d} "
            f"corr flat={row['flat']['correlation']:.4f} "
            f"env={row['envelope']['correlation']:.4f} "
            f"ORACLE={row['oracle']['correlation']:.4f} "
            f"| control route={row['control_route_agreement']:.1e} "
            f"bite={row['control_oracle_bite']['share_of_half_hours_moved']:.2f}"
        )
    print(f"wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
