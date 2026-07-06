"""Phase 7a/7b/8a/9a — The Ledger.

A pure-function ledger that derives a chronological transaction log from
existing simulation outputs. Nine event types:

Phase 7a:
- billing_event: total customer bill (cash in, all-in including non-commodity + VAT from 9a)
- settlement_event: wholesale cost paid to grid (cash out) — one per HH period
- capital_charge_event: VaR-based capital charge (cash out) — one per HH period

Phase 7b (payment lifecycle):
- payment_received_event: cash actually collected (revenue minus bad debt provision)
- bad_debt_event: provision written off (cash out) — only when provision > 0

Phase 8a (growth mandate):
- acquisition_spend_event: cost of a fresh market acquisition attempt (cash out)
- fixed_cost_event: monthly operating overhead (cash out)

CTS reconciliation fix (docs/staging/drafts/NEXT_PHASE.md option B):
- cost_to_serve_event: monthly per-account cost-to-serve, fixed overhead only
  (cash out) — distinct from fixed_cost_event, account 6100 not 6200.

Phase 9a (bill structure — non-commodity + VAT):
- non_commodity_cost_event: network/levy pass-through remitted to network operators (cash out)
- vat_remittance_event: VAT collected from customer, remitted to HMRC (cash out)

P&L accounting (Phase 9a):
- revenue_gbp = billing - vat = ex-VAT revenue (commodity + non-commodity + standing)
- gross_margin_gbp = revenue - wholesale - non_commodity = commodity margin + standing
- Non-commodity and VAT events cancel out their billing-event counterparts so
  the net cash position reflects only supplier-owned margin.

All amounts use the sign convention: positive = cash in, negative = cash out.
Transaction IDs are deterministic UUIDs (uuid5) so the same inputs always
produce the same IDs — the ledger is idempotent and auditable.

Phase 7b: pass a `payment_behaviour` module (or duck-typed equivalent with
`CREDIT_RISK_BY_CUSTOMER`, `DEFAULT_CREDIT_RISK`, `bad_debt_provision_gbp()`,
`expected_payment_date()`) as the third argument to `build_ledger()` to add
payment lifecycle events. Omit it (or pass None) for Phase 7a behaviour.

Phase 8a: pass `extra_events` (list of acquisition_spend_event and
fixed_cost_event dicts) as the fourth argument to `build_ledger()`. These are
generated upstream by the simulation loop and merged into the sorted output.
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


def make_acquisition_spend_event(
    billing_account: str,
    event_date: str,
    amount_gbp: float,
    won: bool,
    segment: str,
) -> dict[str, Any]:
    """Cash out: cost of a fresh market acquisition attempt (win or loss)."""
    return {
        "transaction_id": _tid("acquisition_spend", billing_account, event_date),
        "event_type": "acquisition_spend_event",
        "timestamp": event_date,
        "billing_account": billing_account,
        "segment": segment,
        "amount_gbp": -amount_gbp,
        "acquisition_won": won,
    }



def make_retention_cost_event(
    billing_account: str,
    event_date: str,
    cost_gbp: float,
    company_churn_estimate: float,
) -> dict[str, Any]:
    return {
        'transaction_id': _tid('retention_cost', billing_account, event_date),
        'event_type': 'retention_cost_event',
        'timestamp': event_date,
        'billing_account': billing_account,
        'company_churn_estimate': company_churn_estimate,
        'amount_gbp': -cost_gbp,
    }

def make_fixed_cost_event(month: str, amount_gbp: float) -> dict[str, Any]:
    """Cash out: monthly operating overhead (metering admin, licensing, ops)."""
    return {
        "transaction_id": _tid("fixed_cost", month),
        "event_type": "fixed_cost_event",
        "timestamp": month + "-01",
        "month": month,
        "amount_gbp": -amount_gbp,
    }


def make_cost_to_serve_event(month: str, amount_gbp: float) -> dict[str, Any]:
    """Cash out: monthly per-account cost-to-serve (billing/IT/smart-meter
    fixed overhead, `saas.cost_to_serve.build_cost_to_serve_ledger_events()`).

    Distinct from `fixed_cost_event` (company-wide flat overhead, account
    6200) — this is account 6100, the per-account operational cost the
    customer-value/pricing layer already computes. Bad debt is deliberately
    excluded (see `saas.cost_to_serve` module docstring) — that is
    `bad_debt_event`/account 6001 alone.
    """
    return {
        "transaction_id": _tid("cost_to_serve", month),
        "event_type": "cost_to_serve_event",
        "timestamp": month + "-01",
        "month": month,
        "amount_gbp": -amount_gbp,
    }


def make_non_commodity_cost_event(bill: dict[str, Any]) -> dict[str, Any]:
    """Cash out: network/levy pass-through remitted to network operators.

    Offsets the non-commodity portion of the billing_event — zero net margin
    on this component. Only generated when bill has non_commodity_amount_gbp.
    """
    return {
        "transaction_id": _tid("non_commodity", bill["customer_id"], bill["period_start"]),
        "event_type": "non_commodity_cost_event",
        "timestamp": bill["period_start"],
        "customer_id": bill["customer_id"],
        "commodity": bill.get("commodity", "electricity"),
        "amount_gbp": -bill["non_commodity_amount_gbp"],
    }


def make_vat_remittance_event(bill: dict[str, Any]) -> dict[str, Any]:
    """Cash out: VAT collected from customer, remitted to HMRC.

    Offsets the VAT portion of the billing_event — VAT is not supplier income.
    Only generated when bill has vat_gbp.
    """
    return {
        "transaction_id": _tid("vat_remittance", bill["customer_id"], bill["period_start"]),
        "event_type": "vat_remittance_event",
        "timestamp": bill["period_start"],
        "customer_id": bill["customer_id"],
        "amount_gbp": -bill["vat_gbp"],
    }


def build_ledger(
    all_records: list[dict[str, Any]],
    bills: list[dict[str, Any]],
    payment_behaviour: Any = None,
    extra_events: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Derive the full transaction log from simulation outputs.

    `all_records` — settlement records from run_phase2b (one per HH period)
    `bills` — monthly bills from build_monthly_bills (one per customer-month)
    `payment_behaviour` — optional module (or duck-typed equivalent) with
        `CREDIT_RISK_BY_CUSTOMER`, `DEFAULT_CREDIT_RISK`,
        `bad_debt_provision_gbp()`, `expected_payment_date()`.
        When provided, adds payment_received_event and bad_debt_event entries.
    `extra_events` — optional list of pre-built events (Phase 8a acquisition_spend_event
        and fixed_cost_event dicts) to merge into the sorted output.

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

        # Phase 9a: non-commodity pass-through and VAT offsets
        if b.get("non_commodity_amount_gbp"):
            events.append(make_non_commodity_cost_event(b))
        if b.get("vat_gbp"):
            events.append(make_vat_remittance_event(b))

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

    if extra_events:
        events.extend(extra_events)

    events.sort(key=lambda e: (e["timestamp"], e.get("settlement_period", 0), e["event_type"]))
    return events


def derive_pnl(events: list[dict[str, Any]]) -> dict[str, float]:
    """Aggregate ledger events to P&L. Pure function — no simulation state.

    Phase 9a accounting:
    - revenue_gbp = total billed - VAT remittance (ex-VAT supplier revenue)
    - gross_margin_gbp = revenue - wholesale - non_commodity (commodity + standing margin)
    When no Phase 9a events exist (pre-9a ledgers), behaviour is unchanged.

    When payment lifecycle events are present (Phase 7b), also computes
    `cash_collected_gbp`, `bad_debt_gbp`, and `cash_net_margin_gbp`.
    """
    total_billed = sum(e["amount_gbp"] for e in events if e["event_type"] == "billing_event")
    wholesale = -sum(e["amount_gbp"] for e in events if e["event_type"] == "settlement_event")
    capital = -sum(e["amount_gbp"] for e in events if e["event_type"] == "capital_charge_event")

    # Phase 9a: VAT is not supplier income; non-commodity is a pass-through cost
    vat_events = [e for e in events if e["event_type"] == "vat_remittance_event"]
    nc_events = [e for e in events if e["event_type"] == "non_commodity_cost_event"]
    vat_remittance = -sum(e["amount_gbp"] for e in vat_events)       # positive (cash out)
    non_commodity_cost = -sum(e["amount_gbp"] for e in nc_events)     # positive (cash out)

    revenue = total_billed - vat_remittance      # ex-VAT revenue (supplier's reported revenue)
    gross = revenue - wholesale - non_commodity_cost  # margin on commodity + standing
    net = gross - capital
    result: dict[str, float] = {
        "revenue_gbp": revenue,
        "wholesale_cost_gbp": wholesale,
        "gross_margin_gbp": gross,
        "capital_cost_gbp": capital,
        "net_margin_gbp": net,
    }

    if vat_events or nc_events:
        result["total_billed_gbp"] = total_billed
        if vat_events:
            result["vat_remittance_gbp"] = vat_remittance
        if nc_events:
            result["non_commodity_cost_gbp"] = non_commodity_cost

    payment_events = [e for e in events if e["event_type"] == "payment_received_event"]
    if payment_events:
        cash_collected = sum(e["amount_gbp"] for e in payment_events)
        bad_debt = -sum(
            e["amount_gbp"] for e in events if e["event_type"] == "bad_debt_event"
        )
        result["cash_collected_gbp"] = cash_collected
        result["bad_debt_gbp"] = bad_debt
        result["cash_net_margin_gbp"] = cash_collected - wholesale - capital - non_commodity_cost

    acq_events = [e for e in events if e["event_type"] == "acquisition_spend_event"]
    if acq_events:
        acq_spend = -sum(e["amount_gbp"] for e in acq_events)
        result["acquisition_spend_gbp"] = acq_spend

    fixed_events = [e for e in events if e["event_type"] == "fixed_cost_event"]
    if fixed_events:
        fixed_cost = -sum(e["amount_gbp"] for e in fixed_events)
        result["fixed_cost_gbp"] = fixed_cost

    cts_events = [e for e in events if e["event_type"] == "cost_to_serve_event"]
    if cts_events:
        cts_cost = -sum(e["amount_gbp"] for e in cts_events)
        result["cost_to_serve_gbp"] = cts_cost

    if acq_events or fixed_events or cts_events:
        acq = result.get("acquisition_spend_gbp", 0.0)
        fixed = result.get("fixed_cost_gbp", 0.0)
        cts = result.get("cost_to_serve_gbp", 0.0)
        result["operating_net_margin_gbp"] = net - acq - fixed - cts

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
