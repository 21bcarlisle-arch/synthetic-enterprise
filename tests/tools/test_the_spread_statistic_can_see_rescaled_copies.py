"""The instrument that answers "is the book a spread, or rescaled copies of one profile?"

This is the control on the measurement, not on the world. The published claim it carries is that
the fabric path's 8,911 pairs hold **zero** near-identical shapes while the legacy path holds
**1,773** — so the two things that must be true of the statistic are that it can see a duplicate at
all, and that it cannot be fooled by a level.

TWO PROPERTIES, AND THE SECOND IS THE WHOLE DESIGN.

1. `closest_pair`, not the mean, is what tests "rescaled copies". A mean can look healthy sitting on
   top of a duplicate — the legacy path's own numbers are the proof: mean 0.000747 reads as small
   rather than as broken, while its closest pair is 2e-08, two premises identical to eight decimal
   places.
2. `_normalised_daily` divides the level out. The director's framing: *"two households can differ by
   a factor of three in annual kWh and still have the SAME SHAPE — which is exactly what a rescaled
   national profile produces, and exactly what looks like variety until you normalise."* If
   normalisation stopped working, a book of rescaled copies would report a healthy spread, because
   the copies differ in level. **That is the failure this whole tool exists to prevent, and it would
   look like success.**

`spread` was two copies until 2026-09-17 — one in `measure`, one in `measure_book` — which is two
implementations of the statistic the comparison is made with. These legs exercise the single one.
"""
from __future__ import annotations

from tools import book_shape_spread as bss

#: A day that is not flat, so "same shape" is a real constraint rather than a tautology.
SHAPE_A = [1.0 + (i % 7) for i in range(bss.PERIODS_PER_DAY)]
SHAPE_B = [1.0 + ((i * 3) % 11) for i in range(bss.PERIODS_PER_DAY)]


def test_a_level_difference_is_not_a_shape_difference():
    """A premise using three times the energy on the same pattern normalises to the same shape.

    This is the premise of every number the tool publishes. Without it the measurement answers a
    question about size while claiming to answer one about shape.
    """
    big = [v * 3.0 for v in SHAPE_A]
    assert bss._normalised_daily(SHAPE_A) == bss._normalised_daily(big)
    assert abs(sum(bss._normalised_daily(big)) - 1.0) < 1e-12


def test_rescaled_copies_are_reported_as_identical_however_different_their_levels():
    """The legacy case, constructed: one profile at four scales is one shape, four times.

    The mean would be zero here too, but the mean is not the claim — `identical_pairs` and
    `closest_pair_distance` are what a reader quotes as "these are copies".
    """
    profiles = {f"x{i}": bss._normalised_daily([v * scale for v in SHAPE_A])
                for i, scale in enumerate((1.0, 2.5, 7.0, 0.3))}
    result = bss.spread(profiles)
    assert result["n_pairs"] == 6
    assert result["identical_pairs"] == 6
    assert result["near_identical_pairs"] == 6
    assert result["closest_pair_distance"] == 0.0


def test_distinct_shapes_are_not_reported_as_copies():
    """The other half of the partition: a statistic that called everything identical would pass
    the leg above and be worthless."""
    profiles = {"a": bss._normalised_daily(SHAPE_A), "b": bss._normalised_daily(SHAPE_B)}
    result = bss.spread(profiles)
    assert result["identical_pairs"] == 0
    assert result["near_identical_pairs"] == 0
    assert result["mean_abs_share_difference"] > 1e-3


def test_one_duplicate_pair_survives_a_healthy_average():
    """The defect the `closest_pair` field exists for, made explicit.

    Nine distinct shapes and one exact copy: the mean stays comfortable and the copy is still
    found. A reader watching only the mean would call this book a spread.
    """
    profiles = {f"s{i}": bss._normalised_daily([1.0 + ((i * j) % 13) for j in
                                                range(bss.PERIODS_PER_DAY)])
                for i in range(1, 10)}
    profiles["twin"] = dict(profiles)["s1"]
    result = bss.spread(profiles)
    assert result["mean_abs_share_difference"] > 1e-3, "the average should look healthy here"
    assert result["identical_pairs"] == 1
    assert result["closest_pair_distance"] == 0.0
    assert "twin" in result["closest_pair"] and "s1" in result["closest_pair"]


def test_a_single_profile_is_no_pairs_rather_than_a_spread_of_zero():
    """One premise has no pairwise distance. Reporting 0.0 would read as "perfect copies"."""
    result = bss.spread({"only": bss._normalised_daily(SHAPE_A)})
    assert result["n_pairs"] == 0
    assert "mean_abs_share_difference" not in result
    assert bss.spread({})["n_pairs"] == 0


def test_an_empty_day_normalises_to_zeros_rather_than_dividing_by_zero():
    """A premise with no demand must not take the measurement down, and must not be a shape."""
    assert bss._normalised_daily([0.0] * bss.PERIODS_PER_DAY) == [0.0] * bss.PERIODS_PER_DAY
