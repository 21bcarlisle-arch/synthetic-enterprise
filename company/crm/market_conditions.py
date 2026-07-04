"""Company-observable market switching conditions -- Phase QB.

A real UK supplier tracks published switching-savings estimates every year --
Ofgem Consumer Engagement Survey, DESNZ switching statistics, Cornwall Insight
market commentary -- to gauge how much of its book is genuinely at risk of
leaving for a competitor, independent of its own rate decisions. In a year
where no fixed deal undercuts the default tariff (2022: wholesale costs
exceeded the price cap, suppliers withdrew fixed products), even large rate
rises don't drive switching -- there's nowhere cheaper to go.

This mirrors the SIM's `simulation.market_switching_propensity` (also built
from the same public DESNZ/Ofgem series) but is reimplemented independently
here: the company layer must not import from `simulation/`.

MARKET_SWITCHING_MULTIPLIER_BY_YEAR values match the calibration already
published for board-facing population anchoring
(`tools/population_anchor.py`'s CALIBRATED_MULTIPLIER) -- both are
derived from the same public switching-rate series, normalised to 2024 = 1.0.
"""
from __future__ import annotations

MARKET_SWITCHING_MULTIPLIER_BY_YEAR: dict[int, float] = {
    2016: 2.17, 2017: 1.88, 2018: 1.72, 2019: 1.43,
    2020: 0.95, 2021: 0.57, 2022: 0.44, 2023: 0.79,
    2024: 1.00, 2025: 0.93,
}

DEFAULT_MULTIPLIER = 1.00


def market_conditions_multiplier(renewal_year: int | None) -> float:
    """Return the published market-switching-opportunity multiplier for `renewal_year`.

    Normalised so 2024 (new-normal, post-fairer-pricing-rule) = 1.0. Below 1.0
    means fewer/less attractive competitor deals than the 2024 baseline
    (e.g. 2022 crisis: 0.44); above 1.0 means more competitive switching
    conditions (e.g. 2016 peak-competition era: 2.17).

    Returns DEFAULT_MULTIPLIER (1.0) for `None` or an unlisted year.
    """
    if renewal_year is None:
        return DEFAULT_MULTIPLIER
    return MARKET_SWITCHING_MULTIPLIER_BY_YEAR.get(renewal_year, DEFAULT_MULTIPLIER)
