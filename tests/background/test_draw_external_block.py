"""H_draw_excludes_external_blocked_atoms: an atom `blocked_on` an external/director act is never
drawn (BUILD or idle-DISCOVER), and clearing the field re-admits it.

R15 mutation coverage: the exclusion must FIRE (a blocked atom, even at max dial, is not drawn) and
must be REVERSIBLE (clearing blocked_on re-admits). Without the exclusion the draws would keep
handing back a worker-complete-but-director-gated atom forever -- the treadmill this fixes.
"""
from __future__ import annotations

import pytest

from background import supervisor


@pytest.fixture(autouse=True)
def _isolate_map(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / ".stall.json")
    return tmp_path


_BLOCKED_BUILD = (
    "- id: BLOCKED_ATOM\n  lane: H\n  dial_inherited: 100\n"
    "  level_current: 0\n  level_target: 3\n  loop_stage: build\n"
    "  blocked_on: director_deploy\n"
)
_BLOCKED_IDLE = (
    "- id: BLOCKED_IDLE\n  lane: H\n  dial_inherited: 100\n"
    "  level_current: 0\n  level_target: 3\n  loop_stage: idle\n"
    "  blocked_on: director_live_run\n"
)


def test_build_draw_excludes_a_blocked_atom_even_at_max_dial():
    supervisor.MATURITY_MAP_PATH.write_text(_BLOCKED_BUILD)
    assert supervisor._maturity_map_draw() is None           # single BUILD draw: nothing
    assert supervisor._maturity_map_draw_concurrent() == []  # concurrent BUILD: nothing


def test_idle_draw_excludes_a_blocked_atom():
    supervisor.MATURITY_MAP_PATH.write_text(_BLOCKED_IDLE)
    assert supervisor._idle_discover_frame_draw() is None
    assert supervisor._idle_discover_frame_draw_concurrent(exclude_stalled=True) == []


def test_only_blocked_candidates_returns_empty_not_a_fallback_redraw():
    # THE treadmill case: the only below-target candidates are blocked -> empty, NOT re-handed.
    supervisor.MATURITY_MAP_PATH.write_text(_BLOCKED_BUILD + _BLOCKED_IDLE)
    assert supervisor._maturity_map_draw_concurrent() == []
    assert supervisor._idle_discover_frame_draw_concurrent(exclude_stalled=True) == []


def test_blocked_atom_excluded_but_open_atom_still_drawn():
    two = _BLOCKED_BUILD + (
        "- id: OPEN_BUILD\n  lane: H\n  dial_inherited: 1\n"
        "  level_current: 0\n  level_target: 3\n  loop_stage: build\n"
    )
    supervisor.MATURITY_MAP_PATH.write_text(two)
    ids = [a["id"] for a in supervisor._maturity_map_draw_concurrent()]
    assert "BLOCKED_ATOM" not in ids       # blocked excluded even at dial 100...
    assert "OPEN_BUILD" in ids               # ...while the open one still draws (selective)


def test_clearing_blocked_on_readmits_the_atom():
    supervisor.MATURITY_MAP_PATH.write_text(_BLOCKED_BUILD.replace("  blocked_on: director_deploy\n", ""))
    result = supervisor._maturity_map_draw()
    assert result is not None and "BLOCKED_ATOM" in result   # re-admitted once unblocked


def test_helper_predicate():
    assert supervisor._is_externally_blocked({"blocked_on": "x"}) is True
    assert supervisor._is_externally_blocked({"blocked_on": ""}) is False
    assert supervisor._is_externally_blocked({}) is False
