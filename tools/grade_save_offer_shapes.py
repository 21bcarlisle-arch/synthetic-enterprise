"""Grade three retention shapes -- a blanket renewal cut, a retention fix at term end, a reactive save
on the loss notice -- on the coin-drawn decision set, with the world deciding who is saved.

REUSE: tools/grade_save_offer_shapes.py
CLASS: CUSTOM
INDEX: searched "save offer", "loss notice", "retention fix", "shape". `tools/grade_coin_drawn_holdout.py`
       grades a LEARNED cut decision against cut-for-all and cut-for-none, and its margin and tenure
       arithmetic (`lifetime_value`, `cut_cost_gbp`, `MARGIN_SHARE_ENDS`) is REUSED here, not
       paralleled. What it cannot do is price a shape whose cost lands on a subset chosen by the
       household's own departure: that needs the world's P(stay) at several cuts per decision and
       the roll, which `simulation.coin_drawn_decision_set.build_decision_set(probe_cuts=...)` now
       keeps, and `saved_on_loss_notice` / `implied_save_rate`, which decide a save from the same
       roll and the same curve.

THE ASK (director, 2026-10-08): confirm the world's own price response decides who is saved, so a
published save rate checks the world instead of driving it; then show whether the answer changes
across the range, and name the number if it turns on one.

THE SHAPES, priced per decision at the world's own P(stay) (expected value, as the B8 grader does):
  never  P0*L. Also the existing best flat rule: B8 L2 found cut-for-none best at every cut size.
  A      blanket renewal cut, every renewing household: Pc*(L - cost). Cost lands on every stayer,
         including the P0 who would have stayed anyway.
  B      retention fix at term end, targeted by timing: as A for households on a fixed term ending,
         never-offer for deemed-contract (SVT) arrivals. IN THIS LEAN SET EVERY DECISION IS AN
         ANNIVERSARY, so timing does not separate B from A; what separates them is only who is
         eligible. A household that opened on a switch (`opened_on` None -- NOT established as
         fixed, see `population_draw._draw_tariff_type`) is taken to be on a fix that ends, and a
         stayer under B takes a new fix, so it is eligible again next year; a move-in on a deemed
         contract ("svt") never is.
  C      reactive save on the loss notice: P0*L + (Pc - P0)*(L - cost). Cost lands only on a
         household that was leaving and is saved.
L = `lifetime_value` (margin share of the household's own trailing bills over 1 + s/(1-s) years,
s = the TRAIN seed's observed stay share, a company observable); cost = one year of the cut on
billed kWh. Both margin ends (`MARGIN_SHARE_ENDS`, 0.019 and 0.14) are graded.

THE SENSITIVITY IS ON THE WORLD, LABELLED AS ONE, AND CHANGES NOTHING IN IT: the world's cut
effect Pc - P0 is scaled by k for every shape alike (a world that responds to price k times as
much), with k set so the pooled implied save rate at the chosen cut equals a target. The targets
0.013 and 0.041 are the brief's published-estimate figures; see the report for where they live.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

CUTS = (2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0)
#: The brief's published-estimate save rate and range (q4_save_rate_on_loss_notice, as given by
#: the delivery seat 2026-10-08). Swept as targets for the sensitivity, never fed to the world.
SAVE_RATE_TARGETS = (0.0, 0.013, 0.041)
PUBLISHED_RANGE = (0.0, 0.041)
SHAPES = ("never", "A_blanket", "B_term_end", "C_reactive")


def _scaled(p0: float, pc: float, k: float) -> float:
    return min(1.0, p0 + k * (pc - p0))


def world_save_rate(rows: list[dict], cut: float, k: float = 1.0) -> dict:
    """Expected saves per expected loss notice at `cut` (pooled), and the same counted on the
    world's own rolls: how many leavers at the default the cut keeps."""
    from simulation.coin_drawn_decision_set import implied_save_rate, saved_on_loss_notice

    usable = [r for r in rows if r["p_stay_at_cut"].get(cut) is not None]
    leave = sum(1.0 - r["p_stay_holdout"] for r in usable)
    gain = sum(_scaled(r["p_stay_holdout"], r["p_stay_at_cut"][cut], k) - r["p_stay_holdout"]
               for r in usable)
    leavers = [r for r in usable if r["roll"] > r["p_stay_holdout"]]
    saved = sum(saved_on_loss_notice(r["roll"], r["p_stay_holdout"],
                                     _scaled(r["p_stay_holdout"], r["p_stay_at_cut"][cut], k))
                for r in leavers)
    per_decision = [implied_save_rate(r["p_stay_holdout"], r["p_stay_at_cut"][cut]) for r in usable]
    return {"decisions": len(usable),
            "mean_p_stay_default": sum(r["p_stay_holdout"] for r in usable) / len(usable),
            "implied_save_rate": gain / leave if leave else 0.0,
            "mean_per_decision_save_rate": sum(per_decision) / len(per_decision),
            "leavers_rolled": len(leavers), "saved_rolled": saved,
            "realised_save_rate": saved / len(leavers) if leavers else 0.0}


def grade_shapes(rows: list[dict], *, cut: float, stay_share: float, margin_share: float,
                 k: float = 1.0) -> dict:
    """Mean supplier value per decision of each shape, its net against never-offer, the household
    saving, and the share of decisions each shape pays the cut on."""
    from company.interfaces.sim_interface import holdout_decision_observations
    from tools.grade_coin_drawn_holdout import cut_cost_gbp, lifetime_value

    tot = {s: {"value": 0.0, "household": 0.0, "paid": 0.0} for s in SHAPES}
    n = 0
    for row, obs in zip(rows, holdout_decision_observations(rows)):
        pc_world = row["p_stay_at_cut"].get(cut)
        if pc_world is None:
            continue
        n += 1
        p0 = row["p_stay_holdout"]
        pc = _scaled(p0, pc_world, k)
        life = lifetime_value(obs, stay_share=stay_share, margin_share=margin_share)
        cost = cut_cost_gbp(obs, cut)
        blanket = (pc * (life - cost), pc * cost, pc)
        never = (p0 * life, 0.0, 0.0)
        eligible = row.get("opened_on") != "svt"
        for shape, (v, h, paid) in (
                ("never", never), ("A_blanket", blanket),
                ("B_term_end", blanket if eligible else never),
                ("C_reactive", (p0 * life + (pc - p0) * (life - cost), (pc - p0) * cost, pc - p0))):
            tot[shape]["value"] += v
            tot[shape]["household"] += h
            tot[shape]["paid"] += paid
    base = tot["never"]["value"] / n
    return {s: {"value": t["value"] / n, "net_vs_never": t["value"] / n - base,
                "household_saving": t["household"] / n, "paid_share": t["paid"] / n}
            for s, t in tot.items()} | {"decisions": n}


def break_even_save_rate(rows: list[dict], *, cut: float, stay_share: float, margin_share: float,
                         eligible_only: bool = False) -> float | None:
    """The implied save rate at `cut` above which a cut paid on every stayer (A, or B with
    `eligible_only`) beats never-offering: k* = sum(P0*cost) / sum((Pc-P0)*(L-cost)), times the
    world's own rate. None where no k pays (the saved lifetimes do not cover the cut)."""
    from company.interfaces.sim_interface import holdout_decision_observations
    from tools.grade_coin_drawn_holdout import cut_cost_gbp, lifetime_value

    dead = gain = 0.0
    for row, obs in zip(rows, holdout_decision_observations(rows)):
        pc = row["p_stay_at_cut"].get(cut)
        if pc is None or (eligible_only and row.get("opened_on") == "svt"):
            continue
        life = lifetime_value(obs, stay_share=stay_share, margin_share=margin_share)
        cost = cut_cost_gbp(obs, cut)
        dead += row["p_stay_holdout"] * cost
        gain += (pc - row["p_stay_holdout"]) * (life - cost)
    if gain <= 0:
        return None
    return dead / gain * world_save_rate(rows, cut)["implied_save_rate"]


def _sd(xs: list[float]) -> float:
    return statistics.stdev(xs) if len(xs) > 1 else 0.0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--train-seed", type=int, default=42)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 101, 202])
    ap.add_argument("--per-year", type=float, default=1500.0)
    ap.add_argument("--cut", type=float, default=7.5, help="the cut the sensitivity is set at")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    from company.interfaces.sim_interface import holdout_decision_observations
    from simulation.coin_drawn_decision_set import build_decision_set
    from tools.grade_coin_drawn_holdout import MARGIN_SHARE_ENDS

    sets = {}
    for seed in args.seeds:
        s = build_decision_set(seed, cut_gbp_per_mwh=0.0, acquisitions_per_year=args.per_year,
                               probe_cuts=CUTS)
        sets[seed] = s.rows
        print(json.dumps({"seed": seed, "decisions": len(s.rows), "seconds": round(s.seconds, 1)}),
              flush=True)
    seen = holdout_decision_observations(sets[args.train_seed])
    stay_share = sum(o["stayed"] for o in seen) / len(seen)

    reality = []
    for cut in CUTS:
        per = [world_save_rate(sets[sd], cut) for sd in args.seeds]
        rate = [p["implied_save_rate"] for p in per]
        m = statistics.mean(rate)
        reality.append({
            "cut": cut, "p_stay_default": statistics.mean(p["mean_p_stay_default"] for p in per),
            "implied_save_rate": m, "sd": _sd(rate),
            "realised_save_rate": statistics.mean(p["realised_save_rate"] for p in per),
            "vs_published": ("inside" if PUBLISHED_RANGE[0] <= m <= PUBLISHED_RANGE[1]
                             else "above" if m > PUBLISHED_RANGE[1] else "below")})
    shapes = []
    for g in MARGIN_SHARE_ENDS:
        for target in (None,) + SAVE_RATE_TARGETS:
            cell = {"margin_share": g, "save_rate": "world" if target is None else target}
            per_seed = []
            for sd in args.seeds:
                world = world_save_rate(sets[sd], args.cut)["implied_save_rate"]
                k = 1.0 if target is None else target / world
                per_seed.append(grade_shapes(sets[sd], cut=args.cut, stay_share=stay_share,
                                             margin_share=g, k=k))
            for shape in SHAPES:
                nets = [p[shape]["net_vs_never"] for p in per_seed]
                cell[shape] = {"net_vs_never": statistics.mean(nets), "sd": _sd(nets),
                               "paid_share": statistics.mean(p[shape]["paid_share"] for p in per_seed),
                               "household_saving": statistics.mean(p[shape]["household_saving"]
                                                                   for p in per_seed)}
            cell["ranking"] = sorted(SHAPES, key=lambda sh: -cell[sh]["net_vs_never"])
            shapes.append(cell)
    breakeven = [{"cut": cut, "margin_share": g,
                  "A": [break_even_save_rate(sets[sd], cut=cut, stay_share=stay_share, margin_share=g)
                        for sd in args.seeds],
                  "B": [break_even_save_rate(sets[sd], cut=cut, stay_share=stay_share, margin_share=g,
                                             eligible_only=True) for sd in args.seeds]}
                 for cut in CUTS for g in MARGIN_SHARE_ENDS]
    out = {"args": {k: str(v) for k, v in vars(args).items()}, "train_stay_share": stay_share,
           "eligible_share_B": statistics.mean(
               sum(r.get("opened_on") != "svt" for r in sets[sd]) / len(sets[sd]) for sd in args.seeds),
           "reality_check": reality, "shapes": shapes, "break_even_save_rate": breakeven}
    args.out.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({"reality_check": reality}, indent=1))
    print(json.dumps({"shapes": shapes}, indent=1))
    print(json.dumps({"break_even": breakeven}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
