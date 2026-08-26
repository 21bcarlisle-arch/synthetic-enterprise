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
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"

# STATIC SCRIPT-TEXT GUARDS REMOVED 2026-08-22 -- see the same note in
# tests/tools/test_billing_and_payments_ledger.py. site/customers/index.html was deleted by the
# director's ruling in 03dd8c49e (2026-08-20) and renderBills/toggleBillExpand/EXPANDED_BILL_ID
# exist in no site HTML now, so those three guards asserted on a file that cannot come back.
# KEPT: the closed-account-notice tests below, which are a Python PORT of that page's logic run
# against the live book in site/data/customers/. Worth being explicit about why, because it looks
# inconsistent -- the port is now the only place that behaviour is specified, and the data it runs
# on is still generated, so it still fails if the book changes shape. What it no longer claims is
# that any shipped page renders it; that claim died with the page, and the guards that made it are
# what has been removed.


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


def test_closed_account_notice_real_churned_customer_c1():
    """C1's closed-account notice must render the account's OWN generated churn
    date and final bill -- asserted structurally, never as an RNG-derived literal.

    Why no literal (the queued debt this test's own comment named, paid 2026-08-03):
    the churn date is an RNG draw, so any legitimate life-event/world change moves
    it. It moved 2020-12-30 -> 2021-12-30 -> 2020-12-30 -> 2021-12-30 across
    W2_5 / C-S2 / W2_12-W2_14, and on the last move the pinned literal WEDGED the
    publish gate for ~4 days (2026-07-30 01:28Z -> 2026-08-03), blocking every
    publish while the sim itself was healthy. A control that fires on a legitimate
    content change is a defect in the control (R12: the generated value is a
    DIAGNOSTIC, never a target).

    The structural assertions below are strictly STRONGER than the literal was:
    the literal could not tell a fabricated date from a real one (a hardcoded
    default that happened to match would have passed). These cross-check the
    rendered date against an INDEPENDENT part of the record -- the invoice stream
    -- so the port cannot satisfy them by inventing or defaulting a date.
    """
    d = json.loads((CUSTOMERS_DIR / "C1.json").read_text())
    invoices = d["invoices"]
    churn_events = [e for e in d.get("timeline", []) if e.get("type") == "churned"]
    # Fixture must stay meaningful: if C1 stops being a churned account with a
    # write-off, this test is silently testing nothing -- fail loudly instead.
    assert churn_events, (
        "C1 is no longer a churned account -- this test's whole subject is the "
        "closed-account notice. Re-point it at a real churned account with a "
        "write-off rather than deleting the coverage."
    )
    assert invoices, "C1 has no invoices -- closedAccountNotice() cannot be exercised"

    churn_date = churn_events[-1]["date"]
    notice = _closed_account_notice(d, invoices)
    assert notice.startswith("Account closed " + churn_date + " — "), notice

    # INDEPENDENT ORACLE (not the timeline the date came from): the rendered date
    # must be consistent with the account's own billing history -- billing stops at
    # churn. A fabricated or defaulted date fails this even if it parses.
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", churn_date), churn_date
    last_period_end = max(i["period_end"] for i in invoices)
    assert churn_date >= last_period_end, (
        "churn date {} precedes the last billed period end {} -- the notice is "
        "rendering a date the billing history contradicts".format(
            churn_date, last_period_end)
    )
    assert not [i for i in invoices if i["period_start"] > churn_date], (
        "C1 has invoice periods starting after its churn date -- billing did not "
        "stop at churn, so the rendered closed-account date is not real"
    )

    assert (invoices[-1]["id"] + ".") in notice
    # C1 has a real historical write-off (Phase RP ledger) -- settles to zero, not fabricated as fully collected
    assert "settled to zero" in notice


def test_closed_account_notice_date_tracks_the_record_not_a_constant():
    """R15 mutation proof that the structural assertion above can still FAIL.

    The literal it replaced could only ever catch a date CHANGE; this proves the
    replacement catches the thing that actually matters -- a notice whose date is
    not the account's own. Mutating the record's churn date must move the rendered
    date with it; if closedAccountNotice() ever hardcoded or defaulted a date, the
    rendered value would stay put and this fails.
    """
    d = json.loads((CUSTOMERS_DIR / "C1.json").read_text())
    real_date = [e for e in d["timeline"] if e.get("type") == "churned"][-1]["date"]
    assert _closed_account_notice(d, d["invoices"]).startswith(
        "Account closed " + real_date + " — ")

    mutated = json.loads(json.dumps(d))
    sentinel = "1999-01-01"
    for e in mutated["timeline"]:
        if e.get("type") == "churned":
            e["date"] = sentinel
    mutated_notice = _closed_account_notice(mutated, mutated["invoices"])
    assert mutated_notice.startswith("Account closed " + sentinel + " — "), (
        "the rendered date did not follow the record -- closedAccountNotice() is "
        "not reading the account's own churn event")
    assert real_date not in mutated_notice


def test_closed_account_notice_empty_for_still_active_customer():
    """An account with no churn event gets no closed-account line.

    THE ACCOUNT IS DISCOVERED, NOT NAMED (2026-08-26, R10). This read
    `C_IC1.json` by name until the 2026-08-24 segment suspension stopped the
    company serving I&C: the publish that followed regenerated
    `site/data/customers/` without a single I&C account, and this test died on
    `FileNotFoundError` -- not because the behaviour it guards changed, but
    because the fixture it named had left the book. A test that hardcodes one
    account id is a test the next curriculum dial breaks, and the failure looks
    like a billing regression rather than a stale fixture.

    So the account is now SELECTED by the property under test -- the first still
    active one in the live book. The precondition is asserted rather than
    assumed: if the book ever carries no active account at all, this fails
    loudly instead of passing vacuously over an empty loop.
    """
    active = []
    for f in sorted(CUSTOMERS_DIR.glob("*.json")):
        if f.name == "_index.json":
            continue
        d = json.loads(f.read_text())
        if not any(e.get("type") == "churned" for e in d.get("timeline", [])):
            active.append((f.name, d))

    assert active, (
        "the live book carries no still-active account, so this test would pass "
        "without checking anything -- regenerate site/data/customers/"
    )
    for name, d in active:
        assert _closed_account_notice(d, d.get("invoices", [])) == "", (
            name + " is still active but rendered a closed-account notice")


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
