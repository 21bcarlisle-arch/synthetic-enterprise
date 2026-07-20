"""W1_3 "SHOW THE TAIL" — the joint cold-and-still (Dunkelflaute) demonstration.

DIRECTOR DoD (WEATHER_PHYSICS_HIERARCHY.md, atom W1_3): "temporal autocorrelation
present; the joint cold-still tail demonstrated (SHOW the tail); winter-tail
report compared to a real GB worst week (if our worst week is milder than
reality, physics still wrong)." Cold-and-still is THE single most important GB
power correlation: draw temperature and wind independently and the
supplier-killing winter tail never occurs and every hedge looks fine (a lie).
This module is the failable demonstration that the calibrated weather engine
(`sim/weather_engine.py`) actually PRODUCES that joint tail rather than smoothing
it away.

ADDITIVE, NOT AN ENGINE CHANGE. It reads the engine's existing fit/simulate
functions and the real Open-Meteo calibration series already in the repo
(`sim/weather_data/{C1..C4}.csv`); it changes no engine internals. It is a
HARNESS / director-facing artefact (a "show the tail" instrument), never
company-facing — the company never reads it, so it is free to see SIM internals
(the same standing as run_phase3c_calibration.py).

THE METRIC (a joint tail, never two marginals). For each rolling 7-day winter
(DJF) window it scores a Dunkelflaute severity as the PRODUCT of two intensities:

    cold_intensity  = max(0, temp_threshold - window_mean_temperature)   [degC below]
    still_intensity = max(0, wind_threshold - window_mean_wind)          [m/s below]
    severity        = cold_intensity * still_intensity

The PRODUCT is the point: a cold-but-windy week or a still-but-mild week scores
near zero; only CO-OCCURRING cold AND still scores high. Thresholds are the low
percentiles of the REAL winter distribution (data-anchored, not arbitrary) and
are applied identically to the real and the synthetic series so the comparison
is fair. `_TAIL_PERCENTILE` is an asserted choice (R10), not fitted to any
outcome.

THE FAILABLE CHECK (R12-safe: a CAPABILITY ENVELOPE, never a tuned target). The
director's DoD is literal: "if our worst week is MILDER than reality, physics
still wrong." The real history is ONE draw and the joint tail is genuinely RARE
(in the real series only ~1% of winter windows co-occur cold AND still), so a
tuned "reach the real worst in >= X% of runs" FREQUENCY floor would be an
arbitrary target on a rare event observed once — over-claiming from n=1 and
inviting goal-seek. Instead the gate is the ENVELOPE: over `n_sims` synthetic
realisations the engine must be CAPABLE of producing a worst winter week at
least as severe as the one real history did (`max(synthetic_worst) >=
real_worst`). `assert_tail_not_smoothed` FIRES (raises) only when the engine's
whole synthetic tail sits BELOW the real worst week — i.e. the engine is
categorically milder than reality, the exact "hedge looks fine in a tail that
never co-occurs" failure. `reach_fraction` (how OFTEN the engine reaches the
real worst) is REPORTED as a richer diagnostic and a gap-1 SIGNAL (a low
fraction hints the engine under-produces the tail's FREQUENCY — the FRAME's
wind-only-regime-trigger gap), but is NEVER the gate: n=1 real cannot
distinguish "engine under-produces" from "we happened to observe a modestly-
probable event", so gating on it would assert more than the evidence carries
(R9). The envelope is never used to tune the engine toward the band (R12 / LAW
A / R13: the baseline faces reality, never company P&L).

KNOWN SIMPLIFICATION (R10, gap 3 of the W1_3 FRAME — anti-marking-own-homework).
The comparison anchor is the SAME real series the engine calibrates on, so this
check catches a generator that UNDER-produces the tail its own calibration data
contains; it does NOT independently verify the real series against a DIFFERENT
published GB anchor (degree-days / NESO system-demand worst-week). That
independent validator anchor requires an external published source (network),
deferred; registered here as `_MARKING_OWN_HOMEWORK_SIMP_ID` rather than
pretended away.

C-S2 (determinism): every draw is from a seeded `np.random.default_rng(seed)`;
same seed + same data -> identical demonstration, run to run.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from sim.weather_engine import (
    MACRO_VARS,
    fit_national_macro_model,
    simulate_national_macro,
)

_WEATHER_DIR = Path(__file__).resolve().parent / "weather_data"
_LOCATIONS = ("C1", "C2", "C3", "C4")
_WINTER_MONTHS = frozenset({12, 1, 2})
_WINDOW_DAYS = 7

# Asserted choices (R10), not fitted to any outcome:
_TAIL_PERCENTILE = 15.0   # low-percentile of the REAL winter distribution -> thresholds
_DEFAULT_N_SIMS = 25
_DEFAULT_SEED = 42

_MARKING_OWN_HOMEWORK_SIMP_ID = "w1_3_tail_anchor_same_as_calibration_no_independent_gb_anchor"


@dataclass(frozen=True)
class WorstWeek:
    """The worst joint cold-and-still winter week in one series."""

    start_date: str
    end_date: str
    severity: float
    mean_temperature_c: float
    mean_wind_ms: float


@dataclass(frozen=True)
class TailDemonstration:
    """The full 'show the tail' artefact for the director/harness."""

    temp_threshold_c: float
    wind_threshold_ms: float
    tail_percentile: float
    real_worst: WorstWeek
    synthetic_worst_severities: Tuple[float, ...]
    synthetic_worst_median: float
    synthetic_worst_max: float     # the tail ENVELOPE ceiling across the sims
    reach_fraction: float          # DIAGNOSTIC ONLY (gap-1 signal): fraction of sims whose worst >= real
    envelope_reaches_real: bool    # the GATE: max(synthetic_worst) >= real_worst
    passes: bool                   # == envelope_reaches_real
    n_sims: int
    seed: int
    simplification_id: str


# --------------------------------------------------------------------------
# Real-data loading (reuses the run_phase3c_calibration.py loader shape, R4)
# --------------------------------------------------------------------------

def load_national_daily() -> Tuple[Dict[str, np.ndarray], np.ndarray, List[datetime]]:
    """Load the real 4-location Open-Meteo daily series, averaged to a national
    series (the same national mean run_phase3c_calibration.py fits on). Returns
    (national {var: array}, day_of_year, dates)."""
    per_loc: Dict[str, Dict[str, np.ndarray]] = {}
    dates: List[datetime] = []
    for i, loc in enumerate(_LOCATIONS):
        rows = list(csv.DictReader((_WEATHER_DIR / f"{loc}.csv").open()))
        if i == 0:
            dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in rows]
        per_loc[loc] = {
            var: np.array([float(r[var]) for r in rows]) for var in MACRO_VARS
        }
    national = {
        var: np.mean([per_loc[loc][var] for loc in _LOCATIONS], axis=0)
        for var in MACRO_VARS
    }
    day_of_year = np.array([d.timetuple().tm_yday for d in dates])
    return national, day_of_year, dates


# --------------------------------------------------------------------------
# The joint cold-and-still severity metric
# --------------------------------------------------------------------------

def _rolling_mean(x: np.ndarray, window: int = _WINDOW_DAYS) -> np.ndarray:
    """Trailing window mean; the first (window-1) entries are NaN (no full
    window yet) and are excluded from the winter scan."""
    out = np.full(len(x), np.nan)
    if len(x) >= window:
        c = np.cumsum(np.insert(x, 0, 0.0))
        out[window - 1:] = (c[window:] - c[:-window]) / window
    return out


def _winter_window_end_mask(dates: List[datetime], window: int = _WINDOW_DAYS) -> np.ndarray:
    """True where a trailing `window` ends on a winter (DJF) day and a full
    window exists."""
    mask = np.array([d.month in _WINTER_MONTHS for d in dates])
    mask[: window - 1] = False
    return mask


def derive_thresholds(
    national: Dict[str, np.ndarray], dates: List[datetime], percentile: float = _TAIL_PERCENTILE
) -> Tuple[float, float]:
    """Cold/still thresholds = the low `percentile` of the REAL WINTER daily
    distribution (data-anchored). Winter-only so the thresholds reflect the
    season the tail lives in, not the annual mean."""
    winter = np.array([d.month in _WINTER_MONTHS for d in dates])
    temp_thr = float(np.percentile(national["temperature_mean_c"][winter], percentile))
    wind_thr = float(np.percentile(national["wind_speed_mean_ms"][winter], percentile))
    return temp_thr, wind_thr


def joint_severity(
    temperature: np.ndarray, wind: np.ndarray, dates: List[datetime],
    temp_thr: float, wind_thr: float, window: int = _WINDOW_DAYS,
) -> np.ndarray:
    """Per-window Dunkelflaute severity = cold_intensity * still_intensity, the
    PRODUCT (co-occurrence). Non-winter / incomplete windows are NaN."""
    temp_w = _rolling_mean(temperature, window)
    wind_w = _rolling_mean(wind, window)
    cold = np.clip(temp_thr - temp_w, 0.0, None)
    still = np.clip(wind_thr - wind_w, 0.0, None)
    sev = cold * still
    sev[~_winter_window_end_mask(dates, window)] = np.nan
    return sev


def worst_winter_week(
    temperature: np.ndarray, wind: np.ndarray, dates: List[datetime],
    temp_thr: float, wind_thr: float, window: int = _WINDOW_DAYS,
) -> WorstWeek:
    """The single worst joint cold-and-still winter week (max severity)."""
    sev = joint_severity(temperature, wind, dates, temp_thr, wind_thr, window)
    if np.all(np.isnan(sev)):
        raise ValueError("no winter windows in the series -- cannot show the tail")
    end = int(np.nanargmax(sev))
    start = end - (window - 1)
    tw = _rolling_mean(temperature, window)[end]
    ww = _rolling_mean(wind, window)[end]
    return WorstWeek(
        start_date=dates[start].strftime("%Y-%m-%d"),
        end_date=dates[end].strftime("%Y-%m-%d"),
        severity=float(sev[end]),
        mean_temperature_c=float(tw),
        mean_wind_ms=float(ww),
    )


# --------------------------------------------------------------------------
# The demonstration + the failable check
# --------------------------------------------------------------------------

def demonstrate_tail(
    national: Dict[str, np.ndarray] | None = None,
    day_of_year: np.ndarray | None = None,
    dates: List[datetime] | None = None,
    *,
    n_sims: int = _DEFAULT_N_SIMS,
    seed: int = _DEFAULT_SEED,
    percentile: float = _TAIL_PERCENTILE,
    macro_params: dict | None = None,
) -> TailDemonstration:
    """Fit the engine on the real national series, simulate `n_sims`
    realisations, and compare each synthetic worst winter week against the real
    worst winter week on the SAME thresholds. `macro_params` may be injected
    (used by the R15 mutation test to feed a deliberately-smoothed engine);
    otherwise it is fitted from the real data."""
    if national is None or day_of_year is None or dates is None:
        national, day_of_year, dates = load_national_daily()

    temp_thr, wind_thr = derive_thresholds(national, dates, percentile)
    real_worst = worst_winter_week(
        national["temperature_mean_c"], national["wind_speed_mean_ms"],
        dates, temp_thr, wind_thr,
    )

    if macro_params is None:
        macro_params = fit_national_macro_model(national, day_of_year)

    rng = np.random.default_rng(seed)
    synth_worsts: List[float] = []
    for _ in range(n_sims):
        sim = simulate_national_macro(macro_params, day_of_year, rng)
        w = worst_winter_week(
            sim["temperature_mean_c"], sim["wind_speed_mean_ms"],
            dates, temp_thr, wind_thr,
        )
        synth_worsts.append(w.severity)

    synth = np.array(synth_worsts)
    reach = float(np.mean(synth >= real_worst.severity))
    envelope_max = float(np.max(synth))
    reaches = envelope_max >= real_worst.severity
    return TailDemonstration(
        temp_threshold_c=temp_thr,
        wind_threshold_ms=wind_thr,
        tail_percentile=percentile,
        real_worst=real_worst,
        synthetic_worst_severities=tuple(float(s) for s in synth_worsts),
        synthetic_worst_median=float(np.median(synth)),
        synthetic_worst_max=envelope_max,
        reach_fraction=reach,
        envelope_reaches_real=reaches,
        passes=reaches,
        n_sims=n_sims,
        seed=seed,
        simplification_id=_MARKING_OWN_HOMEWORK_SIMP_ID,
    )


class TailSmoothedError(AssertionError):
    """Raised when the engine systematically produces milder joint cold-and-still
    tails than the real history it was calibrated on -- the 'physics still wrong /
    every hedge looks fine' failure the DoD exists to catch."""


def assert_tail_not_smoothed(demo: TailDemonstration) -> None:
    """FAIL-LOUD DoD gate (the director's literal "not milder than reality"): the
    engine's synthetic tail ENVELOPE must reach the real worst winter week
    (`max(synthetic_worst) >= real_worst`). Gates on capability, not the
    `reach_fraction` frequency (R12: a diagnostic envelope, never a tuning
    target; R9: n=1 real cannot support a frequency claim)."""
    if not demo.passes:
        raise TailSmoothedError(
            f"joint cold-and-still tail SMOOTHED: over {demo.n_sims} sims the engine's "
            f"worst winter week never reached the real worst "
            f"({demo.real_worst.start_date}..{demo.real_worst.end_date}, "
            f"severity {demo.real_worst.severity:.2f}); synthetic envelope max only "
            f"{demo.synthetic_worst_max:.2f} -- physics is categorically milder than the "
            f"GB winter tail (every hedge looks fine in a tail that never co-occurs)"
        )
