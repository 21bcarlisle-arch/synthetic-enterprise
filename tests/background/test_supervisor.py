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
from datetime import datetime, timedelta, timezone

import pytest

from background import action_needed as action_needed_module
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
    # ALWAYS-DRAWABLE LANE (HARD RULE, director console 2026-07-22): the tick
    # never rests while the forward-discovery register has work. Point the
    # register at a nonexistent tmp file so this hermetic world is EMPTY AT EVERY
    # LEVEL by default -- otherwise these unit tests leak the real (non-empty)
    # FORWARD_DISCOVERY_REGISTER.md and every "map empty -> rest/exhausted" test
    # would (correctly, per the new law) draw forward-discovery instead. Tests
    # that assert rest now genuinely have an empty authorized set at every level;
    # the forward-discovery lane itself is proven in test_forward_discovery_draw.py.
    monkeypatch.setattr(supervisor, "FORWARD_DISCOVERY_REGISTER_PATH", tmp_path / "FORWARD_DISCOVERY_REGISTER.md")
    # OPEN-CAMPAIGN LANE (SEVENTH CLASS, director ruling 2026-07-23): same isolation as the
    # forward-discovery register above -- point the campaign register at a nonexistent tmp file so
    # this hermetic world is EMPTY AT EVERY LEVEL by default; otherwise these "map empty -> rest/
    # exhausted" tests would leak the real (open SITE_V5) CAMPAIGN_REGISTER.yaml and (correctly, per
    # the new law) draw the open campaign. The lane itself is proven in test_open_campaign_draw.py.
    monkeypatch.setattr(supervisor, "CAMPAIGN_REGISTER_PATH", tmp_path / "CAMPAIGN_REGISTER.yaml")
    # DECLARED-DEFECT BACKLOG LANE (RUNG 4, director ruling 2026-07-23 WORK_IS_THE_DEFAULT): same
    # isolation as the campaign/forward-discovery registers above -- point the defect register at a
    # nonexistent tmp file so this hermetic world is EMPTY AT EVERY LEVEL by default; otherwise these
    # "map empty -> rest/exhausted" tests leak the real (open SPIKE_TAIL_SSP_RESIDUAL) register and
    # (correctly, per the rung) draw the open defect. Added when the rung landed (572fd628b) omitted
    # it, reddening 16 find_work tests. The lane itself is proven in test_defect_backlog_draw.py.
    monkeypatch.setattr(supervisor, "DECLARED_DEFECTS_REGISTER_PATH", tmp_path / "DECLARED_DEFECTS_REGISTER.yaml")
    # PUBLISH-GATE WEDGE LANE (RUNG 1, PRIORITY ZERO, director rulings 2026-07-23/24): same isolation
    # as every register above -- point the gate-state + last-tested-hash files at nonexistent tmp
    # files so this hermetic world has NO active wedge by default; otherwise these "map empty ->
    # rest/exhausted" tests leak the REAL .publish_gate_state.json (currently wedged) and (correctly,
    # per the rung) draw unwedge work instead of resting. The lane itself is proven both ways in
    # test_publish_gate_wedge_draw.py.
    monkeypatch.setattr(supervisor, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(supervisor, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    # RUNG 1b operational-red drawable (2026-07-25): isolate its state path too, else the real
    # overnight-red .operational_layer_signal.json makes every "map empty -> rest" find_work test
    # draw the persistent-red rung instead of resting.
    monkeypatch.setattr(supervisor, "OPERATIONAL_LAYER_SIGNAL_FILE", tmp_path / ".operational_layer_signal.json")
    # PLANNER REST-WITH-PROOF marker (RUNG 7, 2026-07-25): same isolation as every register/state
    # above -- point the marker at a nonexistent tmp file so this hermetic world has NO fresh rest
    # proof by default; otherwise a "map empty -> planner" test would leak the REAL
    # .planner_rest_with_proof.json (if the live planner has rested-with-proof) and (correctly, per
    # the gate) rest instead of showing the planner drawable. The gate itself is proven both ways in
    # test_planner_rung.py. Lesson (feedback_new_draw_rung_needs_fixture_isolation): every new
    # draw-rung state path must be isolated here or it reds all "map empty -> rest/mint" find_work
    # tests and wedges the next supervisor commit.
    monkeypatch.setattr(supervisor, "PLANNER_REST_PROOF_PATH", tmp_path / ".planner_rest_with_proof.json")
    monkeypatch.setattr(supervisor, "HARDEN_COOLDOWN_PATH", tmp_path / ".harden_cooldown.json")
    # Isolate the SELF_GOVERNANCE fronts-enforcement flag the same way as every
    # other live-state path above -- point it at a nonexistent tmp file so the
    # BUILD-draw fronts/gates filter is OFF for these UNIT tests (fronts
    # enforcement is a director console act, live on main since 2026-07-18;
    # this fixture predates it, so without this the draw's synthetic fixture
    # atoms -- lane L, id X1, not in any real open front -- would be filtered
    # to zero and every draw test would fail on a concern it does not test).
    # The fronts filter itself is covered independently in test_fronts_draw_filter.py.
    monkeypatch.setattr(agenda_module, "AGENDA_FILE", tmp_path / ".open_agenda.json")
    # §4 missing-WORK-THIS-CREATES-block surface (2026-07-27): run_cycle now calls
    # surface_missing_work_block_defects(), which reads/writes the action_needed register. Isolate
    # BOTH the register and its site mirror to tmp so run_cycle tests never read or mutate the REAL
    # docs/observability/action_needed_register.json or site/data/director_reserved.json
    # (feedback_new_draw_rung_needs_fixture_isolation: every new state path a cycle touches must be
    # isolated here). The surface itself is proven both ways in test_missing_work_block_surface.py.
    monkeypatch.setattr(action_needed_module, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    monkeypatch.setattr(action_needed_module, "SITE_RESERVED_PATH", tmp_path / "director_reserved.json")
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


# ── BOUNDED FAN-OUT: hard ceiling on concurrent forks (director P0, 2026-07-17) ──

_ALL12 = ["B0", "B1", "B2", "S0", "S1", "S2", "D0", "D1", "D2", "D3", "D4", "D5"]


def _stub_lanes(monkeypatch, n_build, n_site, n_disc):
    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent",
                        lambda **k: [{"id": f"B{i}"} for i in range(n_build)])
    monkeypatch.setattr(supervisor, "_site_lane_draw_concurrent",
                        lambda **k: [{"id": f"S{i}"} for i in range(n_site)])
    monkeypatch.setattr(supervisor, "_idle_discover_frame_draw_concurrent",
                        lambda **k: [{"id": f"D{i}"} for i in range(n_disc)])
    monkeypatch.setattr(supervisor, "_format_atom_draw", lambda a: a["id"])


def _forks_in(draw):
    return [x for x in _ALL12 if x in draw]


def test_self_refill_draw_bounds_fan_out_to_the_ceiling_not_twelve(monkeypatch):
    """A cycle that could raw-draw 12 forks (3 BUILD + 3 SITE + 6 DISCOVERY) is CAPPED to
    MAX_CONCURRENT_FORKS, BUILD-priority -- no 12-fork blooms. The ceiling is a BUDGET DIAL (narrowed
    3 -> 1 on 2026-08-03); this test owns the capping MECHANISM, so it PINS the dial at 3 rather than
    reading it, and stays meaningful wherever the live dial sits. MUTATION: lift the ceiling and the
    same cycle blooms back to 12, proving the cap is what bounds it (not the draw itself)."""
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 3)
    _stub_lanes(monkeypatch, 3, 3, 6)
    draw = supervisor._self_refill_draw()
    forks = _forks_in(draw)
    assert len(forks) == 3, f"expected <=3, got {len(forks)}: {forks}"
    assert set(forks) == {"B0", "B1", "B2"}                  # BUILD fills the whole budget (priority)
    assert "<=3 concurrent Agent forks" in draw              # doorbell STATES the live ceiling
    assert "merge its branch to main" in draw                # ...and the merge-or-reap lifecycle

    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 99)   # mutation: neuter the ceiling
    assert len(_forks_in(supervisor._self_refill_draw())) == 12   # -> the 12-fork bloom returns


def test_live_fork_ceiling_is_serial_and_takes_the_single_atom_fast_path(monkeypatch):
    """THE BUDGET DIAL ITSELF (director console, 2026-08-03, "fewer forks, only where genuinely
    parallel"). Guards the SHIPPED value, which the mechanism tests above deliberately pin away:
    at the live ceiling a 12-fork-eligible cycle grants exactly ONE atom, and the message is the
    plain single-atom fast path -- no THREE-LANE fan-out preamble, no per-atom fork instruction.
    If someone widens the dial back to >1 without a director decision, this fails."""
    assert supervisor.MAX_CONCURRENT_FORKS == 1, "fork fan-out is serial by director decision"
    _stub_lanes(monkeypatch, 3, 3, 6)
    draw = supervisor._self_refill_draw()
    assert _forks_in(draw) == ["B0"]                          # 12 eligible -> 1 granted
    assert "THREE-LANE" not in draw and "CONCURRENT" not in draw
    assert "one Agent fork per atom" not in draw

    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 99)   # mutation: neuter the ceiling
    assert len(_forks_in(supervisor._self_refill_draw())) == 12   # -> the 12-fork bloom returns


def test_self_refill_draw_cap_fills_across_lanes_by_priority(monkeypatch):
    """With a small BUILD lane the budget fills SITE then DISCOVERY -- still <=cap total, and the
    lowest-priority lane (DISCOVERY) is trimmed first. Pins the dial at 3 (see the mechanism note
    above): lane PRIORITY ORDER is only observable when the budget spans more than one lane."""
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 3)
    _stub_lanes(monkeypatch, 1, 3, 6)
    draw = supervisor._self_refill_draw()
    forks = _forks_in(draw)
    assert len(forks) == 3
    assert "B0" in forks and "S0" in forks and "S1" in forks   # BUILD(1) + SITE(2)
    assert "S2" not in forks and "D0" not in draw               # SITE overflow + all DISCOVERY trimmed


def test_self_refill_draw_single_atom_fast_path_unaffected_by_cap(monkeypatch):
    """The byte-for-byte single-atom BUILD message (1 <= ceiling) is untouched by the cap."""
    _stub_lanes(monkeypatch, 1, 0, 0)
    draw = supervisor._self_refill_draw()
    assert draw.startswith("self-refill from maturity map (dial-weighted):")  # the preserved fast path
    assert "THREE-LANE" not in draw


# ── Anti-livelock stall tracker ──

def test_atom_fingerprint_stable_for_unchanged_atom():
    atom = {"level_current": 2, "level_target": 3, "loop_stage": "idle", "simplifications": ["a", "b"], "expert_hour": {"last": "2026-07-12"}}
    assert supervisor._atom_fingerprint(atom) == supervisor._atom_fingerprint(dict(atom))


def test_atom_fingerprint_changes_when_simplifications_grow():
    # simplifications moved to the sibling store (retro FM-1); the map carries the
    # count, and the fingerprint keys on it (a note appended == count grows == progress).
    before = {"level_current": 2, "level_target": 3, "loop_stage": "idle", "simplifications_count": 1}
    after = {"level_current": 2, "level_target": 3, "loop_stage": "idle", "simplifications_count": 2}
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


def _stall(atom_id: str, streak: int) -> None:
    """Put an atom in the tracker at a chosen streak, through the real recorder."""
    for _ in range(streak):
        supervisor._record_atom_draw_and_check_stall(atom_id, "unchanging-fingerprint")


def test_MUTATION_an_all_stalled_set_draws_the_LEAST_stalled_not_the_whole_set():
    """The defect this tier exists for, driven through the real draw.

    MEASURED, not hypothesised: on 2026-08-19 at 16:25 UTC the live BUILD lane's pool at the
    picker was seven atoms and every one was flagged, so the old `if non_stalled:` fallback
    returned the set unranked and weighted `KNIFE3_wall_crossing_paydown` (1307 consecutive
    unchanged draws) exactly like `EP6_wall_protocol_typing` (6). The tick that measured it was
    itself the 44th draw of `H27_payment_belief_gap`, 43 recorded passes since its level moved.

    The mutation is the pre-fix behaviour: revert to returning `candidates` whole and STUCK,
    with dial 100 against the least-stalled atom's dial 1, wins the weighted pick on every seed.
    """
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: STUCK\n  lane: L\n  dial_inherited: 100\n"
        "  level_current: 1\n  level_target: 2\n"
        "- id: MOVING\n  lane: L\n  dial_inherited: 1\n"
        "  level_current: 1\n  level_target: 2\n"
    )
    _stall("STUCK", 40)
    _stall("MOVING", 2)
    assert supervisor._is_atom_stalled("STUCK") and supervisor._is_atom_stalled("MOVING")

    import random as random_module

    for seed in range(8):
        drawn = supervisor._maturity_map_draw_concurrent(
            rng=random_module.Random(seed), exclude_stalled=True
        )
        assert drawn[0]["id"] == "MOVING", (
            f"seed {seed} drew {drawn[0]['id']} -- a 40-streak atom must lose the primary pick "
            "to a 2-streak one however heavily it is dialled"
        )


def test_the_least_stalled_tier_keeps_ties_whole_and_never_zeroes_the_set():
    """Rule 0 holds STRUCTURALLY: a minimum always exists, so the set can never empty, and
    equal streaks are all kept -- the tier is an ordering, not a winner."""
    state = {
        "A": {"stalled": True, "consecutive_unchanged": 3},
        "B": {"stalled": True, "consecutive_unchanged": 3},
        "C": {"stalled": True, "consecutive_unchanged": 9},
    }
    cands = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
    kept = supervisor._prefer_least_stalled(cands, state)
    assert [a["id"] for a in kept] == ["A", "B"]
    assert supervisor._prefer_least_stalled([{"id": "C"}], state) == [{"id": "C"}]


def test_a_deprioritised_atom_rejoins_once_the_rest_catch_up_to_its_streak():
    """NOT an exclusion. The stuck atom is drawable again the moment nothing else is moving
    either -- the one condition under which drawing it again is the honest answer."""
    state = {
        "STUCK": {"stalled": True, "consecutive_unchanged": 5},
        "OTHER": {"stalled": True, "consecutive_unchanged": 2},
    }
    cands = [{"id": "STUCK"}, {"id": "OTHER"}]
    assert [a["id"] for a in supervisor._prefer_least_stalled(cands, state)] == ["OTHER"]
    state["OTHER"]["consecutive_unchanged"] = 5
    assert [a["id"] for a in supervisor._prefer_least_stalled(cands, state)] == ["STUCK", "OTHER"]


def test_tier_1_is_unchanged_whenever_any_unflagged_candidate_exists():
    """The old behaviour is preserved byte-for-byte on the path that was working: an un-flagged
    candidate wins outright, and its streak is never compared against anything."""
    state = {"FLAGGED": {"stalled": True, "consecutive_unchanged": 900}}
    cands = [{"id": "FLAGGED"}, {"id": "FRESH"}]
    assert [a["id"] for a in supervisor._prefer_least_stalled(cands, state)] == ["FRESH"]
    assert supervisor._prefer_least_stalled(cands, {}) == cands


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


# ── COMPOUNDING tie-break (ONE_FRAMEWORK §7 sub-step 2, C1/C7) ──
# Mechanises COMPOUNDING_WORK_FIRST ("work that shortens the feedback loop
# goes first") as a draw TIE-BREAK, never a gate (LAW A). R15: the control
# must be able to FAIL -- test (a) is what removing the compounding term from
# the tie-break turns RED (mutation proof); test (b) proves it is a tie-break
# not a filter (a sole non-compounding candidate is still drawn).

_EQUAL_DIAL_COMPOUNDING_PAIR_YAML = (
    # Deliberately map order: the NON-compounding atom is listed FIRST, so the
    # only reason the compounding atom is ever drawn first is the tie-break,
    # not accidental yaml order.
    "- id: PLAIN_ATOM\n  lane: L\n  dial_inherited: 3\n"
    "  level_current: 0\n  level_target: 1\n  file_scope: [company]\n"
    "- id: COMPOUND_ATOM\n  lane: L\n  dial_inherited: 3\n  compounding: true\n"
    "  level_current: 0\n  level_target: 1\n  file_scope: [company]\n"
)


def test_compounding_tiebreak_prefers_compounding_among_equal_dial():
    """(a) An equal-dial pair, one compounding, one not -> the compounding
    atom is drawn FIRST (primary) on EVERY seed. With the tie-break in place
    this is deterministic; the mutation (remove the compounding swap) makes
    the primary a ~50/50 weighted-random pick, so at least one of these seeds
    lands PLAIN_ATOM first and this assertion goes RED. Both atoms share
    file_scope, so only ONE is ever granted -- the primary IS the whole draw."""
    supervisor.MATURITY_MAP_PATH.write_text(_EQUAL_DIAL_COMPOUNDING_PAIR_YAML)
    import random as random_module
    for seed in range(30):
        rng = random_module.Random(seed)
        selected = supervisor._maturity_map_draw_concurrent(rng=rng)
        assert selected[0]["id"] == "COMPOUND_ATOM", (
            f"seed {seed}: expected the compounding atom drawn first, "
            f"got {selected[0]['id']}"
        )


def test_compounding_tiebreak_is_not_a_gate_sole_noncompounding_still_drawn():
    """(b) A sole non-compounding candidate is STILL drawn -- proving the flag
    is a TIE-BREAK on ordering, never a gate/filter that could zero the draw
    (LAW A / Rule 0). No compounding atom exists anywhere in the map here."""
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: LONELY_PLAIN\n  lane: L\n  dial_inherited: 3\n"
        "  level_current: 0\n  level_target: 1\n"
    )
    import random as random_module
    selected = supervisor._maturity_map_draw_concurrent(rng=random_module.Random(0))
    assert len(selected) == 1
    assert selected[0]["id"] == "LONELY_PLAIN"


def test_compounding_tiebreak_never_overrides_a_higher_dial():
    """LAW A guard: compounding is ONLY a tie-break among EQUAL dials -- it must
    never displace a higher-dial non-compounding atom (dial still dominates,
    the flag is a diagnostic never a target). A dial-100 plain atom beats a
    dial-1 compounding atom on every seed."""
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: HIGH_DIAL_PLAIN\n  lane: L\n  dial_inherited: 100\n"
        "  level_current: 0\n  level_target: 1\n  file_scope: [company]\n"
        "- id: LOW_DIAL_COMPOUND\n  lane: L\n  dial_inherited: 1\n  compounding: true\n"
        "  level_current: 0\n  level_target: 1\n  file_scope: [company]\n"
    )
    import random as random_module
    for seed in range(30):
        rng = random_module.Random(seed)
        selected = supervisor._maturity_map_draw_concurrent(rng=rng)
        assert selected[0]["id"] == "HIGH_DIAL_PLAIN", (
            f"seed {seed}: a lower-dial compounding atom must never displace a "
            f"higher-dial one, got {selected[0]['id']}"
        )


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
    # Owns the CONCURRENT-GRANT MESSAGE SHAPE, which only exists above a serial ceiling, so it pins
    # the budget dial at 3 (live value is 1 since 2026-08-03 -- see the fan-out ceiling tests).
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 3)
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


def test_site_lane_excludes_externally_blocked_atom():
    """R15 (both directions): a site atom blocked on a GENUINE external act -- an upstream
    real-world data gap, so a fork would find nothing to build -- is NOT drawn. Ungated means
    ignore loop_stage/epoch parking, NEVER ignore blocked_on (matches every other lane). The
    paired UNBLOCKED site atom with the same gap IS still drawn -- the fix does not over-exclude.

    2026-07-29: the block reason here used to be `director_level_up`. That block type is ABOLISHED
    (DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY items 1-3, mechanised in `_is_externally_blocked`),
    so it can no longer stand in for a genuine hold; the lane-respects-blocked_on rule under test is
    unchanged and is now exercised with a reason that is actually still blocking."""
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: SITE_BLOCKED\n  lane: H\n  dial_inherited: 3\n  loop_stage: build\n"
        "  level_current: 1\n  level_target: 3\n"
        "  blocked_on: \"awaiting a citable upstream data series (R10 data gap)\"\n"
        "  file_scope: [\"site\"]\n"
        "- id: SITE_OPEN\n  lane: H\n  dial_inherited: 3\n  loop_stage: build\n"
        "  level_current: 1\n  level_target: 3\n  blocked_on: null\n"
        "  file_scope: [\"site\"]\n"
    )
    ids = {a["id"] for a in supervisor._site_lane_draw_concurrent()}
    assert "SITE_BLOCKED" not in ids   # FIRES: ratification-blocked -> not a buildable draw
    assert "SITE_OPEN" in ids          # QUIET: an unblocked site atom is still drawn


def test_site_lane_excludes_build_in_progress_atom(tmp_path, monkeypatch):
    """R15 (both directions): a site atom a LIVE fork already owns (fresh entry in
    .build_in_progress.json) is NOT re-offered by the ungated SITE lane -- the same
    no-re-offer guard the BUILD lane has (_self_refill_draw), extended to the site
    lane so a focused SITE build (e.g. the P2 operational-window rebuild of SITE1) is
    not raced by the self-drawing scheduled loop. The paired un-owned atom IS drawn,
    so the guard does not over-exclude."""
    import json as _json
    import time as _time
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: SITE_OWNED\n  lane: H\n  dial_inherited: 3\n  loop_stage: build\n"
        "  level_current: 1\n  level_target: 3\n  file_scope: [\"site\"]\n"
        "- id: SITE_FREE\n  lane: H\n  dial_inherited: 3\n  loop_stage: build\n"
        "  level_current: 1\n  level_target: 3\n  file_scope: [\"site\"]\n"
    )
    bip = tmp_path / ".build_in_progress.json"
    bip.write_text(_json.dumps({"SITE_OWNED": _time.time()}))
    monkeypatch.setattr(supervisor, "BUILD_IN_PROGRESS_FILE", bip)
    ids = {a["id"] for a in supervisor._site_lane_draw_concurrent()}
    assert "SITE_OWNED" not in ids   # FIRES: a live fork owns it -> not re-offered
    assert "SITE_FREE" in ids         # QUIET: an un-owned site atom is still drawn


def test_self_refill_draws_all_three_lanes_even_when_build_is_non_empty(monkeypatch):
    """THE regression: with a non-empty BUILD lane, SITE and DISCOVERY MUST
    still draw in the same cycle -- the old cascade returned on BUILD and left
    both idle. One grant message carries all three clearly-labelled sections.
    Pins the budget dial at 3 -- a three-lane message needs a budget of at least three."""
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 3)
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


def test_self_refill_dedups_site_atom_out_of_discovery_lane(monkeypatch):
    """De-dup: BUILD wins over SITE wins over DISCOVERY. A site-scoped idle
    atom is a SITE atom, so it appears in the SITE section, never also in the
    DISCOVERY section (which draws idle atoms). Pins the dial at 3 -- de-dup
    ACROSS lane sections is only observable when the budget spans lanes."""
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 3)
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


def test_self_refill_site_and_discovery_draw_when_build_is_empty(monkeypatch):
    """No BUILD candidate at all, but a SITE atom and a DISCOVERY atom exist
    -- both must still draw (a gated/empty BUILD lane never idles the others).
    Pins the dial at 3: 'both lanes draw' needs a budget of at least two."""
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 3)
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
    maturity-map draw itself, never the backlog-prose fallback.

    Updated (ADVISOR_STEER 2026-07-18, item 1): find_work now has THREE states, so the invariant
    this test protects is precisely `exhausted is False` -- a real map with idle atoms is NEVER a
    false cannot-draw/WALL. A None `reason` is now legitimate IFF it is the DRAINED-AND-GATED quiet
    wait (below-target work exhausted, remainder blocked on a director act); that is a resting
    state, still `exhausted is False`, never the map-exhausted escalation. A None reason with the
    map NOT drained-and-gated would be the real defect this test guards against."""
    real_map = supervisor.PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
    supervisor.MATURITY_MAP_PATH.write_text(real_map.read_text())
    assert not supervisor.PRIORITIES_PATH.exists()
    assert list(supervisor.STAGING_DIR.glob("*")) == []
    reason, exhausted = supervisor.find_work(resumed_from_pause=False)
    assert exhausted is False                             # THE invariant: never a false cannot-draw
    if reason is None:
        # The ONLY legitimate None: a genuine drained-and-gated quiet wait, not a false WALL.
        assert supervisor._is_drained_and_gated() is True


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


# ── AT-TARGET HARDEN COOLDOWN / ROTATION MEMORY (2026-07-25, H1 HARDEN red-team) ──────────
# The 2026-07-18 red-team registered (not-then-fixed) that the at-target HARDEN draw re-offered
# the SAME atoms within a few turns -> an agent churned re-verifying atoms it verified minutes ago.
# The fix is a COOLDOWN (HARDEN is periodic, not saturating): skip an atom hardened within the
# window AND unchanged since, so the draw ROTATES -- but re-offer immediately iff it CHANGED.
_TWO_AT_TARGET_MAP = (
    "- id: A_done\n  level_current: 3\n  level_target: 3\n  loop_stage: build\n"
    "  dial_inherited: 1\n  file_scope: [company/x.py]\n"
    "- id: B_done\n  level_current: 3\n  level_target: 3\n  loop_stage: build\n"
    "  dial_inherited: 1\n  file_scope: [company/y.py]\n"
)


def _atom_from_map(tmp_path, atom_id):
    import yaml
    atoms = yaml.safe_load((tmp_path / "maturity_map.yaml").read_text())
    return next(a for a in atoms if a["id"] == atom_id)


def _stamp_cooldown(atom_id, at_iso, sha):
    supervisor.HARDEN_COOLDOWN_PATH.write_text(
        json.dumps({atom_id: {"at": at_iso, "sha": sha}}))


def test_harden_cooldown_rotates_past_recently_hardened_unchanged_atom(tmp_path):
    """ROTATION: a just-hardened, unchanged atom is skipped so the draw hands out the OTHER
    at-target atom instead of re-churning the one verified minutes ago."""
    _write_map(tmp_path, _TWO_AT_TARGET_MAP)
    stamped = supervisor.record_harden_pass("A_done")     # dogfooded stamp (real sha)
    assert stamped is not None
    for _ in range(25):                                   # weighted-random, but A is filtered out
        assert supervisor._rule0_harden_draw()["id"] == "B_done"


def test_harden_cooldown_reoffers_after_window_expires(tmp_path):
    """EXPIRY re-offers: A stamped > cooldown ago, B stamped fresh -> only A is drawable again.
    This assertion FAILS under a 'never-expires' mutation (the constant-marker defect)."""
    _write_map(tmp_path, _TWO_AT_TARGET_MAP)
    now = datetime.now(timezone.utc)
    old = (now - timedelta(hours=supervisor.HARDEN_COOLDOWN_HOURS + 1)).isoformat()
    supervisor.HARDEN_COOLDOWN_PATH.write_text(json.dumps({
        "A_done": {"at": old, "sha": supervisor._atom_content_sha(_atom_from_map(tmp_path, "A_done"))},
        "B_done": {"at": now.isoformat(), "sha": supervisor._atom_content_sha(_atom_from_map(tmp_path, "B_done"))},
    }))
    for _ in range(25):
        assert supervisor._rule0_harden_draw()["id"] == "A_done"


def test_harden_cooldown_reoffers_immediately_when_atom_changed(tmp_path):
    """CHANGED re-offers within the window: A stamped fresh but with a STALE sha (its content
    changed since -> may have regressed), B stamped fresh + correct sha -> only A is drawable.
    This is the 'a CHANGED alert re-pages at once' half; it FAILS if sha independence is dropped."""
    _write_map(tmp_path, _TWO_AT_TARGET_MAP)
    now = datetime.now(timezone.utc).isoformat()
    supervisor.HARDEN_COOLDOWN_PATH.write_text(json.dumps({
        "A_done": {"at": now, "sha": "deadbeefdeadbeef"},   # wrong sha -> content changed
        "B_done": {"at": now, "sha": supervisor._atom_content_sha(_atom_from_map(tmp_path, "B_done"))},
    }))
    for _ in range(25):
        assert supervisor._rule0_harden_draw()["id"] == "A_done"


def test_harden_cooldown_soft_fallback_never_empties_the_draw(tmp_path):
    """RULE 0 (soft dial): if EVERY at-target atom is in fresh cooldown, the draw must still
    return one -- a genuinely-empty HARDEN draw would false-trip the LOOP_BROKEN transport alarm.
    Single atom, freshly stamped + matching sha (so _harden_in_cooldown is True) -> still drawn."""
    _write_map(tmp_path,
        "- id: A_done\n  level_current: 3\n  level_target: 3\n  loop_stage: build\n"
        "  dial_inherited: 1\n  file_scope: [company/x.py]\n")
    supervisor.record_harden_pass("A_done")
    assert supervisor._harden_in_cooldown(
        _atom_from_map(tmp_path, "A_done"), supervisor._load_harden_cooldown()) is True
    assert supervisor._rule0_harden_draw()["id"] == "A_done"   # soft fallback keeps it non-empty


def test_harden_cooldown_R15_predicate_fails_on_expiry_and_change(tmp_path):
    """R15 both-ways on the predicate directly: _harden_in_cooldown must RETURN FALSE (re-offer)
    when the window has expired OR the content changed, and TRUE only when fresh + unchanged. The
    killer mutation (return True always -- a constant that never invalidates) is caught by the two
    FALSE assertions here; a fresh+unchanged TRUE assertion catches the opposite (never-suppress)."""
    _write_map(tmp_path, _TWO_AT_TARGET_MAP)
    atom = _atom_from_map(tmp_path, "A_done")
    real_sha = supervisor._atom_content_sha(atom)
    now = datetime.now(timezone.utc)
    fresh = {"A_done": {"at": now.isoformat(), "sha": real_sha}}
    expired = {"A_done": {"at": (now - timedelta(hours=99)).isoformat(), "sha": real_sha}}
    changed = {"A_done": {"at": now.isoformat(), "sha": "0000000000000000"}}
    assert supervisor._harden_in_cooldown(atom, fresh) is True       # fresh + unchanged -> suppress
    assert supervisor._harden_in_cooldown(atom, expired) is False    # expired -> re-offer
    assert supervisor._harden_in_cooldown(atom, changed) is False    # changed -> re-offer
    assert supervisor._harden_in_cooldown(atom, {}) is False         # no record -> re-offer


def test_file_scope_sha_tracks_scoped_file_contents(tmp_path):
    """The file_scope-change signal (2026-07-27 H1 red-team): _file_scope_sha flips when a scoped
    SOURCE file changes, and FAILS OPEN to '' (never spuriously suppresses) when file_scope is
    absent or no scoped file exists."""
    (tmp_path / "s.py").write_text("v1")
    a = {"id": "X", "file_scope": ["s.py"]}
    s1 = supervisor._file_scope_sha(a, root=tmp_path)
    (tmp_path / "s.py").write_text("v2 regressed")
    s2 = supervisor._file_scope_sha(a, root=tmp_path)
    assert s1 and s2 and s1 != s2                                   # content change flips the sha
    assert supervisor._file_scope_sha({"id": "Y"}, root=tmp_path) == ""             # no file_scope
    assert supervisor._file_scope_sha({"id": "Z", "file_scope": ["gone.py"]}, root=tmp_path) == ""  # missing file


def test_harden_cooldown_reoffers_when_shared_file_scope_changes(tmp_path, monkeypatch):
    """SHARED-FILE blind spot (2026-07-27 H1 self-HARDEN red-team): an atom stays fresh and its OWN
    maturity-map note is UNCHANGED, but a file in its file_scope moved since the stamp (e.g. a commit
    hardening a SIBLING atom that shares background/supervisor.py). It MUST re-offer -- the code under
    this atom's control just changed and may have regressed. R15 both ways: matching scope_sha ->
    suppress; a changed scoped file -> re-offer. Legacy records (no scope_sha) stay back-compatible.
    KILLER MUTATION: dropping the `scope_sha != _file_scope_sha(a)` re-offer makes the changed-file
    assertion return True (suppressed) -- caught here."""
    monkeypatch.setattr(supervisor, "PROJECT_DIR", tmp_path)
    (tmp_path / "s.py").write_text("v1")
    atom = {"id": "X", "level_current": 3, "level_target": 3, "loop_stage": "build",
            "dial_inherited": 1, "file_scope": ["s.py"]}
    now = datetime.now(timezone.utc)
    rec = {"at": now.isoformat(), "sha": supervisor._atom_content_sha(atom),
           "scope_sha": supervisor._file_scope_sha(atom, root=tmp_path)}
    assert supervisor._harden_in_cooldown(atom, {"X": rec}, now=now) is True    # fresh + code unchanged -> suppress
    (tmp_path / "s.py").write_text("v2 regressed")                             # file_scope code moves
    assert supervisor._harden_in_cooldown(atom, {"X": rec}, now=now) is False   # -> re-offer within window
    legacy = {"at": now.isoformat(), "sha": supervisor._atom_content_sha(atom)}  # pre-scope_sha record
    assert supervisor._harden_in_cooldown(atom, {"X": legacy}, now=now) is True  # back-compat: scope check skipped


def test_record_harden_pass_stamps_scope_sha(tmp_path, monkeypatch):
    """record_harden_pass writes the file_scope signal so the NEXT tick can detect a shared-file
    change; the atom here has a real scoped file so scope_sha is a non-empty hash."""
    monkeypatch.setattr(supervisor, "PROJECT_DIR", tmp_path)
    (tmp_path / "s.py").write_text("body")
    _write_map(tmp_path,
        "- id: A_done\n  level_current: 3\n  level_target: 3\n  loop_stage: build\n"
        "  dial_inherited: 1\n  file_scope: [s.py]\n")
    supervisor.record_harden_pass("A_done")
    rec = supervisor._load_harden_cooldown()["A_done"]
    assert rec.get("scope_sha")                                    # non-empty -> scoped file was hashed
    assert set(rec) >= {"at", "sha", "scope_sha"}


def test_harden_cooldown_fail_open_on_malformed_marker(tmp_path):
    """FAIL-TOWARD-WORK: a malformed marker file must never silence the draw -> _load returns {}
    and the draw behaves exactly as before the cooldown existed."""
    _write_map(tmp_path, _TWO_AT_TARGET_MAP)
    supervisor.HARDEN_COOLDOWN_PATH.write_text("{ not json")
    assert supervisor._load_harden_cooldown() == {}
    assert supervisor._rule0_harden_draw() is not None    # draw unaffected by the broken marker


def test_record_harden_pass_merges_and_ignores_phantom(tmp_path):
    """record_harden_pass MERGES (never clobbers a sibling's record) and never fabricates a stamp
    for an atom id absent from the map."""
    _write_map(tmp_path, _TWO_AT_TARGET_MAP)
    supervisor.record_harden_pass("A_done")
    supervisor.record_harden_pass("B_done")
    marker = supervisor._load_harden_cooldown()
    assert set(marker) == {"A_done", "B_done"}            # both present -> merge, not overwrite
    assert supervisor.record_harden_pass("GHOST_not_in_map") is None
    assert "GHOST_not_in_map" not in supervisor._load_harden_cooldown()


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


# ── §1+§3 HARDEN tier SUPPRESSED while a staged [DIRECTOR-RULING]/[STEER] is unconsumed ─────────
# DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27: reproduce the 08:23-10:25 state -- a
# HARDEN candidate (an at-target atom) AND an unconsumed staged director ruling BOTH present. The
# ruling is RUNG 1 (find_work's `primary`) and must draw within one tick (§3); re-verifying at-target
# atoms while a ruling names undone work is the busywork-bias the ruling forbids (§1: 'with ... an
# unminted ruling present, a HARDEN re-verify draw must FAIL'). Mutation-proven BOTH ways: ruling
# present -> _self_refill_draw returns None (the ruling draws alone as find_work's primary); ruling
# removed -> the HARDEN floor draws again (the floor is not broken, only correctly gated).
_ONE_AT_TARGET_HARDEN_MAP = (
    "- id: A_done\n  level_current: 3\n  level_target: 3\n  loop_stage: build\n"
    "  dial_inherited: 3\n  file_scope: [company/x.py]\n"
)


def test_harden_suppressed_while_staged_director_ruling_unconsumed(tmp_path):
    """R15 (reproduces 2026-07-27 08:23-10:25): an at-target HARDEN candidate + an unconsumed staged
    [DIRECTOR-RULING] both present -> _self_refill_draw() must NOT return a HARDEN doorbell. The
    ruling is RUNG 1; appending HARDEN as 'ALSO' is the exact busywork-bias the ruling forbids."""
    _write_map(tmp_path, _ONE_AT_TARGET_HARDEN_MAP)
    # both-ways teeth: with NO staged ruling the HARDEN floor DOES fire (the control can fire).
    assert "HARDEN" in (supervisor._self_refill_draw() or "")
    (supervisor.STAGING_DIR / "DIRECTOR_RULING_SOMETHING_2026-07-27.md").write_text(
        "# [DIRECTOR-RULING] -- names undone work\nbody"
    )
    assert supervisor._self_refill_draw() is None
    assert supervisor._unconsumed_director_ruling_or_steer() is True


def test_harden_suppression_is_content_driven_not_only_filename(tmp_path):
    """R7/content-driven: a file NOT named DIRECTOR_RULING_* but carrying a [STEER]/[DIRECTOR-RULING]
    header still suppresses HARDEN; a plain staged doc with no tag does NOT (the floor still fires)."""
    _write_map(tmp_path, _ONE_AT_TARGET_HARDEN_MAP)
    (supervisor.STAGING_DIR / "misc_note.md").write_text("just an ordinary note, no tag at all")
    assert "HARDEN" in (supervisor._self_refill_draw() or "")   # ordinary doc -> HARDEN still draws
    (supervisor.STAGING_DIR / "some_advisor_input.md").write_text(
        "# [ADVISOR-STEER] carrying the director's steer\nnames work"
    )
    assert supervisor._self_refill_draw() is None               # header alone suppresses


def test_harden_suppression_ignores_parked_and_archived_rulings(tmp_path):
    """A ruling PARKED in in_progress/ or archived to done/ is consumed -> it does NOT suppress
    HARDEN (only staging ROOT counts). Prevents a stale archived ruling silencing the floor forever
    -- the fail-safe direction is toward WORK, so a consumed ruling must not gate the treadmill."""
    _write_map(tmp_path, _ONE_AT_TARGET_HARDEN_MAP)
    for sub in ("in_progress", "done"):
        d = supervisor.STAGING_DIR / sub
        d.mkdir()
        (d / "DIRECTOR_RULING_OLD_2026-07-01.md").write_text("# [DIRECTOR-RULING] old\nx")
    assert supervisor._unconsumed_director_ruling_or_steer() is False
    assert "HARDEN" in (supervisor._self_refill_draw() or "")


def test_harden_suppression_ignores_daemon_markers(tmp_path):
    """A run_complete_*.md daemon marker in staging root is NOT a ruling -> it must not suppress the
    HARDEN floor (that marker self-processes on the daemon's own cadence, it names no undone work)."""
    _write_map(tmp_path, _ONE_AT_TARGET_HARDEN_MAP)
    (supervisor.STAGING_DIR / "run_complete_20260727T120000Z.md").write_text("routine run marker")
    assert supervisor._unconsumed_director_ruling_or_steer() is False
    assert "HARDEN" in (supervisor._self_refill_draw() or "")


# ── §2+§4 RULINGS/STEERS ARE A MINT SOURCE (DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27) ──
# §2: any ratified ruling/steer that names work is a MINT SOURCE (not only DIRECTOR_AXES). §4: the
# named work lives in a 'WORK THIS CREATES' block; a ruling arriving WITHOUT one is a defect -- say
# so, don't silently absorb. These prove the parser + the doorbell mint instruction both ways (R15).

_RULING_WITH_BLOCK = (
    "# [DIRECTOR-RULING] -- some ruling\n\nbody prose here\n\n"
    "## WORK THIS CREATES\n\n"
    "1. **First deliverable** -- do the thing.\n"
    "2. Second deliverable, lane harness.\n"
    "3. `Third` deliverable.\n\n"
    "**Acceptance:** the usual.\n"
)
_RULING_NO_BLOCK = "# [DIRECTOR-RULING] -- names work only in prose\n\ndo the merit-order thing, please.\n"


def test_work_this_creates_deliverables_parses_the_block():
    """§4 parser: the numbered/bulleted deliverables come out, emphasis stripped; a doc with NO
    block returns [] (the defect signal). R15 mutation-proven via the empty-block case below."""
    got = supervisor.work_this_creates_deliverables(_RULING_WITH_BLOCK)
    assert got == ["First deliverable -- do the thing.", "Second deliverable, lane harness.",
                   "Third deliverable."]
    assert supervisor.work_this_creates_deliverables(_RULING_NO_BLOCK) == []   # [] == §4 defect
    # R15 independence: the parser keys on the ACTUAL heading, not the mere presence of numbered
    # lines -- numbered lines with no WORK THIS CREATES heading yield [] (never fabricated work).
    assert supervisor.work_this_creates_deliverables("1. a\n2. b\n") == []


def test_ruling_mint_instruction_mints_from_block_and_flags_missing_block():
    """§2+§4 doorbell: a drawn ruling WITH a block -> 'MINT one atom per named deliverable'; a ruling
    WITHOUT a block -> the §4 DEFECT clause. A non-ruling staged doc -> None (primary byte-identical).
    Both-ways teeth: the same call fires the mint clause on the block doc and the defect on the other."""
    (supervisor.STAGING_DIR / "DIRECTOR_RULING_A_2026-07-27.md").write_text(_RULING_WITH_BLOCK)
    msg = supervisor.ruling_mint_instruction(["DIRECTOR_RULING_A_2026-07-27.md"])
    assert msg is not None and "MINT one atom per named deliverable" in msg
    assert "First deliverable" in msg and "Second deliverable" in msg
    (supervisor.STAGING_DIR / "DIRECTOR_STEER_B_2026-07-27.md").write_text(_RULING_NO_BLOCK)
    msg2 = supervisor.ruling_mint_instruction(["DIRECTOR_STEER_B_2026-07-27.md"])
    assert msg2 is not None and "DEFECT (§4)" in msg2 and "request the block" in msg2
    # a plain non-ruling doc contributes nothing -> None (so find_work's primary is unchanged)
    (supervisor.STAGING_DIR / "SOME_DOC.md").write_text("ordinary staged content, no tag")
    assert supervisor.ruling_mint_instruction(["SOME_DOC.md"]) is None


def test_ruling_steer_missing_work_block_lists_only_blockless_rulings():
    """§4 defect surface: only ruling/steer docs in the ROOT lacking a block are listed; one WITH a
    block, and a non-ruling doc, are excluded. Content-driven (a [STEER] header with no filename
    prefix still counts) -- R7."""
    (supervisor.STAGING_DIR / "DIRECTOR_RULING_HAS_BLOCK.md").write_text(_RULING_WITH_BLOCK)
    (supervisor.STAGING_DIR / "DIRECTOR_STEER_NO_BLOCK.md").write_text(_RULING_NO_BLOCK)
    (supervisor.STAGING_DIR / "plain_note.md").write_text("# [ADVISOR-STEER] header, prose only\nwork named here")
    (supervisor.STAGING_DIR / "not_a_ruling.md").write_text("ordinary doc")
    assert supervisor.ruling_steer_missing_work_block() == [
        "DIRECTOR_STEER_NO_BLOCK.md", "plain_note.md",
    ]


def test_find_work_ruling_doorbell_carries_the_mint_instruction(tmp_path):
    """Wiring: find_work's staging primary for a drawn ruling carries the §2+§4 mint instruction, so
    the granted turn mints from the block rather than merely 'processing' the ruling. A non-ruling
    staged doc keeps the plain 'unprocessed staging' primary (no mint clause) -- the common case."""
    (supervisor.STAGING_DIR / "DIRECTOR_RULING_C_2026-07-27.md").write_text(_RULING_WITH_BLOCK)
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    assert "unprocessed staging" in reason
    assert "MINT one atom per named deliverable" in reason
    # remove the ruling, stage a plain doc: primary has NO mint clause
    (supervisor.STAGING_DIR / "DIRECTOR_RULING_C_2026-07-27.md").unlink()
    (supervisor.STAGING_DIR / "SOME_DOC.md").write_text("ordinary staged content")
    reason2, _ = supervisor.find_work(resumed_from_pause=False)
    assert "unprocessed staging" in reason2 and "MINT one atom per named deliverable" not in reason2


# ── §3 RUNG-1 ORDERING at the find_work() boundary (DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE) ──
# Item 1 (landed) proves the DRAW HELPER (`_unconsumed_director_ruling_or_steer` suppresses the HARDEN
# tier of `_self_refill_draw`). §3's requirement is stated one level UP, at `find_work()` itself: "with
# a HARDEN candidate and an unconsumed staged ruling both available, the ruling must draw first" and no
# HARDEN is appended as an ALSO. This drives the REAL `find_work()` (the primary the drawn turn actually
# receives), reproducing the 2026-07-27 08:23-10:25 state at the level the user experiences it.
def test_find_work_staged_ruling_draws_before_harden_with_no_also_tail(tmp_path, monkeypatch):
    """§3 verbatim ("Rung 1 means rung 1"): given a live at-target HARDEN candidate AND an unconsumed
    staged [DIRECTOR-RULING] both present, find_work() returns the ruling's mint instruction as the
    SOLE primary -- never with an 'ALSO -- RULE 0 self-refill ... HARDEN' tail. R15 both ways: inverting
    the rung order (the item-1 suppression removed, as if reverted) makes the HARDEN ALSO tail reappear,
    so the ordering assertions have teeth. The mutation targets the ORDERING at the find_work boundary,
    NOT the helper item 1's own tests already cover."""
    _write_map(tmp_path, _ONE_AT_TARGET_HARDEN_MAP)   # one at-target atom => a live HARDEN candidate
    (supervisor.STAGING_DIR / "DIRECTOR_RULING_ORDER_2026-07-27.md").write_text(_RULING_WITH_BLOCK)
    reason, map_exhausted = supervisor.find_work(resumed_from_pause=False)
    # (a) the ruling's mint instruction IS the returned primary
    assert reason is not None and map_exhausted is False
    assert "unprocessed staging" in reason and "DIRECTOR_RULING_ORDER_2026-07-27.md" in reason
    assert "MINT one atom per named deliverable" in reason
    # (b) NO HARDEN ALSO tail -- the ruling draws ALONE (the exact 08:23-10:25 anti-pattern forbidden)
    assert "ALSO" not in reason
    assert "HARDEN" not in reason
    assert "RULE 0 self-refill" not in reason
    # R15: invert the rung order (suppression off) -> the HARDEN floor is no longer gated and find_work
    # appends it as 'ALSO -- ... HARDEN' -> assertions (b) above would FAIL. The defect is catchable.
    monkeypatch.setattr(supervisor, "_unconsumed_director_ruling_or_steer", lambda *a, **k: False)
    mutated, _ = supervisor.find_work(resumed_from_pause=False)
    assert "ALSO" in mutated and "HARDEN" in mutated


# ── DRAINED-AND-GATED quiet wait (ADVISOR_STEER_IDLE_TREADMILL..._2026-07-18, item 1) ──────────
# The mechanism: when the map is DRAINED of below-target work and the remainder is blocked on a
# director act, find_work returns a THIRD state (None, map_exhausted=False) -- a quiet wait -- so
# the pull-loop rests instead of re-offering the at-target HARDEN treadmill every ~2-min cycle
# (the [LOOP BROKEN] N-continuations / stop-hook-thrash / token-burn noise). The anti-idleness
# pressure is preserved for the REAL-work case, which never reaches the drained branch.
_ALL_AT_TARGET_MAP = (
    "- id: A_done\n  level_current: 3\n  level_target: 3\n  loop_stage: build\n"
    "  dial_inherited: 3\n  file_scope: [company/x.py]\n"
    "- id: B_done\n  level_current: 2\n  level_target: 2\n  loop_stage: idle\n"
    "  dial_inherited: 2\n  file_scope: [company/y.py]\n"
)


def test_find_work_drained_and_gated_settles_quiet_not_harden_treadmill(tmp_path):
    """STATE 1 (drained-and-gated -> quiet): every atom at target -> BUILD/SITE/DISCOVER + backlog
    all empty; the ONLY draw would be at-target HARDEN. find_work must settle QUIET (None, False),
    NOT re-offer HARDEN, and NOT report map_exhausted (a THIRD, legitimate resting state). Repeated
    calls stay quiet -- that is the whole point: the treadmill is not re-offered every cycle."""
    _write_map(tmp_path, _ALL_AT_TARGET_MAP)
    assert supervisor._is_drained_and_gated() is True
    # The low-level draw still honours Rule-0 (never-empty) -- the quiet decision is find_work's.
    assert "HARDEN" in supervisor._self_refill_draw()
    for _ in range(5):                                    # stays quiet cycle after cycle
        reason, map_exhausted = supervisor.find_work(resumed_from_pause=False)
        assert reason is None                             # no work delivered -> no HARDEN treadmill
        assert map_exhausted is False                     # NOT the loud exhausted/broken state


def test_run_cycle_drained_and_gated_does_not_count_as_idle_defect(tmp_path, monkeypatch):
    """The supervisor's escalation side must treat the quiet wait as a legitimate rest: no
    map-exhausted NTFY, no stuck escalation, and crucially NOT an increment of the anti-idleness
    idle-turn counter (whose target is ZERO). Only a genuinely-exhausted map is an idle defect."""
    _write_map(tmp_path, _ALL_AT_TARGET_MAP)
    monkeypatch.setattr(supervisor, "is_session_idle", lambda name: True)
    before = supervisor._load_idle_turn_count()
    supervisor.run_cycle()
    assert supervisor._load_idle_turn_count() == before   # a director-gated rest is NOT idleness


def test_find_work_real_below_target_work_draws_normally_not_quiet(tmp_path):
    """STATE 2 (real work exists -> draw normally): with a real below-target BUILD atom present the
    predicate is False and find_work delivers work -- anti-idleness is UNWEAKENED. This is exactly
    the state RULE 0's 'the to-do list is never empty' protects."""
    _write_map(tmp_path, _THREE_LANE_ALL_POPULATED_YAML)
    assert supervisor._is_drained_and_gated() is False
    reason, map_exhausted = supervisor.find_work(resumed_from_pause=False)
    assert reason is not None                             # work IS delivered
    assert map_exhausted is False
    assert "self-refill from maturity map" in reason      # the real THREE-LANE draw, not a rest


def test_is_drained_and_gated_R15_fires_on_its_own_defect(tmp_path, monkeypatch):
    """R15: the mechanism must be able to FAIL on its named defect -- wrongly classifying a REAL-
    work state as drained-and-gated (resting while below-target work exists = an anti-idleness
    violation). INDEPENDENCE: the honest predicate is keyed on the ACTUAL emptiness of the lanes,
    so with real below-target work it returns False and work is delivered. The killer MUTATION
    (hard-code the predicate True -- a fail-open/tautology) is OBSERVABLE: find_work then wrongly
    settles quiet instead of delivering the work that provably exists. A predicate that could not
    fail here (e.g. a constant) would be worse than none."""
    _write_map(tmp_path, _THREE_LANE_ALL_POPULATED_YAML)
    # Honest path: NOT drained (a lane is non-empty) -> work delivered. This assertion is itself
    # the R15 guard -- it FAILS under the always-True mutation.
    assert supervisor._is_drained_and_gated() is False
    reason, _ = supervisor.find_work(resumed_from_pause=False)
    assert reason is not None and "self-refill from maturity map" in reason
    # The mutation made explicit: pretend drained while real work exists -> find_work mis-quiets.
    monkeypatch.setattr(supervisor, "_is_drained_and_gated", lambda: True)
    mutated_reason, mutated_exhausted = supervisor.find_work(resumed_from_pause=False)
    assert mutated_reason is None and mutated_exhausted is False   # the defect is real and catchable


def test_find_work_new_staged_doc_wakes_even_when_drained(tmp_path):
    """Responsiveness preserved: a genuinely new signal (a staged doc) wakes the loop IMMEDIATELY
    even in a drained map, because the `primary` (staging) path is checked BEFORE the drained
    branch -- the quiet wait never swallows a real new instruction."""
    _write_map(tmp_path, _ALL_AT_TARGET_MAP)
    (supervisor.STAGING_DIR / "NEW_STEER.md").write_text("a genuinely new instruction")
    reason, map_exhausted = supervisor.find_work(resumed_from_pause=False)
    assert reason is not None and "NEW_STEER.md" in reason   # woken by the new signal, not resting
    assert map_exhausted is False


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational


# ── BUILD-IN-PROGRESS guard (2026-07-19): the self-drawing loop must not re-offer fork-owned work ──
def test_build_in_progress_ids_fresh_stale_missing_malformed(tmp_path, monkeypatch):
    import time, json
    f = tmp_path / ".build_in_progress.json"
    monkeypatch.setattr(supervisor, "BUILD_IN_PROGRESS_FILE", f)
    assert supervisor._build_in_progress_ids() == set()                       # missing -> fail-open {}
    f.write_text(json.dumps({"ATOM_X": time.time()}))
    assert supervisor._build_in_progress_ids() == {"ATOM_X"}                   # fresh -> excluded id
    f.write_text(json.dumps({"ATOM_X": time.time() - supervisor.BUILD_IN_PROGRESS_TTL_SECONDS - 10}))
    assert supervisor._build_in_progress_ids() == set()                       # stale -> fail-open (Rule 0)
    f.write_text("{not valid json")
    assert supervisor._build_in_progress_ids() == set()                       # malformed -> fail-open


def test_build_draw_excludes_in_progress_atom_R15(tmp_path, monkeypatch):
    """R15: a marked (fork-owned) atom is dropped from the BUILD draw; unmarked, it is drawn.
    MUTATION: remove the marker and the same atom reappears -- proving the guard, not the draw, excludes it."""
    import time, json
    mp = tmp_path / "map.yaml"
    mp.write_text(
        "- id: BIP_TEST_ATOM\n  name: x\n  lane: G_data_learning\n  value_stream: close_to_learn\n"
        "  epoch: 2\n  level_current: 1\n  level_target: 3\n  loop_stage: build\n  dial_inherited: 3\n"
        "  depends_on: []\n")
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", mp)
    bip = tmp_path / ".bip.json"
    monkeypatch.setattr(supervisor, "BUILD_IN_PROGRESS_FILE", bip)
    bip.write_text("{}")
    assert "BIP_TEST_ATOM" in [a.get("id") for a in supervisor._maturity_map_draw_concurrent()]
    bip.write_text(json.dumps({"BIP_TEST_ATOM": time.time()}))                 # mutation: mark in-progress
    assert "BIP_TEST_ATOM" not in [a.get("id") for a in supervisor._maturity_map_draw_concurrent()]


# ── RC3 (2026-07-19): a rested loop must WAKE on an origin-[ADVISOR-STAGED] doc, not only console ──
def _rc3_runner(mapping):
    import types
    def run(*args):
        key = ("show", args[1]) if args[0] == "show" else args[0]
        rc, out = mapping.get(key, (0, ""))
        return types.SimpleNamespace(returncode=rc, stdout=out)
    return run


def test_rc3_sync_pulls_origin_only_staging_doc(tmp_path, monkeypatch):
    """R15: an advisor doc on origin but NOT local is written into the local tree so the draw sees it.
    MUTATION target: without the sync, find_work never sees it (the real 2026-07-19 failure)."""
    sd = tmp_path / "docs" / "staging"; sd.mkdir(parents=True)
    monkeypatch.setattr(supervisor, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(supervisor, "STAGING_DIR", sd)
    monkeypatch.setattr(supervisor, "ORIGIN_STAGING_SYNC_STAMP", tmp_path / ".stamp.json")
    monkeypatch.setattr(supervisor, "log", lambda m: None)
    runner = _rc3_runner({
        "fetch": (0, ""),
        "ls-tree": (0, "docs/staging/NEW_DIRECTIVE.md\ndocs/staging/done\n"),
        ("show", "origin/main:docs/staging/NEW_DIRECTIVE.md"): (0, "the directive body"),
    })
    assert supervisor._sync_origin_staging(_runner=runner) == ["NEW_DIRECTIVE.md"]
    assert (sd / "NEW_DIRECTIVE.md").read_text() == "the directive body"


def test_rc3_sync_skips_locally_present_doc(tmp_path, monkeypatch):
    sd = tmp_path / "docs" / "staging"; sd.mkdir(parents=True)
    (sd / "ALREADY_LOCAL.md").write_text("x")
    monkeypatch.setattr(supervisor, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(supervisor, "STAGING_DIR", sd)
    monkeypatch.setattr(supervisor, "ORIGIN_STAGING_SYNC_STAMP", tmp_path / ".stamp.json")
    monkeypatch.setattr(supervisor, "log", lambda m: None)
    import types
    calls = []
    def runner(*args):
        calls.append(args)
        out = "docs/staging/ALREADY_LOCAL.md\n" if args[0] == "ls-tree" else ""
        return types.SimpleNamespace(returncode=0, stdout=out)
    assert supervisor._sync_origin_staging(_runner=runner) == []
    assert not any(a[0] == "show" for a in calls)   # never re-fetches an already-local doc


def test_rc3_sync_fail_safe_and_rate_limited(tmp_path, monkeypatch):
    import json, time, types
    sd = tmp_path / "docs" / "staging"; sd.mkdir(parents=True)
    monkeypatch.setattr(supervisor, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(supervisor, "STAGING_DIR", sd)
    stamp = tmp_path / ".stamp.json"
    monkeypatch.setattr(supervisor, "ORIGIN_STAGING_SYNC_STAMP", stamp)
    monkeypatch.setattr(supervisor, "log", lambda m: None)
    def boom(*a): raise RuntimeError("git down")
    assert supervisor._sync_origin_staging(_runner=boom) == []          # fail-safe: no exception
    stamp.write_text(json.dumps({"ts": time.time()}))
    called = []
    def runner(*a):
        called.append(a); return types.SimpleNamespace(returncode=0, stdout="")
    assert supervisor._sync_origin_staging(_runner=runner) == []        # rate-limited
    assert called == []                                                 # ...before any git call


def test_real_staged_instructions_self_recovers_misparked_in_progress(tmp_path, monkeypatch):
    """DURABLE draw-visibility fix (2026-07-20 3-hour silent stall): the draw itself SURFACES
    actionable work a worker mis-parked into in_progress/ (so the tick self-recovers), but NOT
    genuinely-blocked in_progress items. R15 both directions."""
    staging = tmp_path / "staging"
    ip = staging / "in_progress"
    ip.mkdir(parents=True)
    (ip / "MISPARK.md").write_text(
        "> **[IN-PROGRESS DISPOSITION -- worker tick]**\n"
        "> Open sub-item (DISCOVER/FRAME, authorised NOW): do the work.\n")
    (ip / "BLOCKED.md").write_text(
        "> **[IN-PROGRESS DISPOSITION -- worker tick]**\n"
        "> AWAITING DIRECTOR: reserved wiring, blocked on his act.\n")
    monkeypatch.setattr(supervisor, "STAGING_DIR", staging)
    got = supervisor._real_staged_instructions()
    assert "in_progress/MISPARK.md" in got      # FIRES: self-recovery draws it
    assert "in_progress/BLOCKED.md" not in got   # QUIET: genuinely blocked stays parked


# ═══════════════════════════════════════════════════════════════════════════════════════════
# LAW B -- LANE ISOLATION (DIRECTOR_RULING_FAILURE_BIAS_LAWS 2026-07-27)
# ═══════════════════════════════════════════════════════════════════════════════════════════
# The director's law B, verbatim: "A block in one lane may never suppress drawing or minting in
# another. Gates are per-cluster, never global." The diagnosis it fixes: a single director-held
# decision (population lambda vs N) stopped work in the site, merit-order, premise-demand and
# DD-cashflow lanes -- failure #2 was "the pending-batch gate blocked minting GLOBALLY when the
# pending batch was all-blocked, instead of per-lane."
#
# The draw ladder (_self_refill_draw) and the rest predicate (_is_drained_and_gated) are ALREADY
# per-cluster BY CONSTRUCTION: a sequential fall-through where a blocked/empty lane falls to the
# NEXT lane and never zeros its siblings; the planner (RUNG 7) rests only after PROVING no
# un-minted non-walled step exists across ALL clusters, so a single held cluster cannot suppress
# minting for the others. LAW B's contribution is to LOCK THAT ISOLATION IN as a mutation-proven
# regression guard, so a FUTURE accretion that adds a global gate (the exact class the ruling
# forbids) reds immediately instead of silently zeroing the feasible set again. This converts the
# policy "gates are per-cluster" into an enforced mechanism (MAKE_IT_STICK: prose decays, a gate
# holds). R15 both ways -- the real draw stays isolated; the modelled global-gate MUTATION reds
# the same assertion, proving the guard discriminates rather than being a tautology.


def _global_gated_draw():
    """MUTATION MODEL of the ruling's failure #2 -- a GLOBAL gate that decides the WHOLE draw off
    the LEAD (BUILD) lane, zeroing every sibling lane when BUILD is blocked/empty instead of
    falling through to SITE/DISCOVERY. If this variant and the real `_self_refill_draw` returned
    the SAME answer under a held lead lane, the isolation assertion would be a tautology; proving
    THIS returns None (a false global rest) while the real draw returns sibling work is the R15
    discriminator that makes the guard real."""
    if not supervisor._maturity_map_draw_concurrent(exclude_stalled=True):
        return None
    return supervisor._self_refill_draw()


def test_lawb_held_build_lane_leaves_siblings_drawable(monkeypatch):
    """Hold the BUILD cluster (all-blocked -> the lane draws empty) but leave SITE+DISCOVERY work:
    the real draw returns the sibling work, NOT rest -- a block in one lane never suppresses the
    others. R15 MUTATION (failure #2): the global-gate variant that reads the lead lane to decide
    the whole draw returns None (the false global rest the ruling forbids), proving the isolation
    the real draw provides is genuine and not incidental.

    LAW B is about ISOLATION (a held lane must not zero the draw), NOT about width -- so the
    invariant is asserted at the LIVE ceiling, where the budget admits only the highest-priority
    surviving sibling. The separate width case is pinned at 3 below."""
    _stub_lanes(monkeypatch, 0, 2, 3)               # BUILD held empty; siblings have work
    draw = supervisor._self_refill_draw()
    assert draw is not None                          # a held lead lane does NOT zero the draw
    assert _forks_in(draw)                           # ...and real sibling work is actually granted
    assert "S0" in draw                              # SITE (next by priority) draws despite the block
    assert _global_gated_draw() is None              # ...but the GLOBAL-gate mutation falsely rests

    # WIDTH case: given budget for more than one, the held lane's siblings BOTH draw in one cycle.
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 3)
    wide = supervisor._self_refill_draw()
    assert "S0" in wide and "D0" in wide              # SITE + DISCOVERY together despite BUILD held


def test_lawb_held_site_lane_leaves_siblings_drawable(monkeypatch):
    """Symmetric direction: a held SITE cluster leaves BUILD+DISCOVERY fully drawable -- isolation
    holds whichever single lane is the one blocked, not just the lead lane. Same split as above:
    isolation at the live ceiling, simultaneity pinned at a widened one."""
    _stub_lanes(monkeypatch, 2, 0, 3)               # SITE held empty; siblings have work
    draw = supervisor._self_refill_draw()
    assert draw is not None
    assert "B0" in draw                              # BUILD (top priority) draws despite the block

    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 3)
    wide = supervisor._self_refill_draw()
    assert "B0" in wide and "D0" in wide              # BUILD + DISCOVERY together despite SITE held


def test_lawb_held_lane_does_not_ground_rest(monkeypatch):
    """The rest predicate must AGREE with the draw: `_is_drained_and_gated` is False while ANY
    sibling lane has work, so a single held cluster can never make the WHOLE set read drained (the
    false-rest a global gate would produce). Mutation: with EVERY lane empty it returns to a rest
    verdict -- proving the predicate reads the real per-lane emptiness, not a constant."""
    _stub_lanes(monkeypatch, 0, 2, 0)               # BUILD held; SITE has work
    assert supervisor._is_drained_and_gated() is False
    _stub_lanes(monkeypatch, 0, 0, 0)               # now truly drain every lane (mutation)
    monkeypatch.setattr(supervisor, "_actionable_backlog_item", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_open_campaign_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_declared_defect_backlog_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_propose_half_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_forward_discovery_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_planner_rung_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_blocked_mints_open", lambda *a, **k: False)
    monkeypatch.setattr(supervisor, "_rule0_harden_draw", lambda *a, **k: {"id": "AT_TARGET"})
    assert supervisor._is_drained_and_gated() is True   # genuinely empty -> rest is legitimate


def test_lawb_blocked_cluster_does_not_suppress_planner_mint(tmp_path, monkeypatch):
    """LAW B on the MINT side (the ruling's failure #2): a blocked cluster must NOT globally
    suppress the planner minting for OTHER ratified clusters. Rungs 1-6 empty (the held cluster) +
    ratified axes present + no pending batch + no fresh rest-proof -> the planner MINTS, never a
    global rest. R15 MUTATION (independence): empty the ratified axes and the planner returns None
    -- proving the mint fires on real ratified content across clusters, not unconditionally."""
    _stub_lanes(monkeypatch, 0, 0, 0)               # the held cluster: nothing to build/site/discover
    monkeypatch.setattr(supervisor, "_actionable_backlog_item", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_open_campaign_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_declared_defect_backlog_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_propose_half_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_forward_discovery_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "PLANNER_RUNG_DISABLED_FLAG", tmp_path / ".no_disable_flag")
    axes = tmp_path / "DIRECTOR_AXES.md"
    axes.write_text("## v1 axes\n\n### 1. Website\n- an operational window.\n")
    monkeypatch.setattr(supervisor, "DIRECTOR_AXES_PATH", axes)
    msg = supervisor._planner_rung_draw()
    assert msg is not None and "RUNG 7 PLANNER" in msg and "MINT" in msg   # mints for other clusters
    axes.write_text("## v1 axes\n\n(no ratified axes yet)\n")               # R15 mutation: no axes
    assert supervisor._planner_rung_draw() is None                          # -> genuinely exhausted
