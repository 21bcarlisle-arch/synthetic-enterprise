"""The population the arm's reach is a share OF, derived from the funnel's own stage counts.

WHY THIS EXISTS (2026-09-07)
----------------------------
`site/data/value_arms.json` published the per-customer arm's reach as

    priced / renewals_the_world_offered  =  216 / 2,039  =  10.59%

and that ratio is not a measure of the method. Its denominator is every TERM BOUNDARY the world
put in front of the arm; its numerator is renewals at which a rate was struck and the arm moved
it. Two correct figures whose ratio is not a quantity — 1,350 of those boundaries are households
on the standard variable tariff, where 2019 onward the rate is the Ofgem default-tariff cap, set
per region and payment method and never struck per household. So the published number is mostly a
measure of what fraction of a domestic book sits on a default tariff: a published fact about GB,
and not a result of this company.

The decision is filed as `docs/staging/SEAT_DECISION_AN_SVT_HOUSEHOLD_IS_NOT_A_DECISION_THIS_ARM
_DECLINES_2026-09-07.md`. Its conclusion: `renewal_margin_uplift` has NO decision to make at an
SVT boundary and its refusal there is correct; the defect is the ratio downstream of it. Both
numbers belong on the page, each with the sentence saying what it counts, and the claim about the
METHOD divides by the decision population.

THE PROPERTY, STATED BEFORE ANYTHING IS DIVIDED
-----------------------------------------------
A renewal PRESENTED A DECISION when all three of these held at the moment the term was struck:

  1. this supplier sells the fuel;
  2. a prior term existed, so there is something observed to price against;
  3. the supplier itself struck a rate for THIS household, which some later party could move.

Every guard the arm fires before `no_observed_history` refuses because one of those three was
false — the world never put a per-customer rate-setting decision in front of the arm. Every stage
from `no_observed_history` onward refuses, or answers, with all three true: the decision existed
and the arm either made it, declined it, or lacked the inputs to make it.

That is why membership is a dict with a reason per stage and not a slice of `FUNNEL_STAGES`. A
slice would be a control pinned to today's guard ORDER; the reason is a statement about the
world that a reader can disagree with by name.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here asserts that the population is 279 or
that most refusals are SVT. `no_observed_history` counts ZERO on every run measured so far and is
still IN the population, because a renewal the world offered and the arm could not price for want
of history is a decision the arm failed to make — counting it out would be fitting the denominator
to the flattering answer. If a future run puts renewals there, the reach falls and it should.

FAIL CLOSED. A funnel carrying a stage this module has never heard of gets `available: False`
naming the stage, not a population computed over the stages it did recognise: a denominator
silently missing a guard is exactly the defect this module was built to repair, one level down.

WHAT IS NOT COUNTED, AND SAID SO
--------------------------------
The product gate's own breakdown separates refusals that are the world's shape (SVT: no rate was
struck) from refusals that are OUR record defect (unlabelled: a household is on SOMETHING and we
lost it). The defect bucket is renewals whose membership is UNKNOWN, not renewals known to be
outside — so it is excluded from the population and published beside it with the population it
would produce if the owed fidelity determination admits it. That figure is a PREDICTION filed
before the determination is made, and the determination must be decided on fidelity grounds blind
to it (R13).

REUSE
-----
REUSE: tools/decisions_that_existed.py
CLASS: CUSTOM
INDEX: searched "decision population", "denominator", "priced share", "reach", "funnel stage",
       "renewals offered".
       `tools/product_gate_refusal.py` is the module this one is SHAPED after — same producer-
       and-publisher split, same fail-closed posture, same refusal to assert a cause — and it is
       IMPORTED here for the defect/structural split rather than re-deriving which products are a
       defect. It cannot be extended to do this job: it reads ONE stage's per-value breakdown and
       this reads every stage's count.
       `tools/run_value_cycle_ab.renewal_funnel` is the PRODUCER of the counts and calls this;
       it deliberately interprets nothing itself.
       `tools/generate_value_arms_data._exclusions` is the PUBLISHER and calls this too, for the
       reason `product_gate_refusal` records: the page renders artefacts weeks old, so a
       population computed only at run time would reach the reader stale or not at all.
       `company/pricing/value_based_renewal.FUNNEL_STAGES` owns the stage vocabulary and is
       IMPORTED, never restated — a second literal list of the arm's stages is one name and two
       answers.
"""
from __future__ import annotations

from company.pricing.value_based_renewal import (
    FUNNEL_STAGES,
    STAGE_ACQUISITION_TERM,
    STAGE_CONTROL_ARM,
    STAGE_DECLINED,
    STAGE_NO_LOCKED_RATE,
    STAGE_NO_OBSERVED_HISTORY,
    STAGE_NOT_THE_ARMS_COMMODITY,
    STAGE_PRICED,
    STAGE_PRODUCT_NOT_UPLIFTABLE,
)
from tools.product_gate_refusal import refusal_breakdown

#: Whether a renewal that stopped at this stage EVER PRESENTED A DECISION, and why — set at one
#: statement per stage so the flag and its reason cannot drift apart, which is the failure that
#: put a five-day-dead sentence under this funnel's largest drop.
#:
#: The reason is the load-bearing half. A reader who thinks a stage is on the wrong side has a
#: sentence to argue with rather than a boolean to guess at.
STAGE_PRESENTED_A_DECISION: dict[str, tuple[bool, str]] = {
    STAGE_CONTROL_ARM: (False, (
        "the arm was not running. Nothing was decided and nothing was declined; on the control "
        "this stage is the whole funnel by construction.")),
    STAGE_NO_LOCKED_RATE: (False, (
        "no rate was struck for this household. A deemed or flex period is priced at settlement, "
        "so there is no per-customer rate for this arm or any other to have moved.")),
    STAGE_ACQUISITION_TERM: (False, (
        "term 0. This is the household's FIRST term with us, so there is no prior rate to move "
        "and no settled history to price against. It is an acquisition, not a renewal.")),
    STAGE_NOT_THE_ARMS_COMMODITY: (False, (
        "a fuel this supplier does not sell. The world offered no decision because the world "
        "offered no supply.")),
    STAGE_PRODUCT_NOT_UPLIFTABLE: (False, (
        "the household's product carries no rate this supplier struck for it. From 2019 an SVT "
        "rate is the Ofgem default-tariff cap, set per region, payment method and consumption "
        "level; before that it was a published per-supplier tariff-level rate. Either way it is "
        "not a per-household strike, so there is no object for a per-customer writer to take as "
        "its argument. WHAT A REAL SUPPLIER DECIDES HERE IS A CONVERSION -- whether to serve this "
        "household a fixed deal -- which is an acquisition-shaped decision about an existing "
        "customer and is a desk this company has not built.")),
    STAGE_NO_OBSERVED_HISTORY: (True, (
        "IN THE POPULATION, and this is the entry worth contesting. The rate was struck, the "
        "prior term existed and the fuel is ours: the world put a decision in front of the arm "
        "and the arm had no settled history inside its observation window to make it from. That "
        "is a decision we FAILED to make, not one that was never offered. This stage has counted "
        "zero on every run measured so far, which is exactly why it is written down: a "
        "denominator that quietly drops the ways we lose is fitted to the answer.")),
    STAGE_DECLINED: (True, (
        "the arm ran, looked, and found no margin surviving both the price cap and the churn "
        "model's support bound. A decision made.")),
    STAGE_PRICED: (True, (
        "the arm chose a margin for this household. A decision made.")),
}


def _unknown_stages(stages: list) -> list[str]:
    """Stage names in the funnel, or in the arm's vocabulary, that this module cannot place.

    BOTH directions. A stage the arm grew and this module has no entry for would silently leave
    its renewals out of every denominator; an entry here for a stage the arm no longer has is a
    membership rule about nothing, and reads to the next author as settled.
    """
    seen = {s.get("stage") for s in stages if isinstance(s, dict)}
    return sorted(
        {str(s) for s in seen if s not in STAGE_PRESENTED_A_DECISION}
        | {str(s) for s in FUNNEL_STAGES if s not in STAGE_PRESENTED_A_DECISION})


def decisions_that_existed(funnel: dict) -> dict:
    """The renewals at which a decision existed, and the arm's reach over them. Never asserts.

    Returns, always:
      available                             -- False when the funnel carries no usable stages
      reason                                -- why, when unavailable
      decisions_that_existed                   -- renewals that presented a decision
      priced / declined                     -- the numerator and its sibling
      priced_share_of_the_decisions_that_existed
      renewals_the_world_offered            -- every term boundary, kept as CONTEXT
      priced_share_of_renewals_offered      -- the old ratio, kept and named for what it is
      in_the_population / outside_it        -- one row per non-empty stage, with its reason
      unresolved                            -- refusals whose membership is not established
      what_each_denominator_counts          -- the sentence pair, derived
    """
    stages = funnel.get("stages")
    if not isinstance(stages, list) or not stages:
        return {
            "available": False,
            "reason": (
                "this run's funnel carries no per-stage counts, so the population a reach claim "
                "would divide by cannot be derived. It is NOT reconstructed from the totals: a "
                "denominator guessed at is the defect this surface exists to have repaired."),
        }
    unknown = _unknown_stages(stages)
    if unknown:
        return {
            "available": False,
            "reason": (
                "the arm's funnel carries stage(s) {} that no membership rule places on either "
                "side of 'did a decision exist here'. The population is NOT computed over the "
                "stages that were recognised -- a denominator silently missing a guard is "
                "precisely the failure this module repairs one level down. Add the stage to "
                "`tools/decisions_that_existed.STAGE_PRESENTED_A_DECISION` with its reason."
            ).format(", ".join(repr(s) for s in unknown)),
        }

    inside, outside = [], []
    for stage in stages:
        if not isinstance(stage, dict):
            continue
        name = stage.get("stage")
        count = stage.get("count") or 0
        member, why = STAGE_PRESENTED_A_DECISION[name]
        row = {"stage": name, "count": count, "why": why}
        (inside if member else outside).append(row)

    population = sum(row["count"] for row in inside)
    priced = next((r["count"] for r in inside if r["stage"] == STAGE_PRICED), 0)
    offered = funnel.get("renewals_the_world_offered")

    # WHAT IS NOT COUNTED AND IS NOT KNOWN TO BE OUTSIDE. The product gate refuses two kinds of
    # renewal and only one of them is the market's shape; the other is a record whose product the
    # world never decided, and whether those households presented a decision is owed a fidelity
    # determination. Unknown is published as unknown.
    breakdown = refusal_breakdown(funnel.get("product_not_upliftable_by_tariff_type"))
    undecided = breakdown["defect_count"] if breakdown["available"] else 0
    unresolved = {
        "renewals": undecided,
        "what_they_are": (
            "refusals at the product gate whose record carries no decided product at all. A "
            "household on the book is on SOMETHING, so these are neither established as inside "
            "the population nor as outside it, and they are EXCLUDED rather than assumed either "
            "way."),
        "if_the_owed_determination_admits_them": {
            "decisions_that_existed": population + undecided,
            "priced_share_of_the_decisions_that_existed": (
                round(priced / (population + undecided), 4) if population + undecided else None),
        },
        "this_is_a_prediction_not_a_result": (
            "filed BEFORE the fidelity determination is made. That determination is a question "
            "about whether the drawn book should carry a decided product and must be settled on "
            "fidelity grounds, blind to what it does to this ratio (R13)."),
    } if undecided else None

    return {
        "available": True,
        "what_this_is": (
            "The renewals at which a rate was struck for this household and a prior term existed "
            "-- the population at which a per-customer renewal-pricing decision was actually "
            "available to be made -- and the share of them this arm priced. Derived from the "
            "funnel's own stage counts at publication time, never read from the artefact, so a "
            "run written before this existed still gets one."),
        "decisions_that_existed": population,
        "priced": priced,
        "declined": next((r["count"] for r in inside if r["stage"] == STAGE_DECLINED), 0),
        "priced_share_of_the_decisions_that_existed": (
            round(priced / population, 4) if population else None),
        "renewals_the_world_offered": offered,
        "priced_share_of_renewals_offered": funnel.get("priced_share_of_renewals_offered"),
        "in_the_population": [r for r in inside if r["count"]],
        "outside_it": sorted((r for r in outside if r["count"]), key=lambda r: -r["count"]),
        "unresolved": unresolved,
        # BOTH NUMBERS, EACH NAMED. Neither alone is the answer, and the failure being repaired is
        # that one of them was published as though it were.
        "what_each_denominator_counts": {
            "renewals_the_world_offered": (
                "every TERM BOUNDARY the world put in front of the arm, including households on "
                "a default tariff whose boundary is a price-cap revision rather than an expiry. "
                "It is the book's shape and it is context: the share of it sitting on a default "
                "tariff is a published fact about GB, not a result of this company."),
            "decisions_that_existed": (
                "the boundaries at which a rate this supplier struck for this household existed "
                "and a prior term existed to price against. It is the denominator of any claim "
                "about the METHOD, because it is the set of decisions there were to make."),
        },
        "reading": _reading(population, priced, offered, unresolved),
    }


def _reading(population: int, priced: int, offered, unresolved: dict | None) -> str:
    """The sentence a reader gets, composed from the counts rather than authored.

    A reach that is small because the book is mostly on a default tariff and a reach that is
    small because the method fails are the same fraction and opposite conclusions, so the
    sentence says which of the two this run is showing, from its own numbers.
    """
    if not population:
        return (
            "This run offered the arm no renewal at which a decision existed, so it carries no "
            "reading about the method's reach at all. That is a statement about the run, not a "
            "result: a reach over an empty population is undefined and is published as such.")
    share = 100.0 * priced / population
    out = (
        "The arm priced {priced:,} of the {population:,} renewals at which a decision existed -- "
        "{share:.1f}%.".format(priced=priced, population=population, share=share))
    if isinstance(offered, int) and offered > population:
        # NOT "carried no struck rate": an acquisition term carries one and is outside the
        # population for the OTHER reason, and collapsing the two would state a single cause for a
        # remainder that has more than one -- the shape this panel has already published twice.
        out += (
            " The world put {offered:,} term boundaries in front of it; at {gap:,} of those there "
            "was no per-customer renewal decision to make -- no rate this supplier had struck for "
            "that household, or no prior term to move one from -- so they are context and not a "
            "denominator. READ BOTH: the first number is about the method, the second is about "
            "the book's product mix.".format(offered=offered, gap=offered - population))
    if unresolved:
        out += (
            " A further {n:,} refusals carry no decided product at all and are excluded as "
            "UNKNOWN rather than counted either way.".format(n=unresolved["renewals"]))
    out += (
        " R12: a diagnostic. Neither denominator is a target and this is specifically not a cue "
        "to relax a guard so the population gets bigger.")
    return out
