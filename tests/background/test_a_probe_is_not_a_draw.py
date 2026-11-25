"""A rest-legitimacy probe is not a draw: `_probe_only` in `background/supervisor.py`.

`_is_drained_and_gated` and `authorized_set_enumeration` ask the real draws whether work exists.
Before the fix each call bumped the drawn atom's `consecutive_unchanged` with nothing dispatched,
which is how parked atoms reached counts in the thousands (seat finding, 2026-10-07, defect 3).
"""
from __future__ import annotations

import json

import pytest

from background import supervisor


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / ".stall.json")
    supervisor.MATURITY_MAP_PATH.write_text(
        "- id: PARKED\n  lane: H\n  dial_inherited: 1\n"
        "  level_current: 0\n  level_target: 2\n  loop_stage: idle\n"
    )
    return tmp_path


def _counts() -> dict:
    path = supervisor.ATOM_STALL_STATE_FILE
    if not path.exists():
        return {}
    return {k: v.get("consecutive_unchanged") for k, v in json.loads(path.read_text()).items()}


def test_a_real_draw_counts_and_a_probe_of_the_same_draw_does_not():
    """Defect: the probe writing a draw (the pre-fix state), or the guard silencing every draw
    -- a tracker that never counts would pass any probe-only test. Both legs on one map."""
    supervisor._idle_discover_frame_draw_concurrent(exclude_stalled=True)
    assert _counts() == {"PARKED": 1}, "the real draw must still count -- the branch can be taken"

    probed = supervisor._probe_only(
        lambda: supervisor._idle_discover_frame_draw_concurrent(exclude_stalled=True))()
    assert [a["id"] for a in probed] == ["PARKED"], "the probe must still see the work"
    assert _counts() == {"PARKED": 1}

    supervisor._idle_discover_frame_draw_concurrent(exclude_stalled=True)
    assert _counts() == {"PARKED": 2}, "the probe flag leaked past the probe"


def test_both_rest_probes_are_wrapped():
    """Defect: the decorator dropped from either production probe. Each is called against a map
    whose only work is an idle atom the discovery draw selects."""
    supervisor._is_drained_and_gated()
    supervisor.authorized_set_enumeration()
    assert _counts() == {}
