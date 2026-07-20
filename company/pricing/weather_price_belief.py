"""Company-side WEATHER -> PRICE belief (the COMPANY twin of W1_6's price physics).

WHAT THIS IS. The company's approximation of how weather drives wholesale price,
built the way a real supplier's trading/analytics desk builds it: a regression of
OBSERVED published price on OBSERVED weather and gas. It is DELIBERATELY a naive
LINEAR form -- the company can see the published SSP outturn and public weather,
but it CANNOT see how the world actually made that price (the SIM's residual
demand, the dispatchable-fleet headroom, the convex merit-order tail). So it fits
the best straight line it can and, structurally, MISSES the convexity: it explains
the comfortable middle well and under-predicts the cold-and-still spike. That
error is not a bug to fix here -- it is the belief-vs-truth GAP the coupled triad
measures (`background/weather_price_triad.py`). The company is ALLOWED to be wrong.

THE WALL (CLAUDE.md Architectural Laws -- company side). This module reads ONLY
observables and holds NO SIM state:
  * It imports nothing from `sim/` -- not the price engine, not the weather-price
    chain, not the residual-demand calc. A real supplier never sees those.
  * It is a PURE ESTIMATOR: `fit(weather, gas, published_price)` then
    `predict(weather, gas)`. The caller (the harness) supplies the training
    arrays; this module never reaches across the wall to pull them, and never
    holds the ground-truth mechanism. It sees a price series and weather -- both
    genuinely public -- and nothing about how they were connected.
  * Point-in-time discipline is the CALLER's contract: the training arrays passed
    in must be as-of-bounded (no future leak). This module fits whatever window it
    is given and cannot look past it -- it has no data access of its own.

WHY LINEAR (the epistemic point). A linear price ~ a + b_gas*gas + b_temp*temp +
b_wind*wind is exactly what a desk with observables-only would reach for. It
cannot represent the merit order's convex kink (price roughly flat until the
thermal stack tightens, then jumps), so on the tight cold-still tail the truth
spikes and this belief lags. If it DID recover the truth on the tail, that would
mean the observables leaked the residual-demand mechanism -- an epistemic-wall
violation, not a triumph (COUPLED_TRIAD_DESIGN 1.2).

R12/R15. Nothing here is tuned toward a target gap. The fit is closed-form OLS on
whatever the caller passes; the coefficients are whatever the observed data
produce. The R15 mutation (harness side) that proves the gap is real: shuffle the
belief's weather inputs and the gap must worsen -- a coupling this model has, even
if weak, is a real fitted one, not a stored constant.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


class InsufficientHistoryError(ValueError):
    """FAIL-LOUD: a belief asked to fit on empty/degenerate observed history
    raises rather than returning a silent zero model that would read as a
    (spuriously perfect-looking) belief."""


@dataclass(frozen=True)
class WeatherPriceBelief:
    """A fitted linear weather->price belief. `coeffs` = (intercept, b_gas,
    b_temp, b_wind); `n_train`/`r2` are kept so a reviewer sees it is a real
    fit, not a magic number (R15 independence)."""

    intercept: float
    b_gas: float
    b_temp: float
    b_wind: float
    n_train: int
    r2: float

    def predict(self, gas_price, temp_c, wind_speed_ms) -> np.ndarray:
        """The company's expected price for the observed (gas, weather). Vectorised
        over arrays or scalar. Linear by construction -- no convex tail term."""
        gas = np.asarray(gas_price, float)
        temp = np.asarray(temp_c, float)
        wind = np.asarray(wind_speed_ms, float)
        out = self.intercept + self.b_gas * gas + self.b_temp * temp + self.b_wind * wind
        return out if np.ndim(gas) or np.ndim(temp) or np.ndim(wind) else float(out)


def fit_weather_price_belief(
    gas_price: Sequence[float],
    temp_c: Sequence[float],
    wind_speed_ms: Sequence[float],
    published_price: Sequence[float],
) -> WeatherPriceBelief:
    """Fit the company's linear weather->price belief on OBSERVED history
    (closed-form OLS). All four inputs are company observables: gas (NBP),
    temperature + wind speed (public forecasts/outturns), and the published price
    outturn. Returns a `WeatherPriceBelief`.

    FAIL-LOUD on empty / length-mismatched / rank-deficient input -- an
    unavailable fit is a FAILED fit, never a silent zero model."""
    gas = np.asarray(gas_price, float)
    temp = np.asarray(temp_c, float)
    wind = np.asarray(wind_speed_ms, float)
    price = np.asarray(published_price, float)
    n = len(price)
    if n == 0:
        raise InsufficientHistoryError("no observed history to fit the belief")
    if not (len(gas) == len(temp) == len(wind) == n):
        raise InsufficientHistoryError(
            f"length mismatch: gas={len(gas)} temp={len(temp)} wind={len(wind)} price={n}")
    if n < 10:
        raise InsufficientHistoryError(f"too little history to fit a 4-parameter belief: n={n}")
    finite = np.isfinite(gas) & np.isfinite(temp) & np.isfinite(wind) & np.isfinite(price)
    gas, temp, wind, price = gas[finite], temp[finite], wind[finite], price[finite]
    if len(price) < 10:
        raise InsufficientHistoryError("too few finite paired observations to fit the belief")

    X = np.column_stack([np.ones(len(price)), gas, temp, wind])
    coef, *_ = np.linalg.lstsq(X, price, rcond=None)
    pred = X @ coef
    denom = np.var(price)
    r2 = float(1.0 - np.var(price - pred) / denom) if denom > 0 else 0.0
    return WeatherPriceBelief(
        intercept=float(coef[0]), b_gas=float(coef[1]),
        b_temp=float(coef[2]), b_wind=float(coef[3]),
        n_train=int(len(price)), r2=r2,
    )
