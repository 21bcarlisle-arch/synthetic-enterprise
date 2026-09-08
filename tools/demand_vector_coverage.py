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
import collections
import csv
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

#: The axes that describe what a household USES. Reproducing their joint distribution is the
#: canon's first number.
DISTRIBUTION_AXES = ("annual_gas_kwh", "annual_electricity_kwh", "seasonal_swing",
                     "weather_sensitivity_kwh_per_degree_day", "peak_window_share")

#: The axes that describe what could be DONE for a household. The canon's second number adds these,
#: and calls it the real one: a sample that reproduces consumption perfectly can still be unable to
#: rank interventions, and ranking interventions is the mission.
RESPONSE_AXES = ("insulation_ceiling_kwh", "turndown_ceiling_kwh")

AXES = DISTRIBUTION_AXES + RESPONSE_AXES

from tools.reduction_dimension import DEMAND_VECTOR, declare  # noqa: E402  (after the path fix)

#: WHAT THIS INSTRUMENT'S N IS AN N FOR. The canon's section 2 vector plus the two response axes it
#: adds, because "two households with identical gas, electricity, shape and fuel can have opposite
#: insulation ceilings" -- so response is a component of the subject here, not a derived view of it.
_SUBJECT = DEMAND_VECTOR + ("insulation_headroom", "turndown_headroom")

#: THE DECLARATION IS WHY EVERY N HERE IS A FLOOR, and it now says something narrower than it did.
#:
#: IT USED TO DECLARE ANNUAL ELECTRICITY BLIND, on the reasoning that there is no non-heat electrical
#: base in the demand model until `W2_19` lands. That bundled two axes with different dependencies:
#: the HALF-HOURLY SHAPE needs a presence pattern and genuinely waits for `W2_19`, while ANNUAL
#: ELECTRICITY is carried per dwelling by NEED -- 46,234 observed rows -- and waits for nothing. The
#: director named the consequence: a floor deferred is a number not taken.
#:
#: `heating_fuel` leaves `blind_to` for a different reason. It is not an axis a distance is measured
#: along -- "how far is gas from electric" is not a quantity -- but the acceptance is now run WITHIN
#: EACH FUEL STRATUM and every stratum must pass, so the figure does distinguish fuel and saying it
#: is blind would be false.
#:
#: What remains blind is the half-hourly electricity shape, and that is the whole of why this N is
#: still a floor.
REDUCES_OVER = declare(
    "the sample size that reproduces the observed demand distribution and spans response",
    kind="sufficiency",
    of=_SUBJECT,
    reduces_over=AXES + ("heating_fuel",),
    derived_from={"seasonal_swing": ("seasonal_gas_shape",),
                  # Sensitivity is how much the gas total MOVES with the weather, so it is built
                  # from the level and the shape together rather than being a fifth thing.
                  "weather_sensitivity_kwh_per_degree_day": ("annual_gas_kwh", "seasonal_gas_shape"),
                  # DERIVED FROM THE LEVEL, NOT THE SHAPE, and the AST control is what forced the
                  # correction. It was declared as derived from `half_hourly_electricity_shape`
                  # while that component was also declared blind, and it refused the pair: one of
                  # the two is wrong. The one that was wrong is this. Two of the three occupancy
                  # patterns produce proportional curves, so what this axis actually varies with is
                  # the household's consumption LEVEL and its elderly / not-elderly flag -- not the
                  # shape. Declaring it as shape-derived is what made the vector look complete.
                  "peak_window_share": ("annual_electricity_kwh",),
                  "insulation_ceiling_kwh": ("insulation_headroom",),
                  "turndown_ceiling_kwh": ("turndown_headroom",)},
    # THE BILLING AXES CANNOT APPEAR HERE, and that absence is itself the finding. `blind_to` may
    # only name components of the SUBJECT vector, and payment method, read pattern, arrears, moves
    # and credit position are not in the demand vector at all -- so the declaration cannot express
    # that this N does not span them. `UNCOUNTED_AXES` carries them instead, and the gap between
    # what the declaration can say and what is actually missing is why the figure is published as a
    # FLOOR rather than as a size.
    # HALF-HOURLY SHAPE GOES BACK ON THE BLIND LIST, and claiming otherwise was premature. The
    # `peak_window_share` axis is in the measurement and does not carry the composition signal it
    # appears to: two of the three occupancy patterns are proportional, so it distinguishes elderly
    # from everyone else and nothing finer. An axis that is PRESENT but carries a level rather than
    # a shape is worse than an absent one, because the vector looks complete.
    blind_to=("half_hourly_electricity_shape",),
    joint=True,
)

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

#: The half-hourly shape, reduced to the statistic the PRICE cares about: the share of a day's
#: electricity consumed in the 16:00-19:00 window. The canon sets the resolution by price rather
#: than physics, and this is that resolution -- two households with identical annual kWh, one with
#: a sharp evening peak and one flat, are a different cost to serve and a different hedge.
#:
#: MEASURED, THEN RE-MEASURED WHEN THE DIRECTOR REFUSED THE RESULT, and the second reading reverses
#: the first. I reported that the peak share runs 0.196 to 0.253 across occupancy patterns and
#: concluded the world varies shape "on effectively one binary". He replied that `single` and
#: `family` agreeing to four decimal places is not two populations agreeing -- it is one object
#: counted twice -- and asked for the mechanism rather than the number.
#:
#: HE IS RIGHT AND THE AXIS IS LARGELY AN ARTEFACT. `demand_model.occupancy_multiplier` does carry a
#: per-pattern shape term, so the world is not simply rescaling one curve. But the `family` and
#: `single` multiplier vectors -- (1.1, 0.85, 1.4) and (1.0, 0.75, 1.25) over morning/day/evening --
#: are NEARLY PROPORTIONAL: their ratios are 1.10, 1.133, 1.12, a spread of 0.033. A share is
#: scale-invariant, so proportional curves have IDENTICAL SHAPE and differ only in level. Measured
#: on the real profile the maximum normalised difference between them is 0.0005, while their totals
#: differ 11.9 kWh against 13.3.
#:
#: `elderly` reshapes because its ratios spread by 0.72 -- daytime ABOVE evening, which no rescaling
#: can produce. So the axis carries an elderly / not-elderly distinction and almost nothing else.
#:
#: AND THE VOCABULARY CANNOT EXPRESS WHAT THE DIRECTOR DESCRIBED. The bands are morning, day and
#: evening; there is no after-school band, and `children_count` is documented as not moving the
#: shape at all. A family with young children cannot have the morning-and-after-school signature he
#: named, because the model has nowhere to put it.
PEAK_WINDOW_IS_LEVEL_DRIVEN = True
PEAK_WINDOW = slice(32, 38)

#: WHAT THIS N IS BLIND TO, ENUMERATED, so no reader can take it for the size of the book. The
#: director, 2026-09-07, refusing the figure: *"It's the number for a partial vector... the number
#: has moved an order of magnitude every time an axis arrived: 800 with retrofit flags, 8,500 when
#: electricity and the non-gas stratum went in. A single missing stratum multiplied it tenfold. I
#: have no reason to expect the remaining axes to behave differently."*
#:
#: He is right on the evidence and the escalation is the point: every one of these is an axis on
#: which two households can differ while matching on everything measured, and each is therefore a
#: direction the sample is currently NOT required to span.
UNCOUNTED_AXES = (
    "half_hourly_shape_by_composition",  # the axis exists and is level-driven -- see PEAK_WINDOW
    "payment_method_third_category",     # DD is anchored; the PPM/standard-credit split is a
                                         # NAMED GAP in ASSUMPTIONS.md, not a rounding
    "meter_read_pattern",                # quarterly estimate against half-hourly settlement
    "arrears_position",
    "move_history",
    "credit_position",
    "tariff_and_dates",
)

#: Significance used for the POWER statement reported beside each n -- the discrepancy a test at
#: this level could actually have detected at that size. Kept because "with a stated power" is what
#: the canon asks for, and a tolerance met by a sample too small to test is worth flagging.
ALPHA = 0.05

#: The KS critical coefficient for `ALPHA`: D_crit = KS_CRITICAL * sqrt(1/n + 1/m). Two-sample,
#: two-sided, large-sample form. 1.358 is the standard tabulated value at 5%.
KS_CRITICAL = 1.358

#: Sizes the acceptance is reported at. Geometric, because the answer is expected in the thousands
#: and an arithmetic ladder would spend every step where the curve is already flat.
#: Sizes the CHOSEN design is reported at. Separate from `NS` because a designed sample
#: answers one to two orders of magnitude lower and a random ladder would spend every
#: step past the answer.
CHOSEN_NS = (34, 55, 89, 110, 130, 150, 175, 200, 230, 260, 300, 377, 500, 700, 1000,
             1400, 1800, 2300, 3000, 4000, 5200)

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
    def _number(row, column):
        try:
            return float(row.get(column))
        except (TypeError, ValueError):
            return None

    with need.NEED_CSV.open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    # SELECTED ON ELECTRICITY, NOT GAS, and the first version's filter was a silent exclusion.
    # Filtering on `Gcons2024` kept only dwellings that HAVE a gas meter: 39,502 rows, every one of
    # them MAIN_HEAT_FUEL = 1. The entire non-gas stratum -- 8,547 dwellings, 18.5% of the stock --
    # was absent from a measurement whose own canon says "gas-heated and electrically-heated
    # households at the same total are not the same case at all". Electricity is near-universal, so
    # selecting on it keeps both fuels; gas is then a QUANTITY that is zero for a home without it,
    # which is what a home without gas actually consumes.
    kept = []
    for row in rows:
        elec = _number(row, "Econs2024")
        if elec is None:
            continue
        row["_elec"] = elec
        row["_gas"] = _number(row, "Gcons2024") or 0.0
        kept.append(row)
    return kept


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


def _peak_window_share(points: int, rng):
    """Each household's share of daily electricity in the 16:00-19:00 window.

    Computed from the world's OWN shape builder rather than invented here: `demand_model.
    build_demand_shape` applied to the published Profile Class 1 base, per occupancy pattern and
    household size. The three patterns are drawn at the shares `household_segments` already uses,
    so the distribution of shapes is the world's and not a second opinion about it.

    FAILS TO A CONSTANT, VISIBLY. If the profile data is absent the axis is a constant, which makes
    it contribute nothing to any distance rather than contributing a fabricated spread -- and a
    constant axis is detectable in the output, where an invented one would not be.
    """
    import numpy as np

    try:
        from sim.profile_class_1 import load_pc1_shape
        from simulation import demand_model as dm
        base = load_pc1_shape("2024-01-15")
    except Exception:      # noqa: BLE001 -- see the docstring
        return np.full(points, 0.2059)

    table = {}
    for pattern in ("single", "family", "elderly"):
        for people in (1, 2, 3, 4, 5):
            prop = {"heating_system": "gas_boiler", "occupancy_pattern": pattern,
                    "assets": {}, "people_count": people}
            try:
                shape = dm.build_demand_shape(list(base), 8.0, "electricity", prop)
                table[(pattern, people)] = float(sum(shape[PEAK_WINDOW]) / sum(shape))
            except Exception:      # noqa: BLE001
                continue
    if not table:
        return np.full(points, 0.2059)

    keys = sorted(table)
    #: Occupancy-pattern shares as `household_segments` holds them; sizes from the TS017 anchor.
    weights = np.array([(0.30 if k[0] == "single" else 0.50 if k[0] == "family" else 0.20)
                        * (0.301, 0.340, 0.160, 0.129, 0.070)[k[1] - 1] for k in keys])
    pick = rng.choice(len(keys), size=points, replace=True, p=weights / weights.sum())
    return np.array([table[keys[i]] for i in pick])


def generated_population(points: int = POPULATION_POINTS, seed: int = 0) -> dict:
    """A GENERATED population: modelled houses, each placed in a real GB weather cell.

    `DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07`: *"NEED -- and any comparable survey --
    is EVIDENCE, NOT POPULATION."* `population()` above selected NEED rows, and two consequences
    followed that the canon names:

      * **No Scottish dwelling could be chosen at all.** NEED covers England and Wales, so the cell
        space was filtered by `region == "S92000003"` and the coldest 8% of the book -- where
        weather sensitivity is largest -- was excluded by construction. The household map already
        carried Scotland's 2,508,542 households; only the survey did not.
      * **Coverage was capped at the combinations 46,000 rows happened to contain.**

    Here the stock attributes are DRAWN FROM THE FITTED JOINT, so combinations appear at the rate
    they co-occur, and consumption is drawn from the evidence CONDITIONAL on the drawn combination
    -- which is what keeps a generated household anchored to something real without selecting it.

    SCOTLAND IS RAKED, NOT ASSUMED. The joint is England-and-Wales-fitted, so its property-type
    margin is moved onto Scotland's own Census 2022 UV402 shares (34.4% flats against England's
    much lower share) and the structure within a type is carried over. That carry-over is the
    assumption and it is smaller than pretending the Scottish stock is English.
    """
    import numpy as np

    from simulation import fabric_physics as fp
    from tools import demand_case_coverage as dcc
    from tools import stock_joint_generator as gen

    grid = dcc.demand_grid(include_scotland=True)
    hdd = np.asarray(grid["cell_hdd"])
    wind = np.asarray(grid["cell_wind"])
    solar_index = np.asarray(grid["cell_solar_index"])
    cell_weight = np.asarray(grid["cell_weights"], dtype=float)
    cell_nation = np.asarray(grid["cell_nation"])

    joint = gen.fit_joint()
    scots = gen.scotland_type_marginal()
    joint_by_nation = {"GB": joint}
    if scots:
        joint_by_nation["S"] = gen.raked_joint(joint, scots)

    # Consumption CONDITIONAL on the combination, from the evidence. A generated household is a
    # real combination and takes a real household's meter reading from that combination's pool.
    import csv as _csv

    from tools import need_stock_joint as need
    with need.NEED_CSV.open(encoding="utf-8-sig") as fh:
        rows = list(_csv.DictReader(fh))
    pools: dict = collections.defaultdict(list)
    for row in rows:
        if row.get("PROP_TYPE") not in need.PROPERTY_TYPE:
            continue
        try:
            elec = float(row.get("Econs2024"))
        except (TypeError, ValueError):
            continue
        try:
            gas = float(row.get("Gcons2024"))
        except (TypeError, ValueError):
            gas = 0.0
        key = (need.PROPERTY_TYPE[row["PROP_TYPE"]], row.get("PROP_AGE_BAND"),
               row.get("FLOOR_AREA_BAND"), row.get("EPC"), row.get("LI_FLAG"),
               row.get("CWI_FLAG"), row.get("PV_FLAG"), row.get("MAIN_HEAT_FUEL"))
        pools[key].append((gas, elec))

    rng = np.random.default_rng(seed)
    cell_pick = rng.choice(len(hdd), size=points, replace=True, p=cell_weight / cell_weight.sum())

    combos, fabric_cache = [], {}
    for nation in ("GB", "S"):
        mask = (cell_nation[cell_pick] == "S") if nation == "S" else (cell_nation[cell_pick] != "S")
        count = int(mask.sum())
        if not count:
            continue
        source = joint_by_nation.get(nation, joint)
        drawn = gen.generate(count, source, rng)
        combos.append((np.flatnonzero(mask), drawn))

    as_built = np.zeros((points, 5))
    retrofit = np.zeros((points, 5))
    gas_obs = np.zeros(points)
    elec_obs = np.zeros(points)
    fuel = np.empty(points, dtype=object)
    for index, drawn in combos:
        for slot, household in zip(index, drawn):
            key = tuple(household[k] for k in gen.JOINT_KEYS)
            if key not in fabric_cache:
                row = {"PROP_TYPE": _PROP_TYPE_BACK[household["property_type"]],
                       "PROP_AGE_BAND": household["age_band"],
                       "FLOOR_AREA_BAND": household["area_band"],
                       "LI_FLAG": household["loft"], "CWI_FLAG": household["cavity"]}
                fabric_cache[key] = (_fabric_for(row, retrofitted=False),
                                     _fabric_for(row, retrofitted=True))
            as_built[slot], retrofit[slot] = fabric_cache[key]
            pool = pools.get(key)
            if pool:
                gas_obs[slot], elec_obs[slot] = pool[int(rng.integers(len(pool)))]
            fuel[slot] = household["fuel"]

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
    swing = np.full(points, 0.5) * (1.0 + 0.15 * (hlc - hlc.mean()) / (hlc.std() or 1.0))

    # WEATHER SENSITIVITY IS AN AXIS, not an assumption that it is spanned. The director named it
    # among the things this figure did not confirm; it is the heat-loss coefficient in kWh per
    # degree-day, which the physics already computes, so there was no reason to leave it implicit.
    peak_share = _peak_window_share(points, rng)
    values = np.stack([gas, elec_obs, swing, hlc * 24.0, peak_share,
                       np.maximum(0.0, gas - gas_retrofit),
                       np.maximum(0.0, gas - gas_turndown)], axis=1)
    # PAYMENT METHOD, DRAWN AND CARRIED BUT NOT GIVEN A CONSUMPTION EFFECT. The canon keeps the
    # physical and commercial layers separate, and this is the commercial one; inventing an
    # under-heating effect to make it "matter" would merge them and would also be unsourced.
    # Carried so it can STRATIFY the acceptance -- which is the whole test of whether a stratum
    # multiplies the count even when it moves no measured axis.
    #
    # TWO CATEGORIES, NOT THREE, and the third is a known gap rather than a rounding. DESNZ QEP
    # anchors the direct-debit share (72% electricity, 75% gas); ASSUMPTIONS.md records the
    # prepayment-versus-standard-credit split of the remainder as NOT FOUND in the published
    # commentary. Splitting it here would be inventing the number this project keeps being burnt by.
    from simulation.population_draw import DD_SHARE_ELEC

    payment = np.where(rng.random(points) < DD_SHARE_ELEC, "direct_debit", "not_direct_debit")

    return {"values": values, "axes": AXES, "fuel": fuel, "observed_gas": gas_obs,
            "payment_method": payment,
            "cells": cell_pick, "cell_nation": cell_nation[cell_pick],
            "distinct_cells": int(len(set(cell_pick.tolist()))),
            "generated": True, "n_need_rows": len(rows)}


#: The generator speaks this project's property names and `_fabric_for` reads NEED's. One mapping,
#: here, rather than the generator learning a second vocabulary.
_PROP_TYPE_BACK = {"DETACHED": "Detached", "SEMI_DETACHED": "Semi detached",
                   "TERRACED": "Mid terrace", "FLAT": "Flat"}


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

    # OBSERVED electricity, not modelled: NEED carries it per dwelling, so this axis needs nothing
    # from `W2_19`. Only the HALF-HOURLY SHAPE does, which is the dependency that was mistakenly
    # taken to cover both.
    elec = np.array([rows[ri]["_elec"] for ri in row_pick])
    values = np.stack([gas, elec, swing, hlc * 24.0, _peak_window_share(len(gas), rng),
                       np.maximum(0.0, gas - gas_retrofit),
                       np.maximum(0.0, gas - gas_turndown)], axis=1)
    fuel = np.array([rows[ri].get("MAIN_HEAT_FUEL", "?") for ri in row_pick])
    observed = np.array([rows[ri]["_gas"] for ri in row_pick])
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


def _stratum_labels(pop, n):
    """The cross of every stratifying attribute the population carries, as one label per household.

    STRATIFY ON THE CROSS RATHER THAN ON EACH ATTRIBUTE IN TURN. Requiring each fuel to pass and
    each payment method to pass is a weaker demand than requiring each COMBINATION to pass, and the
    combination is what a supplier actually serves: an electrically-heated prepayment household is
    not the average of "electric" and "prepayment".
    """
    import numpy as np

    parts = []
    for key in ("fuel", "payment_method"):
        value = pop.get(key)
        if value is not None:
            parts.append(np.asarray(value).astype(str))
    if not parts:
        return None
    out = parts[0]
    for extra in parts[1:]:
        out = np.char.add(np.char.add(out, "|"), extra)
    return out


def smallest_n(pop, axes, ns=NS, replicates: int = REPLICATES, seed: int = 0,
               tolerance: float = DISTRIBUTION_TOLERANCE, reference=None):
    """The smallest n whose draw reproduces the population to within `tolerance` on every axis AND
    on every joint direction, on every replicate. Returns (n, per-n verdicts)."""
    import numpy as np

    values = np.asarray(pop["values"])
    keep = [AXES.index(a) for a in axes]
    reference = reference if reference is not None else _Reference(values[:, keep], axes)
    # FUEL IS A STRATUM, NOT A COORDINATE. Standardising a three-level category and mixing it into
    # a distance would make "how far is gas from electric" a number, which it is not. Stratified,
    # the minority fuel must be reproduced in its own right rather than swamped by the 81%.
    # THE STRATUM KEY IS THE CROSS, not one attribute. Two fuels x two payment methods is four
    # groups and each must be reproduced in its own right -- which is exactly the claim under test:
    # a stratum multiplies the count even when it moves no measured axis, because coverage is owed
    # per group rather than per population.
    labels = _stratum_labels(pop, len(values))
    strata = None
    if labels is not None and len(set(labels.tolist())) > 1:
        strata = {f: (_Reference(values[labels == f][:, keep], axes), np.flatnonzero(labels == f))
                  for f in sorted(set(labels.tolist()))}
    fuel = labels
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
            ok = all(v["accepts"] for v in result.values())
            worst = max(worst, max(v["d"] for v in result.values()))
            if strata:
                for f, (ref_f, members) in strata.items():
                    # Vectorised: the list-comprehension form was O(n) PYTHON per stratum per
                    # replicate, and the ladder runs it tens of thousands of times at sizes up to
                    # 30,000. Same selection, one numpy pass.
                    inside = pick[fuel[pick] == f]
                    if len(inside) < 2:
                        ok = False          # a stratum with no draw is not a reproduced stratum
                        worst = max(worst, 1.0)
                        continue
                    r_f = accepts_against(values[inside][:, keep], ref_f, tolerance=tolerance)
                    ok = ok and all(v["accepts"] for v in r_f.values())
                    worst = max(worst, max(v["d"] for v in r_f.values()))
            passed += ok
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


#: Directions the WEIGHTS are fitted on. Disjoint from the 64 the test scores, and that separation
#: is the only thing standing between "the weights carry the representativeness" and "the weights
#: were fitted to the answer". A design that passes only on the directions it was fitted to has
#: learned the test, not the population.
FIT_SLICES = 32

#: Cut points per axis and per direction used to fit. The weights match the population's CDF at
#: these quantiles; the test then scores the whole CDF against every population point.
FIT_GRID = 60


def choose_for_difference(values, k: int, seed: int = 0, fuel=None):
    """Cases chosen because they BEHAVE differently, with the tails deliberately in.

    THE CHOOSING, and the first version of it was wrong in an instructive way. It used greedy
    maximin -- farthest-from-everything-drawn -- which is right for spanning a space and wrong for
    standing in for a population: every case lands in the sparse outskirts, the dense bulk where
    most households live is represented by a handful of atoms, and no weighting can rebuild a
    bulk-heavy distribution from a set of extremes. Measured, it was WORSE than a random draw.

    So the cases are cluster MEDOIDS -- real households, one per distinct region of behaviour, so
    two near-identical households can never both be chosen -- plus the extreme of every axis, plus
    the extremes WITHIN each fuel, because the minority fuel's tail is not the population's tail and
    the canon says those are different customers.
    """
    import numpy as np
    from sklearn.cluster import KMeans

    values = np.asarray(values, dtype=float)
    mean = values.mean(axis=0)
    sd = values.std(axis=0)
    sd = np.where(sd == 0, 1.0, sd)
    z = (values - mean) / sd

    km = KMeans(n_clusters=k, n_init=1, random_state=seed).fit(z)
    chosen = []
    for c in range(k):
        members = np.flatnonzero(km.labels_ == c)
        if len(members):
            d = np.sum((z[members] - km.cluster_centers_[c]) ** 2, axis=1)
            chosen.append(int(members[int(np.argmin(d))]))
    for j in range(values.shape[1]):
        chosen += [int(np.argmax(values[:, j])), int(np.argmin(values[:, j]))]
    if fuel is not None:
        fuel = np.asarray(fuel)
        for f in sorted(set(fuel.tolist())):
            idx = np.flatnonzero(fuel == f)
            for j in range(values.shape[1]):
                chosen += [int(idx[np.argmax(values[idx, j])]), int(idx[np.argmin(values[idx, j])])]
    return np.array(sorted(set(chosen)))


def fit_weights(values, chosen, reference, seed: int = 999):
    """Solve for the mass each chosen case stands for, so the WEIGHTED sample reproduces the
    population.

    Non-negative least squares against the population's own CDF at `FIT_GRID` quantiles on every
    axis and every FIT direction, with a heavily-weighted sum-to-one row. Non-negativity is not a
    convenience: a negative weight is a household count below zero, and a case that has to be
    subtracted to make the distribution work is a case that should not have been chosen.
    """
    import numpy as np
    from scipy.optimize import nnls

    values = np.asarray(values, dtype=float)
    z = (values - reference.mean) / reference.sd
    rng = np.random.default_rng(seed)
    directions = rng.normal(size=(FIT_SLICES, z.shape[1]))
    directions /= np.linalg.norm(directions, axis=1, keepdims=True)

    rows, targets = [], []
    for j in range(values.shape[1]):
        for cut in np.quantile(values[:, j], np.linspace(0.02, 0.98, FIT_GRID)):
            rows.append((values[chosen, j] <= cut).astype(float))
            targets.append(float((values[:, j] <= cut).mean()))
    for u in directions:
        projected = z @ u
        chosen_projected = z[chosen] @ u
        for cut in np.quantile(projected, np.linspace(0.02, 0.98, FIT_GRID)):
            rows.append((chosen_projected <= cut).astype(float))
            targets.append(float((projected <= cut).mean()))

    A = np.vstack([np.array(rows), np.ones((1, len(chosen))) * 100.0])
    b = np.append(np.array(targets), 100.0)
    weights, _ = nnls(A, b)
    return weights if weights.sum() > 0 else np.ones(len(chosen))


def weighted_ks(sample_values, sample_weights, sorted_reference) -> float:
    """KS distance between a WEIGHTED empirical distribution and an equal-mass reference.

    The sample's steps are its weights rather than 1/n, which is the whole of what "the mass it
    stands for" means when it reaches the test.
    """
    import numpy as np

    x = np.asarray(sample_values, dtype=float)
    w = np.asarray(sample_weights, dtype=float)
    order = np.argsort(x)
    x, w = x[order], w[order]
    total = w.sum()
    if total <= 0:
        return 1.0
    cumulative = np.cumsum(w) / total

    grid = np.concatenate([x, sorted_reference])
    # Step function value at each grid point: the weight at or below it.
    idx = np.searchsorted(x, grid, "right") - 1
    sample_cdf = np.where(idx >= 0, cumulative[np.clip(idx, 0, len(x) - 1)], 0.0)
    reference_cdf = np.searchsorted(sorted_reference, grid, "right") / len(sorted_reference)
    return float(np.max(np.abs(sample_cdf - reference_cdf)))


def accepts_weighted(sample, weights, reference, tolerance: float = DISTRIBUTION_TOLERANCE) -> dict:
    """`accepts_against`, for a chosen-and-weighted sample rather than a random one."""
    import numpy as np

    sample = np.asarray(sample, dtype=float)
    out = {}
    for j, axis in enumerate(reference.axes):
        d = weighted_ks(sample[:, j], weights, reference.marginals[j])
        out[axis] = {"d": round(d, 5), "tolerance": tolerance, "accepts": bool(d <= tolerance)}
    z = (sample - reference.mean) / reference.sd
    worst = max(weighted_ks(z @ u, weights, proj)
                for u, proj in zip(reference.directions, reference.projections))
    out["JOINT"] = {"d": round(worst, 5), "tolerance": tolerance,
                    "accepts": bool(worst <= tolerance), "slices": JOINT_SLICES}
    return out


def _positions(members, chosen):
    """Indices of `chosen` WITHIN `members` -- `fit_weights` indexes the array it is given.

    A stratum's fit runs over that stratum's own rows, so the chosen cases must be addressed by
    their position inside it rather than by their position in the population.
    """
    import numpy as np

    lookup = {int(m): i for i, m in enumerate(members)}
    return np.array([lookup[int(c)] for c in chosen])


def smallest_n_chosen(pop, axes, ns=CHOSEN_NS, seed: int = 0,
                      tolerance: float = DISTRIBUTION_TOLERANCE, reference=None):
    """The smallest DELIBERATELY-CHOSEN, WEIGHTED sample that reproduces the population.

    THE DESIGN THE CANON ACTUALLY SPECIFIES, and the one this module was not running. Its acceptance
    drew `rng.choice(...)` -- a uniform random sample -- while its own docstring quoted "each drawn
    case carries the population mass it stands for". No weight entered the test at all. The director
    wrote the tell into the canon: *if N comes out at the scale a random sample would need, the
    weighting is doing no work.* It came out at 8,500, and it was doing none because there was none.

    ONE DRAW PER SIZE, not five: the choosing is deterministic given its seed, so there is no luck to
    average over. That is a property of designing rather than sampling.
    """
    import numpy as np

    values = np.asarray(pop["values"])
    keep = [AXES.index(a) for a in axes]
    subset = values[:, keep]
    reference = reference if reference is not None else _Reference(subset, axes)
    verdicts, answer = {}, None
    labels = _stratum_labels(pop, len(values))
    # PER-STRATUM REFERENCES BUILT ONCE, not per ladder step. Each one projects its stratum onto 64
    # directions, and the first version rebuilt all four inside the loop -- the same defect this
    # module already fixed for the population reference, committed again one level down. It ran for
    # twenty-five minutes without finishing.
    stratum_refs = {}
    if labels is not None and len(set(labels.tolist())) > 1:
        for f in sorted(set(labels.tolist())):
            members = np.flatnonzero(labels == f)
            stratum_refs[f] = (_Reference(subset[members], axes), members)
    for k in ns:
        if k >= len(subset):
            break
        chosen = choose_for_difference(subset, k, seed=seed, fuel=labels)
        if stratum_refs:
            # WEIGHTS FITTED WITHIN EACH STRATUM, and the first version's were not. It fitted ONE
            # global weight vector to reproduce the population, then scored each stratum's
            # sub-sample against that stratum's own distribution -- asking a sub-sample to match a
            # distribution its weights were never fitted to, which it can only do by luck. It
            # returned "no size accepts" at every tolerance, and that would have read as a
            # gigantic sample requirement rather than as a broken criterion.
            #
            # Fitting per stratum is also the CORRECT reading of "the mass it stands for": strata
            # partition the population, so a set of within-stratum weights aggregates to the
            # population weights exactly.
            weights = np.zeros(len(chosen), dtype=float)
            for f, (ref_f, members) in stratum_refs.items():
                where = labels[chosen] == f
                inside = chosen[where]
                if len(inside) < 2:
                    continue
                share = len(members) / len(subset)
                w_f = fit_weights(subset[members], _positions(members, inside), ref_f)
                total = w_f.sum() or 1.0
                weights[where] = w_f / total * share
        else:
            weights = fit_weights(subset, chosen, reference)
        result = accepts_weighted(subset[chosen], weights, reference, tolerance=tolerance)
        worst = max(v["d"] for v in result.values())
        ok = all(v["accepts"] for v in result.values())
        # EVERY STRATUM IN ITS OWN RIGHT, for the chosen design too. Without this the chosen path
        # would be scored against the population only, while the random comparator is scored per
        # stratum -- and the two numbers would not be answering the same question.
        if stratum_refs:
            for f, (ref_f, _members) in stratum_refs.items():
                inside = chosen[labels[chosen] == f]
                if len(inside) < 2:
                    ok = False
                    worst = max(worst, 1.0)
                    continue
                w_f = weights[labels[chosen] == f]
                r_f = accepts_weighted(subset[inside], w_f, ref_f, tolerance=tolerance)
                ok = ok and all(v["accepts"] for v in r_f.values())
                worst = max(worst, max(v["d"] for v in r_f.values()))
        verdicts[len(chosen)] = {"worst_ks_distance": round(worst, 4), "accepts": ok,
                                 "carrying_weight": int((weights > 1e-9).sum()),
                                 "tolerance": tolerance}
        if ok:
            answer = int(len(chosen))
            break
    return answer, verdicts


def measurement(points: int = POPULATION_POINTS, seed: int = 0, generated: bool = True) -> dict:
    """Both numbers the canon asks for, at several accuracies, and the second is the real one."""
    # GENERATED BY DEFAULT. `population()` selects NEED rows and is kept only as the comparator
    # that shows what selection could not reach.
    pop = (generated_population(points=points, seed=seed) if generated
           else population(points=points, seed=seed))
    import numpy as np

    price_list = {}
    allv = np.asarray(pop["values"])
    ref_d = _Reference(allv[:, [AXES.index(a) for a in DISTRIBUTION_AXES]], DISTRIBUTION_AXES)
    ref_r = _Reference(allv[:, [AXES.index(a) for a in AXES]], AXES)
    for tol in TOLERANCES:
        # THE ANSWER is the deliberately-chosen weighted design. The random figure is kept beside
        # it as the TELL the canon asks for: if the two are the same scale, the weighting is doing
        # no work and the design has reverted to representativeness.
        chosen_n, curve_c = smallest_n_chosen(pop, AXES, tolerance=tol, seed=seed, reference=ref_r)
        nr, curve_r = smallest_n(pop, AXES, tolerance=tol, seed=seed, reference=ref_r)
        price_list[f"{tol:.2f}"] = {
            "n_chosen_and_weighted": chosen_n,
            "n_random_sample_comparator": nr,
            "weighting_factor": (round(nr / chosen_n, 1) if (chosen_n and nr) else None),
            "dominated_by": binding_axis(pop, AXES, nr or max(NS), seed=seed) if nr else None,
        }
    n_distribution, curve_d = smallest_n_chosen(pop, DISTRIBUTION_AXES, seed=seed, reference=ref_d)
    n_response, curve_r = smallest_n_chosen(pop, AXES, seed=seed, reference=ref_r)
    values = allv
    return {
        "price_list_by_tolerance": price_list,
        "population_points": int(len(values)),
        "generated": bool(pop.get("generated")),
        "distinct_cells_reached": pop.get("distinct_cells"),
        "scotland_share_of_points": (round(float((np.asarray(pop["cell_nation"]) == "S").mean()), 4)
                                     if pop.get("cell_nation") is not None else None),
        "need_dwellings": pop["n_need_rows"],
        "axes_measured": list(AXES),
        "this_is_a_floor_not_an_answer": True,
        "uncounted_axes": list(UNCOUNTED_AXES),
        "alpha": ALPHA,
        "tolerance": DISTRIBUTION_TOLERANCE,
        "replicates": REPLICATES,
        "n_to_reproduce_the_distribution": n_distribution,
        "n_to_also_span_intervention_response": n_response,
        "design": ("cases chosen for difference, weights fitted to the mass each stands for; the "
                   "random-sample figure is the comparator, not the answer"),
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
    ap.add_argument("--selected", action="store_true",
                    help="use the OLD NEED-row selection, for comparison")
    args = ap.parse_args(argv)
    if args.measure:
        print(json.dumps(measurement(points=args.points, seed=args.seed,
                                     generated=not args.selected), indent=2, default=str))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
