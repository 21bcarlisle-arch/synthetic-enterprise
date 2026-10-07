"""How a household answers a contact from its supplier at a fixed-term end -- the world side (W2_39).

A CONTACT WAKES; IT DOES NOT DECIDE. Three randomised trials agree on one structure
(`docs/market_research/how_households_respond_to_supplier_contact.md`): a contact makes a share of
the households who would not otherwise have chosen at this moment choose, and a woken household
then chooses by the same price comparison as anyone who chooses. Ofgem's EFTC letter woke
households whose best visible option was their own supplier's, and they re-fixed internally
(14% -> 23%) while external loss stayed at 6%. CMOC and Ascarza et al. (2016) woke households
whose best option was a rival's, or whose plan fitted badly, and they left. So this module plants
NO uplift. The sign of a contact's effect on a household is that household's own -- persuadable,
sure thing, lost cause or sleeping dog -- and follows from its engagement before the contact and
from its price position. The size of a retention offer acts through the latter, via price physics
the world already has.

THE ONE MAGNITUDE, DERIVED NOT TYPED. `WOKEN_SHARE_AT_FIXED_TERM_END` is computed from EFTC's two
published switching rates. EFTC's population (customers ending a one-year fix, written to a few
days before term end) is the world's fixed-term decision.

NAMED SIMPLIFICATIONS:
  1. One woken share for every household (the share of the not-yet-engaged that a contact wakes).
     EFTC's subgroups fit this, a constant pp and a constant ratio about equally. This form is the
     one that stays a probability for every p. Error direction unknown.
  2. The woken share does not vary with the saving the contact names. CMOC shows it should, but
     its cells confound saving with meter type, and EFTC ran at one level (research doc gap 2).
  3. No memory. Ofgem's 2020 follow-up found no persistence in its control arm (gap 3).

The roll is COUPLED to `renewal_engagement.rolls_active_renewal`: the same seed and the same
uniform draw, compared against the contacted probability. A household's contacted and uncontacted
outcomes are therefore both defined. That pair is the true counterfactual an uplift estimate is
graded against (B8, C34), and it is ground truth -- it never crosses the seam. Only whether the
household chose, and what it chose, is observable to a supplier.

NOT WIRED. No run-loop caller passes a contact here yet. Wiring is level 2; the research doc §5
names the question the wiring has to answer first.

BETWEEN BOUNDARIES, ON DEFAULT-TARIFF STOCK (PB4 R6, 2026-10-07). The SVT drift
(`departure_risks.svt_inertia_hazard`) has no saving term, so before this a disengaged household's
elasticity reached behaviour only on the renewal roll, which happened 5 times across 25 such
households in a run. `svt_departure_after_contact` is the second route. A contact wakes a share of
the stock, and that share is set by the INSTRUMENT, not the saving: the CMOL, CMOC and Collective
Switch trials showed savings of the same order and woken shares 14x apart (research doc §2.7). A
woken household then chooses by price comparison, which `churn_if_choosing_off_svt` gives through
the world's own loss curve and the household's own elasticity. How the woken share moves with the
saving is not published causally, and it is carried as `WOKEN_SHARE_SAVING_GRADIENT_ON_SVT_STOCK =
None`. Nothing in the world sends a contact yet, so this route is not wired either.
"""
from __future__ import annotations

from simulation.departure_risks import (
    DECLARED_SENSITIVITY_SCALE,
    DECLARED_SHOCK_WEIGHT,
    build_departure_risks,
    total_departure_probability,
)
from simulation.market_switching_propensity import (
    churn_position_multiplier,
    perceived_price_differential,
)
from simulation.renewal_engagement import rolls_active_renewal

# Ofgem, End of Fixed Term Communications Trial (Sept 2019) §4.1 / Fig. 4.1, n=19,553:
# switching within six weeks of a one-year fix ending.
EFTC_CONTROL_SWITCHING_SHARE = 0.19
EFTC_CONTACTED_SWITCHING_SHARE = 0.28

#: The share of households who would NOT have chosen at a fixed-term end that a contact makes
#: choose. 0.1111, derived from the two rates above.
WOKEN_SHARE_AT_FIXED_TERM_END = (
    (EFTC_CONTACTED_SWITCHING_SHARE - EFTC_CONTROL_SWITCHING_SHARE)
    / (1.0 - EFTC_CONTROL_SWITCHING_SHARE)
)


def engaged_probability_after_contact(p_engaged: float, contacted: bool) -> float:
    """The probability this household chooses at its fixed-term end, given whether it was contacted.

    `p_engaged` is its own probability without a contact (the archetype the world already threads
    into `rolls_active_renewal`). A contact wakes `WOKEN_SHARE_AT_FIXED_TERM_END` of the remainder.
    """
    if not 0.0 <= p_engaged <= 1.0:
        raise ValueError(f"p_engaged must be a probability, got {p_engaged!r}")
    if not contacted:
        return p_engaged
    return p_engaged + WOKEN_SHARE_AT_FIXED_TERM_END * (1.0 - p_engaged)


def rolls_active_renewal_after_contact(
    term_start_str: str, seed: str, p_engaged: float, contacted: bool,
) -> bool:
    """`rolls_active_renewal`, on the same draw, at the contacted probability.

    Same seed, same uniform: a household that chooses uncontacted also chooses contacted, so a
    contact can wake a household and can never put one to sleep. A boundary inside the FTC
    withdrawal window stays passive whatever the contact -- there was no fixed deal to take.
    """
    return rolls_active_renewal(
        term_start_str, seed, engaged_probability_after_contact(p_engaged, contacted))


def departure_change_from_contact(
    p_engaged: float, churn_if_engaged: float, churn_if_inert: float,
) -> float:
    """How much a contact changes this household's probability of leaving at its fixed-term end.

    Only the woken households change behaviour, and each moves from its inert churn to its engaged
    churn. The sign is the household's: positive (the contact CAUSES loss, a sleeping dog) where
    choosing exposes it to a better rival than staying inert would, negative (a persuadable) where
    its own supplier's offer is the best thing it sees, zero for a sure thing or a lost cause
    whose two churns are equal. A deeper retention offer lowers `churn_if_engaged`, which is how
    its size enters.
    """
    woken = engaged_probability_after_contact(p_engaged, True) - p_engaged
    return woken * (churn_if_engaged - churn_if_inert)


# Ofgem, Cheaper Market Offers Letter trial report and technical annex (Nov 2017): SVT customers
# of more than a year at two suppliers, n=137,876, any switch within 30 days, supplier-branded arm.
CMOL_CONTROL_SWITCHING_SHARE = 0.010
CMOL_SUPPLIER_LETTER_SWITCHING_SHARE = 0.034

# Ofgem, Cheaper Market Offers Communications trials (Sept 2019): default-tariff customers at five
# suppliers, ~600,000, any switch within 30 days, mean across all treatment arms.
CMOC_CONTROL_SWITCHING_SHARE = 0.029
CMOC_CONTACTED_SWITCHING_SHARE = 0.068

# Ofgem, Collective Switch trials final report (Sept 2019), first trial: SVT for 3+ years at one
# large supplier, ~50,000, three letters over seven weeks with an exclusive tariff and a phone line.
COLLECTIVE_SWITCH_CONTROL_SWITCHING_SHARE = 0.026
COLLECTIVE_SWITCH_CONTACTED_SWITCHING_SHARE = 0.224


def _woken_share(control: float, contacted: float) -> float:
    return (contacted - control) / (1.0 - control)


#: The share of default-tariff stock that one contact of each kind wakes between fixed-term
#: boundaries, derived from each trial's two published rates: 0.024 / 0.040 / 0.203. Keyed by the
#: trial, because what separates these is the instrument (friction removed, a reminder, a
#: deadline), not the saving it named, which was GBP 200-300 in all three.
WOKEN_SHARE_OF_SVT_STOCK = {
    "cmol_supplier_letter": _woken_share(
        CMOL_CONTROL_SWITCHING_SHARE, CMOL_SUPPLIER_LETTER_SWITCHING_SHARE),
    "cmoc_letter": _woken_share(CMOC_CONTROL_SWITCHING_SHARE, CMOC_CONTACTED_SWITCHING_SHARE),
    "collective_switch": _woken_share(
        COLLECTIVE_SWITCH_CONTROL_SWITCHING_SHARE, COLLECTIVE_SWITCH_CONTACTED_SWITCHING_SHARE),
}

#: HOW THE WOKEN SHARE OF SVT STOCK MOVES WITH THE SAVING IS NOT ESTABLISHED, so this is None. CMOL's
#: +0.52 pp per GBP 100 is pooled across arms with saving as a main effect; CMOC's +1.2-1.3 pp per GBP
#: 100 is among the contacted only; the saving was never randomised in either (research doc §2.7).
#: Those two figures are what the composed route is GRADED against, not inputs to it. The saving
#: reaches a woken household through `churn_if_choosing_off_svt`, i.e. through its own elasticity.
WOKEN_SHARE_SAVING_GRADIENT_ON_SVT_STOCK: float | None = None


def churn_if_choosing_off_svt(
    *, our_premium_pct: float, elasticity: float, annual_bill_gbp: float, level_anchor: float,
    action_propensity: float = 1.0,
) -> float:
    """The probability a woken default-tariff household leaves, rather than re-fixing with us.

    `our_premium_pct` is the best thing we put in front of it (our cheapest fix, or the SVT itself
    if we offer nothing) against the best the market shows it, as a fraction: +0.2 is 20% dearer.
    The household feels that through its OWN elasticity, on its OWN bill in pounds, through the
    loss curve every active renewal uses. Bill shock is zero, since no renewal bill is in front
    of it, and service is neutral. `level_anchor` is the year's, as at a renewal.
    """
    risks = build_departure_risks(
        bill_shock_base=0.0,
        price_response=churn_position_multiplier(
            perceived_price_differential(our_premium_pct, elasticity), annual_bill_gbp),
        dissatisfaction_response=1.0,
        action_propensity=action_propensity,
        sensitivity_scale=DECLARED_SENSITIVITY_SCALE,
        shock_weight=DECLARED_SHOCK_WEIGHT,
        level_anchor=level_anchor,
    )
    return total_departure_probability(risks)


def svt_departure_after_contact(
    *, instrument: str, p_drift: float, churn_if_choosing: float,
) -> float:
    """This SVT segment's departure probability when a contact of `instrument` reaches the household.

    A household that would have drifted still drifts. Of the rest, the instrument's woken share
    chooses, and a chooser leaves with `churn_if_choosing` and otherwise re-fixes with us. So on
    THIS segment a contact can only add departures: waking your own default stock costs some of it
    now, and the households it keeps are on a fix, where the next term end is a choice. That
    trade is the company's to weigh. The world only has to make it real.
    """
    for name, p in (("p_drift", p_drift), ("churn_if_choosing", churn_if_choosing)):
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"{name} must be a probability, got {p!r}")
    if instrument not in WOKEN_SHARE_OF_SVT_STOCK:
        raise ValueError(
            f"no woken share for instrument {instrument!r}: the sourced ones are "
            f"{sorted(WOKEN_SHARE_OF_SVT_STOCK)}, and an unsourced contact cannot be given one")
    woken = WOKEN_SHARE_OF_SVT_STOCK[instrument]
    return p_drift + (1.0 - p_drift) * woken * churn_if_choosing


__all__ = [
    "WOKEN_SHARE_OF_SVT_STOCK",
    "WOKEN_SHARE_SAVING_GRADIENT_ON_SVT_STOCK",
    "churn_if_choosing_off_svt",
    "svt_departure_after_contact",
    "EFTC_CONTACTED_SWITCHING_SHARE",
    "EFTC_CONTROL_SWITCHING_SHARE",
    "WOKEN_SHARE_AT_FIXED_TERM_END",
    "departure_change_from_contact",
    "engaged_probability_after_contact",
    "rolls_active_renewal_after_contact",
]
