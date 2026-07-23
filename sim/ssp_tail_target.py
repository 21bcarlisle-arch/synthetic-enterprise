"""Empirical real SSP (System Sell Price) TAIL target -- step 1 of the spike-tail attack plan
(docs/design/proposals/PROPOSE_SPIKE_TAIL_ATTACK_PLAN.md; defect SPIKE_TAIL_SSP_RESIDUAL).

WHY THIS EXISTS: the attack plan's T1 tail-fidelity test must assert the model's tail (max,
negative-price fraction, and the SHAPE between -- the exceedance curve above ~GBP200/MWh) against a
REAL target. Recon found no machine-readable exceedance target on disk -- only the ledger's headline
max/neg-fraction (site/data/fidelity.json). This module computes the full real target DIRECTLY from
the ingested Elexon record, reproducibly (no magic numbers), so T1 has a target it can load and a
FAIL-OPEN guard (an empty/uncomputable target is a FAILED check, never green) can be built on it.

BLIND TO COMPANY P&L (R12/R13): this is a BASELINE-fidelity target derived only from real settlement
history over the model's own window -- it is the physics the generator must reproduce, decided blind
to any company outcome. It is a DIAGNOSTIC target, never a tuning knob (R12: the generator matches it
because the physics produces a heavier tail, not by write-back).

Reproduce:  python3 -m sim.ssp_tail_target   (prints the target JSON; --emit writes the artifact)
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

# The MODEL's own window (simulation/run_phase3b_recalibration.py) -- the target must be measured over
# the SAME span as the model it grades, else the gap is an artefact of a window mismatch.
MODEL_START_DATE = "2016-03-01"
MODEL_END_DATE = "2025-06-07"

# The exceedance thresholds (GBP/MWh) that characterise the tail SHAPE, not just its max. GBP200 is the
# plan's named "shape between" anchor; the higher rungs pin the scarcity-spike regime the model starves.
EXCEEDANCE_THRESHOLDS_GBP = (200.0, 300.0, 500.0, 1000.0, 2000.0, 3000.0)

TARGET_ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "docs" / "design" / "spike_tail_real_target.json"


def _percentile(sorted_vals: list[float], p: float) -> float:
    n = len(sorted_vals)
    if n == 0:
        raise ValueError("empty distribution -- a target computed from no data is a FAILED check, not zero")
    k = min(n - 1, max(0, int(round(p / 100.0 * (n - 1)))))
    return sorted_vals[k]


def real_ssp_tail(start_date: str = MODEL_START_DATE, end_date: str = MODEL_END_DATE) -> dict:
    """The empirical real SSP tail over [start_date, end_date], computed from the ingested Elexon
    record. Raises on an empty/missing distribution (FAIL-CLOSED: an uncomputable target is a failure,
    never a silently-zero pass -- R15 fail-open guard)."""
    from sim.cache_store import get_cached_prices  # local import: keeps module import cheap/side-effect-free

    records = get_cached_prices(start_date, end_date)
    if not records:
        raise ValueError(
            f"no cached SSP records for {start_date}..{end_date} -- cannot compute the real tail target "
            "(FAIL-CLOSED: a missing target is a failed check, not an empty pass)"
        )
    ssp = sorted(
        float(r["systemSellPrice"])
        for r in records
        if isinstance(r.get("systemSellPrice"), (int, float))
    )
    n = len(ssp)
    if n == 0:
        raise ValueError("cached SSP records carry no numeric systemSellPrice -- FAIL-CLOSED")
    neg = sum(1 for x in ssp if x < 0.0)
    exceedance = {f"frac_gt_{int(t)}": sum(1 for x in ssp if x > t) / n for t in EXCEEDANCE_THRESHOLDS_GBP}
    return {
        "source": "sim/cache/elexon_ssp_full.json (real Elexon settlement SSP, via sim.cache_store.get_cached_prices)",
        "window": {"start": start_date, "end": end_date},
        "n": n,
        "max": ssp[-1],
        "min": ssp[0],
        "mean": statistics.fmean(ssp),
        "median": _percentile(ssp, 50),
        "p95": _percentile(ssp, 95),
        "p99": _percentile(ssp, 99),
        "p99_9": _percentile(ssp, 99.9),
        "p99_99": _percentile(ssp, 99.99),
        "frac_negative": neg / n,
        "exceedance_gbp": exceedance,
    }


def _main(argv: list[str]) -> int:
    target = real_ssp_tail()
    text = json.dumps(target, indent=2)
    if "--emit" in argv:
        TARGET_ARTIFACT_PATH.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {TARGET_ARTIFACT_PATH}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv[1:]))
