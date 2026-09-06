"""What each weather driver is actually FOR, and how much of it a household feels.

REUSE: tools/weather_driver_sensitivity.py
CLASS: CUSTOM
INDEX: searched "sensitivity", "infiltration", "wind chill", "PV yield", "irradiance", "elasticity".
       `simulation/fabric_physics.py` owns the heat-loss model and is IMPORTED here, not copied --
       the point of the measurement is that it is this project's own stock, not a textbook one.
       `company/regulatory/seg_export_estimator.py` holds the single national PV yield figure this
       module measures the error of. `tools/weather_cell_derivation.py` answers how many cells; this
       answers what they are needed FOR, which is the question that decides whether the count is
       worth paying.

WHY THIS EXISTS
---------------
`W1_21` reported that 987 cells are needed for 99% of household-weighted variation across three
drivers, and the director challenged the framing: one grid is being asked to serve three different
jobs, and wind -- fine-grained, terrain-driven -- may not need household resolution at all, because a
household has no turbine and wind reaches it only as a second-order effect on heat loss.

THE MECHANISM IS PUBLISHED AND IT IS NOT SECOND-ORDER. SAP 10.2 and BREDEM adjust a dwelling's
infiltration rate by a wind factor:

    adjusted infiltration ACH = raw ACH  x  shelter factor  x  (wind speed / 4 m/s)

A LINEAR multiplier on the air change rate, normalised at 4 m/s -- not a surface correction. Since
ventilation loss is `0.33 x ACH x volume`, it flows straight into the heat loss coefficient, and
`wind_hlc_sensitivity` measures how far across this project's own stock.

THE SHELTER FACTOR IS DELIBERATELY OMITTED. It is `1 - 0.075 x sides_sheltered`, a PROPERTY
attribute, not a cell attribute -- and it cancels in the ratio between two wind speeds, which is the
only quantity this module reports. Including it would vary the answer by dwelling for a reason that
has nothing to do with the cell question.

PV IS THE OTHER HALF. HadUK publishes sunshine DURATION, not irradiance. The conversion is the
Angstrom-Prescott relation, `H/H0 = a + b*(n/N)`, which is the method the UK's own gridded solar
resource is built with. Because `a > 0` the relative spread in irradiation is strictly SMALLER than
in duration -- so a cell count argued from sunshine hours overstates what PV yield needs, and by
about a factor of two.
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

#: SAP 10.2 / BREDEM. The divisor is the reference wind speed the infiltration tables are keyed to.
SAP_REFERENCE_WIND_MS = 4.0

#: Angstrom-Prescott. Prescott's own monthly-mean values; `pv_yield_error` reports the elasticity
#: across the published range as well, because the conclusion must not turn on the choice.
ANGSTROM_A = 0.25
ANGSTROM_B = 0.50
ANGSTROM_RANGE = ((0.20, 0.54), (0.22, 0.54), (0.25, 0.54))

#: Annual daylight hours are ~4380 at every GB latitude -- the seasonal swing cancels over a year --
#: so the annual sunshine fraction n/N needs no per-cell daylength.
ANNUAL_DAYLIGHT_H = 4380.0

#: The household-weighted wind and winter-temperature spreads measured by `W1_20`, used as the
#: comparison span. Both are 5th and 95th percentiles of the SAME population, so the two effects
#: below are quoted over the same slice of the same book.
WIND_P05_MS, WIND_MEDIAN_MS, WIND_P95_MS = 2.98, 3.85, 5.61
WINTER_TEMP_P05_C, WINTER_TEMP_P95_C = 3.95, 6.13
HDD_BASE_C = 15.5


def _fabric_split(area: float, era, ptype, insulation):
    """(fabric W/K, raw infiltration ACH, volume) using the SIM's OWN parameters."""
    from simulation import fabric_physics as fp
    from simulation.household import InsulationLevel, PropertyType

    exposure = fp._EXPOSED_ENVELOPE_FRACTION[ptype]
    retro = fp._INSULATION_U_MULTIPLIER[insulation]
    horizontal = 0.15 if ptype == PropertyType.FLAT else 0.50
    wall = fp._WALL_AREA_RATIO * area * exposure
    roof = horizontal * area * exposure
    ground = horizontal * area
    window = fp._WINDOW_AREA_RATIO * area
    fabric = (wall * fp._retrofitted_u(fp._WALL_U_BY_ERA[era], retro, fp._WALL_U_FLOOR)
              + roof * fp._retrofitted_u(fp._ROOF_U_BY_ERA[era], retro, fp._ROOF_U_FLOOR)
              + ground * max(fp._GROUND_U_BY_ERA[era], fp._GROUND_U_FLOOR)
              + window * fp._WINDOW_U_BY_ERA[era])
    raw_ach = fp._INFILTRATION_ACH_BY_ERA[era] * (
        0.85 if insulation == InsulationLevel.FULL else 1.0)
    return fabric, raw_ach, area * fp._STOREY_HEIGHT_M


def wind_hlc_sensitivity(areas=(55.0, 90.0, 140.0)) -> dict:
    """How much the heat loss coefficient moves across the household wind spread, and what the
    same span of winter temperature does to heating degree days.

    THE TWO NUMBERS ARE THE POINT, not either alone. "Wind changes heat loss by 15%" means nothing
    until it is set beside the driver everyone agrees matters.
    """
    import numpy as np

    from simulation import fabric_physics as fp

    rows = []
    for era, ptype, insulation, area in itertools.product(
            fp._INFILTRATION_ACH_BY_ERA, fp._EXPOSED_ENVELOPE_FRACTION,
            fp._INSULATION_U_MULTIPLIER, areas):
        fabric, raw_ach, volume = _fabric_split(area, era, ptype, insulation)
        hlc = {}
        for name, wind in (("p05", WIND_P05_MS), ("median", WIND_MEDIAN_MS), ("p95", WIND_P95_MS)):
            ach = max(raw_ach * (wind / SAP_REFERENCE_WIND_MS), fp._MINIMUM_VENTILATION_ACH)
            hlc[name] = fabric + 0.33 * ach * volume
        rows.append({"era": era.name, "type": ptype.name, "insulation": insulation.name,
                     "area": area, "fabric_w_per_k": fabric, **hlc})

    share = np.array([(r["median"] - r["fabric_w_per_k"]) / r["median"] for r in rows])
    lift = np.array([r["p95"] / r["p05"] - 1.0 for r in rows])
    hdd_change = ((HDD_BASE_C - WINTER_TEMP_P95_C) / (HDD_BASE_C - WINTER_TEMP_P05_C)) - 1.0

    def spread(arr):
        return {"min": round(float(arr.min()), 4), "median": round(float(np.median(arr)), 4),
                "max": round(float(arr.max()), 4)}

    return {
        "combinations": len(rows),
        "ventilation_share_of_hlc": spread(share),
        "hlc_change_p05_to_p95_wind": spread(lift),
        "hdd_change_p05_to_p95_winter_temp": round(hdd_change, 4),
        "wind_effect_relative_to_temperature": round(float(np.median(lift)) / abs(hdd_change), 3),
        "the_sim_models_this": _sim_has_a_wind_term(),
    }


def _sim_has_a_wind_term() -> bool:
    """Does the SIM's own heat-loss path consume wind at all?

    FALSE TODAY, and that is the finding rather than a caveat: the company's
    `weather_normalisation_belief` carries an optional wind-chill regressor, so it can fit a
    household wind term against a world that has none. Read from the source rather than asserted,
    so this flips by itself on the day the repair lands.
    """
    import ast

    tree = ast.parse((PROJECT / "simulation" / "fabric_physics.py").read_text(encoding="utf-8"))
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == "fabric_parameters"), None)
    if fn is None:
        raise RuntimeError("simulation.fabric_physics.fabric_parameters has moved or been renamed; "
                           "this check cannot answer and must not report False")
    names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)} | {
        n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)}
    # SUBSTRING MATCHING REPORTED TRUE ON THE FIRST RUN, and it was WINDOW: `window_area`,
    # `_WINDOW_U_BY_ERA`, `_WINDOW_AREA_RATIO`. The function would have published "the SIM models
    # wind" on the strength of its glazing. Segment-matched, so `window` cannot answer for `wind`.
    return any(re.search(r"(?:^|_)wind(?:chill|speed|_speed)?(?:_|$)", name.lower())
               for name in names)


def pv_yield_error(cells=(1, 2, 3, 5, 8, 13, 21, 34)) -> dict:
    """Annual PV yield error against cell count, and the elasticity that halves the sunshine spread.

    `cells=1` is what the company does TODAY: `seg_export_estimator` uses one national
    kWh/kWp figure for every household in the book.
    """
    import numpy as np
    from sklearn.cluster import KMeans

    from tools import weather_cell_derivation as wcd

    z, native, weights, mean, sd = wcd._space(True)
    index = wcd.DRIVERS.index("annual_sun")
    sun = native[:, index]

    def irradiation(hours, a=ANGSTROM_A, b=ANGSTROM_B):
        return a + b * (hours / ANNUAL_DAYLIGHT_H)

    mean_sun = float(np.average(sun, weights=weights))
    truth = irradiation(sun)
    rows = []
    for k in cells:
        if k == 1:
            estimate = np.full_like(sun, mean_sun)
        else:
            km = KMeans(n_clusters=k, n_init=1, random_state=0).fit(z[:, [index]],
                                                                    sample_weight=weights)
            estimate = np.empty_like(sun)
            for label in range(k):
                member = km.labels_ == label
                estimate[member] = np.average(sun[member], weights=weights[member])
        rows.append({
            "cells": k,
            "sunshine_rms_hours": round(float(np.sqrt(
                np.average((sun - estimate) ** 2, weights=weights))), 1),
            "yield_rms": round(float(np.sqrt(np.average(
                (irradiation(estimate) / truth - 1.0) ** 2, weights=weights))), 4),
        })

    mean_irr = float(np.average(truth, weights=weights))
    return {
        "mean_annual_sunshine_hours": round(mean_sun, 1),
        "sunshine_fraction": round(mean_sun / ANNUAL_DAYLIGHT_H, 3),
        "elasticity_of_irradiation_to_sunshine": round(
            ANGSTROM_B * (mean_sun / ANNUAL_DAYLIGHT_H) / mean_irr, 3),
        "elasticity_across_published_coefficients": {
            f"a={a},b={b}": round(b * (mean_sun / ANNUAL_DAYLIGHT_H)
                                  / (a + b * mean_sun / ANNUAL_DAYLIGHT_H), 3)
            for a, b in ANGSTROM_RANGE},
        "curve": rows,
    }


def measurement() -> dict:
    return {"wind": wind_hlc_sensitivity(), "pv": pv_yield_error()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--wind", action="store_true", help="wind's effect on the heat loss coefficient")
    ap.add_argument("--pv", action="store_true", help="PV yield error against cell count")
    args = ap.parse_args(argv)
    if args.wind:
        print(json.dumps(wind_hlc_sensitivity(), indent=2))
        return 0
    if args.pv:
        print(json.dumps(pv_yield_error(), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
