"""Render-side + coherence tests for the electricity-wholesale knowledge page.

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
    assert d["meta"]["topic_id"] == "electricity-wholesale"
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


# ------------------------------------------------ scope-delta (deliverable #5)

def test_scope_delta_present_and_maps_every_gap_to_a_brief_section():
    """The brief-vs-assembly delta exists and every named gap carries the scope-
    brief section that would close it -- the registration-by-reference that makes
    each gap a candidate piece of backlog (DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG)."""
    d = _live()
    s = d["rungs"].get("scope_delta")
    assert s and s.get("items"), "the brief-vs-assembly delta must be published"
    # the director's #1 (traded-product structure, S2) must be named and flagged highest
    s2 = [it for it in s["items"] if it["ref"] == "S2"]
    assert s2 and s2[0].get("priority"), "S2 (traded-product structure) must be named and prioritised"
    for it in s["items"]:
        assert it["ref"], "every gap maps to a scope-brief section (its backlog target)"
        assert it["status"] in ("Named gap", "Partial"), it
        assert it["text"]


def test_scope_delta_renders_every_gap_to_pixel():
    """R11: each named gap's text renders into the actual page HTML."""
    d = _live()
    out = _render(d)
    html = out["r-delta"]["innerHTML"]
    for it in d["rungs"]["scope_delta"]["items"]:
        assert _esc(it["text"]) in html, it["ref"]
        assert _esc(it["title"]) in html, it["ref"]


def test_scope_delta_mutation_changes_rendered_pixel():
    """R15: the delta render is data-driven -- a changed gap changes the pixel,
    and a removed gap disappears from the page (a control that can fail)."""
    d = _live()
    base = _render(d)["r-delta"]["innerHTML"]
    mut = copy.deepcopy(d)
    mut["rungs"]["scope_delta"]["items"][0]["text"] = "MUTANT GAP TEXT"
    after = _render(mut)["r-delta"]["innerHTML"]
    assert base != after and "MUTANT GAP TEXT" in after
    dropped = copy.deepcopy(d)
    gone = dropped["rungs"]["scope_delta"]["items"].pop()["text"]
    assert _esc(gone) not in _render(dropped)["r-delta"]["innerHTML"]


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
    mut["topics"].append({"id": "electricity-wholesale", "title": "dup", "kind": "page"})
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
    mut["edges"].append({"from": "electricity-wholesale", "type": "drives", "to": "ghost-topic"})
    orphaned = any(e["to"] not in ids for e in mut["edges"])
    assert orphaned


def test_prerequisite_edges_acyclic():
    d = _live()
    assert not _prereq_has_cycle(d["edges"]), "prerequisite-for chain must be acyclic"
    # mutation: an injected cycle must be detected
    mut_edges = copy.deepcopy(d["edges"]) + [
        {"from": "hedging-forward-market", "type": "prerequisite-for", "to": "electricity-wholesale"}
    ]
    assert _prereq_has_cycle(mut_edges)


def test_edge_types_in_declared_vocabulary():
    d = _live()
    vocab = {"part-of", "mechanism-of", "drives", "governed-by", "prerequisite-for",
             "modelled-by", "touched-by"}
    for e in d["edges"]:
        assert e["type"] in vocab, f"undeclared edge type {e['type']}"


# ------------------------------------------------- R11 price-series chart (deliverable 4, chart 1)
# The rung-5 chart set renders from the pipeline (real Elexon SSP history), never a static image.
# R11: assert the LIVE rendered SVG, not the source. R15: data-driven, so a changed datum changes
# the rendered pixel -- the chart cannot be a hard-coded constant.

def _rlive_html(d: dict) -> str:
    return _render(d)["r-live"]["innerHTML"]


def _path_vertices(html: str) -> int:
    import re
    m = re.search(r'<path d="([^"]+)"', html)
    return len(re.findall(r"[ML]", m.group(1))) if m else 0


def test_price_series_present_and_pipeline_sourced():
    """The live_evidence rung carries a real price series with provenance + its clock (R14)."""
    ps = _live()["rungs"]["live_evidence"]["price_series"]
    assert ps["points"], "price series must have data points"
    assert ps["unit"] == "GBP/MWh"
    assert "Elexon" in ps["source"] and "hand-drawn" in ps["source"]  # pipeline-sourced, not static
    assert ps["as_of"], "R14: a published figure carries its clock"
    # every point is a real (label, value) pair
    for p in ps["points"]:
        assert isinstance(p["v"], (int, float)) and p["t"]


def test_price_series_chart_renders_to_svg_from_data():
    """R11: the chart renders as an inline SVG whose vertex count == the pipeline point count."""
    d = _live()
    html = _rlive_html(d)
    assert 'class="pchart"' in html, "no inline SVG chart rendered on the price-formation page"
    n = len(d["rungs"]["live_evidence"]["price_series"]["points"])
    assert _path_vertices(html) == n, "rendered path is not one vertex per pipeline datum"
    # the crisis peak value renders as an annotation (the shape the section above predicts)
    peak = round(max(p["v"] for p in d["rungs"]["live_evidence"]["price_series"]["points"]))
    assert str(peak) in html
    # provenance + clock render onto the pixel
    ps = d["rungs"]["live_evidence"]["price_series"]
    assert _esc(ps["as_of"]) in html and "GBP/MWh" in html


def test_price_series_chart_is_data_driven_not_constant():
    """R15 mutation both ways: the render reads the data (a changed/added datum changes the pixel)."""
    d = _live()
    base = _rlive_html(d)
    # (a) change a value -> the rendered path changes
    mv = copy.deepcopy(d)
    mv["rungs"]["live_evidence"]["price_series"]["points"][0]["v"] = 9999.9
    assert _rlive_html(mv) != base, "changing a datum did not change the rendered chart (constant?)"
    # (b) add a point -> the vertex count grows by one (cardinality is data-driven)
    ma = copy.deepcopy(d)
    ma["rungs"]["live_evidence"]["price_series"]["points"].append({"t": "2099-01", "v": 50.0})
    assert _path_vertices(_rlive_html(ma)) == _path_vertices(base) + 1


# ------------------------------------------------- R11 merit-order chart (deliverable 4, chart 2)
# The merit-order supply curve renders from the pipeline SRMC stack
# (sim/merit_order_reconstruction.build_merit_stack) -- never a static image. R11: assert the
# LIVE rendered SVG bars, not the source. R15: data-driven, so a changed/added plant changes the
# rendered pixel; and the plant SRMCs are merit-ordered (ascending), the property the chart claims.

def _mbars(html: str) -> int:
    import re
    return len(re.findall(r'class="mbar"', html))


def test_merit_order_present_and_pipeline_sourced():
    """The live_evidence rung carries a real merit-order stack with provenance + its clock (R14)."""
    mo = _live()["rungs"]["live_evidence"]["merit_order"]
    assert mo["plants"], "merit order must have plants"
    assert mo["unit"] == "GBP/MWh"
    # pipeline-sourced, not static: cites the reconstruction engine and disavows hand-drawing
    assert "merit_order_reconstruction" in mo["source"] and "never hand-drawn" in mo["source"]
    assert mo["as_of"], "R14: a published figure carries its clock"
    # the stack is a real merit order: SRMC ascending, cheapest-first
    srmcs = [p["srmc"] for p in mo["plants"]]
    assert srmcs == sorted(srmcs), "merit order must be SRMC-ascending"
    for p in mo["plants"]:
        assert isinstance(p["srmc"], (int, float)) and isinstance(p["cap_gw"], (int, float))
        assert p["label"]


def test_merit_order_chart_renders_to_svg_from_data():
    """R11: the merit curve renders as inline SVG bars, one per pipeline plant, marginal annotated."""
    d = _live()
    html = _rlive_html(d)
    mo = d["rungs"]["live_evidence"]["merit_order"]
    n = len(mo["plants"])
    assert _mbars(html) == n, "rendered merit bars are not one per pipeline plant"
    # the marginal (price-setting) plant's SRMC renders as the annotation
    marginal = round(max(p["srmc"] for p in mo["plants"]))
    assert "marginal " + str(marginal) in html
    # caption + provenance + clock render onto the pixel
    assert _esc(mo["caption"]) in html
    assert _esc(mo["as_of"]) in html and "GBP/MWh" in html


def test_merit_order_chart_is_data_driven_not_constant():
    """R15 mutation both ways: the render reads the data (a changed/added plant changes the pixel)."""
    d = _live()
    base = _rlive_html(d)
    base_bars = _mbars(base)
    # (a) change a plant's SRMC -> the rendered bars change
    mv = copy.deepcopy(d)
    mv["rungs"]["live_evidence"]["merit_order"]["plants"][-1]["srmc"] = 9999.9
    assert _rlive_html(mv) != base, "changing a plant SRMC did not change the rendered chart (constant?)"
    # (b) add a plant -> one more bar (cardinality is data-driven)
    ma = copy.deepcopy(d)
    ma["rungs"]["live_evidence"]["merit_order"]["plants"].append(
        {"label": "extra peaker", "srmc": 12000.0, "cap_gw": 1.0}
    )
    assert _mbars(_rlive_html(ma)) == base_bars + 1


# ------------------------------------------------- R11 seasonal-shape chart (deliverable 4, chart 3)
# The seasonal shape renders from the pipeline (real Elexon SSP averaged by calendar month) -- never
# a static image. R11: assert the LIVE rendered SVG columns, not the source. R15: data-driven, so a
# changed/added month changes the rendered pixel.

def _sbars(html: str) -> int:
    import re
    return len(re.findall(r'class="sbar"', html))


def test_seasonal_present_and_pipeline_sourced():
    """The live_evidence rung carries a real month-of-year price profile with provenance + clock."""
    se = _live()["rungs"]["live_evidence"]["seasonal"]
    assert se["months"], "seasonal shape must have monthly points"
    assert len(se["months"]) == 12, "a seasonal shape is the twelve calendar months"
    assert se["unit"] == "GBP/MWh"
    assert "Elexon" in se["source"] and "never hand-drawn" in se["source"]  # pipeline-sourced
    assert se["as_of"], "R14: a published figure carries its clock"
    for m in se["months"]:
        assert isinstance(m["v"], (int, float)) and m["m"]


def test_seasonal_chart_renders_to_svg_from_data():
    """R11: the seasonal curve renders as inline SVG columns, one per calendar month, peak annotated."""
    d = _live()
    html = _rlive_html(d)
    se = d["rungs"]["live_evidence"]["seasonal"]
    assert _sbars(html) == len(se["months"]) == 12, "rendered seasonal bars are not one per month"
    peak = round(max(m["v"] for m in se["months"]))
    assert str(peak) in html, "the seasonal peak month value must render as an annotation"
    assert _esc(se["caption"]) in html
    assert _esc(se["as_of"]) in html and "GBP/MWh" in html


def test_seasonal_chart_is_data_driven_not_constant():
    """R15 mutation both ways: a changed/added month changes the rendered pixel."""
    d = _live()
    base = _rlive_html(d)
    base_bars = _sbars(base)
    mv = copy.deepcopy(d)
    mv["rungs"]["live_evidence"]["seasonal"]["months"][0]["v"] = 9999.9
    assert _rlive_html(mv) != base, "changing a month did not change the rendered chart (constant?)"
    ma = copy.deepcopy(d)
    ma["rungs"]["live_evidence"]["seasonal"]["months"].append({"m": "Xtra", "v": 10.0})
    assert _sbars(_rlive_html(ma)) == base_bars + 1


# ------------------------------------------- R11 negative-price-frequency chart (deliverable 4, chart 4)
# The negative-price frequency renders from the pipeline (share of half-hourly SSP periods below zero,
# per year) -- never a static image. R11: assert the LIVE rendered SVG columns. R15: data-driven.

def _nbars(html: str) -> int:
    import re
    return len(re.findall(r'class="nbar"', html))


def test_negative_prices_present_and_pipeline_sourced():
    """The live_evidence rung carries a real negative-price-frequency series with provenance + clock."""
    np_ = _live()["rungs"]["live_evidence"]["negative_prices"]
    assert np_["years"], "negative-price frequency must have yearly points"
    assert np_["unit"] == "% of settlement periods"
    assert "Elexon" in np_["source"] and "never hand-drawn" in np_["source"]  # pipeline-sourced
    assert np_["as_of"], "R14: a published figure carries its clock"
    for a in np_["years"]:
        assert isinstance(a["pct"], (int, float)) and a["y"]
        assert 0 <= a["pct"] <= 100


def test_negative_prices_chart_renders_to_svg_from_data():
    """R11: the frequency chart renders as inline SVG columns, one per year, peak annotated."""
    d = _live()
    html = _rlive_html(d)
    np_ = d["rungs"]["live_evidence"]["negative_prices"]
    assert _nbars(html) == len(np_["years"]), "rendered bars are not one per pipeline year"
    peak = max(a["pct"] for a in np_["years"])
    assert "{:.1f}%".format(peak) in html, "the peak-year frequency must render as an annotation"
    assert _esc(np_["caption"]) in html
    assert _esc(np_["as_of"]) in html


def test_negative_prices_chart_is_data_driven_not_constant():
    """R15 mutation both ways: a changed/added year changes the rendered pixel."""
    d = _live()
    base = _rlive_html(d)
    base_bars = _nbars(base)
    mv = copy.deepcopy(d)
    mv["rungs"]["live_evidence"]["negative_prices"]["years"][-1]["pct"] = 99.9
    assert _rlive_html(mv) != base, "changing a year did not change the rendered chart (constant?)"
    ma = copy.deepcopy(d)
    ma["rungs"]["live_evidence"]["negative_prices"]["years"].append({"y": "2099", "pct": 3.0})
    assert _nbars(_rlive_html(ma)) == base_bars + 1


# ---------------------------------------------------------- DoD gate (deliverable 4): chartless cannot ship
# The ruling's single job for this page: "an explanation of price formation without a price series, a
# merit-order stack, a seasonal shape and a negative-price frequency is not an explanation." So the
# definition-of-done gate requires ALL FOUR rung-5 charts to actually RENDER (R11: rendered pixels,
# not source data). A chartless (or partly-charted) page must NOT ship. This test lives under site/,
# so the site-lane pre-commit gate (tools/site_lane_gate.py) runs it on any change to this page's
# {index.html, data, test} -- it gates the COMMIT, and is isolated from the publish pipeline
# (tests/ only), so it can never wedge publishing on a legitimately-empty page elsewhere.

# The chart kinds the ruling requires, and the rendered marker each leaves in the live section.
_REQUIRED_CHART_MARKERS = {
    "price_series": r'<path d="',   # the price line
    "merit_order": r'class="mbar"',  # the merit-order staircase
    "seasonal": r'class="sbar"',     # the seasonal columns
    "negative_prices": r'class="nbar"',  # the negative-frequency columns
}


def _rung5_charts_missing(d: dict) -> list:
    """DoD checker: the rung-5 chart kinds that do NOT render on the page. Empty == the page ships."""
    import re
    html = _rlive_html(d)
    missing = []
    for kind, marker in _REQUIRED_CHART_MARKERS.items():
        if not re.search(marker, html):
            missing.append(kind)
    return missing


def test_dod_gate_all_four_rung5_charts_render():
    """DoD green on the real page: all four required rung-5 charts render (no missing kind)."""
    d = _live()
    assert _rung5_charts_missing(d) == [], "the price-formation page is missing a required rung-5 chart"
    # and at least four inline charts are actually on the pixel
    import re
    assert len(re.findall(r'class="pchart"', _rlive_html(d))) >= 4


def test_dod_gate_fires_on_chartless_page():
    """R15 (fires): strip the live-evidence chart data -> zero charts render -> the DoD gate reds."""
    d = _live()
    mut = copy.deepcopy(d)
    for kind in _REQUIRED_CHART_MARKERS:
        mut["rungs"]["live_evidence"].pop(kind, None)
    missing = _rung5_charts_missing(mut)
    assert set(missing) == set(_REQUIRED_CHART_MARKERS), "a chartless page must red every required chart"
    import re
    assert not re.findall(r'class="pchart"', _rlive_html(mut)), "chartless mutant still rendered a chart"


def test_dod_gate_fires_on_partly_charted_page():
    """R15 (fires, stricter): dropping ONE required chart still reds the gate -- all four are required."""
    d = _live()
    for kind in _REQUIRED_CHART_MARKERS:
        mut = copy.deepcopy(d)
        mut["rungs"]["live_evidence"].pop(kind, None)
        assert kind in _rung5_charts_missing(mut), f"dropping {kind} did not red the DoD gate"
