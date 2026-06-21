"""Company pricing layer — observable-data forward price model.

The company cannot see the SIM's forward_curve.py internals (parameters,
seasonal multipliers, risk_factor). It builds its own forward price estimate
from the same observable market data a real UK supplier could access:
published spot electricity prices (Elexon SSP) and gas prices (NBP/TTF proxy).

Base algorithm: rolling mean of daily means over the lookback window, plus a
fixed risk premium.

Phase 13d adds a seasonal adjustment for electricity (observable from
historical Elexon spot price patterns — any pricing team would know this):
- Winter delivery (Oct-Mar): +8% above the rolling mean (higher demand)
- Summer delivery (Apr-Sep): -4% below the rolling mean (lower demand)

Phase 13e adds gas-specific seasonal parameters (more pronounced than electricity).

Phase 14c adds an adaptive lookback window: when recent market volatility
(last 30 days) is high relative to the prior 90-day baseline, the lookback
window is shortened so the rolling mean reflects current-regime prices rather
than diluting them with stale pre-crisis data. This reduces the systematic
under-pricing error during the 2021-22 price spike (where a 120-day mean
included several months of pre-spike calm prices that anchored estimates too low).
"""

import statistics
from datetime import date, timedelta

COMPANY_LOOKBACK_DAYS = 120
COMPANY_RISK_PREMIUM_FRACTION = 0.15
MIN_RECORDS_FOR_ESTIMATE = 30

SEASONAL_UPLIFT_ENABLED = True
WINTER_MONTHS = frozenset({10, 11, 12, 1, 2, 3})

# Electricity seasonal parameters (Phase 13d)
WINTER_SEASONAL_UPLIFT = 0.08
SUMMER_SEASONAL_DISCOUNT = 0.04

# Gas seasonal parameters (Phase 13e): more pronounced than electricity
# UK NBP spot prices are structurally higher in winter (heating demand)
# and lower in summer (injection season). Real supplier pricing teams
# would apply a seasonal shape to NBP-based contract pricing.
GAS_WINTER_SEASONAL_UPLIFT = 0.15
GAS_SUMMER_SEASONAL_DISCOUNT = 0.08

# Adaptive lookback parameters (Phase 14c)
# Compare recent 30-day price std vs prior 90-day baseline std.
# High vol_ratio (recent more volatile) → shorten lookback to react to new regime.
# Low vol_ratio (recent calmer) → extend lookback up to max for smoother estimate.
ADAPTIVE_LOOKBACK_ENABLED = True
ADAPTIVE_VOL_RECENT_DAYS = 30       # recent window for volatility comparison
ADAPTIVE_VOL_BASELINE_DAYS = 90     # baseline window (ends RECENT_DAYS before delivery)
ADAPTIVE_LOOKBACK_MIN = 30          # floor (days)
ADAPTIVE_LOOKBACK_MAX = 180         # ceiling (days)
ADAPTIVE_VOL_MIN_BASELINE_STD = 0.5 # £/MWh; below this, vol ratio is undefined — keep base


def _daily_means_for_window(
    price_records: list[dict],
    window_start: date,
    window_end: date,
) -> list[float]:
    daily: dict[str, list[float]] = {}
    for r in price_records:
        d = date.fromisoformat(r["settlementDate"])
        if window_start <= d <= window_end:
            daily.setdefault(r["settlementDate"], []).append(r["systemSellPrice"])
    return [statistics.mean(v) for v in daily.values()]


def _compute_adaptive_lookback(
    delivery_date: str,
    price_records: list[dict],
    base_lookback: int,
) -> int:
    """Return an adaptive lookback window length based on recent vs baseline volatility.

    Compares the price std over the last ADAPTIVE_VOL_RECENT_DAYS with the std
    over the prior ADAPTIVE_VOL_BASELINE_DAYS. If recent vol is elevated (ratio > 1),
    shorten the lookback so the mean tracks the new market regime; if recent vol is
    subdued (ratio < 1), extend toward ADAPTIVE_LOOKBACK_MAX for a smoother estimate.

    Falls back to base_lookback when there are insufficient records for either window
    or when the baseline std is near zero (stable pre-data-history period).
    """
    end_date = date.fromisoformat(delivery_date) - timedelta(days=1)
    recent_start = end_date - timedelta(days=ADAPTIVE_VOL_RECENT_DAYS - 1)
    baseline_start = recent_start - timedelta(days=ADAPTIVE_VOL_BASELINE_DAYS)
    baseline_end = recent_start - timedelta(days=1)

    recent_means = _daily_means_for_window(price_records, recent_start, end_date)
    baseline_means = _daily_means_for_window(price_records, baseline_start, baseline_end)

    if len(recent_means) < 5 or len(baseline_means) < 20:
        return base_lookback

    recent_std = statistics.stdev(recent_means) if len(recent_means) > 1 else 0.0
    baseline_std = statistics.stdev(baseline_means) if len(baseline_means) > 1 else 0.0

    if baseline_std < ADAPTIVE_VOL_MIN_BASELINE_STD:
        return base_lookback

    vol_ratio = recent_std / baseline_std
    adaptive = int(base_lookback / max(0.1, vol_ratio))
    return max(ADAPTIVE_LOOKBACK_MIN, min(ADAPTIVE_LOOKBACK_MAX, adaptive))


class CompanyTariffEngine:
    """Company-observable forward price estimator.

    Reads only publicly available spot price records (same format as
    sim.system_prices_history: {'settlementDate': 'YYYY-MM-DD',
    'systemSellPrice': float}) — never imports sim/forward_curve.py.
    """

    def get_forward_price(
        self,
        fuel: str,
        delivery_date: str,
        price_records: list[dict],
        lookback_days: int = COMPANY_LOOKBACK_DAYS,
        risk_premium: float = COMPANY_RISK_PREMIUM_FRACTION,
        seasonal: bool = SEASONAL_UPLIFT_ENABLED,
        adaptive_lookback: bool = ADAPTIVE_LOOKBACK_ENABLED,
    ) -> float:
        """Estimate forward price from observable spot history.

        fuel: 'electricity' or 'gas' (seasonal adjustment applies to both).
        delivery_date: ISO date string for the contract start (Point-in-Time:
            only records BEFORE this date are used).
        price_records: list of {'settlementDate': str, 'systemSellPrice': float}.
        lookback_days: base days back from delivery_date to look (default 120).
            Overridden by adaptive_lookback when enabled.
        risk_premium: fraction above rolling mean to charge (default 15%).
        seasonal: apply winter/summer adjustment (default True).
            Pass False to use the flat-mean-plus-premium formula.
        adaptive_lookback: adjust lookback window based on recent vs baseline
            volatility (Phase 14c). Pass False for deterministic tests.

        Returns: forward price estimate in £/MWh.

        Raises ValueError if no records found in lookback window and no
        fallback window is available (caller should handle bootstrap cases).
        """
        if adaptive_lookback:
            lookback_days = _compute_adaptive_lookback(delivery_date, price_records, lookback_days)

        start_date = date.fromisoformat(delivery_date)
        end_lookback = start_date - timedelta(days=1)
        start_lookback = start_date - timedelta(days=lookback_days)

        filtered = [
            r for r in price_records
            if start_lookback <= date.fromisoformat(r["settlementDate"]) <= end_lookback
        ]

        if len(filtered) < MIN_RECORDS_FOR_ESTIMATE:
            raise ValueError(
                f"Insufficient price records for company estimate at {delivery_date}: "
                f"found {len(filtered)}, need at least {MIN_RECORDS_FOR_ESTIMATE}"
            )

        daily: dict[str, list[float]] = {}
        for r in filtered:
            daily.setdefault(r["settlementDate"], []).append(r["systemSellPrice"])
        daily_means = [statistics.mean(v) for v in daily.values()]

        base = statistics.mean(daily_means)

        if seasonal:
            delivery_month = start_date.month
            is_winter = delivery_month in WINTER_MONTHS
            if fuel == "electricity":
                base *= (1.0 + WINTER_SEASONAL_UPLIFT) if is_winter else (1.0 - SUMMER_SEASONAL_DISCOUNT)
            elif fuel == "gas":
                base *= (1.0 + GAS_WINTER_SEASONAL_UPLIFT) if is_winter else (1.0 - GAS_SUMMER_SEASONAL_DISCOUNT)

        return base * (1.0 + risk_premium)
