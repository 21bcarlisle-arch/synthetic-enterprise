"""C6's producer: some share of arrivals open on the default tariff, and the exit is reachable.

`docs/staging/SEAT_RESULT_THE_ARRIVAL_EXIT_REACHES_A_PRICED_BOUNDARY_AND_NO_ROSTER_MINTS_A_
HOUSEHOLD_THAT_CAN_TAKE_IT_2026-09-19.md` §5 measured **232 of 232** roster records at
`tariff_type: None`: the arrival-exit built by `05684780e` was reachable code behind an unreachable
input. `simulation/arrival_route.py` is the input.

WHAT EACH CONTROL BELOW IS FOR, because a file of tests over one change is otherwise a file of
restatements of that change:

  (a) the producer PRODUCES, and it produces BOTH values -- one control over the whole partition
      rather than a leg per branch, because a producer that labels EVERY arrival passes a
      "some are svt" leg and a producer that labels NONE passes a "some are None" leg;
  (b) the scope carve-outs hold (domestic only; the unlabelled remainder stays unlabelled);
  (c) THE ARRIVAL PATH, not the string. The drawn item named its own insufficiency: *"minting the
      tariff string without the arrival PATH, so the flag is set on households whose term history
      makes the exit unreachable anyway."* (c) is that control and it is the load-bearing one;
  (d) the share is keyed to the PROPERTY that produced it -- a ratio of two published rates -- and
      not to today's answer, so it goes red when the mechanism breaks and stays green when a
      published series is legitimately re-sourced.
"""
from __future__ import annotations

import collections
import datetime as dt

import simulation.population_draw as pd
from company.interfaces.customer_profitability import (
    MIN_TERM_INDEX_FOR_UPLIFT,
    UPLIFTABLE_TARIFF_TYPES,
)
from simulation.arrival_route import (
    ARRIVAL_DEFAULT_TARIFF_TYPE,
    default_tariff_arrival_share,
    home_move_rate_per_household_year,
    move_rate_reconciliation,
)
from simulation.household_segments import TenureType
from simulation.renewals import build_renewal_schedule

SEED = 7


def _drawn(lam: float = 40) -> list:
    """Same fixture shape as `test_drawn_book_tariff_type_fidelity._drawn`, and same reason: the
    live curriculum is a ~1/year trickle, which cannot distinguish a share from a coincidence.
    The lambda moves the sample size and never the labelling law."""
    return list(
        pd.iter_acquisition_events(
            base_seed=SEED, start_year=2016, end_year=2025, acquisitions_per_year_lambda=lam,
        )
    )


def _flat_price_records(start: str, end: str, price: float = 60.0) -> list:
    """A synthetic SSP series, so (c) does not depend on a warm Elexon cache.

    A cache-dependent control is one that SKIPS when the cache is cold, and a skip wears a pass's
    colour. The exit's reachability is a property of the SCHEDULE BUILDER's term indexing, not of
    any particular price, so a flat series tests the thing under test and nothing else.
    """
    d0, d1 = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    return [
        {"settlementDate": (d0 + dt.timedelta(days=i)).isoformat(), "systemSellPrice": price}
        for i in range((d1 - d0).days + 1)
    ]


# --------------------------------------------------------------------------- #
# (a) The producer produces, and it produces BOTH values                      #
# --------------------------------------------------------------------------- #

def test_the_draw_mints_default_tariff_arrivals_AND_leaves_the_rest_unlabelled():
    """ONE control over the whole partition. Both branches must be REACHABLE.

    Written this way on purpose. A control asserting only "some arrival carries svt" is passed by a
    producer that labels the entire book -- which is the R13 change
    `DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` refused, in the other direction. A control
    asserting only "some arrival is None" is passed by the world as it was before C6, which is the
    gap. Neither leg alone can fail for the reason it was written, so they are one assertion.

    R15 MUTATION (must fire): return `None` unconditionally from
    `population_draw._draw_tariff_type` -- the `svt` count goes to 0 and this reds on the first
    clause, which is the 232-of-232 state the finding measured. RUN AND REVERTED 2026-09-19.
    R15 MUTATION (must fire): return `ARRIVAL_DEFAULT_TARIFF_TYPE` unconditionally -- the `None`
    count goes to 0 and this reds on the second clause. RUN AND REVERTED 2026-09-19.
    """
    resi = [e for e in _drawn() if e.segment == "resi"]
    assert len(resi) >= 100, (
        f"only {len(resi)} resi draws -- too few to say anything about a share, so every bound "
        "below would be passing on a near-empty population"
    )
    counts = collections.Counter(e.tariff_type for e in resi)
    on_default = counts[ARRIVAL_DEFAULT_TARIFF_TYPE]
    unlabelled = counts[None]

    assert on_default and unlabelled, (
        f"the arrival partition is degenerate: {on_default} on the default tariff and "
        f"{unlabelled} unlabelled, out of {len(resi)}. BOTH routes onto this supplier's book must "
        "be reachable -- a move-in opens on the incumbent's deemed contract, a switcher opens on "
        "the deal it chose. A producer that can only do one of them is not a route split."
    )
    assert on_default + unlabelled == len(resi), (
        f"a third label appeared on the drawn book: {dict(counts)}. The published record "
        "establishes what a MOVE-IN opens on and nothing else; anything else here is a label "
        "nobody sourced."
    )


# --------------------------------------------------------------------------- #
# (b) The scope carve-outs                                                     #
# --------------------------------------------------------------------------- #

def test_only_a_DOMESTIC_arrival_can_open_on_the_default_tariff():
    """`simulation/svt_rates.py` is the Ofgem DOMESTIC default tariff cap.

    An SME or I&C site has no default tariff to arrive on and its renewals are broker-driven, so
    labelling one `svt` would settle a business site against the domestic cap for a decade.
    `renewals.build_renewal_schedule` makes the same carve-out at its own SVT branch; this is the
    producer-side half, and without it the two halves would disagree about what the product covers.

    THE SUBJECT HAS TO BE MANUFACTURED, and that is a finding rather than a fixture detail.
    `DEFAULT_SEGMENT_WEIGHTS` is `{"resi": 1.00}`, so the live draw mints no business site at all
    and a carve-out control written over the default draw would be asserting over an EMPTY list --
    passing for free, forever, in the shape this repo keeps catching. The weights are overridden
    here so the branch has something to refuse. If the director ever opens the draw to SME, this
    control is already the one standing over it.

    R15 MUTATION (must fire): drop the `!= "resi"` guard in `_draw_tariff_type`. RUN AND REVERTED
    2026-09-19.
    """
    events = list(
        pd.iter_acquisition_events(
            base_seed=SEED, start_year=2016, end_year=2025, acquisitions_per_year_lambda=40,
            segment_weights={"resi": 0.5, "sme": 0.5},
        )
    )
    non_resi = [e for e in events if e.segment != "resi"]
    assert len(non_resi) >= 50, (
        f"only {len(non_resi)} non-resi draws even with the weights overridden -- this control "
        "would be passing on a near-empty population"
    )
    offenders = [(e.customer_id, e.segment) for e in non_resi if e.tariff_type is not None]
    assert not offenders, (
        f"{len(offenders)} non-domestic arrivals carry a tariff label: {offenders[:5]}. The "
        "anchor behind that label is an England HOUSING survey and the product is the domestic "
        "price cap; neither reaches a business site."
    )


def test_the_unlabelled_remainder_is_still_NOT_given_an_upliftable_product():
    """The 2026-08-28 determination stands, and C6 does not quietly overturn it.

    That ruling refused labelling the drawn book `fixed`: it would assert 100% fixed against a
    published domestic fixed share near one third, and the only thing it improves is the
    experiment's own `n`. C6 labels ONLY arrivals whose product is settled by the licence's
    deemed-contract scheme. The remainder keeps its honest silence, so the drawn book's share of
    UPLIFTABLE products must still be zero.

    R15 MUTATION (must fire): make `_draw_tariff_type` return `"fixed"` on its non-move branch
    instead of `None`. Share goes 0.00 -> ~0.74 and this reds. RUN AND REVERTED 2026-09-19.
    """
    resi = [e for e in _drawn() if e.segment == "resi"]
    upliftable = [e for e in resi if e.tariff_type in UPLIFTABLE_TARIFF_TYPES]
    assert not upliftable, (
        f"{len(upliftable)} of {len(resi)} drawn domestic arrivals carry an UPLIFTABLE product. "
        "C6 establishes what a move-in opens on and establishes nothing about the rest. Giving "
        "the rest a product is the change refused by "
        "docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md."
    )


# --------------------------------------------------------------------------- #
# (c) THE ARRIVAL PATH, not the string                                         #
# --------------------------------------------------------------------------- #

def test_a_default_tariff_arrival_REACHES_the_exit_at_a_priceable_term_index():
    """The drawn item's own stated insufficiency, made into a control.

    > *"What would prove this insufficient: minting the tariff string without the arrival PATH, so
    > the flag is set on households whose term history makes the exit unreachable anyway."*

    So the string is not the deliverable. The deliverable is a household whose schedule actually
    contains a non-SVT term, at a `term_index` the company's arm will price -- `term_index >=
    MIN_TERM_INDEX_FOR_UPLIFT`, the `acquisition_term` stage that refuses a household's FIRST term.

    The mechanism that makes this true is `run_phase2b`'s `term_indices` counter incrementing on
    every term in `all_terms` with no branch on `tariff_type`, so a cap segment consumes an index
    exactly as a fixed term does. That is a PROPERTY and this control is keyed to it: a future
    edit making the index skip indexed tariffs -- which looks like a tidy-up -- would drop every
    post-SVT conversion into `acquisition_term`, and this reds.

    R15 MUTATION (must fire): in `renewals.build_renewal_schedule`, return `build_svt_schedule(...)`
    for the whole window on the SVT-origin branch instead of converting -- no non-SVT term is ever
    built and this reds with "took the exit: 0". RUN AND REVERTED 2026-09-19.
    """
    resi_elec = [
        e for e in _drawn()
        if e.segment == "resi"
        and e.commodity == "electricity"
        and e.tariff_type == ARRIVAL_DEFAULT_TARIFF_TYPE
        # Acquired early enough that a cap year plus a conversion fits inside the window. An
        # arrival in the last year of the record NOT converting is the builder being correct,
        # not a defect, so it is excluded from the subject rather than asserted about.
        and dt.date.fromisoformat(e.acquisition_date).year <= 2022
    ]
    assert resi_elec, "no default-tariff domestic electricity arrival to test the path on"

    report_end = "2025-06-07"
    took_the_exit = 0
    first_indices = []
    for e in resi_elec[:8]:
        records = _flat_price_records(
            (dt.date.fromisoformat(e.acquisition_date) - dt.timedelta(days=400)).isoformat(),
            report_end,
        )
        schedule = build_renewal_schedule(
            e.customer_id, e.acquisition_date, report_end, records, e.eac_kwh,
            segment="resi", tariff_type=e.tariff_type,
        )
        kinds = [t.get("tariff_type") for t in schedule]
        first_non_svt = next(
            (i for i, k in enumerate(kinds) if k != ARRIVAL_DEFAULT_TARIFF_TYPE), None
        )
        if first_non_svt is not None:
            took_the_exit += 1
            first_indices.append(first_non_svt)

    assert took_the_exit, (
        "every default-tariff arrival stayed on the default tariff for the whole window. The "
        "flag is set and the exit is unreachable, which is exactly the outcome the drawn item "
        "named as proof the work was insufficient."
    )
    assert min(first_indices) >= MIN_TERM_INDEX_FOR_UPLIFT, (
        f"a conversion lands at term_index {min(first_indices)}, below "
        f"MIN_TERM_INDEX_FOR_UPLIFT={MIN_TERM_INDEX_FOR_UPLIFT}, so the arm refuses it at the "
        "`acquisition_term` stage and the priced boundary is decoration again. The cap stint's "
        "segments must consume term indices -- see `run_phase2b`'s `term_indices` counter."
    )


# --------------------------------------------------------------------------- #
# (d) The share is keyed to its PROPERTY, not to today's answer                #
# --------------------------------------------------------------------------- #

def test_the_arrival_share_MOVES_WITH_the_published_switching_record():
    """Keyed to the mechanism, not to a number.

    The share is `m / (m + s)`: move-ins over move-ins plus switches. So when the published
    switching record falls, the default-tariff share of ARRIVALS must rise -- not because anyone
    decided it should, but because the same move volume is a larger share of a smaller inflow.
    2022 is the record's own natural experiment: fixed deals were withdrawn and switching collapsed
    from ~23% (2020) to ~4%.

    A control pinned to "2022 == 0.54" would go red the day a year is legitimately re-sourced and
    stay green if the ratio were replaced by a hard-coded table. This one is the other way round.

    R15 MUTATION (must fire): replace the ratio in `default_tariff_arrival_share` with a constant
    -- every year returns the same value, the strict inequality fails and this reds. RUN AND
    REVERTED 2026-09-19.
    """
    tenure = TenureType.OWNER_OCCUPIER
    crisis = default_tariff_arrival_share(2022, tenure)
    calm = default_tariff_arrival_share(2020, tenure)
    assert crisis is not None and calm is not None
    assert crisis > calm, (
        f"2022 ({crisis:.3f}) does not exceed 2020 ({calm:.3f}). Switching collapsed in 2022, so "
        "the move-in route must be a LARGER share of that year's arrivals. If this is equal, the "
        "share has stopped reading the published switching series and is a constant wearing a "
        "function's clothes."
    )


def test_a_renter_arrives_on_the_default_tariff_more_often_than_an_owner():
    """C6 predicted this in prose before it was computed: *"renters move several times more often
    than owners, and tenure is already drawn and already reaches the churn decision."*

    The prediction is on the record and this is the measurement that could have refuted it. It
    does not: EHS 2024-25 puts private-renter move-ins at ~17.5% per household-year against ~3.8%
    for owner-occupiers, a spread of about 4.6x, and that spread is the whole reason conditioning
    on tenure buys anything over an aggregate rate.

    R15 MUTATION (must fire): give every tenure the aggregate move rate in
    `EHS_MOVES_INTO_TENURE_MILLIONS` -- the ratio collapses to 1.0 and both clauses red. RUN AND
    REVERTED 2026-09-19.
    """
    owner = home_move_rate_per_household_year(TenureType.OWNER_OCCUPIER)
    renter = home_move_rate_per_household_year(TenureType.PRIVATE_RENTER)
    assert renter > owner * 2, (
        f"private renter move rate {renter:.4f} is not materially above owner-occupier "
        f"{owner:.4f}. If these have converged, conditioning the arrival route on tenure buys "
        "nothing and C6's simplification should be replaced by an aggregate rate rather than "
        "kept as a tenure table that no longer discriminates."
    )
    for year in (2016, 2022, 2025):
        assert (
            default_tariff_arrival_share(year, TenureType.PRIVATE_RENTER)
            > default_tariff_arrival_share(year, TenureType.OWNER_OCCUPIER)
        ), f"the tenure spread does not survive into the arrival share at {year}"


def test_a_year_the_published_record_cannot_speak_for_gets_None_and_not_a_guess():
    """Fail closed, and say so on the surface.

    The switching commons carries 2016-2025. An arrival outside it has no `s`, so it has no share,
    so it gets no product -- the same honest silence the drawn book carried before C6. The failure
    mode this refuses is the tempting one: clamp to the nearest year, which reads as evidence and
    is not.

    R15 MUTATION (must fire): clamp the year into the commons' range inside
    `default_tariff_arrival_share`. It returns a float for 1999 and this reds. RUN AND REVERTED
    2026-09-19.
    """
    assert default_tariff_arrival_share(1999, TenureType.OWNER_OCCUPIER) is None
    assert default_tariff_arrival_share(2099, TenureType.PRIVATE_RENTER) is None
    # And the in-range years are not None, or the control above passes for the wrong reason --
    # a function that returned None for EVERYTHING would satisfy both assertions.
    assert default_tariff_arrival_share(2019, TenureType.OWNER_OCCUPIER) is not None


def test_the_move_anchor_reports_how_much_of_the_published_volume_it_carries():
    """No silent caps. The per-tenure flows do not sum to the publisher's own headline, and the
    module says so with a number rather than a caveat.

    EHS 2024-25 Annex Table 3.7 breaks out within-tenure moves, newly formed households and the
    private-rent -> owner-occupy flow; the remaining inter-tenure flows are not published
    separately. Distributing them would invent a split the survey does not report. Leaving them
    out biases the arrival share DOWN, which understates this repair -- the conservative
    direction, and the one a reader must be able to see.

    R15 MUTATION (must fire): distribute the uncarried 0.178m across the three tenures.
    `uncarried_millions` goes to 0.0 and the first assertion reds. RUN AND REVERTED 2026-09-19.
    """
    rec = move_rate_reconciliation()
    assert rec["uncarried_millions"] > 0, (
        "the per-tenure flows now account for the entire published move volume. If a genuinely "
        "complete table was sourced, say so and delete this control; if the shortfall was spread "
        "across tenures, that is a split EHS does not publish."
    )
    assert 0.80 <= rec["share_of_published_carried"] <= 1.0, (
        f"the anchor carries {rec['share_of_published_carried']:.0%} of the published move "
        "volume. Below 80% it is no longer a reading of the published series, it is a sample of "
        "it, and the arrival share it produces needs a bound rather than a point."
    )
    assert rec["why_uncarried"], "the shortfall has no stated reason, so a reader cannot judge it"
