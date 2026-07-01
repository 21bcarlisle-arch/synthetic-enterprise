import pytest
from datetime import date
from company.crm.life_events import (
    LifeEventType, LifeEvent, LifeEventLog,
)


@pytest.fixture
def log():
    return LifeEventLog()


def test_job_loss_triggers_vulnerability_review():
    e = LifeEvent("C001", LifeEventType.JOB_LOSS, date(2022, 3, 1))
    assert e.triggers_vulnerability_review is True


def test_birth_does_not_trigger_vulnerability_review():
    e = LifeEvent("C001", LifeEventType.BIRTH, date(2022, 3, 1))
    assert e.triggers_vulnerability_review is False


def test_birth_triggers_occupancy_change():
    e = LifeEvent("C001", LifeEventType.BIRTH, date(2022, 3, 1), occupancy_delta=1)
    assert e.triggers_occupancy_change is True
    assert e.occupancy_delta == 1


def test_move_in_triggers_cot():
    e = LifeEvent("C001", LifeEventType.MOVE_IN, date(2022, 3, 1))
    assert e.triggers_cot is True


def test_job_loss_does_not_trigger_cot():
    e = LifeEvent("C001", LifeEventType.JOB_LOSS, date(2022, 3, 1))
    assert e.triggers_cot is False


def test_serious_illness_triggers_psr_review():
    e = LifeEvent("C001", LifeEventType.SERIOUS_ILLNESS, date(2022, 5, 1))
    assert e.triggers_psr_review is True


def test_marriage_does_not_trigger_psr_review():
    e = LifeEvent("C001", LifeEventType.MARRIAGE, date(2022, 5, 1))
    assert e.triggers_psr_review is False


def test_record_and_retrieve(log):
    e = LifeEvent("C001", LifeEventType.RETIREMENT, date(2022, 6, 1))
    log.record(e)
    events = log.events_for_customer("C001")
    assert len(events) == 1


def test_pending_vulnerability_reviews(log):
    log.record(LifeEvent("C001", LifeEventType.JOB_LOSS, date(2022, 1, 5)))
    log.record(LifeEvent("C002", LifeEventType.BIRTH, date(2022, 1, 10)))
    pending = log.pending_vulnerability_reviews(since=date(2022, 1, 1))
    assert len(pending) == 1
    assert pending[0].customer_id == "C001"


def test_pending_cot_triggers(log):
    log.record(LifeEvent("C003", LifeEventType.MOVE_OUT, date(2022, 2, 15)))
    log.record(LifeEvent("C004", LifeEventType.JOB_GAIN, date(2022, 2, 20)))
    cots = log.pending_cot_triggers(since=date(2022, 2, 1))
    assert len(cots) == 1
    assert cots[0].customer_id == "C003"


def test_annual_summary(log):
    log.record(LifeEvent("C001", LifeEventType.JOB_LOSS, date(2022, 3, 1)))
    log.record(LifeEvent("C002", LifeEventType.BIRTH, date(2022, 4, 1)))
    log.record(LifeEvent("C003", LifeEventType.MOVE_IN, date(2022, 5, 1)))
    summary = log.annual_summary(2022)
    assert summary["total"] == 3
    assert summary["vulnerability_triggers"] == 1
    assert summary["cot_triggers"] == 1
    assert summary["by_type"]["birth"] == 1


# --- Phase LJ depth tests ---

def test_customer_id_stored():
    e = LifeEvent("CUST_LJ", LifeEventType.JOB_LOSS, date(2022, 1, 1))
    assert e.customer_id == "CUST_LJ"


def test_event_type_stored():
    e = LifeEvent("C1", LifeEventType.RETIREMENT, date(2022, 1, 1))
    assert e.event_type == LifeEventType.RETIREMENT


def test_event_date_stored():
    e = LifeEvent("C1", LifeEventType.BIRTH, date(2022, 5, 15))
    assert e.event_date == date(2022, 5, 15)


def test_notes_default_empty():
    e = LifeEvent("C1", LifeEventType.BIRTH, date(2022, 1, 1))
    assert e.notes == ""


def test_occupancy_delta_default_zero():
    e = LifeEvent("C1", LifeEventType.BIRTH, date(2022, 1, 1))
    assert e.occupancy_delta == 0


def test_death_triggers_vulnerability():
    e = LifeEvent("C1", LifeEventType.DEATH, date(2022, 1, 1))
    assert e.triggers_vulnerability_review is True


def test_move_out_triggers_cot():
    e = LifeEvent("C1", LifeEventType.MOVE_OUT, date(2022, 1, 1))
    assert e.triggers_cot is True


def test_retirement_triggers_psr():
    e = LifeEvent("C1", LifeEventType.RETIREMENT, date(2022, 1, 1))
    assert e.triggers_psr_review is True


def test_pending_psr_reviews(log):
    log.record(LifeEvent("C1", LifeEventType.SERIOUS_ILLNESS, date(2022, 4, 1)))
    log.record(LifeEvent("C2", LifeEventType.JOB_GAIN, date(2022, 4, 5)))
    reviews = log.pending_psr_reviews(since=date(2022, 1, 1))
    assert len(reviews) == 1
    assert reviews[0].customer_id == "C1"


def test_annual_summary_year_key(log):
    log.record(LifeEvent("C1", LifeEventType.BIRTH, date(2022, 3, 1)))
    s = log.annual_summary(2022)
    assert s["year"] == 2022
