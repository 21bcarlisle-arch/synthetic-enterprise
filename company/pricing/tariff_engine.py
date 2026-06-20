"""Company pricing layer — observable-data forward price model.

The company cannot see the SIM's forward_curve.py internals (parameters,
seasonal multipliers, risk_factor). It builds its own forward price estimate
from the same observable market data a real UK supplier could access:
published spot electricity prices (Elexon SSP) and gas prices (NBP/TTF proxy).

Algorithm: rolling mean of daily means over the lookback window, plus a
fixed risk premium. No seasonal adjustment (company hasn't built that model
yet). This will systematically differ from the SIM's model — that difference
is basis risk, visible in the P&L for the first time after Phase 11a.

The 2021-22 crisis will show the company's estimate lagging badly as spot
prices spike beyond the lookback window — the same failure mode that killed
real suppliers under price caps.
"""

import statistics
from datetime import date, timedelta

COMPANY_LOOKBACK_DAYS = 120
COMPANY_RISK_PREMIUM_FRACTION = 0.15
MIN_RECORDS_FOR_ESTIMATE = 30


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
    ) -> float:
        """Estimate forward price from observable spot history.

        fuel: 'electricity' or 'gas' (determines logging only — same algo).
        delivery_date: ISO date string for the contract start (Point-in-Time:
            only records BEFORE this date are used).
        price_records: list of {'settlementDate': str, 'systemSellPrice': float}.
        lookback_days: how many days back from delivery_date to look (default 120).
        risk_premium: fraction above rolling mean to charge (default 15%).

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
        return base * (1.0 + risk_premium)
