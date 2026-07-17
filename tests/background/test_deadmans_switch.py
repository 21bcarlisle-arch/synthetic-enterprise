"""Tests for background/deadmans_switch.py -- director-flagged incident,
2026-07-09 (block-escalation didn't reach him for hours; this is deliberately
independent of the tmux/supervisor stack that failed)."""
import json
import time

import pytest

from background import deadmans_switch as dms
from background import action_needed


def _reset_state():
    # Transition state now lives in the notify() contract, not module globals -- the fixture
    # isolates notify.TRANSITIONS_FILE to a fresh per-test tmp file, so nothing to reset here.
    pass


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(dms, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dms, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(dms, "OBSERVABILITY_DIR", tmp_path / "observability")
    # The deadman delegates transition-only + re-escalate to notify(); isolate its store to a fresh
    # per-test tmp file so each test starts un-escalated and never touches the real (G-T2-protected)
    # .notify_transitions.json. Sends are captured via ntfy_utils.send_ntfy (what notify calls).
    import background.notify as _notify
    monkeypatch.setattr(_notify, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    # Isolated from the real, committed action_needed_register.json --
    # every test starts with a genuinely empty register (2026-07-11).
    monkeypatch.setattr(action_needed, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    # These tests exercise the commit-clock / staging escalation via run_cycle. Isolate the two
    # OTHER run_cycle checks (which read real repo state): the pull-loop transport health and the
    # gate-wall detection -- otherwise a real, unrelated LOOP_BROKEN / GATE_VIOLATION pollutes
    # every send_ntfy assertion here. Each has its own dedicated test file.
    monkeypatch.setattr("background.process_reconciler.evaluate_pull_loop",
                        lambda: {"status": "UNKNOWN", "alarm": False, "detail": "(isolated)"})
    monkeypatch.setattr("background.gate_authorization.evaluate_gate_wall",
                        lambda: {"status": "GATE_CLEAN", "alarm": False, "detail": "(isolated)",
                                 "unauthorized": []})
    (tmp_path / "staging").mkdir()
    (tmp_path / "observability").mkdir()
    _reset_state()
    yield
    _reset_state()


def test_no_staged_files_is_clean_no_ntfy(monkeypatch):
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)  # recent commit
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []
    assert "Clean" in dms.LOG_FILE.read_text()


def test_gitkeep_alone_does_not_count_as_staged_work(monkeypatch):
    (dms.STAGING_DIR / ".gitkeep").write_text("")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)  # recent commit
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []


def test_staged_work_with_recent_activity_not_blocked(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)  # 1 min ago
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []
    assert "not blocked" in dms.LOG_FILE.read_text()


def test_staged_work_with_stale_activity_sends_blocked_ntfy(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))  # 2h ago
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[BLOCKED]" in calls[0]
    assert "SOME_DOC.md" in calls[0]


def test_blocked_ntfy_does_not_repeat_within_re_escalate_window(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    dms.run_cycle()
    dms.run_cycle()
    assert len(calls) == 1


def test_blocked_ntfy_re_escalates_after_re_escalate_window(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1

    # Simulate the re-escalation window having elapsed: age the notify transition store's ts.
    import background.notify as _n
    store = json.loads(_n.TRANSITIONS_FILE.read_text())
    store[dms._COMMIT_KEY]["ts"] = time.time() - dms.RE_ESCALATE_SECONDS - 1
    _n.TRANSITIONS_FILE.write_text(json.dumps(store))
    dms.run_cycle()
    assert len(calls) == 2


def test_recovering_to_clean_resets_escalation_state(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    activity = {"epoch": time.time() - (2 * 3600)}
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: activity["epoch"])
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1

    # Genuine recovery: the queue drains AND a fresh commit lands.
    (dms.STAGING_DIR / "SOME_DOC.md").unlink()
    activity["epoch"] = time.time()
    dms.run_cycle()
    # Recovery re-arms: clear_transition popped the commit key from the notify store.
    import background.notify as _n
    store = json.loads(_n.TRANSITIONS_FILE.read_text()) if _n.TRANSITIONS_FILE.exists() else {}
    assert dms._COMMIT_KEY not in store


def test_recent_commits_returns_empty_on_git_failure(monkeypatch):
    """Fail-closed primitive: an unreadable commit history is NO known progress,
    never assumed-recent activity (R15 fail-closed)."""
    def _raise(*a, **k):
        raise Exception("no git")
    monkeypatch.setattr(dms.subprocess, "run", _raise)
    assert dms._recent_commits() == []
    # ...and that propagates to 0.0 ("looks stale") at the meaningful clock:
    assert dms._last_meaningful_commit_epoch() == 0.0


def test_meaningful_clock_fails_closed_and_trips_blocked_when_git_unreadable(monkeypatch):
    """End-to-end: git unreadable -> meaningful epoch 0.0 -> since_commit ~= now
    -> with queued work the alarm MUST fire. An unavailable check is a FAILED
    check (R15 FAIL-SILENT), never a silent pass."""
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: [])  # git unreadable
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[BLOCKED]" in calls[0]


def test_last_activity_epoch_is_the_meaningful_commit_clock_only(monkeypatch):
    """The 2026-07-14 fixes: progress is the MEANINGFUL git commit clock ALONE
    (no observability-mtime term to contaminate it; no any-commit term for the
    auto-process no-op loop to refresh)."""
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: 12345.0)
    assert dms.last_activity_epoch() == 12345.0
    assert not hasattr(dms, "_last_observability_write_epoch")


def test_is_auto_process_commit_classifier():
    """The flat-no-op discriminator: real auto-process publish subjects are
    excluded; any genuine forward-work subject (including a maturity_map level
    bump) is kept."""
    assert dms._is_auto_process_commit(
        "Auto-process run complete: report + LATEST.md + site/ (git=abc, net=£1,521,070)"
    )
    assert not dms._is_auto_process_commit("[build] deadman_liveness_fix")
    assert not dms._is_auto_process_commit("[build] H12_mutation_test_controls L2->L3")
    assert not dms._is_auto_process_commit("Wave-1 integration: bank F7->L2")


def test_flat_auto_process_commits_do_not_refresh_liveness(monkeypatch):
    """R15 MUTATION TEST -- director-named THEATRE control (2026-07-14). PROVES
    the fixed control FIRES on its own named defect.

    The OLD deadman keyed liveness on ANY git commit, so the auto-process publish
    loop's ~15min flat no-op commits (identical net=£1,521,070, no forward work)
    refreshed the staleness clock and the switch reported 'not blocked' straight
    through the real 83-min executor-idle window (22:03-23:26) -- it NEVER fired.

    Here the ONLY commits inside the last 47min are auto-process run-completes;
    the last MEANINGFUL commit is 50min old and staged work is queued. The alarm
    MUST fire now (50min > 45min BLOCKED threshold). Mutation proof: revert
    last_activity_epoch to keying on the newest commit of ANY kind and this goes
    green->red -- the 2-min-old auto-process no-op would mask the stall exactly
    as it did in production."""
    now = time.time()
    commits = [
        (now - 2 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=aa1, net=£1,521,070)"),
        (now - 17 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=bb2, net=£1,521,070)"),
        (now - 32 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=cc3, net=£1,521,070)"),
        (now - 47 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=dd4, net=£1,521,070)"),
        (now - 50 * 60, "[build] real forward progress landed here"),
    ]
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: commits)
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[BLOCKED]" in calls[0]
    assert "STEER_INSTRUCTION.md" in calls[0]
    # Staleness is measured from the MEANINGFUL commit (50min), NOT the 2-min-old
    # auto-process no-op -- the whole point of the fix.
    assert "50 min" in calls[0]


def test_recent_meaningful_commit_is_not_blocked_despite_auto_process_noise(monkeypatch):
    """The legitimate case -- the fixed control must NOT false-fire. A real
    (non-auto-process) commit landed 5min ago; auto-process no-ops surround it.
    Even with staged work queued, this is healthy: no alarm."""
    now = time.time()
    commits = [
        (now - 3 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=ee5, net=£1,521,070)"),
        (now - 5 * 60, "[build] deadman_liveness_fix"),  # genuine progress, 5min ago
        (now - 20 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=ff6, net=£1,521,070)"),
    ]
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: commits)
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []
    assert "not blocked" in dms.LOG_FILE.read_text()


def test_all_auto_process_window_looks_stale(monkeypatch):
    """A window containing NOTHING but auto-process no-ops has no meaningful
    commit -- the real one is older than the whole window, so the honest answer
    is 0.0 ('very stale'), which trips the alarm rather than masking the wedge."""
    now = time.time()
    commits = [
        (now - i * 60, "Auto-process run complete: report + LATEST.md + site/ (git=x, net=£1,521,070)")
        for i in range(1, 40)
    ]
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: commits)
    assert dms._last_meaningful_commit_epoch() == 0.0


def test_daemon_log_writes_do_not_mask_a_stale_commit(monkeypatch):
    """MUTATION/REGRESSION GUARD for the 2026-07-14 fail-silent outage (R15 --
    the control must fire on its own named defect): the OLD deadman used the
    observability-dir mtime as an 'alive' signal, so its own 15-min log write
    (plus every other daemon's) reset the staleness clock every cycle -- it
    logged 'activity recent (0min ago)' for 6 hours straight while the session
    was wedged and staged files climbed 31->59. Here we reproduce EXACTLY that
    state: a stale commit (6h) with freshly-written daemon logs in the obs dir.
    The alarm MUST fire now; if this test ever goes green->red the fail-silent
    signal has been reintroduced."""
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 6 * 3600)
    # The contaminating writes that masked the stall before:
    (dms.OBSERVABILITY_DIR / "supervisor-log.md").write_text("supervisor just logged")
    (dms.OBSERVABILITY_DIR / "deadmans-switch-log.md").write_text("the switch's own write")
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[BLOCKED]" in calls[0]
    assert "STEER_INSTRUCTION.md" in calls[0]


def test_silent_stall_fires_with_empty_queue(monkeypatch):
    """Backstop tier: a wedged main session with NOTHING queued still trips an
    alarm once no commit has landed for SILENT_STALL_THRESHOLD_SECONDS."""
    assert dms._unprocessed_staging_files() == []  # genuinely empty queue
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 2 * 3600)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[STALL]" in calls[0]


def test_usage_pause_suppresses_the_alarm(monkeypatch):
    """A declared usage pause (.usage_pause.json, future resume_at) is a
    KNOWN-quiet window -- no commit for hours is expected, so both tiers are
    suppressed even with queued work and a very stale commit."""
    from datetime import datetime, timedelta, timezone
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 6 * 3600)
    resume_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    (dms.OBSERVABILITY_DIR / dms.USAGE_PAUSE_FILENAME).write_text(
        json.dumps({"resume_at": resume_at})
    )
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []
    assert "Usage pause active" in dms.LOG_FILE.read_text()


def test_expired_usage_pause_does_not_suppress(monkeypatch):
    """A usage pause whose resume_at has passed is NOT a live pause -- the
    alarm must fire (fails toward alarming, never suppresses on a stale file)."""
    from datetime import datetime, timedelta, timezone
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 6 * 3600)
    past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    (dms.OBSERVABILITY_DIR / dms.USAGE_PAUSE_FILENAME).write_text(
        json.dumps({"resume_at": past})
    )
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[BLOCKED]" in calls[0]


def test_blocked_message_names_the_supervisor_stack_explicitly(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
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
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert calls[0].startswith("[ACTION NEEDED] routines-env-id")
    assert "send the environment_id" in calls[0]


def test_run_cycle_does_not_reping_within_24h(monkeypatch):
    action_needed.register_item("a", "w", "h", "y")  # just registered, now
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []


def test_run_cycle_does_not_reping_resolved_items(monkeypatch):
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item("a", "w", "h", "y", now=asked_at.isoformat())
    action_needed.resolve_item("a", "answered")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
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
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert calls[0].startswith("[ACTION NEEDED] a")


def test_run_cycle_repings_resets_the_daily_clock(monkeypatch):
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item("a", "w", "h", "y", now=asked_at.isoformat())
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1

    dms.run_cycle()  # immediately again -- clock was just reset, must stay silent
    assert len(calls) == 1


def test_run_complete_markers_do_not_count_as_blocked_work(monkeypatch):
    """R3 completeness (2026-07-14, director: 'run_complete markers are STILL
    landing in docs/staging -- the R3 exclusion is incomplete'): a pile of
    auto-process markers is NOT a director-instruction backlog, so it must never
    raise [BLOCKED] on its own. With a recent commit and only markers queued, the
    deadman stays silent -- the pile is processing lag, surfaced by the commit
    clock ([STALL]) only if it ever means genuine inactivity, never a false
    [BLOCKED]."""
    for i in range(30):
        (dms.STAGING_DIR / f"run_complete_2026071{i:02d}.md").write_text("marker")
    assert dms._unprocessed_staging_files() == []  # markers excluded from queued work
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 60)  # recent commit
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []  # 30 markers + recent commit -> no alarm


def test_run_complete_pile_with_stale_commit_still_stalls(monkeypatch):
    """But markers do NOT blind the backstop: if the commit clock is genuinely
    stale, [STALL] still fires even though the only things 'queued' are markers
    (this is the exact blackout shape -- markers piling while nothing commits)."""
    for i in range(30):
        (dms.STAGING_DIR / f"run_complete_2026071{i:02d}.md").write_text("marker")
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 2 * 3600)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[STALL]" in calls[0]
