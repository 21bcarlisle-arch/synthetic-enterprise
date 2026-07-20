#!/usr/bin/env python3
"""
Stage-4 VALUE FRONTIER builder (DISCOVER/FRAME; analysis only, NO generator change).

Question shift: stage-3 answered COVERAGE (does every important cell appear? -> N=200 knee).
This answers VALUE (is each SEGMENT worth having?). We build the curve of
   (valuable variance captured) + (critical-group coverage)   vs   segment count
and report its KNEE -- the "value knee", distinct from the N=200 coverage knee.

Two objectives kept DELIBERATELY SEPARATE (a blended metric hides the trade):
  1. VALUABLE VARIANCE  -- volume-weighted between-segment variance of an asserted
     business-value outcome (eta^2 / R^2). Large groups behaving distinctly.
  2. CRITICAL SMALL GROUPS -- protected set, covered regardless of size.

Two constructors that should land on the SAME frontier (director's request to show convergence):
  A. VARIANCE-GREEDY (worst-cell-greedy analogue): greedily split the (segment x dimension)
     that buys the most marginal valuable variance, with a bonus for isolating an
     uncovered critical group.
  B. MODAL-OUTWARD: order dimensions by their main-effect variance share (one-way eta^2)
     and expand outward from the modal customer; segment counts are the running products.

Population is POPULATION-REPRESENTATIVE (volume weights) -- distinct from stage-3's
worst-cell cohorts (see stage-3 doc section 6). Built from the committed stage-2 marginals
+ crosstabs with the SAME joint structure as stage-3 (tenure spine block; fuel pinned to region).

Deterministic: fixed seed, sorted iteration. No microdata. No network.

TWO VALUES-CALLS are read from committed sidecar files (proposed ASSERTED, director changes them):
  value_outcome_model.json  -- (a) what makes variance 'valuable' (outcome effects + weighting)
  critical_groups.json      -- (b) what makes a group 'critical' (protected-set criteria)
"""
import json, os, math, random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
def load(p): return json.load(open(os.path.join(HERE, p)))
MARG = load("marginals.json")
XT = load("crosstabs.json")

SEED = 20260720
N_POP = 60000

NSSEC_BAND = {
    "L1, L2 and L3: Higher managerial, administrative and professional occupations": "higher",
    "L4, L5 and L6: Lower managerial, administrative and professional occupations": "intermediate",
    "L7: Intermediate occupations": "intermediate",
    "L8 and L9: Small employers and own account workers": "intermediate",
    "L10 and L11: Lower supervisory and technical occupations": "routine_semi",
    "L12: Semi-routine occupations": "routine_semi",
    "L13: Routine occupations": "routine_semi",
    "L14.1 and L14.2: Never worked and long-term unemployed": "unemployed_student",
    "L15: Full-time students": "unemployed_student",
}
FUEL_BAND = {
    "Mains gas only": "mains_gas",
    "Two or more types of central heating (not including renewable energy)": "mixed",
    "Two or more types of central heating (including renewable energy)": "mixed",
    "Electric only": "electric",
    "Oil only": "oil",
    "Tank or bottled gas only": "lpg_bottled",
    "District or communal heat networks only": "heat_network",
    "Other central heating only": "other_offgas",
    "Renewable energy only": "other_offgas",
    "Solid fuel only": "other_offgas",
    "Wood only": "other_offgas",
    "No central heating": "other_offgas",
}
TEN_BAND = {
    "Owned: Owns outright": "own_outright",
    "Owned: Owns with a mortgage or loan or shared ownership": "own_mortgage",
    "Rented: Private rented or lives rent free": "private_rent",
    "Rented: Social rented": "social_rent",
}
ACC_BAND = {
    "Whole house or bungalow: Detached": "detached",
    "Whole house or bungalow: Semi-detached": "semi",
    "Whole house or bungalow: Terraced": "terraced",
    "Flat, maisonette or apartment": "flat",
    "A caravan or other mobile or temporary structure": "caravan",
}
CARS_BAND = {"No cars or vans in household": "0", "1 car or van in household": "1",
             "2 or more cars or vans in household": "2plus"}

def norm(d):
    s = float(sum(d.values()))
    return {k: v / s for k, v in d.items()} if s else d

P_tenure = norm({TEN_BAND[k]: v["share"] for k, v in MARG["tenure"]["levels"].items()})
P_region = norm({k: v["share"] for k, v in MARG["region"]["levels"].items()})
P_accom_m = defaultdict(float)
for k, v in MARG["accommodation_type"]["levels"].items():
    P_accom_m[ACC_BAND[k]] += v["share"]
P_accom_m = norm(P_accom_m)
P_fuel_m = defaultdict(float)
for k, v in MARG["heating_fuel_type"]["levels"].items():
    P_fuel_m[FUEL_BAND[k]] += v["share"]
P_fuel_m = norm(P_fuel_m)

# accom_x_tenure: rows=accom, cols=tenure, value=P(tenure|accom) -> Bayes P(accom|tenure)
acc_x = XT["accom_x_tenure"]["table"]
P_accom_given_tenure = {t: defaultdict(float) for t in P_tenure}
for accom_raw, row in acc_x.items():
    a = ACC_BAND[accom_raw]
    for ten_raw, p_t_given_a in row.items():
        t = TEN_BAND[ten_raw]
        P_accom_given_tenure[t][a] += p_t_given_a * P_accom_m[a]
P_accom_given_tenure = {t: norm(dict(d)) for t, d in P_accom_given_tenure.items()}

P_cars_given_tenure = {}
for ten_raw, row in XT["tenure_x_cars"]["table"].items():
    P_cars_given_tenure[TEN_BAND[ten_raw]] = norm({CARS_BAND[c]: p for c, p in row.items()})

P_nssec_given_tenure = {}
for ten_raw, row in XT["tenure_x_nssec"]["table"].items():
    banded = defaultdict(float)
    for ns_raw, p in row.items():
        banded[NSSEC_BAND[ns_raw]] += p
    P_nssec_given_tenure[TEN_BAND[ten_raw]] = norm(dict(banded))

# heatingfuel_x_region: rows=fuel, cols=region, value=P(region|fuel) -> Bayes+band P(fuel|region)
fr = XT["heatingfuel_x_region"]["table"]
P_fuel_given_region = {r: defaultdict(float) for r in P_region}
for fuel_raw, row in fr.items():
    f = FUEL_BAND[fuel_raw]
    p_fuel_raw = MARG["heating_fuel_type"]["levels"][fuel_raw]["share"]
    for reg, p_reg_given_fuel in row.items():
        P_fuel_given_region[reg][f] += p_reg_given_fuel * p_fuel_raw
P_fuel_given_region = {r: norm(dict(d)) for r, d in P_fuel_given_region.items()}

# D/E 'assumed' dims: national marginal rates, crossed (asserted priors)
P_green = {"engaged": 0.30, "neutral": 0.45, "disengaged": 0.25}
P_price = {"high": 0.35, "medium": 0.45, "low": 0.20}
P_channel = {"digital": 0.55, "phone": 0.30, "assisted": 0.15}
P_solar = {"yes": 0.055, "no": 0.945}
P_ev = {"yes": 0.052, "no": 0.948}
P_batt = {"yes": 0.012, "no": 0.988}

def draw(rng, dist):
    r = rng.random(); c = 0.0
    for k in sorted(dist):
        c += dist[k]
        if r <= c: return k
    return sorted(dist)[-1]

def build_population():
    rng = random.Random(SEED)
    pop = []
    for _ in range(N_POP):
        t = draw(rng, P_tenure)
        h = {
            "tenure": t,
            "accommodation": draw(rng, P_accom_given_tenure[t]),
            "cars": draw(rng, P_cars_given_tenure[t]),
            "nssec": draw(rng, P_nssec_given_tenure[t]),
            "region": None, "heating_fuel": None,
            "green_stance": draw(rng, P_green),
            "price_sensitivity": draw(rng, P_price),
            "channel_pref": draw(rng, P_channel),
            "solar_PV": draw(rng, P_solar),
            "EV": draw(rng, P_ev),
            "home_battery": draw(rng, P_batt),
        }
        r = draw(rng, P_region); h["region"] = r
        h["heating_fuel"] = draw(rng, P_fuel_given_region[r])
        pop.append(h)
    return pop

OUTCOME = load("value_outcome_model.json")
EFF = OUTCOME["effects"]; BASE = OUTCOME["base"]; WEIGHTS = OUTCOME["business_value_weighting"]
SCC = OUTCOME["params"]["social_cost_of_carbon_gbp_per_t"]
CAC = OUTCOME["params"]["reacquisition_cost_gbp"]
CRIT_W = OUTCOME["params"]["critical_group_bonus"]

def eff(name, factor, level): return EFF.get(name, {}).get(factor, {}).get(level, 0.0)
def factors(name): return [f for f in EFF[name] if not f.startswith("_")]

def outcomes(h):
    margin = BASE["margin_gbp"] + sum(eff("margin_gbp", f, h[f]) for f in factors("margin_gbp"))
    churn_p = BASE["churn_prob"] + sum(eff("churn_prob", f, h[f]) for f in factors("churn_prob"))
    churn_p = min(0.85, max(0.01, churn_p))
    carbon_t = BASE["carbon_abatable_t"] + sum(eff("carbon_abatable_t", f, h[f]) for f in factors("carbon_abatable_t"))
    carbon_t = max(0.0, carbon_t)
    baddebt = BASE["baddebt_gbp"] + sum(eff("baddebt_gbp", f, h[f]) for f in factors("baddebt_gbp"))
    baddebt = max(0.0, baddebt)
    churn_cost = churn_p * (CAC + max(0.0, margin))
    carbon_value = carbon_t * SCC
    return {"margin": margin, "churn_cost": churn_cost, "baddebt": baddebt, "carbon_value": carbon_value}

def zstats(vals):
    n = len(vals); mu = sum(vals) / n
    var = sum((v - mu) ** 2 for v in vals) / n
    return mu, (math.sqrt(var) if var > 0 else 1.0)

def business_value_vector(pop):
    raw = [outcomes(h) for h in pop]
    comps = {}
    for key, sign in [("margin", +1), ("churn_cost", -1), ("baddebt", -1), ("carbon_value", +1)]:
        mu, sd = zstats([r[key] for r in raw])
        comps[key] = [sign * (r[key] - mu) / sd for r in raw]
    w = WEIGHTS
    bv = [w["margin"] * comps["margin"][i] + w["retention"] * comps["churn_cost"][i]
          + w["bad_debt"] * comps["baddebt"][i] + w["carbon"] * comps["carbon_value"][i]
          for i in range(len(pop))]
    return bv, raw

CRITJSON = load("critical_groups.json")
CRIT = CRITJSON["groups"]
CRIT_PURITY = CRITJSON["purity_threshold"]

def crit_membership(h):
    return [g["id"] for g in CRIT if all(h.get(k) in vs for k, vs in g["predicate"].items())]

DIMS = ["tenure", "accommodation", "cars", "nssec", "heating_fuel", "region",
        "green_stance", "price_sensitivity", "channel_pref", "solar_PV", "EV", "home_battery"]

def eta2(bv, weights, labels):
    tot_w = sum(weights)
    mu = sum(b * w for b, w in zip(bv, weights)) / tot_w
    tot_var = sum(w * (b - mu) ** 2 for b, w in zip(bv, weights)) / tot_w
    grp_sum = defaultdict(float); grp_w = defaultdict(float)
    for b, w, l in zip(bv, weights, labels):
        grp_sum[l] += b * w; grp_w[l] += w
    between = sum(grp_w[l] * (grp_sum[l] / grp_w[l] - mu) ** 2 for l in grp_w) / tot_w
    return between / tot_var if tot_var > 0 else 0.0

def labels_for(pop, dims): return [tuple(h[d] for d in dims) for h in pop]
def n_segments(labels): return len(set(labels))

def critical_coverage_from_seglabels(seglabels, crit_tags):
    seg_tags = defaultdict(list)
    for l, tags in zip(seglabels, crit_tags):
        seg_tags[l].append(tags)
    all_gids = [g["id"] for g in CRIT]
    total = 0.0
    per = {}
    for gid in all_gids:
        segs = [l for l, ms in seg_tags.items() if any(gid in m for m in ms)]
        if not segs:
            per[gid] = 1.0; total += 1.0; continue
        tot = 0; hit = 0
        for l in segs:
            ms = seg_tags[l]; tot += len(ms); hit += sum(1 for m in ms if gid in m)
        purity = hit / tot
        c = 1.0 if purity >= CRIT_PURITY else purity / CRIT_PURITY
        per[gid] = c; total += c
    return total / len(all_gids), per

def constructor_modal_outward(pop, bv, weights, crit_tags):
    main = {d: eta2(bv, weights, [h[d] for h in pop]) for d in DIMS}
    order = sorted(DIMS, key=lambda d: (main[d], d), reverse=True)
    modal = {}
    for d in DIMS:
        cnt = defaultdict(float)
        for h, w in zip(pop, weights): cnt[h[d]] += w
        modal[d] = max(sorted(cnt), key=lambda k: cnt[k])
    curve = []
    lab0 = [() for _ in pop]
    cc0, _ = critical_coverage_from_seglabels(lab0, crit_tags)
    curve.append({"step": 0, "added_dim": None, "dims": [], "segments": 1,
                  "variance_captured": round(eta2(bv, weights, lab0), 4),
                  "critical_coverage": round(cc0, 4)})
    used = []
    for i, d in enumerate(order):
        used.append(d)
        lab = labels_for(pop, used)
        cc, _ = critical_coverage_from_seglabels(lab, crit_tags)
        curve.append({"step": i + 1, "added_dim": d, "dims": list(used),
                      "segments": n_segments(lab), "main_effect_eta2": round(main[d], 4),
                      "variance_captured": round(eta2(bv, weights, lab), 4),
                      "critical_coverage": round(cc, 4)})
    return {"modal_customer": modal, "dim_order": order,
            "main_effects": {k: round(v, 4) for k, v in main.items()}, "curve": curve}

def constructor_variance_greedy(pop, bv, weights, crit_tags, max_leaves=48):
    n = len(pop)
    leaves = [list(range(n))]
    tot_w = sum(weights)
    mu_all = sum(bv[i] * weights[i] for i in range(n)) / tot_w
    tot_var = sum(weights[i] * (bv[i] - mu_all) ** 2 for i in range(n)) / tot_w

    def between_term(idxs):
        w = sum(weights[i] for i in idxs)
        if w == 0: return 0.0, 0.0
        m = sum(bv[i] * weights[i] for i in idxs) / w
        return w, m

    def split_children(leaf, d):
        groups = defaultdict(list)
        for i in leaf: groups[pop[i][d]].append(i)
        return [groups[k] for k in sorted(groups)]

    def split_gain(leaf, d):
        children = split_children(leaf, d)
        if len(children) < 2: return None, None
        w_leaf, m_leaf = between_term(leaf)
        parent = w_leaf * (m_leaf - mu_all) ** 2
        child = 0.0
        for g in children:
            wg, mg = between_term(g); child += wg * (mg - mu_all) ** 2
        return (child - parent) / tot_var, children

    def seglabels(part):
        lab = [0] * n
        for li, leaf in enumerate(part):
            for i in leaf: lab[i] = li
        return lab

    cc, _ = critical_coverage_from_seglabels(seglabels(leaves), crit_tags)
    curve = [{"leaves": 1, "split": None, "variance_captured": round(eta2(bv, weights, seglabels(leaves)), 4),
              "critical_coverage": round(cc, 4)}]
    while len(leaves) < max_leaves:
        best = None
        for li, leaf in enumerate(leaves):
            for d in DIMS:
                g, children = split_gain(leaf, d)
                if g is None: continue
                trial = leaves[:li] + children + leaves[li + 1:]
                cc_trial, _ = critical_coverage_from_seglabels(seglabels(trial), crit_tags)
                score = g + CRIT_W * max(0.0, cc_trial - cc)
                if best is None or score > best[0]:
                    best = (score, li, d, g, cc_trial, trial)
        if best is None or best[0] <= 1e-9: break
        _, li, d, g, cc, trial = best
        leaves = trial
        curve.append({"leaves": len(leaves), "split": d, "marginal_variance": round(g, 4),
                      "variance_captured": round(eta2(bv, weights, seglabels(leaves)), 4),
                      "critical_coverage": round(cc, 4)})
    return {"curve": curve}

def find_knee(curve, xkey, ykey):
    pts = [(c[xkey], c[ykey]) for c in curve]
    x0, y0 = pts[0]; x1, y1 = pts[-1]
    if x1 == x0: return {"segment_count": x0, "value_at_knee": round(y0, 4), "gap_above_chord": 0.0}
    best = None
    for x, y in pts:
        nx = (x - x0) / (x1 - x0)
        d = y - (y0 + (y1 - y0) * nx)
        if best is None or d > best[0]: best = (d, x, y)
    return {"segment_count": best[1], "value_at_knee": round(best[2], 4),
            "gap_above_chord": round(best[0], 4)}

def main():
    pop = build_population()
    weights = [1.0] * len(pop)
    bv, raw = business_value_vector(pop)
    crit_tags = [crit_membership(h) for h in pop]
    prevalence = defaultdict(int)
    for tags in crit_tags:
        for t in tags: prevalence[t] += 1

    B = constructor_modal_outward(pop, bv, weights, crit_tags)
    A = constructor_variance_greedy(pop, bv, weights, crit_tags, max_leaves=48)

    # ---- HYBRID DESIGN: the recommended answer ----------------------------------------
    # variance core (the value knee) + targeted critical-group carve-outs (protect the tail
    # regardless of size, the way stage-3 carved its named worst cells). This is the honest
    # minimum-segment design because the two objectives DON'T co-move: variance is bought by a
    # few coarse main-effect splits; critical protection is bought by specific conjunctive carves.
    def hybrid_design(core_dims, mode):
        base = labels_for(pop, core_dims)               # variance core cells
        lab = []
        for h, bl in zip(pop, base):
            tags = tuple(sorted(crit_membership(h)))
            if mode == "overlay":
                # protected households pulled OUT into a single cross-cutting group-segment
                # (as a real supplier runs a PSR/fuel-poor list): minimum segments.
                lab.append(("CRIT", tags) if tags else ("CORE", bl))
            else:  # intersect: carve within each commercial cell
                lab.append((bl, tags if tags else None))
        vc = eta2(bv, weights, lab)
        cc, per = critical_coverage_from_seglabels(lab, crit_tags)
        return {"core_dims": list(core_dims), "mode": mode, "segments": n_segments(lab),
                "variance_captured": round(vc, 4), "critical_coverage": round(cc, 4),
                "per_group_coverage": {k: round(v, 3) for k, v in per.items()}}
    hybrids = {
        "price_x_tenure_OVERLAY": hybrid_design(["price_sensitivity", "tenure"], "overlay"),
        "price_x_tenure_x_nssec_OVERLAY": hybrid_design(["price_sensitivity", "tenure", "nssec"], "overlay"),
        "price_x_tenure_INTERSECT": hybrid_design(["price_sensitivity", "tenure"], "intersect"),
        "price_x_tenure_x_fuel_INTERSECT": hybrid_design(["price_sensitivity", "tenure", "heating_fuel"], "intersect"),
    }
    for c in A["curve"]: c["value_combined"] = round(c["variance_captured"] + c["critical_coverage"], 4)
    for c in B["curve"]: c["value_combined"] = round(c["variance_captured"] + c["critical_coverage"], 4)

    # ---- robustness of the knee under the two ALTERNATIVE weightings (values-call (a)) ----
    alt = OUTCOME["business_value_weighting"]["alternative_weightings_offered"]
    robustness = {}
    for name, w in [("default", WEIGHTS)] + list(alt.items()):
        wmap = {"margin": w["margin"], "retention": w["retention"],
                "bad_debt": w["bad_debt"], "carbon": w["carbon"]}
        comps = {}
        for key, sign in [("margin", +1), ("churn_cost", -1), ("baddebt", -1), ("carbon_value", +1)]:
            mu, sd = zstats([r[key] for r in raw]); comps[key] = [sign*(r[key]-mu)/sd for r in raw]
        bv2 = [wmap["margin"]*comps["margin"][i] + wmap["retention"]*comps["churn_cost"][i]
               + wmap["bad_debt"]*comps["baddebt"][i] + wmap["carbon"]*comps["carbon_value"][i]
               for i in range(len(pop))]
        me = {d: eta2(bv2, weights, [h[d] for h in pop]) for d in DIMS}
        order = sorted(DIMS, key=lambda d: (me[d], d), reverse=True)
        v3 = eta2(bv2, weights, labels_for(pop, order[:1]))
        v12 = eta2(bv2, weights, labels_for(pop, order[:2]))
        robustness[name] = {"top3_dims": order[:3], "var_at_top1": round(v3, 4),
                            "var_at_top2_dims": round(v12, 4),
                            "leading_dim": order[0], "second_dim": order[1]}

    out = {
        "_meta": {
            "artefact": "value_frontier",
            "track": "DIRECTOR_STEER_COVERAGE_STAGE4_VALUE_FRONTIER_2026-07-20",
            "stage": "4 (value frontier) -- DISCOVER/FRAME, analysis only, NO generator change",
            "created": "2026-07-20",
            "population": {
                "n_households_sampled": N_POP, "seed": SEED,
                "representativeness": "POPULATION-REPRESENTATIVE (volume-weighted) -- distinct from "
                    "stage-3 worst-cell cohorts (stage-3 doc section 6). Built from committed stage-2 "
                    "marginals+crosstabs, SAME joint structure as stage-3 (tenure-spine block; fuel pinned to region).",
                "assumed_dim_rates": {"green": P_green, "price": P_price, "channel": P_channel,
                                       "solar_PV": P_solar, "EV": P_ev, "home_battery": P_batt},
            },
            "objective_1_valuable_variance": "between-segment eta^2 of the asserted business-value "
                "(volume-weighted). values-call (a) = value_outcome_model.json weighting.",
            "objective_2_critical_coverage": "fraction of the protected set (values-call (b) = "
                "critical_groups.json) isolatable at purity>=%.2f. Protected REGARDLESS of size." % CRIT_PURITY,
            "kept_separate": "variance_captured and critical_coverage are separate columns; value_combined "
                "is their sum, REPORTED but never used to tune either objective (R12).",
            "determinism": "fixed seed %d, sorted iteration; no microdata; no network." % SEED,
        },
        "critical_group_prevalence_pct": {k: round(100.0 * prevalence[k] / N_POP, 3)
                                          for k in sorted([g["id"] for g in CRIT])},
        "population_business_value_stats": {
            "note": "raw outcome dispersion across the sampled population (diagnostic only, R12).",
            "margin_gbp": {"mean": round(sum(r["margin"] for r in raw)/len(raw), 2)},
            "churn_cost_gbp": {"mean": round(sum(r["churn_cost"] for r in raw)/len(raw), 2)},
            "baddebt_gbp": {"mean": round(sum(r["baddebt"] for r in raw)/len(raw), 2)},
            "carbon_value_gbp": {"mean": round(sum(r["carbon_value"] for r in raw)/len(raw), 2)},
        },
        "hybrid_recommended_design": {
            "principle": "The two objectives DON'T co-move: valuable variance is captured by a few "
                "coarse main-effect splits (price_sensitivity x tenure); critical-group protection is "
                "bought by TARGETED conjunctive carve-outs (as stage-3 carved its named worst cells), "
                "which add ~zero variance but full tail protection. So the minimum-segment design is a "
                "small variance core PLUS ~5 critical carve-outs -- NOT a deeper cross.",
            "designs": hybrids,
        },
        "constructor_A_variance_greedy": A,
        "constructor_B_modal_outward": B,
        "knees": {
            "A_variance_only": find_knee(A["curve"], "leaves", "variance_captured"),
            "A_combined": find_knee(A["curve"], "leaves", "value_combined"),
            "B_variance_only": find_knee(B["curve"], "segments", "variance_captured"),
            "B_combined": find_knee(B["curve"], "segments", "value_combined"),
        },
        "weighting_robustness": {
            "note": "Does the variance knee (leading dims) survive re-weighting the values-call? "
                    "If the same 1-2 dims lead under all three weightings, the knee is robust to the "
                    "values-call and only the FINE ordering past the knee is weighting-dependent.",
            "results": robustness,
        },
        "coverage_knee_reference": {"N": 200, "meaning": "stage-3 completeness knee (worst-cell coverage "
            "0->1). DIFFERENT axis: households DRAWN, not SEGMENTS defined. The value knee answers a "
            "different question on a different axis and the two are not directly comparable in units."},
    }
    with open(os.path.join(HERE, "value_frontier.json"), "w") as f:
        json.dump(out, f, indent=2)

    print("=== critical-group prevalence (%) ===")
    for k, v in out["critical_group_prevalence_pct"].items(): print(f"  {k}: {v}%")
    print("\n=== Constructor B (modal-outward) ===")
    print("  modal customer:", B["modal_customer"])
    print("  dim order:", B["dim_order"])
    for c in B["curve"]:
        print(f"  step{c['step']:>2} +{str(c['added_dim']):<17} segs={c['segments']:>6} "
              f"var={c['variance_captured']:.3f} crit={c['critical_coverage']:.3f} comb={c['value_combined']:.3f}")
    print("\n=== Constructor A (variance-greedy) ===")
    for c in A["curve"]:
        print(f"  leaves={c['leaves']:>3} split={str(c.get('split')):<16} var={c['variance_captured']:.3f} "
              f"crit={c['critical_coverage']:.3f} comb={c['value_combined']:.3f}")
    print("\n=== HYBRID (variance core + critical carve-outs) ===")
    for k, v in hybrids.items():
        print(f"  {k}: segs={v['segments']} var={v['variance_captured']} crit={v['critical_coverage']} per={v['per_group_coverage']}")
    print("\n=== KNEES ===")
    print(json.dumps(out["knees"], indent=1))

if __name__ == "__main__":
    main()
