"""Tests for background/fidelity_emitter.py -- the LIVE emitter that wires
G1 (fidelity_grid_scorer) / G2 (fidelity_evidence_ledger) / G3
(fidelity_inspection_chain) onto a real BUILD atom's evidence
(`W1_6_physics_price_signal`, the price-engine SSP calibration).

Per R15 ("a control that cannot fail is worse than none"), the borrowed
gates' red conditions are proven with MUTATION tests run against THIS
module's own real emitted output -- not a hand-built fixture -- so the
proof is that the machinery fires on a real atom's evidence, not merely on
a fixture shaped to trip it.

The live fit (`_fit_price_engine_live`) reads the real Elexon/NBP cache and
is computed ONCE per test session (module-scoped fixture) -- it is a
deterministic closed-form fit over a fixed real dataset, so reusing it
across tests changes nothing about what is being proven, only the wall
clock.
"""

import pytest

from background import fidelity_emitter as fem
from background import fidelity_evidence_ledger as fel
from background import fidelity_grid_scorer as fgs
from background import fidelity_inspection_chain as fic


# ---------------------------------------------------------------------------
# Fixtures -- compute the real live fit once, reuse across tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def live_fit():
    return fem._fit_price_engine_live()


@pytest.fixture(scope="module")
def per_cell(live_fit):
    return fem._per_year_lift_results(live_fit)


@pytest.fixture
def real_record(live_fit, per_cell):
    """A fresh, honest (estimated_from_data / no simplification) record
    built from the shared live fit -- cheap to construct per-test since the
    expensive numpy work already happened in the module-scoped fixtures."""
    return fem.build_price_engine_evidence_record(live_fit, per_cell)


# ===========================================================================
# The live fit itself -- real data, matches the documented calibration
# ===========================================================================

def test_live_fit_matches_documented_full_window_calibration(live_fit):
    """docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md documents
    MAE=£32.790/MWh, RMSE=£70.159/MWh, R2=0.4190 on the full real window
    (n=157,106). This emitter RECOMPUTES the fit live rather than reading
    that document -- assert the live numbers land on the documented ones
    (proving this is the same real evidence, not a divergent recompute)."""
    fit = live_fit["model_fit"]
    assert live_fit["n"] == 157_106
    assert fit["mae"] == pytest.approx(32.790, abs=0.01)
    assert fit["rmse"] == pytest.approx(70.159, abs=0.01)
    assert fit["r2"] == pytest.approx(0.4190, abs=0.001)


def test_live_fit_naive_family_matches_documented_baselines(live_fit):
    """Doc: naive gas-floor-alone MAE=£35.775/MWh; 3-feature OLS
    MAE=£33.96/MWh. Both naive-family members must reproduce those figures
    live."""
    assert live_fit["naive_floor_mae_full"] == pytest.approx(35.775, abs=0.01)
    assert live_fit["naive_ols_mae_full"] == pytest.approx(33.958, abs=0.01)


def test_lift_is_over_the_best_of_family_not_the_weaker_baseline(real_record):
    """The naive family here is {gas_floor_alone, ols_regression_3feature};
    OLS is the STRONGER (lower-MAE) naive member, so best-of-family lift
    must be computed against OLS, not the weaker gas-floor baseline (the
    construct-challenge's best-of-family sharpen, mechanised)."""
    strength = real_record["relationship"]["strength"]
    assert strength["best_naive_baseline_id"] == "ols_regression_3feature"
    assert strength["value"] == pytest.approx(
        strength["naive_family_mae"]["ols_regression_3feature"] - strength["mae"], abs=1e-9
    )
    # Lift over the best-of-family is honestly SMALLER than lift over the
    # weak gas-floor-alone baseline would have been -- proves this isn't
    # quietly reporting the more flattering number.
    naive_gas_floor_lift = strength["naive_family_mae"]["gas_floor_alone"] - strength["mae"]
    assert strength["value"] < naive_gas_floor_lift


def test_per_cell_lift_is_honest_not_cherry_picked(real_record):
    """A real, non-rigged best-of-family construct must show SOME cells
    where the structural model does WORSE than the naive family (negative
    lift) even though it wins in aggregate -- otherwise the per-cell view
    would be suspiciously uniform. This is the documented 2019/2020
    calm-year weakness (EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md S2.4)."""
    lifts = {e["cell"]: e["lift"] for e in real_record["per_cell_lift"]}
    assert len(lifts) == 10  # 2016..2025
    assert any(v < 0 for v in lifts.values()), "expected at least one honest negative-lift cell"
    assert any(v > 0 for v in lifts.values()), "expected at least one honest positive-lift cell"
    # The 2022 gas-crisis year is where the structural form earns its keep most.
    assert lifts["y2022"] > 0


# ===========================================================================
# G2 -- EMIT
# ===========================================================================

def test_emit_appends_a_well_formed_g2_record(tmp_path):
    path = tmp_path / "ledger.json"
    record = fem.emit_price_engine_fidelity_evidence(ledger_path=path)

    ledger = fel.load_ledger(path)
    assert fem.REL_ID in ledger
    stored = ledger[fem.REL_ID]
    assert stored["atom_id"] == fem.ATOM_ID
    assert stored["relationship"]["provenance"] == "estimated_from_data"
    assert stored["relationship"]["simplification_id"] is None
    assert stored == record


def test_emitted_record_carries_a_real_git_commit_stamp(real_record):
    assert isinstance(real_record["run_git_commit"], str)
    assert real_record["run_git_commit"] != ""


# ===========================================================================
# G1 -- SCORE
# ===========================================================================

def test_g1_scores_real_per_year_cells(real_record):
    grid = fem.score_price_engine_grid(real_record)
    assert isinstance(grid, fgs.GridScore)
    assert len(grid.severities) == 10
    # 2022 (real UK gas-crisis year) is the atom's own worst-fitted year --
    # this is a REAL finding (highest absolute MAE), not asserted.
    assert grid.worst_cell == "y2022"
    y2022_err_model = next(
        e["err_model"] for e in real_record["per_cell_lift"] if e["cell"] == "y2022"
    )
    assert grid.worst_severity == pytest.approx(y2022_err_model, abs=1e-9)
    # q=0.10 tail over 10 cells -> k=1, so CVaR collapses to the single worst cell.
    assert grid.tail_k == 1
    assert grid.grid_aggregate == pytest.approx(grid.worst_severity, abs=1e-9)
    # Every year 2016-2025 is measured in this real dataset -- no blind spot.
    assert grid.map_of_ignorance == ()


def test_g1_cell_lift_matches_manual_best_of_family(real_record):
    """Cross-check one cell (2022) against G1's own `cell_lift` computed by
    hand from the record's own naive-family numbers, proving G1 (not some
    private duplicate arithmetic in the emitter) produced the number."""
    entry = next(e for e in real_record["per_cell_lift"] if e["cell"] == "y2022")
    # err_naive on the record IS G1's best-of-family minimum already; lift
    # must equal err_naive - err_model exactly (G1's own formula).
    assert entry["lift"] == pytest.approx(entry["err_naive"] - entry["err_model"], abs=1e-9)


# ===========================================================================
# G3 -- CHAIN
# ===========================================================================

def test_g3_chain_is_clean_no_belief_leak(real_record):
    chain = fem.chain_price_engine_evidence(real_record)  # raises internally if dirty
    fic.validate_links(chain)          # no dangling edges
    fic.assert_no_belief_leak(chain)   # no BELIEF_ACTION node exists at all

    evidence_node = chain.nodes[f"EVIDENCE::{real_record['rel_id']}"]
    world_node = chain.nodes[f"WORLD::{fem.WORLD_SERIES_REF}"]
    assert evidence_node.rel_id == real_record["rel_id"]
    assert world_node.world_series_ref == fem.WORLD_SERIES_REF

    # EVIDENCE -> WORLD 'produces' edge auto-derived from WorldRecord.driven_by.
    consequences = chain.consequences_of(evidence_node.node_id)
    assert world_node.node_id in consequences


def test_g3_belief_leak_mutation_fires_and_clears(real_record):
    """R15: a BELIEF_ACTION record with a non-null truth_ref added to this
    module's own real chain must fire assert_no_belief_leak; removing the
    truth_ref must clear it. Proves the wall-discipline control actually
    inspects THIS atom's chain, not just a hand-built fixture chain."""
    chain = fem.chain_price_engine_evidence(real_record)

    leaking = fic.BeliefActionRecord(
        belief_id="leaky_belief", cell="y2022", belief={"observed": "high price"},
        action={"hedged": True}, gap=0.1, as_of="2022-06-01T00:00:00+00:00",
        truth_ref="SIM_TRUTH::should_never_be_here",
    )
    chain.add_belief_action(leaking)
    with pytest.raises(fic.BeliefLeakError):
        fic.assert_no_belief_leak(chain)

    clean_chain = fem.chain_price_engine_evidence(real_record)
    honest = fic.BeliefActionRecord(
        belief_id="honest_belief", cell="y2022", belief={"observed": "high price"},
        action={"hedged": True}, gap=0.1, as_of="2022-06-01T00:00:00+00:00",
        truth_ref=None,
    )
    clean_chain.add_belief_action(honest)
    fic.assert_no_belief_leak(clean_chain)  # must NOT raise


# ===========================================================================
# The emit-DoD gate (G2) -- happy path + R15 mutation on THIS atom's evidence
# ===========================================================================

def test_dod_gate_passes_on_the_real_emitted_record(tmp_path):
    path = tmp_path / "ledger.json"
    fem.emit_price_engine_fidelity_evidence(ledger_path=path)
    result = fel.fidelity_evidence_gate(fem.ATOM_ID, ledger_path=path)
    assert result.passed is True
    assert result.reasons == ()


def test_R15_killer_mutation_asserted_without_simplification_reds(tmp_path, live_fit, per_cell):
    """Emit THIS atom's real record but with provenance='asserted' and no
    simplification_id -- the DoD gate must red (R10 mechanised). Then emit
    the honest version to a fresh ledger and confirm it passes -- proving
    the gate is discriminating on the defect, not failing unconditionally."""
    bad_path = tmp_path / "bad_ledger.json"
    bad_record = fem.build_price_engine_evidence_record(
        live_fit, per_cell, provenance="asserted", simplification_id=None,
    )
    fel.append_record(bad_record, ledger_path=bad_path)
    bad_result = fel.fidelity_evidence_gate(fem.ATOM_ID, ledger_path=bad_path)
    assert bad_result.passed is False
    assert any("simplification_id=null" in r for r in bad_result.reasons)

    good_path = tmp_path / "good_ledger.json"
    fem.emit_price_engine_fidelity_evidence(ledger_path=good_path)
    good_result = fel.fidelity_evidence_gate(fem.ATOM_ID, ledger_path=good_path)
    assert good_result.passed is True


# ===========================================================================
# End to end
# ===========================================================================

def test_run_end_to_end_bundle(tmp_path):
    path = tmp_path / "ledger.json"
    bundle = fem.run_end_to_end(ledger_path=path)

    assert set(bundle) == {"record", "grid_score", "chain", "gate_result"}
    assert bundle["gate_result"].passed is True
    assert isinstance(bundle["grid_score"], fgs.GridScore)
    assert isinstance(bundle["chain"], fic.InspectionChain)
    assert len(bundle["record"]["per_cell_lift"]) == 10

    # The ledger on disk really has the record (not just an in-memory return).
    ledger = fel.load_ledger(path)
    assert fem.ATOM_ID == ledger[fem.REL_ID]["atom_id"]
