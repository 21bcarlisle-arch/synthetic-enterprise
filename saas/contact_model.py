"""Contact and complaints model — Phase 4c-6 (physical simulation layer,
final sub-phase).

Per the Key Domain Insight (CLAUDE.md), a confusing bill (low
`clarity_score` from `saas/bill_generator.py`) or a bill-shock month
(`bill_shock_pct`) drives a customer to contact the supplier. `COMPLAINT_ESCALATION_DAYS`
(14, per the Phase 4c sub-phase spec) is how long a contact can go unresolved
before escalating to a complaint — modelled here as a fixed escalation rate
(`UNRESOLVED_AFTER_14_DAYS_RATE`) applied to the contact probability, since
there's no per-contact resolution-date data to track an actual 14-day clock
yet. The resulting complaint rate feeds a portfolio-level service quality
score.

All constants below are seed estimates pending the
`customer-archetype-data-enrichment` background task — see
`saas/property_model.py`'s module docstring for the same caveat.

This module is pure: plain dicts/lists in, plain dicts out. No imports from
`sim/`.
"""

import statistics

# contact_probability = BASE + (1 - clarity_score) * LOW_CLARITY_CONTACT_PENALTY
#                              + min(bill_shock_pct, 1.0) * BILL_SHOCK_CONTACT_PENALTY
BASE_CONTACT_PROBABILITY = 0.05
LOW_CLARITY_CONTACT_PENALTY = 0.3
BILL_SHOCK_CONTACT_PENALTY = 0.5

COMPLAINT_ESCALATION_DAYS = 14
# Fraction of contacts still unresolved after COMPLAINT_ESCALATION_DAYS,
# escalating to a formal complaint.
UNRESOLVED_AFTER_14_DAYS_RATE = 0.25

# service_quality_score = 1.0 - avg_complaint_probability * SERVICE_QUALITY_PENALTY_FACTOR
SERVICE_QUALITY_PENALTY_FACTOR = 2.0
MIN_SERVICE_QUALITY_SCORE = 0.0
MAX_SERVICE_QUALITY_SCORE = 1.0


def contact_probability(clarity_score: float, bill_shock_pct: float | None = None) -> float:
    """Probability a customer contacts the supplier about this bill.

    clarity_score: from `saas.bill_generator.generate_bill()`, in [0, 1] —
        lower clarity raises contact probability.
    bill_shock_pct: from `saas.bill_generator.generate_bill()`, or None — a
        large month-on-month change further raises contact probability,
        capped at a 100% change for this purpose.

    Result is clamped to [0, 1].
    """
    probability = BASE_CONTACT_PROBABILITY + (1.0 - clarity_score) * LOW_CLARITY_CONTACT_PENALTY
    if bill_shock_pct is not None:
        probability += min(bill_shock_pct, 1.0) * BILL_SHOCK_CONTACT_PENALTY
    return max(0.0, min(1.0, probability))


def complaint_probability(contact_probability_value: float) -> float:
    """Probability a bill's contact escalates to a complaint after
    COMPLAINT_ESCALATION_DAYS unresolved days."""
    return contact_probability_value * UNRESOLVED_AFTER_14_DAYS_RATE


def service_quality_score(complaint_rate: float) -> float:
    """Service quality score in [0, 1], reduced from 1.0 by
    `complaint_rate` scaled by SERVICE_QUALITY_PENALTY_FACTOR."""
    score = MAX_SERVICE_QUALITY_SCORE - complaint_rate * SERVICE_QUALITY_PENALTY_FACTOR
    return max(MIN_SERVICE_QUALITY_SCORE, min(MAX_SERVICE_QUALITY_SCORE, score))


def build_contact_model(bills: list[dict]) -> dict:
    """For each bill (`saas.bill_generator.generate_bill()` output), compute
    contact_probability and complaint_probability from its clarity_score and
    bill_shock_pct.

    Returns:
      {
        "by_customer": {
          "<customer_id>": [
            {customer_id, period_end, contact_probability, complaint_probability},
            ...  # in `bills` order
          ],
        },
        "portfolio": {avg_complaint_probability, service_quality_score},
      }

    An empty `bills` list returns empty `by_customer`, zero
    avg_complaint_probability, and a service_quality_score of 1.0.
    """
    by_customer: dict[str, list[dict]] = {}
    complaint_probabilities: list[float] = []

    for bill in bills:
        customer_id = bill["customer_id"]
        cp = contact_probability(bill["clarity_score"], bill.get("bill_shock_pct"))
        comp = complaint_probability(cp)
        complaint_probabilities.append(comp)
        by_customer.setdefault(customer_id, []).append({
            "customer_id": customer_id,
            "period_end": bill["period_end"],
            "contact_probability": cp,
            "complaint_probability": comp,
        })

    avg_complaint_probability = statistics.mean(complaint_probabilities) if complaint_probabilities else 0.0

    return {
        "by_customer": by_customer,
        "portfolio": {
            "avg_complaint_probability": avg_complaint_probability,
            "service_quality_score": service_quality_score(avg_complaint_probability),
        },
    }
