"""The fidelity-evidence LIVE EMITTER -- wires the already-built Epoch-2 G
machinery (G1 grid scorer / G2 emit-ledger / G3 inspection chain) onto a
REAL BUILD atom's evidence, end to end (`G_data_learning` lane, HARNESS-side).

This is the atom-G "L2 = wire a live emitter + measure a real gap" step: G1,
G2, and G3 were each built and unit-tested against hand-built fixtures only
(their own test suites); nothing had yet fed them a real atom's real
evidence. This module is that feed.

THE REAL ATOM being evidenced: `W1_6_physics_price_signal`
(docs/design/maturity_map.yaml) -- concretely, sim/price_engine.py's
residual-demand-scarcity SSP calibration, whose fitted form + fit quality is
already documented in
docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md. Rather than copying
that document's numbers into a fixture, this module RECOMPUTES them live
against the same real Elexon/NBP cache
(`simulation/run_phase3b_recalibration.py` / `simulation/run_phase3b_regression.py`
/ `sim/price_engine.py` constants, used here purely as libraries -- none of
the three are modified) -- so the emitted evidence record is provably fresh,
not a pasted-in number.

THE THREE STEPS (S3/S4 of docs/design/EPOCH2_G_FIDELITY_EVIDENCE_MACHINERY_DISCOVER.md):

    1. EMIT (G2) -- `emit_price_engine_fidelity_evidence` fits the model live
       and appends a structured G2 ledger record: the fitted relationship
       (residual-demand-scarcity form), its strength (MAE/RMSE/R2 + lift over
       the BEST-OF-a-naive-FAMILY -- the family here is
       {gas-floor-alone, the 3-feature OLS regression}, matching the
       construct-challenge's best-of-family sharpen, not a single frozen
       baseline), provenance=`estimated_from_data` (fit against real n=157,106
       Elexon settlement periods -- no simplification_id needed, matching
       G2's own R10 rule), and per-cell (per-year) lift.

    2. SCORE (G1) -- `score_price_engine_grid` feeds the per-year cells
       through G1's `cell_lift` (best-of-family lift per year) and
       `score_grid` (worst-q% CVaR over the year cells + map of ignorance --
       empty here, every year 2016-2025 is measured, no missing_physics/
       untested cell).

    3. CHAIN (G3) -- `chain_price_engine_evidence` registers an EVIDENCE node
       (the fitted relationship) and a WORLD node (the real SSP/gas/demand/
       renewable series it was fit against), linked EVIDENCE -> WORLD
       (`produces`). The price engine is WORLD-side physics (a real supplier
       observes only the published SSP outcome, never sees "the fitted
       constants behind SSP") -- this chain therefore has NO BELIEF_ACTION
       node and `assert_no_belief_leak` passes trivially (there is nothing
       here that COULD leak truth_ref, by construction, not by omission of
       the check).

`run_end_to_end` composes all three and returns every intermediate result
so a caller (or `tests/test_fidelity_emitter.py`) can inspect and quote the
real lift/CVaR numbers, and asserts the G2 emit-DoD gate passes on the
result.

WHAT THIS MODULE DELIBERATELY DOES NOT DO:
    * No ablation (measure 3) block is emitted. The calibration this atom
      evidences is a deterministic closed-form least-squares fit over a
      fixed real dataset -- there is no seeded stochastic draw and therefore
      no CRN substream to prove isolated. Fabricating a `crn.substream_isolated:
      true` block for a fit that has no randomness to isolate would itself be
      the R15 killer-mutation-C defect in spirit (an ablation claim without a
      real isolation proof behind it); the honest choice is to omit the
      `ablation` field entirely (it's Optional in G2's schema) rather than
      manufacture one. Noted here, not hidden.
    * No consumer beyond the emit-DoD gate is wired this pass (matching G2's
      own module note: nothing else reads `fidelity_evidence_ledger.json`
      yet, so nothing else can red).

THE WALL (CLAUDE.md Architectural Laws). This module is pure HARNESS code,
same standing as G1/G2/G3: it never imports `company.*` / `saas.*`. It DOES
import `sim.price_engine` (for two calibrated physical constants) and
`simulation.run_phase3b_recalibration` / `simulation.run_phase3b_regression`
(for the real dataset + fit routines) -- both are WORLD-side / harness-side
modules, read here as libraries, never modified. This is data flowing
WORLD -> HARNESS (evidence about the world), the same direction G1/G2/G3
themselves already operate in; nothing here crosses HARNESS -> COMPANY or
exposes anything to `company/interfaces/sim_interface.py`.

R12 anti-goal-seek: this module never adjusts the fitted constants, the
naive family, or a threshold to flatter the emitted lift number -- it reads
`sim/price_engine.py`'s own already-calibrated constants
(`SELECTED_X_TIGHT`/`SELECTED_SCARCITY_EXPONENT`, imported from
`simulation.run_phase3b_recalibration`, unchanged) and reports whatever MAE
falls out.

R15: `tests/test_fidelity_emitter.py` mutation-tests both borrowed gates
directly against THIS module's own emitted output (not a hand-built fixture)
-- provenance="asserted" + simplification_id=None must red G2's gate; a
BELIEF_ACTION record with a non-null truth_ref added to this module's own
chain must fire G3's `assert_no_belief_leak`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from background import fidelity_evidence_ledger as fel
from background import fidelity_grid_scorer as fgs
from background import fidelity_inspection_chain as fic
from background.boot_sha import current_head

from simulation import run_phase3b_recalibration as recal
from simulation import run_phase3b_regression as regr
from sim.price_engine import DISPATCHABLE_CAPACITY_MW, THERMAL_EFFICIENCY

# ---------------------------------------------------------------------------
# Identity -- the real atom this evidence is FOR (docs/design/maturity_map.yaml)
# ---------------------------------------------------------------------------

ATOM_ID = "W1_6_physics_price_signal"
DRIVER_FAMILY = "price_engine_ssp_calibration"
REL_ID = "W1_6_physics_price_signal::ssp_residual_demand_scarcity_calibration_2026_07_19"
WORLD_SERIES_REF = "elexon_ssp_calibration_full_2016_03_01_to_2025_06_07"

# 2021/2022 are the real UK gas-crisis years (docs/fidelity/EPOCH2_PRICE_ENGINE
# _FIDELITY_EVIDENCE.md 2.4's own per-year table shows 2022 as by far the
# highest-MAE year) -- used only as a human-readable regime tag on each cell,
# never as a computed input to the fit itself.
CRISIS_YEARS: Tuple[str, ...] = ("2021", "2022")

_NAIVE_FAMILY_IDS = ("gas_floor_alone", "ols_regression_3feature")


# ===========================================================================
# Step 0 -- the live fit (real data, no fixtures)
# ===========================================================================

def _fit_price_engine_live() -> Dict[str, Any]:
    """Recomputes the recalibrated price engine's fit (and the naive-family
    members' fits) LIVE against the real Elexon/NBP cache, using
    `simulation.run_phase3b_recalibration` / `simulation.run_phase3b_regression`
    / `sim.price_engine` purely as libraries (none modified). Returns full-
    window numbers plus per-year residual arrays so callers can slice cells."""
    rows = recal._build_dataset()
    gas_price = np.array([r["gas_price"] for r in rows])
    demand_mw = np.array([r["demand_mw"] for r in rows])
    renewable_mw = np.array([r["renewable_mw"] for r in rows])
    ssp = np.array([r["ssp"] for r in rows])
    dates = np.array([r["settlementDate"] for r in rows])
    years = np.array([d[:4] for d in dates])

    floor = gas_price / THERMAL_EFFICIENCY  # carbon_price=0, matching the landed calibration
    x = (demand_mw - renewable_mw) / DISPATCHABLE_CAPACITY_MW

    fit = recal._fit_form(floor, x, ssp, recal.SELECTED_X_TIGHT, recal.SELECTED_SCARCITY_EXPONENT)
    predictions = fit.pop("predictions")
    model_residual = ssp - predictions
    naive_floor_residual = ssp - floor

    naive_floor_mae_full = float(np.mean(np.abs(naive_floor_residual)))

    # Naive family member B: the 3-feature OLS regression, its own real
    # dataset/join (simulation/run_phase3b_regression.py, unmodified).
    ols_rows = regr._build_dataset()
    ols_fit = regr._fit_ols(ols_rows)
    ols_dates = np.array([r["settlementDate"] for r in ols_rows])
    ols_years = np.array([d[:4] for d in ols_dates])
    ols_X = np.column_stack([
        np.ones(len(ols_rows)),
        [r["gas_price"] for r in ols_rows],
        [r["demand_mw"] for r in ols_rows],
        [r["wind_mw"] for r in ols_rows],
    ])
    ols_coeffs = np.array([
        ols_fit["intercept"], ols_fit["coef_gas_price"],
        ols_fit["coef_demand_mw"], ols_fit["coef_wind_mw"],
    ])
    ols_ssp = np.array([r["ssp"] for r in ols_rows])
    ols_residual = ols_ssp - (ols_X @ ols_coeffs)

    return {
        "n": len(rows),
        "years": years,
        "model_residual": model_residual,
        "naive_floor_residual": naive_floor_residual,
        "ols_years": ols_years,
        "ols_residual": ols_residual,
        "model_fit": fit,          # a0/a1/a2/x_tight/p/mae/rmse/r2
        "naive_floor_mae_full": naive_floor_mae_full,
        "naive_ols_mae_full": ols_fit["mae"],
        "naive_ols_n": ols_fit["n"],
    }


def _per_year_lift_results(live: Mapping[str, Any]) -> List[fgs.LiftResult]:
    """One G1 `LiftResult` per calendar-year cell, best-of-{gas-floor-alone,
    OLS-regression} naive family, computed from the live fit's residual
    arrays (real data, not a fixture)."""
    years = live["years"]
    model_residual = live["model_residual"]
    naive_floor_residual = live["naive_floor_residual"]
    ols_years = live["ols_years"]
    ols_residual = live["ols_residual"]

    results: List[fgs.LiftResult] = []
    for year in sorted(set(years)):
        mask = years == year
        model_mae_year = float(np.mean(np.abs(model_residual[mask])))
        naive_floor_mae_year = float(np.mean(np.abs(naive_floor_residual[mask])))

        err_by_baseline: Dict[str, float] = {"gas_floor_alone": naive_floor_mae_year}
        ols_mask = ols_years == year
        if ols_mask.any():
            err_by_baseline["ols_regression_3feature"] = float(
                np.mean(np.abs(ols_residual[ols_mask]))
            )

        results.append(
            fgs.cell_lift(
                driver_family=DRIVER_FAMILY,
                cell_id=f"y{year}",
                err_model=model_mae_year,
                err_by_baseline=err_by_baseline,
            )
        )
    return results


# ===========================================================================
# Step 1 -- EMIT (G2)
# ===========================================================================

def build_price_engine_evidence_record(
    live: Optional[Mapping[str, Any]] = None,
    per_cell: Optional[Sequence[fgs.LiftResult]] = None,
    *,
    provenance: str = "estimated_from_data",
    simplification_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the G2-shaped ledger record dict for the price-engine SSP
    calibration. `provenance`/`simplification_id` default to the honest real
    values (fit against 157k real periods, no simplification needed) --
    overridable ONLY so `tests/test_fidelity_emitter.py` can construct the
    R15 killer-mutation-B variant (`provenance="asserted"`,
    `simplification_id=None`) against this module's OWN real numbers rather
    than a hand-built fixture.
    """
    if live is None:
        live = _fit_price_engine_live()
    if per_cell is None:
        per_cell = _per_year_lift_results(live)

    naive_best_id, naive_best_mae_full = fgs.best_of_family_error({
        "gas_floor_alone": live["naive_floor_mae_full"],
        "ols_regression_3feature": live["naive_ols_mae_full"],
    })
    model_fit = live["model_fit"]
    lift_full = naive_best_mae_full - model_fit["mae"]

    return {
        "rel_id": REL_ID,
        "atom_id": ATOM_ID,
        "layer": "EVIDENCE",
        "relationship": {
            "kind": "residual_demand_scarcity_price_calibration",
            "observables": [
                "gas_price_gbp_per_mwh", "demand_mw", "renewable_generation_mw",
            ],
            "conditioning": "full_window_2016_03_01_to_2025_06_07",
            "strength": {
                "stat": "MAE_lift_over_best_of_naive_family",
                "value": lift_full,
                "mae": model_fit["mae"],
                "rmse": model_fit["rmse"],
                "r2": model_fit["r2"],
                "u": None, "ci": None, "ci_method": None,
                "best_naive_baseline_id": naive_best_id,
                "err_best_naive_full": naive_best_mae_full,
                "naive_family": list(_NAIVE_FAMILY_IDS),
                "naive_family_mae": {
                    "gas_floor_alone": live["naive_floor_mae_full"],
                    "ols_regression_3feature": live["naive_ols_mae_full"],
                },
                "n": live["n"],
            },
            "provenance": provenance,
            "series_ref": (
                "sim/cache/elexon_ssp_full.json;sim/cache/elexon_demand_full.json;"
                "sim/cache/elexon_agws_full.json;sim/gas_prices_history.py (NBP)"
            ),
            "independent_anchor": (
                "structural form independently motivated by UK merit-order "
                "marginal-cost dispatch theory (gas-plant SRMC + residual-demand "
                "scarcity), not reverse-engineered from the SSP curve shape; no "
                "third-party published benchmark was used to cross-check the "
                "fitted A0/A1/A2 constants themselves in this pass -- a named "
                "gap (docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md S3), "
                "not concealed"
            ),
            "simplification_id": simplification_id,
        },
        "per_cell_lift": [
            {
                "cell": lr.cell_id,
                "err_naive": lr.err_best_naive,
                "err_model": lr.err_model,
                "lift": lr.lift,
                "commercial_weight": lr.commercial_weight,
                "best_baseline_id": lr.best_baseline_id,
                "regime": "crisis" if lr.cell_id[1:] in CRISIS_YEARS else "calm",
            }
            for lr in per_cell
        ],
        "ablation": None,  # see module docstring: no CRN substream to isolate
        "measured_at": "2026-07-19T00:00:00+00:00",
        "run_git_commit": current_head() or "unknown",
    }


def emit_price_engine_fidelity_evidence(
    ledger_path=None,
    *,
    provenance: str = "estimated_from_data",
    simplification_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Fit live, build the G2 record, and append it via G2's own
    `append_record` (structural validation only, per G2's own R10 note).
    Returns the record actually written."""
    live = _fit_price_engine_live()
    per_cell = _per_year_lift_results(live)
    record = build_price_engine_evidence_record(
        live, per_cell, provenance=provenance, simplification_id=simplification_id,
    )
    fel.append_record(record, ledger_path=ledger_path)
    return record


# ===========================================================================
# Step 2 -- SCORE (G1)
# ===========================================================================

def score_price_engine_grid(record: Mapping[str, Any]) -> fgs.GridScore:
    """Feed the emitted record's per-year cells through G1's measure-2
    (worst-q% CVaR + map of ignorance). Every year 2016-2025 is measured in
    this pass (map_of_ignorance is empty by construction -- the real dataset
    covers the whole window continuously)."""
    cells = [
        fgs.CellEvidence(cell_id=entry["cell"], measured=True, gap=entry["err_model"])
        for entry in record["per_cell_lift"]
    ]
    return fgs.score_grid(cells)


# ===========================================================================
# Step 3 -- CHAIN (G3)
# ===========================================================================

def chain_price_engine_evidence(record: Mapping[str, Any]) -> fic.InspectionChain:
    """Register the EVIDENCE node (this record's relationship) and the WORLD
    node (the real SSP/gas/demand/renewable series it was fit against),
    linked EVIDENCE -> WORLD (`produces`). No BELIEF_ACTION node is
    registered -- the price engine is WORLD-side physics with no live
    company consumer (docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md
    S5: "the engine has no live consumer"), so there is nothing here that
    could carry a `truth_ref` leak; `assert_no_belief_leak` passes because
    the leak-prone record type is simply absent, not un-checked."""
    evidence_rec = fic.EvidenceRecord(rel_id=record["rel_id"], relationship=record["relationship"])
    world_rec = fic.WorldRecord(
        world_series_ref=WORLD_SERIES_REF,
        variables=("systemSellPrice", "gas_price_gbp_per_mwh", "demand_mw", "renewable_generation_mw"),
        regime_label=None,
        driven_by=(record["rel_id"],),
    )
    chain = fic.InspectionChain()
    chain.add_evidence(evidence_rec)
    chain.add_world(world_rec)
    fic.validate_chain(chain)
    return chain


# ===========================================================================
# End to end
# ===========================================================================

def run_end_to_end(ledger_path=None) -> Dict[str, Any]:
    """Emit -> score -> chain -> gate, all against real data, in one call.
    Returns every intermediate artefact so a caller can inspect/quote the
    real numbers and assert the G2 emit-DoD gate passes."""
    record = emit_price_engine_fidelity_evidence(ledger_path=ledger_path)
    grid_score = score_price_engine_grid(record)
    chain = chain_price_engine_evidence(record)
    gate_result = fel.fidelity_evidence_gate(ATOM_ID, ledger_path=ledger_path)
    return {
        "record": record,
        "grid_score": grid_score,
        "chain": chain,
        "gate_result": gate_result,
    }


if __name__ == "__main__":
    bundle = run_end_to_end()
    rec = bundle["record"]
    gs = bundle["grid_score"]
    gate = bundle["gate_result"]
    strength = rec["relationship"]["strength"]
    print(f"atom_id={rec['atom_id']}  rel_id={rec['rel_id']}")
    print(f"MAE={strength['mae']:.3f}  RMSE={strength['rmse']:.3f}  R2={strength['r2']:.4f}")
    print(f"lift over best-of-naive-family ({strength['best_naive_baseline_id']}): "
          f"£{strength['value']:.3f}/MWh")
    print(f"worst cell: {gs.worst_cell}  worst_severity={gs.worst_severity:.3f}  "
          f"CVaR(q={gs.q})={gs.grid_aggregate:.3f}  map_of_ignorance={len(gs.map_of_ignorance)} cell(s)")
    print(f"emit-DoD gate passed={gate.passed}  reasons={gate.reasons}")
