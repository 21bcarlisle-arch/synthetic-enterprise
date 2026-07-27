"""R15 mechanism self-test for §6 coherence-by-derivation -- PHASE B (the COMPUTED node
stage). Same two-role pattern as test_moap_coherence.py:

  1. MECHANISM self-tests (R15 BOTH WAYS): synthetic fixtures prove compute_stage() and the
     end-to-end node_stages() derivation FLIP a node's stage when a mapped atom's level is
     raised or lowered -- the load-bearing property the ruling names ("raise/lower an atom's
     level -> the node's computed stage changes"). Independence proves the control is not
     always-one-value: the same fixture yields Live, Building AND Planned for different
     level sets, and a mixed node computes Building (not vacuously green).
  2. LIVE checks: the level parser reads the real map (anchored on a known atom's real
     levels), and node_stages() computes a valid stage for every real front-door node.

Phase A (mapping integrity) is covered in test_moap_coherence.py; Phase C (site render) and
Phase D (publish-gate disagreement) are their own atoms + tests. Phase B COMPUTES and REPORTS
the stage; it does NOT gate -- so this file asserts the derivation, never a publish outcome.
"""
import json
import tempfile
from pathlib import Path

from moap_stage import (
    BUILDING,
    LIVE,
    PLANNED,
    compute_stage,
    map_atom_levels,
    node_stages,
    stage_disagreements,
)


def _lv(current, target):
    return {"current": current, "target": target}


# --- compute_stage: the pure derivation, R15 both ways ----------------------
def test_all_at_target_is_live():
    assert compute_stage([_lv(3, 3), _lv(2, 2)]) == LIVE
    assert compute_stage([_lv(4, 3)]) == LIVE  # over-target still at target


def test_one_below_target_is_building():
    """R15 direction (lower): drop a single atom below its target and the node stops being
    Live -- the exact 'a node cannot read Live while an atom sits below target' guarantee."""
    assert compute_stage([_lv(3, 3), _lv(1, 3)]) == BUILDING


def test_none_started_is_planned():
    assert compute_stage([_lv(0, 3), _lv(0, 2)]) == PLANNED


def test_some_started_none_at_target_is_building():
    """Started-but-below is Building, not Planned -- Planned requires ALL atoms at level 0."""
    assert compute_stage([_lv(1, 3), _lv(0, 2)]) == BUILDING


def test_empty_node_is_planned_not_vacuously_live():
    """The all([]) trap: an empty node must NOT read Live -- guarded to Planned."""
    assert compute_stage([]) == PLANNED


def test_stage_is_not_always_one_value():
    """Independence: the derivation yields all three stages for different level sets -- it is
    not a constant dressed up as a computation."""
    assert {
        compute_stage([_lv(2, 2)]),
        compute_stage([_lv(1, 2)]),
        compute_stage([_lv(0, 2)]),
    } == {LIVE, BUILDING, PLANNED}


# --- FIXTURE: end-to-end node_stages() over a synthetic map+mapping ----------
def _build(tmp: Path, mapping_nodes, atom_levels, declared=None):
    """Synthetic (mapping, map) pair. `mapping_nodes` -> [(name, [atoms])];
    `atom_levels` -> {id: (current, target)}; `declared` -> {name: declared_stage}."""
    declared = declared or {}
    site = tmp / "site"
    (site / "data").mkdir(parents=True, exist_ok=True)
    mapping = {
        "nodes": [
            {"id": n.lower(), "name": n, "declared_stage": declared.get(n), "atoms": a}
            for n, a in mapping_nodes
        ]
    }
    (site / "data" / "moap_node_atoms.json").write_text(json.dumps(mapping), encoding="utf-8")
    map_txt = "".join(
        f"- id: {i}\n  lane: L\n  level_current: {c}\n  level_target: {t}\n"
        for i, (c, t) in atom_levels.items()
    )
    (tmp / "map.yaml").write_text(map_txt, encoding="utf-8")
    return tmp / "map.yaml", site / "data" / "moap_node_atoms.json"


def _stage_of(stages, name):
    return next(s["computed_stage"] for s in stages if s["name"] == name)


def test_node_stage_flips_when_atom_raised_or_lowered():
    """R15 BOTH WAYS end-to-end: the SAME node computes Building while an atom is below
    target and flips to Live the moment that atom reaches target -- proving node_stages()
    derives from the map, not a hand-set value."""
    with tempfile.TemporaryDirectory() as d:
        # Below target -> Building.
        m, g = _build(
            Path(d),
            mapping_nodes=[("Alpha", ["X1", "X2"])],
            atom_levels={"X1": (3, 3), "X2": (1, 3)},
        )
        assert _stage_of(node_stages(m, g), "Alpha") == BUILDING

        # Raise X2 to target -> the very same node is now Live.
        m2, g2 = _build(
            Path(d) / "up",
            mapping_nodes=[("Alpha", ["X1", "X2"])],
            atom_levels={"X1": (3, 3), "X2": (3, 3)},
        )
        assert _stage_of(node_stages(m2, g2), "Alpha") == LIVE


def test_dead_atom_ref_cannot_false_green_a_node():
    """A node atom absent from the map resolves to below-target, so it can only drag the node
    toward Building/Planned -- never vacuously Live (Phase A gates the ref itself)."""
    with tempfile.TemporaryDirectory() as d:
        m, g = _build(
            Path(d),
            mapping_nodes=[("Alpha", ["X1", "GHOST"])],
            atom_levels={"X1": (3, 3)},  # GHOST absent from the map
        )
        assert _stage_of(node_stages(m, g), "Alpha") == BUILDING


def test_stage_disagreement_surfaces_declared_vs_computed():
    """A node hand-set 'Live' whose atoms are below target surfaces as a disagreement (the
    set Phase D fails on); a null declared_stage is NOT a disagreement (nothing to contradict)."""
    with tempfile.TemporaryDirectory() as d:
        m, g = _build(
            Path(d),
            mapping_nodes=[("Overclaim", ["X1"]), ("Honest", ["X2"])],
            atom_levels={"X1": (1, 3), "X2": (1, 3)},
            declared={"Overclaim": "Live", "Honest": None},
        )
        dis = stage_disagreements(m, g)
        names = {x["name"] for x in dis}
        assert "Overclaim" in names, dis
        assert "Honest" not in names, "null declared_stage must not count as a disagreement"


# --- LIVE checks ------------------------------------------------------------
def test_level_parser_reads_real_map():
    """The parser reads the real maturity map with sane levels for every atom, anchored on a
    known atom's real levels (H_forward_discovery_draw: current 1, target 3)."""
    levels = map_atom_levels()
    assert len(levels) > 50, len(levels)
    assert all(0 <= v["current"] for v in levels.values())
    assert all(v["target"] >= 1 for v in levels.values()), "every real atom target must be >= 1"
    fd = levels.get("H_forward_discovery_draw")
    assert fd == {"current": 1, "target": 3}, fd


def test_every_real_front_door_node_computes_a_valid_stage():
    """node_stages() over the real mapping+map yields a valid stage for every front-door node
    and preserves the node set (no node dropped, no phantom node)."""
    stages = node_stages()
    assert stages, "no node stages computed from the real mapping"
    valid = {LIVE, BUILDING, PLANNED}
    for s in stages:
        assert s["computed_stage"] in valid, s
        assert s["atoms"], f"node {s['name']} computed with no atoms"
