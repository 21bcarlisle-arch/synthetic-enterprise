"""A house has one headcount, whichever path in the world asks how many people live there.

THE DEFECT (measured 2026-09-17, on the live book). Two functions drew the household size:

* `household_physical_layer.people_count_for` — its own band-then-within-band draw from TS017, on
  substream `physical_layer_people_count_<id>`. This is what the FABRIC path traces a premise on,
  and 130 of the book's 136 electricity premises settle on the fabric path.
* `dwelling_records.people_count_for_area` → `_derive_people_count` — a second TS017 draw on a
  different named substream, which is what the PROPERTY RECORD carried, and therefore what the
  legacy comparison arm, the EPC multipliers and the switch verdict all saw.

Both were correct draws from the same published distribution. Neither was wrong about the
population: property mean 2.388, physical-layer mean 2.485, ONS TS017 2.37. **The per-home
assignment was two different answers to one question, and the two paths disagreed for 102 of 134
homes, by as much as five people.**

`occupancy_band_for` names this exact shape in its own docstring — *"two draws of one quantity is
the defect this module just fixed"* — so it was committed a second time, one module over, by the
module that had just written the warning.

AND A THIRD ANSWER, which is why 7 homes survived the first repair. `build_properties` applied
`PEOPLE_COUNT_BY_CUSTOMER.get(cid) or _derive_people_count(cid)` INLINE, so the authored roster
outranked the draw at that one call site and nowhere else. A precedence written at a call site is
a precedence the next caller does not inherit.

These legs are about AGREEMENT and PRECEDENCE, not about the distribution — the TS017 shares have
their own tests and were never in doubt.
"""
from __future__ import annotations

import pathlib
import re

from simulation import dwelling_records as dr
from simulation import household_physical_layer as hpl
from simulation import premise_trace as pt
from simulation.household import HeatingSystem, Household, InsulationLevel, PropertyType

#: Enough ids to make an accidental agreement vanishingly unlikely: two independent TS017 draws
#: agree on about a quarter of homes, so 200 ids leave a ~1e-120 chance of a false pass.
IDS = [f"AGREE-{i:04d}" for i in range(200)]


def _household_for(customer_id: str) -> Household:
    """A minimal dwelling for the composition legs below.

    Its FIELDS are deliberately identical for every id, because what the composition legs assert
    must not depend on them: `composition_cuts_for` is keyed on the customer id alone, so a
    household that varied per id would let a passing test hide a draw that had quietly started
    reading bedrooms again.
    """
    return Household(
        customer_id=customer_id, property_type=PropertyType.SEMI_DETACHED,
        build_era="1965_1980", epc_rating="D", bedrooms=3,
        heating_system=HeatingSystem.GAS_BOILER_COMBI, boiler_age=10,
        has_solar=False, solar_kwp=0.0, solar_install_year=None,
        has_battery=False, battery_kwh=0.0, has_ev=False, ev_charger_kw=0.0,
        has_smart_meter=True, smart_meter_install_year=2020,
        insulation=InsulationLevel.PARTIAL, has_driveway=True, roof_aspect="S",
    )


def test_one_home_has_one_headcount_whoever_asks():
    """The property record and the fabric path must not be able to disagree about a house.

    Keyed to AGREEMENT rather than to either function's output, so it stays true if the draw is
    re-anchored, re-seeded, or conditioned on an output area — and goes red the moment a second
    draw reappears anywhere.
    """
    disagreements = [
        (cid, dr.people_count_for_area(cid, None), hpl.people_count_for(cid))
        for cid in IDS
        if dr.people_count_for_area(cid, None) != hpl.people_count_for(cid)
    ]
    assert not disagreements, (
        f"{len(disagreements)} of {len(IDS)} homes have two headcounts: {disagreements[:5]}. "
        "Two correct draws from one distribution are still two answers to one question -- the "
        "fabric path would trace a house with one family and the property record would bill it "
        "for another."
    )


def test_the_book_itself_agrees_and_this_is_not_a_synthetic_id_artefact():
    """The same property on the REAL population, because the ids above are invented.

    A synthetic id exercises the draw; it cannot see an authored roster entry, a customer with no
    property record, or any other real-population shape. This leg is what catches those.
    """
    from simulation.live_population import live_dwellings, live_population

    customers = [c for c in live_population() if c["commodity"] == "electricity"]
    assert len(customers) > 50, (
        f"population floor: only {len(customers)} electricity customers were loaded, which is too "
        "few for this leg to mean anything. A shrunken book must refuse, not pass quietly."
    )
    properties = build = dr.build_properties(customers, dwellings=live_dwellings())
    checked = 0
    disagreements = []
    for customer in customers:
        cid = str(customer["customer_id"])
        record = properties.get(cid)
        if not record or "people_count" not in record:
            continue
        checked += 1
        if int(record["people_count"]) != int(hpl.people_count_for(cid)):
            disagreements.append((cid, record["people_count"], hpl.people_count_for(cid)))
    assert checked > 50, f"population floor: only {checked} property records carried a headcount"
    assert not disagreements, (
        f"{len(disagreements)} of {checked} homes in the live book have two headcounts: "
        f"{disagreements[:5]}"
    )
    del build


def test_an_authored_headcount_outranks_every_draw_for_every_reader():
    """The seven homes that survived the first repair, and the reason they did.

    The authored roster is the world saying it KNOWS who lives here. A reader that draws anyway is
    not approximating -- it is contradicting a stated fact, and `build_properties` was the only
    caller that knew.
    """
    assert dr.PEOPLE_COUNT_BY_CUSTOMER, "population floor: the authored roster is empty"
    for cid, authored in dr.PEOPLE_COUNT_BY_CUSTOMER.items():
        assert dr.people_count_for_area(cid, None) == authored, (
            f"{cid}: the area function drew {dr.people_count_for_area(cid, None)} over an "
            f"authored {authored}"
        )
        assert hpl.people_count_for(cid) == authored, (
            f"{cid}: the physical layer drew {hpl.people_count_for(cid)} over an authored "
            f"{authored} -- this is the fabric path tracing a house the roster describes"
        )


def test_an_authored_headcount_outranks_an_output_area_too():
    """Precedence is authored > area > national, and the area leg must not jump the authored one.

    Asserted with a real roster id against an area the census does not hold, so the area branch is
    entered and must still yield to the authored value.
    """
    cid, authored = next(iter(dr.PEOPLE_COUNT_BY_CUSTOMER.items()))
    assert dr.people_count_for_area(cid, "E00NOTREAL") == authored


def test_the_draw_is_still_deterministic_and_stable_for_a_tenure():
    """Delegation must not have made the headcount re-roll per call.

    A house whose occupancy changes between two asks in one run is worse than two houses that
    disagree: nothing downstream could even name the inconsistency.
    """
    for cid in IDS[:20]:
        assert len({hpl.people_count_for(cid) for _ in range(5)}) == 1


def test_the_within_band_table_is_still_reachable_and_still_published():
    """`_national_headcount_draw` is kept BECAUSE `_WITHIN_BAND_SHARES` lives nowhere else.

    The delegation left that table with no production caller. Deleting the function would have
    made the only written-down copy of the published within-band split (3-person 16.0% / 4-person
    12.9%; 5/6/7/8+ at 4.5/1.5/0.5/0.4%) unreachable and unverified, which trades one defect for a
    quieter one. This leg is the caller that keeps it honest.
    """
    counts = {hpl._national_headcount_draw(f"BAND-{i:04d}") for i in range(300)}
    assert counts, "the retained draw returned nothing"
    assert min(counts) >= 1
    assert max(counts) >= 5, (
        "300 draws produced no 5+ household, so the 5/6/7/8+ branch of _WITHIN_BAND_SHARES is "
        "unreachable -- the table is no longer exercised by anything"
    )
    assert {1, 2, 3, 4} <= counts, f"bands below 5 are not all reachable: {sorted(counts)}"


def test_the_retained_draw_is_not_what_the_world_uses():
    """It must stay a private, test-only relic. If production calls it, the defect is back.

    Checked by CALLER rather than by name: a rename would slip past a string test, and what must
    hold is that no shipped module asks the old question.
    """
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    offenders = []
    for folder in ("simulation", "company", "saas", "tools", "background"):
        for path in (root / folder).rglob("*.py"):
            if path.name == "household_physical_layer.py":
                continue
            if "_national_headcount_draw" in path.read_text():
                offenders.append(str(path.relative_to(root)))
    assert not offenders, (
        f"the pre-delegation draw has production callers again: {offenders}. Every one of them is "
        "a second headcount for a house that already has one."
    )


def test_a_customer_with_no_authored_entry_still_gets_a_headcount():
    """The fallback must survive the precedence change -- most of the book has no roster entry.

    The authored branch is a `dict.get` guarded by truthiness, so the way this breaks is that it
    starts swallowing the un-authored case, and every home in the book is un-authored but seven.
    """
    for cid in ("NOT-IN-ANY-ROSTER-0001", "NOT-IN-ANY-ROSTER-0002"):
        value = dr.people_count_for_area(cid, None)
        assert isinstance(value, int) and value >= 1
        assert value == dr.people_count_for_area(cid, None), "the fallback re-rolls per call"
        assert cid not in dr.PEOPLE_COUNT_BY_CUSTOMER


# ===========================================================================
# THE SAME PROPERTY FOR THE TWO COMPOSITION CUTS (2026-09-23)
#
# `demand_model._daytime_occupancy_rate` is keyed on three EFUS cuts, not one.
# The headcount legs above closed the size cut. `pensioner_present` and
# `someone_employed` were the other two, and they failed the same way ONE FIELD
# ALONG: the property record left both absent on all 144 homes of the live book
# while `premise_trace.behaviour_profile_for` drew both for itself at an uncited
# 0.22 and 0.25-given-a-pensioner. The repair is the same repair — one function,
# `dwelling_records.composition_cuts_for`, delegated to by both paths.
#
# These legs could not have been written before that delegation landed, because
# until then the two paths were DESIGNED to disagree. That is worth saying out
# loud: the absence of this test was not an oversight, it was the defect.
# ===========================================================================

def test_one_home_has_one_composition_whoever_asks():
    """Keyed to AGREEMENT, not to either path's output — so re-anchoring the shares, re-seeding
    the draw or adding an authored override all keep this green, and a second draw reappearing
    anywhere reds it.

    Two independent Bernoulli draws at these shares agree on both cuts for about 55% of homes, so
    200 ids leave a ~1e-52 chance of a false pass.
    """
    disagreements = []
    for cid in IDS:
        record = dr.composition_cuts_for(cid)
        traced = pt.behaviour_profile_for(cid, _household_for(cid))
        if record != (traced.pensioner_present, traced.someone_employed):
            disagreements.append(
                (cid, record, (traced.pensioner_present, traced.someone_employed))
            )
    assert not disagreements, (
        f"{len(disagreements)} of {len(IDS)} homes have two compositions: {disagreements[:5]}. "
        "The fabric path would trace a retired couple at home all day and the property record "
        "would shape-adjust the same house as a working household."
    )


def test_a_caller_supplied_composition_still_wins_over_the_draw():
    """The delegation must not swallow an explicitly-passed value. `behaviour_profile_for` has
    always documented that these fields 'attach UNCHANGED where a caller has them', and the
    delegation is reached only for the ones that are None — so a caller supplying ONE of the two
    must get its value AND the drawn value for the other, not both drawn and not both supplied.

    This is the partition, asserted over the whole of it rather than one leg per branch: the
    both-supplied case is what a fixture uses, the one-supplied case is the one that silently
    breaks, and a delegation that ignored its arguments entirely would pass a both-None test.
    """
    cid = "COMPOSITION-PRECEDENCE-0001"
    drawn_pensioner, drawn_employed = dr.composition_cuts_for(cid)
    household = _household_for(cid)

    both = pt.behaviour_profile_for(cid, household, pensioner_present=not drawn_pensioner,
                                    someone_employed=not drawn_employed)
    assert both.pensioner_present is (not drawn_pensioner)
    assert both.someone_employed is (not drawn_employed)

    pensioner_only = pt.behaviour_profile_for(cid, household,
                                             pensioner_present=not drawn_pensioner)
    assert pensioner_only.pensioner_present is (not drawn_pensioner)
    assert pensioner_only.someone_employed is drawn_employed, (
        "supplying one cut must not overwrite the other with a supplied value"
    )

    employed_only = pt.behaviour_profile_for(cid, household,
                                            someone_employed=not drawn_employed)
    assert employed_only.someone_employed is (not drawn_employed)
    assert employed_only.pensioner_present is drawn_pensioner


def test_the_shares_the_two_paths_share_are_the_published_ones():
    """The agreement leg above is satisfied by both paths being wrong together, so this is the
    leg that says WHICH answer they agree on. Keyed to EFUS's own headline rather than to
    0.3103/0.68, so correcting a rate against the source moves the target with it.

    SAMPLED THROUGH BOTH PATHS, and the first draft of this leg was wrong for exactly the reason
    that matters. It sampled `composition_cuts_for` only — so restoring the old fabric draw left it
    GREEN, because that function is not what the old draw used. A leg whose docstring claims a
    mutation it cannot see is worse than no leg: `population` below is built from the FABRIC path
    for that reason, which is the path whose shares were wrong (0.22 and 0.845, implying 0.400 and
    0.389 against a published 0.430). The agreement leg above then carries it to the record.
    """
    from simulation.demand_model import (
        EFUS_DAYTIME_RATE_ALL_HOUSEHOLDS,
        EFUS_DAYTIME_RATE_ALL_UNEMPLOYED,
        EFUS_DAYTIME_RATE_NO_PENSIONER,
        EFUS_DAYTIME_RATE_PENSIONER_PRESENT,
        EFUS_DAYTIME_RATE_SOMEONE_EMPLOYED,
    )

    ids = [f"SHARE-{i:05d}" for i in range(2000)]
    population = [pt.behaviour_profile_for(cid, _household_for(cid)) for cid in ids]
    pensioner_share = sum(p.pensioner_present for p in population) / len(population)
    employed_share = sum(p.someone_employed for p in population) / len(population)

    # Sampling tolerance for n=2000 at p~0.3/0.7 is ~1.2pp at 3 sigma, which moves the implied
    # rate by well under 0.005; 0.02 is comfortably outside that and comfortably inside the 3.0pp
    # and 4.1pp errors the pre-delegation draw made on the two cuts.
    implied_by_pensioner = (EFUS_DAYTIME_RATE_PENSIONER_PRESENT * pensioner_share
                            + EFUS_DAYTIME_RATE_NO_PENSIONER * (1 - pensioner_share))
    implied_by_employment = (EFUS_DAYTIME_RATE_SOMEONE_EMPLOYED * employed_share
                             + EFUS_DAYTIME_RATE_ALL_UNEMPLOYED * (1 - employed_share))
    assert abs(implied_by_pensioner - EFUS_DAYTIME_RATE_ALL_HOUSEHOLDS) < 0.02, (
        f"the pensioner share {pensioner_share:.4f} implies an all-household daytime rate of "
        f"{implied_by_pensioner:.4f} against EFUS's published {EFUS_DAYTIME_RATE_ALL_HOUSEHOLDS}"
    )
    assert abs(implied_by_employment - EFUS_DAYTIME_RATE_ALL_HOUSEHOLDS) < 0.02, (
        f"the employed share {employed_share:.4f} implies an all-household daytime rate of "
        f"{implied_by_employment:.4f} against EFUS's published {EFUS_DAYTIME_RATE_ALL_HOUSEHOLDS}"
    )


#: The three pre-delegation draws are censused by CALLER, and the call is what the fingerprint
#: matches — NOT the bare word. The children leg was written with a `'"children")'` substring and
#: reddened on `tools/sample_gate_rss_premium.py`, which reads the cgroup file `<task>/children` and
#: has nothing to do with who lives in a house. Its two siblings kept the substring: green on
#: 2026-09-23 by luck of vocabulary, one `record["employed"]` away from naming an innocent file, and
#: a control that names an innocent file is a control someone eventually silences. One shape for all
#: three, because three copies of one census is how the siblings were left behind in the first place.
_CENSUS_ROOTS = ("simulation", "company", "saas", "tools", "background")


def _pre_delegation_fingerprint(*names: str) -> re.Pattern:
    """A `_substream(..., "<name>")` CALL for any of these draw names."""
    return re.compile(r'_substream\([^)]*"(?:' + "|".join(names) + r')"\)')


def _production_callers_drawing(*names: str) -> list[str]:
    root = pathlib.Path(__file__).resolve().parents[2]
    fingerprint = _pre_delegation_fingerprint(*names)
    return [
        str(path.relative_to(root))
        for folder in _CENSUS_ROOTS
        for path in sorted((root / folder).rglob("*.py"))
        if fingerprint.search(path.read_text())
    ]


def test_the_pre_delegation_composition_draw_has_no_production_callers():
    """Checked by CALLER, like the headcount leg above: what must hold is that no shipped module
    draws these two for itself again. The old draw's fingerprint is a `_substream(..., "pensioner")`
    or `_substream(..., "employed")` call, which is what a re-introduced second answer would look
    like. Matched on the CALL — see `_pre_delegation_fingerprint` for why the word is not enough.
    """
    offenders = _production_callers_drawing("pensioner", "employed")
    assert not offenders, (
        f"the pre-delegation composition draw has production callers again: {offenders}. Every "
        "one of them is a second answer about who lives in a house that already has one."
    )


# ===========================================================================
# AND THE THIRD FIELD, ONE ALONG AGAIN (2026-09-23)
#
# `children_count` failed the same way as the two cuts above and for one more
# reason. The property record answered `DEFAULT_CHILDREN_COUNT` on all 144
# homes under a STATED R10 gap — honest, because no reference population for
# children-within-size existed — while `premise_trace.behaviour_profile_for`
# drew `randint(0, people_count - 1)` above a size guard of 3, uncited. One
# home, two answers, and this time one of them had a written reason to be
# silent and the other had none to be uniform.
#
# The reference landed the same day (`demand_model.CHILDREN_WITHIN_SIZE_
# REFERENCE`, ONS Census 2021), which is what made the delegation legal: the
# finding that blocked it blocked it "until the reference has a source", and
# these legs could not have been written before that. The absence was the
# defect, not an oversight — the same sentence as the composition block above.
#
# WHAT THE OLD DRAW ACTUALLY DID, measured over 20,000 ids before the change,
# because the finding that unblocked this got its own instance wrong. It said
# the uniform "puts a child in half of all 2-person homes". It puts a child in
# NONE of them — the `>= 3` guard — against the Census's 8.7%. And it
# disagreed in BOTH directions: short at sizes 2, 4 and 5, long at 3, 6, 7
# and 8 (a 7-person home averaged 2.98 children against the Census's 2.32).
# ===========================================================================

#: Sizes at which the Census conditional has more than one outcome, so a leg over them can fail.
_SIZES_WITH_A_CHOICE = (2, 3, 4, 5, 6, 7, 8)


def test_one_home_has_one_children_count_whoever_asks():
    """Keyed to AGREEMENT, like the two legs above — re-anchoring the Census shares or re-seeding
    the draw keeps this green, and a second children draw reappearing anywhere reds it.

    BOTH PATHS ARE ASKED AT THE SAME HEADCOUNT, deliberately. `behaviour_profile_for` draws its
    own `people_count` from bedrooms when a caller supplies none, so comparing the two at their
    own sizes would conflate a children disagreement with a headcount one — and the headcount has
    its own legs at the top of this file. What must hold here is that one home of a GIVEN size
    has one children count whichever path asks.
    """
    disagreements = []
    for cid in IDS:
        for n in _SIZES_WITH_A_CHOICE:
            record = dr.children_count_for(cid, n)
            traced = pt.behaviour_profile_for(cid, _household_for(cid), people_count=n)
            if traced.children_count != record:
                disagreements.append((cid, n, record, traced.children_count))
    assert not disagreements, (
        f"{len(disagreements)} of {len(IDS) * len(_SIZES_WITH_A_CHOICE)} (home, size) pairs have "
        f"two children counts: {disagreements[:5]}. The fabric path would trace a family with a "
        "child's evening routine and the property record would volume-scale the same house as "
        "all adults."
    )


def test_the_children_draw_can_reach_every_state_the_census_publishes():
    """REACHABILITY BEFORE BEHAVIOUR. A draw that returned 0 for every home would satisfy every
    mean and every share leg written below at some tolerance, and would be the exact defect this
    delegation exists to remove — the old draw's own 2-person answer. So this asserts the
    partition is ENTERED before anything asserts what it contains.

    Asserted as DISTINCTNESS over the whole partition in one control rather than a leg per size,
    because a leg per size is what lets two sizes collapse onto one state unnoticed: a draw that
    ignored `people_count` entirely would pass seven independent "this size reaches some state"
    legs and fail this one.
    """
    ids = [f"CHILD-REACH-{i:05d}" for i in range(2000)]
    reached = {n: {dr.children_count_for(cid, n) for cid in ids} for n in _SIZES_WITH_A_CHOICE}

    # A 2-person home CAN carry a child. Under the draw this replaces it never could.
    assert reached[2] == {0, 1}, (
        f"a 2-person household reaches {sorted(reached[2])}; the Census puts a dependent child in "
        "8.7% of them and the uniform draw this replaces could reach none at all"
    )
    # Every size reaches its own published ceiling, and the ceilings differ.
    assert max(reached[3]) == 2 and max(reached[4]) == 3, (
        f"size 3 reaches up to {max(reached[3])} and size 4 up to {max(reached[4])}"
    )
    # The sizes do not collapse onto one another: the reachable SETS are not all identical.
    assert len({frozenset(v) for v in reached.values()}) > 1, (
        f"every household size reaches the identical set of children counts {reached[2]} — the "
        "draw is not conditional on size at all"
    )
    # And no size can exceed the source's own top band, which is published as "three or more".
    assert max(max(v) for v in reached.values()) == 3, (
        "the Census publishes its top band as three and this draw carries it AS three, so no "
        "household may reach four"
    )


def test_the_children_conditional_the_two_paths_share_is_the_published_one():
    """The agreement leg above is satisfied by both paths being wrong together, so this is the leg
    that says WHICH answer they agree on.

    Keyed to `CHILDREN_WITHIN_SIZE_REFERENCE` itself rather than to today's numbers, so correcting
    the Census derivation moves the target with it and this stays green — and reverting the draw
    to the uniform reds it at sizes 2, 3, 6, 7 and 8 at once.

    SAMPLED THROUGH THE FABRIC PATH for the reason the composition leg above learned the hard way:
    a leg that samples only the delegate cannot see the old draw being restored in `premise_trace`,
    because the old draw is not what the delegate calls.
    """
    from simulation.demand_model import CHILDREN_WITHIN_SIZE_REFERENCE

    assert CHILDREN_WITHIN_SIZE_REFERENCE is not None, (
        "R10 GAP (a)'s population half has been withdrawn; the draw falls back to the all-adult "
        "reading and this leg's subject no longer exists"
    )
    published = {}
    for n, k, share in CHILDREN_WITHIN_SIZE_REFERENCE:
        published.setdefault(n, {})[k] = share
    for n, row in published.items():
        total = sum(row.values())
        published[n] = {k: s / total for k, s in row.items()}

    ids = [f"CHILD-SHARE-{i:05d}" for i in range(4000)]
    worst = (0.0, None)
    for n in _SIZES_WITH_A_CHOICE:
        drawn = [pt.behaviour_profile_for(cid, _household_for(cid), people_count=n).children_count
                 for cid in ids]
        for k, expected in published[n].items():
            got = sum(1 for d in drawn if d == k) / len(drawn)
            if abs(got - expected) > worst[0]:
                worst = (abs(got - expected), (n, k, expected, got))
    # 3 sigma at n=4000 and the worst-case p=0.5 is 0.024; 0.03 is outside sampling noise and
    # well inside the smallest disagreement the uniform draw creates (0.087 at size 2, and
    # 0.20 at size 4 where the Census is bimodal and a uniform cannot be).
    assert worst[0] <= 0.03, (
        f"the fabric path's children conditional is {worst[1][3]:.4f} at (size {worst[1][0]}, "
        f"{worst[1][1]} children) where the Census publishes {worst[1][2]:.4f}"
    )


def test_the_pre_delegation_children_draw_has_no_production_callers():
    """Checked by CALLER, like the two legs above: what must hold is that no shipped module draws
    this for itself again. The old draw's fingerprint is a `_substream(..., "children")` call.

    MATCHED ON THE CALL, NOT ON THE WORD, and the first draft was not. A bare `'"children")'`
    substring reds `tools/sample_gate_rss_premium.py`, which reads the cgroup file
    `<task>/children` and has nothing to do with who lives in a house. A control that names an
    innocent file is a control someone eventually silences.
    """
    offenders = _production_callers_drawing("children")
    assert not offenders, (
        f"the pre-delegation children draw has production callers again: {offenders}. Every one "
        "of them is a second answer about who lives in a house that already has one."
    )


def test_the_draw_census_still_sees_the_call_it_was_built_for_and_not_the_bare_word():
    """The narrowing is worth nothing unless the pattern still SEES the defect, and both halves of
    that fail SILENTLY on their own: a fingerprint that matches nothing greens all three censuses
    for ever, and one that matches the bare word reds an innocent file until someone deletes the
    control. So both directions are asserted here, over the whole partition rather than a leg each.

    The positive fixtures are the `_substream` call each of the three draws actually made before
    the delegation (`simulation/premise_trace.py` at 263b57ac0^ and at 7b792426d^), with the
    expression around the call trimmed to fit. The children negative is the live line at
    `tools/sample_gate_rss_premium.py`; the other two are the ordinary dict reads that the
    substring version was one file away from reddening on.
    """
    drew = {
        "pensioner": '        pensioner_present = _substream(base, "pensioner").random() < 0.22',
        "employed": '        someone_employed = _substream(base, "employed").random() < 0.25',
        "children": '            _substream(base, "children").randint(0, people_count - 1)',
    }
    for name, call in drew.items():
        assert _pre_delegation_fingerprint(name).search(call), (
            f"the {name} fingerprint no longer matches the call it was built for -- its census "
            f"is green on every tree, including one that re-introduced {call.strip()}"
        )
    any_draw = _pre_delegation_fingerprint(*drew)
    innocent = (
        '            kids.extend(int(p) for p in (task / "children").read_text().split())',
        '    if household_profile.get("pensioner"):',
        '        return record["employed"]',
    )
    for line in innocent:
        assert not any_draw.search(line), (
            f"the fingerprint matches the WORD and not the call: {line.strip()} is not a second "
            "answer about who lives in a house, and a census that says it is gets silenced"
        )


def test_the_property_record_declares_the_children_it_draws():
    """The delegation is worth nothing if the record still writes the constant. Keyed to the
    RECORD matching the delegate per home — not to a count of children on the live book, which
    would go red the day the Census derivation is corrected.

    The `{0: 144}` this replaces is in `PREREG_the_volume_normaliser_is_the_second_cut_set_
    instance.md`: children were present-and-zero on every home in the book, so no production
    caller supplied the cut at all and the volume response was latent rather than live.
    """
    customers = [
        {"customer_id": f"CHILD-REC-{i:04d}", "segment": "resi", "commodity": "electricity",
         "home_type": "semi_detached", "epc_rating": "D", "bedrooms": 3}
        for i in range(120)
    ]
    properties = dr.build_properties(customers)
    mismatches = [
        (cid, p["children_count"], dr.children_count_for(cid, p["people_count"]))
        for cid, p in properties.items()
        if p["children_count"] != dr.children_count_for(cid, p["people_count"])
    ]
    assert not mismatches, f"the record and the delegate disagree for {mismatches[:5]}"
    assert any(p["children_count"] for p in properties.values()), (
        "no record in a 120-home book declares a child; the record is writing the constant again"
    )
