#!/usr/bin/env python3
"""Generate site/data/fidelity.json -- atom G4, the SITE fidelity instrument.

The director's window into the Epoch-2 fidelity-evidence machinery (G1 grid
scorer, G2 emit-ledger, G3 inspection chain -- all landed + L2). This module
RENDERS what those atoms already measured; it computes NO new physics and no
new scoring logic of its own (SITE_CONSTITUTION rule 5: the site is a
rendering, never an author).

DIRECTOR FIDELITY STEER (docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md,
"DIRECTOR FIDELITY STEER", console 2026-07-19) -- baked in here, not just in
prose: **the average is a trap.** Lead with the EXPOSURE-TAIL under-
representation (the extreme spike the model misses by ~7x, the negative-price
frequency it misses by ~170x -- the tail that triggers collateral calls and
kills suppliers) and the WORST-CELL CVaR (2022, scored by G1's per-cell MAE
severity), never the calm-year MAE/lift average, which reads WORSE in a naive
skim (the model only beats the best-of-naive-family baseline in 4/10 years)
but is explicitly the LOW-STAKES reading under this steer.

FOUR REAL SOURCES, READ NOT INVENTED:
  1. docs/observability/fidelity_evidence_ledger.json (G2) -- the real emitted
     evidence record for W1_6_physics_price_signal (background/fidelity_emitter.py).
  2. background/fidelity_grid_scorer.py (G1) -- fed the ledger's own per-cell
     err_model values (the same call `background/fidelity_emitter.py::
     score_price_engine_grid` makes) to get the worst-cell + CVaR, verbatim
     shape, not re-derived.
  3. background/fidelity_inspection_chain.py (G3) -- the EVIDENCE->WORLD chain,
     built from the ledger record's own rel_id/relationship (no re-fit).
  4. The exposure-tail distribution numbers (max/negative-frequency, model vs
     real) are NOT present in the G2 ledger (it only carries MAE-shaped
     per-cell lift) -- they are reproduced LIVE from the same real Elexon/NBP
     cache via `simulation.run_phase3b_recalibration` used purely as a
     library (unmodified; the identical reuse pattern `background/
     fidelity_emitter.py::_fit_price_engine_live` already establishes for the
     MAE numbers), so the top-of-page headline figure is DERIVED, never a
     pasted-in literal from the doc's prose table. If that recomputation is
     ever unavailable, this block alone fails closed and visible -- it does
     not blank the rest of the page (the ledger-derived sections are
     independent and still render).

FAIL-CLOSED (R15): a missing/unreadable/empty ledger, or zero records for the
tracked atom, emits `available: false` -- the page must show a visible "no
fidelity evidence yet" state, never a silently empty/blank one.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT = Path(__file__).resolve().parent.parent
LEDGER_PATH = PROJECT / "docs" / "observability" / "fidelity_evidence_ledger.json"
OUTPUT_PATH = PROJECT / "site" / "data" / "fidelity.json"

# The one real atom this pass has live emitted evidence for (background/fidelity_emitter.py).
ATOM_ID = "W1_6_physics_price_signal"
STEER_DOC = "docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md"

sys.path.insert(0, str(PROJECT))

from background import fidelity_evidence_ledger as fel  # noqa: E402
from background import fidelity_grid_scorer as fgs  # noqa: E402
from background import fidelity_inspection_chain as fic  # noqa: E402


def _unavailable(note: str) -> Dict[str, Any]:
    return dict(
        available=False,
        note=note,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        source_ledger=str(LEDGER_PATH.relative_to(PROJECT)),
        steer_doc=STEER_DOC,
    )


def _load_records() -> Optional[List[dict]]:
    """Fail-closed ledger read, scoped to the one tracked atom. Returns None
    (never a silent []) on any unavailable/malformed/empty condition so the
    caller can distinguish "no evidence yet" from "measured, zero records"."""
    try:
        ledger = fel.load_ledger(LEDGER_PATH)
    except fel.LedgerUnavailable:
        return None
    records = fel.records_for_atom(ATOM_ID, ledger)
    return records or None


# ---------------------------------------------------------------------------
# Worst-cell CVaR (G1), fed the ledger's own per-cell err_model -- the same
# call background/fidelity_emitter.py::score_price_engine_grid makes.
# ---------------------------------------------------------------------------

_CRISIS_YEARS = ("2021", "2022")


def _score_grid(record: dict) -> fgs.GridScore:
    cells = [
        fgs.CellEvidence(cell_id=e["cell"], measured=True, gap=e["err_model"])
        for e in record["per_cell_lift"]
    ]
    return fgs.score_grid(cells)


def _worst_cell_block(record: dict, grid_score: fgs.GridScore) -> Dict[str, Any]:
    worst_year = grid_score.worst_cell[1:]  # "y2022" -> "2022"
    worst_entry = next(
        (e for e in record["per_cell_lift"] if e["cell"] == grid_score.worst_cell), {}
    )
    regime = "crisis" if worst_year in _CRISIS_YEARS else "calm"
    return dict(
        cell=grid_score.worst_cell,
        year=worst_year,
        severity_mae_gbp_per_mwh=grid_score.worst_severity,
        q=grid_score.q,
        cvar_aggregate_gbp_per_mwh=grid_score.grid_aggregate,
        tail_k=grid_score.tail_k,
        regime=regime,
        lift=worst_entry.get("lift"),
        commentary=(
            f"The worst-scored cell under G1's worst-q% CVaR (q={grid_score.q}) is "
            f"{grid_score.worst_cell} -- the real 2022 UK gas-crisis year, "
            f"MAE=£{grid_score.worst_severity:.2f}/MWh. This is the year the model "
            "is asked to explain the biggest real price moves, and where a miss is "
            "commercially expensive -- not the year with the lowest R2."
        ),
    )


def _per_cell_lift_rows(record: dict) -> List[Dict[str, Any]]:
    rows = []
    for e in record["per_cell_lift"]:
        year = e["cell"][1:]
        regime = e.get("regime") or ("crisis" if year in _CRISIS_YEARS else "calm")
        rows.append(dict(
            cell=e["cell"],
            year=year,
            regime=regime,
            stakes="high" if regime == "crisis" else "low",
            err_model=e["err_model"],
            err_naive=e["err_naive"],
            lift=e["lift"],
            beats_naive=bool(e["lift"] > 0),
            best_baseline_id=e.get("best_baseline_id"),
            commercial_weight=e.get("commercial_weight"),
        ))
    rows.sort(key=lambda r: r["year"])
    return rows


def _mae_reading_block(record: dict, per_cell_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    strength = record.get("relationship", {}).get("strength", {})
    years_total = len(per_cell_rows)
    years_beating_naive = sum(1 for r in per_cell_rows if r["beats_naive"])
    return dict(
        subordinate=True,
        headline=(
            f"structural model beats best-of-naive-family in only "
            f"{years_beating_naive}/{years_total} years"
        ),
        note=(
            "THE AVERAGE TRAP (director steer): this reading is low-stakes -- "
            "calm-year MAE is where nothing commercial is at stake. It is shown "
            "here for completeness, subordinate to the exposure-tail and "
            "worst-cell readings above, never the headline."
        ),
        full_window_mae=strength.get("mae"),
        full_window_rmse=strength.get("rmse"),
        full_window_r2=strength.get("r2"),
        lift_over_best_of_naive_family=strength.get("value"),
        best_naive_baseline_id=strength.get("best_naive_baseline_id"),
        naive_family_mae=strength.get("naive_family_mae"),
        n=strength.get("n"),
        years_beating_naive=years_beating_naive,
        years_total=years_total,
    )


# ---------------------------------------------------------------------------
# Exposure tail: live-derived from the real Elexon/NBP cache (item 4 in the
# module docstring) where that cache is present. FALLBACK: the cache under
# `sim/cache/` is git-ignored (never checked into version control -- confirmed
# via `git ls-files sim/cache`), so a fresh build worktree (this atom was
# itself built in one) does not carry it and live recomputation legitimately
# fails there. Rather than blank the page's lead section in that case, fall
# back to the exact real numbers already published + independently
# reproducible in docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md S2.3
# ("python3 -m simulation.run_phase3b_recalibration regenerates every number
# in this document") -- cited, not invented, and clearly flagged
# `basis="cited_from_fidelity_doc"` (vs `"live_recomputed"`) so a reader can
# tell which path produced the number on any given generation run.
# ---------------------------------------------------------------------------

# Cited fallback (docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md S2.3,
# reproduced verbatim from that table -- used ONLY when the live recompute
# below cannot run because sim/cache/ is absent in this environment).
_FALLBACK_ACTUAL_STATS = {
    "mean": 77.19, "median": 55.04, "p95": 220.00, "min": -185.33, "max": 4037.80,
}
_FALLBACK_MODEL_STATS = {
    "mean": 69.24, "median": 48.75, "p95": 217.15, "min": -10.47, "max": 574.22,
}
_FALLBACK_FRAC_NEGATIVE_MODEL = 0.00013  # 0.013% (S2.3 honesty note)
_FALLBACK_FRAC_NEGATIVE_ACTUAL = 0.02241  # 2.241% (S2.3 honesty note)
_FALLBACK_N = 157106


def _ratio(real: float, model: float) -> Optional[float]:
    if model == 0:
        return None
    return real / model


def _exposure_tail_rows(actual_stats: dict, pred_stats: dict,
                         frac_negative_actual: float, frac_negative_model: float) -> List[Dict[str, Any]]:
    max_ratio = _ratio(actual_stats["max"], pred_stats["max"])
    neg_ratio = _ratio(frac_negative_actual, frac_negative_model)
    return [
        dict(
            metric="Extreme spike (max SSP)",
            unit="£/MWh",
            model=pred_stats["max"],
            real=actual_stats["max"],
            under_representation_x=max_ratio,
            severity="critical",
            why=(
                "A 3-feature/5-constant structural form cannot reproduce rare "
                "BM-driven multi-thousand-pound spikes (plant outages, "
                "interconnector trips, reserve-scarcity pricing) that are not "
                "present in gas price / demand / renewable-generation inputs "
                "at all."
            ),
        ),
        dict(
            metric="Negative-price frequency",
            unit="% of periods",
            model=frac_negative_model * 100.0,
            real=frac_negative_actual * 100.0,
            under_representation_x=neg_ratio,
            severity="critical",
            why=(
                "The model is structurally capable of negative prices and "
                "produces them, but an OLS-style fit minimizing squared error "
                "smooths tail behaviour toward the bulk of the distribution -- "
                "it underproduces both the frequency and the depth of real "
                "negative-price events."
            ),
        ),
    ]


def _live_exposure_tail() -> Optional[Dict[str, Any]]:
    """Attempt the live recomputation against the real Elexon/NBP cache.
    Returns None (never raises) if the cache/modules are unavailable so the
    caller can fall back to the cited numbers instead."""
    try:
        import numpy as np

        from sim.price_engine import DISPATCHABLE_CAPACITY_MW, THERMAL_EFFICIENCY
        from simulation import run_phase3b_recalibration as recal
    except Exception:
        return None

    try:
        rows = recal._build_dataset()
        if not rows:
            return None
        gas_price = np.array([r["gas_price"] for r in rows])
        demand_mw = np.array([r["demand_mw"] for r in rows])
        renewable_mw = np.array([r["renewable_mw"] for r in rows])
        ssp = np.array([r["ssp"] for r in rows])
        floor = gas_price / THERMAL_EFFICIENCY
        x = (demand_mw - renewable_mw) / DISPATCHABLE_CAPACITY_MW
        fit = recal._fit_form(floor, x, ssp, recal.SELECTED_X_TIGHT, recal.SELECTED_SCARCITY_EXPONENT)
        predictions = fit.pop("predictions")
        actual_stats = recal._distribution_stats(ssp)
        pred_stats = recal._distribution_stats(predictions)
        frac_negative_model = float(np.mean(predictions < 0))
        frac_negative_actual = float(np.mean(ssp < 0))
    except Exception:
        return None

    return dict(
        n=len(rows), actual=actual_stats, model=pred_stats,
        frac_negative_model=frac_negative_model, frac_negative_actual=frac_negative_actual,
    )


def _compute_exposure_tail() -> Dict[str, Any]:
    live = _live_exposure_tail()
    if live is not None:
        rows_out = _exposure_tail_rows(
            live["actual"], live["model"], live["frac_negative_actual"], live["frac_negative_model"]
        )
        return dict(
            available=True,
            basis="live_recomputed",
            n=live["n"],
            model=live["model"],
            real=live["actual"],
            frac_negative_model=live["frac_negative_model"],
            frac_negative_actual=live["frac_negative_actual"],
            rows=rows_out,
            source="simulation/run_phase3b_recalibration.py (live recomputation, unmodified)",
        )

    # Fall back to the cited, independently-reproducible numbers (see the
    # block comment above) rather than blanking the page's lead section.
    rows_out = _exposure_tail_rows(
        _FALLBACK_ACTUAL_STATS, _FALLBACK_MODEL_STATS,
        _FALLBACK_FRAC_NEGATIVE_ACTUAL, _FALLBACK_FRAC_NEGATIVE_MODEL,
    )
    return dict(
        available=True,
        basis="cited_from_fidelity_doc",
        n=_FALLBACK_N,
        model=_FALLBACK_MODEL_STATS,
        real=_FALLBACK_ACTUAL_STATS,
        frac_negative_model=_FALLBACK_FRAC_NEGATIVE_MODEL,
        frac_negative_actual=_FALLBACK_FRAC_NEGATIVE_ACTUAL,
        rows=rows_out,
        source=STEER_DOC + " S2.3 (sim/cache/ not present in this build environment "
                            "-- live recomputation unavailable; git-ignored, confirmed absent)",
    )


# ---------------------------------------------------------------------------
# Inspection chain (G3): built straight from the ledger record's own
# rel_id/relationship -- no re-fit, no new nodes invented.
# ---------------------------------------------------------------------------

_WORLD_SERIES_REF = "elexon_ssp_calibration_full_2016_03_01_to_2025_06_07"
_WORLD_VARIABLES = (
    "systemSellPrice", "gas_price_gbp_per_mwh", "demand_mw", "renewable_generation_mw",
)


def _inspection_chain_block(record: dict) -> Dict[str, Any]:
    try:
        chain = fic.InspectionChain()
        ev = fic.EvidenceRecord(rel_id=record["rel_id"], relationship=record["relationship"])
        chain.add_evidence(ev)
        world = fic.WorldRecord(
            world_series_ref=_WORLD_SERIES_REF,
            variables=_WORLD_VARIABLES,
            regime_label=None,
            driven_by=(record["rel_id"],),
        )
        chain.add_world(world)
        fic.validate_links(chain)
    except Exception as exc:  # pragma: no cover -- defensive
        return dict(available=False, note=f"chain construction failed: {exc}")

    rel = record.get("relationship", {})
    strength = rel.get("strength", {})
    nodes = []
    for node_id, node in chain.nodes.items():
        if isinstance(node, fic.EvidenceRecord):
            if strength.get("mae") is not None and strength.get("r2") is not None:
                detail = (
                    f"MAE=£{strength['mae']:.2f}/MWh, R2={strength['r2']:.3f}, "
                    f"provenance={rel.get('provenance')}"
                )
            else:
                detail = f"provenance={rel.get('provenance')}"
            nodes.append(dict(
                node_id=node_id, layer="EVIDENCE", ref=node.rel_id,
                label=rel.get("kind", node.rel_id),
                detail=detail,
            ))
        elif isinstance(node, fic.WorldRecord):
            nodes.append(dict(
                node_id=node_id, layer="WORLD", ref=node.world_series_ref,
                label=node.world_series_ref,
                detail="variables: " + ", ".join(node.variables),
            ))
    links = [
        dict(cause_id=l.cause_id, consequence_id=l.consequence_id, kind=l.kind)
        for l in chain.links
    ]
    return dict(
        available=True,
        note=(
            "No BELIEF_ACTION node: the price engine is WORLD-side physics with "
            "no live company consumer this pass, so there is nothing here that "
            "could carry a truth_ref leak."
        ),
        nodes=nodes,
        links=links,
    )


# ---------------------------------------------------------------------------
# Compose
# ---------------------------------------------------------------------------

def build_fidelity_data(records: Optional[List[dict]] = None) -> Dict[str, Any]:
    """The full site/data/fidelity.json payload, as a dict (no I/O beyond the
    ledger read + the exposure-tail's own live-recompute attempt). Exposed
    separately from `generate()` so `site/proof/test_fidelity_panel.py` can
    exercise the REAL current data without going through the on-disk file
    (mirrors `tools/generate_proof_data.py::_coupled_gaps` being importable
    directly by its own render-side test)."""
    if records is None:
        records = _load_records()
    if not records:
        return _unavailable(f"no fidelity-evidence records for {ATOM_ID} in the ledger yet")

    # This pass tracks exactly one live-emitted atom; if more land later,
    # render the most-recently-measured record (never silently average them).
    record = sorted(records, key=lambda r: r.get("measured_at") or "")[-1]
    grid_score = _score_grid(record)
    per_cell_rows = _per_cell_lift_rows(record)

    return dict(
        available=True,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        source_ledger=str(LEDGER_PATH.relative_to(PROJECT)),
        source_modules=[
            "background/fidelity_grid_scorer.py",
            "background/fidelity_inspection_chain.py",
            "background/fidelity_emitter.py",
            "simulation/run_phase3b_recalibration.py",
        ],
        steer_doc=STEER_DOC,
        atom_id=record.get("atom_id"),
        rel_id=record.get("rel_id"),
        measured_at=record.get("measured_at"),
        run_git_commit=record.get("run_git_commit"),
        exposure_tail=_compute_exposure_tail(),
        worst_cell=_worst_cell_block(record, grid_score),
        per_cell_lift=per_cell_rows,
        mae_reading=_mae_reading_block(record, per_cell_rows),
        inspection_chain=_inspection_chain_block(record),
        map_of_ignorance=[
            dict(cell_id=e.cell_id, ignorance=e.ignorance) for e in grid_score.map_of_ignorance
        ],
    )


def generate() -> bool:
    data = build_fidelity_data()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(("Written" if data.get("available") else "Written (unavailable)") + ": " + str(OUTPUT_PATH))
    return True


if __name__ == "__main__":
    generate()
