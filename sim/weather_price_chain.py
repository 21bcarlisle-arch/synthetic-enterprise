"""W1_6_physics_price_signal (L4) -- price as a DERIVED output of ONE coherent
weather draw. The SIM-SIDE ground truth of the weather coupled-triad.

WHAT THIS IS. The atom's DoD is: "national weather -> national demand +
renewable output -> residual demand -> merit order -> wholesale price (price is
NEVER an independent draw)." `sim/price_engine.py` already owns the last link
(residual demand -> merit-order SSP, the recalibrated residual-demand-scarcity
form). What was missing -- and what this module adds -- is the FIRST half of the
chain that makes price DERIVED FROM WEATHER rather than an exogenous input: the
weather -> (demand, renewable) maps, composed with the price engine so that one
coherent (temperature, wind, cloud) draw produces demand, renewable output,
residual demand, and finally price, mechanistically. A cold-and-still spell then
produces a price spike BY CONSTRUCTION (high heating demand AND low wind output
AND a tight residual served by the convex tail of the merit order), not by an
independent draw -- the single reason a naive sim under-prices winter risk.

R13 BASELINE (blind to company P&L). Every relationship here is fit to the REAL
2016-2025 record (Elexon INDO demand, AGWS wind/solar generation, Open-Meteo
weather), decided for fidelity-to-reality only, never tuned because company
results look a certain way. `sim/price_engine.py`'s constants are unchanged; the
chain refits the same form on the same window with carbon in its floor
(`fit_price_leg`) and passes those coefficients, so no other engine caller moves.

THE THREE FITTED LINKS (all closed-form, deterministic -- C-S2 replay):
  1. DEMAND ~ WEATHER: national demand = base + b_hdd * HDD + b_cdd * CDD, the
     standard degree-day form (HDD = max(0, T_heat - T), CDD = max(0, T - T_cool)).
     OLS on real (Open-Meteo national temperature, Elexon INDO demand). Convex in
     cold -> the heating plateau (D4). R^2 ~ 0.55.
  2. WIND OUTPUT ~ WIND SPEED: fleet_wind_mw * fleet_wind_fraction(wind_speed), the
     turbine curve convolved with a fitted Gaussian on a transferred speed (the
     fleet-aggregate curve, `fit_fleet_curve`, K8 electricity page s.6a), held flat
     from its in-record maximum; the fleet scale MEAN-MATCHED to real AGWS wind.
  3. SOLAR OUTPUT ~ SEASON x CLOUD: fleet_solar_mw * clear_sky(doy) * (1 - cloud),
     a seasonal clear-sky envelope attenuated by cloud, mean-matched to real AGWS
     solar. A named SIMPLIFICATION (R10): a seasonal+cloud proxy, not a fitted
     irradiance model; solar is a small component of residual demand and its
     imperfection barely moves the winter tail (winter solar ~ 0).

THE WALL (CLAUDE.md Architectural Laws -- LOAD-BEARING). Price formation is
SIM-side physics. NOTHING in `company/` or `saas/` may import this module or the
price engine or read residual demand / the merit-order internals -- the company
observes ONLY the published price OUTTURN (as a real supplier reads Elexon SSP).
This module never imports company/saas. The company's approximation of this
chain lives on the far side of the wall in
`company/pricing/weather_price_belief.py` and is measured against this ground
truth by `background/weather_price_triad.py` (the HARNESS, the only layer that
holds both). The belief-vs-truth GAP is the score.

R10 SIMPLIFICATIONS (registered, not hidden):
  * SOLAR is a seasonal x cloud proxy, not a fitted irradiance/PV model.
  * DEMAND is temperature-only (degree-day); no explicit daylight/working-day
    term (weekday/holiday load structure is out of this atom's L3 scope).
  * WIND fleet: on the record, each day takes its own year's fleet (W1_7,
    `renewable_capacity_trend.capacity_wind`, matched on the same curve); a call
    without `year` takes the whole-window scalar. A forward year holds the last
    full year's fleet flat: a capacity path is owed (GAP), never a matched output.
  * CARBON: CPS + the allowance price by month (`merit_order_reconstruction.
    carbon_price_in_month_gbp_per_tonne`) is passed, and the price leg's A0-A2 are
    refitted with it in the floor (`fit_price_leg`); the two ship together, since
    either alone double counts or drops carbon. Forward carbon is the curriculum's.
  * GAS is the monthly TTF proxy (flat within a month); the daily SAP swap is its
    own one-variable arm (area map C2), not bundled here.
  * NEGATIVE/DISCRETE price structure is the engine's (smooth, can go negative in
    oversupply); no discrete stack is modelled (W1_6 FRAME 3.3).

R12 anti-goal-seek. The chain's agreement with real SSP is a DIAGNOSTIC reported
by `chain_vs_real_ssp_mae`, never a target; no constant here is nudged to flatter
it. The cold-still spike is a MEASURED consequence of the composed physics, not a
tuned output.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict

import numpy as np

from sim.price_engine import synthetic_price, wind_power_output_fraction
from sim.weather_tail_demonstration import load_national_daily

_CACHE = Path(__file__).resolve().parent / "cache"

# Degree-day base temperatures (deg C) -- standard GB heating/cooling balance
# points (R10: conventional values, not fitted; heating dominates GB load).
T_HEAT_C: float = 15.5
T_COOL_C: float = 18.0

# Solar seasonal envelope peaks near the summer solstice (~doy 172).
_SOLAR_PEAK_DOY: int = 172

_WINTER_MONTHS = (12, 1, 2)


class DegenerateChainError(ValueError):
    """FAIL-OPEN: a fit asked for on empty/degenerate data raises loud rather
    than returning silent zeros that would read as a passing chain."""


# ---------------------------------------------------------------------------
# Real aligned daily record (the fit + demonstration substrate)
# ---------------------------------------------------------------------------

def _daily_mean_from_periods(records, date_key: str, value_key: str) -> Dict[str, float]:
    agg: Dict[str, list] = defaultdict(list)
    for r in records:
        v = r.get(value_key)
        if v is not None:
            agg[r[date_key]].append(float(v))
    return {d: float(np.mean(vs)) for d, vs in agg.items()}


@lru_cache(maxsize=1)
def load_daily_record() -> Dict[str, np.ndarray]:
    """The real aligned daily national record over the common window: temperature,
    wind speed, cloud, day-of-year, gas price, INDO demand, AGWS wind + solar
    generation, and published SSP. Independent published sources (Open-Meteo
    weather, Elexon demand/generation/price, NBP gas) -- the anti-marking-own-
    homework rule (generator anchors != validator anchors). Cached (parses the
    large AGWS/SSP caches once)."""
    from sim.gas_prices_history import load_nbp_history
    from sim.generation_demand_history import (
        aggregate_renewable_generation,
        aggregate_wind_generation,
    )

    def _load(name):
        return json.loads((_CACHE / name).read_text())

    demand = _daily_mean_from_periods(_load("elexon_demand_full.json"),
                                      "settlementDate", "initialDemandOutturn")
    ssp = _daily_mean_from_periods(_load("elexon_ssp_full.json"),
                                   "settlementDate", "systemSellPrice")
    agws = _load("elexon_agws_full.json")
    wind_hh = aggregate_wind_generation(agws)
    ren_hh = aggregate_renewable_generation(agws)
    wind_by_date: Dict[str, list] = defaultdict(list)
    ren_by_date: Dict[str, list] = defaultdict(list)
    for (dt, _p), mw in wind_hh.items():
        wind_by_date[dt].append(mw)
    for (dt, _p), mw in ren_hh.items():
        ren_by_date[dt].append(mw)
    wind_gen = {d: float(np.mean(v)) for d, v in wind_by_date.items()}
    solar_gen = {d: float(np.mean(ren_by_date[d])) - wind_gen.get(d, 0.0) for d in ren_by_date}
    gas = {r["settlementDate"]: float(r["systemSellPrice"]) for r in load_nbp_history()}

    national, doy, dates = load_national_daily()
    ds = [d.strftime("%Y-%m-%d") for d in dates]
    temp = {ds[i]: float(national["temperature_mean_c"][i]) for i in range(len(ds))}
    wind_speed = {ds[i]: float(national["wind_speed_mean_ms"][i]) for i in range(len(ds))}
    cloud = {ds[i]: float(national["cloud_cover_pct"][i]) for i in range(len(ds))}
    doy_by_date = {ds[i]: int(doy[i]) for i in range(len(ds))}

    common = sorted(set(demand) & set(ssp) & set(wind_gen) & set(temp) & set(gas))
    if len(common) < 1000:
        raise DegenerateChainError(f"too few aligned daily rows: {len(common)}")
    months = np.array([int(d[5:7]) for d in common])
    return {
        "dates": np.array(common),
        "month": months,
        "temperature_c": np.array([temp[d] for d in common]),
        "wind_speed_ms": np.array([wind_speed[d] for d in common]),
        "cloud_pct": np.array([cloud[d] for d in common]),
        "day_of_year": np.array([doy_by_date[d] for d in common]),
        "gas_price": np.array([gas[d] for d in common]),
        "demand_mw": np.array([demand[d] for d in common]),
        "wind_gen_mw": np.array([wind_gen[d] for d in common]),
        "solar_gen_mw": np.array([solar_gen[d] for d in common]),
        "ssp": np.array([ssp[d] for d in common]),
    }


# ---------------------------------------------------------------------------
# The three fitted front links + the composed chain
# ---------------------------------------------------------------------------

def _hdd(temp_c) -> np.ndarray:
    return np.clip(T_HEAT_C - np.asarray(temp_c, float), 0.0, None)


def _cdd(temp_c) -> np.ndarray:
    return np.clip(np.asarray(temp_c, float) - T_COOL_C, 0.0, None)


def _solar_envelope(day_of_year, cloud_pct) -> np.ndarray:
    """Seasonal clear-sky envelope (positive half of a cosine peaking at the
    summer solstice) attenuated by cloud cover -- the unscaled solar shape."""
    doy = np.asarray(day_of_year, float)
    clear = np.clip(np.cos(2.0 * np.pi * (doy - _SOLAR_PEAK_DOY) / 365.0), 0.0, None)
    return clear * (1.0 - np.asarray(cloud_pct, float) / 100.0)


# ---------------------------------------------------------------------------
# The fleet-aggregate power curve (K8: how_the_gb_electricity_price_forms §6a)
# ---------------------------------------------------------------------------
# One turbine's curve on a town 10 m daily mean is not a fleet: it gives zero below 3 m/s and
# 13x its mean at 10 m/s, and it moved the chain's wind 2.2-3.8x the real fleet's MW per m/s
# (64fd7f5f8). Staffell & Pfenninger (2016, Energy 114) model a fleet as the turbine curve
# convolved with a Gaussian, on a corrected speed w' = a*w + b. Here (a, b, sigma) are fitted
# on 2016-2019 only, against AGWS wind normalised by its own calendar-year mean, so the fit sees
# shape and never level (4413f635ab, where this arm was pre-registered and run).
_CURVE_FIT_WINDOW = ("2016-01-01", "2019-12-31")
_GH_X, _GH_W = np.polynomial.hermite_e.hermegauss(41)
_GH_W = _GH_W / _GH_W.sum()
_CURVE_GRID = np.linspace(-15.0, 45.0, 6001)
_CURVE_P = np.array([wind_power_output_fraction(float(v)) for v in _CURVE_GRID])


@dataclass(frozen=True)
class FleetCurve:
    """The fitted aggregate curve, and where it is held flat."""

    a: float
    b_ms: float
    sigma_ms: float
    # Above about 10 m/s the fitted curve falls, because the transfer takes a 12 m/s town day
    # past the turbine's 25 m/s cut-out. The record has 2 days in 3,337 above 10 m/s, so the
    # fall is unconstrained by data: the curve is held at its maximum over the record's range.
    hold_from_ms: float
    hold_fraction: float
    corr_single: float
    corr_aggregate: float
    n_fit_days: int


def _aggregate_unheld(wind_speed_ms, a: float, b: float, sigma: float) -> np.ndarray:
    v = (a * np.atleast_1d(np.asarray(wind_speed_ms, float))[:, None] + b) + sigma * _GH_X[None, :]
    return (np.interp(v, _CURVE_GRID, _CURVE_P) * _GH_W[None, :]).sum(axis=1)


def _normalise_by_year(values: np.ndarray, years: np.ndarray) -> np.ndarray:
    out = np.empty_like(values)
    for y in np.unique(years):
        m = years == y
        out[m] = values[m] / values[m].mean()
    return out


@lru_cache(maxsize=1)
def fit_fleet_curve() -> FleetCurve:
    """Fit (a, b, sigma) on 2016-2019 by coordinate descent from a coarse start grid
    (closed-form inputs, deterministic). The optimiser's start grid and step are search
    settings, not domain values: the fitted triple is what the record says."""
    rec = load_daily_record()
    dates, wspd, wind = rec["dates"], rec["wind_speed_ms"], rec["wind_gen_mw"]
    years = np.array([int(d[:4]) for d in dates])
    fit_m = (dates >= _CURVE_FIT_WINDOW[0]) & (dates <= _CURVE_FIT_WINDOW[1])
    if fit_m.sum() < 365:
        raise DegenerateChainError(f"too few fit-window days for the fleet curve: {fit_m.sum()}")
    target = _normalise_by_year(wind, years)

    def loss(theta):
        a, b, sg = theta
        if a <= 0 or sg <= 0:
            return 1e9
        fr = _aggregate_unheld(wspd, a, b, sg)
        if (fr[fit_m] <= 0).all():
            return 1e9
        norm = _normalise_by_year(np.where(fr > 0, fr, 1e-9), years)
        return float(np.mean((norm[fit_m] - target[fit_m]) ** 2))

    best = None
    for a0 in (1.0, 1.5, 2.0, 2.5):
        for b0 in (-1.0, 0.0, 1.0, 2.0):
            for s0 in (0.5, 1.5, 3.0):
                val = loss((a0, b0, s0))
                if best is None or val < best[0]:
                    best = (val, (a0, b0, s0))
    theta = np.array(best[1], float)
    step = np.array([0.25, 0.5, 0.5])
    for _ in range(60):
        improved = False
        for i in range(3):
            for sgn in (1, -1):
                t = theta.copy()
                t[i] += sgn * step[i]
                v = loss(t)
                if v < best[0]:
                    best, theta, improved = (v, tuple(t)), t, True
        if not improved:
            step = step / 2
    a, b, sg = (float(x) for x in theta)
    grid = np.linspace(0.0, float(wspd.max()), 1001)
    on_grid = _aggregate_unheld(grid, a, b, sg)
    i = int(np.argmax(on_grid))
    single = np.array([wind_power_output_fraction(float(w)) for w in wspd])
    agg = _aggregate_unheld(wspd, a, b, sg)
    return FleetCurve(
        a=a, b_ms=b, sigma_ms=sg,
        hold_from_ms=float(grid[i]), hold_fraction=float(on_grid[i]),
        corr_single=float(np.corrcoef(single, wind)[0, 1]),
        corr_aggregate=float(np.corrcoef(agg, wind)[0, 1]),
        n_fit_days=int(fit_m.sum()),
    )


def fleet_wind_fraction(wind_speed_ms, curve: FleetCurve | None = None) -> np.ndarray:
    """The fleet's output fraction at a national town wind speed (the chain's wind input):
    the aggregate curve, held flat from its in-record maximum upward."""
    c = curve or fit_fleet_curve()
    w = np.atleast_1d(np.asarray(wind_speed_ms, float))
    out = _aggregate_unheld(w, c.a, c.b_ms, c.sigma_ms)
    return np.where(w >= c.hold_from_ms, c.hold_fraction, out)


# ---------------------------------------------------------------------------
# The price leg, refitted with carbon in its floor (d424b78095)
# ---------------------------------------------------------------------------
# price_engine's A0-A2 were fitted against SSP with carbon at zero, so the multiplier carries
# carbon; passing carbon on top double counts it after 2021 (2ce49dcd3). The chain refits the
# same form, on the same half-hourly window and grid point, with CPS + the allowance price in
# the floor, and passes carbon with it. The two ship together: either alone is worse than both.


@dataclass(frozen=True)
class PriceLegParams:
    a0: float
    a1: float
    a2: float
    mae: float
    r2: float
    n_half_hours: int


def carbon_on(date_str: str) -> float:
    """CPS + allowance price (GBP/tCO2) for a record date, from the one carbon table."""
    from sim.merit_order_reconstruction import carbon_price_in_month_gbp_per_tonne
    return carbon_price_in_month_gbp_per_tonne(str(date_str)[:7])


@lru_cache(maxsize=1)
def fit_price_leg() -> PriceLegParams:
    """Refit A0-A2 with carbon in the floor (closed-form least squares, deterministic)."""
    import sim.price_engine as pe
    from simulation.run_phase3b_recalibration import (
        SELECTED_SCARCITY_EXPONENT,
        SELECTED_X_TIGHT,
        _build_dataset,
        _fit_form,
    )

    rows = _build_dataset()
    if len(rows) < 10_000:
        raise DegenerateChainError(f"too few half-hours to refit the price leg: {len(rows)}")
    gas = np.array([r["gas_price"] for r in rows])
    x = (np.array([r["demand_mw"] for r in rows]) - np.array([r["renewable_mw"] for r in rows])) \
        / pe.DISPATCHABLE_CAPACITY_MW
    by_month: Dict[str, float] = {}
    carbon = np.array([by_month.setdefault(r["settlementDate"][:7], carbon_on(r["settlementDate"]))
                       for r in rows])
    floor = (gas + carbon * pe.EF_GAS_TCO2_PER_MWH_TH) / pe.THERMAL_EFFICIENCY
    f = _fit_form(floor, x, np.array([r["ssp"] for r in rows]),
                  SELECTED_X_TIGHT, SELECTED_SCARCITY_EXPONENT)
    return PriceLegParams(a0=f["a0"], a1=f["a1"], a2=f["a2"], mae=f["mae"], r2=f["r2"],
                          n_half_hours=len(rows))


class CarbonRequiredError(ValueError):
    """The chain's price leg was fitted with carbon in its floor, so a call without carbon
    would price with a multiplier that no longer carries it."""


@dataclass(frozen=True)
class ChainParams:
    """The fitted weather->(demand, renewable) constants (R13 baseline). Kept as
    an explicit record so a reviewer sees exactly what was fit and the fit
    quality (R15 independence -- the chain is not a stored magic number)."""

    demand_base_mw: float
    demand_b_hdd: float          # MW per heating-degree-day
    demand_b_cdd: float          # MW per cooling-degree-day
    demand_r2: float
    wind_fleet_mw: float         # scale on the power-curve fraction (mean-matched)
    wind_corr: float
    solar_fleet_mw: float        # scale on the solar envelope (mean-matched)
    solar_corr: float
    n_days: int


@lru_cache(maxsize=1)
def fit_chain() -> ChainParams:
    """Fit the three front links on the real record (closed-form, deterministic).
    DEMAND: OLS degree-day. WIND/SOLAR: mean-matched scale on their physical
    shape (power curve / seasonal envelope). R13 baseline -- fit blind to P&L."""
    rec = load_daily_record()
    hdd, cdd = _hdd(rec["temperature_c"]), _cdd(rec["temperature_c"])
    X = np.column_stack([np.ones(len(hdd)), hdd, cdd])
    coef, *_ = np.linalg.lstsq(X, rec["demand_mw"], rcond=None)
    demand_pred = X @ coef
    r2 = float(1.0 - np.var(rec["demand_mw"] - demand_pred) / np.var(rec["demand_mw"]))

    frac = fleet_wind_fraction(rec["wind_speed_ms"])
    if frac.mean() <= 0:
        raise DegenerateChainError("wind power-curve fraction has zero mean")
    wind_fleet = float(rec["wind_gen_mw"].mean() / frac.mean())
    wind_pred = wind_fleet * frac
    wind_corr = float(np.corrcoef(wind_pred, rec["wind_gen_mw"])[0, 1])

    env = _solar_envelope(rec["day_of_year"], rec["cloud_pct"])
    if env.mean() <= 0:
        raise DegenerateChainError("solar envelope has zero mean")
    solar_fleet = float(rec["solar_gen_mw"].mean() / env.mean())
    solar_pred = solar_fleet * env
    solar_corr = float(np.corrcoef(solar_pred, rec["solar_gen_mw"])[0, 1])

    return ChainParams(
        demand_base_mw=float(coef[0]), demand_b_hdd=float(coef[1]),
        demand_b_cdd=float(coef[2]), demand_r2=r2,
        wind_fleet_mw=wind_fleet, wind_corr=wind_corr,
        solar_fleet_mw=solar_fleet, solar_corr=solar_corr,
        n_days=len(hdd),
    )


def demand_from_weather(temp_c, params: ChainParams | None = None) -> np.ndarray:
    """Link 1: national demand (MW) from temperature via the fitted degree-day
    model. Convex in cold (the heating plateau)."""
    p = params or fit_chain()
    return p.demand_base_mw + p.demand_b_hdd * _hdd(temp_c) + p.demand_b_cdd * _cdd(temp_c)


def _wind_fleet_mw(p: ChainParams, year: int | None) -> float:
    """The wind fleet scalar to scale the power curve by. Default (year is None) is the
    whole-window mean-matched scalar — unchanged behaviour. When a calendar year τ is
    given, W1_7's time-varying per-year effective fleet is used instead (lazy import
    avoids the module cycle)."""
    if year is None:
        return p.wind_fleet_mw
    from sim.renewable_capacity_trend import capacity_wind
    return capacity_wind(int(year))


def _solar_fleet_mw(p: ChainParams, year: int | None) -> float:
    """As `_wind_fleet_mw`, for the solar seasonal envelope (W1_7 per-year τ fleet)."""
    if year is None:
        return p.solar_fleet_mw
    from sim.renewable_capacity_trend import capacity_solar
    return capacity_solar(int(year))


def wind_output_from_speed(wind_speed_ms, params: ChainParams | None = None,
                           year: int | None = None):
    """Link 2: national wind output (MW) from wind speed via the turbine power
    curve, scaled to the mean-matched fleet. Near-zero in the still tail.

    `year` (W1_7): when given, scales by the time-varying per-year effective fleet
    (`renewable_capacity_trend.capacity_wind(year)`) instead of the whole-window scalar,
    so the same weather draw produces a different output in 2016 than in 2025. Default
    (None) is the whole-window scalar — unchanged for every existing caller."""
    p = params or fit_chain()
    out = _wind_fleet_mw(p, year) * fleet_wind_fraction(wind_speed_ms)
    return out if np.ndim(wind_speed_ms) else float(out[0])


def solar_output_from_weather(day_of_year, cloud_pct, params: ChainParams | None = None,
                              year: int | None = None) -> np.ndarray:
    """Link 3: national solar output (MW) from season x cloud (R10 proxy).

    `year` (W1_7): per-year effective solar fleet when given (see `wind_output_from_speed`);
    None keeps the whole-window scalar (unchanged for existing callers)."""
    p = params or fit_chain()
    return _solar_fleet_mw(p, year) * _solar_envelope(day_of_year, cloud_pct)


def derive_price(temp_c, wind_speed_ms, cloud_pct, day_of_year, gas_price,
                 params: ChainParams | None = None, year: int | None = None,
                 carbon_price_gbp_per_tonne=None, wind_fleet_mw=None):
    """THE CHAIN, closed (W1_6 L4). One coherent weather draw -> demand +
    renewable output -> residual demand -> merit-order price. Price is DERIVED;
    it is never an independent draw. Vectorised over arrays or scalar.

    `carbon_price_gbp_per_tonne` (CPS + allowance, scalar or per-row) is REQUIRED: the price
    leg is refitted with carbon in its floor (`fit_price_leg`). A record day takes
    `carbon_on(date)`; a forward day takes the curriculum's drawn carbon, which is not built.

    `wind_fleet_mw` (scalar or per-row) overrides the fleet scalar, so the record can price
    each day at its own year's fleet without re-stacking the dispatchable side.

    `year` (W1_7): renewable output uses that year's fleet AND the merit order's
    dispatchable denominator uses that year's coal+gas+nuclear capacity
    (`system_margin_price`'s `year=`). Default None keeps the flat dispatchable constant."""
    if carbon_price_gbp_per_tonne is None:
        raise CarbonRequiredError(
            "derive_price needs carbon: the price leg was refitted with CPS + the allowance price "
            "in its floor (d424b78095), so pricing without it under-prices by the carbon cost. "
            "Pass carbon_on(date) on the record; forward carbon is the curriculum's drawn input")
    p = params or fit_chain()
    leg = fit_price_leg()
    coef = (leg.a0, leg.a1, leg.a2)
    demand = np.atleast_1d(demand_from_weather(temp_c, p))
    n = len(demand)
    fleet = (np.broadcast_to(np.asarray(wind_fleet_mw, float), (n,)) if wind_fleet_mw is not None
             else np.full(n, _wind_fleet_mw(p, year)))
    wind = fleet * fleet_wind_fraction(np.broadcast_to(np.asarray(wind_speed_ms, float), (n,)))
    solar = np.broadcast_to(np.atleast_1d(solar_output_from_weather(day_of_year, cloud_pct, p, year)), (n,))
    gas = np.broadcast_to(np.atleast_1d(np.asarray(gas_price, float)), (n,))
    carbon = np.broadcast_to(np.atleast_1d(np.asarray(carbon_price_gbp_per_tonne, float)), (n,))
    renewable = wind + solar
    kw = {} if year is None else {"year": year}
    price = np.array([synthetic_price(float(gas[i]), float(demand[i]), float(renewable[i]),
                                      carbon_price_gbp_per_tonne=float(carbon[i]),
                                      coefficients=coef, **kw)
                      for i in range(n)])
    return price if np.ndim(temp_c) else float(price[0])


def residual_demand(temp_c, wind_speed_ms, cloud_pct, day_of_year,
                    params: ChainParams | None = None, year: int | None = None) -> np.ndarray:
    """RD = demand - wind - solar, the load thermal plant must serve. The exact
    identity the R15 residual-identity control checks.

    `year` (W1_7): per-year time-varying renewable fleet when given; None keeps the
    whole-window scalar (unchanged)."""
    p = params or fit_chain()
    demand = demand_from_weather(temp_c, p)
    wind = wind_output_from_speed(np.atleast_1d(wind_speed_ms), p, year)
    solar = solar_output_from_weather(day_of_year, cloud_pct, p, year)
    return np.asarray(demand) - np.asarray(wind) - np.asarray(solar)


def derive_price_on_record(params: ChainParams | None = None,
                           year_aware: bool = False) -> Dict[str, np.ndarray]:
    """The chain evaluated on every real weather day -- the ground-truth derived
    price series the coupled-triad measures the company against, plus the
    intermediate demand/renewable/residual for inspection.

    Default (24 Nov 2026, the weather-to-price steer's item 4): the fleet-aggregate curve,
    each day's own year's wind fleet (W1_7's per-year scalar, mean-matched on the same curve),
    the whole-window solar scalar, the flat dispatchable constant, and carbon by month with the
    price leg refitted on it. That is arm E of 4413f635ab. A `params` whose wind_fleet_mw
    differs from the fitted one scales every year's fleet by the ratio, so a test can cut a link.

    `year_aware=True` (W1_7) additionally uses each year's solar fleet and real dispatchable
    (coal+gas+nuclear) capacity, the merit-order re-stacking (`system_margin_price`'s `year=`).
    """
    rec = load_daily_record()
    p = params or fit_chain()
    from sim.renewable_capacity_trend import _year_of, capacity_wind
    years = [_year_of(d) for d in rec["dates"]]
    carbon = np.array([carbon_on(d) for d in rec["dates"]])
    demand = demand_from_weather(rec["temperature_c"], p)
    # Each year's fleet, scaled by params' whole-window fleet over the fitted one: identity for
    # the fitted params, zero when a test cuts the wind link (wind_fleet_mw=0).
    scale = p.wind_fleet_mw / fit_chain().wind_fleet_mw
    by_year = {y: capacity_wind(y) * scale for y in set(years)}
    fleet = np.array([by_year[y] for y in years])
    wind = fleet * fleet_wind_fraction(rec["wind_speed_ms"])
    if year_aware:
        solar = np.array([solar_output_from_weather(int(doy), float(c), p, year=y)
                          for doy, c, y in zip(rec["day_of_year"], rec["cloud_pct"], years)])
        renewable = np.asarray(wind) + np.asarray(solar)
        leg = fit_price_leg()
        price = np.array([
            synthetic_price(float(rec["gas_price"][i]), float(demand[i]), float(renewable[i]),
                            carbon_price_gbp_per_tonne=float(carbon[i]),
                            coefficients=(leg.a0, leg.a1, leg.a2), year=years[i])
            for i in range(len(demand))
        ])
    else:
        solar = solar_output_from_weather(rec["day_of_year"], rec["cloud_pct"], p)
        renewable = np.asarray(wind) + np.asarray(solar)
        price = derive_price(rec["temperature_c"], rec["wind_speed_ms"], rec["cloud_pct"],
                             rec["day_of_year"], rec["gas_price"], p,
                             carbon_price_gbp_per_tonne=carbon, wind_fleet_mw=fleet)
    return {
        "dates": rec["dates"], "month": rec["month"],
        "temperature_c": rec["temperature_c"], "wind_speed_ms": rec["wind_speed_ms"],
        "gas_price": rec["gas_price"], "carbon_gbp_per_t": carbon,
        "demand_mw": np.asarray(demand),
        "renewable_mw": renewable, "residual_mw": np.asarray(demand) - renewable,
        "derived_price": np.asarray(price), "real_ssp": rec["ssp"],
    }


# ---------------------------------------------------------------------------
# Diagnostics (R12: reported, never a target)
# ---------------------------------------------------------------------------

def chain_vs_real_ssp_mae(params: ChainParams | None = None,
                          year_aware: bool = False) -> Dict[str, float]:
    """MAE of the composed chain's derived price vs real published SSP. A
    DIAGNOSTIC (R12) -- the number the chain happens to hit, never optimised.

    `year_aware` (W1_7): passthrough to `derive_price_on_record` -- reports the MAE
    of the time-varying-fleet series as a diagnostic ALONGSIDE the default, never as
    a target to beat (R12; FRAME §9 task 7: a worse MAE here is a finding about the
    inputs, surfaced, never a cue to retune the merit-order calibration)."""
    out = derive_price_on_record(params, year_aware=year_aware)
    err = out["derived_price"] - out["real_ssp"]
    return {
        "mae": float(np.mean(np.abs(err))),
        "chain_mean": float(out["derived_price"].mean()),
        "real_mean": float(out["real_ssp"].mean()),
        "n": int(len(err)),
    }


def cold_still_tail_mask(rec: Dict[str, np.ndarray], pct: float = 20.0) -> np.ndarray:
    """The winter cold-AND-still corner: winter days below the `pct` percentile
    of BOTH the winter temperature and the winter wind-speed distribution -- the
    Dunkelflaute co-occurrence, not two marginals."""
    winter = np.isin(rec["month"], _WINTER_MONTHS)
    if not winter.any():
        raise DegenerateChainError("no winter days in the record")
    t_thr = float(np.percentile(rec["temperature_c"][winter], pct))
    w_thr = float(np.percentile(rec["wind_speed_ms"][winter], pct))
    return winter & (rec["temperature_c"] <= t_thr) & (rec["wind_speed_ms"] <= w_thr)


def cold_still_spike(params: ChainParams | None = None) -> Dict[str, float]:
    """SHOW THE TAIL (the DoD deliverable): the derived price on the cold-and-
    still winter corner vs the rest, and the residual-demand tightness that
    causes it. The spike arises mechanistically from ONE weather draw (high
    heating demand + collapsed wind), never an independent draw. A ratio > 1 is
    the coupling; the R15 control cuts the demand-temp link and it collapses."""
    out = derive_price_on_record(params)
    tail = cold_still_tail_mask(out)
    rest = ~tail
    tail_price = float(out["derived_price"][tail].mean())
    rest_price = float(out["derived_price"][rest].mean())
    return {
        "tail_mean_price": tail_price,
        "rest_mean_price": rest_price,
        "spike_ratio": tail_price / rest_price if rest_price else float("nan"),
        "tail_mean_residual_mw": float(out["residual_mw"][tail].mean()),
        "rest_mean_residual_mw": float(out["residual_mw"][rest].mean()),
        "n_tail": int(tail.sum()),
    }
