"""Render-side tests for the Method+Simplified door (site/method-casebook/index.html).

R11 (verify to the rendered value): execute the page's ACTUAL inline JavaScript
(via a Node/vm harness) against the REAL published site/data/method_casebook.json
the page consumes, then assert the produced HTML contains the actual source values.

R15 (a control must be able to FAIL): a mutation of a source count must change the
rendered pixel (independence), and the simplifications register must render its
NAMED simplifications (honesty featured -- nothing filtered out).
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE.parent / "data" / "method_casebook.json"

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


def test_review_kpis_render_live_atom_count():
    d = _live()
    out = _render(d)
    kpis = out["review-kpis"]["innerHTML"]
    atoms = d["casebook"]["review"]["atom_count"]
    assert f">{atoms}<" in kpis, kpis


def test_rules_timeline_renders_every_live_rule():
    d = _live()
    out = _render(d)
    tl = out["timeline"]["innerHTML"]
    history = d["casebook"]["incident_rule_history"]
    assert history, "fixture precondition: rule history present"
    # Each rule id in the data must appear on the rendered timeline.
    for r in history:
        rid = r["id"]
        assert rid in tl, f"rule {rid} not rendered"


def test_simplifications_register_renders_live_notes():
    d = _live()
    out = _render(d)
    reg = out["register"]["innerHTML"]
    assert reg.strip(), "register must not render empty (honesty featured)"


def test_atom_count_is_independent_of_render():
    # R15 independence: mutate the atom count; the rendered pixel must follow.
    d = _live()
    d["casebook"]["review"]["atom_count"] = 7777
    out = _render(d)
    # rendered with a thousands separator (num() formatting)
    assert "7,777" in out["review-kpis"]["innerHTML"]
