"""The physical people layer: what a postcode tells you about a household, and what it cannot.

REUSE: tools/people_physical_layer.py
CLASS: CUSTOM
INDEX: searched "occupancy", "household size", "presence", "people", "small area", "prior".
       `simulation/demand_model.py` owns occupancy -> volume and the daytime shape, and is the
       CONSUMER this conditions -- `people_count` reaches consumption there already; what does not
       exist is where that count comes from. `tools/weather_cell_weights.py` pulls Census TS041
       (household COUNTS per output area) from nomis and its paging is reused, not re-derived.
       `simulation/population_draw.py` draws traits INDEPENDENTLY, which is the thing this replaces
       for the physical axes. Nothing conditions a household's composition on its geography.

WHY THIS EXISTS
---------------
People ruling, and `DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07` section 4:

    "layer one is the household you would EXPECT given the postcode and the house (published at
     small-area level, therefore guessable by the company from an address); layer two is how this
     household DEVIATES from that (the single pensioner in the four-bed, the five people in the
     two-bed flat) -- private, and what the company must DISCOVER."

And the canon's separation, which binds hardest:

    "The PHYSICAL layer drives kWh and shape: occupancy count, presence pattern, heating schedule
     and setpoint, appliance and asset ownership. The COMMERCIAL layer drives payment, arrears,
     churn and elasticity... Merged, we cannot tell a household that used less because nobody was
     home from one that could not afford it -- and those demand the opposite response."

**THIS MODULE IS THE PHYSICAL LAYER ONLY.** No income, no payment method, no attitude, no arrears.
Not because they do not matter but because merging them is the defect the canon names.

WHAT IS ALREADY HERE AND IS NOT REBUILT
----------------------------------------
Three of the four physical quantities already exist and are anchored:

  * **heating schedule and setpoint** -- `fabric_physics.heating_schedule_for`, drawn per premise.
  * **presence pattern** -- `demand_model._daytime_occupancy_rate`, EFUS-anchored on household size
    with published pensioner and employment cuts.
  * **occupancy -> consumption** -- `demand_model.need_volume_index` and the daytime multiplier.

What does NOT exist is the JOINT: `people_count` is consumed everywhere and conditioned on nothing,
so the world draws a household size independent of the address it sits at. The ruling's whole point
is that a supplier CAN see the address, so the prior is knowable and only the deviation is not.

THE MEASUREMENT THAT DECIDES HOW MUCH THIS IS WORTH
-----------------------------------------------------
Census TS017 publishes household size per output area for every one of England and Wales's 188,880
output areas. That makes the two layers separable and MEASURABLE rather than assumed:

    BETWEEN output areas   the PRIOR -- what an address tells you before you meter anything
    WITHIN an output area  the RESIDUAL -- what the company must discover per household

The ratio is what says whether address-based inference is worth building at all. It is reported
rather than assumed, because "geography is the coherence key" is a claim about a number nobody in
this project had looked at.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

CACHE = Path.home() / ".cache" / "synthetic-enterprise" / "people"
TS017_CSV = CACHE / "ts017_household_size_by_oa21.csv"

#: Census 2021 TS017, household size by 2021 output area, via nomis. `TYPE150` is the output-area
#: geography, `measures=20100` the count. Dimension `C2021_HHSIZE_10` was read from the dataset
#: definition rather than guessed: its codes are 0 = total, 1 = "0 people", and 2..9 = one through
#: eight-or-more people. THE ROW ORDER LOOKS LIKE IT WOULD TELL YOU THE SAME THING and must not be
#: relied on -- the first probe came back with the category column EMPTY because the dimension name
#: was wrong, and the arithmetic still worked out, which is exactly how a positional read gets
#: adopted and then silently breaks.
NOMIS_TS017 = ("https://www.nomisweb.co.uk/api/v01/dataset/NM_2037_1.data.csv"
               "?geography=TYPE150&measures=20100"
               "&select=geography_code,c2021_hhsize_10,obs_value")

#: `weather_cell_weights` learned this the expensive way: nomis caps an unpaged request at 25,000
#: rows and says so nowhere in the payload. Same page size, same refusal on a short total.
NOMIS_PAGE = 25_000
TS017_EXPECTED_AREAS = 188_880

#: Code -> people in the household. 0 (total) and 1 ("0 people", always zero) are deliberately not
#: here: a total is not a size, and folding it in would double every count.
HOUSEHOLD_SIZE_BY_CODE = {"2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6, "8": 7, "9": 8}

#: The open top category is "8 or more people". 8 is what it is called and what is used; the true
#: mean of that tail is higher and unpublished at this geography. It holds about 0.1% of households,
#: so the effect on any mean is under a person-tenth -- stated rather than silently taken as exact.
TOP_CATEGORY_IS_OPEN = True


def pull(dest: Path = TS017_CSV, progress=print) -> Path:
    """Fetch TS017 at output-area level, paged, then refuse a short answer."""
    import urllib.request

    dest.parent.mkdir(parents=True, exist_ok=True)
    rows: list[str] = []
    header = ""
    offset = 0
    while True:
        url = f"{NOMIS_TS017}&RecordLimit={NOMIS_PAGE}&RecordOffset={offset}"
        with urllib.request.urlopen(url, timeout=600) as response:
            lines = response.read().decode("utf-8-sig").splitlines()
        if not lines:
            break
        header = header or lines[0]
        body = [ln for ln in lines[1:] if ln.strip()]
        rows.extend(body)
        progress(f"[people] ts017 {len(rows):,} rows")
        if len(body) < NOMIS_PAGE:
            break
        offset += NOMIS_PAGE

    areas = {ln.split(",")[0] for ln in rows}
    if len(areas) < TS017_EXPECTED_AREAS:
        raise RuntimeError(
            f"nomis returned {len(areas):,} output areas, expected {TS017_EXPECTED_AREAS:,}. "
            "A short answer here is SILENT: the CSV is well formed and the prior it produces looks "
            "plausible while describing a fraction of England.")
    dest.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    progress(f"[people] ts017 -> {dest} ({len(rows):,} rows, {len(areas):,} areas)")
    return dest


def size_distribution_by_area(path: Path = TS017_CSV) -> dict[str, dict[int, int]]:
    """{output area: {people in household: households}} -- the PRIOR, as published.

    REFUSES ON ABSENCE rather than falling back to a national distribution. A national prior is
    exactly the independent draw this replaces, and it would be indistinguishable in every output
    from a conditioned one that happened to have no data.
    """
    if not path.is_file():
        raise FileNotFoundError(
            f"{path} is absent. The physical layer's prior is Census TS017 by output area; the only "
            "fallback is a national distribution, which IS the independent draw this replaces. "
            "Run `python3 tools/people_physical_layer.py --pull`.")
    out: dict[str, dict[int, int]] = {}
    with path.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            code = str(row["C2021_HHSIZE_10"]).strip().strip('"')
            size = HOUSEHOLD_SIZE_BY_CODE.get(code)
            if size is None:
                continue
            area = row["GEOGRAPHY_CODE"].strip().strip('"')
            try:
                count = int(float(row["OBS_VALUE"]))
            except (TypeError, ValueError):
                continue
            out.setdefault(area, {})[size] = count
    return out


def prior_and_residual(by_area=None) -> dict:
    """How much of household-size variation an ADDRESS explains, and how much it cannot.

    THE RULING'S TWO LAYERS, AS A VARIANCE DECOMPOSITION. Total variation in household size splits
    exactly into the spread of output-area MEANS (between -- what a postcode tells you) and the
    spread WITHIN each area (what it does not). The law of total variance makes the split exact
    rather than a modelling choice, which is why it can be reported as a fact about Britain.

    A LOW BETWEEN-SHARE IS A FINDING, NOT A FAILURE. It would say the address is a weak predictor of
    who lives there and the company must meter to know -- which is a real answer to "is
    address-based inference worth building", and the opposite of what the ruling assumes.
    """
    by_area = by_area if by_area is not None else size_distribution_by_area()

    grand_n = 0
    grand_sum = 0.0
    grand_sq = 0.0
    between = 0.0
    within = 0.0
    area_means = []
    for counts in by_area.values():
        n = sum(counts.values())
        if n <= 0:
            continue
        total = sum(size * c for size, c in counts.items())
        sq = sum(size * size * c for size, c in counts.items())
        mean = total / n
        area_means.append((n, mean))
        grand_n += n
        grand_sum += total
        grand_sq += sq
        within += sq - n * mean * mean

    if grand_n == 0:
        raise ValueError("no households in the prior; the pull is empty or mis-parsed")
    grand_mean = grand_sum / grand_n
    for n, mean in area_means:
        between += n * (mean - grand_mean) ** 2
    total_variance = grand_sq - grand_n * grand_mean * grand_mean

    return {
        "households": grand_n,
        "output_areas": len(area_means),
        "mean_household_size": round(grand_mean, 4),
        "variance_total": round(total_variance / grand_n, 5),
        "variance_between_areas": round(between / grand_n, 5),
        "variance_within_area": round(within / grand_n, 5),
        "share_explained_by_address": round(between / total_variance, 4),
        "share_the_company_must_discover": round(within / total_variance, 4),
        "top_category_is_open": TOP_CATEGORY_IS_OPEN,
    }


def draw_size(area: str, rng, by_area=None) -> int:
    """One household's size, drawn from ITS OWN output area's published distribution.

    THE PRIOR IS THE DRAW, and the residual is what the draw's spread already contains: sampling
    within the area's own distribution reproduces both layers without inventing a deviation model.
    An area absent from the census refuses rather than falling back to the national mixture -- see
    `size_distribution_by_area`.
    """
    by_area = by_area if by_area is not None else size_distribution_by_area()
    counts = by_area.get(area)
    if not counts:
        raise KeyError(
            f"output area {area!r} is not in Census TS017. Falling back to the national "
            "distribution here would silently restore the independent draw this replaces.")
    sizes = sorted(counts)
    weights = [counts[s] for s in sizes]
    total = sum(weights)
    if total <= 0:
        raise ValueError(f"output area {area!r} publishes no households")
    pick = rng.random() * total
    running = 0.0
    for size, weight in zip(sizes, weights):
        running += weight
        if pick < running:
            return size
    return sizes[-1]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pull", action="store_true", help="fetch Census TS017 by output area")
    ap.add_argument("--split", action="store_true",
                    help="what an address explains, and what it cannot")
    args = ap.parse_args(argv)
    if args.pull:
        pull()
    if args.split:
        print(json.dumps(prior_and_residual(), indent=2))
    if not (args.pull or args.split):
        ap.print_help(sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
