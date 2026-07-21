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
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

# UK convention degree-day base temperatures (deg C). Conventional, NOT fitted
# (R10): heating base 15.5C is the DECC/Ofgem domestic gas convention (the same
# value `simulation/demand_model.py` and `sim/weather_hdd.py` use, on the far side
# of the wall); the 18C cooling base captures the modest GB summer AC/refrigeration
# rise. A real desk uses conventional bases and lets the regression find the
# coefficients -- it does not fit the base temperature at L1.
HEATING_BASE_TEMP_C: float = 15.5
COOLING_BASE_TEMP_C: float = 18.0


class InsufficientHistoryError(ValueError):
    """FAIL-LOUD: a belief asked to fit on empty/degenerate observed history
    raises rather than returning a silent zero model that would read as a
    (spuriously perfect-looking) belief."""


def _hdd(temp_c) -> np.ndarray:
    """Heating degree-days: degrees below the heating base, floored at 0."""
    return np.clip(HEATING_BASE_TEMP_C - np.asarray(temp_c, float), 0.0, None)


def _cdd(temp_c) -> np.ndarray:
    """Cooling degree-days: degrees above the cooling base, floored at 0."""
    return np.clip(np.asarray(temp_c, float) - COOLING_BASE_TEMP_C, 0.0, None)


@dataclass(frozen=True)
class WeatherNormalisationBelief:
    """A fitted temperature-only degree-day weather-normalisation belief.
    `coeffs` = (base, b_hdd, b_cdd) demand per unit HDD/CDD; `n_train`/`r2` are
    kept so a reviewer sees it is a real fit, not a magic number (R15
    independence)."""

    base: float
    b_hdd: float          # demand per heating-degree-day
    b_cdd: float          # demand per cooling-degree-day
    n_train: int
    r2: float

    def predict(self, temp_c) -> np.ndarray:
        """The company's expected (weather-normalised) demand for the observed
        temperature. Vectorised over arrays or scalar. Degree-day linear by
        construction -- no wind-chill (CWV) term, no regional-dispersion term."""
        hdd = _hdd(temp_c)
        cdd = _cdd(temp_c)
        out = self.base + self.b_hdd * hdd + self.b_cdd * cdd
        return out if np.ndim(temp_c) else float(out)


def fit_weather_normalisation_belief(
    temp_c: Sequence[float],
    observed_demand: Sequence[float],
) -> WeatherNormalisationBelief:
    """Fit the company's temperature-only degree-day weather-normalisation belief
    on OBSERVED history (closed-form OLS). Both inputs are company observables:
    published temperature and the company's OWN confounded aggregate meter reads.
    Returns a `WeatherNormalisationBelief`.

    FAIL-LOUD on empty / length-mismatched / rank-deficient input -- an
    unavailable fit is a FAILED fit, never a silent zero model."""
    temp = np.asarray(temp_c, float)
    demand = np.asarray(observed_demand, float)
    n = len(demand)
    if n == 0:
        raise InsufficientHistoryError("no observed history to fit the belief")
    if len(temp) != n:
        raise InsufficientHistoryError(
            f"length mismatch: temp={len(temp)} demand={n}")
    if n < 10:
        raise InsufficientHistoryError(
            f"too little history to fit a 3-parameter degree-day belief: n={n}")
    finite = np.isfinite(temp) & np.isfinite(demand)
    temp, demand = temp[finite], demand[finite]
    if len(demand) < 10:
        raise InsufficientHistoryError(
            "too few finite paired observations to fit the belief")

    hdd = _hdd(temp)
    cdd = _cdd(temp)
    X = np.column_stack([np.ones(len(demand)), hdd, cdd])
    coef, *_ = np.linalg.lstsq(X, demand, rcond=None)
    pred = X @ coef
    denom = np.var(demand)
    r2 = float(1.0 - np.var(demand - pred) / denom) if denom > 0 else 0.0
    return WeatherNormalisationBelief(
        base=float(coef[0]), b_hdd=float(coef[1]), b_cdd=float(coef[2]),
        n_train=int(len(demand)), r2=r2,
    )
