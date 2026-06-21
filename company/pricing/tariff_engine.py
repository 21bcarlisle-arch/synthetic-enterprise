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

The previous no-seasonal version systematically under-priced winter contracts
because the 120-day lookback for an autumn renewal captures summer spot prices,
which are structurally lower than winter spot prices. That lag contributed
to the company underpricing in crisis years when winter prices spiked.

The 2021-22 crisis is genuine market adversity (no seasonal model fixes that),
but the seasonal adjustment reduces the structural component of basis risk
that exists even in normal years.
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
    ) -> float:
        """Estimate forward price from observable spot history.

        fuel: 'electricity' or 'gas' (seasonal adjustment applies to
            electricity only; gas uses same formula without seasonal).
        delivery_date: ISO date string for the contract start (Point-in-Time:
            only records BEFORE this date are used).
        price_records: list of {'settlementDate': str, 'systemSellPrice': float}.
        lookback_days: how many days back from delivery_date to look (default 120).
        risk_premium: fraction above rolling mean to charge (default 15%).
        seasonal: apply winter/summer adjustment for electricity (default True).
            Pass False to use the flat-mean-plus-premium formula (useful in
            tests that check exact arithmetic).

        Returns: forward price estimate in £/MWh.

        Raises ValueError if no records found in lookback window and no
        fallback window is available (caller should handle bootstrap cases).
        """
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
