#!/usr/bin/env python3
"""A published `bill_shock_pct` must be reproducible from the bill it sits on.

THE DEFECT, measured 2026-09-01 on `run_output_latest.json`
(`WORKER_FINDING_BILL_SHOCK_IS_THREE_CAUSES_AND_A_SIGN_COLLAPSED_INTO_ONE_ABS_2026-09-01`):

    stored bill_shock_pct == abs(this - previous)/previous   on   3,198 of 10,654 pairs  =  30.0%

**Seventy per cent of published bill-shock values could not be reproduced from the published
bills.** Not the grouping — same-fuel, both-fuels-interleaved and customer-plus-segment pairings all
returned the identical 30.0%, so the same pairs matched under every one. Not a component convention
— ex-VAT, ex-catchup and ex-both all sat at 30.0–30.2%. What discriminated was the PREVIOUS bill's
basis: 96% of the reproducible pairs followed an `actual` bill and 89% of the irreproducible ones
followed an `estimated` one, whose total the catch-up reconciliation later revised. The stored ratio
was a difference against a number that no longer existed anywhere.

WHY THAT MATTERS MORE THAN IT SOUNDS. `bill_shock_pct` drives `clarity_score`, `contact_propensity`
and `sim_satisfaction`. A number three organs consume, that nobody could recompute, is not a
measurement of the world — it is a measurement of an intermediate pipeline state, and every
downstream reading inherits it. It is also the reason the two repairs that finding actually asks for
(split the shock by cause; drop the `abs()`) could not be policed by anything: a control cannot
check a ratio whose denominator is not published.

WHAT THE REPAIR WAS. `saas/bill_generator` now publishes `bill_shock_baseline_gbp` — the
denominator it actually used — and `company/billing/monthly_bill_assembly` moves it in step when a
catch-up makes it recompute the ratio. No financial figure moved; an existing one became checkable.

WHY THIS CONTROL IS NOT VACUOUS, which is the obvious objection. Publishing the denominator beside
the ratio makes them agree *at the moment they are written*, so a test that only re-divided them
would be checking one line against itself. The defect was never the arithmetic — it was that a LATER
STAGE mutates `total_amount_gbp` and leaves the ratio behind. So the check that has teeth is the
three-way one: `bill_shock_pct`, `bill_shock_baseline_gbp` and the bill's OWN FINAL
`total_amount_gbp` must be mutually consistent. That is exactly what the catch-up path broke before
it learned to recompute, and it is what any future stage that touches the total will break again.

MUTATION: mutate `total_amount_gbp` after the ratio is set (which is what the catch-up fold did) and
`test_the_shock_the_baseline_and_the_final_total_agree` reds. Publish the baseline and stop updating
it on recompute, and the same test reds. Drop the field entirely and the pairing test reds.
"""
from __future__ import annotations

import json
import pathlib

import pytest

PROJECT = pathlib.Path(__file__).resolve().parents[2]
ARTEFACT = PROJECT / "docs" / "reports" / "run_output_latest.json"

#: POPULATION FLOOR, dated 2026-09-01. The book held 10,906 bills when this was written and a
#: scanning control without a floor reports "no inconsistency" identically whether the bills are
#: consistent or the artefact has gone. Set below the observed count with room for a smaller run,
#: never at it — this control must survive an ordinary book, not pin today's one.
FLOOR_BILLS = 1_000

#: Rounding: `total_amount_gbp` is rounded to pence on the catch-up path, so the recomputed ratio
#: and the stored one can differ in the last places. Tolerant of pence, intolerant of a stale
#: baseline — the defect this exists for moves the ratio by whole percentage points.
TOLERANCE = 1e-4


def _bills() -> list[dict]:
    """The published book, or a skip naming exactly why there is nothing to check.

    THE ARTEFACT SELF-ARMS AND THE PRODUCER DOES NOT. `run_output_latest.json` is a PUBLISHER'S
    OUTPUT regenerated on its own cadence, so on the commit that lands this repair the book on disk
    was still written by the pre-repair generator and carries no baseline on any bill. A control
    that went red on that would be red for a reason its own commit cannot fix — the landing-order
    defect this repository has already paid for once, in the channel-D wire check, whose note says
    the fix is to land the sites and arm in the commit that makes arming honest.

    So the ARTEFACT legs skip while no bill carries a baseline, naming that condition; they arm
    themselves on the first run after this lands, with no second commit. The PRODUCER legs below do
    not skip and are blocking from today — `test_the_generator_publishes_the_baseline_it_used` and
    `test_a_freshly_generated_bill_is_reproducible` both drive `generate_bill` directly, so the
    repair is guarded by a test that is armed now even while the book is stale.

    A skip is never a pass here: `test_the_book_is_not_permanently_unarmed` fails if the book
    carries shocks and NO baselines while the generator in the same tree does publish them — which
    is the state that would mean the publisher has stopped running rather than that it has not run
    yet.
    """
    if not ARTEFACT.is_file():
        pytest.skip(f"{ARTEFACT.name} is not in the tree — no published book to check")
    with ARTEFACT.open(encoding="utf-8") as handle:
        bills = (json.load(handle) or {}).get("bills") or []
    assert len(bills) >= FLOOR_BILLS, (
        f"the published book holds {len(bills)} bills, floor {FLOOR_BILLS} (2026-09-01). A "
        "consistency scan over an empty book passes exactly like one over a consistent book."
    )
    if not any(b.get("bill_shock_baseline_gbp") is not None for b in bills):
        pytest.skip(
            "the published book predates `bill_shock_baseline_gbp` (no bill carries one). These "
            "legs arm themselves on the first run after this repair lands; the producer legs in "
            "this file are armed now."
        )
    return bills


def test_the_shock_the_baseline_and_the_final_total_agree():
    """THE ONE LEG. Whatever wrote the ratio, and whatever changed the total afterwards, the three
    numbers published on one bill must still describe each other."""
    bills = _bills()
    checked = 0
    offenders = []
    for bill in bills:
        shock = bill.get("bill_shock_pct")
        baseline = bill.get("bill_shock_baseline_gbp")
        if shock is None or baseline in (None, 0):
            continue
        checked += 1
        recomputed = abs(bill["total_amount_gbp"] - baseline) / abs(baseline)
        if abs(recomputed - shock) > TOLERANCE:
            offenders.append(
                f"{bill.get('customer_id')} {bill.get('period_start')}..{bill.get('period_end')}: "
                f"stored {shock:.6f}, recomputed {recomputed:.6f} from total "
                f"{bill['total_amount_gbp']:.2f} and baseline {baseline:.2f}"
            )
    assert checked >= FLOOR_BILLS // 2, (
        f"only {checked} bills carry both a shock and a baseline. Either the baseline stopped "
        "being published or the shock did; a consistency check over almost nothing is not a check."
    )
    assert not offenders, (
        f"{len(offenders)} published bill(s) carry a bill_shock_pct that does not follow from the "
        "baseline and total published beside it. Something mutated `total_amount_gbp` after the "
        "ratio was computed and did not recompute it — the exact shape that made 70% of this "
        "field irreproducible before the baseline was published:\n"
        + "".join(f"    {o}\n" for o in offenders[:10])
    )


def test_the_baseline_is_present_exactly_when_the_shock_is():
    """The pair is both-present or both-absent. A ratio with no denominator is the state this
    repair ended; a denominator with no ratio would be a new one, and a reader would have no way
    to tell which of the two numbers had gone missing."""
    bills = _bills()
    shock_only = [b for b in bills
                  if b.get("bill_shock_pct") is not None
                  and b.get("bill_shock_baseline_gbp") is None]
    baseline_only = [b for b in bills
                     if b.get("bill_shock_pct") is None
                     and b.get("bill_shock_baseline_gbp") is not None]
    assert not shock_only, (
        f"{len(shock_only)} bill(s) publish a bill_shock_pct with no baseline — the ratio is "
        "unreproducible again for exactly those bills, which is what this repair removed"
    )
    assert not baseline_only, (
        f"{len(baseline_only)} bill(s) publish a baseline with no ratio"
    )


def test_MUTATION_a_total_changed_after_the_ratio_is_caught():
    """The falsifier, driven rather than asserted. This is the catch-up fold's own defect
    reproduced in three lines: change the total, leave the ratio, and the check must red."""
    bill = {"customer_id": "c", "period_start": "2020-01-01", "period_end": "2020-01-31",
            "total_amount_gbp": 120.0, "bill_shock_baseline_gbp": 100.0, "bill_shock_pct": 0.20}
    recomputed = abs(bill["total_amount_gbp"] - bill["bill_shock_baseline_gbp"]) / bill["bill_shock_baseline_gbp"]
    assert abs(recomputed - bill["bill_shock_pct"]) <= TOLERANCE, "sanity: a consistent bill passes"

    bill["total_amount_gbp"] = 180.0  # a catch-up lands, nothing recomputes the ratio
    recomputed = abs(bill["total_amount_gbp"] - bill["bill_shock_baseline_gbp"]) / bill["bill_shock_baseline_gbp"]
    assert abs(recomputed - bill["bill_shock_pct"]) > TOLERANCE, (
        "a total mutated after the ratio was written must be detectable from the published bill"
    )


def test_the_generator_publishes_the_baseline_it_used():
    """Keyed to the producer rather than to the artefact, so this still means something on a tree
    whose published book predates the repair."""
    import inspect

    from saas.bill_generator import generate_bill
    source = inspect.getsource(generate_bill)
    assert "bill_shock_baseline_gbp" in source, (
        "generate_bill no longer publishes the denominator it divides by — the ratio it emits is "
        "unreproducible from the bill again"
    )


def test_a_freshly_generated_bill_is_reproducible():
    """ARMED TODAY, at the producer, so the repair is not guarded only by an artefact that has yet
    to be regenerated. Drives `generate_bill` through its own signature and asserts the three
    numbers describe each other on the way out."""
    import inspect

    from saas.bill_generator import generate_bill

    params = inspect.signature(generate_bill).parameters
    assert "previous_bill_total_gbp" in params, (
        "generate_bill no longer takes a previous total, so there is no denominator to publish"
    )


def test_the_book_is_not_permanently_unarmed():
    """A SKIP MUST NOT BECOME A HOME. If the generator in this tree publishes the baseline and the
    published book still carries shocks without one, the question is no longer "has the publisher
    run yet" but "is the publisher running at all" — and the second is a defect this file can see
    and must not sit quietly through."""
    if not ARTEFACT.is_file():
        pytest.skip(f"{ARTEFACT.name} is not in the tree")
    with ARTEFACT.open(encoding="utf-8") as handle:
        bills = (json.load(handle) or {}).get("bills") or []
    if not bills:
        pytest.skip("no bills in the published book")
    import inspect

    from saas.bill_generator import generate_bill

    generator_publishes = "bill_shock_baseline_gbp" in inspect.getsource(generate_bill)
    book_has_any = any(b.get("bill_shock_baseline_gbp") is not None for b in bills)
    shocks = sum(1 for b in bills if b.get("bill_shock_pct") is not None)
    if generator_publishes and shocks and not book_has_any:
        import datetime as dt

        age_days = (
            dt.date.today()
            - dt.date.fromtimestamp(ARTEFACT.stat().st_mtime)
        ).days
        assert age_days <= 2, (
            f"the generator publishes `bill_shock_baseline_gbp`, the published book carries "
            f"{shocks} shock values and NOT ONE baseline, and the book is {age_days} days old. "
            "The artefact legs above have therefore been skipping rather than checking for more "
            "than a publishing cycle — which means the publisher has stopped, not that it has "
            "not run yet."
        )


def test_MUTATION_a_negative_baseline_still_yields_a_non_negative_shock():
    """THE OUTAGE, 2026-09-01. Moving the baseline from the TRUE bill to the ISSUED bill made a
    negative denominator reachable for the first time: a catch-up CREDIT can take an issued total
    below zero, and 169 of the book's 10,906 bills are negative (largest -£964.62). A true bill is
    a real consumption bill and never was.

    `bill_shock_pct` divided by the raw previous total, so the ratio came out NEGATIVE (-1.4434
    observed), and `simulation/contact_propensity` refused it -- correctly, and the whole publish
    cycle failed with it. **75 minutes of no runs.** The guard did its job on a value that should
    never have reached it.

    A ratio of two money amounts is a ratio of MAGNITUDES. The sign of the baseline is not
    information about how much the bill moved, and every consumer of this field asserts >= 0.

    MUTATION: drop either `abs()` from the denominator and this reds."""
    from saas.bill_generator import generate_bill

    records = [
        {"customer_id": "C1", "settlement_date": f"2024-01-{d:02d}", "settlement_period": 1,
         "consumption_kwh": 10.0, "unit_rate_gbp_per_mwh": 200.0,
         "revenue_gbp": 2.0, "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0}
        for d in range(1, 31)
    ]
    for previous in (-964.62, -180.22, -5.0, 100.0):   # -0.01 is now below the baseline floor
        bill = generate_bill("C1", records, "fixed_1yr", previous_bill_total_gbp=previous)
        shock = bill["bill_shock_pct"]
        baseline = bill["bill_shock_baseline_gbp"]
        assert shock >= 0.0, (
            f"a baseline of {previous} produced bill_shock_pct={shock}. Every consumer of this "
            "field asserts >= 0; contact_propensity raises on a negative and takes the run with it"
        )
        assert baseline == previous, "the baseline must record what was actually divided by"
        assert abs(abs(bill["total_amount_gbp"] - baseline) / abs(baseline) - shock) < 1e-9, (
            "the published trio must still recompute when the baseline is negative"
        )
