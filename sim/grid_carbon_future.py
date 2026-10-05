"""GB grid carbon intensity for GENERATED futures, from the wind, solar and demand the world makes.

REUSE: sim/grid_carbon_future.py
CLASS: CUSTOM
INDEX: `sim/neso_carbon_intensity.py` reads NESO's published series and its settlement key, and
       is reused for both: the fit's target IS that series. `sim/generation_demand_history.py`
       aggregates AGWS wind and solar and is reused for both. `sim/weather_price_chain.py` is
       where the world turns a weather draw into demand (INDO), wind (AGWS) and solar (AGWS), so
       this is fitted on exactly those three quantities and nothing the world cannot generate.
       `sim/grid_carbon_intensity.py` (EP13) rebuilds intensity plant by plant through a
       dispatch model; it is parked, and this is the "correlated estimate at a fraction of
       EP13's cost" the director asked for instead. `sim/grid_carbon_history.py` is G14's
       history half and supplies the past; this supplies only what has not happened.

WHAT THIS IS (director, 2026-10-05): "For generated futures, fit a statistical model of intensity
on the grid's wind, solar and demand, which the world already generates from its weather.
Condition it on fleet era ... or fit it on the recent era."

    intensity_g_per_kwh = a + b_wind * wind_GW + b_solar * solar_GW + b_demand * demand_GW

fitted by least squares on NESO's published `actual`, half hour by half hour, inside one fleet
era. LINEAR ON PURPOSE: the mean of the model over a day is the model at the day's mean inputs,
so the same coefficients serve the world's daily weather chain and a half-hourly caller, and
neither has to be told which it is. A share form ((wind+solar)/demand) was measured beside it
and fits no better in any year (it is worse in-era: R^2 0.69 against 0.74).

THE ERAS. GB's last coal station, Ratcliffe-on-Soar, closed on 30 September 2024
(`docs/market_research/ssp_dispatchable_fleet_renewables_era_boundaries_2026-07-24.md`, H
confidence, two independent sources). A future is drawn on today's fleet, so `post_coal` is the
model futures use. `coal` is fitted from 2020-05-01, NOT from NESO's first half hour, because
NESO's published level steps down by about a tenth around 2020-04-28 for a reason not yet
established (`sim/grid_carbon_history.py`, finding 3); fitting across the step would give a
basis NESO never published.

RESIDUALS BY YEAR, AT REAL INPUTS (printed by the CLI, 2026-10-05, `post_coal` coefficients on
every year's real wind, solar and demand; bias = mean(actual - model), g/kWh):

    year   actual  model   bias   rmse   corr
    2018    237     172    +65     74    0.85
    2019    213     173    +41     53    0.85
    2020    181     153    +28     45    0.82
    2021    189     164    +25     40    0.88
    2022    181     146    +35     55    0.77
    2023    152     149     +3     41    0.75
    2024    125     148    -23     48    0.72
    2025    138     131     +7     26    0.92   (to 2025-06-07, where the regressor caches end)

What the weather explains is the within-year SHAPE (correlation 0.72-0.91 every year). What it
does not explain is the LEVEL, and that is fleet, not weather: the coal and older gas the past
burned, and the imports and nuclear of a given season. April-October 2024 sits 35-57 g BELOW the
model month after month while 2025's months sit within 13 g of it. Conditioning on era does not
rescue it: the `coal` coefficients, fitted on a window that INCLUDES 2024, still miss 2024 by -35 g
and 2023 by -10 g, against +11 to +25 g for 2019-2022. The model cannot see why, and
no term for it is added, because imports and outages are not something the world generates from
weather. A future drawn from this model therefore carries a LEVEL error of that order which no
weather term will remove -- `level_error_g_per_kwh()` publishes it from the fit's own monthly
residuals so a reader of a future's carbon sees the bound beside the number.

WHAT THIS DOES NOT DO
  * NO FLEET GROWTH. The coefficients are the fleet of the fit window. A future world with twice
    the wind will feed this model wind it was never fitted on, and the answer is an
    extrapolation; `outside_fitted_range()` says so per input rather than letting it pass.
  * NO NEGATIVE INTENSITY. Very high wind and solar against low demand drives the linear form
    below zero, which no grid can be (NESO prices zero-carbon output at zero, so a grid of only
    that reads exactly 0). The value is floored at 0 and the floor is reported by
    `outside_fitted_range()`, never applied silently. At real inputs the floor binds on 58 of
    118,455 half hours, the raw form reaching -100 g where NESO's lowest published half hour is
    14 g: the linear form UNDER-reads the cleanest tail, and the real grid's must-run floor is
    not modelled.
  * NO COMPANY READER. This is world truth. The company sees carbon only as published, at
    decision time, through `company/interfaces/sim_interface.py`.

Run:  python3 -m sim.grid_carbon_future            (refit both eras; print residuals by year)
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

#: The first settlement day with no coal station in GB (Ratcliffe-on-Soar closed 2024-09-30;
#: docs/market_research/ssp_dispatchable_fleet_renewables_era_boundaries_2026-07-24.md).
POST_COAL_FROM = "2024-10-01"

COAL = "coal"
POST_COAL = "post_coal"
ERAS = (COAL, POST_COAL)

#: Where each era's fit starts and ends. `None` = the end of the record. The coal era starts
#: after NESO's 2020-04-28 level step (module docstring).
FIT_WINDOWS: dict[str, tuple[str, str | None]] = {
    COAL: ("2020-05-01", "2024-09-30"),
    POST_COAL: (POST_COAL_FROM, None),
}

#: Below this many half hours (about 90 days) an era's fit is a season, not an era, and is
#: refused rather than returned.
MIN_FIT_HALF_HOURS = 90 * 48

#: The NESO half hours `sim/grid_carbon_history.py` fetched beyond the original cache
#: (2018-05-11..2018-12-31 and 2025). Without it the post-coal era is October-December 2024.
NESO_EXTENSION_CACHE_PATH = Path("sim/cache/neso_carbon_intensity_national_extension.json")
DEMAND_CACHE_PATH = Path("sim/cache/elexon_demand_full.json")
AGWS_CACHE_PATH = Path("sim/cache/elexon_agws_full.json")


class FutureCarbonUnavailable(Exception):
    """The record needed to fit or grade the model is absent or too thin to be an era."""


@dataclass(frozen=True)
class EraModel:
    era: str
    intercept: float
    per_gw_wind: float
    per_gw_solar: float
    per_gw_demand: float
    fit_from: str
    fit_to: str
    half_hours: int
    r_squared: float
    #: The fitted inputs' 1st-99th percentile, GW: what `outside_fitted_range` checks against.
    wind_gw_range: tuple[float, float]
    solar_gw_range: tuple[float, float]
    demand_gw_range: tuple[float, float]
    #: Standard deviation of the fit's monthly mean residuals, g/kWh: the level error a future
    #: inherits that weather does not explain.
    monthly_level_sd: float


#: Refitted by `python3 -m sim.grid_carbon_future` on 2026-10-05 from the caches named above.
#: `test_the_frozen_coefficients_are_what_the_record_refits_to` re-derives them where the
#: caches exist, so a refit that moves them goes red rather than drifting.
FROZEN: dict[str, EraModel] = {
    COAL: EraModel(
        era=COAL, intercept=80.43, per_gw_wind=-9.301, per_gw_solar=-6.361, per_gw_demand=5.561,
        fit_from="2020-05-01", fit_to="2024-09-30", half_hours=72781, r_squared=0.568,
        wind_gw_range=(0.5, 18.13), solar_gw_range=(0.0, 7.95), demand_gw_range=(16.6, 41.98),
        monthly_level_sd=29.1,
    ),
    POST_COAL: EraModel(
        era=POST_COAL, intercept=55.73, per_gw_wind=-6.949, per_gw_solar=-3.631,
        per_gw_demand=5.352, fit_from="2024-10-01", fit_to="2025-06-07", half_hours=11975,
        r_squared=0.742, wind_gw_range=(0.49, 20.94), solar_gw_range=(0.0, 11.07),
        demand_gw_range=(16.31, 42.2), monthly_level_sd=13.1,
    ),
}


def era_of(settlement_date: str) -> str:
    """The fleet era a settlement date belongs to."""
    return POST_COAL if str(settlement_date) >= POST_COAL_FROM else COAL


def intensity(wind_mw, solar_mw, demand_mw, *, era: str = POST_COAL,
              model: EraModel | None = None):
    """gCO2/kWh from the world's wind, solar and demand (MW), floored at zero.

    Scalars in, a float out; arrays in, an array out. `era` defaults to the fleet a future runs
    on. Inputs in MW because that is what the world's chain emits.
    """
    m = model or FROZEN[era]
    raw = (m.intercept + m.per_gw_wind * np.asarray(wind_mw, float) / 1e3
           + m.per_gw_solar * np.asarray(solar_mw, float) / 1e3
           + m.per_gw_demand * np.asarray(demand_mw, float) / 1e3)
    floored = np.maximum(raw, 0.0)
    return float(floored) if floored.ndim == 0 else floored


def outside_fitted_range(wind_mw: float, solar_mw: float, demand_mw: float, *,
                         era: str = POST_COAL, model: EraModel | None = None) -> list[str]:
    """Why this input is an extrapolation, one reason per cause; empty means inside the fit."""
    m = model or FROZEN[era]
    reasons = []
    for name, mw, (lo, hi) in (("wind", wind_mw, m.wind_gw_range),
                               ("solar", solar_mw, m.solar_gw_range),
                               ("demand", demand_mw, m.demand_gw_range)):
        gw = mw / 1e3
        if not lo <= gw <= hi:
            reasons.append(f"{name} {gw:.2f} GW is outside the {m.era} fit's {lo}-{hi} GW")
    raw = (m.intercept + m.per_gw_wind * wind_mw / 1e3 + m.per_gw_solar * solar_mw / 1e3
           + m.per_gw_demand * demand_mw / 1e3)
    if raw < 0:
        reasons.append(f"the linear form gives {raw:.1f} g/kWh and is floored at 0")
    return reasons


def level_error_g_per_kwh(era: str = POST_COAL) -> float:
    """The monthly level error a future inherits that its weather does not explain."""
    return FROZEN[era].monthly_level_sd


# ---------------------------------------------------------------------------
# The real record, the fit, and its residuals
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> list:
    if not path.exists():
        raise FutureCarbonUnavailable(f"{path} is absent; the record cannot be read without it")
    return json.loads(path.read_text())


@lru_cache(maxsize=1)
def load_record() -> dict[str, np.ndarray]:
    """NESO actual against INDO demand and AGWS wind and solar, every half hour all four exist."""
    from sim import neso_carbon_intensity as nci
    from sim.generation_demand_history import aggregate_solar_generation, aggregate_wind_generation

    records = nci.load_cached()
    if NESO_EXTENSION_CACHE_PATH.exists():
        records = records + _load_json(NESO_EXTENSION_CACHE_PATH)
    neso = nci.actual_by_period(nci.to_settlement_periods(records))
    demand = {(r["settlementDate"], r["settlementPeriod"]): float(r["initialDemandOutturn"])
              for r in _load_json(DEMAND_CACHE_PATH) if r.get("initialDemandOutturn")}
    agws = _load_json(AGWS_CACHE_PATH)
    wind = aggregate_wind_generation(agws)
    solar = aggregate_solar_generation(agws)
    keys = sorted(k for k in neso if k in demand and k in wind and k in solar)
    if not keys:
        raise FutureCarbonUnavailable("no half hour carries NESO actual, demand, wind and solar")
    return {
        "date": np.array([k[0] for k in keys]),
        "actual": np.array([neso[k] for k in keys]),
        "wind_mw": np.array([wind[k] for k in keys]),
        "solar_mw": np.array([solar[k] for k in keys]),
        "demand_mw": np.array([demand[k] for k in keys]),
    }


def fit(era: str, record: Mapping[str, np.ndarray]) -> EraModel:
    """Least squares on the era's window. Refuses a window too short to be an era."""
    lo, hi = FIT_WINDOWS[era]
    dates = record["date"]
    mask = dates >= lo
    if hi is not None:
        mask &= dates <= hi
    n = int(mask.sum())
    if n < MIN_FIT_HALF_HOURS:
        raise FutureCarbonUnavailable(
            f"the {era} era holds {n} half hours from {lo}; below {MIN_FIT_HALF_HOURS} it is a "
            "season, not an era")
    w, s, d = (record[k][mask] / 1e3 for k in ("wind_mw", "solar_mw", "demand_mw"))
    y = record["actual"][mask]
    x = np.column_stack([np.ones(n), w, s, d])
    coef, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ coef
    months: dict[str, list[float]] = defaultdict(list)
    for day, r in zip(dates[mask], resid):
        months[day[:7]].append(float(r))
    monthly = [float(np.mean(v)) for v in months.values()]

    def pct(a):
        return (round(float(np.percentile(a, 1)), 2), round(float(np.percentile(a, 99)), 2))

    return EraModel(
        era=era, intercept=round(float(coef[0]), 2), per_gw_wind=round(float(coef[1]), 3),
        per_gw_solar=round(float(coef[2]), 3), per_gw_demand=round(float(coef[3]), 3),
        fit_from=str(dates[mask][0]), fit_to=str(dates[mask][-1]), half_hours=n,
        r_squared=round(1.0 - float(resid.var() / y.var()), 3),
        wind_gw_range=pct(w), solar_gw_range=pct(s), demand_gw_range=pct(d),
        monthly_level_sd=round(float(np.std(monthly)), 1),
    )


def residuals_by_year(model: EraModel, record: Mapping[str, np.ndarray]) -> dict[int, dict]:
    """The model at every year's real inputs against NESO's actual: the published error bar."""
    pred = intensity(record["wind_mw"], record["solar_mw"], record["demand_mw"], model=model)
    resid = record["actual"] - pred
    years = np.array([int(d[:4]) for d in record["date"]])
    out = {}
    for year in sorted(set(years.tolist())):
        k = years == year
        out[year] = {
            "half_hours": int(k.sum()),
            "actual_mean": round(float(record["actual"][k].mean()), 1),
            "model_mean": round(float(pred[k].mean()), 1),
            "bias": round(float(resid[k].mean()), 1),
            "rmse": round(math.sqrt(float((resid[k] ** 2).mean())), 1),
            "correlation": round(float(np.corrcoef(record["actual"][k], pred[k])[0, 1]), 2),
        }
    return out


def main(argv: list[str] | None = None) -> int:
    record = load_record()
    for era in ERAS:
        refit = fit(era, record)
        drift = {k: (v, asdict(FROZEN[era])[k]) for k, v in asdict(refit).items()
                 if v != asdict(FROZEN[era])[k]}
        print(f"\n{era}: {asdict(refit)}")
        print(f"  differs from FROZEN: {drift or 'nothing'}")
        print("  year   actual  model    bias   rmse  corr   half-hours")
        for year, row in residuals_by_year(refit, record).items():
            print(f"  {year}   {row['actual_mean']:6.1f} {row['model_mean']:6.1f} "
                  f"{row['bias']:+7.1f} {row['rmse']:6.1f}  {row['correlation']:.2f}   "
                  f"{row['half_hours']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
