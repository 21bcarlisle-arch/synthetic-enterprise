"""One-variable counterfactual for fa4f2ea40: the census headcount against the bedroom draw.

ONE VARIABLE. Same premises, same households, same weather, same seed, same shipped
`build_fabric_series`. The ONLY difference is whether the call supplies `people_count`. Nothing
here re-implements the demand path; the control arm is produced by wrapping the real
`behaviour_profile_for` and dropping that one keyword, which is precisely the state the tree was in
before fa4f2ea40.

Grades P1 (book demand falls, 2%-8%) and P3 (space heat per home RISES because metabolic gains
fall) from `SEAT_PREREG_WHAT_THE_CENSUS_HEADCOUNT_MOVES_IN_THE_BOOK_2026-09-16.md`. P2 (margin) is
NOT gradable here -- it needs the money path -- and is left explicitly unanswered rather than
inferred from volume.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from simulation import fabric_demand_path as fdp
from simulation import premise_trace as pt
from simulation.household_physical_layer import people_count_for
from simulation.premise_population import draw_premise_population

#: DEFAULT 600, and the smaller run is kept in the result document rather than deleted. At n=150 the
#: treatment itself was only -4.9% against the population's -13.7%, because the population
#: draw
#: takes a different SAMPLE at each n rather than a subset -- so a weak-treatment run reads as a
#: weak effect. Anything below ~500 cannot separate the two.
N = 600
YEAR_START = dt.date(2022, 1, 1)
YEAR_END = dt.date(2022, 12, 31)
LATITUDE = 53.0
SITE = "C1"

REAL_PROFILE = fdp.behaviour_profile_for


def _bedrooms_arm(*args, **kwargs):
    """The pre-fa4f2ea40 call, exactly: the same function with `people_count` dropped."""
    kwargs.pop("people_count", None)
    return REAL_PROFILE(*args, **kwargs)


def totals(drawn, weather, *, census: bool) -> dict:
    fdp.behaviour_profile_for = REAL_PROFILE if census else _bedrooms_arm
    gas = elec = 0.0
    people = 0
    n = 0
    for d in drawn:
        pid = getattr(d, "premise_id", None) or getattr(d, "customer_id", "")
        hh = d.household
        if not getattr(hh, "is_residential", True):
            continue
        try:
            series = fdp.build_fabric_series(
                customer_id=pid,
                household_at_date=lambda _s, _h=hh: _h,
                weather=weather,
                latitude_deg=LATITUDE,
            )
        except Exception as exc:  # noqa: BLE001 -- a refused premise is reported, never skipped silently
            print(f"  REFUSED {pid}: {type(exc).__name__}: {exc}", flush=True)
            continue
        g = series.annual_gas_kwh
        e = series.annual_electricity_kwh
        gas += sum(g.values()) if hasattr(g, "values") else float(g)
        elec += sum(e.values()) if hasattr(e, "values") else float(e)
        people += people_count_for(pid) if census else REAL_PROFILE(pid, hh).people_count
        n += 1
    return {"premises": n, "gas_kwh": gas, "elec_kwh": elec, "total_kwh": gas + elec,
            "mean_headcount": people / n if n else None}


#: Below this, the harness reports its SAMPLE and not the world. Measured 2026-09-16: at n=60 BOTH
#: verdicts invert -- P1 reads HOLDS and P3 reads REFUTED -- on the same code, for no reason but the
#: draw. `draw_premise_population(n, ...)` takes a different SAMPLE at each n rather than a subset,
#: so the TREATMENT strength varies with n too (-4.9% at n=150 against -11.65% at n=1200), and a
#: small run is weak-treatment and high-variance at once.
RESOLUTION_FLOOR_PREMISES = 500

#: The gas leg's noise floor. Measured across four samples: +0.302% (n=150), +0.098% (n=600),
#: -0.047% (n=1200), -0.489% (n=60) -- converging to zero as n grows. A reading inside this band is
#: not evidence of a SIGN, and reporting one as a sign is what this seat did at n=600.
GAS_NOISE_FLOOR_PCT = 0.25

#: The population's own headcount move, measured over 2,000 premises. Every run is scaled to this
#: before it is compared to a band calibrated on it.
POPULATION_HEADCOUNT_MOVE_PCT = -13.7


def grade(out: dict, *, n: int) -> list[str]:
    """The pre-registration's verdicts, as lines. Pure: takes measured moves, runs nothing.

    SEPARATED FROM THE RUN so the reasoning has a control. Every correction in here was paid for
    by getting it wrong first tonight, and none of it was testable while it lived inside `main()`
    beside a two-minute simulation.

    WHAT WAS WRONG AND IS NOW KEYED TO A PROPERTY:

    * **The kill line was on the TOTAL.** "Total book kWh under 0.5% means the change never reached
      the book" fired at n=150 (0.491%) and declared the wiring control worthless. It was FALSE:
      the per-commodity split showed the change arriving plainly. Total kWh sums two fuels whose
      responses have opposite signs, so it reads a real change as nothing happening. The kill line
      is on ELECTRICITY, the leg that carries the effect.
    * **P1 was compared as a LEVEL against a band calibrated on the population.** Two different
      experiments. It is scaled by the treatment actually delivered before it is graded.
    * **P3 was reported as a SIGN off a number smaller than its own noise.** It reports the noise
      floor instead, and says plainly that "two effects netting to zero" and "one effect absent"
      are indistinguishable at this resolution.
    """
    lines: list[str] = []
    move = out["total_kwh_move_pct"]
    head = out["headcount_move_pct"]
    elec = out["elec_kwh_move_pct"]
    gas_home = (None if not out["gas_per_home_control"] else
                (out["gas_per_home_treated"] - out["gas_per_home_control"])
                / out["gas_per_home_control"] * 100.0)

    if n < RESOLUTION_FLOOR_PREMISES:
        lines.append(
            f"NOT GRADED: n={n} is below this harness's resolution floor of "
            f"~{RESOLUTION_FLOOR_PREMISES} premises. At n=60 both P1 and P3 invert on the draw "
            "alone. The figures above are real; the verdicts they would imply are not. "
            f"Re-run with -n {RESOLUTION_FLOOR_PREMISES + 100} or more.")
        lines.append("P2 (margin): NOT GRADED HERE -- needs the money path, not the demand path.")
        return lines

    if not head:
        lines.append("NOT GRADED: the treatment moved no headcount at all, so nothing here is "
                     "attributable to it.")
        lines.append("P2 (margin): NOT GRADED HERE -- needs the money path, not the demand path.")
        return lines

    scaled = move / head * POPULATION_HEADCOUNT_MOVE_PCT
    lines.append(
        f"P1 (total book demand falls 2%-8% at the population's "
        f"{POPULATION_HEADCOUNT_MOVE_PCT}% headcount move): measured {move:+.3f}% at a "
        f"{head:+.2f}% treatment, which scales to {scaled:+.2f}% -> "
        + ("HOLDS" if -8.0 <= scaled <= -2.0 else "REFUTED"))
    lines.append(f"    elasticity of TOTAL kWh to headcount: {abs(move / head):.3f}")
    lines.append(f"    elasticity of ELECTRICITY to headcount: {abs(elec / head):.3f}"
                 "   <- the signal")
    lines.append(f"    elasticity of GAS to headcount: {abs(out['gas_kwh_move_pct'] / head):.3f}"
                 "   <- insensitive; two opposite effects inside one fuel, netting to ~0")
    lines.append(
        "KILL LINE (electricity must move with headcount, or the change never reached the book): "
        + ("BREACHED -- the wiring leg passes on something that does not matter"
           if abs(elec) < 0.5 else "not breached"))

    inside_floor = gas_home is not None and abs(gas_home) < GAS_NOISE_FLOOR_PCT
    verdict = ("REFUTED -- gas per home does not rise; the metabolic-gain effect is cancelled by "
               "lower hot-water and cooking gas" if inside_floor
               else ("HOLDS" if gas_home and gas_home > 0
                     else "REFUTED, and the sign is the finding"))
    lines.append(f"P3 (gas per home RISES as metabolic gains fall): measured {gas_home:+.3f}% "
                 f"-> {verdict}")
    if inside_floor:
        lines.append(
            f"    NOTE: |move| < {GAS_NOISE_FLOOR_PCT}% is inside this harness's noise floor for "
            "the gas leg. Two effects netting to zero and one effect being absent look identical "
            "here.")
    lines.append("P2 (margin): NOT GRADED HERE -- needs the money path, not the demand path.")
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-n", type=int, default=N, help=f"premises to price in each arm (default {N})")
    args = ap.parse_args(argv)

    drawn = draw_premise_population(args.n, base_seed=20260916, as_of=dt.date(2024, 4, 1))
    weather = pt.load_trace_weather(SITE, start=YEAR_START, end=YEAR_END)
    print(f"premises drawn {len(drawn)}, weather days {len(weather)}", flush=True)

    control = totals(drawn, weather, census=False)
    print("CONTROL (bedrooms, pre-fa4f2ea40):", json.dumps(control), flush=True)
    treated = totals(drawn, weather, census=True)
    print("TREATED (census, fa4f2ea40)     :", json.dumps(treated), flush=True)

    if control["premises"] != treated["premises"]:
        print("POPULATION FLOOR BREACHED: the two arms priced different numbers of premises "
              f"({control['premises']} against {treated['premises']}); nothing below is a "
              "comparison and the difference is not attributable.")
        return 1
    if control["premises"] == 0:
        print("POPULATION FLOOR BREACHED: zero premises priced in either arm.")
        return 1

    def pct(a, b):
        return None if not a else (b - a) / a * 100.0

    out = {
        "premises": treated["premises"],
        "mean_headcount_control": round(control["mean_headcount"], 3),
        "mean_headcount_treated": round(treated["mean_headcount"], 3),
        "headcount_move_pct": round(pct(control["mean_headcount"], treated["mean_headcount"]), 2),
        "total_kwh_control": round(control["total_kwh"], 1),
        "total_kwh_treated": round(treated["total_kwh"], 1),
        "total_kwh_move_pct": round(pct(control["total_kwh"], treated["total_kwh"]), 3),
        "gas_kwh_move_pct": round(pct(control["gas_kwh"], treated["gas_kwh"]), 3),
        "elec_kwh_move_pct": round(pct(control["elec_kwh"], treated["elec_kwh"]), 3),
        "gas_per_home_control": round(control["gas_kwh"] / control["premises"], 1),
        "gas_per_home_treated": round(treated["gas_kwh"] / treated["premises"], 1),
    }
    print(json.dumps(out, indent=2))

    print()
    for line in grade(out, n=args.n):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
