"""Retention risk scoring -- flag customers at risk of churning.

Uses company-observable signals only:
  - Overdue invoices (debt pressure)
  - Recent complaint (dissatisfaction signal)
  - In renewal notice window (switching pressure)
  - Rate exposure vs market (financial pressure)
  - Smart meter not installed (lower engagement)

Returns a risk score 0-5 and tier: LOW / MEDIUM / HIGH.
"""

from __future__ import annotations
from datetime import date


def _has_overdue_invoice(account_id: str, invoices: list[dict]) -> bool:
    today = date.today().isoformat()
    return any(
        inv["payment_status"] in ("unpaid", "partially_paid")
        and inv.get("due_date", today) < today
        for inv in invoices
        if inv["customer_id"] == account_id
    )


def _has_recent_complaint(account_id: str, contacts: list[dict], lookback_days: int = 90) -> bool:
    from datetime import timedelta
    cutoff = (date.today() - timedelta(days=lookback_days)).isoformat()
    return any(
        c["customer_id"] == account_id
        and c.get("complaint_flag")
        and c.get("event_date", "") >= cutoff
        for c in contacts
    )


def retention_risk(
    customer: dict,
    invoices: list[dict],
    contacts: list[dict],
    renewal_info: dict | None = None,
    rate_cmp: dict | None = None,
) -> dict:
    """Score a customer's churn risk from observable signals.

    Returns dict: score (0-5), tier (LOW/MEDIUM/HIGH), signals list.
    """
    account_id = customer.get("customer_id", "")
    score = 0
    signals = []

    if _has_overdue_invoice(account_id, invoices):
        score += 2
        signals.append("Overdue invoice")

    if _has_recent_complaint(account_id, contacts):
        score += 1
        signals.append("Recent complaint (90 days)")

    if renewal_info and renewal_info.get("in_notice_window") and not renewal_info.get("is_fixed"):
        score += 1
        signals.append("Variable rate in renewal window")
    elif renewal_info and renewal_info.get("in_notice_window"):
        score += 1
        signals.append("Fixed contract in notice window")

    if rate_cmp and not rate_cmp.get("protected") and rate_cmp.get("delta_p", 0) > 1.0:
        score += 1
        signals.append("Rate significantly above market")

    if not customer.get("smart_meter") and customer.get("metering") != "HH":
        score += 0  # signal only, no score impact

    score = min(score, 5)
    if score <= 1:
        tier = "LOW"
    elif score <= 3:
        tier = "MEDIUM"
    else:
        tier = "HIGH"

    return {"score": score, "tier": tier, "signals": signals}


def portfolio_risk_summary(
    customers: list[dict],
    invoices: list[dict],
    contacts: list[dict],
) -> dict:
    """Aggregate retention risk across all customers."""
    results = []
    for c in customers:
        r = retention_risk(c, invoices, contacts)
        results.append({"customer_id": c["customer_id"], **r})

    tiers = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for r in results:
        tiers[r["tier"]] += 1

    return {
        "total": len(results),
        "high_risk": tiers["HIGH"],
        "medium_risk": tiers["MEDIUM"],
        "low_risk": tiers["LOW"],
        "customers": results,
    }
