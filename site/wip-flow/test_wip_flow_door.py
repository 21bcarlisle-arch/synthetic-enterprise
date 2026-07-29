"""Render-side + structure tests for the WIP + Flow door (site/wip-flow/index.html).

Atom G7_wip_cycle_time_dashboard.

R11 (verify to the rendered value): execute the page's ACTUAL inline JavaScript
(via a Node/vm harness) against the REAL published site/data/wip_flow.json the
page consumes, then assert the produced HTML contains the actual source values.

R15 (a control must be able to FAIL):
  * a mutation of a source WIP count must change the rendered pixel (independence);
  * the mobile @media(max-width:640px) pass must be present (a page missing it
    fails this test -- proven by deleting the block).

The generator itself (tools/generate_wip_flow_data.py) is also smoke-tested: it
produces the real keys from real repo data and reuses tools/effort_calibration.py
for cycle-time.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE.parent / "data" / "wip_flow.json"
PROJECT = HERE.parents[1]

NODE = shutil.which("node")


def _live() -> dict:
    return json.loads(DATA.read_text())


def _render(data: dict) -> dict:
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(data),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


# ---------------------------------------------------------------------------
# Generator: real data, real keys, reuses effort_calibration
# ---------------------------------------------------------------------------
def test_generator_produces_real_keys():
    sys.path.insert(0, str(PROJECT))
    from tools.generate_wip_flow_data import generate
    assert generate() is True
    d = _live()
    for key in ("wip", "cycle_time", "throughput", "wip_cap_principle", "dial_not_target"):
        assert key in d, f"missing top-level key {key}"
    w = d["wip"]
    for key in ("total_atoms", "by_stage", "by_lane", "concurrent_build_wip"):
        assert key in w, f"missing wip key {key}"
    assert w["total_atoms"] > 0
    # concurrent BUILD WIP is a real count, consistent with the by_stage board
    build_stage = next((s["count"] for s in w["by_stage"] if s["stage"] == "build"), None)
    assert build_stage == w["concurrent_build_wip"]


def test_cycle_time_reuses_effort_calibration():
    d = _live()
    ct = d["cycle_time"]
    assert ct["source_tool"] == "tools/effort_calibration.py"
    # R14: the clock is stated
    assert ct["basis"] == "git_commit_time_between_level_transitions"
    assert d["throughput"]["basis"] == "git_commit_time_between_level_transitions"


def test_dial_not_target_labelled():
    d = _live()
    assert "R12" in d["dial_not_target"]
    assert "DIAL" in d["dial_not_target"].upper()


# ---------------------------------------------------------------------------
# Render: rendered pixels reflect the live source (R11)
# ---------------------------------------------------------------------------
@pytest.mark.skipif(NODE is None, reason="node not available")
def test_kpis_render_live_build_wip():
    d = _live()
    out = _render(d)
    kpis = out["kpis"]["innerHTML"]
    build_wip = d["wip"]["concurrent_build_wip"]
    assert f">{build_wip}<" in kpis, kpis


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_wip_stages_render_every_stage():
    d = _live()
    out = _render(d)
    board = out["wip-stages"]["innerHTML"]
    assert d["wip"]["by_stage"], "fixture precondition: stages present"
    for s in d["wip"]["by_stage"]:
        assert s["label"] in board, f"stage {s['label']} not rendered"


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_cycle_lanes_render_live_lanes():
    d = _live()
    out = _render(d)
    html = out["cycle-lanes"]["innerHTML"]
    lanes = d["cycle_time"]["by_lane"]
    assert lanes, "fixture precondition: at least one lane with a cycle time"
    for l in lanes:
        # page HTML-escapes the label (& -> &amp;), so match the escaped form
        esc_name = l["lane_name"].replace("&", "&amp;")
        assert esc_name in html, f"cycle-time lane {l['lane_name']} not rendered"


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_principle_and_basis_render():
    d = _live()
    out = _render(d)
    assert d["wip_cap_principle"]["headline"] in out["principle-headline"]["textContent"]
    # R14 basis label surfaces on the page
    assert "R14" in out["cycle-basis"]["textContent"]


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_build_wip_is_independent_of_render():
    # R15 independence: mutate the source WIP count; the rendered pixel must follow.
    d = _live()
    d["wip"]["concurrent_build_wip"] = 8888
    out = _render(d)
    assert "8,888" in out["kpis"]["innerHTML"]


# ---------------------------------------------------------------------------
# R15 structural: mobile pass must be present (a page missing it fails here)
# ---------------------------------------------------------------------------
def test_mobile_pass_present():
    text = INDEX.read_text()
    assert "@media (max-width: 640px)" in text, "mobile pass block missing"


def test_page_is_theme_aware():
    text = INDEX.read_text()
    assert 'prefers-color-scheme: dark' in text
    assert ':root[data-theme="dark"]' in text
    assert ':root[data-theme="light"]' in text


# ---------------------------------------------------------------------------
# R15: the throughput signal must be ABLE TO FALL
#
# Class audit of G5_effort_sizing_discipline's honest-signal law, landed on the
# atom that owns the code (G7). The trailing windows were anchored on the LAST
# TRANSITION's timestamp, so once level transitions stopped, "Trailing 7 days"
# froze at its final healthy value forever -- a stalled build published the same
# throughput as a running one. These tests fail against that mutant.
# ---------------------------------------------------------------------------
def _synthetic_transitions(last_ts, n=19, spacing_hours=1):
    from tools.effort_calibration import LevelTransition
    return [
        LevelTransition(
            atom_id=f"SYNTH{i}",
            lane="H_harness",
            size=None,
            to_level=2,
            commit_sha=f"sha{i}",
            timestamp=last_ts - i * spacing_hours * 3600,
            message="synthetic",
        )
        for i in range(n)
    ]


def test_trailing_windows_decay_to_zero_when_transitions_stop():
    """MUTATION TARGET: restore `anchor = ts[-1]` in _throughput and this fails.
    19 transitions that all landed 60 days ago must report 0 in every trailing
    window -- under the old anchor they reported 19 transitions at 2.71/day."""
    sys.path.insert(0, str(PROJECT))
    from tools.generate_wip_flow_data import _throughput

    now = 1_800_000_000
    out = _throughput(_synthetic_transitions(now - 60 * 86400), now=now)

    assert out["total_transitions"] == 19, "all-time history is unaffected"
    for w in out["windows"]:
        assert w["transitions"] == 0, (
            f"trailing-{w['days']}d reported {w['transitions']} transitions for a build "
            "that has banked none for 60 days -- the window is anchored on the last "
            "transition, not the clock"
        )
        assert w["per_day"] == 0
    assert out["hours_since_last_transition"] == pytest.approx(60 * 24)


def test_trailing_windows_still_count_genuinely_recent_work():
    """Independence: the same function must NOT zero a live build -- otherwise
    the test above would pass on a function that always returns 0."""
    sys.path.insert(0, str(PROJECT))
    from tools.generate_wip_flow_data import _throughput

    now = 1_800_000_000
    out = _throughput(_synthetic_transitions(now - 3600), now=now)
    win7 = next(w for w in out["windows"] if w["days"] == 7)
    assert win7["transitions"] == 19, "19 transitions in the last 19h must be inside trailing-7d"
    assert out["hours_since_last_transition"] == pytest.approx(1.0)


def test_future_dated_commits_are_not_dropped_from_windows():
    """Clock-skew guard: commit timestamps AHEAD of `now` (backdated rebase,
    skewed clock) must still land inside the trailing windows, not vanish."""
    sys.path.insert(0, str(PROJECT))
    from tools.generate_wip_flow_data import _throughput

    now = 1_800_000_000
    out = _throughput(_synthetic_transitions(now + 2 * 86400), now=now)
    win7 = next(w for w in out["windows"] if w["days"] == 7)
    assert win7["transitions"] == 19
    assert out["hours_since_last_transition"] == 0.0


def test_window_basis_is_published_and_rendered():
    """R14: the windows carry their own clock, and the page states it."""
    d = _live()
    assert d["throughput"]["window_basis"] == (
        "trailing_windows_anchored_on_wall_clock_at_generation"
    )
    assert "hours_since_last_transition" in d["throughput"]
    assert "not from the last transition" in INDEX.read_text()


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_staleness_renders_on_the_page():
    """R11: verify to the rendered value -- staleness must reach the pixel."""
    d = _live()
    d["throughput"]["hours_since_last_transition"] = 1234.5
    out = _render(d)
    assert "1,234.5h" in out["throughput-summary"]["innerHTML"], (
        out["throughput-summary"]["innerHTML"]
    )
