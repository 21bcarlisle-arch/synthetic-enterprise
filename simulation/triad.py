"""Phase 27d: Triad risk tracking for I&C electricity customers.

TNUoS (Transmission Network Use of System) charges for large I&C sites are
determined by the customer's consumption during the 3 highest national demand
settlement periods ('Triads') each winter. Triads must be at least 10 days
apart and occur in the November-February window.

A Triad charge is applied by the supplier after the winter ends, based on
the customer's actual consumption at those 3 periods × the applicable
TNUoS Triad tariff (£/kW/year). For large I&C customers, this can be
£50-£100k+ per year, making Triad avoidance significant (demand management,
battery storage, shift to off-peak operation during likely Triad windows).

This module:
  - Identifies candidate Triad periods from national system prices (high SSP
    is a proxy for high demand — not perfect but observable without NESO data)
  - Computes the customer's consumption at those periods
  - Estimates TNUoS Triad exposure (in kW demand and £)

Note: actual UK Triad periods are published by National Grid ESO after the
winter. Suppliers and customers try to predict them from demand/price signals.
Using SSP as a proxy for high-demand periods is the observable-data approach
a real supplier would take.
"""

from datetime import date

# TNUoS Triad tariff (£/kW/year) for HV-connected demand (large I&C, Zone 14 London).
# Source: National Grid ESO TNUoS tariff statements.
# Using a representative Zone 14 (London) HV connected figure.
_TNUOS_TRIAD_TARIFF_BY_YEAR: dict[int, float] = {
    2016: 46.23,
    2017: 47.80,
    2018: 50.14,
    2019: 52.36,
    2020: 55.18,
    2021: 56.41,
    2022: 58.93,
    2023: 61.47,
    2024: 63.82,
}

# Triad window: November through February (months 11, 12, 1, 2)
_TRIAD_WINDOW_MONTHS = {11, 12, 1, 2}
# Minimum separation between Triad periods (days)
_MIN_TRIAD_SEPARATION_DAYS = 10
# Number of Triad settlement periods per winter
_N_TRIADS = 3


def _triad_year(date_str: str) -> int:
    """Return the charging year (winter start year) for a settlement date.

    The Triad year runs Nov-Feb. Nov/Dec belongs to the year that Nov falls in;
    Jan/Feb belongs to the previous year. E.g. Jan 2022 is part of winter 2021-22
    → triad_year = 2021.
    """
    d = date.fromisoformat(date_str)
    return d.year if d.month >= 11 else d.year - 1


def get_tnuos_tariff(triad_year: int) -> float:
    """TNUoS Triad tariff (£/kW/year) for the given winter start year."""
    if triad_year in _TNUOS_TRIAD_TARIFF_BY_YEAR:
        return _TNUOS_TRIAD_TARIFF_BY_YEAR[triad_year]
    if triad_year < min(_TNUOS_TRIAD_TARIFF_BY_YEAR):
        return _TNUOS_TRIAD_TARIFF_BY_YEAR[min(_TNUOS_TRIAD_TARIFF_BY_YEAR)]
    return _TNUOS_TRIAD_TARIFF_BY_YEAR[max(_TNUOS_TRIAD_TARIFF_BY_YEAR)]


def identify_triad_candidates(
    price_records: list[dict],
    triad_year: int,
) -> list[dict]:
    """Identify the 3 Triad settlement periods for a given winter.

    Uses system sell price (SSP) as a proxy for high national demand.
    The 3 highest-SSP periods in the Triad window (Nov-Feb), each at least
    10 days apart, are the Triad candidates.

    Returns list of up to 3 dicts: {settlementDate, settlementPeriod, systemSellPrice}
    sorted by date (chronological).
    """
    # Filter to Triad window for this winter
    nov_start = date(triad_year, 11, 1).isoformat()
    feb_end = date(triad_year + 1, 2, 28).isoformat()

    window_records = [
        r for r in price_records
        if nov_start <= r["settlementDate"] <= feb_end
        and date.fromisoformat(r["settlementDate"]).month in _TRIAD_WINDOW_MONTHS
    ]

    if not window_records:
        return []

    # Sort by SSP descending to find highest demand periods
    sorted_by_price = sorted(window_records, key=lambda r: r["systemSellPrice"], reverse=True)

    triads = []
    for candidate in sorted_by_price:
        if len(triads) >= _N_TRIADS:
            break
        cand_date = date.fromisoformat(candidate["settlementDate"])
        # Check minimum separation from already-selected triads
        too_close = any(
            abs((cand_date - date.fromisoformat(t["settlementDate"])).days) < _MIN_TRIAD_SEPARATION_DAYS
            for t in triads
        )
        if not too_close:
            triads.append(candidate)

    return sorted(triads, key=lambda r: (r["settlementDate"], r["settlementPeriod"]))


def compute_triad_exposure(
    customer_id: str,
    triad_periods: list[dict],
    settlement_records: list[dict],
    triad_year: int,
) -> dict:
    """Compute a customer's TNUoS Triad exposure for one winter.

    Matches customer's consumption at each Triad settlement period and
    computes estimated TNUoS charge based on average demand (kW).

    Returns:
      customer_id, triad_year, triad_periods (list of date/period/ssp/consumption_kw),
      avg_triad_kw (mean of 3 Triad demands in kW),
      estimated_tnuos_gbp (avg_triad_kw × tariff)
    """
    # Build consumption lookup: (date, period) → kWh
    consumption_lookup: dict[tuple[str, int], float] = {}
    for rec in settlement_records:
        if rec.get("customer_id") == customer_id:
            consumption_lookup[(rec["settlement_date"], rec["settlement_period"])] = rec["consumption_kwh"]

    tnuos_tariff = get_tnuos_tariff(triad_year)

    period_details = []
    for t in triad_periods:
        kwh = consumption_lookup.get((t["settlementDate"], t["settlementPeriod"]), 0.0)
        # Convert kWh in 30-min period to kW average demand
        kw = kwh * 2.0  # 30-min period → ×2 to get kW
        period_details.append({
            "date": t["settlementDate"],
            "period": t["settlementPeriod"],
            "system_ssp": t["systemSellPrice"],
            "consumption_kwh": round(kwh, 3),
            "demand_kw": round(kw, 1),
        })

    avg_triad_kw = (
        sum(p["demand_kw"] for p in period_details) / len(period_details)
        if period_details else 0.0
    )
    estimated_tnuos_gbp = avg_triad_kw * tnuos_tariff

    return {
        "customer_id": customer_id,
        "triad_year": triad_year,
        "triad_periods": period_details,
        "avg_triad_kw": round(avg_triad_kw, 1),
        "tnuos_tariff_gbp_per_kw": tnuos_tariff,
        "estimated_tnuos_gbp": round(estimated_tnuos_gbp, 2),
    }
