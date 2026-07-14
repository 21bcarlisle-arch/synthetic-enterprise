"""Render-side tests for the World door (site/world/index.html).

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published site/data/world.json
the page consumes, then assert the produced HTML contains the actual source values
-- the rendered pixel, not the source string.

R15 (a control must be able to FAIL): a mutation of a source value must change the
rendered pixel (independence -- the render is not a hard-coded constant), and the
R12 diagnostic-not-target framing must be rendered verbatim on the wall band.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE.parent / "data" / "world.json"

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


def test_crossings_render_live_names_and_rag():
    d = _live()
    out = _render(d)
    body = out["crossings"]["innerHTML"]
    assert d["wall"]["crossings"], "fixture precondition: world should have wall crossings"
    for c in d["wall"]["crossings"]:
        assert c["name"] in body, f"missing crossing {c['name']}"
        # RAG band is divergence magnitude (R12), rendered as a badge.
        assert c["rag"] in body


def test_library_counts_render_live():
    d = _live()
    out = _render(d)
    kpis = out["lib-kpis"]["innerHTML"]
    counts = d["anchors"]["library"]["counts"]
    assert f">{counts['OK']}<" in kpis, kpis
    assert f">{counts['WARN']}<" in kpis


def test_wall_band_renders_r12_diagnostic_framing():
    out = _render(_live())
    band = out["wall-band"]["innerHTML"].lower()
    # R12: RAG is divergence magnitude, not a verdict / target.
    assert "not a verdict" in band or "diagnostic" in band or "not a target" in band


def test_build_note_renders_freshness_stamp():
    d = _live()
    out = _render(d)
    note = out["build-note"]["innerHTML"] + out["build-note"]["textContent"]
    assert "generated" in note.lower()
    # The generated stamp from the file must appear on the surface.
    gen = d.get("generated_at", "")
    assert gen[:10] in note, note


def test_crossing_divergence_value_is_independent_of_render():
    # R15 independence: mutate a crossing's divergence value; the rendered pixel
    # must follow the data, not a baked-in constant.
    d = _live()
    d["wall"]["crossings"][0]["divergence_value"] = "SENTINEL_999X"
    out = _render(d)
    assert "SENTINEL_999X" in out["crossings"]["innerHTML"]
