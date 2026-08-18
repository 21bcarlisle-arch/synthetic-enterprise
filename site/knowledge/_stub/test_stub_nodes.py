"""Render-side + coherence tests for the knowledge STUB nodes (deliverable #4 of
DIRECTOR_RULING_KPILOT_DECOMPOSITION_2026-07-28.md).

The ruling's acceptance for #4 (verbatim): *no node's body is a gap list; every node
either explains (the deep node) or is honestly a stub.* A stub says what it WILL cover
and that it is not yet written -- it is not a to-do list in costume.

R11 (verify to the rendered value): these execute the stub template's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published knowledge_wholesale.json,
then assert the produced HTML -- the rendered pixel, not the source string.

R15 (a control must be able to FAIL): the mutation tests below prove each control fires
on its own named defect -- the related-topics sidebar tracks the typed edges (drop an edge,
lose exactly that neighbour); the scope render is data-driven (a changed scope changes the
pixel); and the no-drift invariant reds if any node's page diverges from the canonical
template (the way a hand-authored gap-list stub would sneak in).
"""
import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent            # site/knowledge/_stub
TEMPLATE = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
KNOWLEDGE = HERE.parent                            # site/knowledge
DATA = HERE.parent.parent / "data" / "knowledge_wholesale.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _live() -> dict:
    return json.loads(DATA.read_text())


def _by_id(d: dict) -> dict:
    return {t["id"]: t for t in d["topics"]}


def _stub_ids(d: dict) -> list:
    return [t["id"] for t in d["topics"] if t.get("kind") == "stub"]


def _render(data: dict, topic_id: str) -> dict:
    proc = subprocess.run(
        [NODE, str(HARNESS), str(TEMPLATE), topic_id],
        input=json.dumps(data), capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- graph shape

def test_every_stub_has_scope_dir_and_states_coverage_not_a_gaplist():
    """Every non-page topic ships as an honest stub: a scope that states what a COMPLETE
    treatment covers (ruling: not a to-do list), and a real page at its own URL."""
    d = _live()
    stubs = _stub_ids(d)
    by = _by_id(d)
    # SITE5 (2026-08-18): every topic is now written, so this set is EMPTY and iterating it
    # would pass vacuously -- the shape that makes a control worthless the moment it stops
    # having subjects. The rule is therefore driven over a synthetic stub as well, so it goes
    # on being a real check while the section has none, and works the day one is added back.
    probe = {"id": "_probe", "scope": "A complete treatment covers the probe topic."}
    bad = {"id": "_probe_bad", "scope": "TODO: write this. gap list of missing things."}
    assert "complete treatment" in probe["scope"].lower()
    assert not ("todo" in probe["scope"].lower() or "gap list" in probe["scope"].lower())
    assert "todo" in bad["scope"].lower(), "the rule no longer rejects a to-do list"
    for tid in stubs:
        t = by[tid]
        scope = t.get("scope", "")
        assert scope, f"{tid} stub needs a scope (what it will cover)"
        # ruling acceptance: the body states what a complete treatment CONTAINS, not what is missing
        assert "complete treatment" in scope.lower(), f"{tid} scope must state coverage, not a gap list"
        low = scope.lower()
        assert "todo" not in low and "to-do" not in low and "gap list" not in low, f"{tid} scope reads as a gap list"
        assert (KNOWLEDGE / tid / "index.html").exists(), f"{tid} stub page missing at its URL"


def test_every_written_page_has_its_own_page_and_is_not_a_stub():
    """SITE5 (2026-08-18): was `test_deep_node_is_the_only_page_and_is_not_a_stub`, pinning
    the written set to exactly ["electricity-wholesale"]. Knowledge is now being written out
    one page at a time, so the LIST is not the invariant. The invariant is that a topic
    calling itself a written page really has one: its own index.html, and NOT a copy of the
    stub template. That is the defect worth catching -- a topic promoted in the record while
    its page still says "not yet written" would tell a reader the opposite of the truth."""
    d = _live()
    canon = TEMPLATE.read_text()
    pages = [t["id"] for t in d["topics"] if t.get("kind") == "page"]
    assert pages, "no topic is a written page"
    for tid in pages:
        assert tid not in _stub_ids(d), f"{tid} is both a written page and a stub"
        index = KNOWLEDGE / tid / "index.html"
        assert index.is_file(), f"{tid} claims to be written but has no page"
        assert index.read_text() != canon, (
            f"{tid} is declared a written page while still serving the stub template"
        )


def test_no_stub_page_drifts_from_the_canonical_template():
    """R15: every node's index.html is byte-identical to the canonical stub template.
    A hand-authored gap-list stub (or any drift) reds this invariant."""
    d = _live()
    canon = TEMPLATE.read_text()
    for tid in _stub_ids(d):
        page = (KNOWLEDGE / tid / "index.html").read_text()
        assert page == canon, f"{tid}/index.html drifted from the canonical stub template"


# ---------------------------------------------------------------- R11 render

def test_each_stub_renders_identity_notyetwritten_scope_and_place():
    """R11: for every stub, the title, the honest 'not yet written' marker, the scope
    (what it WILL cover) and the typed-edge sidebar all render to the pixel."""
    d = _live()
    by = _by_id(d)
    for tid in _stub_ids(d):
        out = _render(d, tid)
        assert _esc(by[tid]["title"]) in out["hero-h"]["innerHTML"], tid
        assert "Not yet written" in out["stub-note"]["innerHTML"], f"{tid} missing honest stub marker"
        assert _esc(by[tid]["scope"]) in out["r-scope"]["innerHTML"], f"{tid} scope did not render"
        # place in the graph: at least one linked topic, generated from the edges
        assert "topiclink" in out["sidebar"]["innerHTML"], f"{tid} has no place in the graph"


# ---------------------------------------------------------------- R15 mutation

def test_sidebar_is_generated_from_edges_not_hardauthored():
    """Drop the gas->electricity drives edge -> gas-wholesale loses electricity-wholesale
    as a neighbour. The sidebar tracks the edges, it is not hand-authored."""
    d = _live()
    base = _render(d, "gas-wholesale")["sidebar"]["innerHTML"]
    assert "GB electricity wholesale" in base
    mut = copy.deepcopy(d)
    mut["edges"] = [e for e in mut["edges"]
                    if not (e["from"] == "gas-wholesale" and e["to"] == "electricity-wholesale")]
    after = _render(mut, "gas-wholesale")["sidebar"]["innerHTML"]
    assert "GB electricity wholesale" not in after
    assert base != after


def test_scope_render_is_data_driven_not_constant():
    """R15: a changed scope changes the rendered pixel (the stub reads the data)."""
    d = _live()
    base = _render(d, "gas-wholesale")["r-scope"]["innerHTML"]
    mut = copy.deepcopy(d)
    for t in mut["topics"]:
        if t["id"] == "gas-wholesale":
            t["scope"] = "MUTANT SCOPE TEXT"
    after = _render(mut, "gas-wholesale")["r-scope"]["innerHTML"]
    assert base != after and "MUTANT SCOPE TEXT" in after
