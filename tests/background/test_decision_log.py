"""Tests for background/decision_log.py -- MAKE_IT_STICK.md item 3
("the decision log writes itself, hook-written, not discipline-written")."""
import pytest

from background import decision_log
from background.one_way_door import OneWayDoorCategory


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(decision_log, "DECISION_LOG_PATH", tmp_path / "decision_log.jsonl")


def test_decide_on_reversible_action_logs_automatically():
    assert not decision_log.DECISION_LOG_PATH.exists()
    verdict = decision_log.decide(
        "add a new draw tier to the self-refill mechanism",
        why="idle atoms had no DISCOVER/FRAME draw path",
        how_to_reverse="git revert the commit",
    )
    assert verdict.is_one_way_door is False
    entries = decision_log.read_decision_log()
    assert len(entries) == 1
    assert entries[0]["what"] == "add a new draw tier to the self-refill mechanism"
    assert entries[0]["reversible"] is True


def test_decide_on_one_way_door_does_not_log():
    """A one-way door must NOT be silently logged as a proceed-decision --
    the caller is expected to escalate, not act."""
    verdict = decision_log.decide(
        "choose the tournament fitness function",
        why="need to unblock A5",
        explicit_category=OneWayDoorCategory.VALUES_DECISION,
    )
    assert verdict.is_one_way_door is True
    assert decision_log.read_decision_log() == []


def test_decide_uncertain_reversible_proceeds_and_logs():
    """CALIBRATION (ONE_WAY_DOOR_DEFAULTS_TO_ACT.md rule 2): an uncertain-but-reversible
    decision no longer fails closed -- it PROCEEDS and is LOGGED (recorded so it's
    auditable), flagged as an ambiguous-reversible proceed. Overturns the prior
    escalate-and-do-not-log behaviour."""
    verdict = decision_log.decide("do the ambiguous thing", why="unsure", uncertain=True)
    assert verdict.is_one_way_door is False
    assert verdict.ambiguous_reversible_proceed is True
    entries = decision_log.read_decision_log()
    assert len(entries) == 1
    assert entries[0]["confidence"] == "ambiguous_reversible"


def test_decide_uncertain_still_escalates_and_does_not_log_a_provable_wall():
    """The walls stay hard: an uncertain call whose text provably matches a door still
    escalates and is NOT logged as a proceed."""
    verdict = decision_log.decide("make a payment to the vendor", why="unsure", uncertain=True)
    assert verdict.is_one_way_door is True
    assert decision_log.read_decision_log() == []


def test_log_decision_appends_jsonl_not_overwrite():
    decision_log.log_decision("first", "why1", "revert1")
    decision_log.log_decision("second", "why2", "revert2")
    entries = decision_log.read_decision_log()
    assert len(entries) == 2
    assert entries[0]["what"] == "first"
    assert entries[1]["what"] == "second"


def test_read_decision_log_empty_when_file_missing():
    assert decision_log.read_decision_log() == []


def test_read_decision_log_skips_malformed_lines():
    decision_log.DECISION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    decision_log.DECISION_LOG_PATH.write_text('{"what": "good"}\nnot json\n{"what": "also good"}\n')
    entries = decision_log.read_decision_log()
    assert len(entries) == 2


def test_count_since_filters_by_timestamp():
    decision_log.log_decision("old", "w", "r", timestamp="2026-07-01T00:00:00+00:00")
    decision_log.log_decision("new", "w", "r", timestamp="2026-07-12T00:00:00+00:00")
    assert decision_log.count_since("2026-07-10T00:00:00+00:00") == 1
    assert decision_log.count_since("2026-06-01T00:00:00+00:00") == 2
