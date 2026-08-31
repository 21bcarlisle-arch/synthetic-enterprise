"""EP13: THE PER-FUEL ORACLE — what the TRUE half-hourly fuel mix reaches, and WHICH fuel carries it.

REUSE: tools/ep13_per_fuel_oracle_bound.py
CLASS: CUSTOM
INDEX: searched "oracle", "bound", "ceiling", "per fuel", "fuel mix", "ablation", "within-day",
       "FUELHH", "dispatch". The three nearest organs are `tools/ep13_biomass_oracle_bound.py`,
       `tools/ep13_input_ceiling.py` and `tools/ep13_peer_bound.py`, and this is none of them.
       The biomass oracle holds ONE fuel's truth and asks what perfect knowledge of it is worth;
       this holds EVERY held fuel's truth at once and then asks which one the answer lives in,
       which is a different question and needs the ablation ladder that file has no place for.
       The input ceiling FITS a function of the model's own inputs (85 minutes, and it may never
       be published); this fits nothing and runs in minutes. The peer bound scores ANOTHER PARTY's
       forecast; this scores METERED TRUTH through a published factor table. It lives in tools/
       beside the other bounds rather than widening `sim/elexon_fuel_outturn`, whose whole design
       is about what grain of each fuel may cross the wall — an instrument that reads every fuel
       at half-hourly grain must not be reachable from the module that rations that grain.

WHY THIS EXISTS
---------------
EP13 has sat at L2 for nine passes on one axis: correlation against NESO's published series,
0.7425 in 2024. Four candidate inputs were retired by measuring their ceiling BEFORE building the
approximation — the biomass outage model, the merit-order programme, post-hoc recalibration and
embedded generation — and every one came back negative. The ninth pass then broke the run of
negatives from the other side: NESO's OWN forecast reproduces NESO's OWN outturn at 0.9711 in
2024, so the target is reproducible and the axis is not measuring the counterparty's noise. That
pass ended by naming its next hypothesis and deliberately not building it:

    NESO forecasts PER FUEL where this model reduces everything to a residual.

That is what this measures. The shipped reconstruction never sees a fuel dispatched: it takes
demand, subtracts renewables, imports and the zero-carbon must-run block, and splits what is left
by a merit order it decides for itself. This instrument hands it the truth instead.

WHAT IT IS, AND THE ONE THING IT IS NOT — THIS IS NOT A CEILING
----------------------------------------------------------------
Every previous oracle on this atom was a CEILING: perfect knowledge of an input bounds every model
that could ever be built on it, so a NEGATIVE ceiling retires the candidate outright. That is how
four candidates died.

THIS ORACLE IS HANDICAPPED, so it does not bound from above and a negative here would retire
nothing. Three terms NESO's published number carries are missing from this arithmetic:

  * EMBEDDED GENERATION — behind-meter solar and wind are invisible to FUELHH, and they are a
    midday-shaped term, i.e. they bite on exactly the within-day axis under measurement;
  * INTERCONNECTORS — FUELHH publishes nine cables and NESO prices each at its own intensity;
    this repo holds no per-cable factor table, so imports are excluded from BOTH numerator and
    denominator rather than guessed at;
  * OIL and OTHER — not in the four caches at all.

All three omissions run the SAME way: they cost the oracle accuracy it could have had. So the
number this produces is an ATTAINMENT FLOOR on what the per-fuel input is worth, not a ceiling on
it. That inversion is why a POSITIVE result here is worth more than a positive ceiling would be —
a handicapped model that still reaches 0.935 has proved the input carries the information, and a
better-equipped one can only do better.

IT IS NOT PUBLISHABLE, and that is structural rather than a matter of taste. It is NESO's own
published factor table applied to metered truth, which is NESO's arithmetic with the hard parts
removed; republishing it as this world's carbon series would make the reconstruction pointless.
`oracle_reaches_the_published_feed` is an AST walk, not a promise.

THE ABLATION LADDER, which is the part that survives every caveat above
-----------------------------------------------------------------------
A single number saying "per-fuel truth is worth +0.19" tells the atom to go find per-fuel data. It
does not say WHICH fuel, and the fuels are not equally observable from outside: coal availability
is an annual fact about steel, gas dispatch is a half-hourly decision.

So each fuel is ablated in turn — its half-hourly series replaced by ITS OWN DAY MEAN, deleting
that fuel's within-day timing and nothing else, with every other fuel left at truth — and the
correlation it costs is what that fuel's timing was worth. This is a fact about the GB grid, not
about the reconstruction, and it holds even if the headline oracle number is dismissed entirely.

THE TAUTOLOGY GUARD, first thing a reader should check
-------------------------------------------------------
NESO's `actual` is itself built from a metered fuel mix through a factor table. If FUELHH were the
same mix and this the same table, the whole measurement would be NESO's arithmetic replayed and
would report ~1.0 by construction — R15's first killer. `oracle_is_not_nesos_arithmetic` publishes
the distance: the share of half hours where the two agree to a gram, and the mean absolute
difference. A replay scores 1.0 and 0 g. The measured values are 0.000 and 11.7–33.1 g, which is
the embedded, interconnector and loss terms above showing up as the gap they are.

FAIL CLOSED ON AN ABSENT FUEL, which the first draft of this did not and it mattered. The four
FUELHH caches do not cover identical half hours (BIOMASS starts later than COAL). A half hour with
no CCGT row is not a half hour with no gas — it is an absent reading, and summing it as zero
deletes the largest carbon term on the system and reports a clean grid. Every fuel in
`HELD_FUELS` must be present or the half hour is refused, and the refusal count is published:
28,813 half hours, 99.6% of them in 2016–17 before the biomass cache begins.

R12. Every number here is a DIAGNOSTIC. Nothing in this file moves a level, changes an exit test,
or is read by the published feed.

Reproduce: `python3 -m tools.ep13_per_fuel_oracle_bound`
        -> `docs/observability/ep13_per_fuel_oracle_bound.json`.
"""

from __future__ import annotations

import ast
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from sim import neso_carbon_intensity as neso

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_DIR / "docs" / "observability" / "ep13_per_fuel_oracle_bound.json"

#: The GB fuels held at half-hourly grain across the four FUELHH caches. EVERY ONE must be present
#: for a half hour to be scored -- see the fail-closed note in the module docstring. Interconnectors
#: are deliberately absent: this repo holds no per-cable factor and a guessed one would be a
#: constant invented to fill a slot.
HELD_FUELS = ("COAL", "CCGT", "OCGT", "BIOMASS", "NUCLEAR", "NPSHYD")

#: The fuels whose within-day timing is worth ablating. The zero-factor fleets are excluded because
#: flattening them moves only the denominator, and WIND is included -- it is the one carbon-relevant
#: series the reconstruction ALREADY has, so it is the reference the other rungs are read against.
ABLATED = ("COAL", "CCGT", "OCGT", "BIOMASS", "WIND")

#: The shuffle seed for the null rung. Fixed so the null is reproducible; its job is to collapse.
NULL_SEED = 20260830

#: A year needs this many scored half hours before it is measured at all. Roughly two weeks. Same
#: bar and same reason as `ep13_peer_bound.MIN_SCORED_HALF_HOURS`.
MIN_SCORED_HALF_HOURS = 600

#: `oracle_is_not_nesos_arithmetic` fails above this share of half hours agreeing to within a gram.
MAX_IDENTICAL_SHARE = 0.10

#: ...and below this mean absolute difference from NESO's published outturn. A replay of NESO's own
#: sum would sit at 0 g. Set an order of magnitude below the measured 11.7-33.1 g so the bar
#: visibly does not carry the result, and far above the 0.5 g that whole-gram publication rounding
#: alone could produce.
MIN_TAUTOLOGY_DISTANCE_G = 2.0

#: How much the oracle must beat its own day mean by before that counts as a within-day advantage.
#: NOT a strict inequality, and the reason is the mutation that survived `ep13_peer_bound`'s first
#: battery: a control comparing two quantities its own named defect makes IDENTICAL reads 1e-16 of
#: floating point as an advantage and passes fail-open. The measured gap is 0.08-0.12.
MIN_WITHIN_DAY_ADVANTAGE = 0.01

#: The ablation ladder DISCRIMINATES or it has named nothing. At least one fuel must cost more than
#: this and at least one must cost less -- a ladder where every rung costs the same is an
#: instrument that cannot answer the question it was built to answer, and it would otherwise pass
#: by reporting six identical numbers.
MIN_ABLATION_SIGNAL = 0.01

#: The held fuels plus wind, over Elexon demand. KEYED TO THE PROPERTY AND NOT TO TODAY'S ANSWER:
#: the bound is wide because GB is a net importer in most years and was a net EXPORTER in 2022, and
#: because embedded generation serves demand this sum cannot see. What it refuses is a denominator
#: that has lost a fleet -- which is the defect that would silently rescale every intensity here.
MIN_GENERATION_OVER_DEMAND = 0.80
MAX_GENERATION_OVER_DEMAND = 1.20


def held_out(date: str) -> bool:
    """EVEN days of the month are scored, ODD days are not.

    Duplicated from `ep13_peer_bound.held_out` rather than imported, for that file's own stated
    reason: this module fits nothing, so it has no leakage to prevent, and it scores on even days
    ONLY so its baseline column is the same population as the other bounds' and the four artefacts
    can be read in one table. That is a shared CONVENTION, not shared machinery.
    """
    return int(date[8:10]) % 2 == 0


def per_fuel_by_period(rows: Iterable[Mapping]) -> dict[tuple[str, int], dict[str, float]]:
    """{(date, period): {fuelType: MW}} from raw FUELHH rows, summed over duplicate publishes."""
    out: dict[tuple[str, int], dict[str, float]] = defaultdict(dict)
    for row in rows:
        generation = row.get("generation")
        if generation is None:
            continue
        key = (row["settlementDate"], row["settlementPeriod"])
        fuel_type = row["fuelType"]
        out[key][fuel_type] = out[key].get(fuel_type, 0.0) + float(generation)
    return dict(out)


def oracle_intensity(
    mix_at: Mapping[str, float],
    wind_mw: float,
    factors: Mapping[str, float],
    *,
    flatten: str | None = None,
    flat_mw: float | None = None,
) -> float | None:
    """gCO2/kWh from the true mix — `None` when ANY held fuel is absent, which is the whole point.

    `flatten`/`flat_mw` substitute one fuel's day-mean MW for its half-hourly value, which is the
    ablation. Wind enters at factor zero and is flattened by passing `flatten="WIND"`.
    """
    numerator = denominator = 0.0
    for fuel_type in HELD_FUELS:
        megawatts = mix_at.get(fuel_type)
        if megawatts is None:
            return None
        if flatten == fuel_type:
            if flat_mw is None:
                return None
            megawatts = flat_mw
        numerator += float(megawatts) * float(factors.get(fuel_type, 0.0))
        denominator += float(megawatts)
    denominator += flat_mw if (flatten == "WIND" and flat_mw is not None) else float(wind_mw)
    if denominator <= 0.0 or numerator <= 0.0:
        return None
    return numerator / denominator


def day_mean(series: Mapping[tuple[str, int], float]) -> dict[tuple[str, int], float]:
    """Every half hour replaced by its own DAY's mean — the within-day axis deleted, nothing else.

    The placebo that separates the two axes this atom is scored on, and the ablation's own
    substitution. A rung that keeps its correlation under this was never carrying within-day
    information; the between-day ordering alone was doing the work.
    """
    totals: dict[str, list[float]] = {}
    for key, value in series.items():
        acc = totals.setdefault(key[0], [0.0, 0.0])
        acc[0] += float(value)
        acc[1] += 1.0
    return {key: totals[key[0]][0] / totals[key[0]][1] for key in series}


def shuffled(
    series: Mapping[tuple[str, int], float],
    keys: Sequence[tuple[str, int]],
    seed: int = NULL_SEED,
) -> dict[tuple[str, int], float]:
    """The same values dealt to different half hours — VALUES preserved exactly, TIMING destroyed,
    so the null tests the axis under measurement rather than the scale of the numbers."""
    ordered = sorted(keys)
    values = [float(series[k]) for k in ordered]
    random.Random(seed).shuffle(values)
    return dict(zip(ordered, values))


def _published_feed_source() -> str:
    return (PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text(encoding="utf-8")


def oracle_is_unreachable_from(source: str) -> bool:
    """True when nothing in `source` imports this module — an AST walk, not a substring search.

    Same walk and same reason as `ep13_input_ceiling.ceiling_is_unreachable_from`. Publishing
    NESO's factor table applied to metered truth as this world's carbon series would import NESO's
    arithmetic wholesale and make the reconstruction pointless; that it cannot happen is checked
    structurally rather than asserted in prose.
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


def build_oracle(
    mix: Mapping[tuple[str, int], Mapping[str, float]],
    wind: Mapping[tuple[str, int], float],
    factors: Mapping[str, float],
) -> tuple[dict[tuple[str, int], float], dict[str, int]]:
    """(oracle grams by half hour, refusals by year) — fail-closed on an incomplete fuel mix."""
    oracle: dict[tuple[str, int], float] = {}
    refused: dict[str, int] = defaultdict(int)
    for key, fuels in mix.items():
        wind_mw = wind.get(key)
        if wind_mw is None:
            refused[key[0][:4]] += 1
            continue
        grams = oracle_intensity(fuels, float(wind_mw), factors)
        if grams is None:
            refused[key[0][:4]] += 1
            continue
        oracle[key] = grams
    return oracle, dict(refused)


def ablation_series(
    year: str,
    fuel_type: str,
    mix: Mapping[tuple[str, int], Mapping[str, float]],
    wind: Mapping[tuple[str, int], float],
    factors: Mapping[str, float],
) -> dict[tuple[str, int], float]:
    """The oracle with ONE fuel's within-day timing deleted and every other fuel left at truth."""
    totals: dict[str, list[float]] = {}
    for key in mix:
        if key[0][:4] != year:
            continue
        megawatts = wind.get(key) if fuel_type == "WIND" else mix[key].get(fuel_type)
        if megawatts is None:
            continue
        acc = totals.setdefault(key[0], [0.0, 0.0])
        acc[0] += float(megawatts)
        acc[1] += 1.0

    flattened: dict[tuple[str, int], float] = {}
    for key, fuels in mix.items():
        if key[0][:4] != year:
            continue
        wind_mw = wind.get(key)
        day = totals.get(key[0])
        if wind_mw is None or day is None or day[1] <= 0.0:
            continue
        grams = oracle_intensity(
            fuels, float(wind_mw), factors, flatten=fuel_type, flat_mw=day[0] / day[1]
        )
        if grams is not None:
            flattened[key] = grams
    return flattened


def measure_year(
    year: str,
    *,
    shipped: Mapping[tuple[str, int], float],
    actual: Mapping[tuple[str, int], float],
    oracle: Mapping[tuple[str, int], float],
    demand: Mapping[tuple[str, int], float],
    mix: Mapping[tuple[str, int], Mapping[str, float]],
    wind: Mapping[tuple[str, int], float],
    factors: Mapping[str, float],
    ablated: Sequence[str] = ABLATED,
) -> dict:
    """Every rung for one year, on the held-out half hours only.

    Every rung is SHAPED by `neso.published_shape` before scoring, because the reconstruction is a
    dimensionless shape and a gram-valued series compared against it would measure the units.
    """
    published = neso.published_shape(actual, demand)
    oracle_shape = neso.published_shape(oracle, demand)
    score_keys = [
        k
        for k in shipped
        if k[0][:4] == year
        and k in published
        and k in oracle_shape
        and held_out(k[0])
        and float(demand.get(k) or 0.0) > 0.0
    ]
    if len(score_keys) < MIN_SCORED_HALF_HOURS:
        raise neso.NesoIntensityUnavailable(
            f"{year} has {len(score_keys)} scored half hours, under the {MIN_SCORED_HALF_HOURS} bar"
        )

    rungs: dict[str, Mapping[tuple[str, int], float]] = {
        "baseline": shipped,
        "oracle": oracle_shape,
        "oracle_day_mean": day_mean(oracle_shape),
        "oracle_shuffled": neso.published_shape(
            shuffled(oracle, sorted(k for k in oracle if k[0][:4] == year)), demand
        ),
        "target_day_mean": day_mean(published),
    }
    for fuel_type in ablated:
        flattened = ablation_series(year, fuel_type, mix, wind, factors)
        if flattened:
            rungs[f"ablate_{fuel_type}"] = neso.published_shape(flattened, demand)

    row: dict[str, object] = {}
    for name, series in rungs.items():
        present = {k: series[k] for k in score_keys if k in series}
        if len(present) < MIN_SCORED_HALF_HOURS:
            continue
        row[name] = neso.compare_shapes(present, published, demand, year)

    # BIT-IDENTICAL, not "within a gram". The question this leg answers is "is this the same series
    # compared with itself", and a tolerance answers "is it close" instead -- which is the headline,
    # not the control. Conflating the two makes an accurate oracle look like a tautology; the
    # mean-absolute-error leg beside it is what carries "systematically close".
    identical = sum(1 for k in score_keys if abs(oracle[k] - actual[k]) < 1e-9)
    row["control_scored_half_hours"] = float(len(score_keys))
    row["control_oracle_identical_share"] = identical / len(score_keys)
    row["control_oracle_mean_abs_error_g"] = sum(
        abs(oracle[k] - actual[k]) for k in score_keys
    ) / len(score_keys)
    row["control_generation_over_demand"] = sum(
        sum(mix[k].get(f, 0.0) for f in HELD_FUELS) + float(wind.get(k) or 0.0)
        for k in score_keys
        if k in mix
    ) / sum(float(demand[k]) for k in score_keys)

    correlations = {
        name: float(value["correlation"])
        for name, value in row.items()
        if isinstance(value, dict) and value.get("correlation") is not None
    }
    row["oracle_over_baseline"] = correlations["oracle"] - correlations["baseline"]
    costs = {
        fuel_type: correlations["oracle"] - correlations[f"ablate_{fuel_type}"]
        for fuel_type in ablated
        if f"ablate_{fuel_type}" in correlations
    }
    row["ablation_cost"] = costs
    row["dominant_within_day_fuel"] = max(costs, key=lambda f: costs[f]) if costs else None
    return row


def verdicts(row: Mapping[str, object]) -> dict[str, bool]:
    """The controls, computed from the row that was just published rather than only asserted in a
    test — a verdict that lives only in another process is one a reader has to take on trust."""

    def corr(name: str) -> float:
        return float(row[name]["correlation"])  # type: ignore[index]

    oracle = corr("oracle")
    costs: Mapping[str, float] = row["ablation_cost"]  # type: ignore[assignment]
    coverage = float(row["control_generation_over_demand"])  # type: ignore[arg-type]
    return {
        # CONTROL 1, TAUTOLOGY. NESO's outturn is ITSELF a metered fuel mix through a factor table.
        # If this were the same mix and the same table the measurement would be NESO's arithmetic
        # replayed and would report ~1.0 by construction. Check this before reading any number
        # below it: if it fails, none of them mean anything.
        "oracle_is_not_nesos_arithmetic": (
            float(row["control_oracle_identical_share"]) < MAX_IDENTICAL_SHARE  # type: ignore[arg-type]
            and float(row["control_oracle_mean_abs_error_g"]) > MIN_TAUTOLOGY_DISTANCE_G  # type: ignore[arg-type]
        ),
        # CONTROL 2, the advantage is WITHIN-DAY. Deleting the within-day variation from the oracle
        # must cost it MATERIALLY, or the between-day ordering was doing the work and the number
        # says nothing about the axis holding this level. See MIN_WITHIN_DAY_ADVANTAGE for why
        # this is not a strict inequality.
        "oracle_beats_its_own_day_mean": oracle - corr("oracle_day_mean")
        > MIN_WITHIN_DAY_ADVANTAGE,
        # CONTROL 3, the NULL must collapse. One value per scored half hour, so the effective
        # sample behind a shuffled correlation is the half-hour count and the threshold is derived
        # from it rather than chosen.
        "null_collapses": abs(corr("oracle_shuffled"))
        < 3.0 / (float(row["control_scored_half_hours"]) ** 0.5),  # type: ignore[arg-type]
        # CONTROL 4, the DENOMINATOR still has every fleet in it. Keyed to the property -- a sum of
        # generation is near demand -- and not to today's ratio, which legitimately exceeds 1.0 in
        # a net-export year. What it refuses is a lost fleet silently rescaling every intensity.
        "fuel_coverage_is_plausible": MIN_GENERATION_OVER_DEMAND
        < coverage
        < MAX_GENERATION_OVER_DEMAND,
        # CONTROL 5, the ablation ladder DISCRIMINATES. Some fuel's timing must matter and some
        # fuel's must not. A ladder whose rungs all cost the same has named nothing, and would
        # otherwise pass by reporting five identical numbers -- the fail-open shape of a control
        # that only checks its own output exists.
        "ablation_ladder_discriminates": bool(costs)
        and max(costs.values()) > MIN_ABLATION_SIGNAL
        and min(costs.values()) < MIN_ABLATION_SIGNAL,
        # REPORTED, not a control: whether perfect per-fuel knowledge clears the shipped
        # reconstruction on the atom's own axis.
        "oracle_exceeds_baseline": oracle > corr("baseline"),
    }


def measure() -> dict:
    """Every year the caches share. Loads the real caches; fits nothing."""
    from sim import elexon_fuel_outturn as fuel
    from sim.elexon_fuel_outturn import NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH as FACTORS
    from sim.generation_demand_history import aggregate_renewable_generation
    from tools.generate_grid_intensity_feed import (
        AGWS_CACHE,
        DEMAND_CACHE,
        aggregate_demand,
        fuel_mix,
    )

    demand = aggregate_demand(json.loads(Path(DEMAND_CACHE).read_text(encoding="utf-8")))
    wind = aggregate_renewable_generation(
        json.loads(Path(AGWS_CACHE).read_text(encoding="utf-8"))
    )

    mix: dict[tuple[str, int], dict[str, float]] = defaultdict(dict)
    for loader in (
        fuel.load_cached,
        fuel.load_cached_thermal,
        fuel.load_cached_zero_carbon_must_run,
        fuel.load_cached_biomass,
    ):
        for key, fuels in per_fuel_by_period(loader()).items():
            mix[key].update(fuels)

    (imports, coal_capacity, _coverage, thermal_floors, must_run, _mrc, _envelope) = fuel_mix()

    # THE BASELINE IS RE-MEASURED HERE AND NOT QUOTED from a sibling artefact. A cited baseline can
    # come from a different run than the one it is being compared against, and the whole value of
    # this artefact is that every column in it is one process.
    from sim import grid_carbon_intensity as gci

    shipped = gci.build_shape(
        demand,
        wind,
        imports_by_period=imports,
        coal_capacity_by_year=coal_capacity,
        thermal_floor_by_year={y: r["floor_mw"] for y, r in thermal_floors.items()},
        zero_carbon_must_run_by_period=must_run,
        biomass_envelope_by_year=None,
    )

    ceiling = neso._physical_ceiling_g_co2_per_kwh()
    parsed = neso.to_settlement_periods(neso.load_cached())
    actual = {
        key: float(entry["actual"])
        for key, entry in parsed.items()
        if entry.get("actual") is not None and float(entry["actual"]) <= ceiling
    }

    oracle, refused = build_oracle(mix, wind, FACTORS)

    years = sorted({k[0][:4] for k in oracle} & {k[0][:4] for k in actual} & {k[0][:4] for k in shipped})
    rows: dict[str, dict] = {}
    for year in years:
        try:
            row = measure_year(
                year,
                shipped=shipped,
                actual=actual,
                oracle=oracle,
                demand=demand,
                mix=mix,
                wind=wind,
                factors=FACTORS,
            )
        except (neso.NesoIntensityUnavailable, ValueError, KeyError):
            continue
        row["controls"] = verdicts(row)
        rows[year] = row

    return {
        "measured_from": "sim/cache (Elexon FUELHH per fuel + AGWS wind + demand; NESO outturn)",
        "basis": neso.PUBLISHED_BASIS,
        "split": "scored on EVEN days of the month -- the same population the other EP13 bounds score",
        "held_fuels": list(HELD_FUELS),
        "factors_g_co2_per_kwh": "NESO's own published table, sim.elexon_fuel_outturn",
        "physical_ceiling_g_co2_per_kwh": ceiling,
        "half_hours_refused_as_incomplete": refused,
        "rungs": {
            "baseline": "build_shape as shipped -- where the atom is",
            "oracle": "the TRUE half-hourly fuel mix through NESO's own factor table",
            "oracle_day_mean": "the oracle with its within-day variation deleted -- CONTROL",
            "oracle_shuffled": "the oracle dealt to other half hours -- NULL, must collapse",
            "target_day_mean": "the outturn's own day mean -- hindsight, between-day axis only",
            "ablate_FUEL": "the oracle with ONE fuel flattened to its day mean -- the LADDER",
        },
        "this_is_not_a_ceiling": (
            "HANDICAPPED. Embedded generation, interconnectors, OIL and OTHER are all missing from "
            "this arithmetic and all three omissions cost the oracle accuracy. So this is an "
            "ATTAINMENT FLOOR on what the per-fuel input is worth, NOT a ceiling on it -- a "
            "negative here would retire nothing, and a positive is stronger than a ceiling's would "
            "be. NOT PUBLISHABLE: it is NESO's factor table on metered truth."
        ),
        "oracle_reaches_the_published_feed": not oracle_is_unreachable_from(_published_feed_source()),
        "years": rows,
    }


def main(argv: list[str] | None = None) -> int:
    data = measure()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=1, default=str) + "\n", encoding="utf-8")
    print("year     n  baseline  ORACLE  o_daymean   null  gen/dem  MAEg  | " + "  ".join(
        f"ablate_{f}" for f in ABLATED) + "  dominant")
    for year, row in sorted(data["years"].items()):
        controls = row["controls"]
        costs = row["ablation_cost"]
        print(
            f"{year} {int(row['control_scored_half_hours']):5d} "
            f"{row['baseline']['correlation']:8.4f} "
            f"{row['oracle']['correlation']:7.4f} "
            f"{row['oracle_day_mean']['correlation']:10.4f} "
            f"{row['oracle_shuffled']['correlation']:6.3f} "
            f"{row['control_generation_over_demand']:8.3f} "
            f"{row['control_oracle_mean_abs_error_g']:5.1f}  | "
            + "  ".join(f"{-costs.get(f, float('nan')):+9.4f}" for f in ABLATED)
            + f"  {row['dominant_within_day_fuel']}"
            + "  tautology_ok=" + ("Y" if controls["oracle_is_not_nesos_arithmetic"] else "N")
            + " within_day=" + ("Y" if controls["oracle_beats_its_own_day_mean"] else "N")
            + " null=" + ("Y" if controls["null_collapses"] else "N")
            + " coverage=" + ("Y" if controls["fuel_coverage_is_plausible"] else "N")
            + " ladder=" + ("Y" if controls["ablation_ladder_discriminates"] else "N")
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
