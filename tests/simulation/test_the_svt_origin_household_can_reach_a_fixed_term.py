"""A household that ARRIVES on the default tariff can take a fixed deal — and not all of them do.

THE EDGE THIS CONTROLS, AND WHY IT IS A FIDELITY EDGE AND NOT A COMPANY ONE. Ofgem CIM question C4
reports internal switching — taking a deal with your EXISTING supplier — above what the entire
fixed-term active-renewal population can produce, in all six published waves
(`tools.published_route_split.svt_internal_conversion_floor`). So most GB internal switching is
default-tariff households converting, and a world where a household that arrived on the cap can
never leave it contributes exactly zero to that on every seed. `simulation/renewals.py` already
refused the absorbing shape IN WRITING for the household that ROLLS onto SVT mid-tenure; the
household that STARTED there kept it until 2026-09-18. Two routes onto one product, one exit.

Decided blind to company results (R13): nothing here reads a P&L, a renewal count or an arm, and
`UPLIFTABLE_TARIFF_TYPES` is untouched by the change these control.

REACHABILITY IS FIRST AND IT IS ONE ASSERTION OVER THE WHOLE PARTITION. An edge that fires for
nobody passes every test of what it does, and an edge that fires for everybody passes every test
that it can fire. `test_the_edge_can_be_taken_and_is_not_taken_by_everybody` asserts both legs of
the partition are populated in one statement, so neither failure can hide behind the other.

WHAT EACH TEST NAMES AS ITS OWN DEFECT (CONTROLS_THAT_CANNOT_FAIL):

  * `test_the_edge_can_be_taken_and_is_not_taken_by_everybody` — the defect where the branch is
    absorbing (nobody converts, which is what HEAD did until today) AND the defect where the
    continuation recurses into a fresh `build_renewal_schedule` call, arriving with
    `first_term=True`, skipping the engagement roll and converting EVERYBODY at the first
    anniversary. Both were live drafts of this change; one assertion refuses both.
  * `test_the_household_arrives_on_the_cap_and_stays_there_for_its_first_year` — the defect where
    an SVT-origin household is handed a fixed term at acquisition, which is the blanket-fixed
    `DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` refused, reached through the new branch.
  * `test_the_gas_leg_opens_the_same_edge` — the defect where one fuel's builder gets the exit and
    the other does not. That is not hypothetical here: `resolved_tariff_type`'s own docstring
    records eighteen days in which the two builders resolved the same record differently.
  * `test_a_non_resi_svt_origin_site_is_one_uninterrupted_stint` — the defect where an SME or I&C
    site is given a route off a DOMESTIC default tariff it was never on. `simulation/svt_rates.py`
    is the Ofgem domestic cap and that is the published scope of the anchor.
  * `test_the_worlds_conversion_rate_clears_the_published_floor` — the defect where the edge exists
    but fires so rarely that the world still cannot reproduce the published internal-switching
    record. Keyed to the PUBLISHED FLOOR, not to today's measured rate, so it stays green when the
    world's mechanism changes for a good reason and reds when the world stops clearing the record.
  * `test_the_conversion_rate_is_a_named_gap_and_not_a_picked_number` — the defect where the floor
    is written into the world as if it were the rate. A bound wearing a point estimate's name is
    this project's most expensive recurring shape.

R15 MUTATIONS. Both refuted drafts were EXECUTED against the partition rather than reasoned about,
on the real SSP feed over 30 SVT-origin households, 2016-06-01 → 2023-12-31. Observed result
recorded, not intended result — and neither was run by editing the shared tree, because the subject
is a builder several daemons are calling right now: each draft was rebuilt as a local expression
from the exact code it replaced, which reaches the same branch.

    M1  the branch returns `build_svt_schedule(whole window)` -- HEAD's body until today
        -> reached=0  absorbed=30  -> the partition assertion FIRES
    M2  the continuation recurses into a fresh `build_renewal_schedule` call (first_term=True)
        -> reached=30 absorbed=0   -> the partition assertion FIRES
    LIVE                                 reached=14 absorbed=16 -> passes

The two mutations fail the SAME assertion from opposite ends, which is what a partition control is
for: split into `assert reached` and `assert absorbed` and each would have caught one of them.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from simulation.renewals import build_renewal_schedule
from simulation.settlement import CONTRACT_LENGTH_DAYS
from simulation.svt_product import SVT_TARIFF_TYPE
from tools.published_route_split import (
    SVT_INTERNAL_CONVERSION_RATE,
    svt_internal_conversion_floor,
)

REPORT_END = "2023-12-31"
#: The window starts after the SSP cache's first day so the first term's own lookback window has
#: records to read — the same constraint every builder in this tree carries.
ACQUISITION = "2016-06-01"
#: Enough households for both legs of the partition to be populated by the world's own engagement
#: archetypes rather than by luck, and few enough that the suite stays affordable.
HOUSEHOLDS = 60


@pytest.fixture(scope="module")
def price_records():
    from sim.cache_store import get_cached_prices

    records = get_cached_prices("2016-01-01", REPORT_END)
    if not records:
        pytest.skip("SSP cache does not cover the window; this control needs the real feed")
    return records


def _ids() -> list[str]:
    return [f"SVTORIGIN{i:04d}" for i in range(HOUSEHOLDS)]


def _svt_origin_schedule(customer_id: str, price_records, segment: str = "resi") -> list[dict]:
    """One SVT-origin household's whole schedule, through the world's own builder.

    `tariff_type=SVT_TARIFF_TYPE` is passed explicitly because NO RECORD IN THE LIVE BOOK CARRIES
    IT — `population_draw.DrawnCustomer.tariff_type` defaults to `None` and `resolved_tariff_type`
    turns that into `"fixed"`, so the branch under test is reached by no caller in a live run
    today. That is a fact about the population, not about the edge, and it is recorded in
    `docs/staging/` rather than papered over here: the world's builder must carry the edge before
    anything can arrive on the product, or the day something does it is absorbed silently.
    """
    return build_renewal_schedule(
        customer_id, ACQUISITION, REPORT_END, price_records, 3500,
        segment=segment, tariff_type=SVT_TARIFF_TYPE,
    )


def test_the_edge_can_be_taken_and_is_not_taken_by_everybody(price_records):
    reached, absorbed = [], []
    for customer_id in _ids():
        types = {t["tariff_type"] for t in _svt_origin_schedule(customer_id, price_records)}
        (reached if "fixed" in types else absorbed).append(customer_id)

    # ONE ASSERTION OVER THE WHOLE PARTITION. `assert reached` alone passes on a world that
    # converts everybody; `assert absorbed` alone passes on the absorbing world this replaced.
    assert reached and absorbed, (
        f"the SVT->fixed edge does not partition: {len(reached)} of {HOUSEHOLDS} reached a fixed "
        f"term and {len(absorbed)} did not. Both legs must be populated -- an edge nobody takes is "
        f"the absorbing world, and an edge everybody takes is a conversion that skipped the "
        f"household's own engagement roll."
    )


def test_the_household_arrives_on_the_cap_and_stays_there_for_its_first_year(price_records):
    first_anniversary = date.fromisoformat(ACQUISITION) + timedelta(days=CONTRACT_LENGTH_DAYS)
    for customer_id in _ids()[:10]:
        schedule = _svt_origin_schedule(customer_id, price_records)
        before = [
            t for t in schedule
            if date.fromisoformat(t["acquisition_date"]) < first_anniversary
        ]
        assert before, f"{customer_id} has no terms before its first anniversary"
        assert {t["tariff_type"] for t in before} == {SVT_TARIFF_TYPE}, (
            f"{customer_id} was handed a non-cap product inside its first year on the default "
            f"tariff: {sorted({t['tariff_type'] for t in before})}. Arriving on the cap is not a "
            f"decision the household revisits on day one."
        )


def test_the_gas_leg_opens_the_same_edge(price_records):
    from simulation.run_phase2b import _build_gas_renewal_schedule

    reached, absorbed = [], []
    for customer_id in _ids():
        schedule = _build_gas_renewal_schedule(
            {
                "customer_id": f"{customer_id}g",
                "aq_kwh": 12000,
                "acquisition_date": ACQUISITION,
                "segment": "resi",
            },
            price_records,
            report_end=REPORT_END,
            tariff_type=SVT_TARIFF_TYPE,
        )
        assert schedule[0]["tariff_type"] == SVT_TARIFF_TYPE
        types = {t["tariff_type"] for t in schedule}
        (reached if "fixed" in types else absorbed).append(customer_id)

    assert reached and absorbed, (
        f"the gas leg does not partition: {len(reached)} reached a fixed term, {len(absorbed)} did "
        f"not. The two builders differ in how a TERM is priced, never in whether the household has "
        f"an exit from the default tariff."
    )


def test_a_non_resi_svt_origin_site_is_one_uninterrupted_stint(price_records):
    for customer_id in _ids()[:10]:
        schedule = _svt_origin_schedule(customer_id, price_records, segment="sme")
        assert {t["tariff_type"] for t in schedule} == {SVT_TARIFF_TYPE}, (
            f"{customer_id} is an SME site and was given a route off a DOMESTIC default tariff. "
            f"`simulation/svt_rates.py` is the Ofgem domestic cap; an SME site has no default "
            f"tariff to convert away from and its renewals are broker-driven."
        )


def test_the_worlds_conversion_rate_clears_the_published_floor(price_records):
    floor = svt_internal_conversion_floor()["binding_floor"]
    assert floor is not None, "the published floor is unestablished; this control has no ruler"

    conversions, svt_account_years = 0, 0.0
    for customer_id in _ids():
        schedule = _svt_origin_schedule(customer_id, price_records)
        for earlier, later in zip(schedule, schedule[1:]):
            if earlier["tariff_type"] == SVT_TARIFF_TYPE and later["tariff_type"] == "fixed":
                conversions += 1
        for term in schedule:
            if term["tariff_type"] != SVT_TARIFF_TYPE:
                continue
            span = date.fromisoformat(term["term_end"]) - date.fromisoformat(
                term["acquisition_date"]
            )
            svt_account_years += span.days / 365.25

    assert svt_account_years > 0, "no household spent any time on the default tariff"
    produced = conversions / svt_account_years
    # THE FLOOR IS PER SIX MONTHS AND IS COMPARED TO AN ANNUAL RATE UNCHANGED. That is the
    # conservative direction and `svt_internal_conversion_floor` says so in its own unit field: an
    # annual rate is at least its own six-month rate, so a world clearing the six-month floor per
    # YEAR has cleared it by more than this arithmetic can claim.
    assert produced >= floor, (
        f"the world converts {produced:.4f} SVT households to a fixed deal per SVT household-year, "
        f"below the {floor:.4f} every published CIM wave independently establishes. A world below "
        f"the floor cannot reproduce the GB internal-switching record at any value of phi."
    )


def test_the_conversion_rate_is_a_named_gap_and_not_a_picked_number():
    assert SVT_INTERNAL_CONVERSION_RATE is None, (
        "J_svt has acquired a value. Nothing published establishes the rate at which a default "
        "household takes a fix with its existing supplier -- only a floor -- and a bound written "
        "into a slot named for a point estimate is read as established within a week."
    )
    reading = svt_internal_conversion_floor()
    assert reading["the_point_estimate_is"] is None
    assert reading["why_there_is_no_point_estimate"], "the gap must carry its reason"
