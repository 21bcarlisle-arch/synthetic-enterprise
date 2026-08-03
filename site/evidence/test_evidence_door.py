"""Render-side tests for the EVIDENCE door (site/evidence/index.html) -- atom
SITE_evidence_pages_behind_nodes.

This suite tests the RENDER, not the source string: it executes the page's ACTUAL inline
JavaScript (via the Node/vm harness `_render_harness.mjs`) against the real generated data and
against synthetic mutation cases, then asserts on the produced HTML -- the rendered pixel (R11).

THE CRUX THE ATOM NAMES. Exit criterion 2 says a page of narrative DESCRIBING the evidence FAILS;
the page must render the real figures derived from primary state. So the tests below assert that
the numbers the page renders are the numbers the DERIVATION produced -- and, critically, that they
MOVE when the derivation moves (`test_rendered_figures_follow_the_data`). A page that rendered a
constant would pass a presence check and fail this one.

NEVER PIN A GENERATED VALUE (feedback_never_pin_generated_values_in_controls). Every assertion
against live data compares the rendered pixel to the value the derivation itself produced -- the
RELATIONSHIP -- never to a literal figure. A pinned figure here would wedge the publish gate the
first time an atom legitimately moved, which is precisely the 4-day blackout this project already
paid for once.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
PROJECT = HERE.parent.parent  # site/evidence -> repo root

NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(data) -> dict:
    """Run the page's own renderEvidence against `data`; return every captured element."""
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(data),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _live_data() -> dict:
    """The real data the generator emits into site/data/moap_evidence.json."""
    sys.path.insert(0, str(PROJECT))
    from tools.generate_moap_evidence_data import build_evidence_data

    return build_evidence_data()


def _grouped(v: int) -> str:
    """The page renders numbers with en-GB grouping; mirror that for comparison."""
    return f"{v:,}"


# --------------------------------------------------------------------------- #
# R11 -- the page renders the LIVE derivation's actual figures.
# --------------------------------------------------------------------------- #
def test_summary_renders_the_derived_totals():
    """Every headline figure on the page equals the figure the derivation produced -- asserted
    RELATIONALLY against the derivation, never against a pinned number."""
    d = _live_data()
    out = _render(d)
    html = out["summary"]["innerHTML"]
    for key in ("nodes", "atoms", "ledger_records", "fidelity_rows", "test_functions"):
        assert _grouped(d["totals"][key]) in html, f"{key} not rendered"


def test_every_node_renders_its_anchored_section_with_real_levels():
    """Criterion 1 + 2 at the pixel: each node renders a section AT ITS ANCHOR, and inside it the
    atoms' REAL level_current/level_target pairs from the map."""
    d = _live_data()
    html = _render(d)["nodes"]["innerHTML"]
    assert d["nodes"], "derivation produced no nodes -- nothing to assert on"
    for node in d["nodes"]:
        assert f'id="{node["anchor"]}"' in html, f'{node["id"]}: no anchored section rendered'
        assert node["name"].replace("&", "&amp;") in html
        for atom in node["atoms"]:
            assert atom["id"] in html, f'{atom["id"]}: atom row not rendered'
            pair = f'{_grouped(atom["level_current"])} / {_grouped(atom["level_target"])}'
            assert pair in html, f'{atom["id"]}: real level pair {pair} not rendered'


def test_the_suite_execution_stamp_carries_its_clock():
    """R14's discipline applied to a test count: the passing figure is rendered WITH the
    timestamp it was recorded at -- a figure without its clock is a defect."""
    d = _live_data()
    stamp = _render(d)["stamp"]["innerHTML"]
    suite = d["suite_execution"]
    if suite.get("available"):
        assert _grouped(suite["test_count"]) in stamp
        assert suite["timestamp"] in stamp
    else:
        assert "NOT RECORDED" in stamp
    assert d["generated_at_utc"] in stamp


def test_sources_are_named_on_the_page():
    """The reader can check the derivation: every primary source is named on the page itself."""
    d = _live_data()
    html = _render(d)["sources"]["innerHTML"]
    for key in ("map", "mapping", "level_ledger", "fidelity_register"):
        assert d["sources"][key] in html


def test_test_provenance_is_labelled_as_provenance_not_as_passes():
    """Honesty of the label: the per-file figure is 'test functions', and the page says the file
    NAMES the atom. It must never read as a pass count -- the passing figure is the stamp."""
    d = _live_data()
    html = _render(d)["nodes"]["innerHTML"]
    assert "test functions" in html
    assert "names " in html


# --------------------------------------------------------------------------- #
# R15 -- the render must FOLLOW the data, and fail visibly when it cannot.
# --------------------------------------------------------------------------- #
def test_rendered_figures_follow_the_data():
    """THE ANTI-CONSTANT TEST. Feed the page a second, different derivation and assert the
    rendered figures MOVED. A page rendering hand-authored prose (or a cached constant) passes
    every presence check above and fails this one."""
    d = _live_data()
    before = _render(d)["summary"]["innerHTML"]

    mutated = json.loads(json.dumps(d))
    mutated["totals"]["atoms"] = d["totals"]["atoms"] + 7
    mutated["totals"]["test_functions"] = d["totals"]["test_functions"] + 11
    after = _render(mutated)["summary"]["innerHTML"]

    assert after != before
    assert _grouped(mutated["totals"]["atoms"]) in after
    assert _grouped(mutated["totals"]["test_functions"]) in after


def test_a_claim_its_evidence_cannot_support_renders_as_a_failure():
    """R15 at the pixel: a node whose claimed stage its atoms cannot support renders the explicit
    contradiction, not a quiet green tick. The page must not launder a bad claim."""
    d = _live_data()
    mutated = json.loads(json.dumps(d))
    node = mutated["nodes"][0]
    node["claimed_stage"] = "Live"
    for row in node["atoms"]:
        row["level_current"] = 0
        row["at_target"] = False
    node["derived_stage"] = "Planned"
    node["totals"]["at_target"] = 0

    html = _render(mutated)["nodes"]["innerHTML"]
    assert "THE CLAIM IS NOT CARRIED BY THE EVIDENCE" in html
    assert 'class="derivation bad"' in html


def test_no_nodes_renders_unavailable_never_a_silent_blank():
    """R15 FAIL-OPEN guard at the pixel: an empty derivation must say so loudly. A blank section
    would read as 'nothing to report' -- the fail-open shape."""
    html = _render({"nodes": []})["nodes"]["innerHTML"]
    assert "EVIDENCE UNAVAILABLE" in html


def test_a_missing_suite_stamp_says_so_rather_than_printing_a_bare_number():
    """R15: an unavailable execution stamp is stated, never silently omitted or defaulted to 0."""
    d = _live_data()
    mutated = json.loads(json.dumps(d))
    mutated["suite_execution"] = {"available": False}
    assert "NOT RECORDED" in _render(mutated)["stamp"]["innerHTML"]


def test_a_stale_atom_reference_is_rendered_as_stale():
    """R15: an atom row the maturity map no longer contains is called out ON THE PAGE, so a
    reader is never shown a level for an atom that has left the map."""
    d = _live_data()
    mutated = json.loads(json.dumps(d))
    mutated["nodes"][0]["atoms"][0]["in_map"] = False
    html = _render(mutated)["nodes"]["innerHTML"]
    assert "NOT IN THE MATURITY MAP" in html


def test_the_page_authors_no_figure_in_its_markup():
    """Coherence-by-derivation, checked structurally: outside the inline script, the page's body
    markup carries NO multi-digit figure. Every number a reader sees came from the derivation."""
    import re

    html = INDEX.read_text(encoding="utf-8")
    body = html.split("<body>", 1)[1].split("<script>", 1)[0]
    body = re.sub(r"<style>.*?</style>", "", body, flags=re.DOTALL)
    stripped = re.sub(r"<[^>]+>", " ", body)
    assert not re.search(r"\d{2,}", stripped), f"authored figure in the page body: {stripped!r}"
