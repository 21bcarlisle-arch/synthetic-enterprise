#!/usr/bin/env python3
"""FABRIC coupled triad — measure the belief-vs-truth gap and write it to the ledger.

Atom: `H_GAP_fabric_belief_truth_gap`. Siblings: `tools/couple_cohort.py`,
`tools/couple_w2_10_c12.py` (same template, same standing).

PURPOSE, GUARANTEES, WHY — stated first (OPS1) or the mechanism is deleted
=========================================================================

**Purpose.** Be the CALLER that `background.fabric_gap_ledger.write_fabric_gap_entries`
never had. The measurement code landed with the H_GAP build; nothing invoked it, so
the fabric gap existed as a function and never as a NUMBER anyone could read.

**Guarantee.** Running this with `--write-ledger` puts two rows into
`docs/observability/coupled_gap_ledger.json` — `W1_11_fabric_physics_core -> C14`
(what the EPC register believes) and `W1_12_premise_trace_generator -> C14` (what
the company's own inference believes) — which the Proof door then renders from the
map, and which `background.coupled_triad.world_l3_blocked` reads as the L3 gate.

**Why it is needed, and why now.** THE ORPHAN-TRANSITION RULE (R11): a hold, flag or
mechanism whose release triggers nothing is a defect. `write_fabric_gap_entries` had
no production caller — grep-verified 2026-08-03, the only references were its own
definition and its unit test. This is the SECOND recorded instance of exactly that
shape in this codebase (`generate_evidence_data.generate()` was never wired into
`process_run_complete.py` despite its docstring saying it was safe to call there), so
it is a class, not an accident: a measurement function is "done" to a reviewer the
moment it is tested, and nothing about a green test says anyone runs it.

THE WALL, AND WHY THIS FILE MAY CROSS IT
----------------------------------------
This is HARNESS code in `tools/`, outside the epistemic wall, with the same standing
as `background/gap_metric.py` and `tools/couple_cohort.py`. It is the only layer
permitted to hold the SIM's hidden fabric truth (`PremiseTrace.fabric`) and the
company's belief (`ThermalBelief`) side by side. It measures both and HELPS NEITHER:
nothing it computes is fed back to either side, and the company is never told its
own score.

WHAT THE COMPANY IS ALLOWED TO SEE, and it is checked rather than asserted
-------------------------------------------------------------------------
The company side receives ONLY cumulative register reads at its meter's real
cadence, published daily mean temperatures, and an EPC certificate in the register's
own string vocabulary. It never receives a fabric parameter. `--audit-wall` prints
exactly what crossed, and `tests/tools/test_couple_fabric.py` asserts the inference
call is reachable from meter reads alone.

R12 / R13
---------
Every number printed here is a DIAGNOSTIC, never a target. A gap that gets worse is a
REPORTABLE OUTCOME, not a bug to tune away — the company is allowed to be wrong, and
a fabric belief that beats its own register is not guaranteed. Panel composition is
BASELINE fidelity, fixed blind to company P&L.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from background import fabric_gap_ledger as fgl  # noqa: E402
from company.pricing import fabric_intervention as fi  # noqa: E402
from company.pricing import thermal_inference as ti  # noqa: E402
from simulation import fabric_physics as fp  # noqa: E402
from simulation import premise_population as ppop  # noqa: E402
from simulation import premise_trace as pt  # noqa: E402
from simulation.household import (  # noqa: E402
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    InsulationLevel,
    PropertyType,
)

# The measurement window. A full heating season on the REAL Open-Meteo archive
# (Historical Ground Truth) — C14 REFUSES a premise that has not been observed in
# the cold (MIN_PEAK_HDD_K), which is the correct behaviour and means a summer
# window would produce refusals rather than a gap.
WINDOW_START = dt.date(2022, 1, 1)
WINDOW_END = dt.date(2022, 4, 30)

# The weather SITE this panel is driven by, named ONCE so the archive it reads and
# the solar geometry it reconstructs against cannot drift apart. Before 2026-08-03
# they had: `load_weather()` read C1 (London, 51.51 N) while `generate_premise_trace`
# was called without `latitude_deg` and silently fell back to `DEFAULT_LATITUDE_DEG`
# (53.0 N, the UK population-weighted mean). Every gap number this tool has ever
# written to the ledger was therefore computed with sunrise, solar noon and clear-sky
# irradiance for a site ~1.5 degrees north of the weather driving it — the exact
# averaging fault the module docstring claimed had been closed.
SITE = "C1"
AS_OF = dt.date(2022, 5, 1)

# The default unit rate. DIAGNOSTIC input, not a company figure, and it is printed
# alongside every £ result rather than buried (R14 — a figure without its basis is a
# defect). It is NOT a scale factor: forgone value is AFFINE in the rate, not linear,
# because the capex of the measure a wrong belief bought does not move with the price
# — and the rate also decides WHICH measure wins, so a different rate is a different
# decision, not the same one rescaled.
DEFAULT_UNIT_RATE_P_PER_KWH = 7.4

# The degree-day base used to attribute part of a bill to FABRIC loss in the
# intervention decision. 15.5 C is the long-standing UK published convention (the
# base of the Met Office / BizEE UK degree-day series), NOT the per-premise balance
# point C14 searches for.
#
# THAT DISTINCTION IS DELIBERATE AND IT IS A WALL ISSUE. The searched balance point
# is a COMPANY artefact that exists only where a meter fit succeeded; feeding it to
# the decision would (a) leave EPC-only premises with no base at all and (b) put a
# company-derived quantity inside the TRUTH arm, where the whole point is that the
# only thing differing between the arms is the fabric belief. One published
# convention, applied identically to both arms and every premise.
DEGREE_DAY_BASE_C = 15.5

# The EPC register's OWN vocabulary, as `thermal_inference.epc_prior` recognises
# it. These strings are the company's, not the SIM's — the whole point of the
# certificate seam is that the company reads register text, never a SIM enum.
# `epc_prior` RAISES on an unrecognised band rather than defaulting to a stock
# prior, which is the right call and caught a wrong vocabulary here on first run:
# a silent fallback would have measured the stock-prior gap while claiming to
# measure the certificate's.
_EPC_PROPERTY_TYPE = {
    PropertyType.FLAT: "flat",
    PropertyType.TERRACED: "terraced",
    PropertyType.SEMI_DETACHED: "semi-detached",
    PropertyType.DETACHED: "detached",
}

_ERA_BAND = {
    BuildEra.PRE_1919: "pre-1919",
    BuildEra.ERA_1919_1944: "1919-1944",
    BuildEra.ERA_1945_1964: "1945-1964",
    BuildEra.ERA_1965_1980: "1965-1980",
    BuildEra.ERA_1981_2000: "1981-2000",
    BuildEra.POST_2000: "post-2000",
}

# The PANEL — spans the stock deliberately, so a small gap cannot be an artefact
# of asking eight near-identical houses whether they differ. Property type x build
# era x insulation x occupancy, crossed with the HEATING REGIMES the band table
# carries (whose flat assumed ASHP SCOP is a KNOWN bias source C14 copes with by
# widening, never by correcting).
#
# `every_n_days` is the METER CADENCE, and it is deliberately NOT uniform: a real
# supplier's book is a mix of smart (daily) and traditional (monthly/quarterly)
# meters, and C14's measured error runs 0.2% -> 18% across that range. A panel read
# entirely daily would flatter the company by giving every premise smart-meter
# evidence it does not have.
#
# IT IS A SPAN, NOT A SAMPLE — restated here because this panel was widened
# (2026-08-09, atom `H35_the_panel_never_exercises_two_of_its_own_bands`) and a
# silent widening is how a span turns into an implied sample. 15 homes: 9 gas, 3
# heat pump, 3 resistive electric. Real GB stock is ~85% mains gas, ~1% heat pump
# and ~8% electric, so the electric regimes are deliberately over-weighted here by
# roughly an order of magnitude. THAT IS NOT A REPRESENTATIVENESS CLAIM AND MUST
# NEVER BE READ AS ONE: representativeness lives in `build_drawn_population`, which
# draws property type, era and EPC band from a joint raked onto published EHS
# marginals and heating system from its own published shares. This panel exists so
# that every band the ledger carries is EXERCISED by the run that judges it —
# `fabric_gap_ledger` conditions the L1.1 texture floor on heating regime (gas /
# heat pump / resistive), and until 2026-08-09 the resistive band judged ZERO homes
# and the heat-pump band judged ONE, so one band's null was unmeasurable and the
# other's had no estimable spread. A carried-and-never-exercised band reads exactly
# like a clean one.
#
# WHY THE RESISTIVE HOMES ARE `ELECTRIC_DIRECT` AND NOT `ELECTRIC_STORAGE`, which
# is a deliberate deviation from the atom's own wording: the world layer does not
# model a storage heater. `simulation/fabric_physics.py::_CONTROL_MODE` gives
# `ELECTRIC_STORAGE` the same deadband thermostat as a gas combi, and
# `simulation/premise_trace.py` contains no charge window, no thermal store and no
# Economy-7 calendar (`WORKER_FINDING_THE_MODELS_STORAGE_HEATER_IS_NOT_ONE`,
# owner atom W1_12). A home labelled `electric_storage` here would be a panel
# heater wearing a storage heater's register value, and the texture null would then
# be reported as measured on a load set half of which is a mislabel. A panel heater
# is exactly what `ELECTRIC_DIRECT` already is — so the reading is taken on the
# sub-regime the physics genuinely represents, and the storage sub-regime stays
# openly unexercised until the storage-heater fidelity work lands, rather than
# being quietly claimed.
#
# H36 (2026-08-10) removed the regime-conditioned texture FLOORS these homes were
# put here to exercise — L1.1 is now read net of space heat against one floor — but
# not the reason for the widening: a panel with no electrically heated home cannot
# measure what the netting does, and the storage/panel distinction above is a
# statement about the WORLD that survives any change to the control.
PANEL = (
    # id, property type, era, insulation, bedrooms, people, heating, meter cadence
    ("F1", PropertyType.FLAT, BuildEra.POST_2000, InsulationLevel.FULL, 1, 1,
     HeatingSystem.GAS_BOILER_COMBI, 1),
    ("T2", PropertyType.TERRACED, BuildEra.PRE_1919, InsulationLevel.POOR, 2, 2,
     HeatingSystem.GAS_BOILER_COMBI, 1),
    ("S3", PropertyType.SEMI_DETACHED, BuildEra.ERA_1965_1980, InsulationLevel.PARTIAL, 3, 3,
     HeatingSystem.GAS_BOILER_COMBI, 7),
    ("D4", PropertyType.DETACHED, BuildEra.ERA_1919_1944, InsulationLevel.PARTIAL, 4, 4,
     HeatingSystem.GAS_BOILER_COMBI, 7),
    ("T5", PropertyType.TERRACED, BuildEra.ERA_1981_2000, InsulationLevel.FULL, 2, 2,
     HeatingSystem.GAS_BOILER_COMBI, 30),
    ("S6", PropertyType.SEMI_DETACHED, BuildEra.PRE_1919, InsulationLevel.PARTIAL, 3, 5,
     HeatingSystem.GAS_BOILER_COMBI, 30),
    ("D7", PropertyType.DETACHED, BuildEra.POST_2000, InsulationLevel.FULL, 5, 3,
     HeatingSystem.GAS_BOILER_COMBI, 1),
    ("F8", PropertyType.FLAT, BuildEra.ERA_1965_1980, InsulationLevel.POOR, 1, 2,
     HeatingSystem.GAS_BOILER_COMBI, 7),
    ("S9", PropertyType.SEMI_DETACHED, BuildEra.ERA_1945_1964, InsulationLevel.POOR, 3, 3,
     HeatingSystem.GAS_BOILER_COMBI, 30),
    ("H10", PropertyType.SEMI_DETACHED, BuildEra.ERA_1981_2000, InsulationLevel.FULL, 3, 3,
     HeatingSystem.HEAT_PUMP_AIR, 1),
    # The retrofit ASHP archetype — an older detached home, partially insulated,
    # which is where the flat-SCOP assumption hurts most and therefore the home
    # the heat-pump band most needs to be judged on.
    ("H11", PropertyType.DETACHED, BuildEra.ERA_1965_1980, InsulationLevel.PARTIAL, 4, 3,
     HeatingSystem.HEAT_PUMP_AIR, 7),
    # New-build ASHP on a traditional meter: the regime and the cadence are varied
    # independently, so "heat pump" and "read daily" cannot be confounded.
    ("H12", PropertyType.TERRACED, BuildEra.POST_2000, InsulationLevel.FULL, 2, 2,
     HeatingSystem.HEAT_PUMP_AIR, 30),
    # Resistive electric (panel heaters). The canonical electrically-heated
    # dwelling in the GB stock is a converted flat with no gas connection.
    ("E13", PropertyType.FLAT, BuildEra.PRE_1919, InsulationLevel.POOR, 1, 1,
     HeatingSystem.ELECTRIC_DIRECT, 30),
    ("E14", PropertyType.FLAT, BuildEra.ERA_1965_1980, InsulationLevel.PARTIAL, 2, 2,
     HeatingSystem.ELECTRIC_DIRECT, 7),
    ("E15", PropertyType.TERRACED, BuildEra.ERA_1945_1964, InsulationLevel.POOR, 2, 3,
     HeatingSystem.ELECTRIC_DIRECT, 1),
)

# EPC lodgement dates. STALENESS IS PART OF THE MEASUREMENT, not noise to remove:
# C14 inflates the prior's uncertainty per year since lodgement, so a panel of
# uniformly-fresh certificates would understate how wrong the register really is on
# a real book. One premise has NO certificate at all — the company falls back to a
# labelled stock-class prior, which `is_actionable` refuses however tight its band.
_LODGED = {
    "F1": dt.date(2021, 3, 1),
    "T2": dt.date(2012, 7, 1),
    "S3": dt.date(2016, 11, 1),
    "D4": dt.date(2009, 5, 1),
    "T5": dt.date(2020, 1, 1),
    "S6": None,                      # no certificate on the register
    "D7": dt.date(2019, 9, 1),
    "F8": dt.date(2014, 2, 1),
    "S9": dt.date(2011, 6, 1),
    "H10": dt.date(2022, 1, 1),
    "H11": dt.date(2018, 4, 1),
    "H12": dt.date(2021, 6, 1),
    "E13": dt.date(2013, 9, 1),
    "E14": dt.date(2010, 8, 1),
    "E15": dt.date(2022, 2, 1),
}

# The MAIN FUEL string as the EPC register itself records it, in the register's own
# vocabulary ("electricity (not community)" is a real MAIN_FUEL value, not a
# paraphrase). ONE map, read by both the certificate the company is handed and the
# fuel it is told to assume when there is no certificate, because two copies of
# this is how a home ends up with a resistive meter and a boiler's assumed
# efficiency. Nothing here is a SIM internal: a supplier knows which meters it
# supplies and what the register says is in the house.
_REGISTER_FUEL = {
    HeatingSystem.HEAT_PUMP_AIR: "air source heat pump",
    HeatingSystem.HEAT_PUMP_GROUND: "ground source heat pump",
    HeatingSystem.ELECTRIC_DIRECT: "electricity (not community)",
    HeatingSystem.ELECTRIC_STORAGE: "electricity (not community)",
    HeatingSystem.DISTRICT_HEAT: "community scheme",
}


def _register_fuel(household) -> str:
    return _REGISTER_FUEL.get(household.heating_system, "mains gas")


def _household(premise_id, property_type, build_era, insulation, bedrooms, people, heating):
    return Household(
        customer_id=premise_id,
        property_type=property_type,
        build_era=build_era,
        epc_rating="D",
        bedrooms=bedrooms,
        heating_system=heating,
        # NA where there is no boiler. Inert in the physics (`_fuel_for` reads it
        # only on the gas branch), and set anyway so the household RECORD does not
        # assert a mid-life boiler in a home heated by panel heaters — a record a
        # later consumer would be entitled to believe. The gas homes keep MID: a
        # blanket era-derived boiler age would move every gas trace this panel has
        # ever published, which is a different change from this one.
        boiler_age=(
            BoilerAge.MID
            if heating in (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM)
            else BoilerAge.NA
        ),
        has_solar=False,
        solar_kwp=0.0,
        solar_install_year=None,
        has_battery=False,
        battery_kwh=0.0,
        has_ev=False,
        ev_charger_kw=0.0,
        has_smart_meter=True,
        smart_meter_install_year=2020,
        insulation=insulation,
        has_driveway=True,
        roof_aspect="south",
    )


def _reads_from_trace(trace, commodity, *, every_n_days, start):
    """The CUMULATIVE REGISTER READS a supplier would actually hold.

    This is the ONLY consumption information that crosses to the company side —
    a running total at the meter's own cadence, never a half-hourly trace and
    never a fabric parameter.
    """
    cumulative = 0.0
    reads = [ti.MeterRead(start - dt.timedelta(days=1), 0.0)]
    for index, (day, daily_kwh) in enumerate(zip(trace.days, trace.daily(commodity))):
        cumulative += daily_kwh
        if (index + 1) % every_n_days == 0:
            reads.append(ti.MeterRead(day.date, cumulative))
    return reads


def _certificate_for(trace, household, lodged):
    """The EPC record in the REGISTER'S OWN VOCABULARY (plain strings), never the
    SIM's enums. `None` where the register has no certificate for the premise."""
    if lodged is None:
        return None
    return ti.EpcCertificate(
        lodged_date=lodged,
        total_floor_area_m2=trace.fabric.floor_area_m2,
        property_type=_EPC_PROPERTY_TYPE[household.property_type],
        build_era_band=_ERA_BAND[household.build_era],
        insulation=household.insulation.value,
        main_heating_fuel=_register_fuel(household),
    )


def load_weather():
    """The REAL Open-Meteo reanalysis archive (Historical Ground Truth).

    Deliberately NOT wrapped in a try/except: if the archive is missing this must
    raise, never fall back to a synthetic series. A gap measured against invented
    weather would be a number with no meaning, reported as though it had one.
    """
    return pt.load_trace_weather(SITE, start=WINDOW_START, end=WINDOW_END)


def _trace_for(premise_id, household, weather, *, seed):
    return pt.generate_premise_trace(
        premise_id=premise_id,
        household=household,
        weather=weather,
        seed=seed,
        latitude_deg=fp.latitude_for_weather_site(SITE),
    )


def build_panel(weather, *, seed: int = 17, limit: int | None = None):
    """Generate the WORLD side once: truth traces off the real weather archive."""
    specs = PANEL[:limit] if limit else PANEL
    out = []
    for premise_id, ptype, era, insulation, bedrooms, people, heating, cadence in specs:
        household = _household(premise_id, ptype, era, insulation, bedrooms, people, heating)
        trace = _trace_for(premise_id, household, weather, seed=seed)
        # The meter the heat actually lands on, taken from the trace's own
        # statement rather than re-derived here: a list of "which systems are
        # electric" maintained in this file is one heating system away from
        # reading a resistive home's gas register and finding nothing on it.
        commodity = trace.heating_commodity
        out.append((premise_id, household, trace, commodity, cadence, _LODGED.get(premise_id)))
    return out


def build_drawn_population(weather, *, n: int, seed: int = 17, population_seed: int = 17):
    """The SAME world side, on a population NOBODY CHOSE.

    `simulation.premise_population` draws property type, build era and EPC band
    from a joint raked onto published EHS marginals, then heating system, meter
    cadence and EPC lodgement from their own published shares. The panel above
    was composed to span the stock, which is the honest thing to do with ten
    homes and the exact thing that stops ten homes being a finding about a book:
    a result on a chosen population cannot be separated from the chooser's taste.

    Whatever this returns is BASELINE fidelity, fixed blind to company P&L (R13).
    Nothing in `simulation.premise_population` may be adjusted because the gap
    measured on it came out unflattering — that would be goal-seeking (R12) with
    extra steps.
    """
    population = ppop.draw_premise_population(n, base_seed=population_seed, as_of=AS_OF)
    out = []
    for premise in population:
        trace = _trace_for(premise.premise_id, premise.household, weather, seed=seed)
        out.append((
            premise.premise_id,
            premise.household,
            trace,
            premise.commodity,
            premise.meter_cadence_days,
            premise.epc_lodged,
        ))
    return out


def observe(panel, weather, *, unit_rate_p_per_kwh=DEFAULT_UNIT_RATE_P_PER_KWH):
    """Hold the two sides together — the ONE place permitted to do so.

    Returns (observations, per-premise detail). The company's belief is computed
    from observables ONLY; the truth is read from the trace's fabric and never
    passed into the inference call.
    """
    published = [
        ti.PublishedWeatherDay(day.date, day.weather.temperature_mean_c)
        for day in weather
    ]
    # ANNUALISED the SAME WAY the heat total is, and that is not a detail. The
    # measurement window is a heating season (Jan-Apr), and `PremiseTrace.annual_kwh`
    # annualises it as `window mean x 365.25`. Annualising the degree days by the
    # identical rule keeps the two commensurate, so the FABRIC SHARE the decision
    # actually turns on is unaffected by the annualisation — a window-mean heat
    # total divided by a true-annual degree-day count would silently halve every
    # premise's apparent fabric share and steer the whole book away from insulation.
    hdd_by_day = ti.heating_degree_days(published, DEGREE_DAY_BASE_C)
    annual_degree_days = sum(hdd_by_day.values()) / len(hdd_by_day) * 365.25
    observations, detail = [], []
    for premise_id, household, trace, commodity, cadence, lodged in panel:
        certificate = _certificate_for(trace, household, lodged)
        belief = ti.infer_thermal_parameters(
            premise_id=premise_id,
            reads=_reads_from_trace(
                trace, commodity, every_n_days=cadence, start=WINDOW_START
            ),
            weather=published,
            certificate=certificate,
            as_of=AS_OF,
            property_type_hint=_EPC_PROPERTY_TYPE[household.property_type],
            main_heating_fuel=_register_fuel(household),
        )
        # TRUTH — read from the SIM side, never shown to the company.
        actual = trace.fabric.heat_loss_coefficient_kw_per_k
        observations.append(
            fgl.FabricObservation(
                premise_id=premise_id,
                actual_hlc_kw_per_k=actual,
                epc_hlc_kw_per_k=belief.prior.hlc_kw_per_k,
                inferred_hlc_kw_per_k=belief.hlc_kw_per_k,
                floor_area_m2=trace.fabric.floor_area_m2,
                annual_heat_kwh=trace.annual_kwh(commodity),
                annual_degree_days_k_day=annual_degree_days,
                # The register prior taken ON ITS OWN — its own width and its own
                # basis, not the posterior's. A company that had never looked at a
                # meter would hold exactly this, and that is the arm being scored.
                epc_relative_sd=belief.prior.relative_sd,
                epc_basis=belief.prior.basis,
                inferred_relative_sd=belief.relative_sd,
                inferred_basis=belief.basis,
            )
        )
        detail.append(
            {
                "premise_id": premise_id,
                "meter_cadence_days": cadence,
                "certificate": "none" if certificate is None else str(lodged),
                "actual": actual,
                "epc": belief.prior.hlc_kw_per_k,
                "inferred": belief.hlc_kw_per_k,
                "relative_sd": belief.relative_sd,
                "basis": belief.basis.value,
                "is_actionable": belief.is_actionable,
                "recommendation": fi.recommend_measure(
                    belief,
                    annual_heat_kwh=trace.annual_kwh(commodity),
                    annual_degree_days_k_day=annual_degree_days,
                    unit_rate_p_per_kwh=unit_rate_p_per_kwh,
                ).decision.value,
            }
        )
    return observations, detail


def two_level(panel, weather):
    """The realism of the traces the gap was measured ON, so the two are read
    together rather than in two places."""
    return fgl.evaluate_two_level(
        fgl.premise_trace_population([entry[2] for entry in panel], weather)
    )


def _git_head():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, cwd=str(PROJECT_DIR)
        ).strip()
    except Exception:
        return None


def _money_json(m):
    """The money consequence in full. Every count is emitted, not just the misrank
    rate: a reader who saw only `misrank_rate` would read a company that declined
    every premise as flawless."""
    return {
        "premises": m.premises,
        "misrank_rate": m.misrank_rate,
        "misranked_premises": m.misranked_premises,
        "declined_where_value_existed": m.declined_where_value_existed,
        "value_destroying_recommendations": m.value_destroying_recommendations,
        "forgone_lifetime_gbp": m.forgone_lifetime_gbp,
        "forgone_annual_kwh": m.forgone_annual_kwh,
        "forgone_annual_kg_co2e": m.forgone_annual_kg_co2e,
        "gbp_per_tonne_co2e": m.gbp_per_tonne_co2e,
        "basis": m.basis,
    }


def _refresh_args(args) -> list[str]:
    """The arguments that REPRODUCE this run's measurement, for the ledger row to carry.

    Every argument that determines the number is emitted EXPLICITLY, including ones left at
    their default. Recording only the non-defaults would make the row's reproducibility hostage
    to this file's default values: change `--seed`'s default and every legacy row silently
    starts refreshing to a different measurement, which is the class this exists to close.

    `--write-ledger` is NOT included — the reconciler adds it, because whether to write is the
    caller's business, not a property of the population.
    """
    argv = ["--seed", str(args.seed), "--unit-rate", str(args.unit_rate)]
    if args.population:
        argv += ["--population", str(args.population),
                 "--population-seed", str(args.population_seed)]
    elif args.premises:
        argv += ["--premises", str(args.premises)]
    return argv


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--premises", type=int, default=None,
                    help="limit the panel (default: the whole panel)")
    ap.add_argument("--population", type=int, default=None,
                    help="measure on N premises DRAWN from published stock marginals "
                         "instead of the authored panel (the C14 L3 exit condition)")
    ap.add_argument("--population-seed", type=int, default=17,
                    help="base seed for the population draw (C-S2 substream key)")
    ap.add_argument("--unit-rate", type=float, default=DEFAULT_UNIT_RATE_P_PER_KWH,
                    help="p/kWh used to price the money consequence (DIAGNOSTIC)")
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gaps into coupled_gap_ledger.json")
    ap.add_argument("--audit-wall", action="store_true",
                    help="print exactly what crossed to the company side")
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = ap.parse_args()

    weather = load_weather()
    if args.population:
        if args.premises:
            # Two mutually exclusive populations silently resolved one way would
            # let a run label itself with the composition it did not use.
            ap.error("--population and --premises name different populations; pick one")
        panel = build_drawn_population(
            weather, n=args.population, seed=args.seed,
            population_seed=args.population_seed,
        )
    else:
        panel = build_panel(weather, seed=args.seed, limit=args.premises)
    observations, detail = observe(panel, weather, unit_rate_p_per_kwh=args.unit_rate)
    result = two_level(panel, weather)

    epc = fgl.epc_vs_actual_gap(observations)
    inferred = fgl.inferred_vs_actual_gap(observations)
    money_epc = fgl.money_consequence(
        observations, unit_rate_p_per_kwh=args.unit_rate, belief="epc")
    money_inferred = fgl.money_consequence(
        observations, unit_rate_p_per_kwh=args.unit_rate, belief="inferred")
    # THE HEADLINE'S OWN FAILURE MODES (2026-08-11 Expert Hour). Computed on every
    # run, printed above the fold, and NOT behind a flag: the two numbers below are
    # diluted, direction-blind and composition-dependent on the populations this
    # tool actually measures, and a caveat a reader has to opt into is not a caveat.
    agreement = fgl.arm_agreement(observations)
    verdict = fgl.composition_verdict(
        observations, unit_rate_p_per_kwh=args.unit_rate)
    biases = {
        arm: fgl.belief_bias(observations, belief=arm) for arm in ("epc", "inferred")
    }
    caveats = fgl.headline_caveats(observations, unit_rate_p_per_kwh=args.unit_rate)

    composition = (
        f"DRAWN from published stock marginals (n={args.population}, "
        f"population_seed={args.population_seed})"
        if args.population
        else f"AUTHORED panel ({len(observations)} premises, composed to span the stock)"
    )

    if args.json:
        print(json.dumps({
            "population": composition,
            "epc_vs_actual_gap": epc.gap,
            "inferred_vs_actual_gap": inferred.gap,
            "inference_improvement": epc.gap - inferred.gap,
            "arm_agreement": fgl.arm_agreement_components(agreement),
            "belief_bias": {
                arm: fgl.belief_bias_components(b) for arm, b in biases.items()
            },
            "composition_verdict": fgl.composition_verdict_components(verdict),
            "headline_caveats": caveats,
            "money_epc": _money_json(money_epc),
            "money_inferred": _money_json(money_inferred),
            "two_level_is_red": result.is_red,
            "two_level_failed": [c.statistic for c in result.failed],
            "premises": detail,
        }, indent=2))
    else:
        print("FABRIC coupled triad — W1_11 truth / W1_12 traces / C14 belief")
        print(f"  window                    : {WINDOW_START} -> {WINDOW_END}"
              f"  ({len(weather)} days, real Open-Meteo archive)")
        print(f"  premises                  : {len(observations)}")
        print(f"  population                : {composition}")
        print()
        # A 200-row table is not read; the whole point of a population is the
        # aggregate. The head is printed so a reader can still see individual
        # rows, and the truncation is STATED rather than silent.
        shown = detail if len(detail) <= 12 else detail[:12]
        print("  premise  cadence  cert        actual    EPC    inferred   sd   actionable")
        for d in shown:
            print(f"  {d['premise_id']:<8} {d['meter_cadence_days']:>4}d  "
                  f"{d['certificate']:<11} {d['actual']:.4f}  {d['epc']:.4f}  "
                  f"{d['inferred']:.4f}  {d['relative_sd']:.3f}  "
                  f"{'yes' if d['is_actionable'] else 'NO':>3}  ({d['basis']})")
        if len(shown) < len(detail):
            print(f"  ... {len(detail) - len(shown)} further premises not printed"
                  " (all of them are in --json and in every figure below)")
        print()
        print(f"  EPC-vs-actual gap         : {epc.gap:.4f}"
              "   (1.0 = no better than the stock mean)")
        print(f"  inferred-vs-actual gap    : {inferred.gap:.4f}")
        print(f"  inference improvement     : {epc.gap - inferred.gap:+.4f}"
              "   (positive = inference beat the register)")
        print()
        print(f"  MONEY CONSEQUENCE at {args.unit_rate:.2f} p/kWh"
              "  (DIAGNOSTIC; AFFINE in the rate, not proportional to it — the capex of a\n"
              "   wrongly-bought measure does not move with the price, and the price\n"
              "   also decides WHICH measure wins):")
        for label, m in (("on EPC belief", money_epc), ("on inferred belief", money_inferred)):
            print(f"    {label:<20} forgone GBP {m.forgone_lifetime_gbp:,.0f}"
                  f"  {m.forgone_annual_kg_co2e:,.0f} kg CO2e/yr")
            # The THREE kinds of wrong, never summed into one rate: buying the wrong
            # measure, refusing where value existed, and buying something that
            # destroys value are different failures with different remedies.
            print(f"    {'':<20}   bought wrong {m.misranked_premises}"
                  f" (of which value-DESTROYING {m.value_destroying_recommendations})"
                  f"  declined-where-value-existed {m.declined_where_value_existed}"
                  f"  of {m.premises}")
        print()
        # THE HEADLINE ABOUT THE HEADLINE. Printed unconditionally and BEFORE the
        # two-level verdict, because the two figures above are the ones a reader
        # carries away and these are the conditions under which they mean what they
        # appear to mean.
        print("  HOW TO READ THE TWO FIGURES ABOVE:")
        print(f"    inference ran on          : {agreement.informed_premises}"
              f" of {agreement.premises} premises"
              f"  (tie fraction {agreement.tie_fraction:.0%};"
              f" identical arms {agreement.identical_arm_premises},"
              f" of which inference-ran {agreement.informed_but_identical})")
        print(f"    improvement, as published : {agreement.improvement_all:+.4f}")
        print(f"    improvement, where it ran : {agreement.improvement_informed:+.4f}"
              "   (own no-skill baseline, not the same denominator)")
        for arm, b in biases.items():
            print(f"    {arm + ' direction':<26}: {b.direction:<5}"
                  f" {b.n_above} above / {b.n_below} below / {b.n_exact} exact,"
                  f" signed mean {b.signed_mean_relative_error:+.1%},"
                  f" sign-test p={b.sign_test_p:.4f}"
                  f"{'  SYSTEMATIC' if b.is_systematic else ''}")
        print(f"    accuracy favours          : {verdict.accuracy_favours}"
              f"     money favours: {verdict.money_favours}"
              f"     {'AGREE' if verdict.verdicts_agree else 'DISAGREE'}")
        print(f"    money, mirrored PANEL     : {verdict.panel_mirror_money_favours}"
              f"   (a stock that fails the other way; accuracy moved"
              f" {verdict.panel_mirror_accuracy_drift:.4f};"
              f" truth-above-register {verdict.truth_above_epc_share:.0%})"
              f"{'   COMPOSITION-DECIDED' if verdict.composition_decided else ''}")
        print(f"    money, mirrored REVISION  : {verdict.revision_mirror_money_favours}"
              f"   (same step, other way;"
              f" revision agreed with truth on"
              f" {verdict.revision_agrees_with_panel_share:.0%} of moved premises)"
              f"{'   DIRECTION-BOUGHT' if verdict.direction_bought else ''}")
        print(f"    money, swapped ERROR BARS : {verdict.confidence_mirror_money_favours}"
              f"   (estimates untouched, so accuracy is unchanged;"
              f" declined-where-value-existed {verdict.declined_epc} epc /"
              f" {verdict.declined_inferred} inferred)"
              f"{'   CONFIDENCE-BOUGHT' if verdict.confidence_bought else ''}")
        for caveat in caveats:
            print(f"  !! {caveat}")
        print()
        print(f"  two-level test            : {'RED' if result.is_red else 'green'}"
              f"  failed {[c.statistic for c in result.failed]}")
        warning = result.goal_seek_warning()
        if warning:
            print(f"  !! {warning}")

    if args.audit_wall:
        print()
        print("  WALL AUDIT — everything that crossed to the company side:")
        print("    * cumulative meter register reads, at each premise's own cadence")
        print("    * published daily MEAN temperature (date, degC)")
        print("    * the EPC certificate in the register's string vocabulary, or None")
        print("    * a property-type hint and the main heating fuel, both register fields")
        print("  NOT crossed: fabric parameters, HLC truth, half-hourly traces, setpoints,")
        print("  occupancy, the gap itself, or any number computed in this file.")

    if args.write_ledger:
        measured_at = dt.datetime.now(dt.timezone.utc).isoformat()
        written = fgl.write_fabric_gap_entries(
            observations,
            unit_rate_p_per_kwh=args.unit_rate,
            measured_at=measured_at,
            run_git_commit=_git_head(),
            two_level=result,
            composition=composition,
            refresh_args=_refresh_args(args),
        )
        print()
        print(f"  ledger written: {fgl.FABRIC_WORLD_ATOM} -> gap="
              f"{written['epc_vs_actual'].gap:.4f}")
        print(f"                  {fgl.GENERATOR_WORLD_ATOM} -> gap="
              f"{written['inferred_vs_actual'].gap:.4f}")


if __name__ == "__main__":
    main()
