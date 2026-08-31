"""SIM-side churn adjustment for satisfaction (Gap 3 Dim 4).

Satisfaction-based churn multiplier applied to the SIM ground-truth churn
probability before retention modifier. Analogous to switching_propensity.py
for income stress.

This operates at the SIM physics layer -- NOT visible to the company. The
ceiling it clamps to is the WORLD's own (`simulation/churn_ceiling.py`); it
used to be the company's `saas.churn_model.MAX_BILL_SHOCK_CHURN_PROBABILITY`, which made
the company's belief about the ceiling constitute the ceiling. See the
register's §3g.
"""
from __future__ import annotations

from simulation.churn_ceiling import WORLD_MAX_CHURN_PROBABILITY

_HIGH_SATISFACTION_THRESHOLD = 0.80
_LOW_SATISFACTION_THRESHOLD = 0.50

#: NAMED SIMPLIFICATION, AND THE ONLY UNSOURCED NUMBERS ON THIS PAGE. Nothing in the knowledge
#: layer establishes the DOSE -- how much a unit of dissatisfaction converts into switching. These
#: two are inherited from the module's first draft and carry no citation. To do it properly:
#: a published dose-response between service experience and supplier switching, which the Ofgem
#: Consumer Impacts and Consumer Satisfaction surveys do not currently give (they publish
#: satisfaction levels and switching rates, never the two crossed at the individual level).
#: Registered in `WORKER_PREREGISTRATION_WHAT_A_CONTINUOUS_SATISFACTION_RESPONSE_MUST_SHOW_2026-08-31.md`.
_HIGH_SATISFACTION_MULTIPLIER = 0.85
_LOW_SATISFACTION_MULTIPLIER = 1.30


def satisfaction_churn_multiplier(satisfaction_score: float) -> float:
    """Churn multiplier for one household's satisfaction, CONTINUOUS between the two thresholds.

    WHY THIS IS NOT THREE STEPS ANY MORE (2026-08-31, ladder rung 3).
    `sim_satisfaction` produces a continuous per-household score -- 434 distinct values across the
    captured book -- and this function used to collapse it to THREE, with 88% of the book on the
    same one. Measured consequence: `sim_dissatisfaction_response` was tied on **92.0% of
    within-stratum (departed, stayed) pairs** and contributed **+0.0000** to the world's rung-3
    discrimination. Not small; zero. A tied pair scores 0.5 in a rank statistic whatever hazard is
    attached to it, so the variable could not distinguish anyone at any magnitude.

    That is heterogeneity the population already had, discarded in transit: the July repair that
    made satisfaction continuous landed on the PRODUCER and stopped at this consumer.

    NO NEW CONSTANT IS INTRODUCED, AND THE NEUTRAL POINT IS NOT CHOSEN. The straight line between
    the two declared endpoints passes through `sim_satisfaction.BASELINE_SATISFACTION` = 0.70 at
    exactly 1.00 -- `1.30 + (0.85 - 1.30) x (0.20 / 0.30) = 1.00`. A household with no bill shock,
    no income stress and no tenure bonus is neutral, as it always was. The three anchors this model
    already declares are mutually consistent under a line, and the step function was the thing that
    broke that consistency by flattening everyone between them onto the neutral value.

    THE LEVEL CONSEQUENCE, STATED RATHER THAN DISCOVERED. The population-mean multiplier moves
    1.03323 -> 1.10154, **+6.6%**, because the book sits BELOW the model's own baseline satisfaction
    (mean 0.6264) and the steps were rounding all of them up to neutral. This is a fidelity change
    decided blind to company results (R13 baseline), and it moves AGAINST the company -- a leakier
    book. It is not a level dial: nothing here was chosen to hit a number.

    WHAT IS STILL WRONG AND IS FILED, NOT FIXED. The thresholds put 0.6% of the book above 0.80 and
    11.4% below 0.50, against a published Wave 20 distribution of 38% very satisfied and 6%
    dissatisfied. Whether that is a mis-calibration of the cuts or a mis-mapping from a 5-point
    Likert to this 0-1 latent score is NOT established, and picking one would be inventing the
    answer. Named simplification; see the pre-registration.

    MUTATION: return a constant, or re-introduce a bucket, and
    `test_satisfaction_reaches_the_hazard_as_itself` reds on the tie fraction rather than on any
    particular value -- so re-aiming the thresholds or the dose passes it, and flattening does not.
    """
    if satisfaction_score >= _HIGH_SATISFACTION_THRESHOLD:
        return _HIGH_SATISFACTION_MULTIPLIER
    if satisfaction_score <= _LOW_SATISFACTION_THRESHOLD:
        return _LOW_SATISFACTION_MULTIPLIER
    span = _HIGH_SATISFACTION_THRESHOLD - _LOW_SATISFACTION_THRESHOLD
    fraction = (satisfaction_score - _LOW_SATISFACTION_THRESHOLD) / span
    return _LOW_SATISFACTION_MULTIPLIER + (
        _HIGH_SATISFACTION_MULTIPLIER - _LOW_SATISFACTION_MULTIPLIER
    ) * fraction


def adjust_churn_for_satisfaction(
    base_churn_probability: float,
    satisfaction_score: float,
) -> float:
    """Return adjusted churn probability after applying satisfaction multiplier."""
    multiplier = satisfaction_churn_multiplier(satisfaction_score)
    return min(base_churn_probability * multiplier, WORLD_MAX_CHURN_PROBABILITY)
