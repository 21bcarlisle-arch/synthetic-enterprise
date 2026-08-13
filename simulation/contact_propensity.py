"""The WORLD's propensity for a customer to contact its supplier — SIM physics,
not a company belief.

WHY THIS FILE EXISTS (`WORKER_FINDING_THE_WORLDS_CONTACT_RATE_IS_THE_COMPANYS_
ESTIMATE_2026-08-11.md`, recorded as the leak KNIFE pass 3 step 16 did NOT
repair — `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3k).

`simulation/contact_centre.py::generate_contact_centre_log(bills, contact_model)`
drew the world's ACTUAL contact events off `saas.contact_model`'s
`contact_probability` — the SUPPLIER'S ESTIMATE, three hand-set constants the
supplier is free to revise. So the number the company would be measured against
was the number the company chose: revise `BASE_CONTACT_PROBABILITY` down and its
customers contact it less. There was no world-side contact physics for the
belief to be wrong ABOUT, and the COUPLED TRIAD's belief-vs-truth gap on this
quantity was therefore identically zero BY CONSTRUCTION — the shape the design
names: *a gap of 0 is not always a leak, but a gap that CANNOT be non-zero is.*

This is the third application of `B3_world_needs_its_own_cap_physics`, after
§3g (`simulation/churn_ceiling.py`, the world's churn ceiling) and §3e (`B7`,
the hedge floor). The repair direction is the established one: the world's
answer moves here, the company's estimate stays exactly where it is as its
ESTIMATE of it, and nothing pins the two together.

WHAT THE WORLD OWNS HERE, AND WHY IT IS THE WORLD'S
---------------------------------------------------
Whether a confused or shocked customer actually picks up the phone is a fact
about the CUSTOMER, not about the supplier's model of the customer — the same
argument §3g made for whether a customer actually leaves. So the response
function lives on this side of the wall, and it is keyed on something the
company structurally cannot read: the household's engagement archetype
(`simulation/household_segments.py`). An engaged household chases a bill it does
not understand; a disengaged one files it and says nothing. That archetype term
is what makes the truth STRUCTURALLY different from the belief rather than
merely numerically different — the company has no engagement archetype to
estimate with, so the gap can no longer be zero by construction even if every
constant below were copied across.

WHAT THE WORLD READS, AND WHAT REMAINS
--------------------------------------
`clarity_score` and `bill_shock_pct` are read off the BILL — the artefact the
customer physically received. Observing the document you were sent is what a
customer does, and `bills` already crossed to the world here. But it is worth
being exact about what is and is not repaired: `clarity_score` is computed by
`saas/bill_generator.py` and is closer to the company's measure of its own
document than to a property the household perceives directly. The world
measuring the document's complexity FOR ITSELF is a further deepening, NOT taken
here (`SELF_INTERRUPT_DISCIPLINE`); it is recorded as the residual on this cut.
What that residual is not is the defect being repaired: the defect was the
RESPONSE FUNCTION being the company's, and the response function is now here.

WHAT IS DELIBERATELY NOT HERE
-----------------------------
A test asserting these constants equal `saas.contact_model`'s. That would
restore in the suite exactly the coupling this cut removes from the code — the
refusal recorded at §3g and at B7, for the same reason each time. The readings
MAY drift; drift is a finding for the harness to REPORT, never something the
suite pins shut (R12). Independence is proven by mutation with a vacuity guard
(`tests/simulation/test_contact_propensity.py`).

THE VALUES THEMSELVES
---------------------
The base/confusion/shock terms carry the values the company's estimate already
carried (0.05 / 0.3 / 0.5), unchanged and deliberately so: this cut is about WHO
OWNS the function, and starting the world at the same reading keeps the change
attributable. They are a modelling CHOICE, not sourced external figures, and
they are the world's to revise on fidelity grounds alone from here (R13 —
BASELINE changes are decided blind to company P&L).

The engagement multipliers ARE new physics and do move simulated outcomes.
Population-weighted they come to 0.45*1.25 + 0.35*1.00 + 0.20*0.45 = 1.0025 —
within a quarter of a percent of neutral, so the portfolio-level contact rate is
substantially unmoved while the WITHIN-BOOK shape changes. That near-neutrality
is a consequence of picking round numbers with the right ordering, NOT a target
that was solved for: tuning the multipliers to land the aggregate exactly on its
prior value would be goal-seeking an output (R12), and the aggregate is a
diagnostic here, not something to preserve.
"""
from __future__ import annotations

import math

from simulation.household_segments import (
    EngagementLevel,
    engagement_level_for_customer,
)

# contact_propensity = (BASE
#                       + (1 - clarity_score) * CONFUSION_SENSITIVITY
#                       + min(bill_shock_pct, 1.0) * SHOCK_SENSITIVITY)
#                      * the household's engagement multiplier
WORLD_BASE_CONTACT_PROPENSITY = 0.05
WORLD_CONFUSION_SENSITIVITY = 0.3
WORLD_SHOCK_SENSITIVITY = 0.5

# How much more (or less) likely a household of each engagement archetype is to
# actually make contact about a bill it finds confusing or shocking. An ACTIVE
# household is one that already shops around every renewal -- it engages with
# its supplier; a DISENGAGED one is defined by not doing that, and mostly
# absorbs the bill in silence. The company cannot read this dimension at all,
# which is the point (see the module docstring).
ENGAGEMENT_CONTACT_MULTIPLIER: dict[EngagementLevel, float] = {
    EngagementLevel.ACTIVE: 1.25,
    EngagementLevel.PASSIVE: 1.00,
    EngagementLevel.DISENGAGED: 0.45,
}

MIN_CONTACT_PROPENSITY = 0.0
MAX_CONTACT_PROPENSITY = 1.0


def _require_unit_interval(name: str, value: float) -> float:
    """Reject a missing/corrupt reading rather than defaulting it.

    R15 fail-open doctrine, and the precedent `household_segments.
    engagement_level_from_propensity` already sets: a NaN compares False against
    every boundary, so a clamp-and-continue here would silently turn a corrupt
    bill into a perfectly clear one and SUPPRESS contacts -- the failure
    direction that hides itself.
    """
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number, got {value!r}")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite, got {number!r}")
    if not (0.0 <= number <= 1.0):
        raise ValueError(f"{name} must be in [0, 1], got {number!r}")
    return number


def engagement_contact_multiplier(engagement_level: EngagementLevel) -> float:
    """The world's contact multiplier for an engagement archetype."""
    return ENGAGEMENT_CONTACT_MULTIPLIER[engagement_level]


def contact_propensity(
    customer_id: str,
    clarity_score: float,
    bill_shock_pct: float | None = None,
) -> float:
    """The WORLD's probability that this customer contacts the supplier about
    this bill.

    customer_id: resolves the household's engagement archetype -- the dimension
        the company cannot see.
    clarity_score: how legible the bill it received was, in [0, 1].
    bill_shock_pct: month-on-month change, or None where there is no prior bill
        to be shocked against. Counted at most once over (a 100% change).

    Result is clamped to [0, 1]. Note this is the WORLD's answer; the company's
    estimate of the same quantity is `saas.contact_model.contact_probability`
    and the two are free to disagree -- measuring that disagreement is
    `tools/couple_contact.py`'s job.
    """
    clarity = _require_unit_interval("clarity_score", clarity_score)

    propensity = (
        WORLD_BASE_CONTACT_PROPENSITY + (1.0 - clarity) * WORLD_CONFUSION_SENSITIVITY
    )
    if bill_shock_pct is not None:
        shock = float(bill_shock_pct)
        if not math.isfinite(shock) or shock < 0.0:
            raise ValueError(f"bill_shock_pct must be finite and >= 0, got {shock!r}")
        propensity += min(shock, 1.0) * WORLD_SHOCK_SENSITIVITY

    propensity *= engagement_contact_multiplier(
        engagement_level_for_customer(customer_id)
    )
    return max(MIN_CONTACT_PROPENSITY, min(MAX_CONTACT_PROPENSITY, propensity))


def contact_propensity_for_bill(bill: dict) -> float:
    """`contact_propensity` read straight off a bill dict (`saas.bill_generator.
    generate_bill()` output) -- the shape `generate_contact_centre_log` holds."""
    return contact_propensity(
        bill["customer_id"], bill["clarity_score"], bill.get("bill_shock_pct")
    )
