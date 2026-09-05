"""PB4: prepayment separated, and engagement given the antecedent a supplier could observe.

Each test names the defect it exists to catch. The atom's own brief (director, 2026-08-28): *"whether
a household enters a choice process at all is not how far price moves it once it does ... Modelling
one on the other's shape builds a world where never-switchers are also price-insensitive, and the
company will learn a relationship that does not exist."*
"""
from __future__ import annotations

import random
import statistics

from simulation.household_segments import (
    CIM_SWITCH_RATE_BY_CHANNEL,
    DIRECT_DEBIT_SHARE_BY_FUEL,
    FUEL_POVERTY_RATE_BY_CHANNEL,
    NON_DD_PREPAYMENT_SHARE,
    PaymentChannel,
    active_renewal_probability,
    active_renewal_probability_for_customer,
    engagement_level_for_customer,
    engagement_multiplier_for_channel,
    payment_channel_for_customer,
)

_CIDS = [f"CUST{i:05d}" for i in range(6000)]


def test_no_household_changed_direct_debit_status_when_prepayment_was_separated():
    """THE SAFETY PROPERTY OF THE WHOLE CHANGE.

    Prepayment was separated for an ENGAGEMENT reason. Six live consumers -- arrears, satisfaction,
    final-bill, phase2b, phase4c, opex -- key off whether a household pays by direct debit, and none
    of them asked for a change. The second draw is therefore taken ONLY on the non-DD branch, so a
    DD household consumes exactly the one number from exactly the stream it always consumed.

    The rejected alternative was delegating to `payment_behaviour_source.generate_payment_method`,
    which draws the same three categories from a DIFFERENT stream at the SAME DD anchor: that would
    have reshuffled 41% of the book's DD status while changing the DD share not at all.
    """
    def before(cid: str, fuel: str) -> bool:
        share = DIRECT_DEBIT_SHARE_BY_FUEL.get(fuel, DIRECT_DEBIT_SHARE_BY_FUEL["electricity"])
        return random.Random(f"paychannel_{cid}_{fuel}").random() < share

    for fuel in ("electricity", "gas"):
        for cid in _CIDS[:1500]:
            was_dd = before(cid, fuel)
            is_dd = payment_channel_for_customer(cid, fuel) is PaymentChannel.DIRECT_DEBIT
            assert was_dd == is_dd, f"{cid}/{fuel} changed direct-debit status"


def test_prepayment_is_drawn_at_the_published_share_and_actually_appears():
    """REACHABILITY FIRST. A three-member enum whose third member is never drawn would pass every
    test below about multipliers and rates while changing nothing about the world."""
    channels = [payment_channel_for_customer(c) for c in _CIDS]
    ppm = sum(1 for c in channels if c is PaymentChannel.PREPAYMENT) / len(channels)
    sc = sum(1 for c in channels if c is PaymentChannel.STANDARD_CREDIT) / len(channels)

    expected = (1.0 - DIRECT_DEBIT_SHARE_BY_FUEL["electricity"]) * NON_DD_PREPAYMENT_SHARE
    assert abs(ppm - expected) < 0.02, f"prepayment share {ppm:.3f} != published {expected:.3f}"
    assert abs(sc - expected) < 0.02, "the non-DD residual must divide 50/50, per Ofgem 13%/13%"


def test_the_fuel_poverty_rates_are_the_published_ones_and_not_their_average():
    """The blend existed ONLY because the bucket was merged: 0.204 was the unweighted mean of two
    rates DESNZ publishes separately. A repair that separated the bucket and kept the average would
    have carried the approximation forward for no reason."""
    assert FUEL_POVERTY_RATE_BY_CHANNEL[PaymentChannel.PREPAYMENT] == 0.223
    assert FUEL_POVERTY_RATE_BY_CHANNEL[PaymentChannel.STANDARD_CREDIT] == 0.185
    blended = (0.223 + 0.185) / 2
    assert FUEL_POVERTY_RATE_BY_CHANNEL[PaymentChannel.STANDARD_CREDIT] != blended


def test_the_engagement_multiplier_preserves_the_population_mean():
    """R12 AND THE BASELINE WALL. Adding a dimension must not re-level the book: the aggregate
    active-renewal rate is a diagnostic, never a target, and moving it here would be a level change
    made blind to the director's baseline as a side effect of something else.

    Measured THROUGH `active_renewal_probability_for_customer` rather than on the multiplier alone,
    because the clamp inside it is what would silently break mean-preservation if it ever bound.
    """
    before = [active_renewal_probability(engagement_level_for_customer(c)) for c in _CIDS]
    after = [active_renewal_probability_for_customer(c) for c in _CIDS]

    assert abs(statistics.fmean(after) - statistics.fmean(before)) < 0.005, (
        f"the book's aggregate engagement moved: {statistics.fmean(before):.5f} -> "
        f"{statistics.fmean(after):.5f}"
    )


def test_the_multiplier_actually_discriminates_or_the_atom_bought_nothing():
    """THE POINT OF PB4, and the failure that would look exactly like success.

    With prepayment folded into standard credit, the merged bucket's switching rate is
    indistinguishable from direct debit's 5.6% -- so wiring engagement to payment method in the OLD
    world produced ~1.0 for every household: a build that runs, passes, and encodes no signal.
    """
    ppm = engagement_multiplier_for_channel(PaymentChannel.PREPAYMENT)
    dd = engagement_multiplier_for_channel(PaymentChannel.DIRECT_DEBIT)

    assert ppm < 0.75 * dd, (
        f"prepayment ({ppm:.3f}) must shop materially less than direct debit ({dd:.3f}) -- "
        "Ofgem CIM w6 puts them at 3.1% and 5.6%"
    )


def test_two_households_of_the_same_archetype_differ_by_something_observable():
    """R1's actual claim: engagement must stop being a hash of the customer id.

    Before this, `active_renewal_probability_for_customer` was a pure function of the engagement
    archetype, which is `random.Random(f"engagement_{customer_id}")`. Two households in the same
    archetype were therefore identical, and no supplier could ever tell them apart -- the trait
    reached the world only where it set the outcome.
    """
    by_archetype: dict[tuple, set[float]] = {}
    for cid in _CIDS:
        key = (engagement_level_for_customer(cid), payment_channel_for_customer(cid))
        by_archetype.setdefault(key[0], set()).add(round(active_renewal_probability_for_customer(cid), 6))

    for level, probabilities in by_archetype.items():
        assert len(probabilities) > 1, (
            f"every {level} household still has one probability -- engagement is still unobservable"
        )


def test_the_cim_rates_are_the_ones_the_research_note_recorded():
    """Keyed to the published figures, so a later edit that 'tunes' engagement has to change a
    number that visibly disagrees with its own cited source."""
    assert CIM_SWITCH_RATE_BY_CHANNEL[PaymentChannel.DIRECT_DEBIT] == 0.056
    assert CIM_SWITCH_RATE_BY_CHANNEL[PaymentChannel.STANDARD_CREDIT] == 0.057
    assert CIM_SWITCH_RATE_BY_CHANNEL[PaymentChannel.PREPAYMENT] == 0.031


def test_engagement_is_now_recoverable_from_an_observable_and_provably_was_not():
    """THE ATOM'S FALSIFIER, run both ways round.

    R1's claim is not that engagement varies -- it always did -- but that the variation was
    STRUCTURALLY UNLEARNABLE: it reached the world only where it set the outcome, so no supplier
    could recover it. This scores the same instrument the R1 ceiling uses against the same
    observable, on the world BEFORE this change and AFTER it:

        before   held-out -0.0106  against a null of 0.0410   -> does not clear
        after    held-out +0.1192  against a null of 0.0403   -> clears by ~3x

    Both legs matter. Without the BEFORE leg this asserts only that a function of a variable
    correlates with that variable, which is arithmetic; the claim being made is that the world
    changed, and that needs the world's previous answer measured the same way.

    Held-out (+0.1192) sits alongside in-sample (+0.1172) rather than above it, which is the
    signature of a fit reading signal. The inverse -- held-out ABOVE in-sample -- is what exposed
    the R1 ceiling's own 2-D measurement as noise, and is checked here for the same reason.
    """
    from tools import r1_inference_ceiling as ceiling

    encoded = {"direct_debit": 0.0, "standard_credit": 1.0, "prepayment": 2.0}
    xs = [encoded[payment_channel_for_customer(c).value] for c in _CIDS[:3000]]
    after = [active_renewal_probability_for_customer(c) for c in _CIDS[:3000]]
    before = [active_renewal_probability(engagement_level_for_customer(c)) for c in _CIDS[:3000]]

    got_after = ceiling.score_one_feature(xs, after, cells=2)
    got_before = ceiling.score_one_feature(xs, before, cells=2)

    assert got_before["clears"] is False, (
        "engagement must have been UNRECOVERABLE from payment method before this atom, or the "
        "atom's premise is wrong and the AFTER result means nothing"
    )
    assert got_after["clears"] is True, "engagement must now clear its own noise floor"
    assert got_after["held_out"] <= got_after["in_sample"] * 1.5, (
        "held-out far above in-sample is the signature of a fit reading noise, not signal"
    )
