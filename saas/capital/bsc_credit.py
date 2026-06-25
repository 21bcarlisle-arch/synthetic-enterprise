"""BSC credit cover — working capital requirement model.

Elexon requires each BSC party (licensed supplier) to hold credit cover
against their settlement obligations. Cover is calculated as a multiple
of the rolling peak daily settlement charge.

Real formula (simplified): BSC credit = max(daily_charge over 28 days) × buffer.
For a small supplier, this is typically £5k-£700k depending on portfolio size and
spot prices. In 2021-2022, spiking SSP drove credit cover demands that exceeded
many small suppliers\'s available capital — a primary cause of the wave of failures.
"""

from __future__ import annotations

from collections import defaultdict

CREDIT_WINDOW_DAYS: int = 28
CREDIT_BUFFER_MULTIPLIER: float = 1.2


def compute_daily_wholesale_exposure(records: list[dict]) -> dict[str, float]:
    """Aggregate wholesale_cost_gbp by settlement date (electricity only).

    Returns {date_str: total_wholesale_cost_gbp} for all dates in records.
    Only electricity wholesale cost is credit-relevant under BSC settlement.
    """
    by_date: dict[str, float] = defaultdict(float)
    for r in records:
        date_str = r.get("settlement_date", "")[:10]
        if date_str and r.get("commodity", "electricity") == "electricity":
            by_date[date_str] += r.get("wholesale_cost_gbp", 0.0)
    return dict(by_date)


def compute_bsc_credit_requirement(
    daily_exposure: dict[str, float],
    window_days: int = CREDIT_WINDOW_DAYS,
    buffer: float = CREDIT_BUFFER_MULTIPLIER,
) -> float:
    """Compute BSC credit cover required: rolling-window peak × buffer.

    BSC methodology: maximum daily charge observed in a 28-day rolling
    window, scaled by a credit buffer. Conservative: uses the period peak
    rather than a day-specific rolling window.
    """
    if not daily_exposure:
        return 0.0
    peak = max(daily_exposure.values())
    return peak * buffer


def compute_bsc_credit_by_year(
    records: list[dict],
    window_days: int = CREDIT_WINDOW_DAYS,
    buffer: float = CREDIT_BUFFER_MULTIPLIER,
) -> dict[str, dict]:
    """Per-year BSC credit cover requirement derived from settlement records.

    Returns {year: {peak_daily_gbp, credit_cover_gbp, days_data}}.
    """
    by_date = compute_daily_wholesale_exposure(records)
    by_year: dict[str, list] = defaultdict(list)
    for date_str, cost in by_date.items():
        year = date_str[:4]
        by_year[year].append(cost)

    result = {}
    for year in sorted(by_year):
        daily_costs = by_year[year]
        peak = max(daily_costs) if daily_costs else 0.0
        result[year] = {
            "peak_daily_wholesale_gbp": round(peak, 2),
            "credit_cover_required_gbp": round(peak * buffer, 2),
            "days_with_data": len(daily_costs),
        }
    return result
