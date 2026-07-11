"""Tests for background/deadmans_switch.py -- director-flagged incident,
2026-07-09 (block-escalation didn't reach him for hours; this is deliberately
independent of the tmux/supervisor stack that failed)."""
import time

import pytest

from background import deadmans_switch as dms
from background import action_needed


def _reset_state():
    dms._last_escalation_ts = None


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(dms, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dms, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(dms, "OBSERVABILITY_DIR", tmp_path / "observability")
    # Isolated from the real, committed action_needed_register.json --
    # every test starts with a genuinely empty register (2026-07-11).
    monkeypatch.setattr(action_needed, "REGISTER_PATH", tmp_path / "action_needed_register.json")
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


# --- 2026-07-11: daily re-ping of open [ACTION NEEDED] items (director rule) ---

def test_run_cycle_repings_a_due_action_needed_item(monkeypatch):
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item(
        "routines-env-id", "send the environment_id", "via claude.ai/code",
        "RemoteTrigger needs it", now=asked_at.isoformat(),
    )
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert calls[0].startswith("[ACTION NEEDED] routines-env-id")
    assert "send the environment_id" in calls[0]


def test_run_cycle_does_not_reping_within_24h(monkeypatch):
    action_needed.register_item("a", "w", "h", "y")  # just registered, now
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert calls == []


def test_run_cycle_does_not_reping_resolved_items(monkeypatch):
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item("a", "w", "h", "y", now=asked_at.isoformat())
    action_needed.resolve_item("a")
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert calls == []


def test_run_cycle_reping_is_independent_of_staging_activity_check(monkeypatch):
    """An action-needed re-ping must fire even when staging is completely
    clean -- it is not gated on the [BLOCKED]-class staging/activity check
    at all (a genuinely different alert class, see the module docstring)."""
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item("a", "w", "h", "y", now=asked_at.isoformat())
    assert dms._unprocessed_staging_files() == []  # staging genuinely clean
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert calls[0].startswith("[ACTION NEEDED] a")


def test_run_cycle_repings_resets_the_daily_clock(monkeypatch):
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item("a", "w", "h", "y", now=asked_at.isoformat())
    calls = []
    monkeypatch.setattr(dms, "send_ntfy", lambda msg: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1

    dms.run_cycle()  # immediately again -- clock was just reset, must stay silent
    assert len(calls) == 1
