"""ONE household, walked end to end, with the joins asserted where two parts meet.

Canon: `docs/staging/DIRECTOR_CANON_END_TO_END_AND_ONTOLOGY_2026-08-31.md`, §3 — *"Do the
end-to-end journey walk first. Do not build a concept registry yet… a walk EXERCISES the concepts
where a census only INVENTORIES them."*

WHY ONE HOUSEHOLD AND NOT A SUITE. The canon's own constraint: *"one walk that genuinely asserts
joins is worth more than a suite of walks that assert nothing."* Every defect in its §1 list — the
VAT rule with seven declarations, one name with two ceilings, a standing charge that is the sum of
two fuels — sits *between* two parts, and a walk is the only shape that stands in that gap.

WHAT A JOIN IS, HERE. Two parts that must mean the same thing by the same name: a volume measured
and a volume billed; a rate and a period multiplying to a charge; a tax rate implied by a bill and
the rate the law publishes; a belief and the truth it is a belief about. Each leg below is one
join, and each names the defect it would catch.

WHAT THIS WALK CANNOT REACH, SAID RATHER THAN SKIPPED. The canon's journey begins at *weather*, and
the run artefact carries no per-customer weather or temperature series — demand arrives already
resolved as an EAC. So the walk starts at the meter read. **That is a gap in the evidence, not a
join that holds**, and it is stated here because a walk that quietly omits a stage would report
more coverage than it has. Registered in the walk's own finding.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
RUN = PROJECT / "docs" / "reports" / "run_output_latest.json"

#: The household this walk follows, chosen because it has EVIDENCE FOR EVERY STAGE.
#:
#: The first choice was C1, the oldest account in the book — and the demand leg SKIPPED, because C1
#: sits on the standard variable product and never reaches a renewal decision, so no EAC belief is
#: ever formed about it. A skipped join asserts nothing, and a walk with a silent skip in it reports
#: more coverage than it has: the exact failure this standard exists to close.
#:
#: SYN-2016-009 has 109 bills, 109 reads, 7 demand estimations and a departure — the longest
#: complete chain in the book. Measured across all 43 households that carry every stage, not picked.
HOUSEHOLD = "SYN-2016-009"

#: Pennies. Every money join below is asserted at the precision a bill is actually rendered to;
#: tighter would be asserting float noise, looser would let a real error through.
PENNY = 0.01


@pytest.fixture(scope="module")
def run() -> dict:
    if not RUN.exists():
        pytest.skip(f"no run artefact at {RUN}")
    return json.loads(RUN.read_text())


@pytest.fixture(scope="module")
def journey(run) -> dict:
    """Everything the run knows about ONE household, gathered once."""
    bills = [b for b in run["bills"] if b["customer_id"] == HOUSEHOLD]
    if not bills:
        pytest.skip(f"{HOUSEHOLD} has no bills in this run")
    reads = {(r["customer_id"], r["period_end"]): r for r in run.get("meter_read_log", [])}
    demand = [d for d in run.get("demand_estimation_log", []) if d["customer_id"] == HOUSEHOLD]
    events = [e for e in run.get("customer_events", []) if e.get("customer_id") == HOUSEHOLD]
    return {"bills": bills, "reads": reads, "demand": demand, "events": events,
            "churned": set(run.get("churned_billing_accounts", []))}


def test_JOIN_the_volume_measured_is_the_volume_billed(journey):
    """METER → BILL. A read and a bill for one period must carry one number.

    The defect this catches: a bill charged on a different volume from the one measured — the
    shape every estimated-read dispute in a real supplier is about.

    MUTATION: bill from `estimated_consumption_kwh` while the read says `actual`, and this fires.
    """
    checked = 0
    for bill in journey["bills"]:
        read = journey["reads"].get((HOUSEHOLD, bill["period_end"]))
        if read is None:
            continue
        measured = (read["true_consumption_kwh"] if read["status"] == "actual"
                    else read.get("estimated_consumption_kwh"))
        if measured is None:
            continue
        checked += 1
        assert abs(measured - bill["total_consumption_kwh"]) < 1e-6, (
            f"{bill['period_end']}: the meter read says {measured:.6f} kWh and the bill charged "
            f"{bill['total_consumption_kwh']:.6f} kWh"
        )
    assert checked >= 10, f"only {checked} periods had both a read and a bill — the join is untested"


def test_JOIN_the_parts_of_a_bill_sum_to_its_total(journey):
    """Commodity + non-commodity + standing charge + VAT + any CATCH-UP == total.

    THE CATCH-UP TERM IS HERE BECAUSE THE WALK FOUND IT, and finding it is the point. The first run
    of this leg failed on two of C1's twenty-seven bills, both by about £6.24 — and the code was
    right and the assertion was wrong. An estimated read had over-charged, and the next actual read
    carried `catchup_adjustment_gbp: -6.24` to correct it. A bill's composition is five terms, not
    four, and the fifth only appears on the bills that reconcile an estimate.

    That is exactly what a walk is for and a census is not: the term was there to be inventoried
    all along, and only exercising the join showed it was load-bearing.

    MUTATION: drop any component, add VAT twice, or stop applying the catch-up to the total, and
    this fires.
    """
    with_catchup = 0
    for bill in journey["bills"]:
        parts = (bill["commodity_amount_gbp"] + bill["non_commodity_amount_gbp"]
                 + bill["standing_charge_gbp"] + bill["vat_gbp"]
                 + bill.get("catchup_adjustment_gbp", 0.0))
        if bill.get("catchup_adjustment_gbp"):
            with_catchup += 1
        assert abs(parts - bill["total_amount_gbp"]) < PENNY, (
            f"{bill['period_end']}: the parts sum to {parts:.4f} and the total says "
            f"{bill['total_amount_gbp']:.4f}"
            + (f" (catch-up {bill['catchup_adjustment_gbp']:+.2f} included)"
               if bill.get("catchup_adjustment_gbp") else "")
        )
    assert with_catchup > 0, (
        "no bill in this household's history carries a catch-up adjustment, so the fifth term of "
        "the composition is untested — the join would pass on a book where estimates never "
        "reconcile, which is not the book this project models"
    )


def test_JOIN_the_standing_charge_is_its_daily_rate_times_the_days(journey):
    """A rate and a period must multiply to the charge. The director's third named example lives here.

    MUTATION: bill a monthly standing charge as if it were daily, or use a dual-fuel daily total on
    a single-fuel bill, and this fires.
    """
    for bill in journey["bills"]:
        expected = bill["standing_charge_gbp_per_day"] * bill["days_in_period"]
        assert abs(expected - bill["standing_charge_gbp"]) < PENNY, (
            f"{bill['period_end']}: {bill['standing_charge_gbp_per_day']:.6f}/day x "
            f"{bill['days_in_period']} days = {expected:.4f}, but the bill charged "
            f"{bill['standing_charge_gbp']:.4f}"
        )


def test_JOIN_the_VAT_charged_is_the_rate_the_LAW_publishes(journey):
    """The bill's implied VAT rate against the commons — not against another copy of the rate.

    This is the join that closes the canon's first named defect. One legal rule had seven
    declarations in this repository; here the rate a real bill actually charged is read back out
    and compared to `docs/domain_artefact_library/regulatory/uk_vat_rates.json`, which is the
    published document rather than a fourth implementation of it.

    MUTATION: change the segment's VAT rate in `saas/bill_generator` without changing the commons,
    and this fires — which is exactly the drift that let a July repair sit beside an August defect.
    """
    rates = json.loads(
        (PROJECT / "docs" / "domain_artefact_library" / "regulatory" / "uk_vat_rates.json").read_text()
    )["rates"]
    allowed = {band["rate"] for band in rates.values()}
    # EQUALITY, NOT MEMBERSHIP, and the mutation that survived is why. Replacing this read with a
    # hard-coded set that happened to CONTAIN the right values left the leg green — a superset
    # passes every membership check while having drifted from the document. The set must be
    # exactly what the commons publishes.
    assert allowed == {0.20, 0.05, 0.0}, (
        f"the published VAT bands are now {sorted(allowed)}. If the law changed, this leg changes "
        "with it — but a rate reaching the bills that the commons does not carry is the drift this "
        "join exists to catch."
    )

    for bill in journey["bills"]:
        subtotal = (bill["commodity_amount_gbp"] + bill["non_commodity_amount_gbp"]
                    + bill["standing_charge_gbp"])
        if subtotal <= 0:
            continue
        implied = bill["vat_gbp"] / subtotal
        assert any(abs(implied - rate) < 1e-6 for rate in allowed), (
            f"{bill['period_end']}: the bill implies a VAT rate of {implied:.6f}, which is not any "
            f"rate the published record carries {sorted(allowed)}"
        )
        if bill["segment"] == "resi":
            assert abs(implied - rates["reduced"]["rate"]) < 1e-6, (
                f"{bill['period_end']}: a domestic bill implies {implied:.6f}; fuel and power for "
                f"domestic use is the REDUCED rate ({rates['reduced']['rate']}) unconditionally"
            )


def test_JOIN_the_field_called_average_unit_rate_is_NOT_what_the_household_paid(journey):
    """A name doing two jobs, found by this walk, and pinned so it cannot be read the wrong way.

    `average_unit_rate_gbp_per_mwh` is `commodity_amount / MWh` — the wholesale leg alone. What the
    household actually paid per MWh is the whole bill over the same volume, which on this book runs
    around **1.4x to 2x higher**. Both numbers are correct and only one of them is what a reader of
    the words "average unit rate" would take. It reaches `site/data/customers.json` as
    `avg_rate_gbp_per_mwh`.

    THIS LEG DOES NOT DEMAND A RENAME. The canon asks the walk to distinguish a genuine
    disagreement from a word honestly doing two jobs, and this is the second: a bill legitimately
    has a commodity rate AND an effective rate. What it pins is that they are DIFFERENT and which
    one the field is, so the next reader who needs "what the customer paid" cannot take this field
    and be quietly wrong.

    AND THE CATCH-UP BILLS ARE EXCLUDED FROM THE COMPARISON, WHICH THE WALK ALSO FOUND. Four of
    this household's 109 bills carry a correction for up to TWELVE earlier periods — one totals
    **−£5.78 on 328 kWh consumed**, an effective rate of −17.60/MWh. Nothing is wrong with the
    bill: the money spans thirteen periods and the volume spans one, so their ratio is not a rate
    at all. It is the "two true numbers whose legs are different populations" defect, sitting
    inside a single row, and any surface dividing a bill total by a bill volume inherits it.

    MUTATION: redefine the field as `total_amount / MWh`, or include the catch-up bills in the
    comparison, and this fires.
    """
    checked = skipped_catchup = 0
    for bill in journey["bills"]:
        mwh = bill["total_consumption_kwh"] / 1000.0
        if mwh <= 0:
            continue
        commodity_rate = bill["commodity_amount_gbp"] / mwh
        assert abs(bill["average_unit_rate_gbp_per_mwh"] - commodity_rate) < 0.01, (
            f"{bill['period_end']}: `average_unit_rate_gbp_per_mwh` is no longer the COMMODITY "
            "rate. If it has been redefined as what the household paid, that is a change of "
            "meaning for every reader of the field."
        )
        if bill.get("catchup_adjustment_gbp"):
            skipped_catchup += 1
            continue
        checked += 1
        effective_rate = bill["total_amount_gbp"] / mwh
        assert effective_rate > bill["average_unit_rate_gbp_per_mwh"], (
            f"{bill['period_end']}: the effective rate {effective_rate:.2f}/MWh is not above the "
            f"commodity rate {bill['average_unit_rate_gbp_per_mwh']:.2f}/MWh, which would mean "
            "levies, standing charge and VAT sum to nothing"
        )
    assert checked >= 10
    assert skipped_catchup > 0, (
        "no catch-up bill was excluded, so the period-mismatch this leg documents is untested"
    )


def test_JOIN_the_companys_demand_belief_is_graded_against_the_worlds_truth(journey):
    """BELIEF → TRUTH. The company's EAC and the world's, on one customer, with the gap stated.

    The join is that both legs count the same quantity for the same account: an error percentage
    computed from two different populations is the defect this project has published before.

    MUTATION: compute `error_pct` from a different denominator than `true_eac_kwh`, and this fires.
    """
    if not journey["demand"]:
        pytest.skip(f"{HOUSEHOLD} has no demand estimation rows in this run")
    for row in journey["demand"]:
        true_eac = row["true_eac_kwh"]
        if not true_eac:
            continue
        implied = (row["company_eac_kwh"] - true_eac) / true_eac * 100.0
        assert abs(implied - row["error_pct"]) < 0.05, (
            f"{row['term_start']}: the row reports error_pct={row['error_pct']} but the two EACs "
            f"({row['company_eac_kwh']} believed, {true_eac} true) imply {implied:.2f}"
        )


def test_JOIN_the_end_of_the_journey_agrees_with_itself(journey, run):
    """DEPARTURE. The churned list and the event logs must tell ONE story — over the WHOLE book.

    THE SUBJECT IS EVERY CHURNED ACCOUNT, NOT JUST THIS WALK'S HOUSEHOLD, AND A SURVIVING MUTATION
    IS WHY. Asserted on `SYN-2016-009` alone, removing the `svt_departures` union left the leg
    green — that household departs by renewal, so the union it claims to test was never exercised.
    The join is a whole-book property and checking it over one account was checking the fixture.

    C1 is the case that matters: in `churned_billing_accounts`, **zero** entries in
    `customer_events`, because it drifted off the standard variable product and those departures go
    to `svt_departures`, a second list under a second name. The separation is correct — an SVT
    departure carries no renewal-decision fields — and it means **any reader of one list is wrong
    about the book.** The C2 published reason mix still reads one.

    MUTATION: drop the `svt_departures` union and this fires on every SVT departure in the run.
    """
    renewal = {e["customer_id"] for e in run.get("customer_events", [])
               if e.get("event_type") == "churned"}
    svt = {e["customer_id"] for e in (run.get("svt_departures") or [])}
    listed = set(run.get("churned_billing_accounts", []))
    assert listed, "no departures in this run at all — the join is untested"

    unexplained = sorted(listed - (renewal | svt))
    assert not unexplained, (
        f"{len(unexplained)} account(s) are in `churned_billing_accounts` with no departure event "
        f"in EITHER log: {unexplained[:5]}"
    )
    assert svt, (
        "no SVT departures in this run, so the union this leg exists for is not exercised — a "
        "reader of `customer_events` alone would be right by accident"
    )
    assert HOUSEHOLD in listed or HOUSEHOLD not in (renewal | svt), (
        f"{HOUSEHOLD} has a departure event but is absent from `churned_billing_accounts`"
    )


def test_the_walk_NAMES_the_stage_it_cannot_evidence():
    """The canon's journey starts at weather; this walk starts at the meter read.

    A walk that quietly omitted a stage would report more coverage than it has, which is the
    failure this whole standard exists to close, committed by the instrument built to close it.

    MUTATION: claim weather coverage in the module docstring without a leg asserting it, and this
    fires.
    """
    # THE MODULE DOCSTRING, NOT THE WHOLE FILE, AND A SURVIVING MUTATION IS WHY. Reading the source
    # meant this leg matched the phrase inside its own assertion, so renaming the heading renamed
    # both and the check still passed — a control asserting its own text. `__doc__` cannot contain
    # this assertion.
    import sys as _sys

    doc = _sys.modules[__name__].__doc__ or ""
    assert "WHAT THIS WALK CANNOT REACH" in doc, (
        "the walk's own docstring no longer states which journey stage it has no evidence for"
    )
    assert "weather" in doc.lower()
    asserted_stages = {name for name in globals() if name.startswith("test_JOIN_")}
    assert not any("weather" in name for name in asserted_stages), (
        "a weather join is now asserted — remove the not-reached statement above, because the walk "
        "would then cover the stage it currently says it cannot"
    )
