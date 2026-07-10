from background import staging_watcher as watcher


def _reset_pending_wake():
    watcher._pending_wake_names.clear()


# ── Event-driven wake (director directive, in-conversation, 2026-07-08): tmux wake on genuinely new staged files ──

def test_check_once_queues_wake_for_new_actionable_file(tmp_path, monkeypatch):
    """A genuinely new staged instruction must both NTFY and queue a wake
    (the actual send attempt happens in main()'s loop via
    _attempt_pending_wake(), so it can retry across cycles)."""
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    (tmp_path / "CORE_FIDELITY_BEFORE_LOOPS.md").write_text("director reorientation")
    watcher.check_once(set())

    assert watcher._pending_wake_names == {"CORE_FIDELITY_BEFORE_LOOPS.md"}


def test_check_once_does_not_wake_for_from_rich_files(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    (tmp_path / "from_rich_20260708_120000.md").write_text("a message")
    watcher.check_once(set())

    assert watcher._pending_wake_names == set()


def test_check_once_does_not_wake_for_run_complete_markers(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    (tmp_path / "run_complete_20260708T120000Z.md").write_text("sim run done")
    watcher.check_once(set())

    assert watcher._pending_wake_names == set()


def test_check_once_does_not_wake_when_nothing_new(tmp_path, monkeypatch):
    """Zero turns when nothing happens: a poll with no new files must never wake."""
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    (tmp_path / "OLD.md").write_text("already seen")
    watcher.check_once({"OLD.md"})

    assert watcher._pending_wake_names == set()


def test_check_once_batches_multiple_new_files_into_one_pending_set(tmp_path, monkeypatch):
    """Multiple simultaneous new files (e.g. a multi-file ADVISOR-STAGED
    commit) must all queue into the same pending wake, delivered as one
    batched relay call by _attempt_pending_wake()."""
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    (tmp_path / "A.md").write_text("a")
    (tmp_path / "B.md").write_text("b")
    watcher.check_once(set())

    assert watcher._pending_wake_names == {"A.md", "B.md"}


def test_check_once_mixed_batch_only_queues_actionable_names(tmp_path, monkeypatch):
    """A batch containing both actionable and silent-class files must only
    queue the actionable ones for wake."""
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    (tmp_path / "REAL_DIRECTIVE.md").write_text("real")
    (tmp_path / "from_rich_20260708_130000.md").write_text("msg")
    (tmp_path / "run_complete_20260708T130000Z.md").write_text("done")
    watcher.check_once(set())

    assert watcher._pending_wake_names == {"REAL_DIRECTIVE.md"}


def test_relay_wake_to_claude_calls_send_keys_when_idle(monkeypatch):
    """Verify the actual relay call shape via the shared, idle-gated,
    verified background.tmux_relay.send_keys_when_idle() helper (root-cause
    fix, 2026-07-08: plain send_keys() could land text in a busy pane that
    never submits)."""
    calls = []
    monkeypatch.setattr(
        watcher, "send_keys_when_idle",
        lambda session, text, marker: calls.append((session, text, marker)) or True,
    )

    result = watcher._relay_wake_to_claude(["CORE_FIDELITY_BEFORE_LOOPS.md"])

    assert result is True
    assert len(calls) == 1
    session, text, marker = calls[0]
    assert session == watcher.SESSION_NAME
    assert "CORE_FIDELITY_BEFORE_LOOPS.md" in text
    assert marker  # a non-empty verification marker was derived


def test_relay_wake_to_claude_never_includes_file_contents(monkeypatch):
    """This watcher must never leak staged file contents into the injected
    prompt -- names only, per its own standing discipline."""
    calls = []
    monkeypatch.setattr(
        watcher, "send_keys_when_idle",
        lambda session, text, marker: calls.append((session, text, marker)) or True,
    )

    watcher._relay_wake_to_claude(["SECRET_PLAN.md"])

    injected_text = calls[0][1]
    assert "SECRET_PLAN.md" in injected_text
    # Only the filename should appear -- verify no other staging-dir file
    # content could have leaked by checking the message is short and
    # templated, not an arbitrary content dump.
    assert len(injected_text) < 500


def test_relay_wake_to_claude_returns_false_when_send_fails(monkeypatch):
    """Session busy / unconfirmed delivery -- must propagate False, not
    silently succeed, so the caller retries next cycle."""
    monkeypatch.setattr(watcher, "send_keys_when_idle", lambda session, text, marker: False)

    assert watcher._relay_wake_to_claude(["X.md"]) is False


def test_relay_wake_to_claude_swallows_tmux_errors(monkeypatch):
    """Defense in depth: even if send_keys_when_idle() itself somehow raised
    (a regression, or a test double that doesn't replicate its own
    guarantee), _relay_wake_to_claude has its own try/except so the
    watcher's poll loop is still protected."""
    def _raise(*a, **k):
        raise Exception("tmux: no such session")
    monkeypatch.setattr(watcher, "send_keys_when_idle", _raise)

    assert watcher._relay_wake_to_claude(["X.md"]) is False  # must not raise


# ── Pending-wake retry (root-cause fix, docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md, 2026-07-08) ──

def test_attempt_pending_wake_noop_when_nothing_queued(monkeypatch):
    _reset_pending_wake()
    calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: calls.append(names) or True)
    watcher._attempt_pending_wake()
    assert calls == []


def test_attempt_pending_wake_clears_on_success(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    (tmp_path / "A.md").write_text("x")
    (tmp_path / "B.md").write_text("x")
    watcher._pending_wake_names.update({"A.md", "B.md"})
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: True)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    watcher._attempt_pending_wake()

    assert watcher._pending_wake_names == set()


def test_attempt_pending_wake_retains_on_failure(tmp_path, monkeypatch):
    """Session busy -- must stay queued for the next cycle's retry, never
    silently dropped."""
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    (tmp_path / "A.md").write_text("x")
    watcher._pending_wake_names.update({"A.md"})
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: False)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    watcher._attempt_pending_wake()

    assert watcher._pending_wake_names == {"A.md"}


def test_attempt_pending_wake_passes_sorted_names(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    (tmp_path / "A.md").write_text("x")
    (tmp_path / "B.md").write_text("x")
    watcher._pending_wake_names.update({"B.md", "A.md"})
    calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: calls.append(names) or True)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    watcher._attempt_pending_wake()

    assert calls == [["A.md", "B.md"]]


def test_attempt_pending_wake_drops_stale_name_already_archived(tmp_path, monkeypatch):
    """Doorbell failure #6: a name whose file was archived to done/ while the
    session was continuously busy (never once seen idle) must be dropped as
    moot instead of retried forever -- 140+ live retries observed for one
    already-actioned file before this fix."""
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    (tmp_path / "STILL_STAGED.md").write_text("x")
    watcher._pending_wake_names.update({"ALREADY_ARCHIVED.md", "STILL_STAGED.md"})
    calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: calls.append(names) or False)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    watcher._attempt_pending_wake()

    assert calls == [["STILL_STAGED.md"]]
    assert watcher._pending_wake_names == {"STILL_STAGED.md"}


def test_attempt_pending_wake_all_stale_clears_without_relay_call(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    watcher._pending_wake_names.update({"ALREADY_ARCHIVED.md"})
    calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: calls.append(names) or True)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    watcher._attempt_pending_wake()

    assert calls == []
    assert watcher._pending_wake_names == set()


# Open-agenda continuation nudge (Deliverable 1a,
# docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md) retired 2026-07-09
# (doorbell failure #4, R3 architecture rebuild) -- see
# background/agenda.py's module docstring and test_agenda.py's
# test_nudge_once_mechanism_is_retired for the guard against reintroducing
# it. background/supervisor.py is the sole turn-granting authority now.


def test_current_files_ignores_dirs_and_gitkeep(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    (tmp_path / ".gitkeep").write_text("")
    (tmp_path / "TASK_A.md").write_text("hello")
    (tmp_path / "subdir").mkdir()

    assert watcher.current_files() == {"TASK_A.md"}


def test_current_files_missing_dir_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path / "does-not-exist")

    assert watcher.current_files() == set()


def test_save_and_load_seen_roundtrip(tmp_path, monkeypatch):
    state_file = tmp_path / "seen.json"
    monkeypatch.setattr(watcher, "STATE_FILE", state_file)

    watcher.save_seen({"TASK_A.md", "TASK_B.md"})

    assert watcher.load_seen() == {"TASK_A.md", "TASK_B.md"}


def test_load_seen_missing_file_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "missing.json")

    assert watcher.load_seen() is None


def test_check_once_notifies_only_for_new_files(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")

    (tmp_path / "TASK_OLD.md").write_text("old")

    ntfy_messages = []
    monkeypatch.setattr(watcher, "ntfy", lambda msg: ntfy_messages.append(msg))

    seen = {"TASK_OLD.md"}
    seen = watcher.check_once(seen)
    assert ntfy_messages == []

    (tmp_path / "TASK_NEW.md").write_text("new content the watcher must not act on")
    seen = watcher.check_once(seen)

    assert len(ntfy_messages) == 1
    assert "TASK_NEW.md" in ntfy_messages[0]
    # the watcher only ever announces filenames — never staged file contents
    assert "must not act on" not in ntfy_messages[0]
    assert seen == {"TASK_OLD.md", "TASK_NEW.md"}


def test_check_once_persists_seen_state(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    state_file = tmp_path / "seen.json"
    monkeypatch.setattr(watcher, "STATE_FILE", state_file)
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    (tmp_path / "TASK_NEW.md").write_text("new")
    watcher.check_once(set())

    assert watcher.load_seen() == {"TASK_NEW.md"}


def test_current_files_finds_md_files(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    (tmp_path / "from_rich_001.md").write_text("hello")
    (tmp_path / "run_complete_001.md").write_text("done")

    result = watcher.current_files()
    assert "from_rich_001.md" in result
    assert "run_complete_001.md" in result


def test_save_seen_overwrites_previous(tmp_path, monkeypatch):
    state_file = tmp_path / "seen.json"
    monkeypatch.setattr(watcher, "STATE_FILE", state_file)

    watcher.save_seen({"OLD.md"})
    watcher.save_seen({"NEW.md"})

    assert watcher.load_seen() == {"NEW.md"}


def test_check_once_notifies_for_multiple_new_files(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    (tmp_path / "A.md").write_text("a")
    (tmp_path / "B.md").write_text("b")

    ntfy_messages = []
    monkeypatch.setattr(watcher, "ntfy", lambda msg: ntfy_messages.append(msg))

    watcher.check_once(set())

    assert len(ntfy_messages) == 2


def test_check_once_with_empty_staging_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    seen = watcher.check_once(set())
    assert seen == set()


def test_current_files_returns_set(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    result = watcher.current_files()
    assert isinstance(result, set)


def test_save_and_reload_multiple_files(tmp_path, monkeypatch):
    state_file = tmp_path / "seen.json"
    monkeypatch.setattr(watcher, "STATE_FILE", state_file)
    files = {"A.md", "B.md", "C.md", "D.md"}
    watcher.save_seen(files)
    assert watcher.load_seen() == files


def test_check_once_returns_updated_seen(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    (tmp_path / "NEW.md").write_text("content")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)
    result = watcher.check_once(set())
    assert isinstance(result, set)
    assert "NEW.md" in result


def test_check_monthly_maintenance_queues_marker_on_first_of_month(tmp_path, monkeypatch):
    from datetime import datetime, timezone

    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "MAINTENANCE_STATE_FILE", tmp_path / "maint_state.json")

    watcher.check_monthly_maintenance(datetime(2026, 8, 1, tzinfo=timezone.utc))

    marker = tmp_path / "maintenance_due_202608.md"
    assert marker.exists()
    assert "2026-08" in marker.read_text()
    assert watcher._load_maintenance_state() == "2026-08"


def test_check_monthly_maintenance_skips_non_first_day(tmp_path, monkeypatch):
    from datetime import datetime, timezone

    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "MAINTENANCE_STATE_FILE", tmp_path / "maint_state.json")

    watcher.check_monthly_maintenance(datetime(2026, 8, 15, tzinfo=timezone.utc))

    assert not any(tmp_path.glob("maintenance_due_*.md"))


def test_check_monthly_maintenance_is_idempotent_within_month(tmp_path, monkeypatch):
    from datetime import datetime, timezone

    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "MAINTENANCE_STATE_FILE", tmp_path / "maint_state.json")

    watcher.check_monthly_maintenance(datetime(2026, 9, 1, tzinfo=timezone.utc))
    marker = tmp_path / "maintenance_due_202609.md"
    marker.write_text("edited by hand, should not be clobbered")

    watcher.check_monthly_maintenance(datetime(2026, 9, 1, tzinfo=timezone.utc))

    assert marker.read_text() == "edited by hand, should not be clobbered"


def test_check_monthly_maintenance_fires_again_next_month(tmp_path, monkeypatch):
    from datetime import datetime, timezone

    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "MAINTENANCE_STATE_FILE", tmp_path / "maint_state.json")

    watcher.check_monthly_maintenance(datetime(2026, 8, 1, tzinfo=timezone.utc))
    watcher.check_monthly_maintenance(datetime(2026, 9, 1, tzinfo=timezone.utc))

    assert (tmp_path / "maintenance_due_202608.md").exists()
    assert (tmp_path / "maintenance_due_202609.md").exists()


def test_monthly_maintenance_marker_gets_notified_via_check_once(tmp_path, monkeypatch):
    from datetime import datetime, timezone

    _reset_pending_wake()
    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    side_dir = tmp_path / "side"
    side_dir.mkdir()

    monkeypatch.setattr(watcher, "STAGING_DIR", staging_dir)
    monkeypatch.setattr(watcher, "STATE_FILE", side_dir / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", side_dir / "log.md")
    monkeypatch.setattr(watcher, "MAINTENANCE_STATE_FILE", side_dir / "maint_state.json")

    ntfy_messages = []
    monkeypatch.setattr(watcher, "ntfy", lambda msg: ntfy_messages.append(msg))

    watcher.check_monthly_maintenance(datetime(2026, 10, 1, tzinfo=timezone.utc))
    watcher.check_once(set())

    assert len(ntfy_messages) == 1
    assert "maintenance_due_202610.md" in ntfy_messages[0]
