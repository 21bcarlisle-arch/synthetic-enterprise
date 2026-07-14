"""Render-side tests for the Glossary door (site/glossary/index.html).

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published
site/data/glossary.json the page consumes, then assert the produced HTML contains
the actual source values -- the rendered pixel, not the source string.

R15 (a control must be able to FAIL): a mutation of a source term's definition
must change the rendered pixel (independence -- the render is data-driven, not a
hard-coded constant), and the rendered count must track the data length.
"""
import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE.parent / "data" / "glossary.json"

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


def _esc(s: str) -> str:
    """Mirror the page's esc(): only &, <, > are entity-encoded."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def test_data_wellformed():
    d = _live()
    assert d["terms"], "fixture precondition: glossary should have terms"
    cat_ids = {c["id"] for c in d["categories"]}
    for t in d["terms"]:
        assert t["term"], "every term needs a name"
        assert t["definition"], f"term {t['term']} needs a definition"
        assert t["category"] in cat_ids, f"term {t['term']} has unknown category {t['category']}"


def test_every_term_and_definition_renders():
    d = _live()
    out = _render(d)
    body = out["glist"]["innerHTML"]
    for t in d["terms"]:
        assert _esc(t["term"]) in body, f"missing rendered term {t['term']}"
        # a distinctive slice of the definition survives to the pixel
        frag = _esc(t["definition"][:40])
        assert frag in body, f"missing rendered definition for {t['term']}"


def test_category_labels_and_see_links_render():
    d = _live()
    out = _render(d)
    body = out["glist"]["innerHTML"]
    labels = {c["id"]: c["label"] for c in d["categories"]}
    for t in d["terms"]:
        assert _esc(labels[t["category"]]) in body
        if t.get("see_url"):
            assert t["see_url"] in body, f"missing see link {t['see_url']}"


def test_count_tracks_data_length():
    d = _live()
    out = _render(d)
    n = len(d["terms"])
    assert f"{n} of {n}" in out["count"]["textContent"]


def test_intro_renders_from_data():
    d = _live()
    out = _render(d)
    assert d["meta"]["intro"][:30] in out["hero-p"]["textContent"]


def test_mutation_definition_changes_pixel():
    """R15: prove the render is independent of a hard-coded constant."""
    d = _live()
    base = _render(d)["glist"]["innerHTML"]
    sentinel = "ZZ_MUTATION_SENTINEL_DEFINITION_ZZ"
    mutated = copy.deepcopy(d)
    original_def = mutated["terms"][0]["definition"]
    mutated["terms"][0]["definition"] = sentinel
    out = _render(mutated)["glist"]["innerHTML"]
    assert sentinel in out, "mutated definition did not reach the pixel"
    assert original_def[:40] not in base or original_def[:40] not in out, (
        "render appears to ignore source definition (hard-coded?)"
    )


def test_mutation_count_changes_with_length():
    """R15: dropping a term must change the rendered count (not a constant)."""
    d = _live()
    n = len(d["terms"])
    mutated = copy.deepcopy(d)
    mutated["terms"] = mutated["terms"][:-1]
    out = _render(mutated)["count"]["textContent"]
    assert f"{n - 1} of {n - 1}" in out, out
    assert f"{n} of {n}" not in out
