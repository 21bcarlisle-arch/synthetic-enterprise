"""Phase 89: ServiceLog SQLite persistence tests."""

import pytest
from company.crm.service_log import ServiceLog, ServiceEvent, DEFAULT_DB_PATH


def _event(cid="C1", complaint=False, vuln=False, year=2024):
    return ServiceEvent(
        customer_id=cid,
        event_date=f"{year}-06-15",
        channel="portal",
        contact_reason="billing_query",
        outcome="resolved",
        complaint_flag=complaint,
        vulnerability_flag=vuln,
    )


def test_persistent_events_survive_reconnect(tmp_path):
    db = tmp_path / "sl.db"
    log1 = ServiceLog(db_path=db)
    log1.record_contact(_event("C1", complaint=True))
    log2 = ServiceLog(db_path=db)
    contacts = log2.all_contacts()
    assert len(contacts) == 1
    assert contacts[0].customer_id == "C1"


def test_persistent_complaint_rate_after_reconnect(tmp_path):
    db = tmp_path / "sl.db"
    log1 = ServiceLog(db_path=db)
    log1.record_contact(_event(complaint=True))
    log1.record_contact(_event(complaint=False))
    log2 = ServiceLog(db_path=db)
    assert abs(log2.complaint_rate() - 0.5) < 0.01


def test_persistent_vulnerability_register_after_reconnect(tmp_path):
    db = tmp_path / "sl.db"
    log1 = ServiceLog(db_path=db)
    log1.record_contact(_event(vuln=True))
    log2 = ServiceLog(db_path=db)
    reg = log2.vulnerability_register()
    assert len(reg) == 1
    assert reg[0].customer_id == "C1"


def test_persistent_resolve_vulnerability_after_reconnect(tmp_path):
    db = tmp_path / "sl.db"
    log1 = ServiceLog(db_path=db)
    log1.record_contact(_event(vuln=True))
    log2 = ServiceLog(db_path=db)
    log2.resolve_vulnerability("C1", "2024-07-01")
    log3 = ServiceLog(db_path=db)
    assert log3.vulnerability_register() == []


def test_persistent_complaint_stats_year_filter(tmp_path):
    db = tmp_path / "sl.db"
    log = ServiceLog(db_path=db)
    log.record_contact(_event(complaint=True, year=2023))
    log.record_contact(_event(complaint=True, year=2024))
    log.record_contact(_event(complaint=False, year=2024))
    stats2024 = log.complaint_stats(year=2024)
    assert stats2024["total_contacts"] == 2
    assert stats2024["total_complaints"] == 1


def test_inmemory_instances_are_independent():
    log1 = ServiceLog()
    log2 = ServiceLog()
    log1.record_contact(_event("C1"))
    assert log2.all_contacts() == []


def test_persistent_multiple_customers(tmp_path):
    db = tmp_path / "sl.db"
    log = ServiceLog(db_path=db)
    log.record_contact(_event("C1"))
    log.record_contact(_event("C2"))
    log.record_contact(_event("C1"))
    assert len(log.contacts_for_customer("C1")) == 2
    assert len(log.contacts_for_customer("C2")) == 1


def test_default_db_path_is_path_object():
    assert hasattr(DEFAULT_DB_PATH, "parent")


# --- Phase KJ depth tests ---

def test_channel_stored(tmp_path):
    db = tmp_path / "sl.db"
    log = ServiceLog(db_path=db)
    log.record_contact(_event("C1"))
    contacts = log.contacts_for_customer("C1")
    assert contacts[0].channel == "portal"


def test_contact_reason_stored(tmp_path):
    db = tmp_path / "sl.db"
    log = ServiceLog(db_path=db)
    log.record_contact(_event("C1"))
    contacts = log.contacts_for_customer("C1")
    assert contacts[0].contact_reason == "billing_query"


def test_outcome_stored(tmp_path):
    db = tmp_path / "sl.db"
    log = ServiceLog(db_path=db)
    log.record_contact(_event("C1"))
    contacts = log.contacts_for_customer("C1")
    assert contacts[0].outcome == "resolved"


def test_complaint_flag_stored(tmp_path):
    db = tmp_path / "sl.db"
    log = ServiceLog(db_path=db)
    log.record_contact(_event("C1", complaint=True))
    contacts = log.contacts_for_customer("C1")
    assert contacts[0].complaint_flag is True


def test_persistent_empty_initially(tmp_path):
    db = tmp_path / "sl.db"
    log = ServiceLog(db_path=db)
    assert log.all_contacts() == []


def test_two_complaints_in_year(tmp_path):
    db = tmp_path / "sl.db"
    log = ServiceLog(db_path=db)
    log.record_contact(_event("C1", complaint=True, year=2024))
    log.record_contact(_event("C2", complaint=True, year=2024))
    stats = log.complaint_stats(year=2024)
    assert stats["total_complaints"] == 2


def test_vulnerability_flag_false_not_in_register(tmp_path):
    db = tmp_path / "sl.db"
    log = ServiceLog(db_path=db)
    log.record_contact(_event("C1", vuln=False))
    assert log.vulnerability_register() == []


def test_event_date_stored(tmp_path):
    db = tmp_path / "sl.db"
    log = ServiceLog(db_path=db)
    log.record_contact(_event("C1", year=2022))
    contacts = log.contacts_for_customer("C1")
    assert "2022" in contacts[0].event_date


def test_complaint_rate_zero_no_complaints(tmp_path):
    db = tmp_path / "sl.db"
    log = ServiceLog(db_path=db)
    log.record_contact(_event("C1", complaint=False))
    assert log.complaint_rate() == pytest.approx(0.0)


def test_persistent_vulnerability_multiple_reconnect(tmp_path):
    db = tmp_path / "sl.db"
    log1 = ServiceLog(db_path=db)
    log1.record_contact(_event("C1", vuln=True))
    log1.record_contact(_event("C2", vuln=True))
    log2 = ServiceLog(db_path=db)
    reg = log2.vulnerability_register()
    assert len(reg) == 2
