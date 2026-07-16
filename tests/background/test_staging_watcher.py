import time
from datetime import datetime, timedelta, timezone

import pytest

from background import staging_watcher as watcher


@pytest.fixture(autouse=True)
def _isolate_action_needed_register(tmp_path, monkeypatch):
    # check_once/archive now gate through the shared fire-once register; isolate it
    # per test so notification counts are deterministic and never leak live state.
    monkeypatch.setattr("background.action_needed.REGISTER_PATH", tmp_path / "an_register.json")


def _reset_pending_wake():
    # PULL-LOOP MIGRATION (2026-07-15): the tmux wake path is deleted; this
    # is a no-op kept so the many callers that reset state still work.
    return


def _capture_ntfy(monkeypatch):
    calls = []
    monkeypatch.setattr(watcher, "ntfy", lambda msg: calls.append(msg))
    return calls


# ── check_once NOTIFIES on genuinely-new actionable files (no pane wake) ──

def test_check_once_notifies_for_new_actionable_file(tmp_path, monkeypatch):
    """A genuinely new staged instruction must NTFY Rich (the session draws it
    via staging + the pull-loop; there is no tmux wake anymore)."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    calls = _capture_ntfy(monkeypatch)

    (tmp_path / "CORE_FIDELITY_BEFORE_LOOPS.md").write_text("director reorientation")
    watcher.check_once(set())

    assert any("CORE_FIDELITY_BEFORE_LOOPS.md" in m for m in calls)


def test_check_once_does_not_notify_for_from_rich_files(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    calls = _capture_ntfy(monkeypatch)

    (tmp_path / "from_rich_20260708_120000.md").write_text("a message")
    watcher.check_once(set())

    assert calls == []


def test_check_once_does_not_notify_for_run_complete_markers(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    calls = _capture_ntfy(monkeypatch)

    (tmp_path / "run_complete_20260708T120000Z.md").write_text("sim run done")
    watcher.check_once(set())

    assert calls == []


def test_check_once_does_not_notify_when_nothing_new(tmp_path, monkeypatch):
    """Zero turns when nothing happens: a poll with no new files must be silent."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    calls = _capture_ntfy(monkeypatch)

    (tmp_path / "OLD.md").write_text("already seen")
    watcher.check_once({"OLD.md"})

    assert calls == []


def test_check_once_notifies_each_of_multiple_new_files(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    calls = _capture_ntfy(monkeypatch)

    (tmp_path / "A.md").write_text("a")
    (tmp_path / "B.md").write_text("b")
    watcher.check_once(set())

    joined = " ".join(calls)
    assert "A.md" in joined and "B.md" in joined


def test_check_once_mixed_batch_only_notifies_actionable_names(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "STATE_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(watcher, "LOG_FILE", tmp_path / "log.md")
    calls = _capture_ntfy(monkeypatch)

    (tmp_path / "REAL_DIRECTIVE.md").write_text("real")
    (tmp_path / "from_rich_20260708_130000.md").write_text("msg")
    (tmp_path / "run_complete_20260708T130000Z.md").write_text("done")
    watcher.check_once(set())

    joined = " ".join(calls)
    assert "REAL_DIRECTIVE.md" in joined
    assert "from_rich" not in joined and "run_complete" not in joined


def test_staging_watcher_has_no_pane_injection_api():
    for removed in ("_relay_wake_to_claude", "_attempt_pending_wake",
                    "_pending_wake_names", "send_keys_when_idle"):
        assert not hasattr(watcher, removed), f"staging_watcher.{removed} must be deleted"


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
    # Isolate the shared fire-once register (check_once now gates through it).
    monkeypatch.setattr("background.action_needed.REGISTER_PATH", tmp_path / "an.json")
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


# ── archive-on-consumption backstop for instruction docs (2026-07-16) ────────
# The re-stick class one channel over from from_rich: a director/advisor
# instruction .md that was actioned+consumed but never manually moved to done/
# re-grants supervisor turns forever. No "superseded" signal exists for these,
# so the mechanism is an absolute-age sweep that ALWAYS NTFYs (never silent).

def test_instruction_sweep_archives_stale_doc_and_ntfys(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)
    calls = _capture_ntfy(monkeypatch)

    now = datetime(2026, 7, 16, 12, 0, 0, tzinfo=timezone.utc)
    doc = tmp_path / "DIRECTOR_ANSWERS_C7.md"
    doc.write_text("consumed decision, never archived")
    import os
    old_epoch = now.timestamp() - (watcher.INSTRUCTION_STALE_SECONDS + 3600)
    os.utime(doc, (old_epoch, old_epoch))

    archived = watcher.sweep_stale_instruction_docs(now=now)
    assert doc.name in archived
    assert (tmp_path / "done" / doc.name).exists()
    assert not doc.exists()  # moved, not copied
    assert any("STAGING BACKSTOP" in c and doc.name in c for c in calls)


def test_instruction_sweep_leaves_fresh_doc(tmp_path, monkeypatch):
    """A directive the loop simply hasn't reached yet (younger than the long
    backstop) must NEVER be swept out from under it."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)
    calls = _capture_ntfy(monkeypatch)

    now = datetime(2026, 7, 16, 12, 0, 0, tzinfo=timezone.utc)
    doc = tmp_path / "FRESH_DIRECTIVE.md"
    doc.write_text("staged an hour ago, not yet actioned")
    import os
    recent = now.timestamp() - 3600  # 1h old, well under the backstop
    os.utime(doc, (recent, recent))

    assert watcher.sweep_stale_instruction_docs(now=now) == []
    assert doc.exists()
    assert calls == []


def test_instruction_sweep_ignores_from_rich_and_markers(tmp_path, monkeypatch):
    """Scoped to instruction docs only -- from_rich_*.md (its own sweep) and
    run_complete_/run_pending_ markers (process_run_complete.py's job) must
    never be touched by this backstop, even when ancient."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda msg: None)
    calls = _capture_ntfy(monkeypatch)

    now = datetime(2026, 7, 16, 12, 0, 0, tzinfo=timezone.utc)
    import os
    ancient = now.timestamp() - (watcher.INSTRUCTION_STALE_SECONDS + 999999)
    for name in ("from_rich_20260710_000000.md",
                 "run_complete_20260710T000000Z.md",
                 "run_pending_20260710T000000Z.md",
                 ".gitkeep"):
        p = tmp_path / name
        p.write_text("x")
        os.utime(p, (ancient, ancient))

    assert watcher.sweep_stale_instruction_docs(now=now) == []
    assert (tmp_path / "from_rich_20260710_000000.md").exists()
    assert (tmp_path / "run_complete_20260710T000000Z.md").exists()
    assert calls == []


# ── remote-staging bridge must not resurrect an archived doc (2026-07-16) ─────
# While local HEAD trails origin, local_head..origin/main keeps containing the
# [ADVISOR-STAGED] commits that first added a doc, so check_remote() re-created
# it in root every cycle even after it was moved to done/ -- the re-stick root
# cause for advisor-bridged docs. An archived copy in done/ = consumed = skip.

def _bridge_fake_run(show_counter):
    def fake_run(cmd, timeout=30):
        if cmd[:2] == ["git", "fetch"]:
            return (0, "", "")
        if cmd[:2] == ["git", "rev-parse"]:
            return (0, "deadbeefcafe", "")
        if cmd[:3] == ["git", "rev-list", "--count"]:
            return (0, "5", "")  # 5 new remote commits
        if cmd[:2] == ["git", "show"]:
            show_counter["n"] += 1
            return (0, "doc content from origin", "")
        return (0, "", "")
    return fake_run


def test_bridge_does_not_resurrect_archived_doc(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda m: None)
    done = tmp_path / "done"
    done.mkdir()
    (done / "DIRECTOR_ANSWERS_C7.md").write_text("consumed decision")
    monkeypatch.setattr(watcher, "_extract_advisor_staging_files",
                        lambda ref: ["DIRECTOR_ANSWERS_C7.md"])
    counter = {"n": 0}
    monkeypatch.setattr(watcher, "_run", _bridge_fake_run(counter))

    watcher.check_remote(set())

    assert not (tmp_path / "DIRECTOR_ANSWERS_C7.md").exists()  # not resurrected in root
    assert counter["n"] == 0  # git show for its content never even attempted


def test_bridge_materialises_unarchived_advisor_doc(tmp_path, monkeypatch):
    """The guard is scoped: a genuinely-new advisor doc with no done/ copy is
    still materialised into root exactly as before."""
    monkeypatch.setattr(watcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(watcher, "log", lambda m: None)
    (tmp_path / "done").mkdir()
    monkeypatch.setattr(watcher, "_extract_advisor_staging_files",
                        lambda ref: ["NEW_ADVISOR_STEER.md"])
    counter = {"n": 0}
    monkeypatch.setattr(watcher, "_run", _bridge_fake_run(counter))

    watcher.check_remote(set())

    assert (tmp_path / "NEW_ADVISOR_STEER.md").exists()  # materialised
    assert counter["n"] == 1
