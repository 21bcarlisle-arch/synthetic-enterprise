"""R15 mechanism self-test for §6 coherence-by-derivation -- PHASE E (the evidence pages behind
the model-on-a-page nodes: tools/moap_evidence.py, rendered by site/evidence/index.html).

Atom: SITE_evidence_pages_behind_nodes. Its exit criteria are the acceptance:
  (1) every node with a non-trivial claimed stage resolves to an evidence page -- no dangling anchor
  (2) each page renders PRIMARY-STATE evidence, not restated prose (asserted to the RENDERED value
      in site/evidence/test_evidence_pages.py -- this file covers the generator that feeds it)
  (3) a node whose evidence page is missing, or whose stage disagrees with the derivation, FAILS
      the publish gate

Three roles here:

  1. GENERATOR truth -- build_payload() reads PRIMARY STATE: the atoms' real levels, whether each
     artefact an atom names actually exists on disk, how many tests a test file really defines.
     Each is checked against an INDEPENDENT reading of the same primary source (the filesystem, a
     regex over the file), never against the generator's own output. The map's `simplifications`
     narrative is asserted ABSENT -- restated prose is an explicit failure of criterion 2.

  2. GATE surface (R15 BOTH WAYS) -- evidence_findings() FIRES on each of its named defects:
     the page deleted, the page blanked, the data file absent/empty/malformed, a node missing
     from the data, an anchor pointing at a node the data does not have, a node with no evidence
     link at all, and the data recording a stage the map no longer computes. The tautology killer
     holds the evidence data FIXED and moves only an atom LEVEL: the finding appears, proving the
     check reads the map rather than comparing the evidence page to itself.

  3. LIVE -- the real repo's six nodes each resolve to a current evidence page, so the extended
     publish gate is green today; and a REAL-surface mutation (flip one node's declared_stage in
     a copy of the live mapping to a stage its atoms cannot support) makes the real gate FIRE.
"""
import importlib.util
import json
import re
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_SITE = _ROOT / "site"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ev = _load("moap_evidence")
gate = _load("moap_coherence_gate")

from moap_stage import compute_stage  # noqa: E402  (site/ is on sys.path via the modules above)

_HEAD = (
    '<div class="node-head"><span class="node-name">{name}</span>'
    '<span class="stage stage-{cls}">{stage}</span></div>'
)
_CLS = {"Live": "live", "Building": "building", "Planned": "planned"}


def _build(tmp, nodes, atom_levels, *, page=True, blank_page=False, data=True,
           empty_data=False, malformed_data=False, drop_nodes=(), extra_anchors=(),
           skip_anchors=(), skip_page_sections=(), stage_override=None):
    """A synthetic site whose evidence surface can be mutated one defect at a time.
    `nodes`: [{name, atoms, declared, rendered}]; `atom_levels`: {id: (current, target)}."""
    site = tmp / "site"
    (site / "data").mkdir(parents=True, exist_ok=True)
    (site / "evidence").mkdir(parents=True, exist_ok=True)
    ids = {n["name"]: n["name"].lower() for n in nodes}
    mapping = {
        "nodes": [
            {"id": ids[n["name"]], "name": n["name"], "declared_stage": n["declared"],
             "atoms": n["atoms"]}
            for n in nodes
        ]
    }
    mapping_path = site / "data" / "moap_node_atoms.json"
    mapping_path.write_text(json.dumps(mapping), encoding="utf-8")

    map_path = tmp / "map.yaml"
    map_path.write_text(
        "".join(
            f"- id: {i}\n  lane: L\n  level_current: {c}\n  level_target: {t}\n"
            for i, (c, t) in atom_levels.items()
        ),
        encoding="utf-8",
    )

    computed = {
        ids[n["name"]]: compute_stage(
            [
                {"current": atom_levels.get(a, (0, 1))[0], "target": atom_levels.get(a, (0, 1))[1]}
                for a in n["atoms"]
            ]
        )
        for n in nodes
    }

    blocks = []
    for n in nodes:
        nid = ids[n["name"]]
        block = _HEAD.format(name=n["name"], cls=_CLS[n["rendered"]], stage=n["rendered"])
        if computed[nid] != "Planned" and nid not in skip_anchors:
            block += f'<a class="node-look" href="./evidence/#node-{nid}">Evidence</a>'
        blocks.append(block)
    for anchor in extra_anchors:
        blocks.append(f'<a class="node-look" href="./evidence/#node-{anchor}">Evidence</a>')
    (site / "index.html").write_text(
        '<div class="nodes">' + "\n".join(blocks) + "</div>", encoding="utf-8"
    )

    if page:
        sections = "".join(
            f'<section id="node-{nid}"><div id="ev-node-{nid}"></div></section>'
            for nid in computed
            if nid not in skip_page_sections
        )
        (site / "evidence" / "index.html").write_text(
            "" if blank_page else f"<html><body>{sections}</body></html>",
            encoding="utf-8",
        )
    if data:
        payload_nodes = [
            {
                "id": ids[n["name"]],
                "name": n["name"],
                "declared_stage": n["declared"],
                "computed_stage": (stage_override or {}).get(ids[n["name"]], computed[ids[n["name"]]]),
                "atoms": [],
            }
            for n in nodes
            if ids[n["name"]] not in drop_nodes
        ]
        target = site / "data" / "moap_evidence.json"
        if malformed_data:
            target.write_text("{not json", encoding="utf-8")
        else:
            target.write_text(
                json.dumps({"nodes": [] if empty_data else payload_nodes}), encoding="utf-8"
            )
    return site, map_path, mapping_path


def _findings(nodes, atom_levels, **kw):
    with tempfile.TemporaryDirectory() as d:
        site, m, g = _build(Path(d), nodes, atom_levels, **kw)
        return ev.evidence_findings(site, m, g)


def _kinds(findings):
    return {k for k, _, _ in findings}


_LIVE_NODE = [{"name": "Alpha", "atoms": ["X1"], "declared": "Live", "rendered": "Live"}]
_AT_TARGET = {"X1": (3, 3)}


# ============================================================ 2. GATE SURFACE (R15 both ways)


def test_a_complete_evidence_trail_yields_no_findings():
    """The GREEN half of every mutation below: page present, anchor present, data carrying the
    node with the stage the map computes -> nothing to report."""
    assert _findings(_LIVE_NODE, _AT_TARGET) == []


def test_fires_when_the_evidence_page_is_deleted():
    """R15, criterion 1: no evidence page -> every node's link dangles."""
    f = _findings(_LIVE_NODE, _AT_TARGET, page=False)
    assert ev.EVIDENCE_PAGE_MISSING in _kinds(f), f


def test_fires_when_the_evidence_page_is_blanked():
    """R15 fail-open killer: an EMPTY page file must not read as 'a page exists'."""
    f = _findings(_LIVE_NODE, _AT_TARGET, blank_page=True)
    assert ev.EVIDENCE_PAGE_MISSING in _kinds(f), f


def test_fires_when_the_evidence_data_is_absent_empty_or_malformed():
    """R15 fail-open killer, all three shapes of 'no data': absent, node-less, unparseable."""
    for kw in ({"data": False}, {"empty_data": True}, {"malformed_data": True}):
        f = _findings(_LIVE_NODE, _AT_TARGET, **kw)
        assert ev.EVIDENCE_DATA_MISSING in _kinds(f), (kw, f)


def test_fires_when_a_claiming_node_is_missing_from_the_evidence_data():
    f = _findings(_LIVE_NODE, _AT_TARGET, drop_nodes=("alpha",))
    assert ev.EVIDENCE_NODE_MISSING in _kinds(f), f


def test_fires_on_a_dangling_anchor_the_data_cannot_serve():
    """Criterion 1's named class: the front door links an evidence anchor for a node the evidence
    data has no entry for -- the click would land on nothing."""
    f = _findings(_LIVE_NODE, _AT_TARGET, extra_anchors=("ghost_node",))
    assert ev.DANGLING_EVIDENCE_ANCHOR in _kinds(f), f
    assert any(subject == "ghost_node" for _, subject, _ in f), f


def test_fires_when_the_page_has_no_section_for_a_claiming_node():
    """R15, criterion 1's sharpest edge: the page EXISTS and the data carries the node, but the
    page has no `id="node-<id>"` section -- so the front-door deep link would land the reader at
    the page top instead of on that part's evidence."""
    f = _findings(_LIVE_NODE, _AT_TARGET, skip_page_sections=("alpha",))
    assert ev.EVIDENCE_ANCHOR_NOT_ON_PAGE in _kinds(f), f


def test_fires_when_a_claiming_node_carries_no_evidence_link_at_all():
    f = _findings(_LIVE_NODE, _AT_TARGET, skip_anchors=("alpha",))
    assert ev.NODE_WITHOUT_EVIDENCE_LINK in _kinds(f), f


def test_fires_when_the_recorded_stage_is_stale_against_the_derivation():
    """Criterion 3: the evidence page records a stage the map no longer computes."""
    f = _findings(_LIVE_NODE, _AT_TARGET, stage_override={"alpha": "Building"})
    assert ev.EVIDENCE_STAGE_STALE in _kinds(f), f


def test_the_tautology_killer_evidence_fixed_atom_level_moves():
    """Hold the evidence data's recorded stage FIXED at 'Live' and move ONLY the atom's level.
    At target -> clean; below target -> EVIDENCE_STAGE_STALE. Proves the check reads the MAP, not
    the evidence page's own claim about itself."""
    clean = _findings(_LIVE_NODE, {"X1": (3, 3)}, stage_override={"alpha": "Live"})
    assert clean == [], clean
    fired = _findings(_LIVE_NODE, {"X1": (1, 3)}, stage_override={"alpha": "Live"})
    assert ev.EVIDENCE_STAGE_STALE in _kinds(fired), fired


def test_a_planned_node_needs_no_evidence_page():
    """No false positive on a node that claims nothing yet: PLANNED means 'not started', so there
    is no stage claim to substantiate and no evidence link is required."""
    nodes = [{"name": "Alpha", "atoms": ["X1"], "declared": "Planned", "rendered": "Planned"}]
    assert _findings(nodes, {"X1": (0, 3)}) == []
    # ... and with no page or data at all, a purely-Planned diagram still does not fire.
    assert _findings(nodes, {"X1": (0, 3)}, page=False, data=False) == []


# ============================================================ the gate unions it (criterion 3)


def test_the_publish_gate_refuses_a_commit_on_an_evidence_defect():
    """End to end through tools/moap_coherence_gate.py: an evidence defect reaches decide() as a
    site-evidence finding and ENFORCE returns 1 (COMMIT REFUSED); SHADOW returns 0 on the SAME
    findings (the risk rail still does not wedge publishing)."""
    with tempfile.TemporaryDirectory() as d:
        site, m, g = _build(Path(d), _LIVE_NODE, _AT_TARGET, page=False)
        findings = gate.gather_findings(site, m, g)
    surfaces = {s for s, _, _, _ in findings}
    assert gate.S_EVIDENCE in surfaces, findings
    assert gate.decide(findings, gate.ENFORCE) == 1
    assert gate.decide(findings, gate.SHADOW) == 0


def test_the_evidence_files_are_gate_triggers():
    """A commit touching only the evidence page or its data must run this gate."""
    assert gate.is_triggered(["site/evidence/index.html"])
    assert gate.is_triggered(["site/data/moap_evidence.json"])
    assert not gate.is_triggered(["saas/billing/engine.py"])


# ============================================================ 1. GENERATOR reads PRIMARY STATE


def test_artefact_paths_extracts_real_paths_from_annotated_evidence_entries():
    """Map `evidence:` entries are free text that leads with paths and then annotates them. The
    path is extracted; a location suffix (::symbol, :line) is trimmed to the file; an entry that
    names no path yields none (counted as a note, never as a resolving artefact)."""
    assert ev.artefact_paths("tests/sim/test_weather_engine.py (27 tests)") == [
        "tests/sim/test_weather_engine.py"
    ]
    assert ev.artefact_paths("background/retro_cadence_check.py::last_retro (R15 guard)") == [
        "background/retro_cadence_check.py"
    ]
    assert ev.artefact_paths("docs/observability/session-watchdog-log.md:4354 (director)") == [
        "docs/observability/session-watchdog-log.md"
    ]
    assert ev.artefact_paths("tests/a/test_one.py + tests/b/test_two.py (both green)") == [
        "tests/a/test_one.py",
        "tests/b/test_two.py",
    ]
    assert ev.artefact_paths("2026-08-03 DEMOTED L3 -> L1 (director console)") == []


def test_tests_defined_counts_the_real_test_functions():
    """Independent oracle: a regex over this very file must agree with the AST counter."""
    me = Path(__file__)
    text = me.read_text(encoding="utf-8")
    regex_count = len(re.findall(r"^\s*(?:async\s+)?def\s+test_", text, re.MULTILINE))
    assert ev.tests_defined(me) == regex_count > 10


def test_tests_defined_is_zero_for_a_file_that_is_not_there():
    """Fail-closed: an unreadable/absent file counts 0 -- and the artefact row that carries it
    also carries exists=False, so a 0 can never read as 'fine'."""
    assert ev.tests_defined(_ROOT / "tests" / "__no_such_file__.py") == 0


def test_payload_artefact_existence_matches_the_real_filesystem():
    """Every artefact row's `exists` is checked against the actual repo tree -- and the live map
    genuinely names at least one artefact that is NOT there, so this is not a vacuous all-True."""
    payload = ev.build_payload()
    seen_missing = False
    checked = 0
    for node in payload["nodes"]:
        for atom in node["atoms"]:
            for art in atom["artefacts"]:
                assert (_ROOT / art["path"]).exists() == art["exists"], art
                seen_missing = seen_missing or not art["exists"]
                checked += 1
    assert checked > 100, f"only {checked} artefacts inspected -- the extraction broke"
    assert seen_missing, "no dangling artefact found -- the existence check may be vacuous"


def test_payload_levels_match_the_map_and_totals_are_consistent():
    payload = ev.build_payload()
    import yaml

    records = {
        a["id"]: a
        for a in yaml.safe_load((_ROOT / "docs" / "design" / "maturity_map.yaml").read_text())
        if isinstance(a, dict) and a.get("id")
    }
    total_atoms = 0
    for node in payload["nodes"]:
        assert node["atoms_total"] == len(node["atoms"])
        assert node["atoms_at_target"] == sum(1 for a in node["atoms"] if a["at_target"])
        for atom in node["atoms"]:
            rec = records[atom["id"]]
            assert atom["level_current"] == rec["level_current"]
            assert atom["level_target"] == rec["level_target"]
            assert atom["at_target"] == (rec["level_current"] >= rec["level_target"])
        total_atoms += node["atoms_total"]
    assert payload["totals"]["atoms"] == total_atoms
    assert payload["totals"]["nodes"] == len(payload["nodes"]) == 6


def test_the_payload_carries_no_restated_map_narrative():
    """Criterion 2's prose guard at the SOURCE: the map's `simplifications` (and the atom's
    `real_world_twin` sentence) must not be serialised into the evidence data at all."""
    payload = ev.build_payload()
    blob = json.dumps(payload)
    assert "simplifications" not in blob
    assert "real_world_twin" not in blob
    import yaml

    narratives = 0
    for a in yaml.safe_load((_ROOT / "docs" / "design" / "maturity_map.yaml").read_text()):
        if not isinstance(a, dict):
            continue
        for note in a.get("simplifications") or []:
            fragment = str(note)[:80].strip()
            if len(fragment) < 40:
                continue
            assert fragment not in blob, f"{a['id']}: map narrative leaked into the evidence data"
            narratives += 1
    assert narratives > 50, "the prose guard checked almost nothing -- it would pass vacuously"


def test_the_payload_carries_the_measured_gaps_and_ledger_rows():
    """The harness's own measurements reach the pages: coupled-triad gaps, fidelity-ledger rows
    and recorded level moves, each read from its observability ledger."""
    payload = ev.build_payload()
    atoms = [a for n in payload["nodes"] for a in n["atoms"]]
    gaps = [a for a in atoms if a["coupled_gap"]]
    fidelity = [a for a in atoms if a["fidelity_rows"]]
    ledgered = [a for a in atoms if a["level_ledger"]]
    assert len(gaps) >= 5, gaps
    assert fidelity, "no fidelity-ledger row reaches any node"
    assert len(ledgered) >= 5, ledgered
    live = json.loads(
        (_ROOT / "docs" / "observability" / "coupled_gap_ledger.json").read_text(encoding="utf-8")
    )
    for atom in gaps:
        assert atom["coupled_gap"]["gap"] == live[atom["id"]]["gap"]


# ============================================================ 3. LIVE surfaces


def test_the_real_six_nodes_each_resolve_to_a_current_evidence_page():
    """Criterion 1 on the REAL site: no node is dangling today."""
    assert ev.evidence_findings() == []
    anchors = ev.front_door_evidence_anchors()
    ids = {n["id"] for n in json.loads(ev.data_path().read_text(encoding="utf-8"))["nodes"]}
    assert len(anchors) == 6, anchors
    assert anchors <= ids
    assert ev.page_path().is_file()


def test_the_real_publish_gate_is_green_with_the_evidence_surface_unioned():
    real = gate.gather_findings()
    assert real == [], real
    assert gate.decide(real, gate.ENFORCE) == 0


def test_a_real_node_claiming_an_unsupported_stage_fires_the_real_gate():
    """R15 on the LIVE surfaces (criterion 3, verbatim): mutate a real node to claim a stage its
    atoms' levels cannot support -- 'The world' is Building because W1_5 sits below target -- and
    the real gate FIRES on both the stage surface and the evidence surface. Nothing on disk is
    touched: the mutation is a copy of the live mapping."""
    mapping = json.loads(ev._MAPPING.read_text(encoding="utf-8"))
    target = next(n for n in mapping["nodes"] if n["id"] == "the_world")
    assert target["declared_stage"] == "Building", target["declared_stage"]
    target["declared_stage"] = "Live"
    with tempfile.TemporaryDirectory() as d:
        mutated = Path(d) / "moap_node_atoms.json"
        mutated.write_text(json.dumps(mapping), encoding="utf-8")
        findings = gate.gather_findings(_SITE, ev._MAP, mutated)
        kinds = {k for _, k, _, _ in findings}
        surfaces = {s for s, _, _, _ in findings}
        assert "STAGE_DISAGREEMENT" in kinds, findings
        assert ev.EVIDENCE_STAGE_STALE in kinds, findings
        assert gate.S_EVIDENCE in surfaces, findings
        assert gate.decide(findings, gate.ENFORCE) == 1
    # ... and the unmutated live mapping is clean again (both ways).
    assert gate.decide(gate.gather_findings(), gate.ENFORCE) == 0
