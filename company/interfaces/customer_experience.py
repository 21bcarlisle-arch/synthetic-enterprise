"""Seam: the world reports what happened to a customer; the company keeps the book.

KNIFE pass 3, `A_composition_lift` step 21, 2026-08-13, disposition register
§3p. Before this, `simulation/run_phase2b.py::main()` constructed four of the
company's CRM books itself — `CustomerSatisfactionAccumulator`, `NPSTracker`,
`ComplaintBook`, `PaymentBehaviourAnalytics` — and made the company's
bookkeeping decisions on its behalf at nine call sites inside the renewal loop.
Four of that module's wall crossings for one process.

Now the world hands over four observations it genuinely owns — a term boundary
reached with or without a bill shock, an answered survey, a customer contact
and its resolution, a payment outcome — and reads back the company's own
satisfaction score, payment behaviour score, annual NPS/complaint summaries and
per-customer experience record. Every delta, threshold, decay rate, complaint
category and instrument-routing rule is behind this door.

THE READ DIRECTION IS WHY THIS IS A CUT AND NOT A FILE MOVE — the same test
§3f applied to bill assembly, §3i to the month-end close, §3l to the statutory
return and §3o to the churn desk. `company/crm/customer_experience_desk.py`
imports nothing from `simulation/` or `sim/`.

AND THE CHECK THIS STEP OWED, from §3o's finding that world physics keeps
ending up in `company/crm/` because that is where the CRM vocabulary lives:
all four books were re-read for a crossing in the OTHER direction before the
door was drawn, and none of them holds any. Every input they take is an
outcome the supplier observes on its own systems, every constant in them is a
supplier's own model parameter, and none of them rolls a die or caps anything
the world does. Whether a customer answers a survey, whether they get in touch,
and whether a payment actually lands are all decided in `simulation/`
(`feedback_survey.py`, `live_payment_triad.py`) and stay there. Stated because
§3o predicted the opposite result for some remaining group and the prediction
has to be checked, not assumed either way.

WHAT THIS DOES NOT DO. `run_phase2b` keeps its other crossings — the
commercial CRM pair (`customer_profitability`, `tpi_book`), the trading desk,
the pricing/regulatory group and the `saas.*` set — and the two indirect edges
are untouched. This door carries the company's view of its own customers'
experience and nothing else.
"""

from __future__ import annotations

from company.crm.customer_experience_desk import (
    CustomerContact,
    CustomerExperienceDesk,
    PaymentOutcome,
    RenewalReached,
    SurveyInstrument,
    SurveyResponse,
)

__all__ = [
    "CustomerContact",
    "CustomerExperienceDesk",
    "PaymentOutcome",
    "RenewalReached",
    "SurveyInstrument",
    "SurveyResponse",
]
