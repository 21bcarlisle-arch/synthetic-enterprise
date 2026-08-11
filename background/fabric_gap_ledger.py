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

import hashlib
import math
import random
import statistics
from dataclasses import dataclass, replace as _dc_replace
from enum import Enum
from pathlib import Path
from typing import Mapping, Sequence

from background import lcl_household_anchors as lcl_anchors
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
    INSUFFICIENT = "insufficient_to_judge"         # too few judged homes to have power


# ---------------------------------------------------------------------------
# SCALE INVARIANCE — why the L1 verdict is a RATE and not a worst-of-N
# ---------------------------------------------------------------------------
#
# The first version of this suite judged every L1 cell on the WORST home. A
# worst-of-N is monotone in N by construction: it can only move away from the
# band as homes are added, so the SAME generator on the SAME weather with the
# SAME seed scored green at n=25 and red at n=200 and the report said nothing
# about which n produced the verdict
# (`docs/staging/WORKER_FINDING_WORST_OF_N_CONTROL_IS_NOT_SCALE_INVARIANT_2026-08-09.md`).
# A reader could not tell a worse generator from a bigger sample.
#
# THE FIX IS TO THE STATISTIC, NEVER TO THE ANCHORED BAND. Every per-home band
# below stays exactly where it was and keeps its own anchor; what changes is what
# is done with the per-home verdicts. Each home is judged against its own band and
# the CELL reports the VIOLATION RATE — the share of judged homes outside their
# band. A rate converges as n grows instead of drifting, so the same generator
# scores the same thing at n=25 and n=200 and a MOVE in the number is a move in
# the world.
#
# AND THE FAIL-OPEN DIRECTION IS THE ONE THAT NEEDED CLOSING. The old form was not
# merely noisy at small n, it was WEAK: a clean sheet over ten homes is consistent
# with a true violation rate of 26%, so a genuinely bad generator would likely
# pass. A zero-violation result is therefore only allowed to be a PASS when the
# sample could have DETECTED a violation rate this suite cares about. The bound is
# the rule of three (Hanley & Lippman-Hand, JAMA 1983): observing zero events in n
# independent trials puts the one-sided 95% upper bound on the true rate at 3/n.
#
# REQUIRED_RATE_RESOLUTION is a CONTROL-DESIGN parameter, not a fidelity band — it
# says how small a defect this suite claims to be able to see, and it can only ever
# make the control stricter as the population grows. It is not a number any
# generator can move, so it is not goal-seekable (R12).
RULE_OF_THREE = 3.0
REQUIRED_RATE_RESOLUTION = 0.05
MIN_HOMES_FOR_L1_RATE = math.ceil(RULE_OF_THREE / REQUIRED_RATE_RESOLUTION)  # 60


def detectable_violation_rate(homes_judged: int) -> float:
    """The smallest true violation rate a CLEAN sheet over `homes_judged` homes
    rules out at one-sided 95% — the rule of three, 3/n.

    Raises on zero rather than returning infinity: a cell with no judged home has
    not measured anything, and an unavailable check is a FAILED check (R15)."""
    if homes_judged <= 0:
        raise InsufficientEvidence(
            "a violation rate over zero judged homes has no resolution at all"
        )
    return RULE_OF_THREE / homes_judged


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


def half_hourly_texture(
    days: Sequence[Sequence[float]],
    *,
    machines: Sequence[Sequence[float]] | None = None,
) -> float:
    """L1.1 — median |x[t] - x[t-1]| over the whole window, divided by mean(x),
    read on the meter NET OF THE HEATING MACHINES.

    Dimensionless, so a big house and a small house are judged the same way.
    Steps are taken WITHIN each day and across the midnight boundary, because a
    generator that is smooth inside the day but jumps at midnight is not spiky,
    it is discontinuous.

    WHY THE NETTING (H36, 2026-08-10), and it is a measurement rather than a
    preference. This statistic is a ratio to the home's OWN MEAN, and its 0.15
    floor reasons from a purely behavioural denominator ("a kettle is 2.8 kW for
    three minutes on a ~0.7 kWh half-hour"). Where the heating machine is on the
    judged meter that denominator is not behavioural, and the previous repair —
    rescale the FLOOR by the heat share of ONE published typical home — bought a
    fixed number for every home size. Measured on the live panel, the behavioural
    share ranges 0.30-0.74 across six electrically heated homes, so the single
    rescaled floor was 25% too strict for the largest and (the part that matters)
    fail-open for the smallest: with each home's behaviour replaced by its own
    mean profile — smooth by construction, no appliance event anywhere — FIVE of
    the six still cleared their rescaled band on the whole meter, because the
    heating machine's own movement stood in for the behaviour that was gone.
    Read net of space heat, all six fail. See `docs/design/BAND_NULL_SWEEP.md`
    (H36) for the per-home tables.

    So the floor stops moving and the LOAD SET does, which is the netting L1.2
    and L1.3 already apply (`meter_net_of_machines`). One number, every home
    size, no published efficiency for any machine — a heating regime this file
    has no figure for is now judged like any other rather than needing its own.

    THE WATER HEATER IS THE SECOND MACHINE (H38, 2026-08-10). Taking the space
    heater out left one, and it is 36-40% of what this cell then called
    behaviour. It is not caught by being spiky or smooth — three 12-minute draws
    a day move six steps in 47, and this statistic's numerator is a MEDIAN, which
    is exactly robust to that. It is caught in the DENOMINATOR: it adds ~38% to
    the mean of a stream whose floor was derived where it was absent. The 0.15
    anchor reasons from a gas-heated home's electricity meter, and a gas-heated
    home heats its water with gas — so the anchor population never carried this
    load, and the netting restores the load set the floor was derived on rather
    than granting anyone leniency.

    MEASURED IN THE UNIT THAT COMPARES REGIMES, on the drawn 60 (`base_seed=17`,
    real Open-Meteo 2022-01-01..2022-04-30), as "how much of its behaviour must
    this home lose before the cell fires" — the same critical-flattening weight
    H36 used, because raw values across regimes are not comparable and this is:

        homes                      net of space heat    net of BOTH machines
        57 gas homes (median)             0.3066               0.3066
        P0008   electric_direct           0.0000               0.2721
        P0020   electric_direct           0.0168               0.3119
        P0033   electric_storage          0.0914               0.3892

    An electrically heated home was firing at 1.7% breakage where a gas home
    needed 31% — an 18x gap, and P0008 at 0.0000 was already under the floor
    with nothing done to it at all. Net of both machines the three land at
    0.2721-0.3892, astride the gas median. The gas column is IDENTICAL in both
    readings and is not a target that was tuned toward: it is the untouched
    anchor population, and it is what makes this a load-set repair rather than a
    loosening. R12 holds — the floor is still 0.15.

    FAIL-CLOSED on absence: `machines=None` judges the whole meter, exactly as
    before. The leniency is bought with a stated fact and the fact is checked.
    """
    grid = _require_days(days, minimum=MIN_DAYS_FOR_TEXTURE, name="half_hourly_texture")
    grid = meter_net_of_machines(grid, machines)
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


def meter_net_of_machines(
    days: Sequence[Sequence[float]],
    machines: Sequence[Sequence[float]] | None,
) -> list[list[float]]:
    """The judged meter with the HEATING MACHINES taken back out — the load set
    L1.2's band was actually derived to judge.

    TWO MACHINES, ONE STREAM (H38, 2026-08-10). `machines` is the combined draw
    of the space heater and the water heater, summed by `machine_draw` before it
    gets here. It was the space heater alone until H38 measured the second one;
    the per-cell arguments for including the water heater are on the three
    statistics that consume this, because they are three different arguments and
    only one of them is about the denominator.

    WHY THIS EXISTS, and it is a measurement rather than a preference. L1.2's
    0.85 band is a statement about HOUSEHOLDS ("meals, showers and departures
    move by tens of minutes"). It is applied to the ELECTRICITY meter. For a
    gas-heated home those are the same thing; for a home whose heat is electric
    the meter also carries a thermostat, and a thermostat is supposed to repeat.
    Measured on the drawn population (n=200, `population_seed=17`, real
    Open-Meteo archive 2022-01-01..2022-04-30) the two are not close:

        stream                      median day-to-day shape correlation
        heating, gas combi homes                 0.9197   (on the GAS meter)
        heating, gas system homes                0.9080   (on the GAS meter)
        heating, electric storage home           0.9133   (on the ELECTRICITY meter)
        behaviour, every regime                  0.21 - 0.32

    The generator makes heat equally repeatable and behaviour equally diverse in
    EVERY regime. The only thing separating a home that breaches L1.2 from one
    that does not is WHICH METER its heat lands on — which is a fact about the
    house's plumbing, not about whether the generator can produce a household.
    That is the L1.1 class one cell over (`texture_band_for`): a band keyed on a
    population whose heating regime it never names.

    WHY NET RATHER THAN RESCALE THE BAND. L1.1's band could be RE-DERIVED for the
    regime, because that statistic is a ratio to the home's own mean and the mix
    arithmetic follows from published consumption shares alone. A correlation
    does not: blending two streams needs the heating stream's OWN repeatability,
    for which no published figure exists, so any regime-specific L1.2 threshold
    would be a number I chose. Comparing the same load set needs no new number at
    all, and the 0.85 band is untouched.

    FAIL-CLOSED. `machines=None` (a generator that supplies no split) returns
    the meter UNCHANGED, so the whole meter is judged — the strict reading. The
    leniency has to be bought with a stated fact, and the fact is checked: the
    stream must be finite and non-negative everywhere (a heating machine draws,
    it does not generate) and must not exceed the meter it claims to be part of
    over the window. What it may NOT be checked against is each day's own total,
    because a PV home legitimately exports on a mild day and its net meter can
    then be smaller than its heat draw without the split being wrong.

    The result may go slightly negative for the same reason (measured worst case
    -0.0125 kWh in a half hour, on solar homes), which is a meter reading, not a
    load, and the correlation that consumes it neither needs nor assumes
    positivity.
    """
    grid = [list(day) for day in days]
    if machines is None:
        return grid
    heat = _require_component_of_meter(grid, machines)
    return [[v - h for v, h in zip(meter_day, heat_day)]
            for meter_day, heat_day in zip(grid, heat)]


def machine_draw(
    space_heat: Sequence[Sequence[float]] | None,
    water_heat: Sequence[Sequence[float]] | None,
) -> list[list[float]] | None:
    """The two machine streams added into the one stream the L1 cells net out.

    Separated from the subtraction because the ABSENCE rule is the whole of it,
    and it is fail-closed in the direction that costs the harness rather than the
    generator: a stream that is not supplied is not zero, it is UNKNOWN, and a
    machine that might be on the judged meter and cannot be pointed to must stay
    IN the judged meter. So `None` anywhere makes the whole result `None` and the
    caller judges the WHOLE meter — the strict reading — instead of quietly
    netting the half it happens to have been given.

    A home whose heat is on the other commodity supplies ZEROS, which is a stated
    fact ("no machine on this meter") and a different thing from silence. That is
    why the nine gas homes read bit-for-bit what they read before H38 rather than
    being excused from the netting.
    """
    if space_heat is None or water_heat is None:
        return None
    space = [list(day) for day in space_heat]
    water = [list(day) for day in water_heat]
    if len(space) != len(water):
        raise InsufficientEvidence(
            f"the space-heat stream spans {len(space)} days and the water-heat "
            f"stream {len(water)} — they are streams off the same meter"
        )
    for k, (s_day, w_day) in enumerate(zip(space, water)):
        if len(s_day) != len(w_day):
            raise InsufficientEvidence(
                f"day {k}: the space-heat stream has {len(s_day)} periods and the "
                f"water-heat stream {len(w_day)}"
            )
    return [[s + w for s, w in zip(s_day, w_day)]
            for s_day, w_day in zip(space, water)]


def _require_component_of_meter(
    grid: list[list[float]],
    machines: Sequence[Sequence[float]],
) -> list[list[float]]:
    """Check the claim before acting on it: is this stream actually a PART of that
    meter? Separated from the subtraction because it is the whole of the guard —
    the netting itself is one line, and an unchecked subtraction would let a
    generator declare its behaviour to be heat and walk out of the cell.

    What it can NOT check is that the stream is the machine it says it is —
    only that it fits inside the meter. That hole is the same size it was
    when the stream was space heat alone (H36) and H38 did not widen it: the
    streams come off the generator's own `heating_fuel_kwh` and
    `dhw_fuel_kwh`, keyed on the trace's stated heating commodity, and a
    generator that could lie about which of its own components is a machine
    can already lie about the meter."""
    heat = [list(day) for day in machines]
    if len(heat) != len(grid):
        raise InsufficientEvidence(
            f"the machine stream spans {len(heat)} days and the meter {len(grid)}"
        )
    total_meter = 0.0
    total_heat = 0.0
    for k, (meter_day, heat_day) in enumerate(zip(grid, heat)):
        if len(heat_day) != len(meter_day):
            raise InsufficientEvidence(
                f"day {k}: the machine stream has {len(heat_day)} periods and "
                f"the meter {len(meter_day)}"
            )
        for v in heat_day:
            if not math.isfinite(v):
                raise NonFiniteTrace(f"day {k}: a non-finite machine-draw value {v!r}")
            if v < 0.0:
                raise InsufficientEvidence(
                    f"day {k}: a machine draw of {v!r} — a heating machine draws "
                    "energy, it does not generate it"
                )
        total_meter += sum(meter_day)
        total_heat += sum(heat_day)
    if total_heat > total_meter:
        raise InsufficientEvidence(
            f"a machine stream of {total_heat:.4g} kWh over a meter that read "
            f"{total_meter:.4g} kWh is not a COMPONENT of that meter"
        )
    return heat


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

    WHICH LOAD SET IT MUST BE READ ON (H37). This ratio is only an occupancy
    statistic while the denominator is a BASE load. A heat pump runs THROUGH
    00:00-06:00, so on the electricity meter of an electrically-heated home the
    denominator is the thermostat, not the fridge, and the ratio collapses towards
    1.0 for a household that never left. Read the behavioural stream
    (`meter_net_of_machines`) — `trough_statistics(days, machines=...)` does
    it — or this function will call an occupied house empty. It takes no view of
    its own input: give it the wrong stream and it will answer about that one.
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
    days: Sequence[Sequence[float]],
    *,
    machines: Sequence[Sequence[float]] | None = None,
    signature_max: float = AWAY_SIGNATURE_MAX,
) -> TroughStats:
    """L1.3 — the minimum half-hour, and the count of days on which this home was
    demonstrably empty.

    The threshold is derived from occupancy PHYSICS (a day no busier than its own
    3am) and from each home's OWN trace, never from the generator's parameters —
    so it does not re-tautologise the check.

    THE AWAY SIGNATURE IS READ ON THE BEHAVIOURAL STREAM (H37), for the same
    reason L1.2 is (`meter_net_of_machines`) and by the same netting, but the
    argument here is a different one and stands on its own. L1.2's is that a
    thermostat is supposed to repeat, so a correlation band about households is
    unfair to a home whose heat is on the judged meter. L1.3's is stronger: the
    away signature DIVIDES BY the base-load window, and a heat pump does not stop
    at midnight. Its draw enters the denominator, the ratio falls below the 1.30
    threshold on days nobody left, and the home reads empty. Measured on the live
    panel (`tools/couple_fabric.PANEL`, 15 homes x 120 days, against each trace's
    own `is_away` calendar):

        stream            true away days   detected   false positives   recall
        electricity meter          177        176            217         0.994
        net of space heat          177        177             23         1.000

    Recall goes UP, not down — netting removes 194 false positives and finds the
    one true absence the meter had buried (E15, a resistive home). The nine
    gas-heated homes read bit-for-bit what they did before, because a home whose
    heat is on the other meter contributes a stream of zeros.

    THE WATER HEATER IS THE SAME ARGUMENT, ONE MACHINE OVER (H38, 2026-08-10),
    and this was the surprise rather than the expectation. A hot-water draw is
    an EVENT on the household's own clock, so the prior was that netting it would
    remove a genuine occupancy signal and cost recall. Measured on the drawn 60
    (`base_seed=17`, 120 days, 849 true away days, against each trace's own
    `is_away` calendar) it does the opposite:

        stream                 detected   false positives   recall
        net of space heat           849                 8    1.000
        net of BOTH machines        849                 0    1.000

    All eight false positives are P0008, and the mechanism is H37's exactly: an
    early-rising household draws hot water INSIDE the 00:00-06:00 base-load
    window, which is the denominator. Day 68 is the clean case — 1.674 kWh of
    water heat in the base window and 0.000 kWh in the active window — and the
    ratio falls from 4.17 to 1.15, under the 1.30 threshold, on a day nobody
    left. Recall does not move because a water heater draws nothing on an away
    day (`draw_dhw_events` returns none when the house is empty), so the netting
    is the identity on exactly the days this statistic exists to find.

    `min_half_hour_kwh` stays on the METER, unnetted: it is a statement about what
    the meter can read, not about occupancy.

    FAIL-CLOSED, inherited. `machines=None` judges the WHOLE meter, exactly as
    before this argument existed — the leniency has to be bought with a stated,
    checked fact. And netting can only make this statistic's base-load window
    MORE of a base load: what is left after the heating machine comes out is the
    fridge and the standby draw, which is the load the 1.30 threshold was always
    about (measured minimum over the panel, 0.034 kWh per half hour, so the
    non-positive-base branch above stays unreached rather than newly plausible).

    R12: neither `AWAY_SIGNATURE_MAX` (1.30) nor the band's 1.0 away-days-per-year
    floor moved. The load set was wrong, not the number.
    """
    if not math.isfinite(signature_max) or signature_max <= 1.0:
        raise InsufficientEvidence(
            "the away signature threshold must be finite and greater than 1.0"
        )
    grid = _require_days(days, minimum=MIN_DAYS_FOR_TEXTURE, name="trough_statistics")
    behavioural = meter_net_of_machines(grid, machines)
    signatures = [away_signature(day) for day in behavioural]
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


# ---------------------------------------------------------------------------
# L1.4n — THE SAME DISTANCE, JUDGED AGAINST THE HOME'S OWN PERMUTATION NULL
# ---------------------------------------------------------------------------
#
# WHY THIS EXISTS, and it is the direct repair of a named defect in this file.
# `weekday_weekend_separation` above is a distance between two SUBSETS of one
# home's days, and a distance between two subsets is bounded away from zero by
# sampling noise alone: with 85 weekday days against 35 weekend ones, two
# ARBITRARY halves of the same home differ by about as much as a real household's
# weekday differs from its weekend over a full year. That is not a conjecture —
# it was measured on 2026-08-09, and it is why the Low Carbon London anchor for
# L1.4 was derived, wired, and taken back out within the hour: a day-type
# RANDOMISED population cleared the floor with a 1.4x margin, and a band a
# structureless population clears is fail-open (R15).
#
# THE REPAIR IS TO THE STATISTIC, NOT THE THRESHOLD. Each home is compared with
# ITSELF under `WEEKDAY_WEEKEND_NULL_SAMPLES` random relabellings of its own
# day-type calendar, holding the weekday/weekend COUNTS fixed. The judged number
# is the ratio of the real separation to the 95th percentile of that null — a
# one-sided permutation test at alpha = 0.05, expressed so that 1.0 is the
# decision point and the number itself reads as "this home's weekday/weekend
# distance is N times what an arbitrary split of its own days achieves".
#
# NOT A TAUTOLOGY, and this is the R15 pattern most likely to be alleged here:
# the null is built from the same home's data, so it looks like a value checked
# against itself. What is destroyed in the null is exactly the thing under test —
# the ASSOCIATION between the calendar and the shape — while the home's own
# noise, level and day-to-day variability are held. The proof is not the argument
# but the measurement: on the drawn population the real labelling reads a median
# ratio of 1.45 with 1 home of 60 below 1.0, and the randomised labelling reads
# 0.75 with 58 of 60 below. A tautological statistic cannot separate those.
#
# WHAT THIS STILL DOES NOT ANSWER. This band asks whether a home has ANY real
# weekday/weekend structure. It does NOT ask whether that structure is as LARGE
# as a real household's — that is a magnitude question, it needs an external
# panel, and it remains `AnchorStatus.NEED` on the raw L1.4 cell below. The LCL
# extract in this repo cannot close it: it carries each household's ANNUAL MEAN
# weekday and weekend shape, so the panel's own null cannot be computed from it,
# and null-correcting one side of a comparison and not the other is the same
# window-mismatch error in new coordinates.

#: A one-sided permutation test at alpha = 0.05. 99 samples so the 95th
#: percentile is an order statistic rather than an interpolation.
WEEKDAY_WEEKEND_NULL_SAMPLES = 99
WEEKDAY_WEEKEND_NULL_QUANTILE = 0.95

#: Named rather than a literal at the call site (C-S2, RNG substream discipline):
#: a threshold that can be moved by quietly reseeding is not a threshold.
WEEKDAY_WEEKEND_NULL_SEED = 90210

#: THE DEGENERACY GUARD IS RELATIVE, NOT `> 0.0`, and it was written that way
#: because `> 0.0` did not hold. A home whose days are all IDENTICAL has a true
#: null of exactly zero, but the two branches of the difference are summed in a
#: different order, so it computes as ~1e-18 rather than 0.0 — and the ratio of
#: two rounding errors is a number between 0 and 2 that reads as an ordinary
#: verdict. A separation is a total-variation distance between vectors that sum
#: to 1, so it lives in [0, 1] and a real one is O(0.1); 1e-9 is nine orders
#: below anything meaningful and cannot be reached by a home that has structure.
WEEKDAY_WEEKEND_NULL_DEGENERATE_BELOW = 1e-9


class DegenerateNull(InsufficientEvidence):
    """This subject has no null to be judged against — every re-draw gives the
    same reading. Raised by L1.4n for ONE HOME whose relabelled days give the same
    mean shape, and by L2.3n for a POPULATION whose re-dealt days give the same
    timing spread. One type because the two are the same condition at different
    scopes, and a caller that must decide what to score a subject with no null
    would otherwise grow a second except-clause saying the same thing.

    A separate type because the two insufficiencies must be handled differently
    and conflating them was a real defect for the length of one test run: too few
    DAYS is a fact about the RUN and must stop it, while a degenerate null is a
    fact about ONE HOME and must not — a population containing a single flat home
    would otherwise abort the whole suite, which is a control that cannot report.
    What the cell does with it is a decision stated at the call site, not here.
    """


@dataclass(frozen=True)
class SeparationAgainstNull:
    """L1.4n — one home's weekday/weekend separation beside its own null."""

    raw: float
    null_median: float
    null_p95: float
    samples: int

    @property
    def ratio(self) -> float:
        """THE judged statistic. >= 1.0 means the real day-type calendar explains
        more of this home's shape than an arbitrary relabelling of its own days
        does 95% of the time."""
        return self.raw / self.null_p95


def weekday_weekend_separation_vs_own_null(
    days: Sequence[Sequence[float]],
    is_weekend: Sequence[bool],
    *,
    samples: int = WEEKDAY_WEEKEND_NULL_SAMPLES,
    seed: int = WEEKDAY_WEEKEND_NULL_SEED,
) -> SeparationAgainstNull:
    """L1.4n — `weekday_weekend_separation` judged against this home's own
    permutation null. Deterministic given `seed` (C-S2).

    FAIL-CLOSED in every direction an unavailable check could take (R15): too few
    days or too few of either day type RAISES via the same guards the raw
    statistic uses; a non-finite reading RAISES; and a degenerate null — every
    relabelling of this home's days giving the same mean shape, so the
    denominator is zero — RAISES rather than returning an infinite ratio that
    would read as a spectacular pass.
    """
    grid = _require_days(
        days, minimum=MIN_DAYS_FOR_TEXTURE, name="weekday_weekend_separation_vs_own_null"
    )
    if len(is_weekend) != len(grid):
        raise InsufficientEvidence("day-type flags must align with the trace days")
    if samples < 2:
        raise InsufficientEvidence("a permutation null over fewer than two samples is theatre")

    # Normalise each non-empty day ONCE. Every relabelling is then a re-partition
    # of the same normalised shapes, which is what makes the null affordable.
    shapes: list[list[float]] = []
    weekend_flags: list[bool] = []
    for day, flag in zip(grid, is_weekend):
        total = sum(day)
        if total > 0.0:
            shapes.append([v / total for v in day])
            weekend_flags.append(bool(flag))
    n = len(shapes)
    n_weekend = sum(weekend_flags)
    if n_weekend < 5 or n - n_weekend < 5:
        raise InsufficientEvidence(
            f"need >= 5 non-empty days of each type; got {n - n_weekend} weekday / "
            f"{n_weekend} weekend"
        )

    total_shape = [0.0] * PERIODS_PER_DAY
    for shape in shapes:
        for p in range(PERIODS_PER_DAY):
            total_shape[p] += shape[p]

    def separation(weekend_index: Sequence[int]) -> float:
        acc = [0.0] * PERIODS_PER_DAY
        for i in weekend_index:
            shape = shapes[i]
            for p in range(PERIODS_PER_DAY):
                acc[p] += shape[p]
        k = len(weekend_index)
        return 0.5 * sum(
            abs((total_shape[p] - acc[p]) / (n - k) - acc[p] / k) for p in range(PERIODS_PER_DAY)
        )

    raw = separation([i for i, w in enumerate(weekend_flags) if w])
    rnd = random.Random(seed)
    null = sorted(separation(rnd.sample(range(n), n_weekend)) for _ in range(samples))
    p95 = null[min(int(WEEKDAY_WEEKEND_NULL_QUANTILE * (samples - 1)), samples - 1)]
    if not math.isfinite(raw) or not math.isfinite(p95):
        raise InsufficientEvidence("a non-finite separation cannot be judged")
    if p95 <= WEEKDAY_WEEKEND_NULL_DEGENERATE_BELOW:
        raise DegenerateNull(
            f"this home's permutation null is degenerate (p95 {p95:.3g}) — every "
            "relabelling of its days gives the same mean shape, so there is no null "
            "to judge against and the ratio would be one rounding error over another"
        )
    return SeparationAgainstNull(
        raw=raw, null_median=statistics.median(null), null_p95=p95, samples=samples
    )


# ---------------------------------------------------------------------------
# L1.1n — THE SAME TEXTURE, JUDGED AGAINST THE HOME'S OWN FLAT COUNTERFACTUAL
# ---------------------------------------------------------------------------
#
# WHY THIS EXISTS (H39, 2026-08-10). `half_hourly_texture` is `median |x[t] -
# x[t-1]| / mean(x)`, and a home's OWN MEAN DIURNAL PROFILE already moves between
# adjacent half-hours: the morning ramp and the evening peak are period-to-period
# steps that are there whether or not the generator ever fired an appliance. So
# the reading a structureless generator gets is not zero and is not the same for
# every home — it is that home's profile's own roughness, a property of the HOME
# rather than of the generator's honesty. Measured on the live 15-home panel with
# every appliance event removed, the flat reading runs 0.0365 (S3) to 0.1009
# (H12): a 2.8x range under one 0.15 floor. The band-null sweep reads the same
# fact from the outside — the floor clears the 95th percentile of its own null by
# 0.0550 against a null spread across homes of 0.0558.
#
# WHAT THAT COSTS, IN BOTH DIRECTIONS, and neither is hypothetical:
#   * FAIL-OPEN. A home whose mean profile is rough enough between adjacent
#     half-hours needs almost no real behaviour to reach 0.15. The roughest home
#     on the panel is already at 67% of the floor with nothing in it at all (69%
#     on the drawn 60), and a generator that rescales ONE REAL DAY as its base
#     shape clears the floor at EVERY home — measured, below — while having no
#     day-to-day behaviour in it at all, which is the one thing the floor's own
#     anchor text says it exists to fire on.
#   * FALSE POSITIVE. A home with a flat profile has to manufacture the whole
#     0.15 out of appliance events. On the drawn 60 the marginal home sits at
#     0.1521 — 1.4% above the floor — while reading 4.26x its own flat
#     counterfactual, and the home at 2.14x (the closest in the population to its
#     own null) reads 0.1750 and is nowhere near the floor. The floor's ranking
#     of these homes and the evidence's disagree.
#
# THE REPAIR IS TO THE STATISTIC, NOT THE THRESHOLD — and NOT by moving 0.15 in
# either direction, which would be fitting the number to the population (R12 read
# backwards). Each home is compared with ITSELF under the flat counterfactual:
# every day's behavioural stream replaced by that home's own mean behavioural
# profile rescaled to that day's own behavioural total. Level, diurnal shape and
# daily totals all survive; appliance events do not. The judged number is the
# ratio of the two readings, so 1.0 is the decision point BY CONSTRUCTION and the
# number itself reads as "this home's meter is N times rougher than its own
# smooth counterfactual".
#
# THE NULL IS A POINT MASS, WHICH IS THE DIFFERENCE FROM L1.4n ABOVE. L1.4n's null
# is 99 random relabellings, so its 1.0 is a 95th percentile and a structureless
# home clears it 1 time in 20 — its size, not a fail-open. Here the flat
# counterfactual is DETERMINISTIC and idempotent, so a structureless population
# reads EXACTLY 1.0 with no spread at all. That is a stronger null and a sharper
# trap: measured on the panel's own flat null, 15 of 15 homes read 1.0 to within
# 2.4e-15 and FIVE OF THEM LAND ABOVE 1.0 on floating-point rounding alone. A
# band written as `at_least 1.0` would therefore pass a third of a
# smooth-by-construction population, which is the defect this cell is for. Hence
# the tolerance below: it is a NUMERICAL constant sized by float error, not a
# threshold anyone may tune.
#
# WHAT THIS STILL DOES NOT ANSWER, and it is the same gap L1.4n leaves. This band
# asks whether a home has ANY texture of its own beyond its mean profile. It does
# NOT ask whether that texture is as LARGE as a real household's — that is the
# MAGNITUDE question, it is what the 0.15 floor is for, and the two are reported
# as separate cells for the reason L1.4/L1.4n already are: collapsing them into
# one name would be one name carrying two numbers. The floor does not move here.

#: The ratio a structureless population reads is exactly 1.0, so the decision
#: point is "anything above 1.0" — and the only reason this is not written as
#: 1.0 is that the two readings are the same arithmetic in a different order and
#: differ in their last bits. A real home reads 2.1-6.5 on every population
#: measured, so 1e-9 is nine orders below anything a textured home can reach and
#: cannot be crossed by adding behaviour. Sized against float error, never
#: against where the population sits.
TEXTURE_NULL_RATIO_TOLERANCE = 1e-9

#: A home whose flat counterfactual has a zero median step has no null to be
#: judged against. Relative, not `> 0.0`, for the reason recorded on
#: `WEEKDAY_WEEKEND_NULL_DEGENERATE_BELOW`: the ratio of two rounding errors
#: reads as an ordinary verdict. The statistic is a step over a mean, so a real
#: reading is O(0.1) and 1e-9 is eight orders below it.
TEXTURE_NULL_DEGENERATE_BELOW = 1e-9


def flatten_to_mean_profile(days: Sequence[Sequence[float]]) -> list[list[float]]:
    """One home's days, each replaced by the home's own mean profile rescaled to
    THAT DAY'S OWN total — the flat counterfactual L1.1n is judged against.

    What survives: the home's level, its mean diurnal shape, and its daily-total
    series day for day. What is destroyed: appliance events, occupancy variation
    and any difference in shape between one day and the next.

    NOTHING IS RESAMPLED, and that is not a simplification — it is the outcome of
    two recorded mistakes, both made while building the sweep's null and both the
    same mistake. Redrawing each day's TOTAL injected level jumps across midnight
    and inflated texture from ~0.05 to ~0.35; bootstrapping the MEAN PROFILE over
    the home's own days, defended as "the estimation noise a 120-day mean
    genuinely carries", inflated it by ~30%, because sampling noise in a mean
    profile IS half-hourly movement and half-hourly movement is precisely what
    this statistic measures. A null that ADDS structure is not a null, whatever
    the noise is called. The full record is in `docs/design/BAND_NULL_SWEEP.md`.

    IT IS ALSO IDEMPOTENT, which is what makes the ratio's decision point exact:
    flattening an already-flat home returns the same home, so a structureless
    population reads 1.0 rather than something near it.

    THIS IS THE ONE FLATTENING. `background.band_null_sweep` measures L1.1's null
    by calling THIS function rather than keeping its own copy — two
    implementations of "replace each day by the mean profile" would be one name
    carrying two nulls the day one of them was tweaked, and the sweep would then
    be measuring the null of a statistic nobody applies (R15's first killer
    pattern, one module over).
    """
    grid = [list(day) for day in days]
    if not grid:
        return grid
    mean_day = [
        sum(day[p] for day in grid) / len(grid) for p in range(PERIODS_PER_DAY)
    ]
    shape_total = sum(mean_day)
    if shape_total <= 0.0:
        return grid
    unit = [v / shape_total for v in mean_day]
    return [[v * sum(day) for v in unit] for day in grid]


@dataclass(frozen=True)
class TextureAgainstNull:
    """L1.1n — one home's half-hourly texture beside its own flat counterfactual."""

    raw: float
    null: float

    @property
    def ratio(self) -> float:
        """THE judged statistic. Above 1.0 means this home's meter moves more
        between adjacent half-hours than its own mean diurnal profile does — i.e.
        some of the texture is behaviour rather than shape."""
        return self.raw / self.null


def half_hourly_texture_vs_own_null(
    days: Sequence[Sequence[float]],
    *,
    machines: Sequence[Sequence[float]] | None = None,
) -> TextureAgainstNull:
    """L1.1n — `half_hourly_texture` judged against this home's own flat
    counterfactual. Deterministic: there is no seed, so there is no reseeding
    that could move the answer (C-S2).

    READ ON THE SAME LOAD SET as the raw cell — net of the heating machines — and
    the netting happens BEFORE the flattening, not after. Flattening the meter and
    subtracting the real machine would leave `flat_meter - real_heat`, which hands
    the statistic the machine's own day-to-day movement as though it were
    behaviour; that is the exact reading H36 took out of this cell and it must not
    come back in through the null.

    FAIL-CLOSED in every direction an unavailable check could take (R15): too few
    days RAISES through the same guard the raw statistic uses; a non-positive mean
    RAISES there too; a non-finite reading RAISES; and a degenerate null — a home
    whose flat counterfactual has no half-hourly movement at all, so the
    denominator is zero — RAISES rather than returning an infinite ratio that
    would read as a spectacular pass.
    """
    netted = meter_net_of_machines([list(day) for day in days], machines)
    raw = half_hourly_texture(netted)
    null = half_hourly_texture(flatten_to_mean_profile(netted))
    if not math.isfinite(raw) or not math.isfinite(null):
        raise InsufficientEvidence("a non-finite texture cannot be judged")
    if null <= TEXTURE_NULL_DEGENERATE_BELOW:
        raise DegenerateNull(
            f"this home's flat counterfactual has no texture at all (null {null:.3g}) "
            "— its mean diurnal profile is a constant, so there is no null to judge "
            "against and the ratio would be a reading over a rounding error"
        )
    return TextureAgainstNull(raw=raw, null=null)


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


def _evening_peak_picks(days: Sequence[Sequence[float]], *, name: str) -> list[int]:
    """The evening-peak half-hour of each day that HAS one.

    THE ONLY PLACE a day's evening timing is computed. `evening_peak_period`
    averages this list, `timing_diversity` spreads those averages, and
    `timing_diversity_vs_own_null` re-partitions the same list under a permutation
    — so there is one implementation of "when does this day peak" and the three
    cannot drift into one name carrying different numbers.
    """
    grid = _require_days(days, minimum=MIN_DAYS_FOR_TEXTURE, name=name)
    window = range(29, 46)
    picks = [max(window, key=lambda p: day[p]) for day in grid]
    picks = [p for p, day in zip(picks, grid) if day[p] > 0.0]
    if not picks:
        raise InsufficientEvidence("no day has any evening usage — no peak timing to measure")
    return picks


def evening_peak_period(days: Sequence[Sequence[float]]) -> float:
    """The mean half-hour index of a home's evening (periods 30-46) maximum."""
    picks = _evening_peak_picks(days, name="evening_peak_period")
    return sum(picks) / len(picks)


def _spread_of_pick_means(pick_lists: Sequence[Sequence[int]]) -> float:
    return statistics.pstdev([sum(p) / len(p) for p in pick_lists])


def timing_diversity(homes: Sequence[Sequence[Sequence[float]]]) -> float:
    """L2.3 — the population standard deviation, in HALF-HOURS, of each home's
    mean evening-peak period.

    0.0 is a point mass: every home in the country peaks in the same half-hour,
    which is what one national `HEATING_PERIOD_WEIGHTS` constant produces.

    REPORTED, NOT JUDGED, since 2026-08-10 — the number is real and this docstring
    still describes it, but no fixed floor over it is sound at every window. See
    `timing_diversity_vs_own_null` below for why, and for the cell that judges.
    """
    _require_homes(homes, minimum=MIN_HOMES_FOR_DIVERSITY, name="timing_diversity")
    return _spread_of_pick_means(
        [_evening_peak_picks(h, name="timing_diversity") for h in homes]
    )


def deal_preserving_counts(
    items: Sequence, counts: Sequence[int], rng: random.Random
) -> list[list]:
    """Pool `items` and deal them back into groups of `counts` at random.

    THE EXCHANGEABILITY PRIMITIVE, in one place because it is used on two
    different item types and a second copy would be a second null. Dealing DAYS
    gives `band_null_sweep._exchangeable_homes_null` (a whole structureless
    population); dealing this population's evening-PEAK picks gives
    `timing_diversity_vs_own_null`'s null. Same permutation, same guarantee: after
    the deal no group has anything of its own, because its members came from the
    same pot as everybody else's.
    """
    pool = list(items)
    if len(pool) != sum(counts):
        raise InsufficientEvidence(
            f"a deal must place every item: {len(pool)} items into {sum(counts)} places"
        )
    rng.shuffle(pool)
    out: list[list] = []
    cursor = 0
    for k in counts:
        out.append(pool[cursor : cursor + k])
        cursor += k
    return out


# ---------------------------------------------------------------------------
# L2.3n — THE SAME SPREAD, JUDGED AGAINST THE POPULATION'S OWN PERMUTATION NULL
# ---------------------------------------------------------------------------
#
# WHY THIS EXISTS. It is the second instance of the defect L1.4n repaired, found
# by the sweep built to look for it (`background/band_null_sweep.py`, H33, and
# the numbers are in `docs/design/BAND_NULL_SWEEP.md`). `timing_diversity` above
# is a SPREAD OF MEANS, and a spread of sample means is bounded away from zero by
# sampling noise alone: deal one population's days out to its homes at random —
# so that no home has a timing of its own — and the statistic still reads 0.79
# half-hours at 40 days against a floor of 0.5. The floor is not too low. There
# is no height it could be moved to that would be right at every window, which is
# the whole finding:
#
#   window | a TIMING-LESS population passes the 0.5 floor | ... passes this ratio
#      40d |                                           65% |                   7%
#      60d |                                           57% |                  12%
#      90d |                                           15% |                   7%
#     120d |                                            2% |                   2%
#
# (Applied panel — `tools/couple_fabric.py`, the TEN homes it carried on that
# date; widened to 15 by H35 on 2026-08-09 — 40 independent deals per window,
# 2026-08-10; the 8-home test panel reads 68/45/15/3 against 2/5/10/5.
# The old floor's fail-open rate is a function of the WINDOW; the ratio's is flat
# at its own alpha, which is what window-invariance looks like when it is measured
# rather than asserted.)
#
# THE REPAIR IS TO THE STATISTIC, NOT THE THRESHOLD, and never to the window
# (R12). Repairing the window would only move the problem to whichever window is
# run next. The population is compared with ITSELF under
# `TIMING_DIVERSITY_NULL_SAMPLES` random re-deals of its own days' evening peaks,
# holding each home's day count fixed. The judged number is the ratio of the real
# spread to the 95th percentile of that null — a one-sided permutation test at
# alpha = 0.05, so 1.0 is the decision point by CONSTRUCTION and there is nothing
# here for anyone to tune.
#
# NOT A TAUTOLOGY. The null is built from the same population, so it looks like a
# value checked against itself. What the deal destroys is exactly the thing under
# test — the ASSOCIATION between a home and its evening timing — while every
# day's own shape, level and weather response survive intact. The proof is the
# measurement above, not the argument: a tautological statistic could not read
# 1.35-2.07 on the real panel and 0.60-0.68 on its own re-deal.
#
# WHAT THIS DOES NOT ANSWER, and it is the same gap L1.4n left. This asks whether
# the population has ANY real timing diversity. It does not ask whether that
# diversity is as WIDE as a real population's — a magnitude question needing an
# external panel of per-home half-hourly reads (SERL, or the LCL trial's raw
# archive). That stays open on the raw L2.3 cell, unjudged, exactly as L1.4 is.

#: A one-sided permutation test at alpha = 0.05. 99 samples so the 95th
#: percentile is an order statistic rather than an interpolation.
TIMING_DIVERSITY_NULL_SAMPLES = 99
TIMING_DIVERSITY_NULL_QUANTILE = 0.95

#: Named rather than a literal at the call site (C-S2, RNG substream discipline):
#: a threshold that can be moved by quietly reseeding is not a threshold.
TIMING_DIVERSITY_NULL_SEED = 20260810

#: The spread is in HALF-HOURS over a 17-period evening window, so a real one is
#: O(1) and an honest zero is exact (identical pick lists average to identical
#: floats). Nine orders below anything meaningful, for the same reason L1.4n's
#: guard is relative rather than `> 0.0`.
TIMING_DIVERSITY_NULL_DEGENERATE_BELOW = 1e-9


@dataclass(frozen=True)
class DiversityAgainstNull:
    """L2.3n — one population's timing diversity beside its own null."""

    raw: float
    null_median: float
    null_p95: float
    samples: int

    @property
    def ratio(self) -> float:
        """THE judged statistic. >= 1.0 means these homes' own evening timings
        explain more of the population's spread than dealing the same days out at
        random does 95% of the time."""
        return self.raw / self.null_p95


def timing_diversity_vs_own_null(
    homes: Sequence[Sequence[Sequence[float]]],
    *,
    samples: int = TIMING_DIVERSITY_NULL_SAMPLES,
    seed: int = TIMING_DIVERSITY_NULL_SEED,
) -> DiversityAgainstNull:
    """L2.3n — `timing_diversity` judged against this population's own
    permutation null. Deterministic given `seed` (C-S2).

    FAIL-CLOSED in every direction an unavailable check could take (R15): too few
    homes or too few days RAISES through the same guards the raw statistic uses;
    a non-finite reading RAISES; and a degenerate null — every re-deal giving the
    same spread, which is what ONE national timetable produces — RAISES rather
    than returning a ratio of one rounding error over another.
    """
    _require_homes(homes, minimum=MIN_HOMES_FOR_DIVERSITY, name="timing_diversity_vs_own_null")
    if samples < 2:
        raise InsufficientEvidence("a permutation null over fewer than two samples is theatre")

    picks = [_evening_peak_picks(h, name="timing_diversity_vs_own_null") for h in homes]
    counts = [len(p) for p in picks]
    pool = [p for home in picks for p in home]

    raw = _spread_of_pick_means(picks)
    rnd = random.Random(seed)
    null = sorted(
        _spread_of_pick_means(deal_preserving_counts(pool, counts, rnd)) for _ in range(samples)
    )
    p95 = null[min(int(TIMING_DIVERSITY_NULL_QUANTILE * (samples - 1)), samples - 1)]
    if not math.isfinite(raw) or not math.isfinite(p95):
        raise InsufficientEvidence("a non-finite timing spread cannot be judged")
    if p95 <= TIMING_DIVERSITY_NULL_DEGENERATE_BELOW:
        raise DegenerateNull(
            f"this population's permutation null is degenerate (p95 {p95:.3g}) — every "
            "re-deal of its days gives the same spread, which is what a single national "
            "evening timetable produces, so there is no null to judge against"
        )
    return DiversityAgainstNull(
        raw=raw, null_median=statistics.median(null), null_p95=p95, samples=samples
    )


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
# The L1.1 texture band is ONE NUMBER, and what moves by regime is the LOAD SET
# ---------------------------------------------------------------------------
#
# WHY THERE WAS EVER MORE THAN ONE, and why there is no longer (H36, 2026-08-10).
# L1.1 is `median |x[t] - x[t-1]| / mean(x)` — a RATIO to the home's own mean. A
# heat pump puts a large, thermally-driven load into the DENOMINATOR while adding
# little to the numerator, so on the WHOLE METER an electrically heated home is
# arithmetically smoother than a gas home with identical appliance behaviour.
# Judging both by one national floor on that reading is the one-national-constant
# defect W1_12 exists to remove, reappearing in the CONTROL
# (`docs/staging/WORKER_FINDING_L1_TEXTURE_BAND_IS_GAS_SHAPED_2026-08-08.md`).
#
# The first repair rescaled the FLOOR by the heat share of one published typical
# home, once per heating regime. That put a fixed number against every home size,
# and H35 measured what it cost on the six electrically heated homes of the live
# panel (`docs/design/BAND_NULL_SWEEP.md`): behavioural shares of 0.30-0.74, so the
# floor was 25% too strict for the largest home and fail-open for the smallest —
# five of the six cleared their rescaled band with their behaviour replaced by
# their own mean profile, no appliance event left in it, because the heating
# machine's own movement stood in for the behaviour that was gone.
#
# So the floor stops moving and the LOAD SET moves instead: L1.1 is read net of
# space heat (`half_hourly_texture(machines=...)`), where the 0.15 denominator
# argument is the one that was always meant, and every home is judged by it. What
# the register is still needed for is the ONE case the netting cannot cover — a
# home whose heat is on this meter and whose generator supplies no split. That
# home is COUNTED, not guessed at.
_GAS_TEXTURE_THRESHOLD = 0.15


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
            "APPLIES TO THE METER NET OF SPACE HEAT, WHICH IS EVERY HOME — the "
            "kettle-on-a-0.7-kWh-half-hour reasoning is a statement about the "
            "DENOMINATOR, so it holds for any home once the heating machine is out "
            "of it. That is where the regime conditioning went (H36): the floor is "
            "one number for every home size because the load set it is read on is "
            "the same load set in every regime."
        ),
        observed_on_shipped=None,
        rationale=(
            "A rescaled national average has the texture of a national average, which "
            "is the texture of a hundred thousand homes already summed."
        ),
    ),
    "L1.1n_half_hourly_texture_null_ratio": Band(
        statistic="L1.1n_half_hourly_texture_null_ratio",
        level="L1",
        direction="at_least",
        threshold=1.0 + TEXTURE_NULL_RATIO_TOLERANCE,
        anchor=AnchorStatus.STRUCTURAL,
        anchor_source=(
            "structural, and it needs no external figure because the decision "
            "point is a property of the construction: `half_hourly_texture` read "
            "on the home's own flat counterfactual against the same statistic "
            "read on the home itself, so a population with no appliance events in "
            "it reads EXACTLY 1.0 (the flattening is idempotent) and anything "
            "above 1.0 is texture the mean diurnal profile does not account for. "
            "There is nothing in it to tune. The 1e-9 is FLOAT ERROR, not a "
            "margin: the two readings are the same arithmetic in a different "
            "order, and on the live panel's own flat null 5 of 15 homes land "
            "above 1.0 by up to 2.4e-15 — so `at_least 1.0` would pass a third of "
            "a smooth-by-construction population. Real homes read 2.14-6.54 "
            "across both measured populations, nine orders clear of it. See the "
            "L1.1n note above `half_hourly_texture_vs_own_null` and the H39 "
            "section of docs/design/BAND_NULL_SWEEP.md."
        ),
        observed_on_shipped=None,
        rationale=(
            "The 0.15 floor is a MAGNITUDE band and a home's own mean diurnal "
            "profile already spends part of it: on the live panel the flat "
            "reading runs 0.0365-0.1009, so the same floor asks a 2.8x-different "
            "question of different homes and the roughest-profiled is already at 67% "
            "of it "
            "with no behaviour in it at all. This band asks the question the "
            "floor's own anchor text says it is for — is this generator smooth by "
            "construction — where the answer cannot be bought with a peaky shape."
        ),
    ),
    "L1.1u_half_hourly_texture_no_behavioural_stream": Band(
        statistic="L1.1u_half_hourly_texture_no_behavioural_stream",
        level="L1",
        direction="at_least",
        threshold=None,
        anchor=AnchorStatus.NEED,
        anchor_source=(
            "NEED — the space-heat split for a home whose register says its heat "
            "is on the JUDGED meter. Nothing published can stand in for it: the "
            "0.15 floor is a statement about a behavioural denominator, and for "
            "this home the behavioural stream is not recoverable from what the "
            "generator supplied. It is MEASURED AND COUNTED, never judged and "
            "never folded into the floor. Both silent folds are wrong in a "
            "different direction: judging the whole meter at 0.15 fails a correct "
            "heat pump for owning a thermostat, and rescaling the floor by an "
            "assumed home is the fixed-number-for-every-home-size defect this "
            "band replaced (H36). The unjudged count is reported on the cell and "
            "the cell goes INSUFFICIENT if too much of the population lands here, "
            "so a missing split cannot be mistaken for a green suite."
        ),
        observed_on_shipped=None,
        rationale="A generator that cannot say is a visible hole, not a default.",
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
            "fires only on near-replay. A SERL-anchored band is registered as NEED. "
            "THE THRESHOLD IS UNMOVED SINCE IT WAS WRITTEN; what changed on "
            "2026-08-09 is WHAT IT IS APPLIED TO. The sentence above describes a "
            "HOUSEHOLD, so it is judged on the meter NET OF SPACE HEAT "
            "(`meter_net_of_machines`) — otherwise the same band judges "
            "behaviour in a gas-heated home and a thermostat in an electrically "
            "heated one, and a thermostat is supposed to repeat. The heating "
            "stream's own repeatability is reported separately and never judged."
        ),
        observed_on_shipped=None,
        rationale="Normalised to the daily total, so this is shape, not weather.",
    ),
    "L1.2h_heating_shape_repeatability": Band(
        statistic="L1.2h_heating_shape_repeatability",
        level="L1",
        direction="at_most",
        threshold=None,
        anchor=AnchorStatus.NEED,
        anchor_source=(
            "NEED — a published day-to-day shape correlation for a SPACE-HEATING "
            "load. This cell exists so that netting heat out of L1.2 cannot be a "
            "quiet exclusion: the number that was removed from the judged "
            "statistic is MEASURED and REPORTED here, on exactly the homes whose "
            "heat lands on the judged meter, and never given an invented "
            "threshold. What would anchor it: a metered panel of Economy-7 / "
            "electrically-heated dwellings with per-day half-hourly readings — "
            "SERL, or the LCL trial's raw partitioned archive. The repo's LCL "
            "extract (`data/lake/lcl_household_load_shapes_2013`) cannot: it "
            "holds each household's ANNUAL MEAN weekday and weekend shape, from "
            "which no day-to-day correlation can be recovered."
        ),
        observed_on_shipped=None,
        rationale=(
            "The removed quantity is stated, not dropped. A real thermostat "
            "repeats; how much it repeats is a question nobody here has an "
            "external answer to, so it is measured and left visible."
        ),
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
            "STILL NEED, and as of 2026-08-09 the reason is MEASURED rather than "
            "'no source exists'. An anchor WAS found and WAS applied — the Low "
            "Carbon London panel's per-home weekday-vs-weekend total-variation "
            "distance (304 real households, full year 2013: median 0.0724, P05 "
            "0.0279, bootstrap floor 0.0262; background/lcl_household_anchors.py "
            "still derives it) — and it was REMOVED again the same day because it "
            "cannot fail at this window length. THE MEASUREMENT: relabelling the "
            "day-type calendar at random, keeping the same 85/35 counts, is this "
            "cell's own named R15 mutation, and over 600 home-permutation samples "
            "on the drawn population NOT ONE value fell below the floor — null "
            "median 0.0715, null MINIMUM 0.0378, against a floor of 0.0262. The "
            "statistic is strongly biased upward at 120 days: with 35 weekend days "
            "against 85 weekday days, two arbitrary subsets of the SAME home differ "
            "by about as much as a real household's weekday differs from its "
            "weekend over a full year. A band that a day-type-randomised population "
            "clears with a 1.4x margin is fail-open, and a fail-open band is worse "
            "than an honest blank (R15). HALF OF WHAT THIS NEEDED IS NOW BUILT and "
            "sits beside it as L1.4n: each home is judged against its OWN "
            "permutation null, which answers whether the home has ANY real "
            "weekday/weekend structure and DOES fire on the randomised calendar "
            "this raw cell could not. THIS CELL STAYS UNANCHORED ANYWAY, because "
            "it asks the other question — whether that structure is as LARGE as a "
            "real household's — and the repo's LCL extract cannot answer it: it "
            "carries each household's ANNUAL MEAN weekday and weekend shape, so "
            "the panel's own null is not computable from it, and null-correcting "
            "the model's side alone would be this same window-mismatch error in "
            "new coordinates. WHAT WOULD CLOSE IT: a panel with PER-DAY half-hourly "
            "readings — SERL, or the LCL trial's raw partitioned archive — from "
            "which the same null correction can be computed on both sides. SERL "
            "remains the stratified source of record."
        ),
        observed_on_shipped=None,
        rationale=(
            "Present but identical for every home is the real defect — see L2.3. "
            "Reported for the record while unjudged: on the drawn n=200 population "
            "the model's per-home spread of this statistic (P90/P10 = 2.25) is about "
            "half the panel's (4.66) and its LOWEST home (0.072) sits at the panel's "
            "MEDIAN (0.072) — so the model's homes look MORE weekday/weekend-distinct "
            "and LESS varied in that distinction than real ones. Both readings are "
            "confounded by the same window bias, which is why neither is judged."
        ),
    ),
    "L1.4n_weekday_weekend_null_ratio": Band(
        statistic="L1.4n_weekday_weekend_null_ratio",
        level="L1",
        direction="at_least",
        threshold=1.0,
        anchor=AnchorStatus.STRUCTURAL,
        anchor_source=(
            "No external anchor needed and none is borrowed — the comparison is "
            "the home against ITSELF with the calendar/shape association destroyed "
            "(see the L1.4n note above the statistic). The threshold is 1.0 "
            "because the statistic is DEFINED as a ratio to the 95th percentile "
            "of that null, i.e. a one-sided permutation test at alpha = 0.05: the "
            "decision point is a property of the construction, not a number "
            "anyone picked, and there is nothing here to tune. THIS IS THE CELL "
            "L1.4 COULD NOT BE. The raw distance had a null of 0.0715 at this "
            "window and a floor of 0.0262 under it, so a day-type-randomised "
            "population passed; expressed against its own null the SAME "
            "population reads a median 0.75 and fails on 58 homes of 60."
        ),
        observed_on_shipped=None,
        rationale=(
            "A generator with no day-type mechanism at all scores at its own null "
            "whatever the window length — which is exactly what the raw cell could "
            "not say. What this cell does NOT claim is magnitude: a home can beat "
            "its own null with a weekday/weekend difference far smaller than a real "
            "household's, and that question stays open on L1.4."
        ),
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
        threshold=None,
        anchor=AnchorStatus.NEED,
        anchor_source=(
            "THE FLOOR CAME OUT 2026-08-10 (H34) AND THE NUMBER IS NOT COMING BACK "
            "AT ANY HEIGHT. It was 0.5 half-hours on domain knowledge — households "
            "do not all peak in the same half-hour, and the shipped defect is a "
            "single national constant, i.e. an exact point mass at 0.0. The domain "
            "claim is still true; the NUMBER was fail-open, and the H33 sweep "
            "measured it: `timing_diversity` is a SPREAD OF MEANS, so it carries "
            "the same sampling term as its own null, and a population whose days "
            "are dealt out at random — no home with a timing of its own — cleared "
            "0.5 in 65% of deals at 40 days, 57% at 60, 15% at 90 and 2% at 120 "
            "on the applied panel (docs/design/BAND_NULL_SWEEP.md). The band was "
            "INSIDE its own null at "
            "40/60/90d and cleared it at 120d by 3.8% of the null's spread, while "
            "the number in this table never moved. NO fixed floor is right at "
            "every window, so lowering or raising it is not the repair and neither "
            "is picking a kinder window (R12) — the STATISTIC was repaired, and "
            "sits beside this cell as L2.3n, where the same spread is scored "
            "against a re-deal of the population's own days. WHAT WOULD PUT A "
            "NUMBER BACK HERE: a panel of per-home half-hourly reads (SERL, or the "
            "LCL trial's raw archive) from which the panel's OWN null is computable "
            "at the same window — because this cell's remaining question is "
            "MAGNITUDE (is the diversity as wide as a real population's), and "
            "null-correcting the model's side alone would be the same "
            "window-mismatch error in new coordinates."
        ),
        observed_on_shipped=None,
        rationale=(
            "Reported for the record while unjudged: one national "
            "HEATING_PERIOD_WEIGHTS constant is an exact point mass at 0.0, which "
            "L2.3n scores 0.0 and fails. The number here is real and still moves "
            "with the generator — it is the FLOOR over it that no window supports."
        ),
    ),
    "L2.3n_timing_diversity_null_ratio": Band(
        statistic="L2.3n_timing_diversity_null_ratio",
        level="L2",
        direction="at_least",
        threshold=1.0,
        anchor=AnchorStatus.STRUCTURAL,
        anchor_source=(
            "No external anchor needed and none is borrowed — the comparison is "
            "the population against ITSELF with the home/timing association "
            "destroyed (see the L2.3n note above the statistic). The threshold is "
            "1.0 because the statistic is DEFINED as a ratio to the 95th "
            "percentile of that null, i.e. a one-sided permutation test at alpha = "
            "0.05: the decision point is a property of the construction, not a "
            "number anyone picked, and there is nothing here to tune. THE WINDOWS "
            "IT HOLDS AT, measured on the APPLIED panel as it stood that day "
            "(couple_fabric, 10 homes; widened to 15 by H35, which does not "
            "re-date this reading) — 40 independent re-deals per window, "
            "2026-08-10 — at 40 / 60 / 90 / "
            "120 days: a timing-less population passes this ratio 7% / 12% / 7% / "
            "2% — flat at its own alpha — where the floor it replaces passed the "
            "same deals 65% / 57% / 15% / 2%, i.e. fail-open in proportion to how "
            "SHORT the run was. The real panel reads 1.66 / 1.84 / 2.11 / 2.12 "
            "over those windows (8-home test panel: 1.35 / 1.47 / 1.67 / 2.07), so "
            "both directions hold across 40-120d and neither verdict turns on how "
            "long anyone watched."
        ),
        observed_on_shipped=None,
        rationale=(
            "A generator with no per-home clock scores at its own null whatever "
            "the window length — which is exactly what the raw cell could not say. "
            "What this cell does NOT claim is magnitude: a population can beat its "
            "own null with a timing spread far narrower than a real one's, and "
            "that question stays open on L2.3."
        ),
    ),
    "L2.4_scale_spread_p90_p10": Band(
        statistic="L2.4_scale_spread_p90_p10",
        level="L2",
        direction="at_least",
        threshold=lcl_anchors.LCL_SCALE_SPREAD_P90_P10_FLOOR,
        anchor=AnchorStatus.PUBLISHED,
        anchor_source=(
            "ANCHORED 2026-08-09 on the Low Carbon London panel (304 real households, "
            "2013, CC-BY — background/lcl_household_anchors.py). Point estimate "
            "P90/P10 = 5.3769 (IQR ratio 2.4566); the threshold is the bootstrap P05 "
            "of that ratio, i.e. the low end of what the panel's own sampling error "
            "admits. The DESNZ NEED (EPC-linked metered annual consumption stratified "
            "by property type and floor-area band) is NOT retired: this panel says "
            "whether the spread is the right SIZE, never whether it is wrong in the "
            "right PLACES, and a stratified source should replace it."
        ),
        observed_on_shipped=None,
        rationale=(
            "Real UK homes span several-fold in annual kWh across the stock. Not "
            "knife-edge: the drawn n=200 population reads 1.80 against 4.88, so every "
            "tolerance the anchor rule admits lands on the same verdict."
        ),
    ),
}


# ---------------------------------------------------------------------------
# THE HEATING REGISTER — which meter each machine's heat lands on
# ---------------------------------------------------------------------------
#
# A REGISTER fact, never a reading of the trace: `main_heating_fuel` is what a real
# supplier holds, and inferring "this home looks like it has a heat pump" from the
# very smoothness the band is judging is the tautology R15 names first.
#
# WHAT THIS REGISTER IS FOR, SINCE H36. It used to map a machine to its OWN texture
# band, via a published seasonal efficiency per regime. That is gone: L1.1 is read
# net of space heat, so once a generator supplies the split, the machine is out of
# the denominator and the band that judges the home is the same one in every regime
# — no efficiency figure required, and a machine this file has never heard of is
# judged like any other. What is left is a PLUMBING fact with exactly one job: when
# a generator supplies NO split, decide whether the meter in front of us is already
# behavioural (heat elsewhere: judge it) or has a thermostat hiding in it that
# cannot be taken out (heat here: count it, do not guess).
#
# The keys are the string VALUES of `simulation.household.HeatingSystem`, written
# out rather than imported: the harness must not depend on the generator it judges.
# `tests/harness/test_premise_two_level.py::test_EVERY_heating_system_is_registered`
# is the class guard that fails when a new member appears in that enum with no entry
# here — which is the R10 half of this design. A member may legitimately be either
# side; what it may not do is fall through unclassified.
NON_ELECTRIC_TEXTURE_BAND = "L1.1_half_hourly_texture"
NO_BEHAVIOURAL_STREAM_BAND = "L1.1u_half_hourly_texture_no_behavioural_stream"

HEAT_ON_THE_JUDGED_METER: dict[str, bool] = {
    # The electricity meter carries no heat at all, so it IS the behavioural
    # stream and needs no split. District heat and no-heating are here for the
    # same reason as gas: whatever the heat costs, it is not on this meter.
    "gas_boiler_combi": False,
    "gas_boiler_system": False,
    "district_heat": False,
    "none": False,
    # The meter carries the heat. WHICH machine no longer matters — a ground-source
    # heat pump needed its own published SPF under the rescaled-floor design and
    # needs nothing at all under this one, because the split takes the machine out
    # whatever its efficiency is.
    "heat_pump_air": True,
    "heat_pump_ground": True,
    "electric_storage": True,
    "electric_direct": True,
}

# How much of a population may go unjudged before the L1.1 cell stops being
# evidence. Not a fidelity band — a coverage floor on the CONTROL, of the same
# family as `REQUIRED_RATE_RESOLUTION`. A population control that reports a clean
# rate while most of its homes were never judged is the vacuity failure this
# codebase has already been bitten by.
MAX_UNJUDGED_SHARE = 0.10


def texture_band_for(heating_system: str | None, *, has_split: bool = False) -> Band:
    """The L1.1 band that judges a home, given its register fact and whether its
    generator supplied a space-heat split.

    WITH A SPLIT there is nothing to decide: the machine comes out of the
    denominator and every home is judged by the one behavioural floor. The
    register is not consulted at all, which is the H36 result stated as code — a
    band keyed on the machine was a band compensating for the wrong load set.

    WITHOUT ONE, the register is the only thing that can say whether this meter is
    already behavioural. FAIL-CLOSED on ABSENCE, VISIBLE on the UNKNOWN, and the
    two are deliberately different. `None`/empty means the caller asserted
    nothing, which reads as the default UK home and gets JUDGED — a builder who
    forgets the register fact makes an electrically-heated home fail, never pass.
    A machine the register says is on this meter, with no split to take it out,
    cannot be judged on the load set the floor is about, so it is counted rather
    than guessed at. A NAMED machine absent from `HEAT_ON_THE_JUDGED_METER` is a
    hole in this register, and the fail-closed reading of a hole is the same as
    for a heated meter: counted, never quietly judged as if it were gas.
    """
    if has_split:
        return BANDS[NON_ELECTRIC_TEXTURE_BAND]
    if not heating_system:
        return BANDS[NON_ELECTRIC_TEXTURE_BAND]
    if HEAT_ON_THE_JUDGED_METER.get(str(heating_system), True):
        return BANDS[NO_BEHAVIOURAL_STREAM_BAND]
    return BANDS[NON_ELECTRIC_TEXTURE_BAND]


# ---------------------------------------------------------------------------
# RATE BANDS — what share of a population may sit outside its own L1 band
# ---------------------------------------------------------------------------
#
# Read the per-home anchors above before reading these. Every judged L1 band was
# deliberately placed OUTSIDE the plausible real range ("below the low end of the
# 20-40% domain expectation", "well above any plausible real value", "an order of
# magnitude clear of BOTH measured values"). A band placed beyond the support of the
# real distribution should be violated by NO home, at any n — which is why these
# thresholds are 0.0 and why that is not a smuggled-in worst-of-N.
#
# The distinction that matters: the FAIL direction has no n-dependence at all (one
# violating home is evidence of a mechanism, however large the sample), while the
# PASS direction now requires enough homes to have had the power to see one. That
# asymmetry is the fix.
#
# If a real subpopulation is ever found sitting outside one of these bands, the
# correct response is R4 — diagnose the mechanism — and NOT a rate threshold moved
# up to accommodate it. That is exactly what happened to the storage-heater home
# that first breached L1.1: the band was re-derived from the machine's physics, the
# tolerance was not widened.
@dataclass(frozen=True)
class RateBand:
    """A population-level tolerance on the share of homes outside their own band."""

    statistic: str
    threshold: float | None   # None = AnchorStatus.NEED, measured and not judged
    anchor: AnchorStatus
    anchor_source: str


_IMPOSSIBILITY_BOUND = (
    "structural, and it inherits the per-home anchor rather than adding one: the "
    "per-home band sits outside the plausible real range by construction, so the "
    "share of real homes beyond it is zero. A breach is a mechanism to diagnose "
    "(R4), never a tolerance to raise (R12)."
)

RATE_BANDS: dict[str, RateBand] = {
    "L1.1_half_hourly_texture": RateBand(
        "L1.1_half_hourly_texture", 0.0, AnchorStatus.STRUCTURAL, _IMPOSSIBILITY_BOUND
    ),
    "L1.1n_half_hourly_texture_null_ratio": RateBand(
        "L1.1n_half_hourly_texture_null_ratio", 0.0, AnchorStatus.STRUCTURAL,
        _IMPOSSIBILITY_BOUND + " AND IT IS THE IMPOSSIBILITY BOUND HERE, WHERE "
        "L1.4n's sibling rate is NOT — the difference is the null. L1.4n's is 99 "
        "random relabellings, so its 1.0 is a 95th percentile and a correct "
        "generator still puts weak-but-real homes under it 1 time in 20; its "
        "tolerance had to be 0.50 for that reason. L1.1n's flat counterfactual is "
        "DETERMINISTIC and idempotent, so a structureless home reads exactly 1.0 "
        "and there is no sampling under which a home with any behaviour at all "
        "falls below it. A home that does is a home whose meter is no rougher "
        "than its own mean profile, which no real household is — so the tolerated "
        "rate is zero and a breach is a mechanism to diagnose (R4), never a "
        "tolerance to raise (R12).",
    ),
    "L1.2_day_to_day_shape_correlation": RateBand(
        "L1.2_day_to_day_shape_correlation", 0.0, AnchorStatus.STRUCTURAL,
        _IMPOSSIBILITY_BOUND,
    ),
    "L1.3_away_days_per_year": RateBand(
        "L1.3_away_days_per_year", 0.0, AnchorStatus.STRUCTURAL,
        _IMPOSSIBILITY_BOUND + " Here the per-home band is representability — a home "
        "that is never once in a year quieter by day than it is at 3am cannot "
        "represent an empty house AT ALL — so the population tolerance for homes "
        "that cannot is zero. The RATE of away days per home remains unanchored "
        "(ONS/BEIS holiday-taking) and is reported, not judged.",
    ),
    "L1.4_weekday_weekend_separation": RateBand(
        "L1.4_weekday_weekend_separation", None, AnchorStatus.NEED,
        "The per-home band is itself unanchored, so there is nothing to count "
        "violations of. It briefly was not, on 2026-08-09 — see the L1.4 entry in "
        "BANDS for the measurement that took the anchor back out, and for the "
        "tolerated rate (10%) that goes back in with it when the statistic is "
        "null-corrected.",
    ),
    "L1.4n_weekday_weekend_null_ratio": RateBand(
        "L1.4n_weekday_weekend_null_ratio", 0.50, AnchorStatus.STRUCTURAL,
        "NOT the impossibility bound the other structural rates use, and the "
        "difference is the point: L1.4n's per-home band is a SIGNIFICANCE test at "
        "alpha = 0.05, so a clean sheet is not expected even from a perfect "
        "generator — a home with genuine but weak day-type structure lands under "
        "its own null by chance, and the rate at which it does is a POWER "
        "question that shrinks with the window. A zero tolerance would therefore "
        "fail a correct generator for being watched for 60 days instead of 120. "
        "THE RULE WAS FIXED BEFORE THE NUMBER (R12): the tolerance must sit in "
        "the empty gap between a population that HAS day-type structure and one "
        "that does not, and must give the same verdict on every population and "
        "every window measured. BOTH ENDS ARE MEASURED ON BOTH POPULATIONS, and "
        "they are reported separately because they are not the same number — "
        "quoting one population's rate as the other's is how one name comes to "
        "carry two numbers. Real calendar vs day-type-randomised, at 60 / 90 / "
        "120 days: n=60 fixture 0.183 / 0.067 / 0.017 against 0.900 / 0.950 / "
        "0.967; n=200 drawn 0.295 / 0.180 / 0.120 against 0.945 / 0.860 / 0.965. "
        "The TIGHTEST pair across all twelve readings is (0.295, 0.860), and 0.50 "
        "is its geometric midpoint — so the band sits ~1.7x from both ends in "
        "ratio terms, and every threshold in [0.30, 0.86] lands on the same "
        "verdict everywhere measured. The rate RISES with n and FALLS with the "
        "window, both expected: more homes means more genuinely weak ones, and "
        "fewer days means less power to detect the structure a home does have.",
    ),
    "L1.5_max_multiplicity_share": RateBand(
        "L1.5_max_multiplicity_share", 0.0, AnchorStatus.STRUCTURAL,
        _IMPOSSIBILITY_BOUND + " L1.5 is a mechanism detector rather than a "
        "statistic: a generator that rescales a fixed base shape does it for EVERY "
        "home, so there is no tail argument available and no reason any real home "
        "should breach it.",
    ),
}


# The R12 goal-seek pair, named once so a rename cannot silently desync the
# warning from the bands (it did exactly that once — see `goal_seek_warning`).
TEXTURE_STATISTIC = "L1.1_half_hourly_texture"
STRUCTURAL_STATISTIC = "L1.5_max_multiplicity_share"

# The companion band that asks the same cell's SIGNIFICANCE question (H39). Named
# once, for the same reason the two above are: the cell, the sweep's exclusion
# list and the tests all reach it through this constant, so a rename cannot leave
# one of them judging a band that no longer exists.
TEXTURE_NULL_RATIO_STATISTIC = "L1.1n_half_hourly_texture_null_ratio"

# How widespread the structural artefact must be before an L1.1-pass-with-L1.5-fail
# reads as TUNING rather than as one home to diagnose. A rescaled base shape is a
# property of the GENERATOR, so the artefact it leaves is in every home it makes;
# half the population is a deliberately loose floor on "every".
GOAL_SEEK_STRUCTURAL_PREVALENCE = 0.5


@dataclass(frozen=True)
class CellResult:
    statistic: str
    level: str
    value: float
    verdict: Verdict
    band: Band
    note: str = ""
    # POPULATION FIELDS, present on L1 cells only. `value` is the VIOLATION RATE
    # for a judged L1 cell — the thing the verdict is about — so the number and the
    # verdict cannot drift apart. The worst home is carried alongside as a
    # diagnostic, never as the judged quantity.
    homes_judged: int | None = None
    homes_violating: int | None = None
    homes_unjudged: int | None = None
    resolution: float | None = None      # rule of three, 3/n
    worst_value: float | None = None
    worst_home: str | None = None
    rate_band: "RateBand | None" = None


@dataclass(frozen=True)
class TwoLevelResult:
    """The suite's verdict.

    L1 cells are POPULATION VIOLATION RATES against per-home bands (see the scale
    invariance note at the top of this module); L2 cells are population statistics
    in their own right. Neither is an average over homes — an average would hide
    the exact clone-cluster the suite exists to find, and a worst-of-N would make
    the verdict a function of how many homes were looked at.
    """

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
    def inconclusive(self) -> tuple[CellResult, ...]:
        """Cells that COULD have been judged and were not, for want of homes or
        for want of a register fact. Distinct from `unvalidated`, where there is no
        band to judge against in the first place."""
        return tuple(c for c in self.cells if c.verdict is Verdict.INSUFFICIENT)

    @property
    def is_red(self) -> bool:
        """An unavailable check is a FAILED check (R15), so an inconclusive cell
        reds the suite. Read `failed` for the cells that actually breached a band —
        the two are reported separately precisely so 'we did not look at enough
        homes' can never be read as 'the generator is broken', or vice versa."""
        return bool(self.failed) or bool(self.inconclusive)

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
        if texture.verdict is not Verdict.PASS or structural.verdict is not Verdict.FAIL:
            return None
        # THE PREMISE NEEDS A PREVALENCE, and it did not have one until the cells
        # became rates. Tuning is a statement about the GENERATOR: level noise
        # sprinkled onto a rescaled base shape leaves the artefact in EVERY home,
        # because the base shape is the generator's, not the home's. One home in
        # sixty breaching L1.5 while the texture band holds is a single home to
        # diagnose (R4), not evidence that someone moved a number — and reading it
        # as tuning was this warning's first false positive, on the first
        # population-scale run (2026-08-09, n=60, 1/60).
        if structural.value is not None and structural.rate_band is not None:
            if structural.value < GOAL_SEEK_STRUCTURAL_PREVALENCE:
                return None
        return (
            "SOMEONE TUNED THE NUMBER: L1.1 texture passes while L1.5 repeat-rate "
            "fails. Level noise has been injected onto a rescaled base shape — the "
            "symptom moved and the mechanism did not."
        )

    def summary(self) -> str:
        lines = [f"two-level test — generator={self.generator} homes={self.homes} days={self.days}"]
        for c in self.cells:
            if c.homes_judged is not None and c.rate_band is not None:
                # An L1 rate cell. n and the resolution are printed on the SAME line
                # as the verdict, because the whole defect this form exists to fix
                # was a verdict whose report did not say how many homes produced it.
                parts = [f"rate {c.value:.4g}"]
                if c.rate_band.threshold is None:
                    parts.append("NEED tolerance")
                else:
                    parts.append(f"tolerance {c.rate_band.threshold:g}")
                if c.resolution is not None:
                    parts.append(f"resolution {c.resolution:.3g}")
                if c.homes_unjudged:
                    parts.append(f"{c.homes_unjudged} unjudged")
                lines.append(
                    f"  [{c.verdict.value.upper():>18}] {c.statistic}: "
                    f"{c.homes_violating}/{c.homes_judged} homes outside band "
                    f"({', '.join(parts)})"
                    + (f"  — {c.note}" if c.note else "")
                )
                continue
            lines.append(
                f"  [{c.verdict.value.upper():>18}] {c.statistic} = {c.value:.4g}"
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
    # WHICH MACHINE HEATS EACH HOME, for the regime-conditioned L1.1 band. The
    # string values of `simulation.household.HeatingSystem` — a REGISTER fact (what
    # a real supplier holds as `main_heating_fuel`), never inferred from the trace:
    # inferring "this home looks like it has a heat pump" from the very smoothness
    # the band is judging would be the tautology R15 names first.
    #
    # WHAT IT IS STILL FOR. It replaced a BOOLEAN (`electrically_heated`) on
    # 2026-08-09 and then stopped choosing a threshold at all on 2026-08-10 (H36):
    # L1.1 is read net of space heat, so where a split is supplied the machine is
    # out of the denominator and every home meets the same floor. This field now
    # decides ONE thing — whether a home whose generator supplied no split has a
    # meter that is already behavioural, or a thermostat in it that cannot be
    # taken out. See `HEAT_ON_THE_JUDGED_METER`.
    #
    # FAIL-CLOSED when empty: an empty tuple means every home is judged on its
    # whole meter against the behavioural floor, so a builder that forgets to
    # supply it makes an electrically-heated home fail, never pass. The lenient
    # direction requires someone to assert the fact.
    heating_systems: tuple[str, ...] = ()
    # THE PART OF THE JUDGED METER DRAWN BY THE SPACE-HEATING MACHINE, per home,
    # for the cells that must compare the same load set across regimes
    # (`meter_net_of_machines`). Zeros — not absence — where a home's heat is on
    # the OTHER commodity: that is a stated fact ("no heat on this meter"), which
    # is different from a generator that cannot say.
    #
    # FAIL-CLOSED when empty: a generator that supplies no split has its WHOLE
    # meter judged by L1.2, which is the strict reading and the one that keeps the
    # shipped path red. The lenient direction has to be bought with a fact, and
    # `meter_net_of_machines` checks the fact it is given.
    space_heat_grids: tuple[tuple[tuple[float, ...], ...], ...] = ()
    # THE SAME, FOR THE WATER-HEATING MACHINE (H38, 2026-08-10). Carried as its
    # OWN field rather than added into `space_heat_grids` because they are two
    # facts about a home and a caller must be able to supply one without
    # asserting the other — and because a summed field could not tell "this home
    # heats its water on the other meter" (zeros) from "this generator cannot say"
    # (absence), which is the distinction the netting fails closed on.
    #
    # FAIL-CLOSED when empty, and it fails closed HARDER than the space-heat
    # field alone did: `machine_draw` returns None if EITHER stream is missing, so
    # a builder that supplies space heat and forgets water heat judges the whole
    # meter rather than netting the half it has.
    water_heat_grids: tuple[tuple[tuple[float, ...], ...], ...] = ()

    def __post_init__(self) -> None:
        if len(self.homes) != len(self.grids):
            raise InsufficientEvidence("home ids and grids must align")
        if len(self.homes) != len(self.annual_kwh):
            raise InsufficientEvidence("home ids and annual totals must align")
        if self.heating_systems and len(self.heating_systems) != len(self.homes):
            raise InsufficientEvidence(
                "the heating-system register facts must align with the home ids"
            )
        for g in self.grids:
            if len(g) != len(self.is_weekend):
                raise InsufficientEvidence("every home's grid must span the day-type calendar")
        if self.weather_driver and len(self.weather_driver) != len(self.is_weekend):
            raise InsufficientEvidence("the weather driver must span the day-type calendar")
        if self.space_heat_grids:
            if len(self.space_heat_grids) != len(self.homes):
                raise InsufficientEvidence(
                    "the space-heat streams must align with the home ids"
                )
            for g in self.space_heat_grids:
                if len(g) != len(self.is_weekend):
                    raise InsufficientEvidence(
                        "every space-heat stream must span the day-type calendar"
                    )
        if self.water_heat_grids:
            if len(self.water_heat_grids) != len(self.homes):
                raise InsufficientEvidence(
                    "the water-heat streams must align with the home ids"
                )
            for g in self.water_heat_grids:
                if len(g) != len(self.is_weekend):
                    raise InsufficientEvidence(
                        "every water-heat stream must span the day-type calendar"
                    )

    @property
    def days(self) -> int:
        return len(self.is_weekend)


def _null_ratio_or_zero(
    days: Sequence[Sequence[float]], is_weekend: Sequence[bool]
) -> float:
    """L1.4n for one home, with the degenerate case decided HERE rather than
    buried in the statistic.

    A home whose permutation null is degenerate has identical days: its real
    separation is zero AND every relabelling's is too. It is scored 0.0 — a
    definitive violation — and NOT skipped. Both alternatives are worse. Skipping
    it is fail-open, and it is the exact fail-open this suite is built to catch:
    a 7-day-rolling-mean smoothing of a real home is one of the spec's own named
    mutations, and a smoothed home lands here. Raising would let one flat home
    abort the whole population's cell.
    """
    try:
        return weekday_weekend_separation_vs_own_null(days, is_weekend).ratio
    except DegenerateNull:
        return 0.0


def _texture_ratio_or_zero(days: Sequence[Sequence[float]]) -> float:
    """L1.1n for one home, with the degenerate case decided HERE rather than
    buried in the statistic.

    A home whose flat counterfactual has no half-hourly movement has a mean
    diurnal profile that is a CONSTANT — the same value in all 48 periods. Its
    real texture may be anything; the point is that it has no null. It is scored
    0.0, a definitive violation, and NOT skipped, for the reason the two sibling
    helpers give: a flat-profile home is what a rescaled national base shape looks
    like once the rescaling is per-day, so skipping it would be fail-open on
    exactly the generator this cell is written for. Raising would let one such
    home abort the whole population's cell.

    The days are already netted of the heating machines by the caller, which is
    why nothing is passed for `machines` here: netting twice would subtract the
    machine from a stream it is no longer in.
    """
    try:
        return half_hourly_texture_vs_own_null(days).ratio
    except DegenerateNull:
        return 0.0


def _timing_ratio_or_zero(grids: Sequence[Sequence[Sequence[float]]]) -> float:
    """L2.3n for one population, with the degenerate case decided HERE rather than
    buried in the statistic.

    A population whose re-deal null is degenerate is one where every day in every
    home peaks in the same half-hour: its real spread is zero AND every re-deal's
    is too. That is not an edge case to skip — it is the shipped defect this cell
    exists to fail (one national `HEATING_PERIOD_WEIGHTS` constant), so it is
    scored 0.0, a definitive violation. Skipping it would be fail-open on the
    exact population the band was written for; raising would let the L2 level go
    unreported instead of red, and an unavailable check is a failed check (R15).
    """
    try:
        return timing_diversity_vs_own_null(grids).ratio
    except DegenerateNull:
        return 0.0


def _l1_rate_cell(
    statistic: str,
    *,
    values: Sequence[float],
    bands: Sequence[Band],
    homes: Sequence[str],
    note: str = "",
) -> CellResult:
    """Judge every home against its OWN band and report the population VIOLATION
    RATE, with n and the resolution that n bought.

    The asymmetry is the whole design (see the scale-invariance note at the top of
    this module):

    * ANY violation FAILS, at any n. One home outside an impossibility bound is
      evidence of a mechanism, and waiting for a bigger sample to say so would be
      the fail-open direction.
    * A CLEAN sheet only PASSES when the sample could have detected a violation
      rate of `REQUIRED_RATE_RESOLUTION`. Zero-in-ten rules out nothing worth
      ruling out, so it is INSUFFICIENT, not a pass.
    * Homes with no band to be judged by are COUNTED, and if too many of them
      accumulate the cell is INSUFFICIENT rather than quietly clean.
    """
    if len(values) != len(bands) or len(values) != len(homes):
        raise InsufficientEvidence(f"{statistic}: values, bands and homes must align")
    if not values:
        raise InsufficientEvidence(f"{statistic}: no homes to judge")

    rate_band = RATE_BANDS[statistic]
    judged: list[int] = []
    unjudged: list[int] = []
    violating: list[int] = []
    for k, (v, b) in enumerate(zip(values, bands)):
        if b.threshold is None or b.anchor is AnchorStatus.NEED:
            unjudged.append(k)
            continue
        judged.append(k)
        if b.judge(v) is not Verdict.PASS:
            violating.append(k)

    # The worst home is a DIAGNOSTIC and is reported whatever the verdict — worst
    # by MARGIN against its own band, because with several thresholds live the
    # lowest raw number is not necessarily the home in most trouble.
    def _margin(k: int) -> float:
        b = bands[k]
        if b.threshold is None or b.threshold == 0.0:
            return math.inf
        m = values[k] / b.threshold
        return m if b.direction == "at_least" else -m

    worst_k = min(range(len(values)), key=_margin)

    unjudged_share = len(unjudged) / len(values)
    detail = (
        f"worst home {homes[worst_k]} = {values[worst_k]:.4g} judged by "
        f"{bands[worst_k].statistic}"
    )
    if violating:
        detail += "; outside band: " + ", ".join(
            f"{homes[k]}={values[k]:.4g} vs {bands[k].statistic} "
            f"{bands[k].direction} {bands[k].threshold:.4g}"
            for k in violating[:5]
        )
        if len(violating) > 5:
            detail += f" (+{len(violating) - 5} more)"
    if note:
        detail = f"{detail}; {note}"

    if rate_band.threshold is None:
        # NO ANCHOR EXISTS for this statistic, so there is nothing to count
        # violations of and no rate to report. Reported in the plain measured form
        # — the worst home's value — exactly as before, because "unvalidated" and
        # "we did not look at enough homes" are different states and this file has
        # room for both.
        return CellResult(
            statistic, "L1", values[worst_k], Verdict.UNVALIDATED, bands[worst_k],
            note=detail + " — measured, not judged",
            worst_value=values[worst_k], worst_home=homes[worst_k],
        )

    if not judged:
        return CellResult(
            statistic, "L1", float("nan"), Verdict.INSUFFICIENT, bands[worst_k],
            note=detail + "; NO home carried a judgeable band — the register is the hole",
            homes_judged=0, homes_violating=0, homes_unjudged=len(unjudged),
            resolution=None, worst_value=values[worst_k], worst_home=homes[worst_k],
            rate_band=rate_band,
        )

    rate = len(violating) / len(judged)
    resolution = detectable_violation_rate(len(judged))

    if rate > rate_band.threshold:
        verdict = Verdict.FAIL
    elif unjudged_share > MAX_UNJUDGED_SHARE:
        verdict = Verdict.INSUFFICIENT
        detail += (
            f"; {unjudged_share:.1%} of the population had no registered band, "
            f"above the {MAX_UNJUDGED_SHARE:.0%} coverage floor"
        )
    elif resolution > REQUIRED_RATE_RESOLUTION:
        verdict = Verdict.INSUFFICIENT
        detail += (
            f"; {len(judged)} judged homes rule out only a {resolution:.1%} violation "
            f"rate, and this suite claims to see {REQUIRED_RATE_RESOLUTION:.0%} "
            f"(needs {MIN_HOMES_FOR_L1_RATE})"
        )
    else:
        verdict = Verdict.PASS

    return CellResult(
        statistic, "L1", rate, verdict, bands[worst_k], note=detail,
        homes_judged=len(judged), homes_violating=len(violating),
        homes_unjudged=len(unjudged), resolution=resolution,
        worst_value=values[worst_k], worst_home=homes[worst_k], rate_band=rate_band,
    )


def evaluate_two_level(population: PopulationTraces) -> TwoLevelResult:
    """Run every statistic over a population and return the two-level verdict.

    Level 1 statistics are computed PER HOME, judged against that home's own band,
    and reported as the population's VIOLATION RATE with the n behind it. Neither
    an average (which would hide a clone cluster inside an otherwise-diverse
    population) nor a worst-of-N (which would make the verdict a function of how
    many homes were looked at).
    """
    _require_homes(population.grids, minimum=MIN_HOMES_FOR_DIVERSITY, name="evaluate_two_level")
    grids = [[list(day) for day in home] for home in population.grids]
    homes = tuple(population.homes)
    cells: list[CellResult] = []

    # --- L1 ---------------------------------------------------------------
    # THE SAME LOAD SET FOR EVERY L1 CELL, computed ONCE and passed down. L1.1,
    # L1.2 and L1.3 are all statements about a household's behaviour, and all three
    # are read on the meter net of the heating machines: two cells deriving "this
    # home's behaviour" separately is how they come to hold two ideas of it.
    #
    # BOTH MACHINES SINCE H38, and the invariant above is why the water heater was
    # netted from all three rather than from L1.1 alone. L1.1 is the cell with the
    # argument that forced it (the water heater is 36-40% of the denominator, and
    # the floor's anchor population heats its water with gas), but keeping it in
    # for the other two would have bought exactly the two-ideas-of-behaviour defect
    # this comment forbids. The other two were MEASURED rather than assumed, on the
    # drawn 60: L1.3 loses 8 false away days and holds recall at 1.000 (the water
    # heater draws nothing on an away day, so the netting is the identity on the
    # days that cell is about); L1.2 moves its median 0.2104 -> 0.2143 with the
    # worst home and the violation count both unchanged. Neither is the reason —
    # they are the check that the reason costs nothing elsewhere.
    heat_streams: list[list[list[float]] | None] = [
        machine_draw(
            [list(day) for day in population.space_heat_grids[k]]
            if population.space_heat_grids else None,
            [list(day) for day in population.water_heat_grids[k]]
            if population.water_heat_grids else None,
        )
        for k in range(len(grids))
    ]
    behavioural = [meter_net_of_machines(g, h) for g, h in zip(grids, heat_streams)]
    netted = sum(
        1 for h in heat_streams if h is not None and any(any(day) for day in h)
    )
    # A SPLIT IS BOTH MACHINES OR IT IS NOT A SPLIT (H38). `machine_draw` already
    # fails closed per home; this is the same fact for the notes, so a population
    # carrying only half the split says "no split" rather than reporting a netting
    # it did not do.
    split_supplied = all(h is not None for h in heat_streams)

    # L1.1's band was keyed on the MACHINE for as long as the statistic was read on
    # the whole meter, because the heat sat in the denominator of a ratio to the
    # home's own mean. Read net of space heat there is one floor for every home
    # size (H36), and the register only decides the ONE case netting cannot reach:
    # a home whose heat is on this meter and whose generator supplied no split.
    registers = population.heating_systems or ("",) * len(homes)
    texture_bands = tuple(
        texture_band_for(r, has_split=h is not None)
        for r, h in zip(registers, heat_streams)
    )
    unjudged_for_no_split = sum(
        1 for b in texture_bands if b.statistic == NO_BEHAVIOURAL_STREAM_BAND
    )
    cells.append(_l1_rate_cell(
        TEXTURE_STATISTIC,
        values=[half_hourly_texture(b) for b in behavioural],
        bands=texture_bands,
        homes=homes,
        note=(
            f"judged on the meter net of space AND water heat; {netted} of {len(grids)} "
            f"homes carry a heating machine on the judged meter; "
            f"{unjudged_for_no_split} unjudged for want of a split"
            if split_supplied
            else "no machine split supplied — the WHOLE meter is judged where the "
            f"register says the heat is elsewhere, and {unjudged_for_no_split} of "
            f"{len(grids)} homes are counted rather than judged"
        ),
    ))

    # L1.1n — THE SAME TEXTURE, beside each home's own flat counterfactual (H39).
    # A SEPARATE cell rather than a replacement for the floor above, for the reason
    # L1.4/L1.4n are already separate: the floor asks a MAGNITUDE question with a
    # domain anchor behind it, this asks whether ANY of the texture is behaviour
    # rather than the home's own diurnal shape, and collapsing the two into one
    # name would be one name carrying two numbers. It is read on the SAME
    # `behavioural` stream the floor is read on — computed once, above — so the two
    # cannot come to hold two ideas of what this home's behaviour is.
    #
    # ONE BAND FOR EVERY HOME, with no register lookup: the ratio's decision point
    # is a property of the construction rather than of the load set, so unlike the
    # floor it has nothing for a heating regime to condition. A home with no
    # recoverable behavioural stream is already counted, not judged, by the floor's
    # own `L1.1u` routing; here it is judged on the whole meter it presents,
    # because a home whose meter is no rougher than its own mean profile is a
    # finding whatever is in the meter.
    cells.append(_l1_rate_cell(
        TEXTURE_NULL_RATIO_STATISTIC,
        values=[_texture_ratio_or_zero(b) for b in behavioural],
        bands=(BANDS[TEXTURE_NULL_RATIO_STATISTIC],) * len(grids),
        homes=homes,
        note=(
            "read on the same load set as the floor above; a home whose flat "
            "counterfactual has no texture at all is scored 0.0 (a violation), "
            "never skipped"
        ),
    ))

    # L1.2 is judged on the SAME LOAD SET for every home. Its band is a statement
    # about households; where the heating machine is on the judged meter it is
    # taken back out, so the cell cannot fail a home for owning a thermostat
    # (`meter_net_of_machines` carries the measurement that forced this).
    cells.append(_l1_rate_cell(
        "L1.2_day_to_day_shape_correlation",
        values=[day_to_day_shape_correlation(g) for g in behavioural],
        bands=(BANDS["L1.2_day_to_day_shape_correlation"],) * len(grids),
        homes=homes,
        note=(
            f"judged on the meter net of space AND water heat; {netted} of {len(grids)} "
            "homes carry a heating machine on the judged meter"
            if split_supplied
            else "no machine split supplied — the WHOLE meter is judged (fail-closed)"
        ),
    ))
    # THE QUANTITY THAT WAS NETTED OUT, said out loud. Measured on the homes whose
    # heat is actually on the judged meter, never judged, so the exclusion above
    # cannot be a quiet one. A cell nobody can see is how an exclusion becomes a
    # fail-open.
    heat_measured = [
        (homes[k], day_to_day_shape_correlation(h))
        for k, h in enumerate(heat_streams)
        if h is not None and any(any(day) for day in h)
    ]
    heat_band = BANDS["L1.2h_heating_shape_repeatability"]
    worst_heat = max(heat_measured, key=lambda hv: hv[1], default=None)
    cells.append(CellResult(
        heat_band.statistic, "L1",
        worst_heat[1] if worst_heat else float("nan"),
        Verdict.UNVALIDATED, heat_band,
        note=(
            f"worst of {len(heat_measured)} homes whose heat is on the judged "
            f"meter, median {statistics.median(v for _, v in heat_measured):.4g} "
            "— measured, not judged"
            if heat_measured
            else "no home in this population carries space heat on the judged meter"
        ),
        homes_judged=0, homes_violating=0, homes_unjudged=len(heat_measured),
        resolution=None,
        worst_value=worst_heat[1] if worst_heat else None,
        worst_home=worst_heat[0] if worst_heat else None,
    ))

    # L1.3 is judged on the SAME load set as L1.2, and for a sharper reason: its
    # statistic divides by the base-load window, which a heat pump occupies. The
    # netting is passed in rather than re-derived so the two cells cannot come to
    # hold two ideas of what this home's behaviour is (H37).
    cells.append(_l1_rate_cell(
        "L1.3_away_days_per_year",
        values=[
            trough_statistics(g, machines=h).away_days_per_year
            for g, h in zip(grids, heat_streams)
        ],
        bands=(BANDS["L1.3_away_days_per_year"],) * len(grids),
        homes=homes,
        note=(
            f"away signature read net of space AND water heat; {netted} of {len(grids)} "
            "homes carry a heating machine on the judged meter"
            if split_supplied
            else "no machine split supplied — the WHOLE meter is judged (fail-closed)"
        ),
    ))

    for statistic, fn in (
        ("L1.4_weekday_weekend_separation",
         lambda g: weekday_weekend_separation(g, population.is_weekend)),
        # The same distance, judged against each home's own permutation null.
        # Reported as a SEPARATE cell rather than replacing L1.4, because the two
        # answer different questions (structure vs magnitude) and collapsing them
        # into one name would be one name carrying two numbers.
        ("L1.4n_weekday_weekend_null_ratio",
         lambda g: _null_ratio_or_zero(g, population.is_weekend)),
        ("L1.5_max_multiplicity_share",
         lambda g: normalised_fraction_multiplicity(g).max_multiplicity_share),
    ):
        band = BANDS[statistic]
        cells.append(_l1_rate_cell(
            statistic,
            values=[fn(g) for g in grids],
            bands=(band,) * len(grids),
            homes=homes,
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
                            note="population sd of each home's mean evening-peak period "
                                 "— measured, not judged; L2.3n judges it"))

    # The same spread against a re-deal of this population's own days. Reported as
    # a SEPARATE cell rather than replacing L2.3, because the two answer different
    # questions (structure vs magnitude) and collapsing them into one name would be
    # one name carrying two numbers.
    band = BANDS["L2.3n_timing_diversity_null_ratio"]
    value = _timing_ratio_or_zero(grids)
    cells.append(CellResult(band.statistic, "L2", value, band.judge(value), band,
                            note="timing diversity over the p95 of its own re-deal null"))

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


def _register_heating_system(main_heating_fuel: object) -> str:
    """Map a legacy free-text `main_heating_fuel` onto a heating-regime key.

    Only the phrasings this repository's own legacy property dicts actually use.
    An unrecognised string returns the gas key deliberately: on THIS path the
    vocabulary is uncontrolled, so an unrecognised value is far more likely to be a
    spelling of something already listed than a machine nobody has registered, and
    the gas band is the strict end. The typed path (`premise_trace_population`)
    carries an ENUM and therefore gets the visible-hole treatment instead.
    """
    text = str(main_heating_fuel or "").lower()
    if "heat pump" in text or "ashp" in text:
        return "heat_pump_air"
    if "storage" in text:
        return "electric_storage"
    if "electric" in text:
        return "electric_direct"
    return "gas_boiler_combi"


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
    registers: list[str] = []
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
        # The REGISTER field a real supplier holds, mapped from its free-text
        # vocabulary onto the heating-regime keys. Anything unrecognised reads as
        # gas, which is the STRICTER band (fail-closed) — this path's properties
        # are legacy dicts with no controlled vocabulary, so an unrecognised string
        # is far more likely to be a spelling than a new machine.
        registers.append(_register_heating_system(prop.get("main_heating_fuel")))

    return PopulationTraces(
        generator=generator,
        homes=tuple(homes),
        grids=tuple(grids),
        is_weekend=tuple(bool(d.is_weekend) for d in weather_days),
        annual_kwh=tuple(annual),
        heating_systems=tuple(registers),
        # NO SPACE-HEAT SPLIT, deliberately and correctly: this path rescales one
        # national shape and has no notion of which appliance drew what, so it
        # cannot state the fact and does not get the leniency. Its whole meter is
        # judged by L1.2 — which is what keeps the birth condition red.
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
        # `source.system` is the HOUSEHOLD RECORD's heating system, carried onto
        # the trace when it was generated — a register fact, not a reading of the
        # numbers the band then judges. Read as the enum's string VALUE so the
        # harness holds no import on the generator's types.
        heating_systems=tuple(str(getattr(t.source.system, "value", t.source.system))
                              for t in traces),
        # The space-heating machine's own draw, carried ONLY where it lands on the
        # commodity being judged. `heating_commodity` is the trace's own statement
        # of which meter its heat is on — a plumbing fact, not a reading of the
        # numbers — so a gas-heated home contributes zeros and its L1.2 is
        # bit-for-bit what it was before this field existed.
        space_heat_grids=tuple(
            tuple(
                tuple(day.heating_fuel_kwh) if t.heating_commodity == commodity
                else (0.0,) * len(day.heating_fuel_kwh)
                for day in t.days
            )
            for t in traces
        ),
        # The WATER-heating machine, by the same rule and keyed on the same stated
        # plumbing fact (H38). `dhw_fuel_kwh` is the fuel the water heater drew,
        # whichever commodity it drew it on, and this generator puts hot water on
        # the same meter as space heat — so keying on `heating_commodity` puts a
        # gas home's cylinder on the gas meter, where L1.1 cannot see it, and
        # contributes zeros to the electricity meter it is judged on.
        #
        # THE FAILURE DIRECTION IF THAT EVER STOPS BEING TRUE (a gas-heated home
        # with an electric immersion) IS THE STRICT ONE: this would contribute
        # zeros, the water heater would stay in the judged meter, and the home
        # would be held to a floor derived without it. That is the reading this
        # atom calls too strict — it is not a hole, and it is asserted rather than
        # hoped for in `test_a_water_heater_on_the_OTHER_commodity_is_not_netted`.
        water_heat_grids=tuple(
            tuple(
                tuple(day.dhw_fuel_kwh) if t.heating_commodity == commodity
                else (0.0,) * len(day.dhw_fuel_kwh)
                for day in t.days
            )
            for t in traces
        ),
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
    rows = _premise_forgone(
        observations,
        unit_rate_p_per_kwh=unit_rate_p_per_kwh,
        belief=belief,
        fuel=fuel,
        measures=measures,
    )
    misranked = sum(1 for r in rows if r.misranked)
    declined_with_value = sum(1 for r in rows if r.declined_with_value)
    value_destroying = sum(1 for r in rows if r.value_destroying)
    forgone_gbp = sum(r.forgone_gbp for r in rows)
    forgone_kwh = sum(r.forgone_kwh for r in rows)
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


@dataclass(frozen=True)
class PremiseForgone:
    """ONE premise's contribution to the money consequence.

    THE POINT OF SPLITTING IT OUT (2026-08-11, fifth Expert Hour on this machinery).
    `forgone_lifetime_gbp` is a SUM, and a sum carries no error bar: the money
    headline was a 5%-of-the-larger band on the difference of two such sums, which
    on the authored panel published a 57.7% margin that was 80.6% ONE HOUSE. Deciding
    that headline per premise needs the per-premise amounts, and a second loop that
    recomputed them would be two numbers under one name — so `money_consequence`
    aggregates THIS, and the verdict resamples THIS, and there is exactly one
    definition of what a premise forgoes.
    """

    premise_id: str
    forgone_gbp: float
    forgone_kwh: float
    misranked: bool
    declined_with_value: bool
    value_destroying: bool


def _premise_forgone(
    observations: Sequence[FabricObservation],
    *,
    unit_rate_p_per_kwh: float,
    belief: str = "epc",
    fuel: str = "gas",
    measures: Mapping[str, fi.RetrofitOffer] | None = None,
) -> list[PremiseForgone]:
    """The money consequence PER PREMISE, in panel order — the body of
    `money_consequence`, lifted so the verdict and the total read the same numbers.

    Every premise appears, including the ones that cost nothing: a premise where the
    belief is wrong but the DECISION survives is a real zero, not an absence, and a
    paired resample that dropped those rows would be resampling a different panel
    from the one the totals are quoted over.
    """
    if belief not in ("epc", "inferred"):
        raise ValueError(f"unknown belief {belief!r}")
    if fuel not in CARBON_KG_PER_KWH:
        raise ValueError(f"unknown fuel {fuel!r} — no published carbon factor")

    catalogue = dict(measures if measures is not None else fi.OFFER_BOOK)
    rows: list[PremiseForgone] = []
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
            rows.append(
                PremiseForgone(
                    premise_id=o.premise_id,
                    forgone_gbp=0.0,
                    forgone_kwh=0.0,
                    misranked=False,
                    declined_with_value=False,
                    value_destroying=False,
                )
            )
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
        declined = chosen == fi.DO_NOTHING
        rows.append(
            PremiseForgone(
                premise_id=o.premise_id,
                forgone_gbp=true_values[best] - true_values[chosen],
                forgone_kwh=(
                    _saving_of(
                        best,
                        o.actual_hlc_kw_per_k,
                        o.annual_heat_kwh,
                        o.annual_degree_days_k_day,
                        catalogue,
                    )
                    - _saving_of(
                        chosen,
                        o.actual_hlc_kw_per_k,
                        o.annual_heat_kwh,
                        o.annual_degree_days_k_day,
                        catalogue,
                    )
                ),
                misranked=not declined,
                declined_with_value=declined,
                value_destroying=not declined and true_values[chosen] < 0.0,
            )
        )
    return rows


# ===========================================================================
# THE HEADLINE'S OWN FAILURE MODES
# ===========================================================================
#
# Added 2026-08-11 (this atom's Expert Hour, findings 2/3/4). Everything above
# measures the COMPANY. This section measures the MEASUREMENT: three ways the two
# numbers this atom publishes can be right about their arithmetic and wrong about
# what a reader takes from them. Each is a standing, failable control rather than a
# note in a design doc, because the Hour found all three by computing them and a
# prose warning does not recompute itself next tick (MAKE IT STICK).
#
#  (2) DILUTION — `inference_improvement` averages over premises where the
#      inference never ran, so the published number moves with EPC lodgement
#      COVERAGE while the estimator is unchanged. Coverage reading as skill.
#  (3) DIRECTION — the gap is |belief - truth|-shaped, so a belief that is wrong
#      the SAME WAY everywhere scores identically to one that is wrong at random.
#      The first means the company is wrong about the STOCK; the second means it
#      is imprecise about houses. Different failures, different remedies.
#  (4) COMPOSITION — the money verdict can be decided by the panel's own sign
#      composition rather than by the beliefs being compared. An upward-biased
#      belief buys more measures, and on a panel where truth mostly exceeds the
#      register, buying more is right more often. That is not skill.
#
# R10, class not instance: none of the three is patched at its one observed site.
# Each is a measure with a named defect and a mutation that fires it.


# WHICH PREMISES THE INFERENCE ACTUALLY RAN ON, decided by the BASIS the company
# itself stamped on the belief — never by comparing the two arms' numbers. Float
# equality would be a tautology with the very thing being measured: an inference
# that genuinely ran and landed on its prior would be scored as "never ran", and
# the dilution correction would then hide inside the correction. The basis is
# independent evidence, written by `thermal_inference` before this module sees it.
INFERENCE_RAN_BASES = (EvidenceBasis.METER_AND_EPC, EvidenceBasis.METER_ONLY)


def inference_ran(observation: FabricObservation) -> bool:
    """Did meter evidence enter this premise's posterior at all?"""
    return observation.inferred_basis in INFERENCE_RAN_BASES


@dataclass(frozen=True)
class ArmAgreement:
    """How much of the published improvement is carried by rows that can carry any.

    `improvement_all` is the headline as published; `improvement_informed` is the
    same comparison restricted to premises where the inference ran. They are NOT
    the same statistic on different row counts: `prediction_gap` normalises to the
    no-skill baseline of the population it is handed, so the informed figure has
    its own denominator. Both are carried, with the tie fraction between them, so a
    reader can see the dilution instead of inferring it.
    """

    premises: int
    informed_premises: int
    tie_fraction: float
    identical_arm_premises: int
    informed_but_identical: int
    epc_gap_all: float
    inferred_gap_all: float
    improvement_all: float
    epc_gap_informed: float
    inferred_gap_informed: float
    improvement_informed: float

    @property
    def informed_fraction(self) -> float:
        return self.informed_premises / self.premises


def arm_agreement(observations: Sequence[FabricObservation]) -> ArmAgreement:
    """Condition the improvement headline on whether the inference ran at all.

    FAIL-LOUD, deliberately. When too few premises are meter-armed to measure the
    conditioned figure, this raises rather than returning the diluted one — an
    inference headline over a population where inference barely ran is not a weaker
    number, it is a number about something else. Falling back would be the exact
    fail-open shape (`pass on missing/empty`) this module exists to catch.
    """
    _require_homes(observations, minimum=MIN_HOMES_FOR_DIVERSITY, name="arm_agreement")
    informed = [o for o in observations if inference_ran(o)]
    # The basis predicate's own FALSIFIER, and it is not decoration. If a premise
    # whose basis says no meter evidence entered nonetheless holds two DIFFERENT
    # arms, the basis is lying about the belief and every conditioned figure below
    # is meaningless. That contradiction is loud, not logged.
    for o in observations:
        if not inference_ran(o) and o.inferred_hlc_kw_per_k != o.epc_hlc_kw_per_k:
            raise InsufficientEvidence(
                f"{o.premise_id}: basis {o.inferred_basis.value} says no meter evidence "
                f"entered, but the posterior ({o.inferred_hlc_kw_per_k!r}) differs from the "
                f"prior ({o.epc_hlc_kw_per_k!r}) — the basis does not describe the belief"
            )
    if len(informed) < MIN_HOMES_FOR_DIVERSITY:
        raise InsufficientEvidence(
            f"arm_agreement: the inference ran on {len(informed)} of {len(observations)} "
            f"premises, below the {MIN_HOMES_FOR_DIVERSITY} needed to measure what it "
            f"bought; the undiluted headline is not available and the diluted one is "
            f"not a substitute"
        )
    epc_all = epc_vs_actual_gap(observations)
    inferred_all = inferred_vs_actual_gap(observations)
    epc_informed = epc_vs_actual_gap(informed)
    inferred_informed = inferred_vs_actual_gap(informed)
    identical = [
        o for o in observations if o.inferred_hlc_kw_per_k == o.epc_hlc_kw_per_k
    ]
    return ArmAgreement(
        premises=len(observations),
        informed_premises=len(informed),
        tie_fraction=1.0 - len(informed) / len(observations),
        identical_arm_premises=len(identical),
        # An inference that ran and moved the belief by exactly nothing. Reported
        # rather than folded in: it is real (a posterior can land on its prior) and
        # it is also what a broken estimator looks like.
        informed_but_identical=sum(1 for o in identical if inference_ran(o)),
        epc_gap_all=epc_all.gap,
        inferred_gap_all=inferred_all.gap,
        improvement_all=epc_all.gap - inferred_all.gap,
        epc_gap_informed=epc_informed.gap,
        inferred_gap_informed=inferred_informed.gap,
        improvement_informed=epc_informed.gap - inferred_informed.gap,
    )


def _two_sided_sign_test_p(n_above: int, n_below: int) -> float:
    """Exact two-sided binomial sign test at p=0.5. Ties are excluded by the caller,
    which is the standard treatment: a belief that is exactly right took no side."""
    n = n_above + n_below
    if n == 0:
        return 1.0
    k = min(n_above, n_below)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2.0**n)
    return min(1.0, 2.0 * tail)


# The p below which a one-signed belief error is called SYSTEMATIC. A DIAGNOSTIC
# band (R12): it decides what the row SAYS, never what the estimator is tuned to.
SIGN_SYSTEMATIC_P = 0.05


@dataclass(frozen=True)
class BeliefBias:
    """The DIRECTION of one arm's error, which the |gap| headline cannot see.

    A population of beliefs that are each 10% wrong at random and a population that
    are each 10% wrong UPWARD produce the same gap. Only the second means the
    company is wrong about the stock, and only the second survives averaging into
    every portfolio-level number built on top of it.
    """

    belief: str
    premises: int
    n_above: int
    n_below: int
    n_exact: int
    signed_mean_error_kw_per_k: float
    signed_mean_relative_error: float
    sign_test_p: float

    @property
    def share_above(self) -> float:
        decided = self.n_above + self.n_below
        return self.n_above / decided if decided else 0.0

    @property
    def is_systematic(self) -> bool:
        """One-signed beyond chance. `False` on an all-tie population, which is the
        honest reading: a belief that is never wrong has no direction to be wrong in."""
        return (
            self.n_above + self.n_below > 0
            and self.sign_test_p < SIGN_SYSTEMATIC_P
        )

    @property
    def direction(self) -> str:
        if not self.is_systematic:
            return "none"
        return "over" if self.n_above > self.n_below else "under"

    @property
    def mean_agrees_with_majority(self) -> bool:
        """Do the COUNT and the AVERAGE tell the same story?

        They can disagree, and on the drawn 200-premise population they do: the
        register is below truth on 126 of 200 premises while the mean signed error
        is +19.6%, because a minority of large over-statements outweighs a majority
        of small under-statements. Both numbers are correct and a sentence that put
        them side by side without saying so would read as a contradiction — one
        name, two numbers, which is this project's own recurring defect shape. A
        skewed error distribution is itself the finding: a supplier reading the mean
        would insulate the wrong houses from the ones a supplier reading the median
        would pick.
        """
        if self.direction == "none":
            return True
        return (self.signed_mean_relative_error > 0.0) == (self.direction == "over")


def belief_bias(
    observations: Sequence[FabricObservation], *, belief: str = "epc"
) -> BeliefBias:
    """Is this arm wrong in a FIXED direction, or merely wrong?"""
    _require_homes(observations, minimum=MIN_HOMES_FOR_DIVERSITY, name="belief_bias")
    if belief not in ("epc", "inferred"):
        raise ValueError(f"unknown belief {belief!r}")
    errors, relative = [], []
    n_above = n_below = n_exact = 0
    for o in observations:
        held, _sd, _basis = o.belief_arm(belief)
        error = held - o.actual_hlc_kw_per_k
        if not math.isfinite(error):
            raise NonFiniteTrace(f"{o.premise_id}: {belief} error is {error!r}")
        errors.append(error)
        relative.append(error / o.actual_hlc_kw_per_k)
        if error > 0.0:
            n_above += 1
        elif error < 0.0:
            n_below += 1
        else:
            n_exact += 1
    return BeliefBias(
        belief=belief,
        premises=len(observations),
        n_above=n_above,
        n_below=n_below,
        n_exact=n_exact,
        signed_mean_error_kw_per_k=statistics.fmean(errors),
        signed_mean_relative_error=statistics.fmean(relative),
        sign_test_p=_two_sided_sign_test_p(n_above, n_below),
    )


def _reflect(value: float, through: float, *, premise_id: str, name: str) -> float:
    """LOG-preserving reflection: same RATIO error, opposite sign. `through**2/value`.

    Kept as the panel mirror's FALLBACK and as the revision mirror's only rule (a
    posterior reflected through its prior is a ratio statement about a step, and it
    is always positive). It preserves the log error exactly and the LEVEL error only
    approximately — see `_reflect_level` for why that distinction decides whether the
    panel mirror is an instrument or an anecdote.
    """
    for label, v in ((name, value), ("pivot", through)):
        if not math.isfinite(v) or v <= 0.0:
            raise InsufficientEvidence(
                f"{premise_id}: a non-positive {label} ({v!r}) cannot be reflected"
            )
    return through * through / value


def _reflect_level(value: float, through: float, *, premise_id: str, name: str) -> float:
    """LEVEL-preserving reflection: `2*through - value`. Same ABSOLUTE error,
    opposite sign — and the absolute error is the quantity `prediction_gap` is built
    from, so this is the reflection that leaves the mirrored arm's own numerator
    untouched to the bit.

    NOT DEFINED EVERYWHERE, which is the whole reason the log form was reached for
    first: it goes non-positive wherever the truth exceeds TWICE the register. The
    caller therefore tests the WHOLE panel before using it and falls back whole —
    a panel reflected two different ways on two subsets is two instruments, which is
    the confound this mirror exists to detect.
    """
    for label, v in ((name, value), ("pivot", through)):
        if not math.isfinite(v) or v <= 0.0:
            raise InsufficientEvidence(
                f"{premise_id}: a non-positive {label} ({v!r}) cannot be reflected"
            )
    reflected = 2.0 * through - value
    if reflected <= 0.0:
        raise InsufficientEvidence(
            f"{premise_id}: reflecting {name} ({value!r}) through {through!r} gives "
            f"{reflected!r} — a house cannot lose heat at a negative rate"
        )
    return reflected


LEVEL_PRESERVING = "level_preserving"
LOG_PRESERVING_FALLBACK = "log_preserving_fallback"


def _register_mad(
    before: Sequence[FabricObservation], after: Sequence[FabricObservation]
) -> float:
    """How far the reflection moved the register arm's error PER PREMISE, averaged —
    an aggregate of differences, never a difference of aggregates.

    THE DISTINCTION IS THE WHOLE POINT (2026-08-11, third Expert Hour on this
    machinery). `_register_mae` before and after gives `|mean(e') - mean(e)|`, which
    is bounded ABOVE by this number and equals it only when every premise's
    disturbance shares a sign. The reflection promises preservation PER PREMISE
    ("same ABSOLUTE error, opposite sign"), so a term built on the difference of the
    two means is not the promise measured — it is the promise measured after the
    breaches have been allowed to cancel.

    They do cancel here. The log-preserving fallback scales each premise's error by
    `register/truth`, which is BELOW one where the register under-states and ABOVE
    one where it over-states, and both published populations are mixed-direction
    (register over-states on 1 of 15 authored and 74 of 200 drawn). Measured on a
    real 20-premise subpanel of this atom's own drawn population, the difference-of-
    means read 4.36% — inside the 5% band, "faithful" — over a mirror that had moved
    the register arm's error by 44.51% per premise. A factor of 10.2, in the
    passing direction.
    """
    if len(before) != len(after):
        raise InsufficientEvidence(
            f"a mirrored panel of {len(after)} cannot be compared premise-by-premise "
            f"with an original of {len(before)}"
        )
    total = 0.0
    for o, m in zip(before, after):
        if o.premise_id != m.premise_id:
            raise InsufficientEvidence(
                f"mirrored rows are out of order ({o.premise_id!r} vs {m.premise_id!r})"
                " — a per-premise disturbance cannot be measured across a reordering"
            )
        total += abs(
            abs(m.epc_hlc_kw_per_k - m.actual_hlc_kw_per_k)
            - abs(o.epc_hlc_kw_per_k - o.actual_hlc_kw_per_k)
        )
    return total / len(before)


def weight_null_panel(
    observations: Sequence[FabricObservation],
) -> list[FabricObservation]:
    """THE MIRROR'S OWN NULL: the panel re-weighted exactly as the mirror re-weights
    it, with NO mirror signal in it at all.

    Each premise takes the mirrored row's `annual_heat_kwh` and keeps its own truth
    and both its beliefs. So every premise's `register - truth` error is identical to
    the unmirrored panel, bit for bit — the sign composition the panel mirror exists
    to reverse is NOT reversed here — and anything that moves in the money verdict
    moved because the mirror re-composed the panel's money weights, not because the
    stock failed the other way.

    NOT A WORLD, AND NEVER PUBLISHED AS ONE. A house whose bill moves while its heat
    loss does not is not a house; that incoherence is deliberate and is what isolates
    the channel. This is the same kind of instrument as `mirror_decision_confidence`
    (estimates held, error bars swapped) — a panel built to hold one thing fixed so
    the other can be attributed, not a claim about any stock.
    """
    return [
        _dc_replace(o, annual_heat_kwh=m.annual_heat_kwh)
        for o, m in zip(observations, panel_mirror(observations).rows)
    ]


def _register_mae(observations: Sequence[FabricObservation]) -> float:
    """The register arm's RAW mean absolute error — the quantity a reflection built
    around that arm claims to preserve, un-normalised.

    Deliberately NOT read off `epc_vs_actual_gap().components["mae_model"]`: that
    value is rounded to 6 decimals for display, and a fidelity term whose subject is
    quantised at 1e-6 would report a real disturbance below that as exactly zero —
    the DIFFERENCE-shaped control that fires (or here, fails to fire) on the
    quantisation rather than on the effect.
    """
    return sum(
        abs(o.epc_hlc_kw_per_k - o.actual_hlc_kw_per_k) for o in observations
    ) / len(observations)


@dataclass(frozen=True)
class PanelMirror:
    """The mirrored panel AND the statement of how it was made.

    The reflection used is part of the measurement, not an implementation detail:
    the two reflections preserve different errors, and `prediction_gap` consumes one
    of them. A row that reported a mirror verdict without saying which reflection
    produced it would be reporting two different instruments under one name.
    """

    rows: tuple[FabricObservation, ...]
    reflection: str
    infeasible_premises: int


def panel_mirror(observations: Sequence[FabricObservation]) -> PanelMirror:
    """The SIGN-MIRRORED PANEL: a world where the register OVER-states heat loss.

    The truth is reflected through the register prior, so each premise keeps the
    register's error magnitude and reverses its direction. Both beliefs are left
    untouched — this is the SAME company, holding the SAME numbers, in a stock that
    fails the other way. Not a hypothetical stock either: new-build SAP ratings that
    flatter as-built performance, and post-retrofit certificates never re-lodged,
    both produce registers that over-state.

    WHICH REFLECTION, AND WHY IT CHANGED (2026-08-11, Expert Hour on this atom's own
    caveat machinery). This used to be the LOG-preserving reflection unconditionally,
    justified in its own docstring by an assertion that the level-preserving one
    "goes non-positive on a third of real panels". That claim was never measured. It
    is now, on both populations this atom publishes: **0 of 15 authored and 0 of 200
    drawn premises** are infeasible, because a register that under-states by 13-20%
    does not under-state by more than half. The stated reason for the weaker
    instrument did not hold on either population it was applied to — and the weaker
    instrument is what made the mirror's own accuracy artefact big enough to swamp
    the effect it perturbs.

    So: level-preserving by DEFAULT, because `prediction_gap`'s numerator is a mean
    ABSOLUTE error and this reflection leaves the register arm's numerator identical
    to the bit. Whole-panel fallback to the log form where any premise cannot be
    reflected that way, with the count carried, because a mirror nobody can run on a
    real panel is not the improvement it looks like — and because falling back per
    premise would silently make the panel two instruments.

    `annual_heat_kwh` moves with the truth in proportion under either reflection. A
    house whose heat loss halves and whose bill does not is not a house, and leaving
    the bill fixed would let the mirror change the DECISION through the fabric share
    rather than through the fabric — a confound inside the control designed to find
    confounds.
    """
    infeasible = sum(
        1
        for o in observations
        if not _level_reflection_is_feasible(o.actual_hlc_kw_per_k, o.epc_hlc_kw_per_k)
    )
    reflect = _reflect if infeasible else _reflect_level
    mirrored = []
    for o in observations:
        actual = reflect(
            o.actual_hlc_kw_per_k, o.epc_hlc_kw_per_k,
            premise_id=o.premise_id, name="truth",
        )
        scale = actual / o.actual_hlc_kw_per_k
        mirrored.append(
            FabricObservation(
                premise_id=o.premise_id,
                actual_hlc_kw_per_k=actual,
                epc_hlc_kw_per_k=o.epc_hlc_kw_per_k,
                inferred_hlc_kw_per_k=o.inferred_hlc_kw_per_k,
                floor_area_m2=o.floor_area_m2,
                annual_heat_kwh=o.annual_heat_kwh * scale,
                annual_degree_days_k_day=o.annual_degree_days_k_day,
                epc_relative_sd=o.epc_relative_sd,
                inferred_relative_sd=o.inferred_relative_sd,
                epc_basis=o.epc_basis,
                inferred_basis=o.inferred_basis,
            )
        )
    return PanelMirror(
        rows=tuple(mirrored),
        reflection=LOG_PRESERVING_FALLBACK if infeasible else LEVEL_PRESERVING,
        infeasible_premises=infeasible,
    )


def _level_reflection_is_feasible(value: float, through: float) -> bool:
    """Whether `2*through - value` is a heat loss coefficient a house could have."""
    return (
        math.isfinite(value)
        and math.isfinite(through)
        and value > 0.0
        and through > 0.0
        and 2.0 * through - value > 0.0
    )


def mirror_panel_composition(
    observations: Sequence[FabricObservation],
) -> list[FabricObservation]:
    """The mirrored rows alone, for callers that do not need the declaration."""
    return list(panel_mirror(observations).rows)


def mirror_revision_direction(
    observations: Sequence[FabricObservation],
) -> list[FabricObservation]:
    """The SAME inference revising the OTHER WAY, by the same amount.

    The posterior is reflected through the prior it started from, so the company
    moves off its register by an identical step in the opposite direction. Truth and
    register are untouched: this asks whether the inferred arm's money advantage came
    from moving the RIGHT WAY on this panel rather than from moving well.

    A premise the inference never touched stays exactly where it was — reflecting a
    posterior that equals its prior returns the prior, so the untouched rows remain
    untouched by construction rather than by a special case.
    """
    return [
        FabricObservation(
            premise_id=o.premise_id,
            actual_hlc_kw_per_k=o.actual_hlc_kw_per_k,
            epc_hlc_kw_per_k=o.epc_hlc_kw_per_k,
            inferred_hlc_kw_per_k=_reflect(
                o.inferred_hlc_kw_per_k, o.epc_hlc_kw_per_k,
                premise_id=o.premise_id, name="posterior",
            ),
            floor_area_m2=o.floor_area_m2,
            annual_heat_kwh=o.annual_heat_kwh,
            annual_degree_days_k_day=o.annual_degree_days_k_day,
            epc_relative_sd=o.epc_relative_sd,
            inferred_relative_sd=o.inferred_relative_sd,
            epc_basis=o.epc_basis,
            inferred_basis=o.inferred_basis,
        )
        for o in observations
    ]


def mirror_decision_confidence(
    observations: Sequence[FabricObservation],
) -> list[FabricObservation]:
    """SWAP the two arms' error bars and bases, leaving both point estimates alone.

    The third thing that can decide the money verdict, and the one neither sign
    mirror can see. `fabric_intervention.decide` refuses to spend on a belief that
    is too wide or rests on a stock prior, so an arm can forgo less money purely by
    being ALLOWED TO ACT more often — the C14 posterior carries a narrower interval
    and a `meter_and_epc` basis, and declines on 3 premises where the register arm
    declines on 6. If the verdict follows the error bar rather than the estimate,
    the money headline is scoring the company's CONFIDENCE and being read as its
    ACCURACY, which is a different claim about a different organ.

    Every point estimate is untouched, so both accuracy gaps are IDENTICAL under
    this mirror by construction — and that is what makes it a clean instrument: any
    money movement here cannot be an accuracy movement.
    """
    return [
        FabricObservation(
            premise_id=o.premise_id,
            actual_hlc_kw_per_k=o.actual_hlc_kw_per_k,
            epc_hlc_kw_per_k=o.epc_hlc_kw_per_k,
            inferred_hlc_kw_per_k=o.inferred_hlc_kw_per_k,
            floor_area_m2=o.floor_area_m2,
            annual_heat_kwh=o.annual_heat_kwh,
            annual_degree_days_k_day=o.annual_degree_days_k_day,
            epc_relative_sd=o.inferred_relative_sd,
            inferred_relative_sd=o.epc_relative_sd,
            epc_basis=o.inferred_basis,
            inferred_basis=o.epc_basis,
        )
        for o in observations
    ]


@dataclass(frozen=True)
class CompositionVerdict:
    """Do the two published headlines agree, and does the money one survive a mirror?

    The Hour's finding in one object: on the authored panel the inference is WORSE
    on accuracy and BETTER on money, and the money advantage is bought by a bias
    that happens to point the panel's way. `composition_decided` is true when the
    money verdict names the other arm once the panel's sign composition is reversed
    — i.e. when the ranking was decided by the population rather than by the beliefs.
    """

    premises: int
    accuracy_favours: str
    # ...AND ITS ERROR BAR, because until the fourth Hour it had none: the verdict
    # above was a relative band on the difference of two AGGREGATES, and that band
    # sat at the median of its own subject's distribution (see `AccuracyVerdict`).
    # The advantage is per premise, positive where the INFERENCE sat closer.
    accuracy_mean_advantage_kw_per_k: float
    accuracy_ci_lo: float
    accuracy_ci_hi: float
    accuracy_tied_premises: int
    # ...and what the OLD rule said, so the repair never silently deletes a sentence
    # a reader was previously given.
    accuracy_aggregate_favours: str
    accuracy_aggregate_relative_gap: float
    # THE MONEY HEADLINE, AND ITS ERROR BAR — carried as the verdict OBJECT rather
    # than as another eight flat floats (2026-08-11, fifth Hour). Each of the four
    # money verdicts in this row now has a point estimate, an interval, a tie count,
    # a one-house concentration share and the old aggregate rule's answer; flattening
    # four of those into the constructor would have been thirty-two fields and an
    # invitation to wire one of them to the wrong panel. `money_favours` and the
    # three `*_mirror_money_favours` remain as PROPERTIES, so every existing reader
    # keeps its attribute and gets the repaired verdict.
    money: MoneyVerdict
    forgone_epc_gbp: float
    forgone_inferred_gbp: float
    improvement: float
    truth_above_epc_share: float
    revision_agrees_with_panel_share: float
    # THE PANEL MIRROR — same company, stock that fails the other way.
    panel_mirror_money: MoneyVerdict
    panel_mirror_forgone_epc_gbp: float
    panel_mirror_forgone_inferred_gbp: float
    panel_mirror_improvement: float
    # ITS OWN FIDELITY, so the reader is not asked to take the instrument on trust.
    # `epc_gap` and `panel_mirror_epc_gap` are the REGISTER arm's accuracy before and
    # after — the arm the reflection is built around, and therefore the only arm
    # whose movement is pure artefact.
    epc_gap: float
    panel_mirror_epc_gap: float
    # ...and the register arm's RAW error, before and after, because the gap above is
    # a RATIO and the reflection moves its denominator ON PURPOSE (2026-08-11 second
    # Hour). These two are the quantity the reflection actually claims to preserve.
    epc_register_mae: float
    panel_mirror_register_mae: float
    # ...and the PER-PREMISE disturbance, because the pair above are two means and a
    # promise made per premise cannot be audited by the difference of two means
    # (2026-08-11, third Hour). This is the numerator of the fidelity gate.
    panel_mirror_register_mad: float
    panel_mirror_reflection: str
    panel_mirror_infeasible_premises: int
    # THE WEIGHT-ONLY NULL — the mirror's re-composition channel with the mirror's
    # signal removed. The gate above is denominated in kW/K; the verdict it guards is
    # denominated in GBP, and these are the same money figures with the sign flip
    # taken out (2026-08-11, third Hour).
    weight_null_forgone_epc_gbp: float
    weight_null_forgone_inferred_gbp: float
    # THE REVISION MIRROR — same stock, inference stepping the other way.
    revision_mirror_money: MoneyVerdict
    revision_mirror_forgone_epc_gbp: float
    revision_mirror_forgone_inferred_gbp: float
    revision_mirror_improvement: float
    # THE CONFIDENCE MIRROR — same estimates, error bars swapped. Accuracy CANNOT
    # move here, so anything that does move is not accuracy.
    confidence_mirror_money: MoneyVerdict
    confidence_mirror_forgone_epc_gbp: float
    confidence_mirror_forgone_inferred_gbp: float
    declined_epc: int
    declined_inferred: int

    @property
    def money_favours(self) -> str:
        return self.money.favours

    @property
    def panel_mirror_money_favours(self) -> str:
        return self.panel_mirror_money.favours

    @property
    def revision_mirror_money_favours(self) -> str:
        return self.revision_mirror_money.favours

    @property
    def confidence_mirror_money_favours(self) -> str:
        return self.confidence_mirror_money.favours

    @property
    def money_aggregate_overstated(self) -> bool:
        """The old aggregate money rule named an arm the paired per-premise evidence
        cannot resolve.

        THE SAME DISCLOSURE-PROTECTING PROPERTY `accuracy_aggregate_overstated` IS,
        and for the same reason: a repair that makes a published verdict quieter must
        SAY it went quiet. On this atom's own drawn population that is 62% of
        25-home subpanels.
        """
        return self.money.aggregate_overstated

    @property
    def panel_mirror_money_unresolved(self) -> bool:
        """The panel mirror's OWN money verdict cannot be resolved on its own panel.

        A mirror is an instrument, and an instrument whose reading has an interval
        straddling zero has not measured anything. `composition_decided` is already
        safe here — `_flipped` refuses to call a decisive-vs-indecisive pair a flip —
        but SAFE IS NOT DISCLOSED: without this, the authored panel prints a mirror
        that "did not move the verdict" when what the mirror actually did was fail to
        produce a verdict. The two readings are opposite and the row said neither.
        """
        return not self.panel_mirror_money.resolved

    @property
    def verdicts_agree(self) -> bool:
        """The two headlines do not DECISIVELY name different arms. `False` is not a
        bug — it is the thing that must be SAID, because a door that renders two
        numbers without noting they disagree lets a reader take whichever one it read
        first. One headline being too close to call is not a disagreement."""
        return not _flipped(self.accuracy_favours, self.money_favours)

    @property
    def accuracy_aggregate_overstated(self) -> bool:
        """The old aggregate rule named an arm the paired per-premise evidence
        cannot resolve on this panel.

        THIS PROPERTY EXISTS TO STOP A REPAIR FROM DELETING A DISCLOSURE. On the
        authored panel the aggregate rule said accuracy favoured the register while
        money favoured the inference, so `verdicts_agree` was False and a HEADLINES
        DISAGREE caveat fired. Under the repaired verdict accuracy is UNRESOLVABLE
        there (15 premises, 7 of them exact ties), which makes `verdicts_agree` True
        and would have silently retired that sentence. A reader must be told the
        claim failed to resolve, not shown one fewer caveat.
        """
        return (
            self.accuracy_aggregate_favours != "neither"
            and self.accuracy_favours == "neither"
        )

    @property
    def panel_mirror_accuracy_drift(self) -> float:
        """How far the IMPROVEMENT moved under the panel mirror.

        REPORTED, AND EXPLICITLY NOT THE FIDELITY INSTRUMENT (2026-08-11 Expert Hour
        — it was being read as one, and it cannot be). This is a COMPOUND: it
        contains the artefact below AND the movement the mirror is FOR. Reflecting
        the truth is meant to wreck the posterior arm's accuracy — an inference that
        stepped the right way on this panel steps the wrong way in a stock that fails
        the other way, and that is the finding, not the noise. So this number is
        large whenever the mirror WORKS (0.1579 authored, 0.0717 drawn), and reading
        it as "how much the instrument disturbed the measurement" makes a working
        mirror look broken and can never come out small. Use
        `panel_mirror_relative_infidelity`.
        """
        return abs(self.panel_mirror_improvement - self.improvement)

    @property
    def panel_mirror_epc_gap_drift(self) -> float:
        """THE ARTEFACT TERM: how far the REGISTER arm's own accuracy moved.

        The reflection is built around this arm — every premise keeps |register −
        truth| exactly under the level-preserving form — so a faithful mirror leaves
        this at zero and anything left over is the instrument, not the panel. It is
        not identically zero even then, and the residual has one named cause rather
        than a shrug: `prediction_gap` divides by the NO-SKILL baseline, which is a
        property of the truth population, and reflecting the truth moves its spread.
        Measured on the two published populations: numerator identical to 6 decimals
        (0.020202 authored, 0.044774 drawn, before and after), whole-gap drift 0.0308
        and 0.0081 — i.e. the entire residual is the denominator, which is a
        statement about the metric and not about this mirror.
        """
        return abs(self.panel_mirror_epc_gap - self.epc_gap)

    @property
    def panel_mirror_relative_infidelity(self) -> float:
        """REPORTED, AND EXPLICITLY NOT THE FIDELITY GATE — the same compound shape,
        one level down (2026-08-11, second Expert Hour on this machinery).

        The gap is a RATIO: mean|register − truth| over the no-skill baseline. Under
        the level-preserving reflection the NUMERATOR is preserved to the bit — the
        reflection is `2*prior − value`, so every premise's |register − truth| is
        algebraically identical — and it was measured at exactly 0.000e+00 on all
        four populations this atom runs on (authored 15, drawn 200, and both suite
        fixtures). So 100% of this number is the DENOMINATOR: the no-skill baseline
        is a property of the truth population, and reflecting the truth population
        is what the mirror IS. Reading it as "how much the instrument disturbed the
        arm it was built around" restated a figure of 0 as 14.1% on the authored
        panel and published MIRROR INCONCLUSIVE over a mirror that had disturbed
        nothing. Split, exactly as the previous Hour split `accuracy_drift`:
        `panel_mirror_register_infidelity` is the artefact,
        `panel_mirror_normaliser_drift` is the intended move, and the gate is the
        former. NaN-safe and zero-safe as before.
        """
        if self.epc_gap == 0.0:
            return 0.0 if self.panel_mirror_epc_gap_drift == 0.0 else math.inf
        return self.panel_mirror_epc_gap_drift / abs(self.epc_gap)

    @property
    def panel_mirror_register_infidelity(self) -> float:
        """THE ARTEFACT, AND THE GATE: how far the reflection moved the register
        arm's own RAW error — the one quantity it claims to preserve.

        MEASURED off the mirrored rows, never assumed from the algebra — and measured
        PER PREMISE (2026-08-11, third Hour). This used to be
        `|mean(e') - mean(e)| / mean(e)`, a difference of two aggregates standing in
        for a promise the reflection makes about every premise separately. The two
        differ whenever the breaches point different ways, which on a mixed-direction
        panel under the log fallback is always: on a real 20-premise subpanel of this
        atom's own drawn population the old shape read 4.36% and passed the band over
        a mirror that had moved the register arm's error by 44.51% per premise.

        The numerator is now `_register_mad`, which cannot cancel. Under the
        level-preserving form it is still zero — that reflection genuinely does
        preserve every premise's absolute error — and that is a true reading, not a
        control that cannot fail: it fires on the log-preserving fallback, and the
        MONEY channel this term is blind to now has its own gate in
        `panel_mirror_weight_artefact`, because a term denominated in kW/K was never
        going to certify a verdict denominated in GBP.
        """
        if self.epc_register_mae == 0.0:
            return 0.0 if self.panel_mirror_register_mad == 0.0 else math.inf
        return self.panel_mirror_register_mad / abs(self.epc_register_mae)

    @property
    def panel_mirror_weight_artefact(self) -> float:
        """THE SECOND ARTEFACT, AND THE SECOND HALF OF THE GATE: how much of the
        mirror's movement in the DECIDING MARGIN is reproduced with no mirror signal
        in the panel at all (2026-08-11, third Expert Hour on this machinery).

        The money verdict is a comparison, so the quantity that decides it is the
        margin `forgone_inferred - forgone_epc`. The mirror moves that margin. So
        does the plain fact that reflecting the truth rescales every premise's
        `annual_heat_kwh` — by 0.151x to 9.518x on the drawn population, a 62.9x
        spread — and `money_consequence` is built on `annual_heat_kwh` through both
        arms and through the actionability test. This term is the null's share of the
        mirror's own movement: 0.0 means the verdict moved because the stock failed
        the other way, 1.0 means it moved because the panel was re-weighted and the
        sign flip contributed nothing.

        It is large on both published populations — 98% on the drawn panel — which is
        why the previous gate certifying this mirror at 0.0000% disturbance was
        certifying the one dimension the reflection preserves by algebra while the
        dimension the verdict is actually denominated in had done all the moving.

        NOT the same claim as "the verdict is wrong". Neither the mirror nor the null
        flips the ranking on either published population. What it says is that a
        NO-FLIP from this instrument is weak evidence, because the instrument applied
        almost no signal — and a null result from an instrument that barely moved is
        exactly the reading `panel_mirror_is_attributable` exists to prevent.

        THE ZERO CORNER, split rather than lumped. Where the mirror does not move the
        deciding margin the term is 0/0, and the two ways of arriving there are not
        the same event:

        * the weight null did not move it either — nothing happened in either
          channel, so no part of a movement that did not occur can be artefact. 0.0,
          and the verdict is as robust as it looks.
        * the weight null DID move it — then the mirror's net zero is two large
          opposing channels cancelling, not an instrument finding nothing. Infinity:
          a null assembled out of a re-composition and a sign flip that happened to
          annihilate is the least readable result this instrument can produce, and
          reading it as robustness is the exact error the gate exists to prevent.

        A first cut returned infinity for BOTH, which called a perfectly-faithful
        identity mirror (a register that is exactly right has nothing to reflect)
        unattributable. Caught by the suite, and the distinction is the fix.
        """
        moved_by_mirror = (
            self.panel_mirror_forgone_inferred_gbp - self.panel_mirror_forgone_epc_gbp
        ) - (self.forgone_inferred_gbp - self.forgone_epc_gbp)
        moved_by_weight = (
            self.weight_null_forgone_inferred_gbp - self.weight_null_forgone_epc_gbp
        ) - (self.forgone_inferred_gbp - self.forgone_epc_gbp)
        if moved_by_mirror == 0.0:
            return 0.0 if moved_by_weight == 0.0 else math.inf
        return abs(moved_by_weight) / abs(moved_by_mirror)

    @property
    def panel_mirror_normaliser_drift(self) -> float:
        """THE INTENDED MOVE: how far the no-skill baseline shifted, relatively.

        Not a defect and not infidelity — the mirror reflects the truth population,
        so the spread of that population moves unless the register's error is a pure
        translation. It is disclosed because a reader comparing `epc_gap` against
        `panel_mirror_epc_gap` is comparing two numbers measured against DIFFERENT
        yardsticks, which is a real caution about those two figures and says nothing
        about the money verdict (money never divides by this).
        """
        before = self.epc_gap
        after = self.panel_mirror_epc_gap
        if before == 0.0 or after == 0.0:
            return 0.0 if before == after else math.inf
        g0_before = self.epc_register_mae / before
        g0_after = self.panel_mirror_register_mae / after
        if g0_before == 0.0:
            return 0.0 if g0_after == 0.0 else math.inf
        return abs(g0_after - g0_before) / abs(g0_before)

    @property
    def panel_mirror_gap_difference_real(self) -> float:
        """The part of the visible move between the two gap figures that is a REAL
        change in the register arm's error — the yardstick held fixed.

        THE NUMBER THE READER ACTUALLY WANTED. `epc_gap` and `panel_mirror_epc_gap`
        are each `mae / g0`, so their difference mixes a numerator change (the
        register arm genuinely got better or worse under reflection) with a
        denominator change (the no-skill baseline moved, which IS the mirror). This
        re-measures the second figure against the FIRST one's baseline, so what is
        left is the numerator move alone, in the same unit as the two figures it
        sits between.
        """
        before = self.epc_gap
        if before == 0.0:
            return 0.0
        g0_before = self.epc_register_mae / before
        if g0_before == 0.0:
            return 0.0
        return (self.panel_mirror_register_mae - self.epc_register_mae) / g0_before

    @property
    def panel_mirror_gap_difference_relative(self) -> float:
        """How big the move between the two gap figures is, as a share of the larger
        — the SIZE question, kept apart from the attribution question below.

        Both are real and they are not the same: a difference can be entirely
        artefact and still too small to mislead anyone, and it can be large and
        mostly genuine. The old gate asked only a size question (via the drift) and
        answered an attribution question with it.
        """
        larger = max(abs(self.epc_gap), abs(self.panel_mirror_epc_gap))
        if larger == 0.0:
            return 0.0
        return abs(self.panel_mirror_epc_gap - self.epc_gap) / larger

    @property
    def panel_mirror_yardstick_share(self) -> float | None:
        """Of the difference a reader SEES between the two gap figures, how much is
        the baseline moving rather than the register arm's error changing.

        `None` when the two figures are identical at the precision the caveat prints
        them to: there is no visible difference to misattribute, so there is nothing
        to warn about (R11 — the vacuity guard is set by what the CONSUMER renders,
        not by float equality, or a difference invisible on the page would still
        raise a caveat about reading it).

        WHY THIS EXISTS, AND WHY IT IS NOT `panel_mirror_normaliser_drift` (2026-08-11,
        SIXTH Hour). The drift is a SIZE measure — how far the baseline went. The
        sentence it gated makes an ATTRIBUTION claim: "the difference between them is
        not an accuracy change". In the level-preserving regime those agree, because
        the numerator is held to the bit and so the whole difference IS the yardstick
        whenever there is one. In the LOG-FALLBACK regime — the one real path where
        the reflection does not preserve the register arm's error — they come apart,
        and the caveat asserted its claim on 101 of 300 fallback panels where the
        MAJORITY of the difference was a genuine accuracy change. Worst measured: the
        sentence printed "not an accuracy change" over a 18.2% difference that was
        68.6% exactly that.

        NOT THE DEFECT FIRST HYPOTHESISED, AND THE SUITE IS WHAT REFUTED IT. The Hour
        opened by reading the drawn population's silence (1.87% drift, 100% of the
        difference artefact) as a fail-open. It is not: 1.87% of the larger figure is
        a difference too small to mislead anyone, and silence there is right for a
        SIZE reason. Wiring the caveat to attribution alone made it fire on a fixture
        whose own comment recorded it as having nothing to caveat — an existing test
        caught it. Size and attribution are BOTH real questions and neither answers
        the other, which is why there are now two terms and two bands.

        AN ATTRIBUTION, NOT A RATIO OF THE OBSERVED MOVE. The first cut was
        |yardstick| / |observed|, which exceeds 1 whenever the two contributions
        oppose and partly cancel (283% on the log-fallback fixture) — a share that can
        exceed its own whole is not a share. Dividing by the sum of the magnitudes
        bounds it in [0, 1] and answers the attribution question directly.
        """
        real = self.panel_mirror_gap_difference_real
        observed = self.panel_mirror_epc_gap - self.epc_gap
        yardstick = observed - real
        if round(observed, GAP_RENDER_DP) == 0.0:
            return None
        magnitude = abs(yardstick) + abs(real)
        if magnitude == 0.0:
            return None
        return abs(yardstick) / magnitude

    @property
    def panel_mirror_is_attributable(self) -> bool:
        """Whether this mirror's verdict — flip OR no flip — may be read as a
        statement about the panel at all.

        A null result from an uncalibrated instrument is not evidence of no effect,
        and before this existed the mirror's only disclosure rode inside the
        COMPOSITION-DECIDED caveat, which fires exactly when the mirror DID flip. On
        both published populations it does not flip, so the instrument's own
        weakness was unrenderable precisely in the case where the reader was being
        invited to conclude something from silence.

        Gated on the ARTEFACT and not on the ratio (2026-08-11, second Hour): the
        ratio moved the gate in both wrong directions — it refused an exactly
        faithful mirror on the authored panel, and it passed mirrors that had moved
        the register's own error by up to 125% on real subpanels of the drawn one.

        BOTH DIMENSIONS, NOT ONE (2026-08-11, third Hour). The gate guards a verdict
        denominated in GBP and was reading a term denominated in kW/K — a term the
        level-preserving reflection zeroes by algebra, so on both published
        populations it certified the mirror at 0.0000% while the money weights the
        verdict is built from had moved across a 62.9x spread and the weight-only
        null reproduced 98% of the mirror's movement in the deciding margin. A
        fidelity claim has to cover the channel the consumer reads.
        """
        return (
            self.panel_mirror_register_infidelity <= MIRROR_FIDELITY_BAND
            and self.panel_mirror_weight_artefact <= MIRROR_WEIGHT_ARTEFACT_BAND
        )

    @property
    def composition_decided(self) -> bool:
        """The money ranking named a different arm in a stock that fails the other
        way — so it was a property of THIS PANEL, not of the beliefs compared.

        Deliberately still the raw flip, with `panel_mirror_is_attributable` carried
        beside it rather than folded in: a verdict that quietly became False because
        its instrument was blunt would report "the panel did not decide it", which is
        a different claim from "we could not tell", and it is the wrong one.
        """
        return _flipped(self.money_favours, self.panel_mirror_money_favours)

    @property
    def direction_bought(self) -> bool:
        """The money ranking named a different arm once the inference stepped the
        other way by the same amount — so the advantage was bought by moving the
        RIGHT WAY on this panel, not by moving well."""
        return _flipped(self.money_favours, self.revision_mirror_money_favours)

    @property
    def confidence_bought(self) -> bool:
        """The money ranking named a different arm once the two arms' ERROR BARS were
        swapped and nothing else. Accuracy is identical under that swap, so a flip
        here says the money headline is scoring how confidently the company may act,
        not how right it is."""
        return _flipped(self.money_favours, self.confidence_mirror_money_favours)


# How far apart two lower-is-better figures must be before the comparison is called
# a VERDICT at all, as a share of the larger. A DIAGNOSTIC band (R12) — it decides
# what the row says, never what anything is tuned to.
#
# It is here because the first version of this section did without it and was a
# control that fires on everything: `composition_decided` is a flip of a strict
# inequality, so on any population where the two arms cost about the same, an
# irrelevant nudge from the mirror flipped the verdict and the caveat announced a
# composition effect that was two floats in a coin toss. A finding that a
# 0.3%-of-the-larger difference changed sign is not a finding.
#
# MONEY ONLY, AND THAT IS NOW TRUE IN THE CODE AS WELL AS IN THIS COMMENT
# (2026-08-11, FOURTH Hour). Until then this constant ALSO decided
# `accuracy_favours` — a normalised accuracy gap — while the comment below asserted
# a firewall against exactly that ("one constant serving both would mean a change
# made for a money reason silently re-graded every mirror ever run"). It did. On the
# drawn population the published accuracy verdict cleared this band by 0.0032
# (5.32% against 5.00%), so moving it to 0.055 for a money reason erased a published
# accuracy verdict. `accuracy_favours` is now decided per premise with its own error
# bar (`_paired_accuracy_verdict`) and never touches this number.
VERDICT_MATERIALITY = 0.05

# How much of the register arm's own accuracy the panel mirror is allowed to move
# before its verdict is DIRECTIONAL EVIDENCE ONLY. A DIAGNOSTIC band (R12): it
# decides what the row SAYS about its own instrument, never what anything is tuned
# to — no reflection is chosen, and no threshold moved, because of the answer it
# gives.
#
# A SEPARATE CONSTANT FROM `VERDICT_MATERIALITY` ON PURPOSE, though it carries the
# same number today. That one is a band on MONEY (when are two costs the same cost);
# this one is a band on a NORMALISED ACCURACY GAP (when is an instrument's own
# disturbance small enough to read past). One constant serving both would mean a
# change made for a money reason silently re-graded every mirror ever run.
#
# Calibrated against what the mirror is looking FOR, not against what it currently
# scores: a composition effect worth naming reverses a verdict, and the money
# figures it reverses differ by tens of percent, so an artefact that stays inside
# 5% of the arm's own gap is an order of magnitude below the signal.
#
# ONE SUBJECT, AND THAT IS NOW TRUE IN THE CODE AS WELL AS IN THIS COMMENT
# (2026-08-11, SIXTH Hour — the same repair the FOURTH Hour made to
# `VERDICT_MATERIALITY`, one level down, and named as unrepaired by the fifth).
# Until now this constant ALSO gated the yardstick disclosure on
# `panel_mirror_normaliser_drift`, so a change made for a FAULT reason silently
# re-graded a disclosure about the mirror WORKING — the two subjects are not merely
# different, they are opposite in polarity: crossing this band means the instrument
# is broken, crossing that one means it is doing its job. The disclosure now has its
# own term in its own consumer's unit and its own band (`YARDSTICK_SHARE_BAND`).
# The calibration argument above is about artefact-versus-money-signal and was never
# an argument about when a yardstick shift is worth telling a reader about.
MIRROR_FIDELITY_BAND = 0.05

# The precision the two gap figures are RENDERED to wherever they are printed side
# by side. The yardstick caveat's vacuity guard is set from it rather than from float
# equality: a difference that rounds away on the page is not a difference a reader
# can misread, and a caveat about comparing two identical printed numbers is noise
# (R11 — grade the artefact the consumer actually renders).
GAP_RENDER_DP = 4

# How much of the VISIBLE difference between the two gap figures may be the no-skill
# baseline moving before a reader comparing them side by side is being invited to
# read an accuracy change that is not there. A DIAGNOSTIC band (R12): it decides what
# the row SAYS, never what anything is tuned to — no reflection is chosen and no
# figure is moved because of the answer it gives.
#
# A FOURTH CONSTANT, not a reuse of `MIRROR_FIDELITY_BAND`, which is the whole point
# of this Hour: that one is a band on a FAULT in kW/K (how much did the instrument
# disturb the arm it preserves), this is a band on an ATTRIBUTION (how much of what
# the reader sees is the instrument working). They answer opposite questions and the
# published populations prove it — the authored panel is simultaneously perfectly
# faithful on that term (0.0000%) and entirely yardstick on this one (100%).
#
# Set at half on the same logic as `MIRROR_WEIGHT_ARTEFACT_BAND` and
# `ONE_HOUSE_SHARE`: past that, the yardstick explains more of the difference than
# the real change does. Measured, the populations sit either side — 100% on both
# published rows and on the proportional fixture, 60.7% on one log-fallback panel,
# 27.3% on another whose register error genuinely moves — which is what a band that
# can fail looks like.
YARDSTICK_SHARE_BAND = 0.50

# How large the move between the two gap figures must be, as a share of the larger,
# before it is worth cautioning a reader about at all. The SIZE half of the caveat,
# and a FIFTH constant rather than a reuse of any band above — the sixth Hour's whole
# subject is that a size measure and an attribution measure had been collapsed onto
# one number, and answering that by collapsing the new pair onto one would be the
# same defect wearing the repair's name.
#
# It is here because the first cut of this Hour gated on attribution ALONE and fired
# on `test_the_caveat_list_is_EMPTY_on_a_population_with_nothing_to_caveat` — a
# fixture a previous Hour had already tuned to a 1.1% residual precisely so that
# "nothing to caveat" would mean something. Under a level-preserving reflection the
# attribution is 100% BY ALGEBRA whenever the gaps differ at all, so attribution
# alone makes this caveat unconditional on the common path, and a caveat that fires
# on everything is read as attentively as one that never fires.
#
# Set at 5% of the larger figure, the same shape (never the same constant) as
# `VERDICT_MATERIALITY` uses for two money figures: below that the two gaps round to
# the same story. Measured, the populations sit either side — 12.4% authored and 40%
# on the proportional fixture FIRE, 1.87% drawn and 1.1% on the nothing-to-caveat
# fixture stay silent.
YARDSTICK_MATERIAL_DIFFERENCE = 0.05
# How much of the mirror's movement in the deciding margin may be pure re-composition
# before its verdict stops being a statement about the sign flip. Set at half: past
# that, the null explains more of the movement than the signal does, and a no-flip is
# a statement about the weights rather than about the stock (2026-08-11, third Hour).
MIRROR_WEIGHT_ARTEFACT_BAND = 0.50

# How much of the money margin may come from a SINGLE premise before a resolved
# verdict is also reported as a statement about one house (2026-08-11, fifth Hour).
# A DIAGNOSTIC band (R12): it decides what the row SAYS, never what anything is
# tuned to — no premise is dropped and no verdict is changed because of it.
#
# A THIRD CONSTANT, not a reuse of either band above, and the reuse is the reason
# this one is written out longhand: when this was written `MIRROR_FIDELITY_BAND`
# gated the panel mirror AND triggered the yardstick disclosure on
# `panel_mirror_normaliser_drift`, two different subjects on one number, which is
# exactly what that constant's own comment says must never happen. Concentration is
# a third subject again. (That reuse was repaired by the SIXTH Hour, which this
# paragraph is what prompted — the split is `YARDSTICK_SHARE_BAND`.)
#
# Set at half on the same logic as `MIRROR_WEIGHT_ARTEFACT_BAND`: past that, one
# premise explains more of the margin than every other premise combined. Measured,
# the two published populations sit either side (80.6% authored, 22.5% drawn), which
# is what a band that can fail looks like.
ONE_HOUSE_SHARE = 0.50


#: THE ACCURACY VERDICT'S OWN RESAMPLE BUDGET, SEED AND LEVEL. Named rather than
#: literals at the call site (C-S2, RNG substream discipline): a verdict that can be
#: moved by quietly reseeding is not a verdict. The seed is this module's own; the
#: draw never touches the global RNG, so adding it shifted no other subsystem.
ACCURACY_VERDICT_RESAMPLES = 4000
ACCURACY_VERDICT_SEED = 20260811
ACCURACY_VERDICT_ALPHA = 0.05


def _favours(epc_value: float, inferred_value: float) -> str:
    """Which arm a lower-is-better MONEY figure prefers, or 'neither' when the two
    are too close for the difference to mean anything.

    MONEY PAIRS ONLY (2026-08-11, fourth Hour). Every remaining caller passes a pair
    of GBP totals; `accuracy_favours` used to come through here too and now does not.
    """
    larger = max(abs(epc_value), abs(inferred_value))
    if larger == 0.0 or abs(epc_value - inferred_value) <= VERDICT_MATERIALITY * larger:
        return "neither"
    return "inferred" if inferred_value < epc_value else "epc"


def _flipped(before: str, after: str) -> bool:
    """A verdict FLIP, not a verdict change. Going decisive-to-indecisive is a loss
    of resolution and is reported as such by the figures themselves; only two
    decisive verdicts naming DIFFERENT arms is the thing these mirrors look for."""
    return "neither" not in (before, after) and before != after


def _revision_agreement_share(observations: Sequence[FabricObservation]) -> float:
    """WHY THE MONEY VERDICT MIGHT BE BOUGHT RATHER THAN EARNED, as a number: the
    share of premises where the inference stepped the SAME WAY the truth lies from
    the register. Rows where the inference never moved take no side and are excluded,
    exactly as the sign test excludes exact ties."""
    agreeing = moved = 0
    for o in observations:
        step = o.inferred_hlc_kw_per_k - o.epc_hlc_kw_per_k
        truth_side = o.actual_hlc_kw_per_k - o.epc_hlc_kw_per_k
        if step == 0.0 or truth_side == 0.0:
            continue
        moved += 1
        agreeing += (step > 0.0) == (truth_side > 0.0)
    return agreeing / moved if moved else 0.0


@dataclass(frozen=True)
class AccuracyVerdict:
    """WHICH ARM IS THE BETTER BELIEF ABOUT A HOME'S FABRIC — with an error bar.

    THE DEFECT THIS REPLACES (2026-08-11, fourth Hour). `accuracy_favours` was a
    relative band on the DIFFERENCE OF TWO AGGREGATES: each arm's population-level
    normalised gap, compared against `VERDICT_MATERIALITY`. Three things were wrong
    with that, and only the third is about the constant.

    1. IT IS A PER-PREMISE CLAIM AUDITED BY A DIFFERENCE OF AGGREGATES — the exact
       sibling class the THIRD Hour named and then fixed in one place only (the
       mirror's fidelity term, `_register_mad`). The headline verdict itself was left
       on the aggregate form. "The inference is a better belief than the register" is
       a promise made about homes; two means let the breaches cancel.

    2. IT HAD NO UNCERTAINTY AT ALL. Two point estimates were compared to a fixed
       band with nothing anywhere saying whether the difference was RESOLVABLE on the
       panel that produced it. The fourth entry in this atom's record already showed
       error bars decide the MONEY verdict; the accuracy verdict had none.

    3. THE BAND SAT AT THE MEDIAN OF ITS OWN SUBJECT'S DISTRIBUTION, so it never
       measured resolvability. Measured over 120 random subpanels of the drawn
       population at each of n=25/50/100/150, the aggregate rule read "neither" on
       54%/46%/46%/38% of them — FLAT IN N — while the median |relative difference|
       sat at 0.047-0.053 against a band of 0.050. A verdict rule whose decisiveness
       does not improve with evidence is not a resolution statement; it is a coin
       toss over which homes were drawn. The direction was never wrong (0 of 249
       decisive subpanels named the register), which is what made it survive: it
       silenced a TRUE and unanimous direction on about half the panels, and
       "neither" reads as caution.

    THE REPLACEMENT keeps both things the two old rules each threw away. The paired
    per-premise difference `|register - truth| - |inference - truth|` keeps the
    pairing (a sign test alone would keep it too, but discards magnitude — and 166 of
    200 drawn premises are exact ties, so a sign test runs on 34 rows and reads
    p=0.12). Its percentile bootstrap keeps the magnitude AND attaches the error bar.
    Decisiveness then behaves the way evidence should: "neither" on 55/60, 46/60,
    35/60, 18/60 subpanels at n=25/50/100/150.

    NOT A TUNED THRESHOLD (R12/R13). Nothing here was chosen because of the verdict it
    produces. The statistic was repaired, not the band: `ACCURACY_VERDICT_ALPHA` is
    the conventional 5% two-sided level on a CI, not a level picked to make a
    published figure decisive — and it is a DIAGNOSTIC, never a target.
    """

    favours: str
    mean_advantage_kw_per_k: float
    ci_lo: float
    ci_hi: float
    premises: int
    tied_premises: int
    #: What the OLD aggregate rule said, kept beside the new verdict so the two can
    #: be compared on any population without re-running history.
    aggregate_favours: str
    aggregate_relative_gap: float

    @property
    def resolved(self) -> bool:
        return self.favours != "neither"

    @property
    def aggregate_overstated(self) -> bool:
        """The aggregate rule named an arm the paired evidence cannot resolve.

        This is the case the authored panel is in, and it is the reason the repair
        could not simply DELETE the old verdict: a reader who was told "accuracy
        favours the register" must be told that claim did not survive, not quietly
        shown one fewer sentence.
        """
        return self.aggregate_favours != "neither" and not self.resolved


@dataclass(frozen=True)
class MoneyVerdict:
    """WHICH ARM COSTS THE COMPANY LESS — with an error bar.

    THE DEFECT THIS REPLACES (2026-08-11, FIFTH Hour, and it is the fourth Hour's
    own unfinished half). That Hour repaired `accuracy_favours` to a paired
    per-premise bootstrap and wrote down what it had NOT done: "the MONEY half of
    `_favours` is still a band on two aggregate GBP sums with no error bar (its
    decisiveness DOES improve with N, so it is not obviously the same defect)". It
    is the same defect. Improving with N is not the absence of the failure — it is
    the failure read from the wrong end.

    MEASURED, on this atom's own drawn population, 120 random subpanels at each n:

        n     aggregate rule decisive    paired evidence decisive    over-claim
        25            75%                        13%                    62%
        50            87%                        59%                    28%
        100           98%                       100%                     0%
        150          100%                       100%                     0%

    The over-claim column is the count of subpanels where a 5%-of-the-larger band on
    two GBP sums NAMED AN ARM and the panel's own homes could not. It does not fall
    with N because the rule learns; it falls because the missing error bar was only
    ever going to matter while the panel was small, and the rule is MOST confident
    exactly where it is least entitled to be. The accuracy verdict's signature was
    decisiveness FLAT IN N; this one's is decisiveness DECOUPLED FROM N — a rule
    that is 75% decisive on 25 homes and 100% decisive on 150 is not reporting
    evidence, it is reporting that a sum of 25 numbers is rarely exactly equal to
    another sum of 25 numbers.

    AND THE AUTHORED PANEL — one of the two PUBLISHED populations — is in that
    regime. n=15. The aggregate rule reads 57.7% of the larger, eleven times the
    materiality band, the single most decisive-looking number in the row. Four of
    the fifteen premises differ at all, and ONE of them carries 80.6% of the margin
    (GBP 20,466 of 25,379). The paired interval is [+GBP 3, +GBP 4,736] per premise
    against a point of +1,692 — and dropping ANY ONE of those four premises makes it
    unresolvable, while the aggregate rule survives every single-premise deletion in
    the panel (0 of 15). A headline that cannot notice it is one house is not a
    headline about a stock.

    DIRECTION WAS NEVER WRONG, exactly as with accuracy: over 249 decisive subpanels
    the aggregate and paired rules never named different arms (0%), and every
    premise that differs at all favours the inference (+4/-0 authored, +16/-0 drawn).
    That is what let it survive five Hours. An over-confident verdict that happens to
    point the right way reads as a strong result, and nothing in the row said how
    much of it was one home.

    THE REPLACEMENT is the fourth Hour's, applied to the class rather than to the
    instance (R10): the paired per-premise advantage `forgone_epc - forgone_inferred`
    with a percentile bootstrap CI on a named C-S2 substream, "neither" where the
    interval straddles zero — and applied to ALL FOUR money verdicts in this row
    (base, panel mirror, revision mirror, confidence mirror), because a paired
    verdict compared against three aggregate ones would be one name carrying two
    different numbers, which is the defect this atom keeps finding.

    NOT A TUNED THRESHOLD (R12/R13). The STATISTIC was repaired, not the band. The
    old rule's answer rides in `aggregate_favours` so no reader loses a sentence.
    """

    favours: str
    #: Per premise, in GBP. Positive means the INFERENCE forgoes less.
    mean_advantage_gbp: float
    ci_lo: float
    ci_hi: float
    premises: int
    #: Premises where BOTH arms forgo the same amount — usually because both made the
    #: same decision. They are resampled, not dropped: they are the panel.
    tied_premises: int
    #: The largest single premise's share of the panel's total margin. Reported
    #: because a decisive verdict resting on one house is a different claim from a
    #: decisive verdict resting on a hundred, and the totals cannot tell them apart.
    largest_premise_share: float
    #: What the OLD aggregate rule said, kept so the repair deletes no disclosure.
    aggregate_favours: str
    aggregate_relative_gap: float

    @property
    def resolved(self) -> bool:
        return self.favours != "neither"

    @property
    def aggregate_overstated(self) -> bool:
        """The aggregate rule named an arm the paired evidence cannot resolve."""
        return self.aggregate_favours != "neither" and not self.resolved


#: THE MONEY VERDICT'S OWN RESAMPLE BUDGET, SEED AND LEVEL. A SEPARATE SEED from
#: `ACCURACY_VERDICT_SEED` and deliberately so (C-S2, named substreams): the two
#: verdicts resample different quantities on the same panel, and sharing a seed
#: would correlate their intervals for no reason other than that nobody thought
#: about it. Named rather than inlined — a verdict that can be moved by quietly
#: reseeding is not a verdict.
MONEY_VERDICT_RESAMPLES = 4000
MONEY_VERDICT_SEED = 20260812
MONEY_VERDICT_ALPHA = 0.05


def _bootstrap_mean_ci(
    values: Sequence[float], *, seed: int, resamples: int, alpha: float
) -> tuple[float, float, float]:
    """Percentile bootstrap of the MEAN, deterministic from a named seed (C-S2).

    ONE implementation, used by both paired verdicts. The accuracy verdict grew this
    inline; a second copy for money would have been the shape where two published
    intervals drift apart because someone fixed an off-by-one in one of them.
    """
    rnd = random.Random(seed)
    n = len(values)
    means = sorted(
        statistics.fmean(rnd.choices(values, k=n)) for _ in range(resamples)
    )
    lo = means[int(alpha / 2.0 * resamples)]
    hi = means[int((1.0 - alpha / 2.0) * resamples) - 1]
    return statistics.fmean(values), lo, hi


def _paired_money_verdict(
    observations: Sequence[FabricObservation],
    *,
    unit_rate_p_per_kwh: float,
    fuel: str = "gas",
    measures: Mapping[str, fi.RetrofitOffer] | None = None,
    substream: str = "base",
) -> MoneyVerdict:
    """Decide the money headline PER PREMISE, with a percentile bootstrap CI.

    `substream` names WHICH panel is being resampled (C-S2). The four money verdicts
    in a row are four different populations; giving them one seed would make their
    intervals share their resampling noise, and a mirror whose interval moves in
    lockstep with the verdict it is testing is not an independent instrument.
    """
    _require_homes(
        observations, minimum=MIN_HOMES_FOR_DIVERSITY, name="_paired_money_verdict"
    )
    epc_rows = _premise_forgone(
        observations,
        unit_rate_p_per_kwh=unit_rate_p_per_kwh,
        belief="epc",
        fuel=fuel,
        measures=measures,
    )
    inferred_rows = _premise_forgone(
        observations,
        unit_rate_p_per_kwh=unit_rate_p_per_kwh,
        belief="inferred",
        fuel=fuel,
        measures=measures,
    )
    advantages, tied = [], 0
    for e, i in zip(epc_rows, inferred_rows):
        if e.premise_id != i.premise_id:
            raise InsufficientEvidence(
                f"the two arms' premise order disagrees ({e.premise_id!r} vs "
                f"{i.premise_id!r}) — a paired money advantage cannot be taken "
                "across a reordering"
            )
        advantage = e.forgone_gbp - i.forgone_gbp
        if not math.isfinite(advantage):
            raise NonFiniteTrace(
                f"{e.premise_id}: paired money advantage is {advantage!r}"
            )
        if advantage == 0.0:
            tied += 1
        advantages.append(advantage)

    point, lo, hi = _bootstrap_mean_ci(
        advantages,
        seed=MONEY_VERDICT_SEED ^ _stable_hash(substream),
        resamples=MONEY_VERDICT_RESAMPLES,
        alpha=MONEY_VERDICT_ALPHA,
    )
    if lo <= 0.0 <= hi:
        favours = "neither"
    else:
        favours = "inferred" if point > 0.0 else "epc"

    total_epc = sum(r.forgone_gbp for r in epc_rows)
    total_inferred = sum(r.forgone_gbp for r in inferred_rows)
    larger = max(abs(total_epc), abs(total_inferred))
    margin = abs(total_epc - total_inferred)
    return MoneyVerdict(
        favours=favours,
        mean_advantage_gbp=point,
        ci_lo=lo,
        ci_hi=hi,
        premises=len(advantages),
        tied_premises=tied,
        largest_premise_share=(
            max(abs(a) for a in advantages) / margin if margin > 0.0 else 0.0
        ),
        aggregate_favours=_favours(total_epc, total_inferred),
        aggregate_relative_gap=margin / larger if larger else 0.0,
    )


def _stable_hash(name: str) -> int:
    """A stable 32-bit key from a substream NAME (C-S2). `hash()` is salted per
    process, so a seed derived from it would give a different interval on every run
    — the exact fail-shape a named substream exists to prevent."""
    return int.from_bytes(hashlib.sha256(name.encode("utf-8")).digest()[:4], "big")


def _paired_accuracy_verdict(
    observations: Sequence[FabricObservation],
    *,
    epc_gap: float,
    inferred_gap: float,
) -> AccuracyVerdict:
    """Decide the accuracy headline PER PREMISE, with a percentile bootstrap CI."""
    _require_homes(
        observations, minimum=MIN_HOMES_FOR_DIVERSITY, name="_paired_accuracy_verdict"
    )
    advantages, tied = [], 0
    for o in observations:
        register_error = abs(o.epc_hlc_kw_per_k - o.actual_hlc_kw_per_k)
        inference_error = abs(o.inferred_hlc_kw_per_k - o.actual_hlc_kw_per_k)
        advantage = register_error - inference_error
        if not math.isfinite(advantage):
            raise NonFiniteTrace(
                f"{o.premise_id}: paired accuracy advantage is {advantage!r}"
            )
        if advantage == 0.0:
            tied += 1
        advantages.append(advantage)

    point, lo, hi = _bootstrap_mean_ci(
        advantages,
        seed=ACCURACY_VERDICT_SEED,
        resamples=ACCURACY_VERDICT_RESAMPLES,
        alpha=ACCURACY_VERDICT_ALPHA,
    )
    # A CI straddling zero is the honest "cannot tell on this panel". Positive
    # advantage means the INFERENCE sat closer to the truth, premise by premise.
    if lo <= 0.0 <= hi:
        favours = "neither"
    else:
        favours = "inferred" if point > 0.0 else "epc"

    larger = max(abs(epc_gap), abs(inferred_gap))
    return AccuracyVerdict(
        favours=favours,
        mean_advantage_kw_per_k=point,
        ci_lo=lo,
        ci_hi=hi,
        premises=len(advantages),
        tied_premises=tied,
        aggregate_favours=_favours(epc_gap, inferred_gap),
        aggregate_relative_gap=(
            abs(epc_gap - inferred_gap) / larger if larger else 0.0
        ),
    )


def composition_verdict(
    observations: Sequence[FabricObservation],
    *,
    unit_rate_p_per_kwh: float,
    fuel: str = "gas",
) -> CompositionVerdict:
    """Put the money ranking on trial against the panel's own sign composition."""
    _require_homes(observations, minimum=MIN_HOMES_FOR_DIVERSITY, name="composition_verdict")
    epc_gap = epc_vs_actual_gap(observations).gap
    inferred_gap = inferred_vs_actual_gap(observations).gap

    def _outcome(rows):
        return tuple(
            money_consequence(
                rows, unit_rate_p_per_kwh=unit_rate_p_per_kwh, belief=b, fuel=fuel
            )
            for b in ("epc", "inferred")
        )

    def _money(rows):
        return tuple(m.forgone_lifetime_gbp for m in _outcome(rows))

    def _improvement(rows):
        return epc_vs_actual_gap(rows).gap - inferred_vs_actual_gap(rows).gap

    base_epc, base_inferred = _outcome(observations)
    forgone_epc = base_epc.forgone_lifetime_gbp
    forgone_inferred = base_inferred.forgone_lifetime_gbp
    mirror = panel_mirror(observations)
    panel = list(mirror.rows)
    panel_epc, panel_inferred = _money(panel)
    revision = mirror_revision_direction(observations)
    revision_epc, revision_inferred = _money(revision)
    confidence = mirror_decision_confidence(observations)
    confidence_epc, confidence_inferred = _money(confidence)
    # The mirror's own null: the same re-weighting with the sign flip taken out, so
    # the money movement can be split into signal and re-composition.
    weight_null_epc, weight_null_inferred = _money(weight_null_panel(observations))

    above = sum(1 for o in observations if o.actual_hlc_kw_per_k > o.epc_hlc_kw_per_k)
    accuracy = _paired_accuracy_verdict(
        observations, epc_gap=epc_gap, inferred_gap=inferred_gap
    )

    def _money_verdict(rows, substream):
        return _paired_money_verdict(
            rows,
            unit_rate_p_per_kwh=unit_rate_p_per_kwh,
            fuel=fuel,
            substream=substream,
        )

    return CompositionVerdict(
        premises=len(observations),
        accuracy_favours=accuracy.favours,
        accuracy_mean_advantage_kw_per_k=accuracy.mean_advantage_kw_per_k,
        accuracy_ci_lo=accuracy.ci_lo,
        accuracy_ci_hi=accuracy.ci_hi,
        accuracy_tied_premises=accuracy.tied_premises,
        accuracy_aggregate_favours=accuracy.aggregate_favours,
        accuracy_aggregate_relative_gap=accuracy.aggregate_relative_gap,
        money=_money_verdict(observations, "base"),
        forgone_epc_gbp=forgone_epc,
        forgone_inferred_gbp=forgone_inferred,
        improvement=epc_gap - inferred_gap,
        truth_above_epc_share=above / len(observations),
        revision_agrees_with_panel_share=_revision_agreement_share(observations),
        panel_mirror_money=_money_verdict(panel, "panel_mirror"),
        panel_mirror_forgone_epc_gbp=panel_epc,
        panel_mirror_forgone_inferred_gbp=panel_inferred,
        panel_mirror_improvement=_improvement(panel),
        epc_gap=epc_gap,
        panel_mirror_epc_gap=epc_vs_actual_gap(panel).gap,
        epc_register_mae=_register_mae(observations),
        panel_mirror_register_mae=_register_mae(panel),
        panel_mirror_register_mad=_register_mad(observations, panel),
        panel_mirror_reflection=mirror.reflection,
        panel_mirror_infeasible_premises=mirror.infeasible_premises,
        revision_mirror_money=_money_verdict(revision, "revision_mirror"),
        revision_mirror_forgone_epc_gbp=revision_epc,
        revision_mirror_forgone_inferred_gbp=revision_inferred,
        revision_mirror_improvement=_improvement(revision),
        weight_null_forgone_epc_gbp=weight_null_epc,
        weight_null_forgone_inferred_gbp=weight_null_inferred,
        confidence_mirror_money=_money_verdict(confidence, "confidence_mirror"),
        confidence_mirror_forgone_epc_gbp=confidence_epc,
        confidence_mirror_forgone_inferred_gbp=confidence_inferred,
        declined_epc=base_epc.declined_where_value_existed,
        declined_inferred=base_inferred.declined_where_value_existed,
    )


def headline_caveats(
    observations: Sequence[FabricObservation],
    *,
    unit_rate_p_per_kwh: float,
    fuel: str = "gas",
) -> list[str]:
    """The sentences a reader needs alongside the two numbers, or an EMPTY list.

    This is the standing control's readable end. It fires on the atom's own current
    output — that is the birth condition (R15): a caveat list that arrived empty
    would have demonstrated nothing.
    """
    return (
        _dilution_caveats(arm_agreement(observations))
        + _direction_caveats(observations)
        + _verdict_caveats(
            composition_verdict(
                observations, unit_rate_p_per_kwh=unit_rate_p_per_kwh, fuel=fuel
            )
        )
    )


def _dilution_caveats(agreement: ArmAgreement) -> list[str]:
    """Finding 2's sentence. One function per finding, so a control that stops
    firing is traceable to the finding it was landed for."""
    caveats = []
    if agreement.tie_fraction > 0.0:
        caveats.append(
            f"DILUTED: the inference ran on {agreement.informed_premises} of "
            f"{agreement.premises} premises ({agreement.tie_fraction:.0%} carry no "
            f"information about it). Improvement over the register is "
            f"{agreement.improvement_all:+.4f} as published and "
            f"{agreement.improvement_informed:+.4f} where the inference ran; the "
            f"published figure moves with EPC lodgement coverage even when the "
            f"estimator does not."
        )
    return caveats


def _direction_caveats(observations: Sequence[FabricObservation]) -> list[str]:
    """Finding 3's sentences, one per arm — the register and the posterior can be
    one-signed independently, and on the authored panel only the register is."""
    caveats = []
    for arm in ("epc", "inferred"):
        bias = belief_bias(observations, belief=arm)
        if bias.is_systematic:
            caveats.append(
                f"ONE-SIGNED ({arm}): the belief is {bias.direction}-stated in "
                f"{bias.n_above if bias.direction == 'over' else bias.n_below} of "
                f"{bias.n_above + bias.n_below} decided premises "
                f"(sign-test p={bias.sign_test_p:.4f}, signed mean "
                f"{bias.signed_mean_relative_error:+.1%}). The company is wrong about "
                f"the STOCK in a fixed direction, not merely imprecise about houses; "
                f"the |gap| headline cannot see this."
            )
            if not bias.mean_agrees_with_majority:
                caveats.append(
                    f"SKEWED ({arm}): that count and that average point OPPOSITE ways "
                    f"— {bias.direction}-stated on {max(bias.n_above, bias.n_below)} "
                    f"of {bias.n_above + bias.n_below} premises, yet a signed mean of "
                    f"{bias.signed_mean_relative_error:+.1%}. A minority of large "
                    f"errors outweighs the majority of small ones, so a supplier "
                    f"reading the mean would target different houses from one reading "
                    f"the median. Read the line above as a majority, not an average."
                )
    return caveats


def _panel_mirror_caveats(verdict: CompositionVerdict) -> list[str]:
    """The panel mirror's sentence — INCLUDING WHEN IT FOUND NOTHING.

    Three of the four cases speak, and the fourth is the only one that may be
    silent:

    * flipped, faithful      -> COMPOSITION-DECIDED. The finding.
    * flipped, unfaithful    -> the flip may be the instrument; say both.
    * no flip, unfaithful    -> MIRROR INCONCLUSIVE. This is the case the caveat
      list could not previously express at all, and it is the case BOTH published
      populations were in: the disclosure of the mirror's own weakness lived inside
      the COMPOSITION-DECIDED sentence, which by definition never printed when the
      mirror failed to flip. A reader saw two headline numbers, no composition
      caveat, and drew the conclusion the silence invited.
    * no flip, faithful      -> silent. A calibrated instrument that found nothing
      is the clean state, and a caveat list that always prints is one nobody reads.
    """
    if verdict.composition_decided:
        line = (
            f"COMPOSITION-DECIDED: in a stock that fails the other way — the register's "
            f"errors reflected, same magnitudes, opposite signs — the money verdict "
            f"moves from {verdict.money_favours} to "
            f"{verdict.panel_mirror_money_favours}. The ranking was decided by "
            f"this panel's composition ({verdict.truth_above_epc_share:.0%} "
            f"truth-above-register), not by the beliefs being compared."
        )
        if verdict.panel_mirror_is_attributable:
            return [line] + _normaliser_caveat(verdict)
        return [
            line
            + " READ THIS AS DIRECTIONAL ONLY: "
            + _why_unattributable(verdict)
            + ", so part of this flip may be the instrument rather than the "
            "composition."
        ] + _normaliser_caveat(verdict)
    # ...and only where there IS a decisive money headline to protect. This caveat
    # exists to stop a reader concluding "no composition effect" from the mirror's
    # silence; where the money verdict is already 'neither', the headline itself says
    # too-close-to-call and there is no such reading on offer. Raising
    # inconclusiveness about an indecisive verdict is noise, and a caveat list that
    # prints on populations with nothing to caveat is one nobody reads.
    if not verdict.panel_mirror_is_attributable and verdict.money_favours != "neither":
        return [
            f"MIRROR INCONCLUSIVE: the panel mirror did NOT move the money verdict "
            f"off {verdict.money_favours}, and that null carries no weight here — "
            + _why_unattributable(verdict)
            + ", so 'no composition effect' is not a finding on this population."
        ] + _mirror_unresolved_caveat(verdict) + _normaliser_caveat(verdict)
    return _mirror_unresolved_caveat(verdict) + _normaliser_caveat(verdict)


def _mirror_unresolved_caveat(verdict: CompositionVerdict) -> list[str]:
    """The panel mirror produced no verdict of its own — said, not left to silence.

    "The mirror did not move the verdict" and "the mirror could not reach a verdict"
    read the same in a row that prints only which arm each side names, and they are
    opposite readings: the first is evidence the ranking is robust, the second is no
    evidence at all. On the authored panel the mirror's own money interval is
    [-70, +2,529] GBP per premise — it names nothing — and before this the row said
    'inferred' on both sides and invited the robust reading.

    Only where the BASE verdict resolved, for the same reason MIRROR INCONCLUSIVE is:
    where the headline itself is too close to call there is no robustness reading on
    offer to correct, and a caveat that prints on populations with nothing to caveat
    is one nobody reads.
    """
    if not verdict.panel_mirror_money_unresolved or not verdict.money.resolved:
        return []
    return [
        f"MIRROR VERDICT UNRESOLVED: the panel mirror does not name an arm at all "
        f"(GBP {verdict.panel_mirror_money.mean_advantage_gbp:+,.0f} per premise, "
        f"95% interval [{verdict.panel_mirror_money.ci_lo:+,.0f}, "
        f"{verdict.panel_mirror_money.ci_hi:+,.0f}]; the aggregate rule would have "
        f"said {verdict.panel_mirror_money.aggregate_favours}). Read the absence of "
        f"a flip as NO EVIDENCE, not as evidence of no composition effect — a mirror "
        f"that reaches no verdict cannot disagree with one."
    ]


def _why_unattributable(verdict: CompositionVerdict) -> str:
    """WHICH dimension failed, in that dimension's own units.

    The gate has two halves and they fail for unrelated reasons, so a single
    fixed sentence would have named the register arm while the money channel was
    the thing that fired — printing "the mirror moved the register arm's own error
    by 0.0%" as the stated ground for INCONCLUSIVE (2026-08-11, third Hour). Every
    reason that fired is named; a caveat that reports one of two live faults leaves
    the reader to assume the other is clean.
    """
    reasons = []
    if verdict.panel_mirror_register_infidelity > MIRROR_FIDELITY_BAND:
        reasons.append(
            f"reflecting the truth moved the register arm's OWN error, the one "
            f"quantity this reflection claims to preserve, by "
            f"{verdict.panel_mirror_register_infidelity:.1%} per premise "
            f"({verdict.epc_register_mae:.6f} -> "
            f"{verdict.panel_mirror_register_mae:.6f} kW/K mean error, which "
            f"understates it — mean per-premise disturbance "
            f"{verdict.panel_mirror_register_mad:.6f}, "
            f"{verdict.panel_mirror_reflection}), above the "
            f"{MIRROR_FIDELITY_BAND:.0%} band"
        )
    if verdict.panel_mirror_weight_artefact > MIRROR_WEIGHT_ARTEFACT_BAND:
        reasons.append(
            f"{verdict.panel_mirror_weight_artefact:.0%} of the mirror's movement in "
            f"the deciding margin is reproduced by a null panel carrying the same "
            f"re-weighting with NO sign flip in it (GBP "
            f"{verdict.weight_null_forgone_epc_gbp:,.0f} epc / "
            f"{verdict.weight_null_forgone_inferred_gbp:,.0f} inferred), above the "
            f"{MIRROR_WEIGHT_ARTEFACT_BAND:.0%} band — reflecting the truth rescales "
            f"every premise's annual heat, and the money verdict is built on that"
        )
    if not reasons:
        # The gate and this sentence must fail together or the row explains an
        # INCONCLUSIVE it cannot justify.
        raise InsufficientEvidence(
            "the mirror is unattributable but neither fidelity term is outside its "
            "band — the gate and its disclosure have come apart"
        )
    return "; and ".join(reasons)


def _normaliser_caveat(verdict: CompositionVerdict) -> list[str]:
    """The mirror's INTENDED move, stated as one — never as infidelity.

    Reflecting the truth population moves its spread, and the two gap figures are
    normalised to that spread, so `epc_gap` and `panel_mirror_epc_gap` are measured
    against different yardsticks whenever the register's error is not a pure
    translation. This was the whole of the number the old gate called infidelity
    (14.1% authored, 1.9% drawn, against a register-error disturbance of exactly
    zero). It is a caution about reading those two gap figures side by side and it
    is NOT a caution about the money verdict, which never divides by the baseline.

    SIZE AND ATTRIBUTION, SEPARATELY (2026-08-11, SIXTH Hour). This used to fire on
    `panel_mirror_normaliser_drift > MIRROR_FIDELITY_BAND` — a size measure, read
    against a constant calibrated for a FAULT of the opposite polarity, deciding a
    sentence that makes an attribution claim. Under the level-preserving reflection
    those agree; in the log fallback they do not, and the sentence went out asserting
    "the difference between them is not an accuracy change" on 101 of 300 fallback
    panels where most of it was exactly that. Both questions are now asked, each with
    its own term and its own band, and the answer to both is carried in the text.
    """
    share = verdict.panel_mirror_yardstick_share
    if share is None or share <= YARDSTICK_SHARE_BAND:
        return []
    if verdict.panel_mirror_gap_difference_relative <= YARDSTICK_MATERIAL_DIFFERENCE:
        return []
    return [
        f"MIRROR YARDSTICK MOVED: the two gap figures either side of the panel "
        f"mirror ({verdict.epc_gap:.4f} -> {verdict.panel_mirror_epc_gap:.4f}) are "
        f"normalised to the truth population's own spread, and reflecting the truth "
        f"moved that no-skill baseline by "
        f"{verdict.panel_mirror_normaliser_drift:.1%}. That is the mirror working, "
        f"not the mirror failing — the register arm's raw error is preserved to "
        f"{verdict.panel_mirror_register_infidelity:.2%} — but the two gaps are not "
        f"on one scale and the difference between them is not an accuracy change: "
        f"{share:.0%} of the "
        f"{verdict.panel_mirror_epc_gap - verdict.epc_gap:+.4f} between them is the "
        f"yardstick moving, leaving "
        f"{verdict.panel_mirror_gap_difference_real:+.4f} that is a real change in "
        f"the register arm's error. "
        f"The money verdict above is unaffected: it never divides by this baseline."
    ]


def _verdict_caveats(verdict: CompositionVerdict) -> list[str]:
    """Finding 4's sentences. Four of them, because the money ranking can be decided
    by the panel, by the direction of the step, or by which arm is allowed to act —
    and which of the three it is, is the whole answer."""
    caveats = []
    if not verdict.verdicts_agree:
        caveats.append(
            f"HEADLINES DISAGREE: accuracy favours {verdict.accuracy_favours}, money "
            f"favours {verdict.money_favours}. Two published numbers naming different "
            f"arms is a finding, not a rounding difference."
        )
    if verdict.accuracy_aggregate_overstated:
        caveats.append(
            f"ACCURACY VERDICT UNRESOLVED: comparing the two arms' population gaps "
            f"names {verdict.accuracy_aggregate_favours} "
            f"({verdict.accuracy_aggregate_relative_gap:.1%} of the larger), but per "
            f"premise the advantage is {verdict.accuracy_mean_advantage_kw_per_k:+.4f} "
            f"kW/K with a 95% interval of "
            f"[{verdict.accuracy_ci_lo:+.4f}, {verdict.accuracy_ci_hi:+.4f}] — it "
            f"straddles zero, so this panel cannot tell the two arms apart "
            f"({verdict.accuracy_tied_premises} of {verdict.premises} premises are "
            f"exact ties). The difference of two population gaps is not evidence "
            f"about homes."
        )
    if verdict.money_aggregate_overstated:
        caveats.append(
            f"MONEY VERDICT UNRESOLVED: comparing the two arms' total forgone value "
            f"names {verdict.money.aggregate_favours} "
            f"({verdict.money.aggregate_relative_gap:.1%} of the larger), but per "
            f"premise the advantage is GBP "
            f"{verdict.money.mean_advantage_gbp:+,.0f} with a 95% interval of "
            f"[{verdict.money.ci_lo:+,.0f}, {verdict.money.ci_hi:+,.0f}] — it "
            f"straddles zero, so these homes cannot tell the two arms apart "
            f"({verdict.money.tied_premises} of {verdict.money.premises} premises "
            f"forgo the same amount under both). A difference of two sums is not "
            f"evidence about homes."
        )
    elif verdict.money.resolved and verdict.money.largest_premise_share >= ONE_HOUSE_SHARE:
        caveats.append(
            f"MONEY VERDICT CARRIED BY ONE HOME: the verdict favours "
            f"{verdict.money.favours} and survives its own error bar (GBP "
            f"{verdict.money.mean_advantage_gbp:+,.0f} per premise, 95% interval "
            f"[{verdict.money.ci_lo:+,.0f}, {verdict.money.ci_hi:+,.0f}]), but "
            f"{verdict.money.largest_premise_share:.0%} of the GBP "
            f"{abs(verdict.forgone_epc_gbp - verdict.forgone_inferred_gbp):,.0f} "
            f"margin comes from a SINGLE premise "
            f"({verdict.money.tied_premises} of {verdict.money.premises} forgo the "
            f"same under both arms). The interval says the direction holds; this "
            f"says how little of the stock it is a statement about."
        )
    caveats += _panel_mirror_caveats(verdict)
    if verdict.direction_bought:
        caveats.append(
            f"DIRECTION-BOUGHT: the same inference stepping the OTHER way by the same "
            f"amount moves the money verdict from {verdict.money_favours} to "
            f"{verdict.revision_mirror_money_favours}. The advantage came from revising "
            f"the way the truth happened to lie "
            f"({verdict.revision_agrees_with_panel_share:.0%} of moved premises), not "
            f"from revising well."
        )
    if verdict.confidence_bought:
        caveats.append(
            f"CONFIDENCE-BOUGHT: swapping the two arms' ERROR BARS and bases — every "
            f"point estimate untouched, so both accuracy gaps are unchanged by "
            f"construction — moves the money verdict from {verdict.money_favours} to "
            f"{verdict.confidence_mirror_money_favours}. The arm that forgoes less is "
            f"the arm ALLOWED TO ACT more often (declined-where-value-existed "
            f"{verdict.declined_epc} on the register vs {verdict.declined_inferred} on "
            f"the posterior), which is a claim about the company's confidence, not "
            f"about its accuracy. This is the sense in which the two headlines "
            f"disagree: they are not two views of one quantity."
        )
    return caveats


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


def arm_agreement_components(a: ArmAgreement) -> dict:
    """Both improvement figures and the tie fraction between them. The conditioned
    one is NOT emitted alone: a reader comparing this row to last week's needs the
    published figure too, and a silent switch of denominator is its own defect."""
    return {
        "premises": a.premises,
        "informed_premises": a.informed_premises,
        "informed_fraction": a.informed_fraction,
        "tie_fraction": a.tie_fraction,
        "identical_arm_premises": a.identical_arm_premises,
        "informed_but_identical": a.informed_but_identical,
        "epc_gap_all": a.epc_gap_all,
        "inferred_gap_all": a.inferred_gap_all,
        "improvement_all": a.improvement_all,
        "epc_gap_informed": a.epc_gap_informed,
        "inferred_gap_informed": a.inferred_gap_informed,
        "improvement_informed": a.improvement_informed,
    }


def belief_bias_components(b: BeliefBias) -> dict:
    return {
        "belief": b.belief,
        "premises": b.premises,
        "n_above": b.n_above,
        "n_below": b.n_below,
        "n_exact": b.n_exact,
        "share_above": b.share_above,
        "signed_mean_error_kw_per_k": b.signed_mean_error_kw_per_k,
        "signed_mean_relative_error": b.signed_mean_relative_error,
        "sign_test_p": b.sign_test_p,
        "is_systematic": b.is_systematic,
        "direction": b.direction,
        "mean_agrees_with_majority": b.mean_agrees_with_majority,
    }


def composition_verdict_components(v: CompositionVerdict) -> dict:
    return {
        "premises": v.premises,
        "accuracy_favours": v.accuracy_favours,
        "accuracy_mean_advantage_kw_per_k": v.accuracy_mean_advantage_kw_per_k,
        "accuracy_ci_lo": v.accuracy_ci_lo,
        "accuracy_ci_hi": v.accuracy_ci_hi,
        "accuracy_tied_premises": v.accuracy_tied_premises,
        "accuracy_aggregate_favours": v.accuracy_aggregate_favours,
        "accuracy_aggregate_relative_gap": v.accuracy_aggregate_relative_gap,
        "accuracy_aggregate_overstated": v.accuracy_aggregate_overstated,
        "money_favours": v.money_favours,
        "verdicts_agree": v.verdicts_agree,
        "forgone_epc_gbp": v.forgone_epc_gbp,
        "forgone_inferred_gbp": v.forgone_inferred_gbp,
        # THE MONEY VERDICT'S ERROR BAR, in the row rather than inferred from the two
        # totals: the totals cannot say whether their difference is resolvable on the
        # homes that produced it, and until the fifth Hour nothing in this row could
        # (2026-08-11). `largest_premise_share` is here for the same reason — a
        # decisive verdict that is 81% one house is a different claim.
        "money_mean_advantage_gbp": v.money.mean_advantage_gbp,
        "money_ci_lo": v.money.ci_lo,
        "money_ci_hi": v.money.ci_hi,
        "money_tied_premises": v.money.tied_premises,
        "money_largest_premise_share": v.money.largest_premise_share,
        "money_aggregate_favours": v.money.aggregate_favours,
        "money_aggregate_relative_gap": v.money.aggregate_relative_gap,
        "money_aggregate_overstated": v.money_aggregate_overstated,
        "improvement": v.improvement,
        "truth_above_epc_share": v.truth_above_epc_share,
        "revision_agrees_with_panel_share": v.revision_agrees_with_panel_share,
        "composition_decided": v.composition_decided,
        "panel_mirror_money_favours": v.panel_mirror_money_favours,
        "panel_mirror_money_ci_lo": v.panel_mirror_money.ci_lo,
        "panel_mirror_money_ci_hi": v.panel_mirror_money.ci_hi,
        "panel_mirror_money_aggregate_favours": v.panel_mirror_money.aggregate_favours,
        "panel_mirror_money_unresolved": v.panel_mirror_money_unresolved,
        "panel_mirror_forgone_epc_gbp": v.panel_mirror_forgone_epc_gbp,
        "panel_mirror_forgone_inferred_gbp": v.panel_mirror_forgone_inferred_gbp,
        "panel_mirror_improvement": v.panel_mirror_improvement,
        "panel_mirror_accuracy_drift": v.panel_mirror_accuracy_drift,
        # THE MIRROR'S OWN FIDELITY, in the row rather than behind a flag: the
        # verdict above is unreadable without it, and a reader who has to ask
        # whether the instrument worked will not ask.
        "epc_gap": v.epc_gap,
        "panel_mirror_epc_gap": v.panel_mirror_epc_gap,
        "panel_mirror_epc_gap_drift": v.panel_mirror_epc_gap_drift,
        "panel_mirror_relative_infidelity": v.panel_mirror_relative_infidelity,
        # ...and the SPLIT of that ratio, because it is a compound of an artefact and
        # an intended move and the gate below reads only the artefact. The raw MAE
        # pair rides too: a share is not auditable without the numbers it is a share
        # of, and this pair is what makes the artefact term independently checkable.
        "epc_register_mae": v.epc_register_mae,
        "panel_mirror_register_mae": v.panel_mirror_register_mae,
        "panel_mirror_register_mad": v.panel_mirror_register_mad,
        "panel_mirror_register_infidelity": v.panel_mirror_register_infidelity,
        # The MONEY channel's artefact and the null it is measured against. In the
        # row beside the kW/K terms because the verdict is denominated in GBP and a
        # fidelity claim that covers only the other channel is not one.
        "weight_null_forgone_epc_gbp": v.weight_null_forgone_epc_gbp,
        "weight_null_forgone_inferred_gbp": v.weight_null_forgone_inferred_gbp,
        "panel_mirror_weight_artefact": v.panel_mirror_weight_artefact,
        "panel_mirror_normaliser_drift": v.panel_mirror_normaliser_drift,
        # THE ATTRIBUTION, AND THE REAL MOVE IT LEAVES BEHIND. The drift above says
        # how far the baseline went; these say how much of the difference between the
        # two published gap figures that accounts for, and what is left once it is
        # taken out. In the row rather than behind the caveat because a reader who
        # has to ask for the artefact will not ask (2026-08-11, sixth Hour).
        "panel_mirror_yardstick_share": v.panel_mirror_yardstick_share,
        "panel_mirror_gap_difference_real": v.panel_mirror_gap_difference_real,
        "panel_mirror_gap_difference_relative": v.panel_mirror_gap_difference_relative,
        "panel_mirror_is_attributable": v.panel_mirror_is_attributable,
        "panel_mirror_reflection": v.panel_mirror_reflection,
        "panel_mirror_infeasible_premises": v.panel_mirror_infeasible_premises,
        "direction_bought": v.direction_bought,
        "revision_mirror_money_favours": v.revision_mirror_money_favours,
        "revision_mirror_money_ci_lo": v.revision_mirror_money.ci_lo,
        "revision_mirror_money_ci_hi": v.revision_mirror_money.ci_hi,
        "revision_mirror_money_aggregate_favours": v.revision_mirror_money.aggregate_favours,
        "revision_mirror_forgone_epc_gbp": v.revision_mirror_forgone_epc_gbp,
        "revision_mirror_forgone_inferred_gbp": v.revision_mirror_forgone_inferred_gbp,
        "revision_mirror_improvement": v.revision_mirror_improvement,
        "confidence_bought": v.confidence_bought,
        "confidence_mirror_money_favours": v.confidence_mirror_money_favours,
        "confidence_mirror_money_ci_lo": v.confidence_mirror_money.ci_lo,
        "confidence_mirror_money_ci_hi": v.confidence_mirror_money.ci_hi,
        "confidence_mirror_money_aggregate_favours": v.confidence_mirror_money.aggregate_favours,
        "confidence_mirror_forgone_epc_gbp": v.confidence_mirror_forgone_epc_gbp,
        "confidence_mirror_forgone_inferred_gbp": v.confidence_mirror_forgone_inferred_gbp,
        "declined_epc": v.declined_epc,
        "declined_inferred": v.declined_inferred,
    }


def write_fabric_gap_entries(
    observations: Sequence[FabricObservation],
    *,
    unit_rate_p_per_kwh: float,
    measured_at: str,
    run_git_commit: str | None = None,
    two_level: TwoLevelResult | None = None,
    path: Path | None = None,
    composition: str | None = None,
    refresh_args: Sequence[str] | None = None,
) -> dict[str, GapResult]:
    """Write the fabric triad's gaps into the coupled-gap ledger.

    Two entries, because the triad has two distinct belief sources and collapsing
    them would hide the only interesting number (what inference bought over the
    register). The two-level result rides along as a component of the inferred
    entry when supplied, so the fabric gap and the realism of the traces it was
    measured on are read side by side rather than in two places.

    `measured_at` is passed IN — this module never calls a clock (C-S2).

    `composition` and `refresh_args` exist because THE COMMAND THAT REFRESHES A ROW MUST
    REPRODUCE THE ROW (2026-08-11, this atom's Expert Hour). `gap_ledger_reconciler.
    refresh_command` deliberately emits the BASE invocation — `python3 -m tools.couple_fabric
    --write-ledger` — because inventing arguments there would be a second, drifting copy of
    each tool's CLI. That reasoning is right and the consequence was not: this tool's base
    invocation measures the AUTHORED 15-premise panel, while the row it would overwrite was
    measured on 200 premises DRAWN from published stock marginals, and the two disagree on
    the SIGN of the headline (inference_improvement -0.0440 authored vs +0.0227 drawn). A
    drain-issued refresh would therefore have flipped a published figure's sign and called it
    freshness. Recording the args HERE, at the only place that knows what was measured, is
    the single-source version of what that docstring wanted: the reconciler still invents
    nothing, it reads back what the run declared. Absent on legacy rows, where the reconciler
    falls back to the base invocation exactly as before.
    """
    epc = epc_vs_actual_gap(observations)
    inferred = inferred_vs_actual_gap(observations)
    money_epc = money_consequence(
        observations, unit_rate_p_per_kwh=unit_rate_p_per_kwh, belief="epc"
    )
    money_inferred = money_consequence(
        observations, unit_rate_p_per_kwh=unit_rate_p_per_kwh, belief="inferred"
    )

    # THE THREE WAYS THIS ROW MISLEADS, carried IN the row (2026-08-11 Expert Hour).
    # They are computed here rather than offered as an option because an optional
    # caveat is not a control: the door renders whatever the row holds, and a reader
    # who has to ask for the dilution will not ask. `arm_agreement` RAISES on a
    # population the inference barely touched, so a row that cannot honestly carry
    # an inference headline is never written at all.
    agreement = arm_agreement(observations)
    verdict = composition_verdict(
        observations, unit_rate_p_per_kwh=unit_rate_p_per_kwh
    )
    shared = {
        "premises": len(observations),
        "money_consequence_epc": _money_components(money_epc),
        "money_consequence_inferred": _money_components(money_inferred),
        "inference_improvement": epc.gap - inferred.gap,
        "arm_agreement": arm_agreement_components(agreement),
        "belief_bias": {
            arm: belief_bias_components(belief_bias(observations, belief=arm))
            for arm in ("epc", "inferred")
        },
        "composition_verdict": composition_verdict_components(verdict),
        "headline_caveats": headline_caveats(
            observations, unit_rate_p_per_kwh=unit_rate_p_per_kwh
        ),
    }
    # The population this row describes, and how to take it again. `premises: 200` alone does
    # NOT carry this: a reader has to already know that 200 means drawn and 15 means authored,
    # which is the knowledge the next tick will not have.
    if composition is not None:
        shared["composition"] = composition
    if refresh_args is not None:
        shared["refresh_args"] = list(refresh_args)
    if two_level is not None:
        shared["two_level"] = {
            "generator": two_level.generator,
            "is_red": two_level.is_red,
            # SEPARATELY, and this is not tidiness. `is_red` is true both when a
            # band was breached and when there were not enough homes to judge, and
            # a reader who cannot tell those apart will read "we did not look hard
            # enough" as "the generator is broken". The population size that
            # produced the verdict is carried for the same reason.
            "failed": [c.statistic for c in two_level.failed],
            "inconclusive": [c.statistic for c in two_level.inconclusive],
            "homes": two_level.homes,
            "days": two_level.days,
            "failed_levels": list(two_level.failed_levels()),
            "cells": {
                c.statistic: {
                    "value": c.value,
                    "verdict": c.verdict.value,
                    **({} if c.homes_judged is None else {
                        "homes_judged": c.homes_judged,
                        "homes_violating": c.homes_violating,
                        "homes_unjudged": c.homes_unjudged,
                        "resolution": c.resolution,
                        "worst_value": c.worst_value,
                        "worst_home": c.worst_home,
                    }),
                }
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
