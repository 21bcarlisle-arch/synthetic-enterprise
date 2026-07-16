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
