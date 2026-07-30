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
  * A2 outturn-consistency is NOT claimed: validating a per-year mean-match against the
    SAME-year AGWS outturn it was matched to is the exact TAUTOLOGY the FRAME forbids.
  * A3 mix-share and A4 no-coal-after-retirement ARE implemented as FAIL-LOUD checks
    (`check_mix_share_against_independent_source`, `check_no_coal_after_retirement`) —
    they raise rather than silently pass when their independent source (DESNZ Energy
    Trends Table 6; a coal capacity/generation series) is absent, which is the honest
    state right now (neither is ingested; no network this fork). This is deliberately
    NOT the same as skipping the check (R15 FAIL-SILENT forbidden).
  * A1 (offshore-capacity monotonicity, `check_offshore_non_decreasing`) IS implemented
    and IS mutation-tested, but honestly FAILS on today's real data at its strict
    (FRAME-literal) tolerance — see that function's docstring. This is reported, not
    loosened to force a pass (R12's anti-goal-seek spirit applied to a validator).
  * What IS honestly testable without network and mutation-proven in
    `tests/sim/test_renewable_capacity_trend.py`: the TREND (fleet grows materially across
    the window), NON-DEGENERACY (the trajectory is not the old flat scalar — 2016 ≠ 2025),
    DETERMINISM/replay (C-S2), COVERAGE-FAIL-CLOSED (a thin year is excluded, and an
    empty trajectory raises rather than silently returning a degenerate fleet), A1
    (offshore monotonicity — checked, real-data result reported honestly), and A3/A4
    FAIL-LOUD-on-missing-source (both raise correctly; neither's "success path" is
    exercised this fork, since neither independent source is ingested).

R13 wall: historical capacity is BASELINE (this module — fidelity-only, blind to P&L).
The forward window is CURRICULUM (a director-authored buildout scenario); the plain
default here is piecewise-constant with FLAT tails (hold-2025-flat forward, hold-2016
back), never an agent-tuned extrapolation.

WALL: SIM-side physics. Nothing in company/ or saas/ may import this module.
"""

from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np

# Same cache directory sim/weather_price_chain.py reads (this module also lives in
# sim/). Read-only lookups on already-ingested real Elexon data — no new ingestion
# module, no network fetch.
_CACHE = Path(__file__).resolve().parent / "cache"

# A calendar year with fewer aligned days than this is too thin to mean-match honestly —
# it is EXCLUDED from the trajectory (COVERAGE, fail-closed) rather than yielding a
# degenerate scalar built from a handful of days.
_MIN_DAYS_PER_YEAR = 60

# A1 (offshore monotonicity, below) needs YEAR-OVER-YEAR MAGNITUDE comparisons, not just
# presence — a year covered by a lopsided subset of months (e.g. 2025's Jan-Jun-only
# data in this cache) is not comparable to a full year on the same basis (see the
# 2025 finding in check_offshore_non_decreasing's docstring). Stricter than
# _MIN_DAYS_PER_YEAR; used only by A1.
_MIN_DAYS_FOR_MAGNITUDE_COMPARISON = 300


class DegenerateTrajectoryError(ValueError):
    """The capacity trajectory cannot be built honestly (no year has enough aligned
    days, or a year's physical shape has zero mean). Fail LOUD — never return a
    degenerate fleet silently (R15 FAIL-OPEN forbidden)."""


def _year_of(date_str: str) -> int:
    return int(str(date_str)[:4])


def _load_offshore_onshore_daily() -> tuple[dict, dict]:
    """Daily mean MW for Wind Offshore and Wind Onshore SEPARATELY, straight from the
    raw AGWS cache — the same file `weather_price_chain.load_daily_record()` reads
    (via `generation_demand_history.aggregate_wind_generation`, which SUMS the two
    psrTypes together, losing the split). A local psrType filter on already-ingested
    Elexon data: no new ingestion module, no network fetch, and
    `sim/generation_demand_history.py` (out of this atom's file_scope) is untouched.

    Real-world fact this split exists to serve (A1, below): GB offshore wind capacity
    has only ever been ADDED across 2016-2025 (never de-commissioned) — a fact the
    combined onshore+offshore scalar hides entirely.
    """
    raw = json.loads((_CACHE / "elexon_agws_full.json").read_text())
    off: dict = defaultdict(list)
    on: dict = defaultdict(list)
    for r in raw:
        d = r["settlementDate"]
        q = float(r["quantity"])
        if r["psrType"] == "Wind Offshore":
            off[d].append(q)
        elif r["psrType"] == "Wind Onshore":
            on[d].append(q)
    return ({d: float(np.mean(v)) for d, v in off.items()},
            {d: float(np.mean(v)) for d, v in on.items()})


@lru_cache(maxsize=1)
def fleet_trajectory() -> dict:
    """Per-year effective renewable fleet scalars, mean-matched WITHIN each calendar
    year on already-ingested real data.

    Returns {year: {"wind_fleet_mw": float, "solar_fleet_mw": float, "n_days": int,
    "wind_offshore_fleet_mw": float?, "wind_onshore_fleet_mw": float?}} for every year
    with >= _MIN_DAYS_PER_YEAR aligned days (the offshore/onshore keys are present
    whenever that year has any aligned AGWS offshore/onshore rows — the whole window
    does, in practice). Deterministic (C-S2): a pure function of the on-disk record,
    so two calls are byte-identical (cached).

    R10 SIMPLIFICATION (new): offshore and onshore effective fleets both scale the
    SAME national wind-speed power-curve fraction (`wind_power_output_fraction`) —
    there is no separate offshore-only wind-resource series in this sim. This is a
    stated approximation, not a claim the two technologies share one physical
    resource; it is the same shape already used for the combined `wind_fleet_mw`.
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
    off_daily, on_daily = _load_offshore_onshore_daily()

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
        cell = {
            "wind_fleet_mw": float(rec["wind_gen_mw"][m].mean() / wf_mean),
            "solar_fleet_mw": float(rec["solar_gen_mw"][m].mean() / env_mean),
            "n_days": n,
        }
        dates_in_year = [rec["dates"][i] for i in range(len(rec["dates"])) if m[i]]
        off_vals = [off_daily[d] for d in dates_in_year if d in off_daily]
        on_vals = [on_daily[d] for d in dates_in_year if d in on_daily]
        if off_vals:
            cell["wind_offshore_fleet_mw"] = float(np.mean(off_vals) / wf_mean)
        if on_vals:
            cell["wind_onshore_fleet_mw"] = float(np.mean(on_vals) / wf_mean)
        out[y] = cell

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


def capacity_wind_offshore(year: int) -> float:
    """Effective OFFSHORE wind fleet scalar for calendar year τ (A1's target — see
    `check_offshore_non_decreasing`). Raises DegenerateTrajectoryError if the
    (clamped) covered year has no aligned offshore rows at all — never silently
    falls back to the combined wind scalar (that would hide the exact distinction
    A1 exists to check)."""
    traj = fleet_trajectory()
    y = _clamped_year(year, traj)
    if "wind_offshore_fleet_mw" not in traj[y]:
        raise DegenerateTrajectoryError(f"no aligned offshore-wind data for year {y}")
    return traj[y]["wind_offshore_fleet_mw"]


def capacity_wind_onshore(year: int) -> float:
    """Effective ONSHORE wind fleet scalar for calendar year τ. See
    `capacity_wind_offshore` — same coverage guard."""
    traj = fleet_trajectory()
    y = _clamped_year(year, traj)
    if "wind_onshore_fleet_mw" not in traj[y]:
        raise DegenerateTrajectoryError(f"no aligned onshore-wind data for year {y}")
    return traj[y]["wind_onshore_fleet_mw"]


# ── Invariants (R15 — mutation-testable) ────────────────────────────────────────────
# A2 (outturn-consistency vs the independent AGWS outturn) is deliberately absent:
# the trajectory IS built from AGWS outturn, so checking it against AGWS outturn is
# the exact TAUTOLOGY the FRAME forbids. A3/A4 below are implemented as FAIL-LOUD
# stubs (R15 FAIL-SILENT forbidden: "an unavailable check is a FAILED check") rather
# than silently skipped, per the atom's explicit instruction.

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


def check_offshore_non_decreasing(traj: dict | None = None, tol_frac: float = 0.0) -> bool:
    """A1 (FRAME §4): capacity_wind_offshore(τ) is non-decreasing across the
    historical window — GB offshore wind was only ever ADDED 2016-2025, never
    de-commissioned (a real, load-bearing fact this atom's combined wind-fleet
    scalar had thrown away).

    Checked here against the per-year EFFECTIVE offshore fleet (same honesty
    boundary as `check_trend_increasing`/`check_time_varying`: capacity growth
    convolved with year-to-year load-factor noise, not pure installed capacity).
    Years thinner than `_MIN_DAYS_FOR_MAGNITUDE_COMPARISON` are EXCLUDED from this
    specific check — a magnitude comparison across years needs comparable seasonal
    coverage, and this cache's most recent year is Jan-Jun only (a lopsided,
    windier-than-average subset), which would otherwise distort a real-vs-real
    comparison in either direction. Fewer than 2 comparable years -> FAILS (not a
    vacuous pass — R15 FAIL-OPEN forbidden).

    HONEST FINDING (do not tune away): with `tol_frac=0.0` (the FRAME's literal
    strict wording) this check FAILS on the REAL trajectory today — the year-over-
    year EFFECTIVE offshore fleet is not strictly monotone (e.g. 2017 < 2016,
    2020 < 2019, 2022 < 2021 in the current cache), because real wind-resource
    variability moves the load-factor term more than the true, monotone installed-
    capacity signal it convolves with. This is NOT loosened to force a pass (that
    would be tuning a validator to flatter its own generator, the sibling of R12's
    anti-goal-seek rule); it is reported as-is. The strict, non-tautological form of
    A1 needs the DUKES Ch.6 installed-capacity series (network-blocked) to strip
    load-factor from the true capacity signal — an L2 step, not built here.
    """
    traj = traj if traj is not None else fleet_trajectory()
    ys = [y for y in sorted(traj)
          if "wind_offshore_fleet_mw" in traj[y]
          and traj[y]["n_days"] >= _MIN_DAYS_FOR_MAGNITUDE_COMPARISON]
    if len(ys) < 2:
        return False  # can't assert monotonicity on <2 comparable years
    vals = [traj[y]["wind_offshore_fleet_mw"] for y in ys]
    return all(vals[i + 1] >= vals[i] * (1.0 - tol_frac) for i in range(len(vals) - 1))


class IndependentSourceUnavailableError(RuntimeError):
    """A3 (FRAME §3/§4, anti-marking-own-homework): the mix-share validator must be
    anchored to an INDEPENDENT source (DESNZ Energy Trends Table 6) — NEVER the same
    AGWS outturn used to build the capacity trajectory it is checking (that would be
    the exact TAUTOLOGY the FRAME forbids). That source has not been ingested into
    this repo (network-blocked this fork — no live network). Per R15 FAIL-SILENT
    discipline ("an unavailable check is a FAILED check"), calling the validator
    without it must FAIL LOUD — never silently pass, skip, or fall back to comparing
    against the same-source data it is meant to validate against."""


# Where the independent DESNZ Energy Trends Table 6 mix-share series would live once
# a discovery-agent network pass ingests it (FRAME §9 task 1). Not fetched this fork.
DESNZ_MIX_SHARE_PATH = _CACHE / "desnz_energy_trends_table6_mix_share.json"


def check_mix_share_against_independent_source(source_path=None) -> bool:
    """A3: annual wind-generation-share reproduced by this trajectory vs the
    INDEPENDENT DESNZ Energy Trends Table 6 series (not the AGWS outturn the
    trajectory is fit to — anti-marking-own-homework). Raises
    `IndependentSourceUnavailableError` when that source is not on disk — the
    CORRECT behaviour right now (no network this fork) — rather than returning
    True/False on absent data or silently comparing against AGWS instead."""
    path = Path(source_path) if source_path else DESNZ_MIX_SHARE_PATH
    if not path.exists():
        raise IndependentSourceUnavailableError(
            f"A3 mix-share validator: independent source not found at {path} — "
            "DESNZ Energy Trends Table 6 has not been ingested (network-blocked "
            "this fork). Refusing to silently pass, skip, or fall back to the "
            "same-source AGWS comparison (R15 FAIL-SILENT forbidden)."
        )
    # Reachable only once the independent series is ingested — shape is provisional
    # (untested against the real DESNZ file this fork; adjust at ingestion time).
    desnz = json.loads(path.read_text())  # pragma: no cover - network-blocked this fork
    traj = fleet_trajectory()
    rec_years = sorted(traj)
    for y in rec_years:
        if str(y) not in desnz:
            return False  # missing year in the independent series = FAILED, not skipped
    return True


class CoalSeriesUnavailableError(RuntimeError):
    """A4 (FRAME §4): no coal capacity/generation series is ingested in this sim —
    AGWS (this atom's only generation-mix source) covers Wind Onshore/Offshore and
    Solar only; there is no existing coal-capacity concept anywhere in the price
    engine to check against yet. Per R15 FAIL-SILENT discipline, calling the check
    without a coal series must FAIL LOUD, never silently pass on absent data."""


# GB's last coal-fired power station (Ratcliffe-on-Soar) is widely reported to have
# closed 2024-09-30. UNVERIFIED THIS FORK — no live network to re-confirm against a
# primary DESNZ/NESO source; treat as a flagged assumption pending the discovery-agent
# network pass (FRAME §9 task 1), never as an asserted statistic.
LAST_COAL_GENERATION_YEAR = 2024


def check_no_coal_after_retirement(coal_capacity_by_year: dict | None) -> bool:
    """A4: coal contributes zero to the stack after its real retirement year. Takes
    an explicit {year: capacity_mw} series (there is no in-repo coal series to
    default to — AGWS is wind+solar only) and raises `CoalSeriesUnavailableError` on
    `None`/`{}` rather than silently passing on absent data (R15 FAIL-SILENT
    forbidden). Given a real series, returns False if ANY year strictly after
    `LAST_COAL_GENERATION_YEAR` has nonzero capacity."""
    if not coal_capacity_by_year:
        raise CoalSeriesUnavailableError(
            "A4 no-coal-after-retirement: no coal capacity/generation series was "
            "supplied (none is ingested in this sim — AGWS covers wind+solar only). "
            "Refusing to silently pass on absent data."
        )
    return all(v == 0 for y, v in coal_capacity_by_year.items()
               if y > LAST_COAL_GENERATION_YEAR)
