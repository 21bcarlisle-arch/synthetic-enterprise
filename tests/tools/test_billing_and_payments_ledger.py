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
import re
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parents[2]
PORTAL = PROJECT / "site" / "customers" / "index.html"
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"


def _script_body():
    html = PORTAL.read_text()
    return re.search(r"<script>(.*)</script>", html, re.S).group(1)


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


def test_tab_renamed_billing_and_payments():
    body = _script_body()
    assert '["billing","Billing & Payments"]' in body


def test_sub_view_functions_present():
    body = _script_body()
    for fn in ["renderStatementView", "renderCashflowShell", "renderCashflow",
               "combinedLedgerTotals", "reconciliationLine", "monthlyLedgerSeries",
               "scopeCtsAndCollected", "setBillView", "setCashScope"]:
        assert "function " + fn in body or "var " + fn in body, fn + " missing"


def test_bill_view_state_declared():
    body = _script_body()
    decl_line = next(
        l for l in body.split("\n")
        if l.strip().startswith("var ACTIVE_TAB=")
    )
    assert "BILL_VIEW" in decl_line
    assert "CASH_SCOPE" in decl_line


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
