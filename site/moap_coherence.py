#!/usr/bin/env python3
"""Coherence-by-derivation (§6) -- PHASE A: the node->atom mapping + its integrity check.

Director ruling DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27, deliverable §6:
the MODEL, the DIAGRAM, the SITE and the MAP "must not be kept in sync by hand; three of
them must be derived from one." THE_MODEL_ON_A_PAGE.md is the source of truth; every diagram
node maps to named atoms; a node's stage is later COMPUTED from those atoms' levels (Phase B),
rendered from the same derivation on the site (Phase C), with publish FAILING on any
model/diagram/site/map disagreement (Phase D).

THIS FILE IS PHASE A ONLY -- the keystone everything else derives from:
  * load the canonical mapping (site/data/moap_node_atoms.json)
  * prove it COHERES with the two things it binds:
      - the MAP  (docs/design/maturity_map.yaml): every atom a node names must exist there,
        and no node may be empty  -> a mapping that references a renamed/removed atom, or
        leaves a node with nothing behind it, is drift and fails loudly (a §5-backlog gap).
      - the DIAGRAM (site/index.html front-door .node blocks): the mapping's node set and the
        live diagram's node set must be identical -- a node on the diagram with no mapping
        entry, or a mapping entry naming a node not on the diagram, is a bidirectional gap.
  * flag ORPHAN atoms: a map atom mapped to no node "serves no part of the model and must be
    questioned" (§6, bidirectional). Reported for the §5 backlog -- NOT a hard failure, since
    much internal machinery legitimately sits behind 'Governance & method' or is pure harness.

Stage COMPUTATION (Phase B), site RENDERING (Phase C) and the publish GATE (Phase D) are
deliberately NOT here -- each is its own atom + commit. This module never writes the map
(docs/design/maturity_map.yaml is a schema_sim_structure gate); it reads it.

Run standalone for the report:  python3 site/moap_coherence.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
_REPO = SITE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# The map is TWO files since 2026-08-26 (the harness-lane prune): `maturity_map.yaml` holds the
# atoms that still carry work, `maturity_map_closed.yaml` the ones that have reached target.
# EVERY text read below goes through the store, which returns both halves concatenated, because
# this module's node stages are derived from atom LEVELS: a reader that saw only the live half
# would find no atom at target behind a finished node and render it Planned. That is the exact
# hazard the split was designed around, and the store refuses rather than degrades.
from tools import maturity_map_store as map_store  # noqa: E402

_MAP = map_store.LIVE_PATH
_MAPPING = SITE / "data" / "moap_node_atoms.json"

# Front-door diagram node NAMES live in <span class="node-name">...</span>.
_NODE_NAME = re.compile(r'<span class="node-name">(.*?)</span>', re.DOTALL)

# Hard finding kinds (mapping-integrity defects -- a gate would fail on these).
NODE_NO_ATOMS = "NODE_NO_ATOMS"
DEAD_ATOM_REF = "DEAD_ATOM_REF"
DIAGRAM_NODE_UNMAPPED = "DIAGRAM_NODE_UNMAPPED"
MAPPING_NODE_NOT_ON_DIAGRAM = "MAPPING_NODE_NOT_ON_DIAGRAM"
# Soft finding kind (reported for the §5 backlog, not a failure).
ORPHAN_ATOM = "ORPHAN_ATOM"

_HARD = frozenset(
    {NODE_NO_ATOMS, DEAD_ATOM_REF, DIAGRAM_NODE_UNMAPPED, MAPPING_NODE_NOT_ON_DIAGRAM}
)


def load_mapping(path: Path = _MAPPING) -> dict:
    """The canonical node->atom mapping (site/data/moap_node_atoms.json)."""
    return json.loads(path.read_text(encoding="utf-8"))


def map_atom_lanes(path: Path = _MAP) -> dict[str, str]:
    """{atom id -> lane} for every atom in the maturity map. Parsed off the
    committed text (no yaml dependency at site scope): an atom record opens with
    `- id: <slug>` and carries a following `lane: <lane>` line before the next id.
    Lane is used only for the orphan rollup; a missing lane resolves to '?'."""
    lanes: dict[str, str] = {}
    current: str | None = None
    for line in map_store.map_text(path).splitlines():
        m_id = re.match(r"\s*-\s+id:\s*([A-Za-z0-9_]+)\s*$", line)
        if m_id:
            current = m_id.group(1)
            lanes.setdefault(current, "?")
            continue
        m_lane = re.match(r"\s+lane:\s*([A-Za-z0-9_]+)\s*$", line)
        if m_lane and current is not None:
            lanes[current] = m_lane.group(1)
    return lanes


def map_atom_ids(path: Path = _MAP) -> set[str]:
    """The set of every atom id declared in the maturity map. Parsed off the
    committed text (no yaml dependency at site scope) -- ids are `- id: <slug>`
    lines, the canonical atom-record header in docs/design/maturity_map.yaml."""
    return set(map_atom_lanes(path))


def diagram_node_names(site: Path = SITE) -> list[str]:
    """The front-door diagram node names, in document order, entity-decoded so
    they compare equal to the plain-text names in the mapping ('Governance &
    method', not 'Governance &amp; method')."""
    front = site / "index.html"
    if not front.is_file():
        return []
    return [
        html.unescape(m.group(1)).strip()
        for m in _NODE_NAME.finditer(front.read_text(encoding="utf-8"))
    ]


def coherence_findings(
    site: Path = SITE, map_path: Path = _MAP, mapping_path: Path = _MAPPING
) -> list[tuple[str, str, str]]:
    """Every mapping-coherence finding as (kind, subject, detail). Empty (of HARD
    kinds) means the mapping coheres with both the map and the diagram. ORPHAN_ATOM
    entries may be present and are informational (§5 backlog), never a gate failure
    -- callers gate on `has_hard_findings(...)`, not on emptiness."""
    findings: list[tuple[str, str, str]] = []
    mapping = load_mapping(mapping_path)
    nodes = mapping.get("nodes", [])
    live_atom_ids = map_atom_ids(map_path)

    mapped_atoms: set[str] = set()
    mapping_node_names: list[str] = []
    for node in nodes:
        name = node.get("name", node.get("id", "?"))
        mapping_node_names.append(name)
        atoms = node.get("atoms", []) or []
        if not atoms:
            findings.append(
                (NODE_NO_ATOMS, name, "diagram node maps to no atom (bidirectional gap -> §5 backlog)")
            )
        for atom in atoms:
            mapped_atoms.add(atom)
            if atom not in live_atom_ids:
                findings.append(
                    (DEAD_ATOM_REF, name, f"references atom {atom!r} absent from the maturity map (stale/renamed)")
                )

    # Diagram <-> mapping node-set agreement (both directions).
    diagram = diagram_node_names(site)
    diagram_set, mapping_set = set(diagram), set(mapping_node_names)
    for name in diagram:
        if name not in mapping_set:
            findings.append(
                (DIAGRAM_NODE_UNMAPPED, name, "front-door diagram node has no entry in the node->atom mapping")
            )
    for name in mapping_node_names:
        if name not in diagram_set:
            findings.append(
                (MAPPING_NODE_NOT_ON_DIAGRAM, name, "mapping names a node not present on the front-door diagram")
            )

    # Orphan atoms: in the map, behind no front-door diagram node. §6 says these
    # "must be questioned" -- honestly, either the atom belongs under an existing
    # node's claim (widen the mapping) or the front door omits it (§5 backlog);
    # which is the question. Reported soft, never a hard failure.
    for atom in sorted(live_atom_ids - mapped_atoms):
        findings.append(
            (ORPHAN_ATOM, atom, "behind no front-door node -- widen a node's mapping or log a §5 front-door-coverage gap")
        )
    return findings


def has_hard_findings(findings: list[tuple[str, str, str]]) -> bool:
    """True if any mapping-integrity defect is present (excludes ORPHAN_ATOM)."""
    return any(kind in _HARD for kind, _, _ in findings)


def main() -> int:
    findings = coherence_findings()
    hard = [f for f in findings if f[0] in _HARD]
    orphans = [f for f in findings if f[0] == ORPHAN_ATOM]
    print("=== §6 coherence-by-derivation -- Phase A: node->atom mapping integrity ===\n")
    print(f"HARD findings (mapping does not cohere with map/diagram): {len(hard)}")
    for kind, subject, detail in hard:
        print(f"  [{kind}] {subject}: {detail}")
    lanes = map_atom_lanes()
    by_lane: dict[str, int] = {}
    for _, atom, _ in orphans:
        by_lane[lanes.get(atom, "?")] = by_lane.get(lanes.get(atom, "?"), 0) + 1
    print(f"\nORPHAN atoms (in map, behind no front-door node -- §5 backlog): {len(orphans)}")
    print("  by lane:")
    for lane, n in sorted(by_lane.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"    {lane:24s} {n}")
    print(f"\nHARD total: {len(hard)}  ORPHAN total: {len(orphans)}")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
