"""Weather -> wholesale price sensitivity — Phase 4c-3 (physical simulation
layer).

Cold spells tighten gas supply/demand and spike wholesale prices (more gas
burned for heating and for gas-fired power generation simultaneously). This
module estimates a forward-price multiplier from the *lookback window's*
weather — consistent with the Point-in-Time Blindfold law (CLAUDE.md): the
forward price for a contract starting on `acquisition_date` may only use
information available before that date, so "is the market currently in a
cold spell" is read from the same historical lookback window
`sim.forward_curve.generate_forward_price` already uses for its spot-price
average, not from future weather.

Historical Ground Truth note: real Elexon SSP data (`sim/system_prices_history.py`)
already covers the full 2016-2025 simulation window per the Three
Architectural Laws — there is no synthetic price history to "replace" for
that period. This module's multiplier applies to the *synthetic forward
price* `sim.forward_curve` quotes for a new contract, not to historical
settlement prices.

BASELINE_HEATING_DEGREE_DAYS and the threshold/multiplier below are seed
estimates pending the `customer-archetype-data-enrichment` background task —
see `saas/property_model.py`'s module docstring for the same caveat.
"""

import statistics

from simulation.demand_model import heating_degree_days

# Typical UK daily heating-degree-days averaged over a year-round window
# (mild winters and zero-HDD summer days included) — a lookback-window
# average meaningfully above this indicates the window skews toward a cold
# spell rather than "normal" seasonal mix.
BASELINE_HEATING_DEGREE_DAYS = 5.5

# Lookback-window average HDD above this threshold signals a cold spell
# tight enough to move the forward price.
COLD_SPELL_HDD_THRESHOLD = 8.0

# Forward-price multiplier applied when a cold spell is signalled.
COLD_SPELL_PRICE_MULTIPLIER = 1.10


def average_heating_degree_days(daily_mean_temps_c: list[float]) -> float:
    """Mean heating-degree-days across `daily_mean_temps_c` (daily mean
    temperatures, degrees C). Raises ValueError on an empty list."""
    if not daily_mean_temps_c:
        raise ValueError("daily_mean_temps_c must be non-empty")
    return statistics.mean(heating_degree_days(t) for t in daily_mean_temps_c)


def weather_sensitivity_multiplier(daily_mean_temps_c: list[float]) -> float:
    """Forward-price multiplier reflecting cold-spell risk priced from a
    lookback window of daily mean temperatures.

    Returns COLD_SPELL_PRICE_MULTIPLIER if the window's average
    heating-degree-days exceeds COLD_SPELL_HDD_THRESHOLD (a cold spell —
    tight gas supply/demand pushes prices up), otherwise 1.0 (no
    adjustment).
    """
    if average_heating_degree_days(daily_mean_temps_c) > COLD_SPELL_HDD_THRESHOLD:
        return COLD_SPELL_PRICE_MULTIPLIER
    return 1.0
