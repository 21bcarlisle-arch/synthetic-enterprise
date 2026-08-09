"""H33 — does this statistic have a NULL, and is the threshold above it?

THE QUESTION THIS MODULE ASKS, and the one it deliberately does NOT ask.

It does not ask "is the anchor real". Every band in `fabric_gap_ledger` already
carries an `anchor_source` a reader can go and check, and the L1.4 episode
(`docs/staging/done/WORKER_FINDING_AN_ANCHOR_IS_A_NUMBER_AND_A_WINDOW_2026-08-09.md`)
proved that checking it is not enough: L1.4's anchor was a real published figure,
correctly quoted, and the band was STILL fail-open, because a total-variation
distance between two SUBSETS of one home's own data is bounded away from zero by
sampling noise alone. A randomised population — one with no weekday/weekend
structure whatsoever — cleared it. No amount of re-reading the source could have
caught that. Only measuring the statistic's NULL could.

So the question here is: **for each band, what does the statistic read on a
population from which the very structure the band certifies has been removed, at
the window the band is APPLIED at — and is the threshold above that?**

Three outcomes, and the middle one is the reason this is a sweep rather than a
test:

* `INSIDE_NULL` — a structureless population PASSES the band. The band cannot
  fail on the absence of the thing it exists to certify. This is a DEFECT.
* `SAME_ORDER` — the band fails the null, but by less than the null's own spread.
  It is separated by luck of the draw, not by construction. This is a FINDING.
* `SEPARATED` — the gap between the threshold and the null exceeds the null's own
  spread. The band can do its job at this window.

THE WINDOW IS PART OF THE MEASUREMENT (this is the half that is easy to skip).
Sampling nulls shrink with the observation window: a spread-of-means statistic
measured over a year has a null a third the width of the same statistic measured
over 120 days. A band derived on one window and applied on another can sit above
its null in the first place and inside it in the second, while the number in the
table never changes. So the null is always measured on the population as it is
ACTUALLY judged — see `tools/couple_fabric.py`, whose live coupling run judges 10
homes over 2022-01-01..2022-04-30. `applied_window()` reads that window off the
tool rather than restating it, so a change to the tool cannot desync the sweep.

NEVER LOWER THE FLOOR (R12). A hit here is dispositioned one of two ways —
repair the STATISTIC (the L1.4 -> L1.4n permutation-null pattern: subtract the
null instead of hoping to sit above it) or repair the WINDOW (judge where the
null is small enough to leave room). Moving the threshold down until something
fails is goal-seeking the control, and it is forbidden.

THE FAIL-OPEN SHAPE OF THIS MODULE ITSELF is a sweep that finds no bands — an
enumeration that quietly returns empty, or that misses a band table added to
another module, reports a clean sheet indistinguishable from a real one. Two
guards, both tested: `anchored_bands()` derives its list from the LIVE band
tables by iteration (never a hand-copied list of names), and
`unswept_band_sources()` re-scans `background/` and `tools/` for any other module
declaring bands, so a second table cannot appear outside this sweep's sight.
"""

from __future__ import annotations

import ast
import math
import random
import statistics
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Sequence

from background import fabric_gap_ledger as fgl
from background.fabric_gap_ledger import (
    AnchorStatus,
    Band,
    PopulationTraces,
    Verdict,
)

PROJECT_DIR = Path(__file__).resolve().parents[1]

# The anchor classes that make a band EXTERNAL — anchored to something outside
# this machine, which is the class the atom asks about. STRUCTURAL is excluded
# deliberately and NOT silently: a structural band claims a bound that no real
# population can cross by construction (an impossibility bound), so its null is
# the argument itself rather than a measurement. NEED is excluded because there
# is no threshold to sit above anything. Both exclusions are reported by
# `excluded_bands()` with their reason, so a band that changes anchor class
# leaves this sweep's scope VISIBLY rather than by evaporating from a list.
EXTERNAL_ANCHORS = frozenset({AnchorStatus.PUBLISHED, AnchorStatus.DOMAIN_KNOWLEDGE})

# How many times each randomised null is redrawn. The null's SPREAD is the
# quantity the verdict turns on, so this has to be enough draws to estimate a
# 5th and 95th percentile that does not itself move between runs; 200 puts ~10
# draws in each tail.
DEFAULT_REPLICATIONS = 200

# Fixed so the sweep is reproducible and a re-run is a re-measurement rather
# than a re-roll (C-S2). Named rather than inline so a caller who wants a
# genuinely independent second opinion has to say so.
DEFAULT_SEED = 20260809


class NullVerdict(str, Enum):
    INSIDE_NULL = "inside_null"    # DEFECT: the structureless population passes
    SAME_ORDER = "same_order"      # FINDING: separated by less than the null's spread
    SEPARATED = "separated"        # the band can fail on absence of structure
    # No home at the applied window is judged by this band, so its null cannot be
    # measured on the load set it actually governs. Reported as its own state
    # rather than folded into either of the others: measuring a heat-pump band's
    # null on a panel of gas homes is the wrong-load-set defect, and calling an
    # unexercised band clean is the fail-open one.
    UNMEASURABLE = "unmeasurable"


class SweepIncomplete(RuntimeError):
    """Raised when the sweep cannot honestly claim to have covered every band.

    A missing null spec is NOT a pass. This is the fail-silent direction (R15
    pattern 3) and it is the one this whole module would be worthless without:
    a band with no null measured is a band whose null is unknown, which reads
    exactly like a clean one in any report that skips it.
    """


# ===========================================================================
# (1) THE ENUMERATION — derived from the band tables, never from inspection
# ===========================================================================


def anchored_bands() -> dict[str, Band]:
    """Every band carrying a numeric threshold AND an external anchor.

    Derived by iterating the LIVE table. A hand-maintained list of names would
    be a second place for a band to exist, and the band that got added to only
    one of them would be the one that mattered.
    """
    return {
        name: band
        for name, band in fgl.BANDS.items()
        if band.threshold is not None
        and math.isfinite(band.threshold)
        and band.anchor in EXTERNAL_ANCHORS
    }


def excluded_bands() -> dict[str, str]:
    """Every band NOT swept, with the reason — so coverage is readable as a
    complement rather than inferred from an absence."""
    out: dict[str, str] = {}
    for name, band in fgl.BANDS.items():
        if band.threshold is None or not math.isfinite(band.threshold):
            out[name] = f"no numeric threshold (anchor={band.anchor.value})"
        elif band.anchor not in EXTERNAL_ANCHORS:
            out[name] = (
                f"anchor is {band.anchor.value}, not external — its bound is an "
                "argument, not a measured external figure"
            )
    return out


# Modules that are ALLOWED to declare bands and are covered by this sweep. Any
# other module in `background/` or `tools/` that constructs a band is a hole.
SWEPT_BAND_SOURCES = ("background/fabric_gap_ledger.py",)

# Constructor names that mean "a band is being declared here". Matched on the
# AST call node, so a mention in a docstring or a comment — which is how
# `lcl_household_anchors.py` refers to `AnchorStatus.NEED` — does not count as a
# declaration. Prose is not a band.
_BAND_CONSTRUCTORS = ("Band", "RateBand")


def unswept_band_sources() -> list[str]:
    """Modules under `background/` and `tools/` that CONSTRUCT a band and are not
    in `SWEPT_BAND_SOURCES`.

    This is the completeness guard on the enumeration's SOURCE. `anchored_bands`
    can only be as complete as the table it reads; a second table in another
    module would leave it truthfully reporting a clean sweep of the wrong half.
    """
    found: list[str] = []
    for directory in ("background", "tools"):
        for path in sorted((PROJECT_DIR / directory).rglob("*.py")):
            rel = path.relative_to(PROJECT_DIR).as_posix()
            if rel in SWEPT_BAND_SOURCES or rel.endswith("band_null_sweep.py"):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                name = (
                    func.id if isinstance(func, ast.Name)
                    else func.attr if isinstance(func, ast.Attribute)
                    else None
                )
                if name in _BAND_CONSTRUCTORS:
                    found.append(rel)
                    break
    return found


def applied_window() -> tuple[int, int]:
    """(homes, days) as the bands are ACTUALLY judged, read off the live tool.

    Restating the window here as two integers is how it would go stale: the
    tool's window moves, this file keeps reporting the old margin, and the
    sweep's headline claim silently becomes about a population nobody judges.
    """
    from tools import couple_fabric as cf

    days = (cf.WINDOW_END - cf.WINDOW_START).days + 1
    return len(cf.PANEL), days


# ===========================================================================
# (2) THE NULLS — one randomisation per band, each removing exactly the
#     structure that band certifies and leaving everything else intact
# ===========================================================================


def _grids(population: PopulationTraces) -> list[list[list[float]]]:
    return [[list(day) for day in home] for home in population.grids]


def _replace_grids(
    population: PopulationTraces, grids: Sequence[Sequence[Sequence[float]]]
) -> PopulationTraces:
    return PopulationTraces(
        generator=population.generator + "::null",
        homes=population.homes,
        grids=tuple(tuple(tuple(day) for day in home) for home in grids),
        is_weekend=population.is_weekend,
        annual_kwh=population.annual_kwh,
        weather_driver=population.weather_driver,
        pc1_is_an_input=population.pc1_is_an_input,
        heating_systems=population.heating_systems,
        space_heat_grids=population.space_heat_grids,
    )


def _flat_day_null(population: PopulationTraces, rng: random.Random) -> PopulationTraces:
    """Remove WITHIN-DAY and DAY-TO-DAY structure: every day becomes the home's
    own mean diurnal profile, rescaled to THAT DAY'S OWN total.

    What survives: the home's level, its mean diurnal shape, and its daily-total
    series day for day. What is destroyed: appliance events, occupancy
    variation, and any difference in shape between one day and the next —
    everything L1.1 (texture), L1.2 (day-to-day variety) and L1.3 (away days)
    exist to certify. A generator that emitted exactly this is the
    smooth-by-construction generator all three bands are there to reject.

    NOTHING IS RESAMPLED, and it took two goes to get there — both worth
    recording, because both are the same mistake and it is the mistake this
    module exists to catch other people making.

    The first version drew each day's TOTAL independently from the home's own
    days. That injected level jumps across the midnight boundary and inflated
    every step relative to the window mean: texture rose from ~0.05 to ~0.35 and
    L1.3 gained 120 spurious away days per home, so THREE bands reported as
    fail-open on structure the null itself had put there. The second version
    kept a BOOTSTRAP of the mean profile over the home's own days, defended as
    "the estimation noise a 120-day mean genuinely carries" — but sampling noise
    in a mean profile IS half-hourly movement, which is precisely the quantity
    L1.1 measures. It inflated the texture null by ~30% and flipped one band into
    a defect on the strength of noise this function had added. A null that adds
    structure is not a null, whatever the noise is called.

    So this null is DETERMINISTIC. `rng` is accepted for uniformity with the
    randomised nulls and deliberately unused.

    IT IS ALSO THE MOST FAVOURABLE structureless generator available, and that
    asymmetry is the point: it keeps each home's OWN mean profile and its OWN
    daily totals, where a real smooth-by-construction generator (the shipped
    rescaled-PC1 path) has one national profile for everybody. So a band this
    null CLEARS is unambiguously fail-open, and a band it fails is separated
    against the friendliest structureless population that could be built.
    """
    del rng
    return _replace_grids(
        population, [_flatten_home(home) for home in population.grids]
    )


def _flatten_home(home: Sequence[Sequence[float]]) -> list[list[float]]:
    """One home's days, each replaced by the home's own mean profile rescaled to
    THAT DAY'S OWN total. The kernel of `_flat_day_null`, factored out so the
    behavioural null below cannot drift into being a second flattening."""
    mean_day = [
        sum(day[p] for day in home) / len(home) for p in range(fgl.PERIODS_PER_DAY)
    ]
    shape_total = sum(mean_day)
    if shape_total <= 0.0:
        return [list(day) for day in home]
    unit = [v / shape_total for v in mean_day]
    return [[v * sum(day) for v in unit] for day in home]


def _flat_behavioural_day_null(
    population: PopulationTraces, rng: random.Random
) -> PopulationTraces:
    """The flat-day null for a band read NET OF SPACE HEAT: the BEHAVIOURAL
    stream is flattened and the heating machine is left exactly as it is.

    WHY THIS EXISTS AND `_flat_day_null` WILL NOT DO (H37). A null must remove
    the structure its band certifies from the load set the band is READ on. Once
    L1.3 is read net of space heat, the two available shortcuts are both wrong,
    and each is wrong in the way this module exists to catch:

    * flatten the METER and leave the heat stream alone — the netted stream is
      then `flat_meter - real_heat`, which carries the heating machine's whole
      day-to-day structure with a minus sign in front of it. The null would be
      INVENTING the structure the band looks for.
    * flatten BOTH streams — the netted day is `M_d*u_meter - H_d*u_heat`, whose
      SHAPE moves with the ratio of the two daily totals. Less structure than the
      first, but not none, and it appears on cold days: a null that puts a
      weather signal into a band about holidays.

    So the null is taken where the reading is taken. Every day's behavioural
    stream becomes that home's own mean behavioural profile at that day's own
    behavioural total, and the meter is rebuilt as `flat_behavioural + heat` so
    that `meter_net_of_space_heat` recovers exactly the flattened stream and the
    heat stream is still a genuine component of the meter it is subtracted from.

    What survives: the home's level, its mean behavioural shape, its daily
    behavioural totals day for day, and its heating machine in full. What is
    destroyed: any difference in behavioural SHAPE between one day and the next —
    which is the whole of what an absence is, and the only thing L1.3 certifies.
    A home that emitted exactly this took its holidays without changing what it
    did when it was in.

    DETERMINISTIC, for the reason recorded on `_flat_day_null`: `rng` is accepted
    for uniformity with the randomised nulls and deliberately unused.

    Where the generator supplies no split this degrades to `_flat_day_null`
    exactly — with nothing to net, the behavioural stream IS the meter.
    """
    del rng
    out: list[list[list[float]]] = []
    for k, home in enumerate(population.grids):
        heat = _heat_of(population, k)
        behavioural = fgl.meter_net_of_space_heat([list(day) for day in home], heat)
        flat = _flatten_home(behavioural)
        if heat is None:
            out.append(flat)
        else:
            out.append([[b + h for b, h in zip(flat_day, heat_day)]
                        for flat_day, heat_day in zip(flat, heat)])
    return _replace_grids(population, out)


def _exchangeable_homes_null(
    population: PopulationTraces, rng: random.Random
) -> PopulationTraces:
    """Pool every (home, day) and deal the days back out at random, preserving
    each home's day count.

    Under this null the homes are EXCHANGEABLE: no home has a timing, a shape or
    a habit of its own, because its days came from the same pot as everybody
    else's. Any diversity a statistic still reports is the spread of a sample
    mean — which is exactly the quantity L2.3 (timing diversity) reports, and
    exactly the quantity that shrinks with the window.

    THE DEAL ITSELF IS THE LEDGER'S (`fgl.deal_preserving_counts`), not a second
    copy here. L2.3n's repair scores the live cell against the SAME null this
    sweep measures it with, and two implementations of "pool and deal back" would
    be one name carrying two nulls the day one of them was tweaked.
    """
    return _replace_grids(
        population,
        fgl.deal_preserving_counts(
            [list(day) for home in population.grids for day in home],
            [len(home) for home in population.grids],
            rng,
        ),
    )


def _clone_population_null(
    population: PopulationTraces, rng: random.Random
) -> PopulationTraces:
    """Every home becomes the SAME randomly-chosen home, rescaled to its own
    annual total.

    The null for L2.1 (smoothing): a population with no between-home diversity
    left, only a volume factor. Aggregating clones cannot smooth, so the
    smoothing ratio should sit at 1.0 and the at-most band should fail it. The
    template is drawn at random rather than fixed so the null is not a property
    of whichever home happened to be first in the panel.
    """
    template = list(population.grids[rng.randrange(len(population.grids))])
    template_total = sum(v for day in template for v in day)
    out: list[list[list[float]]] = []
    for home in population.grids:
        home_total = sum(v for day in home for v in day)
        k = (home_total / template_total) if template_total > 0.0 else 1.0
        out.append([[v * k for v in day] for day in template])
    return _replace_grids(population, out)


def _no_scale_diversity_null(
    population: PopulationTraces, rng: random.Random
) -> PopulationTraces:
    """Every home's annual total becomes one value drawn from the population.

    The null for L2.4 (scale spread): homes that are all the same size. p90/p10
    is then exactly 1.0. Unlike the others this null is a point mass by
    construction — recorded as such rather than dressed up with a spread it does
    not have.
    """
    value = rng.choice(list(population.annual_kwh))
    return PopulationTraces(
        generator=population.generator + "::null",
        homes=population.homes,
        grids=population.grids,
        is_weekend=population.is_weekend,
        annual_kwh=tuple(value for _ in population.annual_kwh),
        weather_driver=population.weather_driver,
        pc1_is_an_input=population.pc1_is_an_input,
        heating_systems=population.heating_systems,
        space_heat_grids=population.space_heat_grids,
    )


# --- the statistic readers -------------------------------------------------
#
# Every one of these calls the SHIPPED statistic in `fabric_gap_ledger`. None of
# them re-implements it. A re-implementation would be the tautology R15 names
# first: the sweep would be measuring the null of a function that is not the one
# doing the judging, and would go green while the real statistic stayed
# fail-open.


def _per_home_texture(population: PopulationTraces) -> list[float]:
    return [fgl.half_hourly_texture(home) for home in population.grids]


def _judged_by_texture_band(band_name: str) -> Callable[[PopulationTraces], list[int]]:
    """The homes a texture band ACTUALLY judges, routed through the live
    `texture_band_for` rather than by re-reading the register here.

    The three L1.1 bands are regime-conditioned: one gas, one heat pump, one
    resistive. Measuring the heat-pump band's null on a panel of gas homes would
    report a defect in the wrong load set — the band would look fail-open because
    gas homes are spikier, which says nothing about the homes it governs. Routing
    through the shipped router also means a change to `HEATING_REGIMES` moves the
    sweep's sub-populations with it instead of desyncing them.
    """

    def select(population: PopulationTraces) -> list[int]:
        systems = population.heating_systems or (None,) * len(population.homes)
        return [
            i
            for i, system in enumerate(systems)
            if fgl.texture_band_for(system).statistic == band_name
        ]

    return select


def _per_home_day_correlation(population: PopulationTraces) -> list[float]:
    return [fgl.day_to_day_shape_correlation(home) for home in population.grids]


def _per_home_away_days(population: PopulationTraces) -> list[float]:
    """Read on the load set the live cell judges — net of space heat (H37).

    Reading the raw meter here would measure the null of a statistic nobody
    applies: `evaluate_population` passes the space-heat split to
    `trough_statistics`, so a sweep that did not would report a margin for a
    band that is not the one in the ledger.
    """
    return [
        float(fgl.trough_statistics(home, space_heat=_heat_of(population, k)).away_signature_days)
        for k, home in enumerate(population.grids)
    ]


def _heat_of(population: PopulationTraces, k: int) -> list[list[float]] | None:
    """Home `k`'s space-heat stream, or None where the generator supplies no
    split — the fail-closed reading `meter_net_of_space_heat` already defines."""
    if not population.space_heat_grids:
        return None
    return [list(day) for day in population.space_heat_grids[k]]


def _smoothing_ratio(population: PopulationTraces) -> list[float]:
    return [fgl.smoothing_ratio(fgl.smoothing_curve(population.grids))]


def _between_home_correlation(population: PopulationTraces) -> list[float]:
    return [fgl.between_home_correlation(population.grids, population.weather_driver)]


def _timing_diversity(population: PopulationTraces) -> list[float]:
    return [fgl.timing_diversity(population.grids)]


def _scale_spread(population: PopulationTraces) -> list[float]:
    return [fgl.scale_spread(population.annual_kwh).p90_over_p10]


@dataclass(frozen=True)
class NullSpec:
    """How to remove the structure ONE band certifies, and how to read the
    statistic back off what is left."""

    band: str
    scope: str                     # "per_home" | "population"
    randomisation: str             # short name of the null, for the ledger
    why: str                       # what is destroyed and what survives
    make_null: Callable[[PopulationTraces, random.Random], PopulationTraces]
    read: Callable[[PopulationTraces], list[float]]
    is_point_mass: bool = False    # the null has no spread by construction
    # Which homes this band governs, when it does not govern all of them. Returns
    # indices into the population; an empty return makes the band UNMEASURABLE at
    # this window rather than clean.
    subpopulation: Callable[[PopulationTraces], list[int]] | None = None


NULL_SPECS: dict[str, NullSpec] = {
    "L1.1_half_hourly_texture": NullSpec(
        "L1.1_half_hourly_texture", "per_home", "flat_day",
        "every day becomes the home's own mean profile at its own total: level "
        "and diurnal shape survive, appliance events do not",
        _flat_day_null, _per_home_texture, is_point_mass=True,
        subpopulation=_judged_by_texture_band("L1.1_half_hourly_texture"),
    ),
    "L1.1e_half_hourly_texture_electric_heat": NullSpec(
        "L1.1e_half_hourly_texture_electric_heat", "per_home", "flat_day",
        "same null as L1.1, read only on the HEAT-PUMP homes this band governs — "
        "the band differs only in where the threshold sits, but the load set it "
        "sits over is not the same one",
        _flat_day_null, _per_home_texture, is_point_mass=True,
        subpopulation=_judged_by_texture_band("L1.1e_half_hourly_texture_electric_heat"),
    ),
    "L1.1r_half_hourly_texture_resistive_heat": NullSpec(
        "L1.1r_half_hourly_texture_resistive_heat", "per_home", "flat_day",
        "same null as L1.1, read only on the RESISTIVE-heat homes this band "
        "governs",
        _flat_day_null, _per_home_texture, is_point_mass=True,
        subpopulation=_judged_by_texture_band("L1.1r_half_hourly_texture_resistive_heat"),
    ),
    "L1.2_day_to_day_shape_correlation": NullSpec(
        "L1.2_day_to_day_shape_correlation", "per_home", "flat_day",
        "every day becomes the home's own mean profile: there is no day-to-day "
        "shape variety left, which is the property this at-most band certifies",
        _flat_day_null, _per_home_day_correlation, is_point_mass=True,
    ),
    "L1.3_away_days_per_year": NullSpec(
        "L1.3_away_days_per_year", "per_home", "flat_behavioural_day",
        "every day's BEHAVIOURAL stream becomes the home's own mean behavioural "
        "profile at that day's own total, with the heating machine left as it "
        "is: no day is emptier than any other, so no absence is representable — "
        "flattened where the band is now read (net of space heat, H37) rather "
        "than on the meter, since flattening the meter would leave the heat "
        "stream's own structure in the netted result with a minus sign in front",
        _flat_behavioural_day_null, _per_home_away_days, is_point_mass=True,
    ),
    "L2.1_smoothing_ratio": NullSpec(
        "L2.1_smoothing_ratio", "population", "clone_population",
        "every home becomes one randomly drawn home rescaled to its own volume: "
        "no diversity left for aggregation to smooth",
        _clone_population_null, _smoothing_ratio,
    ),
    "L2.2_between_home_correlation": NullSpec(
        "L2.2_between_home_correlation", "population", "clone_population",
        "every home becomes one drawn home rescaled: the between-home "
        "independence this at-most band certifies is gone, and the de-weathered "
        "residuals should sit near +1",
        _clone_population_null, _between_home_correlation,
    ),
    # KEPT AFTER L2.3 LEFT THE JUDGED SET (H34, 2026-08-10). The sweep measured
    # this band INSIDE its own null at 40/60/90d, the disposition was repair-the-
    # statistic, and the floor came out — so `anchored_bands()` no longer returns
    # it and `measure_null` would refuse a band with no threshold. The spec stays
    # because it is the standing offer: the day anyone puts a number back on L2.3
    # from an external panel, the sweep measures its null on the next run instead
    # of silently having no opinion about it.
    "L2.3_timing_diversity_periods": NullSpec(
        "L2.3_timing_diversity_periods", "population", "exchangeable_homes",
        "days are pooled and dealt back at random: homes have no timing of "
        "their own, so the reported spread is the spread of a sample mean",
        _exchangeable_homes_null, _timing_diversity,
    ),
    "L2.4_scale_spread_p90_p10": NullSpec(
        "L2.4_scale_spread_p90_p10", "population", "no_scale_diversity",
        "every home's annual total becomes one drawn value: no size diversity, "
        "so p90/p10 is exactly 1.0",
        _no_scale_diversity_null, _scale_spread, is_point_mass=True,
    ),
}


# ===========================================================================
# (3) THE MEASUREMENT and the verdict
# ===========================================================================


def _quantile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = q * (len(ordered) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


@dataclass(frozen=True)
class NullMeasurement:
    band: str
    direction: str
    threshold: float
    anchor: str
    randomisation: str
    scope: str
    homes: int
    # How many homes this band actually governs at this window. Carried because a
    # band that governs one home has a null estimated from one home, and a reader
    # who saw only the margin would not know that.
    homes_judged: int
    days: int
    draws: int
    null_median: float
    null_p5: float
    null_p95: float
    null_spread: float
    # The null value on the PASS side of the band — the best a structureless
    # population manages. This, not the median, is what the threshold has to
    # clear: a band the null beats one draw in twenty is not a control.
    null_best: float
    margin: float                  # threshold - null_best, signed to the band
    verdict: NullVerdict
    # The SAME statistic on the REAL population, carried alongside because the
    # null on its own cannot tell the two repairs apart. A band inside its null
    # while the real population reads far above it is a THRESHOLD placed too low
    # (repair the window or the number's derivation); a band inside its null
    # while the real population reads no higher than the null is a STATISTIC with
    # no discriminating power at this window (repair the statistic — the L1.4 ->
    # L1.4n pattern). Diagnostic, never a target (R12).
    observed_median: float = float("nan")
    observed_worst: float = float("nan")
    # How many INDEPENDENT readings the null's spread was estimated from. Fewer
    # than two means there is no spread to speak of, so `SEPARATED` rests on a
    # point estimate and the SAME_ORDER branch could never have been reached —
    # a control that cannot reach one of its verdicts on this band. Carried and
    # surfaced rather than folded into the verdict, because suppressing the
    # verdict would be as dishonest as hiding the caveat.
    spread_readings: int = 0
    caveat: str = ""
    note: str = ""

    @property
    def is_hit(self) -> bool:
        return self.verdict is not NullVerdict.SEPARATED

    @property
    def needs_disposition(self) -> bool:
        return self.is_hit or bool(self.caveat)


def _unmeasurable(
    band: Band, spec: NullSpec, population: PopulationTraces
) -> "NullMeasurement":
    nan = float("nan")
    return NullMeasurement(
        band=band.statistic,
        direction=band.direction,
        threshold=band.threshold if band.threshold is not None else nan,
        anchor=band.anchor.value,
        randomisation=spec.randomisation,
        scope=spec.scope,
        homes=len(population.homes),
        homes_judged=0,
        days=population.days,
        draws=0,
        null_median=nan, null_p5=nan, null_p95=nan, null_spread=nan,
        null_best=nan, margin=nan,
        verdict=NullVerdict.UNMEASURABLE,
        note=(
            "no home at this window is judged by this band, so its null cannot be "
            "measured on the load set it governs — the band is carried, and never "
            "exercised, by the live coupling run"
        ),
    )


def _null_best(values: Sequence[float], direction: str) -> float:
    return _quantile(values, 0.95) if direction == "at_least" else _quantile(values, 0.05)


def _draw(
    spec: "NullSpec",
    population: PopulationTraces,
    selected: Sequence[int],
    band_name: str,
    *,
    replications: int,
    seed: int,
) -> tuple[list[float], list[float], int]:
    """Read the statistic on the real population and on `draws` null populations,
    both restricted to the homes this band judges.

    Both empty cases RAISE rather than returning an empty list: a statistic that
    reads nothing finite has no margin to compare, and a null that cannot be
    measured is a null that is UNKNOWN — which must never render as a clear one.
    """
    keep = set(selected)

    def read(pop: PopulationTraces) -> list[float]:
        return [v for k, v in enumerate(spec.read(pop)) if k in keep and math.isfinite(v)]

    observed = read(population)
    if not observed:
        raise SweepIncomplete(
            f"{band_name}: the statistic returned nothing finite on the real "
            "population, so there is no margin to compare a null against"
        )

    rng = random.Random(f"{seed}:{band_name}")
    draws = 1 if spec.is_point_mass else replications
    values: list[float] = []
    for _ in range(draws):
        values.extend(read(spec.make_null(population, rng)))
    if not values:
        raise SweepIncomplete(
            f"{band_name}: the null produced no finite readings — a null that "
            "cannot be measured is a null that is unknown, not one that is clear"
        )
    return observed, values, draws


def _judge_against_null(
    band: Band, values: Sequence[float]
) -> tuple[float, float, float, NullVerdict, str]:
    """The verdict rule, kept in one place and away from the plumbing.

    Fixed BEFORE any number was looked at (R12): the threshold has to clear the
    best the null manages, and clear it by more than the null's own spread. The
    quantity compared is `null_best` — the 95th percentile on the pass side, not
    the median — because a band a structureless population beats one draw in
    twenty is not a control.
    """
    threshold = band.threshold
    assert threshold is not None      # callers check; narrows the type
    best = _null_best(values, band.direction)
    spread = _quantile(values, 0.95) - _quantile(values, 0.05)
    gap = (threshold - best) if band.direction == "at_least" else (best - threshold)

    if band.judge(best) is Verdict.PASS:
        return best, spread, gap, NullVerdict.INSIDE_NULL, (
            "a population with this structure REMOVED clears the band in at least "
            "1 draw in 20 — the band cannot fail on absence"
        )
    if gap <= spread:
        return best, spread, gap, NullVerdict.SAME_ORDER, (
            f"the band clears the null by {gap:.4g}, which is inside the null's own "
            f"spread of {spread:.4g} — separated by the draw, not by construction"
        )
    return best, spread, gap, NullVerdict.SEPARATED, (
        f"the band clears the null by {gap:.4g} against a null spread of {spread:.4g}"
    )


def measure_null(
    band_name: str,
    population: PopulationTraces,
    *,
    replications: int = DEFAULT_REPLICATIONS,
    seed: int = DEFAULT_SEED,
) -> NullMeasurement:
    """Measure one band's null on `population`, at the window `population` spans."""
    band = fgl.BANDS[band_name]
    if band.threshold is None:
        raise SweepIncomplete(f"{band_name} has no threshold to measure a null against")
    spec = NULL_SPECS.get(band_name)
    if spec is None:
        raise SweepIncomplete(
            f"{band_name} has no null spec — an unmeasured null is not a clean one"
        )

    selected = (
        spec.subpopulation(population) if spec.subpopulation is not None
        else list(range(len(population.homes)))
    )
    if not selected:
        return _unmeasurable(band, spec, population)

    observed, values, draws = _draw(
        spec, population, selected, band_name, replications=replications, seed=seed
    )
    best, spread, gap, verdict, note = _judge_against_null(band, values)

    return NullMeasurement(
        band=band_name,
        direction=band.direction,
        threshold=band.threshold,
        anchor=band.anchor.value,
        randomisation=spec.randomisation,
        scope=spec.scope,
        homes=len(population.homes),
        homes_judged=len(selected),
        days=population.days,
        draws=draws,
        null_median=statistics.median(values),
        null_p5=_quantile(values, 0.05),
        null_p95=_quantile(values, 0.95),
        null_spread=spread,
        null_best=best,
        margin=gap,
        verdict=verdict,
        observed_median=statistics.median(observed),
        observed_worst=min(observed) if band.direction == "at_least" else max(observed),
        spread_readings=len(values),
        caveat=(
            f"the null rests on {len(values)} reading(s), so it has no estimable "
            "spread — this verdict is a point estimate and SAME_ORDER was not "
            "reachable for this band at this window"
            if len(values) < 2 else ""
        ),
        note=note,
    )


def sweep(
    population: PopulationTraces,
    *,
    replications: int = DEFAULT_REPLICATIONS,
    seed: int = DEFAULT_SEED,
    require_complete_sources: bool = True,
) -> list[NullMeasurement]:
    """Measure every externally-anchored numeric band's null on `population`.

    Refuses to return at all if the enumeration is empty or if a band has no
    null spec. Both are the fail-open shape here: a sweep that reports nothing
    reads exactly like a sweep that found nothing wrong.
    """
    bands = anchored_bands()
    if not bands:
        raise SweepIncomplete(
            "the enumeration is EMPTY — either the band table moved or the anchor "
            "classes changed; an empty sweep is not a clean sweep"
        )
    missing = sorted(set(bands) - set(NULL_SPECS))
    if missing:
        raise SweepIncomplete(
            "no null spec for: " + ", ".join(missing) + " — every anchored band "
            "must have a declared randomisation before this sweep may report"
        )
    if require_complete_sources:
        stray = unswept_band_sources()
        if stray:
            raise SweepIncomplete(
                "band tables outside the swept set: " + ", ".join(stray)
            )
    return [
        measure_null(name, population, replications=replications, seed=seed)
        for name in sorted(bands)
    ]


def hits(measurements: Sequence[NullMeasurement]) -> list[NullMeasurement]:
    return [m for m in measurements if m.is_hit]


# The verdicts a RUN must not survive, as opposed to the ones it may report and
# carry to a disposition. Declared here rather than in the runner so the rule can
# be exercised without a subprocess, and so there is ONE list rather than a
# report-side idea of "bad" and an exit-code-side one free to drift apart.
#
# UNMEASURABLE is fatal (2026-08-09, atom `H35_the_panel_never_exercises_two_of_its
# _own_bands`) and it was not before. The distinction the old exit code drew was
# "the null is known and the band sits inside it" vs "everything else", which puts
# a band whose null is UNKNOWN on the passing side of the line. That is R15's
# fail-silent pattern applied to the sweep itself: a band no home exercises is an
# unavailable check, an unavailable check is a FAILED check, and the whole reason
# this module exists is that unknown reads exactly like clean. It cost nothing to
# notice for the six weeks L1.1r judged zero homes and reported a clean exit 0.
FATAL_VERDICTS = (NullVerdict.INSIDE_NULL, NullVerdict.UNMEASURABLE)


def fatal(measurements: Sequence[NullMeasurement]) -> list[NullMeasurement]:
    """The measurements a run must FAIL on, not merely print.

    SAME_ORDER stays non-fatal and that is deliberate rather than lenient: it is a
    finding about how far a band sits from its null, dispositioned in
    `docs/design/BAND_NULL_SWEEP.md`, and it does not mean the control is blind.
    A band judging NO home does mean exactly that.
    """
    return [m for m in measurements if m.verdict in FATAL_VERDICTS]


def truncated(population: PopulationTraces, days: int) -> PopulationTraces:
    """The same population watched for fewer days."""
    if days > population.days:
        raise SweepIncomplete(
            f"cannot watch {days} days of a {population.days}-day population"
        )
    return PopulationTraces(
        generator=population.generator,
        homes=population.homes,
        grids=tuple(home[:days] for home in population.grids),
        is_weekend=population.is_weekend[:days],
        annual_kwh=population.annual_kwh,
        weather_driver=population.weather_driver[:days],
        pc1_is_an_input=population.pc1_is_an_input,
        heating_systems=population.heating_systems,
        space_heat_grids=tuple(g[:days] for g in population.space_heat_grids),
    )


def window_sensitivity(
    band_name: str,
    population: PopulationTraces,
    windows: Sequence[int],
    *,
    replications: int = DEFAULT_REPLICATIONS,
    seed: int = DEFAULT_SEED,
) -> list[NullMeasurement]:
    """The same band's null at several observation windows.

    THIS IS WHAT DECIDES THE DISPOSITION, and it is the reason a single margin is
    not enough to act on. A sampling null shrinks with the window, so a band can
    be comfortably above its null at one window and inside it at another with the
    number in the table never moving.

    * The null shrinks and the OBSERVED value does not -> the threshold is a
      window away from being sound: repair the WINDOW (judge where the null is
      small enough), and the band's derivation must state the window it holds at.
    * The null shrinks and the observed value shrinks WITH it -> the statistic
      carries the same sampling term as its own null, so no fixed floor can be
      right at every window: repair the STATISTIC (the L1.4 -> L1.4n pattern —
      score against the permutation null instead of against a constant).

    Neither disposition is "move the threshold until something fails" (R12).
    """
    return [
        measure_null(
            band_name, truncated(population, d), replications=replications, seed=seed
        )
        for d in sorted(windows)
    ]


def to_json(measurements: Sequence[NullMeasurement]) -> dict:
    homes, days = (measurements[0].homes, measurements[0].days) if measurements else (0, 0)
    return {
        "window": {"homes": homes, "days": days},
        "bands_swept": len(measurements),
        "excluded": excluded_bands(),
        "measurements": [
            {
                "band": m.band,
                "direction": m.direction,
                "threshold": m.threshold,
                "anchor": m.anchor,
                "randomisation": m.randomisation,
                "scope": m.scope,
                "homes_judged": m.homes_judged,
                "draws": m.draws,
                "null_median": m.null_median,
                "null_p5": m.null_p5,
                "null_p95": m.null_p95,
                "null_spread": m.null_spread,
                "null_best": m.null_best,
                "margin": m.margin,
                "observed_median": m.observed_median,
                "observed_worst": m.observed_worst,
                "spread_readings": m.spread_readings,
                "caveat": m.caveat,
                "verdict": m.verdict.value,
                "note": m.note,
            }
            for m in measurements
        ],
    }
