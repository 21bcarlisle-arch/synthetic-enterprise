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


def billed_total_by_customer_year(ledger: dict, *, net_of_catchup: bool = False) -> dict:
    """(customer_id, year) -> sum of that year's invoice total_amount_gbp.

    `net_of_catchup` REMOVES each invoice's `catchup_adjustment_gbp`, and the reason is the
    whole of the 2026-08-24 repair below: a catch-up adjustment is a correction to a DIFFERENT
    period's charges that happens to be settled on this period's invoice. Leaving it in compares
    one year's billing against another year's consumption.
    """
    out = defaultdict(float)
    for cid, cust in ledger.get("customers", {}).items():
        for inv in cust.get("invoices", []):
            year = int(inv["period_end"][:4])
            amount = inv["total_amount_gbp"]
            if net_of_catchup and inv.get("catchup_applied"):
                amount -= inv.get("catchup_adjustment_gbp") or 0.0
            out[(cid, year)] += amount
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
    customers").

    THE ORACLE WAS WRONG, 2026-08-24, and the diagnosis is worth keeping because the failure
    looked exactly like the pipeline break this gate exists to catch. Four customer-years came
    back billed NEGATIVE against a positive gross margin -- PROS-2017-0038 2025 at -100.64,
    PROS-2018-0002 2019 at -169.09, PROS-2018-0003 2020 at -199.43, PROS-2018-0024 2024 at
    -10.92. Every one of them is a CORRECT CATCH-UP CREDIT: the customer was estimated too high
    for nine to twelve months, an actual read arrived, and the true-up credit exceeded that
    month's own charge. `payment_status: credited`, `catchup_direction: overcharge`,
    `catchup_back_billing_cap_applied: false`. That is what a real supplier issues, and
    `D3_catchup_rebilling` is the atom that built it.

    MEASURED before changing anything: of the 90 negative invoices in the live ledger, 90 are
    catch-up-explained. Not one is unaccounted for. So the phenomenon is entirely the credit
    mechanism, not a break.

    All four are the same shape -- a PARTIAL year (one invoice, sometimes a single day) whose
    only invoice carries the prior year's over-estimation credit. The adjustment belongs to the
    prior year's consumption; the gate was comparing it against THIS year's trading margin. That
    is the same DEFINITIONAL MISMATCH this module was created to fix, recurring one level up:
    catch-up rebilling puts a prior-period correction inside a later period's invoice.

    So the comparison is now made NET OF CATCH-UP, which restores like-for-like and keeps the
    control's teeth -- a genuine pipeline break still inverts, and
    `test_the_gate_still_fires_on_an_inversion_catchup_cannot_explain` proves it. What is NOT
    done here is silence the negatives: they are real credits and they stay in the ledger, in the
    bills, and in every total a customer or the treasury sees.
    """
    ledger = json.loads(LEDGER_PATH.read_text())
    sample = json.loads(SAMPLE_PATH.read_text())
    billed = billed_total_by_customer_year(ledger, net_of_catchup=True)

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


# test_accounts_tab_explains_gross_vs_billed_distinction WAS HERE, REMOVED 2026-08-22, AND UNLIKE
# THE OTHER REMOVALS IN THIS SWEEP IT LEAVES A REAL GAP RATHER THAN JUST DEAD WEIGHT.
# It asserted the reconciliation note lived on site/customers/index.html, which 03dd8c49e deleted
# (2026-08-20). The other guards removed today were mirrors of a Python port, so losing them cost
# redundancy; this one was the ONLY check that Defect 4's reader-facing half was satisfied -- the
# addendum asks to "define what annual_pnl gross means" WHERE A READER CAN SEE IT, which is not a
# data invariant and is not covered by the two tests above.
# MEASURED, not assumed: grep over site/**/*.html for "commodity trading margin" and
# "Billing &amp; Payments" returns nothing -- not on /explore/ (the page the ruling names as
# superseding customers), not anywhere. So the explanation was dropped by the consolidation and no
# surviving surface carries it. Re-pointing the test was the preferred fix and was not available.
# The gap is filed at docs/staging/WORKER_FINDING_THE_FIVE_TAB_CONSOLIDATION_DROPPED_DEFECT_4S_READER_FACING_HALF_2026-08-22.md
# rather than left implicit in a deleted test. Restore a check here once the note has a home.


# ── the 2026-08-24 repair, proven both ways ──────────────────────────────────────────────────

def test_netting_catchup_leaves_an_ordinary_year_untouched():
    """The null control. If netting moved every year the repair would be a blanket loosening
    rather than a targeted one, and the gate would be weaker everywhere to fix four rows."""
    ledger = {"customers": {"C1": {"invoices": [
        {"period_end": "2020-03-31", "total_amount_gbp": 100.0},
        {"period_end": "2020-06-30", "total_amount_gbp": 150.0},
    ]}}}

    plain = billed_total_by_customer_year(ledger)
    netted = billed_total_by_customer_year(ledger, net_of_catchup=True)

    assert plain == netted, "netting changed a year that has no catch-up adjustment in it"


def test_netting_removes_a_PRIOR_PERIODS_credit_from_THIS_years_total():
    """The repair itself, on PROS-2018-0002 2019's actual shape: one invoice, one day of
    consumption, carrying eleven months of over-estimation credit."""
    ledger = {"customers": {"P": {"invoices": [{
        "period_end": "2019-01-01",
        "total_amount_gbp": -169.09,
        "catchup_applied": True,
        "catchup_adjustment_gbp": -172.86,
    }]}}}

    assert billed_total_by_customer_year(ledger)[("P", 2019)] == pytest.approx(-169.09)
    assert billed_total_by_customer_year(ledger, net_of_catchup=True)[("P", 2019)] == (
        pytest.approx(3.77)
    ), "the one day's own charge should survive the netting"


def test_the_gate_still_fires_on_an_inversion_catchup_cannot_explain():
    """R15: the repair must not be a fail-open.

    An invoice with NO catch-up on it that still bills less than the year's gross margin is the
    genuine pipeline break this module exists to catch, and netting must leave it exposed. If
    this ever passes, the 2026-08-24 change stopped being a definitional correction and became
    an excuse.
    """
    ledger = {"customers": {"BROKEN": {"invoices": [
        {"period_end": "2021-12-31", "total_amount_gbp": 5.0},
    ]}}}
    sample = {"customers": {"BROKEN": {"annual_pnl": [{"year": 2021, "gross_gbp": 500.0}]}}}

    billed = billed_total_by_customer_year(ledger, net_of_catchup=True)
    violations = [
        (cid, row["year"])
        for cid, cust in sample["customers"].items()
        for row in cust["annual_pnl"]
        if billed.get((cid, row["year"]), 0.0) < row["gross_gbp"] - 0.01
    ]

    assert violations == [("BROKEN", 2021)], (
        "netting catch-up swallowed a real inversion -- the repair is now a fail-open"
    )


def test_EVERY_negative_invoice_in_the_live_ledger_is_catchup_explained():
    """The measurement the repair rests on, kept as a standing check rather than quoted once.

    90 of 90 negative invoices carried `catchup_applied` when this was written. A negative
    invoice that is NOT a catch-up credit is a different animal entirely -- a bill the company
    is paying its customer for no stated reason -- and it must never be able to hide inside a
    class that was cleared on the grounds that every member had an explanation.
    """
    if not LEDGER_PATH.exists():
        pytest.skip("requires a real generated run")
    ledger = json.loads(LEDGER_PATH.read_text())

    unexplained = [
        (cid, inv.get("invoice_number"), inv["total_amount_gbp"])
        for cid, cust in ledger.get("customers", {}).items()
        for inv in cust.get("invoices", [])
        if inv["total_amount_gbp"] < 0 and not inv.get("catchup_applied")
    ]

    assert not unexplained, (
        "a NEGATIVE invoice with no catch-up adjustment behind it -- the company is crediting a "
        f"customer for no recorded reason: {unexplained[:5]}"
    )
