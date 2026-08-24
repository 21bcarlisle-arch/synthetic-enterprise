"""Seam: the world reports the loss; the supplier decides whether to replace it.

KNIFE pass 3, `A_composition_lift` step 27, disposition register §3v. Cuts the
acquire-or-retain half of two crossings on `simulation/run_phase2b.py`:

  * `simulation.run_phase2b -> saas.growth_mandate`
  * `simulation.run_phase2b -> saas.ledger`

The overhead half of the same two modules is a SECOND, narrower door —
`company/interfaces/fixed_overhead.py` — and §3v argues why it is not this one.

WHAT THE WORLD WAS DOING THAT IS NOT THE WORLD'S. A customer leaving is the
world's fact and still arrives as one. Everything the world did NEXT was the
supplier's:

  * whether the portfolio is being grown, held flat or wound down (`MANDATE`);
  * what an acquisition attempt is worth spending (`COST_PER_ACQUISITION`, a
    per-segment table the world held in its own namespace);
  * whether to go to market at all when the cap would force the deal below
    wholesale cost (`should_attempt_acquisition`);
  * how much of a lost customer's replacement cost counts as value protected in
    its own retention guard;
  * and the SHAPE OF ITS OWN LEDGER ROWS — the world was constructing the
    supplier's acquisition-spend, gate and retention-cost events by hand.

Every one of those is a commercial judgement a real supplier makes and is
allowed to get WRONG, which is the belief-vs-truth gap the COUPLED TRIAD scores.
None is physics. So this is a DOOR and not a module move: unlike §3u's demand
response, nothing here is misfiled — `saas/growth_mandate.py` and
`saas/ledger.py` are on the correct side of the wall already and have five other
company-side consumers. What was wrong was the world reaching THROUGH them.

THE TABLES ARE DELIBERATELY NOT RE-EXPORTED HERE. `COST_PER_ACQUISITION` and
`FIXED_COST_MONTHLY` are per-market quantities; the portability law's rule 2
(`tests/architecture/test_market_at_the_seams.py`) refuses those on a seam
surface, and a second market sets both for itself. The door returns a BUDGET for
one named segment — a decided number, not the decision table — and the imports
that produce it are made inside the function bodies rather than at module scope.
That is the same measured device as `company/interfaces/renewal_rate_chain.py`:
a module-level import would put the table in this module's namespace, so a
caller could reach it THROUGH the door while the epistemic ratchet stayed green,
because the import still terminates on the exempt seam package.

Controls: `tests/company/interfaces/test_growth_desk_seam.py`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "AcquisitionDecision",
    "book_acquisition_gate",
    "book_acquisition_spend",
    "book_retention_cost",
    "decide_acquisition",
    "growth_mandate_label",
    "mandate_permits_replacement",
    "replacement_cost_avoided_gbp",
]


@dataclass(frozen=True)
class AcquisitionDecision:
    """What the supplier decided to do about one lost supply point.

    The standing MANDATE is deliberately NOT a field here — it is
    `mandate_permits_replacement()`, asked earlier and separately, and the split
    is load-bearing rather than tidy. The mandate is a portfolio stance that
    needs nothing about the customer; the gate is a per-attempt affordability
    judgement that needs the segment, the commodity and this term's forward. The
    two also produce DIFFERENT artefacts — a mandate that forbids replacement
    books nothing at all, while a gate refusal books a zero-amount gate event so
    the suppression stays visible in the ledger. One combined flag would lose
    which of the two suppressed an attempt, and asking one combined question
    would force the world to look the customer up before it is entitled to.
    """

    attempt: bool
    gate_reason: str | None
    budget_gbp: float


def growth_mandate_label() -> str:
    """The supplier's standing portfolio stance, for its own run record.

    A LABEL, for reporting only: the world must not branch on this string. Ask
    `mandate_permits_replacement()` whether replacement is allowed, and
    `decide_acquisition` whether this particular attempt goes ahead.
    """
    from saas.growth_mandate import MANDATE

    return MANDATE


def mandate_permits_replacement() -> bool:
    """May the supplier go to market at all to replace a loss?

    False only under a wind-down mandate. This is the question the world used to
    answer for itself by comparing the mandate string to the literal `"shrink"`
    — which meant the world both held the stance and knew which of its values
    meant stop.
    """
    from saas.growth_mandate import MANDATE

    return MANDATE != "shrink"


def decide_acquisition(
    *,
    segment: str,
    commodity: str,
    company_fwd_gbp_per_mwh: float,
    term_start: str,
) -> AcquisitionDecision:
    """Ask the supplier whether to go to market to replace a lost supply point.

    Keyword-only on purpose — four same-shaped scalars in a row is how a caller
    swaps `segment` and `commodity` without either side noticing.

    Every parameter is a plain value or an observable the world already holds:
    the segment and commodity of the point that was lost, the term's start, and
    the supplier's OWN forward — not the world's. There is deliberately no
    parameter through which a caller could supply, or reach, the per-segment
    cost table or the cap lookup behind the gate.
    """
    from saas.growth_mandate import COST_PER_ACQUISITION, should_attempt_acquisition

    budget_gbp = COST_PER_ACQUISITION.get(segment, 150.0)
    attempt, gate_reason = should_attempt_acquisition(
        segment, commodity, company_fwd_gbp_per_mwh, term_start
    )
    return AcquisitionDecision(
        attempt=attempt,
        gate_reason=gate_reason,
        budget_gbp=budget_gbp,
    )


def replacement_cost_avoided_gbp(*, segment: str, counted_in_guard: bool) -> float:
    """What retaining this customer saves the supplier in replacement spend.

    `counted_in_guard` is the supplier's own policy switch
    (`policy.include_acq_cost_saved_in_guard`), passed as a plain bool so the
    world never has to hold a policy object to ask the question. The frozen
    NAIVE baseline sets it False — the pre-Phase-15b margin-only guard — and
    this function then returns 0.0 rather than the segment's cost, which is the
    whole of that policy's effect.
    """
    if not counted_in_guard:
        return 0.0

    from saas.growth_mandate import COST_PER_ACQUISITION

    return COST_PER_ACQUISITION.get(segment, 150.0)


def book_acquisition_spend(
    *,
    billing_account: str,
    event_date: str,
    amount_gbp: float,
    won: bool,
    segment: str,
) -> dict[str, Any]:
    """The supplier books what the attempt cost it — win or lose."""
    from saas.ledger import make_acquisition_spend_event

    return make_acquisition_spend_event(billing_account, event_date, amount_gbp, won, segment)


def book_acquisition_gate(
    *,
    billing_account: str,
    event_date: str,
    segment: str,
    gate_reason: str | None,
) -> dict[str, Any]:
    """The supplier records that it declined to attempt, and why.

    A zero-amount row rather than silence, and the distinction matters: a
    suppressed acquisition that books nothing is indistinguishable in the ledger
    from a period with no losses. The shape is pinned by
    `tests/company/interfaces/test_growth_desk_seam.py` against the literal dict
    `run_phase2b` built inline before this door existed — including the absence
    of a `transaction_id`, which the spend and retention rows both carry and
    this one has never had.
    """
    return {
        "event_type": "acquisition_gate_event",
        "timestamp": event_date,
        "billing_account": billing_account,
        "segment": segment,
        "amount_gbp": 0.0,
        "acquisition_won": False,
        "gate_reason": gate_reason,
    }


def book_retention_cost(
    *,
    billing_account: str,
    event_date: str,
    cost_gbp: float,
    company_churn_estimate: float,
) -> dict[str, Any]:
    """The supplier books the discount it gave away to keep a customer.

    `company_churn_estimate` is the supplier's OWN belief at the moment of the
    offer, carried onto the row so the belief that justified the spend can later
    be scored against what actually happened. It is not, and must never be, the
    world's churn draw.
    """
    from saas.ledger import make_retention_cost_event

    return make_retention_cost_event(
        billing_account, event_date, cost_gbp, company_churn_estimate
    )


@dataclass(frozen=True)
class GrowthCampaignPlan:
    """The supplier's answer to "how many homes can we go and quote this year?".

    `wins_capital_allows` and `wins_rate_allows` are BOTH reported, and keeping them apart
    is the point: for the published company they differ by two orders of magnitude, and one
    number would hide that the balance sheet is not what limits this book.
    """

    quotes: int
    budget_gbp: float
    wins_capital_allows: int
    wins_rate_allows: int
    binding: str
    headroom_gbp: float
    #: What the supplier assumed its conversion was when it started, what its own quote book has
    #: since told it (None until it has issued enough quotes to have a rate), and which of the two
    #: this year's plan was actually built on. Reported so the growth curve can be read as a
    #: belief being corrected rather than a number that moved.
    believed_win_rate: float | None = None
    realised_win_rate: float | None = None
    planning_on: str = "belief"


def plan_growth_campaign_year(
    *,
    net_assets_gbp: float,
    accounts_held: int,
    quotes_issued_to_date: int = 0,
    wins_to_date: int = 0,
) -> GrowthCampaignPlan:
    """Ask the supplier how large an acquisition campaign it will run this year.

    THE SEAM, AND WHY THIS FUNCTION EXISTS RATHER THAN A DIRECT IMPORT (2026-08-24, atom
    PB3). `simulation/live_population.py` assembles the run's book and needs the supplier's
    quote budget to do it. The obvious move -- `from saas.growth_mandate import
    growth_quote_budget` inside the seam module -- was written, and
    `tests/architecture/test_epistemic_wall_ratchet.py::test_no_new_sim_reads_company` caught
    it as a new SIM->company crossing. It was right to: the ratchet's own message offers two
    answers, allowlist it or route it through the seam, and an allowlist entry for a crossing
    that has a perfectly good seam sitting next to it is how a wall becomes a formality.

    WHAT CROSSES, AND WHAT DOES NOT. Two plain scalars go in -- what the supplier holds and
    how many accounts it has, both of which the world already knows because it is the world
    that settles them. A decision comes back. Nothing here exposes the MCR constant, the
    capital share, the growth-rate cap, or the per-segment cost table, and there is
    deliberately no parameter through which a caller could reach one; the same rule
    `decide_acquisition` above is built on.

    WHY THIS DOES NOT CONSULT `MANDATE`, which looks like an omission and is not. Module-level
    `MANDATE` is "flat" and governs the REPLACEMENT path -- whether the supplier goes to market
    when an account churns (`mandate_permits_replacement`). Whether this world contains a
    supplier that runs acquisition campaigns at all is a different question and a CURRICULUM
    one: it is decided in `docs/design/curriculum/book_growth_activation.json`, default OFF,
    on exactly the terms `SE_DRAW_POPULATION` already sets, and it is the director's under
    R13. So the caller has already established that a campaign is happening before it gets
    here; what it is asking is how big a one this balance sheet supports. Answering "none,
    because MANDATE says flat" would let a company constant silently veto a curriculum act,
    and the two would then disagree with no way to tell which was meant.
    """
    from saas.growth_mandate import growth_quote_budget

    # The two counts are the company's OWN books -- quotes it issued, accounts it won -- so they
    # travel INWARD across this seam exactly as `net_assets_gbp` and `accounts_held` do. Nothing
    # about who won, or why, or which homes were on offer comes back the other way; the world
    # still decides every outcome, and the company still only ever learns the totals it booked.
    plan = growth_quote_budget(
        "grow", net_assets_gbp, accounts_held,
        quotes_issued_to_date=quotes_issued_to_date, wins_to_date=wins_to_date,
    )
    return GrowthCampaignPlan(
        quotes=plan["quotes"],
        budget_gbp=plan["budget_gbp"],
        wins_capital_allows=plan["wins_capital_allows"],
        wins_rate_allows=plan.get("wins_rate_allows", 0),
        binding=plan["binding"],
        headroom_gbp=plan["headroom_gbp"],
        believed_win_rate=plan.get("believed_win_rate"),
        realised_win_rate=plan.get("realised_win_rate"),
        planning_on=plan.get("planning_on", "belief"),
    )


def quote_cost_gbp(*, segment: str) -> float:
    """What issuing one quote costs the supplier. A scalar, not the table.

    `plan_growth_campaign_year` returns a whole-campaign budget; the campaign also has to
    bill each quote as it is issued, won or lost. Handing back one number per segment keeps
    `COST_PER_ACQUISITION` itself on the company side, which is the same trade
    `run_acquisition_funnel` made when it stopped importing that table and took the cost as
    an argument instead (KNIFE pass 3, `B6_cpa_is_company_accounting`).
    """
    from saas.growth_mandate import COST_PER_ACQUISITION

    return COST_PER_ACQUISITION.get(segment, COST_PER_ACQUISITION["resi"])
