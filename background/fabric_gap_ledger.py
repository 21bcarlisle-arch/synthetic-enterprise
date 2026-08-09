"""FABRIC belief-vs-truth GAP — the HARNESS leg of the fabric coupled triad
(atom `H_GAP_fabric_belief_truth_gap`; spec
`docs/design/PREMISE_TWO_LEVEL_TEST_HARNESS_SPEC.md`).

PURPOSE, GUARANTEES, WHY — stated first (OPS1 standard) or the mechanism is deleted
====================================================================================

**Purpose.** Make two questions *falsifiable, standing and automated*:

1. "Are these premise traces realistic?" — the TWO-LEVEL TEST: individual homes
   must be spiky, crowds must smooth. Today this is a question a director answered
   by eye in an afternoon (2026-08-03 house-usage review) and would have to
   re-answer six months later.
2. "How much does the company's fabric BELIEF differ from the world's fabric
   TRUTH, and what does that difference cost?" — the EPC-vs-actual and
   inferred-vs-actual gaps, and the MONEY CONSEQUENCE of deciding a fabric-targeted
   intervention on a belief instead of on the truth.

**Guarantee.** If the premise generator produces traces that are too smooth at the
individual level, insufficiently diverse at the crowd level, or unable to represent
an empty house, `evaluate_two_level` reports RED and names which level failed and on
which statistic — WORST CELL, never average, because an average across homes hides
the exact clone-cluster the test exists to find.

**Why it is needed, and why now.** `observed-in-code`: the pre-existing premise
controls (`simulation/premise_demand.py`: `reconciliation_residual`,
`aggregate_reconciles`, `noise_is_unbiased`) are genuine and R15-failable and are
ALL level-and-sum controls — blind to texture, timing, trough behaviour and
diversity. `W1_5_premise_demand_shape` therefore held L3 while failing both levels
of the by-eye test. The controls were not wrong; the control SET had a hole exactly
the shape of the defect. This module is the missing shape of control, and it is
deliberately NOT owned by either side it measures.

THIS MODULE HELPS NEITHER SIDE
------------------------------
It is HARNESS code and sits OUTSIDE the epistemic wall by design — the only place
permitted to hold the SIM's hidden fabric truth and the COMPANY's fabric belief side
by side (`COUPLED_TRIAD_DESIGN.md` §1.3, same standing as `background/gap_metric.py`).
It NEVER writes a gap, a truth or a band back into any `company/` path: the company
never sees its own score, and no statistic here is available to the generator as an
input. Nothing in `simulation/` or `company/` imports this module, and
`test_no_production_code_imports_the_harness` fails if that ever changes.

THE BIRTH CONDITION — the most important paragraph in this file
---------------------------------------------------------------
This suite was landed **RED against the generator that is actually in the demand
path**. A control introduced already-passing has demonstrated nothing (R15). Every
band below carries the value observed on the shipped path when it was written, so
the first run's failure was predicted, specific and checkable. Two generators exist
and they are judged by the SAME statistics:

* the SHIPPED demand path (`simulation.demand_model.build_demand_shape` rescaling a
  stored national PC1 shape) — the traces the business actually consumes today;
* `simulation.premise_trace.generate_premise_trace` (W1_12) — built but NOT yet
  wired into the demand path.

The distance between those two columns IS the value of wiring W1_12 in, expressed in
the units of the defect rather than in an assertion that it is better.

**If a statistic unexpectedly PASSES on the shipped path, the statistic is
mis-specified — fix the statistic, do not celebrate the pass.**

R12 / R13
---------
Every band here is a DIAGNOSTIC BAND, never a target. Drift toward a band edge
triggers R4 (diagnose the mechanism), never a tuning pass on the generator. This
suite is unusually easy to goal-seek because injecting per-period noise moves
`half_hourly_texture` without making anything more real — which is precisely why
`normalised_fraction_multiplicity` (L1.5) exists: it is STRUCTURAL, it detects the
rescaled-base-shape MECHANISM rather than its symptom, and it fails a noise-injected
fake even when the texture number passes. **L1.1 passing while L1.5 fails reads as
"someone tuned the number", and `evaluate_two_level` says so in those words.**
Bands are calibrated blind to company P&L (R13); this is baseline fidelity work.

THE THREE FAIL-OPEN PATTERNS, DEFENDED EXPLICITLY (R15 doctrine)
----------------------------------------------------------------
A statistical suite is unusually exposed to all three, so each is closed in code and
proven by a mutation test, not asserted in prose:

1. **FAIL-OPEN ON EMPTY INPUT.** A statistic over zero homes, zero days or a short
   trace RAISES `InsufficientEvidence`. It never returns a vacuous pass. Every
   statistic checks its own input sufficiency FIRST, before touching a value.
2. **NaN-BLINDNESS.** Comparison guards are NaN-blind (a known class in this
   codebase — `feedback_comparison_guards_are_nan_blind`). Every statistic rejects
   non-finite values BEFORE any threshold comparison, so a trace containing NaN is a
   FAILURE, not a pass.
3. **TAUTOLOGY.** No statistic is computed against a reference derived from the
   generator's own inputs. `smoothing_curve`'s large-N anchor is the published
   Elexon PC1 GAD shape, which is an INPUT to the shipped generator — so the shipped
   path's large-N limit is tautologically correct and that cell is reported as
   `TAUTOLOGICAL_FOR_THIS_GENERATOR` rather than as a pass. `pc1_is_an_input_to`
   makes the check mechanical instead of a review convention.

ANCHOR HONESTY
--------------
Bands that have a published anchor cite it. Bands that do not are declared
`AnchorStatus.NEED` and are reported as UNVALIDATED — they still compute and still
report their measured value, but they are excluded from the RED/GREEN verdict rather
than being given an invented threshold. A fabricated band would be worse than no
band: it would make the suite unfalsifiable while looking rigorous.

DETERMINISM (C-S2)
------------------
No wall-clock and no unseeded randomness. `measured_at` and `run_git_commit` are
passed IN by the caller. Any sampling draws from this module's OWN named substream.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Mapping, Sequence

from background.gap_metric import GapResult, prediction_gap, write_gap_entry

# HARNESS CROSSES THE WALL BY DESIGN — this module is the only layer permitted to
# hold the SIM's fabric truth and the company's belief together, and the decision it
# scores must be the COMPANY's own or it is scoring a fiction. Importing company code
# here is therefore correct; the reverse direction is what would be a violation, and
# `test_no_production_code_imports_the_harness` fails if it ever happens.
from company.pricing import fabric_intervention as fi
from company.pricing.thermal_inference import (
    EvidenceBasis,
    is_actionable_belief,
    log_normal_interval_95,
)

STREAM_NAME = "H_GAP_fabric_belief_truth_gap"

PERIODS_PER_DAY = 48

# Input sufficiency floors. Below these a statistic cannot be judged, so it RAISES
# rather than returning a number nobody should trust (fail-open pattern 1).
MIN_DAYS_FOR_TEXTURE = 28
MIN_DAYS_FOR_SEASONAL = 90
MIN_HOMES_FOR_DIVERSITY = 5
MIN_HOMES_FOR_SMOOTHING = 3


class InsufficientEvidence(ValueError):
    """Not enough input to judge this statistic. Raised, never swallowed —
    an unavailable check is a FAILED check (R15), not a pass."""


class NonFiniteTrace(ValueError):
    """A trace containing NaN or inf. A failure, never a pass."""


class AnchorStatus(str, Enum):
    """Whether a band is anchored to something outside this repository."""

    PUBLISHED = "published"       # a named external statistic
    DOMAIN_KNOWLEDGE = "domain"   # an order-of-magnitude physical/behavioural claim
    STRUCTURAL = "structural"     # no anchor needed — a self-evident artefact detector
    NEED = "need"                 # no anchor yet: measured and reported, NOT judged


class Verdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNVALIDATED = "unvalidated"                    # AnchorStatus.NEED — measured only
    TAUTOLOGICAL = "tautological_for_this_generator"


# ---------------------------------------------------------------------------
# Guards — these run FIRST, in every statistic, before any comparison
# ---------------------------------------------------------------------------


def _finite_series(values: Sequence[float], *, name: str) -> list[float]:
    """Reject non-finite values BEFORE any threshold comparison (fail-open
    pattern 2). `max(nan, x)` and `nan > t` are both silently False in Python,
    so a NaN reaching a comparison guard passes it."""
    out: list[float] = []
    for i, v in enumerate(values):
        f = float(v)
        if not math.isfinite(f):
            raise NonFiniteTrace(f"{name}[{i}] is {v!r} — a non-finite trace is a failure")
        out.append(f)
    return out


def _require_days(days: Sequence[Sequence[float]], *, minimum: int, name: str) -> list[list[float]]:
    """Input sufficiency FIRST (fail-open pattern 1), then finiteness."""
    if len(days) < minimum:
        raise InsufficientEvidence(
            f"{name} needs at least {minimum} days to judge; got {len(days)}"
        )
    out: list[list[float]] = []
    for d, day in enumerate(days):
        if len(day) != PERIODS_PER_DAY:
            raise InsufficientEvidence(
                f"{name}: day {d} has {len(day)} periods, expected {PERIODS_PER_DAY}"
            )
        out.append(_finite_series(day, name=f"{name} day {d}"))
    return out


def _require_homes(homes: Sequence, *, minimum: int, name: str) -> None:
    if len(homes) < minimum:
        raise InsufficientEvidence(
            f"{name} needs at least {minimum} homes to judge diversity; got {len(homes)}"
        )


def _pearson(a: Sequence[float], b: Sequence[float]) -> float:
    """Pearson r, returning 0.0 for a degenerate (zero-variance) input rather
    than raising — a flat day genuinely has no shape to correlate. Callers that
    need degeneracy to FAIL check it themselves."""
    n = len(a)
    if n != len(b) or n < 2:
        raise InsufficientEvidence("correlation needs two equal-length series of length >= 2")
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    if va <= 0.0 or vb <= 0.0:
        return 0.0
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return cov / math.sqrt(va * vb)


# ===========================================================================
# LEVEL 1 — individual homes must be SPIKY
# ===========================================================================


def half_hourly_texture(days: Sequence[Sequence[float]]) -> float:
    """L1.1 — median |x[t] - x[t-1]| over the whole window, divided by mean(x).

    Dimensionless, so a big house and a small house are judged the same way.
    Steps are taken WITHIN each day and across the midnight boundary, because a
    generator that is smooth inside the day but jumps at midnight is not spiky,
    it is discontinuous.
    """
    grid = _require_days(days, minimum=MIN_DAYS_FOR_TEXTURE, name="half_hourly_texture")
    flat = [v for day in grid for v in day]
    mean = sum(flat) / len(flat)
    if mean <= 0.0:
        raise InsufficientEvidence("a trace with non-positive mean has no texture to measure")
    steps = [abs(flat[i] - flat[i - 1]) for i in range(1, len(flat))]
    return statistics.median(steps) / mean


def day_to_day_shape_correlation(days: Sequence[Sequence[float]]) -> float:
    """L1.2 — median Pearson r between CONSECUTIVE days' 48-vectors, each
    normalised to its own daily total.

    The normalisation is what makes this a test of SHAPE rather than of weather:
    two cold days in a row legitimately have similar levels, but a real home does
    not run the same half-hourly pattern twice. Days with a zero total are skipped
    (an all-zero day has no shape), and if that leaves too few pairs the statistic
    RAISES rather than reporting a correlation over a handful of days.
    """
    grid = _require_days(days, minimum=MIN_DAYS_FOR_TEXTURE, name="day_to_day_shape_correlation")
    shapes: list[list[float]] = []
    for day in grid:
        total = sum(day)
        shapes.append([v / total for v in day] if total > 0.0 else [])
    rs = [
        _pearson(shapes[i - 1], shapes[i])
        for i in range(1, len(shapes))
        if shapes[i - 1] and shapes[i]
    ]
    if len(rs) < MIN_DAYS_FOR_TEXTURE - 1:
        raise InsufficientEvidence(
            f"day_to_day_shape_correlation got only {len(rs)} usable consecutive-day pairs"
        )
    return statistics.median(rs)


@dataclass(frozen=True)
class TroughStats:
    """L1.3 — can this generator represent an EMPTY HOUSE?"""

    min_half_hour_kwh: float
    away_signature_days: int     # days whose daytime is no busier than their own 3am
    days_observed: int
    worst_signature: float       # the most empty-looking day this home ever had

    @property
    def away_days_per_year(self) -> float:
        return self.away_signature_days / self.days_observed * 365.25


# 00:00-06:00 — the base-load window, when a home is quiet whether or not anyone
# is in it. 08:00-22:00 — the active window, when an OCCUPIED home is not.
BASE_LOAD_PERIODS = range(0, 12)
ACTIVE_PERIODS = range(16, 44)

# "No busier by day than at 3am" — a ratio of 1.0 means the active window and the
# base-load window are indistinguishable, which is what an empty house looks like.
AWAY_SIGNATURE_MAX = 1.30


def away_signature(day: Sequence[float]) -> float:
    """Mean active-window consumption divided by mean base-load consumption, for
    one day.

    ~1.0 = nobody was home. ~3.0+ = an ordinary occupied day.

    WHY NOT THE SPEC'S ORIGINAL STATISTIC. The spec (§1, L1.3) defined this as
    "count of days with >= 6 consecutive periods below a low-usage threshold".
    That statistic was BUILT, MEASURED, and found to be **backwards**: measured on
    the real archive it scored the shipped rescaled-PC1 path at 7 consecutive low
    periods per day and `premise_trace` at 1, i.e. it would have PASSED the smooth
    generator and FAILED the spiky one. Two reasons, both physical: (a) every home
    is at base load overnight whether or not it is occupied, so a run-length test
    counts nights, not absences; and (b) an empty house's fridge CYCLES, so its
    trace oscillates across any fixed threshold and never accumulates a long run —
    the spikier and more honest the generator, the shorter its runs.

    The spec's own instruction covers this exactly: "if any statistic unexpectedly
    passes on the current generator, that statistic is mis-specified — fix the
    statistic, do not celebrate the pass." This is the fixed statistic. It asks the
    physical question the spec was reaching for (is an empty house REPRESENTABLE)
    in a form that a cycling base load cannot defeat.
    """
    base = [v for i, v in enumerate(day) if i in BASE_LOAD_PERIODS]
    active = [v for i, v in enumerate(day) if i in ACTIVE_PERIODS]
    base_mean = sum(base) / len(base)
    if base_mean <= 0.0:
        # A home with zero overnight base load is not physical (the fridge is
        # always running). Return inf so it can never be counted as an away day.
        return math.inf
    return (sum(active) / len(active)) / base_mean


def trough_statistics(
    days: Sequence[Sequence[float]], *, signature_max: float = AWAY_SIGNATURE_MAX
) -> TroughStats:
    """L1.3 — the minimum half-hour, and the count of days on which this home was
    demonstrably empty.

    The threshold is derived from occupancy PHYSICS (a day no busier than its own
    3am) and from each home's OWN trace, never from the generator's parameters —
    so it does not re-tautologise the check.
    """
    if not math.isfinite(signature_max) or signature_max <= 1.0:
        raise InsufficientEvidence(
            "the away signature threshold must be finite and greater than 1.0"
        )
    grid = _require_days(days, minimum=MIN_DAYS_FOR_TEXTURE, name="trough_statistics")
    signatures = [away_signature(day) for day in grid]
    return TroughStats(
        min_half_hour_kwh=min(v for day in grid for v in day),
        away_signature_days=sum(1 for s in signatures if s < signature_max),
        days_observed=len(grid),
        worst_signature=min(signatures),
    )


def weekday_weekend_separation(
    days: Sequence[Sequence[float]], is_weekend: Sequence[bool]
) -> float:
    """L1.4 — how far apart the mean weekday shape and mean weekend shape are,
    measured as total-variation distance between the two normalised 48-vectors.

    0.0 means the two day types are indistinguishable. Reported per home, because
    the defect this exists to catch is not "no weekday/weekend difference" but "the
    SAME weekday/weekend difference in every home in the country".
    """
    grid = _require_days(days, minimum=MIN_DAYS_FOR_TEXTURE, name="weekday_weekend_separation")
    if len(is_weekend) != len(grid):
        raise InsufficientEvidence("day-type flags must align with the trace days")
    weekday = [d for d, w in zip(grid, is_weekend) if not w]
    weekend = [d for d, w in zip(grid, is_weekend) if w]
    if len(weekday) < 5 or len(weekend) < 5:
        raise InsufficientEvidence(
            f"need >= 5 of each day type; got {len(weekday)} weekday / {len(weekend)} weekend"
        )

    def mean_shape(block: list[list[float]]) -> list[float]:
        totals = [sum(d) for d in block]
        usable = [(d, t) for d, t in zip(block, totals) if t > 0.0]
        if not usable:
            raise InsufficientEvidence("every day of one type is empty — no shape to compare")
        acc = [0.0] * PERIODS_PER_DAY
        for d, t in usable:
            for p in range(PERIODS_PER_DAY):
                acc[p] += d[p] / t
        return [a / len(usable) for a in acc]

    a, b = mean_shape(weekday), mean_shape(weekend)
    return 0.5 * sum(abs(x - y) for x, y in zip(a, b))


@dataclass(frozen=True)
class FractionMultiplicity:
    """L1.5 — the sharpest control in the suite. It detects the MECHANISM of the
    defect (one deterministic base shape, rescaled per day) rather than its
    symptom, so it cannot be passed by sprinkling noise on the current
    architecture — only by actually generating shape per home."""

    max_multiplicity: int
    distinct_fractions: int
    total_fractions: int
    days_observed: int

    @property
    def repeat_rate(self) -> float:
        """Fraction of normalised values that are NOT unique. Reported as a
        component; NOT the judged statistic, because a home sitting at a flat base
        load repeats values WITHIN a day quite honestly."""
        return 1.0 - self.distinct_fractions / self.total_fractions

    @property
    def max_multiplicity_share(self) -> float:
        """THE judged statistic: the most-repeated normalised fraction's count,
        divided by the number of days observed.

        A generator that rescales a fixed base shape by a daily scalar reproduces
        every one of its base fractions on EVERY day, because the scalar cancels
        exactly in ``x[t] / daily_total`` — so this lands at >= 1.0 by
        construction, no matter how much level noise is added on top. A generator
        that produces shape per home per day lands near zero.

        `observed 2026-08-03 on the real archive`: shipped rescaled-PC1 path
        **2.00** (each base fraction recurs twice a day, every day, for 120 days);
        `premise_trace` **0.042**. Two orders of magnitude apart on a statistic
        with no tunable parameter.
        """
        return self.max_multiplicity / self.days_observed


def normalised_fraction_multiplicity(
    days: Sequence[Sequence[float]], *, decimals: int = 6
) -> FractionMultiplicity:
    """L1.5 — count distinct values of ``x[t] / daily_total`` across the window
    and the maximum multiplicity of any one value.

    Any generator that rescales a fixed base shape by daily scalars produces a
    small set of repeated normalised fractions no matter how much LEVEL noise is
    added, because the division cancels the scalar exactly. This is structural and
    deterministic; it needs no anchor and is near-impossible to game.

    Zero fractions are excluded: a genuinely-off period is a legitimate repeat
    (an empty house repeats 0.0 honestly), and counting them would let a
    mostly-zero trace fail for the wrong reason.
    """
    grid = _require_days(days, minimum=MIN_DAYS_FOR_TEXTURE, name="normalised_fraction_multiplicity")
    counts: dict[float, int] = {}
    total = 0
    usable_days = 0
    for day in grid:
        day_total = sum(day)
        if day_total <= 0.0:
            continue
        usable_days += 1
        for v in day:
            frac = round(v / day_total, decimals)
            if frac == 0.0:
                continue
            counts[frac] = counts.get(frac, 0) + 1
            total += 1
    if total == 0 or usable_days == 0:
        raise InsufficientEvidence("no non-zero normalised fractions — nothing to judge")
    return FractionMultiplicity(
        max_multiplicity=max(counts.values()),
        distinct_fractions=len(counts),
        total_fractions=total,
        days_observed=usable_days,
    )


# ===========================================================================
# LEVEL 2 — crowds must SMOOTH
# ===========================================================================

SMOOTHING_NS = (1, 3, 5, 10, 30, 100, 300, 1000)


def peak_to_mean(series: Sequence[float]) -> float:
    flat = _finite_series(series, name="peak_to_mean")
    if not flat:
        raise InsufficientEvidence("an empty series has no peak/mean")
    mean = sum(flat) / len(flat)
    if mean <= 0.0:
        raise InsufficientEvidence("a series with non-positive mean has no peak/mean")
    return max(flat) / mean


def smoothing_curve(
    homes: Sequence[Sequence[Sequence[float]]], ns: Sequence[int] = SMOOTHING_NS
) -> dict[int, float]:
    """L2.1 — aggregate peak÷mean as a function of the number of homes N.

    Homes are aggregated in the order given (the caller is responsible for the
    population draw), and each N uses the first N homes so the curve is nested and
    monotonic movement is attributable to aggregation rather than to resampling.
    Ns larger than the population are skipped rather than silently clamped — a
    clamp would report an N=1000 result computed on 9 homes.
    """
    _require_homes(homes, minimum=MIN_HOMES_FOR_SMOOTHING, name="smoothing_curve")
    grids = [
        _require_days(h, minimum=MIN_DAYS_FOR_TEXTURE, name=f"smoothing_curve home {i}")
        for i, h in enumerate(homes)
    ]
    length = min(len(g) for g in grids)
    out: dict[int, float] = {}
    for n in ns:
        if n > len(grids):
            continue
        aggregate = [0.0] * (length * PERIODS_PER_DAY)
        for g in grids[:n]:
            k = 0
            for day in g[:length]:
                for v in day:
                    aggregate[k] += v
                    k += 1
        out[n] = peak_to_mean(aggregate)
    if len(out) < 2:
        raise InsufficientEvidence("a smoothing curve needs at least two population sizes")
    return out


def smoothing_ratio(curve: Mapping[int, float]) -> float:
    """The headline number from L2.1: peak/mean at the largest N divided by
    peak/mean at N=1. 1.0 means aggregation smooths NOTHING."""
    if 1 not in curve:
        raise InsufficientEvidence("the smoothing curve must include N=1 as its reference")
    largest = max(curve)
    if largest == 1:
        raise InsufficientEvidence("a smoothing ratio needs an N greater than 1")
    if curve[1] <= 0.0:
        raise InsufficientEvidence("the N=1 peak/mean must be positive")
    return curve[largest] / curve[1]


def _detrend_on_driver(series: Sequence[float], driver: Sequence[float]) -> list[float]:
    """OLS residual of `series` on `driver` — an ordinary least-squares fit with
    intercept, returned as the residual. A driver with no variance leaves the
    series alone (mean-centred), which is the honest behaviour: nothing was
    explained, so nothing is removed."""
    n = len(series)
    mean_x = sum(driver) / n
    mean_y = sum(series) / n
    sxx = sum((x - mean_x) ** 2 for x in driver)
    slope = (
        sum((x - mean_x) * (y - mean_y) for x, y in zip(driver, series)) / sxx
        if sxx > 0.0
        else 0.0
    )
    intercept = mean_y - slope * mean_x
    return [y - (intercept + slope * x) for y, x in zip(series, driver)]


def between_home_correlation(
    homes: Sequence[Sequence[Sequence[float]]],
    weather_driver: Sequence[float],
) -> float:
    """L2.2 — median pairwise Pearson r between homes' WEATHER-CONDITIONED daily
    residuals.

    Weather is a legitimate common mode: every home in a region gets cold on the
    same day, so raw correlation is high even for a perfect generator. Each home's
    daily-total series is therefore regressed on `weather_driver` (heating degree
    days off the real archive) and the correlation is measured on what is LEFT —
    which is where genuine household diversity lives.

    THE DRIVER IS EXTERNAL, AND THAT IS THE POINT. An earlier version of this
    statistic de-trended on the POPULATION'S OWN MEAN daily series, and it was
    wrong in a way worth recording. Residuals from a population mean sum to zero by
    construction, so for a population of near-clones the residuals are exactly
    anti-correlated: measured on the shipped path it returned **-0.98** and PASSED
    a band meant to catch clones. It scored maximum diversity on the most cloned
    population available. Fixed by regressing on an EXTERNAL driver, whose
    residuals carry no such constraint: on the shipped path homes differ only by a
    scalar volume factor, so their de-weathered residuals stay near +1.

    Measured on daily totals rather than half-hourly values because the question is
    "do these behave like different households", and half-hourly correlation is
    dominated by the shared diurnal cycle, which is also legitimate.
    """
    _require_homes(homes, minimum=MIN_HOMES_FOR_DIVERSITY, name="between_home_correlation")
    dailies: list[list[float]] = []
    for i, h in enumerate(homes):
        grid = _require_days(h, minimum=MIN_DAYS_FOR_TEXTURE, name=f"between_home_correlation home {i}")
        dailies.append([sum(day) for day in grid])
    length = min(len(d) for d in dailies)
    driver = _finite_series(weather_driver, name="weather_driver")
    if len(driver) < length:
        raise InsufficientEvidence(
            f"the weather driver spans {len(driver)} days but the homes span {length}"
        )
    driver = driver[:length]
    residuals = [_detrend_on_driver(d[:length], driver) for d in dailies]

    rs: list[float] = []
    for i in range(len(residuals)):
        for j in range(i + 1, len(residuals)):
            rs.append(_pearson(residuals[i], residuals[j]))
    return statistics.median(rs)


def evening_peak_period(days: Sequence[Sequence[float]]) -> float:
    """The mean half-hour index of a home's evening (periods 30-46) maximum."""
    grid = _require_days(days, minimum=MIN_DAYS_FOR_TEXTURE, name="evening_peak_period")
    window = range(29, 46)
    picks: list[int] = []
    for day in grid:
        best = max(window, key=lambda p: day[p])
        if day[best] > 0.0:
            picks.append(best)
    if not picks:
        raise InsufficientEvidence("no day has any evening usage — no peak timing to measure")
    return sum(picks) / len(picks)


def timing_diversity(homes: Sequence[Sequence[Sequence[float]]]) -> float:
    """L2.3 — the population standard deviation, in HALF-HOURS, of each home's
    mean evening-peak period.

    0.0 is a point mass: every home in the country peaks in the same half-hour,
    which is what one national `HEATING_PERIOD_WEIGHTS` constant produces.
    """
    _require_homes(homes, minimum=MIN_HOMES_FOR_DIVERSITY, name="timing_diversity")
    peaks = [evening_peak_period(h) for h in homes]
    return statistics.pstdev(peaks)


@dataclass(frozen=True)
class ScaleSpread:
    """L2.4 — how far apart are the homes' annual totals?"""

    p90_over_p10: float
    iqr_ratio: float
    annual_kwh: tuple[float, ...]


def scale_spread(annual_kwh: Sequence[float]) -> ScaleSpread:
    values = sorted(_finite_series(annual_kwh, name="scale_spread"))
    if len(values) < MIN_HOMES_FOR_DIVERSITY:
        raise InsufficientEvidence(
            f"scale_spread needs at least {MIN_HOMES_FOR_DIVERSITY} homes; got {len(values)}"
        )
    if values[0] <= 0.0:
        raise InsufficientEvidence("a home with non-positive annual consumption is not judgeable")

    def quantile(q: float) -> float:
        pos = q * (len(values) - 1)
        lo = int(math.floor(pos))
        hi = min(lo + 1, len(values) - 1)
        return values[lo] + (values[hi] - values[lo]) * (pos - lo)

    p10, p90 = quantile(0.10), quantile(0.90)
    q1, q3 = quantile(0.25), quantile(0.75)
    return ScaleSpread(
        p90_over_p10=p90 / p10, iqr_ratio=q3 / q1, annual_kwh=tuple(values)
    )


# ===========================================================================
# TAUTOLOGY guard (fail-open pattern 3)
# ===========================================================================

PC1_INPUT_MARKERS = ("load_pc1_shape", "profile_class_1")


def pc1_is_an_input_to(builder) -> bool:
    """True if the published PC1 GAD shape is an INPUT to this generation path.

    L2.1's large-N anchor is PC1. For a path that CONSUMES PC1, comparing its
    large-N limit to PC1 is a tautology — it would pass even if every individual
    home in it were physically absurd. Mechanical, not a review convention.

    `builder` MUST be a population-builder FUNCTION, and both halves of that
    restriction were learned by building this:

    * NOT a module, because `demand_model.build_demand_shape` does not import PC1
      at all — it takes `base_shape` as an argument and the caller supplies
      `load_pc1_shape(date)`. An import-level check on that module returns False
      for the very path whose entire base shape IS the published national profile.
    * NOT a module, ALSO because scanning a module's full text for the marker
      returns True off a docstring that merely MENTIONS `sim.profile_class_1` —
      which `demand_model` does. Widening the scan to fix the first problem
      manufactured the opposite error.

    The tautology lives in the WIRING, and a builder function is small enough for
    a source scan to be exact rather than approximate. Passing anything else
    RAISES: refusing to make an imprecise claim is better than making one, and an
    unavailable check is a FAILED check (R15).
    """
    import inspect

    if not (inspect.isfunction(builder) or inspect.ismethod(builder)):
        raise InsufficientEvidence(
            f"pc1_is_an_input_to needs a population-builder FUNCTION, got {builder!r} — "
            "a module-level scan is either import-blind or docstring-fooled"
        )
    try:
        text = inspect.getsource(builder)
    except (OSError, TypeError) as exc:
        raise InsufficientEvidence(
            f"cannot read the source of {builder!r} ({exc}) — an unavailable check is "
            "a FAILED check"
        ) from exc
    return any(marker in text for marker in PC1_INPUT_MARKERS)


# ===========================================================================
# BANDS and the two-level verdict
# ===========================================================================


@dataclass(frozen=True)
class Band:
    """A DIAGNOSTIC band (R12), never a target.

    `observed_on_shipped` is the value measured on the shipped demand path when
    this band was written. It is recorded so the RED birth condition is checkable
    by anyone re-reading the file, and so drift is visible without re-deriving it.
    """

    statistic: str
    level: str
    direction: str            # "at_least" | "at_most"
    threshold: float | None   # None when AnchorStatus.NEED — measured, not judged
    anchor: AnchorStatus
    anchor_source: str
    observed_on_shipped: float | None
    rationale: str

    def judge(self, value: float) -> Verdict:
        if not math.isfinite(value):
            # Non-finite reaches a verdict as a FAILURE, never as a pass. Both
            # comparisons below are silently False for NaN.
            return Verdict.FAIL
        if self.anchor is AnchorStatus.NEED or self.threshold is None:
            return Verdict.UNVALIDATED
        if self.direction == "at_least":
            return Verdict.PASS if value >= self.threshold else Verdict.FAIL
        if self.direction == "at_most":
            return Verdict.PASS if value <= self.threshold else Verdict.FAIL
        raise ValueError(f"unknown band direction {self.direction!r}")


# ---------------------------------------------------------------------------
# The L1.1 texture band is HEATING-SYSTEM CONDITIONED, and the second band is
# DERIVED from published sources rather than declared
# ---------------------------------------------------------------------------
#
# WHY THERE ARE TWO. L1.1 is `median |x[t] - x[t-1]| / mean(x)` — a RATIO to the
# home's own mean. A heat pump puts a large, thermally-driven, slowly-varying
# load into the DENOMINATOR while adding almost nothing to the numerator, so an
# electrically-heated home is arithmetically smoother in relative terms than a
# gas-heated home with identical appliance behaviour. Judging both against one
# national floor is the same one-national-constant defect W1_12 exists to
# remove, reappearing in the CONTROL rather than in the generator
# (`docs/staging/WORKER_FINDING_L1_TEXTURE_BAND_IS_GAS_SHAPED_2026-08-08.md`,
# where the whole of the failing home's deficit was decomposed to the denominator).
#
# WHERE THE ELECTRIC THRESHOLD COMES FROM. Not from the generator, and not from
# a judgement about what would make it pass — from four published figures and one
# division. Each is a constant below so the arithmetic is RE-DERIVABLE in a test
# and a change to any input is visible in a diff rather than buried in prose.
_GAS_TEXTURE_THRESHOLD = 0.15

# Ofgem, Typical Domestic Consumption Values applying from 1 July 2026 (medium
# band). The electricity TDCV is for a home that is NOT electrically heated, so
# it is exactly the behavioural/appliance baseline this derivation needs.
# Recorded in `docs/market_research/ons_consumption_profiles.md`.
_TDCV_ELECTRICITY_MEDIUM_KWH = 2500.0
_TDCV_GAS_MEDIUM_KWH = 9500.0

# Energy Saving Trust / DECC, "In-situ monitoring of efficiencies of condensing
# boilers" final report: mean MEASURED in-situ efficiency of the trial set of
# COMBINATION boilers = 82.5% (sd 4.0%) against a SEDBUK rating of 90.4%. Combi
# is the right figure here because every gas home in the fabric panel is
# GAS_BOILER_COMBI.
_COMBI_BOILER_IN_SITU_EFFICIENCY = 0.825

# DESNZ / Energy Systems Catapult, Electrification of Heat demonstration project
# summary report: median ASHP SPFH4 = 2.78, IQR [2.55, 3.05], n=428.
_ASHP_MEDIAN_SPFH4 = 2.78


def electric_heat_texture_threshold() -> float:
    """The L1.1 band for an electrically-heated home, derived not declared.

    Gas TDCV -> useful heat at the measured in-situ combi efficiency -> the
    electricity an ASHP needs to deliver that heat at the measured median SPFH4.
    The heat pump's share of total household electricity follows, and the band is
    the gas band scaled by what is LEFT for behaviour:

        heat        = 9500 * 0.825            = 7837.5 kWh/yr
        hp_elec     = 7837.5 / 2.78           = 2818.9 kWh/yr
        behav_share = 2500 / (2500 + 2818.9)  = 0.4700
        band        = 0.15 * 0.4700           = 0.0705

    CONSERVATIVE BY CONSTRUCTION, and this is the assumption to attack first: the
    scaling credits the heat pump with ZERO period-to-period movement, so it is a
    LOWER bound on what a correct electrically-heated home should show in an
    `at_least` direction. A real ASHP cycles, so a correct generator clears this
    band with room; a generator that is smooth by construction still cannot.

    NOT A TAUTOLOGY (R15): every input is external to this repository's
    generators, and none of them is measured on a trace. Sensitivity across the
    published spreads, taken JOINTLY at their corners — SPFH4 over its IQR
    [2.55, 3.05] crossed with boiler efficiency over +/-1sd [0.785, 0.865] — moves
    the band across 0.0655-0.0758, so the number does not rest on any one point
    estimate. `test_the_electric_band_is_ROBUST_across_the_published_spreads`
    pins that envelope.
    """
    heat_kwh = _TDCV_GAS_MEDIUM_KWH * _COMBI_BOILER_IN_SITU_EFFICIENCY
    heat_pump_electricity_kwh = heat_kwh / _ASHP_MEDIAN_SPFH4
    behavioural_share = _TDCV_ELECTRICITY_MEDIUM_KWH / (
        _TDCV_ELECTRICITY_MEDIUM_KWH + heat_pump_electricity_kwh
    )
    return _GAS_TEXTURE_THRESHOLD * behavioural_share


# The bands. Every `observed_on_shipped` value below was MEASURED on the shipped
# demand path (`tests/harness/test_premise_two_level.py::test_MEASURED_shipped_path_values`), not estimated.
BANDS: dict[str, Band] = {
    "L1.1_half_hourly_texture": Band(
        statistic="L1.1_half_hourly_texture",
        level="L1",
        direction="at_least",
        threshold=_GAS_TEXTURE_THRESHOLD,
        anchor=AnchorStatus.DOMAIN_KNOWLEDGE,
        anchor_source=(
            "domain-knowledge, and it reasons from a GAS-HEATED premise: real "
            "individual-home half-hourly electricity moves in "
            "the tens of percent of its own mean between adjacent periods (a kettle is "
            "2.8 kW for three minutes on a ~0.7 kWh half-hour). The SERL/LCL published "
            "band is NOT yet in the artefact library, so the threshold is set at 0.15 — "
            "below the low end of the 20-40% domain expectation, deliberately "
            "loose so that it can only fire on a generator that is smooth by "
            "construction rather than on one that is merely at the calm end of real. "
            "APPLIES TO NON-ELECTRICALLY-HEATED HOMES ONLY — the kettle-on-a-0.7-kWh-"
            "half-hour reasoning is a statement about the denominator, and an "
            "electrically-heated home has a different one. See "
            "L1.1e_half_hourly_texture_electric_heat."
        ),
        observed_on_shipped=None,
        rationale=(
            "A rescaled national average has the texture of a national average, which "
            "is the texture of a hundred thousand homes already summed."
        ),
    ),
    "L1.1e_half_hourly_texture_electric_heat": Band(
        statistic="L1.1e_half_hourly_texture_electric_heat",
        level="L1",
        direction="at_least",
        threshold=electric_heat_texture_threshold(),
        anchor=AnchorStatus.PUBLISHED,
        anchor_source=(
            "published, derived — Ofgem Typical Domestic Consumption Values from "
            "1 July 2026 (medium: electricity 2,500 kWh/yr for a non-electrically-"
            "heated home, gas 9,500 kWh/yr); Energy Saving Trust/DECC 'In-situ "
            "monitoring of efficiencies of condensing boilers' final report, mean "
            "measured in-situ efficiency of the trial COMBINATION boilers 82.5% "
            "(sd 4.0%, vs SEDBUK 90.4%); DESNZ/Energy Systems Catapult Electrification "
            "of Heat demonstration project summary report, median ASHP SPFH4 = 2.78 "
            "(IQR [2.55, 3.05], n=428). Those give a heat-pump share of household "
            "electricity of 53.0%, so the behavioural stream carries 47.0% of the "
            "mean that L1.1 divides by. See `electric_heat_texture_threshold` for "
            "the arithmetic and its sensitivity (0.0655-0.0758 across the joint "
            "corners of the published spreads). NOT a relaxation of the gas band "
            "and not set by looking at "
            "what any generator scores: the ratio of the two bands is the ratio of "
            "the two denominators, and nothing else."
        ),
        observed_on_shipped=None,
        rationale=(
            "The shipped path has no electrically-heated home to observe — it "
            "rescales one national PC1 shape regardless of heating system, which is "
            "the defect. A heat pump is a large slowly-varying load in the "
            "DENOMINATOR of a ratio-to-own-mean statistic, so the same appliance "
            "behaviour scores lower in an ASHP home than in a gas home. Judging both "
            "with one national floor would fail a correct generator for being "
            "correct."
        ),
    ),
    "L1.2_day_to_day_shape_correlation": Band(
        statistic="L1.2_day_to_day_shape_correlation",
        level="L1",
        direction="at_most",
        threshold=0.85,
        anchor=AnchorStatus.DOMAIN_KNOWLEDGE,
        anchor_source=(
            "domain-knowledge: a household does not repeat its half-hourly pattern "
            "day to day — meals, showers and departures move by tens of minutes. The "
            "threshold is set at 0.85, well above any plausible real value, so it "
            "fires only on near-replay. A SERL-anchored band is registered as NEED."
        ),
        observed_on_shipped=None,
        rationale="Normalised to the daily total, so this is shape, not weather.",
    ),
    "L1.3_away_days_per_year": Band(
        statistic="L1.3_away_days_per_year",
        level="L1",
        direction="at_least",
        threshold=1.0,
        anchor=AnchorStatus.DOMAIN_KNOWLEDGE,
        anchor_source=(
            "domain-knowledge: UK households take holidays; a home that is never once "
            "in a year no busier by day than it is at 3am cannot represent an empty "
            "house AT ALL. The threshold is the weakest possible non-vacuous one — at "
            "least ONE such day per year — because the defect is structural "
            "(impossible), not quantitative (too few). An ONS/BEIS holiday-taking band "
            "for the RATE is registered as NEED. The 1.30 signature cutoff sits in a "
            "wide empty gap measured on the real archive (away days 1.00-1.03, the "
            "quietest occupied day 1.56), so it is not knife-edge."
        ),
        observed_on_shipped=0.0,
        rationale="Representability first; the rate is a separate, unanchored question.",
    ),
    "L1.4_weekday_weekend_separation": Band(
        statistic="L1.4_weekday_weekend_separation",
        level="L1",
        direction="at_least",
        threshold=None,
        anchor=AnchorStatus.NEED,
        anchor_source=(
            "NEED — SERL weekday/weekend shape statistics. Measured and reported, NOT "
            "judged. The defect this targets is not absence of a weekday/weekend "
            "difference but IDENTITY of that difference across homes, which is "
            "captured by L2.3 timing diversity; giving this cell an invented "
            "threshold would make the suite look rigorous while being unfalsifiable."
        ),
        observed_on_shipped=None,
        rationale="Present but identical for every home is the real defect — see L2.3.",
    ),
    "L1.5_max_multiplicity_share": Band(
        statistic="L1.5_max_multiplicity_share",
        level="L1",
        direction="at_most",
        threshold=0.10,
        anchor=AnchorStatus.STRUCTURAL,
        anchor_source=(
            "No anchor needed — a self-evident artefact detector with no tunable "
            "parameter. A generator that rescales a fixed base shape reproduces every "
            "base fraction on EVERY day (the daily scalar cancels in x[t]/daily_total), "
            "so its most-repeated fraction recurs at least once per day and the share "
            "is >= 1.0 by construction. A generator that produces shape per home per "
            "day lands near zero. The 0.10 threshold is an order of magnitude clear of "
            "BOTH measured values, so it is not a close call in either direction."
        ),
        observed_on_shipped=2.0,
        rationale=(
            "THE structural guard against goal-seeking: injecting level noise moves "
            "L1.1 without moving this, so L1.1-pass-with-L1.5-fail reads as tuning. "
            "Judged on max multiplicity per day rather than on the raw repeat rate, "
            "because a home sitting at a flat base load repeats values WITHIN a day "
            "quite honestly — measured, the raw repeat rate scored premise_trace at "
            "0.14 for exactly that innocent reason while the shipped path scored 0.96."
        ),
    ),
    "L2.1_smoothing_ratio": Band(
        statistic="L2.1_smoothing_ratio",
        level="L2",
        direction="at_most",
        threshold=0.85,
        anchor=AnchorStatus.DOMAIN_KNOWLEDGE,
        anchor_source=(
            "domain-knowledge / diversity-factor physics: aggregating independent "
            "households MUST reduce peak-to-mean — that is what a diversity factor "
            "IS, and it is why a national profile is smooth while a house is not. "
            "The threshold asks only for a 15% reduction by the largest measured N, "
            "far weaker than the real drop, so it fires only when aggregation "
            "smooths essentially nothing."
        ),
        observed_on_shipped=None,
        rationale="peak/mean at max N divided by peak/mean at N=1. 1.0 = no smoothing.",
    ),
    "L2.2_between_home_correlation": Band(
        statistic="L2.2_between_home_correlation",
        level="L2",
        direction="at_most",
        threshold=0.60,
        anchor=AnchorStatus.DOMAIN_KNOWLEDGE,
        anchor_source=(
            "domain-knowledge: measured on the residual from an EXTERNAL weather "
            "driver (heating degree days off the real archive), so shared weather is "
            "already removed and no population-derived constraint is imposed on the "
            "residuals. Two homes whose de-weathered daily totals still correlate "
            "above 0.6 are near-clones. A SERL diversity-statistics band is NEED."
        ),
        observed_on_shipped=None,
        rationale="Residual on an external driver — see the note in the statistic.",
    ),
    "L2.3_timing_diversity_periods": Band(
        statistic="L2.3_timing_diversity_periods",
        level="L2",
        direction="at_least",
        threshold=0.5,
        anchor=AnchorStatus.DOMAIN_KNOWLEDGE,
        anchor_source=(
            "domain-knowledge: households do not all peak in the same half-hour. The "
            "threshold asks for a population sd of at least half a settlement period "
            "— the weakest possible non-point-mass — because the shipped defect is a "
            "single national constant, i.e. an exact point mass at 0.0."
        ),
        observed_on_shipped=None,
        rationale="One national HEATING_PERIOD_WEIGHTS constant is a point mass.",
    ),
    "L2.4_scale_spread_p90_p10": Band(
        statistic="L2.4_scale_spread_p90_p10",
        level="L2",
        direction="at_least",
        threshold=None,
        anchor=AnchorStatus.NEED,
        anchor_source=(
            "NEED — NEED (the DESNZ National Energy Efficiency Data-Framework) "
            "EPC-linked actual metered annual consumption by property type and floor "
            "area band. Measured and reported, NOT judged. Note the shipped path's "
            "8% spread is visibly wrong against any plausible band, but 'visibly "
            "wrong' is not a threshold, and inventing one here would be exactly the "
            "unfalsifiable-rigour failure this file refuses elsewhere."
        ),
        observed_on_shipped=None,
        rationale="Real UK homes span several-fold in annual kWh across the stock.",
    ),
}


# The R12 goal-seek pair, named once so a rename cannot silently desync the
# warning from the bands (it did exactly that once — see `goal_seek_warning`).
TEXTURE_STATISTIC = "L1.1_half_hourly_texture"
STRUCTURAL_STATISTIC = "L1.5_max_multiplicity_share"


@dataclass(frozen=True)
class CellResult:
    statistic: str
    level: str
    value: float
    verdict: Verdict
    band: Band
    note: str = ""


@dataclass(frozen=True)
class TwoLevelResult:
    """The suite's verdict. WORST CELL, never average — an average across homes
    would hide the exact clone-cluster the test exists to find."""

    generator: str
    cells: tuple[CellResult, ...]
    homes: int
    days: int

    @property
    def failed(self) -> tuple[CellResult, ...]:
        return tuple(c for c in self.cells if c.verdict is Verdict.FAIL)

    @property
    def unvalidated(self) -> tuple[CellResult, ...]:
        return tuple(c for c in self.cells if c.verdict is Verdict.UNVALIDATED)

    @property
    def is_red(self) -> bool:
        return bool(self.failed)

    def cell(self, statistic: str) -> CellResult:
        for c in self.cells:
            if c.statistic == statistic:
                return c
        raise KeyError(statistic)

    def failed_levels(self) -> tuple[str, ...]:
        return tuple(sorted({c.level for c in self.failed}))

    def goal_seek_warning(self) -> str | None:
        """R12. If the texture number passes while the structural artefact
        detector fails, the texture number was tuned. Say so in those words."""
        try:
            texture = self.cell(TEXTURE_STATISTIC)
            structural = self.cell(STRUCTURAL_STATISTIC)
        except KeyError:
            # A partial result (one cell, a synthetic fixture) legitimately has
            # neither. A STALE NAME does not: `test_the_goal_seek_pair_names_are_
            # live_band_keys` fails if either constant stops matching a real band,
            # which is exactly how this method was caught silently returning None
            # after L1.5 was renamed.
            return None
        if texture.verdict is Verdict.PASS and structural.verdict is Verdict.FAIL:
            return (
                "SOMEONE TUNED THE NUMBER: L1.1 texture passes while L1.5 repeat-rate "
                "fails. Level noise has been injected onto a rescaled base shape — the "
                "symptom moved and the mechanism did not."
            )
        return None

    def summary(self) -> str:
        lines = [f"two-level test — generator={self.generator} homes={self.homes} days={self.days}"]
        for c in self.cells:
            lines.append(
                f"  [{c.verdict.value.upper():>12}] {c.statistic} = {c.value:.4g}"
                + (f"  (band {c.band.direction} {c.band.threshold:g})" if c.band.threshold is not None else "  (NEED anchor)")
                + (f"  — {c.note}" if c.note else "")
            )
        warning = self.goal_seek_warning()
        if warning:
            lines.append("  !! " + warning)
        return "\n".join(lines)


@dataclass(frozen=True)
class PopulationTraces:
    """One generator's output over a population, in the only form this module
    consumes: per-home half-hourly grids plus the day-type calendar.

    Deliberately a plain structure with no generator-specific field, so the same
    statistics judge the shipped path and `premise_trace` identically and neither
    can be flattered by the shape of its own output.
    """

    generator: str
    homes: tuple[str, ...]
    grids: tuple[tuple[tuple[float, ...], ...], ...]   # home -> day -> 48 periods
    is_weekend: tuple[bool, ...]
    annual_kwh: tuple[float, ...]
    # The EXTERNAL common-mode driver for L2.2: heating degree days off the real
    # weather archive. External, not population-derived — see `between_home_correlation`.
    weather_driver: tuple[float, ...] = ()
    pc1_is_an_input: bool = False
    # Which homes heat with electricity, for the heating-conditioned L1.1 band.
    # A REGISTER fact (the household's heating system, i.e. what a real supplier
    # holds as main_heating_fuel), never inferred from the trace — inferring
    # "this home looks like it has a heat pump" from the very smoothness the band
    # is judging would be the tautology R15 names first.
    #
    # FAIL-CLOSED when empty: an empty tuple means every home is judged by the
    # STRICTER gas band, so a builder that forgets to supply it makes an
    # electrically-heated home fail, never pass. The lenient direction requires
    # someone to assert the fact.
    electrically_heated: tuple[bool, ...] = ()

    def __post_init__(self) -> None:
        if len(self.homes) != len(self.grids):
            raise InsufficientEvidence("home ids and grids must align")
        if len(self.homes) != len(self.annual_kwh):
            raise InsufficientEvidence("home ids and annual totals must align")
        if self.electrically_heated and len(self.electrically_heated) != len(self.homes):
            raise InsufficientEvidence(
                "the electrically-heated flags must align with the home ids"
            )
        for g in self.grids:
            if len(g) != len(self.is_weekend):
                raise InsufficientEvidence("every home's grid must span the day-type calendar")
        if self.weather_driver and len(self.weather_driver) != len(self.is_weekend):
            raise InsufficientEvidence("the weather driver must span the day-type calendar")

    @property
    def days(self) -> int:
        return len(self.is_weekend)


def evaluate_two_level(population: PopulationTraces) -> TwoLevelResult:
    """Run every statistic over a population and return the WORST-CELL verdict.

    Level 1 statistics are computed per home and the WORST home is reported — an
    average would hide a clone cluster inside an otherwise-diverse population,
    which is the exact failure mode this suite exists to find.
    """
    _require_homes(population.grids, minimum=MIN_HOMES_FOR_DIVERSITY, name="evaluate_two_level")
    grids = [[list(day) for day in home] for home in population.grids]
    cells: list[CellResult] = []

    def worst(fn: Callable[[list[list[float]]], float], *, direction: str) -> tuple[float, int]:
        values = [fn(g) for g in grids]
        if direction == "at_least":
            i = min(range(len(values)), key=lambda k: values[k])
        else:
            i = max(range(len(values)), key=lambda k: values[k])
        return values[i], i

    # --- L1 ---------------------------------------------------------------
    # L1.1 is judged PER HOME against that home's own band, because the statistic
    # is a ratio to the home's own mean and a heat pump changes the denominator.
    # The worst cell is therefore the worst MARGIN (value / its own threshold),
    # not the lowest raw value: with two thresholds live, the lowest raw number is
    # not necessarily the home in most trouble. Both bands are `at_least`, so
    # min(margin) >= 1 if and only if every home passes its own band — the
    # worst-cell contract is preserved, not weakened.
    texture_bands = tuple(
        BANDS["L1.1e_half_hourly_texture_electric_heat"] if electric
        else BANDS["L1.1_half_hourly_texture"]
        for electric in (
            population.electrically_heated or (False,) * len(population.homes)
        )
    )
    texture_values = [half_hourly_texture(g) for g in grids]
    i = min(
        range(len(texture_values)),
        key=lambda k: texture_values[k] / texture_bands[k].threshold,
    )
    value, band = texture_values[i], texture_bands[i]
    cells.append(CellResult(
        TEXTURE_STATISTIC, "L1", value, band.judge(value), band,
        note=(
            f"worst home {population.homes[i]} — judged by {band.statistic} "
            f"(band {band.direction} {band.threshold:.4g}); "
            f"{sum(1 for b in texture_bands if b.anchor is AnchorStatus.PUBLISHED)}"
            f"/{len(texture_bands)} homes electrically heated"
        ),
    ))

    band = BANDS["L1.2_day_to_day_shape_correlation"]
    value, i = worst(day_to_day_shape_correlation, direction=band.direction)
    cells.append(CellResult(band.statistic, "L1", value, band.judge(value), band,
                            note=f"worst home {population.homes[i]}"))

    band = BANDS["L1.3_away_days_per_year"]
    value, i = worst(
        lambda g: trough_statistics(g).away_days_per_year, direction=band.direction
    )
    cells.append(CellResult(
        band.statistic, "L1", value, band.judge(value), band,
        note=(
            f"worst home {population.homes[i]} — best away signature "
            f"{trough_statistics(grids[i]).worst_signature:.3g} (1.0 = empty house)"
        ),
    ))

    band = BANDS["L1.4_weekday_weekend_separation"]
    value, i = worst(
        lambda g: weekday_weekend_separation(g, population.is_weekend), direction="at_least"
    )
    cells.append(CellResult(band.statistic, "L1", value, band.judge(value), band,
                            note=f"worst home {population.homes[i]} — measured, not judged"))

    band = BANDS["L1.5_max_multiplicity_share"]
    value, i = worst(
        lambda g: normalised_fraction_multiplicity(g).max_multiplicity_share,
        direction=band.direction,
    )
    cells.append(CellResult(
        band.statistic, "L1", value, band.judge(value), band,
        note=(
            f"worst home {population.homes[i]} — raw repeat rate "
            f"{normalised_fraction_multiplicity(grids[i]).repeat_rate:.3g} (reported, not judged)"
        ),
    ))

    # --- L2 ---------------------------------------------------------------
    curve = smoothing_curve(grids)
    band = BANDS["L2.1_smoothing_ratio"]
    value = smoothing_ratio(curve)
    verdict = band.judge(value)
    note = f"curve {{{', '.join(f'{n}: {v:.3g}' for n, v in sorted(curve.items()))}}}"
    if population.pc1_is_an_input and verdict is Verdict.PASS:
        # Fail-open pattern 3. This generator CONSUMES the published shape that is
        # L2.1's large-N anchor, so a pass here is a tautology, not evidence.
        verdict = Verdict.TAUTOLOGICAL
        note += " — PC1 is an INPUT to this generator, so a large-N pass is tautological"
    cells.append(CellResult(band.statistic, "L2", value, verdict, band, note=note))

    band = BANDS["L2.2_between_home_correlation"]
    if not population.weather_driver:
        # An unavailable check is a FAILED check (R15). Without an external driver
        # this statistic cannot be computed honestly, so it RAISES rather than
        # falling back to a population-derived mode — the exact fallback that made
        # the earlier version score clones as maximally diverse.
        raise InsufficientEvidence(
            "L2.2 needs an EXTERNAL weather driver; a population-derived common mode "
            "would score a cloned population as maximally diverse"
        )
    value = between_home_correlation(grids, population.weather_driver)
    cells.append(CellResult(band.statistic, "L2", value, band.judge(value), band,
                            note="median pairwise r on the residual from external HDD"))

    band = BANDS["L2.3_timing_diversity_periods"]
    value = timing_diversity(grids)
    cells.append(CellResult(band.statistic, "L2", value, band.judge(value), band,
                            note="population sd of each home's mean evening-peak period"))

    band = BANDS["L2.4_scale_spread_p90_p10"]
    spread = scale_spread(population.annual_kwh)
    cells.append(CellResult(band.statistic, "L2", spread.p90_over_p10,
                            band.judge(spread.p90_over_p10), band,
                            note=f"IQR ratio {spread.iqr_ratio:.3g} — measured, not judged"))

    return TwoLevelResult(
        generator=population.generator,
        cells=tuple(cells),
        homes=len(grids),
        days=population.days,
    )


# ===========================================================================
# POPULATION BUILDERS — the two generators, judged by IDENTICAL statistics
# ===========================================================================
#
# HEATING_BASE_TEMP_C is the UK 15.5 C degree-day base. Imported rather than
# re-declared would couple the harness to the generator it judges, so it is stated
# here as the published convention it is.
HDD_BASE_TEMP_C = 15.5


def hdd_driver(weather_days: Sequence) -> tuple[float, ...]:
    """The EXTERNAL common-mode driver for L2.2 — heating degree days straight off
    the real archive. Derived from published weather, never from any generator's
    output or parameters."""
    if not weather_days:
        raise InsufficientEvidence("the weather driver needs at least one day")
    return tuple(
        max(0.0, HDD_BASE_TEMP_C - _require_finite_scalar(d.weather.temperature_mean_c))
        for d in weather_days
    )


def _require_finite_scalar(value: float) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise NonFiniteTrace(f"the weather archive carries a non-finite temperature {value!r}")
    return v


#
# Both builders live here, in the harness, rather than beside their generators.
# That is deliberate: if each side supplied its own adapter, each side could
# choose the framing that flattered it (which days, which commodity, which
# aggregation). The statistics above never learn which generator they are
# looking at — `PopulationTraces` carries no generator-specific field.


def shipped_path_population(
    properties: Sequence[Mapping],
    weather_days: Sequence,
    *,
    commodity: str = "electricity",
    generator: str = "shipped demand path (demand_model.build_demand_shape on PC1)",
) -> "PopulationTraces":
    """The LEGACY generator: a rescaled national PC1 shape.

    NO LONGER "the generator actually in the demand path today", and the claim is
    corrected here rather than left to rot -- the W1_11 settlement switch made
    `simulation.fabric_demand_path` the provider for every ELIGIBLE DOMESTIC
    premise in `run_phase2b`, so this path now settles only the customers fabric
    refused (half-hourly metered, non-domestic, no household record, or no weather
    coverage). It remains the right BASELINE to score the fabric population
    against -- that comparison is the point -- but reading it as the shipped path
    would now overstate its reach.

    `simulation.demand_model.build_demand_shape` applies weather, occupancy and
    asset adjustments to a stored national PC1 half-hourly shape. `weather_days`
    are `premise_trace.TraceWeatherDay` records off the REAL Open-Meteo archive, so
    both generators are judged on the same real weather rather than on a synthetic
    temperature series (Historical Ground Truth).
    """
    from sim.profile_class_1 import load_pc1_shape
    from simulation.demand_model import build_demand_shape

    if not properties:
        raise InsufficientEvidence("the shipped path needs at least one property")
    if not weather_days:
        raise InsufficientEvidence("the shipped path needs at least one weather day")

    base_by_date = {d.date: load_pc1_shape(d.date) for d in weather_days}
    grids: list[tuple[tuple[float, ...], ...]] = []
    homes: list[str] = []
    annual: list[float] = []
    electric: list[bool] = []
    for prop in properties:
        days: list[tuple[float, ...]] = []
        for wx in weather_days:
            shape = build_demand_shape(
                base_by_date[wx.date],
                wx.weather.temperature_mean_c,
                commodity,
                dict(prop),
            )
            days.append(tuple(shape))
        grids.append(tuple(days))
        homes.append(str(prop.get("customer_id") or prop.get("premise_id")))
        annual.append(sum(sum(d) for d in days) / len(days) * 365.25)
        # The REGISTER field a real supplier holds, read as a register field:
        # anything that is not mains gas heats electrically for L1.1's purposes.
        # Unknown reads as gas, which is the stricter band (fail-closed).
        electric.append("heat pump" in str(prop.get("main_heating_fuel", "")).lower())

    return PopulationTraces(
        generator=generator,
        homes=tuple(homes),
        grids=tuple(grids),
        is_weekend=tuple(bool(d.is_weekend) for d in weather_days),
        annual_kwh=tuple(annual),
        electrically_heated=tuple(electric),
        weather_driver=hdd_driver(weather_days),
        # PC1 IS an input here, so L2.1's large-N anchor is tautological for this
        # generator and `evaluate_two_level` refuses to score that cell as a pass.
        pc1_is_an_input=True,
    )


def premise_trace_population(
    traces: Sequence,
    weather_days: Sequence,
    *,
    commodity: str = "electricity",
    generator: str = "premise_trace.generate_premise_trace (W1_12)",
) -> "PopulationTraces":
    """W1_12's generator — built, but NOT yet wired into the demand path.

    Takes already-generated `PremiseTrace` objects rather than generating them, so
    the harness holds no generator parameters and cannot be accused of choosing
    favourable settings.
    """
    if not traces:
        raise InsufficientEvidence("needs at least one premise trace")
    grids = tuple(
        tuple(tuple(day) for day in t.half_hourly(commodity)) for t in traces
    )
    return PopulationTraces(
        generator=generator,
        homes=tuple(t.premise_id for t in traces),
        grids=grids,
        is_weekend=tuple(bool(d.is_weekend) for d in weather_days),
        annual_kwh=tuple(t.annual_kwh(commodity) for t in traces),
        # `heating_commodity` is set from the HOUSEHOLD RECORD (`is_gas_heated`)
        # when the trace is generated — a register fact, not a reading of the
        # numbers the band then judges.
        electrically_heated=tuple(t.heating_commodity == "electricity" for t in traces),
        weather_driver=hdd_driver(weather_days),
        pc1_is_an_input=False,
    )


# ===========================================================================
# THE FABRIC GAP — belief vs truth, and its MONEY CONSEQUENCE
# ===========================================================================


@dataclass(frozen=True)
class FabricObservation:
    """One premise's fabric TRUTH alongside the two beliefs held about it.

    The harness is the only layer allowed to hold these three numbers together.
    The company sees `epc_hlc_kw_per_k` (its register prior) and computes
    `inferred_hlc_kw_per_k` (C14) from observables; it never sees `actual`.
    """

    premise_id: str
    actual_hlc_kw_per_k: float          # SIM truth (W1_11 fabric physics)
    epc_hlc_kw_per_k: float             # the company's register prior
    inferred_hlc_kw_per_k: float        # the company's C14 posterior
    floor_area_m2: float
    annual_heat_kwh: float
    # THE DECISION INPUTS (added 2026-08-09, C14 L2->L3). A point estimate alone is
    # not enough to decide on: the company refuses to spend money on a belief that is
    # too wide or rests on a stock prior, and it needs the heating degree days of the
    # published weather to attribute any part of the bill to fabric at all. These are
    # REQUIRED rather than defaulted — a default would let a caller silently obtain a
    # certain, actionable belief it never actually had, which is the fail-open shape
    # this whole module exists to catch.
    annual_degree_days_k_day: float
    epc_relative_sd: float
    inferred_relative_sd: float
    epc_basis: EvidenceBasis
    inferred_basis: EvidenceBasis

    def __post_init__(self) -> None:
        for name in (
            "actual_hlc_kw_per_k",
            "epc_hlc_kw_per_k",
            "inferred_hlc_kw_per_k",
            "floor_area_m2",
            "annual_heat_kwh",
            "annual_degree_days_k_day",
            "epc_relative_sd",
            "inferred_relative_sd",
        ):
            v = getattr(self, name)
            if not math.isfinite(v):
                raise NonFiniteTrace(f"{self.premise_id}: {name} is {v!r}")
        if self.actual_hlc_kw_per_k <= 0.0:
            raise InsufficientEvidence(f"{self.premise_id}: the actual HLC must be positive")
        if self.annual_degree_days_k_day <= 0.0:
            raise InsufficientEvidence(
                f"{self.premise_id}: a premise with no heating season gives the fabric "
                f"belief nothing to bite on"
            )

    def belief_arm(self, belief: str) -> tuple[float, float, EvidenceBasis]:
        """The (estimate, relative sd, basis) triple for one of the two beliefs.

        One accessor rather than two parallel `if belief == "epc"` chains at every
        use site: a decision arm that picked the EPC point estimate but the inferred
        uncertainty would be a silent hybrid nobody holds, and it would not show up
        as a wrong number, only as a wrong one.
        """
        if belief == "epc":
            return (self.epc_hlc_kw_per_k, self.epc_relative_sd, self.epc_basis)
        if belief == "inferred":
            return (
                self.inferred_hlc_kw_per_k,
                self.inferred_relative_sd,
                self.inferred_basis,
            )
        raise ValueError(f"unknown belief {belief!r}")


def epc_vs_actual_gap(observations: Sequence[FabricObservation]) -> GapResult:
    """How wrong is the EPC register about fabric, normalised to the no-skill
    stock prior?

    Uses `gap_metric.prediction_gap` so this gap reads on the SAME 0/1 scale as
    every other coupled-triad gap: 1.0 means the register does no better than
    predicting the population mean, and >1.0 means it is actively worse than
    knowing nothing.
    """
    _require_homes(observations, minimum=MIN_HOMES_FOR_DIVERSITY, name="epc_vs_actual_gap")
    truth = [o.actual_hlc_kw_per_k for o in observations]
    belief = [o.epc_hlc_kw_per_k for o in observations]
    result = prediction_gap(truth, belief)
    result.components["belief_form"] = "EPC register prior HLC (kW/K), company-side"
    result.note = "EPC-vs-actual fabric gap: register HLC against SIM truth"
    return result


def inferred_vs_actual_gap(observations: Sequence[FabricObservation]) -> GapResult:
    """How wrong is the company's INFERRED fabric (C14) about fabric?

    The pair (`epc_vs_actual_gap`, `inferred_vs_actual_gap`) is the whole point of
    the fabric triad: the difference between them is what the company's own
    inference bought it over the register it started from. A NEGATIVE difference
    (inference worse than the register) is a real and reportable outcome, not a
    bug — the company is allowed to be wrong.
    """
    _require_homes(observations, minimum=MIN_HOMES_FOR_DIVERSITY, name="inferred_vs_actual_gap")
    truth = [o.actual_hlc_kw_per_k for o in observations]
    belief = [o.inferred_hlc_kw_per_k for o in observations]
    result = prediction_gap(truth, belief)
    result.components["belief_form"] = "C14 posterior HLC (kW/K): EPC prior shrunk toward meter evidence"
    result.note = "inferred-vs-actual fabric gap: C14 posterior against SIM truth"
    return result


def inference_improvement(observations: Sequence[FabricObservation]) -> float:
    """`epc_gap - inferred_gap`. Positive means the company's own inference beat
    the register it started from; negative means it made things worse."""
    return epc_vs_actual_gap(observations).gap - inferred_vs_actual_gap(observations).gap


# --- the money consequence -------------------------------------------------
#
# WHO DECIDES, AND WHY IT MOVED (2026-08-09, C14 L2->L3)
# ------------------------------------------------------
# This section used to hold its OWN decision function (`rank_measures`) and its own
# measure catalogue. That was an R11 orphan of the exact class this repo keeps
# finding: the harness was scoring a decision that no company anywhere in the
# codebase actually made, and `company/pricing/thermal_inference.py`'s uncertainty
# model — `interval_95`, `is_actionable`, `EvidenceBasis` — was computed by C14 and
# read by nobody.
#
# It also had a fail-open that only showed up when the numbers were probed: the
# choice set contained no DO-NOTHING option, so every premise was recommended
# something. A 0.08 kW/K flat using 4,000 kWh/yr at 7.4 p/kWh was recommended
# `time_shift` at a lifetime net value of **-£41** — spend £300 to save £259 — and
# because the truth arm picked the same value-destroying measure, `chosen == best`
# and the metric recorded a PERFECT decision. A control that cannot express "every
# option here loses money" cannot report the loss.
#
# The decision therefore now lives where a decision belongs — in the company
# (`company.pricing.fabric_intervention`) — and this module CALLS it, twice: once
# with the company's belief, once with the truth the company cannot see. That
# second call is the only thing the harness adds, and it is the one thing the
# company could never do for itself. Both arms run the SAME rule and the SAME
# catalogue, so the difference between them is the belief and nothing else.
#
# THE MISSION LINK, unchanged and still structural: savings count ONLY from reduced
# or time-shifted usage, never from discounting — `offer_annual_saving_kwh` has no
# price parameter, so no tariff move can conjure a saved kWh.

# Re-exported so this module's readers and tests reach the company's definitions
# rather than a copy. `MeasureEconomics`/`DEFAULT_MEASURES`/`rank_measures` were the
# harness-private names for these and are deliberately GONE, not aliased: an alias
# would have let a caller keep using the do-nothing-free choice set.
MeasureEconomics = fi.RetrofitOffer
DEFAULT_MEASURES = fi.OFFER_BOOK
MEASURES = tuple(sorted(fi.OFFER_BOOK)) + (fi.DO_NOTHING,)

# kgCO2e per kWh — BEIS/DESNZ conversion factors, used to express the same
# decision in carbon as well as in money. Reported, never optimised.
CARBON_KG_PER_KWH = {"gas": 0.183, "electricity": 0.207}


def measure_annual_saving_kwh(
    hlc_kw_per_k: float,
    annual_heat_kwh: float,
    measure: fi.RetrofitOffer,
    *,
    annual_degree_days_k_day: float,
) -> float:
    """The kWh a measure removes or moves in a year — the COMPANY's physics.

    Kept as a name here only because the carbon arithmetic below needs it; it
    delegates rather than reimplements. `DO_NOTHING` saves exactly zero and is
    handled by `_saving_of`, not here, so that a caller cannot accidentally price
    inaction as a measure.
    """
    return fi.offer_annual_saving_kwh(
        hlc_kw_per_k, annual_heat_kwh, annual_degree_days_k_day, measure
    )


def _saving_of(
    name: str,
    hlc_kw_per_k: float,
    annual_heat_kwh: float,
    annual_degree_days_k_day: float,
    catalogue: Mapping[str, fi.RetrofitOffer],
) -> float:
    """kWh saved by `name` at TRUE fabric. Doing nothing saves nothing."""
    if name == fi.DO_NOTHING:
        return 0.0
    return measure_annual_saving_kwh(
        hlc_kw_per_k,
        annual_heat_kwh,
        catalogue[name],
        annual_degree_days_k_day=annual_degree_days_k_day,
    )


@dataclass(frozen=True)
class MoneyConsequence:
    """What the fabric gap COSTS: the value forgone by deciding on a belief instead
    of on the truth, plus the carbon that decision did not save.

    THREE FAILURE MODES, COUNTED SEPARATELY because they cost different things and
    a supplier would act differently on each:

    * `misranked_premises` — the company acted and bought the wrong measure.
    * `declined_where_value_existed` — the company refused (no evidence, or the
      winner did not survive its own error bar) where the truth said a positive
      measure existed. This is the price of honest caution, and it is a price: a
      metric that only counted wrong purchases would score a company that never
      acts as perfect.
    * `value_destroying_recommendations` — the company recommended a measure whose
      TRUE lifetime value is negative. Structurally invisible before 2026-08-09.

    All three are folded into `forgone_lifetime_gbp`; the counts say WHICH kind of
    wrong the company was.
    """

    premises: int
    misranked_premises: int
    declined_where_value_existed: int
    value_destroying_recommendations: int
    forgone_lifetime_gbp: float
    forgone_annual_kwh: float
    forgone_annual_kg_co2e: float
    basis: str

    @property
    def misrank_rate(self) -> float:
        return self.misranked_premises / self.premises

    @property
    def gbp_per_tonne_co2e(self) -> float | None:
        """Cost per tonne of CO2e forgone. None when nothing was forgone —
        reported as None rather than as 0.0 or inf, because a division that
        silently returns a number here would be a fail-open."""
        if self.forgone_annual_kg_co2e <= 0.0:
            return None
        return self.forgone_lifetime_gbp / (self.forgone_annual_kg_co2e / 1000.0)


def money_consequence(
    observations: Sequence[FabricObservation],
    *,
    unit_rate_p_per_kwh: float,
    belief: str = "epc",
    fuel: str = "gas",
    measures: Mapping[str, fi.RetrofitOffer] | None = None,
) -> MoneyConsequence:
    """The money consequence of the COMPANY deciding on `belief` instead of on truth.

    For each premise the company's own `fabric_intervention.decide` is run twice:
    once on the belief the company holds (with that belief's uncertainty, so it may
    legitimately DECLINE), and once on the SIM truth with no uncertainty at all —
    the counterfactual only the harness can compute. Where the two answers differ,
    the premise is charged the difference in TRUE lifetime value between what the
    truth would have bought and what the belief actually bought.

    A premise where the belief is wrong but the DECISION survives costs nothing —
    the honest reading, and why this is a decision metric rather than an error one.
    """
    _require_homes(observations, minimum=MIN_HOMES_FOR_DIVERSITY, name="money_consequence")
    if belief not in ("epc", "inferred"):
        raise ValueError(f"unknown belief {belief!r}")
    if fuel not in CARBON_KG_PER_KWH:
        raise ValueError(f"unknown fuel {fuel!r} — no published carbon factor")

    catalogue = dict(measures if measures is not None else fi.OFFER_BOOK)
    misranked = 0
    declined_with_value = 0
    value_destroying = 0
    forgone_gbp = 0.0
    forgone_kwh = 0.0
    for o in observations:
        held, relative_sd, held_basis = o.belief_arm(belief)
        if not math.isfinite(held) or held <= 0.0:
            raise InsufficientEvidence(f"{o.premise_id}: a non-positive belief is not decidable")
        lower, _upper = log_normal_interval_95(held, relative_sd)
        company = fi.decide(
            o.premise_id,
            held,
            hlc_pessimistic_kw_per_k=lower,
            actionable=is_actionable_belief(held_basis, relative_sd),
            annual_heat_kwh=o.annual_heat_kwh,
            annual_degree_days_k_day=o.annual_degree_days_k_day,
            unit_rate_p_per_kwh=unit_rate_p_per_kwh,
            offers=catalogue,
            evidence_note=f"basis={held_basis.value}, relative_sd={relative_sd:.3f}",
        )
        # THE TRUTH ARM. Zero uncertainty and actionable by construction: this is
        # not a belief anyone holds, it is what a decider WOULD have chosen with
        # perfect knowledge, and it is the only place in this codebase where the
        # company's rule is fed the SIM's hidden fabric.
        truth = fi.decide(
            o.premise_id,
            o.actual_hlc_kw_per_k,
            hlc_pessimistic_kw_per_k=o.actual_hlc_kw_per_k,
            actionable=True,
            annual_heat_kwh=o.annual_heat_kwh,
            annual_degree_days_k_day=o.annual_degree_days_k_day,
            unit_rate_p_per_kwh=unit_rate_p_per_kwh,
            offers=catalogue,
            evidence_note="SIM truth — harness counterfactual, no company holds this",
        )
        chosen, best = company.measure, truth.measure
        if chosen == best:
            continue
        true_values = dict(
            fi.rank_offers(
                o.actual_hlc_kw_per_k,
                o.annual_heat_kwh,
                o.annual_degree_days_k_day,
                unit_rate_p_per_kwh=unit_rate_p_per_kwh,
                offers=catalogue,
            )
        )
        if chosen == fi.DO_NOTHING:
            declined_with_value += 1
        else:
            misranked += 1
            if true_values[chosen] < 0.0:
                value_destroying += 1
        forgone_gbp += true_values[best] - true_values[chosen]
        forgone_kwh += _saving_of(
            best, o.actual_hlc_kw_per_k, o.annual_heat_kwh, o.annual_degree_days_k_day, catalogue
        ) - _saving_of(
            chosen, o.actual_hlc_kw_per_k, o.annual_heat_kwh, o.annual_degree_days_k_day, catalogue
        )
    return MoneyConsequence(
        premises=len(observations),
        misranked_premises=misranked,
        declined_where_value_existed=declined_with_value,
        value_destroying_recommendations=value_destroying,
        forgone_lifetime_gbp=forgone_gbp,
        forgone_annual_kwh=forgone_kwh,
        forgone_annual_kg_co2e=max(0.0, forgone_kwh) * CARBON_KG_PER_KWH[fuel],
        basis=(
            f"PROVISIONAL — lifetime net value at {unit_rate_p_per_kwh:g} p/kWh on "
            f"domain-knowledge retrofit capex; savings from reduced or time-shifted "
            f"kWh only, never from discounting. Belief = {belief}. Decided by "
            f"company.pricing.fabric_intervention.decide in BOTH arms."
        ),
    )


# ===========================================================================
# LEDGER
# ===========================================================================

# These MUST be real ids in docs/design/maturity_map.yaml, and
# `test_the_ledger_atom_ids_are_REAL_map_atoms` fails if any stops being one.
# That test exists because `FABRIC_WORLD_ATOM` was written here as
# "W1_11_premise_fabric_physics", which has never been an atom — the real id is
# `W1_11_fabric_physics_core`. A ledger entry under a non-existent atom is
# silently invisible: the Proof-door panel derives its rows from the map, so the
# write would have "succeeded" every run while rendering nowhere. An id typo is
# exactly the failure a human review reads straight past.
FABRIC_TWIN_ATOM = "C14_thermal_parameter_inference"
FABRIC_WORLD_ATOM = "W1_11_fabric_physics_core"
GENERATOR_WORLD_ATOM = "W1_12_premise_trace_generator"


def _money_components(m: MoneyConsequence) -> dict:
    """The whole decision outcome, into the ledger row.

    EVERY count, not just `misrank_rate`. A reader who saw only the misrank rate
    would read a company that declined every single premise as flawless, which is
    the fail-open the do-nothing option was added to close — reporting it away in
    the ledger would put it straight back.
    """
    return {
        "premises": m.premises,
        "misrank_rate": m.misrank_rate,
        "misranked_premises": m.misranked_premises,
        "declined_where_value_existed": m.declined_where_value_existed,
        "value_destroying_recommendations": m.value_destroying_recommendations,
        "forgone_lifetime_gbp": m.forgone_lifetime_gbp,
        "forgone_annual_kwh": m.forgone_annual_kwh,
        "forgone_annual_kg_co2e": m.forgone_annual_kg_co2e,
        "gbp_per_tonne_co2e": m.gbp_per_tonne_co2e,
        "basis": m.basis,
    }


def write_fabric_gap_entries(
    observations: Sequence[FabricObservation],
    *,
    unit_rate_p_per_kwh: float,
    measured_at: str,
    run_git_commit: str | None = None,
    two_level: TwoLevelResult | None = None,
    path: Path | None = None,
) -> dict[str, GapResult]:
    """Write the fabric triad's gaps into the coupled-gap ledger.

    Two entries, because the triad has two distinct belief sources and collapsing
    them would hide the only interesting number (what inference bought over the
    register). The two-level result rides along as a component of the inferred
    entry when supplied, so the fabric gap and the realism of the traces it was
    measured on are read side by side rather than in two places.

    `measured_at` is passed IN — this module never calls a clock (C-S2).
    """
    epc = epc_vs_actual_gap(observations)
    inferred = inferred_vs_actual_gap(observations)
    money_epc = money_consequence(
        observations, unit_rate_p_per_kwh=unit_rate_p_per_kwh, belief="epc"
    )
    money_inferred = money_consequence(
        observations, unit_rate_p_per_kwh=unit_rate_p_per_kwh, belief="inferred"
    )

    shared = {
        "premises": len(observations),
        "money_consequence_epc": _money_components(money_epc),
        "money_consequence_inferred": _money_components(money_inferred),
        "inference_improvement": epc.gap - inferred.gap,
    }
    if two_level is not None:
        shared["two_level"] = {
            "generator": two_level.generator,
            "is_red": two_level.is_red,
            "failed_levels": list(two_level.failed_levels()),
            "cells": {
                c.statistic: {"value": c.value, "verdict": c.verdict.value}
                for c in two_level.cells
            },
            "goal_seek_warning": two_level.goal_seek_warning(),
        }

    for result, key in ((epc, "epc_components"), (inferred, "inferred_components")):
        result.components.update(shared)
        result.components["belief_source"] = (
            "EPC register prior only" if key == "epc_components" else "C14 posterior (EPC + meter evidence)"
        )

    write_gap_entry(
        FABRIC_WORLD_ATOM, FABRIC_TWIN_ATOM, epc,
        measured_at=measured_at, run_git_commit=run_git_commit, ledger_path=path,
    )
    write_gap_entry(
        GENERATOR_WORLD_ATOM, FABRIC_TWIN_ATOM, inferred,
        measured_at=measured_at, run_git_commit=run_git_commit, ledger_path=path,
    )
    return {"epc_vs_actual": epc, "inferred_vs_actual": inferred}
