"""Render-side tests for the Method door (site/method/index.html).

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published site/data/method.json
the page consumes, then assert the produced HTML contains the actual source values
-- the rendered pixel, not the source string.

R15 (a control must be able to FAIL): a mutation of a source value must change the
rendered pixel (independence -- the render is not a hard-coded constant).
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE.parent / "data" / "method.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


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


def _live() -> dict:
    return json.loads(DATA.read_text())


def test_roles_render_live_operating_model():
    d = _live()
    out = _render(d)
    grid = out["role-grid"]["innerHTML"]
    roles = (d.get("operating_model") or {}).get("roles") or []
    assert roles, "fixture precondition: operating_model.roles present"
    for r in roles:
        assert r["name"] in grid, f"role {r['name']} not rendered"


def test_rules_render_every_live_rule_with_its_incident():
    d = _live()
    out = _render(d)
    grid = out["rule-grid"]["innerHTML"]
    rules = d.get("rules") or []
    assert rules, "fixture precondition: rules present"
    for r in rules:
        assert r["id"] in grid, f"rule {r['id']} not rendered"
        assert r["incident"] in grid, f"incident text for {r['id']} not rendered"
    stat = out["rules-stat"]["textContent"]
    assert str(len(rules)) in stat, stat


def test_track_record_renders_live_clock_and_counts():
    d = _live()
    out = _render(d)
    body = out["track-record-body"]["innerHTML"]
    tr = d.get("track_record") or {}
    rg = tr.get("renewal_grading") or {}
    assert tr.get("clock_started", "") in body
    assert f">{rg.get('graded_count')}<" in body


def test_retro_library_renders_live_titles():
    d = _live()
    out = _render(d)
    body = out["retro-list"]["innerHTML"]
    lib = d.get("retro_library") or []
    assert lib, "fixture precondition: retro_library present"
    for r in lib:
        assert r["title"] in body, f"retro {r['title']} not rendered"


def test_build_note_renders_freshness_stamp():
    d = _live()
    out = _render(d)
    note = out["build-note"]["textContent"]
    gen = d.get("generated_at", "")
    assert gen and gen in note, note


def test_rule_count_is_independent_of_render():
    # R15 independence: mutate a rule id/incident; the rendered pixel must follow
    # the data, not a baked-in constant.
    d = _live()
    d["rules"][0]["incident"] = "SENTINEL_999X_INCIDENT"
    out = _render(d)
    assert "SENTINEL_999X_INCIDENT" in out["rule-grid"]["innerHTML"]
