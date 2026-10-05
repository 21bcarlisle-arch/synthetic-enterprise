"""GB grid carbon intensity for GENERATED futures: a fitted model run on the analogue year the world replays.

REUSE: sim/grid_carbon_future.py
CLASS: CUSTOM
INDEX: `sim/grid_carbon_history.py` is G14's history half. Its NESO Historic Generation Mix
       series is this fit's TARGET (since 2026-10-05; the Carbon Intensity API before), and its FUELHH loader supplies transmission wind and demand. `sim/neso_embedded_generation.py`
       supplies embedded wind and solar. `sim/weather_world.py::WeatherWorld.extended_by_analogue_years`
       decides which record year a forward year replays, and it is CALLED here, never re-implemented.
       `sim/renewable_capacity_trend.py` supplies the fleet, held flat past 2025 by that module (R13).
       `sim/grid_carbon_intensity.py` (EP13) rebuilds intensity plant by plant. It is parked, and
       this is the "correlated estimate at a fraction of the cost" the director asked for instead.

WHAT THIS IS (director, 2026-10-05): "For generated futures, fit a statistical model of carbon
intensity on that history -- wind and solar on the grid and demand will carry most of it ... That
keeps future carbon consistent with future weather." He accepts a correlated estimate.

HOW A FUTURE IS MADE. The world generates no future grid wind, solar or demand. A generated
future replays one whole record WEATHER year per forward year (`extended_by_analogue_years`). So
for a forward (date, period):
  1. the record year is the one the world's own mapping names for that forward year and seed;
  2. the record half hour is the same calendar date in that year, by the world's own rule (29 Feb
     reads 28 Feb when the record year has none), at the same LOCAL clock time, so clock-change
     days resolve (a 46- or 50-period day against a 48-period one);
  3. that half hour's REAL wind, solar and demand are rescaled to the forward year's fleet and
     demand level, and the fitted model below gives gCO2/kWh.

THE INPUT DEFINITIONS, chosen to match how NESO's intensity counts generation:
  * wind  = FUELHH WIND (transmission-metered) + NESO's embedded wind estimate;
  * solar = NESO's embedded solar estimate (GB solar is almost all embedded);
  * demand = TRUE demand = FUELHH's net total (transmission demand, including net imports and
    pumping) + embedded wind + embedded solar.
  NESO's denominator includes embedded generation, and `grid_carbon_history.py` measured that
  leaving it out biases the estimate. Elexon INDO and AGWS were the first draft's inputs and were
  dropped for three measured reasons. They end on 2025-06-07, so a 2025 analogue year would have no
  second half. AGWS wind tracks metered wind at a correlation of only 0.285 in 2022 and 0.79 in
  2023-24, against 0.90-0.99 in other years. And INDO excludes embedded generation, so a sunny
  midday reads as low demand rather than as generation.
  FUELHH publishes some half hours with every domestic fuel at zero (56 in the record), and some
  partially (2022-08-02 P2 at about 60% of its neighbours). Both are publication defects, and a
  defect half hour is never fitted and never replayed: a future on one returns None with the reason.

THE MODEL (`share_log`), chosen on held-out error from the alternatives `validation_table` prints:

    log(g) = a + b * share + c * demand_GW,    share = (wind + solar) / demand

It is positive by construction, so it needs no floor. The linear form on wind, solar and demand
floored 201 of 2025's half hours at 0, and that exaggerated the within-day swing time-shifting advice
reads (mean daily p95/p5 3.66 against an actual 2.25). Settlement-period and month terms were
measured and earn nothing on held-out error.

THE REGIME. Fitted on the two most recent record years. That rule was chosen by holding out 2025 and
by a rolling origin over 2020-2025. A fit across the decade carries coal and is about 25 g too dirty
on 2025.

VALIDATION (printed by the CLI, re-run 2026-10-05 on the historic-mix target). The 2025 half hours
were held out. Swing is each day's p95/p5, averaged over days; the actual is 2.29.

    FORMS, fitted 2023-2024           corr   bias   rmse   swing
    constant                          --     -9.6   59.2   1.00
    linear wind, solar, demand       0.919   -4.3   24.2   3.49  (model p5 = 0 on 27 days)
    share_log            <- shipped  0.924   -6.2   23.3   2.18
    fossil_fraction_log              0.920   -5.9   23.7   2.15

    REGIMES, share_log
    2018-05..2024                    0.926  -19.5   29.9   2.10
    2018-05..2024 + year term        0.926   -6.0   23.0   2.04
    2021-2024                        0.922  -18.7   30.0   2.12
    2023-2024 (two prior years)      0.924   -6.2   23.3   2.18
    2024 only                        0.924   +4.6   22.8   2.27
    post-coal 2024-10..12            0.923   -4.5   23.0   2.14

  Every recent window ties to within 0.5 g of RMSE. The rolling origin decides among the rules. Its
  mean RMSE over 2020-2025 is: previous year 30.8, two previous 30.8, all previous 30.2. On the API
  target (before 2026-10-05) it was 32.0 / 32.3 / 34.6: the API's 2020-04 basis change had been
  charging the long window for a level the fleet never had. The three now tie, and the two-year
  rule is kept for the reason below, not on this score. The
  year term ties on 2025, but a future would have to freeze it, and then it is a recent-window fit
  with extra steps. Two years was kept over one because a single year carries one year's imports
  and outages as its level (2024 sits 25-39 g below every fit not trained on it).

FUTURES AT REAL INPUTS. A whole forward year on each analogue year, at the 2025 fleet and demand:
annual mean, then the record year's own mean. MEASURED ON THE API TARGET, before 2026-10-05. The
historic-mix refit reads 0.7-1.4% lower at the same inputs (2016 0.993, 2020 0.987, 2025 0.986 of
the old model's mean over each record year's inputs), and the record years' own means are now the
historic mix's (2016-2019 about 8-14% below these bracketed figures; the feed's `annual_level`).
    2016 152 (298)   2017 130 (262)   2018 129 (248)   2019 125 (213)   2020 117 (180)
    2021 133 (187)   2022 121 (183)   2023 126 (152)   2024 129 (125)   2025 126 (129)
  The within-day swing is 2.11-2.57. Without the demand adjustment, 2016 reads 166 rather than 152.
  2016 stays the dirtiest analogue, and the cause is NOT ESTABLISHED. Two candidates cannot yet be
  separated. One is that 2016 was a calm year. The other is that `real_capacity_smoothed` has no
  2015 anchor and returns 2016's year-END wind capacity, which understates the rescale.

THE FLEET AND DEMAND OF A FUTURE. Wind and solar are rescaled by DUKES installed capacity:
year-average (`real_capacity_smoothed`) for the forward year, which that module holds flat at 2025,
over the record year's. The AGWS-fitted "effective fleet" was rejected because it is not monotone
(96 GW 2020, 160 GW 2021): it carries load factor, that is weather, which the replay already
supplies. Demand is held at the 2025 level in the same way: the record year's true demand is scaled
by mean(2025) / mean(record year). That is a NAMED SIMPLIFICATION, because the record shows a
decade trend (33.9 GW mean in 2016, 30.0-31.5 GW in 2022-2025) far larger than weather moves an
annual mean. The error runs one known way: a future loses the record year's weather-driven
annual demand LEVEL (about 1-2%) and keeps its within-year shape. To do it properly would need a
weather-normalised demand trend, which nothing in the tree supplies.

WHAT THIS DOES NOT DO
  * Imports, nuclear outages and the gas/biomass split are not modelled; the world does not
    generate them from weather. Their effect is the LEVEL error a future inherits, published by
    `level_error_g_per_kwh()` from the fit's own monthly residuals. 2024 sits 25-39 g below every
    fit not trained on it, and nothing here explains why.
  * No company reader. This is world truth. The company sees carbon only as published, at decision
    time, through `company/interfaces/sim_interface.py`.

Run:  python3 -m sim.grid_carbon_future [--seed neso_central:20260724] [--week 2027-01-11]
      (validation table, then a forward week beside its analogue record week)
"""
from __future__ import annotations

import argparse
import math
from collections import defaultdict
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from datetime import date as date_cls
from datetime import datetime, timedelta, timezone
from datetime import time as time_cls
from functools import lru_cache

import numpy as np

from sim import grid_carbon_history as gch
from sim import neso_carbon_intensity as nci

Key = tuple[str, int]

#: The fuels FUELHH publishes for generation inside GB. A half hour with every one of them at zero
#: published no generation at all; it is a publication defect, not a calm night.
DOMESTIC_FUELS = ("CCGT", "OCGT", "NUCLEAR", "NPSHYD", "COAL", "WIND", "PS", "OIL", "OTHER",
                  "BIOMASS")

#: A NAMED SIMPLIFICATION: a FUELHH half hour whose net total is under this fraction of the mean of
#: its two neighbours is a partial publication. Measured on the record, 2026-10-05: that ratio's
#: 0.1st percentile is 0.954 and its median 1.00. 23 half hours sit below 0.5, down to 0.14, and GB
#: demand does not halve and recover inside an hour. Glitches milder than this are fitted as real. To
#: do it properly would need a second published demand series for every half hour of 2016-2025; INDO
#: stops on 2025-06-07 and is not refetched.
PARTIAL_PUBLICATION_FRACTION = 0.5

#: The form the futures use. The alternatives are on `FORMS` and in `VALIDATION`.
FORM = "share_log"
FORMS = ("constant", "linear_wind_solar_demand", "share_log", "fossil_fraction_log")

#: The fitted window: the two most recent record years (the rule `VALIDATION` chose).
FIT_WINDOW = ("2024-01-01", "2025-12-31")
#: How the rule was chosen: fit on the two years before, grade on the year held out.
HELD_OUT_YEAR = 2025
HELD_OUT_TRAIN = ("2023-01-01", "2024-12-31")

#: The demand level a future is held at, as the fleet is: the last complete record year.
DEMAND_REFERENCE_YEAR = 2025

#: Below this many half hours (about 90 days) a window is a season, not a regime, and is refused.
MIN_FIT_HALF_HOURS = 90 * 48


class FutureCarbonUnavailable(Exception):
    """The record needed to fit or grade the model is absent or too thin."""


@dataclass(frozen=True)
class Model:
    form: str
    coefficients: tuple[float, ...]
    #: Duan's smearing factor, mean(exp(residual)), so the back-transformed level is unbiased.
    smearing: float
    fit_from: str
    fit_to: str
    half_hours: int
    #: The fitted inputs' 1st-99th percentiles: what `outside_fitted_range` checks.
    share_range: tuple[float, float]
    demand_gw_range: tuple[float, float]
    #: SD of the fit's monthly mean residuals, g/kWh: the level error weather does not explain.
    monthly_level_sd: float


#: Refitted by `python3 -m sim.grid_carbon_future` on 2026-10-05 from the caches the module names.
#: `test_the_frozen_model_is_what_the_record_refits_to` re-derives it where the caches exist, so a
#: refit that moves it goes red rather than drifting.
FROZEN = Model(
    form="share_log", coefficients=(4.97756, -2.41636, 0.02033), smearing=1.02659,
    fit_from="2024-01-01", fit_to="2025-12-31", half_hours=35070,
    share_range=(0.054, 0.795), demand_gw_range=(19.648, 45.211), monthly_level_sd=11.6,
)


# ---------------------------------------------------------------------------------------------
# The model
# ---------------------------------------------------------------------------------------------

def _design(form: str, share, demand_gw, wind_gw=None, solar_gw=None) -> np.ndarray:
    share = np.atleast_1d(np.asarray(share, float))
    d = np.atleast_1d(np.asarray(demand_gw, float))
    one = np.ones_like(d)
    if form == "constant":
        return one[:, None]
    if form == "share_log":
        return np.column_stack([one, share, d])
    if form == "fossil_fraction_log":
        return np.column_stack([one, 1.0 - share, 1.0 / d])
    if form == "linear_wind_solar_demand":
        return np.column_stack([one, np.atleast_1d(np.asarray(wind_gw, float)),
                                np.atleast_1d(np.asarray(solar_gw, float)), d])
    raise ValueError(f"unknown form {form!r}; expected one of {FORMS}")


def _is_log(form: str) -> bool:
    return form.endswith("_log")


def predict(share, demand_gw, *, model: Model = FROZEN, wind_gw=None, solar_gw=None):
    """gCO2/kWh. Scalars in, a float out; arrays in, an array out."""
    x = _design(model.form, share, demand_gw, wind_gw, solar_gw)
    raw = x @ np.asarray(model.coefficients, float)
    out = np.exp(raw) * model.smearing if _is_log(model.form) else np.maximum(raw, 0.0)
    return float(out[0]) if np.ndim(share) == 0 and np.ndim(demand_gw) == 0 else out


def outside_fitted_range(share: float, demand_gw: float, *, model: Model = FROZEN) -> list[str]:
    """Why this input is an extrapolation, one reason per cause; empty means inside the fit."""
    reasons = []
    for name, v, (lo, hi) in (("share", share, model.share_range),
                              ("demand", demand_gw, model.demand_gw_range)):
        if not lo <= v <= hi:
            reasons.append(f"{name} {v:.3f} is outside the fit's 1st-99th percentile {lo}-{hi}")
    return reasons


def level_error_g_per_kwh(model: Model = FROZEN) -> float:
    """The monthly level error a future inherits that its weather does not explain."""
    return model.monthly_level_sd


# ---------------------------------------------------------------------------------------------
# The record: inputs for every half hour 2016-2025, and the published target
# ---------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class HalfHour:
    tx_wind_mw: float
    embedded_wind_mw: float
    embedded_solar_mw: float
    tx_demand_mw: float

    @property
    def wind_mw(self) -> float:
        return self.tx_wind_mw + self.embedded_wind_mw

    @property
    def solar_mw(self) -> float:
        return self.embedded_solar_mw

    @property
    def demand_mw(self) -> float:
        """True demand: what the transmission system served plus what was generated under it."""
        return self.tx_demand_mw + self.embedded_wind_mw + self.embedded_solar_mw


def publication_defects(fuel_mix: Mapping[Key, Mapping[str, float]]) -> dict[Key, str]:
    """{key: reason} for FUELHH half hours that published no, or only part of, GB generation."""
    defects: dict[Key, str] = {}
    keys = sorted(fuel_mix)
    for k in keys:
        if all(fuel_mix[k].get(f, 0.0) == 0.0 for f in DOMESTIC_FUELS):
            defects[k] = "FUELHH published every domestic fuel at zero for this half hour"
    clean = [k for k in keys if k not in defects]
    total = {k: sum(fuel_mix[k].values()) for k in clean}
    for prev, k, nxt in zip(clean, clean[1:], clean[2:]):
        around = (total[prev] + total[nxt]) / 2.0
        if around > 0 and total[k] < PARTIAL_PUBLICATION_FRACTION * around:
            defects[k] = (f"FUELHH's total {total[k]:.0f} MW is under {PARTIAL_PUBLICATION_FRACTION} "
                          f"of its neighbours' {around:.0f} MW: a partial publication")
    return defects


def build_inputs(fuel_mix: Mapping[Key, Mapping[str, float]],
                 embedded: Mapping[Key, Mapping[str, float]]) -> tuple[dict[Key, HalfHour], dict[Key, str]]:
    """(inputs, gaps): every half hour with both sources and no defect, and why each other one is not."""
    defects = publication_defects(fuel_mix)
    inputs: dict[Key, HalfHour] = {}
    gaps: dict[Key, str] = dict(defects)
    for k, fuels in fuel_mix.items():
        if k in defects:
            continue
        e = embedded.get(k)
        if e is None:
            gaps[k] = "NESO publishes no embedded wind and solar estimate for this half hour"
            continue
        if "WIND" not in fuels:
            gaps[k] = "FUELHH publishes no WIND for this half hour"
            continue
        inputs[k] = HalfHour(float(fuels["WIND"]), float(e["wind_mw"]), float(e["solar_mw"]),
                             float(sum(fuels.values())))
    return inputs, gaps


@lru_cache(maxsize=1)
def load_inputs() -> tuple[dict[Key, HalfHour], dict[Key, str]]:
    """The real record's inputs, read once per process (about 40 s from the caches)."""
    from sim import neso_embedded_generation as neg
    try:
        fuel_mix = gch.load_fuel_mix()
        embedded = neg.to_settlement_periods(neg.load_cached())
    except (FileNotFoundError, neg.EmbeddedGenerationUnavailable) as exc:
        raise FutureCarbonUnavailable(f"the record's inputs cannot be read: {exc}") from exc
    if not fuel_mix:
        raise FutureCarbonUnavailable("no FUELHH half hour is cached")
    return build_inputs(fuel_mix, embedded)


def record_arrays(inputs: Mapping[Key, HalfHour],
                  target: Mapping[Key, float]) -> dict[str, np.ndarray]:
    """Aligned arrays over every half hour with inputs AND a published target."""
    keys = sorted(k for k in target if k in inputs)
    if not keys:
        raise FutureCarbonUnavailable("no half hour carries both inputs and a published intensity")
    hh = [inputs[k] for k in keys]
    d = np.array([h.demand_mw for h in hh]) / 1e3
    w = np.array([h.wind_mw for h in hh]) / 1e3
    s = np.array([h.solar_mw for h in hh]) / 1e3
    return {"date": np.array([k[0] for k in keys]), "actual": np.array([target[k] for k in keys]),
            "wind_gw": w, "solar_gw": s, "demand_gw": d, "share": (w + s) / d}


@lru_cache(maxsize=1)
def load_record() -> dict[str, np.ndarray]:
    """NESO's Historic Generation Mix intensity (never the fuel-mix fill) against the inputs, so a
    future is on the same generation basis as the history it continues."""
    series, _ = gch.load_series()
    target = {k: r.value for k, r in series.items()
              if r.source == gch.NESO_HISTORIC_MIX and r.value is not None}
    return record_arrays(load_inputs()[0], target)


# ---------------------------------------------------------------------------------------------
# Fit and grade
# ---------------------------------------------------------------------------------------------

def _window(record: Mapping[str, np.ndarray], lo: str, hi: str) -> np.ndarray:
    return (record["date"] >= lo) & (record["date"] <= hi)


def fit(record: Mapping[str, np.ndarray], window: tuple[str, str] = FIT_WINDOW, *,
        form: str = FORM, year_term: bool = False) -> Model:
    """Least squares on the window. Refuses a window too short to be a regime.

    `year_term` adds (year - 2020) as a regressor; it exists for the validation table only, and a
    model carrying it is never handed to a future (it would extrapolate a cleaning trend forever).
    """
    mask = _window(record, *window)
    n = int(mask.sum())
    if n < MIN_FIT_HALF_HOURS:
        raise FutureCarbonUnavailable(
            f"the window {window} holds {n} half hours; below {MIN_FIT_HALF_HOURS} it is a season, "
            "not a regime")
    x = _design(form, record["share"][mask], record["demand_gw"][mask],
                record["wind_gw"][mask], record["solar_gw"][mask])
    if year_term:
        x = np.column_stack([x, _years(record["date"][mask]) - 2020])
    y = record["actual"][mask]
    target = np.log(y) if _is_log(form) else y
    coef, *_ = np.linalg.lstsq(x, target, rcond=None)
    resid = target - x @ coef
    smearing = float(np.mean(np.exp(resid))) if _is_log(form) else 1.0
    fitted = np.exp(x @ coef) * smearing if _is_log(form) else x @ coef
    months: dict[str, list[float]] = defaultdict(list)
    for day, r in zip(record["date"][mask], y - fitted):
        months[day[:7]].append(float(r))

    def pct(a):
        return (round(float(np.percentile(a, 1)), 3), round(float(np.percentile(a, 99)), 3))

    return Model(
        form=form + ("+year" if year_term else ""),
        coefficients=tuple(round(float(c), 5) for c in coef),
        smearing=round(smearing, 5),
        fit_from=str(record["date"][mask][0]), fit_to=str(record["date"][mask][-1]), half_hours=n,
        share_range=pct(record["share"][mask]), demand_gw_range=pct(record["demand_gw"][mask]),
        monthly_level_sd=round(float(np.std([np.mean(v) for v in months.values()])), 1),
    )


def _years(dates: np.ndarray) -> np.ndarray:
    return np.array([int(d[:4]) for d in dates], float)


def model_values(model: Model, record: Mapping[str, np.ndarray], mask: np.ndarray) -> np.ndarray:
    base = model.form.removesuffix("+year")
    x = _design(base, record["share"][mask], record["demand_gw"][mask],
                record["wind_gw"][mask], record["solar_gw"][mask])
    if model.form.endswith("+year"):
        x = np.column_stack([x, _years(record["date"][mask]) - 2020])
    raw = x @ np.asarray(model.coefficients, float)
    return np.exp(raw) * model.smearing if _is_log(base) else np.maximum(raw, 0.0)


def grade(model: Model, record: Mapping[str, np.ndarray], mask: np.ndarray) -> dict[str, float]:
    """Correlation, bias, RMSE and the within-day swing against the published record.

    The swing is each day's p95/p5, averaged over days: what time-shifting advice reads. Days where
    the model's p5 is 0 are counted separately and left out of the model's mean rather than divided by.
    """
    a = record["actual"][mask]
    p = model_values(model, record, mask)
    r = a - p
    dates = record["date"][mask]
    sw_a, sw_m, zero_days = [], [], 0
    for day in np.unique(dates):
        k = dates == day
        a5, a95 = np.percentile(a[k], [5, 95])
        m5, m95 = np.percentile(p[k], [5, 95])
        sw_a.append(a95 / a5)
        if m5 > 0:
            sw_m.append(m95 / m5)
        else:
            zero_days += 1
    return {
        "half_hours": int(mask.sum()),
        "correlation": round(float(np.corrcoef(a, p)[0, 1]), 3) if p.std() > 0 else float("nan"),
        "bias": round(float(r.mean()), 1),
        "rmse": round(math.sqrt(float((r ** 2).mean())), 1),
        "swing_actual": round(float(np.mean(sw_a)), 2),
        "swing_model": round(float(np.mean(sw_m)), 2) if sw_m else float("nan"),
        "days_model_p5_zero": zero_days,
        "floored_half_hours": int((p == 0).sum()),
    }


def validation_table(record: Mapping[str, np.ndarray]) -> dict[str, list[tuple[str, dict]]]:
    """Every alternative the choice was made against, each graded on the held-out year."""
    test = _years(record["date"]) == HELD_OUT_YEAR
    out: dict[str, list[tuple[str, dict]]] = {"forms": [], "regimes": [], "rolling_origin": []}
    for form in FORMS:
        out["forms"].append((form, grade(fit(record, HELD_OUT_TRAIN, form=form), record, test)))
    prior_end = f"{HELD_OUT_YEAR - 1}-12-31"
    for label, window, year_term in (
            ("2018-05..2024 (all NESO)", (nci.FIRST_PUBLISHED_DATE, prior_end), False),
            ("2018-05..2024 + year term", (nci.FIRST_PUBLISHED_DATE, prior_end), True),
            ("2021-2024", ("2021-01-01", prior_end), False),
            ("2023-2024 (two prior years)", HELD_OUT_TRAIN, False),
            ("2024 only", ("2024-01-01", prior_end), False),
            ("post-coal 2024-10..12", ("2024-10-01", prior_end), False)):
        out["regimes"].append((label, grade(fit(record, window, year_term=year_term), record, test)))
    years = _years(record["date"])
    for year in range(2020, HELD_OUT_YEAR + 1):
        row = {}
        for rule, lo in (("previous year", year - 1), ("two previous", year - 2),
                         ("all previous", 2018)):
            window = (nci.FIRST_PUBLISHED_DATE if lo == 2018 else f"{lo}-01-01", f"{year - 1}-12-31")
            row[rule] = grade(fit(record, window), record, years == year)
        out["rolling_origin"].append((str(year), row))
    return out


# ---------------------------------------------------------------------------------------------
# Futures
# ---------------------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _default_world():
    from sim.weather_world import WeatherWorld
    return WeatherWorld.load()


#: (world, seed, forward year) -> record year. The world object is held in the value and checked by
#: identity, so a recycled `id()` cannot answer for a different world.
_ANALOGUE_CACHE: dict[tuple[int, str, int], tuple[object, int | None]] = {}


def analogue_year(forward_year: int, seed: str, world=None) -> tuple[int | None, str]:
    """(record year, how it was resolved) by the WORLD'S OWN mapping, or (None, why not).

    `world` is the run's WeatherWorld. Passed one already extended (it carries `analogue_years`),
    it is read as is, because that is the weather the run lives through. Otherwise its own
    `extended_by_analogue_years` is called with this seed.
    """
    world = world if world is not None else _default_world()
    own = getattr(world, "analogue_years", None)
    if own is not None:
        year = own.get(forward_year)
        if year is None:
            return None, (f"the run's world replays {sorted(own)} and holds no analogue for "
                          f"{forward_year}")
        return int(year), "the run's extended world"
    record_end = world.record_end()
    if f"{forward_year}-01-01" <= record_end:
        return None, (f"{forward_year} is inside the record (ends {record_end}): read "
                      "sim.grid_carbon_history, not a future")
    cache_key = (id(world), seed, forward_year)
    cached = _ANALOGUE_CACHE.get(cache_key)
    if cached is None or cached[0] is not world:
        extended = world.extended_by_analogue_years(f"{forward_year}-12-31", seed=seed)
        cached = (world, getattr(extended, "analogue_years", {}).get(forward_year))
        _ANALOGUE_CACHE[cache_key] = cached
    year = cached[1]
    if year is None:
        return None, f"the world's mapping names no analogue year for {forward_year} on seed {seed!r}"
    return int(year), f"WeatherWorld.extended_by_analogue_years(seed={seed!r})"


def record_date(forward: date_cls, record_year: int) -> date_cls:
    """The world's day rule: the same calendar date; 29 Feb reads 28 Feb in a year without one.
    `test_the_leap_day_rule_is_the_worlds_own` holds this to `extended_by_analogue_years`."""
    try:
        return forward.replace(year=record_year)
    except ValueError:
        return date_cls(record_year, 2, 28)


@lru_cache(maxsize=4096)
def _local_starts(day: date_cls) -> list[tuple[int, int]]:
    """The LOCAL wall-clock start (hour, minute) of each settlement period of a GB day."""
    start = datetime.combine(day, time_cls(0, 0), tzinfo=nci.LONDON).astimezone(timezone.utc)
    n = gch.settlement_periods_on(day.isoformat())
    out = []
    for p in range(n):
        local = (start + timedelta(minutes=30 * p)).astimezone(nci.LONDON)
        out.append((local.hour, local.minute))
    return out


def record_period(forward: date_cls, period: int, source: date_cls) -> tuple[int | None, str]:
    """The source day's period at the forward period's LOCAL clock time.

    The autumn day's repeated hour maps its second pass to the source's second pass when that day
    has one, else to the single hour. A wall time the source day skipped (spring forward) reads the
    next period that exists.
    """
    fwd = _local_starts(forward)
    if not 1 <= period <= len(fwd):
        return None, f"{forward} has {len(fwd)} settlement periods; {period} is not one of them"
    wall = fwd[period - 1]
    occurrence = fwd[:period - 1].count(wall)
    src = _local_starts(source)
    hits = [i for i, w in enumerate(src) if w == wall]
    if hits:
        return hits[min(occurrence, len(hits) - 1)] + 1, "same local clock time"
    later = [i for i, w in enumerate(src) if w > wall]
    return later[0] + 1, f"{source} skips {wall[0]:02d}:{wall[1]:02d}; the next period that exists"


def fleet_factors(record_year: int, forward_year: int,
                  capacity: Callable[[str, int], float] | None = None) -> dict[str, float]:
    """Forward fleet over record fleet, DUKES year-average installed capacity, per technology."""
    if capacity is None:
        return dict(_dukes_fleet_factors(record_year, forward_year))
    return _fleet_factors(record_year, forward_year, capacity)


@lru_cache(maxsize=256)
def _dukes_fleet_factors(record_year: int, forward_year: int) -> tuple[tuple[str, float], ...]:
    from sim.renewable_capacity_trend import real_capacity_smoothed
    return tuple(_fleet_factors(record_year, forward_year, real_capacity_smoothed).items())


def _fleet_factors(record_year: int, forward_year: int,
                   capacity: Callable[[str, int], float]) -> dict[str, float]:

    def wind(y):
        return capacity("wind_onshore", y) + capacity("wind_offshore", y)

    return {"wind": wind(forward_year) / wind(record_year),
            "solar": capacity("solar", forward_year) / capacity("solar", record_year)}


def mean_demand_by_year(inputs: Mapping[Key, HalfHour]) -> dict[int, float]:
    acc: dict[int, list[float]] = defaultdict(list)
    for k, h in inputs.items():
        acc[int(k[0][:4])].append(h.demand_mw)
    return {y: float(np.mean(v)) for y, v in acc.items()}


#: One entry: (the inputs object, its yearly means). Held by identity, never by `id()` alone, so a
#: recycled id cannot hand one record's means to another.
_DEMAND_MEANS: list[tuple[Mapping[Key, HalfHour], dict[int, float]]] = []


def demand_factor(record_year: int, inputs: Mapping[Key, HalfHour]) -> float:
    """mean true demand of `DEMAND_REFERENCE_YEAR` over the record year's (module docstring)."""
    if not _DEMAND_MEANS or _DEMAND_MEANS[0][0] is not inputs:
        _DEMAND_MEANS[:] = [(inputs, mean_demand_by_year(inputs))]
    means = _DEMAND_MEANS[0][1]
    return means[DEMAND_REFERENCE_YEAR] / means[record_year]


def future_intensity_at(settlement_date: str | date_cls, settlement_period: int, seed: str, *,
                        world=None, inputs: Mapping[Key, HalfHour] | None = None,
                        gaps: Mapping[Key, str] | None = None,
                        capacity: Callable[[str, int], float] | None = None,
                        model: Model = FROZEN) -> tuple[float | None, dict]:
    """(gCO2/kWh or None, provenance) for a forward half hour of a generated future.

    `seed` is the seed the run extends its weather with (`run_phase2b` passes
    f"{world_id}:{run_base_seed()}"). The provenance names the analogue year, the record half hour
    it replays, the rescale, and the model's fit window. A None carries `reason`.
    """
    fwd = (settlement_date if isinstance(settlement_date, date_cls)
           else date_cls.fromisoformat(str(settlement_date)))
    prov: dict = {"data_regime": "synthetic", "forward_date": fwd.isoformat(), "forward_period": int(settlement_period),
                  "seed": seed, "model_form": model.form,
                  "fit_window": (model.fit_from, model.fit_to)}
    year, how = analogue_year(fwd.year, seed, world)
    if year is None:
        return None, {**prov, "reason": how}
    src_day = record_date(fwd, year)
    src_period, period_how = record_period(fwd, int(settlement_period), src_day)
    prov.update(analogue_year=year, analogue_resolved_by=how, record_date=src_day.isoformat())
    if src_period is None:
        return None, {**prov, "reason": period_how}
    key = (src_day.isoformat(), src_period)
    prov.update(record_period=src_period, period_alignment=period_how)
    if inputs is None:
        inputs, gaps = load_inputs()
    hh = inputs.get(key)
    if hh is None:
        why = (gaps or {}).get(key, "the record holds no inputs for this half hour")
        return None, {**prov, "reason": f"record half hour {key}: {why}"}
    fleet = fleet_factors(year, fwd.year, capacity)
    k_d = demand_factor(year, inputs)
    wind, solar = hh.wind_mw * fleet["wind"], hh.solar_mw * fleet["solar"]
    demand = hh.demand_mw * k_d
    share = (wind + solar) / demand
    value = predict(share, demand / 1e3, model=model, wind_gw=wind / 1e3, solar_gw=solar / 1e3)
    prov.update(record_inputs_mw=asdict(hh), wind_factor=round(fleet["wind"], 4),
                solar_factor=round(fleet["solar"], 4), demand_factor=round(k_d, 4),
                share=round(share, 4), demand_gw=round(demand / 1e3, 3),
                outside_fit=outside_fitted_range(share, demand / 1e3, model=model),
                level_error_g_per_kwh=level_error_g_per_kwh(model))
    return round(float(value), 1), prov


# ---------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------

def _row(label: str, g: dict) -> str:
    return (f"  {label:30s} corr {g['correlation']:.3f}  bias {g['bias']:+6.1f}  rmse {g['rmse']:5.1f}"
            f"  swing p95/p5 {g['swing_model']:.2f} (actual {g['swing_actual']:.2f}, model p5=0 on "
            f"{g['days_model_p5_zero']} days)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", default="neso_central:20260724",
                    help="the run's weather seed, f'{world_id}:{run_base_seed()}'")
    ap.add_argument("--week", default="2027-01-11", help="first day of the sample forward week")
    args = ap.parse_args(argv)

    record = load_record()
    refit = fit(record)
    print(f"shipped fit {FIT_WINDOW}: {asdict(refit)}")
    print(f"  differs from FROZEN: {'nothing' if refit == FROZEN else asdict(FROZEN)}")
    table = validation_table(record)
    print(f"\nFORMS: fitted {HELD_OUT_TRAIN}, graded on {HELD_OUT_YEAR} half hours")
    for label, g in table["forms"]:
        print(_row(label, g))
    print(f"\nREGIMES ({FORM}): graded on {HELD_OUT_YEAR}")
    for label, g in table["regimes"]:
        print(_row(label, g))
    print(f"\nROLLING ORIGIN ({FORM}): rmse (bias) on each year from each training rule")
    for year, row in table["rolling_origin"]:
        print(f"  {year}  " + "  ".join(f"{rule}: {g['rmse']:5.1f} ({g['bias']:+5.1f})"
                                        for rule, g in row.items()))

    inputs, gaps = load_inputs()
    start = date_cls.fromisoformat(args.week)
    year, how = analogue_year(start.year, args.seed)
    print(f"\nSAMPLE WEEK from {start} on seed {args.seed!r}: analogue year {year} ({how})")
    series, _ = gch.load_series()
    print("  forward date  rec date    future mean/min/max   record actual mean/min/max   "
          "factors w/s/d")
    for i in range(7):
        day = start + timedelta(days=i)
        vals, provs = [], []
        for p in range(1, gch.settlement_periods_on(day.isoformat()) + 1):
            v, prov = future_intensity_at(day, p, args.seed, inputs=inputs, gaps=gaps)
            if v is not None:
                vals.append(v)
                provs.append(prov)
        if not provs:
            print(f"  {day}  no value: {prov.get('reason')}")
            continue
        rec_day = provs[0]["record_date"]
        rec = [r.value for k, r in series.items() if k[0] == rec_day and r.value is not None]
        pv = provs[0]
        print(f"  {day}  {rec_day}  {np.mean(vals):6.1f} {min(vals):6.1f} {max(vals):6.1f}"
              f"        {np.mean(rec):6.1f} {min(rec):6.1f} {max(rec):6.1f}"
              f"        {pv['wind_factor']:.2f}/{pv['solar_factor']:.2f}/{pv['demand_factor']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
