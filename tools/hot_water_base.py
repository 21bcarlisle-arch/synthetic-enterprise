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

**IT SCALES WITH OCCUPANCY, AND THE FIRST VERSION OF THIS MODULE REFUSED TO -- WRONGLY.** That
refusal quoted the study's caveat that *"further modelling would be required to confirm the
relationship between hot-water and other characteristics such as occupants and floor area"* and read
it as doubt about whether the relationship exists. It is not. The same study says plainly, in its own
normalisation section: **"Hot water demand is known to be occupancy driven."** The caveat is about
the precise functional form, not about the sign.

The director's correction, and it is the general rule now:

    "Omission is not neutrality -- it asserts zero, and zero is usually the one value we know is
     wrong... a flat base per household is itself an assumption: it asserts occupancy has exactly
     zero effect, which is less defensible than a stated elasticity. So the real choice is a named
     parameter versus a hidden one, and we currently have the hidden one."

He is right. A per-household constant is not the absence of a belief about occupancy; it is the
belief that four people take the same number of showers as one, which is the one answer that is
certainly wrong.

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

# --- THE OCCUPANCY RELATIONSHIP, AS A NAMED AND MOVABLE PARAMETER -------------------------------
#
# SAP 2012 / BREDEM, the UK's own regulatory dwelling-energy model, gives daily hot-water volume as
#
#       Vd,average = 36 + 25 x N          litres per day, N = occupancy
#
# a FIXED part plus a PER-PERSON part. The structure matters as much as the numbers: some hot water
# is drawn whatever the headcount (a boiler's own draw-off, a sink run) and the rest is showers,
# which are per person.
#
# AND IT IS CORROBORATED BY THE MEASUREMENT, from a completely independent direction. SAP is
# normative -- what a compliance model assumes. DESNZ is 45,000 metered homes. At the occupancy of
# the prior EST study SAP predicts 36 + 25 x 2.4 = 96 L/day; DESNZ measures a median of 90.
# **Under seven per cent apart**, one a standard and one a measurement, which is the two-source
# agreement this project treats as an anchor rather than a coincidence.
#
# The implied physics checks out too, which is a third direction: matching the DESNZ median energy
# to the SAP volume needs 0.0437 kWh/litre, and raising a litre of water by 37.6 K takes exactly
# that -- a 10 C cold main to a 47.6 C tap. Nothing here had to be tuned to make that work.
#
# BOTH COEFFICIENTS ARE PARAMETERS, NOT CONSTANTS, and that is deliberate: `--sweep` moves them and
# `grade()` reports whether the resulting population still reproduces the DESNZ quartiles. A
# parameter we can move and grade is worth more than a number we are confident in.
HOT_WATER_FIXED_LITRES_PER_DAY = 36.0
HOT_WATER_LITRES_PER_PERSON_PER_DAY = 25.0

#: The occupancy SAP's own figures are stated at, and the one the DESNZ median corresponds to.
#: Used to re-centre the volume curve so the population median stays on the MEASURED value while the
#: SHAPE across occupancy comes from SAP.
REFERENCE_OCCUPANCY = 2.4


def occupancy_factor(people_count: float,
                     litres_per_person: float = HOT_WATER_LITRES_PER_PERSON_PER_DAY,
                     fixed_litres: float = HOT_WATER_FIXED_LITRES_PER_DAY) -> float:
    """How much hot water this household uses relative to the reference-occupancy one.

    SAP's `36 + 25N` re-centred on `REFERENCE_OCCUPANCY`, so a household at the reference sits on
    the DESNZ measured median and everything else scales around it. The result is SUB-LINEAR in
    headcount because of the fixed term -- four people use about 1.5x the hot water of two, not 2x,
    which is what the fixed draw-off implies and what makes this a relationship rather than a
    proportionality.
    """
    reference = fixed_litres + litres_per_person * REFERENCE_OCCUPANCY
    return (fixed_litres + litres_per_person * max(0.0, people_count)) / reference


def draw_daily_kwh(rng, month: int = 1, people_count: float | None = None,
                   litres_per_person: float = HOT_WATER_LITRES_PER_PERSON_PER_DAY) -> float:
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
    if people_count is None:
        return float(rng.lognormvariate(math.log(median), sigma))

    # THE RESIDUAL IS NARROWED SO THE TOTAL SPREAD STAYS ON THE MEASUREMENT. The published
    # quartiles are a MARGINAL across all households and already contain the occupancy spread;
    # multiplying a draw from that marginal by an occupancy factor would count the same variation
    # twice and give a population more dispersed than the one that was measured. What occupancy
    # explains comes out of the residual, and the two together reproduce the measured sigma.
    verdict = grade(litres_per_person)
    residual = verdict["residual_log_variance"]
    if residual <= 0:
        # The coefficient explains more than the whole measured spread -- refuted by the
        # measurement. Fall back to no residual rather than an imaginary standard deviation, and
        # let `grade()` be the thing that says so.
        residual = 0.0
    drawn = float(rng.lognormvariate(math.log(median), math.sqrt(residual)))
    return drawn * occupancy_factor(people_count, litres_per_person)


def annual_kwh(rng, people_count: float | None = None,
               litres_per_person: float = HOT_WATER_LITRES_PER_PERSON_PER_DAY) -> float:
    """A household's hot-water gas for a year, summing the seasonal shape."""
    return sum(draw_daily_kwh(rng, month=m, people_count=people_count,
                              litres_per_person=litres_per_person) * 30.4 for m in range(1, 13))


#: England-and-Wales household-size shares, Census 2021 TS017, as `dwelling_records` already holds
#: them. Used to work out how much of the measured spread OCCUPANCY alone accounts for.
HOUSEHOLD_SIZE_SHARE = ((1, 0.301), (2, 0.340), (3, 0.160), (4, 0.129), (5, 0.070))


def grade(litres_per_person: float = HOT_WATER_LITRES_PER_PERSON_PER_DAY) -> dict:
    """Is this per-person coefficient CONSISTENT with the measured distribution?

    THE TRAP THIS EXISTS TO AVOID, and it is easy to walk into: the DESNZ quartiles are a MARGINAL
    distribution across all households, so they ALREADY CONTAIN the spread that occupancy causes.
    Multiplying a draw from that marginal by an occupancy factor counts the same variation twice and
    produces a population more dispersed than the one that was measured.

    So the occupancy factor is not free: the variance it introduces must fit INSIDE the measured
    variance, and what is left over is the residual spread between households of the SAME size.

    I WROTE THAT THIS MAKES THE PARAMETER FALSIFIABLE AND IT DOES NOT. Correcting it here rather
    than quietly: `occupancy_factor` is a RATIO, so as the coefficient grows it converges on
    `N / 2.4` and its variance converges with it. Household size in the English stock varies too
    little for even PERFECT PROPORTIONALITY to account for the measured spread -- the ceiling is
    **31.8%**, reached at an infinite coefficient. The residual therefore never goes negative and
    **this measurement can refute no value of the parameter.** The guard below is kept because it
    costs nothing and a future measurement with a wider spread would make it live.

    What 25 L/person rests on is SAP 2012 / BREDEM, corroborated by DESNZ at the reference
    occupancy to within 7%. What would refute it is a study measuring hot water AGAINST KNOWN
    OCCUPANCY -- the named gap, since DESNZ metered without knowing who lived there.
    """
    import math
    import statistics

    low, high = HOT_WATER_KWH_PER_DAY["september"], HOT_WATER_KWH_PER_DAY["may"]
    # Log-scale spread of the measured marginal, averaged over the two published seasons.
    total_sigma = statistics.mean(
        math.log(band["p75"] / band["p25"]) / (2 * 0.6745) for band in (low, high))

    logs = [math.log(occupancy_factor(n, litres_per_person)) for n, _ in HOUSEHOLD_SIZE_SHARE]
    weights = [w for _, w in HOUSEHOLD_SIZE_SHARE]
    mean_log = sum(x * w for x, w in zip(logs, weights))
    occupancy_var = sum(w * (x - mean_log) ** 2 for x, w in zip(logs, weights))
    residual_var = total_sigma ** 2 - occupancy_var

    return {
        "litres_per_person_per_day": litres_per_person,
        "measured_log_sigma": round(total_sigma, 4),
        "share_of_spread_explained_by_occupancy": round(occupancy_var / total_sigma ** 2, 4),
        "residual_log_variance": round(residual_var, 5),
        "consistent_with_measurement": bool(residual_var > 0),
        "four_vs_two_person_ratio": round(
            occupancy_factor(4, litres_per_person) / occupancy_factor(2, litres_per_person), 3),
    }


def sweep(values=(0.0, 10.0, 25.0, 40.0, 60.0, 90.0)) -> list[dict]:
    """The parameter's plausible range, measured rather than asserted.

    `0.0` is the OLD BEHAVIOUR -- a flat per-household base -- and it appears here as one value of
    the parameter rather than as the absence of one, which is the director's point: omission is a
    choice of zero.
    """
    return [grade(v) for v in values]


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
        "occupancy": grade(),
        "not_covered": ["cylinder standing loss", "cooking"],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--sweep", action="store_true",
                    help="the per-person coefficient's plausible range, graded")
    args = ap.parse_args(argv)
    if args.sweep:
        print(json.dumps(sweep(), indent=2))
        return 0
    if args.measure:
        print(json.dumps(measurement(), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
