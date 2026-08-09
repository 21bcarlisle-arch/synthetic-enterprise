"""R15 mutation tests for the live fidelity-evidence bridge
(`background/live_fidelity_evidence.py`).

Each control is proven to FIRE on its own named defect and CLEAR when the
defect is removed -- never happy-path only (R15). Covered:

  * FIRES   -- a real belief-vs-truth gap flows through to all three surfaces.
  * QUIET   -- a zero gap still emits + passes the gate (an honest zero is
               evidence too), but the grid is never `clean` while cells are
               untested.
  * WALL    -- the built G3 chain holds no belief leak; a truth_ref mutation
               makes `assert_no_belief_leak` fire (the guard is load-bearing).
  * GATE    -- the emitted record passes its own emit-DoD gate; an `asserted`
               provenance without a simplification_id makes the gate fire and
               `emit_live_fidelity_evidence` RAISE (fail-closed, both
               directions).
  * IGNORANCE -- one measured cell leaves the other 14 in the map of ignorance
               (never silently clean).
  * WALL-STANCE -- the module imports neither sim nor company (AST scan).
  * DETERMINISM -- idempotent, keyed by rel_id (C-S2 replay-safe).
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from background.live_fidelity_evidence import (
    DEFAULT_ATOM_ID,
    LIVE_CELL_ID,
    CellMeasurement,
    LiveFidelityGateFailure,
    build_inspection_chain,
    DETECTION_MEASURE_BOTH_DIRECTIONS,
    DETECTION_MEASURE_RECALL_ONLY,
    build_ledger_record,
    cell_rel_id,
    emit_live_fidelity_cells,
    emit_live_fidelity_evidence,
)
from background.fidelity_evidence_ledger import (
    append_record,
    fidelity_evidence_gate,
)
from background.fidelity_inspection_chain import (
    BeliefActionRecord,
    BeliefLeakError,
    assert_no_belief_leak,
)

_AS_OF = "2025-12-31"


@pytest.fixture()
def ledger(tmp_path) -> Path:
    return tmp_path / "fidelity_evidence_ledger.json"


# --------------------------------------------------------------------------
# FIRES -- a real gap reaches all three surfaces
# --------------------------------------------------------------------------

def test_real_gap_flows_to_all_three_surfaces(ledger):
    em = emit_live_fidelity_evidence(
        detection_gap=0.20, true_failures=10, believed_failures=8,
        as_of=_AS_OF, ledger_path=ledger,
    )
    # G1 grid: the measured cell carries the gap severity.
    assert em.grid_score.severities[LIVE_CELL_ID] == pytest.approx(0.20)
    assert em.cell_id == LIVE_CELL_ID
    # G2 ledger: exactly the emitted record, passing the gate.
    assert em.gate.passed
    data = json.loads(ledger.read_text())
    assert "live_payment_detection_gap" in data
    assert data["live_payment_detection_gap"]["relationship"]["detection_gap"] == 0.20
    # G3 chain: a belief-action record carrying the gap, wall-clean.
    belief_nodes = em.chain.nodes_of_layer("BELIEF_ACTION")
    assert len(belief_nodes) == 1
    assert belief_nodes[0].gap == pytest.approx(0.20)
    assert belief_nodes[0].truth_ref is None


# --------------------------------------------------------------------------
# QUIET -- a zero gap is still honest evidence, but never "clean"
# --------------------------------------------------------------------------

def test_zero_gap_still_emits_and_passes_but_grid_not_clean(ledger):
    em = emit_live_fidelity_evidence(
        detection_gap=0.0, true_failures=10, believed_failures=10,
        as_of=_AS_OF, ledger_path=ledger,
    )
    assert em.gate.passed  # a measured zero is evidence, not a skip
    # The single measured cell reads its zero, but 14 untested cells keep the
    # grid from ever reporting clean.
    assert em.grid_score.clean is False
    assert len(em.grid_score.untested_cells) == 14


# --------------------------------------------------------------------------
# IGNORANCE -- one lit corner, the rest honestly dark
# --------------------------------------------------------------------------

def test_one_measured_cell_leaves_fourteen_untested(ledger):
    em = emit_live_fidelity_evidence(
        detection_gap=0.15, true_failures=5, believed_failures=4,
        as_of=_AS_OF, ledger_path=ledger,
    )
    assert LIVE_CELL_ID not in em.grid_score.untested_cells
    assert len(em.grid_score.untested_cells) == 14
    # Fail-open: every untested cell scores >= the worst measured cell, so the
    # worst cell is never the measured one alone unless it is the max.
    assert em.grid_score.worst_cell in em.grid_score.severities


# --------------------------------------------------------------------------
# PER-CELL (regime-partitioned) emission -- SOURCE 2 of
# PLANNER_MINTED_payment_grid_coverage_2026-07-25. Lights >1 cell honestly.
# --------------------------------------------------------------------------

def test_multicell_lights_each_measured_cell_distinctly(ledger):
    em = emit_live_fidelity_cells(
        cell_gaps={
            "A1_G1": CellMeasurement(detection_gap=0.10, true_failures=8,
                                     believed_failures=7, regime_label="G1_calm"),
            "A1_G2": CellMeasurement(detection_gap=0.42, true_failures=20,
                                     believed_failures=6, regime_label="G2_crisis"),
        },
        as_of=_AS_OF, ledger_path=ledger,
    )
    assert em.gate.passed
    assert set(em.cell_ids) == {"A1_G1", "A1_G2"}
    # Each cell carries its OWN measured gap into the grid.
    assert em.grid_score.severities["A1_G1"] == pytest.approx(0.10)
    assert em.grid_score.severities["A1_G2"] == pytest.approx(0.42)
    # Two lit cells -> 13 dark; the grid is NEVER clean while any cell is dark.
    assert len(em.grid_score.untested_cells) == 13
    assert em.grid_score.clean is False
    # Two distinct ledger rows, keyed by per-cell rel_id (no overwrite).
    data = json.loads(ledger.read_text())
    assert cell_rel_id("A1_G1") in data and cell_rel_id("A1_G2") in data
    assert data[cell_rel_id("A1_G1")]["relationship"]["detection_gap"] == 0.10
    assert data[cell_rel_id("A1_G2")]["relationship"]["detection_gap"] == 0.42


def test_multicell_widening_never_makes_the_grid_cleaner(ledger, tmp_path):
    """Lighting MORE cells is pure coverage: an extra measured cell can only
    RAISE the worst-cell severity, never lower the untested floor (fail-open).
    Prove it -- add a WORSE second cell and the fidelity score cannot improve."""
    one = emit_live_fidelity_cells(
        cell_gaps={"A1_G1": CellMeasurement(0.10, 8, 7, "G1_calm")},
        as_of=_AS_OF, ledger_path=tmp_path / "one.json",
    )
    two = emit_live_fidelity_cells(
        cell_gaps={
            "A1_G1": CellMeasurement(0.10, 8, 7, "G1_calm"),
            "A1_G2": CellMeasurement(0.42, 20, 6, "G2_crisis"),
        },
        as_of=_AS_OF, ledger_path=ledger,
    )
    # More measured cells -> fewer dark cells, never MORE.
    assert len(two.grid_score.untested_cells) < len(one.grid_score.untested_cells)
    # Fidelity score (worst cell, lower=better) never IMPROVES by adding a cell.
    assert two.grid_score.fidelity_score >= one.grid_score.fidelity_score


def test_multicell_records_carry_the_partitioned_simplification(ledger):
    """The honest residual: each per-cell record names that DETECTION is
    regime-resolved while BELIEF/AGEING stay regime-mixed -- not the blanket
    single-cell `attributed_to_G2` simplification."""
    emit_live_fidelity_cells(
        cell_gaps={"A1_G1": CellMeasurement(0.10, 8, 7, "G1_calm")},
        as_of=_AS_OF, ledger_path=ledger,
    )
    rec = json.loads(ledger.read_text())[cell_rel_id("A1_G1")]
    simp = rec["relationship"]["simplification_id"]
    assert simp == "live_payment_gap_detection_regime_partitioned_belief_ageing_mixed"
    assert rec["relationship"]["provenance"] == "estimated_from_data"


def test_multicell_empty_map_raises(ledger):
    """Fail-closed: an empty cell map would silently light nothing -- refuse
    it rather than emit a vacuous 'all dark' pass."""
    with pytest.raises(ValueError):
        emit_live_fidelity_cells(cell_gaps={}, as_of=_AS_OF, ledger_path=ledger)


def test_multicell_chain_per_cell_holds_no_belief_leak(ledger):
    em = emit_live_fidelity_cells(
        cell_gaps={"A1_G1": CellMeasurement(0.10, 8, 7, "G1_calm"),
                   "A1_G2": CellMeasurement(0.42, 20, 6, "G2_crisis")},
        as_of=_AS_OF, ledger_path=ledger,
    )
    for cid, chain in em.chains.items():
        belief_nodes = chain.nodes_of_layer("BELIEF_ACTION")
        assert len(belief_nodes) == 1
        assert belief_nodes[0].truth_ref is None  # the wall in the data model
        assert belief_nodes[0].cell == cid


# --------------------------------------------------------------------------
# WALL -- the belief-leak guard is load-bearing (mutation fires it)
# --------------------------------------------------------------------------

def test_built_chain_has_no_belief_leak():
    chain = build_inspection_chain(
        detection_gap=0.2, true_failures=10, believed_failures=8, as_of=_AS_OF,
    )
    # Clean as built.
    assert_no_belief_leak(chain)


def test_truth_ref_mutation_makes_the_wall_guard_fire():
    chain = build_inspection_chain(
        detection_gap=0.2, true_failures=10, believed_failures=8, as_of=_AS_OF,
    )
    # MUTATION: a belief record that smuggles the answer key across the wall.
    chain.add_belief_action(BeliefActionRecord(
        belief_id="leaky_belief", cell=LIVE_CELL_ID,
        belief={"observed_failures": 8}, action={"kind": "x"},
        gap=0.2, as_of=_AS_OF, truth_ref="w2_11_answer_key",
    ))
    with pytest.raises(BeliefLeakError):
        assert_no_belief_leak(chain)


# --------------------------------------------------------------------------
# GATE -- emit-DoD gate is load-bearing, both directions
# --------------------------------------------------------------------------

def test_good_record_passes_the_gate(ledger):
    rec = build_ledger_record(
        detection_gap=0.2, true_failures=10, believed_failures=8,
    )
    append_record(rec, ledger_path=ledger)
    assert fidelity_evidence_gate(DEFAULT_ATOM_ID, ledger_path=ledger).passed


def test_asserted_without_simplification_makes_the_gate_fire(ledger):
    # MUTATION: the same relationship dressed as 'asserted' with no
    # simplification_id -- the R10 defect the gate exists to catch.
    rec = build_ledger_record(
        detection_gap=0.2, true_failures=10, believed_failures=8,
    )
    rec["relationship"]["provenance"] = "asserted"
    rec["relationship"]["simplification_id"] = None
    append_record(rec, ledger_path=ledger)
    gate = fidelity_evidence_gate(DEFAULT_ATOM_ID, ledger_path=ledger)
    assert not gate.passed
    assert any("R10" in r for r in gate.reasons)


def test_emit_raises_when_the_gate_would_fail(ledger, monkeypatch):
    # MUTATION at the emit boundary: force the builder to produce the R10
    # defect and confirm emit RAISES rather than silently returning.
    import background.live_fidelity_evidence as mod

    good = mod.build_ledger_record

    def _bad(**kw):
        rec = good(**kw)
        rec["relationship"]["provenance"] = "asserted"
        rec["relationship"]["simplification_id"] = None
        return rec

    monkeypatch.setattr(mod, "build_ledger_record", _bad)
    with pytest.raises(LiveFidelityGateFailure):
        emit_live_fidelity_evidence(
            detection_gap=0.2, true_failures=10, believed_failures=8,
            as_of=_AS_OF, ledger_path=ledger,
        )


# --------------------------------------------------------------------------
# DETERMINISM -- idempotent, keyed by rel_id (C-S2)
# --------------------------------------------------------------------------

def test_emitting_twice_is_idempotent(ledger):
    for _ in range(2):
        emit_live_fidelity_evidence(
            detection_gap=0.2, true_failures=10, believed_failures=8,
            as_of=_AS_OF, ledger_path=ledger,
        )
    data = json.loads(ledger.read_text())
    # Keyed by rel_id -> exactly one record, never a duplicate per run.
    assert list(data.keys()) == ["live_payment_detection_gap"]


# --------------------------------------------------------------------------
# WALL-STANCE -- imports neither sim nor company (AST scan)
# --------------------------------------------------------------------------

def test_no_sim_or_company_import():
    src = Path(__file__).resolve().parent.parent / "background" / "live_fidelity_evidence.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    forbidden = ("sim", "simulation", "company", "saas")
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            bad += [n.name for n in node.names if n.name.split(".")[0] in forbidden]
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in forbidden:
                bad.append(node.module)
    assert not bad, f"live fidelity bridge must not import sim/company: {bad}"


# --------------------------------------------------------------------------
# D12 -- THE RECORD NAMES ITS OWN MEASURE, AND BOTH DIRECTIONS TRAVEL WITH IT
#
# WHY THIS IS A CONTROL AND NOT A SCHEMA PREFERENCE. This ledger is a TIME
# SERIES the Proof door reads, and D12 changed what `detection_gap` MEANS for
# the per-cell grid: recall-only before, the mean of the miss rate and the
# wrongful-dunning rate after. On the live fixture the lit cell moved
# 0.1031 -> 0.0584 with NO change in company behaviour. A reader diffing the
# two eras without a measure label banks a 43% fidelity improvement that never
# happened -- which is exactly the "band shaped by its own measure" failure the
# D12 mint told this atom to re-derive rather than inherit.
# --------------------------------------------------------------------------

def _two_directional_cell(**over):
    kw = dict(detection_gap=0.0584, true_failures=291, believed_failures=508,
              regime_label="G1_calm", missed_failure_rate=0.1031,
              false_flag_rate=0.0136, n_false_flags=24, n_negatives=1760,
              n_excluded=649, exclusion_reason="late-past-grace and unknown")
    kw.update(over)
    return CellMeasurement(**kw)


def test_measured_cell_record_names_the_two_directional_measure(ledger):
    """FIRES: a cell carrying both directions is labelled as the new measure and
    publishes both rates plus D10's exclusion, rather than a bare scalar."""
    emit_live_fidelity_cells(
        cell_gaps={"A1_G1": _two_directional_cell(),
                   "A1_G2": _two_directional_cell(detection_gap=0.11)},
        as_of=_AS_OF, ledger_path=ledger,
    )
    rel = json.loads(ledger.read_text())[cell_rel_id("A1_G1")]["relationship"]
    assert rel["detection_measure"] == DETECTION_MEASURE_BOTH_DIRECTIONS
    assert rel["missed_failure_rate"] == pytest.approx(0.1031)
    assert rel["false_flag_rate"] == pytest.approx(0.0136)
    # The exclusion reaches the ledger, not just the docstring (D10).
    assert rel["n_excluded"] == 649 and rel["exclusion_reason"]


def test_a_legacy_single_direction_cell_is_not_relabelled_as_two_directional(ledger):
    """QUIET/must-not-fire: a cell WITHOUT the direction fields is the old
    recall-only shape and must keep the old label. Defaulting it to the new name
    would be the cheapest possible way to make the register look paid."""
    emit_live_fidelity_cells(
        cell_gaps={"A1_G1": CellMeasurement(0.10, 8, 7, "G1_calm"),
                   "A1_G2": CellMeasurement(0.42, 20, 6, "G2_crisis")},
        as_of=_AS_OF, ledger_path=ledger,
    )
    rel = json.loads(ledger.read_text())[cell_rel_id("A1_G1")]["relationship"]
    assert rel["detection_measure"] == DETECTION_MEASURE_RECALL_ONLY
    assert "false_flag_rate" not in rel


def test_a_record_claiming_both_directions_without_them_raises():
    """MUST-FIRE (R15). The label is the whole point of the field, so a record
    that claims the two-directional measure while omitting the two directions
    would rebuild the one-directional defect one layer further out -- with a
    reassuring name on it. It RAISES rather than emitting a headline nobody can
    take apart."""
    with pytest.raises(ValueError, match="must carry BOTH"):
        build_ledger_record(
            detection_gap=0.0584, true_failures=291, believed_failures=508,
            measure=DETECTION_MEASURE_BOTH_DIRECTIONS,
        )
    # ...and CLEARS once the directions are actually present (both directions
    # of the control itself, never a one-way assertion).
    rel = build_ledger_record(
        detection_gap=0.0584, true_failures=291, believed_failures=508,
        measure=DETECTION_MEASURE_BOTH_DIRECTIONS,
        missed_failure_rate=0.1031, false_flag_rate=0.0136,
    )["relationship"]
    assert rel["detection_measure"] == DETECTION_MEASURE_BOTH_DIRECTIONS
