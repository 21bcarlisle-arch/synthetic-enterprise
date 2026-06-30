"""Event Ledger Core (Phase DZ).

The CTO Architecture Guidance mandates event-driven architecture:
everything is an event: timestamped, typed, immutable.
Modules communicate via the ledger, never direct function calls.
Foundation for Horizon 2: 3-horizon CLV, resentment ledger, reputation index.
"""
from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EventDomain(str, Enum):
    BILLING = "billing"
    CRM = "crm"
    TRADING = "trading"
    COMPLIANCE = "compliance"
    SUPPLY = "supply"
    RISK = "risk"
    MARKET = "market"
    SUSTAINABILITY = "sustainability"


class EventType(str, Enum):
    INVOICE_GENERATED = "invoice_generated"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    BILLING_DISPUTE_RAISED = "billing_dispute_raised"
    CREDIT_REFUND_ISSUED = "credit_refund_issued"
    CUSTOMER_ACQUIRED = "customer_acquired"
    CUSTOMER_CHURNED = "customer_churned"
    RENEWAL_NOTICE_SENT = "renewal_notice_sent"
    RETENTION_OFFER_MADE = "retention_offer_made"
    COMPLAINT_RAISED = "complaint_raised"
    COMPLAINT_RESOLVED = "complaint_resolved"
    FORWARD_BOUGHT = "forward_bought"
    FORWARD_SOLD = "forward_sold"
    HEDGE_PLACED = "hedge_placed"
    POSITION_CLOSED = "position_closed"
    MARGIN_CALL_RECEIVED = "margin_call_received"
    SLC_BREACH_IDENTIFIED = "slc_breach_identified"
    REGULATORY_REPORT_SUBMITTED = "regulatory_report_submitted"
    OFGEM_ENQUIRY_RECEIVED = "ofgem_enquiry_received"
    METER_READ_RECEIVED = "meter_read_received"
    CONTRACT_SIGNED = "contract_signed"
    SWITCH_OUT_INITIATED = "switch_out_initiated"
    SWITCH_OUT_COMPLETED = "switch_out_completed"
    SWITCH_IN_COMPLETED = "switch_in_completed"
    VAR_BREACH = "var_breach"
    CREDIT_LIMIT_BREACH = "credit_limit_breach"
    STRESS_TEST_FAILED = "stress_test_failed"


_DOMAIN_MAP: Dict[EventType, EventDomain] = {
    EventType.INVOICE_GENERATED: EventDomain.BILLING,
    EventType.PAYMENT_RECEIVED: EventDomain.BILLING,
    EventType.PAYMENT_FAILED: EventDomain.BILLING,
    EventType.BILLING_DISPUTE_RAISED: EventDomain.BILLING,
    EventType.CREDIT_REFUND_ISSUED: EventDomain.BILLING,
    EventType.CUSTOMER_ACQUIRED: EventDomain.CRM,
    EventType.CUSTOMER_CHURNED: EventDomain.CRM,
    EventType.RENEWAL_NOTICE_SENT: EventDomain.CRM,
    EventType.RETENTION_OFFER_MADE: EventDomain.CRM,
    EventType.COMPLAINT_RAISED: EventDomain.CRM,
    EventType.COMPLAINT_RESOLVED: EventDomain.CRM,
    EventType.FORWARD_BOUGHT: EventDomain.TRADING,
    EventType.FORWARD_SOLD: EventDomain.TRADING,
    EventType.HEDGE_PLACED: EventDomain.TRADING,
    EventType.POSITION_CLOSED: EventDomain.TRADING,
    EventType.MARGIN_CALL_RECEIVED: EventDomain.TRADING,
    EventType.SLC_BREACH_IDENTIFIED: EventDomain.COMPLIANCE,
    EventType.REGULATORY_REPORT_SUBMITTED: EventDomain.COMPLIANCE,
    EventType.OFGEM_ENQUIRY_RECEIVED: EventDomain.COMPLIANCE,
    EventType.METER_READ_RECEIVED: EventDomain.SUPPLY,
    EventType.CONTRACT_SIGNED: EventDomain.SUPPLY,
    EventType.SWITCH_OUT_INITIATED: EventDomain.SUPPLY,
    EventType.SWITCH_OUT_COMPLETED: EventDomain.SUPPLY,
    EventType.SWITCH_IN_COMPLETED: EventDomain.SUPPLY,
    EventType.VAR_BREACH: EventDomain.RISK,
    EventType.CREDIT_LIMIT_BREACH: EventDomain.RISK,
    EventType.STRESS_TEST_FAILED: EventDomain.RISK,
}


@dataclass(frozen=True)
class DomainEvent:
    event_type: EventType
    occurred_at: dt.datetime
    account_id: Optional[str]
    payload: Dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    source_module: Optional[str] = None

    @property
    def domain(self) -> EventDomain:
        return _DOMAIN_MAP.get(self.event_type, EventDomain.BILLING)

    @property
    def is_customer_event(self) -> bool:
        return self.account_id is not None

    @property
    def date(self) -> dt.date:
        return self.occurred_at.date()


class EventLedger:
    """Append-only in-memory event ledger. Modules publish here, never call each other."""

    def __init__(self) -> None:
        self._events: List[DomainEvent] = []

    def publish(self, event: DomainEvent) -> DomainEvent:
        self._events.append(event)
        return event

    def emit(
        self,
        event_type: EventType,
        occurred_at: dt.datetime,
        payload: Dict[str, Any],
        account_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        source_module: Optional[str] = None,
    ) -> DomainEvent:
        event = DomainEvent(
            event_type=event_type,
            occurred_at=occurred_at,
            account_id=account_id,
            payload=payload,
            correlation_id=correlation_id,
            source_module=source_module,
        )
        return self.publish(event)

    def all_events(self) -> List[DomainEvent]:
        return list(self._events)

    def events_for_account(self, account_id: str) -> List[DomainEvent]:
        return [e for e in self._events if e.account_id == account_id]

    def events_by_type(self, event_type: EventType) -> List[DomainEvent]:
        return [e for e in self._events if e.event_type == event_type]

    def events_by_domain(self, domain: EventDomain) -> List[DomainEvent]:
        return [e for e in self._events if e.domain == domain]

    def events_by_correlation(self, correlation_id: str) -> List[DomainEvent]:
        return [e for e in self._events if e.correlation_id == correlation_id]

    def events_in_window(
        self, start: dt.datetime, end: dt.datetime
    ) -> List[DomainEvent]:
        return [e for e in self._events if start <= e.occurred_at <= end]

    def event_count(self) -> int:
        return len(self._events)

    def ledger_summary(self) -> str:
        n = len(self._events)
        domains = {e.domain for e in self._events}
        accounts = {e.account_id for e in self._events if e.account_id}
        return (
            f"Event Ledger: {n} events across {len(domains)} domains, "
            f"{len(accounts)} customer accounts. "
            f"Append-only; modules communicate via events, never direct calls."
        )
