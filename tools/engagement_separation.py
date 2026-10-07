"""PB4 on a page: whether a household shops is not how far price moves it once it does.

REUSE: tools/engagement_separation.py
CLASS: CUSTOM
INDEX: searched "engagement", "elasticity", "separat". `tools/r1_inference_ceiling.true_traits` is
       the elasticity the world used, at the seed the book was drawn at, and is called here rather
       than re-derived. `tools/inside_the_renewal_rule.spearman_with_null` has the right shape
       but is an untracked file no commit carries (since 2026-09-09), so the shuffle null is
       re-stated here in a few lines over scipy. Neither publishes anything about
       ENGAGEMENT, and nothing in `site/` rendered PB4 at all, which is the residual (a) the atom's
       level hold names: "nothing renders PB4 to a reader".

WHAT THE TWO THINGS ARE, before anything is measured (PB4, director 2026-08-28):

    engagement   the probability a household ENTERS a choice at a fixed-term renewal --
                 `household_segments.active_renewal_probability_for_customer`, the persistent
                 archetype times the payment-channel multiplier anchored to Ofgem CIM w6.
    elasticity   how far a price gap moves a household ONCE IT IS CHOOSING --
                 `population_draw.price_elasticity_for_customer`, a weight with book mean 1.0.

THE ZERO ASSOCIATION BETWEEN THEM IS BUILT IN, AND THE PAGE SAYS SO. They are drawn on independent
substreams of the household id, so the rank correlation printed here is a check that the code does
what it says, not a discovery about households. What the reader gets that the code alone does not
show is the CONSEQUENCE on the real book: how many disengaged households carry an elasticity above
the book's mean -- the brief's "a disengaged household can be highly price-sensitive once a bill
shock makes it look" -- counted, not asserted.

AND THE GAP IS PUBLISHED BESIDE IT. The amplitude by which a bill shock raises engagement is a
declared `None` in the world (`BILL_SHOCK_ENGAGEMENT_MULTIPLIER`), so the page carries the gap's
own sentence rather than a figure.

    python3 -m tools.engagement_separation --write
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools import provenance_stamp  # noqa: E402
from tools.r1_inference_ceiling import true_traits  # noqa: E402

OUT_PATH = PROJECT / "site" / "data" / "engagement_separation.json"

#: What the reading depends on. A change to any of these can move a figure, so the stamp names them.
READS = (
    "simulation/household_segments.py",
    "simulation/population_draw.py",
    "simulation/live_population.py",
    "tools/engagement_separation.py",
    "docs/reports/pb4_departure_factors.json",
)

#: The fields a published block must carry, in the order a reader meets them. The freshness
#: control compares exactly these against a re-measurement at HEAD.
MEASURED_KEYS = ("households", "run_base_seed", "by_archetype", "by_channel", "association",
                 "disengaged_but_price_sensitive")


def _mean_ci95(values: list[float]) -> dict:
    """Mean with a t interval. A cell this small (14 standard-credit households) earns a wide
    bound, and the normal 1.96 would understate it."""
    from scipy.stats import t

    n = len(values)
    mean = statistics.fmean(values)
    if n < 2:
        return {"mean": round(mean, 4), "ci95": None, "n": n}
    half = t.ppf(0.975, n - 1) * statistics.stdev(values) / math.sqrt(n)
    return {"mean": round(mean, 4), "ci95": [round(mean - half, 4), round(mean + half, 4)], "n": n}


#: Shuffles in the no-association null, and its seed. Fixed so the published interval reproduces.
PERMUTATIONS = 2000
NULL_SEED = 20261002


def spearman_with_null(xs: list[float], ys: list[float]) -> dict:
    """Rank correlation beside the 95% band a shuffle of the same pairs reaches. The shuffle keeps
    both marginals, including the heavy ties in the engagement column (one value per archetype x
    channel cell), which a parametric interval would assume away."""
    import random

    from scipy.stats import spearmanr

    rho = float(spearmanr(xs, ys).statistic)
    rnd, pool, draws = random.Random(NULL_SEED), list(ys), []
    for _ in range(PERMUTATIONS):
        rnd.shuffle(pool)
        draws.append(float(spearmanr(xs, pool).statistic))
    draws.sort()
    low, high = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws))]
    return {"rho": round(rho, 4), "n": len(xs), "null_low": round(low, 4),
            "null_high": round(high, 4), "outside_the_null": bool(rho < low or rho > high),
            "permutations": PERMUTATIONS}


def households() -> list[str]:
    """Every household on the run's live book -- one id per property, never a supply-point leg,
    because the world draws one elasticity per property."""
    from simulation.household import household_of
    from simulation.live_population import live_population

    return sorted({household_of(p["customer_id"]) for p in live_population()})


def measure() -> dict:
    from simulation import household_segments as hs

    ids = households()
    elasticity, seed = true_traits(ids)
    rows = [{
        "id": cid,
        "archetype": hs.engagement_level_for_customer(cid).value,
        "channel": hs.payment_channel_for_customer(cid).value,
        "engagement": hs.active_renewal_probability_for_customer(cid),
        "elasticity": elasticity[cid],
    } for cid in ids]
    book_mean = statistics.fmean(r["elasticity"] for r in rows)

    def table(key: str, order: list[str]) -> list[dict]:
        groups: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            groups[r[key]].append(r)
        out = []
        for name in order:
            g = groups.get(name, [])
            if not g:
                continue
            out.append({
                key: name,
                "n": len(g),
                "engagement_mean": round(statistics.fmean(r["engagement"] for r in g), 4),
                "elasticity": _mean_ci95([r["elasticity"] for r in g]),
                "above_book_mean_elasticity": sum(r["elasticity"] > book_mean for r in g),
            })
        return out

    disengaged = [r for r in rows if r["archetype"] == hs.EngagementLevel.DISENGAGED.value]
    return {
        "households": len(rows),
        "run_base_seed": seed,
        "book_mean_elasticity": round(book_mean, 4),
        "by_archetype": table("archetype", [e.value for e in (
            hs.EngagementLevel.ACTIVE, hs.EngagementLevel.PASSIVE, hs.EngagementLevel.DISENGAGED)]),
        "by_channel": table("channel", [c.value for c in hs.PaymentChannel]),
        "association": spearman_with_null([r["engagement"] for r in rows],
                                          [r["elasticity"] for r in rows]),
        "disengaged_but_price_sensitive": {
            "disengaged": len(disengaged),
            "above_book_mean_elasticity": sum(r["elasticity"] > book_mean for r in disengaged),
            "max_elasticity": round(max((r["elasticity"] for r in disengaged), default=0.0), 4),
        },
    }


#: One world run, captured by `tools/capture_departure_factors` (the real `roll_lifecycle_event`
#: and the SVT drift roll, their arguments and their outcomes), reduced to the fields read here.
#: Committed, because the run takes about twenty minutes and the publish path cannot pay that.
CAPTURE_PATH = PROJECT / "docs" / "reports" / "pb4_departure_factors.json"

#: Saving bands on `price_differential_vs_market_reference`: how far this supplier's offer sits
#: above the market reference the household faces, as a fraction. Fixed before the capture was
#: read (PB4 D4 pre-registration, docs/staging/SEAT_FINDING_PB4_THE_EFTC_ARM_..._2026-10-07.md).
SAVING_BANDS = ((None, 0.0, "no saving"), (0.0, 0.05, "up to 5%"), (0.05, 0.15, "5% to 15%"),
                (0.15, None, "over 15%"))
#: Below this a cell is shown as too few to read rather than as a rate.
MIN_CELL = 10

#: WHAT THE CAPTURE CAN AND CANNOT SAY, found by reading it (2026-10-07). A household that does
#: not look at its term end never reaches the renewal roll -- it goes onto the default tariff and
#: leaves, if at all, by the SVT drift roll, which carries no saving term. So the renewal rows are
#: almost all households that LOOKED, and a band x archetype table over them measures leaving
#: given looking, which the world draws independently of the archetype. That table would have
#: been captioned "who leaves at the end of a deal" and been something else. What is published
#: instead: per archetype, both routes and departures per household; and, pooled, whether leaving
#: rises with the saving among those who looked.


def _wilson(k: int, n: int) -> list[float]:
    z = 1.959964
    centre = (k + z * z / 2) / (n + z * z)
    half = z * math.sqrt(k * (n - k) / n + z * z / 4) / (n + z * z)
    return [round(centre - half, 4), round(centre + half, 4)]


def _rate(left: int, n: int, probs: list[float]) -> dict:
    readable = n >= MIN_CELL
    return {"n": n, "left": left,
            "world_probability_mean": round(statistics.fmean(probs), 4) if readable else None,
            "left_ci95": _wilson(left, n) if readable else None}


def looked_by_saving(renewals: list[dict]) -> list[dict]:
    """Among the households that reached the renewal roll: does leaving rise with the saving?"""
    out = []
    for lo, hi, label in SAVING_BANDS:
        g = [r for r in renewals if r.get("price_differential_vs_market_reference") is not None
             and (lo is None or r["price_differential_vs_market_reference"] > lo)
             and (hi is None or r["price_differential_vs_market_reference"] <= hi)]
        out.append({"band": label, **_rate(sum(r["event_type"] == "churned" for r in g), len(g),
                                           [r["realized_churn_probability"] for r in g])})
    return out


def by_archetype_both_routes(renewals: list[dict], svt: list[dict], archetype: dict) -> list[dict]:
    """Per archetype: how often its households reached the renewal roll and left there, how fast
    they left the default tariff, and departures per household over the run. `archetype` maps
    each resi household on the book to its archetype; anything else is not counted."""
    from simulation.household import household_of

    out = []
    for name in ("active", "passive", "disengaged"):
        households = sum(a == name for a in archetype.values())
        rr = [r for r in renewals if archetype.get(household_of(r["customer_id"])) == name]
        ss = [r for r in svt if archetype.get(household_of(r["customer_id"])) == name]
        svt_years = sum(r["sim_segment_days"] for r in ss) / 365.25
        svt_left = sum(r["event_type"] != "stayed" for r in ss)
        roll_left = sum(r["event_type"] == "churned" for r in rr)
        out.append({
            "archetype": name, "households": households,
            "renewal_roll": _rate(roll_left, len(rr), [r["realized_churn_probability"] for r in rr]),
            "svt_years": round(svt_years, 1), "svt_left": svt_left,
            "svt_left_per_year": round(svt_left / svt_years, 4) if svt_years else None,
            "left_per_household": round((roll_left + svt_left) / households, 3) if households else None,
            # The world's own chance summed over every decision: what the dice average to. One run
            # of ~120 households cannot tell 0.05 from 0.12 a year by counting departures.
            "svt_world_probability_mean": round(statistics.fmean(
                r["realized_churn_probability"] for r in ss), 4) if ss else None,
            "expected_left_per_household": round(sum(
                r["realized_churn_probability"] for r in rr + ss) / households, 3) if households else None,
        })
    return out


def emerged() -> dict:
    """The capture's tables, or an absence with its reason -- never an empty table."""
    if not CAPTURE_PATH.is_file():
        return {"available": False, "reason": f"no world capture at {CAPTURE_PATH.name}"}
    from simulation import household_segments as hs
    from simulation.household import household_of
    from simulation.live_population import live_population

    cap = json.loads(CAPTURE_PATH.read_text(encoding="utf-8"))
    archetype = {household_of(p["customer_id"]): None for p in live_population()
                 if p.get("segment", "resi") == "resi"}
    archetype = {hh: hs.engagement_level_for_customer(hh).value for hh in archetype}
    renewals = [r for r in cap["renewals"] if household_of(r["customer_id"]) in archetype]
    return {
        "available": True,
        "captured_at_commit": cap["commit"],
        "renewal_decisions": len(renewals),
        "svt_decisions": len(cap["svt_segments"]),
        "by_archetype": by_archetype_both_routes(renewals, cap["svt_segments"], archetype),
        "looked_by_saving": looked_by_saving(renewals),
        "source": str(CAPTURE_PATH.relative_to(PROJECT)),
    }


def _headline(m: dict) -> str:
    d = m["disengaged_but_price_sensitive"]
    a = m["association"]
    return (
        f"Of the {d['disengaged']} disengaged households on the book -- the long-default tail, "
        f"the least likely to choose at a renewal -- {d['above_book_mean_elasticity']} are MORE price-sensitive than the "
        f"book's average household. Whether a household shops and how far price moves it once it "
        f"does are two different facts in this world: across {a['n']} households their rank "
        f"correlation is {a['rho']:+.2f}, inside the {a['null_low']:+.2f} to {a['null_high']:+.2f} "
        "that shuffling the pairs produces.")


def build() -> dict:
    from simulation.household_segments import (
        BILL_SHOCK_ENGAGEMENT_GAP,
        BILL_SHOCK_ENGAGEMENT_MULTIPLIER,
    )

    m = measure()
    return {
        "available": True,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        provenance_stamp.STAMP_KEY: provenance_stamp.stamp(READS, PROJECT),
        "headline": _headline(m),
        "definitions": {
            "engagement": "the probability a household enters a choice at a fixed-term renewal: "
                          "its persistent disposition to shop, times how much more or less its "
                          "payment method shops (Ofgem Consumer Impacts of Market Conditions "
                          "survey, wave 6)",
            "elasticity": "how far a price gap moves a household once it is choosing, as a weight "
                          "whose average over the book is 1.0",
        },
        "by_construction": (
            "The two are drawn independently for every household, so a correlation near zero is "
            "what the world is built to produce; the figure checks the build, it does not "
            "discover anything about real households. What it shows a reader is the consequence: "
            "disengagement here is not price-insensitivity."),
        "bill_shock_amplitude": {
            "established": BILL_SHOCK_ENGAGEMENT_MULTIPLIER is not None,
            "value": BILL_SHOCK_ENGAGEMENT_MULTIPLIER,
            # The reader's sentence, not the code's: `BILL_SHOCK_ENGAGEMENT_GAP` names a module
            # and a repo path, which mean nothing on a public page. Same three reasons, in order.
            "gap": None if BILL_SHOCK_ENGAGEMENT_MULTIPLIER is not None else (
                "no published study gives it; the nearest published figures (Ofgem's survey of "
                "households in arrears or finding bills hard to pay) describe a household's "
                "circumstances rather than its response to an event, and cannot be separated from "
                "the payment-method effect the world already applies; and the bill's size is not the "
                "trigger -- in 2022 every bill rose and switching collapsed"),
            "code_gap": BILL_SHOCK_ENGAGEMENT_GAP if BILL_SHOCK_ENGAGEMENT_MULTIPLIER is None else None,
        },
        "emerged_by_saving": emerged(),
        **m,
    }


def write() -> Path:
    """Measure and write the feed. The publish path's entry (`background/process_run_complete`)."""
    OUT_PATH.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    return OUT_PATH


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help=f"write {OUT_PATH.relative_to(PROJECT)}")
    args = ap.parse_args(argv)
    if args.write:
        print(f"wrote {write().relative_to(PROJECT)}")
    else:
        print(json.dumps(build(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
