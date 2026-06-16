"""Phase 7a — The Ledger (Gap #2 MVP).

A pure-function ledger that derives a chronological transaction log from
existing simulation outputs. Three event types:

- billing_event: revenue collected (cash in) — one per customer per billing month
- settlement_event: wholesale cost paid to grid (cash out) — one per HH period
- capital_charge_event: VaR-based capital charge (cash out) — one per HH period

All amounts use the sign convention: positive = cash in, negative = cash out.
Transaction IDs are deterministic UUIDs (uuid5) so the same inputs always
produce the same IDs — the ledger is idempotent and auditable.

`derive_pnl(events)` and `derive_cash_position(starting_treasury, events)`
are pure aggregations that let us verify the ledger agrees with the
simulation's direct P&L calculation without re-running the simulation.
"""

import uuid
from typing import Any

_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # uuid.NAMESPACE_URL


def _tid(namespace: str, *parts: str) -> str:
    """Deterministic UUID from namespace + content parts."""
    key = f"{namespace}:" + "|".join(parts)
    return str(uuid.uuid5(_NAMESPACE, key))


def make_billing_event(
    customer_id: str,
    commodity: str,
    billing_period: str,
    amount_gbp: float,
    total_consumption_kwh: float,
) -> dict[str, Any]:
    return {
        "transaction_id": _tid("billing", customer_id, commodity, billing_period),
        "event_type": "billing_event",
        "timestamp": billing_period,
        "customer_id": customer_id,
        "commodity": commodity,
        "amount_gbp": amount_gbp,
        "total_consumption_kwh": total_consumption_kwh,
    }


def make_settlement_event(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "transaction_id": _tid(
            "settlement",
            record["customer_id"],
            record["settlement_date"],
            str(record["settlement_period"]),
        ),
        "event_type": "settlement_event",
        "timestamp": record["settlement_date"],
        "settlement_period": record["settlement_period"],
        "customer_id": record["customer_id"],
        "commodity": record.get("commodity", "electricity"),
        "amount_gbp": -record["wholesale_cost_gbp"],
        "volume_kwh": record["consumption_kwh"],
        "unit_rate_gbp_per_mwh": record["unit_rate_gbp_per_mwh"],
    }


def make_capital_charge_event(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "transaction_id": _tid(
            "capital",
            record["customer_id"],
            record["settlement_date"],
            str(record["settlement_period"]),
        ),
        "event_type": "capital_charge_event",
        "timestamp": record["settlement_date"],
        "settlement_period": record["settlement_period"],
        "customer_id": record["customer_id"],
        "commodity": record.get("commodity", "electricity"),
        "amount_gbp": -record["capital_cost_gbp"],
    }


def build_ledger(
    all_records: list[dict[str, Any]],
    bills: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Derive the full transaction log from simulation outputs.

    `all_records` — settlement records from run_phase2b (one per HH period)
    `bills` — monthly bills from build_monthly_bills (one per customer-month)

    Returns events sorted chronologically. Settlement and capital-charge events
    always precede billing events in the same month because settlement runs
    daily across the month while the bill is issued at month-end.
    """
    events: list[dict[str, Any]] = []

    # Infer commodity per customer from settlement records (needed for billing events
    # because generate_bill() doesn't carry the commodity field).
    customer_commodity: dict[str, str] = {}
    for r in all_records:
        cid = r["customer_id"]
        if cid not in customer_commodity:
            customer_commodity[cid] = r.get("commodity", "electricity")

    # One settlement_event + one capital_charge_event per settlement record
    for r in all_records:
        events.append(make_settlement_event(r))
        cap = r.get("capital_cost_gbp", 0.0)
        if cap:
            events.append(make_capital_charge_event(r))

    # One billing_event per bill
    for b in bills:
        cid = b["customer_id"]
        commodity = customer_commodity.get(cid, "electricity")
        events.append(make_billing_event(
            cid,
            commodity,
            b["period_start"],
            b["total_amount_gbp"],
            b["total_consumption_kwh"],
        ))

    events.sort(key=lambda e: (e["timestamp"], e.get("settlement_period", 0), e["event_type"]))
    return events


def derive_pnl(events: list[dict[str, Any]]) -> dict[str, float]:
    """Aggregate ledger events to P&L. Pure function — no simulation state."""
    revenue = sum(e["amount_gbp"] for e in events if e["event_type"] == "billing_event")
    wholesale = -sum(e["amount_gbp"] for e in events if e["event_type"] == "settlement_event")
    capital = -sum(e["amount_gbp"] for e in events if e["event_type"] == "capital_charge_event")
    gross = revenue - wholesale
    net = gross - capital
    return {
        "revenue_gbp": revenue,
        "wholesale_cost_gbp": wholesale,
        "gross_margin_gbp": gross,
        "capital_cost_gbp": capital,
        "net_margin_gbp": net,
    }


def derive_cash_position(starting_treasury: float, events: list[dict[str, Any]]) -> float:
    """Ending cash = starting treasury + sum of all event amounts."""
    return starting_treasury + sum(e["amount_gbp"] for e in events)


def ledger_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    """High-level summary for the report section."""
    by_type: dict[str, int] = {}
    for e in events:
        by_type[e["event_type"]] = by_type.get(e["event_type"], 0) + 1
    pnl = derive_pnl(events)
    return {
        "event_count": len(events),
        "by_type": by_type,
        "pnl": pnl,
    }
