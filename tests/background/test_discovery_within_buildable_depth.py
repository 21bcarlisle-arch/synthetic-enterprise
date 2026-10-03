"""H45: the idle discovery draw may not investigate an atom further ahead than its prerequisite
can build. `_within_buildable_depth` in `background/supervisor.py`, wired into both idle draws.

Each test names the defect it catches. The partition control comes first: a filter that holds
EVERY atom passes every "does it hold" test, so the held and the kept branch are both asserted
on one fixture before anything else is.
"""
from __future__ import annotations

import pytest

from background import supervisor


@pytest.fixture(autouse=True)
def _isolate_map(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / ".stall.json")
    return tmp_path


def _atom(aid, level, target, stage="idle", deps=()):
    row = (
        f"- id: {aid}\n  lane: H\n  dial_inherited: 1\n"
        f"  level_current: {level}\n  level_target: {target}\n  loop_stage: {stage}\n"
    )
    if deps:
        row += f"  depends_on: [{', '.join(deps)}]\n"
    return row


# ROOT is idle at 0; CHILD (0 -> 1) sits behind it. STEPPED (1 -> 2) sits behind a BUILD-stage
# prerequisite already at 2, so it is met by the level-matched rule though below its own target.
# GHOST names a prerequisite that is on no map.
_MAP = (
    _atom("ROOT", 0, 3)
    + _atom("CHILD", 0, 3, deps=["ROOT"])
    + _atom("PREREQ", 2, 3, stage="build")
    + _atom("STEPPED", 1, 3, deps=["PREREQ"])
    + _atom("GHOST", 0, 2, deps=["NOT_ON_THE_MAP"])
)


def _drawn():
    supervisor.MATURITY_MAP_PATH.write_text(_MAP)
    return {a["id"] for a in supervisor._idle_discover_frame_draw_concurrent(width=10)}


def test_the_draw_both_keeps_and_holds_on_one_map():
    """Defect: a filter that holds everything, or nothing, passes any one-sided test."""
    drawn = _drawn()
    assert {"ROOT", "STEPPED"} <= drawn
    assert not drawn & {"CHILD", "GHOST"}


def test_an_idle_prerequisite_below_the_step_holds_its_dependent():
    """Defect: the BUILD draw's idle exemption copied in -- the hole H45 names (SITE9 behind
    SITE8 behind SITE6, all idle, all offered for discovery on 2026-10-03)."""
    assert "CHILD" not in _drawn()


def test_a_prerequisite_at_the_step_level_releases_its_dependent():
    """Defect: requiring the prerequisite at its OWN target rather than at this atom's next
    level would serialise the whole chain on the last atom's target."""
    supervisor.MATURITY_MAP_PATH.write_text(_atom("ROOT", 1, 3) + _atom("CHILD", 0, 3, deps=["ROOT"]))
    assert "CHILD" in {a["id"] for a in supervisor._idle_discover_frame_draw_concurrent(width=10)}


def test_a_prerequisite_missing_from_the_map_holds_rather_than_frees():
    """Defect: `by_id.get` returning None read as met -- a typo would free any atom."""
    assert "GHOST" not in _drawn()


def test_the_single_atom_draw_applies_the_same_rule():
    """Defect: the rule wired into one of the two idle draws only -- how the pass ceiling was
    once enforced in a function no production path called."""
    supervisor.MATURITY_MAP_PATH.write_text(_atom("ROOT", 0, 3, stage="build") + _atom("CHILD", 0, 3, deps=["ROOT"]))
    assert supervisor._idle_discover_frame_draw() is None
    assert supervisor._idle_discover_frame_draw_concurrent(width=10) == []
