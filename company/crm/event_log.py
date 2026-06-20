"""Company CRM event log - Phase 12a.

Append-only record of customer lifecycle events as seen by the company layer.
The company learns of churn and acquisition through the SimInterface; this log
is the permanent, dated artefact that makes a customer departure (or arrival)
a real event rather than a flag in a set.

Phase 12a: events mirror SIM ground truth exactly - the company learns the
outcome immediately after the SIM rolls it. Divergence becomes possible in
Phase 12b when the company acts on its own churn estimate before the SIM
rolls, potentially reducing churn probability via a retention offer.
"""

from dataclasses import dataclass


@dataclass
class ChurnEvent:
    customer_id: str
    event_date: str
    reason: str = "non-renewal"
    sim_churn_probability: object = None
    company_churn_estimate: object = None


@dataclass
class AcquisitionEvent:
    customer_id: str
    event_date: str
    channel: str = "market-acquisition"
    predecessor_id: object = None


class CompanyEventLog:
    """Append-only company CRM event log."""

    def __init__(self):
        self._events = []

    def record_churn(self, event):
        self._events.append(event)

    def record_acquisition(self, event):
        self._events.append(event)

    def all_events(self):
        return list(self._events)

    def active_accounts(self, as_of_date):
        """Set of customer IDs the company believes are active on as_of_date.

        Replays events in chronological order up to and including as_of_date.
        An AcquisitionEvent adds the account; a ChurnEvent removes it.
        """
        active = set()
        for ev in sorted(self._events, key=lambda e: e.event_date):
            if ev.event_date > as_of_date:
                break
            if isinstance(ev, AcquisitionEvent):
                active.add(ev.customer_id)
            elif isinstance(ev, ChurnEvent):
                active.discard(ev.customer_id)
        return active

    def churn_events(self):
        return [e for e in self._events if isinstance(e, ChurnEvent)]

    def acquisition_events(self):
        return [e for e in self._events if isinstance(e, AcquisitionEvent)]

    def as_dicts(self):
        result = []
        for ev in self._events:
            if isinstance(ev, ChurnEvent):
                result.append({
                    "event_type": "churn",
                    "customer_id": ev.customer_id,
                    "event_date": ev.event_date,
                    "reason": ev.reason,
                    "sim_churn_probability": ev.sim_churn_probability,
                    "company_churn_estimate": ev.company_churn_estimate,
                })
            else:
                result.append({
                    "event_type": "acquisition",
                    "customer_id": ev.customer_id,
                    "event_date": ev.event_date,
                    "channel": ev.channel,
                    "predecessor_id": ev.predecessor_id,
                })
        return result
