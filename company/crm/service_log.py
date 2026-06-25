"""CRM service interaction log (C4 -- Phase 69).

Records every customer service contact: channel, reason, outcome, agent type,
complaint/vulnerability flags. Extends CompanyEventLog with service events.
Provides vulnerability register and complaint statistics for reporting.
"""

from dataclasses import dataclass, field


@dataclass
class ServiceEvent:
    customer_id: str
    event_date: str
    channel: str          # phone / email / webchat / letter / portal
    contact_reason: str   # billing_query / payment / complaint / general / switch_query / smart_meter
    outcome: str          # resolved / escalated / pending / no_action
    agent_type: str = "ai"        # ai / human / hybrid
    complaint_flag: bool = False
    vulnerability_flag: bool = False
    notes: str = ""


@dataclass
class VulnerabilityFlag:
    customer_id: str
    flagged_date: str
    flag_type: str    # financial_difficulty / health / accessibility / elderly
    active: bool = True
    resolved_date: str = ""


class ServiceLog:
    """Append-only service interaction log. Independent from CompanyEventLog
    lifecycle events so the two concerns stay separate."""

    def __init__(self):
        self._events: list[ServiceEvent] = []
        self._vulnerability_flags: list[VulnerabilityFlag] = []

    def record_contact(self, event: ServiceEvent) -> None:
        self._events.append(event)
        if event.vulnerability_flag:
            self._vulnerability_flags.append(
                VulnerabilityFlag(
                    customer_id=event.customer_id,
                    flagged_date=event.event_date,
                    flag_type="financial_difficulty",
                )
            )

    def all_contacts(self) -> list[ServiceEvent]:
        return list(self._events)

    def contacts_for_customer(self, customer_id: str) -> list[ServiceEvent]:
        return [e for e in self._events if e.customer_id == customer_id]

    def complaints(self) -> list[ServiceEvent]:
        return [e for e in self._events if e.complaint_flag]

    def complaint_rate(self) -> float:
        """Complaints as a proportion of all contacts. 0.0 if no contacts."""
        if not self._events:
            return 0.0
        return len(self.complaints()) / len(self._events)

    def complaint_stats(self, year: int | None = None) -> dict:
        """Complaint counts and rate, optionally filtered to a calendar year."""
        events = self._events
        if year is not None:
            yr = str(year)
            events = [e for e in events if e.event_date.startswith(yr)]
        complaints = [e for e in events if e.complaint_flag]
        rate = len(complaints) / len(events) if events else 0.0
        return {
            "total_contacts": len(events),
            "total_complaints": len(complaints),
            "complaint_rate": round(rate, 4),
        }

    def vulnerability_register(self) -> list[VulnerabilityFlag]:
        """Active vulnerability flags across the customer base."""
        return [v for v in self._vulnerability_flags if v.active]

    def resolve_vulnerability(self, customer_id: str, resolved_date: str) -> int:
        """Mark vulnerability flags for a customer as resolved. Returns count resolved."""
        count = 0
        for v in self._vulnerability_flags:
            if v.customer_id == customer_id and v.active:
                v.active = False
                v.resolved_date = resolved_date
                count += 1
        return count

    def as_dicts(self) -> list[dict]:
        return [
            {
                "event_type": "service_contact",
                "customer_id": e.customer_id,
                "event_date": e.event_date,
                "channel": e.channel,
                "contact_reason": e.contact_reason,
                "outcome": e.outcome,
                "agent_type": e.agent_type,
                "complaint_flag": e.complaint_flag,
                "vulnerability_flag": e.vulnerability_flag,
                "notes": e.notes,
            }
            for e in self._events
        ]
