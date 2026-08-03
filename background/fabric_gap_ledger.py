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


# The bands. Every `observed_on_shipped` value below was MEASURED on the shipped
# demand path (`tests/harness/test_premise_two_level.py::test_MEASURED_shipped_path_values`), not estimated.
BANDS: dict[str, Band] = {
    "L1.1_half_hourly_texture": Band(
        statistic="L1.1_half_hourly_texture",
        level="L1",
        direction="at_least",
        threshold=0.15,
        anchor=AnchorStatus.DOMAIN_KNOWLEDGE,
        anchor_source=(
            "domain-knowledge: real individual-home half-hourly electricity moves in "
            "the tens of percent of its own mean between adjacent periods (a kettle is "
            "2.8 kW for three minutes on a ~0.7 kWh half-hour). The SERL/LCL published "
            "band is NOT yet in the artefact library, so the threshold is set at 0.15 — "
            "below the low end of the 20-40% domain expectation, deliberately "
            "loose so that it can only fire on a generator that is smooth by "
            "construction rather than on one that is merely at the calm end of real."
        ),
        observed_on_shipped=None,
        rationale=(
            "A rescaled national average has the texture of a national average, which "
            "is the texture of a hundred thousand homes already summed."
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

    def __post_init__(self) -> None:
        if len(self.homes) != len(self.grids):
            raise InsufficientEvidence("home ids and grids must align")
        if len(self.homes) != len(self.annual_kwh):
            raise InsufficientEvidence("home ids and annual totals must align")
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
    band = BANDS["L1.1_half_hourly_texture"]
    value, i = worst(half_hourly_texture, direction=band.direction)
    cells.append(CellResult(band.statistic, "L1", value, band.judge(value), band,
                            note=f"worst home {population.homes[i]}"))

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

    return PopulationTraces(
        generator=generator,
        homes=tuple(homes),
        grids=tuple(grids),
        is_weekend=tuple(bool(d.is_weekend) for d in weather_days),
        annual_kwh=tuple(annual),
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

    def __post_init__(self) -> None:
        for name in (
            "actual_hlc_kw_per_k",
            "epc_hlc_kw_per_k",
            "inferred_hlc_kw_per_k",
            "floor_area_m2",
            "annual_heat_kwh",
        ):
            v = getattr(self, name)
            if not math.isfinite(v):
                raise NonFiniteTrace(f"{self.premise_id}: {name} is {v!r}")
        if self.actual_hlc_kw_per_k <= 0.0:
            raise InsufficientEvidence(f"{self.premise_id}: the actual HLC must be positive")


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
# THE MISSION LINK, and the constraint that governs it: savings count ONLY from
# reduced or time-shifted usage, NEVER from discounting. Every measure below is
# scored on the kWh it removes or moves, priced at the unit rate, and nothing here
# can create a saving by changing a tariff.

MEASURES = ("insulate", "heat_pump", "solar_pv", "time_shift")


@dataclass(frozen=True)
class MeasureEconomics:
    """A fabric-targeted measure, scored on the kWh it removes or moves.

    R13: these are BASELINE physical/cost parameters, set blind to company P&L and
    to any gap number. They are DIAGNOSTIC inputs, never tuned to move a result.
    """

    name: str
    capex_gbp: float
    hlc_reduction_fraction: float       # how much of the fabric loss it removes
    delivered_efficiency_gain: float    # kWh out per kWh in, relative to today
    shiftable_fraction: float           # of annual heat kWh, moved not removed
    lifetime_years: float


# `domain-knowledge` order-of-magnitude UK retrofit parameters. Registered as an
# UNVALIDATED SIMPLIFICATION on the atom: the RANKING these produce is what the
# gap metric consumes, and the ranking is robust to the level of these numbers in
# a way the absolute £ is not. Absolute £ is therefore reported as PROVISIONAL.
DEFAULT_MEASURES: dict[str, MeasureEconomics] = {
    "insulate": MeasureEconomics("insulate", 6000.0, 0.30, 0.0, 0.0, 30.0),
    "heat_pump": MeasureEconomics("heat_pump", 12000.0, 0.0, 2.6, 0.0, 18.0),
    "solar_pv": MeasureEconomics("solar_pv", 7000.0, 0.0, 0.0, 0.0, 25.0),
    "time_shift": MeasureEconomics("time_shift", 300.0, 0.0, 0.0, 0.25, 10.0),
}

# kgCO2e per kWh — BEIS/DESNZ conversion factors, used to express the same
# decision in carbon as well as in money. Reported, never optimised.
CARBON_KG_PER_KWH = {"gas": 0.183, "electricity": 0.207}

SOLAR_KWH_PER_YEAR = 3200.0   # a typical 4 kWp south-facing UK domestic array
TIME_SHIFT_PRICE_ADVANTAGE = 0.35   # off-peak unit rate relative to peak


def measure_annual_saving_kwh(
    hlc_kw_per_k: float,
    annual_heat_kwh: float,
    measure: MeasureEconomics,
) -> float:
    """The kWh a measure removes (or, for time-shift, moves) in a year, for a home
    whose fabric loss coefficient is `hlc_kw_per_k`.

    Fabric-driven measures scale with the heat demand that HLC implies, which is
    why getting HLC wrong misprices them. `solar_pv` deliberately does NOT scale
    with fabric — it is in the choice set precisely so the decision can be wrong in
    both directions: a home whose fabric is overestimated will be steered toward
    insulation when PV was the better buy.
    """
    if hlc_kw_per_k <= 0.0 or not math.isfinite(hlc_kw_per_k):
        raise InsufficientEvidence("a measure cannot be scored against a non-positive HLC")
    if not math.isfinite(annual_heat_kwh) or annual_heat_kwh < 0.0:
        raise InsufficientEvidence("annual heat demand must be finite and non-negative")
    if measure.name == "solar_pv":
        return SOLAR_KWH_PER_YEAR
    saved = annual_heat_kwh * measure.hlc_reduction_fraction
    if measure.delivered_efficiency_gain > 0.0:
        saved += annual_heat_kwh * (1.0 - 1.0 / measure.delivered_efficiency_gain)
    return saved


def rank_measures(
    hlc_kw_per_k: float,
    annual_heat_kwh: float,
    *,
    unit_rate_p_per_kwh: float,
    measures: Mapping[str, MeasureEconomics] | None = None,
) -> list[tuple[str, float]]:
    """Rank measures by lifetime net saving, best first, for a given fabric BELIEF.

    This is the decision function. Run it on the belief and on the truth and the
    difference between the two answers is the money consequence of the gap.
    """
    if not math.isfinite(unit_rate_p_per_kwh) or unit_rate_p_per_kwh <= 0.0:
        raise InsufficientEvidence("the unit rate must be positive and finite")
    catalogue = dict(measures or DEFAULT_MEASURES)
    scored: list[tuple[str, float]] = []
    for name, m in catalogue.items():
        if m.name == "time_shift":
            moved = annual_heat_kwh * m.shiftable_fraction
            annual_gbp = moved * unit_rate_p_per_kwh / 100.0 * TIME_SHIFT_PRICE_ADVANTAGE
        else:
            annual_gbp = (
                measure_annual_saving_kwh(hlc_kw_per_k, annual_heat_kwh, m)
                * unit_rate_p_per_kwh
                / 100.0
            )
        scored.append((name, annual_gbp * m.lifetime_years - m.capex_gbp))
    scored.sort(key=lambda kv: (-kv[1], kv[0]))
    return scored


@dataclass(frozen=True)
class MoneyConsequence:
    """What the fabric gap COSTS: the value forgone by choosing a measure on a
    belief instead of on the truth, plus the carbon that decision did not save."""

    premises: int
    misranked_premises: int
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
    measures: Mapping[str, MeasureEconomics] | None = None,
) -> MoneyConsequence:
    """The money consequence of deciding on `belief` instead of on the truth.

    For each premise: rank the measures on the belief, rank them on the truth, and
    if the top choice differs, charge the difference in TRUE lifetime value between
    the measure that would have been chosen and the measure that should have been.
    A premise where the belief is wrong but the RANKING survives costs nothing —
    which is the honest reading, and is why this is a decision metric rather than
    an error metric.

    Savings are counted only from reduced or time-shifted kWh (`rank_measures`
    prices no tariff change), so no result here can be manufactured by discounting.
    """
    _require_homes(observations, minimum=MIN_HOMES_FOR_DIVERSITY, name="money_consequence")
    if belief not in ("epc", "inferred"):
        raise ValueError(f"unknown belief {belief!r}")
    if fuel not in CARBON_KG_PER_KWH:
        raise ValueError(f"unknown fuel {fuel!r} — no published carbon factor")

    catalogue = dict(measures or DEFAULT_MEASURES)
    misranked = 0
    forgone_gbp = 0.0
    forgone_kwh = 0.0
    for o in observations:
        held = o.epc_hlc_kw_per_k if belief == "epc" else o.inferred_hlc_kw_per_k
        if not math.isfinite(held) or held <= 0.0:
            raise InsufficientEvidence(f"{o.premise_id}: a non-positive belief is not decidable")
        # The heat demand the company BELIEVES this home has, scaled from the
        # observed demand by the ratio of believed to actual fabric — the company
        # sees the bill, so its demand estimate is anchored, but it attributes that
        # demand to the fabric it believes in.
        believed_heat = o.annual_heat_kwh * held / o.actual_hlc_kw_per_k
        chosen = rank_measures(
            held, believed_heat, unit_rate_p_per_kwh=unit_rate_p_per_kwh, measures=catalogue
        )[0][0]
        truth_ranked = rank_measures(
            o.actual_hlc_kw_per_k,
            o.annual_heat_kwh,
            unit_rate_p_per_kwh=unit_rate_p_per_kwh,
            measures=catalogue,
        )
        best = truth_ranked[0][0]
        if chosen == best:
            continue
        misranked += 1
        true_values = dict(truth_ranked)
        forgone_gbp += true_values[best] - true_values[chosen]
        forgone_kwh += (
            measure_annual_saving_kwh(o.actual_hlc_kw_per_k, o.annual_heat_kwh, catalogue[best])
            - measure_annual_saving_kwh(o.actual_hlc_kw_per_k, o.annual_heat_kwh, catalogue[chosen])
        )
    return MoneyConsequence(
        premises=len(observations),
        misranked_premises=misranked,
        forgone_lifetime_gbp=forgone_gbp,
        forgone_annual_kwh=forgone_kwh,
        forgone_annual_kg_co2e=max(0.0, forgone_kwh) * CARBON_KG_PER_KWH[fuel],
        basis=(
            f"PROVISIONAL — lifetime net value at {unit_rate_p_per_kwh:g} p/kWh on "
            f"domain-knowledge retrofit capex; savings from reduced or time-shifted "
            f"kWh only, never from discounting. Belief = {belief}."
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
        "money_consequence_epc": {
            "misrank_rate": money_epc.misrank_rate,
            "forgone_lifetime_gbp": money_epc.forgone_lifetime_gbp,
            "forgone_annual_kg_co2e": money_epc.forgone_annual_kg_co2e,
            "gbp_per_tonne_co2e": money_epc.gbp_per_tonne_co2e,
            "basis": money_epc.basis,
        },
        "money_consequence_inferred": {
            "misrank_rate": money_inferred.misrank_rate,
            "forgone_lifetime_gbp": money_inferred.forgone_lifetime_gbp,
            "forgone_annual_kg_co2e": money_inferred.forgone_annual_kg_co2e,
            "gbp_per_tonne_co2e": money_inferred.gbp_per_tonne_co2e,
            "basis": money_inferred.basis,
        },
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
