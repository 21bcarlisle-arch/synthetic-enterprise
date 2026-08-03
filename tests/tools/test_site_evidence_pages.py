"""The model-on-a-page EVIDENCE PAGES and their publish gate (atom
``SITE_evidence_pages_behind_nodes``).

WHAT THIS SUITE IS FOR
----------------------
Three exit criteria, each tested here against the REAL repository and then mutation-proven:

  (1) NO DANGLING ANCHOR -- every diagram node making a non-trivial claim resolves to an
      evidence page that exists.
  (2) PRIMARY STATE, NOT PROSE -- each page renders the actual figures (atom levels, test
      counts, ledger rows, provenance) and they EQUAL the values derived from primary state.
  (3) THE GATE CAN FAIL -- a node claiming a stage its evidence cannot support, or a page
      that is missing / stale / empty, blocks publication.

This module lives under ``tests/`` and carries no ``operational`` marker, so it is inside
``background/process_run_complete.publish_gate_pytest_argv("tests/")``'s blocking scope: a
finding here really does stop a publish. That wiring is asserted, not assumed
(``test_this_suite_is_inside_the_publish_gate_scope``).

R15 DOCTRINE, EXPLICITLY
------------------------
Every mutation below runs against a COPY of the real site/map in ``tmp_path`` -- the real
tree is never mutated, so there is no restore step to forget. Each mutation names the defect
it plants and asserts the SPECIFIC finding kind fires; each is paired with an unmutated
control asserting the same call returns clean, so no test can pass because the checker is
broken (an always-red control is as worthless as an always-green one).

NO PINNED GENERATED VALUES. Nothing here asserts a literal level, count or date. Every
assertion is a RELATIONSHIP between the rendered page and the derivation. A pinned generated
value in a control has already cost this project a four-day publish blackout once.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
SITE = ROOT / "site"


def _load(name: str):
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


moap_evidence = _load("moap_evidence")
gate = _load("moap_evidence_gate")
generator = _load("generate_evidence_pages")


# --------------------------------------------------------------------------- fixtures


@pytest.fixture(scope="module")
def model():
    """The derivation off the REAL repository (git disabled: provenance decoration only,
    and a subprocess per atom would make every test in this module pay for it)."""
    return moap_evidence.evidence_model(with_git=False)


@pytest.fixture
def sandbox(tmp_path, model):
    """A mutable copy of the primary state + the built evidence pages.

    Returns a ``Sandbox`` whose ``findings()`` runs the real gate over the copy, so a
    mutation test can break one thing and see exactly what fires -- without ever touching
    the working tree.
    """

    class Sandbox:
        def __init__(self):
            self.site = tmp_path / "site"
            self.site.mkdir()
            shutil.copytree(SITE / "evidence", self.site / "evidence")
            shutil.copy2(SITE / "index.html", self.site / "index.html")
            (self.site / "data").mkdir()
            self.mapping_path = self.site / "data" / "moap_node_atoms.json"
            shutil.copy2(moap_evidence.MAPPING_PATH, self.mapping_path)
            self.map_path = tmp_path / "maturity_map.yaml"
            shutil.copy2(moap_evidence.MAP_PATH, self.map_path)

        def findings(self):
            return gate.gate_findings(
                site_root=self.site, map_path=self.map_path, mapping_path=self.mapping_path
            )

        def kinds(self):
            return {k for k, _, _ in self.findings()}

        def mapping(self):
            return json.loads(self.mapping_path.read_text(encoding="utf-8"))

        def write_mapping(self, data):
            self.mapping_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        def page(self, node_id: str) -> Path:
            return self.site / "evidence" / node_id / "index.html"

        def first_node(self, predicate=lambda n: True) -> dict:
            for node in self.mapping()["nodes"]:
                if predicate(node):
                    return node
            raise AssertionError("no node matched the predicate")

    return Sandbox()


# --------------------------------------------------------------------------- the real tree


def test_the_real_site_passes_the_gate(model):
    """The shipped surface is clean. This is the control every mutation below is measured
    against: if this were red, a mutation firing would prove nothing."""
    findings = gate.gate_findings(model=model)
    assert findings == [], "\n".join(f"[{k}] {s}: {d}" for k, s, d in findings)


def test_criterion_1_every_non_trivial_node_resolves_to_an_evidence_page(model):
    """(1) NO DANGLING ANCHOR."""
    non_trivial = [n for n in model["nodes"] if n["non_trivial"]]
    assert non_trivial, "derivation found no non-trivially-claimed node -- the model is empty?"
    for node in non_trivial:
        href = node["evidence_href"]
        assert href, f"{node['name']} declares no evidence_href"
        target = gate._href_target(href, SITE)
        assert target is not None and target.is_file(), f"{node['name']} -> {href} resolves to nothing"


def test_criterion_2_pages_render_the_derived_values_not_prose(model):
    """(2) PRIMARY STATE. Every atom behind every node has a row on its node's page whose
    RENDERED level equals the level the maturity map holds right now.

    The assertion is the RELATIONSHIP (rendered == derived), never a literal figure, so the
    control survives every legitimate level move and fires only on real drift.
    """
    checked = 0
    for node in model["nodes"]:
        if not node["non_trivial"]:
            continue
        text = gate._href_target(node["evidence_href"], SITE).read_text(encoding="utf-8")
        rendered = {}
        for block in gate._ATOM_ROW.findall(text):
            rid = gate._ROW_ID.search(block)
            rlv = gate._ROW_LEVEL.search(block)
            if rid and rlv:
                rendered[rid.group(1)] = (int(rlv.group(1)), int(rlv.group(2)))
        assert rendered, f"{node['name']}: page renders no atom rows"
        for atom in node["atoms"]:
            assert rendered.get(atom["id"]) == (atom["level_current"], atom["level_target"]), (
                f"{node['name']}/{atom['id']}: rendered {rendered.get(atom['id'])} != "
                f"derived {(atom['level_current'], atom['level_target'])}"
            )
            checked += 1
        assert gate._STAGE_WORD.search(text).group(1) == node["computed_stage"]
    assert checked > 0, "no atom rows were checked -- the parser matched nothing (fail-silent)"


def test_pages_carry_the_provenance_of_every_source_they_derive_from(model):
    """A figure without its source is restated prose. Each page names every primary source
    it was derived from, so a reader can go and check."""
    for node in model["nodes"]:
        if not node["non_trivial"]:
            continue
        text = gate._href_target(node["evidence_href"], SITE).read_text(encoding="utf-8")
        for source in model["sources"]:
            assert source["path"] in text, f"{node['name']}: page does not cite {source['path']}"


def test_pages_state_absent_evidence_rather_than_hiding_it(model):
    """Absence of evidence is primary state too. A node whose atoms have no recorded level
    move / no measured fidelity row must SAY so on the page -- silence would read as
    'nothing to report' when the honest reading is 'nothing on record'."""
    silent = [
        n for n in model["nodes"]
        if n["non_trivial"] and (n["ledger_row_count"] == 0 or n["fidelity_row_count"] == 0)
    ]
    assert silent, "expected at least one node with a gap in its record (else this control is vacuous)"
    for node in silent:
        text = gate._href_target(node["evidence_href"], SITE).read_text(encoding="utf-8")
        assert "no recorded move" in text or "no measured row" in text


def test_the_two_independent_stage_derivations_agree(model):
    """The site's own Phase-B derivation (``site/moap_stage.py``, a regex parse of the map)
    and this atom's derivation (a yaml parse) are separate implementations of the same rule.
    They must agree on every node -- an independent cross-check that neither has drifted."""
    # site/ is not a package and site/moap_stage.py imports its sibling by bare name, so it
    # needs site/ on sys.path -- added and removed around the import so this suite cannot
    # leave site/*.py shadowing anything for the rest of the session.
    site_dir = str(SITE)
    sys.path.insert(0, site_dir)
    try:
        moap_stage = _load_site_module("moap_stage")
        site_stages = {s["id"]: s["computed_stage"] for s in moap_stage.node_stages()}
    finally:
        sys.path.remove(site_dir)
        for name in ("moap_stage", "moap_coherence"):
            sys.modules.pop(name, None)
    for node in model["nodes"]:
        assert site_stages[node["id"]] == node["computed_stage"], node["id"]


def _load_site_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SITE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_this_suite_is_inside_the_publish_gate_scope():
    """R11 / no orphan transitions: a gate whose failure reaches nobody is not a gate. This
    asserts the publish gate's own argv really would run this file -- keyed on the argv the
    publish gate builds, not on a comment claiming it does."""
    spec = importlib.util.spec_from_file_location(
        "process_run_complete", ROOT / "background" / "process_run_complete.py"
    )
    prc = importlib.util.module_from_spec(spec)
    sys.modules["process_run_complete"] = prc
    spec.loader.exec_module(prc)
    argv = prc.publish_gate_pytest_argv("tests/")
    rel = str(Path(__file__).resolve().relative_to(ROOT))
    assert "tests/" in argv, argv
    ignores = [a.split("=", 1)[1] for a in argv if a.startswith("--ignore=")]
    assert not any(rel.startswith(i) for i in ignores), f"{rel} is ignored by the publish gate"


# --------------------------------------------------------------------------- R15 mutations


def test_r15_control_the_unmutated_sandbox_is_clean(sandbox):
    """Both-ways proof, half one: the copied tree passes. Every mutation below is a single
    edit away from THIS state, so a finding it produces is attributable to that edit alone."""
    assert sandbox.findings() == []


def test_r15_a_node_claiming_a_stage_its_evidence_cannot_support_fires(sandbox):
    """THE HEADLINE MUTATION (exit criterion 3, verbatim): take a node whose atoms are NOT
    all at target and make it claim 'Live'. The gate must FIRE."""
    data = sandbox.mapping()
    target = None
    for node in data["nodes"]:
        if node.get("declared_stage") == "Building":
            node["declared_stage"] = "Live"
            target = node
            break
    assert target is not None, "no Building node to over-claim -- fixture assumption broken"
    sandbox.write_mapping(data)
    findings = sandbox.findings()
    assert gate.DECLARED_STAGE_DRIFT in {k for k, _, _ in findings}
    detail = next(d for k, _, d in findings if k == gate.DECLARED_STAGE_DRIFT)
    assert "Live" in detail and "Building" in detail, detail


def test_r15_understating_a_stage_also_fires(sandbox):
    """Drift in EITHER direction is drift. A node lagging its own evidence is still a page
    that disagrees with the derivation, and a gate that only catches over-claims would let a
    stale mapping rot quietly."""
    data = sandbox.mapping()
    for node in data["nodes"]:
        if node.get("declared_stage") == "Live":
            node["declared_stage"] = "Planned"
            break
    sandbox.write_mapping(data)
    assert gate.DECLARED_STAGE_DRIFT in sandbox.kinds()


def test_r15_a_map_level_moving_without_the_page_being_regenerated_fires(sandbox):
    """The staleness mutation, and the independence proof: change the MAP (one source) while
    the PAGE (the other source) is untouched. If the gate were reading the page's own numbers
    back at itself -- the TAUTOLOGY pattern -- nothing would fire. It must."""
    atoms = yaml.safe_load(sandbox.map_path.read_text(encoding="utf-8"))
    node = sandbox.first_node(lambda n: n.get("declared_stage") == "Live")
    victim = node["atoms"][0]
    for rec in atoms:
        if rec.get("id") == victim:
            rec["level_current"] = 0
            rec["level_target"] = 3
            break
    sandbox.map_path.write_text(yaml.safe_dump(atoms), encoding="utf-8")
    kinds = sandbox.kinds()
    assert gate.EVIDENCE_LEVEL_DRIFT in kinds, kinds
    # ... and the same edit changes the DERIVED stage, so the page's stage word is now stale
    # and the node's own declared stage is now an over-claim. All three must fire together.
    assert gate.EVIDENCE_STAGE_DRIFT in kinds, kinds
    assert gate.DECLARED_STAGE_DRIFT in kinds, kinds


def test_r15_a_missing_evidence_page_fires(sandbox):
    """FAIL-OPEN guard: the dangling anchor. Delete a page; the node still claims a stage."""
    node = sandbox.first_node(lambda n: n.get("declared_stage") in ("Live", "Building"))
    sandbox.page(node["id"]).unlink()
    kinds = sandbox.kinds()
    assert gate.NO_EVIDENCE_PAGE in kinds, kinds


def test_r15_a_node_with_no_evidence_href_fires(sandbox):
    """FAIL-OPEN guard: an ABSENT field must fail, not skip. A missing evidence_href is the
    cheapest possible way to silence this whole control, so it is the first thing to try."""
    data = sandbox.mapping()
    for node in data["nodes"]:
        if node.get("declared_stage") in ("Live", "Building"):
            node.pop("evidence_href", None)
            break
    sandbox.write_mapping(data)
    assert gate.NO_EVIDENCE_PAGE in sandbox.kinds()


def test_r15_an_href_pointing_somewhere_else_fires(sandbox):
    """A node that walks to a page which is not ITS page. Without the node-id check a single
    generic 'evidence' page would satisfy all six nodes -- the cheapest possible fake."""
    data = sandbox.mapping()
    nodes = [n for n in data["nodes"] if n.get("declared_stage") in ("Live", "Building")]
    nodes[0]["evidence_href"] = nodes[1]["evidence_href"]
    sandbox.write_mapping(data)
    assert gate.EVIDENCE_PAGE_UNREADABLE in sandbox.kinds()


def test_r15_a_page_of_prose_with_no_primary_state_fires(sandbox):
    """The failure this atom exists to kill: a page that LOOKS like evidence and contains no
    primary state. Strip the atom rows but keep the headline, the stage word and the prose."""
    node = sandbox.first_node(lambda n: n.get("declared_stage") in ("Live", "Building"))
    page = sandbox.page(node["id"])
    text = page.read_text(encoding="utf-8")
    stripped = gate._ATOM_ROW.sub("<p>This node is doing extremely well.</p>", text)
    page.write_text(stripped, encoding="utf-8")
    assert gate.EVIDENCE_PAGE_EMPTY in sandbox.kinds()


def test_r15_an_empty_page_file_fires(sandbox):
    """FAIL-OPEN guard: zero bytes is not a pass."""
    node = sandbox.first_node(lambda n: n.get("declared_stage") in ("Live", "Building"))
    sandbox.page(node["id"]).write_text("", encoding="utf-8")
    assert sandbox.kinds() & {gate.EVIDENCE_PAGE_EMPTY, gate.EVIDENCE_PAGE_UNREADABLE}


def test_r15_a_page_dropping_one_atom_row_fires(sandbox):
    """The subtle over-claim: keep the page, delete the row for the one atom that is dragging
    the node down. Coverage must be per-atom, not 'some rows exist'."""
    node = sandbox.first_node(lambda n: n.get("declared_stage") in ("Live", "Building"))
    page = sandbox.page(node["id"])
    text = page.read_text(encoding="utf-8")
    assert len(gate._ATOM_ROW.findall(text)) > 1, "need >1 row for this mutation to be meaningful"
    page.write_text(gate._ATOM_ROW.sub("", text, count=1), encoding="utf-8")
    assert gate.EVIDENCE_ATOM_MISSING in sandbox.kinds()


def test_r15_an_extra_atom_row_the_node_does_not_map_fires(sandbox):
    """The reverse over-claim: a page padded with atoms the node's claim does not actually
    rest on, borrowing their green levels."""
    node = sandbox.first_node(lambda n: n.get("declared_stage") in ("Live", "Building"))
    page = sandbox.page(node["id"])
    text = page.read_text(encoding="utf-8")
    fake = ('<tr class="ev-atom" id="atom-NOT_A_MAPPED_ATOM">'
            '<td><code class="ev-atom-id">NOT_A_MAPPED_ATOM</code></td>'
            '<td class="ev-atom-level">9 / 9</td></tr>')
    page.write_text(text.replace("</tbody>", fake + "</tbody>", 1), encoding="utf-8")
    assert gate.EVIDENCE_ATOM_UNMAPPED in sandbox.kinds()


def test_r15_a_node_backed_by_no_atoms_fires(sandbox):
    """FAIL-OPEN guard: an atom-less node derives PLANNED and would otherwise slip through
    every downstream check by claiming nothing. A diagram node backed by nothing is a defect
    in its own right."""
    data = sandbox.mapping()
    data["nodes"][0]["atoms"] = []
    data["nodes"][0]["declared_stage"] = None
    sandbox.write_mapping(data)
    assert gate.NODE_HAS_NO_ATOMS in sandbox.kinds()


def test_r15_an_unreadable_derivation_fails_rather_than_skips(sandbox):
    """FAIL-SILENT guard, the R15 pattern that matters most here: if the gate cannot read the
    primary state it is supposed to check against, that is a FAILED check. It must never
    return 'no findings' because it found nothing to look at."""
    sandbox.map_path.write_text("", encoding="utf-8")
    kinds = sandbox.kinds()
    assert gate.DERIVATION_UNAVAILABLE in kinds, kinds

    sandbox.map_path.unlink()
    assert gate.DERIVATION_UNAVAILABLE in sandbox.kinds()

    sandbox.mapping_path.write_text('{"nodes": []}', encoding="utf-8")
    assert gate.DERIVATION_UNAVAILABLE in sandbox.kinds()


def test_r15_a_missing_evidence_index_fires(sandbox):
    """The whole set must stay walkable: an orphaned page nobody links to is not inspectable."""
    (sandbox.site / "evidence" / "index.html").unlink()
    assert gate.NO_EVIDENCE_PAGE in sandbox.kinds()


def test_r15_the_index_dropping_a_node_fires(sandbox):
    """...and the index must link EVERY node, not merely exist."""
    index = sandbox.site / "evidence" / "index.html"
    node_id = sandbox.mapping()["nodes"][0]["id"]
    index.write_text(index.read_text(encoding="utf-8").replace(f'href="./{node_id}/"', 'href="./"'),
                     encoding="utf-8")
    assert gate.EVIDENCE_INDEX_MISSING_NODE in sandbox.kinds()


def test_derivation_unavailable_is_raised_not_swallowed(tmp_path):
    """The library half of the fail-silent guard: each loader RAISES on a missing/empty
    source rather than returning a benign empty structure."""
    missing = tmp_path / "nope.yaml"
    with pytest.raises(moap_evidence.DerivationUnavailable):
        moap_evidence.load_atoms(missing)
    empty = tmp_path / "empty.yaml"
    empty.write_text("[]", encoding="utf-8")
    with pytest.raises(moap_evidence.DerivationUnavailable):
        moap_evidence.load_atoms(empty)
    with pytest.raises(moap_evidence.DerivationUnavailable):
        moap_evidence.load_gate_ledger(tmp_path / "no_ledger.jsonl")
    with pytest.raises(moap_evidence.DerivationUnavailable):
        moap_evidence.load_fidelity_ledger(tmp_path / "no_fidelity.json")
    with pytest.raises(moap_evidence.DerivationUnavailable):
        moap_evidence.build_test_index(["X"], tmp_path / "no_tests")


def test_compute_stage_never_vacuously_greens(model):
    """An empty atom set must NOT read as Live (``all([])`` is True -- the classic fail-open),
    and an atom with no declared target must not read as at-target."""
    assert moap_evidence.compute_stage([]) == moap_evidence.PLANNED
    assert moap_evidence.compute_stage(
        [{"level_current": 0, "level_target": 1}]
    ) == moap_evidence.PLANNED
    assert moap_evidence.compute_stage(
        [{"level_current": 3, "level_target": 3}, {"level_current": 0, "level_target": 1}]
    ) == moap_evidence.BUILDING
    assert moap_evidence.compute_stage(
        [{"level_current": 2, "level_target": 2}]
    ) == moap_evidence.LIVE


# --------------------------------------------------------------------------- generator


def test_the_generator_is_the_only_author(tmp_path, model):
    """The site is a rendering, never an author: regenerating from the same derivation
    reproduces pages the gate accepts. (Deliberately NOT byte-equality -- the pages carry a
    build timestamp, and pinning a generated value inside a control is the exact pattern that
    caused a four-day publish blackout.)"""
    out = tmp_path / "site" / "evidence"
    written = generator.generate(evidence_root=out, model=model)
    assert len(written) == len(model["nodes"]) + 1
    shutil.copy2(SITE / "index.html", tmp_path / "site" / "index.html")
    data_dir = tmp_path / "site" / "data"
    data_dir.mkdir()
    shutil.copy2(moap_evidence.MAPPING_PATH, data_dir / "moap_node_atoms.json")
    findings = gate.gate_findings(site_root=tmp_path / "site", model=model)
    assert findings == [], findings


def test_front_door_wiring_flag_matches_reality(model):
    """THE WIRING INTERLOCK (criterion 1, last mile).

    ``site/index.html`` was outside this build's write scope, so the front-door link check
    ships READY and OFF (``FRONT_DOOR_LINKS_REQUIRED = False``). This test makes that state
    self-correcting rather than a permanent fail-open: the moment the per-node evidence links
    land on the front door, this goes RED until the flag is flipped to True -- so the links
    can never arrive with their own gate silently disabled.

    To wire it: add ``<a href="./evidence/<node_id>/">`` inside each ``.node`` block of
    site/index.html, then set FRONT_DOOR_LINKS_REQUIRED = True.
    """
    wired = not gate.front_door_findings(model, SITE)
    assert wired == gate.FRONT_DOOR_LINKS_REQUIRED, (
        "front-door evidence links "
        + ("ARE now present -- set moap_evidence_gate.FRONT_DOOR_LINKS_REQUIRED = True"
           if wired else
           "are NOT present but FRONT_DOOR_LINKS_REQUIRED is True")
    )


def test_r15_the_front_door_check_fires_and_clears(tmp_path, model):
    """R15 both ways on the held-back check itself, so flipping the flag is a one-line change
    to a control already proven able to fail AND to pass."""
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<html><body>no evidence links here</body></html>",
                                     encoding="utf-8")
    assert gate.front_door_findings(model, site), "check did not fire on a front door with no links"

    links = "".join(
        f'<a href="./evidence/{n["id"]}/">evidence</a>' for n in model["nodes"] if n["non_trivial"]
    )
    (site / "index.html").write_text(f"<html><body>{links}</body></html>", encoding="utf-8")
    assert gate.front_door_findings(model, site) == [], "check did not clear once links exist"

    (site / "index.html").unlink()
    assert gate.front_door_findings(model, site), "a missing front door must FAIL, not skip"
