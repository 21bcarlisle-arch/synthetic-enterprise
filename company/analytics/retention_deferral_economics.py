"""Retention offers price a deferral window, not lifetime CLV -- docs/staging/QL_WIRE_AND_DEFERRAL.md.

H1 = assumed_deferral_months baked into the retention decision at run_phase2b.py (one renewal term).
H2 = realized months to the customer's next terminal event -- another offer, or churn.
Phase QK found C1/C5/C6 retained then churned once the underlying signal decayed: an offer buys time, not loyalty.
"""
from __future__ import annotations

from datetime import date


def compute_realized_deferrals(retention_log: list[dict], company_event_log: list[dict]) -> list[dict]:
    offers_by_cust: dict[str, list[dict]] = {}
    for r in retention_log:
        if r.get("outcome") == "pending":
            continue
        offers_by_cust.setdefault(r["customer_id"], []).append(r)
    for offers in offers_by_cust.values():
        offers.sort(key=lambda r: r["event_date"])

    churns_by_cust: dict[str, list[str]] = {}
    for e in company_event_log:
        if e.get("event_type") == "churn":
            churns_by_cust.setdefault(e["customer_id"], []).append(e["event_date"])
    for dates in churns_by_cust.values():
        dates.sort()

    records = []
    for cid, offers in offers_by_cust.items():
        churn_dates = churns_by_cust.get(cid, [])
        for i, offer in enumerate(offers):
            offer_date = date.fromisoformat(offer["event_date"])
            candidates: list[tuple[date, str]] = []
            if i + 1 < len(offers):
                candidates.append((date.fromisoformat(offers[i + 1]["event_date"]), "next_offer"))
            future_churns = [c for c in churn_dates if date.fromisoformat(c) >= offer_date]
            if future_churns:
                candidates.append((date.fromisoformat(future_churns[0]), "churn"))

            assumed = offer.get("assumed_deferral_months", 12)
            if candidates:
                next_date, next_event_type = min(candidates, key=lambda t: t[0])
                realized = round((next_date - offer_date).days / 30.44, 1)
            else:
                next_event_type = None
                realized = None

            records.append({
                "customer_id": cid,
                "offer_date": offer["event_date"],
                "assumed_deferral_months": assumed,
                "realized_deferral_months": realized,
                "next_event_type": next_event_type,
                "underperformed": realized is not None and realized < assumed,
                "cost_gbp": offer.get("retention_cost_gbp", 0.0),
                "expected_term_margin_gbp": offer.get("expected_term_margin_gbp", 0.0),
            })
    return records


def serial_saver_summary(retention_log: list[dict]) -> list[dict]:
    offers_by_cust: dict[str, list[dict]] = {}
    for r in retention_log:
        if r.get("outcome") == "pending":
            continue
        offers_by_cust.setdefault(r["customer_id"], []).append(r)

    summaries = []
    for cid, offers in offers_by_cust.items():
        offers_sorted = sorted(offers, key=lambda r: r["event_date"])
        cumulative_cost = sum(o.get("retention_cost_gbp", 0.0) for o in offers_sorted)
        final_outcome = offers_sorted[-1]["outcome"]
        is_serial_saver = len(offers_sorted) >= 2
        summaries.append({
            "customer_id": cid,
            "offer_count": len(offers_sorted),
            "cumulative_cost_gbp": round(cumulative_cost, 2),
            "final_outcome": final_outcome,
            "is_serial_saver": is_serial_saver,
            "ev_negative": is_serial_saver and final_outcome == "churned_despite_offer",
        })
    return summaries
