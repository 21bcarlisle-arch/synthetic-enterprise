"""A contact wakes households, never puts one to sleep, and moves each in its own direction (W2_39).

Each test names the defect it exists to catch. Mutations run against `simulation/contact_response.py`
before landing are recorded in the docstrings.
"""
from __future__ import annotations

import pytest

from simulation import contact_response as cr
from simulation.renewal_engagement import FTC_WITHDRAWAL_WINDOW, rolls_active_renewal

# A boundary outside the FTC withdrawal window, so a fixed deal existed to be taken.
_OPEN = "2019-03-01"


def test_the_trials_own_control_rate_comes_out_at_the_trials_contacted_rate():
    """DEFECT: the woken share drifts from the source it is derived from.

    Keyed to the published pair, not to 0.111 as a literal. MUTATION: `WOKEN_SHARE_AT_FIXED_TERM_END
    = 0.0` reds this.
    """
    got = cr.engaged_probability_after_contact(cr.EFTC_CONTROL_SWITCHING_SHARE, contacted=True)
    assert got == pytest.approx(cr.EFTC_CONTACTED_SWITCHING_SHARE)
    assert cr.engaged_probability_after_contact(0.19, contacted=False) == 0.19


def test_a_contact_wakes_some_households_and_leaves_others_and_puts_none_to_sleep():
    """DEFECT: the contacted roll is not coupled to the uncontacted one, so the pair is not a
    counterfactual and a contact can "unwake" a household that would have chosen anyway.

    The whole partition is asserted reachable first: a roll that woke everyone, or no one, would
    pass every per-branch check. MUTATION: seeding the contacted roll with a different string
    makes `slept` non-zero; `WOKEN_SHARE_AT_FIXED_TERM_END = 0.0` empties `woken`.
    """
    p = 0.15  # the world's PASSIVE archetype
    woken = slept = chose_anyway = inert_anyway = 0
    for i in range(4000):
        seed = f"hh{i}_1"
        before = rolls_active_renewal(_OPEN, seed, p)
        after = cr.rolls_active_renewal_after_contact(_OPEN, seed, p, contacted=True)
        woken += (not before) and after
        slept += before and not after
        chose_anyway += before and after
        inert_anyway += (not before) and not after
    assert woken and chose_anyway and inert_anyway, (woken, chose_anyway, inert_anyway)
    assert slept == 0
    expected = cr.WOKEN_SHARE_AT_FIXED_TERM_END * (1 - p) * 4000
    assert abs(woken - expected) < 4 * expected ** 0.5, (woken, expected)


def test_an_uncontacted_household_rolls_exactly_as_the_world_rolls_it_today():
    """DEFECT: introducing the module moves the baseline for every household it never contacts."""
    for i in range(500):
        seed = f"hh{i}_2"
        assert cr.rolls_active_renewal_after_contact(_OPEN, seed, 0.35, contacted=False) == \
            rolls_active_renewal(_OPEN, seed, 0.35)


def test_no_contact_wakes_a_household_when_there_was_no_fixed_deal_to_take():
    """DEFECT: a contact in 2022 conjures a choice the record says did not exist."""
    inside = FTC_WITHDRAWAL_WINDOW[0].isoformat()
    assert not any(
        cr.rolls_active_renewal_after_contact(inside, f"hh{i}_3", 0.65, contacted=True)
        for i in range(300))


def test_the_same_contact_moves_different_households_by_different_amounts():
    """DEFECT: the response is uniform, so targeting on effect and on risk score the same.

    The point of the atom (`next_best_action_and_cross_sell.md` §6.3, property 1).
    """
    lifts = {p: cr.engaged_probability_after_contact(p, True) - p for p in (0.02, 0.15, 0.65)}
    assert lifts[0.02] > lifts[0.15] > lifts[0.65] > 0


def test_a_contacts_effect_on_leaving_can_be_harmful_helpful_or_nothing():
    """DEFECT: the world has no sleeping dogs (the flat 0.20 cut can only ever help).

    All three signs asserted reachable, and a deeper offer (lower churn once engaged) does more.
    MUTATION: flipping the difference to `churn_if_inert - churn_if_engaged` reds the sign checks.
    """
    sleeping_dog = cr.departure_change_from_contact(0.15, churn_if_engaged=0.30, churn_if_inert=0.10)
    persuadable = cr.departure_change_from_contact(0.15, churn_if_engaged=0.05, churn_if_inert=0.10)
    unmoved = cr.departure_change_from_contact(0.15, churn_if_engaged=0.10, churn_if_inert=0.10)
    assert sleeping_dog > 0 > persuadable
    assert unmoved == 0
    deeper = cr.departure_change_from_contact(0.15, churn_if_engaged=0.02, churn_if_inert=0.10)
    assert deeper < persuadable


def test_a_non_probability_is_refused_with_its_value():
    with pytest.raises(ValueError, match="1.2"):
        cr.engaged_probability_after_contact(1.2, True)

