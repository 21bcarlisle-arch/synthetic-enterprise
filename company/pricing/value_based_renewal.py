"""Price one renewal on what THAT customer is worth, and keep the flat rule beside it as the control.

REUSE: company/pricing/value_based_renewal.py
CLASS: CUSTOM
INDEX: searched "renewal", "price", "margin", "clv", "lifetime", "churn", "retention", "offer",
       "cost to serve", "decision". Six organs came back and every one of them is CALLED here
       rather than rebuilt, because the whole point of this module is that the company already
       knows enough to decide and does not:
         - `company/crm/enriched_churn_estimate.enriched_churn_estimate` — P(leave) given a
           CANDIDATE new rate, from company observables only. This is the load-bearing one and
           it is already GRADED against the world's truth (`churn_estimate_error_pct`).
         - `saas/clv_model.expected_lifetime_periods` + `_annuity_factor` + `DISCOUNT_RATE_ANNUAL`
           — the horizon and the discounting the book is already valued on. A second opinion
           about how long a customer lasts would be a second CLV.
         - `saas/cost_to_serve.build_cost_to_serve` — what this account costs to serve, per year.
         - `saas/tariff_pricing.TARGET_MARGIN_GBP_PER_MWH` — the flat rule, imported as the
           CONTROL rather than copied, so the control cannot drift from what the company
           actually does today.
         - `company/pricing/renewal_desk.strike_fixed_unit_rate` is deliberately NOT called: this
           module decides a MARGIN, and the rate chain stays exactly where it is.
       Nothing here computes a churn probability, a lifetime or a cost.

WHY THIS EXISTS
---------------
Director, 2026-08-25, stating the thesis: *"a supplier that makes commercial and operational
decisions customer-by-customer on lifetime value — using only what it can actually know ...
Measured against that, what exists today is rules, not decisions: a dunning ladder, a churn
estimate, a price. Nothing yet chooses per customer on what that customer is worth."*

Read off HEAD, that is exactly right, and the renewal price is the sharpest instance:

    saas/tariff_pricing.TARGET_MARGIN_GBP_PER_MWH = 2.00

Two pounds a megawatt-hour, for every customer on the book, whoever they are. The one hook that
could have varied it — `price_fixed_tariff(..., profitability_uplift_per_mwh=...)` — has NO
CALLER anywhere in the tree, so even the parameter that exists is dead.

Meanwhile the company holds two honest per-customer beliefs and acts on neither. It estimates
P(leave) per account at a candidate rate and SCORES that estimate against what the world
actually did. It computes cost-to-serve per account. Both are then reported and dropped.

THE DECISION
------------
For a grid of candidate margins, ask the company's own churn model what each one would do to
this customer's chance of staying, and take the one with the highest expected discounted
contribution:

    EV(m) = P(stay | m) x (m x eac_mwh - cost_to_serve_per_year) x annuity(lifetime, r)

A cheap-to-serve customer who is unlikely to leave is worth keeping keenly. One who is leaving
anyway and expensive to serve should not be bought back at a loss. Neither sentence is
expressible in a flat £2.

THE ADVANTAGE IS INFERENCE, NEVER ACCESS, and that is a property of the arithmetic rather than a
promise. Every term above is the company's own belief from its own records: the rate it charged,
the rate it is about to offer, tenure from its own contracts, consumption from its own meters,
payment behaviour from its own ledger, cost from its own cost model. The world's true churn
probability exists — `sim_churn_probability` rides on the churn event — and this module cannot
name it, cannot reach it, and a test refuses any import that would let it.

So this arm beats flat EXACTLY to the degree `enriched_churn_estimate` predicts better than
chance, and not at all otherwise. If that model is noise, the grid search maximises noise and
the arm loses. That is the intended failure mode, it is not guarded against, and
`test_a_BLIND_churn_model_gives_the_value_arm_NO_advantage` pins it.

THE CONTROL, AND WHY IT IS FREE
-------------------------------
The director: *"there has to be a baseline to beat. Average behaviour is the control — the same
book run by a supplier applying flat rules with no per-customer view. Without that comparison,
'it performed well' means nothing."*

Today's company IS that control, exactly — flat £2.00, no per-customer view — so the baseline
does not have to be invented, only FROZEN before it is replaced. `decide_margin(arm=FLAT_RULES)`
returns what HEAD does today and imports the constant rather than restating it, so the control
cannot quietly drift toward the arm it is supposed to judge.

WHAT THIS MODULE DOES NOT CLAIM, said here because the claim would be easy to make and wrong.
It does not show that pricing on value earns more. It cannot: the objective is built from the
company's own beliefs, so scoring the arms on EXPECTED value would let the value arm win by
construction — it maximises the very number it would be judged on, which is R15's tautology
pattern with money in it. The only honest comparison is REALISED: the same book, the same world,
run once per arm, scored on what actually happened. That needs two runs and it is the next step,
not this one.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from company.crm.enriched_churn_estimate import enriched_churn_estimate
from company.crm.payment_behaviour_analytics import BehaviourScore
from saas.clv_model import DISCOUNT_RATE_ANNUAL, _annuity_factor
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH

#: The two arms. `FLAT_RULES` is what the company does today and is the CONTROL; `VALUE_BASED`
#: is the arm under test. Named rather than a boolean so a decision record says which supplier
#: made it, and so a third arm can be added without every call site growing a second flag.
FLAT_RULES = "flat_rules"
VALUE_BASED = "value_based"
ARMS = (FLAT_RULES, VALUE_BASED)

#: The margins the value arm may choose between, £/MWh. Deliberately BRACKETING the flat rule
#: rather than starting at it: an arm that can only price ABOVE the control would beat it on
#: revenue-per-retained-customer by construction and lose customers to pay for it, and one that
#: can only price BELOW would be a discount programme wearing a decision's clothes.
#:
#: THE FIRST GRID WAS 0.50..8.00 AND IT WAS DECIDING NOTHING. Measured on the first probe, every
#: customer shape came back at exactly 8.00 -- the ceiling -- because over that range the
#: company's churn model barely moves: £2 to £8 on a 3,100 kWh account is £18.60 a year on a
#: ~£1,700 bill, about one percent, and the DESNZ-calibrated switching curve correctly shrugs at
#: one percent. The "decision" was my own constant, read back.
#:
#: Widened until the model actually turns over, which it does. On that same account the expected
#: value peaks near £80/MWh and falls away after, as churn passes half the book:
#:
#:      margin   offered   P(leave)      EV
#:        2.00     120.0     0.060    -114.08
#:       20.00     138.0     0.180      14.27
#:       80.00     198.0     0.580     201.58     <- turn-over
#:      160.00     278.0     0.925      81.76
#:
#: That is a finding about the company and not about this grid, and it is stated rather than
#: tuned away: ON ITS OWN MODEL, the flat £2 is an order of magnitude below the value-maximising
#: margin, and the only thing that stops a value-maximising supplier charging it is the
#: competitive/lawful ceiling the renewal desk already applies. `max_offered_rate_gbp_per_mwh`
#: is where that comes in, and `ceiling_bound` is how a reader is told it bound.
CANDIDATE_MARGINS_GBP_PER_MWH: tuple[float, ...] = (
    0.50, 1.00, 2.00, 3.00, 5.00, 8.00, 12.00, 20.00, 30.00, 45.00,
    60.00, 80.00, 100.00, 130.00, 160.00, 200.00,
)

def max_supported_rate_increase_pct() -> float:
    """The largest single-step price rise this company's churn model has any evidence for,
    DERIVED from the published domestic cap rather than chosen.

    WHY A DECISION NEEDS THIS AND A REPORT DOES NOT. `company/crm/churn_model.py` caps churn at
    `MAX_CHURN_PROBABILITY = 0.95` and saturates toward it: measured, a customer facing +100%
    leaves with p=0.86, +200% with p=0.946, +400% with p=0.950. So five percent of the book is
    modelled as staying WHATEVER they are charged — harmless in a number that is reported, and
    fatal in one that is maximised, because expected value then rises without bound in the
    price. Run unbounded against the real book, this arm priced all 263 accounts between £60 and
    £200/MWh against a flat £2 — thirty to a hundred times, enough to double a domestic bill —
    and reported no losses, because on the model there are none. The maximiser was not wrong; it
    found a floor of unconditionally captive customers and did exactly what that implies.

    THE FIX IS NOT TO CHANGE THE MODEL. That cap is a calibrated company belief and moving it so
    this arm behaves is precisely the goal-seeking R12 forbids. The fix is that a DECISION may
    not rest on an extrapolation its belief cannot support.

    THE BOUND IS SOURCED, NOT PICKED. `estimate_churn_probability` is calibrated on GB domestic
    switching behaviour, and the largest single-step domestic price move ever published is the
    Ofgem cap's own — +83.1% on 1 Oct 2022, from `PUBLISHED_CAP_WINDOWS`, the same commons
    artefact both lanes read. Domestic customers have never been observed responding to a bigger
    one-step rise than the market itself has ever made, so the company may not price on a
    prediction beyond it. Derived from the schedule rather than written down, so a re-ingest
    moves it and a reader can decompose it.

    READ THROUGH THE COMPANY'S OWN CAP MODULE, and the first draft got this wrong: it imported
    `simulation.price_cap_enforcement` — the WORLD's reading of the same schedule — and this
    module's own wall test refused it, correctly and immediately. The regulatory TEXT is a shared
    commons, but each lane's READING of it is independently owned, which is the whole point of
    `company/pricing/ofgem_price_cap.py` existing separately at all. A supplier bounds its own
    pricing by its own reading of the law; borrowing the world's would be the company checking
    its homework against the answer sheet.
    """
    from company.pricing.ofgem_price_cap import _CAP_WINDOWS

    steps = []
    previous = None
    for window in _CAP_WINDOWS:
        level = window.get("elec")
        if previous and level:
            steps.append(100.0 * (level - previous) / previous)
        previous = level or previous
    if not steps:
        raise MarginDecisionUnavailable(
            "the published cap schedule carries no step to derive a support bound from, so "
            "there is no defensible range for this decision -- not an unbounded one"
        )
    return max(steps)


#: Payment-behaviour scores that mean this household is in difficulty. Taken from the company's
#: OWN ledger, which is where a real supplier sees it.
DISTRESS_SCORES = (BehaviourScore.POOR, BehaviourScore.CRITICAL)

#: Bill shocks that count as distress on their own, for an account with no behaviour score yet.
#: Two rather than one: a single shock is a cold winter.
DISTRESS_BILL_SHOCKS = 2

#: A customer with no usable lifetime estimate is priced at ONE period rather than at the book's
#: average. Borrowing the average would let a brand-new account inherit a long lifetime it has
#: given no evidence for, which is the direction that flatters the value arm — it would justify
#: keener pricing on exactly the accounts the company knows least about.
FALLBACK_LIFETIME_PERIODS = 1.0


class MarginDecisionUnavailable(Exception):
    """The decision could not be made. Never a silent fall back to the flat rule.

    A value arm that quietly returns the control's answer whenever an input is missing would
    report itself as "no different from flat" on every account it could not price, which is
    indistinguishable from an arm that ran and found nothing to gain (R15 fail-silent).
    """


@dataclass(frozen=True)
class MarginDecision:
    """One customer's margin, and enough of the reasoning to refute it."""

    customer_id: str
    arm: str
    margin_gbp_per_mwh: float
    #: The company's OWN expected discounted contribution at the chosen margin. A belief, and
    #: labelled as one: it is never evidence that the decision was right.
    expected_value_gbp: float
    p_retain: float
    expected_periods: float
    cost_to_serve_gbp_per_year: float
    eac_mwh: float
    #: Every candidate and its score, so a reader can see the shape of the trade-off rather than
    #: take the argmax on trust. Cheap: sixteen rows.
    considered: tuple[tuple[float, float], ...] = field(default_factory=tuple)
    #: TRUE when the choice sits at an END of the candidate grid. An argmax at an endpoint is not
    #: an optimum, it is a constant of this module read back, and the first version of this grid
    #: returned one for every customer shape probed. Reported so nobody has to notice.
    endpoint_bound: bool = False
    #: WHY the value arm declined to charge what it wanted to. `None` when it did not decline.
    #: This is the one place the arm is deliberately NOT a maximiser, and it says so out loud.
    withheld_reason: str | None = None
    #: TRUE when candidates were removed because they implied a price change beyond anything the
    #: churn model has evidence for. Reported, because "the model would have gone further" and
    #: "the model turned over here" are completely different statements about the company.
    extrapolation_bound: bool = False
    #: TRUE when a lawful/competitive ceiling removed candidates the model preferred. A
    #: value-maximising supplier is still a supplier that obeys the cap, and when the cap is what
    #: decided the price the reader should be told that rather than shown a "decision".
    ceiling_bound: bool = False

    @property
    def differs_from_flat(self) -> bool:
        return abs(self.margin_gbp_per_mwh - TARGET_MARGIN_GBP_PER_MWH) > 1e-9


def expected_value_gbp(
    *,
    margin_gbp_per_mwh: float,
    eac_mwh: float,
    cost_to_serve_gbp_per_year: float,
    p_retain: float,
    expected_periods: float,
    discount_rate: float = DISCOUNT_RATE_ANNUAL,
) -> float:
    """Expected discounted contribution from one customer at one candidate margin.

    COST TO SERVE IS SUBTRACTED INSIDE THE RETAINED BRANCH, not outside it, and the difference
    is the whole economics of a bad customer: a supplier does not pay to serve an account that
    left. Outside, a loss-making customer would look equally bad at every margin and the model
    would price them as though nothing could be done; inside, raising the margin until they
    leave is a legitimate outcome and the arithmetic can say so.

    Discounting is the CLV model's own (`DISCOUNT_RATE_ANNUAL`, `_annuity_factor`), because a
    second opinion about the time value of a customer would be a second CLV — and this repo has
    already paid for having three of a thing that should be one.
    """
    annual_contribution = margin_gbp_per_mwh * eac_mwh - cost_to_serve_gbp_per_year
    return p_retain * annual_contribution * _annuity_factor(expected_periods, discount_rate)


def decide_margin(
    *,
    customer_id: str,
    arm: str,
    current_rate_gbp_per_mwh: float,
    base_rate_gbp_per_mwh: float,
    eac_kwh: float,
    tenure_years: float,
    cost_to_serve_gbp_per_year: float,
    expected_periods: float | None = None,
    segment: str = "resi",
    fuel: str = "electricity",
    bill_shock_count: int = 0,
    behaviour_score: BehaviourScore | None = None,
    satisfaction_score: float | None = None,
    renewal_year: int | None = None,
    candidates: tuple[float, ...] = CANDIDATE_MARGINS_GBP_PER_MWH,
    max_offered_rate_gbp_per_mwh: float | None = None,
) -> MarginDecision:
    """The offered margin for ONE customer, under ONE arm.

    `base_rate_gbp_per_mwh` is the rate BEFORE margin — wholesale + capital + policy + network,
    exactly what `renewal_desk.strike_fixed_unit_rate` already computes. This module adds the
    margin and nothing else; the rate chain is untouched and stays the single place a rate is
    built.

    EVERY ARGUMENT IS A COMPANY OBSERVABLE. There is deliberately no parameter through which a
    caller could hand in the world's churn probability, the world's population draw, or anything
    else the supplier could not look up in its own records — the same shape `growth_desk`'s
    docstring holds for the acquisition gate.
    """
    if arm not in ARMS:
        raise MarginDecisionUnavailable(f"{arm!r} is not an arm; expected one of {ARMS}")
    if eac_kwh is None or float(eac_kwh) <= 0.0:
        raise MarginDecisionUnavailable(
            f"{customer_id} has no annual consumption on record, so there is no volume to earn a "
            "margin on and no decision to make -- not a flat-rule default"
        )
    eac_mwh = float(eac_kwh) / 1000.0
    periods = FALLBACK_LIFETIME_PERIODS if not expected_periods else float(expected_periods)

    def _score(margin: float) -> tuple[float, float]:
        offered = base_rate_gbp_per_mwh + margin
        p_leave = enriched_churn_estimate(
            current_rate_gbp_per_mwh, offered, tenure_years, float(eac_kwh),
            bill_shock_count=bill_shock_count,
            behaviour_score=behaviour_score,
            satisfaction_score=satisfaction_score,
            fuel=fuel,
            segment=segment,
            renewal_year=renewal_year,
        )
        p_stay = max(0.0, 1.0 - float(p_leave))
        return p_stay, expected_value_gbp(
            margin_gbp_per_mwh=margin, eac_mwh=eac_mwh,
            cost_to_serve_gbp_per_year=cost_to_serve_gbp_per_year,
            p_retain=p_stay, expected_periods=periods,
        )

    if arm == FLAT_RULES:
        # THE CONTROL DOES NOT SEARCH. It prices the constant and then reports what that choice
        # was worth, so the two arms are scored by the same function and any difference between
        # them is the DECISION and never the scorer.
        p_stay, value = _score(TARGET_MARGIN_GBP_PER_MWH)
        return MarginDecision(
            customer_id=customer_id, arm=FLAT_RULES,
            margin_gbp_per_mwh=TARGET_MARGIN_GBP_PER_MWH,
            expected_value_gbp=value, p_retain=p_stay, expected_periods=periods,
            cost_to_serve_gbp_per_year=cost_to_serve_gbp_per_year, eac_mwh=eac_mwh,
            considered=((TARGET_MARGIN_GBP_PER_MWH, value),),
        )

    if not candidates:
        raise MarginDecisionUnavailable(
            f"{customer_id}: the value arm was given no candidate margins, so its 'choice' would "
            "be an empty search reported as a decision"
        )
    # THE CEILING IS APPLIED BEFORE THE SEARCH, not after it. Scoring a candidate the company
    # may not lawfully offer and then clamping the winner would report an expected value nobody
    # can earn, and would make the arm look better than the supplier it describes.
    lawful = tuple(
        m for m in candidates
        if max_offered_rate_gbp_per_mwh is None
        or base_rate_gbp_per_mwh + m <= max_offered_rate_gbp_per_mwh + 1e-9
    )
    ceiling_bound = len(lawful) < len(candidates)

    # AND THE MODEL'S OWN EVIDENCE BOUNDS IT TOO. See `max_supported_rate_increase_pct`: the
    # churn cap at 0.95 leaves a floor of customers who never leave, so an unbounded maximiser
    # prices to infinity, and on the real book it very nearly did.
    support_pct = max_supported_rate_increase_pct()
    ceiling_from_support = current_rate_gbp_per_mwh * (1.0 + support_pct / 100.0)
    allowed = tuple(m for m in lawful if base_rate_gbp_per_mwh + m <= ceiling_from_support + 1e-9)
    extrapolation_bound = len(allowed) < len(lawful)
    if not allowed:
        raise MarginDecisionUnavailable(
            f"{customer_id}: no candidate margin survives both the ceiling "
            f"({max_offered_rate_gbp_per_mwh} GBP/MWh) and the model's support bound "
            f"({ceiling_from_support:.1f} GBP/MWh, {support_pct:.1f}% above the current rate) at "
            f"a base rate of {base_rate_gbp_per_mwh}. That is a real answer -- there is no offer "
            "here this company can both lawfully make and honestly predict -- and not a default."
        )
    scored = [(margin, *_score(margin)) for margin in allowed]
    # TIES GO TO THE LOWER MARGIN, and it is not a rounding convention. On a flat stretch of the
    # switching curve several margins score identically; taking the highest would make the arm
    # prefer charging more for no expected gain, which is the shape a reader would rightly call
    # an excuse rather than a decision.
    best_margin, best_p, best_value = min(
        scored, key=lambda row: (-round(row[2], 6), row[0])
    )

    # THE ARM WANTS TO CHARGE A STRUGGLING HOUSEHOLD MORE, AND IT IS NOT ALLOWED TO BY ACCIDENT.
    #
    # Measured on the first probe, not reasoned about afterwards. Three customer shapes, no
    # ceiling: the loyal, cheap-to-serve, high-volume household priced at £80/MWh -- and the
    # FLIGHTY, EXPENSIVE-TO-SERVE, THREE-BILL-SHOCK household priced HIGHEST of all, at £100. The
    # logic is impeccable and the conclusion is that a customer who is probably leaving anyway
    # should be extracted from while they are still here. That is what unconstrained expected-
    # value maximisation says about a household in payment difficulty, and it is what a regulator
    # fines a real supplier for.
    #
    # THE WEIGHT THAT WOULD SETTLE IT IS THE DIRECTOR'S AND IS UNSIGNED. `A7_harm_cost_weights_
    # ratio` is the harm:loss ratio for exactly this trade-off -- the cost of treating someone
    # who genuinely cannot pay as though they would not, against the cost of forbearing with
    # someone who simply will not. It is an R13 curriculum value, it is open in the action
    # register, and it is not the builder's to pick.
    #
    # So the arm does not pick it either. Where the company's own ledger says this household is
    # in difficulty, the value arm may price DOWN from the flat rule but never UP, and it records
    # that it wanted to. A silent fall-back to flat would have made "no different from flat" mean
    # two different things -- nothing to gain, and refused to take it -- which is the fail-silent
    # shape R15 names third.
    in_distress = (
        behaviour_score in DISTRESS_SCORES or bill_shock_count >= DISTRESS_BILL_SHOCKS
    )
    withheld = None
    if in_distress and best_margin > TARGET_MARGIN_GBP_PER_MWH:
        withheld = (
            "the company's own payment records put this household in difficulty (behaviour "
            "{}, {} bill shock(s)), and the value arm wanted {:.2f} GBP/MWh -- above the flat "
            "rule. Charging a struggling customer MORE because they are likely to leave is the "
            "harm side of A7_harm_cost_weights_ratio, whose weight is a director-reserved "
            "curriculum value and is unsigned. Held at the flat rule rather than taken."
        ).format(getattr(behaviour_score, "value", behaviour_score), bill_shock_count, best_margin)
        best_margin = TARGET_MARGIN_GBP_PER_MWH
        best_p, best_value = _score(best_margin)

    return MarginDecision(
        customer_id=customer_id, arm=VALUE_BASED, margin_gbp_per_mwh=best_margin,
        expected_value_gbp=best_value, p_retain=best_p, expected_periods=periods,
        cost_to_serve_gbp_per_year=cost_to_serve_gbp_per_year, eac_mwh=eac_mwh,
        considered=tuple((m, v) for m, _p, v in scored),
        endpoint_bound=withheld is None and best_margin in (allowed[0], allowed[-1]),
        ceiling_bound=ceiling_bound,
        extrapolation_bound=extrapolation_bound,
        withheld_reason=withheld,
    )
