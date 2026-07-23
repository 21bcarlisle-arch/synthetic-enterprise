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

# The DAILY-granularity real target (step-3 diagnosis, 2026-07-23). The forward scenario generator
# (sim/scenario/bimodal_generator.py) emits ONE price per calendar day, flat-expanded to 48 identical
# half-hours by simulation/run_scenario.py::_expand_daily_to_hh. So the residual in forward worlds
# settles against a DAILY price with NO intraday shape -- the generator's natural comparand is the real
# DAILY tail, NOT the half-hourly one above. `spike_tail_real_target.json` (HH) and this artifact (daily)
# together make the granularity seam explicit, so a future T1 grades the generator like-for-like instead
# of against a half-hourly max no daily-mean series can (or should) reach.
DAILY_TARGET_ARTIFACT_PATH = (
    Path(__file__).resolve().parent.parent / "docs" / "design" / "spike_tail_real_target_daily.json"
)


def _percentile(sorted_vals: list[float], p: float) -> float:
    n = len(sorted_vals)
    if n == 0:
        raise ValueError("empty distribution -- a target computed from no data is a FAILED check, not zero")
    k = min(n - 1, max(0, int(round(p / 100.0 * (n - 1)))))
    return sorted_vals[k]


def tail_stats(values) -> dict:
    """The numeric tail-shape block (n, max/min, percentiles, negative-fraction, exceedance curve)
    for any SSP-price distribution -- shared by the REAL target (this module) and the MODEL tail
    (sim/ssp_tail_model.py) so T1 grades like-for-like (same maths on both sides, no apples-to-oranges
    that would let a spurious 'match' pass). Raises on an empty distribution (FAIL-CLOSED: an
    uncomputable tail is a failed check, never a silently-zero pass -- R15 fail-open guard)."""
    ssp = sorted(float(v) for v in values)
    n = len(ssp)
    if n == 0:
        raise ValueError("empty distribution -- a tail computed from no data is a FAILED check, not zero")
    neg = sum(1 for x in ssp if x < 0.0)
    exceedance = {f"frac_gt_{int(t)}": sum(1 for x in ssp if x > t) / n for t in EXCEEDANCE_THRESHOLDS_GBP}
    return {
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
    ssp = [
        float(r["systemSellPrice"])
        for r in records
        if isinstance(r.get("systemSellPrice"), (int, float))
    ]
    if not ssp:
        raise ValueError("cached SSP records carry no numeric systemSellPrice -- FAIL-CLOSED")
    return {
        "source": "sim/cache/elexon_ssp_full.json (real Elexon settlement SSP, via sim.cache_store.get_cached_prices)",
        "window": {"start": start_date, "end": end_date},
        **tail_stats(ssp),
    }


def _daily_aggregate(records, agg: str) -> list[float]:
    """Collapse half-hourly SSP records to one value per settlementDate. agg="mean" gives the daily
    average SSP (the generator's natural comparand -- its daily price flat-expands to 48 equal SPs);
    agg="max" gives the worst SP of each day (where the real half-hourly spike lives). Raises on empty
    (FAIL-CLOSED)."""
    from collections import defaultdict

    buckets: dict[str, list[float]] = defaultdict(list)
    for r in records:
        v = r.get("systemSellPrice")
        if isinstance(v, (int, float)):
            buckets[r["settlementDate"]].append(float(v))
    if not buckets:
        raise ValueError("no numeric daily SSP buckets -- FAIL-CLOSED")
    if agg == "mean":
        return [statistics.fmean(vs) for vs in buckets.values()]
    if agg == "max":
        return [max(vs) for vs in buckets.values()]
    raise ValueError(f"unknown daily aggregation '{agg}' (expected 'mean' or 'max')")


def real_ssp_daily_tail(
    agg: str = "mean", start_date: str = MODEL_START_DATE, end_date: str = MODEL_END_DATE
) -> dict:
    """The empirical real DAILY SSP tail over [start_date, end_date], aggregating the ingested half-hourly
    Elexon record to one value per day (agg="mean" or "max"). This is the granularity the FORWARD generator
    actually settles at (daily price, flat-expanded to 48 SPs) -- so it, not the half-hourly target, is what
    the generator's daily tail must be graded against. Raises on an empty/missing distribution (FAIL-CLOSED).

    BLIND TO COMPANY P&L (R12/R13): a baseline-fidelity target from real settlement history only."""
    from sim.cache_store import get_cached_prices  # local import: cheap/side-effect-free module import

    records = get_cached_prices(start_date, end_date)
    if not records:
        raise ValueError(
            f"no cached SSP records for {start_date}..{end_date} -- cannot compute the daily tail target "
            "(FAIL-CLOSED: a missing target is a failed check, not an empty pass)"
        )
    daily = _daily_aggregate(records, agg)
    return {
        "source": "sim/cache/elexon_ssp_full.json aggregated to daily via sim.ssp_tail_target._daily_aggregate",
        "granularity": f"daily_{agg}",
        "window": {"start": start_date, "end": end_date},
        **tail_stats(daily),
    }


def _main(argv: list[str]) -> int:
    if "--daily" in argv:
        target = {
            "why": (
                "The forward scenario generator emits one price per day, flat-expanded to 48 equal "
                "half-hours (run_scenario.py::_expand_daily_to_hh), so forward residuals settle at DAILY "
                "granularity with no intraday shape. daily_mean is the generator's natural comparand; "
                "daily_max shows where the real half-hourly spike (GBP4,038) actually lives -- it is a "
                "sub-daily phenomenon a daily-mean series cannot and should not reach."
            ),
            "daily_mean": real_ssp_daily_tail("mean"),
            "daily_max": real_ssp_daily_tail("max"),
        }
        text = json.dumps(target, indent=2)
        if "--emit" in argv:
            DAILY_TARGET_ARTIFACT_PATH.write_text(text + "\n", encoding="utf-8")
            print(f"wrote {DAILY_TARGET_ARTIFACT_PATH}")
        else:
            print(text)
        return 0

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
