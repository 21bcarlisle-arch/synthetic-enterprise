"""HDD (heating degree day) model for gas consumption weather-adjustment.

UK standard base temperature 15.5°C (DECC/Ofgem domestic gas standard).
Reference monthly HDD: UK Met Office 1991-2020 climate normals (England & Wales).

THE PREMISE READS ITS OWN CELL (2026-09-21, W1_14 step 3)
---------------------------------------------------------
This leg was the THIRD resolver of "which sky did this household have", and the last one still
answering from a per-property file. `_premise_sky()` below now asks
`simulation.weather_inputs.cell_weather_for_customer_id`, which is `WeatherWorld.cell_id_for` --
the one rule the fabric leg (2026-09-17) and the demand-shape/forward-price legs (2026-09-21)
already resolve by. 16 of the book's 18 premises hold a cell; the two that do not (C_IC1, C_IC2,
7.4 km outside the store) still get `REFERENCE_MONTHLY_HDD`, and `hdd_reading()` NAMES that
substitution in what it returns rather than handing back a climatological number that reads like
weather.

THIS IS NOT AN EQUIVALENCE. Measured annual HDD over the whole book moves on 16 of 18 premises,
-2.5% to -34.5% (2018 and 2022), for two reasons that must not be confused: the ten premises that
were on the normal now see weather at all, and the eight that were on an ERA5 ~9 km archive now
read HadUK-Grid 1 km, which is ~1.2 C warmer at an urban cell. An R13 fidelity decision, taken
blind to what it does to company results. Full before/after in
`docs/staging/WORKER_RESULT_THE_HDD_LEG_READS_THE_WORLDS_OWN_CELLS_NOW_2026-09-21.md`.

Cumulative/rolling HDD windows (thermal memory), added 2026-08-03
------------------------------------------------------------------
`get_hdd()` below is memoryless: HDD(D) depends only on D's own mean
temperature. Real gas demand does not work this way -- building thermal mass
means a cold snap's third day draws more gas than its first day at an
identical temperature, and (at system level) storage/linepack drawdown
behaves the same way. `get_cumulative_hdd()` (bottom of this module) adds a
decay-weighted rolling HDD signal to capture this, additively -- every
existing function/signature above is untouched.

CITED source for the decay shape (NOT fabricated -- full citation and fetch
note in `docs/market_research/gas_demand_cumulative_hdd_cwv.md`): National Grid
plc, "Gas Demand Forecasting Methodology" (2020, v1), Appendix 1.1. The
document defines an "Effective Temperature" used throughout GB gas demand
forecasting as
    Et = 0.5 * Et-1 + 0.5 * ATt
i.e. today's actual temperature and *all* prior days folded in with weight
halving once per day back ("Effective temperature takes into account the
previous day's temperature due to consumer behaviour and perception of the
weather" -- p.11). `get_cumulative_hdd()` reuses that halving-per-day decay
shape but is an ENGINEERING ADAPTATION, not a literal reimplementation of
National Grid's formula: (a) it is applied directly to daily HDD rather than
to raw temperature (HDD is already the monotonic-under-clip transform this
module uses elsewhere), and (b) the true recursion is infinite-lookback,
truncated here to a finite, testable window (see `HDD_WINDOW_DAYS` below).
Both adaptations are engineering choices, flagged as such, not attributed to
the cited source.
"""
from __future__ import annotations

import math
from calendar import monthrange
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Mapping

HDD_BASE_TEMP_C = 15.5

# UK 1991-2020 HDD climate normals (base 15.5°C, England & Wales).
# Sourced from Met Office HDD/CDD tabulations and Ofgem annual consumption data.
REFERENCE_MONTHLY_HDD: dict[int, float] = {
    1: 350.0,
    2: 315.0,
    3: 275.0,
    4: 200.0,
    5: 118.0,
    6:  30.0,
    7:   5.0,
    8:   5.0,
    9:  38.0,
    10: 140.0,
    11: 249.0,
    12: 341.0,
}

#: Opening words of the basis an `HddReading` carries when it could NOT read the premise's own
#: weather and fell back to `REFERENCE_MONTHLY_HDD`. A caller asking "is this weather?" asks
#: `HddReading.from_normal`; this prefix is for the reader of a printed record, and it is a
#: constant so the two can never drift apart.
NORMAL_BASIS_PREFIX = "1991-2020 England & Wales monthly normal"


@dataclass(frozen=True)
class PremiseSky:
    """One premise's daily mean-temperature series, the cell it came from, and why there is none.

    THE REFUSAL TRAVELS WITH THE SERIES, for the same reason it does in
    `simulation.weather_inputs.CellWeather`: without it, "this cell's January was mild" and "this
    premise has no weather at all" both arrive here as a number in the right range, and the second
    one settles.
    """

    customer_id: str
    cell: str | None = None
    series: Mapping[str, float] = field(default_factory=dict)
    refusal: str | None = None


@dataclass(frozen=True)
class HddReading:
    """A day's HDD and WHAT IT WAS READ FROM -- a cell of the world, or a climate normal."""

    hdd: float
    basis: str
    from_normal: bool


#: Resolved skies by customer_id. Also the injection door for controls that need an exact
#: temperature (`PremiseSky("X", cell="fixture", series={...})`) -- seeding it is what keeps them
#: independent of which 1 km cell the store happens to hold.
_WEATHER_CACHE: dict[str, PremiseSky] = {}


def _premise_sky(customer_id: str) -> PremiseSky:
    """The premise's sky, from the PER-CELL STORE -- the same cell its physics runs on.

    WHAT THIS REPLACED, and why the replacement is not a widening (W1_14 step 3, 2026-09-21).
    Until this date the resolver here was a STRING RULE with no notion of location: strip a
    trailing `g`, else pass the id through, then look for `sim/weather_data/{id}.csv`. Four such
    archives exist, so ten of the book's eighteen premises found no file -- and `get_hdd` then
    returned `REFERENCE_MONTHLY_HDD[month] / 30.0` silently. That normal is the same number in
    2018 and in 2022, so a premise on it could not see the coldest winter in the record; it is
    biased high by a third to a half at an urban cell; and C1 and C7, which are the SAME
    COORDINATE, read annual HDD 12-20% apart purely because one id matched a filename.

    The import is deferred because `simulation.weather_inputs` reaches the registered supply book
    and this module is imported by `simulation.gas_settlement` -- at call time there is no cycle,
    at import time there would be.
    """
    if customer_id in _WEATHER_CACHE:
        return _WEATHER_CACHE[customer_id]
    from simulation.weather_inputs import cell_weather_for_customer_id

    cell_weather = cell_weather_for_customer_id(customer_id)
    sky = PremiseSky(customer_id, cell_weather.cell, cell_weather.series, cell_weather.refusal)
    _WEATHER_CACHE[customer_id] = sky
    return sky


def hdd_reading(date_str: str, customer_id: str) -> HddReading:
    """HDD for one day at the premise's CELL, carrying what it was read from.

    `get_hdd` is this function's `.hdd` and is what every arithmetic caller wants. This one exists
    so the substitution can NAME ITSELF: a run that prints `HddReading.basis`, or asserts on
    `from_normal`, can tell "the world's weather at cell E529N0180" from "no weather for this
    premise, so a climate normal stood in" -- which two plausible HDD numbers cannot.

    R15 hardening (2026-08-03, kept): a non-finite (NaN/inf) recorded temperature is rejected with
    ValueError rather than silently reaching the max(0.0, ...) comparison below. Python's
    `max(0.0, nan)` evaluates to 0.0 (NaN never compares greater than 0.0), which would otherwise
    silently read a corrupt/missing temperature reading as "warm, zero heating demand" -- the
    exact FAIL-OPEN pattern this codebase has been bitten by before.
    """
    sky = _premise_sky(customer_id)
    temp = sky.series.get(date_str)
    if temp is not None:
        if not math.isfinite(temp):
            raise ValueError(
                f"non-finite mean temperature ({temp!r}) for {customer_id} "
                f"(cell {sky.cell}) on {date_str}"
            )
        return HddReading(max(0.0, HDD_BASE_TEMP_C - temp), f"cell {sky.cell}", False)
    month = int(date_str[5:7])
    why = sky.refusal or (
        f"cell {sky.cell} holds no mean temperature on {date_str}" if sky.cell
        else f"no cell resolved for {customer_id}"
    )
    return HddReading(REFERENCE_MONTHLY_HDD[month] / 30.0, f"{NORMAL_BASIS_PREFIX} -- {why}", True)


def get_hdd(date_str: str, customer_id: str) -> float:
    """HDD for one day at the premise's cell. max(0, 15.5 - mean_temp).

    A bare float, so it stays the arithmetic every caller already does with it. When the premise
    has no weather this is a climate normal and the float cannot say so -- `hdd_reading` is the
    call that can, and `HddReading.from_normal` is the question.
    """
    return hdd_reading(date_str, customer_id).hdd


def get_monthly_hdd(year: int, month: int, customer_id: str) -> float:
    """Sum of daily HDD for one calendar month."""
    _, days = monthrange(year, month)
    return sum(
        get_hdd(f"{year:04d}-{month:02d}-{day:02d}", customer_id)
        for day in range(1, days + 1)
    )


def get_weather_factor(year: int, month: int, customer_id: str) -> float:
    """Ratio of actual to reference monthly HDD, clipped to [0.3, 2.0].

    < 1.0 -> warmer than normal -> less gas consumed.
    > 1.0 -> colder than normal -> more gas consumed.
    """
    ref = REFERENCE_MONTHLY_HDD.get(month, 30.0)
    if ref <= 0:
        return 1.0
    actual = get_monthly_hdd(year, month, customer_id)
    return max(0.3, min(2.0, actual / ref))


def weather_factor_for_term(term_start: str, term_end: str, customer_id: str) -> float:
    """Day-weighted average weather factor across all months in [term_start, term_end)."""
    start = date.fromisoformat(term_start)
    end = date.fromisoformat(term_end)

    total_days = 0
    weighted_sum = 0.0
    current = date(start.year, start.month, 1)

    while current < end:
        yr, mo = current.year, current.month
        _, mdays = monthrange(yr, mo)
        month_start = max(start, current)
        month_end_date = date(yr, mo, mdays)
        month_end = min(end, month_end_date + timedelta(days=1))
        days_in_period = (month_end - month_start).days
        if days_in_period > 0:
            factor = get_weather_factor(yr, mo, customer_id)
            weighted_sum += factor * days_in_period
            total_days += days_in_period
        if mo == 12:
            current = date(yr + 1, 1, 1)
        else:
            current = date(yr, mo + 1, 1)

    return weighted_sum / total_days if total_days > 0 else 1.0


# ---------------------------------------------------------------------------
# Cumulative HDD windows (thermal memory) -- see module docstring for the
# cited source (National Grid CWV effective-temperature decay) and the two
# engineering adaptations (applied to HDD not raw temperature; finite
# truncation of an infinite recursion).
# ---------------------------------------------------------------------------

#: Decay factor per day back, taken from National Grid's cited
#: Et = 0.5*Et-1 + 0.5*ATt effective-temperature recursion (halves once per
#: day of lookback). R12: fixed by the cited external convention, never
#: tuned against company P&L.
HDD_WINDOW_DECAY = 0.5

#: Finite truncation depth. Weight of the day `k` days back under the decay
#: above is `HDD_WINDOW_DECAY ** (k + 1)`; at k=9 (the 10th day, i.e. window
#: length 10) that weight is 0.5**10 = 0.0009765625 -- under 0.1% of the total
#: recursion mass (sum of all weights = 1 - 0.5**10 = 0.9990234375 before
#: renormalisation). A window of 10 days therefore captures >99.9% of the
#: true infinite recursion; this is an engineering truncation choice (not
#: part of the cited source) driven by needing a finite, testable window.
HDD_WINDOW_DAYS = 10


def _finite_hdd_window_weights(window_days: int, decay: float) -> list[float]:
    """Weights for [today, yesterday, ..., window_days-1 days ago], summing to 1.0.

    Renormalised truncation of the geometric decay `decay ** (k + 1)` --
    dividing by the truncated sum keeps the window's own weights a proper
    (sum-to-1) average regardless of how many days are actually available,
    which is what makes the short-history behaviour below well-defined rather
    than an implicit zero-pad (a FAIL-OPEN pattern this function deliberately
    avoids).
    """
    if window_days < 1:
        raise ValueError(f"window_days must be >= 1, got {window_days}")
    if not (0.0 < decay < 1.0):
        raise ValueError(f"decay must be in (0, 1), got {decay}")
    raw = [decay ** (k + 1) for k in range(window_days)]
    total = sum(raw)
    return [w / total for w in raw]


#: Precomputed weights for the default (window_days=10, decay=0.5) case --
#: the common path, computed once rather than on every call.
_HDD_WINDOW_WEIGHTS = _finite_hdd_window_weights(HDD_WINDOW_DAYS, HDD_WINDOW_DECAY)


def _parse_date_or_raise(date_str: str) -> date:
    """Strict ISO date parse. Rejects malformed input before any arithmetic."""
    try:
        return date.fromisoformat(date_str)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid date_str for cumulative HDD window: {date_str!r}") from exc


def get_cumulative_hdd(
    date_str: str,
    customer_id: str,
    window_days: int = HDD_WINDOW_DAYS,
    decay: float = HDD_WINDOW_DECAY,
) -> float:
    """Decay-weighted rolling HDD -- a thermal-memory-adjusted heating-demand signal.

    Unlike `get_hdd()` (memoryless: depends only on `date_str`'s own
    temperature), this folds in the `window_days - 1` days before `date_str`
    too, weighted so the day `k` days back counts for
    `decay ** (k + 1) / sum(decay ** (j + 1) for j in range(window_days))` --
    i.e. weight roughly halves (at the default decay=0.5) for every day
    further back, matching the National Grid effective-temperature shape
    cited in the module docstring. This is what lets two days with identical
    *own* HDD but different *antecedent* HDD (a cold snap's third day vs. an
    isolated cold day) produce different cumulative HDD -- the exact
    real-world behaviour a memoryless HDD cannot reproduce.

    Point-in-Time Blindfold: only reads `date_str` and the `window_days - 1`
    days STRICTLY BEFORE it -- never a future day. This holds by
    construction (the loop below only ever subtracts days).

    Event-arrival tolerance (C-S1): this function is a pure, stateless
    recomputation from `get_hdd()`'s own keyed (date-string) lookups every
    call -- it holds no running/incremental state across calls. Calling it
    for dates in any order, calling it twice for the same date, or calling it
    for a date whose neighbours haven't been "seen" yet in some external
    ingestion order all produce the identical, correct result, because
    nothing here depends on call sequence or on any prior call having
    happened first.

    Short-history / missing-day behaviour (explicit choice, not an
    accident): a day within the window that the premise's CELL has no
    temperature for falls through to `get_hdd()`'s own monthly-climatology
    fallback (`REFERENCE_MONTHLY_HDD`) -- exactly the same fallback the
    memoryless API already uses and existing callers already depend on. A
    short/missing history therefore reads as "typical weather for that
    month", never as a silent zero (FAIL-OPEN) and never as if the full
    window were present with today's value repeated (a different, equally
    wrong FAIL-OPEN shape). The weights above are also renormalised to sum
    to 1 regardless of `window_days`, so shrinking the window never
    silently drops mass.

    THIS FUNCTION RETURNS A BARE FLOAT AND SO CANNOT SAY WHICH DAYS OF ITS
    WINDOW WERE THE NORMAL. `hdd_reading()` is the per-day call that names
    its basis; a caller that needs the window's provenance must ask that
    function over the same days rather than infer it from this sum, because
    a window blended from nine real days and one normal is indistinguishable
    here from ten real days.

    Raises ValueError (never silently returns a value) if `date_str` is
    malformed, if `window_days`/`decay` are out of range, or if any day in
    the window carries a non-finite (NaN/inf) recorded temperature -- the
    non-finite check happens inside `get_hdd()` and is rejected FIRST, before
    it could ever reach a numeric comparison in the weighted sum below (the
    known NaN-blind-comparison defect class this project has hit before).
    """
    target = _parse_date_or_raise(date_str)
    if window_days == HDD_WINDOW_DAYS and decay == HDD_WINDOW_DECAY:
        weights = _HDD_WINDOW_WEIGHTS
    else:
        weights = _finite_hdd_window_weights(window_days, decay)

    total = 0.0
    for k, w in enumerate(weights):
        day = target - timedelta(days=k)
        h = get_hdd(day.isoformat(), customer_id)
        if not math.isfinite(h):
            # get_hdd() already guards its own input; this is a defence-in-depth
            # backstop so a future change to get_hdd() cannot silently
            # reintroduce a NaN/inf into this weighted sum uncaught.
            raise ValueError(f"non-finite HDD for {day.isoformat()} customer={customer_id}")
        total += w * h
    return total
