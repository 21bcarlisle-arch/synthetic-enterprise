"""Customer lifetime value (CLV) calculator.

CLV = sum of discounted future net margins over the customer tenure.
Used by the company to:
  - Prioritise retention investment (spend up to CLV to retain)
  - Compare against CAC (Phase 123) for LTV:CAC ratio
  - Segment customers for targeted offers

CLV uses a simple discounted cash flow (DCF) model:
  CLV = annual_net_margin * (1 - (1 + discount_rate)^-tenure_years) / discount_rate

The annual_net_margin is derived from observable billing data (company layer),
not from simulation internals. Churn risk adjusts the expected tenure.

Discount rate reflects the company cost of capital (approximately 8-12% for
a UK energy retail business without investment-grade credit).
"""

from __future__ import annotations

from dataclasses import dataclass


_DEFAULT_DISCOUNT_RATE = 0.10  # 10% WACC for small UK energy retailer
_DEFAULT_CHURN_RATE = 0.18     # 18% annual churn (observed UK average 2016-2020)


@dataclass
class ClvResult:
    customer_id: str
    annual_net_margin_gbp: float
    expected_tenure_years: float
    discount_rate: float
    clv_gbp: float
    margin_tier: str     # PREMIUM / STANDARD / LOW / NET_NEGATIVE


def _dcf_sum(cash_flow: float, rate: float, years: float) -> float:
    if rate == 0:
        return cash_flow * years
    return cash_flow * (1 - (1 + rate) ** -years) / rate


def _tenure_from_churn(churn_rate: float) -> float:
    """Expected tenure = 1 / churn_rate (geometric series, years)."""
    return 1.0 / max(churn_rate, 0.01)


def _margin_tier(annual_gbp: float) -> str:
    if annual_gbp < 0:
        return "NET_NEGATIVE"
    elif annual_gbp < 50:
        return "LOW"
    elif annual_gbp < 200:
        return "STANDARD"
    return "PREMIUM"


def compute_clv(
    customer_id: str,
    annual_net_margin_gbp: float,
    churn_rate: float = _DEFAULT_CHURN_RATE,
    discount_rate: float = _DEFAULT_DISCOUNT_RATE,
    tenure_years: float | None = None,
) -> ClvResult:
    """Compute CLV using DCF over expected tenure derived from churn rate."""
    if tenure_years is None:
        tenure_years = _tenure_from_churn(churn_rate)
    clv = round(_dcf_sum(annual_net_margin_gbp, discount_rate, tenure_years), 2)
    return ClvResult(
        customer_id=customer_id,
        annual_net_margin_gbp=round(annual_net_margin_gbp, 2),
        expected_tenure_years=round(tenure_years, 2),
        discount_rate=discount_rate,
        clv_gbp=clv,
        margin_tier=_margin_tier(annual_net_margin_gbp),
    )


def clv_to_cac_ratio(clv_gbp: float, cac_gbp: float) -> dict:
    """Assess customer economics by comparing CLV to acquisition cost."""
    if cac_gbp <= 0:
        ratio = float("inf")
        verdict = "UNCAPPED"
    else:
        ratio = round(clv_gbp / cac_gbp, 2)
        if ratio >= 3.0:
            verdict = "HEALTHY"
        elif ratio >= 1.5:
            verdict = "MARGINAL"
        elif ratio >= 1.0:
            verdict = "BREAK_EVEN"
        else:
            verdict = "LOSS_MAKING"
    return {"clv_gbp": clv_gbp, "cac_gbp": cac_gbp, "ratio": ratio, "verdict": verdict}


def portfolio_clv_summary(results: list[ClvResult]) -> dict:
    if not results:
        return {"count": 0, "total_clv_gbp": 0.0, "mean_clv_gbp": 0.0}
    total = sum(r.clv_gbp for r in results)
    tiers = {}
    for r in results:
        tiers[r.margin_tier] = tiers.get(r.margin_tier, 0) + 1
    return {
        "count": len(results),
        "total_clv_gbp": round(total, 2),
        "mean_clv_gbp": round(total / len(results), 2),
        "tiers": tiers,
    }
