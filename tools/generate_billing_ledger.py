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

from simulation.arrears_engine import (
    PAYMENT_TERMS_DAYS,
    stress_for_year as _stress_for_year,
    payment_method as _payment_method,
    payment_outcome as _payment_outcome,
    arrears_stages as _arrears_stages,
    ic_arrears_stages as _ic_arrears_stages,
    debt_archetype as _debt_archetype,
    _CORP_BACS_ON_TIME_PROB,
    _CORP_BACS_LATE_PROB,
    _CORP_BACS_DISPUTE_PROB,
    _CORP_LATE_DAYS,
    _IC_SEGMENTS,
    _DD_FAILURE_PROB,
    _ON_TIME_PROB,
    _LATE_DAYS,
)
from company.billing.pre_bill_validation import validate_bills, exception_queue_as_dicts

PROJECT = Path(__file__).parent.parent
RUN_JSON = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_PATH = PROJECT / "site" / "state" / "billing_ledger.json"


# BILL_CORRECTNESS_ADDENDUM.md Defect 2 (2026-07-09): every bill must state
# meter serial + MPAN/MPRN. Same deterministic-from-account-id scheme as
# company/crm/customer_registry.py's _mpan()/_mprn() (duplicated rather than
# imported -- that module pulls in sqlite3 for its registry DB, which this
# JSON-only pipeline script has no other reason to depend on; kept
# byte-for-byte identical so the two would agree if that registry is ever
# wired into the real run pipeline).
def _mpan(account_id: str) -> str:
    """Synthetic MPAN (Meter Point Administration Number) -- 13 digits."""
    seed = sum(ord(c) for c in account_id)
    return f"1{seed:012d}"[:13]


def _mprn(account_id: str) -> str:
    """Synthetic MPRN (Meter Point Reference Number) -- 10 digits."""
    seed = sum(ord(c) * 17 for c in account_id)
    return f"{seed:010d}"[:10]


def _meter_serial(account_id: str, commodity: str) -> str:
    """Synthetic meter serial number, deterministic per account+commodity
    (an account with both fuels gets two distinct serials, matching two
    physical meters)."""
    seed = sum(ord(c) * 31 for c in account_id + commodity)
    return f"M{seed % 100000000:08d}"

# Phase 3 (CORE_FIDELITY_PHASES.md item 3, unhappy-path audit finding #2):
# "issue_date = period_end -- the bill is issued the same calendar day the
# billing period ends, with no generation or postal delay and zero chance
# of a late bill." Real supplier billing runs process a batch some days
# after period-end before a bill is issued (paperless/portal delivery is
# then near-instant, so the delay is dominated by the internal generation
# run, not post). Provisional distribution pending a dedicated discovery-
# agent anchor (no DESNZ/Ofgem billing-cycle-latency benchmark registered
# yet in docs/market_research/ASSUMPTIONS.md) -- a small mean with an
# occasional longer tail (batch-run slippage / a postal fallback for the
# minority of customers not on paperless billing).
BILL_GENERATION_DELAY_MEAN_DAYS = 3.0


def _bill_generation_delay_days(customer_id: str, period_end: str) -> int:
    delay_rng = random.Random(f"billgen_{customer_id}_{period_end}")
    return max(0, round(delay_rng.expovariate(1.0 / BILL_GENERATION_DELAY_MEAN_DAYS)))


def generate(run_json_path=None, out_path=None):
    if run_json_path is None:
        run_json_path = RUN_JSON
    if out_path is None:
        out_path = OUT_PATH
    data = json.loads(Path(run_json_path).read_text())

    bills = data.get("bills", [])
    behavioral = data.get("per_customer_behavioral", {})
    churned = set(data.get("churned_billing_accounts", []))

    # DOMAIN_SENSE_AND_COMPLIANCE.md Phase 3: Tier-1 pre-bill validation gate
    # (director's Principle 1 -- 100% of bills validated before issue, zero
    # tolerance). A held bill is excluded from this cycle's normal issuance
    # entirely (never sent) and recorded on the exception queue below rather
    # than silently dropped.
    bills, held_bills = validate_bills(bills)

    # BILL_CORRECTNESS_ADDENDUM.md Defect 2: meter-read status (A=actual,
    # E=estimated) per bill, from Phase 3's real estimation physics
    # (simulation/meter_reads.py), keyed the same way the bills themselves
    # are (customer_id, period_end).
    read_by_key: dict[tuple[str, str], dict] = {}
    for read in data.get("meter_read_log", []):
        read_by_key[(read["customer_id"], read["period_end"])] = read

    # Running cumulative meter register value per (customer_id, commodity) --
    # opening read for a bill is the previous bill's closing read (0.0 for
    # the account's first bill on that meter). An estimated period advances
    # the register by the ESTIMATED consumption, not the true value, exactly
    # modelling what the physical meter/estimate would actually show until
    # the next actual read corrects it.
    running_closing_read: dict[tuple[str, str], float] = {}

    if not bills:
        result = {
            "meta": {"note": "No bill data -- re-run simulation with Phase PP extract_report_data",
                     "invoice_count": 0, "customer_count": 0},
            "customers": {},
            "exception_queue": exception_queue_as_dicts(held_bills),
        }
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(json.dumps(result, indent=2))
        return result

    rng = random.Random(42)
    invoices_by_cid = {}
    payments_by_cid = {}
    arrears_by_cid = {}
    segment_by_cid = {}
    invoice_number = 1

    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        cid = bill["customer_id"]
        segment = bill.get("segment", "resi")
        segment_by_cid.setdefault(cid, segment)
        amount = bill["total_amount_gbp"]
        period_end = bill["period_end"]
        commodity = bill.get("commodity", "electricity")
        year = int(period_end[:4])

        generation_delay_days = _bill_generation_delay_days(cid, period_end)
        issue_date = date.fromisoformat(period_end) + timedelta(days=generation_delay_days)
        due_date = issue_date + timedelta(days=PAYMENT_TERMS_DAYS)

        beh = behavioral.get(cid) or {}
        stress = _stress_for_year(beh, year)
        method = _payment_method(segment, amount, cid, commodity)
        outcome, days_late = _payment_outcome(method, stress, rng, segment)

        # Defect 2: meter-read status, opening/closing reads, meter serial,
        # MPAN/MPRN. read_event is None for a bill Phase 3's meter-read
        # simulation doesn't cover (e.g. a run predating that data) --
        # falls back to "actual" at the bill's own consumption figure
        # rather than omitting the fields.
        read_event = read_by_key.get((cid, period_end))
        if read_event is not None and read_event["status"] == "estimated":
            read_type = "E"
            register_consumption_kwh = read_event["estimated_consumption_kwh"]
        else:
            read_type = "A"
            register_consumption_kwh = bill.get("total_consumption_kwh", 0)
        read_key = (cid, commodity)
        opening_read_kwh = running_closing_read.get(read_key, 0.0)
        closing_read_kwh = opening_read_kwh + register_consumption_kwh
        running_closing_read[read_key] = closing_read_kwh

        inv = {
            "invoice_number": invoice_number,
            "customer_id": cid,
            "period_start": bill["period_start"],
            "period_end": period_end,
            "commodity": commodity,
            "consumption_kwh": round(bill.get("total_consumption_kwh", 0), 1),
            "commodity_amount_gbp": round(bill.get("commodity_amount_gbp", 0), 2),
            "non_commodity_amount_gbp": round(bill.get("non_commodity_amount_gbp", 0), 2),
            "standing_charge_gbp": round(bill.get("standing_charge_gbp", 0), 2),
            "vat_gbp": round(bill.get("vat_gbp", 0), 2),
            "total_amount_gbp": round(amount, 2),
            "issue_date": issue_date.isoformat(),
            "generation_delay_days": generation_delay_days,
            "due_date": due_date.isoformat(),
            "payment_status": "disputed" if outcome == "dispute" else ("paid" if outcome == "success" else "overdue"),
            "meter_serial": _meter_serial(cid, commodity),
            "mpan": _mpan(cid) if commodity == "electricity" else None,
            "mprn": _mprn(cid) if commodity == "gas" else None,
            "read_type": read_type,
            "opening_read_kwh": round(opening_read_kwh, 1),
            "closing_read_kwh": round(closing_read_kwh, 1),
        }
        # BILL_CORRECTNESS_ADDENDUM.md Defect 3 (2026-07-09): consumption
        # structured as a list of registers/periods, not one flat line --
        # today every tariff is single-register ("Anytime"), so this is
        # always a one-element list, but the SHAPE supports N so a future
        # ToU tariff (Day/Night/Peak registers) bills correctly without a
        # schema change. Do not build ToU itself here -- just the structure
        # that permits it, per the addendum's own instruction.
        inv["registers"] = [{
            "register_id": "1",
            "label": "Anytime",
            "consumption_kwh": inv["consumption_kwh"],
            "amount_gbp": inv["commodity_amount_gbp"],
        }]
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
            write_off_year = (due_date + timedelta(days=90)).year
            archetype = _debt_archetype(beh.get("income_stress_trajectory") or [], write_off_year)
            arr = {
                "case_id": "ARR-%s-%s" % (cid, period_end),
                "invoice_number": invoice_number,
                "arrears_gbp": round(amount, 2),
                "opened_date": due_date.isoformat(),
                "stages": _arrears_stages(amount, due_date, eventually_resolved, archetype),
            }
            arrears_by_cid.setdefault(cid, []).append(arr)
        elif outcome == "dispute":
            eventually_resolved = cid not in churned
            write_off_year = (due_date + timedelta(days=60)).year
            archetype = _debt_archetype(beh.get("income_stress_trajectory") or [], write_off_year)
            arr = {
                "case_id": "DIS-%s-%s" % (cid, period_end),
                "invoice_number": invoice_number,
                "arrears_gbp": round(amount, 2),
                "opened_date": due_date.isoformat(),
                "stages": _ic_arrears_stages(amount, due_date, eventually_resolved, archetype),
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
        failed_count = sum(1 for p in pays if p["outcome"] in ("failed", "dispute"))
        customers[cid] = {
            "segment": segment_by_cid.get(cid, "resi"),
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
            "held_bill_count": len(held_bills),
        },
        "customers": customers,
        "exception_queue": exception_queue_as_dicts(held_bills),
    }

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    r = generate()
    print("Generated %s (%d invoices, %d customers)" % (OUT_PATH, r["meta"]["invoice_count"], r["meta"]["customer_count"]))
