"""Company churn model incorporating payment behaviour score (Phase MY).

Extends the bill-shock churn signal (saas/churn_model.py) with payment behaviour.
Uses only observable signals: bill_shock_count (billing records) and
BehaviourScore (payment records from PaymentBehaviourAnalytics).
No SIM internals accessed -- consistent with epistemic barrier.

CHURN_UPLIFT_BY_SCORE encodes the empirical relationship:
- EXCELLENT payers are loyal; slightly suppress churn probability
- CRITICAL payers are at high risk of default-before-departure or imminent leave
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


def combined_churn_probability(
    bill_shock_count: int,
    behaviour_score: Optional[BehaviourScore] = None,
) -> float:
    """Return combined churn probability from bill shocks + payment behaviour.

    base = churn_probability(bill_shock_count) from saas/churn_model.py
    uplift = CHURN_UPLIFT_BY_SCORE[behaviour_score] (zero if score is None)
    result capped at MAX_CHURN_PROBABILITY (0.95).
    """
    base = churn_probability(bill_shock_count)
    uplift = CHURN_UPLIFT_BY_SCORE.get(behaviour_score, 0.0) if behaviour_score is not None else 0.0
    return min(base + uplift, MAX_CHURN_PROBABILITY)
