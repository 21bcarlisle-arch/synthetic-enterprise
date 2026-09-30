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
from datetime import date, timedelta
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

    The adjustment is then credited back to the period it corrects (`catchup_period_start` to
    `catchup_period_end`), pro rata by day (2026-09-30). Removing it without doing that left the
    corrected year short by exactly the amount it was under-billed, and that read as an inversion:
    6 of the 11 on the 2026-09-28 book were catch-ups that landed in the next year. An invoice
    that does not name its period keeps the 2026-08-24 behaviour, which is removal only.
    """
    out = defaultdict(float)
    for cid, cust in ledger.get("customers", {}).items():
        for inv in cust.get("invoices", []):
            year = int(inv["period_end"][:4])
            amount = inv["total_amount_gbp"]
            if net_of_catchup and inv.get("catchup_applied"):
                adjustment = inv.get("catchup_adjustment_gbp") or 0.0
                amount -= adjustment
                start, end = inv.get("catchup_period_start"), inv.get("catchup_period_end")
                if start and end:
                    first, last = date.fromisoformat(start), date.fromisoformat(end)
                    days = (last - first).days + 1
                    for offset in range(days):
                        out[(cid, (first + timedelta(days=offset)).year)] += adjustment / days
            out[(cid, year)] += amount
    return out


def unresolved_account_years(ledger: dict) -> set:
    """(billing account, year) pairs whose billed amount is still provisional.

    A year is provisional when a leg STILL ON SUPPLY at the window's end was billed on an
    estimate that no later actual read resolved. Its true-up falls after the window. The margin is
    on true consumption and the bill is on the estimate, so neither side is final yet.
    PROS-2024-0197 is the case that forced this: live at the end after ten consecutive estimates,
    at 307 kWh a month against 3,000-4,200 true.

    A leg that LEFT is never provisional. It is owed a final read at closure (SLC 21B), so an
    unresolved estimate on a leaver is the defect itself. Keying on "no later actual" alone
    excused 95 account-years, most of them leavers' gas legs that never got that read.
    """
    all_ends = [i["period_end"] for c in ledger.get("customers", {}).values()
                for i in c.get("invoices", [])]
    if not all_ends:
        return set()
    final_month = max(all_ends)[:7]
    out = set()
    for cid, cust in ledger.get("customers", {}).items():
        invoices = sorted(cust.get("invoices", []), key=lambda i: i["period_end"])
        if not invoices or invoices[-1]["period_end"][:7] != final_month:
            continue
        last_actual = max((i["period_end"] for i in invoices if i.get("read_type") == "A"),
                          default="")
        for inv in invoices:
            if inv.get("read_type") == "E" and inv["period_end"] > last_actual:
                out.add((_base_id(cid), int(inv["period_end"][:4])))
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


# THE THREE INVERSIONS STILL OPEN ON THE 2026-09-28 BOOK, each with its cause. They are named
# rather than xfailed so that any OTHER inversion still reds the gate. An entry that stops
# inverting excuses nothing, so it rots harmlessly, but delete it when its cause lands. See
# docs/staging/WORKER_FINDING_A_LEAVING_HOUSEHOLDS_GAS_LEG_READ_AS_A_STAYER_AND_CLOSED_ON_AN_ESTIMATE_2026-09-30.md
KNOWN_OPEN_INVERSIONS = {
    ("PROS-2020-0132", 2021): "gas leg of a leaver closed on an estimate; fixed in code, clears on "
                              "the next published run",
    ("PROS-2016-0092", 2017): "the leaver's final actual bill is held by validate_bills",
    ("PROS-2016-0098", 2020): "the leaver's final actual bill is held by validate_bills",
}


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

    # COMPARED AT THE BILLING ACCOUNT, NOT THE SUPPLY POINT (2026-08-27).
    #
    # A dual-fuel household is ONE billing account with TWO supply points -- the property
    # `tests/simulation/test_dual_fuel_wins.py::test_the_two_legs_are_one_billing_account`
    # asserts, and the whole reason dual fuel reaches cost-to-serve and lifetime value at all.
    # Its INVOICES are cut per billing account; its SETTLEMENT margin accrues per supply point.
    # Comparing one leg's invoices against that same leg's margin therefore compares a part
    # against a differently-cut part, and the remainder shows up as an impossible inversion.
    #
    # MEASURED, which is what promoted this from a plausible story to the fix: after the
    # 2026-08-26 dual-fuel draw, 18 customer-years inverted at supply-point level -- 18 of 611
    # gas-leg years, and 0 of 721 electricity years. Aggregated to the billing account, **all 18
    # go away**. The money was never missing; only its attribution between two legs of one home
    # was, and this control was reading that attribution as a pipeline break.
    #
    # THIS IS NOT A LOOSENING. The billing account is the unit at which billing actually
    # happens, so it is the only unit at which "billed less than the margin inside it" is even a
    # well-formed claim. A genuine break still inverts the household total, and
    # `test_the_gate_still_fires_on_an_inversion_catchup_cannot_explain` proves the netting half
    # has not gone fail-open. The single-fuel case is untouched: for an account with no sibling
    # leg the billing account IS the supply point, which is 703 of the 721 electricity years.
    gross_by_account: dict = {}
    for cid, cust in sample.get("customers", {}).items():
        base_cid = _base_id(cid)
        for row in cust.get("annual_pnl", []):
            key = (base_cid, row["year"])
            gross_by_account[key] = gross_by_account.get(key, 0.0) + row["gross_gbp"]

    billed_by_account: dict = {}
    for (cid, year), total in billed.items():
        key = (_base_id(cid), year)
        billed_by_account[key] = billed_by_account.get(key, 0.0) + total

    # A provisional year is left out, not passed: see `unresolved_account_years`. The control
    # below asks that the exclusion stays a small minority, so it cannot quietly empty the gate.
    provisional = unresolved_account_years(ledger)

    violations = []
    checked = 0
    for account, year in sorted(set(gross_by_account) - provisional):
        gross = gross_by_account[(account, year)]
        total = billed_by_account.get((account, year))
        if total is None:
            continue
        checked += 1
        if total < gross - 0.01 and (account, year) not in KNOWN_OPEN_INVERSIONS:
            violations.append((account, year, round(total, 2), round(gross, 2)))

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


def test_a_catchup_is_credited_back_to_the_period_it_corrects():
    """SYN-2016-055's first catch-up, shape for shape: billed in June 2017 and correcting
    2016-11-01 to 2017-05-31. 61 of its 212 days are in 2016, so that share goes back to 2016. The
    total is conserved, so the re-attribution moves money between years and creates none."""
    ledger = {"customers": {"P": {"invoices": [{
        "period_end": "2017-06-30",
        "total_amount_gbp": 400.0,
        "catchup_applied": True,
        "catchup_adjustment_gbp": 212.0,
        "catchup_period_start": "2016-11-01",
        "catchup_period_end": "2017-05-31",
    }]}}}

    netted = billed_total_by_customer_year(ledger, net_of_catchup=True)

    assert netted[("P", 2016)] == pytest.approx(61.0)
    assert netted[("P", 2017)] == pytest.approx(400.0 - 61.0)
    assert sum(netted.values()) == pytest.approx(400.0)


def _invoice(end, read_type):
    return {"period_end": end, "read_type": read_type, "total_amount_gbp": 10.0}


def test_only_a_leg_still_on_supply_can_hold_a_provisional_year():
    """All three shapes at once, so none of them can be unreachable. LIVE ends in the window's
    final month on an unresolved estimate and is provisional. LEFT ends earlier on the same kind
    of estimate: it was owed a final read, so it stays in the gate. RESOLVED is live, but its
    estimate was followed by an actual read."""
    ledger = {"customers": {
        "LIVE": {"invoices": [_invoice("2025-04-30", "A"), _invoice("2025-05-31", "E")]},
        "LEFTg": {"invoices": [_invoice("2021-03-31", "A"), _invoice("2021-04-18", "E")]},
        "RESOLVED": {"invoices": [_invoice("2025-04-30", "E"), _invoice("2025-05-31", "A")]},
    }}

    assert unresolved_account_years(ledger) == {("LIVE", 2025)}


def test_the_gate_compares_more_years_than_it_leaves_out_on_the_real_book():
    """The exclusion is for the tail of the window. If it ever covers most of the book, the gate
    has been emptied by its own exception."""
    if not LEDGER_PATH.exists() or not SAMPLE_PATH.exists():
        pytest.skip("requires a real generated run")
    ledger = json.loads(LEDGER_PATH.read_text())
    sample = json.loads(SAMPLE_PATH.read_text())
    compared = {(_base_id(c), row["year"]) for c, cust in sample.get("customers", {}).items()
                for row in cust.get("annual_pnl", [])}
    provisional = unresolved_account_years(ledger) & compared

    assert len(compared - provisional) > len(provisional), (
        f"{len(provisional)} of {len(compared)} account-years excused as provisional")


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


def test_the_gate_still_fires_when_a_DUAL_FUEL_HOUSEHOLD_total_inverts():
    """R15 partner for the 2026-08-27 move to billing-account level.

    Aggregating two supply points into one account makes the haystack bigger, and a bigger
    haystack is how a comparison quietly stops discriminating. The move is only legitimate if a
    real break still inverts the HOUSEHOLD -- so here is one: an electricity leg and a gas leg
    that together bill £60 against £500 of combined margin.

    Without this, the repair above would be indistinguishable from switching the control off for
    every dual-fuel customer on the book -- which, after 2026-08-26, is most of them.
    """
    ledger = {"customers": {
        "C99": {"invoices": [{"period_end": "2021-12-31", "total_amount_gbp": 40.0}]},
        "C99g": {"invoices": [{"period_end": "2021-12-31", "total_amount_gbp": 20.0}]},
    }}
    sample = {"customers": {
        "C99": {"annual_pnl": [{"year": 2021, "gross_gbp": 300.0}]},
        "C99g": {"annual_pnl": [{"year": 2021, "gross_gbp": 200.0}]},
    }}
    billed = billed_total_by_customer_year(ledger, net_of_catchup=True)

    gross_by_account: dict = {}
    for cid, cust in sample["customers"].items():
        for row in cust["annual_pnl"]:
            key = (_base_id(cid), row["year"])
            gross_by_account[key] = gross_by_account.get(key, 0.0) + row["gross_gbp"]
    billed_by_account: dict = {}
    for (cid, year), total in billed.items():
        key = (_base_id(cid), year)
        billed_by_account[key] = billed_by_account.get(key, 0.0) + total

    violations = [(a, y) for (a, y), g in gross_by_account.items()
                  if billed_by_account.get((a, y), 0.0) < g - 0.01]
    assert violations == [("C99", 2021)], (
        "a dual-fuel household billing £60 against £500 of margin was not caught -- "
        "aggregating to the billing account has switched the control off")


def test_one_leg_covering_for_the_other_is_NOT_reported_as_a_break():
    """The other direction, and the exact 18 cases this repair was built for: the household
    reconciles, only the split between its two legs does not. That is an attribution question,
    not a pipeline break, and the gate must stay quiet on it."""
    ledger = {"customers": {
        "C98": {"invoices": [{"period_end": "2021-12-31", "total_amount_gbp": 900.0}]},
        "C98g": {"invoices": [{"period_end": "2021-12-31", "total_amount_gbp": 15.0}]},
    }}
    sample = {"customers": {
        "C98": {"annual_pnl": [{"year": 2021, "gross_gbp": 300.0}]},
        "C98g": {"annual_pnl": [{"year": 2021, "gross_gbp": 200.0}]},
    }}
    billed = billed_total_by_customer_year(ledger, net_of_catchup=True)
    # The gas leg alone inverts (15 < 200); the household does not (915 >= 500).
    assert billed[("C98g", 2021)] < sample["customers"]["C98g"]["annual_pnl"][0]["gross_gbp"]
    total = billed[("C98", 2021)] + billed[("C98g", 2021)]
    assert total >= 500.0
