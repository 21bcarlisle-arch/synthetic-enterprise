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

#: THE SAME §4 BANDS, KEPT AS EDGES RATHER THAN COLLAPSED TO THEIR MIDPOINT — because the width
#: of a published range is information and the midpoints above throw it away.
#:
#: Source is the identical table the two midpoints are read from
#: (`docs/market_research/svt_rates_active_passive_2016_2025.md` §4): long-stayer ~5-10%/yr,
#: recent roller ~15-20%/yr. No new number is minted here; these ARE those two rows, unrounded.
SVT_DRIFT_BELIEF_BAND_LONG_STAYER = (0.05, 0.10)
SVT_DRIFT_BELIEF_BAND_RECENT = (0.15, 0.20)

#: WHERE INSIDE ITS BAND ONE ACCOUNT SITS, AS A FRACTION OF THE BAND'S WIDTH — and this is a
#: POSITION, not a rate, which is why it declares no currency and no per-year.
#:
#: WHY THE BAND HAS A WIDTH AT ALL IS THE WHOLE ARGUMENT. §4's stated basis for the long-stayer
#: row is "Ofgem engagement surveys: most inert segment", and for the recent row "switched once
#: before; some re-engagement". The published range is therefore a range BECAUSE ENGAGEMENT
#: VARIES INSIDE IT. Placing an account within the range by an engagement observable is following
#: the source's own reason for the range's existence, not imposing a structure on it.
#:
#: THE DIRECTION IS PUBLISHED AND THE MAGNITUDE IS NOT, AND ONLY THE DIRECTION IS USED. A domestic
#: account in arrears is materially LESS able to leave: under the domestic debt-objection regime
#: (Ofgem, "Decision on review of domestic objections", 2016) a supplier may object to the
#: transfer of an indebted domestic customer, and indebted prepayment switches run through the
#: Debt Assignment Protocol. The mechanism is not in question — an objection legally stops the
#: transfer. What is NOT established anywhere I could check is any MAGNITUDE for it, and both
#: Ofgem source PDFs refused text extraction, so the figures a search summary offered are
#: deliberately not quoted or used. `docs/market_research/svt_drift_by_payment_behaviour.md`
#: records exactly what was and was not established, including that failure.
#:
#: SO THE SPACING IS UNIFORM, AND UNIFORM IS THE HONEST CHOICE RATHER THAN A CONVENIENT ONE.
#: Nothing published gives a within-band structure, so the five grades are spread evenly and the
#: MIDDLE grade lands exactly on the midpoint the belief used before this term existed — an
#: account the company knows nothing bad about is scored exactly as it was. It is also why the
#: spacing is not load-bearing: the belief is graded by a RANKING statistic within a band, and
#: every strictly-monotone spacing gives the identical ranking there. A different spacing could
#: not have produced a different verdict, which is the property that stops this being a number
#: picked to make a result.
_SVT_DRIFT_BAND_POSITION_BY_BEHAVIOUR: dict[str, float] = {
    "EXCELLENT": 1.00,
    "GOOD": 0.75,
    "FAIR": 0.50,
    "POOR": 0.25,
    "CRITICAL": 0.00,
}


@dataclass(frozen=True)
class SvtSegmentObservation:
    """Everything the company can observe about one account over one cap period on its SVT.

    Every field is one of the company's OWN RECORDS and none is an inference: it set the tariff,
    so it knows when this account last left a fixed deal; it issues the bills, so it knows how
    long this cap period ran; and it collects the money, so it knows whether this account paid on
    time, paid late, or had a Direct Debit returned. Nothing here is a simulation internal.

    `payment_behaviour` IS THE ONE FIELD THAT VARIES ACROSS HOUSEHOLDS AT THE SAME INSTANT, which
    the other two do not do in any useful way — see `estimate_svt_drift` for why that sentence is
    the reason this field exists. It is the `BehaviourScore` name
    (`company.crm.payment_behaviour_analytics`) the company's own desk already computes from its
    own collections history, passed as a plain string so this seam type does not drag an enum
    across it. `None` means the company holds no payment history for this account yet — a new
    account, most often — and is handled as an absence rather than as a good record.
    """

    years_on_svt: float
    segment_days: float
    payment_behaviour: str | None = None


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

    V1 SHIPPED WITH NOTHING IN ITS PLACE AND WAS GRADED FOR IT. Both of its observables are
    CALENDAR — years since a fixed deal ended, and the length of this cap period — so the belief
    could only order the billing calendar, and the instrument said so: **0.4691 per exposure-day,
    inside a null of [0.4164, 0.5834], against an oracle ceiling of 0.6091 that clears.** The
    signal on this route is real and v1 found none of it. Result and scoring:
    `docs/staging/WORKER_PREREGISTRATION_WHAT_THE_SVT_DRIFT_BELIEF_MUST_SHOW_2026-08-31.md`.

    V2 ADDS THE ONE THING THAT VARIES ACROSS HOUSEHOLDS AT THE SAME INSTANT, and that phrase is
    the specification rather than a description of it. `years_on_svt` and `segment_days` are both
    properties of a clock; two accounts sitting side by side on the same cap period differ in
    neither in any way the company could act on. **A belief every household shares cannot select
    a household.** `payment_behaviour` is the company's own collections record — on-time rate and
    returned Direct Debits, off its own bank feed — and it is genuinely different per account at
    one instant, which is the property that makes selection possible at all.

    AND IT IS AN INFERENCE, WHICH IS THE ENTIRE POINT AND ALSO THE ONLY THING THAT KEEPS IT LEGAL.
    The company is NOT handed propensity to act. It is handed whether the money arrived, and must
    work out for itself that the two are related. The world happens to generate both from one
    hardship substrate (`simulation.arrears_engine.payment_outcome` takes income stress; so does
    `stress_switching_multiplier`) — but that shared cause is a fact about the world the company
    has to DISCOVER from its own book, not a channel it reads. Nothing about income stress,
    housing tenure, segment or `sim_action_propensity` crosses here, in this direction or any
    other; the wall argument is set out in full in `company/interfaces/churn_estimation.py`.

    IF THIS STILL READS INSIDE ITS NULL, THAT IS THE PUBLISHED RESULT AND IT IS WORTH MORE THAN
    THE FIRST ONE. It would say the company's best honest proxy for who acts cannot reach the
    dimension the world uses — and on a route where the oracle proves the signal exists, that is a
    measurement of how much of this world's advantage is unreachable by inference. Written here
    before the run, not after it.

    IT MUST NEVER SEED THE ROLL. `saas.churn_model.build_churn_risk` seeds `effective_p_retain`
    and is then graded against the roll it seeded, so its 0.6815 against a 0.7400 ceiling measures
    the world reading back its own input and its capture ratio is refused. This one is RECORDED
    ALONGSIDE the SVT decision and reaches no hazard, which is what makes it gradable at all.
    """
    if observation.segment_days <= 0:
        return 0.0
    long_stayer = observation.years_on_svt >= SVT_DRIFT_BELIEF_LONG_STAYER_YEARS
    annual = (
        SVT_DRIFT_BELIEF_ANNUAL_LONG_STAYER if long_stayer else SVT_DRIFT_BELIEF_ANNUAL_RECENT
    )
    # AN UNRECOGNISED GRADE FALLS BACK TO THE MIDPOINT AND DOES NOT GUESS A POSITION. `.get` with
    # no default would have handed `None` to the arithmetic below and raised; a numeric default
    # would have silently scored an unknown grade as though it were a known one. The midpoint is
    # the same answer the belief gives when it holds no payment history at all, which is the
    # honest reading of "the company cannot tell where this account sits".
    position = (
        None
        if observation.payment_behaviour is None
        else _SVT_DRIFT_BAND_POSITION_BY_BEHAVIOUR.get(observation.payment_behaviour)
    )
    if position is not None:
        low, high = (
            SVT_DRIFT_BELIEF_BAND_LONG_STAYER if long_stayer else SVT_DRIFT_BELIEF_BAND_RECENT
        )
        annual = low + position * (high - low)
    drift = 1.0 - (1.0 - annual) ** (observation.segment_days / 365.25)
    return round(max(0.0, min(1.0, drift)), _ESTIMATE_DP)
