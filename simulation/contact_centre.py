"""Contact-centre first-response time model (Phase 3 item 4, docs/design/
CORE_FIDELITY_PHASES.md: "No dedicated latency module exists -- distinct
from complaint *resolution* time [simulation/feedback_survey.py, real], the
*first-response* SLA is not [modelled]").

`simulation/contact_propensity.py` computes, per bill, the WORLD's probability
that a confusing/shocking bill drives a customer to contact the supplier -- but
that probability is not yet a discrete contact EVENT with its own timing. This
module is that event layer: given a contact occurs, it picks a real contact
channel (phone / webchat / email -- UK energy-sector contact mix skews heavily
to phone) and simulates how long the FIRST acknowledgement takes, distinct from
`feedback_survey.dispatch_complaint_and_resolution`'s full-resolution
timer.

⚠ THE TRIGGER USED TO BE THE COMPANY'S. Until 2026-08-13 this module drew its
events off `saas.contact_model`'s `contact_probability` -- the SUPPLIER'S
ESTIMATE -- so the contact rate the company was measured against was the one the
company chose (`WORKER_FINDING_THE_WORLDS_CONTACT_RATE_IS_THE_COMPANYS_ESTIMATE
_2026-08-11.md`, register §3k, the B2/B3 inversion). The trigger is now the
world's own propensity and this module no longer takes `contact_model` at all.
The company's estimate is untouched and stays its estimate; the gap between the
two is scored by `tools/couple_contact.py`.

⚠ Anchors provisional: channel-mix shares and the 24-business-hour written-
channel first-response target are seed estimates (industry customer-service
convention, not yet independently confirmed against a discovery-agent-
fetched Ofgem/Citizens Advice source) -- registered honestly as provisional
in docs/market_research/ASSUMPTIONS.md rather than presented as confirmed
(Anchored-noise law). Phone/webchat first-response is near-real-time by
channel nature and is not similarly provisional.

Deterministic dispatch: `random.Random(f"contact_{customer_id}_{period_end}")`,
matching simulation/feedback_survey.py's convention.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from simulation.contact_propensity import contact_propensity_for_bill

# Channel mix for a contact that occurs (UK energy-sector contact centres
# remain phone-heavy relative to general retail; provisional -- see module
# docstring).
CHANNEL_WEIGHTS = {"phone": 0.55, "email": 0.25, "webchat": 0.20}

# First-response delay distribution per channel, in HOURS. Phone/webchat are
# live-conversation channels -- a real "first response" is effectively
# immediate (a short hold/queue time). Email is asynchronous and dominates
# the unhappy-path tail.
_PHONE_QUEUE_MEAN_MINUTES = 6.0
_WEBCHAT_QUEUE_MEAN_MINUTES = 4.0
_EMAIL_RESPONSE_MEAN_HOURS = 14.0

# Provisional first-response SLA target for asynchronous (email) contact --
# industry customer-service convention (⚠ not yet discovery-agent-verified
# against a specific Ofgem complaint-handling-standards figure).
EMAIL_FIRST_RESPONSE_SLA_HOURS = 24.0


@dataclass(frozen=True)
class ContactEvent:
    customer_id: str
    period_end: str
    occurred: bool
    channel: Optional[str] = None
    first_response_hours: Optional[float] = None
    breached_sla: Optional[bool] = None


def simulate_contact(
    customer_id: str, period_end: str, contact_probability_value: float
) -> ContactEvent:
    """Roll whether a contact occurs this bill, and if so, its channel and
    first-response latency.

    `contact_probability_value` is the WORLD's propensity
    (`simulation.contact_propensity.contact_propensity`). This function is the
    event/timing layer and is deliberately agnostic about where the probability
    came from; `generate_contact_centre_log` below is what fixes it to the
    world's side of the wall.
    """
    rng = random.Random(f"contact_{customer_id}_{period_end}")
    if rng.random() >= contact_probability_value:
        return ContactEvent(customer_id, period_end, occurred=False)

    channel_roll = rng.random()
    cumulative = 0.0
    channel = "email"
    for candidate, weight in CHANNEL_WEIGHTS.items():
        cumulative += weight
        if channel_roll < cumulative:
            channel = candidate
            break

    if channel == "phone":
        hours = rng.expovariate(1.0 / _PHONE_QUEUE_MEAN_MINUTES) / 60.0
        breached = False  # live channel -- no async SLA to breach
    elif channel == "webchat":
        hours = rng.expovariate(1.0 / _WEBCHAT_QUEUE_MEAN_MINUTES) / 60.0
        breached = False
    else:
        hours = rng.expovariate(1.0 / _EMAIL_RESPONSE_MEAN_HOURS)
        breached = hours > EMAIL_FIRST_RESPONSE_SLA_HOURS

    return ContactEvent(
        customer_id, period_end, occurred=True,
        channel=channel, first_response_hours=round(hours, 2), breached_sla=breached,
    )


def generate_contact_centre_log(bills: list[dict]) -> list[dict]:
    """One contact-centre event per bill that generates a contact, triggered by
    the WORLD's own contact propensity.

    Takes `bills` -- the documents that were actually sent -- and nothing else.
    It deliberately no longer accepts `contact_model`: taking the supplier's
    estimate here is the defect this signature change repairs, and a parameter
    that still existed would be a parameter something could pass again.

    The returned log is in `bills` order (it was previously grouped by
    customer). The event SET and each event's contents are unaffected by that:
    `simulate_contact` seeds on `(customer_id, period_end)`, so an event does
    not depend on where in the list it is drawn, and every downstream consumer
    (`saas/reporting/annual_report.py`'s SLC 25C breach rate,
    `saas/reporting/css_statement.py`) aggregates rather than indexes.
    """
    log: list[dict] = []
    for bill in bills:
        event = simulate_contact(
            bill["customer_id"],
            bill["period_end"],
            contact_propensity_for_bill(bill),
        )
        if not event.occurred:
            continue
        log.append({
            "customer_id": event.customer_id,
            "period_end": event.period_end,
            "channel": event.channel,
            "first_response_hours": event.first_response_hours,
            "breached_sla": event.breached_sla,
        })
    return log
