"""Grade P1-P4 of the acquisition-selection pre-registration on the funnel-sourced decision set.

REUSE: tools/grade_acquisition_selection.py
CLASS: CUSTOM
INDEX: searched "grade", "P1", "acquisition", "selection", "flat rule". `tools/grade_coin_drawn_holdout`
       grades the learned retention decision against both flat rules on the draw-sourced set; this
       REUSES its value terms (`lifetime_value`, `cut_cost_gbp`, `_rule_value`, `MARGIN_SHARE_ENDS`)
       and adds what that one cannot do: build the set from the campaign's winners under each
       switch setting (`simulation.coin_drawn_decision_set.build_funnel_decision_set`), group the
       read by the three save positions, and grade the pre-registered P1-P4.

THE TEST (`docs/staging/records/SEAT_PREREG_ACQUISITION_SELECTS_ON_EACH_PROSPECTS_OWN_RESPONSIVENESS_2026-10-08.md`),
as this file operationalises it, once per arm, observable and margin end:
  * P1 -- at least one group of the observable has its OWN read (enough decisions for the pooled
    effect) and the learned decision offers the cut on it.
  * P2 -- every cut the learned decision offers lands in such a group, and at least one group is
    offered nothing.
  * P3 -- on each fresh seed, the learned rule's supplier value per decision beats the better flat
    rule by more than two seed-noise SDs, the SD of that margin over the noise seeds.
  * P4 -- with option 1 OFF, the decision learned in that world offers no cut at all.

THE SWITCHES are set on a temporary copy of the curriculum file, never on the director's file: the
module global the readers default to is pointed at the copy for the life of the process.
"""
from __future__ import annotations

import argparse
import json
import statistics
import tempfile
from pathlib import Path

ARMS = {"off": (False, "independent"), "I": (True, "independent"), "L": (True, "linked")}


def set_switches(arm: str) -> None:
    """Point this process's acquisition-selection readers at a copy carrying `arm`'s switches."""
    import simulation.population_draw as pd

    on, level = ARMS[arm]
    src = json.loads(pd.ACQUISITION_RESPONSIVENESS_PATH.read_text(encoding="utf-8"))
    src["activated"]["value"] = on
    src["sensitivity_level_draw"]["value"] = level
    copy = Path(tempfile.mkdtemp(prefix="acq_switch_")) / f"{arm}.json"
    copy.write_text(json.dumps(src), encoding="utf-8")
    pd.ACQUISITION_RESPONSIVENESS_PATH = copy


def build(argv=None) -> int:
    """Build one arm's sets, one JSON file of rows per seed, for `grade` to read."""
    ap = argparse.ArgumentParser(description="build funnel-sourced decision sets for one arm")
    ap.add_argument("--arm", choices=tuple(ARMS), required=True)
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--cut", type=float, default=7.5)
    ap.add_argument("--dir", type=Path, required=True)
    args = ap.parse_args(argv)
    set_switches(args.arm)
    from simulation.coin_drawn_decision_set import build_funnel_decision_set

    args.dir.mkdir(parents=True, exist_ok=True)
    for seed in args.seeds:
        path = args.dir / f"{args.arm}_{seed}.json"
        if path.exists():
            continue
        s = build_funnel_decision_set(seed, cut_gbp_per_mwh=args.cut)
        path.write_text(json.dumps({"seed": seed, "households": s.households, "rows": s.rows}),
                        encoding="utf-8")
        print(args.arm, seed, s.households, len(s.rows), round(s.seconds, 1), flush=True)
    return 0


def _rows(d: Path, arm: str, seeds) -> dict[int, list]:
    return {s: json.loads((d / f"{arm}_{s}.json").read_text(encoding="utf-8"))["rows"] for s in seeds}


def rule_values(rows, decide, *, cut: float, margin_share: float, stay_share: float) -> dict:
    """Supplier value per decision under the learned rule and both flat rules, with the world's own
    P(stay) at each offer, and which groups the learned rule cut."""
    from company.interfaces.sim_interface import holdout_decision_observations
    from tools.grade_coin_drawn_holdout import _rule_value, cut_cost_gbp, lifetime_value

    totals = {"learned": 0.0, "all": 0.0, "none": 0.0}
    cut_n = 0
    for row, obs in zip(rows, holdout_decision_observations(rows)):
        d = decide(obs)
        lifetime = lifetime_value(obs, stay_share=stay_share, margin_share=margin_share)
        cost = cut_cost_gbp(obs, cut)
        cut_n += d.offer_cut
        for rule, takes in (("learned", d.offer_cut), ("all", True), ("none", False)):
            totals[rule] += _rule_value(row, takes, cut_cost=cost, lifetime=lifetime)
    n = len(rows)
    return {**{k: v / n for k, v in totals.items()}, "cut_share": cut_n / n, "decisions": n}


def grade_arm(d: Path, arm: str, *, train_seeds, fresh_seeds, noise_seeds, cut: float) -> list[dict]:
    from company.interfaces.sim_interface import holdout_decision_observations
    from company.pricing.discovered_price_sensitivity import (
        SAVE_POSITION_OBSERVABLES,
        decisions_needed_per_arm,
        estimate_offer_effect,
        estimate_offer_effect_by_position,
        position_group,
        retention_cut_decision,
    )
    from tools.grade_coin_drawn_holdout import MARGIN_SHARE_ENDS

    train = [r for rows in _rows(d, arm, train_seeds).values() for r in rows]
    fresh = _rows(d, arm, fresh_seeds)
    noise = _rows(d, arm, noise_seeds)
    seen = holdout_decision_observations(train)
    pooled = estimate_offer_effect(seen)
    need = decisions_needed_per_arm(pooled)
    stay_share = pooled.stayed_held_out / pooled.held_out
    out = []
    for observable in SAVE_POSITION_OBSERVABLES:
        by = estimate_offer_effect_by_position(seen, observable)
        for margin in MARGIN_SHARE_ENDS:
            def decide(obs, _by=by, _o=observable, _m=margin):
                return retention_cut_decision(obs, cut_gbp_per_mwh=cut, margin_share=_m,
                                              by_channel=_by, pooled=pooled, observable=_o)
            own = {g for g, e in by.items()
                   if need is not None and min(e.treated, e.held_out) >= need}
            cut_groups: dict[str, int] = {}
            for obs in holdout_decision_observations([r for rows in fresh.values() for r in rows]):
                if decide(obs).offer_cut:
                    g = position_group(obs, observable)
                    cut_groups[g] = cut_groups.get(g, 0) + 1
            margins = []
            for rows in noise.values():
                v = rule_values(rows, decide, cut=cut, margin_share=margin, stay_share=stay_share)
                margins.append(v["learned"] - max(v["all"], v["none"]))
            sd = statistics.stdev(margins) if len(margins) > 1 else None
            per_fresh = {}
            for seed, rows in fresh.items():
                v = rule_values(rows, decide, cut=cut, margin_share=margin, stay_share=stay_share)
                lead = v["learned"] - max(v["all"], v["none"])
                per_fresh[seed] = {**{k: round(x, 4) for k, x in v.items()}, "lead_over_best_flat": round(lead, 4),
                                   "beats_by_two_sd": sd is not None and lead > 2 * sd}
            p1 = any(g in own for g in cut_groups)
            p2 = p1 and set(cut_groups) <= own and len(cut_groups) < len(by)
            out.append({
                "arm": arm, "observable": observable, "margin_share": margin, "cut_per_mwh": cut,
                "train_decisions": len(train), "pooled": {"effect": pooled.effect, "low": pooled.low,
                                                          "high": pooled.high, "verdict": pooled.verdict,
                                                          "needed_per_arm": need},
                "groups": {g: {"treated": e.treated, "held_out": e.held_out, "effect": e.effect,
                               "low": e.low, "high": e.high, "verdict": e.verdict, "own_read": g in own}
                           for g, e in by.items()},
                "cut_offered_by_group_on_fresh": cut_groups,
                "seed_noise_sd_of_lead": sd and round(sd, 4), "noise_seeds": len(margins),
                "fresh": per_fresh,
                "P1": p1, "P2": p2, "P3": p2 and all(f["beats_by_two_sd"] for f in per_fresh.values()),
                "offers_nothing": not cut_groups,
            })
    return out


def grade(argv=None) -> int:
    ap = argparse.ArgumentParser(description="grade P1-P4 on built funnel-sourced sets")
    ap.add_argument("--dir", type=Path, required=True)
    ap.add_argument("--train-seeds", type=int, nargs="+", required=True)
    ap.add_argument("--fresh-seeds", type=int, nargs="+", default=[101, 202])
    ap.add_argument("--noise-seeds", type=int, nargs="+", required=True)
    ap.add_argument("--cut", type=float, default=7.5)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    result = {arm: grade_arm(args.dir, arm, train_seeds=args.train_seeds, fresh_seeds=args.fresh_seeds,
                             noise_seeds=args.noise_seeds, cut=args.cut) for arm in ARMS}
    for arm in ("I", "L"):
        for row in result[arm]:
            control = next(c for c in result["off"] if c["observable"] == row["observable"]
                           and c["margin_share"] == row["margin_share"])
            row["P4"] = control["offers_nothing"]
    args.out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    for arm in ("I", "L"):
        for r in result[arm]:
            print(arm, r["observable"], r["margin_share"], "P1", r["P1"], "P2", r["P2"], "P3", r["P3"],
                  "P4", r["P4"], "cut", r["cut_offered_by_group_on_fresh"])
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit((build if sys.argv[1:2] == ["build"] else grade)(sys.argv[2:]))
