"""Ofgem per-customer solvency signal (Minimum Capital Requirement).

Ofgem's supply licence Standard Condition 27 requires licensed suppliers to
maintain net assets sufficient to cover obligations to customers. The default
requirement is approximately £130 per dual-fuel customer (the 'MCR target').

The actual MCR is computed from the supplier's gross revenue and customer
obligations, but for our purposes the per-customer net asset floor is the
key signal. When treasury per customer falls below the MCR floor, the company
is in Ofgem compliance stress.

This module computes annual per-customer solvency metrics from settlement data:
- per_customer_net_assets_gbp: treasury / active_customers at year-end
- mcr_floor_gbp: £130/customer (regulatory minimum; MCR target for dual-fuel)
- solvency_ratio: per_customer_net_assets / mcr_floor
- status: OK / Watch / STRESS

The company can observe these values from its own P&L and treasury — no SIM
internals are read here.
"""

from __future__ import annotations

MCR_FLOOR_GBP_PER_CUSTOMER: float = 130.0
MCR_WATCH_RATIO: float = 2.0
MCR_STRESS_RATIO: float = 1.0


def compute_solvency_signal(
    treasury_gbp: float,
    active_customer_count: int,
    mcr_floor: float = MCR_FLOOR_GBP_PER_CUSTOMER,
) -> dict:
    """Compute Ofgem solvency signal for a given year-end position.

    Parameters
    ----------
    treasury_gbp : year-end treasury balance (£)
    active_customer_count : number of active accounts at year-end
    mcr_floor : minimum net assets per customer (£); defaults to £130

    Returns
    -------
    dict with keys:
        per_customer_net_assets_gbp: treasury / customers
        mcr_floor_gbp: the regulatory floor per customer
        solvency_ratio: per_customer_net_assets / mcr_floor
        status: 'OK' | 'Watch' | 'STRESS'
    """
    if active_customer_count <= 0:
        return {
            "per_customer_net_assets_gbp": 0.0,
            "mcr_floor_gbp": mcr_floor,
            "solvency_ratio": 0.0,
            "status": "STRESS",
        }

    per_customer = treasury_gbp / active_customer_count
    ratio = per_customer / mcr_floor if mcr_floor > 0 else float("inf")

    if ratio < MCR_STRESS_RATIO:
        status = "STRESS"
    elif ratio < MCR_WATCH_RATIO:
        status = "Watch"
    else:
        status = "OK"

    return {
        "per_customer_net_assets_gbp": round(per_customer, 2),
        "mcr_floor_gbp": mcr_floor,
        "solvency_ratio": round(ratio, 3),
        "status": status,
    }


def compute_solvency_by_year(years_data: dict) -> dict:
    """Compute solvency signal for each year from report data.

    years_data: the 'years' dict from extract_report_data(), each entry
    must contain 'treasury_gbp' and either 'active_customer_count'
    or 'active_customer_ids' (list).
    """
    result: dict = {}
    for year, yd in years_data.items():
        # Support both "treasury_gbp" (clean) and "treasury_end_gbp" (annual report dict key)
        treasury = yd.get("treasury_gbp", yd.get("treasury_end_gbp", 0.0))
        customers = yd.get("active_customer_count", 0)
        if customers == 0:
            customers = len(yd.get("active_customer_ids", []))
        result[year] = compute_solvency_signal(treasury, customers)
    return result
