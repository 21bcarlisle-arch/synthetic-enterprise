"""EP13: THE CCGT SWAP CEILING — what perfect within-day gas timing is worth INSIDE the shipped model.

REUSE: tools/ep13_ccgt_swap_ceiling.py
CLASS: CUSTOM
INDEX: searched "ccgt", "swap", "ceiling", "within-day", "dispatch", "counterfactual". Thirty-nine
       rows match "dispatch" and thirty-two match "ceiling"; the three that are near neighbours are
       `tools/ep13_input_ceiling.py`, `tools/ep13_per_fuel_oracle_bound.py` and
       `tools/ep13_biomass_oracle_bound.py`, and this is none of them. The input ceiling FITS the
       best possible function of the model's OWN inputs and takes 85 minutes; this fits nothing and
       substitutes an input the model does not have. The per-fuel oracle REPLACES THE WHOLE
       ARITHMETIC -- NESO's factor table over the metered mix -- which is precisely why its +0.193
       cannot be attributed and why this file exists. The biomass oracle holds one fuel's truth but
       hands it to the same dispatch as a CAPACITY, one scalar a year, where this hands over a
       half-hourly series and must therefore live outside `sim/` for the reason
       `sim/elexon_fuel_outturn.py` states: a module that can reach the metered gas series is one
       edit away from being NESO's arithmetic with a different cache. `per_fuel_by_period`,
       `day_mean` and `held_out` are IMPORTED from the per-fuel oracle rather than re-typed: the
       parse, the placebo and the even-day split are the same machinery and the four EP13 bounds
       have to be readable in one table.

WHY THIS EXISTS
---------------
§14 of the frame doc measured the true half-hourly FUELHH mix through NESO's own factor table at
0.9352 in 2024 against the shipped reconstruction's 0.7425, put the within-day information almost
entirely in CCGT, and named L3's build target: A PUBLISHABLE PROXY FOR WITHIN-DAY CCGT DISPATCH.

THAT +0.193 IS NOT ATTRIBUTABLE TO CCGT TIMING, and the rule is this project's own: when a result
moves and more than one thing changed, you cannot attribute it. The oracle changed the factor
mapping, the denominator, the fuel coverage, the must-run block, coal's dispatch and the CCGT
efficiency band all at once, and dropped imports from both sides. So the number that would SIZE the
named build target -- what perfect within-day gas timing is worth INSIDE THE SHIPPED
RECONSTRUCTION -- had never been measured. This is the one-variable version.

`emissions_rate_t_per_mwh` is re-implemented here line for line with ONE override point, at
`ccgt_mw`. Everything upstream and downstream of that line is the shipped arithmetic, and
`reimplementation_reproduces_the_shipped_shape` proves it to floating point with the override off.
Read that control before any number below it: without it these rungs measure a second model.

WHAT IT IS, AND THE INVERSION FROM §14 — THIS IS A CEILING
-----------------------------------------------------------
§14's oracle was HANDICAPPED (no embedded generation, no interconnectors, no OIL or OTHER), so it
bounded the per-fuel input from BELOW and a negative would have retired nothing. This instrument
hands the shipped model PERFECT knowledge of the exact quantity a proxy would approximate and
changes nothing else, so no build of that class can beat it. A negative here RETIRES THE NAMED
BUILD TARGET, which is what a ceiling is for and what a floor cannot do.

UP TO ERROR CANCELLATION, which is the standing caveat on every oracle on this atom and is stated
rather than buried: an imperfect proxy whose errors happened to offset the model's other errors
could score above this ceiling. A build that does is fitting the residual, not modelling gas.

THE FIVE RUNGS, and why the primary one is not the obvious one
---------------------------------------------------------------
The build target is within-day TIMING. The shipped model's residual already decides the daily LEVEL
of gas, so a rung that substitutes raw metered CCGT changes two things again and reproduces the
attribution defect one layer down. The primary rung therefore keeps the model's own day mean and
imports only truth's within-day DEVIATIONS -- the exact inverse of §14's ablation, which replaced a
fuel by its day mean and deleted them.

  * `ccgt_timing`          model's day mean + truth's within-day deviations. THE CEILING, and the
                           only rung that is one: it preserves the model's own day total exactly,
                           so the half hour is still met by the same energy.
  * `ccgt_level`           truth's day mean + the model's own within-day deviations. The exact
                           COMPLEMENT, added on the second draft.
  * `ccgt_full`            raw metered CCGT. Level and timing at once.
  * `ccgt_day_mean`        truth's day mean, FLAT inside the day. THE DESTRUCTION RUNG, not a
                           candidate build: it deletes within-day gas variation entirely, so what
                           it costs is what that variation is worth IN TOTAL -- the scale the
                           ceiling has to be read against.
  * `ccgt_timing_shuffled` truth's within-day profile dealt to the WRONG days. THE NULL: it
                           preserves every value and the whole substitution machinery and destroys
                           only the correct timing, so a gain here would mean the rungs are
                           measuring the act of substituting rather than what was substituted.

ONLY `ccgt_timing` IS A CEILING, AND THE OTHER THREE ARE DIAGNOSTICS. `ccgt_timing` is day-total
preserving by construction, so the substitution leaves the model's energy balance where it found
it. `ccgt_level` and `ccgt_full` move the daily gas total without re-deciding the residual's other
terms, so the half hour is met by more or less energy than its demand and part of what they report
is that disturbance. They point at an axis; they do not bound it. Said here rather than in a
footnote because the largest number in this artefact is one of them.

FAIL CLOSED ON AN ABSENT GAS READING, which is §14's lesson taken forward rather than re-learned. A
half hour with no CCGT row is not a half hour with no gas; it is no reading, and substituting zero
deletes the largest carbon term on the system and reports a clean grid. Such half hours are refused
from EVERY rung including the baseline, so all five score the identical population and the
comparison is not partly a coverage difference.

THE CLAMP IS COUNTED, NOT ASSUMED HARMLESS. Truth's deviations added to a small modelled day mean
go negative in quiet half hours, and gas cannot be negative; the shipped line `min(thermal_mw,
CCGT_CAPACITY_MW)` bounds it above. Both clamps are applied and both counts are published, because
a rung that clamps often is partly measuring the clamp.

R12. Every number here is a DIAGNOSTIC. Nothing in this file moves a level, changes an exit test, or
is read by the published feed -- `ceiling_reaches_the_published_feed` is an AST walk over
`tools/generate_grid_intensity_feed.py`, not a promise.

Reproduce: `python3 -m tools.ep13_ccgt_swap_ceiling`
        -> `docs/observability/ep13_ccgt_swap_ceiling.json`.
"""

from __future__ import annotations

import ast
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Sequence

from sim import grid_carbon_intensity as gci
from sim import neso_carbon_intensity as neso
from tools.ep13_per_fuel_oracle_bound import day_mean, held_out, per_fuel_by_period

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_DIR / "docs" / "observability" / "ep13_ccgt_swap_ceiling.json"

#: The one fuel this instrument substitutes. Named rather than parameterised: the ablation ladder of
#: §14 already answered "which fuel", and a knob here would invite re-running until a fuel scores.
SWAPPED_FUEL = "CCGT"

#: The shuffle seed for the null rung. Fixed so the null is reproducible; its job is to collapse.
NULL_SEED = 20260831

#: A year needs this many scored half hours before it is measured at all. The same bar and the same
#: reason as `ep13_per_fuel_oracle_bound.MIN_SCORED_HALF_HOURS` -- roughly two weeks.
MIN_SCORED_HALF_HOURS = 600

#: The re-implementation must reproduce `gci.build_shape`'s shape, on the same population, to
#: better than this. NOT a tolerance on "close": it is the same arithmetic on the same inputs, so
#: the only thing between the two is float association order. A loose bar here would let a
#: genuinely different model pass as the shipped one, and every rung below would then be measuring
#: that difference rather than the substitution.
MAX_REIMPLEMENTATION_DRIFT = 1e-12

#: How much a rung must beat the baseline by before that counts as a gain. The mutation that
#: survived `ep13_peer_bound`'s first battery is why this is not a strict inequality: a control
#: comparing two quantities its own named defect makes IDENTICAL reads 1e-16 of floating point as an
#: advantage and passes fail-open.
MIN_MATERIAL_GAIN = 0.01

#: Correct timing must clear SCRAMBLED timing by this, or the rungs are not measuring timing. Set
#: an order of magnitude below the measured 0.24-0.27 gap so the bar visibly does not carry the
#: result, and above the largest gain any rung reports so it cannot be met by the gain alone.
MIN_NULL_DISCRIMINATION = 0.05

#: The substituted series must actually differ from the model's own, or a zero gain is
#: uninterpretable -- it would be equally consistent with "gas timing is worth nothing" and with
#: "the substitution was a no-op". Mean absolute difference, MW, across the scored half hours. Set
#: two orders of magnitude below the measured gap so the bar visibly does not carry the result.
MIN_SUBSTITUTION_DISTANCE_MW = 100.0

#: Above this share of clamped half hours the timing rung is partly measuring the clamp rather than
#: the timing, and its reading is refused rather than footnoted.
MAX_CLAMPED_SHARE = 0.25


def dispatch_rate(
    demand_mw: float,
    renewable_generation_mw: float,
    year: int,
    *,
    import_mw: float = 0.0,
    import_rate_t_per_mwh: float = 0.0,
    coal_capacity_mw: float = 0.0,
    thermal_floor_mw: float = 0.0,
    zero_carbon_must_run_mw: float | None = None,
    biomass_capacity_mw: float | None = None,
    biomass_floor_mw: float | None = None,
    ccgt_mw_override: float | None = None,
) -> tuple[float, float, bool, bool]:
    """`gci.emissions_rate_t_per_mwh`, line for line, with ONE override point at `ccgt_mw`.

    Returns `(rate, implied_ccgt_mw, clamped_low, clamped_high)` -- the rate the shipped function
    would return, the gas dispatch the shipped merit order DECIDED for this half hour (which is the
    quantity a publishable proxy would replace, and which the shipped function does not expose), and
    whether the override hit either bound.

    THE OVERRIDE MOVES ONE TERM AND NOT THE MERIT ORDER. `above_ccgt_mw`, and therefore coal and the
    peaker band, are computed from the residual exactly as shipped and are NOT re-decided around the
    substituted gas. That is what makes this one variable rather than two, and it is deliberate: a
    version that re-balanced the stack would be a second dispatch model and its result would be
    attributable to neither the substitution nor the rebalance.

    WHY THIS IS A COPY AND NOT A CALL. The shipped function returns one float and takes no override,
    and widening its signature to accept a half-hourly gas series would put a route to the metered
    mix inside `sim/` -- the one thing `sim/elexon_fuel_outturn.py` draws its line to prevent. The
    copy is held to the original by `reimplementation_reproduces_the_shipped_shape`, which compares
    RATES rather than shapes so no normalisation can hide a difference.
    """
    y = gci._year_of(int(year))
    worst_eff, best_eff = gci._ccgt_efficiency_band(y)
    demand_mw = float(demand_mw)
    if demand_mw <= 0.0:
        raise gci.ShapeUnavailable("a half hour with no demand has no emissions rate")

    import_mw = min(max(0.0, float(import_mw)), demand_mw)
    residual_mw = demand_mw - float(renewable_generation_mw) - import_mw
    zero_carbon_mw = (
        gci.MUST_RUN_ZERO_CARBON_MW
        if zero_carbon_must_run_mw is None
        else max(0.0, float(zero_carbon_must_run_mw))
    )
    biomass_capacity = (
        gci.MUST_RUN_BIOMASS_MW
        if biomass_capacity_mw is None
        else max(0.0, float(biomass_capacity_mw))
    )
    biomass_floor = (
        biomass_capacity
        if biomass_floor_mw is None
        else min(max(0.0, float(biomass_floor_mw)), biomass_capacity)
    )
    biomass_mw = min(max(residual_mw - zero_carbon_mw, biomass_floor), biomass_capacity)

    must_run_capacity_mw = biomass_mw + zero_carbon_mw
    must_run_mw = min(demand_mw, must_run_capacity_mw)
    thermal_mw = max(0.0, residual_mw - must_run_capacity_mw)
    floor_mw = min(max(0.0, float(thermal_floor_mw)), max(0.0, demand_mw - must_run_mw))
    thermal_mw = max(thermal_mw, floor_mw)

    implied_ccgt_mw = min(thermal_mw, gci.CCGT_CAPACITY_MW)
    ccgt_mw = implied_ccgt_mw
    clamped_low = clamped_high = False
    if ccgt_mw_override is not None:
        raw = float(ccgt_mw_override)
        clamped_low = raw < 0.0
        clamped_high = raw > gci.CCGT_CAPACITY_MW
        ccgt_mw = min(max(0.0, raw), gci.CCGT_CAPACITY_MW)

    above_ccgt_mw = max(0.0, thermal_mw - gci.CCGT_CAPACITY_MW)
    coal_mw = min(above_ccgt_mw, max(0.0, float(coal_capacity_mw)))
    peaker_mw = max(0.0, above_ccgt_mw - coal_mw)
    peaker_mw = min(
        peaker_mw,
        max(0.0, gci.TOTAL_DISPATCHABLE_MW - gci.MUST_RUN_FLOOR_MW - gci.CCGT_CAPACITY_MW),
    )

    load_fraction = (ccgt_mw / gci.CCGT_CAPACITY_MW) if gci.CCGT_CAPACITY_MW > 0 else 0.0
    mean_dispatched_eff = best_eff - (best_eff - worst_eff) * load_fraction / 2.0

    biomass_served_mw = (
        biomass_mw * (must_run_mw / must_run_capacity_mw) if must_run_capacity_mw > 0.0 else 0.0
    )
    tonnes = (
        biomass_served_mw * (gci.BIOMASS_G_CO2_PER_KWH / 1000.0)
        + import_mw * max(0.0, float(import_rate_t_per_mwh))
        + ccgt_mw * (gci.EF_GAS_TCO2_PER_MWH_TH / mean_dispatched_eff)
        + coal_mw * gci.EF_COAL_TCO2_PER_MWH_E_BY_YEAR[y]
        + peaker_mw * (gci.EF_GAS_TCO2_PER_MWH_TH / gci.OCGT_REFERENCE_EFFICIENCY)
    )
    return tonnes / demand_mw, implied_ccgt_mw, clamped_low, clamped_high


def build_rates(
    demand_by_period: Mapping[tuple[str, int], float],
    renewables_by_period: Mapping[tuple[str, int], float],
    *,
    imports_by_period: Mapping[tuple[str, int], tuple[float, float]] | None = None,
    coal_capacity_by_year: Mapping[int, float] | None = None,
    thermal_floor_by_year: Mapping[int, float] | None = None,
    zero_carbon_must_run_by_period: Mapping[tuple[str, int], float] | None = None,
    biomass_envelope_by_year: Mapping[int, Mapping[str, float]] | None = None,
    ccgt_override_by_period: Mapping[tuple[str, int], float] | None = None,
    only_keys: Sequence[tuple[str, int]] | None = None,
) -> tuple[dict[tuple[str, int], float], dict[tuple[str, int], float], dict[str, int]]:
    """`gci.build_shape`'s loop, stopping at the RATES -- the un-normalised tonnes per MWh.

    Returns `(rates, implied_ccgt_mw, clamp counts)`. Rates rather than the shape because the
    normalisation is per calendar year over whatever keys survived, so two runs over different
    populations produce shapes that differ by their coverage; comparing rates is what makes
    `reimplementation_reproduces_the_shipped_shape` a statement about the arithmetic.

    `only_keys` restricts the population, and every rung here is built over the SAME restriction --
    the half hours with a metered gas reading. A baseline scored on a wider population than the
    rungs it is compared against would put the coverage difference into the gain.
    """
    keys = list(only_keys) if only_keys is not None else list(demand_by_period)
    rates: dict[tuple[str, int], float] = {}
    implied: dict[tuple[str, int], float] = {}
    clamps = {"low": 0, "high": 0}
    for key in keys:
        demand_mw = demand_by_period.get(key)
        renewable_mw = renewables_by_period.get(key)
        if renewable_mw is None or not demand_mw or float(demand_mw) <= 0.0:
            continue
        year = int(key[0][:4])
        import_mw, import_rate = (imports_by_period or {}).get(key, (0.0, 0.0))
        envelope = (biomass_envelope_by_year or {}).get(year)
        zero_carbon_mw = (zero_carbon_must_run_by_period or {}).get(key)
        override = None if ccgt_override_by_period is None else ccgt_override_by_period.get(key)
        # AN ABSENT OVERRIDE IS A REFUSAL, NOT A FALLBACK TO THE MODEL'S OWN GAS. Falling back
        # would silently mix baseline half hours into a swap rung and dilute the very gain being
        # measured -- the fail-open shape §14 caught in its first draft, one layer over.
        if ccgt_override_by_period is not None and override is None:
            continue
        try:
            rate, implied_ccgt, low, high = dispatch_rate(
                float(demand_mw),
                float(renewable_mw),
                year,
                import_mw=float(import_mw),
                import_rate_t_per_mwh=float(import_rate),
                coal_capacity_mw=float((coal_capacity_by_year or {}).get(year, 0.0)),
                thermal_floor_mw=float((thermal_floor_by_year or {}).get(year, 0.0)),
                zero_carbon_must_run_mw=(None if zero_carbon_mw is None else float(zero_carbon_mw)),
                biomass_capacity_mw=(None if envelope is None else float(envelope["capacity_mw"])),
                biomass_floor_mw=(None if envelope is None else float(envelope["floor_mw"])),
                ccgt_mw_override=(None if override is None else float(override)),
            )
        except (gci.ShapeUnavailable, ValueError, KeyError):
            continue
        rates[key] = rate
        implied[key] = implied_ccgt
        clamps["low"] += int(low)
        clamps["high"] += int(high)
    return rates, implied, clamps


def normalise(
    rates: Mapping[tuple[str, int], float],
    demand_by_period: Mapping[tuple[str, int], float],
) -> dict[tuple[str, int], float]:
    """Rates -> the dimensionless shape, per calendar year, demand-weighted mean exactly 1.0.

    The same normalisation `gci.build_shape` and `neso.published_shape` both apply, for the reason
    stated there: a comparison between two series normalised differently measures the normalisation.
    """
    totals: dict[str, list[float]] = {}
    for key, rate in rates.items():
        weight = float(demand_by_period.get(key) or 0.0)
        if weight <= 0.0:
            continue
        acc = totals.setdefault(key[0][:4], [0.0, 0.0])
        acc[0] += rate * weight
        acc[1] += weight
    shape: dict[tuple[str, int], float] = {}
    for key, rate in rates.items():
        acc = totals.get(key[0][:4])
        if acc is None or acc[1] <= 0.0 or acc[0] <= 0.0:
            continue
        shape[key] = rate / (acc[0] / acc[1])
    return shape


def timing_swap(
    implied: Mapping[tuple[str, int], float],
    truth: Mapping[tuple[str, int], float],
) -> dict[tuple[str, int], float]:
    """The model's own DAY MEAN plus TRUTH's within-day deviations — the primary rung.

    The exact inverse of §14's ablation, which replaced a fuel by its day mean and deleted those
    deviations. Additive rather than multiplicative on purpose: a day the model dispatches no gas at
    all has a zero day total, and a multiplicative rescale would hand that day no timing while
    silently reporting a number.
    """
    implied_day = day_mean(implied)
    truth_day = day_mean({k: truth[k] for k in implied if k in truth})
    out: dict[tuple[str, int], float] = {}
    for key in implied:
        if key not in truth or key not in truth_day:
            continue
        out[key] = implied_day[key] + (float(truth[key]) - truth_day[key])
    return out


def level_swap(
    implied: Mapping[tuple[str, int], float],
    truth: Mapping[tuple[str, int], float],
) -> dict[tuple[str, int], float]:
    """TRUTH's day mean plus the MODEL's own within-day deviations — the exact complement.

    Added on the second draft, after `ccgt_timing` came back at a quarter of what §14's headline
    implied and `ccgt_full` came back at more than all of it. Without this rung the difference
    between those two is a residual carrying everything the other two do not, which is the shape of
    a quantity nobody has counted; with it, the decomposition closes and the level can be read as a
    number rather than as a subtraction.
    """
    implied_day = day_mean(implied)
    truth_day = day_mean({k: truth[k] for k in implied if k in truth})
    out: dict[tuple[str, int], float] = {}
    for key in implied:
        if key not in truth or key not in truth_day:
            continue
        out[key] = truth_day[key] + (float(implied[key]) - implied_day[key])
    return out


def shuffled_days(
    implied: Mapping[tuple[str, int], float],
    truth: Mapping[tuple[str, int], float],
    seed: int = NULL_SEED,
) -> dict[tuple[str, int], float]:
    """`timing_swap` with truth's within-day PROFILES dealt to the wrong days — THE NULL.

    Every value and the whole substitution machinery are preserved; only the day a profile belongs
    to is destroyed. A gain here would mean the rungs measure the act of substituting.
    """
    truth_day = day_mean({k: truth[k] for k in implied if k in truth})
    deviations: dict[str, dict[int, float]] = defaultdict(dict)
    for key in implied:
        if key in truth and key in truth_day:
            deviations[key[0]][key[1]] = float(truth[key]) - truth_day[key]
    days = sorted(deviations)
    dealt = list(days)
    random.Random(seed).shuffle(dealt)
    reassigned = {day: deviations[other] for day, other in zip(days, dealt)}

    implied_day = day_mean(implied)
    out: dict[tuple[str, int], float] = {}
    for key in implied:
        profile = reassigned.get(key[0])
        if profile is None or key[1] not in profile:
            continue
        out[key] = implied_day[key] + profile[key[1]]
    return out


def within_day_correlation(
    left: Mapping[tuple[str, int], float],
    right: Mapping[tuple[str, int], float],
    keys: Sequence[tuple[str, int]],
) -> float | None:
    """Correlation of the two series with each one's OWN day mean removed.

    The axis this atom's level has turned on for ten passes, measured directly on the MW series
    rather than inferred from the shapes -- a household can move its washing from 6pm to 2am and
    cannot move it to a windier Tuesday, so the between-day agreement is not the question.
    """
    left_day, right_day = day_mean(left), day_mean(right)
    xs = [float(left[k]) - left_day[k] for k in keys if k in left and k in right]
    ys = [float(right[k]) - right_day[k] for k in keys if k in left and k in right]
    return _pearson(xs, ys)


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    n = len(xs)
    if n < 2 or n != len(ys):
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0.0 or syy <= 0.0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return sxy / (sxx * syy) ** 0.5


def _published_feed_source() -> str:
    return (PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text(encoding="utf-8")


def ceiling_is_unreachable_from(source: str) -> bool:
    """True when nothing in `source` imports this module — an AST walk, not a substring search.

    The same walk and the same reason as `ep13_input_ceiling.ceiling_is_unreachable_from`. This
    module holds metered half-hourly gas, which is the largest emissions term on the system;
    publishing a series built from it would make the reconstruction NESO's arithmetic with a
    different cache, and that it cannot happen is checked structurally rather than promised.
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


def measure_year(
    year: str,
    *,
    rungs: Mapping[str, Mapping[tuple[str, int], float]],
    published: Mapping[tuple[str, int], float],
    demand: Mapping[tuple[str, int], float],
    implied: Mapping[tuple[str, int], float],
    truth: Mapping[tuple[str, int], float],
    timing_override: Mapping[tuple[str, int], float],
) -> dict:
    """Every rung for one year, on the half hours EVERY rung covers and nothing else."""
    score_keys = [
        k
        for k in rungs["baseline"]
        if k[0][:4] == year
        and k in published
        and held_out(k[0])
        and float(demand.get(k) or 0.0) > 0.0
        and all(k in series for series in rungs.values())
    ]
    if len(score_keys) < MIN_SCORED_HALF_HOURS:
        raise neso.NesoIntensityUnavailable(
            f"{year} has {len(score_keys)} scored half hours, under the {MIN_SCORED_HALF_HOURS} bar"
        )

    row: dict[str, object] = {}
    for name, series in rungs.items():
        row[name] = neso.compare_shapes(
            {k: series[k] for k in score_keys}, published, demand, year
        )

    correlations = {
        name: float(value["correlation"])
        for name, value in row.items()
        if isinstance(value, dict) and value.get("correlation") is not None
    }
    baseline = correlations["baseline"]
    row["gain_over_baseline"] = {
        name: correlations[name] - baseline for name in correlations if name != "baseline"
    }

    row["control_scored_half_hours"] = float(len(score_keys))
    row["control_substitution_distance_mw"] = sum(
        abs(implied[k] - truth[k]) for k in score_keys
    ) / len(score_keys)
    # COUNTED ON THIS YEAR'S SCORED HALF HOURS, not run-wide. A run-wide share would let a year
    # whose clamp binds constantly hide behind five that never do -- and the years differ, because
    # the modelled gas level falls across the window while truth's swing does not.
    row["control_clamped_low_share"] = sum(
        1 for k in score_keys if float(timing_override.get(k, 0.0)) < 0.0
    ) / len(score_keys)
    row["control_clamped_high_share"] = sum(
        1 for k in score_keys if float(timing_override.get(k, 0.0)) > gci.CCGT_CAPACITY_MW
    ) / len(score_keys)
    row["implied_gas_vs_truth"] = {
        "correlation": _pearson(
            [implied[k] for k in score_keys], [truth[k] for k in score_keys]
        ),
        "within_day_correlation": within_day_correlation(implied, truth, score_keys),
        "mean_implied_mw": sum(implied[k] for k in score_keys) / len(score_keys),
        "mean_truth_mw": sum(truth[k] for k in score_keys) / len(score_keys),
        "mean_abs_error_mw": row["control_substitution_distance_mw"],
    }
    return row


def verdicts(row: Mapping[str, object]) -> dict[str, bool]:
    """The controls, computed from the row that was just published rather than only asserted in a
    test — a verdict that lives only in another process is one a reader has to take on trust."""
    gains: Mapping[str, float] = row["gain_over_baseline"]  # type: ignore[assignment]
    return {
        # CONTROL 1, THE SUBSTITUTION IS NOT A NO-OP. If the metered series were near-identical to
        # the model's own implied gas, a zero gain would be equally consistent with "gas timing is
        # worth nothing" and with "nothing was substituted" -- the shape R15 calls a control whose
        # PASS branch is unreachable. Read this before any gain below it.
        "the_substituted_series_is_not_the_models_own": (
            float(row["control_substitution_distance_mw"]) > MIN_SUBSTITUTION_DISTANCE_MW  # type: ignore[arg-type]
        ),
        # CONTROL 2, THE NULL DOES NOT GAIN. Truth's within-day profiles dealt to the wrong days
        # keep every value and the whole substitution machinery, so a GAIN here is the machinery
        # talking rather than the information.
        #
        # KEYED TO THE PROPERTY, AND THE FIRST DRAFT WAS NOT. It asked for `abs(gain) <
        # MIN_MATERIAL_GAIN` -- "the null collapses to nothing" -- which is a control pinned to a
        # guessed answer rather than to what a null must satisfy, and it went RED on the real run
        # against a perfectly sound instrument. Scrambled timing does not sit at zero: it actively
        # replaces the model's own gas timing with wrong timing, and it MUST hurt. Measured, it
        # costs 0.22-0.31, and requiring that to be small would have refused the instrument for
        # working. What a null owes is that it does not FLATTER.
        "the_null_does_not_gain": float(gains.get("ccgt_timing_shuffled", 0.0)) < MIN_MATERIAL_GAIN,
        # CONTROL 3, AND IT IS THE ONE THAT MAKES THE NULL MEAN SOMETHING. A null that cannot gain
        # is satisfied by an instrument that reports the same number whatever it is handed. Correct
        # timing must beat scrambled timing by a material margin, or these rungs are not measuring
        # timing at all.
        "correct_timing_beats_scrambled_timing": (
            float(gains.get("ccgt_timing", 0.0)) - float(gains.get("ccgt_timing_shuffled", 0.0))
            > MIN_NULL_DISCRIMINATION
        ),
        # CONTROL 3, THE CLAMP IS NOT CARRYING THE RUNG. Deviations added to a small modelled day
        # mean go negative and are clamped at zero; past this share the rung is partly measuring
        # the clamp and its reading is refused rather than footnoted.
        "the_clamp_is_not_carrying_the_rung": (
            float(row["control_clamped_low_share"]) + float(row["control_clamped_high_share"])  # type: ignore[arg-type]
            < MAX_CLAMPED_SHARE
        ),
        # REPORTED, NOT CONTROLS. These are the answers, and a control that asserts its own answer
        # is a control that cannot fail (R15 TAUTOLOGY).
        "timing_clears_the_baseline": float(gains.get("ccgt_timing", 0.0)) > MIN_MATERIAL_GAIN,
        # AGAINST `ccgt_level`, THE COMPLEMENT, AND THE FIRST DRAFT READ `ccgt_day_mean` HERE --
        # which is the DESTRUCTION rung, not the level rung, and reported this True in every year
        # including the two where it is False. A comparison is only as good as the name of what it
        # compares against, and there was no level rung to compare against until the second draft.
        "timing_beats_level": float(gains.get("ccgt_timing", 0.0))
        > float(gains.get("ccgt_level", 0.0)),
    }


def measure() -> dict:
    """Every year the caches share. Loads the real caches; fits nothing."""
    from sim import elexon_fuel_outturn as fuel
    from sim.generation_demand_history import aggregate_renewable_generation
    from tools.generate_grid_intensity_feed import (
        AGWS_CACHE,
        DEMAND_CACHE,
        aggregate_demand,
        fuel_mix,
    )

    demand = aggregate_demand(json.loads(Path(DEMAND_CACHE).read_text(encoding="utf-8")))
    wind = aggregate_renewable_generation(json.loads(Path(AGWS_CACHE).read_text(encoding="utf-8")))
    (imports, coal_capacity, _coverage, thermal_floors, must_run, _mrc, _envelope) = fuel_mix()
    floors = {y: r["floor_mw"] for y, r in thermal_floors.items()}

    # THE METERED GAS SERIES, AND IT LIVES ONLY IN THIS PROCESS. FUELHH's thermal cache is the one
    # place CCGT is published half-hourly; nothing here hands it to `sim/`.
    truth = {
        key: fuels[SWAPPED_FUEL]
        for key, fuels in per_fuel_by_period(fuel.load_cached_thermal()).items()
        if SWAPPED_FUEL in fuels
    }

    # THE POPULATION IS FIXED FIRST AND SHARED BY EVERY RUNG. A half hour with no gas reading is
    # refused from the baseline too, so no part of any gain below is a coverage difference.
    scored_keys = [k for k in demand if k in truth]

    common = dict(
        imports_by_period=imports,
        coal_capacity_by_year=coal_capacity,
        thermal_floor_by_year=floors,
        zero_carbon_must_run_by_period=must_run,
        biomass_envelope_by_year=None,
    )
    baseline_rates, implied, _ = build_rates(demand, wind, only_keys=scored_keys, **common)

    # THE RE-IMPLEMENTATION IS HELD TO THE SHIPPED FUNCTION BEFORE ANYTHING IS SCORED, and not by a
    # test that lives in another process -- a reader of this artefact has to be able to see it.
    #
    # `gci.build_shape` IS HANDED THE SAME RESTRICTED DEMAND, which is the whole subtlety. It
    # normalises per calendar year over whatever keys survive, so running it over the full demand
    # map and comparing against a baseline built on the gas-reading subset would report the
    # COVERAGE difference as arithmetic drift and this control would fail for the wrong reason --
    # or, with a looser bar, pass while hiding a real one.
    shipped_shape = gci.build_shape({k: demand[k] for k in scored_keys}, wind, **common)
    reference = normalise(baseline_rates, demand)
    drift = max(
        (abs(reference[k] - shipped_shape[k]) for k in reference if k in shipped_shape),
        default=None,
    )

    overrides = {
        "ccgt_timing": timing_swap(implied, truth),
        "ccgt_level": level_swap(implied, truth),
        "ccgt_full": {k: truth[k] for k in implied if k in truth},
        "ccgt_day_mean": day_mean({k: truth[k] for k in implied if k in truth}),
        "ccgt_timing_shuffled": shuffled_days(implied, truth),
    }
    rungs = {"baseline": normalise(baseline_rates, demand)}
    clamps: dict[str, dict[str, int]] = {}
    for name, override in overrides.items():
        rates, _, clamped = build_rates(
            demand,
            wind,
            only_keys=scored_keys,
            ccgt_override_by_period=override,
            **common,
        )
        rungs[name] = normalise(rates, demand)
        clamps[name] = clamped

    ceiling = neso._physical_ceiling_g_co2_per_kwh()
    parsed = neso.to_settlement_periods(neso.load_cached())
    actual = {
        key: float(entry["actual"])
        for key, entry in parsed.items()
        if entry.get("actual") is not None and float(entry["actual"]) <= ceiling
    }
    published = neso.published_shape(actual, demand)

    rows: dict[str, dict] = {}
    for year in sorted({k[0][:4] for k in rungs["baseline"]} & {k[0][:4] for k in published}):
        try:
            row = measure_year(
                year,
                rungs=rungs,
                published=published,
                demand=demand,
                implied=implied,
                truth=truth,
                timing_override=overrides["ccgt_timing"],
            )
        except (neso.NesoIntensityUnavailable, ValueError, KeyError):
            continue
        row["controls"] = verdicts(row)
        rows[year] = row

    return {
        "measured_from": "sim/cache (Elexon FUELHH thermal + AGWS wind + demand; NESO outturn)",
        "basis": neso.PUBLISHED_BASIS,
        "split": "scored on EVEN days of the month -- the same population the other EP13 bounds score",
        "swapped_fuel": SWAPPED_FUEL,
        "what_this_is": (
            "A CEILING, which inverts the per-fuel oracle of 2026-08-30. That instrument was "
            "handicapped and bounded the per-fuel input from BELOW; this one hands the SHIPPED "
            "reconstruction perfect knowledge of the exact quantity a proxy would approximate and "
            "changes nothing else, so no build of that class can beat it and a negative RETIRES the "
            "named build target. Up to error cancellation: a proxy whose errors offset the model's "
            "other errors could score above it, and one that does is fitting the residual."
        ),
        "why_the_primary_rung_is_timing_only": (
            "The build target named at L3 is within-day CCGT DISPATCH. The residual already sets "
            "the daily level, so a rung substituting raw metered gas moves two things and "
            "reproduces one layer down the attribution defect this instrument exists to repair."
        ),
        "rungs": {
            "baseline": "build_shape as shipped, on the half hours with a metered gas reading",
            "ccgt_timing": "the model's own day mean + TRUTH's within-day deviations -- THE CEILING",
            "ccgt_level": "TRUTH's day mean + the model's own within-day deviations -- the exact "
            "complement, so the two axes are two numbers rather than one and a subtraction",
            "ccgt_full": "raw metered CCGT -- level and timing, a larger and different build",
            "ccgt_day_mean": "truth's day mean, FLAT inside the day -- the DESTRUCTION rung. Not a "
            "candidate build: it deletes within-day gas variation entirely, so what it costs is "
            "what that variation is worth IN TOTAL, against which the ceiling is read",
            "ccgt_timing_shuffled": "truth's profiles dealt to the WRONG days -- the NULL",
        },
        "reimplementation_max_drift": drift,
        "reimplementation_reproduces_the_shipped_shape": (
            drift is not None and drift < MAX_REIMPLEMENTATION_DRIFT
        ),
        "clamped_half_hours": clamps,
        "ceiling_reaches_the_published_feed": not ceiling_is_unreachable_from(
            _published_feed_source()
        ),
        "years": rows,
    }


def main(argv: list[str] | None = None) -> int:
    data = measure()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=1, default=str) + "\n", encoding="utf-8")
    print(
        f"reimplementation drift {data['reimplementation_max_drift']} -> "
        f"reproduces_shipped={data['reimplementation_reproduces_the_shipped_shape']}"
    )
    print(
        "year     n  baseline  +TIMING  +level  +full  +flat  +NULL |  gas r  gas r_within  "
        "implied MW  true MW  clampLo"
    )
    for year, row in sorted(data["years"].items()):
        gains = row["gain_over_baseline"]
        gas = row["implied_gas_vs_truth"]
        controls = row["controls"]
        print(
            f"{year} {int(row['control_scored_half_hours']):5d} "
            f"{row['baseline']['correlation']:8.4f} "
            f"{gains['ccgt_timing']:+8.4f} "
            f"{gains['ccgt_level']:+7.4f} "
            f"{gains['ccgt_full']:+6.4f} "
            f"{gains['ccgt_day_mean']:+6.4f} "
            f"{gains['ccgt_timing_shuffled']:+6.4f} | "
            f"{(gas['correlation'] or float('nan')):6.3f} "
            f"{(gas['within_day_correlation'] or float('nan')):12.3f} "
            f"{gas['mean_implied_mw']:11.0f} "
            f"{gas['mean_truth_mw']:8.0f} "
            f"{row['control_clamped_low_share']:8.3f}"
            + "  distinct=" + ("Y" if controls["the_substituted_series_is_not_the_models_own"] else "N")
            + " null=" + ("Y" if controls["the_null_does_not_gain"] else "N")
            + " discrim=" + ("Y" if controls["correct_timing_beats_scrambled_timing"] else "N")
            + " clamp_ok=" + ("Y" if controls["the_clamp_is_not_carrying_the_rung"] else "N")
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
