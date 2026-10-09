"""Forward price model for fixed-rate tariff acquisition.

Phase MS: seasonal multipliers loaded from sim/data/seasonal_calibration.json,
derived empirically from real market data 2016-2024:
  - Electricity: Elexon BMRS half-hourly SSP (per-year monthly/annual ratio)
  - Gas: FRED PNGASEUUSDM TTF proxy in GBP/MWh (same methodology)
Includes 2021-2022 energy crisis — real events, not excluded.
Falls back to hand-calibrated constants if calibration file is missing.

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

import bisect
import json
import statistics
from datetime import date, timedelta
from pathlib import Path

from sim.weather_price_sensitivity import weather_sensitivity_multiplier

#: Date indexes over price-record lists, keyed by the list's id. Each entry holds the list itself
#: (so an id cannot be reused while its entry lives), the length it was built at, the ISO dates in
#: sorted order and the record positions in that order. Bounded: a run holds two lists (SSP, NBP).
_WINDOW_INDEX: dict[int, tuple] = {}
_WINDOW_INDEX_MAX = 8


def records_in_window(records: list[dict], first: date, last: date) -> list[dict]:
    """The records whose `settlementDate` falls in [first, last], in the list's own order.

    WHY AN INDEX (2026-10-09, the director's "index once"). `generate_forward_price` and
    `risk_engine.calculate_sigma_recent` each parsed every date in ten years of half-hourly prices
    on every call -- per account, per term -- to keep a 90- or 365-day window: ~16% of a run's wall,
    measured on a 40-founder run (258 s -> 218 s with this index, the extracted book identical).
    The answer is unchanged by construction: the same records, in the same order, are returned.

    The index is rebuilt whenever the list's length changes, and it is not used at all for a list
    whose dates are not all plain `YYYY-MM-DD` -- string order equals date order only for that
    form, so any other form takes the original parse-every-date scan.
    """
    entry = _WINDOW_INDEX.get(id(records))
    if entry is None or entry[0] is not records or entry[1] != len(records):
        dates = [r["settlementDate"] for r in records]
        if all(isinstance(d, str) and len(d) == 10 and d[4] == "-" and d[7] == "-" for d in dates):
            order = sorted(range(len(records)), key=dates.__getitem__)
            entry = (records, len(records), [dates[i] for i in order], order)
        else:
            entry = (records, len(records), None, None)
        if len(_WINDOW_INDEX) >= _WINDOW_INDEX_MAX:
            _WINDOW_INDEX.pop(next(iter(_WINDOW_INDEX)))
        _WINDOW_INDEX[id(records)] = entry
    _, _, sorted_dates, order = entry
    if sorted_dates is None:
        return [r for r in records if first <= date.fromisoformat(r["settlementDate"]) <= last]
    lo = bisect.bisect_left(sorted_dates, first.isoformat())
    hi = bisect.bisect_right(sorted_dates, last.isoformat())
    return [records[i] for i in sorted(order[lo:hi])]

_CALIBRATION_PATH = Path(__file__).parent / 'data' / 'seasonal_calibration.json'


def _load_calibration():
    try:
        with open(_CALIBRATION_PATH) as _f:
            _cal = json.load(_f)
        _elec = {int(k): float(v) for k, v in _cal['electricity_n2ex']['multipliers'].items()}
        _gas = {int(k): float(v) for k, v in _cal['gas_nbp']['multipliers'].items()}
        if len(_elec) == 12 and len(_gas) == 12:
            return _elec, _gas
    except (FileNotFoundError, KeyError, ValueError):
        pass
    return None, None


# Monthly seasonal multipliers (1=Jan … 12=Dec).
# ELECTRICITY: calibrated to UK N2EX historical baseload seasonality 2016-2025.
#   Q4/Q1: peak demand, low renewable output → premium
#   Q2/Q3: mild demand, high solar/wind surplus → discount
# Annual arithmetic mean = 1.002 — 12-month contracts are near-flat on seasonal.
_ELEC_FALLBACK: dict[int, float] = {
    1: 1.12, 2: 1.12, 3: 1.08,
    4: 0.95, 5: 0.92, 6: 0.88,
    7: 0.88, 8: 0.90, 9: 0.95,
    10: 1.02, 11: 1.08, 12: 1.12,
}
_cal_elec, _cal_gas = _load_calibration()
MONTH_SEASONAL_MULTIPLIER: dict[int, float] = _cal_elec if _cal_elec is not None else _ELEC_FALLBACK

# GAS (NBP): much steeper winter premium reflecting UK space-heating demand.
# Q1 peak: up to 3-4× July demand in UK (National Grid gas consumption data).
# Monthly spreads calibrated to NBP seasonal price structure 2016-2025.
# Annual arithmetic mean ≈ 0.99 — 12-month contracts are near-flat.
_GAS_FALLBACK: dict[int, float] = {
    1: 1.22, 2: 1.17, 3: 1.06,
    4: 0.92, 5: 0.87, 6: 0.82,
    7: 0.80, 8: 0.82, 9: 0.90,
    10: 1.00, 11: 1.10, 12: 1.20,
}
GAS_MONTH_SEASONAL_MULTIPLIER: dict[int, float] = _cal_gas if _cal_gas is not None else _GAS_FALLBACK

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

    filtered = records_in_window(system_price_records, start_lookback, end_lookback)

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


def short_first_term_lookbacks(
    customers: list[dict], record_start: str, short_record_reason: str | None,
    fuel: str, lookback_days: int = 90,
) -> list[dict]:
    """The customers whose FIRST term starts less than `lookback_days` after the price record does,
    so `generate_forward_price` prices it off a window the record only partly fills.

    A short window is not an error -- the EWMA reads what is there, strictly before the start --
    but it must never be SILENT: for gas a record starting on the founders' own day left an empty
    window, and the fallback that "fixed" it priced the term off the 90 days AFTER its start
    (removed 2026-10-06, b8808f4ad). So a short window is allowed only on a record that declares
    why it cannot reach further back; on any other it raises, naming the customer. Each row it
    returns carries that reason, for the run to publish.
    """
    first = date.fromisoformat(record_start)
    shortfalls = []
    for customer in customers:
        start = date.fromisoformat(customer["acquisition_date"])
        missing = (first - (start - timedelta(days=lookback_days))).days
        if missing <= 0:
            continue
        if not short_record_reason:
            raise ValueError(
                f"{customer['customer_id']}'s first {fuel} term starts {customer['acquisition_date']}, "
                f"{lookback_days - missing} days into a {fuel} record that begins {record_start}: "
                f"its {lookback_days}-day lookback is {missing} days short and the record declares "
                f"no reason it cannot reach further back. Extend the record from its source, or "
                f"declare why it cannot be.")
        shortfalls.append({
            "customer_id": customer["customer_id"], "fuel": fuel,
            "acquisition_date": customer["acquisition_date"],
            "lookback_days_covered": max(0, lookback_days - missing),
            "reason": short_record_reason,
        })
    return shortfalls
