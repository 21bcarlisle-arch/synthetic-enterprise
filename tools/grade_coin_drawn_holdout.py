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


#: The two published ends of the share of a retained household's bill a supplier keeps. The floor
#: is the cap's EBIT allowance (1.9%, `docs/market_research/ASSUMPTIONS.md` row 49; 2.5-2.6% by
#: Jul-Sep 2026, row 300): every opex pound leaves with the customer. The ceiling is the sector's
#: gross margin before opex (8-14%, `docs/market_research/supplier_financial_reporting.md`): no
#: opex pound does. Where between them one customer sits is not established; both are graded.
MARGIN_SHARE_ENDS = (0.019, 0.14)


def lifetime_value(obs: dict, *, stay_share: float, margin_share: float) -> float:
    """What keeping one household is worth to the supplier: a margin share of its own trailing
    year's bills over 1 + s/(1-s) years of tenure at the observed stay share s, undiscounted."""
    return margin_share * sum(obs["monthly_bills"]) * (1.0 + stay_share / (1.0 - stay_share))


def cut_cost_gbp(obs: dict, cut: float) -> float:
    """One year of a per-MWh cut on the household's billed kWh."""
    return cut * obs["billed_kwh"] / 1000.0


def _rule_value(row: dict, cut: bool, *, cut_cost: float, lifetime: float) -> float:
    """The supplier's forward value of one decision under the world's own P(stay)."""
    p = row["p_stay_treated"] if cut else row["p_stay_holdout"]
    return p * (lifetime - (cut_cost if cut else 0.0))


def grade_decision(train, fresh, *, cut: float, margin_share: float) -> dict:
    """The company learns on `train` and decides on `fresh`; each rule is graded on `fresh` with
    the world's own P(stay) at each offer. Supplier value and household saving are kept apart."""
    from company.interfaces.sim_interface import holdout_decision_observations
    from company.pricing.discovered_price_sensitivity import (
        decisions_needed_per_arm,
        estimate_offer_effect,
        estimate_offer_effect_by_channel,
        retention_cut_decision,
    )

    seen_train = holdout_decision_observations(train.rows)
    pooled = estimate_offer_effect(seen_train)
    by_channel = estimate_offer_effect_by_channel(seen_train)
    s = pooled.stayed_held_out / pooled.held_out
    totals = {k: {"cut": 0, "supplier": 0.0, "household": 0.0} for k in ("learned", "all", "none")}
    reads: dict[str, int] = {}
    seen_fresh = holdout_decision_observations(fresh.rows)
    for row, obs in zip(fresh.rows, seen_fresh):
        d = retention_cut_decision(obs, cut_gbp_per_mwh=cut, margin_share=margin_share,
                                   by_channel=by_channel, pooled=pooled)
        reads[d.read.split(":")[0]] = reads.get(d.read.split(":")[0], 0) + 1
        lifetime = lifetime_value(obs, stay_share=s, margin_share=margin_share)
        cut_cost = cut_cost_gbp(obs, cut)
        for rule, takes in (("learned", d.offer_cut), ("all", True), ("none", False)):
            t = totals[rule]
            t["cut"] += takes
            t["supplier"] += _rule_value(row, takes, cut_cost=cut_cost, lifetime=lifetime)
            t["household"] += row["p_stay_treated"] * cut_cost if takes else 0.0
    n = len(fresh.rows)
    return {
        "margin_share": margin_share, "fresh_seed": fresh.seed, "fresh_decisions": n,
        "train_seed": train.seed, "train_per_arm": {"treated": pooled.treated, "holdout": pooled.held_out},
        "learned_pooled": {"effect": pooled.effect, "low": pooled.low, "high": pooled.high,
                           "verdict": pooled.verdict, "needed_per_arm": decisions_needed_per_arm(pooled)},
        "by_channel": {m: {"treated": e.treated, "held_out": e.held_out, "effect": e.effect,
                           "low": e.low, "high": e.high, "verdict": e.verdict}
                       for m, e in by_channel.items()},
        "reads": reads, "fresh_true_effect": fresh.true_effect,
        "rules": {k: {"cut_share": round(v["cut"] / n, 4),
                      "supplier_per_decision": round(v["supplier"] / n, 3),
                      "household_saving_per_decision": round(v["household"] / n, 3)}
                  for k, v in totals.items()},
    }


def decide(argv=None) -> int:
    ap = argparse.ArgumentParser(description="grade the learned retention decision against both flat rules")
    ap.add_argument("--arm", choices=("real", "null", "planted"), required=True)
    ap.add_argument("--train-seed", type=int, default=42)
    ap.add_argument("--fresh-seeds", type=int, nargs="+", default=[101])
    ap.add_argument("--cut", type=float, default=7.5)
    ap.add_argument("--planted", type=float, default=0.10)
    ap.add_argument("--train-per-year", type=float, default=4700.0)
    ap.add_argument("--fresh-per-year", type=float, default=850.0)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    from simulation.coin_drawn_decision_set import build_decision_set

    kw = {"real": dict(cut_gbp_per_mwh=args.cut), "null": dict(cut_gbp_per_mwh=0.0),
          "planted": dict(cut_gbp_per_mwh=0.0, planted_effect=args.planted)}[args.arm]
    train = build_decision_set(args.train_seed, acquisitions_per_year=args.train_per_year, **kw)
    out = []
    for seed in args.fresh_seeds:
        fresh = build_decision_set(seed, acquisitions_per_year=args.fresh_per_year, **kw)
        for g in MARGIN_SHARE_ENDS:
            row = {"arm": args.arm, **grade_decision(train, fresh, cut=args.cut, margin_share=g)}
            print(json.dumps(row), flush=True)
            out.append(row)
    args.out.write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


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
    import sys
    if sys.argv[1:2] == ["decide"]:
        raise SystemExit(decide(sys.argv[2:]))
    raise SystemExit(main())
