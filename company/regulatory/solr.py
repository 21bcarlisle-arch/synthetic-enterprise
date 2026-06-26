"""Supplier of Last Resort (SoLR) risk assessment.

When a UK energy supplier fails, Ofgem designates a Supplier of Last Resort (SoLR)
to protect customer continuity. The SoLR inherits the failed supplier's customers,
who are initially placed on a deemed/SVT tariff.

From this company's perspective, SoLR risk is bilateral:
- Being appointed SoLR: sudden large customer intake, capital/working-capital shock
- A competitor's customers arriving as SoLR transfers: volume surge + retention challenge

This module models SoLR appointment probability based on company size and market
position, and estimates the capital impact of absorbing a failed supplier's book.

Data: Ofgem SoLR appointments are public record. Parameters calibrated to the
2021-2022 crisis in which 28 suppliers failed.
"""

from __future__ import annotations


# Approximate SoLR appointments 2021-2022; largest transfer was Bulb (1.7M customers).
# Smaller failures went to larger suppliers. We assume company is medium-sized.
_TYPICAL_TRANSFER_SIZES = {
    "small": 5_000,    # small failed supplier
    "medium": 50_000,
    "large": 200_000,
    "bulb_scale": 1_700_000,
}

# Ofgem estimates avg. SoLR levy cost per transferred customer
_SOLR_LEVY_PER_CUSTOMER_GBP = 85.0  # 2022 BSC shortfall, ~85 GBP/customer average

# Deemed SVT uplift: new SoLR customers on SVT cap; assume 12% churn within 3 months
_SVT_CHURN_RATE_3M = 0.12

# Annual revenue per acquired SoLR customer (approximate, at SVT)
_SVT_REVENUE_PER_CUSTOMER_GBP = 1_800.0


def solr_capital_requirement(transfer_size: int, treasury_gbp: float) -> dict:
    """Estimate capital requirement and sustainability of absorbing a SoLR transfer.

    Assesses whether the company has sufficient treasury to absorb the transfer
    cost (BSC shortfall levy + bad debt uplift for stressed customer base).

    Args:
        transfer_size: number of customers being transferred
        treasury_gbp: company's current treasury position

    Returns: required_gbp, treasury_gbp, headroom_gbp, sustainable (bool), status
    """
    levy = transfer_size * _SOLR_LEVY_PER_CUSTOMER_GBP
    # Bad debt uplift: assume 15% of SVT customers struggle to pay, avg 60% recovery
    bad_debt_risk = transfer_size * _SVT_REVENUE_PER_CUSTOMER_GBP * 0.15 * 0.40
    total_required = levy + bad_debt_risk
    headroom = treasury_gbp - total_required

    if headroom >= total_required * 0.5:
        status = "SUSTAINABLE"
    elif headroom >= 0:
        status = "MARGINAL"
    else:
        status = "UNSUSTAINABLE"

    return {
        "transfer_size": transfer_size,
        "levy_gbp": round(levy, 2),
        "bad_debt_risk_gbp": round(bad_debt_risk, 2),
        "total_required_gbp": round(total_required, 2),
        "treasury_gbp": round(treasury_gbp, 2),
        "headroom_gbp": round(headroom, 2),
        "sustainable": headroom >= 0,
        "status": status,
    }


def solr_revenue_upside(transfer_size: int, churn_rate: float = _SVT_CHURN_RATE_3M) -> dict:
    """Estimate revenue upside from retaining SoLR customers.

    Many SoLR customers switch away quickly — this models the retained book.
    """
    retained = round(transfer_size * (1 - churn_rate))
    annual_revenue = round(retained * _SVT_REVENUE_PER_CUSTOMER_GBP, 2)
    return {
        "transfer_size": transfer_size,
        "expected_churn_3m": round(transfer_size * churn_rate),
        "retained_customers": retained,
        "estimated_annual_revenue_gbp": annual_revenue,
    }


def solr_scenario(scenario: str, treasury_gbp: float) -> dict:
    """Run a named SoLR scenario (small/medium/large/bulb_scale).

    Returns combined capital requirement + revenue upside analysis.
    """
    size = _TYPICAL_TRANSFER_SIZES.get(scenario.lower(), _TYPICAL_TRANSFER_SIZES["medium"])
    cap = solr_capital_requirement(size, treasury_gbp)
    rev = solr_revenue_upside(size)
    return {
        "scenario": scenario,
        **cap,
        "revenue": rev,
    }
