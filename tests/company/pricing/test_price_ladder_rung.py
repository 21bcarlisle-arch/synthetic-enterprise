"""The price ladder's rung: what it delivers, what it is scored at, and what still binds it.

WHY THIS FILE EXISTS
--------------------
`docs/design/THE_VALUE_CYCLE_REALISED_AB.md`, 2026-08-27, item 2: a price ladder is "the only
design here that can separate 'wrong level' from 'wrong reference'". It works only if two
properties hold, and both are the kind that look obviously true and are not:

  1. **RUNG ZERO IS THE FLAT RULE, EXACTLY.** The whole ladder is read against a null rung whose
     job is to reproduce the flat-rules control arm. If the rung were parameterised as
     `k x chosen` rather than `flat + k x (chosen - flat)`, rung zero would be a ZERO-margin
     offer -- a price the control never made, in a world the control never produced -- and the
     null check would be comparing the ladder against something else.

  2. **THE RUNG IS SCORED AT THE PRICE IT DELIVERS.** If the multiplier were applied to the arm's
     uplift AFTER `decide_margin` returned, `believed_p_retain` would still describe the UNSCALED
     price: the believed leg of the ladder would be flat across every rung while the realised leg
     moved, and the measured "the company cannot see the response" would be an artefact of the
     plumbing. This is the same defect the 2026-08-26 ceiling repair closed from the other side
     ("the two sides of that comparison were different prices") and it is R15's tautology shape
     -- a believed slope of zero that cannot be anything else.

Both are asserted BEHAVIOURALLY below, and the mutation that breaks each is named at the
assertion. The third property -- that the multiplier reaches the decision from the RUN'S policy
rather than a pinned constant -- is not this file's: it is
`tests/company/policy/test_policy_field_consumption.py`, which drives the real wall door.
"""
from __future__ import annotations

import pytest

from company.pricing.value_based_renewal import (
    TARGET_MARGIN_GBP_PER_MWH,
    decide_margin,
)

#: One account the arm has an opinion about. The rate is well above the flat rule's answer so the
#: arm's chosen margin is comfortably interior -- a rung ladder over an endpoint-bound decision
#: would move nothing and every assertion below would pass vacuously.
ACCOUNT = dict(
    customer_id="LADDER-1",
    arm="value_based",
    current_rate_gbp_per_mwh=150.0,
    base_rate_gbp_per_mwh=120.0,
    eac_kwh=3000.0,
    tenure_years=2.0,
    cost_to_serve_gbp_per_year=90.0,
    renewal_year=2018,
)


def _at(k: float, **over):
    return decide_margin(ladder_multiplier=k, **{**ACCOUNT, **over})


def test_rung_zero_delivers_the_flat_rule_exactly():
    """THE NULL RUNG. Not "close to" the flat rule -- the flat rule, to the last decimal, because
    the ladder's only structural control is that rung zero reproduces the flat-rules control arm's
    world.

    MUTATION: parameterise the rung as `k x chosen` instead of `flat + k x (chosen - flat)` and
    this reds at 0.0 != 2.0.
    """
    zero = _at(0.0)
    assert zero.margin_gbp_per_mwh == pytest.approx(TARGET_MARGIN_GBP_PER_MWH, abs=1e-12)
    # And it is a RUNG, not a decision: the arm's own answer is carried unscaled beside it, so a
    # reader is never shown the flat rule as though the arm had chosen it.
    assert zero.unscaled_margin_gbp_per_mwh > TARGET_MARGIN_GBP_PER_MWH
    assert zero.ladder_multiplier == 0.0


def test_rung_one_is_the_arm_untouched():
    """A ladder that perturbs its own k=1 rung is not measuring the arm the A/B published.

    MUTATION: apply the scaling unconditionally (drop the `abs(k - 1.0) > 1e-12` guard) and any
    re-scoring or re-clamping at k=1 shows up here.
    """
    plain = decide_margin(**ACCOUNT)
    one = _at(1.0)
    assert one.margin_gbp_per_mwh == pytest.approx(plain.margin_gbp_per_mwh, abs=1e-12)
    assert one.p_retain == pytest.approx(plain.p_retain, abs=1e-12)
    assert one.expected_value_gbp == pytest.approx(plain.expected_value_gbp, abs=1e-12)


def test_the_belief_is_taken_at_the_rung_and_not_at_the_unscaled_choice():
    """THE ASSERTION THE WHOLE MEASUREMENT RESTS ON.

    The company's believed retention must MOVE with the rung, because the rung is the price the
    customer is offered. A believed leg that does not move is the flat-slope artefact this file's
    docstring names.

    MUTATION: move the scaling out of `decide_margin` and into the rate chain (multiply
    `arm_uplift.uplift_gbp_per_mwh` after the fact). `margin_gbp_per_mwh` still ladders; every
    `p_retain` below collapses to the same number and this reds on the strict inequality.
    """
    p = [(_at(k).margin_gbp_per_mwh, _at(k).p_retain) for k in (0.0, 0.5, 1.0, 1.5)]
    margins = [m for m, _ in p]
    retains = [r for _, r in p]
    assert margins == sorted(margins), "a rising rung must deliver a rising margin"
    assert len(set(round(r, 9) for r in retains)) == len(retains), (
        "every rung returned the same believed retention -- the belief is being taken at a price "
        "the customer is not offered")
    assert all(a > b for a, b in zip(retains, retains[1:])), (
        "believed retention must FALL as the offered price rises")


def test_the_lawful_ceiling_still_binds_the_rung_and_says_so():
    """A rung is an experiment, the price cap is a wall. A rung above it must be cut back HERE --
    so that the scored price and the delivered price stay the same number -- and flagged, so a
    flat top of the ladder is not read as the world refusing to respond.

    MUTATION: drop the clamp and `ladder_ceiling_clamped` never fires while the delivered rate
    sails past `max_offered_rate_gbp_per_mwh`.
    """
    ceiling = 180.0
    high = _at(3.0, max_offered_rate_gbp_per_mwh=ceiling)
    assert high.ladder_ceiling_clamped is True
    assert high.offered_rate_gbp_per_mwh == pytest.approx(ceiling, abs=1e-9)
    # And an unclamped rung under the same ceiling does NOT claim to have been clamped -- the flag
    # has to be able to be False for the True to mean anything.
    low = _at(0.25, max_offered_rate_gbp_per_mwh=ceiling)
    assert low.ladder_ceiling_clamped is False
    assert low.offered_rate_gbp_per_mwh < ceiling


def test_a_rung_past_the_companys_own_evidence_is_priced_and_flagged_not_refused():
    """The support bound stops the arm CHOOSING a price it cannot predict. It does not stop a
    ladder ASKING at one -- that region is the only place the two legs can be told apart by
    something other than their level -- so the rung is delivered and the state is reported.

    MUTATION: clamp the rung to `ceiling_from_support` as well and the flag becomes structurally
    unreachable (R15 fail-silent: the one field telling a reader the believed leg is an
    extrapolation could never fire).
    """
    far = _at(3.0)
    assert far.ladder_above_support_bound is True
    assert far.margin_gbp_per_mwh > _at(1.0).margin_gbp_per_mwh
    assert _at(1.0).ladder_above_support_bound is False


def test_both_price_references_are_carried_out_of_the_decision():
    """THE COMPANY'S REFERENCE, published per decision so the world's can be put beside it.

    `rate_increase_pct` is a delta against the customer's OWN prior rate -- the quantity
    `estimate_churn_probability` keys on -- and it is structurally incapable of containing the SVT
    level the world keys on. That is the point: the artefact publishes both and the divergence is
    a count rather than something a reader has to infer from a bucket table.
    """
    one = _at(1.0)
    assert one.current_rate_gbp_per_mwh == pytest.approx(150.0)
    assert one.offered_rate_gbp_per_mwh == pytest.approx(120.0 + one.margin_gbp_per_mwh)
    assert one.rate_increase_pct == pytest.approx(
        100.0 * (one.offered_rate_gbp_per_mwh - 150.0) / 150.0)
    # It ladders with the rung, and at rung zero it is the flat rule's own position -- which on
    # this account is a price CUT, and the sign is load-bearing: the reference-divergence count
    # keys on it.
    assert _at(0.0).rate_increase_pct < 0.0 < one.rate_increase_pct


def test_the_default_multiplier_changes_nothing():
    """Every existing caller -- including both arms of the standing realised A/B -- must be
    byte-identical to before this field existed."""
    assert decide_margin(**ACCOUNT).ladder_multiplier == 1.0
    assert decide_margin(**ACCOUNT).ladder_ceiling_clamped is False
    assert decide_margin(**ACCOUNT).ladder_above_support_bound is False
