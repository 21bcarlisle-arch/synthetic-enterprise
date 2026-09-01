#!/usr/bin/env python3
"""The satisfaction score's composition must be able to reach its consumer's thresholds.

THE FALSIFIER THIS IS OWED, named by its own finding rather than invented here
(`WORKER_FINDING_THE_WORLD_CAN_PUNISH_BAD_SERVICE_BUT_BARELY_REWARD_GOOD_AND_A_HASH_DECIDES_WHO_
2026-08-30`, closing section): *"a control asserting 'the protective band is reachable' pins
today's answer, and a control asserting 'the score's maximum exceeds its highest threshold' is the
property. The second is what the repair should ship, keyed to the composition rather than to any
particular constant, so that lowering the ceiling or raising the threshold in future reds it."*

THE STATE IT WAS BUILT AGAINST. `sim_satisfaction_score` composes a baseline with four terms, of
which every one except tenure is zero or negative. Its ceiling is
`0.70 + 0.10 (max tenure) + 0.04 (max individual variation) = 0.84`, and its consumer's high
threshold is 0.80 — so the protective end was reachable only by a household with simultaneously
zero bill shocks, maximum tenure, low income stress, direct debit **and** a non-negative variation
term, which is the sign of a hash of the customer id. Measured on the live book at the time: 77 of
150 accounts could EVER reach it and the other 73 could not, at any tenure, with any bill history,
on any payment method.

WHY THIS IS NOT THE FINDING'S OWN ASSERTION. That finding's headline claim ("satisfaction is a
two-state variable in practice") was measured against a THREE-BAND STEP consumer, and the consumer
was made continuous the next day. The step is gone and the claim with it. What survives the repair
is narrower and is the thing tested here: **a composition whose reachable range does not span its
consumer's declared thresholds is a variable whose model cannot express one end of its own
response**, whether the response between them is a step or a line.

KEYED TO THE COMPOSITION AND TO THE CONSUMER, NOT TO EITHER'S NUMBERS. The bounds below are
computed by driving `sim_satisfaction_score` to its extremes through its public signature, and the
thresholds are imported from the consumer. Change a delta, add a term, move a threshold, cap the
score differently — this re-derives and stays meaningful. It is exactly the shape of control this
project's standing rule asks for: keyed to the property, never to today's answer.

WHAT IT DELIBERATELY DOES NOT ASSERT. Not that any particular share of the book lands in any band
— that is rung 1, it is currently failing for a reason this control cannot see (the score is
denominated in cohort satisfied-SHARE and read as a household level; see
`docs/design/LADDER_APPLIED_TO_SATISFACTION_2026-09-01.md`), and pinning a share here would be
pinning today's answer at the very address where the repair has to move it.
"""
from __future__ import annotations

import itertools

from simulation.household import IncomeStress
from simulation.household_segments import PaymentChannel
from simulation.satisfaction_churn import (
    _HIGH_SATISFACTION_THRESHOLD,
    _LOW_SATISFACTION_THRESHOLD,
    satisfaction_churn_multiplier,
)
from simulation.sim_satisfaction import _individual_variation, sim_satisfaction_score

#: Enough customer ids to find both signs of the variation term. It is a hash, so a handful is
#: plenty and a floor below asserts that both ends were actually observed rather than assumed.
_IDS = tuple(f"probe-{i}" for i in range(64))

#: Tenure years spanning zero to past the model's own cap, so the bonus is exercised at both ends
#: without this file knowing what the cap is.
_TENURE = (0.0, 1.0, 5.0, 25.0)

#: Bill-shock counts spanning none to many, same argument.
_SHOCKS = (0, 1, 3, 12)


def _reachable_range() -> tuple[float, float]:
    """The (min, max) the composition can actually produce, driven through its own signature."""
    scores = [
        sim_satisfaction_score(shocks, tenure, stress, channel, customer_id)
        for shocks, tenure, stress, channel, customer_id in itertools.product(
            _SHOCKS, _TENURE, IncomeStress, PaymentChannel, _IDS
        )
    ]
    assert len(scores) >= 1_000, (
        f"the probe swept only {len(scores)} combinations — a reachability control that sweeps "
        "nothing reports a reachable range exactly like one that sweeps everything"
    )
    return min(scores), max(scores)


def test_the_scores_reachable_maximum_clears_its_consumers_high_threshold():
    """THE PROPERTY. A model that cannot reach the top of its own response curve cannot express a
    satisfied household at all, and the world then systematically understates the return on the
    company's own service investment — which is the wrong bias for a project whose thesis is that
    the company creates value rather than transferring it."""
    _low, high = _reachable_range()
    assert high >= _HIGH_SATISFACTION_THRESHOLD, (
        f"the satisfaction score's reachable maximum is {high:.4f} and its consumer's high "
        f"threshold is {_HIGH_SATISFACTION_THRESHOLD:.4f}. No household can reach the protective "
        "end of the response, so the world can punish bad service and cannot reward good. Repair "
        "the COMPOSITION (a positive term for something a supplier can do) rather than the "
        "threshold — lowering the threshold makes this green while leaving the score with no way "
        "to express a satisfied customer, which is a control pinned to today's answer."
    )


def test_the_scores_reachable_minimum_clears_its_consumers_low_threshold():
    """The other end, and it is not symmetry for its own sake. If the punitive threshold were
    unreachable the world could not express a household that has had a bad time either, and the
    same one-sidedness would be hiding at the opposite end where nobody was looking for it."""
    low, _high = _reachable_range()
    assert low <= _LOW_SATISFACTION_THRESHOLD, (
        f"the satisfaction score's reachable minimum is {low:.4f} and its consumer's low "
        f"threshold is {_LOW_SATISFACTION_THRESHOLD:.4f}. No household can reach the punitive end "
        "of the response."
    )


def test_both_extremes_of_the_response_are_actually_produced_by_the_consumer():
    """Reachability of the SCORE is not reachability of the RESPONSE. The consumer clamps outside
    its thresholds, so a score that clears a threshold must also produce the multiplier that
    threshold declares — otherwise this file would be asserting a property of one module while the
    thing it exists to protect lives in the other."""
    low, high = _reachable_range()
    assert satisfaction_churn_multiplier(high) < satisfaction_churn_multiplier(low), (
        "the reachable extremes of the score do not produce different churn multipliers, so "
        "satisfaction reaches the hazard as a constant however well the score itself varies"
    )


def test_MUTATION_the_probe_observes_both_signs_of_the_individual_variation():
    """The reachability result leans on the per-customer term being able to help as well as hurt.
    If every probed id happened to hash negative, the maximum above would understate the ceiling
    and this file would red on a world that is fine — the direction that gets a control deleted."""
    values = [_individual_variation(i) for i in _IDS]
    assert max(values) > 0 > min(values), (
        "the probe ids do not span both signs of the individual-variation term, so the reachable "
        "maximum is not the composition's maximum"
    )
