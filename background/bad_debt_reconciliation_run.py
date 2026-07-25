"""HARNESS collector for the bad-debt reconciliation bridge.

WHY THIS LIVES IN background/ (NOT company/): it is the both-sides measurement
bridge -- it reads the company's OWN flat provision (`saas.payment_behaviour`)
AND the SIM's settled-clock realised write-off
(`simulation.arrears_engine.compute_emergent_bad_debt`) to compute the gap. A
module under `company/` importing `simulation.*` breaches the epistemic wall and
trips `tools.epistemic_verifier`; `background/` is the verifier-exempt harness
path where `background/live_payment_triad.py` legitimately holds both sides for
exactly this reason. The pure finance math (the reconciliation itself, the report
shape, the ledger record, the R15-failable control) lives wall-clean in
`company/finance/bad_debt_reconciliation.py`; this file only GATHERS the two
per-year primitives and hands them across, then writes the report + ledger row.

C-S2 (determinism): `seed` is passed straight through to
`compute_emergent_bad_debt` (default 42, the same seed the billing ledger uses);
`as_of`/`generated_from` are gathered by the caller. No clock/random draw here.

R12: reports what was measured; never tunes a figure. Report-first -- this MOVES
NO PUBLISHED FIGURE (it writes docs/observability/bad_debt_reconciliation.json and
one fidelity-ledger row; it does not touch net_margin, EV, dashboards, or the
margin bridge).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Mapping, Optional, Tuple

from company.finance.bad_debt_reconciliation import (
    LEDGER_ATOM_ID,
    build_ledger_record,
    build_report,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_PATH = PROJECT_DIR / "docs" / "observability" / "bad_debt_reconciliation.json"


def flat_provision_by_year(bills: list) -> Dict[int, float]:
    """Method 1 (LIVE, billed clock): the flat-haircut bad-debt provision per
    year, summed from the company's own bills via
    `saas.payment_behaviour.build_payment_behaviour` (rate x billed revenue per
    bill, keyed by the bill's period-end year -- the billed clock)."""
    from saas.payment_behaviour import build_payment_behaviour

    behaviour = build_payment_behaviour(bills)
    by_year: Dict[int, float] = {}
    for records in behaviour.values():
        for rec in records:
            year = int(rec["period_end"][:4])
            by_year[year] = by_year.get(year, 0.0) + float(rec["bad_debt_provision_gbp"])
    return {y: round(v, 2) for y, v in by_year.items()}


def realised_by_year(
    bills: list,
    behavioral: Mapping,
    churned_ids: set,
    *,
    seed: int = 42,
) -> Dict[int, float]:
    """Method 4 (TRUTH, settled clock): GBP actually written off per year, from
    `simulation.arrears_engine.compute_emergent_bad_debt` (keyed by
    (customer_id, write_off_year)), aggregated to the write-off year."""
    from simulation.arrears_engine import compute_emergent_bad_debt

    emergent = compute_emergent_bad_debt(bills, behavioral, churned_ids, seed=seed)
    by_year: Dict[int, float] = {}
    for (_cid, year), gbp in emergent.items():
        by_year[year] = by_year.get(year, 0.0) + float(gbp)
    return {y: round(v, 2) for y, v in by_year.items()}


def collect_primitives_from_run(
    run_data: Mapping,
    *,
    seed: int = 42,
) -> Tuple[Dict[int, float], Dict[int, float]]:
    """Gather the two reconcilable per-year primitives from a run-output dict
    (the shape of docs/reports/run_output_latest.json: `bills`,
    `per_customer_behavioral`, `churned_billing_accounts`). Returns
    (flat_provision_by_year, realised_by_year)."""
    bills = run_data.get("bills", []) or []
    behavioral = run_data.get("per_customer_behavioral", {}) or {}
    churned = set(run_data.get("churned_billing_accounts", []) or [])
    return (
        flat_provision_by_year(bills),
        realised_by_year(bills, behavioral, churned, seed=seed),
    )


def generate_report(
    run_data: Mapping,
    *,
    generated_from: str,
    seed: int = 42,
) -> dict:
    """Build (do NOT write) the reconciliation report from a run-output dict."""
    flat, realised = collect_primitives_from_run(run_data, seed=seed)
    return build_report(flat, realised, generated_from=generated_from)


def write_report(report: Mapping, *, report_path: Optional[Path] = None) -> Path:
    """Write the report artifact (docs/observability/bad_debt_reconciliation.json)."""
    path = Path(report_path) if report_path is not None else REPORT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def register_ledger_row(report: Mapping, *, ledger_path: Optional[Path] = None) -> dict:
    """Register the provision-vs-realised variance as a fidelity-ledger row
    (steer D2). Uses `append_record` (read-merge-write), preserving every other
    row. Returns the full ledger dict after the merge."""
    from background.fidelity_evidence_ledger import append_record

    record = build_ledger_record(report)
    return append_record(record, ledger_path=ledger_path)


def run_from_run_output(
    run_json_path: Optional[Path] = None,
    *,
    seed: int = 42,
    report_path: Optional[Path] = None,
    ledger_path: Optional[Path] = None,
    register_ledger: bool = True,
) -> dict:
    """End-to-end: read a run-output JSON, build + write the report, and (by
    default) register the fidelity-ledger row. Returns the report dict.

    `register_ledger=False` lets a smoke/test build+write the report without
    touching the real ledger."""
    path = Path(run_json_path) if run_json_path is not None else (
        PROJECT_DIR / "docs" / "reports" / "run_output_latest.json"
    )
    run_data = json.loads(path.read_text(encoding="utf-8"))
    report = generate_report(
        run_data,
        generated_from=f"run_output {path.name} (seed={seed})",
        seed=seed,
    )
    write_report(report, report_path=report_path)
    if register_ledger:
        register_ledger_row(report, ledger_path=ledger_path)
    return report
