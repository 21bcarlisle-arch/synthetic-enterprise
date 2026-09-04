"""The book lands on the SVT product the world already chose — and only that book.

C1b. `simulation/renewal_engagement.rolls_active_renewal` has been called at every electricity
renewal since Phase 33 and returns "False if a passive SVT roll". The answer reached
`event["is_active_renewal"]`, was written to the log, and then the world built the household
another fixed term anyway. These are the controls over stopping that, and over the interlock
`simulation/svt_product.py` named: an account that cannot leave is worth more than a real one.

WHAT EACH TEST NAMES AS ITS OWN DEFECT (CONTROLS_THAT_CANNOT_FAIL):

  * `test_a_fixed_term_household_is_never_given_the_inertia_hazard` — THE ONE THE DIRECTION ASKED
    FOR. The defect where the 10-20%/yr drift off a default tariff is applied to a household that
    is on a fixed term and cannot drift off anything. Driven through the real guard with real
    schedule terms, not asserted about the branch condition of the run loop.
  * `test_the_assignment_is_the_worlds_own_roll_and_not_a_second_one` — the defect where the
    schedule builder mints its own coin instead of reading the one the world already flipped, so
    the roster's engagement archetypes and the settled products disagree about the same household.
  * `test_an_always_active_household_never_reaches_the_svt_product` — the defect where assignment
    is keyed to something other than engagement (tenure, index, a hash) and therefore puts
    households on SVT that the world says shopped every year.
  * `test_a_passive_household_leaves_the_fixed_product_and_can_come_back` — the defect where SVT
    is ABSORBING. It is the first draft of this mechanism and the published split refutes it: with
    no route back the domestic fixed share decays to nothing, against a published share that is a
    minority in every year of the window and never vanishes.
  * `test_the_svt_stint_carries_no_notice_and_no_struck_rate` — the defect where the passive
    stint is a fixed term wearing a new label, which is exactly what
    `DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` refused.
  * `test_an_svt_departure_is_not_recorded_as_a_renewal` — the defect where an SVT departure is
    filed with `departure_occasion: "renewal"`, which would put it in the denominator of every
    reader whose subject is renewal DECISIONS (`tools/population_anchor._churn_by_year`) and move
    a published churn rate with no reader able to say which quantity had changed.

R15 MUTATIONS, applied in place and reverted, observed result recorded rather than intended:
  * `inertia_hazard_for_term` drops its `tariff_type` guard (returns the hazard unconditionally)
    -> **1 red**, `..._fixed_term_household_is_never_given_the_inertia_hazard`. Nothing else
    moves, which is the point: without that control the guard could be deleted and every other
    test here would still pass.
  * `build_renewal_schedule` seeds the roll with `customer_id` instead of `household_of(...)`
    -> **1 red**, `..._is_the_worlds_own_roll_and_not_a_second_one` (the two disagree on the gas
    leg and on the founder households whose supply point is not their household id).
  * the passive branch returns `terms + build_svt_schedule(...)` — i.e. SVT becomes absorbing —
    -> **1 red**, `..._leaves_the_fixed_product_and_can_come_back`.
  * `departure_event`'s occasion set to `DEPARTURE_OCCASION_RENEWAL` -> **1 red**,
    `..._not_recorded_as_a_renewal`, and it reds inside `departure_event` itself, which is the
    refusal that constructor already carried.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from simulation.customer_events import (
    DEPARTURE_OCCASION_RENEWAL,
    DEPARTURE_OCCASION_SVT_SEGMENT,
    departure_event,
)
from simulation.departure_risks import CAUSE_SVT_INERTIA
from simulation.household import household_of
from simulation.household_segments import (
    EngagementLevel,
    active_renewal_probability,
    active_renewal_probability_for_customer,
    engagement_level_for_customer,
)
from simulation.renewal_engagement import rolls_active_renewal
from simulation.renewals import NOTICE_DAYS, build_renewal_schedule
from simulation.settlement import CONTRACT_LENGTH_DAYS
from simulation.svt_product import SVT_TARIFF_TYPE, inertia_hazard_for_term

REPORT_END = "2023-12-31"


@pytest.fixture(scope="module")
def price_records():
    from sim.cache_store import get_cached_prices
    from simulation.run_phase2b import EARLIEST_SSP_DATE

    records = get_cached_prices(EARLIEST_SSP_DATE, REPORT_END)
    if not records:
        pytest.skip("SSP cache does not cover the window; this control needs the real feed")
    return records


def _schedule(customer_id: str, acquisition: str, price_records, **kw):
    return build_renewal_schedule(
        customer_id, acquisition, REPORT_END, price_records, 3500,
        segment=kw.pop("segment", "resi"), tariff_type=kw.pop("tariff_type", "fixed"), **kw,
    )


def _a_household_with(level: EngagementLevel) -> str:
    """A real roster household whose engagement archetype is `level`, or skip.

    Drawn from the live roster rather than invented, because the archetype is a hash of the
    household id and a made-up id would be a different population from the one that settles.
    """
    from simulation.run_phase2b import ELEC_CUSTOMERS

    for c in ELEC_CUSTOMERS:
        if c.get("segment", "resi") != "resi":
            continue
        household = household_of(c["customer_id"])
        if engagement_level_for_customer(household) is level:
            return c["customer_id"]
    pytest.skip(f"no {level} household on the live roster")


# ---------------------------------------------------------------------------------------------
# THE HAZARD GOES TO SVT SEGMENTS AND NOWHERE ELSE
# ---------------------------------------------------------------------------------------------

def test_a_fixed_term_household_is_never_given_the_inertia_hazard(price_records):
    """A household on a fixed term cannot drift off a default tariff it is not on.

    THE DEFECT: the published 10-20%/yr SVT inertia rate applied to a fixed-term account. It
    would be invisible in aggregate — the book would simply churn more — and it would corrupt
    the reason mix C2 publishes, because every one of those departures would be labelled
    `svt_inertia` with no SVT anywhere in the household's history.

    Driven with the schedule's own terms so the control fails on the real records rather than on
    a hand-built dict that could drift from what settlement actually reads.
    """
    cid = _a_household_with(EngagementLevel.PASSIVE)
    schedule = _schedule(cid, "2016-01-01", price_records)
    fixed_terms = [t for t in schedule if (t.get("tariff_type") or "") != SVT_TARIFF_TYPE]
    svt_terms = [t for t in schedule if t.get("tariff_type") == SVT_TARIFF_TYPE]
    assert fixed_terms, "no fixed terms in the schedule; this control has lost its subject"
    assert svt_terms, (
        "no SVT segments either, so a hazard of 0.0 everywhere would satisfy the assertion below "
        "by having nothing to distinguish -- the control would go quiet rather than loud")

    for term in fixed_terms:
        # `stint_start=None` is the WORST case the caller can supply: unknown tenure resolves to
        # the RECENT band, the higher of the two. If the guard leaks at all it leaks here.
        assert inertia_hazard_for_term(term, stint_start=None) == 0.0, (
            f"a {term.get('tariff_type')!r} term starting {term['acquisition_date']} was given "
            f"the SVT inertia hazard; it has no default tariff to drift off")

    assert any(inertia_hazard_for_term(t, stint_start=None) > 0.0 for t in svt_terms), (
        "no SVT segment carries a hazard either, so the guard above is indistinguishable from a "
        "function that returns 0.0 for everything")


def test_the_long_stayer_band_needs_a_stint_and_not_a_tenure(price_records):
    """`stint_start` is continuous tenure on SVT; an unknown one takes the HIGHER hazard."""
    cid = _a_household_with(EngagementLevel.DISENGAGED)
    schedule = _schedule(cid, "2016-01-01", price_records)
    svt = [t for t in schedule if t.get("tariff_type") == SVT_TARIFF_TYPE]
    assert svt, "no SVT segments; this control has lost its subject"
    term = svt[-1]
    long_stayer = inertia_hazard_for_term(term, stint_start="2016-01-01")
    unknown = inertia_hazard_for_term(term, stint_start=None)
    assert long_stayer < unknown, (
        "an unknown stint must fail toward the account being MORE likely to leave, never less: "
        f"unknown={unknown:.5f} long_stayer={long_stayer:.5f}")


# ---------------------------------------------------------------------------------------------
# THE ASSIGNMENT IS THE WORLD'S OWN DECISION, READ RATHER THAN RE-MADE
# ---------------------------------------------------------------------------------------------

def test_the_assignment_is_the_worlds_own_roll_and_not_a_second_one(price_records):
    """Every product boundary in the schedule is what `rolls_active_renewal` already said.

    THE DEFECT: the builder mints its own coin. The world would then hold two answers for the
    same household at the same renewal -- one in `event["is_active_renewal"]`, one in the settled
    product -- and every reader that joins them would silently be joining two populations.

    Replayed here from the same function, the same seed grammar and the same per-household
    engagement probability, over the whole schedule.
    """
    cid = _a_household_with(EngagementLevel.PASSIVE)
    household = household_of(cid)
    p_active = active_renewal_probability_for_customer(household)
    schedule = _schedule(cid, "2016-01-01", price_records)

    checked = 0
    for index, term in enumerate(schedule):
        if index == 0:
            continue
        product = term.get("tariff_type") or "fixed"
        previous = schedule[index - 1].get("tariff_type") or "fixed"
        if product == previous:
            continue  # not a boundary the roll decides -- a later cap period in the same stint
        if product == SVT_TARIFF_TYPE:
            expected_active = False
        elif previous == SVT_TARIFF_TYPE:
            continue  # the return to a fixed deal is decided at the anniversary, tested below
        else:
            continue
        assert rolls_active_renewal(
            term["acquisition_date"], f"{household}_{index}", p_active) is expected_active, (
            f"{cid} moved to {product} at {term['acquisition_date']} but the world's own roll "
            f"for that boundary says active={not expected_active}")
        checked += 1
    assert checked, "no product boundary in this schedule; the control has lost its subject"


def test_an_always_active_household_never_reaches_the_svt_product(price_records):
    """p_active = 1.0 shops at every renewal, so it is never put on the default tariff.

    THE DEFECT: assignment keyed to something other than engagement -- a tenure, a term index, a
    hash of the customer id. Such a rule would put households on SVT that the world says shopped
    every single year, and the engagement archetype would stop being the thing that decides.

    THE FTC WITHDRAWAL WINDOW IS EXCLUDED FROM THE ASSERTION AND THAT IS THE POINT, NOT A
    LOOPHOLE: `FTC_WITHDRAWAL_WINDOW` forces every renewal inside it passive because fixed deals
    were withdrawn, so even a p=1.0 household rolls onto SVT there. The published record does the
    same thing -- domestic fixed share fell to 10-20% -- and a control that demanded otherwise
    would be asserting the world stay wrong.

    KEYED TO THE PREDICATE, NOT TO A YEAR SET. This read `stint_start[:4] not in
    CRISIS_PASSIVE_YEARS` until 2026-09-04, when the window gained a partial year (H1 2023). A
    year-string test would have called that half-year's forced stints a defect -- the exclusion
    has to follow the window's own dates or it goes red for the world becoming more faithful.
    """
    from simulation.renewal_engagement import ftc_withdrawn_at

    cid = _a_household_with(EngagementLevel.ACTIVE)

    from simulation import renewals as renewals_module

    original = renewals_module.active_renewal_probability_for_customer
    renewals_module.active_renewal_probability_for_customer = lambda _h: 1.0
    try:
        schedule = _schedule(cid, "2016-01-01", price_records)
    finally:
        renewals_module.active_renewal_probability_for_customer = original

    # Keyed to the STINT's first day, not the segment's. A crisis stint begins on the account's
    # own anniversary, which drifts (365-day terms), so it can begin in late 2022 and emit cap
    # segments dated 2023 -- selecting on the segment date would have called those a defect.
    off_crisis_svt, stint_start = [], None
    previous = "fixed"
    for term in schedule:
        product = term.get("tariff_type") or "fixed"
        if product == SVT_TARIFF_TYPE:
            if previous != SVT_TARIFF_TYPE:
                stint_start = term["acquisition_date"]
            if not ftc_withdrawn_at(stint_start):
                off_crisis_svt.append(term)
        previous = product
    assert not off_crisis_svt, (
        "a household that shops at every renewal was put on the standard variable product "
        f"outside the crisis year: {[t['acquisition_date'] for t in off_crisis_svt][:5]}")
    assert len(schedule) > 1, "single-term schedule; the control has lost its subject"


def test_a_passive_household_leaves_the_fixed_product_and_can_come_back(price_records):
    """SVT is not absorbing: a stint ends at the anniversary and the household may re-fix.

    THE DEFECT, and it was the first draft: once on SVT, always on SVT. It reads as the more
    conservative choice and the published split refutes it. With no route back the generated
    domestic fixed share decays to 12% by the second renewal and to nothing after the 2022 crisis
    forcing, against a published share that is a minority in every year of the window -- 10-46% --
    and is ~33% in 2025. `tools/svt_generated_share_check.py` prints the measurement.
    """
    cid = _a_household_with(EngagementLevel.PASSIVE)
    schedule = _schedule(cid, "2016-01-01", price_records)
    products = [t.get("tariff_type") or "fixed" for t in schedule]
    assert SVT_TARIFF_TYPE in products, (
        f"{cid} is a passive household and never reached SVT in ten years; the assignment is "
        "not reading the roll")
    returned = any(
        products[i] == SVT_TARIFF_TYPE and products[i + 1] == "fixed"
        for i in range(len(products) - 1)
    )
    assert returned, (
        "this household never took a fixed deal again after rolling onto SVT, so the product is "
        "absorbing -- see the docstring for what the published split says about that")


def test_the_svt_stint_carries_no_notice_and_no_struck_rate(price_records):
    """A passive stint is the SVT product, not a fixed term wearing a new `tariff_type`."""
    cid = _a_household_with(EngagementLevel.DISENGAGED)
    schedule = _schedule(cid, "2016-01-01", price_records)
    svt = [t for t in schedule if t.get("tariff_type") == SVT_TARIFF_TYPE]
    assert svt, "no SVT segments; the control has lost its subject"
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

    for term in svt:
        assert term["notice_date"] == term["acquisition_date"], (
            "a notice date on a product that never ends -- the 42-day statutory notice is an "
            "artefact of a contract expiring")
        assert term["unit_rate_gbp_per_mwh"] == get_svt_elec_rate_gbp_per_mwh(
            term["acquisition_date"]), (
            "the rate was struck rather than read off the published cap; no supplier prices a "
            "capped default tariff, it is handed the number")
        length = (date.fromisoformat(term["term_end"])
                  - date.fromisoformat(term["acquisition_date"])).days
        assert length <= CONTRACT_LENGTH_DAYS - NOTICE_DAYS, (
            f"a {length}-day 'cap period' is a contract year in disguise")


# ---------------------------------------------------------------------------------------------
# THE DEPARTURE IS NOT A RENEWAL
# ---------------------------------------------------------------------------------------------

def test_an_svt_departure_is_not_recorded_as_a_renewal():
    """The occasion is the segment. A renewal-occasion SVT churn would move a published rate.

    `tools/population_anchor._churn_by_year` divides churns by `renewals + churns`. An SVT
    departure filed as a renewal would add to both sides of that ratio at once, and no reader
    could tell the resulting move from a change in the world's departure level.
    """
    event = departure_event(
        customer_id="C1", event_date="2020-04-01", commodity="electricity",
        occasion=DEPARTURE_OCCASION_SVT_SEGMENT, cause=CAUSE_SVT_INERTIA,
    )
    assert event["departure_occasion"] == DEPARTURE_OCCASION_SVT_SEGMENT
    assert event["departure_occasion"] != DEPARTURE_OCCASION_RENEWAL
    assert event["departure_cause"] == CAUSE_SVT_INERTIA
    assert event["event_type"] == "churned"

    with pytest.raises(ValueError, match="roll_lifecycle_event"):
        departure_event(
            customer_id="C1", event_date="2020-04-01", commodity="electricity",
            occasion=DEPARTURE_OCCASION_RENEWAL, cause=CAUSE_SVT_INERTIA,
        )


def test_the_year_level_anchor_does_not_scale_the_published_inertia_rate():
    """The one hazard that arrives with units is not multiplied by the fit that gives the others units.

    THE DEFECT, AND IT WAS LIVE UNTIL THE FIRST ASSIGNMENT RUN PRINTED IT. `level_anchor` is a
    per-year table running 1.524 to 4.597, fitted so the response risks reach the published
    departure level. `svt_inertia` is already a published ANNUAL RATE converted to the segment's
    length. Scaling it delivered the 10-20%/yr band to the roll as 15-92%/yr, and one cap quarter
    came out of the run log at a hazard of 0.2532 against 0.0547 unscaled.

    `test_departure_risks.py`'s own anchor control cannot see this: it drives
    `build_departure_risks` with the `svt_inertia=0.0` default, and zero times any anchor is
    zero. A fixture sitting at the fallback value cannot see a mispricing of the thing the
    fallback stands in for, which is why this control is here rather than a parameter added there.
    """
    from simulation.departure_risks import (
        DECLARED_SENSITIVITY_SCALE,
        build_departure_risks,
    )

    inputs = dict(
        bill_shock_base=0.05, price_response=1.0, dissatisfaction_response=1.0,
        sensitivity_scale=DECLARED_SENSITIVITY_SCALE, svt_inertia=0.05,
    )
    at_one = build_departure_risks(level_anchor=1.0, **inputs)
    at_four = build_departure_risks(level_anchor=4.0, **inputs)

    assert at_four[CAUSE_SVT_INERTIA] == at_one[CAUSE_SVT_INERTIA], (
        "the year level anchor is scaling the published SVT inertia rate; it is a calibration of "
        "the dimensionless response risks onto the published departure level, and applying it to "
        "a rate that already has units multiplies the anchor by itself")
    assert at_four["bill_shock"] > at_one["bill_shock"], (
        "the anchor no longer scales the response risks either, so the assertion above passes "
        "for the wrong reason -- it would hold for an anchor that had stopped working entirely")


def test_the_engagement_probabilities_the_assignment_reads_are_the_anchored_ones():
    """The assignment mints no rate of its own — it reads the Ofgem-anchored archetype table.

    THE DEFECT: a second population rate introduced beside `PASSIVE_RENEWAL_RATE`, so the world
    would hold two answers for how many households shop and only one of them would be cited.
    """
    from simulation.renewal_engagement import PASSIVE_RENEWAL_RATE

    for level in EngagementLevel:
        assert 0.0 <= active_renewal_probability(level) <= 1.0
    assert PASSIVE_RENEWAL_RATE == 0.35, (
        "the anchored population-wide active-renewal rate moved; the assignment reads it and "
        "every generated fixed/SVT share moves with it")


def test_no_household_can_reach_a_renewal_decision_in_a_crisis_year(price_records):
    """A CRISIS YEAR'S EMPTY RENEWAL POPULATION IS STRUCTURAL, AND NOTHING SAID SO IN CODE.

    THE DEFECT THIS EXISTS FOR, and it cost a Lane 0 direction. `departure_level_anchor`'s
    `UNFITTED_YEARS[2022]` cause said the empty renewal population was CAPTURE-SCOPED and named a
    committed artefact as proof — *"`c3_shown_price_departure_factors.json` carries 53 renewal rows
    in 2022 under the retired ten-year block, so a re-capture CAN close this one"*. It cannot. The
    forcing in `rolls_active_renewal` is unconditional in a crisis year and the divert in
    `build_renewal_schedule` is unconditional on a passive roll, so their COMPOSITION is that no
    fixed term can start in such a year — at any seed, for any household, under any engagement
    archetype. A re-capture reproduces the absence exactly.

    Each half was already held on its own (`test_renewal_engagement` for the forcing,
    `..._an_always_active_household_never_reaches_the_svt_product` for the divert, which excludes
    the crisis year from its assertion and says why). NEITHER HELD THE COMPOSITION, which is the
    claim a reader of the anchor actually needs, and the register above it therefore carried a
    false locator for two days with every leg green.

    KEYED TO `FTC_WITHDRAWAL_WINDOW`, NOT TO 2022. Widening the window brings more boundaries into
    the subject; emptying it empties the subject and the floor below fails rather than passing
    quietly. This was keyed to `CRISIS_PASSIVE_YEARS` (a set of year strings) until 2026-09-04,
    when the window gained a partial year and a year-string key stopped being able to express it.

    THE FLOOR IS LOAD-BEARING AND IS NOT THE SAME ASSERTION AS THE VERDICT. "No fixed term starts
    in a crisis year" is satisfied for free by a schedule with no crisis-year boundary at all, so
    the floor demands that a term actually STARTS in one — i.e. that the world reached the year at
    all, rather than never arriving.

    AND THE FLOOR IS DELIBERATELY PRODUCT-BLIND, WHICH IS A CORRECTION TO ITS FIRST DRAFT. That
    draft asked for an SVT STINT to begin in the crisis year, which is the same fact the verdict
    tests, from the other side. Under the mutation below no household rolls to SVT at all, so the
    floor emptied and fired FIRST: a true red, reported as a scope failure instead of the
    substantive one, which is this repository's catalogued *scope guard before the verdict*.
    Counting boundaries of EITHER product keeps the floor satisfied under the mutation and lets the
    verdict speak.

    MUTATIONS (`python3 -B`), observed rather than intended:
      * drop the withdrawal-window branch from `rolls_active_renewal` -> **1 red, this leg
        alone, on the VERDICT**, naming `C3@2022-12-30`, `C1@2022-12-30`, `SYN-2016-003@2022-12-30`.
        Nothing else in this file moves, which is the point: the two halves are each already held
        and only their composition is new.
      * remove the passive divert entirely, i.e. restore the pre-C1b world in which a passive roll
        was settled as a fixed term -> **6 reds, this leg among them**. That is the second half of
        the claim: the 53 rows `UNFITTED_YEARS[2022]` cites are recoverable only by re-introducing
        the defect C1b removed.
      * make the divert unconditional on EVERY year -> **2 reds, and NEITHER is this leg.** An
        EQUIVALENCE for this control, stated rather than left flattering: the first term is always
        fixed, so `off_crisis_fixed` survives. This leg does not hold the divert's SCOPE; its
        siblings `..._always_active_household_never_reaches_the_svt_product` and
        `..._leaves_the_fixed_product_and_can_come_back` do, and they fire.
    """
    from simulation import renewals as renewals_module
    from simulation.renewal_engagement import FTC_WITHDRAWAL_WINDOW, ftc_withdrawn_at

    crisis_fixed_starts: list[str] = []
    crisis_boundaries: list[str] = []
    off_crisis_fixed = 0
    checked = 0
    for level in EngagementLevel:
        cid = _a_household_with(level)
        # p = 1.0 is the SOLE WITNESS for the forcing: a household the world says shops at every
        # renewal is the only one whose crisis-year SVT stint cannot be explained by its own
        # archetype. Without it the verdict would also pass on a world with no forcing at all,
        # because a passive household rolls to SVT in every year anyway.
        original = renewals_module.active_renewal_probability_for_customer
        renewals_module.active_renewal_probability_for_customer = lambda _h: 1.0
        try:
            schedule = _schedule(cid, "2016-01-01", price_records)
        finally:
            renewals_module.active_renewal_probability_for_customer = original

        for term in schedule:
            product = term.get("tariff_type") or "fixed"
            start = term["acquisition_date"]
            if ftc_withdrawn_at(start):
                crisis_boundaries.append(start)
            if product == "fixed":
                if ftc_withdrawn_at(start):
                    crisis_fixed_starts.append(f"{cid}@{start}")
                else:
                    off_crisis_fixed += 1
        checked += 1

    assert checked, "no roster household reached this control; its PASS means nothing"
    assert crisis_boundaries, (
        f"no term of ANY product starts inside {FTC_WITHDRAWAL_WINDOW} across {checked} "
        f"households, so the world never reached a crisis-year boundary and the verdict below is "
        f"vacuous — the emptied-subject fail-open, not a pass")
    assert off_crisis_fixed, (
        "no fixed term starts in ANY year, so the verdict below would hold for a world in which "
        "the fixed product had disappeared entirely rather than one that withdraws it in a crisis")
    assert not crisis_fixed_starts, (
        f"a fixed term STARTS in a crisis year: {crisis_fixed_starts[:5]}. Then the renewal roll "
        f"can fire there, the empty renewal population is not structural, and the cause in "
        f"`departure_level_anchor.UNFITTED_YEARS` that says a capture can never carry one is "
        f"wrong. Fix the cause or the code — do not widen this control.")
