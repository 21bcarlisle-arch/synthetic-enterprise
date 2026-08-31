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
    # The SVT route, added 2026-08-31. Same door, because it is the same question (will this
    # account leave) asked at a different moment in the account's life.
    "SvtSegmentObservation",
    "estimate_svt_drift",
]


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE STANDARD VARIABLE ROUTE — 61% of this book's departures, and the company had no view at all
# ═════════════════════════════════════════════════════════════════════════════════════════════
#
# Measured 2026-08-31 (`WORKER_FINDING_THE_COMPANY_FORMS_NO_BELIEF_ON_THE_ROUTE_CARRYING_61_
# PERCENT_OF_DEPARTURES_2026-08-31.md`): 50 of 82 departures happen when an account drifts off the
# standard variable product, and `estimate_renewal_churn` above is indexed on renewal
# anniversaries, which an SVT segment does not have. So the company's churn belief was scored on
# the minority of departures it could see and was BLIND BY CONSTRUCTION to the majority. Not
# mis-calibrated — looking somewhere else.
#
# This is the view it was missing. A real supplier can form it: it sets the tariff, so it knows
# exactly which accounts sit on its default product and since when.

#: THE COMPANY'S READING OF THE PUBLISHED BANDS, AND IT IS THE MIDPOINT, NOT THE TOP.
#:
#: `docs/market_research/svt_rates_active_passive_2016_2025.md` §4 publishes two RANGES and is
#: explicit that they are structural inferences rather than a series — long-stayers (3+ years on
#: the default tariff) ~5-10%/yr, recent rollers (under 3 years) ~15-20%/yr, confidence M on both.
#:
#: A supplier reading a published range reads out its MIDPOINT. Taking the top of each band is the
#: director's §7 anti-flattering tie-break, which governs where the WORLD is aimed — and the
#: company's belief about the market is not the director's dial. This is the identical distinction
#: `company/crm/market_conditions` already draws on the switching band, in the same words, and it
#: is followed here rather than re-argued.
#:
#: THE CONSEQUENCE IS REAL AND IS PREDICTED RATHER THAN DISCOVERED: the world runs 0.20/0.10 and
#: the company believes 0.175/0.075, so **the company systematically under-estimates drift by
#: about 12.5% relative** on every SVT account. That is a belief-vs-truth gap with a stated cause,
#: which is the only kind worth having, and the coupled triad scores it.
SVT_DRIFT_BELIEF_ANNUAL_RECENT = 0.175
SVT_DRIFT_BELIEF_ANNUAL_LONG_STAYER = 0.075
#: The published boundary between the two bands, in continuous years on the default tariff.
SVT_DRIFT_BELIEF_LONG_STAYER_YEARS = 3.0


@dataclass(frozen=True)
class SvtSegmentObservation:
    """Everything the company can observe about one account over one cap period on its SVT.

    Both fields are the company's OWN RECORDS and neither is an inference: it set the tariff, so
    it knows when this account last left a fixed deal, and it issues the bills, so it knows how
    long this cap period ran. Nothing here is a simulation internal.
    """

    years_on_svt: float
    segment_days: float


def estimate_svt_drift(observation: SvtSegmentObservation) -> float:
    """The company's probability that this account drifts off the default tariff this period.

    THE SEGMENT CONVERSION IS ARITHMETIC, NOT A BELIEF. The bands are annual and cap periods are
    neither equal nor quarters — the first one after a household arrives can be 47 days. Constant
    hazard, `1 - (1 - annual) ** (days / 365.25)`, is the only conversion that makes four real cap
    quarters recompose to the annual figure. Using the annual rate as a per-period rate would give
    `1-(1-0.175)**4 = 0.5361` a year against 0.175. The company and the world necessarily agree on
    this step and disagree on the BAND, which is the whole point: the disagreement is a belief,
    not an arithmetic error.

    WHAT THE COMPANY CANNOT SEE, AND IT IS THE INTERESTING HALF. The world damps every departure
    risk by an ACTION PROPENSITY built from income stress and housing tenure — measured
    `corr(dissatisfaction, action_propensity) = -0.5188`, and realised churn running 0.243 / 0.200
    / 0.083 across low / moderate / high income stress. **No term for that appears here**, because
    no observable the company holds at a cap boundary carries it: income stress is SIM ground
    truth and housing tenure is a segment label, and the D-SEGMENT wall forbids either crossing.
    Payment behaviour is the honest proxy and it is NOT wired in v1 — the company's own arrears
    history is available but joining it here needs a payment view this seam does not carry.
    **So this belief is expected to order accounts by EXPOSURE and to miss the dimension that
    decides who actually acts.** That is stated before the measurement rather than after it; the
    pre-registration is
    `docs/staging/WORKER_PREREGISTRATION_WHAT_THE_SVT_DRIFT_BELIEF_MUST_SHOW_2026-08-31.md`.

    IT MUST NEVER SEED THE ROLL. `saas.churn_model.build_churn_risk` seeds `effective_p_retain`
    and is then graded against the roll it seeded, so its 0.6815 against a 0.7400 ceiling measures
    the world reading back its own input and its capture ratio is refused. This one is RECORDED
    ALONGSIDE the SVT decision and reaches no hazard, which is what makes it gradable at all.
    """
    if observation.segment_days <= 0:
        return 0.0
    annual = (
        SVT_DRIFT_BELIEF_ANNUAL_LONG_STAYER
        if observation.years_on_svt >= SVT_DRIFT_BELIEF_LONG_STAYER_YEARS
        else SVT_DRIFT_BELIEF_ANNUAL_RECENT
    )
    drift = 1.0 - (1.0 - annual) ** (observation.segment_days / 365.25)
    return round(max(0.0, min(1.0, drift)), _ESTIMATE_DP)
