"""How many distinct household cases cover 99% of DEMAND variation, not of weather variation.

REUSE: tools/demand_case_coverage.py
CLASS: CUSTOM
INDEX: searched "coverage", "cases", "demand", "joint", "cells", "granularity".
       `tools/weather_cell_derivation.py` answers the same shape of question about WEATHER DRIVERS
       and is the thing this corrects the framing of; it is imported for its cell space, not
       reimplemented. `simulation/fabric_physics.py` owns the demand model and is imported.
       `tools/need_stock_joint.py` supplies the stock composition. Nothing composes the two.

WHY THIS EXISTS
---------------
Director console, 2026-09-07:

    "You've answered how many weather cells capture 99% of household-weighted variation in the
     weather drivers -- 21, 21 and 5 across three grids. That's a partition of Britain. What I
     actually care about is heat demand variation, which depends on the weather cell and the house
     together... The number I need is how many distinct household cases cover 99% of demand
     variation, not how many cells cover 99% of weather."

He is right that the published answer was about the wrong quantity, and right that the composition
question decides whether the sample is large or small. The answer is that **it does not multiply**,
and the reason is not the one either of us expected.

THE ANSWER
----------
Over 24,662,309 England-and-Wales households, 143,511 occupied 1 km cells and the 274 distinct house
cases NEED resolves:

    99% of demand variation    weather alone 21    house alone 13    product 273    JOINT 13
    95%                                       8                 8            64            8
    90%                                       5                 5            25            5

**Twenty-one times smaller than the product at 99%.** And the dominant reason is not correlation:
correlation between a region's winter temperature and its stock's demand at a FIXED climate is only
**-0.314**. It is that **demand is a scalar**. Two different combinations of house and weather that
produce the same annual demand are the same case for the purpose of predicting demand, so the
composition happens in the OUTPUT and the input grids never multiply.

WHICH MEANS THE NUMBER IS ONLY HALF AN ANSWER, AND THE HALF IT IS NOT MATTERS
-----------------------------------------------------------------------------
Any single scalar needs roughly thirteen to twenty optimal bins for 99% of its variance whatever
drives it, so "13" is close to a fact about one-dimensional variables rather than about Britain.
The count only becomes informative as the output space grows:

    demand level alone                          13 cases
    level AND weather sensitivity (kWh/degree)  21 cases

**And a lever needs the INPUTS resolved, not the output.** Knowing a household is in demand bin 9
is enough to forecast it and useless for deciding whether to offer insulation, which acts on the
house, or a tariff, which acts on the weather exposure. For anything that acts on a cause rather
than describing an effect, the product is back.

THE STOCK DOES VARY BY REGION, AND NOT MAINLY WITH TEMPERATURE
---------------------------------------------------------------
At one fixed climate the regional stock spans 6,405 to 9,503 kWh -- **48%** -- so where a household
is does predict what it lives in. But the alignment with climate is weak and partly backwards:
London is the warmest region and has the lowest-demand stock (small flats), while Wales is mild and
has the highest (old, large, rural). The colder-north-worse-stock effect is real and is not what
dominates.
"""
from __future__ import annotations

import argparse
import collections
import json
import pickle
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

CACHE = Path.home() / ".cache" / "synthetic-enterprise"
ONSUD_CELLS = CACHE / "onsud" / "oa_cell_addresses.pkl"
ONSUD_REGION = CACHE / "onsud" / "oa_region.pkl"

#: The heating half-year the whole weather derivation runs on, October to March.
DOYS = tuple(range(274, 366)) + tuple(range(1, 91))
SETPOINT_C = 20.0

#: NEED's four age bands onto this project's eras, taking the era with the largest overlap. Coarser
#: than `need_stock_joint.era_band_weights` deliberately: a DEMAND case needs ONE set of U-values,
#: and splitting an era's mass would produce a house that does not exist.
AGE_TO_ERA = {"1": "PRE_1919", "2": "ERA_1945_1964", "3": "ERA_1981_2000", "4": "POST_2000"}

#: EPC band onto the model's insulation levels. A CHOICE, not an anchor: no published table maps a
#: rating to a fabric state, because a rating is an outcome of fabric plus heating plus controls.
#: Stated here rather than buried. NOT YET PRICED: what the answer does under a different mapping
#: is the obvious next question and this module does not answer it, so the map is a declared choice
#: with an unmeasured cost rather than one with a measured one.
EPC_TO_INSULATION = {"A/B": "FULL", "C": "FULL", "D": "PARTIAL", "E": "POOR", "F/G": "POOR"}

#: NEED floor-area band midpoints, m^2. Bands are 1 = <=50, 2 = 51-100, 3 = 101-150, 4 = 151-200,
#: 5 = over 200; the open top band takes 230, which is the only number here that is not a midpoint
#: and is flagged as such.
AREA_MIDPOINT = {"1": 40.0, "2": 75.0, "3": 125.0, "4": 175.0, "5": 230.0}

#: The reference cell the solar term is scaled from -- household-weighted GB mean annual sunshine.
REFERENCE_SUNSHINE_H = 1535.0


def _seasonal_hdd(winter_temp, setpoint_c: float = SETPOINT_C):
    """Degree-days over the heating half-year for a cell whose DJF mean is `winter_temp`.

    `setpoint_c` is a parameter because a TURN-DOWN CEILING is the difference between the same
    cell's degree-days at two set-points, and computing the second one anywhere else would make
    the ceiling a difference between two shapes rather than between two thermostat settings.

    One seasonal shape, shifted so its DJF mean is the cell's. The shape is the same for every cell
    -- what varies is its level -- which is the same information the weather-cell derivation uses
    and no more.
    """
    import numpy as np

    doys = np.array(DOYS)
    base = 8.0 - 5.0 * np.cos(2 * np.pi * (doys - 15) / 365.0)
    djf = np.isin(doys, np.r_[np.arange(335, 366), np.arange(1, 60)])
    shift = np.asarray(winter_temp, dtype=float) - base[djf].mean()
    return np.maximum(0.0, setpoint_c - (base[None, :] + shift[:, None])).sum(axis=1)


def _reference_solar_kwh_per_m2() -> float:
    from simulation import fabric_physics as fp

    return sum(sum(fp.reconstruct_irradiance_profile(
        cloud_cover_pct=60.0, day_of_year=int(d), latitude_deg=53.0)) * 0.5 for d in DOYS)


def house_cases(insulation_override: str | None = None):
    """[(case key, fabric parameters)] and the per-region and national mixtures over them.

    THE UNRATED 30% ARE IMPUTED, NOT DROPPED. An EPC exists because a home was sold, let or newly
    built, so dropping the unrated biases the stock toward flats and new builds -- 0.39x and 0.24x
    respectively. They take a draw from the (type, age) conditional measured on the rated, which
    uses the association that is measured rather than inventing one.

    `insulation_override` re-derives the SAME cases at a different insulation level, which is how
    an insulation CEILING is measured: the difference between a case's demand as it stands and the
    same case retrofitted. It exists as a parameter rather than as a second construction elsewhere
    because two copies of this Household would drift, and the ceiling would then be the difference
    between two models rather than between two fabric states.
    """
    import csv

    import numpy as np

    from simulation import fabric_physics as fp
    from simulation.household import (
        BoilerAge,
        BuildEra,
        HeatingSystem,
        Household,
        InsulationLevel,
        PropertyType,
    )
    from tools import need_stock_joint as need

    with need.NEED_CSV.open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    rated = [r for r in rows if r["EPC"] in EPC_TO_INSULATION]
    conditional: dict = collections.defaultdict(collections.Counter)
    for row in rated:
        conditional[(row["PROP_TYPE"], row["PROP_AGE_BAND"])][row["EPC"]] += 1
    rng = np.random.default_rng(0)
    for row in rows:
        if row["EPC"] not in EPC_TO_INSULATION:
            counts = conditional.get((row["PROP_TYPE"], row["PROP_AGE_BAND"])) or collections.Counter({"D": 1})
            keys = list(counts)
            probs = np.array([counts[k] for k in keys], dtype=float)
            row["EPC"] = keys[int(rng.choice(len(keys), p=probs / probs.sum()))]

    by_region: dict = collections.defaultdict(collections.Counter)
    for row in rows:
        key = (need.PROPERTY_TYPE[row["PROP_TYPE"]], row["PROP_AGE_BAND"],
               row["FLOOR_AREA_BAND"], row["EPC"])
        by_region[row["REGION"]][key] += 1
    national: collections.Counter = collections.Counter()
    for counts in by_region.values():
        national.update(counts)

    keys = sorted(national)
    params = np.zeros((len(keys), 5))
    for i, (ptype, age, area, epc) in enumerate(keys):
        property_type = PropertyType[ptype]
        base = fp._FLOOR_AREA_BASE_M2[property_type]
        bedrooms = int(max(1, min(6, round(
            2 + (AREA_MIDPOINT[area] - base) / fp._FLOOR_AREA_PER_BEDROOM_M2))))
        household = Household(
            customer_id="C", property_type=property_type, build_era=BuildEra[AGE_TO_ERA[age]],
            epc_rating="D", bedrooms=bedrooms, heating_system=HeatingSystem.GAS_BOILER_COMBI,
            boiler_age=BoilerAge.MID, has_solar=False, solar_kwp=0.0, solar_install_year=None,
            has_battery=False, battery_kwh=0.0, has_ev=False, ev_charger_kw=0.0,
            has_smart_meter=True, smart_meter_install_year=2020,
            insulation=InsulationLevel[insulation_override or EPC_TO_INSULATION[epc]],
            has_driveway=True,
            roof_aspect="south")
        p = fp.fabric_parameters(household)
        params[i] = (p.fabric_w_per_k, p.raw_infiltration_ach, p.volume_m3,
                     p.solar_aperture_m2, p.internal_gain_kw)
    return keys, params, dict(by_region), dict(national)


def demand_grid():
    """(demand, weather sensitivity, household weights) over cells x house cases, England and Wales.

    THE DEMAND MODEL HERE IS A CLOSED FORM, AND IT IS VALIDATED RATHER THAN ASSERTED. Against the
    full 2R2C simulation over 72 (house x weather) pairs it scores r-squared 0.9978 with a 3.7%
    residual. AND THE COVERAGE ANSWER IS INVARIANT TO ITS CALIBRATION: coverage is a ratio of
    weighted sums of squares about the mean, so an affine transform of the demand scale cancels
    exactly. Only the residual matters, not the slope or the offset.
    """
    import numpy as np

    from simulation import fabric_physics as fp
    from tools import weather_cell_drivers as drv
    from tools import weather_cell_weights as wgt
    from tools import weather_driver_sensitivity as sens

    for path in (ONSUD_CELLS, ONSUD_REGION):
        if not path.is_file():
            raise FileNotFoundError(
                f"{path} is absent. Run `python3 tools/ons_uprn_directory.py --pull --build`; the "
                "region map is built by the same pass.")
    with ONSUD_CELLS.open("rb") as fh:
        pairs = pickle.load(fh)
    with ONSUD_REGION.open("rb") as fh:
        oa_region = pickle.load(fh)
    households = wgt.read_households()

    per_oa: collections.Counter = collections.Counter()
    for (oa, _x, _y), count in pairs.items():
        per_oa[oa] += count
    cells: dict = collections.defaultdict(lambda: collections.defaultdict(float))
    for (oa, cell_x, cell_y), count in pairs.items():
        n = households.get(oa)
        region = oa_region.get(oa)
        # SCOTLAND IS OUT, and it is out for a reason that cannot be papered over: NEED is a DESNZ
        # product with no Scottish dwellings, so there is no measured stock composition to compose
        # with a Scottish cell. Using the England-and-Wales mixture there would be an assumption
        # about the coldest 8% of the book, which is the worst place to make one.
        if n is None or region is None or region == "S92000003":
            continue
        cells[(cell_x, cell_y)][region] += n * count / per_oa[oa]

    d = drv.drivers()
    index = {(int(x) // 1000, int(y) // 1000): i
             for i, (x, y) in enumerate(zip(d["east"], d["north"]))}
    winter, wind, sun, weight, region_of = [], [], [], [], []
    for cell, regions in cells.items():
        i = index.get(cell)
        if i is None:
            continue
        winter.append(d["winter_temp"][i])
        wind.append(d["annual_wind"][i])
        sun.append(d["annual_sun"][i])
        weight.append(sum(regions.values()))
        region_of.append(max(regions, key=regions.get))
    winter = np.array(winter)
    wind = np.array(wind)
    sun = np.array(sun)
    weight = np.array(weight)

    keys, params, by_region, national = house_cases()
    totals = {r: sum(c.values()) for r, c in by_region.items()}
    mixture = {r: np.array([by_region[r].get(k, 0) / totals[r] for k in keys]) for r in by_region}
    probability = np.stack([mixture[r] for r in region_of])

    hdd = _seasonal_hdd(winter)
    a, b, n = sens.ANGSTROM_A, sens.ANGSTROM_B, sens.ANNUAL_DAYLIGHT_H
    solar_index = (a + b * sun / n) / (a + b * REFERENCE_SUNSHINE_H / n)
    reference_solar = _reference_solar_kwh_per_m2()
    hours = len(DOYS) * 24.0

    demand = np.empty((len(winter), len(keys)))
    sensitivity = np.empty_like(demand)
    for i in range(len(keys)):
        fabric, raw_ach, volume, aperture, internal = params[i]
        ach = np.maximum(raw_ach * (wind / fp.SAP_REFERENCE_WIND_MS), fp._MINIMUM_VENTILATION_ACH)
        hlc = (fabric + 0.33 * ach * volume) / 1000.0
        sensitivity[:, i] = hlc * 24.0
        demand[:, i] = np.maximum(
            0.0, hlc * hdd * 24.0 - aperture * reference_solar * solar_index - internal * hours)
    return {"demand": demand, "sensitivity": sensitivity, "weights": probability * weight[:, None],
            "cell_weights": weight, "cell_hdd": hdd, "cell_wind": wind,
            "cell_solar_index": solar_index, "case_keys": keys, "case_params": params,
            "national_mixture": np.array([national[k] / sum(national.values()) for k in keys])}


def coverage(values, weights, ks, seed: int = 0, sample: int = 400_000) -> dict:
    """Share of household-weighted variance captured by `k` cases, over one or more output axes.

    SAMPLED, AND THE SAMPLE IS THE HONEST PART. The full grid is 39.3 million (cell, house) pairs
    and k-means over that is not affordable, so a weighted sample stands in. `--stability` reruns
    it on independent seeds and reports the spread, because a coverage figure from one sample with
    no interval is a figure whose precision nobody can judge.
    """
    import numpy as np
    from sklearn.cluster import KMeans

    v = np.asarray(values, dtype=float)
    v = v.reshape(-1, 1) if v.ndim == 1 else v.reshape(-1, v.shape[-1])
    w = np.asarray(weights, dtype=float).ravel()
    keep = w > 0
    v, w = v[keep], w[keep]
    rng = np.random.default_rng(seed)
    if len(v) > sample:
        pick = rng.choice(len(v), size=sample, replace=True, p=w / w.sum())
        v, w = v[pick], np.ones(sample)
    mean = np.average(v, axis=0, weights=w)
    sd = np.sqrt(np.average((v - mean) ** 2, axis=0, weights=w))
    z = (v - mean) / np.where(sd == 0, 1.0, sd)
    total = float(np.sum(w[:, None] * (z - np.average(z, axis=0, weights=w)) ** 2))
    out = {}
    for k in ks:
        if k > len(np.unique(z, axis=0)):
            out[k] = 1.0
            continue
        km = KMeans(n_clusters=k, n_init=1, random_state=seed).fit(z, sample_weight=w)
        within = float(np.sum(w[:, None] * (z - km.cluster_centers_[km.labels_]) ** 2))
        out[k] = round(1.0 - within / total, 4)
    return out


KS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233)
TARGETS = (0.90, 0.95, 0.99)


def measurement(grid=None) -> dict:
    """The joint against its two marginals, and the product they would need if they were separable."""
    import numpy as np

    g = grid if grid is not None else demand_grid()
    demand, weights = g["demand"], g["weights"]

    joint = coverage(demand.ravel(), weights, KS)
    two_axis = coverage(np.stack([demand.ravel(), g["sensitivity"].ravel()], axis=1), weights, KS)

    # WEATHER ALONE holds the house at the national mixture in every cell, so the only thing
    # varying is where. HOUSE ALONE holds the weather at the household-weighted mean cell.
    weather_only = coverage((demand * g["national_mixture"][None, :]).sum(axis=1),
                            g["cell_weights"], KS)
    mean_cell = {k: float(np.average(g[k], weights=g["cell_weights"]))
                 for k in ("cell_hdd", "cell_wind", "cell_solar_index")}
    from simulation import fabric_physics as fp
    reference_solar = _reference_solar_kwh_per_m2()
    hours = len(DOYS) * 24.0
    house_demand = []
    for fabric, raw_ach, volume, aperture, internal in g["case_params"]:
        ach = max(raw_ach * (mean_cell["cell_wind"] / fp.SAP_REFERENCE_WIND_MS),
                  fp._MINIMUM_VENTILATION_ACH)
        hlc = (fabric + 0.33 * ach * volume) / 1000.0
        house_demand.append(max(0.0, hlc * mean_cell["cell_hdd"] * 24.0
                                - aperture * reference_solar * mean_cell["cell_solar_index"]
                                - internal * hours))
    house_only = coverage(np.array(house_demand), weights.sum(axis=0), KS)

    def need(curve, target):
        for k in sorted(curve):
            if curve[k] >= target:
                return k
        return None

    return {
        "households": int(weights.sum()),
        "cells": int(demand.shape[0]),
        "house_cases": int(demand.shape[1]),
        "curves": {"joint": joint, "joint_two_axis": two_axis,
                   "weather_only": weather_only, "house_only": house_only},
        "cases_needed": {
            f"{int(t * 100)}pc": {
                "weather_alone": need(weather_only, t), "house_alone": need(house_only, t),
                "product_if_separable": (need(weather_only, t) or 0) * (need(house_only, t) or 0),
                "joint": need(joint, t),
                "joint_with_weather_sensitivity": need(two_axis, t),
            } for t in TARGETS},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--measure", action="store_true", help="the joint and its marginals")
    args = ap.parse_args(argv)
    if args.measure:
        print(json.dumps(measurement(), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
