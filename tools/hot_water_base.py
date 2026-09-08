"""The gas base load -- hot water and cooking -- drawn from measurement, not from physics.

REUSE: tools/hot_water_base.py
CLASS: CUSTOM
INDEX: searched "hot water", "base load", "cooking", "gas base", "standing loss".
       `simulation/fabric_physics.py` models SPACE HEAT and deliberately has no hot-water term.
       `simulation/demand_model.py` owns electricity shape. Nothing models the gas base.

WHY THIS IS DRAWN AND NOT DERIVED
---------------------------------
Director, 2026-09-08, setting the rule this module obeys:

    "Theorise where the physics is solid -- heat loss, delta-T, boiler efficiency curves. Don't
     theorise where it's behaviour, and hot water is behaviour."

He is right, and the published record proves it: hot-water shares of domestic gas disagree by a
factor of two across sources (12% for combi boilers in one 2018-2024 daily-data study, 15-25% in the
ECUK-consistent range). Nobody has settled it, and cylinder standing loss and shower duration are
not derivable from fabric.

THE SOURCE, AND IT IS BETTER THAN SERL FOR THIS PURPOSE
--------------------------------------------------------
DESNZ, *Domestic hot-water use: observations on hot-water use from connected devices*, March 2024.
**45,000 homes** drawn from 115,000, sub-daily gas end-use monitoring on GAS COMBINATION BOILERS --
62.6% of UK homes. It gives what a model needs and a headline share does not: a DISTRIBUTION, a
seasonal swing, and a time-of-day profile.

    daily hot-water energy   median 3.9 kWh (September) rising to 4.5 kWh (May), +0.6 kWh / +16%
    interquartile range      1.9-6.6 kWh and 2.1-8.0 kWh at those two points
    daily volume             19-222 L, median 90 L (down from 104 L in the 2008 EST study)
    event duration           4.7-7.5 minutes, median 6.7
    time of day              peaks 06:00-08:00 and 17:00-19:00

SERL was considered and is NOT the source here. Its Observatory carries half-hourly gas for 13,000
households, but access needs accredited-researcher status, university ethics approval and a two-to-
three month lead -- a real-world application the director has already declined once. The DESNZ study
is open, larger, and end-use DISAGGREGATED, which SERL's meter-level data is not: SERL would give
total gas and leave the base-versus-heating split to be inferred.

WHAT THIS DOES NOT COVER, NAMED
--------------------------------
**Combi boilers only.** Cylinders are outside the sample, so STANDING LOSS is unmeasured here and is
not modelled -- inventing it would be theorising a behaviour-and-hardware term, which is the thing
the rule forbids.

**The occupancy relationship is NOT established, and the study says so itself:** *"Further modelling
would be required to confirm the relationship between hot-water and other characteristics such as
occupants and floor area."* So this module draws from the published distribution and does NOT scale
by household size. That is a deliberate refusal: the intuition that four people use twice the hot
water of two is exactly the kind of plausible unanchored term that has cost this project repeatedly,
and the one study large enough to settle it declined to.

**Cooking is not separated.** ECUK-consistent figures put it at 5-10% of domestic gas; this base is
hot water as measured, and cooking is left in the named residual rather than split on a guess.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

#: DESNZ March 2024, daily hot-water ENERGY. Median and interquartile range at the seasonal
#: extremes. September is the low point and May the high one, which is the study's own framing.
HOT_WATER_KWH_PER_DAY = {
    "september": {"median": 3.9, "p25": 1.9, "p75": 6.6},
    "may": {"median": 4.5, "p25": 2.1, "p75": 8.0},
}

#: The seasonal swing, as the study states it: +0.6 kWh/day, a 16% increase, driven by colder mains
#: water rather than by behaviour.
HOT_WATER_SEASONAL_SWING_KWH = 0.6

#: Peak draw-off windows, as half-hourly settlement periods. 06:00-08:00 and 17:00-19:00.
HOT_WATER_PEAKS = ((12, 16), (34, 38))

#: Share of UK homes with a gas combination boiler (BSRIA 2022, quoted by the study). The figure
#: this distribution can honestly speak for.
COMBI_SHARE_OF_HOMES = 0.626


def draw_daily_kwh(rng, month: int = 1) -> float:
    """One household's hot-water energy for a day, drawn from the published distribution.

    A LOGNORMAL FITTED TO THE PUBLISHED QUARTILES, not a normal: the reported range is 1.9 to 8.0
    kWh around a median of 3.9-4.5, which is strongly right-skewed and would go negative under a
    normal wide enough to reach 8.
    """
    import math

    # Linear in the seasonal swing between the two published points; September is month 9 and May
    # month 5, so the swing is expressed on the calendar rather than on a heating-season index.
    winter_weight = abs(((month - 9) % 12) / 12.0 * 2 - 1)
    low, high = HOT_WATER_KWH_PER_DAY["september"], HOT_WATER_KWH_PER_DAY["may"]
    median = low["median"] + (high["median"] - low["median"]) * winter_weight
    p25 = low["p25"] + (high["p25"] - low["p25"]) * winter_weight
    p75 = low["p75"] + (high["p75"] - low["p75"]) * winter_weight

    # sigma from the published quartile ratio: log(p75/p25) = 2 * 0.6745 * sigma
    sigma = math.log(p75 / p25) / (2 * 0.6745)
    return float(rng.lognormvariate(math.log(median), sigma))


def annual_kwh(rng) -> float:
    """A household's hot-water gas for a year, summing the seasonal shape."""
    return sum(draw_daily_kwh(rng, month=m) * 30.4 for m in range(1, 13))


def measurement(n: int = 20000, seed: int = 0) -> dict:
    import random
    import statistics

    rng = random.Random(seed)
    annual = [annual_kwh(rng) for _ in range(n)]
    daily_jan = sorted(draw_daily_kwh(rng, 1) for _ in range(n))
    return {
        "source": "DESNZ Domestic hot-water use, March 2024; 45,000 homes, gas combi boilers",
        "annual_kwh_median": round(statistics.median(annual)),
        "annual_kwh_p25": round(annual[int(0.25 * n)] if False else sorted(annual)[n // 4]),
        "annual_kwh_p75": round(sorted(annual)[3 * n // 4]),
        "january_daily_median": round(statistics.median(daily_jan), 2),
        "january_daily_iqr": [round(daily_jan[n // 4], 2), round(daily_jan[3 * n // 4], 2)],
        "combi_share_of_homes": COMBI_SHARE_OF_HOMES,
        "not_covered": ["cylinder standing loss", "cooking", "scaling by household size"],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--measure", action="store_true")
    args = ap.parse_args(argv)
    if args.measure:
        print(json.dumps(measurement(), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
