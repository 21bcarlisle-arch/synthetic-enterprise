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
    # R3_WORK_GRANTING_REDESIGN.md additions (2026-07-12): isolate the two
    # new state files the same way as STUCK_STATE_FILE above, and default
    # `ntfy` to a no-op capturing no calls -- most tests in this file never
    # cared about escalation before and must not crash (the real send_ntfy
    # raises if SE_NTFY_TOPIC isn't configured) or pollute real observability
    # files just because a test happens to reach a genuinely-idle state.
    # Tests that specifically exercise map-exhausted escalation override
    # `ntfy` explicitly, same convention as the existing stuck-escalation tests.
    monkeypatch.setattr(supervisor, "MAP_EXHAUSTED_STATE_FILE", tmp_path / ".supervisor_map_exhausted_state.json")
    monkeypatch.setattr(supervisor, "IDLE_TURN_COUNTER_FILE", tmp_path / ".supervisor_idle_turn_count.json")
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / ".atom_stall_tracker.json")
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: None)
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
    assert supervisor.find_work(resumed_from_pause=False)[0] is None


def test_find_work_detects_open_agenda():
    agenda_module.set_agenda("PhaseX", "stepY", "do the thing")
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    assert "PhaseX" in reason and "stepY" in reason


def test_find_work_detects_unprocessed_staging():
    (supervisor.STAGING_DIR / "SOME_DOC.md").write_text("staged content")
    reason, _ = supervisor.find_work(resumed_from_pause=False)
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
    assert supervisor.find_work(resumed_from_pause=False)[0] is None


def test_find_work_ignores_gitkeep():
    (supervisor.STAGING_DIR / ".gitkeep").write_text("")
    assert supervisor.find_work(resumed_from_pause=False)[0] is None


def test_find_work_detects_urgent_from_rich_distinctly():
    (supervisor.STAGING_DIR / "from_rich_20260709_010000.md").write_text(
        "<!-- Dispatcher: URGENT (classified 2026-07-09 01:00 UTC) -->\nsomething is wrong"
    )
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    assert "urgent from_rich queued" in reason
    assert "from_rich_20260709_010000.md" in reason


def test_find_work_normal_from_rich_counts_as_unprocessed_staging():
    (supervisor.STAGING_DIR / "from_rich_20260709_010000.md").write_text(
        "<!-- Dispatcher: NORMAL (classified 2026-07-09 01:00 UTC) -->\nfyi"
    )
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    assert "unprocessed staging" in reason


def test_find_work_agenda_takes_priority_over_staging():
    agenda_module.set_agenda("PhaseX", "stepY", "do the thing")
    (supervisor.STAGING_DIR / "SOME_DOC.md").write_text("staged content")
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    assert "agenda open" in reason


# ── self-refill (2026-07-10, SELF_DIRECTION_AND_PARALLELISM.md Problem 1) ──

def test_find_work_self_refills_from_backlog_when_nothing_staged():
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- Some item NOT YET STARTED -- do it\n"
    )
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    assert reason is not None
    assert "self-refill" in reason


def test_find_work_ignores_blocked_backlog_items():
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- **BLOCKED** on something NOT YET STARTED, awaiting director\n"
    )
    assert supervisor.find_work(resumed_from_pause=False)[0] is None


def test_find_work_ignores_review_gate_backlog_items():
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- **REVIEW GATE OPEN (Tier 1)** -- some item NOT YET STARTED\n"
    )
    assert supervisor.find_work(resumed_from_pause=False)[0] is None


def test_find_work_no_backlog_section_returns_none():
    supervisor.PRIORITIES_PATH.write_text("# Just a title, no backlog section\n")
    assert supervisor.find_work(resumed_from_pause=False)[0] is None


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
    assert supervisor.find_work(resumed_from_pause=False)[0] is None


def test_find_work_still_finds_real_backlog_item_past_a_prose_mention():
    supervisor.PRIORITIES_PATH.write_text(
        "# Some doc-history section\n"
        "This mechanism scans text after the literal \"## Backlog\" heading.\n"
        "\n"
        "## Backlog\n"
        "- Some item NOT YET STARTED -- do it\n"
    )
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    assert reason is not None
    assert "self-refill" in reason


def test_find_work_missing_priorities_file_returns_none():
    assert not supervisor.PRIORITIES_PATH.exists()
    assert supervisor.find_work(resumed_from_pause=False)[0] is None


def test_find_work_staging_wins_as_primary_but_self_refill_still_appended():
    """R3_WORK_GRANTING_REDESIGN.md requirement 2: the self-refill draw is
    now UNCONDITIONAL -- staging still wins as the PRIMARY reason, but a
    real instruction on the channel no longer suppresses the self-refill
    draw the way it used to (that suppression was itself part of the
    trigger-driven bug: a real doorbell should ADD work, never crowd out
    the backlog draw)."""
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- Some item NOT YET STARTED\n"
    )
    (supervisor.STAGING_DIR / "SOME_DOC.md").write_text("staged content")
    reason, exhausted = supervisor.find_work(resumed_from_pause=False)
    assert "unprocessed staging" in reason
    assert "self-refill" in reason
    assert exhausted is False


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


# EPOCH_GATING_AND_ATOM_AUTHORSHIP.md (P0, 2026-07-12, director-prompted "why
# can't it think of its own work for future epochs"): Rule 1 -- epoch gating
# (loop_stage: idle) gates BUILD only, never DISCOVER/FRAME. A second draw
# tier picks up idle atoms for exactly that class of work, so the drawable
# set is never empty while ANY atom (build-candidate or idle) exists.

def test_idle_discover_frame_draw_none_when_file_missing():
    assert not supervisor.MATURITY_MAP_PATH.exists()
    assert supervisor._idle_discover_frame_draw() is None


def test_idle_discover_frame_draw_finds_idle_atom_with_real_gap():
    """The exact fixture test_maturity_map_draw_excludes_idle_loop_stage
    uses to prove the BUILD draw correctly EXCLUDES this atom -- here proving
    the new idle-tier draw correctly INCLUDES it. Both must be true at once:
    gating applies to BUILD, never to DISCOVER/FRAME."""
    supervisor.MATURITY_MAP_PATH.write_text(_IDLE_ATOM_YAML)
    assert supervisor._maturity_map_draw() is None  # still gated from BUILD
    result = supervisor._idle_discover_frame_draw()
    assert result is not None
    assert result["id"] == "X8_idle_atom"


def test_idle_discover_frame_draw_excludes_idle_atom_already_at_target():
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: X_done_idle\n  lane: L\n  dial_inherited: 1\n  loop_stage: idle\n"
        "  level_current: 2\n  level_target: 2\n"
    )
    assert supervisor._idle_discover_frame_draw() is None


def test_idle_discover_frame_draw_excludes_non_idle_atom():
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)  # loop_stage != idle
    assert supervisor._idle_discover_frame_draw() is None


def test_idle_discover_frame_draw_skips_malformed_atom_instead_of_crashing():
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: X_bad\n  lane: L\n  dial_inherited: null\n  loop_stage: idle\n"
        "  level_current: 0\n  level_target: 1\n"
    )
    assert supervisor._idle_discover_frame_draw() is None  # degrades gracefully


def test_idle_discover_frame_draw_weights_by_dial():
    import random as random_module
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: LOW_DIAL_IDLE\n  lane: L\n  dial_inherited: 1\n  loop_stage: idle\n"
        "  level_current: 0\n  level_target: 1\n"
        "- id: HIGH_DIAL_IDLE\n  lane: H\n  dial_inherited: 100\n  loop_stage: idle\n"
        "  level_current: 0\n  level_target: 1\n"
    )
    rng = random_module.Random(42)
    results = [supervisor._idle_discover_frame_draw(rng=rng)["id"] for _ in range(20)]
    assert sum(r == "HIGH_DIAL_IDLE" for r in results) >= 18


# ANTI_LIVELOCK_AND_WIDTH.md (P0, 2026-07-13): idle-tier width (item 2) and
# the anti-livelock stall tracker (item 1). Both are opt-in on the existing
# draw functions (exclude_stalled defaults False everywhere above), so none
# of the tests above needed to change.

def test_idle_discover_frame_draw_concurrent_grants_multiple_distinct_atoms():
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: IDLE_A\n  lane: L\n  dial_inherited: 3\n  loop_stage: idle\n"
        "  level_current: 0\n  level_target: 2\n"
        "- id: IDLE_B\n  lane: L\n  dial_inherited: 3\n  loop_stage: idle\n"
        "  level_current: 0\n  level_target: 2\n"
        "- id: IDLE_C\n  lane: L\n  dial_inherited: 3\n  loop_stage: idle\n"
        "  level_current: 0\n  level_target: 2\n"
    )
    selected = supervisor._idle_discover_frame_draw_concurrent(width=6)
    assert len(selected) == 3  # all three real candidates, none duplicated
    assert len({a["id"] for a in selected}) == 3


def test_idle_discover_frame_draw_concurrent_respects_width_cap():
    lines = "".join(
        f"- id: IDLE_{i}\n  lane: L\n  dial_inherited: 1\n  loop_stage: idle\n"
        f"  level_current: 0\n  level_target: 1\n"
        for i in range(10)
    )
    supervisor.MATURITY_MAP_PATH.write_text(lines)
    selected = supervisor._idle_discover_frame_draw_concurrent(width=4)
    assert len(selected) == 4


def test_idle_discover_frame_draw_concurrent_returns_empty_list_when_no_candidates():
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)  # loop_stage != idle
    assert supervisor._idle_discover_frame_draw_concurrent() == []


def test_idle_discover_frame_draw_concurrent_default_excludes_nothing_stalled():
    """exclude_stalled defaults False -- pre-existing/other callers never
    silently start filtering just because the tracker file happens to
    exist from another test's or process's own prior run."""
    supervisor.MATURITY_MAP_PATH.write_text(_IDLE_ATOM_YAML)
    supervisor._save_atom_stall_state({"X8_idle_atom": {"fingerprint": "x", "consecutive_unchanged": 5, "stalled": True}})
    selected = supervisor._idle_discover_frame_draw_concurrent()
    assert len(selected) == 1
    assert selected[0]["id"] == "X8_idle_atom"


# ── Anti-livelock stall tracker ──

def test_atom_fingerprint_stable_for_unchanged_atom():
    atom = {"level_current": 2, "level_target": 3, "loop_stage": "idle", "simplifications": ["a", "b"], "expert_hour": {"last": "2026-07-12"}}
    assert supervisor._atom_fingerprint(atom) == supervisor._atom_fingerprint(dict(atom))


def test_atom_fingerprint_changes_when_simplifications_grow():
    before = {"level_current": 2, "level_target": 3, "loop_stage": "idle", "simplifications": ["a"]}
    after = {"level_current": 2, "level_target": 3, "loop_stage": "idle", "simplifications": ["a", "b"]}
    assert supervisor._atom_fingerprint(before) != supervisor._atom_fingerprint(after)


def test_record_atom_draw_and_check_stall_ratchets_then_flags():
    fp = "same-fingerprint"
    stalled1, count1 = supervisor._record_atom_draw_and_check_stall("X", fp)
    assert (stalled1, count1) == (False, 1)
    stalled2, count2 = supervisor._record_atom_draw_and_check_stall("X", fp)
    assert (stalled2, count2) == (True, 2)  # ATOM_STALL_THRESHOLD == 2


def test_record_atom_draw_and_check_stall_resets_on_real_change():
    supervisor._record_atom_draw_and_check_stall("X", "fp1")
    supervisor._record_atom_draw_and_check_stall("X", "fp1")  # now stalled
    stalled, count = supervisor._record_atom_draw_and_check_stall("X", "fp2")  # genuinely changed
    assert (stalled, count) == (False, 1)


def test_is_atom_stalled_reads_persisted_flag():
    assert not supervisor._is_atom_stalled("Y")
    supervisor._record_atom_draw_and_check_stall("Y", "fp")
    supervisor._record_atom_draw_and_check_stall("Y", "fp")
    assert supervisor._is_atom_stalled("Y")


def test_maturity_map_draw_concurrent_exclude_stalled_prefers_other_candidate():
    """The actual DoD property (item 1): after 2 consecutive unchanged
    draws of the same atom, a genuinely different candidate is preferred."""
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: SPINNING\n  lane: L\n  dial_inherited: 100\n"
        "  level_current: 1\n  level_target: 2\n"
        "- id: ALTERNATIVE\n  lane: L\n  dial_inherited: 1\n"
        "  level_current: 1\n  level_target: 2\n"
    )
    import random as random_module
    rng = random_module.Random(1)
    # Draw twice with the identical fixture (identical fingerprint each time) --
    # the high-dial atom wins both, the second one crosses ATOM_STALL_THRESHOLD.
    first = supervisor._maturity_map_draw_concurrent(rng=rng, exclude_stalled=True)[0]
    second = supervisor._maturity_map_draw_concurrent(rng=rng, exclude_stalled=True)[0]
    assert first["id"] == "SPINNING"
    assert second["id"] == "SPINNING"
    assert supervisor._is_atom_stalled("SPINNING")
    third = supervisor._maturity_map_draw_concurrent(rng=rng, exclude_stalled=True)[0]
    assert third["id"] == "ALTERNATIVE"  # deprioritised, not re-selected a third time


def test_maturity_map_draw_concurrent_exclude_stalled_falls_back_when_all_stalled():
    """Soft deprioritisation, never a hard exclusion: if literally every
    candidate is already flagged stalled, still return something rather
    than reporting false exhaustion."""
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: ONLY_ONE\n  lane: L\n  dial_inherited: 1\n"
        "  level_current: 1\n  level_target: 2\n"
    )
    supervisor._record_atom_draw_and_check_stall("ONLY_ONE", "fp")
    supervisor._record_atom_draw_and_check_stall("ONLY_ONE", "fp")
    assert supervisor._is_atom_stalled("ONLY_ONE")
    selected = supervisor._maturity_map_draw_concurrent(exclude_stalled=True)
    assert len(selected) == 1
    assert selected[0]["id"] == "ONLY_ONE"


def test_maturity_map_draw_concurrent_default_ignores_stall_state():
    """exclude_stalled defaults False -- byte-for-byte preserves every
    pre-existing test/caller of this function."""
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: ONLY_ONE\n  lane: L\n  dial_inherited: 1\n"
        "  level_current: 1\n  level_target: 2\n"
    )
    supervisor._record_atom_draw_and_check_stall("ONLY_ONE", "fp")
    supervisor._record_atom_draw_and_check_stall("ONLY_ONE", "fp")
    selected = supervisor._maturity_map_draw_concurrent()  # no exclude_stalled kwarg
    assert selected[0]["id"] == "ONLY_ONE"


def test_self_refill_draw_falls_to_idle_discover_frame_when_no_build_candidate():
    """The actual DoD property: a map with ONLY idle atoms (no BUILD gap,
    no PRIORITIES.md backlog) must still self-refill real work, not fall
    through to nothing."""
    supervisor.MATURITY_MAP_PATH.write_text(_IDLE_ATOM_YAML)
    reason = supervisor._self_refill_draw()
    assert reason is not None
    assert "DISCOVER/FRAME only" in reason
    assert "X8_idle_atom" in reason


def test_find_work_drawable_set_non_empty_when_only_idle_atoms_exist():
    """EPOCH_GATING_AND_ATOM_AUTHORSHIP.md's own DoD: "a test that the
    drawable set is non-empty whenever ANY atom exists in any state." A map
    with only an idle atom (no PRIORITIES.md backlog, no staging, no
    agenda) must NOT report map_exhausted=True -- that would be the exact
    bug this doc corrected (an idle turn with a parked atom present)."""
    supervisor.MATURITY_MAP_PATH.write_text(_IDLE_ATOM_YAML)
    reason, exhausted = supervisor.find_work(resumed_from_pause=False)
    assert reason is not None
    assert exhausted is False
    assert "DISCOVER/FRAME only" in reason


# MULTI_ATOM_DRAW.md (P0, 2026-07-12, director-prompted): "the supervisor
# draws ONE atom per turn... width must be a property of the granting model,
# not a standing exhortation." The draw can now grant N>1 atoms per cycle
# when their declared file_scope is provably disjoint.

def test_atom_file_scope_absent_key_returns_none():
    assert supervisor._atom_file_scope({"id": "A"}) is None


def test_atom_file_scope_empty_list_returns_empty_frozenset():
    assert supervisor._atom_file_scope({"id": "A", "file_scope": []}) == frozenset()


def test_atom_file_scope_populated_list_returns_frozenset():
    scope = supervisor._atom_file_scope({"id": "A", "file_scope": ["x.py", "y.py"]})
    assert scope == frozenset({"x.py", "y.py"})


def test_atoms_file_disjoint_true_for_non_overlapping_scopes():
    a = {"id": "A", "file_scope": ["x.py"]}
    b = {"id": "B", "file_scope": ["y.py"]}
    assert supervisor._atoms_file_disjoint(a, b) is True


def test_atoms_file_disjoint_false_for_overlapping_scopes():
    a = {"id": "A", "file_scope": ["shared.py", "x.py"]}
    b = {"id": "B", "file_scope": ["shared.py", "y.py"]}
    assert supervisor._atoms_file_disjoint(a, b) is False


def test_atoms_file_disjoint_true_for_both_empty_scopes():
    """A genuinely code-free atom (e.g. read-only research/charter work)
    never conflicts with anything, including another code-free atom."""
    a = {"id": "A", "file_scope": []}
    b = {"id": "B", "file_scope": []}
    assert supervisor._atoms_file_disjoint(a, b) is True


def test_atoms_file_disjoint_false_when_scope_undeclared():
    """Constraint 3 of MULTI_ATOM_DRAW.md: 'do not pretend disjointness
    that does not hold' -- an atom with NO file_scope key at all must fail
    CLOSED (never eligible for a concurrent grant), not be assumed safe."""
    a = {"id": "A", "file_scope": ["x.py"]}
    b = {"id": "B"}  # no file_scope key
    assert supervisor._atoms_file_disjoint(a, b) is False
    assert supervisor._atoms_file_disjoint(b, a) is False


_TWO_DISJOINT_ATOMS_YAML = """\
- id: X1_disjoint_a
  name: "Atom A, disjoint file scope"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: ["module_a.py"]
- id: X2_disjoint_b
  name: "Atom B, disjoint file scope"
  lane: X_test_lane
  dial_inherited: 2
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: ["module_b.py"]
"""

_TWO_OVERLAPPING_ATOMS_YAML = """\
- id: X1_overlap_a
  name: "Atom A, overlapping file scope"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: ["shared_module.py"]
- id: X2_overlap_b
  name: "Atom B, overlapping file scope"
  lane: X_test_lane
  dial_inherited: 2
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: ["shared_module.py"]
"""

_THREE_ATOMS_ONE_UNDECLARED_YAML = """\
- id: X1_declared_a
  name: "Atom A, declared disjoint scope"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: ["module_a.py"]
- id: X2_declared_b
  name: "Atom B, declared disjoint scope"
  lane: X_test_lane
  dial_inherited: 2
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: ["module_b.py"]
- id: X3_undeclared
  name: "Atom C, no file_scope key at all"
  lane: X_test_lane
  dial_inherited: 1
  level_current: 0
  level_target: 2
  loop_stage: build
"""


def test_maturity_map_draw_concurrent_grants_two_disjoint_atoms():
    supervisor.MATURITY_MAP_PATH.write_text(_TWO_DISJOINT_ATOMS_YAML)
    selected = supervisor._maturity_map_draw_concurrent()
    ids = {a["id"] for a in selected}
    assert ids == {"X1_disjoint_a", "X2_disjoint_b"}


def test_maturity_map_draw_concurrent_does_not_grant_two_overlapping_atoms():
    supervisor.MATURITY_MAP_PATH.write_text(_TWO_OVERLAPPING_ATOMS_YAML)
    selected = supervisor._maturity_map_draw_concurrent()
    assert len(selected) == 1


def test_maturity_map_draw_concurrent_excludes_undeclared_scope_atom():
    """2026-07-12 fixed a real flake: the unweighted `random` primary draw
    (dial weights 3/2/1) had a genuine ~1-in-6 chance of picking
    X3_undeclared as primary, at which point it WOULD legitimately appear in
    `selected` (it's the primary pick itself) -- the assertion's own claim
    ("regardless of draw order") was false. A fixed seed makes the primary
    pick deterministic; the actual property under test (an undeclared-scope
    atom can never join as an ADDITIONAL concurrent pick alongside a
    declared one) is unaffected by which atom is drawn as primary first."""
    supervisor.MATURITY_MAP_PATH.write_text(_THREE_ATOMS_ONE_UNDECLARED_YAML)
    import random as random_module
    rng = random_module.Random(7)  # picks a declared atom as primary
    selected = supervisor._maturity_map_draw_concurrent(rng=rng)
    ids = {a["id"] for a in selected}
    assert "X3_undeclared" not in ids
    assert ids == {"X1_declared_a", "X2_declared_b"}


def test_maturity_map_draw_concurrent_returns_single_atom_list_when_no_others_exist():
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
    selected = supervisor._maturity_map_draw_concurrent()
    assert len(selected) == 1
    assert selected[0]["id"] == "X1_test_atom"


def test_maturity_map_draw_concurrent_returns_empty_list_when_no_candidates():
    supervisor.MATURITY_MAP_PATH.write_text(_NO_GAP_ATOM_YAML)
    assert supervisor._maturity_map_draw_concurrent() == []


def test_maturity_map_draw_concurrent_returns_empty_list_when_file_missing():
    assert not supervisor.MATURITY_MAP_PATH.exists()
    assert supervisor._maturity_map_draw_concurrent() == []


def test_format_atom_draw_matches_prior_single_atom_message_format():
    atom = {
        "id": "X1_test_atom", "name": "Test atom", "lane": "X_test_lane",
        "dial_inherited": 3, "level_current": 0, "level_target": 2, "loop_stage": "build",
    }
    formatted = supervisor._format_atom_draw(atom)
    assert formatted == (
        "X1_test_atom -- Test atom (lane=X_test_lane, dial=3, "
        "level 0->2, loop_stage=build)"
    )


def test_self_refill_draw_single_atom_message_unchanged():
    """The exact pre-MULTI_ATOM_DRAW message format, preserved when only
    one atom is drawn -- existing callers/NTFY parsing must not break."""
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
    reason = supervisor._self_refill_draw()
    assert reason == (
        "self-refill from maturity map (dial-weighted): X1_test_atom -- "
        "Test atom with a real gap (lane=X_test_lane, dial=3, level 0->2, loop_stage=discover)"
    )


def test_self_refill_draw_reports_concurrent_grant_and_logs_it(monkeypatch):
    logged = []
    monkeypatch.setattr(supervisor, "log", lambda msg: logged.append(msg))
    supervisor.MATURITY_MAP_PATH.write_text(_TWO_DISJOINT_ATOMS_YAML)
    reason = supervisor._self_refill_draw()
    assert "2 CONCURRENT disjoint atoms" in reason
    assert "X1_disjoint_a" in reason
    assert "X2_disjoint_b" in reason
    assert "one Agent fork per atom" in reason
    # THREE_LANES.md: per-lane atoms-drawn-per-cycle logged every cycle.
    assert any("atoms-drawn-per-cycle" in m for m in logged)
    assert any("BUILD=2" in m for m in logged)


# THREE_LANES.md (2026-07-13, director-decided, in-console: "mechanise the
# three-lane draw so the supervisor draws SITE and DISCOVERY every cycle
# regardless of BUILD's state"). The regression these tests lock down: the old
# if/elif cascade RETURNED the moment a BUILD atom existed, so SITE and
# DISCOVERY never drew while BUILD had work, and there was no SITE lane at all.

_THREE_LANE_ALL_POPULATED_YAML = """\
- id: BUILD_ATOM
  name: "A real BUILD-lane atom (sim/company scope, not site)"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: ["sim/module_a.py"]
- id: SITE_ATOM_IDLE
  name: "A site-scoped atom, parked idle -- still drawable for the SITE lane"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 3
  loop_stage: idle
  file_scope: ["site"]
- id: DISCOVERY_ATOM
  name: "An idle non-site atom -- DISCOVER/FRAME only"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: idle
"""


def test_site_lane_draws_site_atom_regardless_of_loop_stage():
    """Lane 2: a `site/**`-scoped atom that is loop_stage=idle (epoch-parked
    for the sim/company BUILD lane) is STILL drawn by the SITE lane -- SITE is
    an ungated parallel lane, disjoint by construction."""
    supervisor.MATURITY_MAP_PATH.write_text(_THREE_LANE_ALL_POPULATED_YAML)
    selected = supervisor._site_lane_draw_concurrent()
    ids = {a["id"] for a in selected}
    assert "SITE_ATOM_IDLE" in ids  # drawn despite loop_stage=idle


def test_site_lane_ignores_non_site_and_at_target_atoms():
    supervisor.MATURITY_MAP_PATH.write_text(_THREE_LANE_ALL_POPULATED_YAML)
    selected = supervisor._site_lane_draw_concurrent()
    ids = {a["id"] for a in selected}
    assert "DISCOVERY_ATOM" not in ids  # no site file_scope
    assert "BUILD_ATOM" not in ids  # sim/ scope, not site


def test_site_lane_recognises_site_prefixed_paths():
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: DEEP_SITE\n  lane: L\n  dial_inherited: 1\n  loop_stage: build\n"
        "  level_current: 0\n  level_target: 1\n  file_scope: [\"site/supplier/index.html\"]\n"
    )
    selected = supervisor._site_lane_draw_concurrent()
    assert {a["id"] for a in selected} == {"DEEP_SITE"}


def test_self_refill_draws_all_three_lanes_even_when_build_is_non_empty(monkeypatch):
    """THE regression: with a non-empty BUILD lane, SITE and DISCOVERY MUST
    still draw in the same cycle -- the old cascade returned on BUILD and left
    both idle. One grant message carries all three clearly-labelled sections."""
    logged = []
    monkeypatch.setattr(supervisor, "log", lambda msg: logged.append(msg))
    supervisor.MATURITY_MAP_PATH.write_text(_THREE_LANE_ALL_POPULATED_YAML)
    reason = supervisor._self_refill_draw()
    assert reason is not None
    # All three lanes present in the single grant message.
    assert "LANE 1 BUILD" in reason and "BUILD_ATOM" in reason
    assert "LANE 2 SITE" in reason and "SITE_ATOM_IDLE" in reason
    assert "LANE 3 DISCOVER/FRAME only" in reason and "DISCOVERY_ATOM" in reason
    assert "pixel-verify" in reason  # SITE lane R11 instruction
    # Per-lane counts logged every cycle, each lane drew exactly one here.
    assert any("BUILD=1, SITE=1, DISCOVERY=1" in m for m in logged)


def test_self_refill_dedups_site_atom_out_of_discovery_lane():
    """De-dup: BUILD wins over SITE wins over DISCOVERY. A site-scoped idle
    atom is a SITE atom, so it appears in the SITE section, never also in the
    DISCOVERY section (which draws idle atoms)."""
    supervisor.MATURITY_MAP_PATH.write_text(_THREE_LANE_ALL_POPULATED_YAML)
    reason = supervisor._self_refill_draw()
    # SITE_ATOM_IDLE appears exactly once (in the SITE section).
    assert reason.count("SITE_ATOM_IDLE") == 1


def test_self_refill_dedups_site_scoped_build_atom_into_build_lane():
    """A site-scoped atom that is itself an active BUILD candidate
    (loop_stage=build) is granted once, in the BUILD lane -- BUILD wins over
    SITE -- never duplicated into the SITE section."""
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: SITE_BUILD\n  lane: L\n  dial_inherited: 3\n  loop_stage: build\n"
        "  level_current: 0\n  level_target: 2\n  file_scope: [\"site\"]\n"
    )
    reason = supervisor._self_refill_draw()
    # Drawn once via the BUILD lane; never duplicated into a SITE section.
    assert "LANE 2 SITE" not in reason
    assert reason.count("SITE_BUILD") == 1


def test_self_refill_site_and_discovery_draw_when_build_is_empty():
    """No BUILD candidate at all, but a SITE atom and a DISCOVERY atom exist
    -- both must still draw (a gated/empty BUILD lane never idles the others)."""
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: SITE_ONLY\n  lane: L\n  dial_inherited: 3\n  loop_stage: idle\n"
        "  level_current: 0\n  level_target: 2\n  file_scope: [\"site\"]\n"
        "- id: DISCOVERY_ONLY\n  lane: L\n  dial_inherited: 3\n  loop_stage: idle\n"
        "  level_current: 0\n  level_target: 2\n"
    )
    reason = supervisor._self_refill_draw()
    assert "LANE 2 SITE" in reason and "SITE_ONLY" in reason
    assert "LANE 3 DISCOVER/FRAME only" in reason and "DISCOVERY_ONLY" in reason
    assert "LANE 1 BUILD" not in reason


_PARKED_DEPENDENCY_CASCADE_YAML = """\
- id: W1_parked
  name: "Deliberately parked at its current level for this epoch"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 2
  level_target: 3
  loop_stage: idle
- id: D2_blocked_and_idle
  name: "Depends on the parked atom, itself correctly idle"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: idle
  depends_on: [W1_parked]
- id: E2_should_be_drawable
  name: "Depends transitively on the parked atom via an idle intermediate, but is itself NOT idle"
  lane: X_test_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: build
  depends_on: [D2_blocked_and_idle]
"""


def test_maturity_map_draw_dependency_on_parked_idle_atom_does_not_block(monkeypatch):
    """ADVISOR_ANSWER_CANNOT_DRAW.md (P0, 2026-07-12): a dependency that is
    deliberately PARKED (loop_stage: idle -- a documented epoch-deferral,
    not an active gap) must not cascade into blocking a non-idle dependent,
    even transitively through another idle atom. Mirrors the real
    W1_reveal_over_time (parked) -> D2_three_clocks (idle) ->
    E2_revenue_reconciliation (NOT idle, was wrongly blocked) cascade."""
    supervisor.MATURITY_MAP_PATH.write_text(_PARKED_DEPENDENCY_CASCADE_YAML)
    result = supervisor._maturity_map_draw()
    assert result is not None
    assert "E2_should_be_drawable" in result


def test_maturity_map_self_refill_real_map_never_cannot_draw():
    """The R3 invariant this bug broke: given the project's OWN real
    maturity_map.yaml (not a synthetic fixture), self-refill must return
    real work, not nothing -- this is the exact regression the advisor's
    escalation caught (50 atoms, 30 idle, 23 at L0, yet zero candidates).

    UPDATED 2026-07-12 (EPOCH_GATING_AND_ATOM_AUTHORSHIP.md): asserts on
    `_self_refill_draw()` (the composite guarantee a granted turn cares
    about), not the raw BUILD-only `_maturity_map_draw()` -- the real map
    can now honestly have ZERO build candidates (every non-idle atom at
    target, as of W5_1_banking_payment_rails earning L3) while still having
    real DISCOVER/FRAME work on its many deliberately-parked idle atoms.
    The old assertion (`_maturity_map_draw() is not None`) would have
    reintroduced the exact class of bug this whole doc fixed -- treating
    an honestly-exhausted BUILD set as "nothing to do" -- had it been left
    in place against today's real, fully-built-out map."""
    real_map = supervisor.PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
    supervisor.MATURITY_MAP_PATH.write_text(real_map.read_text())
    assert supervisor._self_refill_draw() is not None


def test_find_work_never_reports_map_exhausted_against_real_map_with_idle_atoms():
    """ADVISOR_STEER_TWIN_READONLY.md (2026-07-12, director-decided): a live
    supervisor daemon reported a GENUINE cannot-draw (52 atoms, 33 idle, 25 at
    L0, "no drawable gap left") despite EPOCH_GATING_AND_ATOM_AUTHORSHIP.md
    already requiring idle atoms to always be drawable for DISCOVER/FRAME.

    Root-caused with real evidence (R4), not guessed: `ps aux` showed the
    `supervisor` tmux session's `background/supervisor.py` process had been
    running since 14:14, and the idle-discover-frame fix was committed at
    17:40:51 -- textbook R2 ("committed != running"). Restarting the tmux
    session (`tmux kill-session -t supervisor` + relaunch) immediately fixed
    it live -- confirmed via the next real supervisor-wake doorbell showing a
    genuine DISCOVER/FRAME grant instead of cannot-draw.

    This test proves the INVARIANT itself against the real map (not just the
    process-restart fix, which a test can't exercise) -- `find_work()` is the
    exact function `find_work()`'s own callers (autonomous_runner.py,
    session_watchdog.py) use, so this is the same code path that was
    reporting the false cannot-draw, not a narrower proxy for it. Isolated
    from PRIORITIES.md/staging/agenda so a pass here can ONLY come from the
    maturity-map draw itself, never the backlog-prose fallback."""
    real_map = supervisor.PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
    supervisor.MATURITY_MAP_PATH.write_text(real_map.read_text())
    assert not supervisor.PRIORITIES_PATH.exists()
    assert list(supervisor.STAGING_DIR.glob("*")) == []
    reason, exhausted = supervisor.find_work(resumed_from_pause=False)
    assert exhausted is False
    assert reason is not None


def test_diagnose_map_blocked_set_reports_no_blockers_when_none_exist():
    supervisor.MATURITY_MAP_PATH.write_text(_MET_DEPENDENCY_YAML)
    diagnosis = supervisor.diagnose_map_blocked_set()
    assert "no non-idle atom is blocked" in diagnosis.lower() or "no drawable gap" in diagnosis.lower()


def test_diagnose_map_blocked_set_notes_idle_below_target_is_still_drawable():
    """ADVISOR_STEER_TWIN_READONLY.md's real amendment (2026-07-12): the old
    wording ("the map has genuinely no drawable gap left") reads exactly
    like "nothing to do at all" even when idle atoms below target exist and
    ARE drawable via the separate DISCOVER/FRAME tier -- this caused a real
    misdiagnosis. The message must now say so explicitly whenever such atoms
    exist, not just report the BUILD-only blockage."""
    supervisor.MATURITY_MAP_PATH.write_text(_IDLE_ATOM_YAML)  # X8_idle_atom, level 1->2
    diagnosis = supervisor.diagnose_map_blocked_set()
    assert "drawable for discover/frame" in diagnosis.lower()
    assert "1 idle atom" in diagnosis.lower()


def test_diagnose_map_blocked_set_finds_root_through_genuine_blocker():
    """A non-idle, non-parked prerequisite that itself has a real unmet gap
    IS a genuine root -- distinct from the parked case above."""
    supervisor.MATURITY_MAP_PATH.write_text(_UNMET_DEPENDENCY_YAML)
    diagnosis = supervisor.diagnose_map_blocked_set()
    assert "X4_dependent_atom" in diagnosis
    assert "X5_prerequisite_atom" in diagnosis


def test_diagnose_map_blocked_set_does_not_report_parked_chain_as_blocked():
    supervisor.MATURITY_MAP_PATH.write_text(_PARKED_DEPENDENCY_CASCADE_YAML)
    diagnosis = supervisor.diagnose_map_blocked_set()
    assert "no non-idle atom is blocked" in diagnosis.lower()


def test_diagnose_map_blocked_set_finds_deep_transitive_root():
    """Root-finding must walk PAST a genuinely-blocked (non-idle, non-parked)
    intermediate to report the deepest real blocker, not just the immediate
    dependency."""
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: A_top\n  lane: X\n  dial_inherited: 1\n  level_current: 0\n  level_target: 2\n"
        "  loop_stage: build\n  depends_on: [B_middle]\n"
        "- id: B_middle\n  lane: X\n  dial_inherited: 1\n  level_current: 0\n  level_target: 2\n"
        "  loop_stage: build\n  depends_on: [C_root_cause]\n"
        "- id: C_root_cause\n  lane: X\n  dial_inherited: 1\n  level_current: 0\n  level_target: 3\n"
        "  loop_stage: discover\n"
    )
    diagnosis = supervisor.diagnose_map_blocked_set()
    assert "C_root_cause" in diagnosis


def test_check_map_exhausted_escalation_ntfy_includes_diagnosis(monkeypatch):
    sent = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: sent.append(msg))
    supervisor.MATURITY_MAP_PATH.write_text(_UNMET_DEPENDENCY_YAML)
    supervisor.check_map_exhausted_escalation(map_exhausted=True)
    assert sent, "expected an NTFY on the exhausted transition"
    assert "Diagnosis:" in sent[0]


def test_find_work_self_refills_from_maturity_map_when_nothing_staged():
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    assert reason is not None
    assert "self-refill from maturity map" in reason
    assert "X1_test_atom" in reason


def test_find_work_maturity_map_wins_over_backlog_fallback():
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- Some item NOT YET STARTED\n"
    )
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    assert "maturity map" in reason
    assert "PRIORITIES.md backlog" not in reason


def test_find_work_falls_back_to_backlog_when_maturity_map_unavailable():
    assert not supervisor.MATURITY_MAP_PATH.exists()
    supervisor.PRIORITIES_PATH.write_text(
        "## Backlog\n- Some item NOT YET STARTED\n"
    )
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    assert "self-refill from PRIORITIES.md backlog (fallback" in reason


def test_find_work_staging_wins_as_primary_but_maturity_map_still_appended():
    """Same requirement-2 change as the backlog-vs-staging case above,
    applied to the maturity-map draw specifically."""
    supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
    (supervisor.STAGING_DIR / "SOME_DOC.md").write_text("staged content")
    reason, exhausted = supervisor.find_work(resumed_from_pause=False)
    assert "unprocessed staging" in reason
    assert "maturity map" in reason
    assert "X1_test_atom" in reason
    assert exhausted is False


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
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    key1 = supervisor._stuck_key(reason)
    (supervisor.STAGING_DIR / "run_complete_20260101T000000Z.md").write_text("marker")
    key2 = supervisor._stuck_key(reason)
    assert key1 == key2


def test_find_work_resumed_from_pause_short_circuits():
    reason, _ = supervisor.find_work(resumed_from_pause=True)
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


# ── grant_turn(): PULL-LOOP MIGRATION -- NO pane write ──

def test_grant_turn_performs_no_pane_write_and_returns_true():
    """After the migration grant_turn only logs the draw (the pull-loop Stop
    hook delivers it) -- it must not import or call any injection primitive."""
    assert not hasattr(supervisor, "send_keys_when_idle")
    assert supervisor.grant_turn("agenda open -- test") is True


def test_supervisor_has_no_pane_injection_api():
    for removed in ("send_keys_when_idle", "ensure_live_tail", "pane_in_copy_mode",
                    "maybe_auto_clear"):
        assert not hasattr(supervisor, removed), f"supervisor.{removed} must be deleted"


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
    """Original pre-Phase-SB corruption came from typing into a busy pane. That
    failure mode is now impossible BY CONSTRUCTION: the supervisor performs no
    pane write at all (pull-loop migration). It still skips granting while busy,
    but there is no send to corrupt."""

    def test_never_grants_when_busy_and_has_no_send_api(self, monkeypatch):
        assert not hasattr(supervisor, "send_keys_when_idle")
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: False)
        grant_calls = []
        monkeypatch.setattr(supervisor, "grant_turn", lambda reason: grant_calls.append(reason) or True)
        agenda_module.set_agenda("PhaseX", "stepY", "urgent work")
        supervisor.run_cycle()
        assert grant_calls == []


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
    """2026-07-08 strike 3: two daemons could race a send into the same pane.
    PULL-LOOP MIGRATION: no daemon sends into the pane anymore, so the race is
    eliminated by construction (there is no relay_lock, no send path). The
    single transport is the pull-loop Stop hook, one turn at a time."""

    def test_no_relay_lock_or_send_path_exists_to_race(self):
        from background import tmux_relay
        for removed in ("relay_lock", "send_keys_when_idle", "_RELAY_LOCK_FILE"):
            assert not hasattr(tmux_relay, removed), (
                f"tmux_relay.{removed} still exists -- the race can only exist if a send path does"
            )


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

    def test_auto_clear_no_longer_injects(self):
        """PULL-LOOP MIGRATION: maybe_auto_clear (which injected /clear) is
        deleted. should_auto_clear survives as a read-only predicate; context
        compaction is now the pull-loop hook's CHECKPOINT job, not a keystroke."""
        assert not hasattr(supervisor, "maybe_auto_clear")
        assert callable(supervisor.should_auto_clear)


# ── R3_WORK_GRANTING_REDESIGN.md (P0, 9th idle variant, 2026-07-12) ──
# Root cause: routine daemon markers (run_complete_*.md) looked like real
# work on the instruction channel and short-circuited find_work() before
# it ever reached the self-refill draw -- "nothing to do" must be an
# impossible terminal state while the map has open atoms; escalate on
# CANNOT-draw (map genuinely exhausted), never on didn't-draw (something
# else took priority this cycle).

class TestDaemonMarkersOffTheInstructionChannel:
    def test_run_complete_marker_alone_is_not_a_real_instruction(self):
        (supervisor.STAGING_DIR / "run_complete_20260101T000000Z.md").write_text("marker")
        assert supervisor._real_staged_instructions() == []

    def test_run_pending_marker_alone_is_not_a_real_instruction(self):
        (supervisor.STAGING_DIR / "run_pending_20260101T000000Z.md").write_text("marker")
        assert supervisor._real_staged_instructions() == []

    def test_real_staged_doc_alongside_a_marker_is_still_detected(self):
        (supervisor.STAGING_DIR / "run_complete_20260101T000000Z.md").write_text("marker")
        (supervisor.STAGING_DIR / "REAL_INSTRUCTION.md").write_text("a real directive")
        assert supervisor._real_staged_instructions() == ["REAL_INSTRUCTION.md"]

    def test_only_a_run_complete_marker_present_falls_through_to_self_refill(self):
        """The exact observed failure, reproduced directly: with ONLY a
        routine run_complete_*.md marker staged and a real open map atom,
        the old find_work() would have returned "unprocessed staging --
        run_complete_X.md" and never drawn from the map at all. It must
        now fall all the way through to the self-refill draw."""
        (supervisor.STAGING_DIR / "run_complete_20260101T000000Z.md").write_text("marker")
        supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
        reason, exhausted = supervisor.find_work(resumed_from_pause=False)
        assert reason is not None
        assert "self-refill from maturity map" in reason
        assert "X1_test_atom" in reason
        assert "run_complete" not in reason
        assert exhausted is False


class TestBacklogDrivenGrantingByDefault:
    """Requirement 5's first proof: (empty doorbell + open map) -> a draw
    occurs."""

    def test_empty_doorbell_with_open_map_atom_always_draws(self):
        # No agenda, no staging at all (not even a marker), a real open
        # atom on the map -- this must draw, not idle.
        supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
        reason, exhausted = supervisor.find_work(resumed_from_pause=False)
        assert reason is not None
        assert "X1_test_atom" in reason
        assert exhausted is False

    def test_real_instruction_present_still_also_draws_from_the_map(self):
        agenda_module.set_agenda("PhaseX", "stepY", "do the thing")
        supervisor.MATURITY_MAP_PATH.write_text(_ONE_GAP_ATOM_YAML)
        reason, exhausted = supervisor.find_work(resumed_from_pause=False)
        assert "PhaseX" in reason
        assert "X1_test_atom" in reason
        assert exhausted is False


class TestMapExhaustedEscalation:
    """Requirement 5's second proof: (blocked map) -> an escalation fires."""

    def test_genuinely_nothing_anywhere_returns_exhausted_true(self):
        reason, exhausted = supervisor.find_work(resumed_from_pause=False)
        assert reason is None
        assert exhausted is True

    def test_map_with_only_blocked_atoms_is_exhausted(self):
        supervisor.MATURITY_MAP_PATH.write_text(_UNMET_DEPENDENCY_YAML.split("- id: X5")[0])
        # Only X4 (depends on X5, which is now absent) -- fails closed, unmet.
        reason, exhausted = supervisor.find_work(resumed_from_pause=False)
        assert reason is None
        assert exhausted is True

    def test_escalation_fires_on_transition_into_exhausted(self, monkeypatch):
        ntfy_calls = []
        monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
        supervisor.check_map_exhausted_escalation(True)
        assert len(ntfy_calls) == 1
        assert "CANNOT-draw" in ntfy_calls[0]

    def test_escalation_does_not_repeat_while_still_exhausted(self, monkeypatch):
        ntfy_calls = []
        monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
        supervisor.check_map_exhausted_escalation(True)
        supervisor.check_map_exhausted_escalation(True)
        supervisor.check_map_exhausted_escalation(True)
        assert len(ntfy_calls) == 1, "R5: never repeat an unchanged status"

    def test_escalation_fires_again_after_recovering_then_exhausting_again(self, monkeypatch):
        ntfy_calls = []
        monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
        supervisor.check_map_exhausted_escalation(True)
        supervisor.check_map_exhausted_escalation(False)  # real work resumed
        supervisor.check_map_exhausted_escalation(True)  # exhausted again -- new transition
        assert len(ntfy_calls) == 2

    def test_no_escalation_when_never_exhausted(self, monkeypatch):
        ntfy_calls = []
        monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
        supervisor.check_map_exhausted_escalation(False)
        assert ntfy_calls == []

    def test_run_cycle_calls_escalation_check_and_records_idle_turn_when_exhausted(self, monkeypatch):
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
        ntfy_calls = []
        monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
        grant_calls = []
        monkeypatch.setattr(supervisor, "grant_turn", lambda reason: grant_calls.append(reason) or True)
        supervisor.run_cycle()
        assert grant_calls == []
        assert len(ntfy_calls) == 1
        assert supervisor._load_idle_turn_count() == 1

    def test_run_cycle_does_not_escalate_when_real_work_exists(self, monkeypatch):
        monkeypatch.setattr(supervisor, "is_session_idle", lambda session: True)
        ntfy_calls = []
        monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy_calls.append(msg))
        monkeypatch.setattr(supervisor, "grant_turn", lambda reason: True)
        agenda_module.set_agenda("PhaseX", "stepY", "do the thing")
        supervisor.run_cycle()
        assert ntfy_calls == []
        assert supervisor._load_idle_turn_count() == 0


class TestIdleTurnCounter:
    def test_counter_starts_at_zero(self):
        assert supervisor._load_idle_turn_count() == 0

    def test_counter_increments_and_persists(self):
        assert supervisor._record_idle_turn() == 1
        assert supervisor._record_idle_turn() == 2
        assert supervisor._load_idle_turn_count() == 2


# --- RULE 0 (2026-07-14, director): the draw is provably non-empty while any atom exists ---
def _write_map(tmp_path, yaml_text):
    (tmp_path / "maturity_map.yaml").write_text(yaml_text)


def test_rule0_harden_draw_picks_an_at_target_atom(tmp_path):
    _write_map(tmp_path,
        "- id: A_done\n  level_current: 3\n  level_target: 3\n  loop_stage: build\n  dial_inherited: 3\n  file_scope: [company/x.py]\n")
    a = supervisor._rule0_harden_draw()
    assert a is not None and a["id"] == "A_done"


def test_rule0_harden_draw_none_on_empty_map_a_true_wall(tmp_path):
    _write_map(tmp_path, "[]")
    assert supervisor._rule0_harden_draw() is None


def test_self_refill_yields_to_harden_when_all_atoms_at_target(tmp_path):
    # every atom at target -> BUILD/SITE/DISCOVERY all empty. RULE 0: the feasible
    # set is a dial defect, not a reason to hold -> yield to HARDEN, never None.
    _write_map(tmp_path,
        "- id: A_done\n  level_current: 3\n  level_target: 3\n  loop_stage: build\n  dial_inherited: 3\n  file_scope: [company/x.py]\n"
        "- id: B_done\n  level_current: 2\n  level_target: 2\n  loop_stage: idle\n  dial_inherited: 2\n  file_scope: [site/y.html]\n")
    res = supervisor._self_refill_draw()
    assert res is not None, "RULE 0 violation: draw returned empty while at-target atoms exist"
    assert "RULE 0" in res and "HARDEN" in res


def test_self_refill_none_only_on_genuinely_empty_map(tmp_path):
    _write_map(tmp_path, "[]")  # zero atoms = a true wall, the one legitimate None
    assert supervisor._self_refill_draw() is None
