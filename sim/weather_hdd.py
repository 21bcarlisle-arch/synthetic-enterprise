"""HDD (heating degree day) model for gas consumption weather-adjustment.

UK standard base temperature 15.5°C (DECC/Ofgem domestic gas standard).
Reference monthly HDD: UK Met Office 1991-2020 climate normals (England & Wales).

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

import csv
import math
from calendar import monthrange
from datetime import date, timedelta

WEATHER_DATA_DIR = "sim/weather_data"
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

_WEATHER_CACHE: dict[str, dict[str, float]] = {}


def _load_weather_means(customer_id: str) -> dict[str, float]:
    if customer_id in _WEATHER_CACHE:
        return _WEATHER_CACHE[customer_id]
    path = f"{WEATHER_DATA_DIR}/{customer_id}.csv"
    try:
        with open(path, newline="") as f:
            result = {row["date"]: float(row["temperature_mean_c"]) for row in csv.DictReader(f)}
    except FileNotFoundError:
        result = {}
    _WEATHER_CACHE[customer_id] = result
    return result


def _resolve_source_cid(customer_id: str) -> str:
    """Map gas customer IDs to their weather-data counterpart.

    C1g -> C1 (shares location with dual-fuel electricity customer).
    Non-gas customers and unrecognised IDs pass through unchanged.
    """
    if customer_id.endswith("g") and len(customer_id) > 1:
        return customer_id[:-1]
    return customer_id


def get_hdd(date_str: str, customer_id: str) -> float:
    """HDD for one day at customer's location. max(0, 15.5 - mean_temp).

    R15 hardening (2026-08-03): a non-finite (NaN/inf) recorded temperature is
    rejected with ValueError rather than silently reaching the max(0.0, ...)
    comparison below. Python's `max(0.0, nan)` evaluates to 0.0 (NaN never
    compares greater than 0.0), which would otherwise silently read a
    corrupt/missing temperature reading as "warm, zero heating demand" -- the
    exact FAIL-OPEN pattern this codebase has been bitten by before. Genuine
    CSV weather data never contains non-finite values, so this changes nothing
    for any existing well-formed input/caller.
    """
    source_cid = _resolve_source_cid(customer_id)
    means = _load_weather_means(source_cid)
    if date_str in means:
        temp = means[date_str]
        if not math.isfinite(temp):
            raise ValueError(
                f"non-finite mean temperature ({temp!r}) for {source_cid} on {date_str}"
            )
        return max(0.0, HDD_BASE_TEMP_C - temp)
    month = int(date_str[5:7])
    return REFERENCE_MONTHLY_HDD[month] / 30.0


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
    accident): a day within the window that has no per-customer weather
    record falls through to `get_hdd()`'s own existing monthly-climatology
    fallback (`REFERENCE_MONTHLY_HDD`) -- exactly the same fallback the
    memoryless API already uses and existing callers already depend on. A
    short/missing history therefore reads as "typical weather for that
    month", never as a silent zero (FAIL-OPEN) and never as if the full
    window were present with today's value repeated (a different, equally
    wrong FAIL-OPEN shape). The weights above are also renormalised to sum
    to 1 regardless of `window_days`, so shrinking the window never
    silently drops mass.

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
