#!/usr/bin/env python3
"""Generate site/data/premise_demand.json -- the demand-arrow evidence feed for
the World door's causal spine (weather -> demand).

The model-on-a-page campaign (WORDS -> DIAGRAM -> EVIDENCE) requires every arrow
of the walkable causal spine to carry its evidence chart. The demand arrow
(weather -> the demand each home places) rendered a headline weather number but
NO belief-vs-truth evidence for the company's half-hourly demand model. This
feed closes that gap.

SOURCE (single, already-committed): docs/observability/coupled_gap_ledger.json ->
  W1_5_premise_demand_shape.components. This is a RENDERING of an existing
measured result, never a re-computation (SITE_CONSTITUTION rule: "the site is a
rendering, never an author"). W1_5 is the COUPLED twin of company
C13_weather_normalisation; its belief-vs-truth was measured at TWO belief forms:

  L1 (comparison):  demand ~ base + b_hdd*HDD + b_cdd*CDD              (r2 ~ 0.551)
  L2 (headline):    + b_windchill*windchill_DD  (the CWV wind-chill term, r2 ~ 0.552)

against a no-skill baseline g0 = climatological mean (predict the average demand).
The SCORE is the WORST-explained cell (campaign requirement), not the flattering
population average -- worst cell = summer, CWV MAE 2276 MW vs no-skill 2190 MW
(a near-tie: the wind-chill term barely helps its worst cell, and we say so).

R11/R14/R15 obligations honoured here:
  - R11: this feed carries the raw measured MAE/N so the page renders the actual
    value; the render test asserts the deployed pixel (2276 / 2190 / n=3337).
  - R14: every figure carries its basis -- MAE in MW, N train records, the belief
    FORM label, and the measured_at/run_git_commit clock of the measurement.
  - R15 (a control must be able to FAIL): `available` is False and `cells` is empty
    when the ledger block is missing/malformed, so the panel fails closed and
    VISIBLE (never a silently empty or fabricated bar). R12: MAE is a diagnostic
    of belief-vs-truth, never a target -- the worst-cell near-tie is surfaced.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
LEDGER_PATH = PROJECT / "docs" / "observability" / "coupled_gap_ledger.json"
OUT_PATH = PROJECT / "site" / "data" / "premise_demand.json"

ATOM_ID = "W1_5_premise_demand_shape"

# Cells ordered coldest -> warmest for a readable table; the two wind-relevant
# tail cells sit next to their base cell. Missing cells are simply skipped.
CELL_ORDER = ["winter", "cold", "cold_windy_tail", "shoulder", "warm", "summer"]
CELL_LABEL = {
    "winter": "Winter",
    "cold": "Cold",
    "cold_windy_tail": "Cold & windy (tail)",
    "shoulder": "Shoulder",
    "warm": "Warm",
    "summer": "Summer",
}


def _load(path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _num(v):
    """Round MAE-scale MW to whole numbers; pass floats (r2/gap) through."""
    try:
        return round(float(v))
    except (TypeError, ValueError):
        return None


def _fnum(v, nd=3):
    try:
        return round(float(v), nd)
    except (TypeError, ValueError):
        return None


def _empty(reason):
    """Fail-closed, VISIBLE payload (R15): available False, no fabricated bar."""
    return dict(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        atom=ATOM_ID,
        available=False,
        reason=reason,
        cells=[],
    )


def build():
    ledger = _load(LEDGER_PATH)
    if not isinstance(ledger, dict) or ATOM_ID not in ledger:
        return _empty("coupled_gap_ledger.json has no " + ATOM_ID + " block")
    block = ledger.get(ATOM_ID) or {}
    comp = block.get("components") or {}
    per_cell = comp.get("per_cell") or {}
    coeffs = comp.get("belief_coeffs") or {}
    coeffs_l1 = comp.get("belief_coeffs_l1") or {}
    if not per_cell:
        return _empty(ATOM_ID + " has no per_cell measurements")

    cells = []
    for key in CELL_ORDER:
        c = per_cell.get(key)
        if not isinstance(c, dict):
            continue
        mm = _num(c.get("mae_model"))
        ns = _num(c.get("mae_noskill"))
        if mm is None or ns is None:
            continue
        cells.append(dict(
            key=key,
            label=CELL_LABEL.get(key, key),
            mae_model=mm,                       # L2 headline (CWV) MAE, MW
            mae_model_l1=_num(c.get("mae_model_l1")),  # L1 (temperature-only) MAE, MW
            mae_noskill=ns,                     # g0 climatological-mean MAE, MW
            gap=_fnum(c.get("gap")),            # L2 prediction gap (model/noskill)
            gap_l1=_fnum(c.get("gap_l1")),      # L1 prediction gap
            bias_model=_num(c.get("bias_model")),
            n=c.get("n"),
        ))
    if not cells:
        return _empty(ATOM_ID + " per_cell had no renderable cell")

    worst_key = comp.get("worst_cell")
    worst = next((c for c in cells if c["key"] == worst_key), None)

    n_train = coeffs.get("n_train") or coeffs_l1.get("n_train")

    return dict(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        atom=ATOM_ID,
        twin_atom=block.get("twin_atom_id"),
        available=True,
        measured_at=block.get("measured_at"),
        run_git_commit=block.get("run_git_commit"),
        n_train=n_train,
        baseline_label="g0 = climatological-mean no-skill (predict the average demand)",
        belief_form_l1="demand ~ base + b_hdd·HDD + b_cdd·CDD",
        belief_form_l2="+ b_windchill·windchill_DD  (the CWV wind-chill degree-day term)",
        r2_l1=_fnum(coeffs_l1.get("r2")),
        r2_l2=_fnum(coeffs.get("r2")),
        score_definition=comp.get("score_definition"),
        worst_cell=worst_key,
        worst=worst,
        cwv_worst_cell_gap_delta=_fnum(comp.get("cwv_worst_cell_gap_delta"), 5),
        # Honest caveat, surfaced not hidden (R12/R15): the CWV term barely helps
        # its worst cell, and a 2nd L1->L2 refinement is built but not yet
        # measurable in this atom's file_scope.
        honesty_note=(
            "The wind-chill (CWV) term barely improves the worst cell "
            "(summer near-tie); it helps the wind-relevant cells it targets. "
            "MAE is belief-vs-truth here, a diagnostic, never a target (R12)."
        ),
        cells=cells,
    )


def generate():
    data = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return data


if __name__ == "__main__":
    generate()
