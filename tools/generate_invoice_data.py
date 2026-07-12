#!/usr/bin/env python3
"""Real per-customer invoice records for the customer portal, sourced from the
actual billed usage -- not a fabrication.

Phase RJ finding: site/state/billing_ledger.json (tools/generate_billing_ledger.py)
already carries the real per-invoice breakdown from the simulation's own bills --
consumption_kwh, commodity_amount_gbp, standing_charge_gbp, non_commodity_amount_gbp,
vat_gbp, total_amount_gbp -- everything CUSTOMER_360_REDESIGN.md v4 item 2 (the bill
equation made visible) needs. This module previously fabricated invoice amounts by
splitting lifetime revenue across months with a hand-picked seasonal weight curve
unrelated to the customer's real consumption; that fabrication is replaced here with
a straight field-mapping from the real ledger. unit_rate_p_per_kwh is a derived
figure (commodity_amount_gbp / consumption_kwh), not an invented one.

Output: patches the invoices key into each existing site/data/customers json file
(same read-existing/patch-key pattern as tools/generate_customer_consumption.py).
"""
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
LEDGER_PATH = PROJECT / "site" / "state" / "billing_ledger.json"
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"

# ADVISOR_STEER_BILL_ARITHMETIC.md Defect 2 (2026-07-11): a written-off invoice
# is labelled WRITTEN_OFF, not silently defaulted to PAID (masking a credit
# loss as if collected) nor left as UNPAID/overdue (double-counting it as
# still-outstanding against a household ledger that has already zeroed it via
# total_written_off_gross_gbp). generate_billing_ledger sets payment_status=
# "written_off" for any invoice whose arrears reached WRITTEN_OFF by the book
# reference date.
_STATUS_MAP = dict(paid="PAID", overdue="UNPAID", disputed="DISPUTED", written_off="WRITTEN_OFF")


def _real_invoice(inv):
    """Map one billing_ledger.json invoice record onto the customer-portal
    invoice schema, adding the derived unit rate the bill equation needs.
    Field names amount_gbp/date/status kept for backward compatibility with
    the existing bill-list rendering.

    BILL_CORRECTNESS_ADDENDUM.md Defect 2 (2026-07-09): meter serial,
    MPAN/MPRN, and read type (A=actual/E=estimated) + opening/closing reads
    carried straight through from the ledger record -- not fabricated here,
    just mapped, same as every other field in this function.
    Defect 3 (2026-07-09): the register/period-structured consumption list
    (single-register today, schema supports N) carried through the same way."""
    kwh = inv.get("consumption_kwh", 0) or 0
    commodity_amt = inv.get("commodity_amount_gbp", 0) or 0
    unit_rate_p_per_kwh = round(commodity_amt / kwh * 100, 2) if kwh else None
    return dict(
        id="%s-INV%d" % (inv["customer_id"], inv["invoice_number"]),
        date=inv["period_end"],
        period_start=inv["period_start"],
        period_end=inv["period_end"],
        commodity=inv["commodity"],
        consumption_kwh=kwh,
        unit_rate_p_per_kwh=unit_rate_p_per_kwh,
        commodity_amount_gbp=round(commodity_amt, 2),
        standing_charge_gbp=round(inv.get("standing_charge_gbp", 0) or 0, 2),
        # Calculation-transparency breakdown (2026-07-10, director page comment:
        # "Days x standing charges... explain the maths properly") -- carried
        # through from the ledger record, same as every other field here.
        days_in_period=inv.get("days_in_period"),
        standing_charge_gbp_per_day=inv.get("standing_charge_gbp_per_day"),
        non_commodity_amount_gbp=round(inv.get("non_commodity_amount_gbp", 0) or 0, 2),
        vat_gbp=round(inv.get("vat_gbp", 0) or 0, 2),
        amount_gbp=round(inv.get("total_amount_gbp", 0) or 0, 2),
        status=_STATUS_MAP.get(inv.get("payment_status"), "PAID"),
        meter_serial=inv.get("meter_serial"),
        mpan=inv.get("mpan"),
        mprn=inv.get("mprn"),
        read_type=inv.get("read_type"),
        opening_read_kwh=inv.get("opening_read_kwh"),
        closing_read_kwh=inv.get("closing_read_kwh"),
        registers=inv.get("registers"),
        # D3 step 2 (docs/design/maturity_map.yaml "Estimated billing &
        # catch-up rebilling cycle"): carried straight through from the
        # ledger record, same as read_type above -- not fabricated here.
        catchup_applied=inv.get("catchup_applied", False),
        catchup_period_start=inv.get("catchup_period_start"),
        catchup_period_end=inv.get("catchup_period_end"),
        catchup_periods_covered=inv.get("catchup_periods_covered"),
        catchup_direction=inv.get("catchup_direction"),
        catchup_raw_delta_gbp=inv.get("catchup_raw_delta_gbp"),
        catchup_adjustment_gbp=inv.get("catchup_adjustment_gbp"),
        catchup_written_off_gbp=inv.get("catchup_written_off_gbp"),
        catchup_back_billing_cap_applied=inv.get("catchup_back_billing_cap_applied"),
    )


def real_invoices_for(cid, ledger_customers):
    entry = ledger_customers.get(cid)
    if not entry:
        return []
    return [_real_invoice(inv) for inv in entry.get("invoices", [])]


def generate(run_json_path=None):
    path = Path(run_json_path) if run_json_path else RUN_OUTPUT

    if not LEDGER_PATH.exists():
        print("Skipped: no billing ledger at", str(LEDGER_PATH))
        return 0
    ledger = json.loads(LEDGER_PATH.read_text())
    ledger_customers = ledger.get("customers", dict())

    run = json.loads(path.read_text())
    pcl = run.get("per_customer_lifetime", dict())
    CUSTOMERS_DIR.mkdir(parents=True, exist_ok=True)
    count = total = 0
    for cid in pcl:
        cust_file = CUSTOMERS_DIR / (cid + ".json")
        existing = json.loads(cust_file.read_text()) if cust_file.exists() else dict(account_id=cid)
        invs = real_invoices_for(cid, ledger_customers)
        existing["invoices"] = invs
        cust_file.write_text(json.dumps(existing, indent=2))
        count += 1
        total += len(invs)
    print("Updated", count, "customers,", total, "invoices (real, from billing_ledger.json)")
    return count


if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv) > 1 else None)
