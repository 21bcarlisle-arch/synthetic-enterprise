"""The WORLD's ceiling on churn probability — SIM physics, not a company belief.

WHY THIS FILE EXISTS (KNIFE pass 3, `B3_world_needs_its_own_cap_physics`
applied a second time — see `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`
§3g).

`simulation/satisfaction_churn.py` clamped the world's GROUND-TRUTH churn
probability at `saas.churn_model.MAX_BILL_SHOCK_CHURN_PROBABILITY` — the company's own
constant. That is the B2 inversion in miniature: whatever the company believed
the ceiling was, that is what the world enforced, so the belief could not be
wrong about it. The COUPLED TRIAD scores the gap between what the company
believes and what the world does; a quantity pinned to the company's opinion by
construction contributes a guaranteed zero to that score.

The world's ceiling now lives here, on the world's side of the wall, and the
company's `MAX_BILL_SHOCK_CHURN_PROBABILITY` stays exactly where it is as the company's
ESTIMATE of it. Today the two numbers agree (both 0.95) and no simulated
outcome moves; what changed is who depends on whom.

WHAT IS DELIBERATELY NOT HERE: a test asserting the two constants are equal.
That would restore in the suite precisely the coupling this cut removes from
the code — the refusal recorded for `B3` (the cap schedule) and `B7` (the hedge
floor), for the same reason each time. The readings MAY drift; drift is a
finding for the harness to report, never something the suite pins shut (R12).

WHY ONE HOME RATHER THAN A CONSTANT PER MODULE. Before this cut the world
expressed its own ceiling three different ways: borrowed from the company
(`satisfaction_churn`), a private module constant (`switching_propensity.
_MAX_CHURN_PROBABILITY`), and a bare `0.95` literal inside a `min()`
(`customer_events`). Three copies of one world fact is `one name, two numbers`
waiting to happen — the fidelity defect the register names — so the cut that
removes the company's copy folds the other two in as well. Only the first of
those three is a wall crossing; the other two are recorded as housekeeping that
came with it, not as edges cut.

THE VALUE ITSELF. 0.95 is the value all three copies already carried, kept
unchanged so this cut moves no number. It is a modelling choice, not a sourced
external figure: it says that no combination of dissatisfaction, income stress
and market conditions makes a customer's annual churn a certainty — there is
always a residual 5% who stay through anything (inertia, no viable alternative
supplier, a tariff nobody can beat). It belongs to the world because whether a
customer actually leaves is a fact about the customer, not about the supplier's
model of the customer.
"""
from __future__ import annotations

WORLD_MAX_CHURN_PROBABILITY = 0.95
