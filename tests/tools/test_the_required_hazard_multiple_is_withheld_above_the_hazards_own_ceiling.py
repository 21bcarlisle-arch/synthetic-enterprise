"""The composition counterfactual's required hazard multiple is withheld where it is not a plan.

DEFECT THIS EXISTS FOR: `hazard_multiple_still_required_at_band_low` divides by `svt_pp`, which is
`100 x world_hazard x target` exactly -- so its denominator IS the world's MEASURED SVT hazard and
has no lower bound. As that hazard falls the multiple has no upper bound, and the site's previous
guard, `svt_pp > 0`, is a degenerate-input check rather than a statement about the interval: it
fires on the one input nobody meets and publishes 4 and 4,000 under the same plan-grammar name.

WHY THE CEILING IS THE BAR AND NOT A NUMBER PICKED HERE. `_SVT_FACTOR_CEILINGS["hazard"]` is this
file's own established ceiling for the quantity -- `years_a_factor_could_close_alone` already
divides by it -- and `tools/published_route_split.py` already multiplies the world hazard by this
very multiple to form `H_joint`. A multiple above the ceiling ratio puts the hazard somewhere no
world runs it, so buying it is not a plan. Nothing in this control chooses a threshold.

THE FIRST LEG IS THE ONE THAT MATTERS, and it is here because of the trap `CLAUDE.md` names: every
test of a guard asks "does it refuse correctly", and a guard that refuses EVERYTHING passes all of
them. On the real record the gate withholds nothing -- ceiling multiples run 4.82 to 10.16 against
requirements of 0.72 to 1.89 -- so a suite that only checked the published artefact would be green
against a gate wired shut, and green against no gate at all. `test_the_partition_is_WHOLE` asserts
both sides are reachable from one call before any leg asserts what either side does.
"""
from __future__ import annotations

import pytest

from simulation.churn_ceiling import WORLD_MAX_CHURN_PROBABILITY
from tools.fit_year_level_anchor import _composition_accounting

#: A YEAR'S WORTH OF SHAPE, at the record's own scale. `lo` is a band low in pp of book and
#: `renewal_pp` the renewal route's contribution; `svt_pp` is what the SVT route carries, and it is
#: the only thing varied across these cases because it is the denominator.
BAND_LOW = 13.5
RENEWAL_PP = 1.0


def _ceiling_multiple(world_hazard: float) -> float:
    return WORLD_MAX_CHURN_PROBABILITY / world_hazard


def test_the_partition_is_WHOLE():
    """DEFECT: a gate that withholds everything, or nothing, and reads identical either way."""
    ceiling = _ceiling_multiple(0.13)
    published = _composition_accounting(9.0, RENEWAL_PP, BAND_LOW, ceiling)
    withheld = _composition_accounting(0.05, RENEWAL_PP, BAND_LOW, ceiling)
    empty = _composition_accounting(0.0, RENEWAL_PP, BAND_LOW, ceiling)

    assert published["hazard_multiple_still_required_at_band_low"] is not None
    assert withheld["hazard_multiple_still_required_at_band_low"] is None
    assert empty["hazard_multiple_still_required_at_band_low"] is None
    # THREE OUTCOMES AND NOT TWO: a published multiple, one withheld for exceeding the ceiling, and
    # one withheld because there is no hazard to multiply at all. The last two are different
    # sentences and the reasons must not collapse into one.
    assert (withheld["hazard_multiple_unavailable_because"]
            != empty["hazard_multiple_unavailable_because"])
    assert published["hazard_multiple_unavailable_because"] is None
    # AND EACH REASON NAMES ITS OWN CAUSE. Asserting only that the two strings DIFFER passes a
    # refusal gutted to the word "withheld" -- found by mutation, 2026-09-22, and this is the leg
    # that killed it. A refusal that does not say why is how a wrong refusal survives.
    assert "no expected departures" in empty["hazard_multiple_unavailable_because"]
    assert "ceiling multiple" in withheld["hazard_multiple_unavailable_because"]


def test_the_multiple_is_WITHHELD_above_the_ceiling_and_the_arithmetic_is_KEPT():
    """DEFECT: withholding the plan and losing the measurement with it."""
    ceiling = _ceiling_multiple(0.13)
    row = _composition_accounting(0.05, RENEWAL_PP, BAND_LOW, ceiling)

    assert row["hazard_multiple_still_required_at_band_low"] is None
    # The point estimate survives: "how far short is composition" is still answerable, and it is
    # only the PLAN reading the ceiling refuses.
    assert row["hazard_multiple_at_the_point_estimate"] == pytest.approx(
        (BAND_LOW - RENEWAL_PP) / 0.05, rel=1e-3)
    assert row["hazard_multiple_ceiling"] == pytest.approx(ceiling, rel=1e-3)
    # THE REFUSAL CARRIES BOTH NUMBERS A READER NEEDS TO CHECK IT -- what was required and what the
    # ceiling was. A refusal naming neither cannot be argued with, and a refusal that turns out to
    # be wrong is only discoverable through the figures it quotes.
    why = row["hazard_multiple_unavailable_because"]
    assert "not a plan" in why
    assert "{:.4g}".format(row["hazard_multiple_at_the_point_estimate"]) in why
    assert "{:.4g}".format(ceiling) in why


def test_the_multiple_is_PUBLISHED_where_it_is_reachable():
    """DEFECT: a gate wired shut, which every refusal test above would pass."""
    ceiling = _ceiling_multiple(0.13)
    row = _composition_accounting(9.0, RENEWAL_PP, BAND_LOW, ceiling)

    expected = (BAND_LOW - RENEWAL_PP) / 9.0
    assert row["hazard_multiple_still_required_at_band_low"] == pytest.approx(expected, rel=1e-3)
    assert row["hazard_multiple_at_the_point_estimate"] == pytest.approx(expected, rel=1e-3)
    assert row["hazard_multiple_unavailable_because"] is None


def test_the_gate_turns_on_the_HAZARD_and_not_on_the_multiple_alone():
    """DEFECT: keying the bar to a fixed number, which would move with no change in the world.

    THE SAME REQUIRED MULTIPLE, GRADED BOTH WAYS by the hazard it is multiplying. This is what
    makes the bar a statement about the world rather than about today's answer: a multiple of 6 is
    a plan in a year whose hazard is 0.09 (ceiling multiple 10.6) and is not one in a year whose
    hazard is 0.19 (ceiling multiple 5.0). A threshold pinned to the multiple could not tell those
    apart, and it is the flattering reading -- it would publish the second.
    """
    svt_pp = (BAND_LOW - RENEWAL_PP) / 6.0

    low_hazard = _composition_accounting(svt_pp, RENEWAL_PP, BAND_LOW, _ceiling_multiple(0.09))
    high_hazard = _composition_accounting(svt_pp, RENEWAL_PP, BAND_LOW, _ceiling_multiple(0.19))

    assert low_hazard["hazard_multiple_still_required_at_band_low"] is not None
    assert high_hazard["hazard_multiple_still_required_at_band_low"] is None
    # And the measurement is the SAME in both -- only its status as a plan differs.
    assert (low_hazard["hazard_multiple_at_the_point_estimate"]
            == high_hazard["hazard_multiple_at_the_point_estimate"])


def test_the_two_ACCOUNTINGS_cannot_drift():
    """DEFECT: one accounting gated and the other not, which is how this pair was written before.

    Both rows come from one helper now. Handing it the generous accounting's renewal figure and the
    consistent one's must produce rows of the same SHAPE, or a reader comparing them is comparing
    two different instruments.
    """
    ceiling = _ceiling_multiple(0.13)
    rescaled = _composition_accounting(9.0, 0.8, BAND_LOW, ceiling)
    held = _composition_accounting(9.0, 1.2, BAND_LOW, ceiling)

    assert set(rescaled) == set(held)
    # Holding the renewal route where it is is the MORE generous accounting, so it must require a
    # SMALLER multiple -- the direction is the check, not the values.
    assert (held["hazard_multiple_at_the_point_estimate"]
            < rescaled["hazard_multiple_at_the_point_estimate"])
