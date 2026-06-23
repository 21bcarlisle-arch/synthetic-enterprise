"""VaR-constrained hedge decision — Phase 43b.

The company's trading desk decides how much to hedge at each term signing.
Decision is forward-looking (current market conditions) rather than backward-looking
(past performance outcomes, which was the Phase 22b evolve_hedge_fraction approach).

All inputs must be company-observable:
- price_records: published spot market data (Elexon SSP — public)
- eac_kwh: company demand estimate from own meter reads
- fwd_price: company forward price from its own tariff engine
- unit_rate: the tariff the company proposes to charge
"""

from __future__ import annotations

import math
from company.risk.hedge_policy import COMPANY_MIN_HEDGE_FLOOR

# VaR parameters
VAR_CONFIDENCE = 0.95          # 95th percentile
VAR_Z_95 = 1.6449              # norm.ppf(0.95) — avoid scipy dependency
VAR_REVENUE_LIMIT = 0.15       # max acceptable VaR as % of term revenue

# Bid-ask spread parameters calibrated to UK N2EX OTC market microstructure
# Source: industry knowledge — N2EX 1yr contracts typically 0.5-1.5% spread
BID_ASK_BASE_PCT = 0.005       # 0.5% of forward price for short-dated contracts
BID_ASK_TENOR_PCT = 0.002      # additional 0.2% per year of tenor
MAX_BID_ASK_PCT = 0.015        # cap at 1.5% (very long-dated)

# Volatility estimation
VOL_LOOKBACK_DAYS = 90         # rolling window for realized vol estimate
MIN_VOL_ANNUAL = 0.10          # floor: at least 10% annualized vol (prevents 0-div)
MAX_VOL_ANNUAL = 2.50          # cap: even during crisis, VaR constraint should be finite


def estimate_price_volatility(price_records: list[dict]) -> float:
    """Estimate annualized realized volatility from observable spot price history.

    Uses the most recent VOL_LOOKBACK_DAYS of daily settlement prices.
    Computes 90-day EWMA of squared log returns, annualizes.

    price_records: list of {settlementDate: YYYY-MM-DD, systemSellPrice: float}

    Returns annualized vol in decimal (e.g. 0.40 = 40% vol).
    """
    # Extract daily closing prices (last period per day, or mean)
    daily: dict[str, list[float]] = {}
    for r in price_records:
        d = r.get("settlementDate", "")
        p = r.get("systemSellPrice", 0.0)
        if d and p and p > 0:
            daily.setdefault(d, []).append(p)

    if len(daily) < 5:
        return MIN_VOL_ANNUAL

    # Take daily mean price, sorted
    sorted_days = sorted(daily.keys())
    prices = [sum(daily[d]) / len(daily[d]) for d in sorted_days]

    # Use only last VOL_LOOKBACK_DAYS
    prices = prices[-VOL_LOOKBACK_DAYS:]
    if len(prices) < 5:
        return MIN_VOL_ANNUAL

    # Daily log returns
    log_returns = [
        math.log(prices[i] / prices[i - 1])
        for i in range(1, len(prices))
        if prices[i] > 0 and prices[i - 1] > 0
    ]
    if not log_returns:
        return MIN_VOL_ANNUAL

    # EWMA variance (lambda=0.94, decay half-life ~12 days)
    lam = 0.94
    var = sum(r * r for r in log_returns) / len(log_returns)  # seed with simple variance
    for r in log_returns:
        var = lam * var + (1 - lam) * r * r

    # Annualize: daily vol × sqrt(252 trading days)
    daily_vol = var ** 0.5
    annual_vol = daily_vol * (252 ** 0.5)
    return float(max(MIN_VOL_ANNUAL, min(MAX_VOL_ANNUAL, annual_vol)))


def compute_bid_ask_cost(forward_price_gbp_per_mwh: float, tenor_years: float) -> float:
    """Estimate the bid-ask cost of executing a forward hedge (£/MWh).

    The company buys at ask (not mid) when hedging supply obligations.
    Calibrated to UK N2EX OTC market microstructure: ~0.5-1.5% of forward price.
    """
    spread_pct = min(MAX_BID_ASK_PCT, BID_ASK_BASE_PCT + BID_ASK_TENOR_PCT * tenor_years)
    return forward_price_gbp_per_mwh * spread_pct


def decide_hedge_fraction(
    eac_kwh: float,
    fwd_price_gbp_per_mwh: float,
    unit_rate_gbp_per_mwh: float,
    price_records: list[dict],
    term_days: int,
) -> float:
    """Decide hedge fraction subject to 95% VaR ≤ VAR_REVENUE_LIMIT × term revenue.

    The VaR model: the unhedged position's 95th percentile loss over the term
    must not exceed VAR_REVENUE_LIMIT (15%) of expected term revenue.

    Derivation:
      VaR = fwd_price × unhedged_mwh_term × vol_annual × sqrt(term_years) × z_95
      unhedged_mwh_term = eac_mwh × (1 - hf) × (term_days / 365.25)
      max_var = VAR_REVENUE_LIMIT × unit_rate × eac_mwh × (term_days / 365.25)
      Solve for hf: hf = 1 - max_var / (fwd_price × eac_mwh_term × vol_term × z_95)

    Returns hf in [COMPANY_MIN_HEDGE_FLOOR, 1.0].
    """
    if eac_kwh <= 0 or fwd_price_gbp_per_mwh <= 0 or term_days <= 0:
        return COMPANY_MIN_HEDGE_FLOOR

    vol_annual = estimate_price_volatility(price_records)
    vol_term = vol_annual * ((term_days / 365.25) ** 0.5)

    eac_mwh = eac_kwh / 1000.0
    term_fraction = term_days / 365.25
    eac_mwh_term = eac_mwh * term_fraction

    # Maximum acceptable VaR in £
    term_revenue_estimate = unit_rate_gbp_per_mwh * eac_mwh_term
    max_var_gbp = VAR_REVENUE_LIMIT * term_revenue_estimate

    # Maximum unhedged fraction that keeps VaR ≤ max_var
    denominator = fwd_price_gbp_per_mwh * eac_mwh_term * vol_term * VAR_Z_95
    if denominator <= 0:
        return COMPANY_MIN_HEDGE_FLOOR

    max_unhedged_fraction = max_var_gbp / denominator
    hf = 1.0 - max_unhedged_fraction

    return float(max(COMPANY_MIN_HEDGE_FLOOR, min(1.0, hf)))
