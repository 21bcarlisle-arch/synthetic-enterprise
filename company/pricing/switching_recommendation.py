"""Switching recommendation engine — synthesises contract status, market rate, and price cap
into a plain-language recommendation for domestic customers.

Considers:
  1. Contract type (fixed/variable)
  2. Days until renewal (renewal window)
  3. Market rate vs contracted rate (protected or exposed)
  4. Ofgem price cap relative to effective rate
"""

from __future__ import annotations
from datetime import date

from company.billing.contract import renewal_summary
from company.pricing.ofgem_price_cap import get_cap_unit_rate_gbp_per_mwh


def _cap_p_per_kwh(year: int) -> float | None:
    """Ofgem cap unit rate ceiling in p/kWh (divides £/MWh by 10)."""
    rate_mwh = get_cap_unit_rate_gbp_per_mwh("electricity", year)
    if rate_mwh is None:
        return None
    return round(rate_mwh / 10.0, 2)


def switching_recommendation(
    customer: dict,
    rate_cmp: dict | None = None,
    as_of: date | None = None,
) -> dict:
    """Generate a switching recommendation for a domestic customer.

    customer: customer dict from saas/customers.py
    rate_cmp: output from market_rate_comparison() (optional)
    Returns dict: action (switch / consider_switching / stay / not_applicable),
    reason (plain text), urgency (high/medium/low).
    """
    pivot = as_of or date.today()
    segment = str(customer.get("segment", "")).lower()

    if segment not in ("resi", "sme"):
        return {"action": "not_applicable", "reason": "Switching tool applies to domestic/SME only.",
                "urgency": "none"}

    renewal = renewal_summary(customer, as_of)
    cap_p = _cap_p_per_kwh(pivot.year)

    contracted_p = rate_cmp.get("contracted_p") if rate_cmp else None
    protected = rate_cmp.get("protected") if rate_cmp else None
    market_p = rate_cmp.get("market_p") if rate_cmp else None

    # Variable SVT customer — always compare against market
    if not renewal["is_fixed"]:
        if market_p and contracted_p and market_p < contracted_p * 0.95:
            return {"action": "switch",
                    "reason": f"On variable rate ({contracted_p}p/kWh). Market fixed rates are lower ({market_p}p/kWh). Switch now.",
                    "urgency": "high"}
        return {"action": "consider_switching",
                "reason": "On variable rate — check fixed tariffs to lock in.",
                "urgency": "low"}

    # Fixed contract — check if in notice window
    days = renewal.get("days_until_renewal")
    in_window = renewal.get("in_notice_window", False)

    if in_window:
        if protected:
            return {"action": "stay",
                    "reason": f"Contract renews in {days} days. You are locked in below market — consider renewing fixed.",
                    "urgency": "medium"}
        else:
            return {"action": "switch",
                    "reason": f"Contract renews in {days} days. Market rate is lower. Compare tariffs now.",
                    "urgency": "high"}

    # Not in window — fixed contract, stable
    if protected:
        return {"action": "stay",
                "reason": f"Fixed contract active ({days} days remaining). Locked in below market — stay.",
                "urgency": "none"}

    return {"action": "consider_switching",
            "reason": f"Fixed contract active ({days} days remaining). Review options at renewal.",
            "urgency": "low"}
