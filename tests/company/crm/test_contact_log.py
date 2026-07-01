import pytest
from datetime import date
from company.crm.contact_log import (
    ContactChannel, ContactReason, ContactInteraction, ContactLog,
    _AVG_HANDLE_MINUTES,
)


@pytest.fixture
def log():
    return ContactLog()


@pytest.fixture
def billing_call(log):
    return log.record(
        "C001", ContactChannel.PHONE, ContactReason.BILLING_QUERY, date(2022, 3, 10)
    )


def test_record_uses_avg_handle_minutes_by_default(billing_call):
    expected = _AVG_HANDLE_MINUTES["billing_query"]
    assert billing_call.handle_minutes == pytest.approx(expected)


def test_record_custom_handle_minutes(log):
    interaction = log.record(
        "C001", ContactChannel.WEBCHAT, ContactReason.COMPLAINT,
        date(2022, 3, 15), handle_minutes=30.0
    )
    assert interaction.handle_minutes == pytest.approx(30.0)


def test_auto_increment_ids(log):
    i1 = log.record("C001", ContactChannel.PHONE, ContactReason.OTHER, date(2022, 1, 1))
    i2 = log.record("C002", ContactChannel.EMAIL, ContactReason.OTHER, date(2022, 1, 2))
    assert i1.interaction_id == 1
    assert i2.interaction_id == 2


def test_contacts_for_customer(log, billing_call):
    log.record("C002", ContactChannel.EMAIL, ContactReason.METER_READ, date(2022, 3, 11))
    c1_contacts = log.contacts_for_customer("C001")
    assert len(c1_contacts) == 1
    assert c1_contacts[0].reason == ContactReason.BILLING_QUERY


def test_complaint_higher_handle_time_than_meter_read():
    complaint_time = _AVG_HANDLE_MINUTES["complaint"]
    meter_time = _AVG_HANDLE_MINUTES["meter_read"]
    assert complaint_time > meter_time


def test_bereavement_longest_handle_time():
    bereavement = _AVG_HANDLE_MINUTES["bereavement"]
    assert all(bereavement >= v for v in _AVG_HANDLE_MINUTES.values())


def test_avg_handle_minutes_for_reason(log):
    log.record("C001", ContactChannel.PHONE, ContactReason.BILLING_QUERY, date(2022, 1, 5), handle_minutes=10.0)
    log.record("C002", ContactChannel.PHONE, ContactReason.BILLING_QUERY, date(2022, 1, 6), handle_minutes=6.0)
    avg = log.avg_handle_minutes_for_reason(ContactReason.BILLING_QUERY)
    assert avg == pytest.approx(8.0)


def test_annual_summary_empty(log):
    summary = log.annual_summary(2021)
    assert summary["total"] == 0
    assert summary["total_handle_minutes"] == 0.0


def test_annual_summary_with_data(log):
    log.record("C001", ContactChannel.PHONE, ContactReason.BILLING_QUERY, date(2022, 1, 5))
    log.record("C002", ContactChannel.WEBCHAT, ContactReason.COMPLAINT, date(2022, 2, 1), escalated=True)
    log.record("C003", ContactChannel.EMAIL, ContactReason.BILLING_QUERY, date(2022, 3, 1), resolved=False)
    summary = log.annual_summary(2022)
    assert summary["total"] == 3
    assert summary["escalated"] == 1
    assert summary["unresolved"] == 1
    assert summary["by_reason"]["billing_query"] == 2
    assert summary["total_handle_minutes"] > 0


def test_contacts_for_customer_empty(log):
    contacts = log.contacts_for_customer("UNKNOWN")
    assert contacts == []


def test_annual_summary_by_reason_multiple(log):
    log.record("C001", ContactChannel.PHONE, ContactReason.BILLING_QUERY, date(2022, 1, 1))
    log.record("C002", ContactChannel.PHONE, ContactReason.BILLING_QUERY, date(2022, 1, 2))
    log.record("C003", ContactChannel.EMAIL, ContactReason.METER_READ, date(2022, 1, 3))
    summary = log.annual_summary(2022)
    assert summary["by_reason"]["billing_query"] == 2
    assert summary["by_reason"]["meter_read"] == 1


def test_avg_handle_minutes_fallback_to_default(log):
    # No records yet — should return _AVG_HANDLE_MINUTES["tariff_query"]
    avg = log.avg_handle_minutes_for_reason(ContactReason.TARIFF_QUERY)
    assert avg == pytest.approx(_AVG_HANDLE_MINUTES["tariff_query"])


def test_record_notes_stored(log):
    interaction = log.record(
        "C001", ContactChannel.EMAIL, ContactReason.OTHER, date(2022, 6, 1), notes="Test note"
    )
    assert interaction.notes == "Test note"


def test_escalated_flag_stored(log):
    interaction = log.record(
        "C001", ContactChannel.PHONE, ContactReason.COMPLAINT, date(2022, 4, 1), escalated=True
    )
    assert interaction.escalated is True


def test_resolved_false_stored(log):
    interaction = log.record(
        "C001", ContactChannel.PHONE, ContactReason.COMPLAINT, date(2022, 4, 1), resolved=False
    )
    assert interaction.resolved is False


def test_channel_stored(log):
    interaction = log.record(
        "C001", ContactChannel.LETTER, ContactReason.BILLING_QUERY, date(2022, 5, 1)
    )
    assert interaction.channel == ContactChannel.LETTER


def test_annual_summary_year_filter(log):
    log.record("C001", ContactChannel.PHONE, ContactReason.OTHER, date(2021, 6, 1))
    log.record("C002", ContactChannel.PHONE, ContactReason.OTHER, date(2022, 6, 1))
    summary = log.annual_summary(2022)
    assert summary["total"] == 1


def test_record_returns_interaction(log):
    result = log.record("C001", ContactChannel.PHONE, ContactReason.BILLING_QUERY, date(2022, 1, 1))
    from company.crm.contact_log import ContactInteraction
    assert isinstance(result, ContactInteraction)


def test_interaction_not_escalated_by_default(log):
    interaction = log.record("C001", ContactChannel.EMAIL, ContactReason.TARIFF_QUERY, date(2022, 3, 1))
    assert interaction.escalated is False
