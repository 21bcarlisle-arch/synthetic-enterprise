"""One premise's year of half-hourly gas and electricity, and WHY it looks like that.

REUSE: tools/explain_premise_year.py
CLASS: CUSTOM
INDEX: searched "explain", "premise trace", "decompose demand", "attribution", "why".
       `tools/couple_fabric.py` scores the company's BELIEF against the trace -- a measurement of
       the gap, not an account of the world. `tools/fabric_settlement_gap.py` reports WHO settles
       on fabric physics and whether the totals sit inside an envelope; it does not open a day.
       `simulation/premise_trace.py` GENERATES the trace and is read here, never re-implemented.
       Nothing takes one premise's year and says what produced it.

WHY THIS EXISTS
---------------
Director, setting phase one: *"What I want to be able to do at the end of phase one: look at a
household's half-hourly gas and electricity for a year and believe it, and be able to say why it
looks like that -- this fabric, this weather, these people, this heating pattern."*

That is a test of the WORLD, not of a number. A total can be plausible for the wrong reasons; a
year of half-hours cannot, because every hour has to be produced by something nameable. So this
walks the four causes and shows each one's fingerprint in the series:

  FABRIC   the heat-loss coefficient, and what the year's degree-days do to it
  WEATHER  the cell's actual days -- the coldest, the mildest, and the spread between them
  PEOPLE   how many, when they are in, and what that does to the base load and the hot water
  PATTERN  the set-point and the hours the heating runs, visible as the shape of a winter day

**IT RECONCILES RATHER THAN NARRATES.** Every section ends in an arithmetic identity that either
closes or does not. A story about a house is not an explanation; `HLC x degree-days x 24 - gains`
landing on the modelled space heat is.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

PERIODS_PER_DAY = 48


def _fmt(x: float, places: int = 0) -> str:
    return f"{x:,.{places}f}"


def explain(premise_id: str = "C1", year: int = 2022, seed: int = 42) -> dict:
    """The premise's year, decomposed, with the arithmetic that accounts for it."""
    import simulation.premise_trace as pt
    from simulation import fabric_physics as fp
    from simulation.household_physical_layer import people_count_for

    sys.path.insert(0, str(PROJECT / "tests" / "simulation"))
    from test_premise_trace import make_household

    household = make_household()
    weather = pt.load_trace_weather(
        premise_id, start=dt.date(year, 1, 1), end=dt.date(year, 12, 31))
    if not weather:
        raise SystemExit(f"no weather for {premise_id} in {year}")

    # THE HOUSEHOLD EXPLAINED HERE IS THE ONE THE BOOK SETTLED, and the argument below is the
    # whole of what makes that true. `behaviour_profile_for` falls back to `_PEOPLE_BY_BEDROOMS`
    # when a caller omits `people_count`, and that fallback is legitimate for a caller with no
    # census draw -- so an explanation built on it is green, plausible, and about a different
    # home. It was: C1 was three people here and one in the book.
    # (SEAT_RESULT_THE_CENSUS_HEADCOUNT_REACHED_EVERY_CALLER_EXCEPT_THE_ONE_THE_BOOK_IS_SETTLED_ON.)
    # Drawn ONCE and handed to the generator, not drawn again beside it: the PEOPLE section below
    # reports this same object, so the count in the explanation is the count that produced the
    # gains and the hot water it is explaining.
    profile = pt.behaviour_profile_for(
        premise_id, household, seed=seed, people_count=people_count_for(premise_id))
    trace = pt.generate_premise_trace(
        premise_id=premise_id, household=household, weather=weather, seed=seed,
        behaviour=profile, latitude_deg=pt.DEFAULT_LATITUDE_DEG)

    params = fp.fabric_parameters(household)
    hlc_kw_per_k = (params.fabric_w_per_k
                    + 0.33 * params.raw_infiltration_ach * params.volume_m3) / 1000.0

    days = trace.days
    gas = sum(sum(d.gas_kwh) for d in days)
    elec = sum(sum(d.electricity_kwh) for d in days)
    heat = sum(sum(d.heating_fuel_kwh) for d in days)
    dhw = sum(sum(d.dhw_fuel_kwh) for d in days)
    cook = sum(sum(d.cooking_fuel_kwh) for d in days)
    delivered = sum(sum(d.heat_delivered_kwh) for d in days)

    # --- WEATHER: the cell's own year -----------------------------------------------------
    temps = [d.mean_ambient_c for d in days]
    setpoints = [sum(d.setpoint_c) / PERIODS_PER_DAY for d in days]
    degree_days = sum(max(0.0, sp - t) for sp, t in zip(setpoints, temps))
    coldest = min(days, key=lambda d: d.mean_ambient_c)
    mildest = max(days, key=lambda d: d.mean_ambient_c)

    # --- THE IDENTITY THAT MUST CLOSE ------------------------------------------------------
    # Gross fabric loss at the household's own set-point, less what the gains cover, is what the
    # boiler had to deliver. If this does not land near the modelled heat, the trace is not
    # explained by the fabric and the explanation is wrong rather than approximate.
    gross_kwh = hlc_kw_per_k * degree_days * 24.0
    gains_kwh = gross_kwh - delivered

    # --- PEOPLE ---------------------------------------------------------------------------
    # `profile` is the one built above and handed to the generator. It is NOT re-drawn: a second
    # draw would be a second answer to "how many people live here", which is the defect this
    # module's own subject closed one file over.
    away_days = sum(1 for d in days if d.is_away)

    # --- PATTERN ---------------------------------------------------------------------------
    winter = [d for d in days if d.date.month in (1, 2, 12)]
    on_periods = []
    for d in winter:
        comfort = max(d.setpoint_c)
        on_periods.append(sum(1 for s in d.setpoint_c if s >= comfort - 0.01) / 2.0)
    heated_hours = sum(on_periods) / len(on_periods) if on_periods else 0.0

    def day_shape(day) -> dict:
        return {
            "date": day.date.isoformat(),
            "mean_ambient_c": round(day.mean_ambient_c, 2),
            "is_weekend": day.is_weekend,
            "gas_kwh": [round(v, 4) for v in day.gas_kwh],
            "electricity_kwh": [round(v, 4) for v in day.electricity_kwh],
            "heating_fuel_kwh": [round(v, 4) for v in day.heating_fuel_kwh],
            "dhw_fuel_kwh": [round(v, 4) for v in day.dhw_fuel_kwh],
            "cooking_fuel_kwh": [round(v, 4) for v in day.cooking_fuel_kwh],
            "setpoint_c": [round(v, 2) for v in day.setpoint_c],
            "indoor_air_c": [round(v, 2) for v in day.indoor_air_c],
        }

    return {
        "premise_id": premise_id,
        "year": year,
        "fabric": {
            "property_type": household.property_type.name,
            "build_era": household.build_era.name,
            "bedrooms": household.bedrooms,
            "insulation": household.insulation.name,
            "heating_system": household.heating_system.name,
            "hlc_kw_per_k": round(hlc_kw_per_k, 4),
            "fabric_w_per_k": round(params.fabric_w_per_k, 1),
            "infiltration_ach": round(params.raw_infiltration_ach, 3),
            "volume_m3": round(params.volume_m3, 1),
            "solar_aperture_m2": round(params.solar_aperture_m2, 2),
            "internal_gain_kw": round(params.internal_gain_kw, 3),
        },
        "weather": {
            "days": len(days),
            "mean_ambient_c": round(sum(temps) / len(temps), 2),
            "coldest_day": coldest.date.isoformat(),
            "coldest_mean_c": round(coldest.mean_ambient_c, 2),
            "mildest_day": mildest.date.isoformat(),
            "mildest_mean_c": round(mildest.mean_ambient_c, 2),
            "degree_days_at_own_setpoint": round(degree_days, 0),
        },
        "people": {
            "people_count": profile.people_count,
            "people_count_source": "ONS Census 2021 TS017, via household_physical_layer",
            "away_days": away_days,
        },
        "pattern": {
            "mean_setpoint_c": round(sum(setpoints) / len(setpoints), 2),
            "peak_setpoint_c": round(max(max(d.setpoint_c) for d in days), 2),
            "setback_setpoint_c": round(min(min(d.setpoint_c) for d in days), 2),
            "heated_hours_per_winter_day": round(heated_hours, 2),
        },
        "year_totals": {
            "gas_kwh": round(gas, 1),
            "electricity_kwh": round(elec, 1),
            "space_heat_fuel_kwh": round(heat, 1),
            "hot_water_fuel_kwh": round(dhw, 1),
            "cooking_fuel_kwh": round(cook, 1),
            "heat_delivered_kwh": round(delivered, 1),
        },
        "reconciliation": {
            "gross_fabric_loss_kwh": round(gross_kwh, 1),
            "covered_by_gains_kwh": round(gains_kwh, 1),
            "gains_share_of_gross": round(gains_kwh / gross_kwh, 4) if gross_kwh else None,
            "heat_delivered_kwh": round(delivered, 1),
            "boiler_efficiency_implied": round(delivered / heat, 4) if heat else None,
        },
        "days": {
            "coldest": day_shape(coldest),
            "mildest": day_shape(mildest),
        },
    }


def render(report: dict) -> str:
    """The explanation as prose a person can check line by line."""
    f, w, p, pat = report["fabric"], report["weather"], report["people"], report["pattern"]
    t, r = report["year_totals"], report["reconciliation"]
    out = []
    out.append(f"PREMISE {report['premise_id']} — {report['year']}\n")
    out.append("THIS FABRIC")
    out.append(f"  a {f['bedrooms']}-bedroom {f['property_type'].lower().replace('_',' ')}, "
               f"{f['build_era'].lower().replace('_',' ')}, {f['insulation'].lower()} insulation")
    out.append(f"  heat-loss coefficient {f['hlc_kw_per_k']} kW/K "
               f"= {f['fabric_w_per_k']} W/K fabric + {f['infiltration_ach']} ach over "
               f"{f['volume_m3']} m3")
    out.append(f"  gains: {f['solar_aperture_m2']} m2 solar aperture, "
               f"{f['internal_gain_kw']} kW internal\n")
    out.append("THIS WEATHER")
    out.append(f"  {w['days']} days in cell {report['premise_id']}, mean {w['mean_ambient_c']} C")
    out.append(f"  coldest {w['coldest_day']} at {w['coldest_mean_c']} C; "
               f"mildest {w['mildest_day']} at {w['mildest_mean_c']} C")
    out.append(f"  {_fmt(w['degree_days_at_own_setpoint'])} degree-days at this "
               f"household's own set-point\n")
    out.append("THESE PEOPLE")
    out.append(f"  {p['people_count']} occupant(s); away {p['away_days']} days of the year\n")
    out.append("THIS HEATING PATTERN")
    out.append(f"  set-point {pat['peak_setpoint_c']} C, setback {pat['setback_setpoint_c']} C, "
               f"mean over the year {pat['mean_setpoint_c']} C")
    out.append(f"  heated {pat['heated_hours_per_winter_day']} hours on a winter day\n")
    out.append("WHAT THAT PRODUCES")
    out.append(f"  gas         {_fmt(t['gas_kwh'])} kWh  = space heat {_fmt(t['space_heat_fuel_kwh'])}"
               f" + hot water {_fmt(t['hot_water_fuel_kwh'])} + cooking {_fmt(t['cooking_fuel_kwh'])}")
    out.append(f"  electricity {_fmt(t['electricity_kwh'])} kWh\n")
    out.append("AND THE ARITHMETIC CLOSES")
    out.append(f"  gross fabric loss  = {f['hlc_kw_per_k']} kW/K x "
               f"{_fmt(w['degree_days_at_own_setpoint'])} degree-days x 24 h "
               f"= {_fmt(r['gross_fabric_loss_kwh'])} kWh")
    out.append(f"  less gains covered = {_fmt(r['covered_by_gains_kwh'])} kWh "
               f"({r['gains_share_of_gross']:.1%} of gross)")
    out.append(f"  heat delivered     = {_fmt(r['heat_delivered_kwh'])} kWh")
    out.append(f"  burnt as gas       = {_fmt(t['space_heat_fuel_kwh'])} kWh "
               f"(boiler at {r['boiler_efficiency_implied']:.1%})")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--premise", default="C1")
    ap.add_argument("--year", type=int, default=2022)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    report = explain(args.premise, args.year)
    print(json.dumps(report, indent=1) if args.json else render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
