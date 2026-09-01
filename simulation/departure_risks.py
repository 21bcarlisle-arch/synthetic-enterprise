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
#: C1b. The drift off a standard variable tariff, which has no term and therefore no renewal
#: decision to leave AT. It is a fourth REASON and not a fourth modulator: "I was on the default
#: tariff and eventually got round to it" is something a household did, and it is the single
#: largest departure route in a real domestic book, because two thirds of one sits on SVT.
CAUSE_SVT_INERTIA = "svt_inertia"

#: Declared order is presentational only. The cause SHARES below are computed from the hazards'
#: cumulative-hazard weights, which are order-free -- the sequential decomposition
#: (h1, then (1-h1)h2, then ...) is exact in TOTAL but gives earlier risks a systematically larger
#: share, which would bias P2's reason mix by the order of a tuple literal.
ORDERED_CAUSES = (CAUSE_BILL_SHOCK, CAUSE_PRICE_POSITION, CAUSE_DISSATISFACTION,
                  CAUSE_SVT_INERTIA)

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

#: SVT INERTIA, BY TENURE ON THE DEFAULT TARIFF. Annual rates, M confidence.
#:
#: `docs/market_research/svt_rates_active_passive_2016_2025.md` §4, which is explicit that these
#: are STRUCTURAL INFERENCES rather than a published series -- "Direct published SVT vs fixed churn
#: rates by tariff type are not available". Confidence M on every row, and that is carried here
#: rather than left in the source file, because a number whose confidence lives somewhere else gets
#: quoted as though it were H.
#:
#:     SVT long-stayer (3+ years)   ~5-10%   Ofgem engagement surveys: the most inert segment
#:     SVT recent (under 3 years)   ~15-20%  switched once before; some re-engagement
#:
#: THE TOP OF EACH BAND IS TAKEN, and the direction is recorded because the brief requires it.
#: Under the director's §7 tie-break -- where the evidence is ambiguous, choose the option that
#: makes the company's advantage harder to demonstrate -- the higher rate is the harder world: the
#: company loses accounts it has NO renewal lever on, since an SVT account has no renewal to price.
#: It is pure loss with no instrument against it, and it shrinks the book the A/B is measured on.
#:
#: THESE ARE ABSOLUTE RATES AND THEY CARRY A BASE YEAR: 2019-20. §4 states its basis on the
#: all-customer row the segment rows must average to -- "DESNZ: ~6M switches / ~28M accounts
#: (2019-20)" -- which is the published band's own numerator and denominator. The base year is
#: recorded HERE because an absolute rate whose base year lives in someone else's table gets
#: composed with a ratio that has a different one.
#:
#: SO ANY MARKET TERM ADDED HERE MUST DIVIDE BY THE BASE YEAR'S MULTIPLIER, NOT MERELY MULTIPLY BY
#: THE YEAR'S. `market_switching_multiplier` is normalised to `MULTIPLIER_REFERENCE_YEAR = 2024`,
#: and the record puts 2019-20 at 1.3758x of 2024. The repair filed at `18a09617d` is written
#: `floor * market_switching_multiplier(year)`, which levels a 2019-20 rate up into the market it
#: was already measured in: 0.20 becomes 0.2857 at 2020, against a source figure of 0.20. The
#: correct form is `floor * market_switching_multiplier(year) / 1.3758`.
#:
#: THE ERROR IS A CONSTANT FACTOR, SO NO YEAR-SHAPED CHECK CAN SEE IT, and it is exactly zero at
#: 2024 -- the reference year, where `multiplier` is 1.00 by definition and the naive form looks
#: like it did nothing. That is the year a reader spot-checks. Measured and written up at
#: `docs/staging/WORKER_FINDING_THE_SVT_FLOORS_FILED_REPAIR_APPLIES_A_2024_REFERENCED_RATIO_TO_A_2019_20_RATE_2026-08-31.md`.
#: No production caller composes the two today, so nothing is mis-levelled yet; this is here to
#: stop the filed repair being implemented in its filed form.
SVT_INERTIA_ANNUAL_RECENT = 0.20
SVT_INERTIA_ANNUAL_LONG_STAYER = 0.10
#: The published boundary between the two bands, in years on SVT.
SVT_LONG_STAYER_YEARS = 3.0

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

#: WHAT THE PER-YEAR LEVEL ANCHOR CHANGED ABOUT THE PARAGRAPH ABOVE (2026-08-30), AND WHAT IT DID
#: NOT. P0 was one equation -- hold the population mean -- and it tied `a_shock` to the scale, so
#: the family above is the set of pairs satisfying it. `simulation/departure_level_anchor.py` now
#: sets each year's level from the published record, which DISCHARGES that equation: the anchor
#: absorbs whatever level the pair implies, so the pair no longer has a level to hit and only its
#: RATIO survives. That makes `a_shock` cleanly free rather than entangled -- and free is what it
#: still is. No domestic instrument separates "my own bill rose" from "someone else is cheaper";
#: Ofgem's Consumer Impacts survey codes both as one answer, and only the non-domestic instrument
#: splits them, on a population the evidence itself records as differing in kind.
#:
#: THE WORLD STILL HAS TO ROLL A DIE, so a pair is DECLARED below rather than fitted, and the
#: reason mix it produces is published as an INTERVAL over the feasible family -- never as a point.
#: The declared pair is the a_shock = 0.50 row of that family, measured in
#: `docs/staging/WORKER_FINDING_THE_P0_CALIBRATION_IS_EITHER_INFEASIBLE_OR_IT_CHOOSES_THE_ANSWER_2026-08-30.md`
#: §1, and the reason is FIDELITY under R13 and not a tie-break: it is the end of the published
#: feasible set at which all three risks are materially live. The other end (a_shock = 0.87,
#: mix 99.9%/0.0%/0.0%) is a world in which a supplier's price position and service quality cause
#: no departures at all -- which is the defect `churn_position_multiplier` was wired in to remove,
#: arriving again through a calibration parameter. A world where what a supplier does has no
#: consequence is not a harder world, it is an unmodelled one.
DECLARED_SHOCK_WEIGHT = 0.50
DECLARED_SENSITIVITY_SCALE = 0.039520


def _clip_hazard(h: float) -> float:
    """A hazard is a probability in [0, WORLD_MAX_CHURN_PROBABILITY].

    The upper clip is the world's own churn ceiling and is what keeps `-log(1 - h)` finite; a
    hazard reaching exactly 1.0 would make the cumulative hazard infinite and hand that risk 100%
    of every departure share in the population, silently.
    """
    if h != h or h < 0.0:  # NaN or negative
        return 0.0
    return min(h, WORLD_MAX_CHURN_PROBABILITY)


def svt_inertia_hazard(*, years_on_svt: float, segment_days: float) -> float:
    """The drift off a standard variable tariff, over ONE cap period of `segment_days`.

    C1b. Returns 0.0 for an account that is not on SVT -- the caller signals that by passing
    `segment_days <= 0`, which is what a fixed-term account's renewal point has: no cap period
    elapsed under a variable tariff.

    WHY THE CONVERSION IS CONSTANT-HAZARD AND NOT A FLAT QUARTERLY RATE. The published anchor is
    ANNUAL and the world's SVT segments are cap periods, which are neither equal nor quarters: the
    first one runs from the day a household arrives to the next cap boundary, so it can be 47 days.
    A flat per-quarter rate would charge a 47-day segment the same as a 92-day one. Driven at the
    real segment lengths the cap calendar emits, before this function was written:

        days     recent (.20)   long-stayer (.10)
          47        0.02831          0.01347
          90        0.05350          0.02563
          92        0.05466          0.02619

    and the four real cap quarters of a year recompose to 0.19988 / 0.09994 against targets of
    0.20 / 0.10 -- the shortfall is the 365 vs 365.25 day-count and is not worth a correction it
    would take a sentence to explain.

    WHAT WOULD HAVE BEEN WRONG, AND BY HOW MUCH. Using the annual figure as a per-quarter rate
    gives 1-(1-0.20)**4 = 0.5904 a year against 0.20: nearly three times the anchor, in the
    direction that flatters nothing and is simply wrong. Pinned by
    `test_the_annual_anchor_recomposes_from_the_segment_hazard`.
    """
    if segment_days <= 0:
        return 0.0
    annual = (SVT_INERTIA_ANNUAL_LONG_STAYER if years_on_svt >= SVT_LONG_STAYER_YEARS
              else SVT_INERTIA_ANNUAL_RECENT)
    return _clip_hazard(1.0 - (1.0 - annual) ** (segment_days / 365.25))


def build_departure_risks(
    *,
    bill_shock_base: float,
    price_response: float,
    dissatisfaction_response: float,
    market_opportunity: float = 1.0,
    action_propensity: float = 1.0,
    retention_offer_retained_fraction: float = 1.0,
    sensitivity_scale: float | None = None,
    shock_weight: float = 1.0,
    level_anchor: float = 1.0,
    svt_inertia: float = 0.0,
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

    `shock_weight` is `a_shock`, the within-price split. It is FREE and the caller declares it;
    see the note on `_SENSITIVITY_SCALE`.

    `level_anchor` is the YEAR'S LEVEL and it is not a preference either -- it is what makes this
    form able to sit on the published record at all. It scales every hazard by the same factor, so
    it moves the year's departure LEVEL and cannot move the reason MIX within that year: the
    published rate says how many households left in 2020, the hazards say which ones and why. See
    `simulation/departure_level_anchor.py` for where the number comes from and why one constant
    could not do this job.
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
            level_anchor * shock_weight * bill_shock_base
            * market_opportunity * action_propensity
        ),
        # Opportunity-seeking, so market opportunity applies; and the retention offer is a PRICE
        # cut, so it scales this risk and nothing else (P6).
        CAUSE_PRICE_POSITION: _clip_hazard(
            level_anchor * scale * PRICE_IMPORTANCE * price_response
            * market_opportunity * action_propensity * retention_offer_retained_fraction
        ),
        # NOT opportunity-scaled, and this is the substantive consequence of the split. Today a
        # household disgusted with its supplier in 2022 is modelled as 56% less likely to leave
        # because fixed deals were expensive -- a mechanism nobody would defend once it is
        # written down. Dissatisfaction is a reason to leave whatever the market is doing.
        CAUSE_DISSATISFACTION: _clip_hazard(
            level_anchor * scale * SERVICE_IMPORTANCE
            * dissatisfaction_response * action_propensity
        ),
        # C1b. DAMPED BY ACTION PROPENSITY like every other risk, and the first draft of this
        # line was not -- the argument being that the published 10-20% band is measured across a
        # real SVT population and so already contains its engagement mix, making a second
        # multiplication a double-count.
        #
        # `test_action_propensity_damps_every_risk_because_it_is_not_a_reason_anyone_left` reds on
        # that exception, and it is the better rule: the general property ("engagement is not a
        # reason anyone left, it gates whether they act at all") holds for drifting off SVT
        # exactly as it holds for responding to a price. A carve-out justified by one anchor's
        # provenance would make this the one risk a disengaged household runs at full rate.
        #
        # THE CONSEQUENCE IS REAL AND IS PREDICTED HERE RATHER THAN DISCOVERED LATER. Measured on
        # the live book across its own tenure mix and every income-stress level:
        # `action_propensity` has mean 0.8635 (min 0.488, max 1.100), materially below 1.0 -- so
        # damping SHIFTS the SVT sub-population's realised rate down by roughly 14%, it does not
        # merely add spread around the anchor. **Prediction, filed before the assignment run: the
        # realised SVT departure rate will land near the BOTTOM of the published band, or just
        # under it, and if it does, the repair is to divide the anchor by the book's own mean
        # propensity -- never to widen the band.** Same discipline as the year-level anchor's own
        # note: a reading out of band means the anchor has gone stale, not that the record has.
        CAUSE_SVT_INERTIA: _clip_hazard(level_anchor * svt_inertia * action_propensity),
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
