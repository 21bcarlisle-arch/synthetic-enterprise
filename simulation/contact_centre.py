"""Contact-centre first-response time model (Phase 3 item 4, docs/design/
CORE_FIDELITY_PHASES.md: "No dedicated latency module exists -- distinct
from complaint *resolution* time [simulation/feedback_survey.py, real], the
*first-response* SLA is not [modelled]").

saas/contact_model.py already computes, per bill, the probability a
confusing/shocking bill drives a customer to contact the supplier
(`contact_probability`) -- but that probability was never turned into a
discrete contact EVENT with its own timing. This module is that event
layer: given a contact occurs, it picks a real contact channel (phone /
webchat / email -- UK energy-sector contact mix skews heavily to phone) and
simulates how long the FIRST acknowledgement takes, distinct from
`feedback_survey.dispatch_complaint_and_resolution`'s full-resolution
timer.

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
    """Roll whether a contact occurs this bill (using the same probability
    saas.contact_model.contact_probability already computes from clarity/
    bill-shock), and if so, its channel and first-response latency.
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


def generate_contact_centre_log(bills: list[dict], contact_model: dict) -> list[dict]:
    """One contact-centre event per bill, using saas.contact_model's already-
    computed per-bill contact_probability as the trigger. `contact_model` is
    saas.contact_model.build_contact_model(bills)'s output (`by_customer`).
    """
    by_customer = contact_model.get("by_customer", {})
    log: list[dict] = []
    for cid, entries in by_customer.items():
        for entry in entries:
            event = simulate_contact(
                cid, entry["period_end"], entry["contact_probability"]
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
