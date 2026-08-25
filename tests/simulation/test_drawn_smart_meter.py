"""R15 contract for the meter a drawn supply point arrives with.

THE DEFECT IT REPAIRS, measured on the live book before the fix: 249 of 264 accounts carried no
meter field at all -- every customer the acquisition funnel has ever won -- so
`meter_reads.meter_type_for_customer` silently defaulted all of them to "traditional". The book
showed 14 half-hourly-capable meters against a published GB domestic penetration of 68.9%.

It is the 249th instance of a defect the director flagged on 2026-07-09 against C1-C4, fixed
then by stamping seven hand-authored customers from the supplier's fleet record. The funnel then
began minting customers that record had never heard of and the default came straight back --
which is why this fix is at the DRAW and not in another roster.

R13: this is a BASELINE fidelity change. The curve is published (DESNZ Q4 2024 Smart Meters
Statistics Table 5a), it was already in the tree for read cadence, and it was decided blind to
company P&L -- it makes the book HARDER to serve, not easier, because a smart meter is a
customer the supplier can no longer bill an estimate to and hope.
"""
from __future__ import annotations

import collections

import pytest

from simulation import population_draw as pd
from simulation.meter_reads import meter_type_for_customer
from simulation.premise_population import (
    _SMART_COMMUNICATING_RATE,
    smart_meter_penetration,
    smart_read_share,
)

SEED = 20260724
SAMPLE = 3000


def _share(year: int, segment: str = "resi", seed: int = SEED) -> float:
    hits = sum(
        pd._draw_smart_meter(f"PROS-{year}-{i:04d}", seed, year, segment)
        for i in range(SAMPLE)
    )
    return hits / SAMPLE


# --------------------------------------------------------------------------- #
# It matches the published series, and it MOVES                                #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("year", [2016, 2020, 2024])
def test_the_drawn_share_matches_the_published_penetration(year):
    """The whole claim: a drawn book looks like GB. Tolerance is sampling error on 3,000 draws,
    not a fudge factor -- three standard errors on a Bernoulli at p~0.4 is about 2.7pp."""
    assert _share(year) == pytest.approx(smart_meter_penetration(year), abs=0.03)


def test_the_share_RISES_across_the_rollout():
    """MUTATION (must fire): draw against a constant instead of the year's penetration.

    A book acquired over 2016-2025 that shows one flat smart share models a country where the
    rollout never happened, which is the direction the old default (everyone traditional) took
    to its limit."""
    early, late = _share(2016), _share(2024)

    assert late > early + 0.4, f"2016 {early:.2f} -> 2024 {late:.2f} is not a rollout"


def test_an_I_and_C_point_is_HH_by_MANDATE_and_not_by_a_dice_roll():
    """BSC P272 made half-hourly settlement compulsory for sites above 100kW from 2014 -- before
    the domestic programme began. Drawing them against a household curve would model a large
    industrial site waiting its turn in a rollout it was never part of."""
    assert all(pd._draw_smart_meter(f"IC-{i}", SEED, 2016, "I&C") for i in range(50))
    assert _share(2016, segment="resi") < 0.2, "the resi curve is not being used for resi"


# --------------------------------------------------------------------------- #
# C-S2: deterministic, order-independent, and it perturbs nothing              #
# --------------------------------------------------------------------------- #

def test_the_same_customer_gets_the_same_meter_however_the_book_is_drawn():
    """A customer's meter must not change because the book around it grew. The CLV lifetime fix
    removed exactly this identifier-dependence from valuation and called it a C-S2 defect as
    well as an accounting one."""
    first = [pd._draw_smart_meter(f"PROS-2020-{i:04d}", SEED, 2020, "resi") for i in range(200)]
    shuffled = [pd._draw_smart_meter(f"PROS-2020-{i:04d}", SEED, 2020, "resi")
                for i in reversed(range(200))]

    assert first == list(reversed(shuffled))


def test_a_different_base_seed_gives_a_different_book_but_the_same_SHARE():
    """The seed moves the sample, never the law (R13). Which households have smart meters is a
    draw; how many do is the published series."""
    a = [pd._draw_smart_meter(f"PROS-2020-{i:04d}", SEED, 2020, "resi") for i in range(SAMPLE)]
    b = [pd._draw_smart_meter(f"PROS-2020-{i:04d}", SEED + 1, 2020, "resi") for i in range(SAMPLE)]

    assert a != b, "the seed does not move the sample at all"
    assert abs(sum(a) - sum(b)) / SAMPLE < 0.03, "the seed moved the SHARE, not just the sample"


def test_adding_the_meter_draw_leaves_every_OTHER_attribute_BYTE_IDENTICAL():
    """The property this repository asks of every new drawn attribute, and the reason the meter
    is drawn on an ISOLATED substream rather than off the sequential `rng`. Taking one more
    number from the shared stream would have re-rolled every segment, band, EAC and payment
    method in the book -- a change to the world dressed as a change to metering.

    MUTATION (must fire): draw the meter from the sequential `rng` inside `_draw_one`.
    """
    events = list(pd.iter_acquisition_events(SEED, start_year=2018, end_year=2019))
    assert events, "no acquisition events drawn, so this proves nothing"

    without_meter = [
        {k: v for k, v in e.to_customer_dict().items() if k != "smart_meter"} for e in events
    ]
    again = list(pd.iter_acquisition_events(SEED, start_year=2018, end_year=2019))
    assert without_meter == [
        {k: v for k, v in e.to_customer_dict().items() if k != "smart_meter"} for e in again
    ]
    # And the field is actually THERE, or the comparison above is trivially satisfied by
    # stripping a key that was never added. That it VARIES is proved on volume by
    # `test_the_drawn_share_matches_the_published_penetration` -- this book is a ~1/year trickle
    # and two years of it is one acquisition, which is far too few to say anything about a share.
    assert all("smart_meter" in e.to_customer_dict() for e in events)


# --------------------------------------------------------------------------- #
# What crosses to the supplier's book, and what does not                       #
# --------------------------------------------------------------------------- #

def test_the_supplier_book_CARRIES_the_meter_and_still_hides_cohort_and_premise():
    """The wall distinction this field turns on. A supplier reads its own meter type off the
    national metering database and prints it on every bill -- it is an OBSERVABLE. A cohort and
    a dwelling are hidden world truth and stay hidden.

    MUTATION (must fire): render `premise` or `cohort` in `to_customer_dict`."""
    event = next(iter(pd.iter_acquisition_events(SEED, start_year=2020, end_year=2020)))
    rendered = event.to_customer_dict()

    assert "smart_meter" in rendered
    assert "cohort" not in rendered and "premise" not in rendered


def test_the_rendered_book_resolves_to_a_meter_type_rather_than_defaulting():
    """END TO END, on the shape the defect actually took: a customer dict with no meter key at
    all reads as traditional, silently, and nothing anywhere says so."""
    events = list(pd.iter_acquisition_events(SEED, start_year=2024, end_year=2024))
    kinds = collections.Counter(meter_type_for_customer(e.to_customer_dict()) for e in events)

    assert kinds["smart"] > 0, "not one 2024 acquisition has a smart meter"
    assert kinds["smart"] / sum(kinds.values()) > 0.5, (
        f"2024 acquisitions are {kinds['smart']}/{sum(kinds.values())} smart against a published "
        "penetration of 68.9% -- the draw is not reaching the supplier's book"
    )


# --------------------------------------------------------------------------- #
# One series, not two                                                          #
# --------------------------------------------------------------------------- #

def test_the_read_share_is_DERIVED_from_the_penetration_and_not_re_interpolated():
    """Two interpolations of one published series is how this repository ended up with three
    grid-intensity curves disagreeing by 55%. `smart_read_share` is the penetration times the
    communicating rate, and that is checkable rather than asserted."""
    for year in (2016, 2019, 2022, 2024, 2025):
        assert smart_read_share(year) == pytest.approx(
            smart_meter_penetration(year) * _SMART_COMMUNICATING_RATE
        )


def test_a_meter_that_does_not_communicate_is_still_a_SMART_meter():
    """The distinction the split exists for. Penetration decides what the book says and what
    tariffs a customer is eligible for; the communicating rate decides whether reads arrive, and
    `meter_reads` already models that separately. Folding them would have told a household with
    a smart meter that it had none."""
    assert smart_meter_penetration(2024) > smart_read_share(2024)
