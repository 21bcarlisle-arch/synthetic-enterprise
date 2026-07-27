"""R15 mechanism self-test for §6 coherence-by-derivation -- PHASE A (node->atom
mapping integrity), PLUS the live-state coherence gate.

Two roles in one file (the site/test_link_walk.py pattern):
  1. MECHANISM self-tests (R15): synthetic fixtures prove coherence_findings() FIRES
     on each of its four named HARD defects (empty node, dead atom ref, diagram node
     with no mapping, mapping node not on the diagram) AND fires the soft ORPHAN flag
     (an atom behind no node) -- the bidirectional gap in both directions. An
     independence test proves a wholly-coherent fixture yields zero HARD findings
     (the control is not always-positive).
  2. LIVE GATE: the real mapping (site/data/moap_node_atoms.json) coheres with the
     real map (docs/design/maturity_map.yaml) and the real front door (site/index.html)
     -- zero HARD findings. Phase A's exit assertion.

Phase B (computed stage), C (site render) and D (publish-gate disagreement) are NOT
covered here -- each is its own atom + test.
"""
import tempfile
from pathlib import Path

from moap_coherence import (
    DEAD_ATOM_REF,
    DIAGRAM_NODE_UNMAPPED,
    MAPPING_NODE_NOT_ON_DIAGRAM,
    NODE_NO_ATOMS,
    ORPHAN_ATOM,
    coherence_findings,
    has_hard_findings,
    map_atom_ids,
    map_atom_lanes,
)

SITE = Path(__file__).resolve().parent
import json


def _kinds(findings):
    return {kind for kind, _, _ in findings}


# --- LIVE GATE ---------------------------------------------------------------
def test_live_mapping_coheres():
    """LIVE GATE (§6 Phase A): the real node->atom mapping coheres with the real map
    and the real front-door diagram -- no empty nodes, no stale atom refs, and the
    mapping's node set equals the diagram's node set. If this reds, the mapping has
    drifted from one of the two things it binds (fix the mapping, not the map)."""
    findings = coherence_findings()
    hard = [f for f in findings if f[0] != ORPHAN_ATOM]
    assert not has_hard_findings(findings), (
        "node->atom mapping does not cohere: "
        + "; ".join(f"{k}:{s} ({d})" for k, s, d in hard)
    )


def test_live_every_node_maps_at_least_one_atom():
    """Bidirectional (node->atom side): every front-door diagram node is backed by at
    least one named atom -- a node with none is a §5-backlog gap."""
    findings = coherence_findings()
    empties = [s for k, s, _ in findings if k == NODE_NO_ATOMS]
    assert not empties, f"diagram nodes with no mapped atom: {empties}"


# --- FIXTURE BUILDERS --------------------------------------------------------
def _build(tmp: Path, node_names, mapping_nodes, map_ids_with_lane):
    """A synthetic (site/, map, mapping) triple. `node_names` -> the diagram; each
    `mapping_nodes` entry is (name, [atoms]); `map_ids_with_lane` -> [(id, lane)]."""
    site = tmp / "site"
    (site / "data").mkdir(parents=True, exist_ok=True)
    spans = "".join(
        f'<div class="node"><span class="node-name">{n}</span></div>' for n in node_names
    )
    (site / "index.html").write_text(f'<div class="nodes">{spans}</div>', encoding="utf-8")
    mapping = {"nodes": [{"id": n.lower(), "name": n, "atoms": a} for n, a in mapping_nodes]}
    (site / "data" / "moap_node_atoms.json").write_text(json.dumps(mapping), encoding="utf-8")
    map_txt = "".join(f"- id: {i}\n  lane: {lane}\n" for i, lane in map_ids_with_lane)
    (tmp / "map.yaml").write_text(map_txt, encoding="utf-8")
    return site, tmp / "map.yaml", site / "data" / "moap_node_atoms.json"


def _find(tmp):
    s, m, g = tmp
    return coherence_findings(site=s, map_path=m, mapping_path=g)


def test_clean_fixture_has_no_hard_findings():
    """Independence: a coherent triple (diagram == mapping node set, every atom exists,
    every node non-empty) yields zero HARD findings -- the control is not always-red."""
    with tempfile.TemporaryDirectory() as d:
        tmp = _build(
            Path(d),
            node_names=["Alpha", "Beta"],
            mapping_nodes=[("Alpha", ["X1"]), ("Beta", ["X2"])],
            map_ids_with_lane=[("X1", "L"), ("X2", "L")],
        )
        findings = _find(tmp)
        assert not has_hard_findings(findings), findings
        assert _kinds(findings) - {ORPHAN_ATOM} == set(), findings


def test_empty_node_is_flagged():
    """R15 direction 1: a diagram node mapped to zero atoms fires NODE_NO_ATOMS."""
    with tempfile.TemporaryDirectory() as d:
        tmp = _build(
            Path(d),
            node_names=["Alpha", "Beta"],
            mapping_nodes=[("Alpha", ["X1"]), ("Beta", [])],
            map_ids_with_lane=[("X1", "L"), ("X2", "L")],
        )
        findings = _find(tmp)
        assert NODE_NO_ATOMS in _kinds(findings), findings
        assert has_hard_findings(findings)


def test_dead_atom_ref_is_flagged():
    """R15 direction 2: a node referencing an atom absent from the map fires
    DEAD_ATOM_REF (the drift guard -- catches a renamed/removed atom)."""
    with tempfile.TemporaryDirectory() as d:
        tmp = _build(
            Path(d),
            node_names=["Alpha"],
            mapping_nodes=[("Alpha", ["X1", "GHOST_ATOM"])],
            map_ids_with_lane=[("X1", "L")],
        )
        findings = _find(tmp)
        assert DEAD_ATOM_REF in _kinds(findings), findings
        assert any(s == "Alpha" and "GHOST_ATOM" in det for k, s, det in findings if k == DEAD_ATOM_REF)
        assert has_hard_findings(findings)


def test_diagram_node_unmapped_is_flagged():
    """R15 direction 3: a node on the front-door diagram with no mapping entry fires
    DIAGRAM_NODE_UNMAPPED (the diagram grew a node the mapping does not cover)."""
    with tempfile.TemporaryDirectory() as d:
        tmp = _build(
            Path(d),
            node_names=["Alpha", "Beta", "Gamma"],
            mapping_nodes=[("Alpha", ["X1"]), ("Beta", ["X2"])],
            map_ids_with_lane=[("X1", "L"), ("X2", "L")],
        )
        findings = _find(tmp)
        assert DIAGRAM_NODE_UNMAPPED in _kinds(findings), findings
        assert any(s == "Gamma" for k, s, _ in findings if k == DIAGRAM_NODE_UNMAPPED)
        assert has_hard_findings(findings)


def test_mapping_node_not_on_diagram_is_flagged():
    """R15 direction 4: a mapping entry naming a node absent from the diagram fires
    MAPPING_NODE_NOT_ON_DIAGRAM (a renamed/removed diagram node left the mapping stale)."""
    with tempfile.TemporaryDirectory() as d:
        tmp = _build(
            Path(d),
            node_names=["Alpha"],
            mapping_nodes=[("Alpha", ["X1"]), ("Ghost", ["X2"])],
            map_ids_with_lane=[("X1", "L"), ("X2", "L")],
        )
        findings = _find(tmp)
        assert MAPPING_NODE_NOT_ON_DIAGRAM in _kinds(findings), findings
        assert any(s == "Ghost" for k, s, _ in findings if k == MAPPING_NODE_NOT_ON_DIAGRAM)
        assert has_hard_findings(findings)


def test_orphan_atom_is_flagged_soft():
    """Bidirectional (atom->node side): an atom present in the map but behind no node
    fires the soft ORPHAN_ATOM flag -- reported for the §5 backlog, NOT a hard failure
    (has_hard_findings stays False when orphans are the only finding)."""
    with tempfile.TemporaryDirectory() as d:
        tmp = _build(
            Path(d),
            node_names=["Alpha"],
            mapping_nodes=[("Alpha", ["X1"])],
            map_ids_with_lane=[("X1", "L"), ("X_ORPHAN", "L")],
        )
        findings = _find(tmp)
        assert ORPHAN_ATOM in _kinds(findings), findings
        assert any(s == "X_ORPHAN" for k, s, _ in findings if k == ORPHAN_ATOM)
        assert not has_hard_findings(findings), "orphan alone must not be a hard failure"


def test_map_atom_lanes_parses_real_map():
    """The lane parser (used for the orphan rollup) reads the real map: ids non-empty
    and each maps to a lane string."""
    lanes = map_atom_lanes()
    assert len(lanes) > 50, len(lanes)
    assert map_atom_ids() == set(lanes)
    assert all(isinstance(v, str) and v for v in lanes.values())
