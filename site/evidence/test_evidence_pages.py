"""Rendered-value tests for the Evidence surface (site/evidence/index.html).

Atom: SITE_evidence_pages_behind_nodes. This is the criterion-2 control -- "each page renders
PRIMARY-STATE evidence for that node: the actual figures, the passing-test counts/provenance,
the fidelity-ledger rows -- NOT restated prose, verified to the RENDERED value".

R11 (verify to the rendered value): every assertion here runs the page's OWN inline JavaScript
through a Node/vm harness (_render_harness.mjs) against the REAL site/data/moap_evidence.json and
asserts on the produced HTML -- never on the source string, never on the JSON alone. Live-fetch
verification of poesys.net/evidence/ is a publish-from-main step this worktree cannot perform.

INDEPENDENCE (R15 / LAW C -- the tautology killer): the EXPECTED figures are recomputed here from
docs/design/maturity_map.yaml and docs/observability/coupled_gap_ledger.json directly -- a
different source from the generated JSON the page renders. If the generator ever stopped reading
the map, or the JSON went stale against it, these assertions would fail rather than agree with
themselves. `test_a_mutated_level_changes_the_rendered_pixel` proves the render is not constant.

THE PROSE GUARD: the map's `simplifications` narrative is the biggest restated-prose risk on this
surface, and this atom's exit criterion explicitly fails on it. `test_no_map_narrative_prose_is
_restated_on_the_page` asserts none of it reaches the rendered HTML.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
ROOT = SITE.parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = SITE / "data" / "moap_evidence.json"
MAP = ROOT / "docs" / "design" / "maturity_map.yaml"
GAP_LEDGER = ROOT / "docs" / "observability" / "coupled_gap_ledger.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _live() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def _render(data: dict) -> dict:
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(data),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


@pytest.fixture(scope="module")
def rendered() -> dict:
    return _render(_live())


def _map_atoms() -> dict:
    return {
        a["id"]: a
        for a in (yaml.safe_load(MAP.read_text(encoding="utf-8")) or [])
        if isinstance(a, dict) and a.get("id")
    }


# --------------------------------------------------------------- criterion 1: a page per node


def test_every_front_door_node_deep_links_to_a_section_that_renders_content(rendered):
    """Criterion 1, both halves: every node the front door deep-links has (a) a STATIC
    `id="node-<id>"` section on this page -- so the fragment resolves in the browser and in
    site/test_link_walk.py's source-level anchor gate -- and (b) real rendered content in that
    section, so the anchor does not land on an empty shell."""
    front = (SITE / "index.html").read_text(encoding="utf-8")
    anchors = set(re.findall(r'href="\./evidence/#node-([A-Za-z0-9_]+)"', front))
    assert len(anchors) == 6, anchors
    page = INDEX.read_text(encoding="utf-8")
    for node_id in sorted(anchors):
        assert f'id="node-{node_id}"' in page, f"no static anchor section for {node_id}"
        slot = rendered.get(f"ev-node-{node_id}")
        assert slot and len(slot["innerHTML"]) > 500, f"{node_id}: section renders (almost) nothing"
        assert "<table>" in slot["innerHTML"], f"{node_id}: no evidence table rendered"


def test_each_section_renders_the_stage_and_its_derivation(rendered):
    """The stage word on each evidence section is the COMPUTED one, rendered with the count it is
    derived from ('N of M build atoms ... are at their target level')."""
    html = rendered["ev-nodes"]["innerHTML"]
    for node in _live()["nodes"]:
        assert f">{node['computed_stage']}</span>" in html
        assert (
            f"<strong>{node['atoms_at_target']}</strong> of <strong>{node['atoms_total']}</strong>"
            in html
        ), f"{node['id']}: derivation count not rendered"


# --------------------------------------------------- criterion 2: PRIMARY STATE, to the pixel


def test_every_mapped_atom_renders_its_real_level_from_the_map(rendered):
    """The level cell for every atom behind every node equals the map's own level_current /
    level_target -- read here straight from docs/design/maturity_map.yaml, not from the page's
    JSON (independence)."""
    html = rendered["ev-nodes"]["innerHTML"]
    atoms = _map_atoms()
    checked = 0
    for node in _live()["nodes"]:
        for atom in node["atoms"]:
            rec = atoms[atom["id"]]
            row = re.search(
                r"<td><code>" + re.escape(atom["id"]) + r"</code></td>.*?</tr>", html, re.DOTALL
            )
            assert row, f"{atom['id']} renders no atom row"
            want = f'<td class="num">{rec["level_current"]} / {rec["level_target"]}</td>'
            assert want in row.group(0), f"{atom['id']}: rendered level != the map's level"
            checked += 1
    assert checked >= 40, f"only {checked} atom levels checked -- the scan broke"


def test_artefact_existence_is_rendered_as_the_real_on_disk_state(rendered):
    """Each artefact an atom names renders yes/MISSING matching the ACTUAL repo tree, checked
    here against the filesystem. A dangling evidence path is shown, not hidden."""
    html = rendered["ev-nodes"]["innerHTML"]
    missing_rendered = set(
        re.findall(
            r"<td><code>([^<]+)</code></td><td><code>[^<]+</code></td><td>[a-z]+</td>"
            r'<td class="num no">MISSING</td>',
            html,
        )
    )
    for path in missing_rendered:
        assert not (ROOT / path).exists(), f"{path} renders MISSING but exists on disk"
    yes_rendered = set(
        re.findall(
            r"<td><code>([^<]+)</code></td><td><code>[^<]+</code></td><td>[a-z]+</td>"
            r'<td class="num yes">yes</td>',
            html,
        )
    )
    assert yes_rendered, "no artefact renders as resolving -- the artefact table broke"
    for path in yes_rendered:
        assert (ROOT / path).exists(), f"{path} renders as resolving but is not on disk"
    # The known-dangling artefacts of the live map must be VISIBLE, not silently dropped.
    assert missing_rendered, "not one dangling artefact rendered -- the existence check went blind"


def test_test_counts_rendered_match_the_real_test_files(rendered):
    """A test file's rendered 'tests defined' equals the number of test functions the file really
    defines -- counted here by an independent regex over the file, not by the generator's AST."""
    html = rendered["ev-nodes"]["innerHTML"]
    rows = re.findall(
        r"<td><code>(tests/[^<]+\.py)</code></td><td><code>[^<]+</code></td><td>test</td>"
        r'<td class="num yes">yes</td><td class="num">(\d+)</td>',
        html,
    )
    assert len(rows) >= 10, f"only {len(rows)} test-file rows rendered -- the scan broke"
    for path, shown in rows:
        text = (ROOT / path).read_text(encoding="utf-8")
        real = len(re.findall(r"^\s*(?:async\s+)?def\s+test_", text, re.MULTILINE))
        assert int(shown) == real, f"{path}: page shows {shown} tests, the file defines {real}"


def test_measured_belief_vs_truth_gaps_render_their_real_values(rendered):
    """The coupled-triad gap figures are rendered from docs/observability/coupled_gap_ledger.json
    -- read here independently and compared to the page's own 3dp formatting."""
    html = rendered["ev-nodes"]["innerHTML"]
    ledger = json.loads(GAP_LEDGER.read_text(encoding="utf-8"))
    mapped = {a["id"] for n in _live()["nodes"] for a in n["atoms"]}
    shown = 0
    for atom, row in ledger.items():
        if atom not in mapped:
            continue
        assert f"{row['gap']:.3f}" in html, f"{atom}: measured gap {row['gap']} not rendered"
        assert f"{row['g0']:.3f}" in html, f"{atom}: naive baseline g0 not rendered"
        shown += 1
    assert shown >= 5, f"only {shown} measured gaps rendered -- the gap table broke"


def test_fidelity_ledger_row_renders_its_worst_cell(rendered):
    """The fidelity-evidence-ledger row behind W1_6 renders its per-cell lift table's WORST cell
    -- an actual measured figure, not a summary sentence."""
    html = rendered["ev-nodes"]["innerHTML"]
    rows = [r for n in _live()["nodes"] for a in n["atoms"] for r in a["fidelity_rows"]]
    assert rows, "no fidelity-ledger row reaches any node -- the join broke"
    for row in rows:
        if not row["cells"]:
            continue
        worst = min(row["cells"], key=lambda c: c["lift"])
        assert f"worst cell {worst['cell']}" in html
        assert f"{worst['lift']:.2f}" in html


def test_provenance_footer_carries_the_generation_stamp_and_sources(rendered):
    """Provenance is rendered, not implied: when it was generated, off which map digest, from
    which primary files, and the suite collection stamp."""
    text = rendered["ev-provenance"]["innerHTML"]
    live = _live()
    assert live["generated_at"] in text
    assert live["map_digest"] in text and len(live["map_digest"]) == 12
    for src in ("docs/design/maturity_map.yaml", "docs/observability/coupled_gap_ledger.json"):
        assert src in text, f"{src} not cited in the provenance footer"
    assert str(live["suite_stamp"]["test_count"]) in text


def test_summary_renders_the_real_totals(rendered):
    html = rendered["ev-summary"]["innerHTML"]
    t = _live()["totals"]
    assert f"{t['atoms_at_target']} / {t['atoms']} at target" in html
    assert f"{t['artefacts_resolving']} / {t['artefacts_total']} resolve" in html
    assert str(t["tests_defined"]) in html


# --------------------------------------------------- criterion 2: NOT restated prose


def test_no_map_narrative_prose_is_restated_on_the_page(rendered):
    """The map's `simplifications` field is its long narrative about each atom. None of it may
    reach this surface -- the page shows figures, paths and ledger rows, so a reader is looking at
    the state itself rather than at someone's account of it."""
    html = rendered["ev-nodes"]["innerHTML"] + rendered["ev-provenance"]["innerHTML"]
    atoms = _map_atoms()
    mapped = {a["id"] for n in _live()["nodes"] for a in n["atoms"]}
    checked = 0
    for aid in mapped:
        for note in atoms[aid].get("simplifications") or []:
            fragment = str(note)[:80].strip()
            if len(fragment) < 40:
                continue
            assert fragment not in html, f"{aid}: map narrative restated on the evidence page"
            checked += 1
    assert checked >= 20, "the prose guard checked almost nothing -- it would pass vacuously"


# --------------------------------------------------- R15: the render can FAIL


def test_a_mutated_level_changes_the_rendered_pixel():
    """R15/independence: move ONE atom's level in the payload and the rendered level cell and the
    derivation count both change. Proves the page renders its data rather than a constant."""
    live = _live()
    node = next(n for n in live["nodes"] if n["atoms_at_target"] == n["atoms_total"])
    before = _render(live)["ev-nodes"]["innerHTML"]
    atom = node["atoms"][0]
    assert f'<td class="num">{atom["level_current"]} / {atom["level_target"]}</td>' in before

    atom["level_current"] = 0
    atom["at_target"] = False
    node["atoms_at_target"] -= 1
    node["computed_stage"] = "Building"
    after = _render(live)["ev-nodes"]["innerHTML"]
    assert f'<td class="num">0 / {atom["level_target"]}</td>' in after
    assert f"Below target: <code>{atom['id']}</code>" in after
    assert (
        f"<strong>{node['atoms_at_target']}</strong> of <strong>{node['atoms_total']}</strong>"
        in after
    )
    assert before != after


def test_an_empty_payload_renders_no_evidence_rather_than_a_false_claim():
    """R15 fail-closed at the render: given no nodes, the page renders an empty evidence list and
    a '--' summary -- it can never render a substantiating figure it was not given."""
    out = _render({"nodes": [], "totals": {}, "sources": [], "suite_stamp": {}})
    assert out["ev-nodes"]["innerHTML"] == ""
    assert not [k for k in out if k.startswith("ev-node-")]
    assert "--" in out["ev-summary"]["innerHTML"]
    assert "at target" in out["ev-summary"]["innerHTML"]


def test_the_page_fetches_the_generated_evidence_data_and_it_exists():
    """The page renders from the generated derivation, and that file is on disk (no dangling
    evidence link of the site's own)."""
    src = INDEX.read_text(encoding="utf-8")
    assert 'fetch("../data/moap_evidence.json")' in src
    assert DATA.exists()
