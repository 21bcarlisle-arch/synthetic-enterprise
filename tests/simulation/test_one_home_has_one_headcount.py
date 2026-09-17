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

from simulation import dwelling_records as dr
from simulation import household_physical_layer as hpl

#: Enough ids to make an accidental agreement vanishingly unlikely: two independent TS017 draws
#: agree on about a quarter of homes, so 200 ids leave a ~1e-120 chance of a false pass.
IDS = [f"AGREE-{i:04d}" for i in range(200)]


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
