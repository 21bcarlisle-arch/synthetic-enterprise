"""Seam: the world hands over one renewal's observables and takes back a belief.

KNIFE pass 3, `A_composition_lift` step 20, 2026-08-12, disposition register
§3o. Before this, `simulation/run_phase2b.py::main()` picked between the
company's two churn estimators itself, knew the industry base rate, knew the
crisis-hangover window and ran the company's own calibration report — three of
that module's wall crossings (`company.crm.churn_model`,
`company.crm.enriched_churn_estimate`,
`company.analytics.churn_accuracy_report`).

Now the world hands over what it owns — the rates it set, the tenure it can
read, the signals the company itself accumulated — as one `RenewalObservation`,
and receives a probability. Which estimator runs, the industry base rate, the
market-conditions multiplier and the hangover window are unreachable from the
SIM; what crosses is this one door.

THE READ DIRECTION IS WHY THIS IS A CUT AND NOT A FILE MOVE — the same test §3f
applied to bill assembly, §3i to the month-end close and §3l to the statutory
return. `company/crm/churn_desk.py` imports nothing from `simulation/` or
`sim/`.

AND THE HALF THAT MAKES IT A CUT RATHER THAN A RE-EXPORT: two things the world
was importing from `company.crm.churn_model` did NOT come through this door,
because they were never the company's. `is_active_renewal` rolls the dice on
whether a household actually shops, and `PASSIVE_CHURN_CAP` — labelled `# SIM
ground-truth cap` in the company module's own source — clamps what that
household's REAL churn probability may reach. A door carrying those would have
let the company's belief keep constituting the fact it is a belief about, which
is B2's inversion and §3g's finding. They are now the world's, in
`simulation/renewal_engagement.py`, and the company keeps its own reading of the
cap for its own estimate. Nothing pins the two equal.

WHAT THIS DOES NOT DO. `run_phase2b` keeps its other crossings — the rest of the
CRM builders, the trading desk, the pricing group and the `saas.*` set are
separate processes on separate inputs, and the two indirect edges are untouched.
This door carries the company's churn belief and nothing else. Stated rather
than left to be discovered from a count that stops at 3.
"""

from __future__ import annotations

from company.crm.churn_desk import (
    RenewalObservation,
    crisis_hangover_periods,
    estimate_churn_without_rate_history,
    estimate_renewal_churn,
    estimate_secondary_fuel_churn,
    score_churn_estimates,
)

__all__ = [
    "RenewalObservation",
    "crisis_hangover_periods",
    "estimate_churn_without_rate_history",
    "estimate_renewal_churn",
    "estimate_secondary_fuel_churn",
    "score_churn_estimates",
]
