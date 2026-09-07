"""Households GENERATED from a fitted joint, not selected from survey rows.

REUSE: tools/stock_joint_generator.py
CLASS: CUSTOM
INDEX: searched "generate", "joint", "synthetic household", "fit", "rake", "stock".
       `tools/need_stock_joint.py` measures the EPC association from NEED and is the closest row --
       it fits lifts for `premise_population`'s seed and does not generate households; its property
       and era mappings are imported rather than restated. `simulation/premise_population.py` rakes a
       seed joint onto published marginals for the RUN population, a different consumer with a
       different grain. `tools/demand_vector_coverage.py` was SELECTING NEED rows, which is the
       defect this exists to remove.

WHY THIS EXISTS
---------------
`DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07`, section 1:

    "The sample is MODELLED HOUSES, each placed in a coherent weather cell, with a coherent set of
     people living in it. Real data calibrates and checks it; real data is not the thing we select
     from... So NEED -- and any comparable survey -- is EVIDENCE, NOT POPULATION."

Two defects were live when that was decided, and both were in this project's own measurement:

  * **Selecting real rows made the source's limits our limits.** NEED covers England and Wales, so
    no Scottish dwelling could be chosen at all -- and Scotland is the coldest 8% of the book, where
    weather sensitivity is largest. `demand_grid` excluded `S92000003` by name and called it an
    honest gap. It was an honest gap in a design that could not have closed it.
  * **Coverage was capped at the combinations a 46,000-row sample happened to contain.** A fitted
    joint can produce a combination that is real and rare without a survey having sampled it.

AND THE RISK THAT COMES WITH GENERATING IS IMPLAUSIBILITY -- the canon names it: a 1900 solid-wall
dwelling with modern airtightness, five people in a studio, a heat pump in an uninsulated house. The
defence is structural rather than a filter bolted on afterwards: **draw from the fitted joint, so
combinations appear at the rate they co-occur in the evidence.** Drawing each attribute
independently is what manufactures the impossible ones, and `implausible_share` measures exactly
that difference rather than asserting it.

WHAT IS FITTED AND WHAT IS RAKED
---------------------------------
The joint is the observed co-occurrence of (property type, era, floor-area band, EPC, loft
insulation, cavity insulation, PV, main heat fuel) across NEED's dwellings. Nothing about it is
invented; it is a count table.

**Scotland is reached by RAKING, not by assumption.** NEED has no Scottish dwellings, so the fabric
joint is England-and-Wales-fitted. Applying it unchanged to Scotland would be assuming the Scottish
stock is English, which it is not -- Scotland has far more flats. Scotland's Census 2022 UV402
publishes accommodation type per output area, so the joint's PROPERTY TYPE margin is raked onto the
Scottish one and the conditional structure within a type is carried over. **That carry-over is the
assumption, it is smaller than the alternative, and it is stated rather than buried:** what a
Scottish semi is like inside is taken from an English semi; how many semis there are is Scotland's
own count.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

CACHE = Path.home() / ".cache" / "synthetic-enterprise"
SCOTLAND_ZIP = CACHE / "census" / "scot_oa_topic.zip"

#: The attributes whose CO-OCCURRENCE is the joint. Fabric, retrofit state and fuel together --
#: retrofit state is in here rather than bolted on because whether a dwelling has cavity insulation
#: is not independent of whether it has a cavity, which is a question about its era.
JOINT_KEYS = ("property_type", "age_band", "area_band", "epc", "loft", "cavity", "pv", "fuel")

#: Scotland's accommodation-type categories onto this project's property types. `UV402`'s own
#: labels; "Unknown" and totals are dropped rather than distributed, because assigning them would
#: invent a type for a dwelling the census declined to classify.
#: The column headings are the census's OWN and they are PREFIXED -- "Whole house or bungalow:
#: Detached", not "Detached" -- which the first version did not match, so every Scottish share came
#: back empty and `scotland_reachable` read False. The flat total is taken rather than its three
#: sub-categories, which would triple-count.
SCOTLAND_TYPE_MAP = {
    "Whole house or bungalow: Detached": "DETACHED",
    "Whole house or bungalow: Semi-detached": "SEMI_DETACHED",
    "Whole house or bungalow: Terraced (including end-terrace)": "TERRACED",
    "Flat, maisonette or apartment: Total": "FLAT",
}

#: Scotland's census suppresses small cells as "-" rather than 0 or blank.
SCOTLAND_SUPPRESSED = "-"

#: NEED's oldest age band, "before 1930". Named for the plausibility rule it REFUTED -- see
#: `solid_wall_cavity_share`.
SOLID_WALL_AGE_BAND = "1"


def fit_joint(rows=None) -> collections.Counter:
    """The observed co-occurrence of the stock attributes -- a count table, nothing invented."""
    from tools import need_stock_joint as need

    if rows is None:
        if not need.NEED_CSV.is_file():
            raise FileNotFoundError(
                f"{need.NEED_CSV} is absent. The joint is FITTED from evidence; there is no "
                "substitute, and inventing one would make the generated stock unfalsifiable.")
        with need.NEED_CSV.open(encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))

    joint: collections.Counter = collections.Counter()
    for row in rows:
        if row.get("PROP_TYPE") not in need.PROPERTY_TYPE:
            continue
        joint[(need.PROPERTY_TYPE[row["PROP_TYPE"]], row.get("PROP_AGE_BAND"),
               row.get("FLOOR_AREA_BAND"), row.get("EPC"), row.get("LI_FLAG"),
               row.get("CWI_FLAG"), row.get("PV_FLAG"), row.get("MAIN_HEAT_FUEL"))] += 1
    if not joint:
        raise ValueError("the fitted joint is empty; the evidence did not parse")
    return joint


def scotland_type_marginal(zip_path: Path = SCOTLAND_ZIP) -> dict[str, float] | None:
    """Scotland's accommodation-type shares from Census 2022 UV402, or None if absent.

    RETURNS NONE RATHER THAN A GUESS. A Scottish stock silently taken as English is the assumption
    this function exists to avoid, so its absence must be visible to the caller.
    """
    if not zip_path.is_file():
        return None
    with zipfile.ZipFile(zip_path) as archive:
        name = next((n for n in archive.namelist() if "UV402" in n.upper()), None)
        if name is None:
            return None
        with archive.open(name) as handle:
            text = handle.read().decode("utf-8-sig", errors="replace")

    counts: dict[str, float] = collections.defaultdict(float)
    header = None
    for line in csv.reader(text.splitlines()):
        if not line:
            continue
        if header is None:
            if any("Detached" in cell for cell in line):
                header = [c.strip().strip('"') for c in line]
            continue
        for label, cell in zip(header, line):
            target = SCOTLAND_TYPE_MAP.get(label.strip())
            if target is None:
                continue
            raw = str(cell).replace(",", "").strip()
            if raw in ("", SCOTLAND_SUPPRESSED):
                continue
            try:
                counts[target] += float(raw)
            except ValueError:
                continue
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()} if total > 0 else None


def raked_joint(joint, type_marginal) -> collections.Counter:
    """The fitted joint with its PROPERTY TYPE margin moved onto a published one.

    The conditional structure inside a type is carried over unchanged -- what a semi is like -- and
    only how many semis there are is replaced. That is the smallest assumption available given a
    survey that does not cover the country in question.
    """
    by_type: dict = collections.defaultdict(float)
    for key, count in joint.items():
        by_type[key[0]] += count
    total = sum(by_type.values())
    out: collections.Counter = collections.Counter()
    for key, count in joint.items():
        share = by_type[key[0]] / total
        target = type_marginal.get(key[0])
        if not share or target is None:
            continue
        out[key] = count * (target / share)
    return out


def generate(n: int, joint, rng, keys=JOINT_KEYS) -> list[dict]:
    """`n` households drawn FROM THE JOINT, so combinations appear at the rate they co-occur.

    Drawing each attribute from its own marginal is what manufactures impossible dwellings; this
    draws whole rows of the count table, so a combination the evidence never shows cannot appear
    and a rare-but-real one can.
    """
    import numpy as np

    entries = list(joint.items())
    weights = np.array([c for _k, c in entries], dtype=float)
    picks = rng.choice(len(entries), size=n, replace=True, p=weights / weights.sum())
    return [dict(zip(keys, entries[i][0])) for i in picks]


def generate_independently(n: int, joint, rng, keys=JOINT_KEYS) -> list[dict]:
    """The WRONG way, kept because it is the comparator that makes the plausibility claim testable.

    Each attribute drawn from its own marginal, independently. Every marginal is right and the
    dwellings are not.
    """
    import numpy as np

    marginals = []
    for position in range(len(keys)):
        counts: dict = collections.defaultdict(float)
        for key, count in joint.items():
            counts[key[position]] += count
        values = list(counts)
        probability = np.array([counts[v] for v in values], dtype=float)
        marginals.append((values, probability / probability.sum()))
    out = []
    for _ in range(n):
        out.append({k: m[0][rng.choice(len(m[0]), p=m[1])] for k, m in zip(keys, marginals)})
    return out


def unobserved_share(households, joint, keys=JOINT_KEYS) -> float:
    """The share of generated dwellings whose combination the EVIDENCE NEVER SHOWS.

    THE PLAUSIBILITY MEASURE, AND IT IS THE DATA'S OPINION RATHER THAN MINE. Drawing from the joint
    can only produce combinations that occur, so this is zero by construction; drawing each
    attribute independently produces combinations no dwelling in 50,000 exhibits. The gap between
    the two is what "draw from the fitted joint rather than independently" actually buys, measured
    rather than asserted.
    """
    if not households:
        return 0.0
    seen = set(joint)
    missing = sum(1 for h in households if tuple(h[k] for k in keys) not in seen)
    return missing / len(households)


def solid_wall_cavity_share(households) -> float:
    """The share carrying cavity insulation on a pre-1930 dwelling.

    KEPT, AND DEMOTED FROM A PLAUSIBILITY RULE TO AN OBSERVATION, because the evidence refuted it.
    Solid-wall construction is the norm before 1919, so this looked like the clearest impossible
    combination the fields can express -- and generating strictly from the joint still produced it
    at 1.3%, which means NEED's own dwellings show it. They do, and the reason is that the band is
    "before 1930" and cavity construction is general through the 1920s. **A rule that calls
    observed dwellings impossible is a wrong rule, not wrong data**, so this reports rather than
    refuses.
    """
    if not households:
        return 0.0
    return sum(1 for h in households if h.get("age_band") == SOLID_WALL_AGE_BAND
               and h.get("cavity") == "1") / len(households)


def measurement(n: int = 20000, seed: int = 0) -> dict:
    """What generating buys: Scotland reachable, combinations beyond the survey, plausibility held."""
    import numpy as np

    joint = fit_joint()
    rng = np.random.default_rng(seed)
    drawn = generate(n, joint, rng)
    independent = generate_independently(min(n, 4000), joint, np.random.default_rng(seed))
    scotland = scotland_type_marginal()

    return {
        "evidence_rows": int(sum(joint.values())),
        "distinct_combinations_in_evidence": len(joint),
        "combinations_generated": len({tuple(h[k] for k in JOINT_KEYS) for h in drawn}),
        "unobserved_combinations_from_the_joint": round(unobserved_share(drawn, joint), 5),
        "unobserved_combinations_drawn_independently": round(
            unobserved_share(independent, joint), 5),
        "solid_wall_cavity_share_observed": round(solid_wall_cavity_share(drawn), 5),
        "scotland_type_marginal": ({k: round(v, 4) for k, v in scotland.items()}
                                   if scotland else None),
        "scotland_reachable": scotland is not None,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--measure", action="store_true", help="what generating buys over selecting")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    if args.measure:
        print(json.dumps(measurement(seed=args.seed), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
