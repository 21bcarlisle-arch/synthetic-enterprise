"""Grade the company's holdout estimate of a retention offer's effect against the world's truth.

REUSE: tools/grade_coin_drawn_holdout.py
CLASS: CUSTOM
INDEX: searched "grade", "holdout", "planted", "null arm". `tools/_pb6_engagement_recovery_arm.py`
       is the same plant-or-none recovery design, but through the full settled run loop and for a
       payment-channel effect, so it cannot reach thousands of decisions;
       `tools/grade_renewal_churn_belief.py` grades the churn BELIEF against realised departures.
       Nothing grades an offer-effect estimate against the world's own effect. The set is
       `simulation.coin_drawn_decision_set`, the company's view of it is
       `company.interfaces.sim_interface.holdout_decision_observations`, and the estimate is
       `company.pricing.discovered_price_sensitivity.estimate_offer_effect`: this file only joins
       them, which is why it lives in tools/, where reading the truth is allowed.

THREE ARMS PER SEED, so a result can be told from an artefact:
  * REAL -- the treated arm is offered `--cut` below the default; truth is the world's own curve.
  * NULL -- no cut, so the true effect is exactly zero. An estimate that "raises staying" here is a
    false positive, whatever it says on the real arm.
  * PLANTED -- the treated arm stays with the world's holdout probability plus `--planted`, so the
    truth is known by construction and does not depend on the world's curve being right.
Each is graded on whether its interval covers the truth and on its verdict.

THE CAVEAT THE DIRECTOR NAMED, which no arm here removes: the truth is the world's churn curve,
which we wrote. This grades whether the company can LEARN the curve from a holdout, not whether
the curve is the real one.
"""
from __future__ import annotations

import argparse
import json
import math
import tracemalloc
from pathlib import Path


def _power_n(p: float, effect: float, alpha_z: float = 1.96, power_z: float = 0.8416) -> int | None:
    """Decisions per arm for an 80%-power two-sided 5% test of `effect` at stay share `p`."""
    if not effect:
        return None
    return math.ceil(2 * (alpha_z + power_z) ** 2 * p * (1 - p) / effect ** 2)


def grade_arm(seed: int, *, cut: float, planted: float | None, per_year: float) -> dict:
    from company.interfaces.sim_interface import holdout_decision_observations
    from company.pricing.discovered_price_sensitivity import estimate_offer_effect
    from simulation.coin_drawn_decision_set import build_decision_set

    tracemalloc.start()
    s = build_decision_set(seed, cut_gbp_per_mwh=cut, planted_effect=planted,
                           acquisitions_per_year=per_year)
    _cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    est = estimate_offer_effect(holdout_decision_observations(s.rows))
    truth = s.true_effect
    covered = (est.low is not None and truth is not None and est.low <= truth <= est.high)
    p_hold = sum(r["p_stay_holdout"] for r in s.rows) / len(s.rows)
    return {
        "seed": seed, "arm": "planted" if planted is not None else ("null" if cut == 0 else "real"),
        "cut_per_mwh": cut, "planted_effect": planted,
        "households": s.households, "decisions": len(s.rows), "per_arm": s.per_arm,
        "true_effect": round(truth, 5), "estimate": est.effect and round(est.effect, 5),
        "low": est.low and round(est.low, 5), "high": est.high and round(est.high, 5),
        "covered": covered, "verdict": est.verdict,
        "mean_true_p_stay_held_out": round(p_hold, 4),
        "per_arm_for_80pct_power": _power_n(p_hold, truth),
        "cost": {"seconds": round(s.seconds, 1),
                 "ms_per_decision": round(1000 * s.seconds / len(s.rows), 2),
                 "day_records_built": s.day_records_built,
                 "day_records_per_decision": round(s.day_records_built / len(s.rows), 1),
                 "traced_peak_mb": round(peak / 1e6, 1)},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seeds", type=int, nargs="+", default=[42])
    ap.add_argument("--cut", type=float, default=7.5, help="the real arm's cut, per MWh")
    ap.add_argument("--planted", type=float, default=0.05)
    ap.add_argument("--per-year", type=float, default=800.0,
                    help="households drawn per acquisition year (sets the decision count)")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    results = []
    for seed in args.seeds:
        for cut, planted in ((args.cut, None), (0.0, None), (0.0, args.planted)):
            row = grade_arm(seed, cut=cut, planted=planted, per_year=args.per_year)
            print(json.dumps(row), flush=True)
            results.append(row)
    args.out.write_text(json.dumps({"args": {k: str(v) for k, v in vars(args).items()},
                                    "arms": results}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
