"""Fit C2's ONE free constant — the P0 calibration — and print the table it is judged on.

Pre-registration: `docs/staging/WORKER_PREREGISTRATION_WHAT_A_DEPARTURE_WITH_A_CAUSE_MUST_SHOW_2026-08-30.md`.
Design: `docs/design/C2_DEPARTURE_WITH_A_CAUSE_DESIGN.md` §5, which fixes the order of work and says
not to reorder it: P0 first, because until the LEVEL is held still the DECOMPOSITION is the only
thing that should have moved and nothing else in the pre-registration is readable.

WHAT IS FITTED, AND WHY IT IS ONLY ONE NUMBER. `simulation/departure_risks.py` takes the published
Ofgem/BMG importances (price 0.40, service 0.32) as the RATIO between the two sensitivities, and
the bill-shock hazard keeps the churn model's own calibrated base rate unscaled. That leaves a
single global scale with nothing published behind it, and this module fits it — by bisection, to
the population-mean realised churn of the run the factor table was captured from.

A SCALE CANNOT TUNE THE ANSWER, which is the property that keeps P0 from quietly setting P2. It
moves every non-shock hazard together, so it moves the LEVEL and leaves the price:service ratio
where the published evidence put it. If the fit needed a second parameter, one of them would be
free to shape the reason mix, and the mix is the thing being measured.

THE BASELINE IS THE SAME RUN, NOT A STORED ONE. The target mean is read from
`realized_churn_probability` in the captured table itself, not from a previous
`run_output_latest.json`. A calibration fitted against a baseline from a DIFFERENT run measures the
difference between two runs and reports it as the effect of the change.

Usage:  python3 -m tools.fit_departure_hazards [factor_table.json]
"""
import json
import statistics
import sys
from pathlib import Path

from simulation.departure_risks import (
    ORDERED_CAUSES,
    build_departure_risks,
    cause_shares,
    total_departure_probability,
)

PROJECT = Path(__file__).resolve().parent.parent
DEFAULT_TABLE = PROJECT / "docs" / "reports" / "c2_departure_factors.json"

#: Pre-registration P0: population-mean realised churn must match the composed form within this
#: RELATIVE tolerance. Not a target to be approached -- the one number that must NOT be interesting.
P0_RELATIVE_TOLERANCE = 0.005


def _risks_for(row: dict, scale: float) -> dict[str, float]:
    """The competing risks for one captured renewal.

    `retention_offer_retained_fraction` is deliberately 1.0: the baseline being matched is
    `realized_churn_probability`, which is captured BEFORE any retention offer, so including the
    offer here would compare a post-intervention probability against a pre-intervention one.
    """
    return build_departure_risks(
        bill_shock_base=row["sim_bill_shock_base"],
        price_response=row["sim_price_response"],
        dissatisfaction_response=row["sim_dissatisfaction_response"],
        market_opportunity=row["sim_market_opportunity"],
        action_propensity=row["sim_action_propensity"],
        retention_offer_retained_fraction=1.0,
        sensitivity_scale=scale,
    )


def mean_departure_probability(rows: list[dict], scale: float) -> float:
    return statistics.fmean(
        total_departure_probability(_risks_for(r, scale)) for r in rows
    )


def fit_scale(rows: list[dict], target_mean: float) -> float:
    """Bisect the sensitivity scale onto the target population mean.

    Monotone by construction -- every hazard the scale touches is increasing in it, and
    `1 - Π(1-h)` is increasing in every hazard — so bisection cannot land on a local solution.
    """
    lo, hi = 0.0, 1.0
    if mean_departure_probability(rows, hi) < target_mean:
        raise SystemExit(
            "P0 CANNOT BE MET: even a sensitivity scale of 1.0 leaves mean departure probability "
            f"at {mean_departure_probability(rows, hi):.6f}, below the target {target_mean:.6f}. "
            "Per the pre-registration this is a RESULT, not something to force: the composed form "
            "is encoding something the competing-risks form cannot express. Leave the composed "
            "form standing and find out what."
        )
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if mean_departure_probability(rows, mid) < target_mean:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _quantile(sorted_vals: list[float], q: float) -> float:
    """Nearest-rank quantile, stated because the pre-registration's baseline table used one method
    and a reader comparing against a different one would see a move that is not there."""
    if not sorted_vals:
        return float("nan")
    idx = min(len(sorted_vals) - 1, int(q * len(sorted_vals)))
    return sorted_vals[idx]


def _distribution(vals: list[float]) -> dict[str, float]:
    s = sorted(vals)
    return {
        "min": s[0], "median": _quantile(s, 0.5), "mean": statistics.fmean(s),
        "p90": _quantile(s, 0.90), "p95": _quantile(s, 0.95), "p99": _quantile(s, 0.99),
        "max": s[-1],
    }


def main(table_path: Path) -> int:
    rows = [r for r in json.loads(table_path.read_text())
            if r.get("sim_bill_shock_base") is not None]
    baseline = [r["realized_churn_probability"] for r in rows]
    target = statistics.fmean(baseline)
    scale = fit_scale(rows, target)
    achieved = mean_departure_probability(rows, scale)
    rel = (achieved - target) / target

    print(f"rows: {len(rows)}   composed-form mean (baseline): {target:.6f}")
    print(f"fitted sensitivity scale: {scale:.8f}")
    print(f"competing-risks mean:     {achieved:.6f}   relative error {rel:+.5%}")
    print(f"P0 (|rel| <= {P0_RELATIVE_TOLERANCE:.1%}): "
          f"{'HOLDS' if abs(rel) <= P0_RELATIVE_TOLERANCE else 'FAILS'}")

    new = [total_departure_probability(_risks_for(r, scale)) for r in rows]
    print("\nP1 -- distribution of the departure probability (nearest-rank quantiles)")
    print(f"{'':>8} {'composed':>10} {'competing':>10}   {'move':>8}")
    b, n = _distribution(baseline), _distribution(new)
    for k in ("min", "median", "mean", "p90", "p95", "p99", "max"):
        print(f"{k:>8} {b[k]:10.4f} {n[k]:10.4f}   {n[k] - b[k]:+8.4f}")

    print("\nP2 -- reason mix, EXPECTED shares (hazard-weighted over all renewals).")
    print("     This is NOT the realised mix and must not be published as one: the realised mix")
    print("     is ~40 departures in a decade and needs measuring across seeds (see P2).")
    agg = {c: 0.0 for c in ORDERED_CAUSES}
    weight = 0.0
    for r in rows:
        risks = _risks_for(r, scale)
        p = total_departure_probability(risks)
        for c, sh in cause_shares(risks).items():
            agg[c] += sh * p
        weight += p
    for c in ORDERED_CAUSES:
        print(f"  {c:>16}: {agg[c] / weight:6.1%}")
    return 0


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TABLE
    raise SystemExit(main(path))
