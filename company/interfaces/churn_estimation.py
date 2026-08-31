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

THE SECOND ROUTE CROSSES HERE TOO (2026-08-31). `estimate_svt_drift` is the
company's view of an account drifting off the standard variable product — 61% of
this book's departures, and a route it formed no belief about at all until now.
It goes through THIS door rather than a second one, because it is the same
question (will this account leave) asked at a different moment, and a second door
for the same question is how a wall acquires a hole nobody is watching. What
crosses is an `SvtSegmentObservation` of two things the company reads off its own
systems: when the account last left a fixed deal, and how long this cap period
ran. Nothing about income, tenure or segment crosses — see the belief's own
docstring for why that absence is the finding rather than a gap.
"""

from __future__ import annotations

from company.crm.churn_desk import (
    RenewalObservation,
    SvtSegmentObservation,
    active_pressure_ledger,
    crisis_hangover_periods,
    estimate_churn_without_rate_history,
    estimate_renewal_churn,
    estimate_secondary_fuel_churn,
    estimate_svt_drift,
    pressure_ledger_scope,
    score_churn_estimates,
)

__all__ = [
    "RenewalObservation",
    "SvtSegmentObservation",
    "estimate_svt_drift",
    "active_pressure_ledger",
    "pressure_ledger_scope",
    "crisis_hangover_periods",
    "estimate_churn_without_rate_history",
    "estimate_renewal_churn",
    "estimate_secondary_fuel_churn",
    "score_churn_estimates",
]

# THE SECOND HALF OF THE SAME DOOR, ADDED 2026-08-28. `estimate_renewal_churn` hands the company
# a belief; `active_pressure_ledger` is how the world hands back the one OUTCOME that belief is
# later graded and updated against -- that an account did not renew. Nothing about the rival
# crosses here, in either direction: what the world reports is a departure from THIS supplier's
# own book, which is the single competitive fact a real supplier observes without knowing any
# rival's price. The ledger it returns is company-owned state; the world may append a departure
# to it and can read nothing back out of it.
#
# It is exported through this seam rather than imported from `company.crm.competitive_pressure`
# directly, for the reason the door exists at all: `run_phase2b` should not grow a fourth
# crossing into the CRM package to book a fact it already holds.
