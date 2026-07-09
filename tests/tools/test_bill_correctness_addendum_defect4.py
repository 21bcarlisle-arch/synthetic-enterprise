"""Permanent consistency-gate test for BILL_CORRECTNESS_ADDENDUM.md Defect 4
(2026-07-09): "Portal 2024 bills for C6 total ~£13k; customer_sample.json
annual_pnl records ~£1.5k gross for 2024. Establish which is authoritative
(ledger), define what annual_pnl gross means, reconcile, and add
bills-vs-ledger-vs-sample to the consistency gate."

Root cause (not a bug -- a definitional mismatch that was never made
explicit): customer_sample.json's annual_pnl[year].gross_gbp comes straight
from the SIM's run_output per-customer-year commodity trading margin
(revenue minus wholesale cost -- see tools/generate_customer_sample.py's
_per_year(), cdata["gross_gbp"]). site/state/billing_ledger.json's invoice
total_amount_gbp is the real all-in customer-facing bill: commodity +
standing charge + non-commodity network/environmental pass-through + VAT.
The ledger is authoritative for "what was this customer actually billed" --
annual_pnl's gross_gbp measures a narrower, different thing (trading
margin), and is legitimately smaller because it excludes the pass-through
components AND subtracts wholesale cost. The invariant that must always
hold given those definitions: billed total (ledger) >= gross margin
(sample), never the reverse -- if it ever inverts, something in the
pipeline has genuinely broken, not just diverged as expected.

Also verifies the reconciliation note (site/customers/index.html's Accounts
tab) that explains this distinction inline, so the "wait, these don't
match" confusion the director hit can't recur silently.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
LEDGER_PATH = PROJECT / "site" / "state" / "billing_ledger.json"
SAMPLE_PATH = PROJECT / "site" / "data" / "customer_sample.json"
PORTAL = PROJECT / "site" / "customers" / "index.html"


def billed_total_by_customer_year(ledger: dict) -> dict:
    """(customer_id, year) -> sum of that year's invoice total_amount_gbp,
    from a billing_ledger.json-shaped dict."""
    out = defaultdict(float)
    for cid, cust in ledger.get("customers", {}).items():
        for inv in cust.get("invoices", []):
            year = int(inv["period_end"][:4])
            out[(cid, year)] += inv["total_amount_gbp"]
    return out


def _base_id(cid: str) -> str:
    """Gas companion accounts (e.g. C1g) bill separately but share the same
    underlying household -- matches generate_customer_sample.py's own
    convention."""
    if cid.endswith("g") and len(cid) > 1:
        return cid[:-1]
    return cid


def test_billed_total_helper_sums_by_customer_and_year():
    ledger = {"customers": {"C1": {"invoices": [
        {"period_end": "2020-03-31", "total_amount_gbp": 100.0},
        {"period_end": "2020-06-30", "total_amount_gbp": 150.0},
        {"period_end": "2021-03-31", "total_amount_gbp": 90.0},
    ]}}}
    totals = billed_total_by_customer_year(ledger)
    assert totals[("C1", 2020)] == 250.0
    assert totals[("C1", 2021)] == 90.0


@pytest.mark.skipif(not LEDGER_PATH.exists() or not SAMPLE_PATH.exists(),
                     reason="requires a real generated run (billing_ledger.json + customer_sample.json)")
def test_billed_total_never_less_than_gross_margin_for_any_real_customer_year():
    """The actual gate: sweeps every customer-year in the live data, not
    just C6 -- exactly what the addendum's own DoD asks for ("sweep ALL
    customers")."""
    ledger = json.loads(LEDGER_PATH.read_text())
    sample = json.loads(SAMPLE_PATH.read_text())
    billed = billed_total_by_customer_year(ledger)

    violations = []
    checked = 0
    for cid, cust in sample.get("customers", {}).items():
        base_cid = _base_id(cid)
        for row in cust.get("annual_pnl", []):
            year = row["year"]
            gross = row["gross_gbp"]
            total = billed.get((cid, year), billed.get((base_cid, year)))
            if total is None:
                continue
            checked += 1
            if total < gross - 0.01:
                violations.append((cid, year, total, gross))

    assert checked > 0, "no customer-year pairs matched between the two files -- gate is vacuous"
    assert violations == [], (
        f"{len(violations)} customer-year(s) billed LESS than their own gross "
        f"trading margin, which cannot happen given the definitions -- a real "
        f"pipeline break, not the expected gross-vs-billed gap: {violations[:5]}"
    )


def test_accounts_tab_explains_gross_vs_billed_distinction():
    """The reconciliation note itself must exist on the page, not just hold
    as a data invariant -- Defect 4 asks to "define what annual_pnl gross
    means" where a reader can actually see it."""
    html = PORTAL.read_text()
    assert "commodity trading margin" in html
    assert "Billing &amp; Payments tab" in html
