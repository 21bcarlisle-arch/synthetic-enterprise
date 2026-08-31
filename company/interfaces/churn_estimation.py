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
crosses is an `SvtSegmentObservation` of things the company reads off its own
systems: when the account last left a fixed deal, how long this cap period ran,
and — from v2 — what its own collections record on this account looks like.

THE THIRD FIELD IS THE SECOND BELIEF THROUGH THIS DOOR AND IT IS ARGUED HERE
RATHER THAN ASSUMED (2026-08-31). A door that grows a hole is how a wall fails,
so the crossing gets its own paragraph instead of a shrug.

WHAT IS BEING ASKED FOR. v1 carried two observables and both were CALENDAR, so
it could only order the billing calendar and the instrument caught it doing
exactly that — 0.4691 per exposure-day, inside its own null, against a ceiling
of 0.6091 that clears. The repair needs an observable that VARIES ACROSS
HOUSEHOLDS AT THE SAME INSTANT, because a belief every household shares cannot
select a household. The world's own SVT hazard has exactly one such term:
`action_propensity`, built from income stress and housing tenure.

WHY THAT TERM MAY NOT CROSS, IN ITS OWN WORDS. Income stress is SIM ground
truth and housing tenure is a segment label; the D-SEGMENT ruling
(`docs/design/SEGMENTATION_RECONCILIATION_FRAME.md` §0) says no segment label,
attitude or sensitivity ever crosses this wall directly, and "directly" has
never been read here as leaving a proxy-with-a-different-name open. Handing the
company a renamed `sim_action_propensity` would let it score 0.6091 and prove
nothing whatever, because the thesis under test is that the advantage comes from
INFERENCE and never from ACCESS. A belief fed the answer cannot test that
sentence; it can only flatter it.

WHY `payment_behaviour` IS NOT THAT. It is the company's own record of its own
collections on its own account — did the money arrive, was it late, was the
Direct Debit returned. A real GB supplier holds precisely this and holds it
without asking anyone: it is the output of its billing and its bank feed, and
it already crosses this wall through an established door for the fixed-term
belief (`CustomerExperienceDesk.observe_payment`, feeding
`RenewalObservation.behaviour_score` above). No new channel is opened here; the
SVT route is joined to a channel that was already legal, already used, and
already point-in-time — the desk is fed inside the same term loop that makes
this decision, so the score reflects payments observed BEFORE this cap period
and never after it.

THE PART THAT IS THE COMPANY'S WORK, NOT THE WALL'S GIFT. Payment behaviour and
propensity to act are related in this world because both descend from one
hardship substrate — `simulation.arrears_engine.payment_outcome` takes income
stress as an input, and so does `stress_switching_multiplier`. That common cause
is a FACT ABOUT THE WORLD, and the company is not told it. It observes only
whether the money arrived and must infer the rest from its own book. That is the
distinction the whole project turns on, and it is the reason this field is a
legal crossing where a renamed propensity would not be: one is an observable the
company must reason FROM, the other is the conclusion handed over.

WHAT STILL DOES NOT CROSS, AND THE LIST IS UNCHANGED. Income stress, housing
tenure, segment label, green stance, `sim_action_propensity`, and any
probability the world computed. If the belief cannot reach the ceiling on the
observables above, that gap is the finding — see the belief's own docstring for
why an honest shortfall is worth more here than a closed one.
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
