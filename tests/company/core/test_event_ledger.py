"""Tests for Event Ledger Core (Phase DZ)."""
import datetime as dt
import pytest
from company.core.event_ledger import (
    EventDomain, EventType, DomainEvent, EventLedger,
    _DOMAIN_MAP,
)


NOW = dt.datetime(2024, 6, 15, 12, 0, 0)
LATER = dt.datetime(2024, 6, 15, 14, 0, 0)


@pytest.fixture
def ledger():
    return EventLedger()


def emit(ledger, etype=EventType.PAYMENT_RECEIVED, account="C1",
         ts=None, payload=None, corr=None):
    return ledger.emit(
        event_type=etype,
        occurred_at=ts or NOW,
        payload=payload or {"amount": 50.0},
        account_id=account,
        correlation_id=corr,
        source_module="billing",
    )


class TestDomainEvent:
    def test_domain_billing(self):
        e = DomainEvent(
            event_type=EventType.PAYMENT_RECEIVED,
            occurred_at=NOW,
            account_id="C1",
            payload={},
        )
        assert e.domain == EventDomain.BILLING

    def test_domain_crm(self):
        e = DomainEvent(
            event_type=EventType.CUSTOMER_CHURNED,
            occurred_at=NOW,
            account_id="C1",
            payload={},
        )
        assert e.domain == EventDomain.CRM

    def test_domain_trading(self):
        e = DomainEvent(
            event_type=EventType.FORWARD_BOUGHT,
            occurred_at=NOW,
            account_id=None,
            payload={},
        )
        assert e.domain == EventDomain.TRADING

    def test_domain_risk(self):
        e = DomainEvent(
            event_type=EventType.VAR_BREACH,
            occurred_at=NOW,
            account_id=None,
            payload={},
        )
        assert e.domain == EventDomain.RISK

    def test_is_customer_event(self):
        e = DomainEvent(EventType.PAYMENT_RECEIVED, NOW, "C1", {})
        assert e.is_customer_event

    def test_not_customer_event(self):
        e = DomainEvent(EventType.FORWARD_BOUGHT, NOW, None, {})
        assert not e.is_customer_event

    def test_date_property(self):
        e = DomainEvent(EventType.PAYMENT_RECEIVED, NOW, "C1", {})
        assert e.date == dt.date(2024, 6, 15)

    def test_unique_event_ids(self):
        e1 = DomainEvent(EventType.PAYMENT_RECEIVED, NOW, "C1", {})
        e2 = DomainEvent(EventType.PAYMENT_RECEIVED, NOW, "C1", {})
        assert e1.event_id != e2.event_id

    def test_immutable(self):
        e = DomainEvent(EventType.PAYMENT_RECEIVED, NOW, "C1", {})
        with pytest.raises(Exception):
            e.account_id = "C2"


class TestEventLedger:
    def test_emit_adds_event(self, ledger):
        emit(ledger)
        assert ledger.event_count() == 1

    def test_events_for_account(self, ledger):
        emit(ledger, account="C1")
        emit(ledger, account="C2")
        assert len(ledger.events_for_account("C1")) == 1

    def test_events_by_type(self, ledger):
        emit(ledger, etype=EventType.PAYMENT_RECEIVED)
        emit(ledger, etype=EventType.CUSTOMER_CHURNED)
        assert len(ledger.events_by_type(EventType.PAYMENT_RECEIVED)) == 1

    def test_events_by_domain(self, ledger):
        emit(ledger, etype=EventType.PAYMENT_RECEIVED)
        emit(ledger, etype=EventType.FORWARD_BOUGHT, account=None)
        assert len(ledger.events_by_domain(EventDomain.BILLING)) == 1
        assert len(ledger.events_by_domain(EventDomain.TRADING)) == 1

    def test_events_by_correlation(self, ledger):
        emit(ledger, corr="SWITCH-001")
        emit(ledger, corr="SWITCH-001", etype=EventType.SWITCH_OUT_COMPLETED)
        emit(ledger, corr="OTHER")
        assert len(ledger.events_by_correlation("SWITCH-001")) == 2

    def test_events_in_window(self, ledger):
        emit(ledger, ts=NOW)
        emit(ledger, ts=LATER)
        window = ledger.events_in_window(NOW, NOW)
        assert len(window) == 1

    def test_all_events_copy(self, ledger):
        emit(ledger)
        all_e = ledger.all_events()
        all_e.append("noise")
        assert ledger.event_count() == 1  # original unmodified

    def test_domain_map_coverage(self):
        for etype in EventType:
            assert etype in _DOMAIN_MAP

    def test_ledger_summary(self, ledger):
        emit(ledger, account="C1")
        emit(ledger, account="C2")
        s = ledger.ledger_summary()
        assert "Event Ledger" in s
        assert "2 events" in s
        assert "modules communicate" in s.lower()
