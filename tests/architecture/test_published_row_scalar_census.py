"""The census that finds a scalar copy of a published row must be able to find one.

WHAT THIS CONTROLS, and it is deliberately not the count. A ratchet on "how many collisions are
there today" is keyed to the answer, and this project has learned what that costs: it goes red
when the code becomes MORE honest (a constant renamed to declare its unit ENTERS the ranked
population) and stays green when the claim rots. What must not rot is the census's REACH -- the
property that it can still see the shape it was built for. That is what is asserted here.

THE POISON ROUND IS THE FIRST TEST AND IT IS NOT DECORATION. `tools/published_row_scalar_census`
exists because `_CAPACITY_MARKET_GBP_PER_KW_YR = 75.0` in `company/market/flexibility_potential`
was a scalar copy of one published Capacity Market clearing price, was the third home of that
number, disagreed with the other two, and did GBP 930/household/year of damage -- and every census
in the repo was blind to it. A census that reports zero because it cannot see is indistinguishable
from a census that reports zero because there is nothing there. So the historical defect is fed
back in, and if it is not found, this file fails.
"""
from __future__ import annotations

from tools import published_row_scalar_census as census_tool

#: The constant exactly as it stood in `company/market/flexibility_potential.py` before it came
#: off on 2026-09-07 (commit 8c1ffe816). Reconstructed rather than read from git so the control
#: does not depend on history staying reachable.
POISON = census_tool.Constant(
    module="company/market/flexibility_potential.py",
    name="_CAPACITY_MARKET_GBP_PER_KW_YR",
    lineno=1,
    value=75.0,
    shape="SCALAR",
)


def test_the_census_finds_the_scalar_copy_that_every_other_census_was_blind_to():
    """POISON ROUND. Defect: the pass reports nothing because it reaches nothing."""
    rows = census_tool.published_rows()
    hits = [h for h in census_tool.census([POISON], rows) if h.scale == 1.0]

    assert hits, (
        "the census cannot see _CAPACITY_MARKET_GBP_PER_KW_YR = 75.0, which is the exact defect "
        "it was built for -- every count it reports is therefore uninterpretable"
    )
    pointers = {(h.published.artefact, h.published.pointer) for h in hits}
    assert (
        "regulatory/capacity_market_auction_results.json",
        "clearing_prices/6/t1_gbp_per_kw_year",
    ) in pointers


def test_the_poison_is_the_most_specific_collision_the_commons_can_produce():
    """Defect: specificity ranks the damage case DOWN, so the reader never reaches it.

    Specificity is the census's ranking axis, and a ranking that buries the motivating case is
    the "discovery narrower than the thing it governs" defect wearing a rank instead of a filter.
    """
    rows = census_tool.published_rows()
    assert census_tool.specificity(POISON.value, rows) == 1


def test_a_module_level_scalar_is_discovered_at_all():
    """Defect: the pass rediscovers only year-keyed dicts, which the old census already saw.

    This is the whole point of the file. If SCALAR never appears in the discovered population,
    the new census has been quietly narrowed back to the old one's subject.
    """
    constants = census_tool.module_constants()
    shapes = {c.shape for c in constants}
    assert "SCALAR" in shapes, "the census discovers no bare scalars -- it is the old census again"
    assert len(shapes) > 1, "the census discovers ONLY scalars -- container-held rows went blind"


def test_units_agreeing_is_a_partition_both_of_whose_legs_are_reachable():
    """Defect: `units_agree` answers one way for everything, so the ranking sorts nothing.

    One control over the WHOLE partition, not a leg each: a discriminator that says False to
    every pair passes any number of "it correctly declined" assertions, and this project has
    entered that trap through three different doors in one afternoon.
    """
    rows = census_tool.published_rows()
    hits = [h for h in census_tool.census(None, rows) if h.scale == 1.0]

    agreeing = [h for h in hits if census_tool.units_agree(h)]
    unranked = [h for h in hits if not census_tool.units_agree(h)]
    assert agreeing and unranked, (
        f"units_agree is not a partition: {len(agreeing)} agree, {len(unranked)} unranked"
    )


def test_an_unnamed_unit_is_unranked_and_never_silently_agreeing():
    """Defect: the unit vocabulary fails OPEN, so two numbers that name nothing 'agree'.

    A constant called `_X` and a published key called `q` must not rank as the same quantity.
    Fail-closed is the property; without it the ranked population fills with noise and the
    reader stops reading it, which is how a census dies without ever going red.
    """
    assert census_tool.unit_signature("_X") == frozenset()
    assert census_tool.unit_signature("some_unrecognised_key") == frozenset()

    unnamed = census_tool.Hit(
        constant=census_tool.Constant("company/x.py", "_X", 1, 75.0, "SCALAR"),
        published=census_tool.Published("regulatory/a.json", "q", 75.0),
        scale=1.0,
    )
    assert not census_tool.units_agree(unnamed)


def test_within_rounding_admits_a_transcribed_copy_and_refuses_a_different_number():
    """Defect: the tolerance is absolute again, so a coarse value swallows a band.

    Both failed drafts are pinned here as the thing that must stay refused. The first read
    "within rounding" as half a unit in the published row's last decimal place, so an integer
    `15` admitted everything in [14.5, 15.5]. The second compared at whichever side claimed
    fewer decimals, so a constant written `3.0` admitted everything in [2.5, 3.5].
    """
    # A copy transcribed to fewer places than the publisher stated is still a copy.
    assert census_tool._within_rounding(0.00695, 0.006948)
    assert census_tool._within_rounding(75.0, 75.0)

    # The two failed drafts, as refusals.
    assert not census_tool._within_rounding(15.4, 15.0), "draft 1: absolute half-unit on published"
    assert not census_tool._within_rounding(3.0, 3.2), "draft 2: absolute half-unit on candidate"


def test_a_year_is_not_a_row_on_either_side():
    """Defect: year keys enter as values and the census measures its own keys.

    2016..2025 appear as a key on nearly every published series and as a bound in nearly every
    module. Admitting them makes the population mostly self-collision.
    """
    assert not census_tool._interesting(2022.0)
    assert not census_tool._interesting(1.0)
    assert census_tool._interesting(75.0)
    assert census_tool._interesting(0.05)

    values = {row.value for row in census_tool.published_rows()}
    assert not any(2016.0 <= v <= 2025.0 and float(v).is_integer() for v in values)
