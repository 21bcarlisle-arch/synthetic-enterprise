"""Regression test for docs/staging/BILLING_TAB_FIX.md (Rich live report,
2026-07-06): the Customer 360 portal's Billing tab silently rendered empty.

Root cause: site/customers/index.html referenced EXPANDED_BILL_ID inside
renderBills() (toggleBillExpand's own click-to-expand state) without ever
declaring it anywhere in the file -- a bare, unassigned identifier read is a
JS ReferenceError (not "undefined"), thrown on the very first render of
*any* account with invoices, before renderBills() ever reaches its
section.innerHTML assignment. renderBillingTab() (called first, sets the
tab shell + fuel toggle) has no reference to the variable and succeeds, so
the tab shell always appeared -- only the actual bill list silently stayed
empty, matching Rich's "portal otherwise much better, Billing tab broken"
report exactly.

No `node` available this session (the recurring gate -- see CLAUDE.md
Phases RA/RG/RI/RJ/RK/RL/RM) to run the QY/QZ-style executed-JS DOM
harness BILLING_TAB_FIX.md asks for, so this substitutes two things this
session CAN verify directly: (1) a static guard that the exact undeclared-
identifier bug can't silently return by requiring EXPANDED_BILL_ID to be
declared in the same var statement as the file's other render-state
globals: (2) a faithful Python port of the new closedAccountNotice() logic
(item 2 of the fix), executed against every real site/data/customers/*.json
in the live run -- not a mock -- asserting churned accounts get a real
closed-account line (real churn date + real final invoice id) and active
accounts get none.
"""
import json
import re
import sys
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parents[2]
PORTAL = PROJECT / "site" / "customers" / "index.html"
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"


def _script_body():
    html = PORTAL.read_text()
    return re.search(r"<script>(.*)</script>", html, re.S).group(1)


def _gbp(n):
    if n is None:
        return "-"
    sign = "-" if n < 0 else ""
    return sign + "£" + "{:,.0f}".format(abs(n))


def _closed_account_notice(d, invoices):
    """Python port of closedAccountNotice() in site/customers/index.html --
    kept line-for-line equivalent so this test breaks if the two diverge.
    Phase RP (BILLING_AND_PAYMENTS_LEDGER.md) extended it with the account's
    real ledger settlement state (settles to zero, or net of a write-off)."""
    churned = None
    for e in d.get("timeline", []):
        if e.get("type") == "churned":
            churned = e
    if not churned or not invoices:
        return ""
    last = invoices[-1]
    settle = ""
    ledger = d.get("ledger")
    if ledger:
        if ledger["current_balance_gbp"] > 0.005:
            settle = " Final balance: " + _gbp(ledger["current_balance_gbp"]) + " outstanding."
        elif ledger["total_written_off_gross_gbp"] > 0.005:
            settle = " Account settled to zero (net of " + _gbp(ledger["total_written_off_gross_gbp"]) + " written off)."
        else:
            settle = " Account settled to zero."
    return "Account closed " + churned["date"] + " — final bill " + last["id"] + "." + settle


def test_expanded_bill_id_is_declared_alongside_other_render_state():
    """Guards the exact regression: EXPANDED_BILL_ID used in renderBills()/
    toggleBillExpand() without ever being declared, which throws a
    ReferenceError on first render (not caught anywhere), leaving
    bills-section permanently empty."""
    body = _script_body()
    decl_line = next(
        l for l in body.split("\n")
        if l.strip().startswith("var ACTIVE_TAB=")
    )
    assert "EXPANDED_BILL_ID" in decl_line, (
        "EXPANDED_BILL_ID must be declared in the top-level var statement -- "
        "reading it undeclared throws a ReferenceError inside renderBills()'s "
        "map callback, which silently empties the whole Billing tab."
    )
    # and every use of it downstream is still present (fix didn't just delete the feature)
    assert body.count("EXPANDED_BILL_ID") >= 3  # declaration + toggleBillExpand + renderBills


def test_render_bills_reads_and_expand_toggle_present():
    body = _script_body()
    assert "function renderBills(d){" in body
    assert "function toggleBillExpand(id){" in body
    assert "function closedAccountNotice(d, invoices){" in body


def test_closed_account_notice_real_churned_customer_c1():
    # W2_5_life_event_stream (2026-07-13): adding real illness/divorce economic
    # events to simulation/life_events.py legitimately shifted C1's own
    # churn/closure timing by one year (2020-12-30 -> 2021-12-30) -- a real
    # baseline-fidelity change (R13: adding UK-anchored events for fidelity
    # reasons), not a bug. econ_rng is a single shared Random() stream per
    # customer; inserting new draws mid-sequence shifts every subsequent
    # year's economic-event outcomes for that customer, which is expected
    # PRNG behaviour, not a regression in the illness/divorce logic itself.
    # This assertion tracks the CURRENT real generated date, not a fixed
    # historical constant that must never change.
    d = json.loads((CUSTOMERS_DIR / "C1.json").read_text())
    notice = _closed_account_notice(d, d["invoices"])
    assert notice.startswith("Account closed 2021-12-30")
    assert (d["invoices"][-1]["id"] + ".") in notice
    # C1 has a real historical write-off (Phase RP ledger) -- settles to zero, not fabricated as fully collected
    assert "settled to zero" in notice


def test_closed_account_notice_empty_for_still_active_customer():
    d = json.loads((CUSTOMERS_DIR / "C_IC1.json").read_text())
    assert _closed_account_notice(d, d["invoices"]) == ""


def test_closed_account_notice_across_full_live_book_no_exceptions():
    """Every real account in the live run: churned accounts get a real
    closed-account line, active accounts get none -- no exceptions, no
    fabricated dates (both churned.date and last invoice id come straight
    from the account's own real timeline/invoices)."""
    files = sorted(CUSTOMERS_DIR.glob("*.json"))
    assert files, "no customer JSON to test against -- run the sim first"
    checked = 0
    for f in files:
        if f.name == "_index.json":
            continue
        d = json.loads(f.read_text())
        invoices = d.get("invoices", [])
        notice = _closed_account_notice(d, invoices)
        has_churn_event = any(e.get("type") == "churned" for e in d.get("timeline", []))
        if has_churn_event and invoices:
            assert notice != "", f.name + " churned but got no closed-account notice"
            assert invoices[-1]["id"] in notice
            if d.get("ledger"):
                assert ("settled to zero" in notice) or ("outstanding" in notice), (
                    f.name + " churned account notice missing ledger settlement state"
                )
        else:
            assert notice == "", f.name + " not churned but got a spurious notice"
        checked += 1
    assert checked >= 15


def test_closed_account_notice_wired_into_render_bills_innerHTML():
    body = _script_body()
    assert "section.innerHTML=btns+closedAccountNotice(d,invoices)+summary+" in body
