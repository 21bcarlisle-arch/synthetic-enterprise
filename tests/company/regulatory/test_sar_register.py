"""Tests for SAR Register (Phase DF)."""
import datetime as dt
import pytest
from company.regulatory.sar_register import (
    SARStatus, SARTrigger, SARRefusalReason, SARRegister,
    _STANDARD_DEADLINE_DAYS, _EXTENDED_DEADLINE_DAYS, _MAX_FINE_GBP,
)


@pytest.fixture
def reg():
    return SARRegister()


@pytest.fixture
def received_sar(reg):
    return reg.receive("C1", dt.date(2024, 1, 15), SARTrigger.BILLING_DISPUTE)


class TestSARRecord:
    def test_receive_creates_record(self, reg):
        rec = reg.receive("C2", dt.date(2024, 3, 1), SARTrigger.DEBT_DISPUTE)
        assert rec.customer_id == "C2"
        assert rec.status == SARStatus.RECEIVED
        assert rec.trigger == SARTrigger.DEBT_DISPUTE
        assert not rec.is_extended

    def test_sar_id_sequential(self, reg):
        r1 = reg.receive("C1", dt.date(2024, 1, 1), SARTrigger.UNKNOWN)
        r2 = reg.receive("C2", dt.date(2024, 1, 2), SARTrigger.UNKNOWN)
        assert r1.sar_id != r2.sar_id

    def test_standard_deadline_30_days(self, received_sar):
        assert received_sar.deadline == dt.date(2024, 1, 15) + dt.timedelta(days=30)

    def test_extended_deadline_90_days(self, reg):
        rec = reg.receive("C3", dt.date(2024, 1, 15), SARTrigger.GENERAL_ENQUIRY)
        extended = reg.extend(rec.sar_id)
        assert extended.deadline == dt.date(2024, 1, 15) + dt.timedelta(days=90)
        assert extended.is_extended

    def test_not_overdue_before_deadline(self, received_sar):
        before = received_sar.received_at + dt.timedelta(days=29)
        assert not received_sar.is_overdue(before)

    def test_overdue_after_deadline(self, received_sar):
        after = received_sar.received_at + dt.timedelta(days=31)
        assert received_sar.is_overdue(after)

    def test_not_overdue_on_deadline_day(self, received_sar):
        on_day = received_sar.deadline
        assert not received_sar.is_overdue(on_day)

    def test_responded_not_overdue(self, reg, received_sar):
        responded = reg.respond(received_sar.sar_id, dt.date(2024, 2, 14))
        assert not responded.is_overdue(dt.date(2024, 3, 1))

    def test_days_to_deadline_positive(self, received_sar):
        before = received_sar.received_at + dt.timedelta(days=10)
        assert received_sar.days_to_deadline(before) == 20

    def test_days_to_respond_none_until_responded(self, received_sar):
        assert received_sar.days_to_respond is None

    def test_days_to_respond_calculated_on_response(self, reg, received_sar):
        responded = reg.respond(received_sar.sar_id, dt.date(2024, 2, 1))
        expected = (dt.date(2024, 2, 1) - dt.date(2024, 1, 15)).days
        assert responded.days_to_respond == expected

    def test_responded_within_deadline_on_time(self, reg, received_sar):
        responded = reg.respond(received_sar.sar_id, dt.date(2024, 2, 1))
        assert responded.responded_within_deadline is True

    def test_responded_within_deadline_late(self, reg, received_sar):
        responded = reg.respond(received_sar.sar_id, dt.date(2024, 3, 1))
        assert responded.responded_within_deadline is False

    def test_is_active_statuses(self, reg):
        rec = reg.receive("C5", dt.date(2024, 1, 1), SARTrigger.PRE_LITIGATION)
        assert rec.is_active
        ack = reg.acknowledge(rec.sar_id)
        assert ack.is_active
        rsp = reg.respond(rec.sar_id, dt.date(2024, 1, 20))
        assert not rsp.is_active

    def test_refused_not_active(self, reg):
        rec = reg.receive("C6", dt.date(2024, 1, 1), SARTrigger.UNKNOWN)
        refused = reg.refuse(rec.sar_id, SARRefusalReason.MANIFESTLY_EXCESSIVE)
        assert not refused.is_active
        assert refused.refused_reason == SARRefusalReason.MANIFESTLY_EXCESSIVE

    def test_fee_charged_for_excessive(self, reg):
        rec = reg.receive("C7", dt.date(2024, 1, 1), SARTrigger.UNKNOWN)
        refused = reg.refuse(rec.sar_id, SARRefusalReason.MANIFESTLY_EXCESSIVE, fee_charged_gbp=10.0)
        assert refused.fee_charged_gbp == 10.0

    def test_ico_complaint_raised(self, reg, received_sar):
        ico = reg.mark_ico_complaint(received_sar.sar_id, "ICO/2024/12345")
        assert ico.ico_complaint_ref == "ICO/2024/12345"
        assert ico.status == SARStatus.COMPLAINT_RAISED


class TestSARRegisterQueries:
    def test_overdue_list(self, reg):
        rec = reg.receive("C1", dt.date(2024, 1, 1), SARTrigger.BILLING_DISPUTE)
        as_of = dt.date(2024, 2, 15)
        assert rec in reg.overdue(as_of)

    def test_overdue_excludes_responded(self, reg):
        rec = reg.receive("C1", dt.date(2024, 1, 1), SARTrigger.BILLING_DISPUTE)
        reg.respond(rec.sar_id, dt.date(2024, 1, 20))
        assert reg.overdue(dt.date(2024, 2, 15)) == []

    def test_active_list(self, reg):
        r1 = reg.receive("C1", dt.date(2024, 1, 1), SARTrigger.BILLING_DISPUTE)
        r2 = reg.receive("C2", dt.date(2024, 1, 1), SARTrigger.DEBT_DISPUTE)
        reg.respond(r2.sar_id, dt.date(2024, 1, 25))
        active = reg.active()
        assert r1 in active
        assert all(r.sar_id != r2.sar_id for r in active)

    def test_late_responses(self, reg):
        rec = reg.receive("C3", dt.date(2024, 1, 1), SARTrigger.UNKNOWN)
        reg.respond(rec.sar_id, dt.date(2024, 3, 1))
        late = reg.late_responses()
        assert any(r.sar_id == rec.sar_id for r in late)

    def test_on_time_responses_not_in_late(self, reg):
        rec = reg.receive("C4", dt.date(2024, 1, 1), SARTrigger.UNKNOWN)
        reg.respond(rec.sar_id, dt.date(2024, 1, 25))
        assert reg.late_responses() == []

    def test_by_trigger(self, reg):
        reg.receive("C1", dt.date(2024, 1, 1), SARTrigger.BILLING_DISPUTE)
        reg.receive("C2", dt.date(2024, 1, 2), SARTrigger.BILLING_DISPUTE)
        reg.receive("C3", dt.date(2024, 1, 3), SARTrigger.DEBT_DISPUTE)
        trig = reg.by_trigger()
        assert trig[SARTrigger.BILLING_DISPUTE.value] == 2
        assert trig[SARTrigger.DEBT_DISPUTE.value] == 1

    def test_compliance_rate_all_on_time(self, reg):
        rec = reg.receive("C1", dt.date(2024, 1, 1), SARTrigger.UNKNOWN)
        reg.respond(rec.sar_id, dt.date(2024, 1, 25))
        assert reg.compliance_rate() == 1.0

    def test_compliance_rate_one_late(self, reg):
        r1 = reg.receive("C1", dt.date(2024, 1, 1), SARTrigger.UNKNOWN)
        r2 = reg.receive("C2", dt.date(2024, 1, 1), SARTrigger.UNKNOWN)
        reg.respond(r1.sar_id, dt.date(2024, 1, 25))
        reg.respond(r2.sar_id, dt.date(2024, 3, 1))
        assert reg.compliance_rate() == pytest.approx(0.5)

    def test_compliance_rate_no_responses(self, reg):
        assert reg.compliance_rate() == 1.0

    def test_sar_summary_string(self, reg):
        rec = reg.receive("C1", dt.date(2024, 1, 1), SARTrigger.BILLING_DISPUTE)
        reg.respond(rec.sar_id, dt.date(2024, 1, 25))
        s = reg.sar_summary()
        assert "SAR Register" in s
        assert "30" in s

    def test_constants(self):
        assert _STANDARD_DEADLINE_DAYS == 30
        assert _EXTENDED_DEADLINE_DAYS == 90
        assert _MAX_FINE_GBP == 17_500_000.0

    def test_vulnerability_trigger_exists(self, reg):
        rec = reg.receive("C9", dt.date(2024, 6, 1), SARTrigger.VULNERABILITY_CONCERN)
        assert rec.trigger == SARTrigger.VULNERABILITY_CONCERN

    def test_multiple_customers_isolated(self, reg):
        r1 = reg.receive("C1", dt.date(2024, 1, 1), SARTrigger.BILLING_DISPUTE)
        r2 = reg.receive("C1", dt.date(2024, 2, 1), SARTrigger.DEBT_DISPUTE)
        assert r1.sar_id != r2.sar_id
        assert len(reg.active()) == 2

    def test_extended_not_overdue_before_90d(self, reg):
        rec = reg.receive("C10", dt.date(2024, 1, 1), SARTrigger.GENERAL_ENQUIRY)
        reg.extend(rec.sar_id)
        assert not reg._requests[rec.sar_id].is_overdue(dt.date(2024, 3, 30))

    def test_refusal_reasons_exist(self):
        reasons = list(SARRefusalReason)
        assert SARRefusalReason.MANIFESTLY_UNFOUNDED in reasons
        assert SARRefusalReason.MANIFESTLY_EXCESSIVE in reasons
        assert SARRefusalReason.THIRD_PARTY_RIGHTS in reasons
        assert SARRefusalReason.LEGAL_EXEMPTION in reasons
