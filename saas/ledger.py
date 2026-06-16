"""Phase 7a/7b — The Ledger.

A pure-function ledger that derives a chronological transaction log from
existing simulation outputs. Five event types:

Phase 7a:
- billing_event: revenue raised when a bill is issued (cash in)
- settlement_event: wholesale cost paid to grid (cash out) — one per HH period
- capital_charge_event: VaR-based capital charge (cash out) — one per HH period

Phase 7b (payment lifecycle):
- payment_received_event: cash actually collected (revenue minus bad debt provision)
- bad_debt_event: provision written off (cash out) — only when provision > 0

All amounts use the sign convention: positive = cash in, negative = cash out.
Transaction IDs are deterministic UUIDs (uuid5) so the same inputs always
produce the same IDs — the ledger is idempotent and auditable.

Phase 7b: pass a `payment_behaviour` module (or duck-typed equivalent with
`CREDIT_RISK_BY_CUSTOMER`, `DEFAULT_CREDIT_RISK`, `bad_debt_provision_gbp()`,
`expected_payment_date()`) as the third argument to `build_ledger()` to add
payment lifecycle events. Omit it (or pass None) for Phase 7a behaviour.
"""

import uuid
from datetime import date, timedelta
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


def make_payment_received_event(
    bill: dict[str, Any],
    provision_gbp: float,
    payment_date: str,
) -> dict[str, Any]:
    """Cash collected against a bill: total billed minus bad-debt provision."""
    return {
        "transaction_id": _tid("payment_received", bill["customer_id"], bill["period_end"]),
        "event_type": "payment_received_event",
        "timestamp": payment_date,
        "customer_id": bill["customer_id"],
        "bill_period_end": bill["period_end"],
        "amount_gbp": bill["total_amount_gbp"] - provision_gbp,
    }


def make_bad_debt_event(
    bill: dict[str, Any],
    provision_gbp: float,
    payment_date: str,
) -> dict[str, Any]:
    """Bad-debt write-off: provision posted 30 days after expected payment date."""
    write_off_date = (date.fromisoformat(payment_date) + timedelta(days=30)).isoformat()
    return {
        "transaction_id": _tid("bad_debt", bill["customer_id"], bill["period_end"]),
        "event_type": "bad_debt_event",
        "timestamp": write_off_date,
        "customer_id": bill["customer_id"],
        "bill_period_end": bill["period_end"],
        "amount_gbp": -provision_gbp,
    }


def build_ledger(
    all_records: list[dict[str, Any]],
    bills: list[dict[str, Any]],
    payment_behaviour: Any = None,
) -> list[dict[str, Any]]:
    """Derive the full transaction log from simulation outputs.

    `all_records` — settlement records from run_phase2b (one per HH period)
    `bills` — monthly bills from build_monthly_bills (one per customer-month)
    `payment_behaviour` — optional module (or duck-typed equivalent) with
        `CREDIT_RISK_BY_CUSTOMER`, `DEFAULT_CREDIT_RISK`,
        `bad_debt_provision_gbp()`, `expected_payment_date()`.
        When provided, adds payment_received_event and bad_debt_event entries.

    Returns events sorted chronologically.
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

        if payment_behaviour is not None:
            credit_risk = payment_behaviour.CREDIT_RISK_BY_CUSTOMER.get(
                cid, payment_behaviour.DEFAULT_CREDIT_RISK
            )
            provision = payment_behaviour.bad_debt_provision_gbp(
                credit_risk, b["total_amount_gbp"]
            )
            payment_date = payment_behaviour.expected_payment_date(
                b["period_end"], credit_risk
            )
            events.append(make_payment_received_event(b, provision, payment_date))
            if provision > 0:
                events.append(make_bad_debt_event(b, provision, payment_date))

    events.sort(key=lambda e: (e["timestamp"], e.get("settlement_period", 0), e["event_type"]))
    return events


def derive_pnl(events: list[dict[str, Any]]) -> dict[str, float]:
    """Aggregate ledger events to P&L. Pure function — no simulation state.

    When payment lifecycle events are present (Phase 7b), also computes
    `cash_collected_gbp`, `bad_debt_gbp`, and `cash_net_margin_gbp`
    (cash actually collected minus wholesale and capital costs).
    """
    revenue = sum(e["amount_gbp"] for e in events if e["event_type"] == "billing_event")
    wholesale = -sum(e["amount_gbp"] for e in events if e["event_type"] == "settlement_event")
    capital = -sum(e["amount_gbp"] for e in events if e["event_type"] == "capital_charge_event")
    gross = revenue - wholesale
    net = gross - capital
    result: dict[str, float] = {
        "revenue_gbp": revenue,
        "wholesale_cost_gbp": wholesale,
        "gross_margin_gbp": gross,
        "capital_cost_gbp": capital,
        "net_margin_gbp": net,
    }

    payment_events = [e for e in events if e["event_type"] == "payment_received_event"]
    if payment_events:
        cash_collected = sum(e["amount_gbp"] for e in payment_events)
        bad_debt = -sum(
            e["amount_gbp"] for e in events if e["event_type"] == "bad_debt_event"
        )
        result["cash_collected_gbp"] = cash_collected
        result["bad_debt_gbp"] = bad_debt
        result["cash_net_margin_gbp"] = cash_collected - wholesale - capital

    return result


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


def build_payment_behaviour_map(payment_behaviour: Any) -> dict[str, Any]:
    """Extract per-customer credit-risk and provision data for reporting.

    Returns a dict keyed by customer_id with credit_risk segment.
    Used by the annual report's Transaction Log section.
    """
    return {
        cid: seg
        for cid, seg in payment_behaviour.CREDIT_RISK_BY_CUSTOMER.items()
    }
