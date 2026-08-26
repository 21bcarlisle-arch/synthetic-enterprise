#!/usr/bin/env python3
"""Coherence-by-derivation (§6) -- PHASE B: the COMPUTED node stage.

Director ruling DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27, deliverable §6:
the MODEL, the DIAGRAM, the SITE and the MAP "must not be kept in sync by hand; three of
them must be derived from one." Phase A (moap_coherence.py) fixed the node->atom mapping and
proved it coheres. Phase B is the DERIVATION itself: a node's Live/Building/Planned stage is a
PURE FUNCTION of its mapped atoms' levels in docs/design/maturity_map.yaml -- never hand-set.

THE RULE (verbatim from site/data/moap_node_atoms.json `_derivation_rule`):
  * LIVE     = every mapped atom is AT TARGET (level_current >= level_target).
  * BUILDING = at least one mapped atom is BELOW target (but some work has started).
  * PLANNED  = none started (every mapped atom sits at level 0).
Precedence follows that order (LIVE checked first), matching the documented rule.

Independence (R15 / the tautology killer, LAW C): the computed stage reads the atoms' ACTUAL
levels from the map -- a DIFFERENT source than the site's hand-authored `declared_stage`. The
two can therefore DISAGREE, which is the whole point: `stage_disagreements()` surfaces every
node whose live-site claim outruns (or lags) its atoms' real levels. Phase B only COMPUTES and
REPORTS that; the publish GATE that FAILS on a disagreement is Phase D (its own atom + commit).
This module never writes docs/design/maturity_map.yaml (a schema_sim_structure gate) -- it reads it.

Run standalone for the per-node stage report:  python3 site/moap_stage.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from moap_coherence import _MAP, _MAPPING, load_mapping

SITE = Path(__file__).resolve().parent

# Stage vocabulary -- the exact title-case strings the live site's `declared_stage`
# uses (site/data/moap_node_atoms.json), so Phase C/D compare computed vs declared directly.
LIVE = "Live"
BUILDING = "Building"
PLANNED = "Planned"

_ID = re.compile(r"\s*-\s+id:\s*([A-Za-z0-9_]+)\s*$")
_CUR = re.compile(r"\s+level_current:\s*([0-9]+)\s*$")
_TGT = re.compile(r"\s+level_target:\s*([0-9]+)\s*$")

# An atom a node references but which is ABSENT from the map is a Phase-A coherence
# defect (DEAD_ATOM_REF, gated there). Phase B must still never crash and never let a
# missing atom FALSE-GREEN a node, so an unknown atom resolves to "started but below
# target" (current 0, target 1) -- it can only ever drag a node toward Building/Planned.
_UNKNOWN_ATOM = {"current": 0, "target": 1}


def map_atom_levels(path: Path = _MAP) -> dict[str, dict[str, int]]:
    """{atom id -> {'current': level_current, 'target': level_target}} for every atom in
    the maturity map. Parsed off the committed text (no yaml dependency at site scope, same
    convention as moap_coherence.map_atom_lanes): an atom record opens with `- id: <slug>`
    and carries `level_current:`/`level_target:` lines before the next id. A target that is
    absent from a record defaults to 1 (not 0) so a level-less atom can never vacuously read
    'at target' and false-green its node."""
    levels: dict[str, dict[str, int]] = {}
    seen_target: set[str] = set()
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m_id = _ID.match(line)
        if m_id:
            current = m_id.group(1)
            levels.setdefault(current, {"current": 0, "target": 1})
            continue
        if current is None:
            continue
        m_cur = _CUR.match(line)
        if m_cur:
            levels[current]["current"] = int(m_cur.group(1))
            continue
        m_tgt = _TGT.match(line)
        if m_tgt:
            levels[current]["target"] = int(m_tgt.group(1))
            seen_target.add(current)
    return levels


def compute_stage(atom_levels: list[dict[str, int]]) -> str:
    """The derivation, as a pure function of a node's mapped atoms' levels. Returns LIVE /
    BUILDING / PLANNED per THE RULE above. An empty node (a Phase-A defect, gated there) is
    guarded to PLANNED rather than vacuously LIVE (`all([])` is True) -- it can never
    false-green."""
    if not atom_levels:
        return PLANNED
    # A CLOSED ATOM CANNOT MAKE A NODE LIVE, and without this line it is the easiest false-green
    # in the module. `level_target: 0` is how the map records a decision NOT to build something --
    # eight D-lane atoms were closed that way on 2026-08-26 ("the record is the deliverable: no
    # build closes it, because the answer is a longer book and not more code. Reopen by raising
    # level_target back to 2"). Read through the rule above, such an atom satisfies
    # `current >= target` as `0 >= 0` and reports itself AT TARGET, so a node whose capability was
    # explicitly abandoned would publish as Live on the front door. That is the same vacuous-truth
    # shape this function already guards on the empty list, arriving through a different door.
    #
    # EXCLUDED, NOT COUNTED AS BELOW TARGET, because a closed atom is not work in progress either:
    # counting it as below target would peg every node touching one to Building for ever. A node
    # left with NO open atoms falls through to PLANNED -- never LIVE -- which is the conservative
    # end of a three-value vocabulary and the one Phase D can surface as a disagreement.
    open_atoms = [a for a in atom_levels if a.get("target", 1) > 0]
    if not open_atoms:
        return PLANNED
    if all(a["current"] >= a["target"] for a in open_atoms):
        return LIVE
    if all(a["current"] == 0 for a in open_atoms):
        return PLANNED
    return BUILDING


def node_stages(
    map_path: Path = _MAP, mapping_path: Path = _MAPPING
) -> list[dict]:
    """Per front-door node: its declared stage (hand-set on the site today) alongside the
    COMPUTED stage derived from its mapped atoms' real levels, plus the per-atom detail. This
    is the single derivation Phase C renders and Phase D gates on -- the site can no longer
    hand-set a stage that outruns the map."""
    mapping = load_mapping(mapping_path)
    levels = map_atom_levels(map_path)
    out: list[dict] = []
    for node in mapping.get("nodes", []):
        atoms = node.get("atoms", []) or []
        atom_detail = []
        for atom in atoms:
            lv = levels.get(atom, _UNKNOWN_ATOM)
            atom_detail.append(
                {
                    "id": atom,
                    "current": lv["current"],
                    "target": lv["target"],
                    "at_target": lv["current"] >= lv["target"],
                    "in_map": atom in levels,
                }
            )
        computed = compute_stage(atom_detail)
        declared = node.get("declared_stage")
        out.append(
            {
                "id": node.get("id"),
                "name": node.get("name", node.get("id", "?")),
                "declared_stage": declared,
                "computed_stage": computed,
                "matches": declared == computed,
                "atoms": atom_detail,
            }
        )
    return out


def stage_disagreements(
    map_path: Path = _MAP, mapping_path: Path = _MAPPING
) -> list[dict]:
    """Every node whose hand-set `declared_stage` disagrees with the stage COMPUTED from its
    atoms' real levels. Empty means model/map/site agree on every node's stage. This is the
    exact set Phase D's publish gate fails on -- exposed here as a pure query (Phase B does not
    itself gate). A node with `declared_stage == null` (never hand-set) is NOT a disagreement:
    it has nothing to contradict the computed value, which becomes its rendered stage."""
    return [
        s
        for s in node_stages(map_path, mapping_path)
        if s["declared_stage"] is not None and not s["matches"]
    ]


def main() -> int:
    stages = node_stages()
    print("=== §6 coherence-by-derivation -- Phase B: computed node stage ===\n")
    print(f"{'node':22s} {'declared':10s} {'computed':10s}  atoms (current/target)")
    for s in stages:
        flag = "" if s["matches"] or s["declared_stage"] is None else "  <-- DISAGREES"
        atoms = " ".join(f"{a['id']}={a['current']}/{a['target']}" for a in s["atoms"])
        print(
            f"{s['name']:22s} {str(s['declared_stage']):10s} {s['computed_stage']:10s}{flag}\n"
            f"    {atoms}"
        )
    disagreements = stage_disagreements()
    print(f"\nDISAGREEMENTS (declared != computed -- Phase D would FAIL here): {len(disagreements)}")
    for d in disagreements:
        print(f"  [{d['name']}] declared={d['declared_stage']} computed={d['computed_stage']}")
    # Phase B never gates -- it reports. Exit 0 always (the gate is Phase D).
    return 0


if __name__ == "__main__":
    sys.exit(main())
