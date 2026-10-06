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
"""
from __future__ import annotations

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


__all__ = [
    "EFTC_CONTACTED_SWITCHING_SHARE",
    "EFTC_CONTROL_SWITCHING_SHARE",
    "WOKEN_SHARE_AT_FIXED_TERM_END",
    "departure_change_from_contact",
    "engaged_probability_after_contact",
    "rolls_active_renewal_after_contact",
]
