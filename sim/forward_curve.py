"""Generation of synthetic forward prices for fixed-rate tariffs.

Synthetic Forward Curve law: no real UK forward-curve data exists for this
purpose, so a forward price is built FROM real historical spot data — the
Historical Ground Truth law stays satisfied because the base is always real
spot, never invented. The output is a SYNTHETIC number and must be labelled
as such wherever it is used downstream (it is the input `saas/tariff_pricing`
applies its margin to, not a real market quote).

PHASE 41-PREP REFORM: replaced the old (base + pstdev × risk_factor) formula
with a proper term-structure model matching how UK baseload forwards actually
behave:

    forward = spot_ewma × seasonal_shape(delivery_months, fuel) × (1 + term_premium)

Components:
  1. spot_ewma — exponentially weighted moving average of daily mean System
     Sell Price over [acquisition_date − lookback_days, acquisition_date − 1].
     EWMA half-life = 30 days (faster regime adaptation than the old 90-day SMA;
     still strictly backward-looking → PIT safe).
  2. seasonal_shape — arithmetic mean of monthly multipliers across every
     calendar month in the delivery window. Separate tables for electricity
     (N2EX baseload) and gas (NBP). For a 12-month contract, each averages
     to ≈ 1.00 regardless of start month.
  3. term_premium — BASE_TERM_PREMIUM × sqrt(tenor_years) × (risk_factor / 1.2).
     Captures: liquidity premium (thin far-forward book), cost of carry
     (collateral on forward positions), and uncertainty growing as sqrt(time).
     Electricity: ≈ 6% for 1-year baseload (2016-2020 range: 8-19%).
     Gas: ≈ 5% for 1-year NBP (more liquid forward market → lower liquidity premium).

PHASE 42 ADDITION: fuel-specific seasonal multipliers.
  Gas has much more extreme winter/summer seasonality than electricity:
  - Q1 (Jan-Mar): space heating peak — up to 3-4× summer demand in UK.
  - Q2-Q3 (Apr-Sep): minimal heating, industrial only — summer trough.
  - Q4 (Oct-Dec): winter onset, storage injection season ends.
  Calibrated to UK NBP seasonal price spreads 2016-2025.

Phase 4c-3 weather sensitivity multiplier is preserved unchanged.
"""

import statistics
from datetime import date, timedelta

from sim.weather_price_sensitivity import weather_sensitivity_multiplier

# Monthly seasonal multipliers (1=Jan … 12=Dec).
# ELECTRICITY: calibrated to UK N2EX historical baseload seasonality 2016-2025.
#   Q4/Q1: peak demand, low renewable output → premium
#   Q2/Q3: mild demand, high solar/wind surplus → discount
# Annual arithmetic mean = 1.002 — 12-month contracts are near-flat on seasonal.
MONTH_SEASONAL_MULTIPLIER: dict[int, float] = {
    1: 1.12, 2: 1.12, 3: 1.08,
    4: 0.95, 5: 0.92, 6: 0.88,
    7: 0.88, 8: 0.90, 9: 0.95,
    10: 1.02, 11: 1.08, 12: 1.12,
}

# GAS (NBP): much steeper winter premium reflecting UK space-heating demand.
# Q1 peak: up to 3-4× July demand in UK (National Grid gas consumption data).
# Monthly spreads calibrated to NBP seasonal price structure 2016-2025.
# Annual arithmetic mean ≈ 0.99 — 12-month contracts are near-flat.
GAS_MONTH_SEASONAL_MULTIPLIER: dict[int, float] = {
    1: 1.22, 2: 1.17, 3: 1.06,
    4: 0.92, 5: 0.87, 6: 0.82,
    7: 0.80, 8: 0.82, 9: 0.90,
    10: 1.00, 11: 1.10, 12: 1.20,
}

# Aggregate winter/summer values — kept for backward-compat (callers and tests).
WINTER_MONTHS: frozenset[int] = frozenset({10, 11, 12, 1, 2, 3})
WINTER_MULTIPLIER: float = statistics.mean(
    v for m, v in MONTH_SEASONAL_MULTIPLIER.items() if m in WINTER_MONTHS
)
SUMMER_MULTIPLIER: float = statistics.mean(
    v for m, v in MONTH_SEASONAL_MULTIPLIER.items() if m not in WINTER_MONTHS
)

# Term risk premiums — base value for a 1-year contract.
# Scaled by sqrt(tenor_years) and by (risk_factor / DEFAULT_RISK_FACTOR).
BASE_TERM_PREMIUM: float = 0.06       # electricity (N2EX baseload)
GAS_BASE_TERM_PREMIUM: float = 0.05  # gas NBP (more liquid forward market → lower premium)
DEFAULT_RISK_FACTOR: float = 1.2

# EWMA half-life for spot expectation smoothing (days).
EWMA_HALF_LIFE_DAYS: int = 30


def _ewma(daily_means: list[float], half_life: int) -> float:
    """Exponentially weighted moving average of a chronologically ordered series.

    daily_means[-1] is most recent; receives highest weight.
    alpha = 1 − 0.5^(1/half_life) so the most-recent half_life observations
    account for half the total weight.
    """
    alpha = 1.0 - 0.5 ** (1.0 / half_life)
    numerator = 0.0
    denominator = 0.0
    for i, price in enumerate(reversed(daily_means)):
        weight = (1.0 - alpha) ** i
        numerator += weight * price
        denominator += weight
    return numerator / denominator


def _seasonal_shape(start_month: int, contract_length_months: int, fuel: str = "electricity") -> float:
    """Arithmetic mean of monthly multipliers over the delivery period.

    fuel: "electricity" uses N2EX baseload table; "gas" uses NBP heating-demand table.
    """
    table = GAS_MONTH_SEASONAL_MULTIPLIER if fuel == "gas" else MONTH_SEASONAL_MULTIPLIER
    return statistics.mean(
        table[(start_month - 1 + offset) % 12 + 1]
        for offset in range(max(1, contract_length_months))
    )


def generate_forward_price(
    acquisition_date: str,
    system_price_records: list[dict],
    contract_length_months: int = 12,
    lookback_days: int = 90,
    risk_factor: float = 1.2,
    lookback_daily_mean_temps_c: list[float] | None = None,
    fuel: str = "electricity",
) -> float:
    """Synthetic forward price using a term-structure model.

    acquisition_date: ISO date string — contract start / delivery date.
        Only records strictly before this date are used (PIT safe).
    system_price_records: half-hourly Elexon SSP records (electricity) or
        daily NBP records (gas): {'settlementDate': 'YYYY-MM-DD', 'systemSellPrice': float}.
    contract_length_months: delivery window (default 12).
    lookback_days: backward window for spot_ewma (default 90).
    risk_factor: scales the term premium (1.2 → calibrated base premium for fuel type).
        Monotone: higher risk_factor → higher forward price.
    lookback_daily_mean_temps_c: optional list of lookback-window daily mean
        temperatures for the Phase 4c-3 cold-spell weather premium (electricity only).
    fuel: "electricity" (default) or "gas". Selects seasonal multiplier table and
        base term premium (electricity: 6%, gas: 5%).

    Returns: forward price in £/MWh.
    Raises ValueError if no records fall within the lookback window.
    """
    start_date = date.fromisoformat(acquisition_date)
    end_lookback = start_date - timedelta(days=1)
    start_lookback = start_date - timedelta(days=lookback_days)

    filtered = [
        r for r in system_price_records
        if start_lookback <= date.fromisoformat(r["settlementDate"]) <= end_lookback
    ]

    if not filtered:
        raise ValueError(
            f"No price records found in the lookback window "
            f"[{start_lookback}, {end_lookback}] for acquisition date {acquisition_date}."
        )

    # Aggregate to daily means — avoids loading normal intraday peak/off-peak
    # spread into the price estimate (intraday spread ≠ forward uncertainty).
    daily_buckets: dict[str, list[float]] = {}
    for r in filtered:
        daily_buckets.setdefault(r["settlementDate"], []).append(r["systemSellPrice"])
    daily_means = [
        statistics.mean(prices)
        for _date_str, prices in sorted(daily_buckets.items())
    ]

    # 1. EWMA spot estimate (chronological; most-recent weighted highest)
    effective_half_life = min(EWMA_HALF_LIFE_DAYS, len(daily_means))
    spot_ewma = _ewma(daily_means, effective_half_life)

    # 2. Seasonal shape over delivery period (fuel-specific table)
    seasonal = _seasonal_shape(start_date.month, contract_length_months, fuel)

    # 3. Term risk premium: grows with sqrt(tenor) and scales with risk_factor.
    # Gas has a slightly lower base premium (more liquid forward market).
    tenor_years = contract_length_months / 12.0
    base_premium = GAS_BASE_TERM_PREMIUM if fuel == "gas" else BASE_TERM_PREMIUM
    term_premium = base_premium * (tenor_years ** 0.5) * (risk_factor / DEFAULT_RISK_FACTOR)

    forward_price = spot_ewma * seasonal * (1.0 + term_premium)

    # Phase 4c-3: optional cold-spell weather premium (electricity only)
    if lookback_daily_mean_temps_c is not None and fuel == "electricity":
        forward_price *= weather_sensitivity_multiplier(lookback_daily_mean_temps_c)

    return forward_price
