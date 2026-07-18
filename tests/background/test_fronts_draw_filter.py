"""Self-Governance Scope Model — sub-step 5: the supervisor BUILD-draw filter.

The filter is PREVENTION (read-side): the compliant loop never even DRAWS a gated/off-front atom
for BUILD. Two invariants proven here:
  1. DORMANT/SAFE by default — with the enforcement flag ABSENT (the state through sub-steps 1-5),
     `_maturity_map_draw_concurrent` is byte-for-byte unchanged (this is why the live supervisor is
     safe without a restart, and why every existing supervisor test stays green).
  2. When enforcement IS enabled and both fronts are HELD, the BUILD candidate set empties — but the
     DISCOVER/FRAME and SITE lanes are separate functions, untouched, so there is no idle-stall.
"""
from __future__ import annotations

import pytest

from background import supervisor
from background import fronts_reconciler as FR


_BUILD_ATOM_IN_HELD_FRONT = """\
- id: X1_weather_build
  name: "a build-stage atom inside the (HELD) SIM_ACTORS front"
  lane: W1_market_weather
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: build
- id: X2_idle_discover
  name: "an idle atom with real DISCOVER/FRAME work"
  lane: Z_some_lane
  dial_inherited: 3
  level_current: 0
  level_target: 2
  loop_stage: idle
"""


@pytest.fixture(autouse=True)
def _iso(tmp_path, monkeypatch):
    import yaml as _yaml
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "map.yaml")
    monkeypatch.setattr(supervisor, "LOG_FILE", tmp_path / "log.md")
    (tmp_path / "map.yaml").write_text(_BUILD_ATOM_IN_HELD_FRONT)
    # SYNTHETIC fronts manifest: reuse the REAL structure (lanes/gates) but force both fronts HELD,
    # so these HELD-posture invariants are tested DETERMINISTICALLY regardless of the LIVE fronts
    # state (the director opened both on 2026-07-18). Posture tests use synthetic manifests — the
    # project's standing discipline (a live-state assertion is brittle by construction).
    _real = _yaml.safe_load(FR.FRONTS_PATH.read_text())
    for _f in _real.get("fronts", []):
        _f["state"] = "held"
        _f["opened_by"] = None
    _syn = tmp_path / "fronts.yaml"
    _syn.write_text(_yaml.safe_dump(_real))
    monkeypatch.setattr(FR, "FRONTS_PATH", _syn)
    # point the enforcement flag at a tmp path so the test controls it (default: absent = dormant)
    monkeypatch.setattr(FR, "FRONTS_ENFORCEMENT_FLAG", tmp_path / ".fronts_enforcement_enabled")
    yield


def test_draw_is_DORMANT_when_flag_absent(tmp_path):
    # flag file absent -> filter is a no-op -> the build atom is drawn exactly as before
    assert FR.fronts_enforcement_enabled() is False
    drawn = supervisor._maturity_map_draw_concurrent()
    assert [a["id"] for a in drawn] == ["X1_weather_build"]


def test_enforcement_on_both_fronts_HELD_empties_BUILD(tmp_path):
    # enable enforcement -> the build atom (SIM_ACTORS is HELD, no BUILD_OPEN) is filtered OUT
    (tmp_path / ".fronts_enforcement_enabled").write_text("on")
    assert FR.fronts_enforcement_enabled() is True
    drawn = supervisor._maturity_map_draw_concurrent()
    assert drawn == []


def test_DISCOVER_lane_still_draws_when_BUILD_is_empty(tmp_path):
    # the CRITICAL no-idle-stall property: with BUILD emptied by the filter, the idle DISCOVER/FRAME
    # draw is a SEPARATE function and is untouched -> it still finds the idle atom.
    (tmp_path / ".fronts_enforcement_enabled").write_text("on")
    assert supervisor._maturity_map_draw_concurrent() == []          # BUILD empty
    idle = supervisor._idle_discover_frame_draw()                    # DISCOVER lane unaffected
    assert idle is not None and idle["id"] == "X2_idle_discover"
