"""W1_7 — Renewable capacity + generation-mix evolution over time (L1 skeletal).

THE GAP (named verbatim in `sim/weather_price_chain.py`'s own header): the renewable
fleet there is a single MEAN-MATCHED scalar over the whole 2016–2025 window, but GB's
real fleet roughly *tripled* across that window. So today the same weather draw prices
IDENTICALLY in 2016 and 2025 — false to reality, and the single biggest driver of the
falling-baseload / rising-volatility regime the price engine tries to reproduce.

L1 MECHANISM (network-free, from data already on disk): replace the whole-window
mean-match with a PER-YEAR mean-match. For each calendar year τ the effective fleet
scalar is that year's mean renewable outturn / that year's mean physical shape
(power-curve fraction for wind, seasonal envelope for solar) — using the AGWS outturn
`weather_price_chain.load_daily_record()` already ingests. This makes `capacity_k(τ)`
time-varying: a slow calendar clock τ (years), explicitly SEPARATE from the fast
half-hourly weather clock t (a registered C-S5 time-scale exception). Layered ON TOP of
the merit order — the merit-order γ calibration is not re-opened (R12 / FRAME §2).

HONESTY BOUNDARIES (R15 + FRAME §10, load-bearing — do NOT overclaim):
  * The per-year mean-match yields an EFFECTIVE fleet that combines true installed-
    capacity growth with residual year-to-year LOAD-FACTOR variation (the power curve
    is an imperfect model of real output). It is NOT pure installed capacity. It is a
    strictly better approximation than one whole-window scalar (it carries the ~tripling
    trend), but separating capacity from load-factor needs the DUKES Ch.6 installed-
    capacity series — network-blocked (discovery-agent pass), an L2 step.
  * A2 outturn-consistency and A3 mix-share are therefore NOT claimed here: validating a
    per-year mean-match against the SAME-year outturn it was matched to is the exact
    TAUTOLOGY the FRAME forbids. The independent validators (DESNZ Energy Trends Table 6
    mix-share; DUKES capacity) require network and are registered as blocked, not asserted.
  * What IS honestly testable without network and mutation-proven in
    `tests/sim/test_renewable_capacity_trend.py`: the TREND (fleet grows materially across
    the window), NON-DEGENERACY (the trajectory is not the old flat scalar — 2016 ≠ 2025),
    DETERMINISM/replay (C-S2), and COVERAGE-FAIL-CLOSED (a thin year is excluded, and an
    empty trajectory raises rather than silently returning a degenerate fleet).

R13 wall: historical capacity is BASELINE (this module — fidelity-only, blind to P&L).
The forward window is CURRICULUM (a director-authored buildout scenario); the plain
default here is piecewise-constant with FLAT tails (hold-2025-flat forward, hold-2016
back), never an agent-tuned extrapolation.

WALL: SIM-side physics. Nothing in company/ or saas/ may import this module.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np

# A calendar year with fewer aligned days than this is too thin to mean-match honestly —
# it is EXCLUDED from the trajectory (COVERAGE, fail-closed) rather than yielding a
# degenerate scalar built from a handful of days.
_MIN_DAYS_PER_YEAR = 60


class DegenerateTrajectoryError(ValueError):
    """The capacity trajectory cannot be built honestly (no year has enough aligned
    days, or a year's physical shape has zero mean). Fail LOUD — never return a
    degenerate fleet silently (R15 FAIL-OPEN forbidden)."""


def _year_of(date_str: str) -> int:
    return int(str(date_str)[:4])


@lru_cache(maxsize=1)
def fleet_trajectory() -> dict:
    """Per-year effective renewable fleet scalars, mean-matched WITHIN each calendar
    year on already-ingested real data.

    Returns {year: {"wind_fleet_mw": float, "solar_fleet_mw": float, "n_days": int}}
    for every year with >= _MIN_DAYS_PER_YEAR aligned days. Deterministic (C-S2): a
    pure function of the on-disk record, so two calls are byte-identical (cached).
    """
    # Lazy imports break the weather_price_chain <-> this-module cycle (that module's
    # year-aware paths import capacity_wind/capacity_solar from here).
    from sim.weather_price_chain import (
        _solar_envelope,
        load_daily_record,
        wind_power_output_fraction,
    )

    rec = load_daily_record()
    years = np.array([_year_of(d) for d in rec["dates"]])
    frac = np.array([wind_power_output_fraction(float(w)) for w in rec["wind_speed_ms"]])
    env = np.asarray(_solar_envelope(rec["day_of_year"], rec["cloud_pct"]), float)

    out: dict = {}
    for y in sorted({int(v) for v in years}):
        m = years == y
        n = int(m.sum())
        if n < _MIN_DAYS_PER_YEAR:
            continue  # too thin — excluded (COVERAGE), never a hand-full-of-days fleet
        wf_mean = float(frac[m].mean())
        env_mean = float(env[m].mean())
        if wf_mean <= 0 or env_mean <= 0:
            raise DegenerateTrajectoryError(
                f"year {y}: physical shape has non-positive mean "
                f"(wind_frac={wf_mean}, solar_env={env_mean})"
            )
        out[y] = {
            "wind_fleet_mw": float(rec["wind_gen_mw"][m].mean() / wf_mean),
            "solar_fleet_mw": float(rec["solar_gen_mw"][m].mean() / env_mean),
            "n_days": n,
        }

    if not out:
        raise DegenerateTrajectoryError(
            "no calendar year had enough aligned days to mean-match — "
            "refusing to return a degenerate fleet"
        )
    return out


def _clamped_year(year: int, traj: dict | None = None) -> int:
    """Map an arbitrary year onto the nearest year the trajectory covers. Interior thin
    years (excluded) snap to the nearest covered year; years outside the historical
    window CLAMP to the first/last covered year — the R13 hold-flat default (never an
    agent-authored forward extrapolation)."""
    traj = traj if traj is not None else fleet_trajectory()
    ys = sorted(traj)
    y = min(max(int(year), ys[0]), ys[-1])  # clamp into [first, last] covered year
    if y in traj:
        return y
    return min(ys, key=lambda k: abs(k - y))  # nearest covered interior year


def capacity_wind(year: int) -> float:
    """Effective wind fleet scalar (MW on the power-curve fraction) for calendar year τ.
    Piecewise-constant, flat outside the historical window (R13 hold-flat default)."""
    traj = fleet_trajectory()
    return traj[_clamped_year(year, traj)]["wind_fleet_mw"]


def capacity_solar(year: int) -> float:
    """Effective solar fleet scalar (MW on the seasonal envelope) for calendar year τ.
    Piecewise-constant, flat outside the historical window (R13 hold-flat default)."""
    traj = fleet_trajectory()
    return traj[_clamped_year(year, traj)]["solar_fleet_mw"]


# ── Invariants (R15 — mutation-testable; the ones honestly checkable WITHOUT network) ──
# A2/A3 (outturn-consistency, mix-share) are deliberately absent: against the same-year
# data they'd be tautological, and their independent sources are network-blocked (§10).

def check_trend_increasing(traj: dict | None = None, min_ratio: float = 1.5) -> bool:
    """A1 (weak, honest form): the effective wind fleet grows MATERIALLY across the
    window — mean of the last two covered years >= min_ratio x mean of the first two.
    (Real GB wind fleet roughly doubled 2016->2025; 1.5x is a conservative floor.)
    A whole-window flat scalar collapses per-year variance -> ratio ~ 1 -> FAILS. The
    stronger year-over-year monotone form needs DUKES capacity to strip load-factor
    (network-blocked) — not asserted here."""
    traj = traj if traj is not None else fleet_trajectory()
    ys = sorted(traj)
    first = float(np.mean([traj[y]["wind_fleet_mw"] for y in ys[:2]]))
    last = float(np.mean([traj[y]["wind_fleet_mw"] for y in ys[-2:]]))
    if first <= 0:
        return False
    return last >= min_ratio * first


def check_time_varying(traj: dict | None = None, min_cv: float = 0.05) -> bool:
    """NON-DEGENERACY: the trajectory is not the old flat scalar. The wind fleet's
    coefficient of variation across covered years exceeds min_cv, i.e. a given weather
    draw prices differently in 2016 than in 2025. Reverting to a single whole-window
    scalar -> CV = 0 -> FAILS. This is the invariant that proves the mechanism does
    something."""
    traj = traj if traj is not None else fleet_trajectory()
    vals = np.array([traj[y]["wind_fleet_mw"] for y in sorted(traj)], float)
    if vals.mean() <= 0:
        return False
    return float(vals.std() / vals.mean()) > min_cv
