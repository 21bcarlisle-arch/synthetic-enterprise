"""The company's churn desk — its own belief about who will leave, and its score.

KNIFE pass 3, `A_composition_lift` step 20, disposition register §3o. Before
this, `simulation/run_phase2b.py::main()` chose between the company's two churn
estimators itself, assembled their keyword arguments itself, knew the industry
base rate to fall back on when an account had no rate history, knew how many
renewal periods the company thinks a post-crisis hangover lasts, and called the
company's own calibration report at the end of the run — three wall crossings
(`company.crm.churn_model`, `company.crm.enriched_churn_estimate`,
`company.analytics.churn_accuracy_report`).

Forming a view on which customers are about to leave is a supplier's own
commercial judgement, and it is ALLOWED TO BE WRONG — that wrongness is the
quantity the COUPLED TRIAD scores. The world's job is that renewals happen and
customers do or do not leave; deciding that a passive roller should be estimated
by a different formula from an active shopper, that an account with no history
is worth the industry base rate, and that a crisis scars a customer for two
renewals, is the company's reading of its own book.

WHAT CROSSES NOW is one `RenewalObservation` of things the company can see — the
old and new rate on its own tariff, tenure from its own acquisition record, its
own EAC estimate, bill shocks it caused, the payment behaviour score it computed,
the satisfaction score it accumulated, its own hedge fraction, and whether the
account renewed actively or rolled to SVT (observable after the fact from its own
books). Which estimator runs, and every constant behind it, is unreachable from
the SIM.

WHAT THIS DESK DOES NOT DO, and it is the load-bearing half of this step. It does
NOT roll the dice on whether a customer engages, and it does NOT cap what a
passive roller's REAL churn probability may reach. Those two lived in
`company/crm/churn_model.py` and the world imported them back across the wall to
decide what actually happened — B2's inversion in miniature, §3g's shape for the
third time. They are now the world's, in `simulation/renewal_engagement.py`. A
door that carried them would have moved the crossing, not cut it.

THE READ DIRECTION. This module imports nothing from `simulation/` or `sim/`:
the observation arrives as a plain frozen dataclass through one signature.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from company.analytics.churn_accuracy_report import compute_churn_model_performance
from company.crm.churn_model import (
    CRISIS_HANGOVER_WINDOW_PERIODS,
    estimate_churn_probability,
)
from company.crm.competitive_pressure import active_pressure_ledger, pressure_ledger_scope
from company.crm.enriched_churn_estimate import (
    INDUSTRY_BASE_CHURN_RATE,
    enriched_churn_estimate,
    enriched_passive_churn_estimate,
)
from company.crm.payment_behaviour_analytics import BehaviourScore

# The company's estimates are published to four decimal places — the precision the
# renewal log, the churn-basis-risk surface and the calibration report all read.
_ESTIMATE_DP = 4


@dataclass(frozen=True)
class RenewalObservation:
    """Everything the company can observe about one account at one renewal.

    Every field is something a real supplier reads off its own systems. Nothing
    here is a simulation internal, and nothing here is a world DECISION: whether
    the account renewed actively is an OUTCOME the company sees after the fact,
    not a roll it makes.
    """

    old_rate_gbp_per_mwh: float
    new_rate_gbp_per_mwh: float
    tenure_years: float
    annual_consumption_kwh: float = 0.0
    bill_shock_count: int = 0
    behaviour_score: Optional[BehaviourScore] = None
    satisfaction_score: Optional[float] = None
    hedge_fraction: float = 0.0
    hangover_periods_remaining: int = 0
    segment: str = "resi"
    renewal_year: int | None = None
    active_renewal: bool = True


def estimate_renewal_churn(observation: RenewalObservation) -> float:
    """The company's probability that this account leaves at this renewal.

    Passive resi rollers get the SVT-inertia formula; active renewers and I&C
    accounts (whose brokers shop every renewal, so there is no passive roll) get
    the full enriched model. Which of the two applies is the company's own
    segmentation judgement and is not visible to the caller.
    """
    estimate = _estimate_renewal_churn(observation)
    # THE DESK IS THE COMPANY'S ONCE-PER-RENEWAL BELIEF SITE, so it is where the belief is
    # BOOKED for later comparison against what actually happened. Recorded here rather than
    # inside `enriched_churn_estimate` because the value arm's margin search calls that dozens
    # of times per renewal while scoring candidate prices -- a counter there would measure the
    # search, not the book. Recorded AFTER rounding, so the ledger holds the same number the
    # renewal log, the calibration report and the churn-basis surface all read.
    ledger = active_pressure_ledger()
    if ledger is not None:
        ledger.observe_renewal_decision(observation.renewal_year, estimate)
    return estimate


def _estimate_renewal_churn(observation: RenewalObservation) -> float:
    """The estimate itself, split out so the booking above wraps exactly one return value.

    Two returns in one function is how a belief comes to be booked on one branch and not the
    other -- and the passive branch is 65% of resi renewals in most years and 100% of them in
    crisis years, so that is the branch whose absence would be least visible.
    """
    if not observation.active_renewal and observation.segment != "I&C":
        return round(
            enriched_passive_churn_estimate(
                observation.old_rate_gbp_per_mwh,
                observation.new_rate_gbp_per_mwh,
                observation.tenure_years,
                bill_shock_count=observation.bill_shock_count,
                behaviour_score=observation.behaviour_score,
                satisfaction_score=observation.satisfaction_score,
                renewal_year=observation.renewal_year,
            ),
            _ESTIMATE_DP,
        )
    return round(
        enriched_churn_estimate(
            observation.old_rate_gbp_per_mwh,
            observation.new_rate_gbp_per_mwh,
            observation.tenure_years,
            observation.annual_consumption_kwh,
            bill_shock_count=observation.bill_shock_count,
            behaviour_score=observation.behaviour_score,
            satisfaction_score=observation.satisfaction_score,
            hedge_fraction=observation.hedge_fraction,
            hangover_periods_remaining=observation.hangover_periods_remaining,
            segment=observation.segment,
            renewal_year=observation.renewal_year,
        ),
        _ESTIMATE_DP,
    )


def estimate_churn_without_rate_history() -> float:
    """The company's estimate for an account it has never renewed before.

    No prior rate means the rate-sensitivity model has nothing to work on, so the
    company falls back on the published industry base switching rate. That the
    fallback is the industry rate rather than, say, zero or its own portfolio
    average is a company judgement, and the number behind it is not the world's.
    """
    return INDUSTRY_BASE_CHURN_RATE


def estimate_secondary_fuel_churn(
    old_rate_gbp_per_mwh: float,
    new_rate_gbp_per_mwh: float,
    tenure_years: float,
) -> float:
    """The company's gas-leg churn estimate, for dual-fuel early-warning monitoring.

    Gas legs do not drive the churn decision — that sits at electricity
    billing-account level — but the company tracks the gas renewal rate separately
    to spot pressure building on a dual-fuel portfolio. Rate sensitivity only:
    there is no separate satisfaction or payment record per fuel.
    """
    return round(
        estimate_churn_probability(
            old_rate_gbp_per_mwh,
            new_rate_gbp_per_mwh,
            tenure_years,
            fuel="gas",
        ),
        _ESTIMATE_DP,
    )


def crisis_hangover_periods() -> int:
    """How many further renewals the company keeps a scarred account elevated for.

    The company observes a >20% net loss on a term from its OWN P&L and concludes
    that customers who lived through it stay anxious afterwards. How long that
    lasts is its belief, not a world parameter.
    """
    return CRISIS_HANGOVER_WINDOW_PERIODS


def score_churn_estimates(
    customer_events: list[dict],
    retention_log: list[dict],
    no_offer_churn_log: list[dict],
) -> dict:
    """Score the company's own churn estimates against what actually happened.

    The calibration report the desk runs on itself: TP/FP/FN/TN, recall,
    precision, F1 and a per-year breakdown. This is the company marking its own
    homework against observed outcomes — which is exactly what a real supplier's
    retention analytics team does, and why it belongs on this side of the door.
    """
    return compute_churn_model_performance(
        customer_events, retention_log, no_offer_churn_log
    )


__all__ = [
    "RenewalObservation",
    # THE DESK OWNS THE LEDGER'S NAMES, and re-exports them so the door can stay a mirror of
    # exactly one module (`test_the_door_exports_exactly_the_desk`). That control is right and it
    # caught this: the first draft had `company.interfaces.churn_estimation` importing these two
    # from `competitive_pressure` directly, which made the door a mirror of two modules and its
    # own test unable to say what it mirrors. The ledger belongs to the desk on the merits too --
    # it holds what the desk believed and what became of it, which is the desk's own score.
    "active_pressure_ledger",
    "pressure_ledger_scope",
    "crisis_hangover_periods",
    "estimate_churn_without_rate_history",
    "estimate_renewal_churn",
    "estimate_secondary_fuel_churn",
    "score_churn_estimates",
]
