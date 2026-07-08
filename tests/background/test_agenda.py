"""Tests for background/agenda.py -- the open-agenda continuation marker
(docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md, Deliverable 1a)."""
from background import agenda


def _patch_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(agenda, "AGENDA_FILE", tmp_path / "agenda.json")
    monkeypatch.setattr(agenda, "NUDGE_STATE_FILE", tmp_path / "nudge.json")


def test_load_agenda_none_when_absent(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    assert agenda.load_agenda() is None


def test_set_and_load_agenda(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    agenda.set_agenda("Phase 3", "item 2", "wire credit_refund.py")
    loaded = agenda.load_agenda()
    assert loaded["phase"] == "Phase 3"
    assert loaded["step"] == "item 2"
    assert loaded["next_action"] == "wire credit_refund.py"
    assert "updated_at" in loaded


def test_clear_agenda_removes_file(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    agenda.set_agenda("Phase 3", "item 2", "wire credit_refund.py")
    agenda.clear_agenda()
    assert agenda.load_agenda() is None


def test_clear_agenda_safe_when_nothing_to_clear(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    agenda.clear_agenda()  # must not raise


def test_is_stale_enough_to_nudge_false_when_fresh():
    fresh = {"updated_at": 1000.0}
    assert agenda.is_stale_enough_to_nudge(fresh, now=1000.0 + 60) is False


def test_is_stale_enough_to_nudge_true_when_old():
    old = {"updated_at": 1000.0}
    assert agenda.is_stale_enough_to_nudge(old, now=1000.0 + agenda.IDLE_THRESHOLD_SECONDS) is True


def test_should_nudge_none_when_no_agenda(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    assert agenda.should_nudge() is None


def test_should_nudge_none_when_fresh(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    agenda.set_agenda("Phase 3", "item 1", "build meter reads")
    assert agenda.should_nudge(now=time_now_plus(agenda, 10)) is None


def test_should_nudge_true_when_stale(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    agenda.set_agenda("Phase 3", "item 1", "build meter reads")
    result = agenda.should_nudge(now=time_now_plus(agenda, agenda.IDLE_THRESHOLD_SECONDS + 1))
    assert result is not None
    assert result["phase"] == "Phase 3"


def test_should_nudge_only_once_per_agenda_snapshot(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    agenda.set_agenda("Phase 3", "item 1", "build meter reads")
    later = time_now_plus(agenda, agenda.IDLE_THRESHOLD_SECONDS + 1)
    first = agenda.should_nudge(now=later)
    assert first is not None
    agenda.record_nudged(first)
    # Same agenda snapshot, still stale -- must not nudge again (R5: never
    # repeat an unchanged status).
    second = agenda.should_nudge(now=later + 100)
    assert second is None


def test_should_nudge_again_after_agenda_advances(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    agenda.set_agenda("Phase 3", "item 1", "build meter reads")
    later = time_now_plus(agenda, agenda.IDLE_THRESHOLD_SECONDS + 1)
    first = agenda.should_nudge(now=later)
    agenda.record_nudged(first)

    # Session wakes, advances the agenda to a new step -- proves it's alive
    # and working, resets eligibility.
    agenda.set_agenda("Phase 3", "item 2", "wire credit_refund.py")
    even_later = time_now_plus(agenda, agenda.IDLE_THRESHOLD_SECONDS + 1)
    second = agenda.should_nudge(now=even_later)
    assert second is not None
    assert second["step"] == "item 2"


def time_now_plus(agenda_module, offset):
    loaded = agenda_module.load_agenda()
    return loaded["updated_at"] + offset
