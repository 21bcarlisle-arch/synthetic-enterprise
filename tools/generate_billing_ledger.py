"""Phase PP -- Per-Customer Invoice & Payment Ledger.

Reads bills and per_customer_behavioral from run_output_latest.json and generates
a per-customer billing ledger with invoice records, payment events, and arrears cases.

Payment outcome driven by income_stress_trajectory from behavioral data:
  LOW    -> 92% on-time, 3% DD failure
  MODERATE -> 50% on-time, 12% DD failure
  HIGH   -> 10% on-time, 35% DD failure

Payment method by segment:
  I&C     -> CHAPS (>10k) or BACS
  SME     -> BACS or DD
  Resi    -> DD (default)

Output: site/state/billing_ledger.json
"""
from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

PROJECT = Path(__file__).parent.parent
RUN_JSON = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_PATH = PROJECT / "site" / "state" / "billing_ledger.json"

PAYMENT_TERMS_DAYS = 14

_DD_FAILURE_PROB = {"LOW": 0.03, "MODERATE": 0.12, "HIGH": 0.35}
_ON_TIME_PROB = {"LOW": 0.92, "MODERATE": 0.50, "HIGH": 0.10}
_LATE_DAYS = {"LOW": (3, 14), "MODERATE": (14, 45), "HIGH": (30, 90)}


def _stress_for_year(behavioral, year):
    trajectory = behavioral.get("income_stress_trajectory") or []
    for entry in trajectory:
        if entry.get("year") == year:
            return (entry.get("stress") or "LOW").upper()
    return "LOW"


def _payment_method(segment, amount_gbp):
    if segment in ("ic", "I&C"):
        return "chaps" if amount_gbp >= 10000 else "bacs"
    if segment == "sme":
        return "bacs"
    return "direct_debit"


def _payment_outcome(method, stress, rng):
    if method in ("bacs", "chaps"):
        return ("success", 0)
    dd_fail_prob = _DD_FAILURE_PROB.get(stress, 0.03)
    if rng.random() < dd_fail_prob:
        return ("failed", 0)
    on_time_prob = _ON_TIME_PROB.get(stress, 0.92)
    if rng.random() < on_time_prob:
        return ("success", 0)
    lo, hi = _LATE_DAYS.get(stress, (3, 14))
    return ("success", rng.randint(lo, hi))


def _arrears_stages(arrears_gbp, due_date, eventually_resolved):
    stages = [
        {"stage": "DD_FAILED", "date": due_date.isoformat(), "note": "Direct debit returned"},
        {"stage": "FIRST_NOTICE", "date": (due_date + timedelta(days=7)).isoformat(),
         "note": "First overdue notice -- GBP%.2f outstanding" % arrears_gbp},
        {"stage": "SECOND_NOTICE", "date": (due_date + timedelta(days=21)).isoformat(),
         "note": "Second notice -- payment plan offered"},
    ]
    if eventually_resolved:
        stages.append({"stage": "RESOLVED", "date": (due_date + timedelta(days=45)).isoformat(),
                        "note": "Arrears cleared via payment plan"})
    else:
        stages.append({"stage": "WRITTEN_OFF", "date": (due_date + timedelta(days=90)).isoformat(),
                        "note": "Debt written off -- bad debt provision raised"})
    return stages


def generate(run_json_path=None, out_path=None):
    if run_json_path is None:
        run_json_path = RUN_JSON
    if out_path is None:
        out_path = OUT_PATH
    data = json.loads(Path(run_json_path).read_text())

    bills = data.get("bills", [])
    behavioral = data.get("per_customer_behavioral", {})
    churned = set(data.get("churned_billing_accounts", []))

    if not bills:
        result = {
            "meta": {"note": "No bill data -- re-run simulation with Phase PP extract_report_data",
                     "invoice_count": 0, "customer_count": 0},
            "customers": {},
        }
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(json.dumps(result, indent=2))
        return result

    rng = random.Random(42)
    invoices_by_cid = {}
    payments_by_cid = {}
    arrears_by_cid = {}
    invoice_number = 1

    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        cid = bill["customer_id"]
        segment = bill.get("segment", "resi")
        amount = bill["total_amount_gbp"]
        period_end = bill["period_end"]
        year = int(period_end[:4])

        issue_date = date.fromisoformat(period_end)
        due_date = issue_date + timedelta(days=PAYMENT_TERMS_DAYS)

        beh = behavioral.get(cid) or {}
        stress = _stress_for_year(beh, year)
        method = _payment_method(segment, amount)
        outcome, days_late = _payment_outcome(method, stress, rng)

        inv = {
            "invoice_number": invoice_number,
            "customer_id": cid,
            "period_start": bill["period_start"],
            "period_end": period_end,
            "commodity": bill.get("commodity", "electricity"),
            "consumption_kwh": round(bill.get("total_consumption_kwh", 0), 1),
            "commodity_amount_gbp": round(bill.get("commodity_amount_gbp", 0), 2),
            "non_commodity_amount_gbp": round(bill.get("non_commodity_amount_gbp", 0), 2),
            "standing_charge_gbp": round(bill.get("standing_charge_gbp", 0), 2),
            "vat_gbp": round(bill.get("vat_gbp", 0), 2),
            "total_amount_gbp": round(amount, 2),
            "issue_date": issue_date.isoformat(),
            "due_date": due_date.isoformat(),
            "payment_status": "paid" if outcome == "success" else "overdue",
        }
        invoices_by_cid.setdefault(cid, []).append(inv)

        payment_date = due_date + timedelta(days=days_late)
        pay = {
            "invoice_number": invoice_number,
            "payment_date": payment_date.isoformat(),
            "amount_gbp": round(amount, 2),
            "method": method,
            "outcome": outcome,
            "income_stress_at_time": stress,
        }
        payments_by_cid.setdefault(cid, []).append(pay)

        if outcome == "failed":
            eventually_resolved = cid not in churned
            arr = {
                "case_id": "ARR-%s-%s" % (cid, period_end),
                "invoice_number": invoice_number,
                "arrears_gbp": round(amount, 2),
                "opened_date": due_date.isoformat(),
                "stages": _arrears_stages(amount, due_date, eventually_resolved),
            }
            arrears_by_cid.setdefault(cid, []).append(arr)

        invoice_number += 1

    customers = {}
    for cid in sorted(invoices_by_cid):
        invs = invoices_by_cid[cid]
        pays = payments_by_cid.get(cid, [])
        arrs = arrears_by_cid.get(cid, [])
        total_billed = sum(i["total_amount_gbp"] for i in invs)
        total_paid = sum(p["amount_gbp"] for p in pays if p["outcome"] == "success")
        failed_count = sum(1 for p in pays if p["outcome"] == "failed")
        customers[cid] = {
            "invoice_count": len(invs),
            "total_billed_gbp": round(total_billed, 2),
            "total_paid_gbp": round(total_paid, 2),
            "balance_gbp": round(total_paid - total_billed, 2),
            "failed_payment_count": failed_count,
            "arrears_case_count": len(arrs),
            "invoices": invs,
            "payments": pays,
            "arrears_history": arrs,
        }

    result = {
        "meta": {
            "source_json": str(run_json_path),
            "invoice_count": invoice_number - 1,
            "customer_count": len(customers),
        },
        "customers": customers,
    }

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    r = generate()
    print("Generated %s (%d invoices, %d customers)" % (OUT_PATH, r["meta"]["invoice_count"], r["meta"]["customer_count"]))
