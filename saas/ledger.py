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

from company.governance.decision_rights import DecisionClass, log_decision_event

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


def make_back_billing_write_off_event(bill: dict[str, Any]) -> dict[str, Any]:
    """ADVISOR_STEER_BACKBILLING_GATE.md item 1: a named, visible P&L line
    for the SLC 21BA back-billing cap's unrecoverable tranche -- "the
    excess becomes a supplier loss (write-off ledger event), not revenue"
    (REGULATORY_RULES_AS_FIDELITY_ORACLE.md finding #1).

    `amount_gbp` is deliberately 0.0 -- this is a MEMO/visibility event, not
    a second cash-impact event. The real cash effect already happened
    correctly and silently: `bill["total_amount_gbp"]` (the billing_event
    this bill produces) was built from `catchup["chargeable_gbp"]`, the
    CAPPED amount, never the full raw delta -- so revenue already excludes
    the written-off tranche, while `settlement_event` still charges the
    company the true wholesale cost of the energy actually consumed. That
    gap IS the write-off's margin impact, and it already flows correctly
    through `derive_pnl`'s wholesale/revenue arithmetic. Adding a second
    negative-amount event here would double-count it. What was missing
    before this steer was not the cash effect but a NAMED, auditable line
    saying why -- `write_off_amount_gbp` carries that figure for reporting.
    """
    return {
        "transaction_id": _tid("back_billing_write_off", bill["customer_id"], bill["period_end"]),
        "event_type": "back_billing_write_off_event",
        "timestamp": bill["period_end"],
        "customer_id": bill["customer_id"],
        "amount_gbp": 0.0,
        "write_off_amount_gbp": bill.get("catchup_written_off_gbp", 0.0),
        "adjustment_id": bill.get("catchup_write_off_adjustment_id", ""),
        "reason": bill.get("catchup_write_off_adjustment_reason", ""),
    }


def make_revenue_restatement_event(bill: dict[str, Any]) -> dict[str, Any]:
    """E3_accrual_restatement: a named, visible P&L line for D3's own real
    catch-up-rebilling delta -- accrual accounting requires that estimated-
    basis revenue recognised in one period, then corrected against an
    actual read in a later period, is traceable as a RESTATEMENT of prior
    accrued revenue, not indistinguishable from ordinary new-period revenue.

    `amount_gbp` is deliberately 0.0 -- this is a MEMO/visibility event, same
    pattern as `make_back_billing_write_off_event`. The real cash effect
    already happened correctly via the resolving bill's own
    `total_amount_gbp` (which already folds in `catchup_adjustment_gbp`) --
    a second cash-impact event here would double-count it. This event
    exists purely to make the restatement NAMED and auditable: how much of
    today's billed revenue is a correction of a PRIOR period's estimate,
    in which direction, and covering how many prior periods.
    """
    return {
        "transaction_id": _tid("revenue_restatement", bill["customer_id"], bill["period_end"]),
        "event_type": "revenue_restatement_event",
        "timestamp": bill["period_end"],
        "customer_id": bill["customer_id"],
        "amount_gbp": 0.0,
        "restated_gbp": bill.get("catchup_raw_delta_gbp", 0.0),
        "chargeable_gbp": bill.get("catchup_adjustment_gbp", 0.0),
        "direction": bill.get("catchup_direction", ""),
        "periods_covered": bill.get("catchup_periods_covered", 0),
    }


def unbilled_revenue_accrual(bills: list[dict[str, Any]]) -> dict[str, Any]:
    """E3_accrual_restatement: the accrual-accounting counterpart to D3's
    customer-facing catch-up mechanism.

    An estimated-basis bill's revenue is already recognised in full via its
    own billing_event (Phase 7a) -- that cash/revenue effect is correct and
    unchanged. What accrual accounting additionally requires is a way to
    tell HOW MUCH of currently-recognised revenue is still PROVISIONAL
    (estimated, not yet confirmed against an actual meter read) versus
    CONFIRMED -- the real "unbilled revenue" asset a real supplier's
    accounts would carry until the true-up lands.

    A bill is OUTSTANDING (still provisional) if it is `billing_basis ==
    "estimated"` and no LATER bill for the same customer has a
    `catchup_applied` covering its period (`catchup_period_start` <=
    this bill's `period_end` <= `catchup_period_end`) -- exactly the same
    real period-range D3's own `_resolve_catchup()` already computes and
    stamps on the resolving bill, reused here rather than re-derived.

    Returns a dict: `unbilled_revenue_gbp` (portfolio total, GBP still
    provisional as of the last bill in `bills`), `outstanding_bill_count`,
    and `by_customer` (customer_id -> outstanding GBP, only customers with
    a non-zero balance).
    """
    by_customer_estimated: dict[str, list[dict[str, Any]]] = {}
    resolved_ranges: dict[str, list[tuple[str, str]]] = {}
    for b in bills:
        cid = b["customer_id"]
        if b.get("billing_basis") == "estimated":
            by_customer_estimated.setdefault(cid, []).append(b)
        if b.get("catchup_applied"):
            resolved_ranges.setdefault(cid, []).append(
                (b.get("catchup_period_start", ""), b.get("catchup_period_end", ""))
            )

    unbilled_total = 0.0
    outstanding_count = 0
    by_customer: dict[str, float] = {}
    for cid, est_bills in by_customer_estimated.items():
        ranges = resolved_ranges.get(cid, [])
        customer_total = 0.0
        for b in est_bills:
            period_end = b.get("period_end", "")
            resolved = any(start <= period_end <= end for start, end in ranges)
            if not resolved:
                customer_total += b.get("total_amount_gbp", 0.0)
                outstanding_count += 1
        if customer_total:
            by_customer[cid] = round(customer_total, 2)
            unbilled_total += customer_total

    return {
        "unbilled_revenue_gbp": round(unbilled_total, 2),
        "outstanding_bill_count": outstanding_count,
        "by_customer": by_customer,
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
        if b.get("catchup_written_off_gbp", 0.0) > 0:
            events.append(make_back_billing_write_off_event(b))
        if b.get("catchup_applied"):
            events.append(make_revenue_restatement_event(b))

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
                # A2_decision_rights_register (2026-07-12): CREDIT_COLLECTIONS_
                # POLICY's real, already-existing decision instance -- the
                # company writing off a provisioned amount against this
                # account's arrears, per payment_behaviour's credit-risk
                # model, for every bill across the full historical replay.
                # Same "log each real instance, not a change to the policy
                # itself" pattern PRICING_MOVE already established.
                log_decision_event(
                    DecisionClass.CREDIT_COLLECTIONS_POLICY,
                    entity_id=cid,
                    request={
                        "bill_period_end": b["period_end"],
                        "total_amount_gbp": b["total_amount_gbp"],
                    },
                    context={"credit_risk": credit_risk, "provision_gbp": provision},
                    decision={"write_off_gbp": provision},
                    rationale=(
                        "bad-debt provision applied per payment_behaviour's "
                        "credit-risk model for this account/bill"
                    ),
                    valid_time=date.fromisoformat(payment_date),
                )

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

    write_off_events = [e for e in events if e["event_type"] == "back_billing_write_off_event"]
    if write_off_events:
        result["back_billing_write_off_gbp"] = sum(
            e["write_off_amount_gbp"] for e in write_off_events
        )

    restatement_events = [e for e in events if e["event_type"] == "revenue_restatement_event"]
    if restatement_events:
        result["revenue_restated_gbp"] = sum(e["restated_gbp"] for e in restatement_events)
        result["revenue_restatement_count"] = len(restatement_events)

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
