"""Company churn model incorporating payment behaviour score (Phase MY)
and satisfaction score (Phase NB).

Extends the bill-shock churn signal (saas/churn_model.py) with payment behaviour
and customer satisfaction. Uses only observable signals:
- bill_shock_count (billing records)
- BehaviourScore (payment records from PaymentBehaviourAnalytics)
- satisfaction_score (company/crm/satisfaction_accumulator.py)
No SIM internals accessed -- consistent with epistemic barrier.

CHURN_UPLIFT_BY_SCORE encodes the empirical relationship:
- EXCELLENT payers are loyal; slightly suppress churn probability
- CRITICAL payers are at high risk of default-before-departure or imminent leave

SATISFACTION_CHURN_UPLIFT encodes emotional dimension:
- Low satisfaction (<0.50) adds meaningful churn uplift
- High satisfaction (>=0.80) slightly suppresses churn (loyal, satisfied customer)
"""
from __future__ import annotations

from typing import Optional

from company.crm.payment_behaviour_analytics import BehaviourScore
from saas.churn_model import MAX_CHURN_PROBABILITY, churn_probability

CHURN_UPLIFT_BY_SCORE: dict[BehaviourScore, float] = {
    BehaviourScore.EXCELLENT: -0.02,
    BehaviourScore.GOOD:       0.00,
    BehaviourScore.FAIR:      +0.03,
    BehaviourScore.POOR:      +0.10,
    BehaviourScore.CRITICAL:  +0.20,
}

_HIGH_SATISFACTION_THRESHOLD = 0.80
_LOW_SATISFACTION_THRESHOLD = 0.50
_HIGH_SATISFACTION_UPLIFT = -0.02
_LOW_SATISFACTION_UPLIFT = +0.10


def _satisfaction_uplift(satisfaction_score: float | None) -> float:
    """Return churn uplift from satisfaction score (None -> 0.0)."""
    if satisfaction_score is None:
        return 0.0
    if satisfaction_score >= _HIGH_SATISFACTION_THRESHOLD:
        return _HIGH_SATISFACTION_UPLIFT
    if satisfaction_score < _LOW_SATISFACTION_THRESHOLD:
        return _LOW_SATISFACTION_UPLIFT
    return 0.0


def combined_churn_probability(
    bill_shock_count: int,
    behaviour_score: Optional[BehaviourScore] = None,
    satisfaction_score: Optional[float] = None,
) -> float:
    """Return combined churn probability from bill shocks + payment behaviour + satisfaction.

    base = churn_probability(bill_shock_count) from saas/churn_model.py
    payment_uplift = CHURN_UPLIFT_BY_SCORE[behaviour_score] (zero if None)
    satisfaction_uplift = function of satisfaction_score (zero if None)
    result capped at MAX_CHURN_PROBABILITY (0.95).
    """
    base = churn_probability(bill_shock_count)
    payment_uplift = CHURN_UPLIFT_BY_SCORE.get(behaviour_score, 0.0) if behaviour_score is not None else 0.0
    sat_uplift = _satisfaction_uplift(satisfaction_score)
    return min(base + payment_uplift + sat_uplift, MAX_CHURN_PROBABILITY)
