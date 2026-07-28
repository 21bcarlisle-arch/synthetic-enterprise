"""Render-side + coherence tests for the wholesale-price-formation knowledge page.

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published
site/data/knowledge_wholesale.json the page consumes, then assert the produced
HTML contains the actual source values -- the rendered pixel, not the source
string.

R15 (a control must be able to FAIL): mutation tests below prove each control
fires on its own named defect -- a changed figure changes the rendered pixel
(the render is data-driven, not a hard-coded constant); the "related topics"
sidebar tracks the typed edges (not hand-authored); and the three coherence
checks (one canonical page, no orphan edge targets, acyclic prerequisites) each
red on an injected duplicate / orphan / cycle.
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
DATA = HERE.parent.parent / "data" / "knowledge_wholesale.json"

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
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- data shape

def test_data_wellformed():
    d = _live()
    assert d["meta"]["topic_id"] == "wholesale-price-formation"
    # the six explanatory rungs are all present and non-empty
    for k in ("headline", "plain", "theory", "expected_shape", "live_evidence", "residuals"):
        assert d["rungs"].get(k), f"missing rung {k}"
    assert d["rungs"]["plain"]["body"], "plain explanation must have body paragraphs"
    assert d["rungs"]["theory"]["figures"], "theory needs cited figures"
    for f in d["rungs"]["theory"]["figures"]:
        assert f["class"] in ("Fact", "Choice", "Wiring"), f"figure {f['id']} bad class"
        assert f["citation"], f"Fact figure {f['id']} needs a citation"


def test_claim_classes_present_everywhere():
    """Every figure/band/residual carries a claim class (Fact/Choice/Wiring)."""
    d = _live()
    classed = (
        d["rungs"]["theory"]["figures"]
        + d["rungs"]["expected_shape"]["bands"]
        + d["rungs"]["residuals"]["items"]
    )
    for c in classed:
        assert c["class"] in ("Fact", "Choice", "Wiring"), c


def test_both_staleness_dimensions_present():
    d = _live()
    assert d["meta"]["data_freshness"]["as_of"]
    assert d["meta"]["claim_freshness"]["last_verified"]


# ---------------------------------------------------------------- R11 render

def test_headline_and_plain_render_to_pixel():
    d = _live()
    out = _render(d)
    # the one-sentence headline claim renders into the hero one-liner
    assert _esc(d["meta"]["one_line"]) in out["hero-one"]["innerHTML"]
    for para in d["rungs"]["plain"]["body"]:
        assert _esc(para) in out["r-plain"]["innerHTML"]


def test_theory_figures_render_with_values_and_citations():
    d = _live()
    out = _render(d)
    for f in d["rungs"]["theory"]["figures"]:
        assert _esc(f["value"]) in out["r-theory"]["innerHTML"], f
        assert _esc(f["citation"]) in out["r-theory"]["innerHTML"], f


def test_expected_shape_and_residuals_render():
    d = _live()
    out = _render(d)
    for b in d["rungs"]["expected_shape"]["bands"]:
        assert _esc(b["shape"]) in out["r-expected"]["innerHTML"]
    for it in d["rungs"]["residuals"]["items"]:
        assert _esc(it["text"]) in out["r-residuals"]["innerHTML"]


def test_revision_renders_both_clocks_and_struck_old_claim():
    d = _live()
    out = _render(d)
    html = out["revision"]["innerHTML"]
    assert "rev-old" in html and _esc(d["revision"]["old_claim"]) in html
    assert _esc(d["revision"]["new_claim"]) in html
    assert _esc(d["revision"]["valid_time"]) in html
    assert _esc(d["revision"]["transaction_time"]) in html


# ---------------------------------------------------------------- R15 mutation

def test_figure_mutation_changes_rendered_pixel():
    """Independence: the render is data-driven, not a hard-coded constant."""
    d = _live()
    base = _render(d)["r-theory"]["innerHTML"]
    mut = copy.deepcopy(d)
    mut["rungs"]["theory"]["figures"][0]["value"] = "~99% MUTANT"
    after = _render(mut)["r-theory"]["innerHTML"]
    assert base != after
    assert "~99% MUTANT" in after


def test_sidebar_is_generated_from_edges_not_hardauthored():
    """Remove an edge -> the related-topics sidebar loses exactly that neighbour."""
    d = _live()
    base = _render(d)["sidebar"]["innerHTML"]
    assert "hedging-forward-market" in base  # a prerequisite-for neighbour of this topic
    mut = copy.deepcopy(d)
    mut["edges"] = [e for e in mut["edges"] if e.get("to") != "hedging-forward-market"]
    after = _render(mut)["sidebar"]["innerHTML"]
    assert "hedging-forward-market" not in after
    assert base != after


# ---------------------------------------------------------------- coherence (DoD 5)

def _prereq_has_cycle(edges) -> bool:
    graph = {}
    for e in edges:
        if e["type"] == "prerequisite-for":
            graph.setdefault(e["from"], []).append(e["to"])
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {}

    def visit(n):
        colour[n] = GREY
        for m in graph.get(n, []):
            c = colour.get(m, WHITE)
            if c == GREY:
                return True
            if c == WHITE and visit(m):
                return True
        colour[n] = BLACK
        return False

    return any(colour.get(n, WHITE) == WHITE and visit(n) for n in list(graph))


def test_exactly_one_canonical_page():
    d = _live()
    pages = [t for t in d["topics"] if t.get("kind") == "page"]
    assert len(pages) == 1, "exactly one canonical page per topic"
    # mutation: a duplicate canonical page must red this check
    mut = copy.deepcopy(d)
    mut["topics"].append({"id": "wholesale-price-formation", "title": "dup", "kind": "page"})
    dup_pages = [t for t in mut["topics"] if t.get("kind") == "page"]
    assert len(dup_pages) != 1


def test_no_orphan_edge_targets():
    d = _live()
    ids = {t["id"] for t in d["topics"]}
    for e in d["edges"]:
        assert e["from"] in ids, f"orphan edge source {e['from']}"
        assert e["to"] in ids, f"orphan edge target {e['to']}"
    # mutation: an edge to a non-existent topic must red this check
    mut = copy.deepcopy(d)
    mut["edges"].append({"from": "wholesale-price-formation", "type": "drives", "to": "ghost-topic"})
    orphaned = any(e["to"] not in ids for e in mut["edges"])
    assert orphaned


def test_prerequisite_edges_acyclic():
    d = _live()
    assert not _prereq_has_cycle(d["edges"]), "prerequisite-for chain must be acyclic"
    # mutation: an injected cycle must be detected
    mut_edges = copy.deepcopy(d["edges"]) + [
        {"from": "hedging-forward-market", "type": "prerequisite-for", "to": "wholesale-price-formation"}
    ]
    assert _prereq_has_cycle(mut_edges)


def test_edge_types_in_declared_vocabulary():
    d = _live()
    vocab = {"part-of", "mechanism-of", "drives", "governed-by", "prerequisite-for",
             "modelled-by", "touched-by"}
    for e in d["edges"]:
        assert e["type"] in vocab, f"undeclared edge type {e['type']}"
