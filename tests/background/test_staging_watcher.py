from background import staging_watcher as watcher


# ── EVENT_DRIVEN_WAKE.md (2026-07-08): tmux wake on genuinely new staged files ──

def test_check_once_wakes_claude_for_new_actionable_file(tmp_path, monkeypatch):
    """A genuinely new staged instruction must both NTFY and inject a wake."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    wake_calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: wake_calls.append(names))

    (tmp_path / "CORE_FIDELITY_BEFORE_LOOPS.md").write_text("director reorientation")
    watcher.check_once(set())

    assert wake_calls == [["CORE_FIDELITY_BEFORE_LOOPS.md"]]


def test_check_once_does_not_wake_for_from_rich_files(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    wake_calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: wake_calls.append(names))

    (tmp_path / "from_rich_20260708_120000.md").write_text("a message")
    watcher.check_once(set())

    assert wake_calls == []


def test_check_once_does_not_wake_for_run_complete_markers(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    wake_calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: wake_calls.append(names))

    (tmp_path / "run_complete_20260708T120000Z.md").write_text("sim run done")
    watcher.check_once(set())

    assert wake_calls == []


def test_check_once_does_not_wake_when_nothing_new(tmp_path, monkeypatch):
    """Zero turns when nothing happens: a poll with no new files must never wake."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    wake_calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: wake_calls.append(names))

    (tmp_path / "OLD.md").write_text("already seen")
    watcher.check_once({"OLD.md"})

    assert wake_calls == []


def test_check_once_batches_multiple_new_files_into_one_wake(tmp_path, monkeypatch):
    """Multiple simultaneous new files (e.g. a multi-file ADVISOR-STAGED
    commit) must trigger exactly one relay call, not one per file."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    wake_calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: wake_calls.append(names))

    (tmp_path / "A.md").write_text("a")
    (tmp_path / "B.md").write_text("b")
    watcher.check_once(set())

    assert len(wake_calls) == 1
    assert sorted(wake_calls[0]) == ["A.md", "B.md"]


def test_check_once_mixed_batch_only_wakes_for_actionable_names(tmp_path, monkeypatch):
    """A batch containing both actionable and silent-class files must only
    name the actionable ones in the wake."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(watcher, "ntfy", lambda msg: None)

    wake_calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: wake_calls.append(names))

    (tmp_path / "REAL_DIRECTIVE.md").write_text("real")
    (tmp_path / "from_rich_20260708_130000.md").write_text("msg")
    (tmp_path / "run_complete_20260708T130000Z.md").write_text("done")
    watcher.check_once(set())

    assert wake_calls == [["REAL_DIRECTIVE.md"]]


def test_relay_wake_to_claude_calls_tmux_send_keys(monkeypatch):
    """Verify the actual tmux invocation shape, not just that _relay_wake_to_claude
    was called -- this is the one function the mocked tests above never exercise."""
    calls = []
    monkeypatch.setattr(
        watcher.subprocess, "run",
        lambda cmd, **kw: calls.append(cmd) or type("R", (), {"returncode": 0})(),
    )

    watcher._relay_wake_to_claude(["CORE_FIDELITY_BEFORE_LOOPS.md"])

    assert len(calls) == 1
    cmd = calls[0]
    assert cmd[:4] == ["tmux", "send-keys", "-t", watcher.SESSION_NAME]
    assert "CORE_FIDELITY_BEFORE_LOOPS.md" in cmd[4]
    assert cmd[-1] == "Enter"


def test_relay_wake_to_claude_never_includes_file_contents(monkeypatch):
    """This watcher must never leak staged file contents into the injected
    prompt -- names only, per its own standing discipline."""
    calls = []
    monkeypatch.setattr(
        watcher.subprocess, "run",
        lambda cmd, **kw: calls.append(cmd) or type("R", (), {"returncode": 0})(),
    )

    watcher._relay_wake_to_claude(["SECRET_PLAN.md"])

    injected_text = calls[0][4]
    assert "SECRET_PLAN.md" in injected_text
    # Only the filename should appear -- verify no other staging-dir file
    # content could have leaked by checking the message is short and
    # templated, not an arbitrary content dump.
    assert len(injected_text) < 500


def test_relay_wake_to_claude_swallows_tmux_errors(monkeypatch):
    """A dead/missing tmux session must never crash the watcher's poll loop."""
    def _raise(*a, **k):
        raise Exception("tmux: no such session")
    monkeypatch.setattr(watcher.subprocess, "run", _raise)

    watcher._relay_wake_to_claude(["X.md"])  # must not raise


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
