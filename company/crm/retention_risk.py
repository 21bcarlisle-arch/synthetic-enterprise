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


def _required_as_of(as_of: date) -> date:
    if as_of is None:
        raise ValueError(
            "retention_risk needs the as_of date its signals are read on; there is no wall-clock "
            "default inside a simulated run"
        )
    return as_of


def _has_overdue_invoice(account_id: str, invoices: list[dict], as_of: date) -> bool:
    today = _required_as_of(as_of).isoformat()
    return any(
        inv["payment_status"] in ("unpaid", "partially_paid")
        and inv.get("due_date", today) < today
        for inv in invoices
        if inv["customer_id"] == account_id
    )


def _has_recent_complaint(account_id: str, contacts: list[dict], as_of: date,
                          lookback_days: int = 90) -> bool:
    from datetime import timedelta
    cutoff = (_required_as_of(as_of) - timedelta(days=lookback_days)).isoformat()
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
    as_of: date | None = None,
) -> dict:
    """Score a customer's churn risk from observable signals.

    Returns dict: score (0-5), tier (LOW/MEDIUM/HIGH), signals list.

    `as_of` defaults to the machine's date ONLY because this score's one caller is the portal's
    admin page (via `portfolio_risk_summary`), which serves a finished book in real time and has
    no run date to give. A run must pass its own date; `retention_risk_feature_vector` refuses
    to go without one.
    """
    as_of = as_of if as_of is not None else date.today()
    account_id = customer.get("customer_id", "")
    score = 0
    signals = []

    if _has_overdue_invoice(account_id, invoices, as_of):
        score += 2
        signals.append("Overdue invoice")

    if _has_recent_complaint(account_id, contacts, as_of):
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


def retention_risk_feature_vector(
    customer: dict,
    invoices: list[dict],
    contacts: list[dict],
    renewal_info: dict | None = None,
    rate_cmp: dict | None = None,
    *,
    as_of: date,
) -> dict:
    """Re-express the same observable signals `retention_risk()` scores as a
    numeric feature vector (Phase QL Part 2, docs/design/PROCESS_MODEL.md
    Section 3).

    PROCESS_MODEL.md names retention_risk.py's composite score as "the
    natural feature vector" a churn-estimate model should consume for the
    company's only proxy on the SIM-hidden churn-journey state
    (simulation/churn_journey.py): the company can never read
    ChurnJourneyState directly, only its exhaust -- overdue invoices, a
    recent complaint, the renewal window opening, and its own tariff-vs-
    market rate comparison. This function collapses nothing to a single
    0-5 score; it returns the raw named features so a model can weight them
    independently. Every feature is something a real UK supplier's own CRM/
    billing systems would already hold -- no SIM-internal read, consistent
    with `retention_risk()` above (unchanged, still epistemically clean).

    `as_of` is the date the company reads these signals on and is REQUIRED; a run reaches this
    (tools/generate_shadow_html.py, after every run) and must never age its book against today.
    """
    account_id = customer.get("customer_id", "")
    return {
        "customer_id": account_id,
        "overdue_invoice": 1.0 if _has_overdue_invoice(account_id, invoices, as_of) else 0.0,
        "recent_complaint_90d": 1.0 if _has_recent_complaint(account_id, contacts, as_of) else 0.0,
        "renewal_window_open": 1.0 if (renewal_info and renewal_info.get("in_notice_window")) else 0.0,
        "renewal_is_fixed": 1.0 if (renewal_info and renewal_info.get("is_fixed")) else 0.0,
        "rate_gap_pct_vs_market": float(rate_cmp.get("delta_p", 0.0)) if rate_cmp else 0.0,
        "rate_protected": 1.0 if (rate_cmp and rate_cmp.get("protected")) else 0.0,
        "smart_meter_installed": 1.0 if customer.get("smart_meter") else 0.0,
    }


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
