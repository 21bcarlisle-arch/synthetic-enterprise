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

Phase 17a adds a portfolio learning premium: the company observes its own
completed electricity term margin rates (actual margin / revenue) and adjusts
future tariffs upward when recent margins are below a target rate. This is a
slower-acting, portfolio-wide signal complementing Phase 16c's per-customer
emergency surcharge. Expected impact: sustained under-pricing in 2021-22
triggers a portfolio-wide premium lift that carries into 2023-24.
"""

import statistics
from datetime import date, timedelta

COMPANY_LOOKBACK_DAYS = 120
# Phase 45c: recalibrated from 15% to 8% (electricity) and 20% to 10% (gas).
# UK I&C competitive market: brokers price at 5-8% above NAP/NBP for electricity;
# gas market more volatile but pass-through now handles gas directly at spot.
# Original 15%/20% created systematic C_IC1/C_IC2 overpricing (~33% net vs 3-8% benchmark).
COMPANY_RISK_PREMIUM_FRACTION = 0.08
GAS_RISK_PREMIUM_FRACTION = 0.10    # Phase 20a: gas higher basis risk; Phase 45c: 20%→10%
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

# Phase 17a: Portfolio learning premium — adjust tariff based on recent margin outcomes
PORTFOLIO_TARGET_MARGIN_RATE = 0.08   # company targets 8% net margin on electricity revenue
PORTFOLIO_PREMIUM_LOOKBACK = 4        # look at last N completed electricity terms (portfolio-wide)
PORTFOLIO_PREMIUM_HALF_LIFE = 0.50    # fraction of gap to close per pricing cycle (50%)
PORTFOLIO_PREMIUM_MIN = -0.05         # max tariff reduction if over-earning (5%)
PORTFOLIO_PREMIUM_MAX = 0.15          # max tariff surcharge if under-earning (15%)

# Phase 18a: Regime detection — compare short-term price trend vs longer baseline.
# If prices are in an upswing (short mean > long mean by THRESHOLD), apply a crisis premium
# to the forward estimate. If in a downswing, apply a discount.
# Complementary to Phase 14c (adaptive lookback handles volatility; this handles trend direction).
REGIME_DETECT_ENABLED = True
REGIME_SHORT_WINDOW = 60     # days for the "recent" regime mean
REGIME_LONG_WINDOW = 180     # days for the "baseline" regime mean
REGIME_UPWARD_THRESHOLD = 1.10   # short/long ratio above this → upward regime
REGIME_DOWNWARD_THRESHOLD = 0.90 # short/long ratio below this → downward regime
REGIME_PREMIUM_FACTOR = 0.50     # fraction of excess ratio to apply as premium
REGIME_PREMIUM_MAX = 0.15        # cap upward premium at +15%
REGIME_PREMIUM_MIN = -0.05       # cap downward discount at -5%
REGIME_MIN_RECORDS = 20          # minimum records in each window to compute ratio


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


def _compute_regime_premium(
    delivery_date: str,
    price_records: list[dict],
) -> float:
    """Compute a regime premium from the short-term vs long-term price trend.

    If spot prices have been trending upward (short mean > long mean × THRESHOLD),
    the company charges a premium above its baseline estimate to compensate for
    the likelihood of continued price rises. Downward trend yields a small discount.

    Returns a premium fraction in [REGIME_PREMIUM_MIN, REGIME_PREMIUM_MAX].
    Returns 0.0 if there are insufficient records in either window.
    """
    if not REGIME_DETECT_ENABLED:
        return 0.0
    end_date = date.fromisoformat(delivery_date) - timedelta(days=1)
    short_start = end_date - timedelta(days=REGIME_SHORT_WINDOW - 1)
    long_start = end_date - timedelta(days=REGIME_LONG_WINDOW - 1)

    short_means = _daily_means_for_window(price_records, short_start, end_date)
    long_means = _daily_means_for_window(price_records, long_start, end_date)

    if len(short_means) < REGIME_MIN_RECORDS or len(long_means) < REGIME_MIN_RECORDS:
        return 0.0
    if (long_mean := statistics.mean(long_means)) <= 0:
        return 0.0

    ratio = statistics.mean(short_means) / long_mean

    if ratio >= REGIME_UPWARD_THRESHOLD:
        excess = ratio - REGIME_UPWARD_THRESHOLD
        return min(REGIME_PREMIUM_MAX, excess * REGIME_PREMIUM_FACTOR)
    if ratio <= REGIME_DOWNWARD_THRESHOLD:
        deficit = REGIME_DOWNWARD_THRESHOLD - ratio
        return max(REGIME_PREMIUM_MIN, -deficit * REGIME_PREMIUM_FACTOR)
    return 0.0


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
        risk_premium: float | None = None,
        seasonal: bool = SEASONAL_UPLIFT_ENABLED,
        adaptive_lookback: bool = ADAPTIVE_LOOKBACK_ENABLED,
        regime_detect: bool = REGIME_DETECT_ENABLED,
    ) -> float:
        """Estimate forward price from observable spot history.

        fuel: 'electricity' or 'gas' (seasonal adjustment applies to both).
        delivery_date: ISO date string for the contract start (Point-in-Time:
            only records BEFORE this date are used).
        price_records: list of {'settlementDate': str, 'systemSellPrice': float}.
        lookback_days: base days back from delivery_date to look (default 120).
            Overridden by adaptive_lookback when enabled.
        risk_premium: fraction above rolling mean to charge. Defaults to
            GAS_RISK_PREMIUM_FRACTION (20%) for gas, COMPANY_RISK_PREMIUM_FRACTION
            (15%) for electricity (Phase 20a: gas basis risk is higher).
        seasonal: apply winter/summer adjustment (default True).
            Pass False to use the flat-mean-plus-premium formula.
        adaptive_lookback: adjust lookback window based on recent vs baseline
            volatility (Phase 14c). Pass False for deterministic tests.
        regime_detect: apply regime premium when short-term price trend diverges
            from long-term baseline (Phase 18a). Pass False for deterministic tests.

        Returns: forward price estimate in £/MWh.

        Raises ValueError if no records found in lookback window and no
        fallback window is available (caller should handle bootstrap cases).
        """
        if risk_premium is None:
            risk_premium = GAS_RISK_PREMIUM_FRACTION if fuel == "gas" else COMPANY_RISK_PREMIUM_FRACTION
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

        # Phase 18a: apply regime premium before final risk premium
        if regime_detect:
            regime_prem = _compute_regime_premium(delivery_date, price_records)
            base *= (1.0 + regime_prem)

        return base * (1.0 + risk_premium)


def compute_portfolio_premium(
    recent_margin_rates: list[float],
    target: float = PORTFOLIO_TARGET_MARGIN_RATE,
    half_life: float = PORTFOLIO_PREMIUM_HALF_LIFE,
    premium_min: float = PORTFOLIO_PREMIUM_MIN,
    premium_max: float = PORTFOLIO_PREMIUM_MAX,
) -> float:
    """Compute a tariff adjustment premium from recent portfolio-wide electricity margin rates.

    recent_margin_rates: list of (actual_margin / revenue) floats from completed electricity
        terms across all customers. The company observes these from its own P&L — no SIM
        internals required.

    Returns a premium fraction to multiply onto unit_rate: positive = surcharge,
    negative = discount, clamped to [premium_min, premium_max].

    If no history is available (first N terms), returns 0.0 (no adjustment).
    """
    if not recent_margin_rates:
        return 0.0
    mean_margin = statistics.mean(recent_margin_rates)
    shortfall = target - mean_margin   # positive when below target → raise rates
    raw_premium = shortfall * half_life
    return max(premium_min, min(premium_max, raw_premium))
