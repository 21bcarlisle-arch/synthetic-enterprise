"""Regression tests for docs/staging/BILLING_AND_PAYMENTS_LEDGER.md (Phase RP):
Billing tab renamed to BILLING & PAYMENTS with Bills/Statement/Cashflow
sub-views, sourced from the new "ledger" key tools/generate_payment_ledger_data.py
patches onto site/data/customers/<cid>.json (see tests/tools/test_generate_payment_ledger_data.py
for the generator's own unit tests). This file follows the established
node-unavailable substitute pattern (tests/tools/test_billing_tab_fix.py):
static guards on the raw script text, plus a faithful Python port of the
household-level reconciliation identity, executed against the full live
book -- not a mock."""
import json
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parents[2]
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"

# RENDER-LAYER GUARDS REMOVED 2026-08-22. Their subject, site/customers/index.html, was deleted by
# the director's own ruling in 03dd8c49e (2026-08-20, "eleven pages deleted... customers -> Explore,
# which supersedes it"), and the content did not move: no site/**/*.html now contains renderBills,
# setBillView, combinedLedgerTotals or any other token these asserted on. So the three static
# script-text tests here (tab rename, sub-view functions, BILL_VIEW/CASH_SCOPE declaration) could
# never pass again -- they were not detecting a regression, they were reporting the deletion, once
# per nightly census, for ever. That commit set the precedent by deleting
# tests/tools/test_evidence_reader_ready.py for the same reason; it simply missed this file.
# WHAT IS DELIBERATELY KEPT: everything below that reads site/data/customers/<cid>.json. That data
# layer is LIVE and still generated, so the reconciliation identity across the full book is real
# coverage and is untouched. Only the guards on the dead page are gone.


def _combined_ledger_totals(elec, gas):
    """Python port of combinedLedgerTotals() in site/customers/index.html."""
    e = (elec or {}).get("ledger")
    g = (gas or {}).get("ledger")

    def get(l, k):
        return l[k] if l else 0

    return dict(
        balance=get(e, "current_balance_gbp") + get(g, "current_balance_gbp"),
        billed=get(e, "total_billed_gbp") + get(g, "total_billed_gbp"),
        collected=get(e, "total_collected_gbp") + get(g, "total_collected_gbp"),
        written_off=get(e, "total_written_off_gross_gbp") + get(g, "total_written_off_gross_gbp"),
        recovered=get(e, "total_recovered_gbp") + get(g, "total_recovered_gbp"),
    )


def _households():
    files = [f for f in sorted(CUSTOMERS_DIR.glob("*.json")) if f.name != "_index.json"]
    households = {}
    for f in files:
        d = json.loads(f.read_text())
        base = d.get("base_account_id")
        households.setdefault(base, {})
        if d.get("commodity") == "gas":
            households[base]["gas"] = d
        else:
            households[base]["elec"] = d
    return households


def test_reconciliation_identity_holds_across_full_live_book():
    """Collected + Outstanding + Written off == Billed, for every real
    household in the live run (both fuel legs combined) -- the exact
    identity reconciliationLine() displays and asserts on the page."""
    households = _households()
    assert households, "no customer JSON to test against -- run the sim first"
    checked = 0
    for base, hh in households.items():
        t = _combined_ledger_totals(hh.get("elec"), hh.get("gas"))
        lhs = round(t["collected"] + t["balance"] + t["written_off"], 2)
        assert abs(lhs - round(t["billed"], 2)) < 0.02, (
            base + " reconciliation mismatch: " + str(t) + " lhs=" + str(lhs)
        )
        checked += 1
    assert checked >= 10


def test_at_least_one_household_has_a_real_write_off_and_one_has_open_balance():
    """Evidence ask: a churned account settling via write-off, and a live
    billed-vs-collected divergence (still-open arrears) -- both must be
    real, not fabricated, in the live book."""
    households = _households()
    has_write_off = any(
        _combined_ledger_totals(hh.get("elec"), hh.get("gas"))["written_off"] > 0.005
        for hh in households.values()
    )
    has_open_balance = any(
        _combined_ledger_totals(hh.get("elec"), hh.get("gas"))["balance"] > 0.005
        for hh in households.values()
    )
    assert has_write_off, "expected at least one household with a real lifetime write-off"
    assert has_open_balance, "expected at least one household with a real open/current balance"
