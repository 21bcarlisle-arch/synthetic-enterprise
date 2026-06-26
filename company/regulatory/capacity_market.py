"""Capacity Market (CM) obligation management.

UK energy suppliers with more than 50MWh/year metered load have capacity
obligations under the Capacity Market (run by NESO). Obligations are
derived from the supplier's Total Final Demand (TFD) during the four
highest system demand settlement periods of the year (Triads for old
mechanism; replaced by Capacity Market charge in settlement).

The CM charge appears as a pass-through cost on customer bills.
Failure to meet delivery obligations results in penalty charges.

This module models the company's CM obligation, estimated charge,
and delivery status — all from company-observable settlement data.
"""

from __future__ import annotations

from dataclasses import dataclass


# CM obligation rate (GBP/kW per annum), varies by auction year
# Source: NESO Capacity Market auction results, clearing prices
_CM_OBLIGATION_RATE_BY_YEAR: dict[int, float] = {
    2016: 22.50,
    2017: 6.95,
    2018: 8.40,
    2019: 15.97,
    2020: 6.44,
    2021: 0.77,   # Covid demand reduction
    2022: 75.00,  # T-1 auction crisis price
    2023: 63.00,
    2024: 65.00,
    2025: 68.00,
}

# Assumed average de-rated supply margin %, used to size obligation
_DERATING_FACTOR = 0.92

# Penalty rate for missed delivery: 1/8 of the clearing price per MWh shortfall
_PENALTY_DIVISOR = 8


@dataclass
class CMObligationResult:
    year: int
    total_demand_mwh: float
    obligation_kw: float          # derived from TFD; kW of firm capacity required
    clearing_price_gbp_per_kw: float
    annual_charge_gbp: float
    delivery_status: str          # DELIVERED / PARTIAL / FAILED
    shortfall_kw: float
    penalty_gbp: float


def compute_cm_obligation(year: int, total_demand_mwh: float, firm_capacity_kw: float = None) -> CMObligationResult:
    """Compute Capacity Market obligation and charge for a given year.

    Args:
        year: delivery year
        total_demand_mwh: supplier's total annual metered demand
        firm_capacity_kw: contracted firm capacity (if any); None = zero (all pass-through)

    Returns CMObligationResult with annual charge and delivery status.
    """
    rate = _CM_OBLIGATION_RATE_BY_YEAR.get(year, _CM_OBLIGATION_RATE_BY_YEAR[2025])
    # Peak demand estimate: annual MWh / 8760h * peak-to-average factor 1.8
    peak_mw = (total_demand_mwh / 8760.0) * 1.8
    obligation_kw = round(peak_mw * 1000 * _DERATING_FACTOR, 1)

    firm = firm_capacity_kw or 0.0
    shortfall_kw = max(0.0, obligation_kw - firm)

    annual_charge = round(obligation_kw * rate, 2)
    penalty = round((shortfall_kw / 1000.0) * (rate / _PENALTY_DIVISOR), 2) if shortfall_kw > 0 else 0.0

    if shortfall_kw == 0:
        delivery_status = "DELIVERED"
    elif shortfall_kw < obligation_kw * 0.1:
        delivery_status = "PARTIAL"
    else:
        delivery_status = "FAILED"

    return CMObligationResult(
        year=year,
        total_demand_mwh=total_demand_mwh,
        obligation_kw=obligation_kw,
        clearing_price_gbp_per_kw=rate,
        annual_charge_gbp=annual_charge,
        delivery_status=delivery_status,
        shortfall_kw=round(shortfall_kw, 1),
        penalty_gbp=penalty,
    )


def cm_charge_per_mwh(year: int, total_demand_mwh: float) -> float:
    """Return the CM pass-through charge in GBP/MWh for a given year and demand."""
    result = compute_cm_obligation(year, total_demand_mwh)
    if total_demand_mwh <= 0:
        return 0.0
    return round(result.annual_charge_gbp / total_demand_mwh, 4)
