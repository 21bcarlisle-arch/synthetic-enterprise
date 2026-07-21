"""Company-side WEATHER -> DEMAND belief -- weather-normalisation (the COMPANY
twin of W1_5's premise-demand physics, C13_weather_normalisation).

WHAT THIS IS. The company's approximation of how weather drives its book's
demand, built the way a real supplier's forecasting/settlement desk builds it: a
DEGREE-DAY regression of OBSERVED metered demand on OBSERVED published
temperature. It is the industry-standard "regression-based weather normalisation"
method (DISCOVER doc section 2): fit consumption per unit heating/cooling
degree-day on the company's own confounded meter history, then feed a given
weather outturn back through the fitted coefficients to predict demand. It is
DELIBERATELY temperature-only degree-days -- the company sees published
temperature and its own aggregate meter reads, but it CANNOT see the wind-driven
heat loss (the gas-industry Composite Weather Variable), the working-day/daylight
load structure, or the regional dispersion of its book across the weather field.
So it fits the best degree-day model it can and, structurally, MISSES those --
worst on the cold stress cell where the missing structure bites hardest. That
error is not a bug to fix here -- it is the belief-vs-truth GAP the coupled triad
measures (`background/weather_demand_triad.py`). The company is ALLOWED to be
wrong; that imperfection is the point.

THE WALL (CLAUDE.md Architectural Laws -- company side). This module reads ONLY
observables and holds NO SIM state:
  * It imports nothing from `sim/`/`simulation/` -- not the premise-demand
    physics (W1_5, `simulation/premise_demand.py`), not the regional weather
    field (W1_4), not `sim/weather_hdd.py`'s per-customer real-CSV read (exactly
    the read a real supplier CANNOT do, DISCOVER section 1's single most important
    finding). It reconstructs the HDD/CDD METHOD company-side from observables.
  * It is a PURE ESTIMATOR: `fit(temp_c, observed_demand)` then `predict(temp_c)`.
    The caller (the harness) supplies the training arrays -- OBSERVED published
    temperature and the company's OWN confounded aggregate meter reads. This
    module never reaches across the wall to pull demand or weather itself, and it
    never holds the ground-truth demand mechanism. It sees a demand series and
    temperature, both genuinely observable to a real supplier, and nothing about
    how the demand was physically formed.
  * Point-in-time discipline is the CALLER's contract: the training arrays passed
    in must be as-of-bounded (no future leak). This module fits whatever window it
    is given and cannot look past it -- it has no data access of its own.

WHY TEMPERATURE-ONLY DEGREE-DAYS (the epistemic point + R10 named simplification).
HDD/CDD regression is exactly what a desk with observables-only reaches for
(UK domestic gas convention: HDD base 15.5C). It CANNOT represent wind chill (real
heat loss rises with wind speed on cold days -- the industry's CWV term), nor the
non-linear regional-dispersion convexity of the W1_5 field. So on the cold-and-
windy tail the truth runs above what a temperature-only degree-day model expects
and this belief lags. If it DID recover the truth on the tail, that would mean the
observables leaked the W1_5 thermal/regional mechanism -- an epistemic-wall
violation, not a triumph (COUPLED_TRIAD_DESIGN 1.2). The wind term is a REGISTERED
simplification (R10), a named L1->L2 refinement, not a hidden defect.

R12/R15. Nothing here is tuned toward a target gap. The fit is closed-form OLS on
whatever the caller passes; the coefficients are whatever the observed data
produce. The R15 mutation (harness side) that proves the gap is real: degrade the
belief (zero its weather sensitivity, or shuffle its temperature inputs) and the
gap must worsen -- a coupling this model has is a real fitted one, not a stored
constant.

L1->L2 REFINEMENT (2026-07-21, the two named refinements from the C13 map block).
Both are ADDITIVE and OPTIONAL -- omitting them reproduces the L1 temperature-only
model EXACTLY (regression-safe by construction, no re-opening the L1 fit):

  1. WIND-CHILL (Composite Weather Variable) TERM. Real GB gas-NDM-allocation
     practice adjusts degree-days by wind: heat loss on a heating day rises with
     wind speed above a light-breeze reference (the gas industry's CWV term,
     C13_WEATHER_NORMALISATION_DISCOVER.md sec2). Both TEMPERATURE and WIND SPEED
     are published weather observables (Open-Meteo/Met Office) -- the SAME
     epistemic status as temperature, so adding wind crosses no wall the L1 model
     didn't already cross. `fit_weather_normalisation_belief(..., wind_speed_ms=...)`
     adds a 4th OLS regressor (HDD * excess-wind-above-calm); the coefficient is
     FITTED, never fabricated (R12/R15) -- it may come out small/zero on a given
     window, which is itself an honest finding, not a defect.
  2. BOOK-WEIGHTED (regional-dispersion) TEMPERATURE. A belief fit purely on the
     NATIONAL mean temperature implicitly assumes the company's book is
     regionally distributed like the nation -- false for any book with regional
     skew (the C13 map note's "nationally-normalised book with regional skew
     mis-predicts"). `book_weighted_temperature` lets a caller combine (a)
     PUBLISHED per-region weather outturns (genuinely public, the same status as
     national temperature) with (b) the company's OWN book's regional
     concentration (genuinely company-knowable -- its own customer register, not
     a SIM read) into a book-weighted temperature series, which then flows
     through the SAME fit/predict pipeline in place of the raw national series.
     No new model form is needed -- discrimination is an INPUT transform, not a
     new coefficient. R10 NAMED LIMIT (FRAME sec5/6 open-Q3): a genuine per-book
     regional DEMAND truth to fit/measure this against does not yet exist inside
     this atom's wall-respecting file_scope (it needs W1_4's regional field to
     cross via a typed `sim_interface.py` observable, out-of-scope BUILD named
     separately in the FRAME) -- so this capability is built and unit-proven
     against SYNTHETIC truth (same pattern as the existing wind-coupled-truth
     test below), and is NOT yet wired into `background/weather_demand_triad.py`'s
     real-record coupled-triad measurement. Registered, not hidden.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

import numpy as np

# UK convention degree-day base temperatures (deg C). Conventional, NOT fitted
# (R10): heating base 15.5C is the DECC/Ofgem domestic gas convention (the same
# value `simulation/demand_model.py` and `sim/weather_hdd.py` use, on the far side
# of the wall); the 18C cooling base captures the modest GB summer AC/refrigeration
# rise. A real desk uses conventional bases and lets the regression find the
# coefficients -- it does not fit the base temperature at L1.
HEATING_BASE_TEMP_C: float = 15.5
COOLING_BASE_TEMP_C: float = 18.0

# CWV wind-chill reference (m/s). A CONVENTION, not fitted (R10), mirroring how
# the degree-day bases above are held fixed: the "calm" reference above which
# extra wind-driven heat loss is counted -- UK Met Office Beaufort force 3
# ("light breeze", ~3.4-5.4 m/s midpoint ~4 m/s). Below this, wind contributes no
# additional heat-loss load; above it, heat loss on a heating day rises with the
# excess. The REGRESSION finds how much (b_windchill); this constant only sets
# where the effect starts, exactly as the degree-day bases set where heating/
# cooling load starts.
WINDCHILL_CALM_THRESHOLD_MS: float = 4.0


class InsufficientHistoryError(ValueError):
    """FAIL-LOUD: a belief asked to fit on empty/degenerate observed history
    raises rather than returning a silent zero model that would read as a
    (spuriously perfect-looking) belief."""


class MissingWindObservableError(ValueError):
    """FAIL-LOUD: a belief fitted WITH a wind-chill term asked to `predict`
    WITHOUT a wind observable would otherwise silently drop the fitted term
    (FAIL-OPEN) -- raise instead of quietly degrading to a worse prediction the
    caller never asked for."""


class InvalidRegionWeightsError(ValueError):
    """FAIL-LOUD: `book_weighted_temperature` given a malformed book-composition
    weighting (missing region, negative weight, weights not summing to 1) raises
    rather than silently producing a wrongly-weighted (and wrongly-confident)
    book temperature series."""


def _hdd(temp_c) -> np.ndarray:
    """Heating degree-days: degrees below the heating base, floored at 0."""
    return np.clip(HEATING_BASE_TEMP_C - np.asarray(temp_c, float), 0.0, None)


def _cdd(temp_c) -> np.ndarray:
    """Cooling degree-days: degrees above the cooling base, floored at 0."""
    return np.clip(np.asarray(temp_c, float) - COOLING_BASE_TEMP_C, 0.0, None)


def _windchill_dd(hdd: np.ndarray, wind_ms) -> np.ndarray:
    """Wind-chill degree-days: heating-degree-day load scaled by EXCESS wind
    above the calm reference (`WINDCHILL_CALM_THRESHOLD_MS`) -- zero on a
    non-heating day (hdd=0) or a calm day (wind<=threshold), rising with both
    cold and wind together (a co-occurrence term, not two separate marginals --
    same construction as the harness's `cold_windy_tail_mask`)."""
    excess_wind = np.clip(np.asarray(wind_ms, float) - WINDCHILL_CALM_THRESHOLD_MS, 0.0, None)
    return np.asarray(hdd, float) * excess_wind


@dataclass(frozen=True)
class WeatherNormalisationBelief:
    """A fitted degree-day weather-normalisation belief. `coeffs` = (base, b_hdd,
    b_cdd[, b_windchill]) demand per unit HDD/CDD[/wind-chill-DD]; `n_train`/`r2`
    are kept so a reviewer sees it is a real fit, not a magic number (R15
    independence).

    `b_windchill`/`has_wind_term` default to the L1 temperature-only shape
    (0.0/False) -- an L1-era caller constructing this dataclass by hand (as the
    coupled-triad's own degraded-belief mutation test does) is unaffected;
    `has_wind_term` is set only by `fit_weather_normalisation_belief` when a
    wind observable was actually supplied and fitted (L2)."""

    base: float
    b_hdd: float          # demand per heating-degree-day
    b_cdd: float          # demand per cooling-degree-day
    n_train: int
    r2: float
    b_windchill: float = 0.0     # demand per wind-chill-degree-day (L2, CWV term)
    has_wind_term: bool = False  # True only if fitted WITH a wind observable

    def predict(self, temp_c, wind_speed_ms=None) -> np.ndarray:
        """The company's expected (weather-normalised) demand for the observed
        temperature[, wind]. Vectorised over arrays or scalar.

        L1 behaviour (has_wind_term=False) is UNCHANGED: degree-day linear, no
        wind-chill term, `wind_speed_ms` (if passed) is simply ignored -- this is
        what makes the L2 addition regression-safe by construction.

        L2 behaviour (has_wind_term=True): FAIL-LOUD if `wind_speed_ms` is not
        supplied -- silently dropping a fitted wind-chill term would quietly
        degrade the prediction the caller never asked for (FAIL-OPEN, forbidden
        by R15's own doctrine)."""
        hdd = _hdd(temp_c)
        cdd = _cdd(temp_c)
        out = self.base + self.b_hdd * hdd + self.b_cdd * cdd
        if self.has_wind_term:
            if wind_speed_ms is None:
                raise MissingWindObservableError(
                    "belief was fitted WITH a wind-chill (CWV) term "
                    "(has_wind_term=True) but predict() was called without "
                    "wind_speed_ms -- pass the observed wind speed"
                )
            out = out + self.b_windchill * _windchill_dd(hdd, wind_speed_ms)
        return out if np.ndim(temp_c) else float(out)


def fit_weather_normalisation_belief(
    temp_c: Sequence[float],
    observed_demand: Sequence[float],
    wind_speed_ms: Optional[Sequence[float]] = None,
) -> WeatherNormalisationBelief:
    """Fit the company's degree-day weather-normalisation belief on OBSERVED
    history (closed-form OLS). Inputs are all company observables: published
    temperature[, published wind speed] and the company's OWN confounded
    aggregate meter reads. Returns a `WeatherNormalisationBelief`.

    `wind_speed_ms=None` (default) -- L1 behaviour, byte-identical to the
    original temperature-only 3-parameter fit (regression-safe by
    construction: no wind column is ever added to X unless a caller opts in).

    `wind_speed_ms=<observed wind>` -- L2: adds a 4th regressor, the wind-chill
    degree-day (`_windchill_dd`, the CWV term) alongside HDD/CDD. The extra
    parameter is more data-hungry (4 unknowns vs 3), so the minimum history
    requirement is stricter than the temperature-only fit.

    FAIL-LOUD on empty / length-mismatched / rank-deficient input -- an
    unavailable fit is a FAILED fit, never a silent zero model."""
    temp = np.asarray(temp_c, float)
    demand = np.asarray(observed_demand, float)
    n = len(demand)
    use_wind = wind_speed_ms is not None
    min_n = 20 if use_wind else 10
    n_params = 4 if use_wind else 3

    if n == 0:
        raise InsufficientHistoryError("no observed history to fit the belief")
    if len(temp) != n:
        raise InsufficientHistoryError(
            f"length mismatch: temp={len(temp)} demand={n}")
    wind: Optional[np.ndarray] = None
    if use_wind:
        wind = np.asarray(wind_speed_ms, float)
        if len(wind) != n:
            raise InsufficientHistoryError(
                f"length mismatch: wind={len(wind)} demand={n}")
    if n < min_n:
        raise InsufficientHistoryError(
            f"too little history to fit a {n_params}-parameter degree-day "
            f"belief: n={n} (need >= {min_n})")

    finite = np.isfinite(temp) & np.isfinite(demand)
    if use_wind:
        finite = finite & np.isfinite(wind)
        temp, demand, wind = temp[finite], demand[finite], wind[finite]
    else:
        temp, demand = temp[finite], demand[finite]
    if len(demand) < min_n:
        raise InsufficientHistoryError(
            "too few finite paired observations to fit the belief")

    hdd = _hdd(temp)
    cdd = _cdd(temp)
    if use_wind:
        windchill = _windchill_dd(hdd, wind)
        X = np.column_stack([np.ones(len(demand)), hdd, cdd, windchill])
    else:
        X = np.column_stack([np.ones(len(demand)), hdd, cdd])
    coef, *_ = np.linalg.lstsq(X, demand, rcond=None)
    pred = X @ coef
    denom = np.var(demand)
    r2 = float(1.0 - np.var(demand - pred) / denom) if denom > 0 else 0.0
    return WeatherNormalisationBelief(
        base=float(coef[0]), b_hdd=float(coef[1]), b_cdd=float(coef[2]),
        n_train=int(len(demand)), r2=r2,
        b_windchill=float(coef[3]) if use_wind else 0.0,
        has_wind_term=use_wind,
    )


# ---------------------------------------------------------------------------
# Regional-dispersion discrimination (L1->L2 refinement 2): book-weighted
# temperature -- an INPUT transform, not a new model form (see module docstring).
# ---------------------------------------------------------------------------

def book_weighted_temperature(
    region_temps: Mapping[str, Sequence[float]],
    region_weights: Mapping[str, float],
) -> np.ndarray:
    """Combine PUBLISHED per-region weather outturns (`region_temps`, genuinely
    public) with the company's OWN book's regional concentration
    (`region_weights`, genuinely company-knowable -- its own customer register,
    never a SIM read) into a book-weighted temperature series.

    Feeding this series into `fit_weather_normalisation_belief`/`predict` in
    place of the raw national temperature discriminates a regionally-skewed
    book from a nationally-average one -- the "regional-dispersion" refinement:
    a book concentrated in a colder region should be normalised against ITS
    weather, not the national mean.

    FAIL-LOUD (not FAIL-OPEN): the region key sets of `region_temps` and
    `region_weights` must match exactly, every weight must be non-negative, and
    the weights must sum to 1 (a book's regional shares, a genuine partition of
    the whole book) within 1e-6 -- a silently mismatched or unnormalised
    weighting would produce a wrongly-confident book temperature no different
    in shape from a bug."""
    temp_keys = set(region_temps.keys())
    weight_keys = set(region_weights.keys())
    if temp_keys != weight_keys:
        raise InvalidRegionWeightsError(
            f"region_temps keys {sorted(temp_keys)} != "
            f"region_weights keys {sorted(weight_keys)}"
        )
    if not temp_keys:
        raise InvalidRegionWeightsError("no regions supplied")
    weights = {r: float(w) for r, w in region_weights.items()}
    if any(w < 0 for w in weights.values()):
        raise InvalidRegionWeightsError(
            f"negative book weight(s): {weights}")
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-6:
        raise InvalidRegionWeightsError(
            f"book weights must sum to 1 (own book's regional shares); "
            f"sum={total:g}"
        )
    arrays = {r: np.asarray(t, float) for r, t in region_temps.items()}
    lengths = {len(a) for a in arrays.values()}
    if len(lengths) != 1:
        raise InvalidRegionWeightsError(
            f"region temperature series have mismatched lengths: "
            f"{ {r: len(a) for r, a in arrays.items()} }"
        )
    n = lengths.pop()
    out = np.zeros(n, dtype=float)
    for region, w in weights.items():
        out = out + w * arrays[region]
    return out
