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


# ---------------------------------------------------------------------------
# THE PHONE QUEUE AS A FUNCTION OF STAFFING (2026-11-21)
#
# The draw above gives every phone call a 6-minute mean wait whatever the
# supplier does, so no staffing decision can move it. What follows is the
# world's answer to a staffing plan: calls arriving at `calls_per_hour`, each
# held for `handle_minutes`, met by `agents`. It is the M/M/N (Erlang C) queue.
# That is standard telephony arithmetic, a stated belief and not an energy
# finding, and it is wrong in two known directions: real callers abandon,
# which bounds the wait, and real arrivals surge, so a mean hour understates
# the peak. Evidence and gaps:
# docs/market_research/contact_centre_staffing_cost_and_call_wait_gb_energy_2026-11-21.md
#
# Handle time has NO default. It is the input that sets the agent count almost
# one for one (that page, s.4) and GB energy publishes none (s.5). A caller that
# has not established it gets a refusal naming that gap, never a plausible
# number. It is not wired into `generate_contact_centre_log` yet for the same
# reason: the run has no sourced handle time to give it.
# ---------------------------------------------------------------------------

HANDLE_TIME_GAP = (
    "average handle time for GB energy calls is unpublished "
    "(contact_centre_staffing_cost_and_call_wait_gb_energy_2026-11-21.md s.5)"
)


@dataclass(frozen=True)
class PhoneQueue:
    """The world's phone queue for one staffing plan.

    `saturated` is True when agents <= offered load. Erlang C then has no
    steady state: the wait grows without bound until callers abandon, and
    abandonment is not modelled (same page, s.5). Both wait fields are None
    rather than a large number, because any number there would be invented.
    """

    offered_load_erlangs: float
    agents: int
    saturated: bool
    probability_of_waiting: Optional[float]
    mean_wait_seconds: Optional[float]
    mean_wait_of_those_who_wait_seconds: Optional[float]


def erlang_c(offered_load_erlangs: float, agents: int) -> float:
    """Probability an arriving call waits, M/M/N. 1.0 when saturated.

    Computed by the Erlang B recursion, which is stable at large N where the
    factorial form overflows."""
    if offered_load_erlangs <= 0:
        return 0.0
    if agents <= offered_load_erlangs:
        return 1.0
    blocking = 1.0
    for n in range(1, agents + 1):
        blocking = offered_load_erlangs * blocking / (n + offered_load_erlangs * blocking)
    rho = offered_load_erlangs / agents
    return blocking / (1.0 - rho + rho * blocking)


def phone_queue(
    calls_per_hour: float, handle_minutes: Optional[float], agents: int
) -> PhoneQueue:
    """The wait the world gives a supplier staffing `agents` against this load."""
    if handle_minutes is None:
        raise ValueError(f"phone_queue needs a handle time: {HANDLE_TIME_GAP}")
    if handle_minutes <= 0 or calls_per_hour < 0 or agents < 0:
        raise ValueError(
            f"phone_queue: handle_minutes {handle_minutes} must be > 0, "
            f"calls_per_hour {calls_per_hour} and agents {agents} >= 0"
        )
    load = calls_per_hour * handle_minutes / 60.0
    if load == 0:
        return PhoneQueue(0.0, agents, False, 0.0, 0.0, None)
    if agents <= load:
        return PhoneQueue(load, agents, True, None, None, None)
    p_wait = erlang_c(load, agents)
    of_those_who_wait = handle_minutes * 60.0 / (agents - load)
    return PhoneQueue(
        load, agents, False, p_wait, p_wait * of_those_who_wait, of_those_who_wait
    )


def draw_phone_wait_seconds(queue: PhoneQueue, rng: random.Random) -> Optional[float]:
    """One caller's wait from this queue: zero with probability 1 - C, else
    exponential with the conditional mean (exact for M/M/N under FCFS).
    None when the queue is saturated, for the reason `PhoneQueue` gives."""
    if queue.saturated:
        return None
    if queue.mean_wait_of_those_who_wait_seconds is None or rng.random() >= queue.probability_of_waiting:
        return 0.0
    return rng.expovariate(1.0 / queue.mean_wait_of_those_who_wait_seconds)
