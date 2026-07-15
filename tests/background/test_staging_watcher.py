import time
from datetime import datetime, timedelta, timezone

from background import staging_watcher as watcher


def _reset_pending_wake():
    watcher._pending_wake_names.clear()
    watcher._pending_wake_first_attempt.clear()


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


# ── Bounded retry (2026-07-10, docs/design/STAGING_WATCHER_WAKE_CONFIRMATION_BUG.md) ──

def test_attempt_pending_wake_records_first_attempt_time(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    (tmp_path / "A.md").write_text("x")
    watcher._pending_wake_names.update({"A.md"})
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: False)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    watcher._attempt_pending_wake()

    assert "A.md" in watcher._pending_wake_first_attempt


def test_attempt_pending_wake_gives_up_after_timeout(tmp_path, monkeypatch):
    """The known tmux_relay consumption-check bug means a genuinely-delivered
    wake can never be confirmed -- must stop retrying after
    _WAKE_GIVE_UP_SECONDS rather than hammering the session forever."""
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    (tmp_path / "A.md").write_text("x")
    watcher._pending_wake_names.update({"A.md"})
    watcher._pending_wake_first_attempt["A.md"] = time.monotonic() - 700.0  # older than the 600s bound
    calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: calls.append(names) or False)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    watcher._attempt_pending_wake()

    assert calls == []  # gave up before even attempting the relay call
    assert watcher._pending_wake_names == set()
    assert "A.md" not in watcher._pending_wake_first_attempt


def test_attempt_pending_wake_does_not_give_up_before_timeout(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    (tmp_path / "A.md").write_text("x")
    watcher._pending_wake_names.update({"A.md"})
    watcher._pending_wake_first_attempt["A.md"] = time.monotonic() - 30.0  # well within the 600s bound
    calls = []
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: calls.append(names) or False)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    watcher._attempt_pending_wake()

    assert calls == [["A.md"]]  # still attempted the relay call
    assert watcher._pending_wake_names == {"A.md"}


def test_attempt_pending_wake_clearing_on_success_also_clears_first_attempt(tmp_path, monkeypatch):
    _reset_pending_wake()
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    (tmp_path / "A.md").write_text("x")
    watcher._pending_wake_names.update({"A.md"})
    monkeypatch.setattr(watcher, "_relay_wake_to_claude", lambda names: True)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    watcher._attempt_pending_wake()

    assert "A.md" not in watcher._pending_wake_first_attempt


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


# ── Archive-on-answer (2026-07-14, director triage #3: "archive-on-answer never landed") ──
#
# A stale from_rich ("Are you busy?") re-jammed the director's box TWICE because
# answered messages were never moved to done/. The mechanism is a sweep this
# daemon runs; it must archive answered/superseded/stale messages and NEVER
# touch a fresh, unanswered one (or the live director question loses its turn).

def _from_rich_name(dt: datetime) -> str:
    return f"from_rich_{dt.strftime('%Y%m%d_%H%M%S')}.md"


def test_from_rich_timestamp_parses_canonical_name(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    p = tmp_path / "from_rich_20260714_083015.md"
    p.write_text("msg")
    assert watcher._from_rich_timestamp(p) == datetime(2026, 7, 14, 8, 30, 15, tzinfo=timezone.utc)


def test_from_rich_timestamp_falls_back_to_mtime_on_bad_name(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    p = tmp_path / "from_rich_not_a_timestamp.md"
    p.write_text("msg")
    ts = watcher._from_rich_timestamp(p)
    # falls back to mtime (roughly now) rather than raising
    assert abs((datetime.now(timezone.utc) - ts).total_seconds()) < 120


def test_archive_from_rich_moves_to_done(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)
    p = tmp_path / "from_rich_20260714_000000.md"
    p.write_text("are you busy?")

    assert watcher.archive_from_rich(p) is True
    assert not p.exists()
    dest = tmp_path / "done" / "from_rich_20260714_000000.md"
    assert dest.exists()
    assert dest.read_text() == "are you busy?"  # content preserved, never lost


def test_archive_from_rich_is_idempotent_when_already_gone(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)
    p = tmp_path / "from_rich_20260714_000000.md"  # never created
    assert watcher.archive_from_rich(p) is True  # no-op success, no crash


def test_archive_from_rich_preserves_differing_content_on_name_collision(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)
    done = tmp_path / "done"
    done.mkdir()
    (done / "from_rich_20260714_000000.md").write_text("ORIGINAL in done/")
    p = tmp_path / "from_rich_20260714_000000.md"
    p.write_text("DIFFERENT content, must not be lost")

    assert watcher.archive_from_rich(p) is True
    assert not p.exists()
    # original preserved AND the differing copy preserved under a suffix
    assert (done / "from_rich_20260714_000000.md").read_text() == "ORIGINAL in done/"
    dups = list(done.glob("from_rich_20260714_000000.dup*.md"))
    assert len(dups) == 1
    assert dups[0].read_text() == "DIFFERENT content, must not be lost"


# ── R15 MUTATION TEST: the control must FAIL on its own named defect ──
# Named defect: an answered/superseded from_rich stays in the scanned root and
# keeps re-granting supervisor turns. This test asserts BOTH directions in one
# place so mutating the mechanism is caught either way:
#   * remove/loosen the archive → the superseded assertion fails (it stays put)
#   * broaden to archive everything → the fresh-file assertion fails (it's gone)
def test_sweep_archives_superseded_but_not_fresh_unanswered(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    now = datetime(2026, 7, 15, 12, 0, 5, tzinfo=timezone.utc)
    # An old, answered-but-never-archived ping, superseded by a newer message.
    old = tmp_path / _from_rich_name(datetime(2026, 7, 14, 0, 0, 0, tzinfo=timezone.utc))
    old.write_text("are you busy?")
    # The FRESH, live director message (newest, seconds old) -- must be kept.
    fresh = tmp_path / _from_rich_name(datetime(2026, 7, 15, 12, 0, 0, tzinfo=timezone.utc))
    fresh.write_text("start the next phase please")

    archived = watcher.sweep_answered_from_rich(now=now)

    # superseded stale ping IS archived to done/ ...
    assert old.name in archived
    assert not old.exists()
    assert (tmp_path / "done" / old.name).exists()
    # ... and the fresh, unanswered, live message is NOT touched.
    assert fresh.name not in archived
    assert fresh.exists()
    assert not (tmp_path / "done" / fresh.name).exists()


def test_sweep_leaves_lone_fresh_unanswered_from_rich(tmp_path, monkeypatch):
    """A single fresh message with no newer engagement must never be swept --
    it is the live question and still needs its turn-grant."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    now = datetime(2026, 7, 15, 12, 0, 30, tzinfo=timezone.utc)
    fresh = tmp_path / _from_rich_name(datetime(2026, 7, 15, 12, 0, 0, tzinfo=timezone.utc))
    fresh.write_text("real instruction that must survive")

    assert watcher.sweep_answered_from_rich(now=now) == []
    assert fresh.exists()


def test_sweep_archives_lone_stale_from_rich_backstop(tmp_path, monkeypatch):
    """The last/only lingering message that no newer engagement will supersede
    must still stop re-granting turns once it is past the absolute backstop."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    old_dt = datetime(2026, 7, 14, 0, 0, 0, tzinfo=timezone.utc)
    now = old_dt + timedelta(seconds=watcher.FROM_RICH_STALE_SECONDS + 60)
    lone = tmp_path / _from_rich_name(old_dt)
    lone.write_text("answered days ago, never archived")

    archived = watcher.sweep_answered_from_rich(now=now)
    assert lone.name in archived
    assert (tmp_path / "done" / lone.name).exists()


def test_sweep_does_not_tear_apart_a_recent_burst(tmp_path, monkeypatch):
    """Two messages that are part of ONE multi-part instruction, sent within
    minutes of each other, must both be kept -- supersession only sweeps once
    the older one is past FROM_RICH_SUPERSEDE_MIN_AGE_SECONDS."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    first_dt = datetime(2026, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
    second_dt = first_dt + timedelta(minutes=2)  # a burst, both recent
    now = second_dt + timedelta(seconds=10)
    first = tmp_path / _from_rich_name(first_dt)
    first.write_text("part 1 of a multi-part instruction")
    second = tmp_path / _from_rich_name(second_dt)
    second.write_text("part 2, please do both")

    assert watcher.sweep_answered_from_rich(now=now) == []
    assert first.exists() and second.exists()


def test_sweep_noop_on_empty_or_missing_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)
    assert watcher.sweep_answered_from_rich() == []
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path / "does-not-exist")
    assert watcher.sweep_answered_from_rich() == []


def test_sweep_ignores_non_from_rich_files(tmp_path, monkeypatch):
    """The sweep is scoped to from_rich_*.md only -- a real staged directive or
    a run_complete marker must never be moved by it."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)

    now = datetime(2026, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
    directive = tmp_path / "SOME_DIRECTIVE.md"
    directive.write_text("a real instruction from months ago")
    import os
    old_epoch = (now - timedelta(days=10)).timestamp()
    os.utime(directive, (old_epoch, old_epoch))

    assert watcher.sweep_answered_from_rich(now=now) == []
    assert directive.exists()
