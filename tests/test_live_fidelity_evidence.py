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
    LiveFidelityGateFailure,
    build_inspection_chain,
    build_ledger_record,
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
