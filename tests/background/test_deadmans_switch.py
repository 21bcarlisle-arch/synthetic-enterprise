"""Tests for background/deadmans_switch.py -- director-flagged incident,
2026-07-09 (block-escalation didn't reach him for hours; this is deliberately
independent of the tmux/supervisor stack that failed)."""
import time

import pytest

from background import deadmans_switch as dms


def _reset_state():
    dms._last_escalation_ts = None


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(dms, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dms, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(dms, "OBSERVABILITY_DIR", tmp_path / "observability")
    (tmp_path / "staging").mkdir()
    (tmp_path / "observability").mkdir()
    _reset_state()
    yield
    _reset_state()


def test_no_staged_files_is_clean_no_ntfy(monkeypatch):
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert calls == []
    assert "Clean" in dms.LOG_FILE.read_text()


def test_gitkeep_alone_does_not_count_as_staged_work(monkeypatch):
    (dms.STAGING_DIR / ".gitkeep").write_text("")
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert calls == []


def test_staged_work_with_recent_activity_not_blocked(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)  # 1 min ago
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert calls == []
    assert "not blocked" in dms.LOG_FILE.read_text()


def test_staged_work_with_stale_activity_sends_blocked_ntfy(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))  # 2h ago
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[BLOCKED]" in calls[0]
    assert "SOME_DOC.md" in calls[0]


def test_blocked_ntfy_does_not_repeat_within_re_escalate_window(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    dms.run_cycle()
    dms.run_cycle()
    assert len(calls) == 1


def test_blocked_ntfy_re_escalates_after_re_escalate_window(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1

    # Simulate the re-escalation window having elapsed.
    dms._last_escalation_ts = time.time() - dms.RE_ESCALATE_SECONDS - 1
    dms.run_cycle()
    assert len(calls) == 2


def test_recovering_to_clean_resets_escalation_state(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1

    (dms.STAGING_DIR / "SOME_DOC.md").unlink()
    dms.run_cycle()
    assert dms._last_escalation_ts is None


def test_last_commit_epoch_returns_zero_on_git_failure(monkeypatch):
    def _raise(*a, **k):
        raise Exception("no git")
    monkeypatch.setattr(dms.subprocess, "run", _raise)
    assert dms._last_commit_epoch() == 0.0


def test_last_observability_write_epoch_reflects_real_mtimes(monkeypatch):
    f = dms.OBSERVABILITY_DIR / "some-log.md"
    f.write_text("entry")
    epoch = dms._last_observability_write_epoch()
    assert epoch > 0
    assert abs(epoch - time.time()) < 5


def test_last_activity_epoch_takes_the_max_of_both_signals(monkeypatch):
    monkeypatch.setattr(dms, "_last_commit_epoch", lambda: 100.0)
    monkeypatch.setattr(dms, "_last_observability_write_epoch", lambda: 200.0)
    assert dms.last_activity_epoch() == 200.0
    monkeypatch.setattr(dms, "_last_commit_epoch", lambda: 300.0)
    assert dms.last_activity_epoch() == 300.0


def test_blocked_message_names_the_supervisor_stack_explicitly(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert "supervisor" in calls[0].lower()
