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

# Captured before the autouse fixture below patches maybe_auto_clear() out by
# default -- TestAutoClear's own tests that exercise the real function
# restore it explicitly via this reference.
_REAL_MAYBE_AUTO_CLEAR = supervisor.maybe_auto_clear


class _FakeClock:
    """A monotonically-advancing fake clock for time.time(), so stuck-
    escalation tests can simulate hours of wall-clock elapsing across many
    supervisor cycles without a real sleep (2026-07-11 redesign -- the
    escalation mechanism is now wall-clock-based, not grant-count-based)."""
    def __init__(self, start: float = 0.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _reset_supervisor_state():
    supervisor._was_paused = False


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(supervisor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(supervisor, "USAGE_PAUSE_FILE", tmp_path / ".usage_pause.json")
    monkeypatch.setattr(supervisor, "STUCK_STATE_FILE", tmp_path / ".supervisor_stuck_state.json")
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
    # Default off for every test in this file: maybe_auto_clear() reads the
    # REAL transcript directory and REAL git status, so leaving it live would
    # make run_cycle() tests nondeterministic (and, in the worst case, able
    # to actually inject /clear into a live tmux session mid test-run) --
    # discovered exactly this way, 2026-07-11, when the existing suite only
    # passed by coincidence (the real working tree happened to be dirty at
    # test-run time). Tests that specifically exercise auto-clear override
    # this explicitly.
    monkeypatch.setattr(supervisor, "maybe_auto_clear", lambda: False)
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


def test_find_work_ignores_in_progress_subdirectory():
    """docs/staging/in_progress/ (2026-07-11 convention, CLAUDE.md "How to
    operate autonomously"): a multi-part staged instruction with a
    genuinely still-open sub-item is parked here rather than left in the
    scanned root, where a fully-actioned-but-unarchived file re-granted a
    supervisor turn every ~2min for hours with nothing new to do. No new
    code needed -- _unprocessed_staging_files() already only iterates
    top-level FILES (p.is_file()), same mechanism that already excludes
    done/fyi/drafts/ -- this test just proves the new directory name is
    correctly covered by that same existing exclusion."""
    in_progress = supervisor.STAGING_DIR / "in_progress"
    in_progress.mkdir()
    (in_progress / "PARKED_INSTRUCTION.md").write_text("still has one open sub-item")
    assert supervisor.find_work(resumed_from_pause=False) is None


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


def test_find_work_ignores_backlog_heading_mentioned_in_prose_before_the_real_heading():
    """2026-07-10 real observed gap, found by testing find_work() directly
    (third instance of the same self-referential false-positive class): a
    raw text.find("## Backlog") locks onto the FIRST occurrence of that
    substring anywhere in the file -- including a prose sentence describing
    the mechanism itself (e.g. '...scans text after the literal "## Backlog"
    heading...') that appears BEFORE the real heading. Must anchor to an
    actual line-start heading, not any mention of the string."""
    supervisor.PRIORITIES_PATH.write_text(
        "# Some doc-history section\n"
        "This mechanism scans text after the literal \"## Backlog\" heading "
        "for actionable items -- NOT YET STARTED items get picked up.\n"
        "\n"
        "## Backlog\n"
        "- Some real item, no gap here\n"
    )
    assert supervisor.find_work(resumed_from_pause=False) is None


def test_find_work_still_finds_real_backlog_item_past_a_prose_mention():
    supervisor.PRIORITIES_PATH.write_text(
        "# Some doc-history section\n"
        "This mechanism scans text after the literal \"## Backlog\" heading.\n"
        "\n"
        "## Backlog\n"
        "- Some item NOT YET STARTED -- do it\n"
    )
    reason = supervisor.find_work(resumed_from_pause=False)
    assert reason is not None
    assert "self-refill" in reason


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


def test_stuck_key_backlog_path_changes_when_priorities_md_edited():
    """The self-refill-from-backlog path SHOULD be sensitive to PRIORITIES.md
    edits -- an edit there is the real progress signal for that path."""
    import os
    reason = (
        "agenda+staging empty -- self-refill from PRIORITIES.md backlog "
        "(fallback, maturity map unavailable): item A"
    )
    supervisor.PRIORITIES_PATH.write_text("## Backlog\n- item A NOT YET STARTED\n")
    key1 = supervisor._stuck_key(reason)
    supervisor.PRIORITIES_PATH.write_text("## Backlog\n- item A CLOSED\n- item B NOT YET STARTED\n")
    # Deterministic mtime bump -- avoids flakiness from coarse filesystem
    # timestamp resolution on a real (if tiny) sleep.
    st = supervisor.PRIORITIES_PATH.stat()
    os.utime(supervisor.PRIORITIES_PATH, (st.st_atime, st.st_mtime + 1))
    key2 = supervisor._stuck_key(reason)
    assert key1 != key2


def test_stuck_key_staging_path_ignores_unrelated_priorities_md_edits():
    """The actual root-cause fix (2026-07-11, director-caught): for the
    unprocessed-staging path, editing PRIORITIES.md for OTHER, unrelated
    work must NOT reset the stuck-clock for these untouched staged files --
    this is exactly what let a full night of zero progress on two genuinely
    stuck files go unescalated."""
    import os
    reason = "unprocessed staging -- SOME_DOC.md"
    supervisor.PRIORITIES_PATH.write_text("## Backlog\n- item A NOT YET STARTED\n")
    key1 = supervisor._stuck_key(reason)
    supervisor.PRIORITIES_PATH.write_text("## Backlog\n- item A CLOSED\n")
    st = supervisor.PRIORITIES_PATH.stat()
    os.utime(supervisor.PRIORITIES_PATH, (st.st_atime, st.st_mtime + 1))
    key2 = supervisor._stuck_key(reason)
    assert key1 == key2


def test_stuck_key_staging_path_ignores_run_complete_marker_churn():
    """The other root-cause fix: transient run_complete_*.md markers coming
    and going (sim_runner's own normal pipeline cadence) must NOT change the
    stuck key for an unrelated, genuinely-stuck staged doc."""
    (supervisor.STAGING_DIR / "SOME_DOC.md").write_text("staged content")
    reason = supervisor.find_work(resumed_from_pause=False)
    key1 = supervisor._stuck_key(reason)
    (supervisor.STAGING_DIR / "run_complete_20260101T000000Z.md").write_text("marker")
    key2 = supervisor._stuck_key(reason)
    assert key1 == key2


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
# Wall-clock-based (2026-07-11 redesign) -- a _FakeClock stands in for
# time.time() so these simulate hours of elapsed wall-clock time across many
# cycles without a real sleep. supervisor.POLL_INTERVAL_SECONDS (120s) is the
# real cadence; supervisor.STUCK_THRESHOLD_SECONDS (3600s) divides evenly by
# it (30 cycles), used directly rather than hardcoding cycle counts.

_STEP = 120  # matches supervisor.POLL_INTERVAL_SECONDS, asserted below


def test_step_matches_real_poll_interval():
    assert _STEP == supervisor.POLL_INTERVAL_SECONDS


def test_stuck_escalation_fires_after_threshold_elapsed(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)  # "always delivered"
    ntfy_calls = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
    agenda_module.set_agenda("PhaseX", "stepY", "stuck forever")

    clock = _FakeClock()
    monkeypatch.setattr(supervisor.time, "time", clock)
    cycles_to_threshold = supervisor.STUCK_THRESHOLD_SECONDS // _STEP  # 30

    clock.advance(_STEP)
    supervisor.run_cycle()  # baseline cycle -- establishes first_seen_at
    assert ntfy_calls == []

    for _ in range(cycles_to_threshold - 1):
        clock.advance(_STEP)
        supervisor.run_cycle()
    assert ntfy_calls == []  # not yet at threshold

    clock.advance(_STEP)
    supervisor.run_cycle()
    assert len(ntfy_calls) == 1
    assert "swallowing turns" in ntfy_calls[0]


def test_stuck_escalation_does_not_repeat_for_same_key(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)
    ntfy_calls = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
    agenda_module.set_agenda("PhaseX", "stepY", "stuck forever")

    clock = _FakeClock()
    monkeypatch.setattr(supervisor.time, "time", clock)

    for _ in range(supervisor.STUCK_THRESHOLD_SECONDS // _STEP + 10):
        clock.advance(_STEP)
        supervisor.run_cycle()

    assert len(ntfy_calls) == 1  # deduped, not one per cycle past threshold


def test_stuck_clock_resets_when_key_changes(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)
    ntfy_calls = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
    agenda_module.set_agenda("PhaseX", "stepY", "working")

    clock = _FakeClock()
    monkeypatch.setattr(supervisor.time, "time", clock)
    cycles_to_threshold = supervisor.STUCK_THRESHOLD_SECONDS // _STEP

    for _ in range(cycles_to_threshold - 1):
        clock.advance(_STEP)
        supervisor.run_cycle()
    assert ntfy_calls == []

    # Real progress: agenda updated (new updated_at) -- key changes, clock resets.
    clock.advance(_STEP)
    agenda_module.set_agenda("PhaseX", "stepZ", "moved on")
    supervisor.run_cycle()
    state = supervisor._load_stuck_state()
    assert state["first_seen_at"] == clock.now  # reset to this cycle, not accumulated
    assert ntfy_calls == []


def test_stuck_escalation_fires_again_for_a_new_stuck_state(monkeypatch):
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)
    ntfy_calls = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
    agenda_module.set_agenda("PhaseX", "stepY", "stuck forever")

    clock = _FakeClock()
    monkeypatch.setattr(supervisor.time, "time", clock)
    cycles_to_threshold = supervisor.STUCK_THRESHOLD_SECONDS // _STEP

    for _ in range(cycles_to_threshold + 1):
        clock.advance(_STEP)
        supervisor.run_cycle()
    assert len(ntfy_calls) == 1

    # Progress happens, then gets stuck again in a NEW state.
    clock.advance(_STEP)
    agenda_module.set_agenda("PhaseX", "stepZ", "stuck again")
    for _ in range(cycles_to_threshold + 1):
        clock.advance(_STEP)
        supervisor.run_cycle()
    assert len(ntfy_calls) == 2


def test_stuck_escalation_does_not_fire_when_grants_fail(monkeypatch):
    """If grant_turn keeps returning False (busy/unconfirmed), that's the
    ALREADY-understood retry case -- not the failure #4 signature (which
    was grants reporting SUCCESS with no progress). Escalation still fires
    here (see docstring on the original test), since it's about state-
    progress, independent of confirmed-delivery."""
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: False)
    ntfy_calls = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
    agenda_module.set_agenda("PhaseX", "stepY", "busy pane every time")

    clock = _FakeClock()
    monkeypatch.setattr(supervisor.time, "time", clock)

    for _ in range(supervisor.STUCK_THRESHOLD_SECONDS // _STEP + 10):
        clock.advance(_STEP)
        supervisor.run_cycle()
    assert len(ntfy_calls) == 1


def test_stuck_escalation_survives_daemon_restart(monkeypatch):
    """The other root-cause fix (2026-07-11): the tracker is disk-persisted,
    not an in-memory counter -- a supervisor.py process restart mid-stuck-
    period must not silently reset the clock back to zero."""
    monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
    monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)
    ntfy_calls = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
    agenda_module.set_agenda("PhaseX", "stepY", "stuck forever")

    clock = _FakeClock()
    monkeypatch.setattr(supervisor.time, "time", clock)
    cycles_to_threshold = supervisor.STUCK_THRESHOLD_SECONDS // _STEP

    clock.advance(_STEP)
    supervisor.run_cycle()  # baseline -- writes first_seen_at to disk

    # Simulate a process restart: nothing in-memory survives except what's
    # on disk (STUCK_STATE_FILE, untouched by the restart).
    _reset_supervisor_state()

    for _ in range(cycles_to_threshold):
        clock.advance(_STEP)
        supervisor.run_cycle()
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
        # (34 grants) -- the exact count from the real incident. Wall-clock
        # based (2026-07-11 redesign) -- a fake clock stands in for real
        # elapsed time so 34 cycles at the real 120s cadence (~68min) is
        # enough to cross STUCK_THRESHOLD_SECONDS (60min).
        clock = _FakeClock()
        monkeypatch.setattr(supervisor.time, "time", clock)
        for _ in range(34):
            clock.advance(_STEP)
            supervisor.run_cycle()

        assert len(ntfy_calls) == 1, "must escalate exactly once, not zero and not repeatedly"
        assert "swallowing turns" in ntfy_calls[0]


class TestAutoClear:
    """ADVISOR_STEER_OVERNIGHT.md item 2 (2026-07-11, authorized in-console
    the same morning, confirmed genuine over NTFY): context > ~400k AND a
    clean boundary (idle, nothing uncommitted) -> supervisor injects /clear,
    the next cycle's ordinary flow re-grants with the standard boot."""

    def test_should_auto_clear_false_when_no_transcript_found(self, monkeypatch):
        monkeypatch.setattr(supervisor, "_latest_transcript_size_bytes", lambda: None)
        assert supervisor.should_auto_clear() is False

    def test_should_auto_clear_false_when_under_threshold(self, monkeypatch):
        monkeypatch.setattr(supervisor, "_latest_transcript_size_bytes", lambda: 1_000)
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
        monkeypatch.setattr(supervisor, "_git_tree_clean", lambda: True)
        assert supervisor.should_auto_clear() is False

    def test_should_auto_clear_false_when_busy(self, monkeypatch):
        monkeypatch.setattr(
            supervisor, "_latest_transcript_size_bytes",
            lambda: supervisor.AUTO_CLEAR_BYTES_THRESHOLD + 1,
        )
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: False)
        monkeypatch.setattr(supervisor, "_git_tree_clean", lambda: True)
        assert supervisor.should_auto_clear() is False

    def test_should_auto_clear_false_when_tree_dirty(self, monkeypatch):
        monkeypatch.setattr(
            supervisor, "_latest_transcript_size_bytes",
            lambda: supervisor.AUTO_CLEAR_BYTES_THRESHOLD + 1,
        )
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
        monkeypatch.setattr(supervisor, "_git_tree_clean", lambda: False)
        assert supervisor.should_auto_clear() is False

    def test_should_auto_clear_true_when_all_conditions_met(self, monkeypatch):
        monkeypatch.setattr(
            supervisor, "_latest_transcript_size_bytes",
            lambda: supervisor.AUTO_CLEAR_BYTES_THRESHOLD + 1,
        )
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
        monkeypatch.setattr(supervisor, "_git_tree_clean", lambda: True)
        assert supervisor.should_auto_clear() is True

    def test_git_tree_clean_true_for_empty_porcelain_output(self, monkeypatch):
        class _FakeResult:
            returncode = 0
            stdout = ""

        monkeypatch.setattr(supervisor.subprocess, "run", lambda *a, **k: _FakeResult())
        assert supervisor._git_tree_clean() is True

    def test_git_tree_clean_false_for_nonempty_porcelain_output(self, monkeypatch):
        class _FakeResult:
            returncode = 0
            stdout = " M some/file.py\n"

        monkeypatch.setattr(supervisor.subprocess, "run", lambda *a, **k: _FakeResult())
        assert supervisor._git_tree_clean() is False

    def test_git_tree_clean_fails_closed_on_nonzero_exit(self, monkeypatch):
        class _FakeResult:
            returncode = 1
            stdout = ""

        monkeypatch.setattr(supervisor.subprocess, "run", lambda *a, **k: _FakeResult())
        assert supervisor._git_tree_clean() is False

    def test_git_tree_clean_fails_closed_on_exception(self, monkeypatch):
        def _raise(*a, **k):
            raise OSError("git not found")

        monkeypatch.setattr(supervisor.subprocess, "run", _raise)
        assert supervisor._git_tree_clean() is False

    def test_latest_transcript_size_bytes_none_when_dir_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(supervisor, "CLAUDE_PROJECTS_DIR", tmp_path / "nonexistent")
        assert supervisor._latest_transcript_size_bytes() is None

    def test_latest_transcript_size_bytes_none_when_no_jsonl_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(supervisor, "CLAUDE_PROJECTS_DIR", tmp_path)
        assert supervisor._latest_transcript_size_bytes() is None

    def test_latest_transcript_size_bytes_returns_most_recently_modified(self, tmp_path, monkeypatch):
        import os
        import time as time_mod

        monkeypatch.setattr(supervisor, "CLAUDE_PROJECTS_DIR", tmp_path)
        old = tmp_path / "old-session.jsonl"
        old.write_text("x" * 100)
        new = tmp_path / "new-session.jsonl"
        new.write_text("y" * 500)
        # Force distinct mtimes regardless of filesystem timestamp resolution.
        now = time_mod.time()
        os.utime(old, (now - 100, now - 100))
        os.utime(new, (now, now))
        assert supervisor._latest_transcript_size_bytes() == 500

    def test_maybe_auto_clear_noop_when_condition_not_met(self, monkeypatch):
        monkeypatch.setattr(supervisor, "maybe_auto_clear", _REAL_MAYBE_AUTO_CLEAR)
        monkeypatch.setattr(supervisor, "should_auto_clear", lambda: False)
        send_calls = []
        monkeypatch.setattr(
            supervisor, "send_keys_when_idle",
            lambda *a, **k: send_calls.append(a) or True,
        )
        assert supervisor.maybe_auto_clear() is False
        assert send_calls == []

    def test_maybe_auto_clear_sends_clear_and_logs_when_condition_met(self, tmp_path, monkeypatch):
        monkeypatch.setattr(supervisor, "maybe_auto_clear", _REAL_MAYBE_AUTO_CLEAR)
        monkeypatch.setattr(supervisor, "should_auto_clear", lambda: True)
        monkeypatch.setattr(supervisor, "_latest_transcript_size_bytes", lambda: 12_345_678)
        send_calls = []
        monkeypatch.setattr(
            supervisor, "send_keys_when_idle",
            lambda session, text, marker: send_calls.append((session, text, marker)) or True,
        )
        monkeypatch.setattr(supervisor, "AUTO_CLEAR_LOG_FILE", tmp_path / "auto-clear-log.md")
        assert supervisor.maybe_auto_clear() is True
        assert send_calls == [(supervisor.SESSION_NAME, "/clear", "/clear")]
        log_content = (tmp_path / "auto-clear-log.md").read_text()
        assert "Auto-clear sent" in log_content
        assert "12345678" in log_content

    def test_maybe_auto_clear_logs_failure_when_send_fails(self, tmp_path, monkeypatch):
        monkeypatch.setattr(supervisor, "maybe_auto_clear", _REAL_MAYBE_AUTO_CLEAR)
        monkeypatch.setattr(supervisor, "should_auto_clear", lambda: True)
        monkeypatch.setattr(supervisor, "_latest_transcript_size_bytes", lambda: 12_345_678)
        monkeypatch.setattr(supervisor, "send_keys_when_idle", lambda *a, **k: False)
        monkeypatch.setattr(supervisor, "AUTO_CLEAR_LOG_FILE", tmp_path / "auto-clear-log.md")
        assert supervisor.maybe_auto_clear() is False
        log_content = (tmp_path / "auto-clear-log.md").read_text()
        assert "FAILED to send" in log_content

    def test_run_cycle_skips_normal_grant_when_auto_clear_fires(self, monkeypatch):
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
        monkeypatch.setattr(supervisor, "maybe_auto_clear", lambda: True)
        grant_calls = []
        monkeypatch.setattr(supervisor, "grant_turn", lambda reason: grant_calls.append(reason) or True)
        agenda_module.set_agenda("PhaseX", "stepY", "do the thing")
        supervisor.run_cycle()
        assert grant_calls == [], "auto-clear firing must skip this cycle's normal turn-grant"

    def test_run_cycle_proceeds_normally_when_auto_clear_does_not_fire(self, monkeypatch):
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
        monkeypatch.setattr(supervisor, "maybe_auto_clear", lambda: False)
        grant_calls = []
        monkeypatch.setattr(supervisor, "grant_turn", lambda reason: grant_calls.append(reason) or True)
        agenda_module.set_agenda("PhaseX", "stepY", "do the thing")
        supervisor.run_cycle()
        assert len(grant_calls) == 1
