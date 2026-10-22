"""Split each arm pair's money by the channel it moved through, per dice seed (record section 14).

REUSE: tools/grade_per_customer_switch_seeds.py
CLASS: CUSTOM
INDEX: searched "arm pair split by channel", "departure versus tariff transfer", "per seed arm
       grade". `tools/run_value_cycle_ab.noise_floor` spreads `selection_gbp` across seeds but has no
       per-household channel. `tools/grade_save_offer_shapes.py` grades one save offer's shapes,
       not a pair of whole runs. The section 13 grade lived in /tmp and read two named files.

WHY THE SPLIT. Section 13 found the one-seed -£810 between the save-odds guard and the switch
without it came entirely from 5 households that stayed in both arms: with the discount they were
below the default and fixed, without it they were above and the dominance rule
(`customer_events.renewal_outcome`) left them on the default. No offer changed a departure. By M2
that is transfer from households who were staying anyway, not retention value. A mean over seeds
that does not keep the channels apart would publish it as retention value.

THE CHANNELS, one per household, decided in this order on its renewal rows paired by
(household, roll date, fuel) in `customer_events`:
  * `departure` -- its set of departures differs between the arms.
  * `parity`    -- it stayed in both, and at some roll one arm fixed (`renewal`, renewed) where the
                   other declined the fix (`declined_fix`). The edge section 13 found.
  * `other`     -- any other difference in its renewal rows: an SVT conversion against a fix, or a
                   roll present in one arm only.
  * `same_choice` -- identical renewal rows. Gross can still move, by the discount a stayer
                   would have taken anyway.
Gross is `per_cid_pnl[...]["gross"]` summed over the household's supply points. The net the
record grades is `provisioned_net_gbp`; what gross does not explain (provision, capital, cost
lines) is `unattributed_gbp`, printed, never folded into a channel.

    python3 -m tools.grade_per_customer_switch_seeds LABEL:FLAT.json:ENDING_TERM.json:SAVE_ODDS.json ...
"""
from __future__ import annotations

import collections
import json
import math
import sys

CHANNELS = ("departure", "parity", "other", "same_choice")
ARM_NAMES = ("flat", "ending_term", "save_odds")
PAIRS = (("ending_term", "flat"), ("save_odds", "flat"), ("save_odds", "ending_term"))
# Two-sided 95% Student t for n-1 degrees of freedom; a mean over n seeds is printed with it.
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}


def household(cid: str) -> str:
    """A gas supply point carries a trailing `g` on its household id (`C5g`, `PROS-2016-0263g`)."""
    return cid[:-1] if cid.endswith("g") and not cid[:-1].endswith("-") else cid


def outcome(event: dict) -> str:
    if event["event_type"] == "churned":
        return "left"
    return {"renewal": "fixed", "declined_fix": "declined_fix"}.get(event.get("departure_occasion"),
                                                                    event.get("departure_occasion"))


def reduce_run(d: dict) -> dict:
    """The few fields the split reads, so a seed's three 128 MB outputs need not be held at once."""
    rows = collections.defaultdict(dict)
    for e in d["customer_events"]:
        rows[household(e["customer_id"])][(e["event_date"][:10], e["commodity"])] = outcome(e)
    gross = collections.defaultdict(float)
    for cid, pnl in d["per_cid_pnl"].items():
        gross[household(cid)] += pnl["gross"]
    return {"rows": dict(rows), "gross": dict(gross), "net": d["provisioned_net_gbp"],
            "offers": len(d.get("retention_log") or ()),
            "departures": len(d["churned_billing_accounts"]),
            "arm": d.get("_per_customer_switch_arm"), "dice": d.get("_dice_seed")}


def channel(a_rows: dict, b_rows: dict) -> str:
    if {k for k, v in a_rows.items() if v == "left"} != {k for k, v in b_rows.items() if v == "left"}:
        return "departure"
    if any({a_rows.get(k), b_rows.get(k)} == {"fixed", "declined_fix"} for k in a_rows):
        return "parity"
    return "other" if a_rows != b_rows else "same_choice"


def split(a: dict, b: dict) -> dict:
    """a - b, by channel. Every household with a renewal row or a gross line in either arm is in
    exactly one channel, so the channels' gross sums to the total gross difference."""
    out = {c: {"households": 0, "gross_gbp": 0.0} for c in CHANNELS}
    for h in set(a["rows"]) | set(b["rows"]) | set(a["gross"]) | set(b["gross"]):
        c = channel(a["rows"].get(h, {}), b["rows"].get(h, {}))
        dg = a["gross"].get(h, 0.0) - b["gross"].get(h, 0.0)
        if c != "same_choice" or abs(dg) > 0.005:
            out[c]["households"] += 1
        out[c]["gross_gbp"] += dg
    gross = sum(v["gross_gbp"] for v in out.values())
    net = a["net"] - b["net"]
    return {"net_gbp": net, "gross_gbp": gross, "unattributed_gbp": net - gross, "channels": out,
            "departures": (a["departures"], b["departures"]), "offers": (a["offers"], b["offers"])}


def mean_interval(xs: list[float]) -> tuple[float, float | None]:
    """The mean and its 95% half-width, None for one seed: one seed is a run, not a spread."""
    n = len(xs)
    m = sum(xs) / n
    if n < 2:
        return m, None
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return m, T95.get(n - 1, 1.96) * sd / math.sqrt(n)


def grade(seeds: dict[str, dict[str, str]]) -> dict:
    per_seed = {}
    for label, paths in seeds.items():
        runs = {arm: reduce_run(json.load(open(paths[arm]))) for arm in ARM_NAMES}
        per_seed[label] = {f"{x}-{y}": split(runs[x], runs[y]) for x, y in PAIRS}
        per_seed[label]["dice"] = {arm: runs[arm]["dice"] for arm in ARM_NAMES}
    summary = {}
    for x, y in PAIRS:
        key = f"{x}-{y}"
        rows = [per_seed[s][key] for s in per_seed]
        summary[key] = {"net_gbp": mean_interval([r["net_gbp"] for r in rows]),
                        **{c: mean_interval([r["channels"][c]["gross_gbp"] for r in rows])
                           for c in CHANNELS}}
    return {"per_seed": per_seed, "summary": summary, "seeds": len(per_seed)}


def _fmt(mi: tuple[float, float | None]) -> str:
    m, h = mi
    return f"{m:+10.2f}" + ("" if h is None else f" ±{h:8.2f}")


def cli(argv: list[str]) -> None:
    seeds = {}
    for spec in argv:
        label, *paths = spec.split(":")
        if len(paths) != 3:
            raise SystemExit(f"REFUSED: {spec!r} is not LABEL:FLAT:ENDING_TERM:SAVE_ODDS")
        seeds[label] = dict(zip(ARM_NAMES, paths))
    g = grade(seeds)
    for label, pairs in g["per_seed"].items():
        print(f"seed {label}  dice {pairs['dice']}")
        for x, y in PAIRS:
            r = pairs[f"{x}-{y}"]
            ch = "  ".join(f"{c} {v['households']}h {v['gross_gbp']:+.2f}" for c, v in r["channels"].items())
            print(f"  {x}-{y}: net {r['net_gbp']:+.2f} (gross {r['gross_gbp']:+.2f}, unattributed "
                  f"{r['unattributed_gbp']:+.2f}) departures {r['departures']} offers {r['offers']}\n    {ch}")
    print(f"across {g['seeds']} seed(s), mean ± 95% half-width:")
    for key, s in g["summary"].items():
        print(f"  {key}: net {_fmt(s['net_gbp'])}  " + "  ".join(f"{c} {_fmt(s[c])}" for c in CHANNELS))


if __name__ == "__main__":
    cli(sys.argv[1:])
