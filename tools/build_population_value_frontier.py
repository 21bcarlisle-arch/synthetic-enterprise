#!/usr/bin/env python3
"""Stage 4 -- the VALUE frontier for population segmentation.

Track: DIRECTOR_STEER_COVERAGE_STAGE4_VALUE_FRONTIER_2026-07-20
Status: DESIGN + committed structure only. NO generator change (director-reserved).
        No network, no microdata. Reads only the banked Stage-3 committed JSONs.

Stage-3 answered COVERAGE ("does every important cell appear?"; coverage knee N=200).
Stage 4 asks "is each segment WORTH having?" -- the curve of value captured vs
segment count, and its KNEE (the *value* knee, distinct from the coverage knee).

Two metrics kept DELIBERATELY SEPARATE (a blended metric would trade them silently):
  (1) VALUABLE VARIANCE      -- volume-weighted variance-decomposition of a business
                               outcome over an asserted behavioural-response model.
  (2) CRITICAL SMALL GROUPS  -- rare cells protected regardless of size (welfare /
                               regulatory / mortality weight); barely move variance.
Rule: a segment is justified if it adds material valuable-variance OR captures a
critical group.

Determinism: no RNG anywhere; all iteration sorted; all figures analytic/enumerated.
Output is hash-independent by construction. Verify by running under PYTHONHASHSEED=0
and PYTHONHASHSEED=1 and diffing the emitted JSON.
"""
from __future__ import annotations
import json, math, os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir))
PC = os.path.join(REPO, "docs", "market_research", "population_coverage")
OUT_PATH = os.path.join(PC, "value_frontier.json")

AXES = OrderedDict([
    ("tenure",          dict(group="block",      prov="observed",
                             levels=["own_outright", "own_mortgage", "private_rent", "social_rent"])),
    ("accommodation",   dict(group="block",      prov="observed",
                             levels=["detached", "semi", "terraced", "flat", "caravan"])),
    ("cars",            dict(group="block",      prov="observed",
                             levels=["0", "1", "2plus"])),
    ("nssec",           dict(group="block",      prov="observed",
                             levels=["higher", "intermediate", "routine_semi", "unemployed_student"])),
    ("heating_fuel",    dict(group="fuel",       prov="observed",
                             levels=["mains_gas", "mixed", "electric", "oil", "lpg_bottled", "heat_network", "other_offgas"])),
    ("region",          dict(group="geo",        prov="observed",
                             levels=["South East", "London", "North West", "East", "South West",
                                     "West Midlands", "Yorkshire and The Humber", "East Midlands", "Wales", "North East"])),
    ("green_stance",    dict(group="attitude",   prov="assumed",
                             levels=["engaged", "neutral", "disengaged"])),
    ("price_sensitivity", dict(group="attitude", prov="assumed",
                             levels=["high", "medium", "low"])),
    ("channel_pref",    dict(group="engagement", prov="assumed",
                             levels=["digital", "phone", "assisted"])),
    ("solar_PV",        dict(group="tech",       prov="assumed", levels=["yes", "no"])),
    ("EV",              dict(group="tech",       prov="assumed", levels=["yes", "no"])),
    ("home_battery",    dict(group="tech",       prov="assumed", levels=["yes", "no"])),
])
OBSERVED = [a for a in AXES if AXES[a]["prov"] == "observed"]

BANDING = {
    "tenure": {
        "own_outright": ["outright"], "own_mortgage": ["mortgage", "shared"],
        "private_rent": ["private", "rent-free", "rent free"],
        "social_rent": ["social"],
    },
    "accommodation": {
        "detached": ["detached"], "semi": ["semi"], "terraced": ["terrace"],
        "flat": ["flat", "maisonette", "apartment"], "caravan": ["caravan", "temporary", "mobile"],
    },
    "cars": {"0": ["no car", "no cars", "0 car"], "1": ["1 car", "one car"], "2plus": ["2", "two", "more"]},
    "nssec": {
        "higher": ["l1-l3", "higher managerial"],
        "intermediate": ["l4-l6", "lower managerial", "l7", "intermediate"],
        "routine_semi": ["l8-l9", "l10-l11", "l12", "l13", "small employers", "lower supervisory",
                          "semi-routine", "routine"],
        "unemployed_student": ["l14", "l15", "never worked", "unemployed", "student"],
    },
    "heating_fuel": {
        "mains_gas": ["mains gas"], "electric": ["electric only"],
        "oil": ["oil only", "oil"], "lpg_bottled": ["tank", "bottled"],
        "heat_network": ["district", "communal", "heat network"],
        "mixed": ["two+ types", "two or more"],
        "other_offgas": ["other central heating", "other ch", "renewable only", "solid fuel", "wood"],
    },
    "region": {
        "South East": ["south east"], "London": ["london"], "North West": ["north west"],
        "East": ["east"], "South West": ["south west"], "West Midlands": ["west midlands"],
        "Yorkshire and The Humber": ["yorkshire"], "East Midlands": ["east midlands"],
        "Wales": ["wales"], "North East": ["north east"],
    },
}
DROP_SUBSTRINGS = ["no central heating", "no ch"]

ASSERTED_MARGINALS = {
    "green_stance":      {"engaged": 0.30, "neutral": 0.40, "disengaged": 0.30},
    "price_sensitivity": {"high": 0.35, "medium": 0.40, "low": 0.25},
    "channel_pref":      {"digital": 0.55, "phone": 0.30, "assisted": 0.15},
    "solar_PV":          {"yes": 0.05, "no": 0.95},
    "EV":                {"yes": 0.05, "no": 0.95},
    "home_battery":      {"yes": 0.02, "no": 0.98},
}
ASSERTED_OBSERVED_FALLBACK = {
    "tenure": {"own_outright": 0.3283, "own_mortgage": 0.2971, "private_rent": 0.2040, "social_rent": 0.1706},
    "accommodation": {"detached": 0.2321, "semi": 0.3151, "terraced": 0.2316, "flat": 0.2169, "caravan": 0.0042},
    "cars": {"0": 0.2331, "1": 0.4131, "2plus": 0.3538},
    "nssec": {"higher": 0.1614, "intermediate": 0.3185, "routine_semi": 0.4309, "unemployed_student": 0.0892},
    "heating_fuel": {"mains_gas": 0.7494, "mixed": 0.0921, "electric": 0.0866, "oil": 0.0354,
                     "lpg_bottled": 0.0107, "heat_network": 0.0090, "other_offgas": 0.0168},
    "region": {"South East": 0.1537, "London": 0.1382, "North West": 0.1272, "East": 0.1061,
               "South West": 0.0988, "West Midlands": 0.0980, "Yorkshire and The Humber": 0.0940,
               "East Midlands": 0.0822, "Wales": 0.0544, "North East": 0.0474},
}
PARSE_LOG = {}

def _flatten_pairs(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (int, float)):
                out.append((str(k), float(v)))
            else:
                _flatten_pairs(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _flatten_pairs(v, out)

def _match_level(axis, label):
    low = str(label).lower()
    if axis in BANDING:
        best_lv, best_len = None, -1
        for lv, subs in BANDING[axis].items():
            for s in subs:
                if s in low and len(s) > best_len:
                    best_lv, best_len = lv, len(s)
        return best_lv
    return None

def _band_axis(axis, raw_pairs):
    levels = AXES[axis]["levels"]
    acc = {lv: 0.0 for lv in levels}
    matched_any = False
    for label, prob in raw_pairs:
        low = label.lower().strip()
        if any(d in low for d in DROP_SUBSTRINGS):
            continue
        best_lv, best_len = None, -1
        for lv, subs in BANDING[axis].items():
            for s in subs:
                if s in low and len(s) > best_len:
                    best_lv, best_len = lv, len(s)
        if best_lv is not None:
            acc[best_lv] += prob
            matched_any = True
    tot = sum(acc.values())
    if not matched_any or tot <= 0:
        return None
    return {lv: acc[lv] / tot for lv in levels}

def load_marginals():
    marg = {}
    path = os.path.join(PC, "marginals.json")
    raw = {}
    try:
        with open(path) as fh:
            raw = json.load(fh)
    except Exception as e:
        PARSE_LOG["marginals_file"] = "unreadable (%s); asserted fallback used" % e
    dim_aliases = {
        "tenure": ["tenure"], "accommodation": ["accommodation", "accommodation_type"],
        "cars": ["cars", "cars_or_vans"], "nssec": ["nssec", "nssec_hrp"],
        "heating_fuel": ["heating_fuel", "heating_fuel_type"], "region": ["region"],
    }
    for axis in OBSERVED:
        blob = None
        if isinstance(raw, dict):
            for alias in dim_aliases[axis]:
                for k, v in raw.items():
                    if k.lower() == alias or alias in k.lower():
                        blob = v
                        break
                if blob is not None:
                    break
        parsed = None
        if blob is not None:
            pairs = []
            _flatten_pairs(blob, pairs)
            parsed = _band_axis(axis, pairs)
        if parsed is not None:
            marg[axis] = parsed
            PARSE_LOG[axis] = "parsed_from_marginals.json"
        else:
            marg[axis] = dict(ASSERTED_OBSERVED_FALLBACK[axis])
            PARSE_LOG[axis] = "ASSERTED_FALLBACK (marginals.json blob not matched/banded)"
    for axis in AXES:
        if axis not in OBSERVED:
            marg[axis] = dict(ASSERTED_MARGINALS[axis])
            PARSE_LOG[axis] = "asserted (crossed dim, no open joint)"
    return marg

EFFECTS = {
    "margin": {
        "heating_fuel": {"mains_gas": 40, "mixed": 30, "electric": -10, "oil": 20,
                          "lpg_bottled": 10, "heat_network": -20, "other_offgas": 0},
        "accommodation": {"detached": 60, "semi": 20, "terraced": 0, "flat": -40, "caravan": -60},
        "nssec": {"higher": 50, "intermediate": 15, "routine_semi": -15, "unemployed_student": -50},
        "tenure": {"own_outright": 20, "own_mortgage": 15, "private_rent": -15, "social_rent": -20},
        "cars": {"0": -15, "1": 5, "2plus": 15},
        "channel_pref": {"digital": 20, "phone": -10, "assisted": -30},
        "price_sensitivity": {"high": -20, "medium": 0, "low": 20},
        "region": {"South East": 15, "London": -15, "North West": 0, "East": 5, "South West": 5,
                    "West Midlands": 0, "Yorkshire and The Humber": -5, "East Midlands": 0,
                    "Wales": 5, "North East": -5},
        "solar_PV": {"yes": -15, "no": 0}, "EV": {"yes": 30, "no": 0}, "home_battery": {"yes": -5, "no": 0},
        "green_stance": {"engaged": 5, "neutral": 0, "disengaged": -5},
    },
    "churn": {
        "price_sensitivity": {"high": 0.12, "medium": 0.0, "low": -0.08},
        "channel_pref": {"digital": 0.05, "phone": -0.02, "assisted": -0.03},
        "tenure": {"own_outright": -0.03, "own_mortgage": -0.02, "private_rent": 0.08, "social_rent": 0.02},
        "green_stance": {"engaged": 0.03, "neutral": 0.0, "disengaged": -0.02},
        "nssec": {"higher": 0.0, "intermediate": 0.0, "routine_semi": 0.01, "unemployed_student": 0.03},
        "EV": {"yes": 0.04, "no": 0.0}, "solar_PV": {"yes": 0.03, "no": 0.0},
        "region": {"South East": 0.0, "London": 0.0, "North West": 0.0, "East": 0.0, "South West": 0.0,
                    "West Midlands": 0.0, "Yorkshire and The Humber": 0.0, "East Midlands": 0.0,
                    "Wales": 0.0, "North East": 0.0},
    },
    "carbon": {
        "green_stance": {"engaged": 300, "neutral": 0, "disengaged": -100},
        "EV": {"yes": 800, "no": 0}, "solar_PV": {"yes": 600, "no": 0}, "home_battery": {"yes": 300, "no": 0},
        "heating_fuel": {"mains_gas": 0, "mixed": 100, "electric": 200, "oil": 400,
                          "lpg_bottled": 300, "heat_network": 100, "other_offgas": 250},
        "accommodation": {"detached": 150, "semi": 60, "terraced": 30, "flat": -40, "caravan": 80},
        "tenure": {"own_outright": 60, "own_mortgage": 80, "private_rent": -40, "social_rent": -40},
    },
    "baddebt": {
        "nssec": {"higher": -0.03, "intermediate": 0.0, "routine_semi": 0.04, "unemployed_student": 0.12},
        "tenure": {"own_outright": -0.03, "own_mortgage": -0.02, "private_rent": 0.03, "social_rent": 0.06},
        "heating_fuel": {"mains_gas": 0.0, "mixed": 0.0, "electric": 0.03, "oil": 0.02,
                          "lpg_bottled": 0.02, "heat_network": 0.01, "other_offgas": 0.02},
        "price_sensitivity": {"high": 0.02, "medium": 0.0, "low": -0.01},
        "cars": {"0": 0.03, "1": 0.0, "2plus": -0.01},
        "region": {"South East": -0.01, "London": 0.01, "North West": 0.0, "East": -0.01, "South West": 0.0,
                    "West Midlands": 0.0, "Yorkshire and The Humber": 0.0, "East Midlands": 0.0,
                    "Wales": 0.02, "North East": 0.02},
    },
}
OUTCOME_SIGN = {"margin": 1.0, "churn": -1.0, "carbon": 1.0, "baddebt": -1.0}
DEFAULT_WEIGHTS = {"margin": 0.40, "churn": 0.25, "baddebt": 0.20, "carbon": 0.15}

def axis_effect(axis, outcome):
    tbl = EFFECTS[outcome].get(axis, {})
    return {lv: float(tbl.get(lv, 0.0)) for lv in AXES[axis]["levels"]}

def moments(marg_axis, eff_axis):
    mean = sum(marg_axis[lv] * eff_axis[lv] for lv in eff_axis)
    ex2 = sum(marg_axis[lv] * eff_axis[lv] ** 2 for lv in eff_axis)
    return mean, max(ex2 - mean ** 2, 0.0)

CRITICAL_GROUPS = [
    dict(id="fuel_poor_offgas", weight=1.0, klass="welfare",
         rationale="off-gas fuel-poor: winter mortality / fuel-poverty; protected regardless of size",
         predicate={"heating_fuel": ["oil", "lpg_bottled", "other_offgas"], "nssec": ["unemployed_student"]}),
    dict(id="vulnerable_all_electric", weight=1.0, klass="welfare",
         rationale="all-electric low-income renters: prepay self-disconnection / cold-home risk",
         predicate={"heating_fuel": ["electric"], "nssec": ["unemployed_student"],
                    "tenure": ["social_rent", "private_rent"]}),
    dict(id="oil_fuel_poor_rural", weight=1.0, klass="welfare",
         rationale="Stage-3 named worst cell: oil rural social-rented never-worked HRP",
         predicate={"heating_fuel": ["oil"], "region": ["Wales"], "tenure": ["social_rent"],
                    "accommodation": ["detached"], "nssec": ["unemployed_student"]}),
    dict(id="all_electric_flat_london", weight=1.0, klass="welfare",
         rationale="Stage-3 named worst cell: electric-only flat London private-rent",
         predicate={"heating_fuel": ["electric"], "accommodation": ["flat"], "region": ["London"],
                    "tenure": ["private_rent"]}),
    dict(id="heat_network_captive", weight=0.7, klass="regulatory",
         rationale="heat-network households: no supplier switch, new Ofgem heat-network regulation exposure",
         predicate={"heating_fuel": ["heat_network"]}),
    dict(id="solar_ev_battery_owner", weight=0.5, klass="strategic_lowcarbon",
         rationale="Stage-3 named cell: PV+EV+battery co-owner; flexibility/low-carbon strategic value, not welfare",
         predicate={"solar_PV": ["yes"], "EV": ["yes"], "home_battery": ["yes"]}),
]
CRIT_TOTAL_W = sum(g["weight"] for g in CRITICAL_GROUPS)

def critical_defining_axes(g):
    return set(g["predicate"].keys())

def critical_coverage(selected):
    sel = set(selected)
    covered = [g for g in CRITICAL_GROUPS if critical_defining_axes(g) <= sel]
    frac = sum(g["weight"] for g in covered) / CRIT_TOTAL_W
    return frac, sorted(g["id"] for g in covered)

def load_fuel_region_joint(marg):
    floor = 1e-4
    path = os.path.join(PC, "crosstabs.json")
    joint = {}
    used = "asserted_pinning"
    try:
        with open(path) as fh:
            ct = json.load(fh)
        blob = None
        for k, v in ct.items():
            if "heatingfuel" in k.lower().replace("_", "") and "region" in k.lower():
                blob = v
                break
        table = blob.get("table") if isinstance(blob, dict) else None
        if table:
            row_keys = list(table.keys())
            rows_are_region = sum(any(s in rk.lower() for s in ["london", "wales", "east", "west",
                                    "north", "south", "yorkshire", "midlands"]) for rk in row_keys) > len(row_keys) / 2.0
            reg_marg = marg["region"]
            for rk, cols in table.items():
                if not isinstance(cols, dict):
                    continue
                for ck, p in cols.items():
                    fuel_lv = _match_level("heating_fuel", ck if not rows_are_region else rk)
                    reg_lv = _match_level("region", rk if rows_are_region else ck)
                    if fuel_lv and reg_lv:
                        joint[(fuel_lv, reg_lv)] = joint.get((fuel_lv, reg_lv), 0.0) + reg_marg[reg_lv] * float(p)
            if joint:
                used = "parsed_from_crosstabs.json"
    except Exception:
        joint = {}
    if not joint:
        pin = {
            "mains_gas":   {"default": 1.0},
            "mixed":       {"default": 1.0},
            "electric":    {"London": 2.0, "default": 1.0},
            "oil":         {"Wales": 6.0, "South West": 3.0, "East": 2.0, "East Midlands": 2.0,
                            "London": 0.05, "default": 0.5},
            "lpg_bottled": {"Wales": 4.0, "South West": 3.0, "North East": 1.5, "London": 0.1, "default": 0.6},
            "heat_network": {"London": 3.8, "default": 0.6},
            "other_offgas": {"Wales": 3.0, "South West": 2.5, "London": 0.2, "default": 0.7},
        }
        for f in AXES["heating_fuel"]["levels"]:
            weights = {r: pin[f].get(r, pin[f]["default"]) for r in AXES["region"]["levels"]}
            wsum = sum(marg["region"][r] * weights[r] for r in weights)
            for r in AXES["region"]["levels"]:
                pf_given_r = marg["heating_fuel"][f] * weights[r] / wsum
                joint[(f, r)] = marg["region"][r] * pf_given_r
    tot = sum(joint.values())
    joint = {k: v / tot for k, v in joint.items()}
    n_real = sum(1 for v in joint.values() if v > floor)
    return joint, n_real, used

BLOCK = {"tenure", "accommodation", "cars", "nssec"}
BLOCK_REALISTIC = 201
FUEL_REGION_FALLBACK_REAL = 63

def build(weights):
    marg = load_marginals()
    outcome_sd = {}
    for o in EFFECTS:
        var_o = 0.0
        for axis in AXES:
            _, v = moments(marg[axis], axis_effect(axis, o))
            var_o += v
        outcome_sd[o] = math.sqrt(var_o) if var_o > 0 else 1.0

    def blended_effect(axis):
        out = {}
        for lv in AXES[axis]["levels"]:
            s = 0.0
            for o in EFFECTS:
                s += weights[o] * OUTCOME_SIGN[o] * axis_effect(axis, o)[lv] / outcome_sd[o]
            out[lv] = s
        return out
    G = {axis: blended_effect(axis) for axis in AXES}
    var_axis = {}
    for axis in AXES:
        _, v = moments(marg[axis], G[axis])
        var_axis[axis] = v
    fr_joint, fr_real, fr_src = load_fuel_region_joint(marg)

    def var_over_joint(axes_in):
        mean = 0.0; ex2 = 0.0
        for (f, r), p in fr_joint.items():
            val = 0.0
            if "heating_fuel" in axes_in:
                val += G["heating_fuel"][f]
            if "region" in axes_in:
                val += G["region"][r]
            mean += p * val; ex2 += p * val * val
        return max(ex2 - mean * mean, 0.0)
    var_region_marg = var_axis["region"]
    var_fuel_marg = var_axis["heating_fuel"]
    var_fuel_region_joint = var_over_joint({"heating_fuel", "region"})

    def subset_variance(selected):
        sel = set(selected)
        v = 0.0
        has_f = "heating_fuel" in sel
        has_r = "region" in sel
        if has_f and has_r:
            v += var_fuel_region_joint
        elif has_f:
            v += var_fuel_marg
        elif has_r:
            v += var_region_marg
        for axis in sel:
            if axis in ("heating_fuel", "region"):
                continue
            v += var_axis[axis]
        return v

    total_var = subset_variance(list(AXES.keys()))

    def segment_count(selected):
        sel = set(selected)
        count = 1
        handled = set()
        if BLOCK <= sel:
            count *= BLOCK_REALISTIC
            handled |= BLOCK
        if {"heating_fuel", "region"} <= sel:
            count *= (fr_real if fr_real > 0 else FUEL_REGION_FALLBACK_REAL)
            handled |= {"heating_fuel", "region"}
        for axis in sorted(sel):
            if axis in handled:
                continue
            count *= len(AXES[axis]["levels"])
        return count

    def centre_out_order():
        remaining = sorted(AXES.keys())
        order = []
        while remaining:
            cur = subset_variance(order)
            scored = sorted((-round(subset_variance(order + [a]) - cur, 12), a) for a in remaining)
            best = scored[0][1]
            order.append(best); remaining.remove(best)
        return order

    def worst_cell_order():
        remaining = sorted(AXES.keys())
        order = []
        while remaining:
            cur_cov = critical_coverage(order)[0]
            cur_var = subset_variance(order)
            scored = []
            for a in remaining:
                cov_gain = critical_coverage(order + [a])[0] - cur_cov
                var_gain = subset_variance(order + [a]) - cur_var
                scored.append((-round(cov_gain, 12), -round(var_gain, 12), a))
            scored.sort()
            best = scored[0][2]
            order.append(best); remaining.remove(best)
        return order

    def frontier_for(order):
        pts = []
        prev_var = 0.0; prev_cov = 0.0
        for k in range(len(order) + 1):
            sel = order[:k]
            vc = subset_variance(sel) / total_var if total_var > 0 else 0.0
            cov, covered = critical_coverage(sel)
            combined = 0.5 * vc + 0.5 * cov
            pts.append(dict(
                k=k, axis_added=(order[k - 1] if k > 0 else None), selected=list(sel),
                segment_count=segment_count(sel), variance_captured=round(vc, 6),
                marginal_variance=round(vc - prev_var, 6), critical_coverage=round(cov, 6),
                marginal_critical=round(cov - prev_cov, 6), critical_groups_covered=covered,
                combined_value=round(combined, 6)))
            prev_var, prev_cov = vc, cov
        return pts

    def find_knee(pts, metric, eps):
        knee = 0
        for i in range(1, len(pts)):
            if pts[i][metric] - pts[i - 1][metric] >= eps:
                knee = pts[i]["k"]
        return knee

    co = centre_out_order()
    wc = worst_cell_order()
    fr_co = frontier_for(co)
    fr_wc = frontier_for(wc)
    EPS = 0.02
    knee_var_co = find_knee(fr_co, "variance_captured", EPS)
    knee_var_wc = find_knee(fr_wc, "variance_captured", EPS)
    knee_comb_co = find_knee(fr_co, "combined_value", EPS)
    knee_comb_wc = find_knee(fr_wc, "combined_value", EPS)
    crit_complete_co = next((p["k"] for p in fr_co if p["critical_coverage"] >= 0.999), len(co))
    crit_complete_wc = next((p["k"] for p in fr_wc if p["critical_coverage"] >= 0.999), len(wc))
    knee_set_co = set(co[:knee_comb_co])
    knee_set_wc = set(wc[:knee_comb_wc])
    converged = knee_set_co == knee_set_wc

    result = dict(
        _meta=dict(
            artefact="value_frontier",
            track="DIRECTOR_STEER_COVERAGE_STAGE4_VALUE_FRONTIER_2026-07-20 (stage 4, DISCOVER/FRAME)",
            created="2026-07-20",
            status="DESIGN + committed structure only -- NO generator change (director-reserved). "
                   "No network, no microdata; derives from banked Stage-3 committed numbers.",
            question="Stage 3 answered COVERAGE (coverage knee N=200). Stage 4 answers VALUE -- the value knee.",
            two_metrics_kept_separate="valuable_variance and critical_group_coverage are reported separately; "
                     "a blended combined_value curve is provided only as a tie-breaker for the knee.",
            determinism="No RNG; sorted iteration; analytic/enumerated -> hash-independent. "
                     "Verify identical output under PYTHONHASHSEED=0 and =1.",
            parse_log=PARSE_LOG,
            fuel_region_joint_source=fr_src,
            simplifications=[
                "Variance decomposition treats axes as independent EXCEPT the load-bearing fuel x region "
                "coupling (enumerated joint). Observed-block couplings are NOT modelled in the variance "
                "(independence approx) -- they slightly overstate block variance; the frontier SHAPE and "
                "knee are second-order to this (logged, R10).",
                "Behavioural model is ADDITIVE with no axis-interaction terms (asserted v1 simplification).",
                "Segment counts reuse banked Stage-3 realistic-cell counts (block=201, fuel x region "
                "enumerated) so outer rings hold no phantom households (tail-aware, per the steer).",
            ],
        ),
        values_call_1_what_makes_variance_valuable=dict(
            claim_status="asserted",
            description="The business outcome(s) the segmentation optimises toward, and their weighting. "
                        "DIRECTOR'S to set; proposed default below. Recomputable under any other weighting "
                        "by re-running this script with a different weights dict.",
            outcomes=dict(margin="annual gross-margin contribution (GBP/yr), + good",
                          churn="annual churn probability, bad (retention value = -churn)",
                          carbon="annual CO2 abatable (kg), + good",
                          baddebt="annual bad-debt probability, bad"),
            proposed_default_weighting=dict(weights),
            recompute="re-run build_population_value_frontier.py after editing DEFAULT_WEIGHTS; deterministic."),
        values_call_2_what_makes_a_group_critical=dict(
            claim_status="asserted",
            description="The protected set surviving regardless of size. DIRECTOR'S to set; proposed "
                        "criteria below. A group is 'covered' once the segmentation splits on all its "
                        "defining axes so it can be distinguished and protected.",
            criteria_classes=["welfare (fuel poverty / mortality / self-disconnection)",
                              "regulatory (captive / newly-regulated)",
                              "strategic_lowcarbon (flexibility value, NOT welfare)"],
            proposed_groups=[dict(id=g["id"], weight=g["weight"], klass=g["klass"], rationale=g["rationale"],
                                  predicate=g["predicate"], defining_axes=sorted(critical_defining_axes(g)))
                             for g in CRITICAL_GROUPS]),
        behavioural_response_model=dict(
            claim_status="asserted",
            description="Additive per-axis deltas on 4 outcomes. NOT ground truth -- a transparent, "
                        "changeable modelling choice so the value question can be posed at all. Every entry "
                        "is inspectable and editable.",
            outcome_signs=OUTCOME_SIGN, per_outcome_per_axis_effects=EFFECTS,
            per_outcome_population_sd=outcome_sd, per_axis_blended_variance=var_axis,
            fuel_region_joint_variance=var_fuel_region_joint, total_value_variance=total_var),
        population=dict(
            marginals=marg,
            axes={a: dict(levels=AXES[a]["levels"], group=AXES[a]["group"], provenance=AXES[a]["prov"],
                          cardinality=len(AXES[a]["levels"])) for a in AXES},
            fuel_region_realistic_cells=fr_real, block_realistic_cells=BLOCK_REALISTIC),
        constructors=dict(
            centre_out=dict(
                description="Greedy variance capture from the modal customer outward; adds the axis giving "
                            "the largest incremental captured variance.",
                axis_order=co, frontier=fr_co, knee_variance=knee_var_co, knee_combined=knee_comb_co,
                critical_complete_at_k=crit_complete_co),
            worst_cell_greedy=dict(
                description="Greedy critical-group coverage first (ties by incremental variance); "
                            "front-loads the protected small groups.",
                axis_order=wc, frontier=fr_wc, knee_variance=knee_var_wc, knee_combined=knee_comb_wc,
                critical_complete_at_k=crit_complete_wc)),
        value_knee=dict(
            claim_status="derived", eps_marginal=EPS,
            centre_out=dict(k=knee_comb_co, segment_count=fr_co[knee_comb_co]["segment_count"],
                            variance_captured=fr_co[knee_comb_co]["variance_captured"],
                            critical_coverage=fr_co[knee_comb_co]["critical_coverage"], axis_set=co[:knee_comb_co]),
            worst_cell=dict(k=knee_comb_wc, segment_count=fr_wc[knee_comb_wc]["segment_count"],
                            variance_captured=fr_wc[knee_comb_wc]["variance_captured"],
                            critical_coverage=fr_wc[knee_comb_wc]["critical_coverage"], axis_set=wc[:knee_comb_wc]),
            variance_only_knee=dict(centre_out_k=knee_var_co, worst_cell_k=knee_var_wc,
                                    centre_out_segment_count=fr_co[knee_var_co]["segment_count"]),
            comparison_to_coverage_knee="Stage-3 COVERAGE knee was N=200 cohorts. The VALUE knee is a segment "
                "count at which the next segment adds < %.0f%% combined value." % (EPS * 100)),
        convergence=dict(
            converged_on_knee_axis_set=converged,
            centre_out_knee_axis_set=sorted(knee_set_co), worst_cell_knee_axis_set=sorted(knee_set_wc),
            shared_axes=sorted(knee_set_co & knee_set_wc),
            centre_out_only=sorted(knee_set_co - knee_set_wc), worst_cell_only=sorted(knee_set_wc - knee_set_co),
            note="Both constructors are expected to agree on the high-value early axes and diverge only in "
                 "the low-value tail ordering. Variance rises faster under centre-out; critical coverage "
                 "completes earlier under worst-cell -- the two halves the steer keeps separate."),
    )
    return result

def main():
    res = build(dict(DEFAULT_WEIGHTS))
    with open(OUT_PATH, "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("=== VALUE FRONTIER (Stage 4) ===")
    print("parse_log:", json.dumps(res["_meta"]["parse_log"]))
    print("fuel_region_joint_source:", res["_meta"]["fuel_region_joint_source"])
    print("total_value_variance: %.4f" % res["behavioural_response_model"]["total_value_variance"])
    print("fuel_region_realistic_cells:", res["population"]["fuel_region_realistic_cells"])
    for name in ("centre_out", "worst_cell_greedy"):
        c = res["constructors"][name]
        print("\n--- %s ---" % name)
        print("axis_order:", c["axis_order"])
        print(" k  axis_added           segs   var_cap  d_var   crit_cov d_crit  combined")
        for p in c["frontier"]:
            print("%2d  %-18s %8d  %6.3f  %6.3f  %6.3f  %6.3f  %6.3f" % (
                p["k"], str(p["axis_added"]), p["segment_count"], p["variance_captured"],
                p["marginal_variance"], p["critical_coverage"], p["marginal_critical"], p["combined_value"]))
        print("knee_variance k=%d  knee_combined k=%d  critical_complete k=%d" % (
            c["knee_variance"], c["knee_combined"], c["critical_complete_at_k"]))
    vk = res["value_knee"]
    print("\n=== VALUE KNEE ===")
    print("centre_out: k=%d segs=%d var=%.3f crit=%.3f" % (
        vk["centre_out"]["k"], vk["centre_out"]["segment_count"],
        vk["centre_out"]["variance_captured"], vk["centre_out"]["critical_coverage"]))
    print("worst_cell: k=%d segs=%d var=%.3f crit=%.3f" % (
        vk["worst_cell"]["k"], vk["worst_cell"]["segment_count"],
        vk["worst_cell"]["variance_captured"], vk["worst_cell"]["critical_coverage"]))
    print("converged_on_knee_axis_set:", res["convergence"]["converged_on_knee_axis_set"])
    print("shared:", res["convergence"]["shared_axes"])
    print("centre_out_only:", res["convergence"]["centre_out_only"], "worst_cell_only:", res["convergence"]["worst_cell_only"])
    print("\nwrote", OUT_PATH)

if __name__ == "__main__":
    main()
