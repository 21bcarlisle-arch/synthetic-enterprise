"""How many household cases reproduce the observed demand DISTRIBUTION, and how many span response.

REUSE: tools/demand_vector_coverage.py
CLASS: CUSTOM
INDEX: searched "distribution", "acceptance", "sample size", "vector", "coverage", "KS".
       `tools/demand_case_coverage.py` answered the same question against a SCALAR (annual kWh) and
       is the thing the canon corrects; its cell space and demand model are imported, its criterion
       is not. `tools/space_filling_sample.py` draws for difference and measures variance covered --
       also a scalar criterion, also superseded here. `tools/need_stock_joint.py` reads NEED and is
       imported. Nothing measures a DISTRIBUTIONAL acceptance.

WHY THIS EXISTS
---------------
`DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07`, section 5:

    "Variance coverage is not the criterion, and a chosen percentage is not a test... the goal here
     is distributional... Span-the-support and reproduce-the-distribution are OPPOSED criteria -- a
     space-filling draw deliberately over-represents tails -- and you get both only if each drawn
     case carries the population mass it stands for. So the sample is weighted, and N is set by a
     weighted distributional acceptance test with a stated power."

And section 2: **two numbers are reported, and the second is the real one** -- N to reproduce the
observed distribution, and N to also span intervention response, because two households with
identical consumption and opposite insulation ceilings are different customers and the mission is
ranking interventions.

THE POPULATION IS NEED ROWS CROSSED WITH CELLS, NOT AGGREGATED CASES
--------------------------------------------------------------------
`demand_case_coverage` bucketed the stock into 274 (type, age, area, EPC) cases. That was right for
a variance question and wrong here: the intervention axes depend on what is ALREADY INSTALLED, and
NEED carries `LI_FLAG`, `CWI_FLAG` and `PV_FLAG` per dwelling. Bucketing averages those away --
precisely the two-households-one-bucket collapse the canon names. So a household here is a NEED ROW
crossed with a weather cell, and the joint of fabric with existing measures is the observed one
rather than a product of marginals.

WHAT IS MEASURED AND WHAT IS NAMED ABSENT
------------------------------------------
Measured (the heat-driven axes, per the director's sequencing decision):

    annual_gas_kwh          modelled space-heat demand
    seasonal_swing          the share of the year's demand falling in the coldest half
    insulation_ceiling_kwh  what the REMAINING measures would save, given LI/CWI already installed
    turndown_ceiling_kwh    one degree off the set-point

NAMED ABSENT, not silently skipped: annual ELECTRICITY and its half-hourly shape. For the 81% of
households on gas, electricity is appliances, lights and EV rather than fabric, and there is no
non-heat electrical base in the demand model until `W2_19` lands. The canon's decision is to measure
now on the heat-driven axes and re-measure the full vector then, so **every N here is a FLOOR**.

SHAPE IS MODELLED AND NOT VALIDATED, by the director's decision of 2026-09-07. The only household
shape artefact available is Elexon Profile Class 1 -- one population-average curve on a 1997
reference year -- and NEED is annual. SERL is accredited-access and is not being pursued.
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

#: The axes that describe what a household USES. Reproducing their joint distribution is the
#: canon's first number.
DISTRIBUTION_AXES = ("annual_gas_kwh", "seasonal_swing")

#: The axes that describe what could be DONE for a household. The canon's second number adds these,
#: and calls it the real one: a sample that reproduces consumption perfectly can still be unable to
#: rank interventions, and ranking interventions is the mission.
RESPONSE_AXES = ("insulation_ceiling_kwh", "turndown_ceiling_kwh")

AXES = DISTRIBUTION_AXES + RESPONSE_AXES

#: THE TOLERANCE, AND IT IS A DECLARED CHOICE. The sample's empirical distribution must lie within
#: this distance of the population's, everywhere, on every axis: no point of any distribution is
#: misplaced by more than five percentage points of mass, which is half a decile.
#:
#: IT IS AN ABSOLUTE BAR, AND THE FIRST VERSION'S WAS NOT. That version accepted a sample when its
#: KS distance fell under the two-sample CRITICAL VALUE at alpha -- and the critical value grows as
#: n shrinks, so a 13-case sample passed trivially because a test that size has almost no power to
#: fail. It returned N = 13 and N = 21, the smallest sizes on the ladder, which is the answer that
#: criterion will always give. A sample-size rule whose bar loosens as the sample shrinks is not a
#: sample-size rule.
DISTRIBUTION_TOLERANCE = 0.05

#: Significance used for the POWER statement reported beside each n -- the discrepancy a test at
#: this level could actually have detected at that size. Kept because "with a stated power" is what
#: the canon asks for, and a tolerance met by a sample too small to test is worth flagging.
ALPHA = 0.05

#: The KS critical coefficient for `ALPHA`: D_crit = KS_CRITICAL * sqrt(1/n + 1/m). Two-sample,
#: two-sided, large-sample form. 1.358 is the standard tabulated value at 5%.
KS_CRITICAL = 1.358

#: Sizes the acceptance is reported at. Geometric, because the answer is expected in the thousands
#: and an arithmetic ladder would spend every step where the curve is already flat.
NS = (13, 21, 34, 55, 89, 144, 233, 300, 377, 450, 520, 610, 700, 800, 987, 1200, 1597, 2000,
      2584, 3300, 4181, 5400, 6765, 8500, 10946, 14000, 17711, 23000, 30000)

#: How many independent draws each n is judged over. An acceptance that holds on one lucky seed is
#: not an acceptance; N is the smallest size that passes on EVERY replicate.
REPLICATES = 5

#: Random directions the joint is tested along, on top of the axes themselves.
#:
#: A PER-AXIS TEST ONLY COMPARES MARGINALS, and that is the canon's own defect one level up. The
#: first version tested each axis separately and returned the SAME N with and without the response
#: axes -- because two households with identical consumption and opposite insulation ceilings differ
#: in the JOINT and not in either margin, which is the exact pair the canon says are different
#: customers. Projecting the standardised vector onto random unit directions and taking the worst
#: KS over all of them tests the joint: a discrepancy in any linear combination shows up in some
#: direction, and the coordinate axes are included so the marginal test is not lost.
JOINT_SLICES = 64

#: The reference population size the acceptance is measured against. Large enough that the critical
#: value is set by the SAMPLE rather than by the reference.
POPULATION_POINTS = 120_000


def _need_rows():
    from tools import need_stock_joint as need

    if not need.NEED_CSV.is_file():
        raise FileNotFoundError(
            f"{need.NEED_CSV} is absent. This measurement is against DESNZ NEED's observed stock; "
            "there is no substitute that carries the installed-measure flags.")
    with need.NEED_CSV.open(encoding="utf-8-sig") as fh:
        return [r for r in csv.DictReader(fh) if r.get("Gcons2024") not in (None, "", "NA")]


def _fabric_for(row, *, retrofitted: bool):
    """The fabric vector for one NEED dwelling, as built or with the remaining measures taken.

    THE CEILING IS WHAT IS LEFT TO DO, not what a bare fabric would gain. A dwelling whose
    `LI_FLAG` and `CWI_FLAG` are already 1 has had the cheap measures; crediting it the full
    retrofit is how a sample comes to rank two very different customers identically, which is the
    collapse this module exists to measure.
    """
    from simulation import fabric_physics as fp
    from simulation.household import (
        BoilerAge,
        BuildEra,
        HeatingSystem,
        Household,
        InsulationLevel,
        PropertyType,
    )
    from tools import demand_case_coverage as dcc
    from tools import need_stock_joint as need

    property_type = PropertyType[need.PROPERTY_TYPE[row["PROP_TYPE"]]]
    base = fp._FLOOR_AREA_BASE_M2[property_type]
    area = dcc.AREA_MIDPOINT[row["FLOOR_AREA_BAND"]]
    bedrooms = int(max(1, min(6, round(2 + (area - base) / fp._FLOOR_AREA_PER_BEDROOM_M2))))

    installed = (row.get("LI_FLAG") == "1") + (row.get("CWI_FLAG") == "1")
    if retrofitted:
        level = "FULL"
    else:
        level = ("FULL" if installed == 2 else "PARTIAL" if installed == 1 else "POOR")

    household = Household(
        customer_id="C", property_type=property_type,
        build_era=BuildEra[dcc.AGE_TO_ERA[row["PROP_AGE_BAND"]]],
        epc_rating="D", bedrooms=bedrooms, heating_system=HeatingSystem.GAS_BOILER_COMBI,
        boiler_age=BoilerAge.MID, has_solar=False, solar_kwp=0.0, solar_install_year=None,
        has_battery=False, battery_kwh=0.0, has_ev=False, ev_charger_kw=0.0,
        has_smart_meter=True, smart_meter_install_year=2020,
        insulation=InsulationLevel[level], has_driveway=True, roof_aspect="south")
    p = fp.fabric_parameters(household)
    return (p.fabric_w_per_k, p.raw_infiltration_ach, p.volume_m3,
            p.solar_aperture_m2, p.internal_gain_kw)


def population(points: int = POPULATION_POINTS, seed: int = 0) -> dict:
    """A household-weighted sample of (NEED dwelling x weather cell), with its output vector.

    Each point stands for the same population mass by construction -- the cell is drawn with
    probability proportional to its households and the dwelling with probability proportional to
    its region's share -- so the sample IS the distribution and no separate weight is carried.
    That is what makes a distributional test over it meaningful.
    """
    import numpy as np

    from simulation import fabric_physics as fp
    from tools import demand_case_coverage as dcc

    grid = dcc.demand_grid()
    hdd = np.asarray(grid["cell_hdd"])
    wind = np.asarray(grid["cell_wind"])
    solar_index = np.asarray(grid["cell_solar_index"])
    cell_weight = np.asarray(grid["cell_weights"], dtype=float)

    rows = _need_rows()
    rng = np.random.default_rng(seed)
    cell_pick = rng.choice(len(hdd), size=points, replace=True, p=cell_weight / cell_weight.sum())
    row_pick = rng.integers(0, len(rows), size=points)

    # Fabric is derived per DISTINCT dwelling shape, not per point: the same (type, age, area,
    # measures) recomputes an identical vector, and 40,000 constructions is minutes where 120,000
    # would be tens of minutes for no new information.
    cache: dict = {}
    as_built = np.empty((points, 5))
    retrofit = np.empty((points, 5))
    for i, ri in enumerate(row_pick):
        row = rows[ri]
        key = (row["PROP_TYPE"], row["PROP_AGE_BAND"], row["FLOOR_AREA_BAND"],
               row.get("LI_FLAG"), row.get("CWI_FLAG"))
        if key not in cache:
            cache[key] = (_fabric_for(row, retrofitted=False), _fabric_for(row, retrofitted=True))
        as_built[i], retrofit[i] = cache[key]

    reference_solar = dcc._reference_solar_kwh_per_m2()
    hours = len(dcc.DOYS) * 24.0
    cold = hdd[cell_pick]
    warm = dcc._seasonal_hdd(_winter_from_hdd(cold), setpoint_c=dcc.SETPOINT_C - 1.0)
    site_wind = wind[cell_pick]
    site_solar = solar_index[cell_pick]

    def demand(params, degree_days):
        ach = np.maximum(params[:, 1] * (site_wind / fp.SAP_REFERENCE_WIND_MS),
                         fp._MINIMUM_VENTILATION_ACH)
        hlc = (params[:, 0] + 0.33 * ach * params[:, 2]) / 1000.0
        gross = hlc * degree_days * 24.0
        gains = params[:, 3] * reference_solar * site_solar + params[:, 4] * hours
        return np.maximum(0.0, gross - gains), hlc

    gas, hlc = demand(as_built, cold)
    gas_turndown, _ = demand(as_built, warm)
    gas_retrofit, _ = demand(retrofit, cold)

    # SEASONAL SWING: the share of demand falling in the coldest half of the heating season. A
    # MODELLED quantity, published as such -- see the module docstring and the director's decision.
    half = len(dcc.DOYS) // 2
    doys = np.array(dcc.DOYS)
    coldest = np.isin(doys, doys[np.argsort(-_seasonal_profile())][:half])
    swing = np.full(points, float(coldest.sum()) / len(doys))
    swing = swing * (1.0 + 0.15 * (hlc - hlc.mean()) / (hlc.std() or 1.0))

    values = np.stack([gas, swing,
                       np.maximum(0.0, gas - gas_retrofit),
                       np.maximum(0.0, gas - gas_turndown)], axis=1)
    fuel = np.array([rows[ri].get("MAIN_HEAT_FUEL", "?") for ri in row_pick])
    observed = np.array([float(rows[ri]["Gcons2024"]) for ri in row_pick])
    return {"values": values, "axes": AXES, "fuel": fuel, "observed_gas": observed,
            "cells": cell_pick, "rows": row_pick, "n_need_rows": len(rows)}


def _seasonal_profile():
    import numpy as np

    from tools import demand_case_coverage as dcc

    doys = np.array(dcc.DOYS)
    return 8.0 - 5.0 * np.cos(2 * np.pi * (doys - 15) / 365.0)


def _winter_from_hdd(hdd):
    import numpy as np

    from tools import demand_case_coverage as dcc

    probe = np.linspace(-5.0, 15.0, 401)
    table = dcc._seasonal_hdd(probe)
    order = np.argsort(table)
    return np.interp(np.asarray(hdd), table[order], probe[order])


def ks_distance(sample, reference) -> float:
    """Two-sample Kolmogorov-Smirnov distance between two 1-D sets of equal-mass points."""
    import numpy as np

    a = np.sort(np.asarray(sample, dtype=float))
    b = np.sort(np.asarray(reference, dtype=float))
    grid = np.concatenate([a, b])
    return float(np.max(np.abs(np.searchsorted(a, grid, "right") / len(a)
                               - np.searchsorted(b, grid, "right") / len(b))))


def accepts(sample_values, population_values, axes=AXES,
            tolerance: float = DISTRIBUTION_TOLERANCE, alpha: float = ALPHA) -> dict:
    """Does this sample reproduce the population's distribution to within `tolerance`, per axis?

    THE BAR DOES NOT MOVE WITH n, and that is the whole correction. `detectable` reports what a KS
    test at `alpha` could have caught at this size -- so a row where `detectable` exceeds
    `tolerance` is a size at which the sample is being asked for more accuracy than a test that
    size could verify, and it is flagged rather than quietly counted as a pass.
    """
    import numpy as np

    sample = np.asarray(sample_values, dtype=float)
    reference = np.asarray(population_values, dtype=float)
    n, m = len(sample), len(reference)
    detectable = KS_CRITICAL * ((1.0 / n + 1.0 / m) ** 0.5)

    # Standardised on the POPULATION's own scale, so a direction mixes the axes by their spread
    # rather than by their units -- kWh and a dimensionless swing are four orders apart.
    mean = reference.mean(axis=0)
    sd = reference.std(axis=0)
    sd = np.where(sd == 0, 1.0, sd)
    zs, zr = (sample - mean) / sd, (reference - mean) / sd

    out = {}
    for j, axis in enumerate(axes):
        d = ks_distance(sample[:, j], reference[:, j])
        out[axis] = {"d": round(d, 5), "tolerance": tolerance,
                     "detectable_at_alpha": round(detectable, 5),
                     "accepts": bool(d <= tolerance)}

    rng = np.random.default_rng(12345)          # fixed: the directions are part of the TEST
    directions = rng.normal(size=(JOINT_SLICES, zr.shape[1]))
    directions /= np.linalg.norm(directions, axis=1, keepdims=True)
    worst = max(ks_distance(zs @ u, zr @ u) for u in directions)
    out["JOINT"] = {"d": round(worst, 5), "tolerance": tolerance,
                    "detectable_at_alpha": round(detectable, 5),
                    "accepts": bool(worst <= tolerance),
                    "slices": JOINT_SLICES}
    return out


class _Reference:
    """The population, pre-projected once onto every test direction.

    WITHOUT THIS THE MEASUREMENT DOES NOT FINISH. `accepts` re-projected a 120,000-point reference
    onto 64 directions on EVERY call, and the ladder makes tens of thousands of calls -- the same
    arithmetic repeated for an answer that never changes. Projected and sorted once here; a sample
    then costs only its own projection and a searchsorted.
    """

    def __init__(self, values, axes, slices: int = JOINT_SLICES):
        import numpy as np

        self.axes = tuple(axes)
        self.values = np.asarray(values, dtype=float)
        self.mean = self.values.mean(axis=0)
        sd = self.values.std(axis=0)
        self.sd = np.where(sd == 0, 1.0, sd)
        rng = np.random.default_rng(12345)      # fixed: the directions are part of the TEST
        directions = rng.normal(size=(slices, self.values.shape[1]))
        self.directions = directions / np.linalg.norm(directions, axis=1, keepdims=True)
        z = (self.values - self.mean) / self.sd
        self.marginals = [np.sort(self.values[:, j]) for j in range(self.values.shape[1])]
        self.projections = [np.sort(z @ u) for u in self.directions]
        self.n = len(self.values)


def _ks_against_sorted(sample, sorted_reference) -> float:
    import numpy as np

    a = np.sort(np.asarray(sample, dtype=float))
    grid = np.concatenate([a, sorted_reference])
    return float(np.max(np.abs(
        np.searchsorted(a, grid, "right") / len(a)
        - np.searchsorted(sorted_reference, grid, "right") / len(sorted_reference))))


def accepts_against(sample, reference, tolerance: float = DISTRIBUTION_TOLERANCE,
                    alpha: float = ALPHA) -> dict:
    """`accepts`, against a pre-projected reference. Same statistic, same bar."""
    import numpy as np

    sample = np.asarray(sample, dtype=float)
    detectable = KS_CRITICAL * ((1.0 / len(sample) + 1.0 / reference.n) ** 0.5)
    out = {}
    for j, axis in enumerate(reference.axes):
        d = _ks_against_sorted(sample[:, j], reference.marginals[j])
        out[axis] = {"d": round(d, 5), "tolerance": tolerance,
                     "detectable_at_alpha": round(detectable, 5), "accepts": bool(d <= tolerance)}
    z = (sample - reference.mean) / reference.sd
    worst = max(_ks_against_sorted(z @ u, proj)
                for u, proj in zip(reference.directions, reference.projections))
    out["JOINT"] = {"d": round(worst, 5), "tolerance": tolerance,
                    "detectable_at_alpha": round(detectable, 5),
                    "accepts": bool(worst <= tolerance), "slices": JOINT_SLICES}
    return out


def smallest_n(pop, axes, ns=NS, replicates: int = REPLICATES, seed: int = 0,
               tolerance: float = DISTRIBUTION_TOLERANCE, reference=None):
    """The smallest n whose draw reproduces the population to within `tolerance` on every axis AND
    on every joint direction, on every replicate. Returns (n, per-n verdicts)."""
    import numpy as np

    values = np.asarray(pop["values"])
    keep = [AXES.index(a) for a in axes]
    reference = reference if reference is not None else _Reference(values[:, keep], axes)
    rng = np.random.default_rng(seed)
    verdicts, answer = {}, None
    for n in ns:
        if n >= len(values):
            break
        passed = 0
        worst = 0.0
        for r in range(replicates):
            pick = rng.choice(len(values), size=n, replace=False)
            # THE AXES BEING TESTED ARE PASSED IN, not assumed. The first draft let `accepts`
            # iterate the full axis list while being handed a two-column subset, so the response
            # columns were read off the end of the array -- a sizing answer would have come from
            # whatever those indices hit.
            result = accepts_against(values[pick][:, keep], reference, tolerance=tolerance)
            worst = max(worst, max(v["d"] for v in result.values()))
            passed += all(v["accepts"] for v in result.values())
        verdicts[n] = {"replicates_passed": passed, "of": replicates,
                       "worst_ks_distance": round(worst, 4),
                       "tolerance": tolerance}
        if passed == replicates and answer is None:
            answer = n
    return answer, verdicts


#: The price list. The canon asks for answers "as price lists, not single numbers", so N is
#: reported at several accuracies rather than at the one this module happens to prefer.
TOLERANCES = (0.10, 0.05, 0.02)


def binding_axis(pop, axes, n, seed: int = 0) -> str:
    """Which axis or direction is the one still failing at `n` -- what dominates the count."""
    import numpy as np

    values = np.asarray(pop["values"])
    keep = [AXES.index(a) for a in axes]
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(values), size=min(n, len(values) - 1), replace=False)
    result = accepts_against(values[pick][:, keep], _Reference(values[:, keep], axes))
    return max(result, key=lambda k: result[k]["d"])


def measurement(points: int = POPULATION_POINTS, seed: int = 0) -> dict:
    """Both numbers the canon asks for, at several accuracies, and the second is the real one."""
    pop = population(points=points, seed=seed)
    import numpy as np

    price_list = {}
    allv = np.asarray(pop["values"])
    ref_d = _Reference(allv[:, [AXES.index(a) for a in DISTRIBUTION_AXES]], DISTRIBUTION_AXES)
    ref_r = _Reference(allv[:, [AXES.index(a) for a in AXES]], AXES)
    for tol in TOLERANCES:
        nd, curve_d = smallest_n(pop, DISTRIBUTION_AXES, tolerance=tol, seed=seed, reference=ref_d)
        nr, curve_r = smallest_n(pop, AXES, tolerance=tol, seed=seed, reference=ref_r)
        price_list[f"{tol:.2f}"] = {
            "n_to_reproduce_the_distribution": nd,
            "n_to_also_span_intervention_response": nr,
            "dominated_by": binding_axis(pop, AXES, nr or max(NS), seed=seed) if nr else None,
        }
    n_distribution, curve_d = smallest_n(pop, DISTRIBUTION_AXES, seed=seed, reference=ref_d)
    n_response, curve_r = smallest_n(pop, AXES, seed=seed, reference=ref_r)
    values = allv
    return {
        "price_list_by_tolerance": price_list,
        "population_points": int(len(values)),
        "need_dwellings": pop["n_need_rows"],
        "axes_measured": list(AXES),
        "axes_named_absent": ["annual_electricity_kwh", "half_hourly_electricity_shape"],
        "alpha": ALPHA,
        "tolerance": DISTRIBUTION_TOLERANCE,
        "replicates": REPLICATES,
        "n_to_reproduce_the_distribution": n_distribution,
        "n_to_also_span_intervention_response": n_response,
        "distribution_curve": curve_d,
        "response_curve": curve_r,
        "every_n_is_a_floor_because": (
            "annual electricity and its half-hourly shape are absent until W2_19 lands, so adding "
            "them can only raise N"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--measure", action="store_true", help="both N figures and their curves")
    ap.add_argument("--points", type=int, default=POPULATION_POINTS)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    if args.measure:
        print(json.dumps(measurement(points=args.points, seed=args.seed), indent=2, default=str))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
