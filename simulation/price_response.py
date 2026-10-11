"""A household's 2022 price response, drawn from SERL's published per-household elasticity.

WHAT IT IS
----------
Each household draws two short-run price elasticities, one per fuel. It then scales that fuel's
kWh by how far the cap's household-facing unit rate on the day sits from the mean rate over its
PRIOR winter. The response years run April to March, and the level each year ends on is carried
into the next:

    M(d) = L(k-1) * (1 + e * (p(d) / pbar_winter(k-1) - 1))
    L(k) = L(k-1) * (1 + e * (pbar_winter(k) / pbar_winter(k-1) - 1)),   L(2021) = 1

So the response is re-evaluated at every cap change. A cut, once made, is carried forward. A fall
in price is answered against the winter just gone, which is where the partial decay comes from.

WHY THIS AND NOT THE PREBOUND PRICE LEG
----------------------------------------
`premise_trace.comfort_constraint_for` has a price leg (`_PRICE_ELASTICITY = 0.45`, unsourced) that
no caller feeds. Measured on and off, it got SERL's gas median roughly right and the rest wrong: no
spread, a cut a quarter before the price rose (one constraint per calendar year), no decay, and no
electricity response at all
(`docs/staging/records/SEAT_RESULT_THE_PREBOUND_PRICE_LEG_GETS_THE_2022_GAS_MEDIAN_ROUGHLY_RIGHT_AND_THE_DISTRIBUTION_WRONG_2026-10-11.md`).
This replaces the coefficient with the published distribution and the calendar year with the cap
period. It is graded in
`docs/staging/records/SEAT_PREREG_A_PER_HOUSEHOLD_SERL_ELASTICITY_AGAINST_THE_PRIOR_WINTERS_PRICE_2026-10-11.md`.

WHAT IS ASSUMED, AND WHICH WAY IT RUNS
--------------------------------------
- The tails beyond SERL's quartiles are not published. A split normal through the median and each
  quartile is a shape assumption. It is thinner-tailed than SERL's reduction histogram, which has a
  long tail past 50%.
- The joint of the two fuels is not published, so they are drawn independently. SERL Fig. 3
  (poorer households more elastic on gas, wealthier on electricity) says the draws are not
  comonotone. It does not say they are independent, and no income gradient is drawn.
- Every household responds to the CAP rate, not to its own tariff. A household on a fixed term saw
  the rise later than the cap moved. That needs the demand<->tariff coupling W1_12 names.
- Nothing responds before response year 2022. SERL's counterfactual winter is 2021/22, and its
  elasticity is crisis-specific (the knowledge file: not "the world's general-purpose
  elasticity"). So the October 2021 rise, and any anticipation of April's, goes unanswered.
  ECUK's annual 2021->2022 fall carries both.
- The whole fuel scales, and the day's shape is kept. SERL's top quintile cut its thermostat, which
  would reshape the heating day. That shape change is not modelled.

EPISTEMIC NOTE
--------------
World-side ground truth. The elasticities never cross the seam: the company sees only the metered
kWh they produce.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from statistics import NormalDist
from typing import Callable, Mapping, Sequence

from simulation.rng_substream import substream
from simulation.svt_rates import (
    get_svt_elec_rate_charged_to_household_gbp_per_mwh,
    get_svt_gas_rate_charged_to_household_gbp_per_mwh,
)

#: (lower quartile, median, upper quartile) of the per-household short-run price elasticity, same
#: households, winter 2022/23 against 2021/22. Zapata-Webborn et al. (2024), Energy and Buildings
#: 305, 113869, as recorded in
#: docs/market_research/how_much_a_same_households_use_moves_year_on_year_and_in_2022.md.
SERL_GAS_ELASTICITY_QUARTILES = (-0.144, -0.071, -0.010)
SERL_ELECTRICITY_ELASTICITY_QUARTILES = (-0.223, -0.099, 0.016)

#: SERL's winter: October to March (the paper's Oct 2022-Mar 2023 against Oct 2021-Mar 2022).
WINTER_MONTHS = (10, 11, 12, 1, 2, 3)

#: The first response year (April 2022 - March 2023). Its reference is winter 2021/22, which is
#: SERL's counterfactual winter, so the response is measured from exactly where SERL measured it.
FIRST_RESPONSE_YEAR = 2022

RNG_NAMESPACE = "price_response"
_Z_QUARTILE = NormalDist().inv_cdf(0.75)


@dataclass(frozen=True)
class HouseholdPriceElasticity:
    gas: float
    electricity: float


def split_normal_quantile(u: float, quartiles: tuple[float, float, float]) -> float:
    """The value at probability `u` of a split normal through (q1, median, q3)."""
    if not 0.0 < u < 1.0:
        raise ValueError(f"a quantile needs 0 < u < 1, got {u}")
    q1, median, q3 = quartiles
    if not q1 < median < q3:
        raise ValueError(f"quartiles must be strictly increasing, got {quartiles}")
    z = NormalDist().inv_cdf(u)
    scale = (median - q1 if z < 0 else q3 - median) / _Z_QUARTILE
    return median + scale * z


def draw_elasticity(customer_id: str, seed: int) -> HouseholdPriceElasticity:
    """One household's two elasticities, from its own named substream."""
    rng = substream(RNG_NAMESPACE, f"elasticity::{customer_id}", seed)
    u_gas, u_elec = rng.random(), rng.random()
    # random() can return exactly 0.0; the quantile is undefined there.
    u_gas, u_elec = max(u_gas, 1e-12), max(u_elec, 1e-12)
    return HouseholdPriceElasticity(
        gas=split_normal_quantile(u_gas, SERL_GAS_ELASTICITY_QUARTILES),
        electricity=split_normal_quantile(u_elec, SERL_ELECTRICITY_ELASTICITY_QUARTILES),
    )


def _response_year(day: dt.date) -> int:
    return day.year if day.month >= 4 else day.year - 1


def _winter_days(response_year: int) -> list[dt.date]:
    start, end = dt.date(response_year, 10, 1), dt.date(response_year + 1, 3, 31)
    return [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]


def _rate(rate_fn: Callable[[str], float | None], day: dt.date) -> float:
    rate = rate_fn(day.isoformat())
    if rate is None or not rate > 0:
        raise ValueError(f"no household-facing rate on {day.isoformat()}: cannot price the response")
    return rate


def response_multipliers(
    dates: Sequence[dt.date],
    elasticity: float,
    rate_fn: Callable[[str], float | None],
) -> dict[str, float]:
    """The per-day multiplier on one fuel's kWh, keyed by ISO date.

    1.0 on every day before response year `FIRST_RESPONSE_YEAR`. Raises rather than answering 1.0
    on a day whose rate is missing: a silent 1.0 would read as "this household did not respond".
    """
    winter_mean: dict[int, float] = {}

    def pbar(year: int) -> float:
        if year not in winter_mean:
            days = _winter_days(year)
            winter_mean[year] = sum(_rate(rate_fn, d) for d in days) / len(days)
        return winter_mean[year]

    level: dict[int, float] = {FIRST_RESPONSE_YEAR - 1: 1.0}

    def level_at(year: int) -> float:
        for k in range(max(level) + 1, year + 1):
            level[k] = level[k - 1] * (1.0 + elasticity * (pbar(k) / pbar(k - 1) - 1.0))
        return level[year]

    out: dict[str, float] = {}
    for day in dates:
        k = _response_year(day)
        if k < FIRST_RESPONSE_YEAR:
            out[day.isoformat()] = 1.0
            continue
        m = level_at(k - 1) * (1.0 + elasticity * (_rate(rate_fn, day) / pbar(k - 1) - 1.0))
        # kWh cannot go negative. Reaching this needs e below -1/(p/pbar - 1), about -0.65 for gas
        # in 2022: a draw more than five scales out.
        out[day.isoformat()] = max(m, 0.0)
    return out


def household_multipliers(
    customer_id: str, dates: Sequence[dt.date], *, seed: int
) -> Mapping[str, dict[str, float]]:
    """Both fuels' per-day multipliers for one household, at the cap's household-facing rates."""
    e = draw_elasticity(customer_id, seed)
    return {
        "gas": response_multipliers(dates, e.gas, get_svt_gas_rate_charged_to_household_gbp_per_mwh),
        "electricity": response_multipliers(
            dates, e.electricity, get_svt_elec_rate_charged_to_household_gbp_per_mwh
        ),
    }
