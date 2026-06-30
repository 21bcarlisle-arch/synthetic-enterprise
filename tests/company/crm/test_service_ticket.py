"""Tests for Customer Service Ticket Book (Phase EW)."""
import datetime as dt
import pytest
from company.crm.service_ticket import (
    TicketCategory, TicketStatus, ServiceTicket, ServiceTicketBook,
    _add_working_days, _ACKNOWLEDGEMENT_DEADLINE_WD, _FULL_RESPONSE_DEADLINE_DAYS,
)

DATE = dt.date(2024, 1, 15)


class TestAddWorkingDays:
    def test_adds_3_wd(self):
        mon = dt.date(2024, 1, 15)  # Monday
        result = _add_working_days(mon, 3)
        assert result == dt.date(2024, 1, 18)  # Thursday

    def test_skips_weekend(self):
        fri = dt.date(2024, 1, 19)  # Friday
        result = _add_working_days(fri, 1)
        assert result == dt.date(2024, 1, 22)  # Monday


def make_ticket(status=TicketStatus.OPEN, resolved=None, ack=None, comp=0.0):
    return ServiceTicket(
        ticket_id="TKT-000001",
        account_id="C1",
        category=TicketCategory.BILLING_QUERY,
        opened_at=DATE,
        status=status,
        resolved_at=resolved,
        acknowledged_at=ack,
        compensation_offered_gbp=comp,
    )


class TestServiceTicket:
    def test_acknowledgement_deadline(self):
        t = make_ticket()
        assert t.acknowledgement_deadline > DATE

    def test_full_response_deadline(self):
        t = make_ticket()
        expected = DATE + dt.timedelta(days=56)
        assert t.full_response_deadline == expected

    def test_is_acknowledgement_overdue(self):
        t = make_ticket()
        future = DATE + dt.timedelta(days=10)
        assert t.is_acknowledgement_overdue(future)

    def test_is_not_acknowledgement_overdue_when_acked(self):
        t = make_ticket(ack=DATE + dt.timedelta(days=2))
        assert not t.is_acknowledgement_overdue(DATE + dt.timedelta(days=10))

    def test_is_response_overdue(self):
        t = make_ticket(status=TicketStatus.IN_PROGRESS)
        far_future = DATE + dt.timedelta(days=70)
        assert t.is_response_overdue(far_future)

    def test_is_not_response_overdue_when_resolved(self):
        t = make_ticket(status=TicketStatus.RESOLVED, resolved=DATE + dt.timedelta(days=5))
        assert not t.is_response_overdue(DATE + dt.timedelta(days=70))

    def test_is_escalated(self):
        t = make_ticket(status=TicketStatus.ESCALATED)
        assert t.is_escalated()

    def test_days_to_resolve(self):
        t = make_ticket(resolved=DATE + dt.timedelta(days=5))
        assert t.days_to_resolve() == 5

    def test_days_to_resolve_none(self):
        t = make_ticket()
        assert t.days_to_resolve() is None

    def test_ticket_summary(self):
        t = make_ticket()
        s = t.ticket_summary()
        assert "TKT-000001" in s
        assert "billing_query" in s


class TestServiceTicketBook:
    def test_open_ticket(self):
        book = ServiceTicketBook()
        t = book.open_ticket("C1", TicketCategory.BILLING_QUERY, DATE)
        assert t.ticket_id == "TKT-000001"
        assert t.status == TicketStatus.OPEN

    def test_sequential_ticket_ids(self):
        book = ServiceTicketBook()
        t1 = book.open_ticket("C1", TicketCategory.BILLING_QUERY, DATE)
        t2 = book.open_ticket("C1", TicketCategory.SWITCHING, DATE)
        assert t1.ticket_id != t2.ticket_id

    def test_update_status_resolved(self):
        book = ServiceTicketBook()
        t = book.open_ticket("C1", TicketCategory.BILLING_QUERY, DATE)
        updated = book.update_status(t.ticket_id, TicketStatus.RESOLVED, DATE + dt.timedelta(days=3))
        assert updated.status == TicketStatus.RESOLVED
        assert updated.resolved_at == DATE + dt.timedelta(days=3)

    def test_tickets_for(self):
        book = ServiceTicketBook()
        book.open_ticket("C1", TicketCategory.BILLING_QUERY, DATE)
        book.open_ticket("C2", TicketCategory.SWITCHING, DATE)
        assert len(book.tickets_for("C1")) == 1

    def test_open_tickets(self):
        book = ServiceTicketBook()
        t = book.open_ticket("C1", TicketCategory.BILLING_QUERY, DATE)
        book.update_status(t.ticket_id, TicketStatus.RESOLVED, DATE)
        book.open_ticket("C2", TicketCategory.SWITCHING, DATE)
        assert len(book.open_tickets()) == 1

    def test_overdue_acknowledgements(self):
        book = ServiceTicketBook()
        book.open_ticket("C1", TicketCategory.BILLING_QUERY, DATE)
        far_future = DATE + dt.timedelta(days=10)
        assert len(book.overdue_acknowledgements(far_future)) == 1

    def test_escalated_tickets(self):
        book = ServiceTicketBook()
        t = book.open_ticket("C1", TicketCategory.BILLING_QUERY, DATE)
        book.update_status(t.ticket_id, TicketStatus.ESCALATED, DATE)
        assert len(book.escalated_tickets()) == 1

    def test_total_compensation(self):
        book = ServiceTicketBook()
        t = book.open_ticket("C1", TicketCategory.BILLING_QUERY, DATE)
        book.update_status(t.ticket_id, TicketStatus.RESOLVED, DATE, compensation_gbp=50.0)
        assert book.total_compensation_gbp() == pytest.approx(50.0)

    def test_avg_resolution_days(self):
        book = ServiceTicketBook()
        t = book.open_ticket("C1", TicketCategory.BILLING_QUERY, DATE)
        book.update_status(t.ticket_id, TicketStatus.RESOLVED, DATE + dt.timedelta(days=5))
        assert book.avg_resolution_days() == pytest.approx(5.0)

    def test_avg_resolution_none_when_none_resolved(self):
        book = ServiceTicketBook()
        book.open_ticket("C1", TicketCategory.BILLING_QUERY, DATE)
        assert book.avg_resolution_days() is None

    def test_service_summary(self):
        book = ServiceTicketBook()
        book.open_ticket("C1", TicketCategory.BILLING_QUERY, DATE)
        s = book.service_summary(DATE)
        assert "Service Tickets" in s
