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

#: SAP 10.2 / BREDEM reference wind speed, IMPORTED FROM THE SIM rather than kept here. It was a
#: local copy while the world had no wind term and there was nothing to import; now that
#: `fabric_physics` owns the physics, two definitions of one constant is the shape that lets them
#: drift apart and disagree in a report nobody re-derives.
def _sap_reference_wind_ms() -> float:
    from simulation.fabric_physics import SAP_REFERENCE_WIND_MS as reference

    return reference


SAP_REFERENCE_WIND_MS = _sap_reference_wind_ms()

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
SUNSHINE_P05_H, SUNSHINE_P95_H = 1320.13, 1734.48
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
    """Does the SIM's own heat-loss path consume wind -- MEASURED, not read.

    THIS FUNCTION HAS BEEN WRONG TWICE, in opposite directions, and both times because it was
    reading source text instead of running the model.

      1. It asked `"wind" in name.lower()` over `fabric_parameters` and returned TRUE on
         `window_area`. It would have published "the SIM models wind" on the strength of the
         glazing.
      2. Segment-matched, it returned FALSE -- correctly, until `W1_26` landed the SAP factor in
         `FabricParameters.with_wind` rather than in `fabric_parameters`. The mechanism moved one
         method along and the control could not see it. A control keyed to WHERE a thing is written
         goes stale the moment it is written somewhere else.

    So it now does what the solar-gain check does: builds a parameter vector, asks for it at two
    wind speeds, and reports whether the heat loss coefficient actually moved. That cannot be
    fooled by a name and cannot go stale on a rename.
    """
    from simulation import fabric_physics as fp

    params = fp.fabric_parameters(_probe_household())
    calm = params.with_wind(2.0).heat_loss_coefficient_kw_per_k
    windy = params.with_wind(8.0).heat_loss_coefficient_kw_per_k
    return calm != windy


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


#: The heating half-year the HadUK daily archive covers, and the window every solar-gain figure
#: below is taken over. October to March.
HEATING_HALF_YEAR_DOYS = tuple(range(274, 366)) + tuple(range(1, 91))

#: A representative dwelling, and a synthetic smooth seasonal temperature so that the ONLY thing
#: varying between two runs is the sun. A real weather series would move the answer by whatever the
#: temperature did that year, which is not what is being measured.
SOLAR_PROBE_FLOOR_AREA_M2 = 90.0
SOLAR_PROBE_CLOUD_PCT = 60.0
SOLAR_PROBE_LATITUDE_DEG = 53.0


def _seasonal_days(cloud_pct: float = SOLAR_PROBE_CLOUD_PCT):
    import math

    from simulation.fabric_physics import DailyWeather

    days = []
    for doy in HEATING_HALF_YEAR_DOYS:
        mean = 8.0 - 5.0 * math.cos(2 * math.pi * (doy - 15) / 365.0)
        # THE CALM REFERENCE, so the solar sweep varies the sun and nothing else. At 4 m/s the
        # SAP factor is 1.0, which is what the solar figures were measured against before W1_26
        # gave the world a wind term at all -- holding it here keeps them comparable.
        days.append(DailyWeather(day_of_year=doy, temperature_min_c=mean - 3.0,
                                 temperature_max_c=mean + 3.0, temperature_mean_c=mean,
                                 cloud_cover_pct=cloud_pct,
                                 wind_speed_mean_ms=SAP_REFERENCE_WIND_MS))
    return days


def _probe_household(**overrides):
    from simulation.household import (
        BoilerAge,
        BuildEra,
        HeatingSystem,
        Household,
        InsulationLevel,
        PropertyType,
    )

    base = dict(customer_id="C1", property_type=PropertyType.SEMI_DETACHED,
                build_era=BuildEra.ERA_1965_1980, epc_rating="D", bedrooms=3,
                heating_system=HeatingSystem.GAS_BOILER_COMBI, boiler_age=BoilerAge.MID,
                has_solar=False, solar_kwp=0.0, solar_install_year=None, has_battery=False,
                battery_kwh=0.0, has_ev=False, ev_charger_kw=0.0, has_smart_meter=True,
                smart_meter_install_year=2020, insulation=InsulationLevel.PARTIAL,
                has_driveway=True, roof_aspect="south")
    base.update(overrides)
    return Household(**base)


def _half_year_fuel(household, days, latitude_deg, aperture_scale=1.0) -> float:
    import dataclasses

    from simulation import fabric_physics as fp

    params = fp.fabric_parameters(household)
    if aperture_scale != 1.0:
        params = dataclasses.replace(
            params, solar_aperture_m2=params.solar_aperture_m2 * aperture_scale)
    schedule = fp.heating_schedule_for("P1", household, seed=7)
    source = fp.heat_source_for(household, params, schedule.comfort_setpoint_c)
    state = fp.ThermalState(indoor_air_c=schedule.setback_setpoint_c,
                            mass_c=schedule.setback_setpoint_c)
    total = 0.0
    for day in days:
        profile = fp.reconstruct_ambient_profile(
            temperature_min_c=day.temperature_min_c, temperature_max_c=day.temperature_max_c,
            temperature_mean_c=day.temperature_mean_c, day_of_year=day.day_of_year,
            latitude_deg=latitude_deg)
        irradiance = fp.reconstruct_irradiance_profile(
            cloud_cover_pct=day.cloud_cover_pct, day_of_year=day.day_of_year,
            latitude_deg=latitude_deg)
        result = fp.simulate_day(household=household, params=params, schedule=schedule,
                                 source=source, ambient_profile=profile,
                                 irradiance_kw_per_m2=irradiance, initial_state=state)
        total += sum(result.fuel_kwh)
        state = result.end_state
    return total


def solar_gain_sensitivity() -> dict:
    """Is solar gain in the world, does it REACH the heat balance, and how much does it move?

    THE WIND TERM'S HISTORY IS WHY THIS RUNS THE MODEL RATHER THAN READING IT. Wind was listed in
    `fabric_physics`'s own docstring as an available archive field and consumed by nothing; a check
    that grepped for the word would have said both drivers were present. This zeroes the aperture
    and re-runs, so "reachable" means the fuel number changed.

    `irradiation_spread` scales the aperture, which is exactly equivalent to scaling the irradiance
    a cell receives -- `phi_s = ghi * aperture` -- so the solar effect is quoted over the SAME
    household 5th-to-95th-percentile span as the wind and temperature ones.
    """
    from simulation.household import BuildEra, InsulationLevel

    days = _seasonal_days()
    household = _probe_household()
    with_sun = _half_year_fuel(household, days, SOLAR_PROBE_LATITUDE_DEG, 1.0)
    without = _half_year_fuel(household, days, SOLAR_PROBE_LATITUDE_DEG, 0.0)

    spread = pv_irradiation_spread()
    by_stock = {}
    for era in (BuildEra.PRE_1919, BuildEra.ERA_1965_1980, BuildEra.POST_2000):
        for insulation in (InsulationLevel.POOR, InsulationLevel.FULL):
            probe = _probe_household(build_era=era, insulation=insulation)
            low = _half_year_fuel(probe, days, SOLAR_PROBE_LATITUDE_DEG, 1.0)
            high = _half_year_fuel(probe, days, SOLAR_PROBE_LATITUDE_DEG, spread)
            by_stock[f"{era.name}/{insulation.name}"] = round(high / low - 1.0, 4)

    latitudes = {name: round(_half_year_fuel(household, days, lat, 1.0) / with_sun - 1.0, 4)
                 for name, lat in (("london_51.51N", 51.5074), ("manchester_53.48N", 53.4808),
                                   ("glasgow_55.86N", 55.8642))}
    clouds = {}
    base = None
    for cloud in (35.0, 60.0, 85.0):
        fuel = _half_year_fuel(household, _seasonal_days(cloud), SOLAR_PROBE_LATITUDE_DEG, 1.0)
        base = base if base is not None else fuel
        clouds[f"cloud_{int(cloud)}pc"] = round(fuel / base - 1.0, 4)

    # NO `reachable` BOOLEAN. It was here, it summarised the two fuel numbers below, and it
    # SURVIVED a mutation that hardcoded it to True -- a flag that can lie about the evidence
    # printed beside it, guarding nothing. The two numbers are the evidence; a reader (and the
    # control) compares them. Deleted rather than given a control of its own.
    return {
        "half_year_fuel_kwh": {"with_solar_gain": round(with_sun),
                               "aperture_zeroed": round(without)},
        "solar_gain_offsets_of_heating_fuel": round(1.0 - with_sun / without, 4),
        "irradiation_spread_p05_to_p95": round(spread - 1.0, 4),
        "fuel_change_across_that_spread_by_stock": by_stock,
        "fuel_change_by_latitude": latitudes,
        "fuel_change_by_cloud_cover": clouds,
        "the_world_carries_a_wind_field": _daily_weather_has_wind(),
    }


def pv_irradiation_spread() -> float:
    """The p95/p05 ratio of Angstrom-Prescott irradiation over the household sunshine spread."""
    low = ANGSTROM_A + ANGSTROM_B * (SUNSHINE_P05_H / ANNUAL_DAYLIGHT_H)
    high = ANGSTROM_A + ANGSTROM_B * (SUNSHINE_P95_H / ANNUAL_DAYLIGHT_H)
    return high / low


def _daily_weather_has_wind() -> bool:
    """Does the record the whole demand path runs on carry wind AT ALL?

    ONE LAYER DEEPER THAN `_sim_has_a_wind_term`, and a stronger statement: that function found no
    wind in the heat-loss calculation, this finds nowhere to put one. `DailyWeather` has five
    fields and none of them is wind, so the repair changes a data contract and not a formula.
    """
    import dataclasses

    from simulation.fabric_physics import DailyWeather

    return any(re.search(r"(?:^|_)wind(?:chill|speed|_speed)?(?:_|$)", f.name.lower())
               for f in dataclasses.fields(DailyWeather))


def measurement() -> dict:
    return {"wind": wind_hlc_sensitivity(), "pv": pv_yield_error(),
            "solar_gain": solar_gain_sensitivity()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--wind", action="store_true", help="wind's effect on the heat loss coefficient")
    ap.add_argument("--pv", action="store_true", help="PV yield error against cell count")
    ap.add_argument("--solar-gain", action="store_true",
                    help="is solar gain in the world, and how much does it move demand")
    args = ap.parse_args(argv)
    if args.wind:
        print(json.dumps(wind_hlc_sensitivity(), indent=2))
        return 0
    if args.pv:
        print(json.dumps(pv_yield_error(), indent=2))
        return 0
    if args.solar_gain:
        print(json.dumps(solar_gain_sensitivity(), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
