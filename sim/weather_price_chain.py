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
results look a certain way. The price engine's constants are `sim/price_engine.py`'s
own already-landed calibration, imported unchanged. This module ADDS the two
front links; it does not retune the engine (R12/R13 wall).

THE THREE FITTED LINKS (all closed-form, deterministic -- C-S2 replay):
  1. DEMAND ~ WEATHER: national demand = base + b_hdd * HDD + b_cdd * CDD, the
     standard degree-day form (HDD = max(0, T_heat - T), CDD = max(0, T - T_cool)).
     OLS on real (Open-Meteo national temperature, Elexon INDO demand). Convex in
     cold -> the heating plateau (D4). R^2 ~ 0.55.
  2. WIND OUTPUT ~ WIND SPEED: fleet_wind_mw * power_curve(wind_speed), the
     idealised turbine curve `sim/price_engine.wind_power_output_fraction`
     (cubic ramp, D5), the fleet scale MEAN-MATCHED to real AGWS wind generation.
     Low speed -> near-zero output (the still tail).
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
  * WIND fleet is a single MEAN-MATCHED scalar over the whole window -- the real
    fleet ~ doubled 2016-2025 (that time-trend is W1_7, an explicit follow-on).
  * CARBON term left at the engine default (0.0) -- see sim/price_engine.py's own
    R10 note; adding a real UK-ETS series is future work, out of scope here.
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
    from sim.generation_demand_history import aggregate_renewable_generation, aggregate_wind_generation
    from sim.gas_prices_history import load_nbp_history

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

    frac = np.array([wind_power_output_fraction(w) for w in rec["wind_speed_ms"]])
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


def wind_output_from_speed(wind_speed_ms, params: ChainParams | None = None):
    """Link 2: national wind output (MW) from wind speed via the turbine power
    curve, scaled to the mean-matched fleet. Near-zero in the still tail."""
    p = params or fit_chain()
    frac = np.array([wind_power_output_fraction(float(w)) for w in np.atleast_1d(wind_speed_ms)])
    out = p.wind_fleet_mw * frac
    return out if np.ndim(wind_speed_ms) else float(out[0])


def solar_output_from_weather(day_of_year, cloud_pct, params: ChainParams | None = None) -> np.ndarray:
    """Link 3: national solar output (MW) from season x cloud (R10 proxy)."""
    p = params or fit_chain()
    return p.solar_fleet_mw * _solar_envelope(day_of_year, cloud_pct)


def derive_price(temp_c, wind_speed_ms, cloud_pct, day_of_year, gas_price,
                 params: ChainParams | None = None):
    """THE CHAIN, closed (W1_6 L4). One coherent weather draw -> demand +
    renewable output -> residual demand -> merit-order price. Price is DERIVED;
    it is never an independent draw. Vectorised over arrays or scalar."""
    p = params or fit_chain()
    demand = np.atleast_1d(demand_from_weather(temp_c, p))
    wind = np.atleast_1d(p.wind_fleet_mw * np.array(
        [wind_power_output_fraction(float(w)) for w in np.atleast_1d(wind_speed_ms)]))
    solar = np.atleast_1d(solar_output_from_weather(day_of_year, cloud_pct, p))
    gas = np.atleast_1d(np.asarray(gas_price, float))
    renewable = wind + solar
    price = np.array([synthetic_price(float(gas[i]), float(demand[i]), float(renewable[i]))
                      for i in range(len(demand))])
    return price if np.ndim(temp_c) else float(price[0])


def residual_demand(temp_c, wind_speed_ms, cloud_pct, day_of_year,
                    params: ChainParams | None = None) -> np.ndarray:
    """RD = demand - wind - solar, the load thermal plant must serve. The exact
    identity the R15 residual-identity control checks."""
    p = params or fit_chain()
    demand = demand_from_weather(temp_c, p)
    wind = wind_output_from_speed(np.atleast_1d(wind_speed_ms), p)
    solar = solar_output_from_weather(day_of_year, cloud_pct, p)
    return np.asarray(demand) - np.asarray(wind) - np.asarray(solar)


def derive_price_on_record(params: ChainParams | None = None) -> Dict[str, np.ndarray]:
    """The chain evaluated on every real weather day -- the ground-truth derived
    price series the coupled-triad measures the company against, plus the
    intermediate demand/renewable/residual for inspection."""
    rec = load_daily_record()
    p = params or fit_chain()
    demand = demand_from_weather(rec["temperature_c"], p)
    wind = wind_output_from_speed(rec["wind_speed_ms"], p)
    solar = solar_output_from_weather(rec["day_of_year"], rec["cloud_pct"], p)
    renewable = np.asarray(wind) + np.asarray(solar)
    price = derive_price(rec["temperature_c"], rec["wind_speed_ms"], rec["cloud_pct"],
                         rec["day_of_year"], rec["gas_price"], p)
    return {
        "dates": rec["dates"], "month": rec["month"],
        "temperature_c": rec["temperature_c"], "wind_speed_ms": rec["wind_speed_ms"],
        "gas_price": rec["gas_price"], "demand_mw": np.asarray(demand),
        "renewable_mw": renewable, "residual_mw": np.asarray(demand) - renewable,
        "derived_price": np.asarray(price), "real_ssp": rec["ssp"],
    }


# ---------------------------------------------------------------------------
# Diagnostics (R12: reported, never a target)
# ---------------------------------------------------------------------------

def chain_vs_real_ssp_mae(params: ChainParams | None = None) -> Dict[str, float]:
    """MAE of the composed chain's derived price vs real published SSP. A
    DIAGNOSTIC (R12) -- the number the chain happens to hit, never optimised."""
    out = derive_price_on_record(params)
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
