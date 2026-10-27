#!/usr/bin/env python3
"""BILLING_AND_PAYMENTS_LEDGER.md (Phase RP) -- per-account chronological
payment ledger for the customer portal's Statement/Cashflow views.

docs/state/billing_ledger.json (tools/generate_billing_ledger.py) already
carries real invoices, payments (with real payment_date = due_date +
days_late, method, outcome), and arrears_history (dated dunning cascades
from simulation/arrears_engine.py, now including a structured amount_gbp
on the terminal RECOVERED/SOLD stages -- previously that figure only lived
inside a prose note string). This module turns that raw record into a
chronological ledger per account: one entry per invoice/payment/notice/
write-off/recovery, with a running balance, patched onto each customer's
site/data/customers/{cid}.json under a new "ledger" key.

Point-in-time honesty: `as_of` is the latest invoice issue_date anywhere in
the whole ledger (i.e. "today" for this closed historical book). Any arrears
stage dated after `as_of` is withheld -- the ledger only ever shows what has
actually happened by the book's own reference date, never a scheduled-but-
not-yet-occurred escalation. This is what lets some recent invoices still
show a genuinely open balance instead of every account trivially settling
to zero.

Reconciliation identity (holds by construction, every invoice's total ends
up in exactly one bucket): total_billed_gbp == total_collected_gbp +
current_balance_gbp (still open) + total_written_off_gross_gbp. DCA/debt-sale
recovery after a write-off is shown as an informational "recovery_note"
entry (total_recovered_gbp) -- it does not reopen or reduce the ledger
balance a second time, since the write-off already closed that invoice's
line from the customer's own statement perspective.

Output: patches "ledger" onto each existing site/data/customers/{cid}.json
(same read-existing/patch-key pattern as tools/generate_invoice_data.py).
"""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
LEDGER_PATH = PROJECT / "docs" / "state" / "billing_ledger.json"
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"

_NOTE_STAGES = {"DD_FAILED": "payment_failed", "INVOICE_DISPUTED": "invoice_disputed",
                "FIRST_NOTICE": "notice", "SECOND_NOTICE": "notice", "DISPUTE_NOTICE": "notice",
                # The credit invoice already reduced the balance; this says which arrears it met.
                "CREDIT_APPLIED": "credit_applied"}
_RESOLVED_STAGES = {"RESOLVED", "PAYMENT_PLAN_AGREED"}
_TYPE_ORDER = {"invoice_raised": 0, "payment_failed": 1, "invoice_disputed": 1,
               "payment_received": 1, "refund_debit": 3, "scheme_credit": 1, "notice": 2, "credit_applied": 2,
               "arrears_resolved": 3, "write_off": 3, "recovery_note": 4}


def _book_as_of_date(ledger_customers):
    dates = [inv["issue_date"] for cust in ledger_customers.values() for inv in cust.get("invoices", [])]
    return max(dates) if dates else None


def build_account_ledger(cust, as_of):
    """Build the chronological entries + summary totals for one account
    (one entry per docs/state/billing_ledger.json customer record)."""
    invoices = {inv["invoice_number"]: inv for inv in cust.get("invoices", [])}
    payments = {p["invoice_number"]: p for p in cust.get("payments", [])}
    arrears = {a["invoice_number"]: a for a in cust.get("arrears_history", [])}

    entries = []
    for num, inv in invoices.items():
        entries.append({
            "date": inv["issue_date"], "type": "invoice_raised", "invoice_number": num,
            "amount_gbp": round(inv["total_amount_gbp"], 2), "info_amount_gbp": None,
            "method": None, "description": "Invoice INV%d raised" % num,
        })
        arr = arrears.get(num)
        pay = payments.get(num)
        # The government's bill credit (EBSS) the account received for this bill. Not money the
        # household paid, so it lowers the balance without counting as collected. Without it a
        # bill the credit settled whole stood owed for ever, and one it covered in part was paid
        # in full (the 2026-10-27 finding). A ledger from before carried the credit as the amount.
        # The month's WHOLE credit, where the ledger carries it, as the raw export posts it: the
        # payment's share is capped at the bill, and the rest is the account's credit that later
        # bills draw on (`credit_applied_gbp`). Posting only the share left the bills that credit
        # settled standing owed for ever (cold read O27, OCC-f6813bf9f05e: £92.19 of 2023 bills).
        scheme = inv.get("scheme_credit_month_gbp") or (pay and (
            pay.get("scheme_credit_gbp")
            or (pay["amount_gbp"] if pay.get("method") == "scheme_credit" else 0.0)))
        if scheme and inv["issue_date"] <= as_of:
            entries.append({
                "date": inv["issue_date"], "type": "scheme_credit", "invoice_number": num,
                "amount_gbp": round(-scheme, 2), "info_amount_gbp": None,
                "method": None, "description": "Energy Bills Support Scheme credit",
            })
        if arr is None:
            # A bill the account's credit wholly covered asked for nothing, so nothing was received.
            if (pay and pay["outcome"] == "success" and pay["payment_date"] <= as_of
                    and pay["amount_gbp"] > 0):
                entries.append({
                    "date": pay["payment_date"], "type": "payment_received", "invoice_number": num,
                    "amount_gbp": round(-pay["amount_gbp"], 2), "info_amount_gbp": None,
                    "method": pay["method"], "description": "Payment received",
                })
            continue
        method = pay["method"] if pay else None
        if pay and pay.get("part_paid_gbp") and pay["payment_date"] <= as_of:
            entries.append({
                "date": pay["payment_date"], "type": "payment_received", "invoice_number": num,
                "amount_gbp": round(-pay["part_paid_gbp"], 2), "info_amount_gbp": None,
                "method": pay["method"], "description": "Part payment received",
            })
        for stage in arr["stages"]:
            if stage["date"] > as_of:
                break
            name = stage["stage"]
            if name in _NOTE_STAGES:
                entries.append({
                    "date": stage["date"], "type": _NOTE_STAGES[name], "invoice_number": num,
                    "amount_gbp": 0.0, "info_amount_gbp": None, "method": method,
                    "description": stage["note"],
                })
            elif name == "ARREARS_REPAID":
                # The household's own repayment (the world's payment truth): money in.
                entries.append({
                    "date": stage["date"], "type": "payment_received", "invoice_number": num,
                    "amount_gbp": round(-stage["amount_gbp"], 2), "info_amount_gbp": None,
                    "method": None, "description": stage["note"],
                })
            elif name in _RESOLVED_STAGES:
                entries.append({
                    "date": stage["date"], "type": "arrears_resolved", "invoice_number": num,
                    "amount_gbp": round(-arr["arrears_gbp"], 2), "info_amount_gbp": None,
                    "method": "payment_plan", "description": stage["note"],
                })
            elif name == "WRITTEN_OFF":
                entries.append({
                    "date": stage["date"], "type": "write_off", "invoice_number": num,
                    "amount_gbp": round(-arr["arrears_gbp"], 2), "info_amount_gbp": None,
                    "method": None, "description": stage["note"],
                })
            elif name in ("RECOVERED", "SOLD"):
                entries.append({
                    "date": stage["date"], "type": "recovery_note", "invoice_number": num,
                    "amount_gbp": 0.0, "info_amount_gbp": round(stage.get("amount_gbp", 0.0), 2),
                    "method": "dca" if name == "RECOVERED" else "debt_sale",
                    "description": stage["note"],
                })

    # Reg 6D: the credit a leaver's final bill closed in, paid back on the day the company pays it.
    for ref in cust.get("refunds", []):
        if ref["paid_date"] <= as_of:
            entries.append({
                "date": ref["paid_date"], "type": "refund_debit", "invoice_number": 0,
                "amount_gbp": round(ref["amount_gbp"], 2), "info_amount_gbp": None,
                "method": None, "description": "Credit balance refunded on closing the account",
            })

    entries.sort(key=lambda e: (e["date"], e["invoice_number"], _TYPE_ORDER.get(e["type"], 9)))

    running = 0.0
    for e in entries:
        running = round(running + e["amount_gbp"], 2)
        e["running_balance_gbp"] = running

    total_billed = round(sum(inv["total_amount_gbp"] for inv in invoices.values()), 2)
    # Collected is what the supplier kept: a refunded credit was paid in and paid back, so it nets
    # off and billed = collected + scheme credit + balance + written off still foots.
    total_refunded = round(sum(e["amount_gbp"] for e in entries if e["type"] == "refund_debit"), 2)
    total_collected = round(sum(-e["amount_gbp"] for e in entries
                                 if e["type"] in ("payment_received", "arrears_resolved",
                                                  "refund_debit")), 2)
    total_written_off = round(sum(-e["amount_gbp"] for e in entries if e["type"] == "write_off"), 2)
    total_scheme_credit = round(sum(-e["amount_gbp"] for e in entries if e["type"] == "scheme_credit"),
                                2)
    total_recovered = round(sum(e["info_amount_gbp"] or 0.0 for e in entries
                                 if e["type"] == "recovery_note"), 2)
    current_balance = entries[-1]["running_balance_gbp"] if entries else 0.0

    return {
        "as_of_date": as_of,
        "entries": entries,
        "current_balance_gbp": current_balance,
        "total_billed_gbp": total_billed,
        "total_collected_gbp": total_collected,
        "total_written_off_gross_gbp": total_written_off,
        # Billed = collected + scheme credit + balance + written off.
        "total_scheme_credit_gbp": total_scheme_credit,
        "total_refunded_gbp": total_refunded,
        "total_recovered_gbp": total_recovered,
    }


def generate(customers_dir=None, ledger_path=None):
    customers_dir = Path(customers_dir) if customers_dir else CUSTOMERS_DIR
    ledger_path = Path(ledger_path) if ledger_path else LEDGER_PATH

    if not ledger_path.exists():
        print("Skipped: no billing ledger at", str(ledger_path))
        return 0
    ledger = json.loads(ledger_path.read_text())
    ledger_customers = ledger.get("customers", dict())
    as_of = _book_as_of_date(ledger_customers)
    if as_of is None:
        print("Skipped: billing ledger has no invoices")
        return 0

    count = 0
    for cid, cust in ledger_customers.items():
        cust_file = customers_dir / (cid + ".json")
        if not cust_file.exists():
            continue
        existing = json.loads(cust_file.read_text())
        existing["ledger"] = build_account_ledger(cust, as_of)
        cust_file.write_text(json.dumps(existing, indent=2))
        count += 1
    print("Updated", count, "customer ledgers (as of", as_of, ")")
    return count


if __name__ == "__main__":
    generate()
