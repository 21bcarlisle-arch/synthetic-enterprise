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
    "offer_framing_for",
    "replacement_cost_avoided_gbp",
    "retention_discount_for_risk",
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


def replacement_cost_avoided_gbp(*, segment: str) -> float:
    """What retaining this customer saves the supplier in replacement spend.

    THE `counted_in_guard` PARAMETER IS GONE — KNIFE3 step 39 (§3ah), and this
    reverses a choice this docstring used to record in its own words. It said
    the switch was "passed as a plain bool so the world never has to hold a
    policy object to ask the question". That was true and it was the best
    available shape while `run_phase2b.main()` still took a `policy` argument:
    the world already held the object, so handing over a bool was strictly
    better than handing over the object.

    Step 39 removed the argument, so the premise is gone. The world holds no
    policy at all now and cannot read the switch to pass it. The guard term is
    resolved HERE, from the run's active policy, on the company side of the
    seam — the same device `collections_tone_for` uses, for the same reason.
    A bool the world reads off a company object and hands straight back to a
    company door was never the world's; it was pass-through, and this is where
    it always belonged.

    The frozen NAIVE arm sets the switch False — the pre-Phase-15b margin-only
    guard — and this function then returns 0.0 rather than the segment's cost,
    which is the whole of that policy's effect. That is unchanged; only the
    channel it arrives by has moved.
    """
    from company.policy.decision_policy import active_policy

    if not active_policy().include_acq_cost_saved_in_guard:
        return 0.0

    from saas.growth_mandate import COST_PER_ACQUISITION

    return COST_PER_ACQUISITION.get(segment, 150.0)


def retention_discount_for_risk(company_est: float) -> float:
    """How big a discount the supplier offers a customer at this churn estimate.

    KNIFE3 step 39 (§3ah). `run_phase2b` used to call
    `policy.retention_discount_for_risk(company_est)` off a `DecisionPolicy` it
    held as a parameter. Sizing a retention discount is a commercial judgement
    the supplier makes and is allowed to get wrong — it is not physics, and the
    world's only legitimate interest is the NUMBER, not the tier table that
    produced it.

    Resolved against the run's active policy, so the frozen baseline's naive arm
    gets its flat 5% and the live arm gets its tiers, without either arm's
    identity travelling through the world.
    """
    from company.policy.decision_policy import active_policy

    return active_policy().retention_discount_for_risk(company_est)


def offer_framing_for(customer_id: str, event_date: str) -> str:
    """The comms framing the supplier chose for one retention offer —
    "loss_framed" / "gain_framed".

    KNIFE3 step 39 (§3ah). The exact sibling of
    `company/interfaces/collections_communication.py::collections_tone_for`,
    which §3aa named as the live precedent for this half: `framing_type_for` is
    `tone_for` with the retention channel substituted for the dunning one. The
    world may learn the FRAMING of the offer that was made — a real customer
    reads the letter, and their loss-aversion response to it is world physics —
    but never the `DecisionPolicy` that chose it, its `framing_mode`, or its
    cohort split.

    THE SAME HONEST LIMIT AS ITS SIBLING: this is a PULL, and B5's design asks
    for a PUSH — the framing stamped onto a retention offer the company EMITS,
    with the world reacting to what it receives. That is not built here, and the
    reason is the one `collections_communication.py` records: the retention
    offer is not yet a company-emitted event. It is assembled inline in
    `run_phase2b`'s term loop, which is the composition this design has been
    unwinding for thirty-nine steps. Stamping it at emission needs an emitter
    that does not exist. So the push stays owed and is recorded as owed, not
    simulated — building the shape of a push over a value the world pulled and
    reads back would be strictly worse than an honest pull through a named door.

    Never reads `simulation/nudge_physics.py`'s hidden loss-aversion
    susceptibility. That is the customer's private responsiveness; the company
    discovers it only statistically, via `company/analytics/nudge_discovery.py`.
    """
    from company.policy.decision_policy import active_policy, framing_type_for

    return framing_type_for(active_policy(), customer_id, event_date)


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
