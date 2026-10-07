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



# ── Between boundaries, on default-tariff stock (PB4 R6) ─────────────────────────────────────────


@pytest.mark.parametrize("instrument,control,contacted", [
    ("cmol_supplier_letter",
     cr.CMOL_CONTROL_SWITCHING_SHARE, cr.CMOL_SUPPLIER_LETTER_SWITCHING_SHARE),
    ("cmoc_letter", cr.CMOC_CONTROL_SWITCHING_SHARE, cr.CMOC_CONTACTED_SWITCHING_SHARE),
    ("collective_switch",
     cr.COLLECTIVE_SWITCH_CONTROL_SWITCHING_SHARE, cr.COLLECTIVE_SWITCH_CONTACTED_SWITCHING_SHARE),
])
def test_each_svt_stock_woken_share_returns_its_own_trials_contacted_rate(
    instrument, control, contacted,
):
    """DEFECT: a woken share drifts from the published pair it is derived from, or is keyed to the
    wrong trial.

    A household whose every choice is a switch (`churn_if_choosing=1.0`), drifting at the trial's
    control rate, must switch at the trial's contacted rate. MUTATION: pointing the CMOC entry at
    the collective-switch pair reds the CMOC case.
    """
    got = cr.svt_departure_after_contact(
        instrument=instrument, p_drift=control, churn_if_choosing=1.0)
    assert got == pytest.approx(contacted)


def test_a_disengaged_households_elasticity_reaches_its_departure_once_it_is_woken_on_svt():
    """DEFECT (the R6 disqualifier): on SVT, a household's elasticity reaches no behaviour, so
    "a disengaged household is not assumed price-insensitive" is true of a weight nothing reads.

    The branch must be TAKEABLE first: at our premium, the more elastic household leaves more; at a
    discount, it leaves LESS (elasticity is two-sided, not spite); at parity it makes no difference.
    MUTATION: passing `1.0` instead of `elasticity` to `perceived_price_differential` reds all three
    inequalities.
    """
    def leave(premium, elasticity):
        c = cr.churn_if_choosing_off_svt(
            our_premium_pct=premium, elasticity=elasticity, annual_bill_gbp=1100.0,
            level_anchor=6.2)
        return cr.svt_departure_after_contact(
            instrument="collective_switch", p_drift=0.05, churn_if_choosing=c)

    assert leave(0.20, 2.5) > leave(0.20, 1.0) > leave(0.20, 0.3)
    assert leave(-0.10, 2.5) < leave(-0.10, 0.3)
    assert leave(0.0, 2.5) == pytest.approx(leave(0.0, 0.3))


def test_a_contact_never_lowers_this_segments_departure_and_without_waking_changes_nothing():
    """DEFECT: the drift is replaced rather than kept (a contact would put a drifter to sleep), or a
    woken household that re-fixes with us is counted as leaving.

    MUTATION: `return (1 - woken) * p_drift + woken * churn_if_choosing` reds the first assertion
    (a woken household below the drift would then pull the segment under it).
    """
    for instrument in cr.WOKEN_SHARE_OF_SVT_STOCK:
        assert cr.svt_departure_after_contact(
            instrument=instrument, p_drift=0.05, churn_if_choosing=0.01) >= 0.05
        assert cr.svt_departure_after_contact(
            instrument=instrument, p_drift=0.05, churn_if_choosing=0.0) == 0.05


def test_an_unsourced_instrument_is_refused_by_name():
    with pytest.raises(ValueError, match="text_message"):
        cr.svt_departure_after_contact(
            instrument="text_message", p_drift=0.05, churn_if_choosing=0.2)
