# Increment 3: the legs of tests/company/test_phase_ir_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase IR: deeper coverage for tpi_book, vulnerability_index, contact_log."""
import datetime as dt
import pytest


# ===== contact_log =====
from company.crm.contact_log import (
    ContactLog, ContactChannel, ContactReason
)


def _log():
    l = ContactLog()
    l.record("C1", ContactChannel.PHONE, ContactReason.BILLING_QUERY, dt.date(2022,3,1))
    l.record("C1", ContactChannel.WEBCHAT, ContactReason.COMPLAINT, dt.date(2022,4,1),
              handle_minutes=20.0, escalated=True, resolved=False)
    l.record("C2", ContactChannel.EMAIL, ContactReason.PAYMENT_DIFFICULTY,
              dt.date(2022,5,1))
    return l


class TestContactLog:
    def test_interaction_id_sequential(self):
        l = _log()
        assert l._interactions[0].interaction_id == 1
        assert l._interactions[1].interaction_id == 2

    def test_default_handle_minutes_from_lookup(self):
        l = _log()
        # billing_query default = 8.0
        assert l._interactions[0].handle_minutes == pytest.approx(8.0)

    def test_contacts_for_customer(self):
        l = _log()
        assert len(l.contacts_for_customer("C1")) == 2

    def test_escalated_flag(self):
        l = _log()
        assert l._interactions[1].escalated

    def test_not_resolved_flag(self):
        l = _log()
        assert not l._interactions[1].resolved

    def test_avg_handle_minutes_for_reason(self):
        l = _log()
        # Only one complaint at 20 minutes
        avg = l.avg_handle_minutes_for_reason(ContactReason.COMPLAINT)
        assert avg == pytest.approx(20.0)

    def test_annual_summary_total(self):
        l = _log()
        s = l.annual_summary(2022)
        assert s["total"] == 3

    def test_annual_summary_escalated(self):
        l = _log()
        s = l.annual_summary(2022)
        assert s["escalated"] == 1

    def test_annual_summary_unresolved(self):
        l = _log()
        s = l.annual_summary(2022)
        assert s["unresolved"] == 1

    def test_annual_summary_by_reason(self):
        l = _log()
        s = l.annual_summary(2022)
        assert "billing_query" in s["by_reason"]
