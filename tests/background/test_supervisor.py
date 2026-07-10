"""Tests for background/supervisor.py -- the sole turn-granting authority
built after doorbell failure #4 (2026-07-09, R3 architecture rebuild).

Includes explicit simulations of all four historical wake/turn-granting
failure modes, per the director's directive to test against each one:
  1. Original raw-send-into-a-busy-pane corruption (pre-Phase-SB).
  2. 17:47 urgent-from_rich queued-no-wake (Phase SB).
  3. session_watchdog's autoloop racing staging_watcher's wake (strike 3,
     2026-07-08, fixed by relay_lock).
  4. Delivered-confirmed-but-no-progress: 34 "successful" autoloop sends
     over 5.5 hours with zero resulting work (2026-07-09, this rebuild).
"""
import json
import time

import pytest

from background import agenda as agenda_module
from background import supervisor


def _reset_supervisor_state():
    supervisor._was_paused = False
    supervisor._last_fingerprint = None
    supervisor._fingerprint_unchanged_grants = 0
    supervisor._escalated_for_fingerprint = None


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(supervisor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(supervisor, "USAGE_PAUSE_FILE", tmp_path / ".usage_pause.json")
    # Isolated from the real, committed PRIORITIES.md -- defaults to a
    # nonexistent tmp_path file (no backlog found, matching the pre-existing
    # "nothing open" test expectations), never the real repo file.
    monkeypatch.setattr(supervisor, "PRIORITIES_PATH", tmp_path / "PRIORITIES.md")
    # Isolated from the real, committed maturity_map.yaml for the same reason
    # -- defaults to a nonexistent tmp_path file so pre-existing backlog-
    # fallback tests still exercise the fallback path specifically.
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    monkeypatch.setattr(agenda_module, "AGENDA_FILE", tmp_path / ".open_agenda.json")
    (tmp_path / "staging").mkdir()
    _reset_supervisor_state()
    yield
    _reset_supervisor_state()


# ── find_work() ──

def test_find_work_none_when_nothing_open():
    assert supervisor.find_work(resumed_from_pause=False) is None


def test_find_work_detects_open_agenda():
    agenda_module.set_agenda("PhaseX", "stepY", "do the thing")
    reason = supervisor.find_work(resumed_from_pause=False)
    assert "PhaseX" in reason and "stepY" in reason


def test_find_work_detects_unprocessed_staging():
    (supervisor.STAGING_DIR / "SOME_DOC.md").write_text("staged content")
    reason = supervisor.find_work(resumed_from_pause=False)
    assert "SOME_DOC.md" in reason


def test_find_work_ignores_gitkeep():
    (supervisor.STAGING_DIR / ".gitkeep").write_text("")
    assert supervisor.find_work(resumed_from_pause=False) is None


def test_find_work_detects_urgent_from_rich_distinctly():
    (supervisor.STAGING_DIR / "from_rich_20260709_010000.md").write_text(
        "<!-- Dispatcher: URGENT (classified 2026-07-09 01:00 UTC) -->\nsomething is wrong"
    )
    reason = supervisor.find_work(resumed_from_pause=False)
    assert "urgent from_rich queued" in reason
    assert "from_rich_20260709_010000.md" in reason


def test_find_work_normal_from_rich_counts_as_unprocessed_staging():
    (supervisor.STAGING_DIR / "from_rich_20260709_010000.md").write_text(
        "<!-- Dispatcher: NORMAL (classified 2026-07-09 01:00 UTC) -->\nfyi"
    )
    reason = supervisor.find_work(resumed_from_pause=False)
    assert "unprocessed staging" in reason


def test_find_work_agenda_takes_priority_over_staging():
    agenda_module.set_agenda("PhaseX", "stepY", "do the thing")
    (supervisor.STAGING_DIR / "SOME_DOC.md").write_text("staged content")
    reason = supervisor.find_work(resumed_from_pause=False)
    assert "agenda open" in reason


# ── self-refill (2026-07-10, SELF_DIRECTION_AND_PARALLELISM.md Problem 1) ──

def test_find_work_self_refills_from_backlog_when_nothing_staged():
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- Some item NOT YET STARTED -- do it\n"
    )
    reason = supervisor.find_work(resumed_from_pause=False)
    assert reason is not None
    assert "self-refill" in reason


def test_find_work_ignores_blocked_backlog_items():
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- **BLOCKED** on something NOT YET STARTED, awaiting director\n"
    )
    assert supervisor.find_work(resumed_from_pause=False) is None


def test_find_work_ignores_review_gate_backlog_items():
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- **REVIEW GATE OPEN (Tier 1)** -- some item NOT YET STARTED\n"
    )
    assert supervisor.find_work(resumed_from_pause=False) is None


def test_find_work_no_backlog_section_returns_none():
    supervisor.PRIORITIES_PATH.write_text("# Just a title, no backlog section\n")
    assert supervisor.find_work(resumed_from_pause=False) is None


def test_find_work_missing_priorities_file_returns_none():
    assert not supervisor.PRIORITIES_PATH.exists()
    assert supervisor.find_work(resumed_from_pause=False) is None


def test_find_work_staging_and_agenda_still_win_over_backlog():
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- Some item NOT YET STARTED\n"
    )
    (supervisor.STAGING_DIR / "SOME_DOC.md").write_text("staged content")
    reason = supervisor.find_work(resumed_from_pause=False)
    assert "unprocessed staging" in reason
    assert "self-refill" not in reason


# ── maturity-map dial-weighted draw (2026-07-10, director audit + R3 redesign
#    of the backlog-prose-scan root cause of a real 2h40m idle hole) ──

_ONE_GAP_ATOM_YAML = """\
- id: X1_test_atom
  name: "Test atom with a real gap"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: discover
"""

_NO_GAP_ATOM_YAML = """\
- id: X2_done_atom
  name: "Test atom already at target"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 3
  level_target: 3
  loop_stage: harden
"""

_UNASSESSED_ATOM_YAML = """\
- id: X3_unassessed_atom
  name: "Honestly unassessed atom"
  lane: X_test_lane
  dial_inherited: 3
  level_current: null
  level_target: 2
  loop_stage: idle
"""

_UNMET_DEPENDENCY_YAML = """\
- id: X4_dependent_atom
  name: "Atom whose dependency is not yet at target"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: build
  depends_on: [X5_prerequisite_atom]
- id: X5_prerequisite_atom
  name: "Prerequisite not yet done"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 3
  loop_stage: discover
"""

_MET_DEPENDENCY_YAML = """\
- id: X4_dependent_atom
  name: "Atom whose dependency IS at target"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: build
  depends_on: [X5_prerequisite_atom]
- id: X5_prerequisite_atom
  name: "Prerequisite already done"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 3
  level_target: 3
  loop_stage: harden
"""

_MISSING_DEPENDENCY_YAML = """\
- id: X6_dependent_on_nonexistent
  name: "Atom depending on an id not present in the map at all"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: build
  depends_on: [X7_does_not_exist]
"""

_IDLE_ATOM_YAML = """\
- id: X8_idle_atom
  name: "Atom explicitly parked, not in the active loop"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 1
  level_target: 2
  loop_stage: idle
"""

_MALFORMED_LEVEL_TYPE_YAML = """\
- id: X9_malformed_atom
  name: "Atom with a quoted string level instead of an int"
  lane: X_test_lane
  dial_inherited: 3
  level_current: "2"
  level_target: 3
"""

_NULL_DIAL_YAML = """\
- id: X10_null_dial_atom
  name: "Atom with dial_inherited explicitly null"
  lane: X_test_lane
  dial_inherited: null
  level_current: 0
  level_target: 2
"""

_MIXED_MALFORMED_AND_VALID_YAML = """\
- id: X9_malformed_atom
  name: "Atom with a quoted string level instead of an int"
  lane: X_test_lane
  dial_inherited: 3
  level_current: "2"
  level_target: 3
- id: X1_test_atom
  name: "Test atom with a real gap"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: discover
"""


def test_maturity_map_draw_none_when_file_missing():
    assert not supervisor.MATURITY_MAP_PATH.exists()
    assert supervisor._maturity_map_draw() is None


def test_maturity_map_draw_finds_atom_with_real_gap():
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
    result = supervisor._maturity_map_draw()
    assert result is not None
    assert "X1_test_atom" in result
    assert "lane=X_test_lane" in result
    assert "level 0->2" in result


def test_maturity_map_draw_excludes_atoms_already_at_target():
    supervisor.MATURITY_MAP_PATH.write_text(_NO_GAP_ATOM_YAML)
    assert supervisor._maturity_map_draw() is None


def test_maturity_map_draw_excludes_unassessed_atoms():
    supervisor.MATURITY_MAP_PATH.write_text(_UNASSESSED_ATOM_YAML)
    assert supervisor._maturity_map_draw() is None


def test_maturity_map_draw_excludes_atom_with_unmet_dependency():
    """2026-07-10 real observed gap: the first live draw surfaced
    W1_2_generate_futures (level 0->2) whose own depends_on
    (W1_reveal_over_time) was itself at level 0/3 -- premature, unbuildable
    "work". A dependency not yet at its own target level must exclude the
    dependent atom entirely -- but the prerequisite atom itself (which has
    no unmet dependencies of its own) remains a legitimately drawable
    candidate on its own merits, e.g. the fixture's own X5_prerequisite_atom."""
    supervisor.MATURITY_MAP_PATH.write_text(_UNMET_DEPENDENCY_YAML)
    results = [supervisor._maturity_map_draw() for _ in range(20)]
    assert all(r is not None and "X4_dependent_atom" not in r for r in results)
    assert any("X5_prerequisite_atom" in r for r in results)


def test_maturity_map_draw_includes_atom_once_dependency_met():
    supervisor.MATURITY_MAP_PATH.write_text(_MET_DEPENDENCY_YAML)
    result = supervisor._maturity_map_draw()
    assert result is not None
    assert "X4_dependent_atom" in result


def test_maturity_map_draw_excludes_atom_depending_on_nonexistent_id():
    """A depends_on id absent from the map entirely fails closed (treated as
    unmet), not silently assumed satisfied."""
    supervisor.MATURITY_MAP_PATH.write_text(_MISSING_DEPENDENCY_YAML)
    assert supervisor._maturity_map_draw() is None


def test_maturity_map_draw_excludes_idle_loop_stage():
    """2026-07-10 real observed gap: the third live draw surfaced
    W3_1_price_cap_binding (loop_stage=idle) -- per MATURITY_MAP.md's own
    schema, "idle" means explicitly parked/not in the active Hardening Loop
    (this atom is also Step 5 of MARGIN_REALISM, sequenced after Steps 3-4),
    so it must never be surfaced as active self-refill work even though it
    has a real level gap and no unmet dependency."""
    supervisor.MATURITY_MAP_PATH.write_text(_IDLE_ATOM_YAML)
    assert supervisor._maturity_map_draw() is None


def test_maturity_map_draw_skips_atom_with_string_level_instead_of_crashing():
    """2026-07-10, HARDEN-stage adversarial review of this exact function
    (H1_supervisor_turn_granting's own Expert Hour): a malformed atom (e.g.
    a quoted "2" instead of an int, an easy hand-editing typo) must not
    raise -- comparing str < int raises TypeError, which would previously
    propagate uncaught out of _maturity_map_draw(), aborting find_work()
    before it ever reaches the backlog-prose fallback -- silently
    reintroducing the exact idle-hole class of bug this whole mechanism
    was built to eliminate, specifically during agenda+staging-empty
    periods (self-refill's own use case)."""
    supervisor.MATURITY_MAP_PATH.write_text(_MALFORMED_LEVEL_TYPE_YAML)
    assert supervisor._maturity_map_draw() is None  # degrades gracefully, does not raise


def test_maturity_map_draw_skips_atom_with_null_dial_instead_of_crashing():
    """dial_inherited: null (explicit YAML null, distinct from the key being
    absent entirely) previously reached max(1, None), raising TypeError."""
    supervisor.MATURITY_MAP_PATH.write_text(_NULL_DIAL_YAML)
    assert supervisor._maturity_map_draw() is None


def test_maturity_map_draw_skips_malformed_atom_but_still_draws_a_valid_one():
    """The real robustness property: ONE malformed atom degrades to
    "excluded from this draw", not "the whole draw stops working" -- a
    valid atom elsewhere in the same file must still be drawable."""
    supervisor.MATURITY_MAP_PATH.write_text(_MIXED_MALFORMED_AND_VALID_YAML)
    result = supervisor._maturity_map_draw()
    assert result is not None
    assert "X1_test_atom" in result
    assert "X9_malformed_atom" not in result


def test_maturity_map_draw_weights_by_dial():
    """A weighted-random draw is inherently probabilistic -- a fixed seed
    makes this deterministic rather than a real (if small) flake risk on
    an unweighted `random` draw across CI runs."""
    import random as random_module
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: LOW_DIAL\n  lane: L\n  dial_inherited: 1\n  level_current: 0\n  level_target: 1\n"
        "- id: HIGH_DIAL\n  lane: H\n  dial_inherited: 100\n  level_current: 0\n  level_target: 1\n"
    )
    rng = random_module.Random(42)
    results = [supervisor._maturity_map_draw(rng=rng) for _ in range(20)]
    assert sum("HIGH_DIAL" in r for r in results) >= 18  # overwhelmingly the high-dial atom


def test_find_work_self_refills_from_maturity_map_when_nothing_staged():
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
    reason = supervisor.find_work(resumed_from_pause=False)
    assert reason is not None
    assert "self-refill from maturity map" in reason
    assert "X1_test_atom" in reason


def test_find_work_maturity_map_wins_over_backlog_fallback():
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- Some item NOT YET STARTED\n"
    )
    reason = supervisor.find_work(resumed_from_pause=False)
    assert "maturity map" in reason
    assert "PRIORITIES.md backlog" not in reason


def test_find_work_falls_back_to_backlog_when_maturity_map_unavailable():
    assert not supervisor.MATURITY_MAP_PATH.exists()
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- Some item NOT YET STARTED\n"
    )
    reason = supervisor.find_work(resumed_from_pause=False)
    assert "self-refill from PRIORITIES.md backlog (fallback" in reason


def test_find_work_staging_wins_over_maturity_map():
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
    (supervisor.STAGING_DIR / "SOME_DOC.md").write_text("staged content")
    reason = supervisor.find_work(resumed_from_pause=False)
    assert "unprocessed staging" in reason
    assert "maturity map" not in reason


def test_work_fingerprint_changes_when_priorities_md_edited():
    import os
    supervisor.PRIORITIES_PATH.write_text("## Backlog\n- item A NOT YET STARTED\n")
    fp1 = supervisor._work_fingerprint()
    supervisor.PRIORITIES_PATH.write_text("## Backlog\n- item A CLOSED\n- item B NOT YET STARTED\n")
    # Deterministic mtime bump -- avoids flakiness from coarse filesystem
    # timestamp resolution on a real (if tiny) sleep.
    st = supervisor.PRIORITIES_PATH.stat()
    os.utime(supervisor.PRIORITIES_PATH, (st.st_atime, st.st_mtime + 1))
    fp2 = supervisor._work_fingerprint()
    assert fp1 != fp2


def test_find_work_resumed_from_pause_short_circuits():
    reason = supervisor.find_work(resumed_from_pause=True)
    assert "usage-limit pause just ended" in reason


# ── _pause_active_readonly() ──

def test_pause_readonly_false_when_no_file():
    assert supervisor._pause_active_readonly() is False


def test_pause_readonly_true_when_future(tmp_path):
    from datetime import datetime, timedelta, timezone
    resume_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    supervisor.USAGE_PAUSE_FILE.write_text(json.dumps({"resume_at": resume_at}))
    assert supervisor._pause_active_readonly() is True
    # Read-only: must not delete the file (session_watchdog owns that).
    assert supervisor.USAGE_PAUSE_FILE.exists()


def test_pause_readonly_false_when_past():
    from datetime import datetime, timedelta, timezone
    resume_at = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    supervisor.USAGE_PAUSE_FILE.write_text(json.dumps({"resume_at": resume_at}))
    assert supervisor._pause_active_readonly() is False
    # Still read-only even when expired.
    assert supervisor.USAGE_PAUSE_FILE.exists()


def test_pause_readonly_false_on_malformed_file():
    supervisor.USAGE_PAUSE_FILE.write_text("not json")
    assert supervisor._pause_active_readonly() is False


# ── run_cycle(): basic gating ──

def test_run_cycle_skips_when_paused(monkeypatch):
    from datetime import datetime, timedelta, timezone
    resume_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    supervisor.USAGE_PAUSE_FILE.write_text(json.dumps({"resume_at": resume_at}))
    grant_calls = []
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: grant_calls.append(reason) or True)
    supervisor.run_cycle()
    assert grant_calls == []
    assert supervisor._was_paused is True


def test_run_cycle_skips_when_busy(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: False)
    grant_calls = []
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: grant_calls.append(reason) or True)
    agenda_module.set_agenda("PhaseX", "stepY", "do the thing")
    supervisor.run_cycle()
    assert grant_calls == []


def test_run_cycle_clears_copy_mode_before_idle_check(monkeypatch):
    """R4 (2026-07-09): a pane frozen in tmux copy-mode/scrollback must be
    cleared before this cycle trusts its own idle check -- not left to read
    stale content forever."""
    monkeypatch.setattr(supervisor, "pane_in_copy_mode", lambda session: True)
    clear_calls = []
    monkeypatch.setattr(supervisor, "ensure_live_tail", lambda session: clear_calls.append(session))
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    grant_calls = []
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: grant_calls.append(reason) or True)
    agenda_module.set_agenda("PhaseX", "stepY", "do the thing")
    supervisor.run_cycle()
    assert clear_calls == [supervisor.SESSION_NAME]
    assert len(grant_calls) == 1


def test_run_cycle_does_not_clear_copy_mode_when_not_in_copy_mode(monkeypatch):
    monkeypatch.setattr(supervisor, "pane_in_copy_mode", lambda session: False)
    clear_calls = []
    monkeypatch.setattr(supervisor, "ensure_live_tail", lambda session: clear_calls.append(session))
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)
    supervisor.run_cycle()
    assert clear_calls == []


def test_run_cycle_skips_when_idle_and_no_work(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    grant_calls = []
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: grant_calls.append(reason) or True)
    supervisor.run_cycle()
    assert grant_calls == []


def test_run_cycle_grants_when_idle_and_work_exists(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    grant_calls = []
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: grant_calls.append(reason) or True)
    agenda_module.set_agenda("PhaseX", "stepY", "do the thing")
    supervisor.run_cycle()
    assert len(grant_calls) == 1
    assert "PhaseX" in grant_calls[0]


def test_run_cycle_resume_transition_grants_even_with_no_other_work(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)
    supervisor._was_paused = True  # was paused last cycle
    # no agenda, no staging -- pure resume-transition work
    reason_holder = {}
    monkeypatch.setattr(
        supervisor, "grant_turn",
        lambda reason: reason_holder.setdefault("reason", reason) or True,
    )
    supervisor.run_cycle()
    assert "usage-limit pause just ended" in reason_holder["reason"]


# ── grant_turn(): reuses the shared locked relay ──

def test_grant_turn_calls_send_keys_when_idle(monkeypatch):
    calls = []
    monkeypatch.setattr(
        supervisor, "send_keys_when_idle",
        lambda session, text, marker: calls.append((session, text)) or True,
    )
    result = supervisor.grant_turn("agenda open -- test")
    assert result is True
    assert len(calls) == 1
    assert calls[0][0] == supervisor.SESSION_NAME
    assert "agenda open -- test" in calls[0][1]


# ── Stuck-grant escalation (the piece beyond the literal spec) ──

def test_stuck_escalation_fires_after_threshold_unchanged_grants(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)  # "always delivered"
    ntfy_calls = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
    agenda_module.set_agenda("PhaseX", "stepY", "stuck forever")

    for _ in range(supervisor.STUCK_GRANT_THRESHOLD - 1):
        supervisor.run_cycle()
    assert ntfy_calls == []  # not yet at threshold

    supervisor.run_cycle()
    assert len(ntfy_calls) == 1
    assert "swallowing turns" in ntfy_calls[0]


def test_stuck_escalation_does_not_repeat_for_same_fingerprint(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)
    ntfy_calls = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
    agenda_module.set_agenda("PhaseX", "stepY", "stuck forever")

    for _ in range(supervisor.STUCK_GRANT_THRESHOLD + 5):
        supervisor.run_cycle()

    assert len(ntfy_calls) == 1  # deduped, not one per cycle past threshold


def test_stuck_counter_resets_when_fingerprint_changes(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)
    ntfy_calls = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
    agenda_module.set_agenda("PhaseX", "stepY", "working")

    for _ in range(supervisor.STUCK_GRANT_THRESHOLD - 1):
        supervisor.run_cycle()
    assert ntfy_calls == []

    # Real progress: agenda updated (new updated_at) -- fingerprint changes.
    time.sleep(0.01)
    agenda_module.set_agenda("PhaseX", "stepZ", "moved on")
    supervisor.run_cycle()
    assert supervisor._fingerprint_unchanged_grants == 1  # grant #1 for the new fingerprint
    assert ntfy_calls == []


def test_stuck_escalation_fires_again_for_a_new_stuck_state(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)
    ntfy_calls = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
    agenda_module.set_agenda("PhaseX", "stepY", "stuck forever")

    for _ in range(supervisor.STUCK_GRANT_THRESHOLD):
        supervisor.run_cycle()
    assert len(ntfy_calls) == 1

    # Progress happens, then gets stuck again in a NEW state.
    time.sleep(0.01)
    agenda_module.set_agenda("PhaseX", "stepZ", "stuck again")
    for _ in range(supervisor.STUCK_GRANT_THRESHOLD):
        supervisor.run_cycle()
    assert len(ntfy_calls) == 2


def test_stuck_escalation_does_not_fire_when_grants_fail(monkeypatch):
    """If grant_turn keeps returning False (busy/unconfirmed), that's the
    ALREADY-understood retry case -- not the failure #4 signature (which
    was grants reporting SUCCESS with no progress). No escalation."""
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: False)
    ntfy_calls = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
    agenda_module.set_agenda("PhaseX", "stepY", "busy pane every time")

    for _ in range(supervisor.STUCK_GRANT_THRESHOLD + 5):
        supervisor.run_cycle()
    # Fingerprint tracking still runs (grant attempted), so this documents
    # current behaviour: escalation is about state-progress, independent of
    # confirmed-delivery. Failed-delivery has its own log line already.
    assert len(ntfy_calls) == 1


# ── The four historical failure modes, simulated explicitly ──

class TestFailureMode1RawSendIntoBusyPane:
    """Original pre-Phase-SB corruption: a signed wake landed partially in
    a busy pane's input box and never submitted. The supervisor must never
    even attempt a send while the pane is busy."""

    def test_never_calls_send_when_busy(self, monkeypatch):
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: False)
        send_calls = []
        monkeypatch.setattr(
            supervisor, "send_keys_when_idle",
            lambda *a, **k: send_calls.append(a) or True,
        )
        agenda_module.set_agenda("PhaseX", "stepY", "urgent work")
        supervisor.run_cycle()
        assert send_calls == []


class TestFailureMode2UrgentFromRichQueuedNoWake:
    """2026-07-08 17:47: an urgent from_rich message was classified and
    queued for relay, but the fast-path wake never delivered. The
    supervisor's guarantee does not depend on dispatcher.py's own relay --
    it reads the classified file straight off disk on its own poll."""

    def test_supervisor_grants_a_turn_for_urgent_from_rich_independent_of_dispatcher(self, monkeypatch):
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
        grant_calls = []
        monkeypatch.setattr(
            supervisor, "grant_turn",
            lambda reason: grant_calls.append(reason) or True,
        )
        # Simulate dispatcher.py having classified the file (header
        # prepended) but its own _pending_urgent relay never having fired --
        # the supervisor never reads dispatcher's in-memory state at all.
        (supervisor.STAGING_DIR / "from_rich_20260708_174700.md").write_text(
            "<!-- Dispatcher: URGENT (classified 2026-07-08 17:47 UTC) -->\n"
            "gross margin looks wrong, investigate now"
        )
        supervisor.run_cycle()
        assert len(grant_calls) == 1
        assert "urgent from_rich queued" in grant_calls[0]


class TestFailureMode3AutoloopRacingStagingWake:
    """2026-07-08 strike 3: session_watchdog's autoloop nudge and
    staging_watcher's wake could both attempt a send into the same pane at
    once. The supervisor's grant goes through the same relay_lock-protected
    send_keys_when_idle as every other daemon, so a concurrent holder of
    the lock makes this attempt fail closed, never interleave."""

    def test_grant_turn_fails_closed_when_relay_lock_held_by_another_daemon(self, monkeypatch, tmp_path):
        import fcntl
        from background import tmux_relay

        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        monkeypatch.setattr(tmux_relay, "_RELAY_LOCK_FILE", tmp_path / ".tmux_relay.lock")
        monkeypatch.setattr(tmux_relay, "_RELAY_LOCK_TIMEOUT_SECONDS", 0.3)
        send_calls = []
        monkeypatch.setattr(
            tmux_relay.subprocess, "run",
            lambda cmd, **kw: send_calls.append(cmd) or type("R", (), {"returncode": 0, "stdout": "❯ \n"})(),
        )

        lock_fh = open(tmp_path / ".tmux_relay.lock", "w")
        fcntl.flock(lock_fh, fcntl.LOCK_EX)
        try:
            # supervisor.grant_turn -> tmux_relay.send_keys_when_idle directly
            # (bypassing the module-level pytest guard via the same pattern
            # test_tmux_relay.py uses) to prove the real lock is what fails
            # this closed, not a mock.
            result = tmux_relay.send_keys_when_idle("claude", "hello|123|abc123", "abc123")
        finally:
            fcntl.flock(lock_fh, fcntl.LOCK_UN)
            lock_fh.close()

        assert result is False
        assert send_calls == []  # never even attempted the idle check


class TestFailureMode4DeliveredButNoProgress:
    """2026-07-09: session_watchdog's autoloop logged "delivered
    (confirmed)" 34 times over 5.5 hours with zero resulting work. The
    supervisor cannot force the CLI to actually execute a granted turn
    (root cause lives outside this codebase, see the retrospective) -- but
    it must DETECT the pattern and escalate instead of retrying silently
    forever, which is what let tonight's failure go unnoticed for 5+ hours."""

    def test_repeated_confirmed_grants_with_no_progress_trigger_one_escalation(self, monkeypatch):
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
        # Every grant reports success, exactly like the 34 real log lines
        # from 2026-07-08 22:47 to 2026-07-09 04:32.
        monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)
        ntfy_calls = []
        monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
        agenda_module.set_agenda(
            "BILL_CORRECTNESS_ADDENDUM.md", "Defects 2-4", "wire meter-read status into bills",
        )

        # Simulate ~5.5 hours at the real 2-minute cadence worth of cycles
        # (34 grants) -- the exact count from the real incident.
        for _ in range(34):
            supervisor.run_cycle()

        assert len(ntfy_calls) == 1, "must escalate exactly once, not zero and not repeatedly"
        assert "swallowing turns" in ntfy_calls[0]
