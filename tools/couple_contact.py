"""COUPLED-TRIAD measurement: the CONTACTING WORLD <-> the supplier's contact model.

This is HARNESS code. Like the other ``tools/couple_*`` runners it sits OUTSIDE
the epistemic wall by design and is the only layer permitted to hold the world's
answer (``simulation.contact_propensity.contact_propensity``) and the company's
belief (``saas.contact_model.contact_probability``) side by side to score the
GAP (``docs/design/COUPLED_TRIAD_DESIGN.md`` 1.3). It lives in ``tools/`` so it
is not scanned by the epistemic verifier and may legitimately import both sides.

WHY THIS PAIR EXISTS. Until 2026-08-13 there was nothing to measure: the world
drew its actual contact events off the company's estimate, so belief and truth
were THE SAME NUMBER and this gap was identically zero BY CONSTRUCTION -- the
shape the design names, *a gap of 0 is not always a leak, but a gap that CANNOT
be non-zero is*. The cut recorded in ``simulation/contact_propensity.py`` gives
the world its own response function, keyed on the household engagement archetype
the company structurally cannot read. This runner is what turns that into a
score.

WHAT IS AND IS NOT CLAIMED HERE. ``main()`` prints the measurement as JSON and,
under the opt-in ``--write-ledger`` flag every sibling ``couple_*`` runner
carries, merges one row into ``docs/observability/coupled_gap_ledger.json``.

The flag is the whole of the wiring, and that is deliberate: NOTHING schedules
this runner, so no publish path changes and no door starts rendering a new
figure. Reading the ledger into the digest and the Proof door remains a separate
step. The write itself is NOT optional though, and the first version of this file
was wrong to defer it -- ``background.gap_ledger_reconciler`` takes its producer
population from the ``tools/couple_*.py`` GLOB, so a family member that cannot
write is not a deferral, it is a member the reconciler can never attribute a
stale row to. That control (``test_discovery_reads_SOURCE_so_the_family_cannot_
be_escaped_by_not_editing_a_list``) exists precisely so membership cannot be
declined by omission, and it was red at HEAD from the commit that added this file
until the flag below landed.

READING THE HEADLINE. ``mean_signed_error`` is the company's belief MINUS the
world's truth, averaged over bills: positive means the supplier over-estimates
how often it will be contacted. ``mean_absolute_error`` is the size of the
disagreement regardless of direction. Both are diagnostics, never targets (R12)
-- a gap that closes because someone tuned a constant toward the other side is
the coupling coming back, not an improvement.
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from datetime import datetime, timezone
from typing import Iterable, Mapping, Sequence

from background.gap_metric import GapResult, prediction_gap, write_gap_entry
from saas.contact_model import contact_probability as company_belief
from simulation.contact_propensity import contact_propensity as world_truth
from simulation.household_segments import engagement_level_for_customer

# The world side has no maturity-map atom of its own -- the response function
# landed inside `simulation/contact_propensity.py` rather than as a W-atom -- so
# the pair is keyed by a descriptive WORLD_ id, the precedent
# `WORLD_recontracting_relationship_start` already set in this ledger.
WORLD_ATOM_ID = "WORLD_contact_propensity_response"
TWIN_ATOM_ID = "C_contact_model"


def _pairs(bills: Iterable[Mapping]) -> list[tuple[str, float, float]]:
    """(customer_id, belief, truth) per bill, in bills order."""
    rows: list[tuple[str, float, float]] = []
    for bill in bills:
        clarity = bill["clarity_score"]
        shock = bill.get("bill_shock_pct")
        rows.append((
            bill["customer_id"],
            company_belief(clarity, shock),
            world_truth(bill["customer_id"], clarity, shock),
        ))
    return rows


def _summarise(errors: Sequence[float]) -> dict:
    if not errors:
        return {"n": 0}
    return {
        "n": len(errors),
        "mean_signed_error": statistics.fmean(errors),
        "mean_absolute_error": statistics.fmean(abs(e) for e in errors),
        "max_absolute_error": max(abs(e) for e in errors),
    }


def measure(bills: Sequence[Mapping]) -> dict:
    """Score the company's contact belief against the world's contact truth.

    Broken out BY ENGAGEMENT ARCHETYPE as well as in aggregate, because the
    archetype is the dimension the company cannot see -- so that is where a real
    supplier's model would be systematically wrong, and an aggregate alone would
    average the two directions against each other and report a smaller gap than
    the company is actually running (the `a headline that changes sign with the
    population` shape).
    """
    rows = _pairs(bills)
    errors = [belief - truth for _, belief, truth in rows]

    by_archetype: dict[str, list[float]] = {}
    for (customer_id, belief, truth), error in zip(rows, errors):
        level = engagement_level_for_customer(customer_id).value
        by_archetype.setdefault(level, []).append(error)

    return {
        "pair": "contact_propensity_world <-> saas.contact_model",
        "aggregate": _summarise(errors),
        "by_engagement_archetype": {
            level: _summarise(values) for level, values in sorted(by_archetype.items())
        },
    }


def gap_result(bills: Sequence[Mapping]) -> GapResult:
    """The ledger-shaped score for this pair.

    ``prediction_gap`` (formula f) is the right family member because both sides
    are CONTINUOUS per-bill probabilities, and it normalises to a no-skill
    baseline -- predict the mean contact rate every time. That baseline is what
    makes the number readable: gap 1.0 says the supplier's model is worth nothing
    over guessing the average, and gap > 1 says it is actively worse than blind.
    A raw mean absolute error could not say either.

    The headline deliberately scores the AGGREGATE while `measure()` keeps the
    per-archetype split beside it. Neither is redundant: the ledger reader takes
    one float per pair, and an aggregate that averaged the archetypes' opposing
    signs would be the `headline that changes sign with the population` shape --
    so the components below carry the worst archetype, which is the number that
    would move first if the company's belief drifted for one group only.
    """
    rows = _pairs(bills)
    truth = [truth_p for _, _, truth_p in rows]
    belief = [belief_p for _, belief_p, _ in rows]
    result = prediction_gap(truth, belief)

    per_archetype = measure(bills)["by_engagement_archetype"]
    worst = max(
        per_archetype.items(),
        key=lambda kv: abs(kv[1].get("mean_signed_error", 0.0)),
        default=(None, {}),
    )
    result.components.update({
        "worst_archetype": worst[0],
        "worst_archetype_mean_signed_error": worst[1].get("mean_signed_error"),
        "n_archetypes": len(per_archetype),
    })
    result.note = (
        "Supplier's contact-probability belief (saas.contact_model) vs the world's "
        "own response function (simulation.contact_propensity), which is keyed on "
        "the household engagement archetype the company structurally cannot read. "
        "Truth is therefore structurally different from belief, not merely "
        "numerically different: this gap cannot return to zero by construction "
        "even if every constant were copied across, which is the property the "
        "pair was built to have. Diagnostic, never a target (R12)."
    )
    return result


def _git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "bills_json",
        help="path to a JSON file holding a list of bills "
             "(saas.bill_generator.generate_bill() output)",
    )
    parser.add_argument(
        "--write-ledger", action="store_true",
        help="persist the measured gap into coupled_gap_ledger.json",
    )
    args = parser.parse_args()
    with open(args.bills_json) as handle:
        bills = json.load(handle)
    print(json.dumps(measure(bills), indent=2, sort_keys=True))

    if args.write_ledger:
        result = gap_result(bills)
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, result,
            measured_at=datetime.now(timezone.utc).isoformat(),
            run_git_commit=_git_head(),
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
