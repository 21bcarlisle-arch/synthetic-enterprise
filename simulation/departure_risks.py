"""Competing risks: a departure carries the cause that produced it.

Design: `docs/design/C2_DEPARTURE_WITH_A_CAUSE_DESIGN.md`.
Pre-registration: `docs/staging/WORKER_PREREGISTRATION_WHAT_A_DEPARTURE_WITH_A_CAUSE_MUST_SHOW_2026-08-30.md`.

WHAT THIS REPLACES. `customer_events.roll_lifecycle_event` used to multiply every churn factor
into one scalar and roll once. By the time the die was cast the causes were gone, so a departure
was not merely unlabelled -- it was UNCAUSED BY CONSTRUCTION, and any `reason` field bolted onto
the emitted record could only carry a story invented after the roll. Here each risk keeps its own
hazard, survival is the product of the survivals, and the risk that fires names the departure.

-------------------------------------------------------------------------------
THE RISK / MODULATOR SPLIT, AND WHERE THE DESIGN WAS WRONG
-------------------------------------------------------------------------------
§2 of the design draws the line correctly and then puts one term on the wrong side of it. Its own
test for a modulator is: **a competing-risks model has no negative hazards, so a term that can
make people leave LESS is not a reason anyone left.** It applies that test to market opportunity
(`market_switching_multiplier(2022) = 0.444`) and correctly demotes it to a modulator.

Applied to the same table's `financial_stress` row, the test demotes that too, and the design did
not notice:

    STRESS_SWITCHING_MULTIPLIER   low 1.10   moderate 0.85   high 0.65
    TENURE_SWITCHING_MULTIPLIER   owner 1.00  private_renter 0.80  social_renter 0.75

A household under HIGH income stress is modelled as 35% LESS likely to leave, and a social renter
25% less. "I was too financially stressed to switch" is not a reason anyone left; it is a
precondition that damps whether they act at all -- exactly the shape of "there was nowhere to go".
So income stress and tenure are a single ACTION PROPENSITY modulator scaling every risk, and there
are THREE risks here, not the design's four. This was caught by printing the multiplier table
before writing the formula, which is the second time on this design that printing the numbers
first caught a term facing the wrong way (§3 caught the first).

Satisfaction passes the test and stays a risk: it runs 1.30 / 1.00 / 0.85, and the protective 0.85
branch is not a negative hazard but a smaller dissatisfaction hazard, bounded below by zero.

  RISKS (each is a reason someone leaves, each carries its own hazard)
    bill_shock        this household's own bill rose
    price_position    our rate against the market reference, felt in pounds at their bill
    dissatisfaction   service failures
                      (C1b adds svt_inertia; C6 adds home_move)

  MODULATORS (each scales risks and is never a risk itself)
    market opportunity   is there anywhere to go   -> the opportunity-seeking risks only
    action propensity    income stress x tenure    -> every risk
    engagement           the passive-renewal cap   -> the bill-shock base, as today
    retention offer      a price cut we made       -> price_position only

`retention offer` scaling price alone is pre-registration P6 and is the first genuinely actionable
consequence in this programme: a discount cannot retain a service-driven churner, so the answer to
one is a service intervention -- and a supplier can observe its own service failures.

-------------------------------------------------------------------------------
WHY THE HAZARDS ARE FUNCTIONS OF STATE AND NEVER CONSTANTS (design §3)
-------------------------------------------------------------------------------
Constant per-cause hazards reproduce the input weights as the output reason mix exactly, which
would satisfy pre-registration P2 by construction while measuring nothing. The published weights
therefore set each risk's SENSITIVITY -- how much a unit of felt price differential, or a unit of
dissatisfaction, converts into hazard -- and never the hazard itself. Every hazard below carries a
per-household term, so the realised mix emerges from the population's actual states and CAN differ
from the weights. `test_departure_risks.py` pins this: it is the one property whose loss turns P2
back into a tautology.

Only ONE number here is fitted (`_SENSITIVITY_SCALE`, the P0 calibration), and the split between
the two sensitivities it scales is published rather than chosen.
"""
import math

from simulation.churn_ceiling import WORLD_MAX_CHURN_PROBABILITY

CAUSE_BILL_SHOCK = "bill_shock"
CAUSE_PRICE_POSITION = "price_position"
CAUSE_DISSATISFACTION = "dissatisfaction"

#: Declared order is presentational only. The cause SHARES below are computed from the hazards'
#: cumulative-hazard weights, which are order-free -- the sequential decomposition
#: (h1, then (1-h1)h2, then ...) is exact in TOTAL but gives earlier risks a systematically larger
#: share, which would bias P2's reason mix by the order of a tuple literal.
ORDERED_CAUSES = (CAUSE_BILL_SHOCK, CAUSE_PRICE_POSITION, CAUSE_DISSATISFACTION)

# Ofgem/BMG consumer research 2024, n=3,235: the importance households place on each factor in a
# switching decision. Price 40% (35-44% across every reported subgroup), customer service 32%.
# See docs/design/WHAT_A_HOUSEHOLD_DECIDES_ON.md.
PRICE_IMPORTANCE = 0.40
SERVICE_IMPORTANCE = 0.32

# EXIT FEES ARE 22% OF THE PUBLISHED DECISION AND THIS WORLD DOES NOT MODEL THEM (design §4).
# That weight is NOT redistributed across the two above: doing so would inflate price and service
# by a third between them and bury the gap in a constant nobody could later attribute. The honest
# statement is that this world models a switching decision missing its third-largest published
# factor, and the roadmap carries exit fees as a named item ahead of S3.
UNMODELLED_EXIT_FEE_IMPORTANCE = 0.22

#: THERE IS NO CALIBRATED DEFAULT, AND THE ABSENCE IS THE POINT (2026-08-30).
#:
#: The P0 calibration was run and it does not identify this number. Measured on the real 708-renewal
#: factor table, every bill-shock scale from 0.87 downward reproduces population-mean realised churn
#: EXACTLY, while the reason mix across that family runs from 99.9%/0.0%/0.0% to 56.6%/23.2%/20.1%.
#: P0 therefore cannot tell a right sensitivity from a wrong one, and picking one would BE the
#: answer to P2 rather than a calibration of it -- the same trap design §3 caught one level up.
#: The only scale with published evidence behind it (1.0, the world's own calibrated base rate) is
#: infeasible: it overshoots the target by 14.9%.
#:
#: See `docs/staging/WORKER_FINDING_THE_P0_CALIBRATION_IS_EITHER_INFEASIBLE_OR_IT_CHOOSES_THE_ANSWER_2026-08-30.md`.
#:
#: So this module FAILS CLOSED. A default of 0.0 would have been worse than no default at all: it
#: silently zeroes the price and service hazards, makes every departure a bill-shock departure, and
#: reports a reason mix of 100%/0%/0% that looks like a measurement. Callers must pass a scale and
#: say where they got it.
_SENSITIVITY_SCALE: float | None = None


def _clip_hazard(h: float) -> float:
    """A hazard is a probability in [0, WORLD_MAX_CHURN_PROBABILITY].

    The upper clip is the world's own churn ceiling and is what keeps `-log(1 - h)` finite; a
    hazard reaching exactly 1.0 would make the cumulative hazard infinite and hand that risk 100%
    of every departure share in the population, silently.
    """
    if h != h or h < 0.0:  # NaN or negative
        return 0.0
    return min(h, WORLD_MAX_CHURN_PROBABILITY)


def build_departure_risks(
    *,
    bill_shock_base: float,
    price_response: float,
    dissatisfaction_response: float,
    market_opportunity: float = 1.0,
    action_propensity: float = 1.0,
    retention_offer_retained_fraction: float = 1.0,
    sensitivity_scale: float | None = None,
) -> dict[str, float]:
    """Return `{cause: hazard}` for one household at one renewal point.

    Every argument is a fact about THIS household's state at THIS renewal, which is what keeps the
    hazards functions rather than constants (see the module note).

    `bill_shock_base` is the churn model's per-household base rate after the engagement
    (passive-renewal) cap -- the one risk that already arrives as a probability and therefore needs
    no fitted sensitivity of its own. `price_response` and `dissatisfaction_response` are the
    world's existing calibrated response curves, both ~1.0 at a neutral household, so the fitted
    scale multiplies a dimensionless response rather than re-deriving a curve that already has a
    source behind it.
    """
    scale = _SENSITIVITY_SCALE if sensitivity_scale is None else sensitivity_scale
    if scale is None:
        raise ValueError(
            "no sensitivity scale: the P0 calibration does not identify one (every value from "
            "0.87 down reproduces the population mean exactly, with reason mixes from 99.9% to "
            "56.6% bill-shock), and the only evidenced value overshoots by 14.9%. Pass "
            "`sensitivity_scale=` explicitly and record where it came from."
        )
    return {
        CAUSE_BILL_SHOCK: _clip_hazard(
            bill_shock_base * market_opportunity * action_propensity
        ),
        # Opportunity-seeking, so market opportunity applies; and the retention offer is a PRICE
        # cut, so it scales this risk and nothing else (P6).
        CAUSE_PRICE_POSITION: _clip_hazard(
            scale * PRICE_IMPORTANCE * price_response
            * market_opportunity * action_propensity * retention_offer_retained_fraction
        ),
        # NOT opportunity-scaled, and this is the substantive consequence of the split. Today a
        # household disgusted with its supplier in 2022 is modelled as 56% less likely to leave
        # because fixed deals were expensive -- a mechanism nobody would defend once it is
        # written down. Dissatisfaction is a reason to leave whatever the market is doing.
        CAUSE_DISSATISFACTION: _clip_hazard(
            scale * SERVICE_IMPORTANCE * dissatisfaction_response * action_propensity
        ),
    }


def survival(risks: dict[str, float]) -> float:
    """Probability the household survives every risk: `Π (1 - h_k)`."""
    s = 1.0
    for h in risks.values():
        s *= (1.0 - h)
    return s


def total_departure_probability(risks: dict[str, float]) -> float:
    """`1 - Π (1 - h_k)`.

    Bounded by 1 and always below `Σ h_k`, which is the whole reason the upper tail compresses
    relative to the multiplicative form it replaces (pre-registration P1).
    """
    return 1.0 - survival(risks)


def cause_shares(risks: dict[str, float]) -> dict[str, float]:
    """Each risk's share of the departures, conditional on a departure happening.

    CUMULATIVE HAZARD, NOT RAW HAZARD, and the difference is what makes this order-free. With
    `λ_k = -log(1 - h_k)`, survival is `exp(-Σλ_k)` exactly, and the continuous-time competing-risks
    result gives `P(cause k | departure) = λ_k / Σλ_j`. Allocating by raw `h_k / Σh_j` instead is
    close but not exact, and its error grows with the hazards -- it would show up as a drift in
    P2's reason mix that no experiment could distinguish from a property of the world.

    Returns an empty mapping when no risk carries any hazard, so the caller must handle "nobody
    could have left" rather than receive a fabricated uniform split.
    """
    lambdas = {c: -math.log(1.0 - h) for c, h in risks.items() if h > 0.0}
    total = sum(lambdas.values())
    if total <= 0.0:
        return {}
    return {c: lam / total for c, lam in lambdas.items()}


def resolve_departure(risks: dict[str, float], roll: float) -> tuple[bool, str | None]:
    """Return `(departed, cause)` for a single deterministic roll in [0, 1).

    ONE ROLL, AND THE SAME COMPARISON DIRECTION AS THE FORM THIS REPLACES. The old code kept the
    account when `roll <= p_retain`, so a departure is the UPPER tail of the roll; keeping that
    convention means the same seed produces the same retain/depart decision wherever the total
    probability is unchanged, and any difference in the event log is attributable to the physics
    rather than to a re-rolled die.

    The cause is read from WHERE IN that upper tail the roll landed, so it costs no second random
    draw and cannot decorrelate from the departure it explains.
    """
    p = total_departure_probability(risks)
    retained_below = 1.0 - p
    if roll <= retained_below:
        return False, None
    shares = cause_shares(risks)
    if not shares:
        # Unreachable while p > 0 (p > 0 implies some h > 0), and fails closed rather than
        # naming an arbitrary cause if that ever stops being true.
        return True, None
    position = (roll - retained_below) / p if p > 0.0 else 0.0
    cumulative = 0.0
    for cause in ORDERED_CAUSES:
        if cause not in shares:
            continue
        cumulative += shares[cause]
        if position < cumulative:
            return True, cause
    return True, ORDERED_CAUSES[-1]


def price_move_symmetry(risks_dearer, risks_parity, risks_cheaper) -> float:
    """`p(+d)·p(−d) / p(0)²` — the anti-goal-seek guarantee, pre-registration P4.

    THE GUARANTEE CHANGES SHAPE UNDER COMPETING RISKS, AND P4 PREDICTED THAT IT WOULD. The
    composed form carried `m(d)·m(−d) == 1` at the population mean because price multiplied the
    WHOLE probability. Here price scales one hazard among several, and the identity does not
    survive that -- writing `p(d) = c + b·m(d)` with `c = 1 - Π_{k≠price}(1 - h_k)` and
    `b = Π_{k≠price}(1 - h_k)·h_price(0)`:

        p(d)·p(−d) = c² + c·b·(m + 1/m) + b²   ≥   c² + 2cb + b² = p(0)²

    since `m + 1/m ≥ 2` for every `m > 0`, with equality only at `m = 1`. So the ratio this
    function returns is **≥ 1 always**, and equals 1 exactly when price is the only risk.

    THE BREAK IS IN THE COMPANY-UNFAVOURABLE DIRECTION, which is why it is kept rather than
    corrected. A ratio below 1 would be the goal-seeking hole R12 exists to close: a supplier could
    price up one year and down the next and end with less churn than holding parity. A ratio above
    1 means symmetric price oscillation costs MORE departures than parity -- over-pricing is
    punished harder than under-pricing is rewarded. Restoring the exact equality would mean
    correcting a bound that runs against us, which is the direction R13 forbids tuning.

    The exact identity survives where it is a property rather than an artefact: at the PRICE
    HAZARD itself, `h_price(d)·h_price(−d) == h_price(0)²` for every household, because
    `churn_position_multiplier` is unchanged and `perceived_price_differential` is linear in the
    differential. Both legs are pinned by `test_departure_risks.py`.
    """
    p0 = total_departure_probability(risks_parity)
    if p0 <= 0.0:
        raise ValueError("price_move_symmetry is undefined at zero parity departure probability")
    return (
        total_departure_probability(risks_dearer)
        * total_departure_probability(risks_cheaper)
    ) / (p0 * p0)


__all__ = [
    "CAUSE_BILL_SHOCK",
    "CAUSE_DISSATISFACTION",
    "CAUSE_PRICE_POSITION",
    "ORDERED_CAUSES",
    "PRICE_IMPORTANCE",
    "SERVICE_IMPORTANCE",
    "UNMODELLED_EXIT_FEE_IMPORTANCE",
    "build_departure_risks",
    "cause_shares",
    "price_move_symmetry",
    "resolve_departure",
    "survival",
    "total_departure_probability",
]
