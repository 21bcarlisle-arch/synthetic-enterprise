"""Generate the REALISED COHORT COVERAGE artifact (CA2, ruling §3).

DIRECTOR_RULING_COHORT_ASSIGNMENT_ACTIVATED_2026-07-27 §3: "the coverage report
… must now also make the realised cohort structure legible: which cells actually
fill at N=200 and which stay thin, per dimension and jointly where it matters."

WHAT THIS DOES
--------------
Draws the population at the director's stated pool target (N≈200) with cohorts
ASSIGNED and regions drawn — the same seam parameters `simulation/live_population.
py` uses (base seed 20260724, `draw_region=True`, default 2021-2025 window) — plus
`assign_cohorts=True` (the CA1 flag). Builds the per-axis + JOINT coverage report
and writes it to a published, inspectable artifact:

    docs/observability/cohort_coverage_realised.json

so a run's realised cohort distribution — per-dimension AND the ~12-cell value
knee — is inspectable and the thin cells at N=200 are NAMED (ruling Acceptance).

HONESTY ABOUT N (R13, NOT a curriculum change)
----------------------------------------------
The SHIPPED default acquisition rate is λ=1.0 (a handful of customers); the λ that
realises the director's N=200 pool is R13-reserved and ESCALATED — it is NOT
flipped here. This report is the coverage MACHINERY's own diagnostic draw: it
sets λ = N_target / n_years locally to answer the ruling's "which cells fill at
N=200" question WITHOUT touching `segmentation_curriculum_v1.json` or any live
default. The artifact records this provenance explicitly so no reader mistakes it
for the live run's realised N (which follows the reserved λ once activated).

RC7 / R12
---------
Cell counts only — NO cohort-derived financial figure (RC7 holds: this artifact
never leads a £ surface). Cell counts are a DIAGNOSTIC and thinness is a FINDING,
never a target to tune the draw toward (R12).
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from simulation.population_coverage import (
    DEFAULT_JOINT_THIN_FLOOR,
    coverage_gate_ok,
    population_coverage_report,
)
from simulation.population_draw import (
    DEFAULT_END_YEAR,
    DEFAULT_START_YEAR,
    draw_population,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACT_PATH = _REPO_ROOT / "docs" / "observability" / "cohort_coverage_realised.json"

# Same seam parameters live_population.py draws with (determinism + replay, C-S2).
_SEAM_BASE_SEED = 20260724
_N_TARGET = 200  # the director's stated pool size (2026-07-25 activation)


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO_ROOT, text=True
        ).strip()[:12]
    except Exception:
        return "unknown"


def build_artifact(
    *,
    base_seed: int = _SEAM_BASE_SEED,
    n_target: int = _N_TARGET,
    joint_thin_floor: int = DEFAULT_JOINT_THIN_FLOOR,
    generated_at: str | None = None,
) -> dict:
    """Draw at N≈`n_target` with cohorts+regions and build the coverage dict."""
    n_years = DEFAULT_END_YEAR - DEFAULT_START_YEAR + 1
    # λ chosen locally to hit the N_target diagnostic draw — NOT written to the
    # curriculum, NOT the shipped default (R13-reserved λ stays escalated).
    lam = n_target / n_years
    pop = draw_population(
        base_seed,
        assign_cohorts=True,
        draw_region=True,
        acquisitions_per_year_lambda=lam,
    )
    report = population_coverage_report(pop, joint_thin_floor=joint_thin_floor)
    gen = generated_at or datetime.now(timezone.utc).isoformat()
    return {
        "_meta": {
            "artefact": "cohort_coverage_realised",
            "atom": "CA2_coverage_report_realised_cohort",
            "ruling": "DIRECTOR_RULING_COHORT_ASSIGNMENT_ACTIVATED_2026-07-27 §3",
            "purpose": "make the realised cohort structure legible — which cells "
                       "fill at N=200 and which stay thin, per dimension AND at "
                       "the ~12-cell value knee. Thin cells are FINDINGS (§3).",
            "generated_at": gen,
            "code_sha": _git_head(),
            "provenance": {
                "base_seed": base_seed,
                "draw_region": True,
                "assign_cohorts": True,
                "year_window": [DEFAULT_START_YEAR, DEFAULT_END_YEAR],
                "n_target": n_target,
                "acquisitions_per_year_lambda_used": lam,
                "n_realised": report.n_customers,
                "lambda_note": "λ set locally to hit the N_target DIAGNOSTIC draw; "
                               "the shipped default is λ=1.0 and the live-run λ that "
                               "realises N=200 is R13-reserved/escalated — NOT set here.",
            },
            "rc7": "cell counts only; no cohort-derived financial figure (RC7 holds).",
            "r12": "cell counts are a diagnostic; thinness is a finding, never a target.",
        },
        "coverage": report.as_dict(),
        "gate_ok": coverage_gate_ok(report),
    }


def write_artifact(artifact: dict, path: Path = _ARTIFACT_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=False) + "\n")
    return path


def _print_summary(artifact: dict) -> None:
    cov = artifact["coverage"]
    meta = artifact["_meta"]["provenance"]
    print(f"N realised = {cov['n_customers']} (target {meta['n_target']}, "
          f"seed {meta['base_seed']})")
    for name, j in cov.get("joints", {}).items():
        print(f"\nJOINT {name}: {j['n_cells_filled']}/{j['n_cells_grid']} cells "
              f"filled, N_scored={j['n_customers_scored']}, "
              f"uniform-expected {j['uniform_expected']}")
        for f in j["findings"]:
            print(f"  • {f}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n-target", type=int, default=_N_TARGET)
    ap.add_argument("--seed", type=int, default=_SEAM_BASE_SEED)
    ap.add_argument("--stdout", action="store_true",
                    help="print the artifact to stdout instead of writing the file")
    args = ap.parse_args()
    artifact = build_artifact(base_seed=args.seed, n_target=args.n_target)
    if args.stdout:
        print(json.dumps(artifact, indent=2))
        return
    path = write_artifact(artifact)
    _print_summary(artifact)
    print(f"\nwrote {path.relative_to(_REPO_ROOT)}")


if __name__ == "__main__":
    main()
