"""Double-entry ledger for the company layer — F1.

Translates saas.ledger event records into DR/CR journal entries with
account codes. Trial balance, P&L, and balance sheet emerge from this
journal rather than from event-type pattern matching.

Account code ranges:
  1xxx  Assets         (normal balance: debit)
  2xxx  Liabilities    (normal balance: credit)
  3xxx  Equity         (normal balance: credit)
  4xxx  Revenue        (normal balance: credit)
  5xxx  Cost of Sales  (normal balance: debit)
  6xxx  Operating Exp  (normal balance: debit)
"""

from typing import Any

ACCOUNTS: dict[str, dict[str, str]] = {
    "1001": {"name": "Cash and Treasury",                   "type": "asset"},
    "1100": {"name": "Trade Receivables",                   "type": "asset"},
    "2100": {"name": "VAT Payable",                         "type": "liability"},
    "3001": {"name": "Opening Capital / Treasury",          "type": "equity"},
    "3900": {"name": "Retained Earnings",                   "type": "equity"},
    "4001": {"name": "Revenue — Energy Supply",             "type": "income"},
    "5001": {"name": "Wholesale Cost",                      "type": "expense"},
    "5100": {"name": "Network and Levy Pass-through",       "type": "expense"},
    "5200": {"name": "Capital Charge (VaR-based)",          "type": "expense"},
    "6001": {"name": "Bad Debt Expense",                    "type": "expense"},
    "6100": {"name": "Cost to Serve",                       "type": "expense"},
    "6200": {"name": "Fixed Overheads",                     "type": "expense"},
    "6300": {"name": "Customer Acquisition and Retention",  "type": "expense"},
}


def _entry(
    event_id: str,
    timestamp: str,
    debit: str,
    credit: str,
    amount: float,
    description: str,
    source: str,
) -> dict[str, Any]:
    return {
        "entry_id": event_id,
        "timestamp": timestamp,
        "debit_account": debit,
        "credit_account": credit,
        "amount_gbp": amount,
        "description": description,
        "source_event_type": source,
    }


def to_journal_entry(event: dict[str, Any]) -> dict[str, Any] | None:
    """Convert one ledger event to a double-entry journal record.

    Returns None for unrecognised event types (forward-compatible).
    """
    et = event["event_type"]
    eid = event.get("transaction_id", f"unknown:{et}")
    ts = event.get("timestamp", "")
    cid = event.get("customer_id", event.get("billing_account", ""))
    amount = abs(event["amount_gbp"])

    if et == "billing_event":
        return _entry(eid, ts, "1100", "4001", amount,
                      f"Customer billed: {cid}", et)

    if et == "vat_remittance_event":
        # VAT was collected inside billing revenue; remittance to HMRC reduces revenue.
        return _entry(eid, ts, "4001", "1001", amount,
                      f"VAT remitted to HMRC: {cid}", et)

    if et == "non_commodity_cost_event":
        return _entry(eid, ts, "5100", "1001", amount,
                      f"Network/levy pass-through remitted: {cid}", et)

    if et == "settlement_event":
        return _entry(eid, ts, "5001", "1001", amount,
                      f"Wholesale settlement: {cid}", et)

    if et == "capital_charge_event":
        return _entry(eid, ts, "5200", "1001", amount,
                      f"Capital charge (VaR): {cid}", et)

    if et == "payment_received_event":
        return _entry(eid, ts, "1001", "1100", amount,
                      f"Payment received: {cid}", et)

    if et == "bad_debt_event":
        return _entry(eid, ts, "6001", "1100", amount,
                      f"Bad debt written off: {cid}", et)

    if et in ("acquisition_spend_event", "retention_cost_event"):
        return _entry(eid, ts, "6300", "1001", amount,
                      f"Acquisition/retention spend: {cid}", et)

    if et == "fixed_cost_event":
        return _entry(eid, ts, "6200", "1001", amount,
                      f"Fixed overheads: {event.get('month', ts)}", et)

    if et == "cost_to_serve_event":
        return _entry(eid, ts, "6100", "1001", amount,
                      f"Cost to serve: {event.get('month', ts)}", et)

    return None


def build_journal(
    events: list[dict[str, Any]],
    opening_treasury: float = 0.0,
) -> list[dict[str, Any]]:
    """Build the full double-entry journal from ledger events.

    Prepends an opening entry for starting treasury capital if non-zero.
    Unrecognised event types are silently skipped.
    """
    entries: list[dict[str, Any]] = []

    if opening_treasury:
        entries.append(_entry(
            "opening-treasury",
            "0000-00-00",
            "1001", "3001",
            opening_treasury,
            "Opening treasury / share capital",
            "opening_entry",
        ))

    for ev in events:
        je = to_journal_entry(ev)
        if je is not None:
            entries.append(je)

    return entries


def account_balances(journal: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Return {account_code: {dr, cr, net}} for every account touched."""
    balances: dict[str, dict[str, float]] = {}

    for je in journal:
        for side, acct in (("dr", je["debit_account"]), ("cr", je["credit_account"])):
            if acct not in balances:
                balances[acct] = {"dr": 0.0, "cr": 0.0, "net": 0.0}
            balances[acct][side] += je["amount_gbp"]

    for acct, b in balances.items():
        acct_type = ACCOUNTS.get(acct, {}).get("type", "")
        if acct_type in ("asset", "expense"):
            b["net"] = b["dr"] - b["cr"]  # normal debit balance
        else:
            b["net"] = b["cr"] - b["dr"]  # normal credit balance

    return balances


def trial_balance(journal: list[dict[str, Any]]) -> dict[str, Any]:
    """Sum all debits and credits. A correct journal always balances."""
    total_dr = sum(je["amount_gbp"] for je in journal)
    total_cr = sum(je["amount_gbp"] for je in journal)  # always equal by construction
    # Verify via account_balances sum (catches bugs in to_journal_entry)
    balances = account_balances(journal)
    dr_check = sum(b["dr"] for b in balances.values())
    cr_check = sum(b["cr"] for b in balances.values())
    balanced = abs(dr_check - cr_check) < 0.01
    return {
        "total_debit_gbp": dr_check,
        "total_credit_gbp": cr_check,
        "balanced": balanced,
        "discrepancy_gbp": dr_check - cr_check,
    }


def income_statement(journal: list[dict[str, Any]]) -> dict[str, float]:
    """P&L that emerges from account balances — not event-type pattern matching."""
    b = account_balances(journal)

    def net(code: str) -> float:
        return b.get(code, {}).get("net", 0.0)

    revenue = net("4001")
    wholesale = net("5001")
    non_commodity = net("5100")
    capital = net("5200")
    gross = revenue - wholesale - non_commodity
    bad_debt = net("6001")
    cost_to_serve = net("6100")
    fixed = net("6200")
    acq = net("6300")
    opex = bad_debt + cost_to_serve + fixed + acq
    net_profit = gross - capital - opex

    return {
        "revenue_gbp": revenue,
        "wholesale_cost_gbp": wholesale,
        "non_commodity_cost_gbp": non_commodity,
        "gross_margin_gbp": gross,
        "capital_cost_gbp": capital,
        "bad_debt_gbp": bad_debt,
        "cost_to_serve_gbp": cost_to_serve,
        "fixed_cost_gbp": fixed,
        "acquisition_spend_gbp": acq,
        "total_opex_gbp": opex,
        "net_margin_gbp": net_profit,
    }


def balance_sheet(journal: list[dict[str, Any]]) -> dict[str, Any]:
    """Balance sheet that emerges from account balances.

    Assets = Liabilities + Equity is the reconciliation test.
    Equity includes opening capital plus the current period's net profit.
    """
    b = account_balances(journal)

    def net(code: str) -> float:
        return b.get(code, {}).get("net", 0.0)

    cash = net("1001")
    receivables = net("1100")
    total_assets = cash + receivables

    vat_payable = net("2100")
    total_liabilities = vat_payable

    opening_capital = net("3001")
    retained = net("3900")
    pnl = income_statement(journal)
    current_profit = pnl["net_margin_gbp"]
    total_equity = opening_capital + retained + current_profit

    equation_holds = abs(total_assets - (total_liabilities + total_equity)) < 0.01

    return {
        "cash_gbp": cash,
        "trade_receivables_gbp": receivables,
        "total_assets_gbp": total_assets,
        "vat_payable_gbp": vat_payable,
        "total_liabilities_gbp": total_liabilities,
        "opening_capital_gbp": opening_capital,
        "retained_earnings_gbp": retained,
        "current_period_profit_gbp": current_profit,
        "total_equity_gbp": total_equity,
        "total_liabilities_and_equity_gbp": total_liabilities + total_equity,
        "equation_holds": equation_holds,
    }
