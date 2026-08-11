"""Seam: the world hands over the bills and takes back what the supplier expects of them.

KNIFE pass 3, `A_composition_lift` step 16, 2026-08-11, disposition register
§3k. Before this, `simulation/run_phase4c_on_phase2b.py::main()` composed the
supplier's billing-experience layer itself — the credit-risk segmentation and
bad-debt provisioning behind `payment_behaviour`, and the contact/complaint
estimates behind `contact_model`. That was two of that module's three remaining
wall crossings (`saas.payment_behaviour`, `saas.contact_model`).

Now the world hands over what it owns — the bills, as DATA — and receives a
`BillingExperienceView`. How this supplier segments its customers by credit
risk, what it provisions against them, and how it models a confusing bill
turning into a complaint are unreachable from the SIM; what crosses is this one
door.

WHAT THIS DOOR IS NOT. It is not a claim that the direction is clean in the
other sense: the world's own contact-centre generator consumes the returned
`contact_probability` as its draw rate, so the supplier's estimate constitutes
the world's outcome. That inversion is real, pre-dates this cut, and is NOT
repaired by it — `company/analytics/billing_experience_view.py`'s docstring
records it in full and §3k files it. A reader must not take this seam as
evidence that question was settled.

WHAT IS LEFT. `company.billing.dd_review_runner` remains a live crossing of the
run module — §3h ruled it a ROUTING residual (the world threads the desk's own
register into the report) rather than a decision the world takes. It is the last
one on that module, and it is the one this design was never going to cut.
"""

from __future__ import annotations

from company.analytics.billing_experience_view import (
    BillingExperienceView,
    build_billing_experience_view,
)

__all__ = ["BillingExperienceView", "build_billing_experience_view"]
