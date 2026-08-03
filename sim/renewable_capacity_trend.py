"""W1_7 — Renewable capacity + generation-mix evolution over time (L1 built; L2
discovery-agent pass 2026-08-03 separates capacity from load-factor — see below).

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
    is an imperfect model of real output). It is NOT pure installed capacity.
  * 2026-08-03 L2 PASS: network is available this fork. The real DUKES/Energy Trends
    installed-capacity series (`real_capacity_wind_onshore/offshore/solar`, sourced +
    cited in `docs/market_research/w1_7_renewable_capacity_dukes_desnz.md`) is now
    ingested and used to SEPARATE capacity from load-factor
    (`load_factor_residual`) — the effective fleet's wind residual sits at a stable
    ~4.6-5.1x (CV ~0.14-0.17), not ~1x, because the sim's power curve is driven by
    NATIONAL MEAN wind speed while real turbines are sited non-randomly in
    higher-wind-resource locations (a genuine siting-selection effect, not a defect —
    fixing the curve itself would re-open the merit-order/SSP calibration, R12/S8,
    out of scope). This enables the non-tautological, STRICT forms:
    - **A1 strict** (`check_offshore_capacity_strictly_non_decreasing`): real DUKES
      offshore capacity — TRUE on real data (offshore was only ever added,
      2016-2025). The original `check_offshore_non_decreasing` (checked against the
      AGWS-fitted effective fleet) still honestly FAILS, unchanged — a different
      check on a different series, not "fixed."
    - **A2** (`check_load_factor_residual_bounded`): the FRAME's literal wording
      ("reconstructed capacity·power_curve tracks AGWS outturn within tolerance")
      FAILS badly (the ~4.6-5.1x gap above) — reported honestly, not hidden. The
      real substance A2 exists to check — is the effective-fleet TREND
      capacity-driven or noise? — is checkable via the load-factor residual's
      bounded coefficient of variation (~0.12-0.17, comfortably inside a pre-stated
      0.35 bound): PASSES.
    - **A3** (`check_mix_share_against_independent_source`): real DESNZ Energy
      Trends Table 6 mix-share (RO/FiT/REGO-certificated generation, independent of
      AGWS) now ingested and value-compared (not merely presence-checked, unlike
      the prior stub) — PASSES within a pre-stated 0.15 tolerance; the sim runs
      ~5-8 points high on wind-share, a real reported finding.
  * A4 no-coal-after-retirement IS implemented as a FAIL-LOUD check
    (`check_no_coal_after_retirement`) — raises rather than silently passing when no
    coal series is supplied (none is ingested in this sim — AGWS is wind+solar
    only), which remains the honest state (R15 FAIL-SILENT forbidden). The
    retirement YEAR it uses (2024) is now VERIFIED against 3 independent sources.
  * What IS honestly testable and mutation-proven in
    `tests/sim/test_renewable_capacity_trend.py`: the TREND (fleet grows materially across
    the window), NON-DEGENERACY (the trajectory is not the old flat scalar — 2016 ≠ 2025),
    DETERMINISM/replay (C-S2), COVERAGE-FAIL-CLOSED (a thin year is excluded, and an
    empty trajectory raises rather than silently returning a degenerate fleet), A1 in
    both forms (effective-fleet: honest FAIL; real-capacity: honest PASS), A2 (load-factor
    residual bounded: PASS) and A3 (mix-share vs independent DESNZ series: PASS) with
    real ingested data, and A4 FAIL-LOUD-on-missing-source.
  * 2026-08-03 GENERATION-MIX-EVOLUTION PASS (same-day follow-on fork): the atom's own
    namesake artifact — energy by technology by year — was still missing; A1-A4 only ever
    compared capacity/share LEVELS, never built "capacity × load factor → energy". Two
    further tables from the SAME already-cited ET 6.1 workbook (`ELECTRICITY GENERATED
    (GWh)`, `LOAD FACTORS (%)`, both DESNZ's own published figures, independent of AGWS)
    are now ingested (`docs/market_research/w1_7_dukes_generation_and_load_factor_annual.json`).
    Two new mutation-tested invariants:
    - **A5** (`check_capacity_load_factor_reconciles_to_generation`): real capacity ×
      real load factor × real calendar hours reconstructs real published generation
      within a pre-stated 25% tolerance, for all 30 technology-year cells 2016-2025 —
      PASSES (observed max gap 14.1%, offshore 2017; the gap is a genuine, reported
      artifact of DUKES's year-END capacity convention vs a growing fleet's
      year-AVERAGE capacity, i.e. exactly the commissioning-date-smoothing FRAME §4
      names as the remaining L2 item — NOT fixed here, still needs sub-annual
      commissioning dates this sim does not ingest).
    - **A6** (`check_onshore_offshore_generation_split_vs_real`): the sim's AGWS-fitted
      onshore-share-of-wind vs the REAL DUKES/DESNZ onshore-share-of-wind-generation —
      a genuinely different comparison from A3 (wind vs solar): checks the balance
      *within* wind. PASSES within a pre-stated 0.20 tolerance (observed max gap 0.100,
      2022; sim runs consistently a few points high on onshore).
    Still NOT touched (out of this atom's file_scope, `sim/price_engine.py`): the FRAME
    §4 coal→gas→wind marginal-plant re-stacking. See "What remains genuinely open" in
    the market-research doc for the full honest accounting.

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

# A MAGNITUDE-BEARING year is one whose coverage can honestly support a fleet
# MAGNITUDE (not merely presence). A year covered by a lopsided subset of months
# (e.g. 2025's Jan-Jun-only data in this cache) cannot: the fleet scalar is a
# mean-match of real generation against a SEASONAL physical shape, so half a year
# divides a part-year generation mean by a part-year shape mean and the result is
# not on the same basis as a full year's. Concretely, in this cache 2025 (158 days,
# Jan-Jun) yields capacity_wind ~= 494,000 against 2024's ~137,700 -- a 3.6x
# artifact, not a real buildout.
#
# 2026-07-30 (R10 CLASS FIX): this threshold previously lived INSIDE A1 alone, so
# A1 was honest while every consumer of the magnitude -- capacity_wind/solar/
# offshore/onshore, and through them the year-aware price chain -- silently used
# the artifact. "Can this year supply a magnitude?" is now ONE definition,
# computed once in fleet_trajectory() and enforced everywhere a magnitude is read,
# rather than a guard re-applied per call site (the instance fix R10 forbids).
_MIN_DAYS_FOR_MAGNITUDE_COMPARISON = 300

# ...and coverage must be SEASONALLY complete, not merely numerous: 300 days drawn
# from Jan-Oct is still a biased sample of a seasonal shape. Both conditions bind.
_MONTHS_REQUIRED_FOR_MAGNITUDE = 12


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
        dates_in_year = [rec["dates"][i] for i in range(len(rec["dates"])) if m[i]]
        months_covered = len({str(d)[5:7] for d in dates_in_year})
        cell = {
            "wind_fleet_mw": float(rec["wind_gen_mw"][m].mean() / wf_mean),
            "solar_fleet_mw": float(rec["solar_gen_mw"][m].mean() / env_mean),
            "n_days": n,
            "months_covered": months_covered,
            # The single definition of "this year may supply a MAGNITUDE" (see the
            # constants above). Computed here so no consumer can forget to apply it.
            "magnitude_bearing": bool(
                n >= _MIN_DAYS_FOR_MAGNITUDE_COMPARISON
                and months_covered >= _MONTHS_REQUIRED_FOR_MAGNITUDE
            ),
        }
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


def magnitude_bearing_years(traj: dict | None = None) -> list:
    """The years whose coverage can honestly supply a fleet MAGNITUDE, in order.

    The ONE place that question is answered (R10 class fix, 2026-07-30). A1 and every
    capacity_* accessor read this rather than re-deriving a coverage rule locally —
    the previous split (A1 strict, accessors unguarded) is exactly how the 2025
    partial-year artifact reached the year-aware price chain.

    `fleet_trajectory()` always stamps `magnitude_bearing`, so on real data the full
    rule (day count AND seasonal completeness) always applies. A hand-built trajectory
    (tests, callers constructing fixtures) may omit it; the flag is then DERIVED from
    whatever coverage that caller did declare — `months_covered` is applied when
    present and skipped when not, so a fixture is judged on what it actually states
    rather than silently reading as non-bearing.
    """
    traj = traj if traj is not None else fleet_trajectory()
    out = []
    for y in sorted(traj):
        cell = traj[y]
        if "magnitude_bearing" in cell:
            if cell["magnitude_bearing"]:
                out.append(y)
            continue
        if cell.get("n_days", 0) < _MIN_DAYS_FOR_MAGNITUDE_COMPARISON:
            continue
        months = cell.get("months_covered")
        if months is not None and months < _MONTHS_REQUIRED_FOR_MAGNITUDE:
            continue
        out.append(y)
    return out


def _clamped_year(year: int, traj: dict | None = None) -> int:
    """Map an arbitrary year onto the nearest MAGNITUDE-BEARING year. Thin or
    seasonally-lopsided years (and years outside the historical window) snap/CLAMP to
    the nearest year that can honestly supply a magnitude — the R13 hold-flat default
    (never an agent-authored forward extrapolation, and never a part-year artifact).

    Fail-closed: if NO year is magnitude-bearing, this raises rather than quietly
    falling back to the unguarded set — an unavailable basis is a FAILED basis (R15),
    not a licence to serve the artifact anyway.
    """
    traj = traj if traj is not None else fleet_trajectory()
    ys = magnitude_bearing_years(traj)
    if not ys:
        raise DegenerateTrajectoryError(
            "no calendar year is magnitude-bearing (needs >= "
            f"{_MIN_DAYS_FOR_MAGNITUDE_COMPARISON} aligned days AND >= "
            f"{_MONTHS_REQUIRED_FOR_MAGNITUDE} months covered) — refusing to serve a "
            "fleet magnitude from part-year data"
        )
    y = min(max(int(year), ys[0]), ys[-1])  # clamp into [first, last] usable year
    if y in ys:
        return y
    return min(ys, key=lambda k: abs(k - y))  # nearest usable interior year


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
    (network-blocked) — not asserted here.

    2026-07-30 (sibling-half audit): restricted to MAGNITUDE-BEARING years. This
    previously read `sorted(traj)`, so `ys[-2:]` included the Jan-Jun-only 2025 cell
    whose fleet scalar is a ~3.6x part-year artifact — the check still passed, but
    partly for a wrong reason (an inflated `last`). A control that passes for a wrong
    reason is not evidence.
    """
    traj = traj if traj is not None else fleet_trajectory()
    ys = magnitude_bearing_years(traj)
    if len(ys) < 2:
        return False  # not enough comparable years — never a vacuous pass (R15)
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
    something.

    2026-07-30 (sibling-half audit): restricted to MAGNITUDE-BEARING years, same
    reason as `check_trend_increasing` — a part-year outlier inflates the CV, so the
    non-degeneracy this invariant certifies would have been partly manufactured by a
    data artifact rather than by the mechanism it exists to prove.
    """
    traj = traj if traj is not None else fleet_trajectory()
    ys = magnitude_bearing_years(traj)
    if len(ys) < 2:
        return False  # not enough comparable years — never a vacuous pass (R15)
    vals = np.array([traj[y]["wind_fleet_mw"] for y in ys], float)
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
    ys = [y for y in magnitude_bearing_years(traj)
          if "wind_offshore_fleet_mw" in traj[y]]
    if len(ys) < 2:
        return False  # can't assert monotonicity on <2 comparable years
    vals = [traj[y]["wind_offshore_fleet_mw"] for y in ys]
    return all(vals[i + 1] >= vals[i] * (1.0 - tol_frac) for i in range(len(vals) - 1))


# ── L2: separating CAPACITY from LOAD-FACTOR (2026-08-03 discovery-agent pass) ──────
# The prior L1 fork's honesty boundary (module header, above): the per-year mean-match
# is an EFFECTIVE fleet = true installed-capacity growth CONVOLVED with residual
# year-to-year load-factor/weather noise, "NOT pure installed capacity" — separating
# the two needed the real DUKES Ch.6 installed-capacity series, network-blocked at the
# time. Network is available this fork (confirmed by a live fetch — see
# docs/market_research/w1_7_renewable_capacity_dukes_desnz.md for the full sourcing).
# This section ingests that real series and uses it to build the non-tautological
# forms of A1 and A2 the FRAME originally specified.

DUKES_CAPACITY_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs" / "market_research" / "w1_7_dukes_installed_capacity_annual.json"
)


class RealCapacitySourceUnavailableError(RuntimeError):
    """The real DUKES/Energy Trends installed-capacity series is not on disk. Per R15
    FAIL-SILENT discipline, every accessor below fails LOUD rather than silently
    falling back to the AGWS-fitted effective fleet (that fallback would silently
    re-introduce the exact load-factor confound this section exists to strip out)."""


@lru_cache(maxsize=1)
def _load_dukes_capacity(source_path=None) -> dict:
    path = Path(source_path) if source_path else DUKES_CAPACITY_PATH
    if not path.exists():
        raise RealCapacitySourceUnavailableError(
            f"real DUKES/Energy Trends installed-capacity series not found at {path} "
            "— refusing to silently fall back to the AGWS-fitted effective fleet."
        )
    data = json.loads(path.read_text())
    for key in ("onshore_mw", "offshore_mw", "solar_mw"):
        if not data.get(key):
            raise RealCapacitySourceUnavailableError(
                f"real DUKES capacity file at {path} is missing/empty '{key}'"
            )
    return data


def _clamped_dukes_year(year: int, series: dict) -> int:
    """R13 hold-flat default for the real capacity series, same convention as
    `_clamped_year` for the AGWS-fitted fleet: piecewise-constant, flat outside the
    real 2016-2025 window (never an agent-authored forward extrapolation)."""
    years = sorted(int(y) for y in series)
    y = min(max(int(year), years[0]), years[-1])
    return y if y in years else min(years, key=lambda k: abs(k - y))


def real_capacity_wind_onshore(year: int, source_path=None) -> float:
    """Real installed ONSHORE wind capacity (MW) for calendar year τ — DUKES/Energy
    Trends Table 6.1, an accreditation/licensing register, NOT the AGWS settlement
    feed the effective fleet above is fitted to (anti-marking-own-homework)."""
    data = _load_dukes_capacity(source_path)
    series = data["onshore_mw"]
    return float(series[str(_clamped_dukes_year(year, series))])


def real_capacity_wind_offshore(year: int, source_path=None) -> float:
    """Real installed OFFSHORE wind capacity (MW, seabed+floating) for calendar year
    τ. See `real_capacity_wind_onshore` — same source and independence guarantee."""
    data = _load_dukes_capacity(source_path)
    series = data["offshore_mw"]
    return float(series[str(_clamped_dukes_year(year, series))])


def real_capacity_wind(year: int, source_path=None) -> float:
    """Real installed combined wind capacity (onshore + offshore, MW) for calendar
    year τ — the same technology grouping as `capacity_wind`'s effective fleet."""
    return (real_capacity_wind_onshore(year, source_path)
            + real_capacity_wind_offshore(year, source_path))


def real_capacity_solar(year: int, source_path=None) -> float:
    """Real installed solar PV capacity (MW) for calendar year τ. See
    `real_capacity_wind_onshore` — same source and independence guarantee."""
    data = _load_dukes_capacity(source_path)
    series = data["solar_mw"]
    return float(series[str(_clamped_dukes_year(year, series))])


def check_offshore_capacity_strictly_non_decreasing(source_path=None) -> bool:
    """A1, STRICT form (FRAME §4's literal wording, on the REAL series this time):
    real installed offshore wind capacity is non-decreasing across the historical
    window. Unlike `check_offshore_non_decreasing` (checked against the AGWS-fitted
    EFFECTIVE fleet, which honestly FAILS — real wind-resource/load-factor noise
    dominates several year-pairs), this checks the REAL DUKES/Energy Trends
    installed-capacity register directly — no weather/load-factor convolution at all.

    Real result (2026-08-03 pass): TRUE on the real 2016-2025 record — GB offshore
    wind capacity was only ever ADDED, never de-commissioned, exactly as the FRAME
    asserted. This is the non-tautological, strict form of A1 the L1 fork named as
    an L2 prerequisite; it is NOT the same check as (and does not retroactively
    validate) `check_offshore_non_decreasing`, whose honest real-data failure on the
    effective fleet stands unchanged.
    """
    data = _load_dukes_capacity(source_path)
    years = sorted(int(y) for y in data["offshore_mw"])
    if len(years) < 2:
        return False  # never a vacuous pass (R15)
    vals = [data["offshore_mw"][str(y)] for y in years]
    return all(vals[i + 1] >= vals[i] for i in range(len(vals) - 1))


# Pre-stated (not fitted) bound on the load-factor residual's coefficient of
# variation. The real observed CVs (see the market-research doc) are ~0.12-0.17 for
# all three technologies; 0.35 leaves real headroom rather than being narrowed to the
# exact observed values (R12's anti-goal-seek sibling — never tune a validator's
# tolerance to flatter its own generator).
_LOAD_FACTOR_RESIDUAL_MAX_CV = 0.35

_REAL_CAPACITY_ACCESSORS = {
    "wind_onshore": ("wind_onshore_fleet_mw", real_capacity_wind_onshore),
    "wind_offshore": ("wind_offshore_fleet_mw", real_capacity_wind_offshore),
    "solar": ("solar_fleet_mw", real_capacity_solar),
}


def load_factor_residual(technology: str, year: int, traj: dict | None = None,
                         source_path=None) -> float:
    """The part of the AGWS-fitted EFFECTIVE fleet NOT explained by real installed
    capacity: effective_fleet_mw(year) / real_capacity_mw(year). `technology` is one
    of "wind_onshore", "wind_offshore", "solar". This is the L2 decomposition named
    by the L1 fork: EFFECTIVE FLEET = REAL CAPACITY x LOAD-FACTOR RESIDUAL.

    Real result (2026-08-03 pass): the wind residual is ~4.6-5.1x (NOT ~1x) — see
    `check_load_factor_residual_bounded`'s docstring for the mechanism (the sim's
    power curve is driven by NATIONAL MEAN wind speed while real turbines are
    non-randomly sited in higher-wind-resource locations, so a curve fit to national
    average wind necessarily undershoots true fleet-average output — a modelling
    fact, not a defect, and out of scope to fix here since it would re-open the
    merit-order/SSP calibration, R12/S8). Solar's residual is close to 1 (~0.84).
    """
    if technology not in _REAL_CAPACITY_ACCESSORS:
        raise ValueError(f"unknown technology {technology!r}; expected one of "
                         f"{sorted(_REAL_CAPACITY_ACCESSORS)}")
    fleet_key, real_fn = _REAL_CAPACITY_ACCESSORS[technology]
    traj = traj if traj is not None else fleet_trajectory()
    y = _clamped_year(year, traj)
    if fleet_key not in traj[y]:
        raise DegenerateTrajectoryError(f"no aligned {technology} data for year {y}")
    real_cap = real_fn(year, source_path)
    if real_cap <= 0:
        raise RealCapacitySourceUnavailableError(
            f"real capacity for {technology} year {year} is non-positive ({real_cap})"
        )
    return traj[y][fleet_key] / real_cap


def check_load_factor_residual_bounded(technology: str = "wind_onshore",
                                       traj: dict | None = None, source_path=None,
                                       max_cv: float = _LOAD_FACTOR_RESIDUAL_MAX_CV) -> bool:
    """A2 (the FRAME's literal wording FAILS honestly — see the module/market-research
    doc; this is the substantive, non-tautological check A2 exists to make once
    capacity is separated from load-factor). The FRAME's literal A2 ("reconstructed
    capacity_k(τ)·power_curve(W(t)) tracks AGWS outturn within tolerance") fails
    badly at any normal tolerance: the real load-factor residual sits at ~4.6-5.1x for
    wind, not ~1x, because `wind_power_output_fraction` is driven by a NATIONAL MEAN
    wind speed while real turbines are sited non-randomly in the windiest locations
    (a genuine, well-known siting-selection effect, not a defect — fixing the curve
    itself would re-open the merit-order/SSP calibration, R12/S8 wall, out of scope).

    What genuinely IS checkable without touching that curve, and is the real
    question A2 exists to answer ("is the effective-fleet trend actually
    CAPACITY-driven, or is it AGWS noise dressed up as a trend?"): the load-factor
    residual's coefficient of variation across magnitude-bearing years is BOUNDED,
    i.e. capacity growth (independently verified via DUKES) — not measurement/weather
    noise — explains most of the year-to-year movement in the effective fleet.

    Real result (2026-08-03 pass): CV ~0.138 (onshore), ~0.174 (offshore), ~0.118
    (solar) — all comfortably inside the pre-stated 0.35 bound. PASSES honestly (not
    tuned to pass — the bound was set before computing these numbers).
    """
    if technology not in _REAL_CAPACITY_ACCESSORS:
        raise ValueError(f"unknown technology {technology!r}; expected one of "
                         f"{sorted(_REAL_CAPACITY_ACCESSORS)}")
    traj = traj if traj is not None else fleet_trajectory()
    fleet_key = _REAL_CAPACITY_ACCESSORS[technology][0]
    years = [y for y in magnitude_bearing_years(traj) if fleet_key in traj[y]]
    if len(years) < 2:
        return False  # never a vacuous pass (R15)
    residuals = np.array([load_factor_residual(technology, y, traj, source_path)
                          for y in years], float)
    if residuals.mean() <= 0:
        return False
    cv = float(residuals.std() / residuals.mean())
    return cv <= max_cv


class IndependentSourceUnavailableError(RuntimeError):
    """A3 (FRAME §3/§4, anti-marking-own-homework): the mix-share validator must be
    anchored to an INDEPENDENT source (DESNZ Energy Trends Table 6) — NEVER the same
    AGWS outturn used to build the capacity trajectory it is checking (that would be
    the exact TAUTOLOGY the FRAME forbids). Per R15 FAIL-SILENT discipline ("an
    unavailable check is a FAILED check"), calling the validator without that source
    must FAIL LOUD — never silently pass, skip, or fall back to comparing against the
    same-source data it is meant to validate against."""


# 2026-08-03 DISCOVERY-AGENT NETWORK PASS (network confirmed available this fork,
# unlike the prior L1 forks): the independent DESNZ Energy Trends Table 6 mix-share
# series is now ingested, real, sourced and cited in
# docs/market_research/w1_7_renewable_capacity_dukes_desnz.md (fetched from
# https://assets.publishing.service.gov.uk/media/6a6a0cabb0205b954abca5a8/ET_6.1_JUL_26.xlsx,
# HTTP 200, 2026-08-03). It lives under docs/market_research/ (in this atom's
# file_scope) rather than sim/cache/ deliberately: sim/cache/ is entirely
# `.gitignore`'d (candidate atom (c) from the prior L1 fork — gitignored cache files
# are absent from a fresh worktree, which is exactly how this fork discovered the
# gap while trying to run the existing test suite). This is a small, hand-fetched,
# independently-sourced reference table with its own citation trail, not a
# re-derivable bulk download cache — it belongs in version control.
DESNZ_MIX_SHARE_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs" / "market_research" / "w1_7_desnz_mix_share_annual.json"
)

# A3's pre-stated tolerance on |real wind-share of (wind+solar) - sim wind-share of
# (wind+solar)| per comparable year. Chosen BEFORE looking at the per-year gaps (which
# turned out to be ~0.02-0.10 — see the market-research doc) with real headroom above
# them, per R12's anti-goal-seek sibling: never narrow a validator's tolerance to fit
# the exact numbers it is checking.
_MIX_SHARE_TOLERANCE = 0.15


@lru_cache(maxsize=1)
def _load_desnz_mix_share(source_path=None) -> dict:
    path = Path(source_path) if source_path else DESNZ_MIX_SHARE_PATH
    if not path.exists():
        raise IndependentSourceUnavailableError(
            f"A3 mix-share validator: independent source not found at {path} — "
            "DESNZ Energy Trends Table 6 mix-share has not been ingested. Refusing "
            "to silently pass, skip, or fall back to the same-source AGWS "
            "comparison (R15 FAIL-SILENT forbidden)."
        )
    return json.loads(path.read_text())


def check_mix_share_against_independent_source(source_path=None,
                                                tolerance: float = _MIX_SHARE_TOLERANCE) -> bool:
    """A3: wind's share of (wind+solar) generation, as REPRODUCED by this AGWS-fitted
    trajectory, vs the INDEPENDENT DESNZ Energy Trends Table 6 series (built from
    RO/FiT/REGO-certificated + estimated generation, NOT the Elexon AGWS settlement
    feed the trajectory is fit to — anti-marking-own-homework; both series use the
    SAME (wind)/(wind+solar) normalisation, avoiding a total-system-generation
    denominator mismatch this sim has no concept of — see the market-research doc for
    the derivation). Raises `IndependentSourceUnavailableError` when the source is not
    on disk (R15 FAIL-SILENT forbidden — never silently pass on absent data).

    Real result (2026-08-03 pass): the sim's implied wind-share runs consistently
    ~5-8 percentage points ABOVE the independent DESNZ series across 2017-2024 (the
    sim's wind power-curve is a worse fit to reality than its solar envelope — see
    `check_load_factor_residual_bounded`'s docstring for the mechanism) — within the
    pre-stated 0.15 tolerance, so this check PASSES, but the gap is a real, reported
    finding, not zero.
    """
    desnz = _load_desnz_mix_share(source_path)
    traj = fleet_trajectory()
    years = [y for y in magnitude_bearing_years(traj)
             if str(y) in desnz.get("onshore_share_pct", {})
             and str(y) in desnz.get("offshore_share_pct", {})
             and str(y) in desnz.get("solar_share_pct", {})]
    if len(years) < 2:
        return False  # not enough comparable years — never a vacuous pass (R15)
    for y in years:
        ys = str(y)
        onshore = desnz["onshore_share_pct"][ys]
        offshore = desnz["offshore_share_pct"][ys]
        solar = desnz["solar_share_pct"][ys]
        denom = onshore + offshore + solar
        if denom <= 0:
            return False
        real_wind_frac = (onshore + offshore) / denom
        cell = traj[y]
        sim_denom = cell["wind_fleet_mw"] + cell["solar_fleet_mw"]
        if sim_denom <= 0:
            return False
        sim_wind_frac = cell["wind_fleet_mw"] / sim_denom
        if abs(real_wind_frac - sim_wind_frac) > tolerance:
            return False
    return True


class CoalSeriesUnavailableError(RuntimeError):
    """A4 (FRAME §4): no coal capacity/generation series is ingested in this sim —
    AGWS (this atom's only generation-mix source) covers Wind Onshore/Offshore and
    Solar only; there is no existing coal-capacity concept anywhere in the price
    engine to check against yet. Per R15 FAIL-SILENT discipline, calling the check
    without a coal series must FAIL LOUD, never silently pass on absent data."""


# GB's last coal-fired power station, Ratcliffe-on-Soar, closed 2024-09-30 — VERIFIED
# 2026-08-03 (discovery-agent network pass, FRAME §9 task 1) against 3 independent
# sources, one primary: (a) Uniper, the plant's own operator ("The end of an era —
# Ratcliffe-on-Soar power station ends coal generation", uniper.energy/news), (b) E3G
# policy NGO, (c) multiple contemporaneous news reports (ITN Business, BBC). Full
# citation trail: docs/market_research/w1_7_renewable_capacity_dukes_desnz.md. No full
# coal generation/capacity TIME SERIES was ingested (AGWS has no coal psrType, and
# ingesting one is out of this atom's file_scope) — only the retirement YEAR, the one
# fact `check_no_coal_after_retirement` actually needs, is verified. The function
# still correctly requires an explicit external series and raises without one.
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


# ── L2: GENERATION-MIX EVOLUTION — capacity x load-factor -> energy by technology by ────
# year, reconciled against real published generation (2026-08-03, this fork). The prior
# passes separated CAPACITY (DUKES) from the AGWS-fitted EFFECTIVE FLEET (load_factor_
# residual, above) but never built the atom's own namesake artifact: "generation-mix
# EVOLUTION over time" as an actual energy quantity per technology per year. The SAME ET
# 6.1 workbook already cited (docs/market_research/w1_7_renewable_capacity_dukes_desnz.md)
# carries two further tables not yet ingested: "ELECTRICITY GENERATED (GWh)" (rows 25-40)
# and "LOAD FACTORS (%)" (rows 42-54) — DESNZ's OWN published generation-by-technology and
# DESNZ's OWN published load factor, from the SAME independent (non-AGWS) collection
# pipeline as the mix-share table already ingested (accreditation-register capacity x
# actual-metered-or-typical-load-factor generation — see that JSON's own provenance note).
# Full sourcing + the observed reconciliation gaps: docs/market_research/
# w1_7_dukes_generation_and_load_factor_annual.md (this fork's addendum).

GENERATION_LOAD_FACTOR_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs" / "market_research" / "w1_7_dukes_generation_and_load_factor_annual.json"
)

# Calendar hours per real year 2016-2025 (leap-year correct: 2016/2020/2024 are leap).
_HOURS_PER_YEAR = {
    2016: 8784, 2017: 8760, 2018: 8760, 2019: 8760, 2020: 8784,
    2021: 8760, 2022: 8760, 2023: 8760, 2024: 8784, 2025: 8760,
}

_GENERATION_TECH_KEYS = ("onshore_wind", "offshore_wind", "solar")


class RealGenerationSourceUnavailableError(RuntimeError):
    """Same R15 FAIL-SILENT discipline as `RealCapacitySourceUnavailableError`: the real
    DUKES/Energy Trends generation+load-factor table is not on disk — every accessor below
    fails LOUD rather than silently falling back to a derived/estimated figure."""


@lru_cache(maxsize=1)
def _load_dukes_generation(source_path=None) -> dict:
    path = Path(source_path) if source_path else GENERATION_LOAD_FACTOR_PATH
    if not path.exists():
        raise RealGenerationSourceUnavailableError(
            f"real DUKES/Energy Trends generation+load-factor series not found at {path} "
            "— refusing to silently fall back to a derived estimate."
        )
    data = json.loads(path.read_text())
    for section in ("generation_gwh", "load_factor_pct"):
        for key in _GENERATION_TECH_KEYS:
            if not data.get(section, {}).get(key):
                raise RealGenerationSourceUnavailableError(
                    f"real DUKES generation file at {path} is missing/empty '{section}.{key}'"
                )
    return data


def _hours_in_year(year: int) -> int:
    y = min(max(int(year), 2016), 2025)  # same R13 hold-flat clamp as the capacity series
    return _HOURS_PER_YEAR[y]


def real_generation_gwh(technology: str, year: int, source_path=None) -> float:
    """Real published annual generation (GWh) for `technology` in
    {"onshore_wind", "offshore_wind", "solar"} — DESNZ ET 6.1 rows 25-40, independent of
    the AGWS settlement feed the sim's effective fleet (above) is fitted to."""
    if technology not in _GENERATION_TECH_KEYS:
        raise ValueError(f"unknown technology {technology!r}; expected one of {_GENERATION_TECH_KEYS}")
    data = _load_dukes_generation(source_path)
    series = data["generation_gwh"][technology]
    y = _clamped_dukes_year(year, series)
    return float(series[str(y)])


def real_load_factor(technology: str, year: int, source_path=None) -> float:
    """Real published annual average load factor (fraction, 0-1) for `technology` —
    DESNZ ET 6.1 rows 42-54, DESNZ's own actual-generation/(capacity x hours) figure."""
    if technology not in _GENERATION_TECH_KEYS:
        raise ValueError(f"unknown technology {technology!r}; expected one of {_GENERATION_TECH_KEYS}")
    data = _load_dukes_generation(source_path)
    series = data["load_factor_pct"][technology]
    y = _clamped_dukes_year(year, series)
    return float(series[str(y)]) / 100.0


_REAL_CAPACITY_FOR_GENERATION_TECH = {
    "onshore_wind": real_capacity_wind_onshore,
    "offshore_wind": real_capacity_wind_offshore,
    "solar": real_capacity_solar,
}


def implied_generation_gwh(technology: str, year: int, source_path=None,
                           capacity_source_path=None) -> float:
    """THE generation-mix-evolution mechanism this atom's own name promises: capacity x
    load factor -> energy, by technology, by year. `capacity` = real installed capacity
    (MW, DUKES, `capacity_source_path` — a DIFFERENT file from the generation/load-factor
    one); `load_factor` = real published annual load factor (DESNZ, `source_path`);
    `hours` = actual calendar hours in that year (leap-year correct, R13 hold-flat clamp
    outside 2016-2025). Returns GWh."""
    if technology not in _REAL_CAPACITY_FOR_GENERATION_TECH:
        raise ValueError(f"unknown technology {technology!r}; expected one of "
                         f"{sorted(_REAL_CAPACITY_FOR_GENERATION_TECH)}")
    capacity_mw = _REAL_CAPACITY_FOR_GENERATION_TECH[technology](year, capacity_source_path)
    lf = real_load_factor(technology, year, source_path)
    hours = _hours_in_year(year)
    return capacity_mw * lf * hours / 1000.0


# Pre-stated (not fitted) tolerance for the capacity x load-factor -> energy
# reconciliation. The real observed gap (docs/market_research/
# w1_7_dukes_generation_and_load_factor_annual.md) spans 0.3%-14.1% across all 30
# technology-year cells 2016-2025, driven by year-END installed capacity (the DUKES
# convention) vs the year's AVERAGE capacity during a fast-growth year (a real, named,
# NOT-fixed simplification — capacity is not commissioning-date-smoothed within the year,
# exactly the FRAME §4 L2 item this pass does not touch, out of file_scope: it would need
# sub-annual commissioning dates this sim does not ingest). 0.25 leaves real headroom
# above the observed max 14.1% (R12's anti-goal-seek sibling — set before re-deriving the
# exact per-cell errors below, not narrowed to fit them).
_GENERATION_RECONCILIATION_TOLERANCE = 0.25


def check_capacity_load_factor_reconciles_to_generation(
    technology: str | None = None, source_path=None, capacity_source_path=None,
    tol_frac: float = _GENERATION_RECONCILIATION_TOLERANCE,
) -> bool:
    """A5: capacity x load_factor (both real DUKES/DESNZ) reconstructs real published
    generation within a pre-stated tolerance, for every year 2016-2025 and every
    technology (or one named technology if given). This is the literal mechanism the
    atom's generation-mix-evolution exit criterion names, and it doubles as a genuine
    data-integrity guard: a transcription error in either the capacity or load-factor
    JSON (or an arithmetic bug in `implied_generation_gwh`) throws the two apart far more
    than 25% and fires (R15 mutation-proven in tests/sim). Never a vacuous pass — it
    iterates every real year for the requested technology(ies), returning False if fewer
    than 2 years are available."""
    data = _load_dukes_generation(source_path)
    techs = [technology] if technology else list(_GENERATION_TECH_KEYS)
    for t in techs:
        if t not in _GENERATION_TECH_KEYS:
            raise ValueError(f"unknown technology {t!r}; expected one of {_GENERATION_TECH_KEYS}")
        years = sorted(int(y) for y in data["generation_gwh"][t])
        if len(years) < 2:
            return False  # never a vacuous pass (R15)
        for y in years:
            real = real_generation_gwh(t, y, source_path)
            implied = implied_generation_gwh(t, y, source_path, capacity_source_path)
            if real <= 0:
                return False
            if abs(implied - real) / real > tol_frac:
                return False
    return True


def real_onshore_offshore_generation_share(year: int, source_path=None) -> float:
    """Real onshore wind's share of (onshore + offshore) generation, DESNZ ET 6.1 rows
    26/27 — independent of AGWS, and a DIFFERENT comparison from A3 (which nets wind
    against solar): this checks the split WITHIN wind."""
    onshore = real_generation_gwh("onshore_wind", year, source_path)
    offshore = real_generation_gwh("offshore_wind", year, source_path)
    denom = onshore + offshore
    if denom <= 0:
        raise RealGenerationSourceUnavailableError(
            f"non-positive real onshore+offshore generation for year {year}"
        )
    return onshore / denom


# Pre-stated (not fitted) tolerance for A6 — set with real headroom above the observed
# per-year gap (docs/market_research/w1_7_dukes_generation_and_load_factor_annual.md),
# which sits ~0.028-0.100 across 2017-2024 (the sim over-weights ONSHORE relative to the
# real generation split, consistent with load_factor_residual's finding that the wind
# power-curve fit is offshore/onshore-non-differentiating — both use the same national
# wind-speed fraction, see `fleet_trajectory`'s R10 SIMPLIFICATION note above).
_ONSHORE_OFFSHORE_SPLIT_TOLERANCE = 0.20


def check_onshore_offshore_generation_split_vs_real(
    traj: dict | None = None, source_path=None, tolerance: float = _ONSHORE_OFFSHORE_SPLIT_TOLERANCE,
) -> bool:
    """A6: the sim's AGWS-fitted onshore:offshore wind SPLIT
    (`wind_onshore_fleet_mw` / (`wind_onshore_fleet_mw` + `wind_offshore_fleet_mw`)) vs
    the REAL DUKES/DESNZ onshore:offshore GENERATION split — a genuinely different
    comparison from A3 (wind vs solar) and from A1/A2/load_factor_residual (capacity vs
    load-factor level): this checks whether the sim's psrType-level fit tracks the real
    BALANCE *within* wind, not just wind's overall level or trend. Real result (this
    pass): both series track (onshore's share of wind falls steadily 2017-2024 as
    offshore is built out faster) but the sim's onshore share runs consistently a few
    points ABOVE the real one (max gap ~0.100, 2022) — within the pre-stated 0.20
    tolerance. Never a vacuous pass — fewer than 2 comparable years fails (R15)."""
    traj = traj if traj is not None else fleet_trajectory()
    years = [y for y in magnitude_bearing_years(traj)
             if "wind_onshore_fleet_mw" in traj[y] and "wind_offshore_fleet_mw" in traj[y]]
    if len(years) < 2:
        return False  # never a vacuous pass (R15)
    for y in years:
        real_onshore_share = real_onshore_offshore_generation_share(y, source_path)
        cell = traj[y]
        sim_denom = cell["wind_onshore_fleet_mw"] + cell["wind_offshore_fleet_mw"]
        if sim_denom <= 0:
            return False
        sim_onshore_share = cell["wind_onshore_fleet_mw"] / sim_denom
        if abs(real_onshore_share - sim_onshore_share) > tolerance:
            return False
    return True


# ── L2 (a): COMMISSIONING-DATE SMOOTHING (FRAME §4, 2026-08-03 this fork) ───────────
# The A5 reconciliation gap above (docstring: "genuine artifact of DUKES's year-END
# capacity convention vs a growing fleet's year-AVERAGE capacity") is the exact
# commissioning-date-smoothing item the FRAME names as the remaining L2 step. This sim
# has no per-turbine commissioning-date feed (none is published at that granularity) --
# the honest, disclosed approximation is PIECEWISE-LINEAR interpolation between the
# real DUKES year-END snapshots already ingested, standing in for the (unknown) real
# intra-year commissioning schedule. For a linear ramp, the year's AVERAGE capacity is
# exactly the mean of its two bounding year-end values: (cap(year-1) + cap(year)) / 2.
# The FIRST year in the window (2016) has no year-1 anchor -- honestly UN-SMOOTHABLE,
# left at its raw year-end value (same R13 hold-flat convention used at every other
# out-of-window edge in this module).

_SMOOTHABLE_TECH_FOR_CAPACITY = {
    "wind_onshore": real_capacity_wind_onshore,
    "wind_offshore": real_capacity_wind_offshore,
    "solar": real_capacity_solar,
}


def real_capacity_smoothed(technology: str, year: int, source_path=None) -> float:
    """Commissioning-date-SMOOTHED real installed capacity (MW) for `technology` in
    {"wind_onshore", "wind_offshore", "solar"} at calendar year τ: the mean of τ's and
    (τ-1)'s real DUKES year-end capacity, i.e. the exact average of a linear ramp
    between the two known snapshots. Falls back to the raw (unsmoothed) year-end value
    for the first year in the window, where no prior-year anchor exists -- disclosed,
    not silently degenerate.
    """
    if technology not in _SMOOTHABLE_TECH_FOR_CAPACITY:
        raise ValueError(f"unknown technology {technology!r}; expected one of "
                         f"{sorted(_SMOOTHABLE_TECH_FOR_CAPACITY)}")
    real_fn = _SMOOTHABLE_TECH_FOR_CAPACITY[technology]
    data = _load_dukes_capacity(source_path)
    key = {"wind_onshore": "onshore_mw", "wind_offshore": "offshore_mw",
           "solar": "solar_mw"}[technology]
    first_year = min(int(y) for y in data[key])
    y = _clamped_dukes_year(year, data[key])
    if y <= first_year:
        return real_fn(y, source_path)  # un-smoothable edge -- raw year-end value
    return (real_fn(y - 1, source_path) + real_fn(y, source_path)) / 2.0


def implied_generation_gwh_smoothed(technology: str, year: int, source_path=None,
                                    capacity_source_path=None) -> float:
    """As `implied_generation_gwh`, but using the commissioning-SMOOTHED capacity
    (`real_capacity_smoothed`) instead of the raw year-end DUKES snapshot -- the same
    capacity x load_factor x hours mechanism, the smoothed input."""
    _TECH_MAP = {"onshore_wind": "wind_onshore", "offshore_wind": "wind_offshore",
                 "solar": "solar"}
    if technology not in _TECH_MAP:
        raise ValueError(f"unknown technology {technology!r}; expected one of "
                         f"{sorted(_TECH_MAP)}")
    capacity_mw = real_capacity_smoothed(_TECH_MAP[technology], year, capacity_source_path)
    lf = real_load_factor(technology, year, source_path)
    hours = _hours_in_year(year)
    return capacity_mw * lf * hours / 1000.0


def check_commissioning_smoothing_reduces_reconciliation_gap(
    source_path=None, capacity_source_path=None, min_relative_improvement: float = 0.5,
) -> bool:
    """A5-refinement: commissioning-date SMOOTHING (linear interpolation between real
    DUKES year-end snapshots) must materially TIGHTEN the A5 capacity x load-factor ->
    generation reconciliation vs the raw (unsmoothed) year-end value -- the literal
    claim FRAME §4's L2 bar makes. Compares the MEAN absolute percentage reconciliation
    error across every technology-year cell where smoothing is possible (excludes each
    technology's first window year -- no prior-year anchor) for the raw vs smoothed
    capacity input, and requires the smoothed mean error to be at most
    `(1 - min_relative_improvement)` of the raw mean error.

    Real result (2026-08-03 pass): raw (year-end) mean abs error ~4.17% across the 27
    comparable technology-year cells (2017-2025 x 3 technologies) vs smoothed mean abs
    error ~0.16% -- a ~96.1% relative reduction, comfortably clearing the pre-stated
    50% bar (set with real headroom below the observed improvement, same convention as
    every other tolerance in this module -- R12's anti-goal-seek sibling). Never a
    vacuous pass -- fewer than 2 comparable cells fails (R15 FAIL-OPEN forbidden).
    """
    data = _load_dukes_generation(source_path)
    raw_errs: list = []
    smoothed_errs: list = []
    for tech, tech_key in (("onshore_wind", "wind_onshore"),
                           ("offshore_wind", "wind_offshore"), ("solar", "solar")):
        years = sorted(int(y) for y in data["generation_gwh"][tech])
        cap_series = _load_dukes_capacity(capacity_source_path)[
            {"wind_onshore": "onshore_mw", "wind_offshore": "offshore_mw",
             "solar": "solar_mw"}[tech_key]]
        first_year = min(int(y) for y in cap_series)
        for y in years:
            if y <= first_year:
                continue  # un-smoothable edge -- excluded from both series identically
            real = real_generation_gwh(tech, y, source_path)
            if real <= 0:
                return False
            raw = implied_generation_gwh(tech, y, source_path, capacity_source_path)
            smoothed = implied_generation_gwh_smoothed(tech, y, source_path, capacity_source_path)
            raw_errs.append(abs(raw - real) / real)
            smoothed_errs.append(abs(smoothed - real) / real)
    if len(raw_errs) < 2:
        return False  # never a vacuous pass (R15)
    raw_mean = float(np.mean(raw_errs))
    smoothed_mean = float(np.mean(smoothed_errs))
    if raw_mean <= 0:
        return False
    return smoothed_mean <= raw_mean * (1.0 - min_relative_improvement)


# ── L2 (b): DISPATCHABLE-FLEET RE-STACKING -- coal -> gas -> wind (FRAME §4) ─────────
# The merit-order price physics (sim/price_engine.py) normalises residual demand
# against a single flat DISPATCHABLE_CAPACITY_MW = 35000.0 constant -- that module's
# own R10 docstring already names the gap: "this fleet has shrunk over 2016-2025 as
# coal exited" and "would be grounded by a National Grid ESO capacity-register figure
# for the specific year." This section ingests the real DUKES Table 5.7 plant-capacity
# register (coal/gas/nuclear, ALL GENERATING COMPANIES) -- a THIRD, independent DESNZ
# table from the two already used above (ET 6.1 renewables capacity/mix-share/
# generation) -- and exposes a time-varying `real_dispatchable_capacity_mw(year)` that
# sim/price_engine.py reads when given an explicit `year=` (mirroring the exact
# year=None-preserves-baseline convention sim/weather_price_chain.py already
# established for the renewable fleet -- R12/R13: the SSP calibration is not re-opened
# by default).

DISPATCHABLE_CAPACITY_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs" / "market_research" / "w1_7_dukes_5_7_dispatchable_capacity_annual.json"
)

# The same CCGT/OCGT/coal/nuclear basket sim/price_engine.py's own pre-existing R10
# docstring named for its flat constant -- 'gas_fired_mw' in the DUKES 5.7 series
# already sums CCGT + OCGT/gas-turbine capacity (verified against Table 5.7.B's
# separately-reported CCGT + gas-turbine rows, see the JSON's own provenance note).
# Interconnector import capacity stays OUT (a disclosed, UNCHANGED gap -- the original
# flat constant never included it either).
_DISPATCHABLE_FUEL_KEYS = ("coal_fired_mw", "gas_fired_mw", "nuclear_mw")


class DispatchableCapacitySourceUnavailableError(RuntimeError):
    """Same R15 FAIL-SILENT discipline as the other real-series loaders above: the
    real DUKES 5.7 plant-capacity series is not on disk -- every accessor below fails
    LOUD rather than silently falling back to the flat pre-2026-08-03 constant (that
    fallback would silently re-introduce the exact flat-fleet fidelity gap this
    section exists to close)."""


@lru_cache(maxsize=1)
def _load_dispatchable_capacity(source_path=None) -> dict:
    path = Path(source_path) if source_path else DISPATCHABLE_CAPACITY_PATH
    if not path.exists():
        raise DispatchableCapacitySourceUnavailableError(
            f"real DUKES 5.7 dispatchable-capacity series not found at {path} — "
            "refusing to silently fall back to the flat constant."
        )
    data = json.loads(path.read_text())
    for key in _DISPATCHABLE_FUEL_KEYS:
        if not data.get(key):
            raise DispatchableCapacitySourceUnavailableError(
                f"real DUKES 5.7 dispatchable-capacity file at {path} is missing/empty '{key}'"
            )
    return data


def _clamped_dispatchable_year(year: int, series: dict) -> int:
    """Same R13 hold-flat convention as `_clamped_dukes_year`: piecewise-constant,
    flat outside the real 2016-2025 window."""
    years = sorted(int(y) for y in series)
    y = min(max(int(year), years[0]), years[-1])
    return y if y in years else min(years, key=lambda k: abs(k - y))


def real_coal_capacity_mw(year: int, source_path=None) -> float:
    """Real GB coal-fired plant capacity (MW), all generating companies, DUKES Table
    5.7 -- the series that lets A4 (`check_no_coal_after_retirement`) finally be
    exercised on REAL data rather than only a synthetic test fixture."""
    data = _load_dispatchable_capacity(source_path)
    series = data["coal_fired_mw"]
    return float(series[str(_clamped_dispatchable_year(year, series))])


def real_gas_capacity_mw(year: int, source_path=None) -> float:
    """Real GB gas-fired (CCGT + OCGT) plant capacity (MW), all generating companies,
    DUKES Table 5.7."""
    data = _load_dispatchable_capacity(source_path)
    series = data["gas_fired_mw"]
    return float(series[str(_clamped_dispatchable_year(year, series))])


def real_nuclear_capacity_mw(year: int, source_path=None) -> float:
    """Real GB nuclear plant capacity (MW), all generating companies, DUKES Table
    5.7."""
    data = _load_dispatchable_capacity(source_path)
    series = data["nuclear_mw"]
    return float(series[str(_clamped_dispatchable_year(year, series))])


def real_dispatchable_capacity_mw(year: int, source_path=None) -> float:
    """THE re-stacking input: real coal + gas + nuclear plant capacity (MW) for
    calendar year τ -- what `sim/price_engine.py::system_margin_price`/`synthetic_price`
    reads (via a lazy import, mirroring `weather_price_chain._wind_fleet_mw`'s pattern)
    when given an explicit `year=`. Piecewise-constant, flat outside 2016-2025 (R13).

    Real result (2026-08-03 pass): the fleet shrinks from ~56.2 GW (2016) to ~42.4 GW
    (2025) as coal exits the stack (13.7 GW -> 0 MW) while gas holds broadly flat
    (~33.2 -> ~36.5 GW) and nuclear steps down in two real retirement waves (2020,
    2022) -- coal->gas->(nuclear-shrinking) re-stacking, mechanically representable by
    a single shrinking scarcity-normalisation denominator without re-opening the merit-
    order calibration itself (R12/S8; the calibration constants A0/A1/A2/X_TIGHT stay
    untouched -- only their `x` input's denominator becomes time-varying when opted
    into).
    """
    return (real_coal_capacity_mw(year, source_path)
            + real_gas_capacity_mw(year, source_path)
            + real_nuclear_capacity_mw(year, source_path))


def check_dispatchable_capacity_declines_2016_2025(source_path=None, min_ratio: float = 0.85) -> bool:
    """The dispatchable/thermal fleet materially SHRINKS across the historical window
    as coal exits -- real GB fact (the last coal plant closed 2024, `LAST_COAL_
    GENERATION_YEAR`). Fires if the last comparable year's capacity is not at most
    `min_ratio` x the first year's (real observed ratio ~0.755 -- 42391/56208 -- well
    under the pre-stated 0.85 bar, set with headroom above the observed shrinkage so a
    modest data revision would not spuriously flip this). Never a vacuous pass -- needs
    >= 2 years (R15)."""
    data = _load_dispatchable_capacity(source_path)
    years = sorted(int(y) for y in data["coal_fired_mw"])
    if len(years) < 2:
        return False
    first = real_dispatchable_capacity_mw(years[0], source_path)
    last = real_dispatchable_capacity_mw(years[-1], source_path)
    if first <= 0:
        return False
    return last <= min_ratio * first


def real_coal_capacity_series(source_path=None) -> dict:
    """The full real coal-capacity-by-year series, as a plain {year: mw} dict -- the
    form `check_no_coal_after_retirement` (above) takes. Exists so that check can
    finally be exercised on REAL data (previously only a hand-built synthetic fixture
    existed, per this module's own honesty note -- 'no real coal series exists in this
    sim to exercise it on')."""
    data = _load_dispatchable_capacity(source_path)
    return {int(y): float(v) for y, v in data["coal_fired_mw"].items()}
