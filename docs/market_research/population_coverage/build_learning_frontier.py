#!/usr/bin/env python3
"""
Stage-4 LEARNING-VALUE FRONTIER -- REFRAME per
DIRECTOR_STEER_SEGMENTATION_LEARNING_VALUE_REFRAME_2026-07-20.

Supersedes the OBJECTIVE of build_value_frontier.py (the population construction and the
outcome model are re-used UNCHANGED -- same physics, reframed metric, so the knee-delta is
clean). The director caught a conflation: the old frontier optimised VALUE OF THE CUSTOMER
(a signed £ business value in which bad debt was a value REDUCTION with a guessed 0.20 weight).
The reframed objective is VALUE OF MODELLING THE SEGMENT WELL -- information/learning value:
which segments teach the company the most.

Three data-derived criteria (values-call file: learning_value_model.json):
  1. CONSEQUENCE MAGNITUDE (unsigned, EITHER direction) -- bad debt RAISES stakes.
  2. LEARNING VALUE / VoI -- between-segment eta^2 of each STANDARDIZED outcome, equal weight
     (the ONE declared, sensitivity-tested choice replacing the four guessed weights).
  3. DISTINCTNESS -- marginal learning value given dims already chosen.

PROTECTION IS A FLOOR OUTSIDE THE RANKING: critical groups covered by carve-out construction,
never a term in the score (critical_group_bonus removed). No metric can demote a
regulatorily-significant group below full-fidelity modelling.

Analysis only. NO generator change (director-reserved wall). Deterministic; no network.
Reports how/why the value knee MOVED from the P&L-weighted version.
"""
import json, os, math
from collections import defaultdict

# Re-use the population construction + outcome model UNCHANGED (same physics, reframed metric).
from build_value_frontier import (
    build_population, outcomes, eta2, zstats, DIMS, CRIT,
    crit_membership, critical_coverage_from_seglabels,
    find_knee, labels_for, n_segments, business_value_vector, SEED, N_POP,
)

HERE = os.path.dirname(os.path.abspath(__file__))
def load(p): return json.load(open(os.path.join(HERE, p)))
LVM = load("learning_value_model.json")

OUTCOME_KEYS = LVM["aggregation"]["outcome_keys"]
# tilt entries only (skip the "_comment" documentation key)
SENS = {k: v for k, v in LVM["sensitivity_weightings"].items() if not k.startswith("_")}


def standardized_outcomes(pop):
    """z-score each raw outcome to unit variance (no signs -- variance-explained ignores sign)."""
    raw = [outcomes(h) for h in pop]
    z = {}
    for k in OUTCOME_KEYS:
        mu, sd = zstats([r[k] for r in raw])
        z[k] = [(r[k] - mu) / sd for r in raw]
    return raw, z


def consequence_vector(z):
    """Unsigned stakes in EITHER direction: quadrature over standardized outcomes.
    A household extreme on ANY outcome -- including bad debt -- is high-consequence."""
    n = len(z[OUTCOME_KEYS[0]])
    return [math.sqrt(sum(z[k][i] ** 2 for k in OUTCOME_KEYS)) for i in range(n)]


def learning_value(z, weights, labels, tilt=None):
    """Between-segment eta^2 per standardized outcome, aggregated by (optionally tilted) mean.
    tilt = per-outcome multiplier dict; None => equal (the declared default)."""
    per = {k: eta2(z[k], weights, labels) for k in OUTCOME_KEYS}
    if tilt is None:
        agg = sum(per.values()) / len(per)
    else:
        num = sum(tilt[k] * per[k] for k in OUTCOME_KEYS)
        den = sum(tilt[k] for k in OUTCOME_KEYS)
        agg = num / den if den else 0.0
    return agg, per


def main_effect_lv(z, weights, pop, tilt=None):
    """One-way learning value of each dimension alone (the ranking table)."""
    out = {}
    for d in DIMS:
        agg, per = learning_value(z, weights, [h[d] for h in pop], tilt)
        out[d] = {"learning_value": round(agg, 4),
                  "per_outcome_eta2": {k: round(v, 4) for k, v in per.items()}}
    return out


def greedy_distinctness_curve(z, weights, pop, crit_tags, cons):
    """Nested curve: at each step add the dimension with the highest MARGINAL learning value
    given those already chosen (encodes distinctness / 'not predictable from the others').
    Reports learning value, per-outcome eta^2, consequence-tail capture, and critical coverage."""
    used, remaining = [], list(DIMS)
    lab0 = [() for _ in pop]
    agg0, per0 = learning_value(z, weights, lab0)
    cc0, _ = critical_coverage_from_seglabels(lab0, crit_tags)
    curve = [{"step": 0, "added_dim": None, "dims": [], "segments": 1,
              "learning_value": round(agg0, 4), "marginal_lv": 0.0,
              "per_outcome_eta2": {k: round(v, 4) for k, v in per0.items()},
              "consequence_eta2": round(eta2(cons, weights, lab0), 4),
              "critical_coverage": round(cc0, 4)}]
    prev = agg0
    while remaining:
        best = None
        for d in remaining:
            lab = labels_for(pop, used + [d])
            agg, per = learning_value(z, weights, lab)
            if best is None or agg > best[0]:
                best = (agg, d, per, lab)
        agg, d, per, lab = best
        used.append(d); remaining.remove(d)
        cc, _ = critical_coverage_from_seglabels(lab, crit_tags)
        curve.append({"step": len(used), "added_dim": d, "dims": list(used),
                      "segments": n_segments(lab), "learning_value": round(agg, 4),
                      "marginal_lv": round(agg - prev, 4),
                      "per_outcome_eta2": {k: round(v, 4) for k, v in per.items()},
                      "consequence_eta2": round(eta2(cons, weights, lab), 4),
                      "critical_coverage": round(cc, 4)})
        prev = agg
    return curve


def old_signed_curve(pop, weights, crit_tags):
    """Recompute the WITHDRAWN P&L-signed objective's greedy curve, so we can report how the
    knee MOVED. Uses business_value_vector (the old fixed weights) unchanged."""
    bv, _ = business_value_vector(pop)
    main = {d: eta2(bv, weights, [h[d] for h in pop]) for d in DIMS}
    order = sorted(DIMS, key=lambda d: (main[d], d), reverse=True)
    curve = [{"step": 0, "dims": [], "segments": 1, "variance_captured": round(eta2(bv, weights, [() for _ in pop]), 4)}]
    used = []
    for i, d in enumerate(order):
        used.append(d)
        lab = labels_for(pop, used)
        curve.append({"step": i + 1, "added_dim": d, "dims": list(used),
                      "segments": n_segments(lab),
                      "variance_captured": round(eta2(bv, weights, lab), 4)})
    return order, main, curve


def hybrid_design(pop, z, weights, crit_tags, core_dims, mode):
    """Learning-value core + PROTECTED carve-outs (the floor outside the ranking).
    overlay = protected households pulled into a cross-cutting group-segment (PSR/fuel-poor list);
    intersect = protected carved within each core cell. Same structure as the old build; the CORE
    is now chosen by learning value, and the carve-out is a floor, not a scored bonus."""
    base = labels_for(pop, core_dims)
    lab = []
    for h, bl in zip(pop, base):
        tags = tuple(sorted(crit_membership(h)))
        if mode == "overlay":
            lab.append(("CRIT", tags) if tags else ("CORE", bl))
        else:
            lab.append((bl, tags if tags else None))
    agg, per = learning_value(z, weights, lab)
    cc, pergrp = critical_coverage_from_seglabels(lab, crit_tags)
    return {"core_dims": list(core_dims), "mode": mode, "segments": n_segments(lab),
            "learning_value": round(agg, 4), "per_outcome_eta2": {k: round(v, 4) for k, v in per.items()},
            "critical_coverage": round(cc, 4),
            "per_group_coverage": {k: round(v, 3) for k, v in pergrp.items()}}


def main():
    pop = build_population()
    weights = [1.0] * len(pop)
    raw, z = standardized_outcomes(pop)
    cons = consequence_vector(z)
    crit_tags = [crit_membership(h) for h in pop]

    # ---- ranking: one-way learning value per dimension (default + sensitivity tilts) ----
    me_default = main_effect_lv(z, weights, pop)
    ranking = sorted(DIMS, key=lambda d: (me_default[d]["learning_value"], d), reverse=True)
    me_tilts = {name: sorted(DIMS, key=lambda d: (main_effect_lv(z, weights, pop, tilt)[d]["learning_value"], d), reverse=True)[:4]
                for name, tilt in SENS.items()}

    # ---- the reframed frontier: greedy-by-distinctness nested curve + its knee ----
    curve = greedy_distinctness_curve(z, weights, pop, crit_tags, cons)
    knee_seg = find_knee(curve, "segments", "learning_value")
    knee_step = find_knee(curve, "step", "learning_value")

    # ---- the delta: how the knee MOVED vs the withdrawn P&L-signed objective ----
    old_order, old_main, old_curve = old_signed_curve(pop, weights, crit_tags)
    old_knee = find_knee(old_curve, "segments", "variance_captured")

    # ---- consequence tail: does the reframed core isolate the high-stakes (incl. arrears) tail ----
    order_c = sorted(range(len(cons)), key=lambda i: cons[i], reverse=True)
    top10 = set(order_c[: len(cons) // 10])
    # per-critical-group mean consequence vs population (evidence bad debt now raises priority)
    grp_cons = {}
    for g in CRIT:
        idx = [i for i, tags in enumerate(crit_tags) if g["id"] in tags]
        if idx:
            grp_cons[g["id"]] = {"mean_consequence": round(sum(cons[i] for i in idx) / len(idx), 3),
                                 "share_in_top_decile": round(sum(1 for i in idx if i in top10) / len(idx), 3),
                                 "n": len(idx)}
    pop_mean_cons = round(sum(cons) / len(cons), 3)

    # ---- hybrid recommended designs (LV core + protected floor) ----
    lv_core = [d for d in ranking[:2]]      # the two leading learning-value dims
    hybrids = {
        "lvcore2_OVERLAY": hybrid_design(pop, z, weights, crit_tags, lv_core, "overlay"),
        "lvcore3_OVERLAY": hybrid_design(pop, z, weights, crit_tags, ranking[:3], "overlay"),
        "lvcore2_INTERSECT": hybrid_design(pop, z, weights, crit_tags, lv_core, "intersect"),
    }

    # ---- sensitivity of the leading dims + knee under each outcome tilt ----
    tilt_frontiers = {}
    for name, tilt in SENS.items():
        c = []
        used = []
        c.append({"segments": 1, "learning_value": 0.0})
        # nested in the DEFAULT distinctness order, re-scored under this tilt (isolates weighting effect)
        order_here = [step["added_dim"] for step in curve[1:]]
        for d in order_here:
            used.append(d)
            agg, _ = learning_value(z, weights, labels_for(pop, used), tilt)
            c.append({"segments": n_segments(labels_for(pop, used)), "learning_value": round(agg, 4)})
        tilt_frontiers[name] = {"leading_dims": me_tilts[name],
                                "knee": find_knee(c, "segments", "learning_value")}

    out = {
        "_meta": {
            "artefact": "learning_value_frontier",
            "track": "DIRECTOR_STEER_SEGMENTATION_LEARNING_VALUE_REFRAME_2026-07-20",
            "supersedes": "value_frontier.json (the P&L-weighted objective)",
            "stage": "4 REFRAMED -- learning/information value, data-guided, protection as a floor. DISCOVER/FRAME, analysis only, NO generator change.",
            "created": "2026-07-20",
            "objective": "LEARNING value: which segments teach the company most. eta^2 of each standardized outcome (VoI), equal weight (the ONE declared choice), bad debt a POSITIVE learning signal, protection a floor OUTSIDE the ranking.",
            "population": {"n_households_sampled": N_POP, "seed": SEED,
                           "representativeness": "POPULATION-REPRESENTATIVE (volume-weighted), same joint structure as build_value_frontier.py -- construction re-used unchanged."},
            "determinism": "fixed seed %d, sorted iteration; no microdata; no network." % SEED,
            "anti_goal_seek": "R12: outcomes are diagnostics used to RANK by learning value, never targets.",
        },
        "reframe_note": "Bad debt was a value REDUCTION in value_frontier.json; here its VARIANCE is a positive learning signal and its MAGNITUDE raises consequence. The four fixed weights are withdrawn; ranking is data-derived (measured eta^2). critical_group_bonus removed -- protection is a carve-out floor.",
        "dimension_ranking_by_learning_value": {d: me_default[d] for d in ranking},
        "learning_value_frontier_curve": curve,
        "value_knee_reframed": {"by_segment_count": knee_seg, "by_dimension_count": knee_step,
            "reading": "segments where the next dimension buys almost no additional learning value."},
        "knee_delta_vs_pnl_signed": {
            "old_objective": "signed business_value (margin+0.40, retention-0.25, bad_debt-0.20, carbon+0.15) -- WITHDRAWN",
            "old_leading_dims": old_order[:3], "old_knee": old_knee,
            "new_leading_dims": ranking[:3], "new_knee_by_segments": knee_seg,
            "how_to_read": "Compare old_leading_dims vs new_leading_dims and the two knees. A rise of bad-debt-bearing dimensions (nssec, tenure, heating_fuel, channel_pref) in the new ranking is the reframe working: segments where arrears varies are now high-learning-value rather than low-value.",
        },
        "consequence_tail": {
            "note": "Bad debt now RAISES priority: protected/affordability groups should sit ABOVE population-mean consequence and be over-represented in the high-stakes tail -- the inverted-bell-curve thesis made measurable.",
            "population_mean_consequence": pop_mean_cons,
            "per_critical_group": grp_cons,
        },
        "hybrid_recommended_designs": {
            "principle": "Learning-value core (the two-to-three leading dims) PLUS protected carve-outs. The carve-out is a FLOOR outside the ranking, not a scored bonus. Two objectives still do NOT co-move -- variance/learning is bought by coarse main-effect splits; protection by targeted conjunctive carves.",
            "designs": hybrids,
        },
        "sensitivity_to_the_declared_choice": {
            "note": "Rebuild the frontier under each outcome-importance tilt. If the same 1-2 dims lead and the knee holds under all tilts, the reframed knee is robust to the one declared choice and only the fine ordering past the knee is tilt-dependent.",
            "results": tilt_frontiers,
        },
        "protection_floor": {
            "principle": "No metric -- learning value included -- can demote a regulatorily-significant group below full-fidelity modelling. Protected set = critical_groups.json, covered by carve-out construction. Director invited it to WIDEN.",
            "critical_group_bonus_status": "REMOVED from the ranking (was 0.05 in value_outcome_model.json).",
        },
    }
    with open(os.path.join(HERE, "learning_value_frontier.json"), "w") as f:
        json.dump(out, f, indent=2)

    print("=== DIMENSION RANKING by learning value (default equal-standardized) ===")
    for d in ranking:
        m = me_default[d]
        print(f"  {d:<17} LV={m['learning_value']:.3f}  per-outcome={m['per_outcome_eta2']}")
    print("\n=== REFRAMED FRONTIER (greedy by distinctness) ===")
    for c in curve:
        print(f"  step{c['step']:>2} +{str(c['added_dim']):<17} segs={c['segments']:>6} "
              f"LV={c['learning_value']:.3f} dLV={c['marginal_lv']:+.3f} "
              f"consEta2={c['consequence_eta2']:.3f} crit={c['critical_coverage']:.3f}")
    print("\n=== VALUE KNEE (reframed) ===")
    print("  by segments:", knee_seg)
    print("  by dim-count:", knee_step)
    print("\n=== KNEE DELTA vs withdrawn P&L-signed objective ===")
    print("  OLD leading dims:", old_order[:3], "OLD knee:", old_knee)
    print("  NEW leading dims:", ranking[:3], "NEW knee:", knee_seg)
    print("\n=== CONSEQUENCE TAIL (bad debt raises priority) ===")
    print("  pop mean consequence:", pop_mean_cons)
    for gid, s in grp_cons.items():
        print(f"  {gid:<24} mean_cons={s['mean_consequence']:.3f} top-decile-share={s['share_in_top_decile']:.3f} n={s['n']}")
    print("\n=== HYBRID (LV core + protected floor) ===")
    for k, v in hybrids.items():
        print(f"  {k}: segs={v['segments']} LV={v['learning_value']} crit={v['critical_coverage']}")
    print("\n=== SENSITIVITY to the declared choice ===")
    for name, r in tilt_frontiers.items():
        print(f"  {name:<14} lead={r['leading_dims']} knee={r['knee']}")


if __name__ == "__main__":
    main()
