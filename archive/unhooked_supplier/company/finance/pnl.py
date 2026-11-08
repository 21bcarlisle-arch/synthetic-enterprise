"""Company Layer — P&L from Ledger Events.

Reads the simulation's ledger events and produces a company income statement.
This view is intentionally different from the simulation's own P&L: it uses
cash-collected (payment_received_event) as revenue, not billing_event, which
gives a truer picture of actual cash flow.

The result should agree with saas.ledger.derive_pnl() for the energy-margin
components (wholesale, capital, gross) but may differ on the revenue line
because the company sees cash collected while the simulation sees billed.
"""

from typing import Any


def company_income_statement(
    ledger_events: list[dict[str, Any]],
    cost_to_serve_gbp: float = 0.0,
) -> dict[str, float]:
    """Produce a company income statement from ledger events.

    Uses payment_received_event as revenue (cash basis) if available;
    falls back to billing_event (accrual basis) if not.

    cost_to_serve_gbp: total cost-to-serve from saas.cost_to_serve (passed
    through — it's a SIM output, not derived from ledger events directly).
    """
    by_type: dict[str, list] = {}
    for e in ledger_events:
        by_type.setdefault(e["event_type"], []).append(e)

    # Revenue: cash collected if available, else billed
    payment_events = by_type.get("payment_received_event", [])
    billing_events = by_type.get("billing_event", [])
    cash_basis = bool(payment_events)

    if cash_basis:
        revenue = sum(e["amount_gbp"] for e in payment_events)
        revenue_basis = "cash (payment_received_event)"
    else:
        revenue = sum(e["amount_gbp"] for e in billing_events)
        revenue_basis = "accrual (billing_event)"

    wholesale = -sum(e["amount_gbp"] for e in by_type.get("settlement_event", []))
    capital = -sum(e["amount_gbp"] for e in by_type.get("capital_charge_event", []))
    bad_debt = -sum(e["amount_gbp"] for e in by_type.get("bad_debt_event", []))
    acq_spend = -sum(e["amount_gbp"] for e in by_type.get("acquisition_spend_event", []))
    fixed_cost = -sum(e["amount_gbp"] for e in by_type.get("fixed_cost_event", []))

    gross_margin = revenue - wholesale
    operating_costs = capital + cost_to_serve_gbp + acq_spend + fixed_cost
    net_margin = gross_margin - operating_costs

    result: dict[str, Any] = {
        "revenue_basis": revenue_basis,
        "revenue_gbp": revenue,
        "bad_debt_gbp": bad_debt,
        "net_revenue_gbp": revenue - bad_debt if cash_basis else revenue,
        "wholesale_cost_gbp": wholesale,
        "gross_margin_gbp": gross_margin,
        "capital_cost_gbp": capital,
        "cost_to_serve_gbp": cost_to_serve_gbp,
        "acquisition_spend_gbp": acq_spend,
        "fixed_cost_gbp": fixed_cost,
        "total_operating_costs_gbp": operating_costs,
        "net_margin_gbp": net_margin,
    }

    if gross_margin > 0:
        result["net_margin_pct"] = net_margin / gross_margin

    return result


def reconcile_with_sim(
    company_pnl: dict[str, float],
    sim_net_margin: float,
) -> dict[str, Any]:
    """Check whether the company P&L agrees with the simulation's net margin.

    Returns a reconciliation dict noting any gap and its source.
    """
    company_net = company_pnl.get("net_margin_gbp", 0.0)
    gap = company_net - sim_net_margin
    agrees = abs(gap) < 0.01  # within 1p

    return {
        "sim_net_margin_gbp": sim_net_margin,
        "company_net_margin_gbp": company_net,
        "gap_gbp": gap,
        "agrees": agrees,
        "note": (
            "Agreement within £0.01 — company P&L reconciles to simulation."
            if agrees
            else (
                f"Gap of £{gap:+.2f}. "
                "Likely cause: company P&L uses cash-collected revenue while "
                "simulation uses billed revenue. Check revenue_basis."
            )
        ),
    }
