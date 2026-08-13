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

WHAT IS AND IS NOT CLAIMED HERE. This measures the gap on a supplied set of
bills; it does NOT write to ``docs/observability/coupled_gap_ledger.json`` and is
not yet wired into the digest or the Proof door. That wiring is a publish-path
change with its own gate consequences and is deliberately a separate step, named
rather than quietly skipped. ``main()`` prints the measurement as JSON.

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
from typing import Iterable, Mapping, Sequence

from saas.contact_model import contact_probability as company_belief
from simulation.contact_propensity import contact_propensity as world_truth
from simulation.household_segments import engagement_level_for_customer


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "bills_json",
        help="path to a JSON file holding a list of bills "
             "(saas.bill_generator.generate_bill() output)",
    )
    args = parser.parse_args()
    with open(args.bills_json) as handle:
        bills = json.load(handle)
    print(json.dumps(measure(bills), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
