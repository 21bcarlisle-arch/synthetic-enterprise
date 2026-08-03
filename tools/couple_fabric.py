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
from company.pricing import thermal_inference as ti  # noqa: E402
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
AS_OF = dt.date(2022, 5, 1)

# The default unit rate. DIAGNOSTIC input, not a company figure: the money
# consequence scales linearly with it, so it is printed alongside every £ result
# rather than buried (R14 — a figure without its basis is a defect).
DEFAULT_UNIT_RATE_P_PER_KWH = 7.4

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
# era x insulation x occupancy, plus a heat pump (whose flat assumed SCOP is a
# KNOWN bias source C14 copes with by widening, never by correcting).
#
# `every_n_days` is the METER CADENCE, and it is deliberately NOT uniform: a real
# supplier's book is a mix of smart (daily) and traditional (monthly/quarterly)
# meters, and C14's measured error runs 0.2% -> 18% across that range. A panel read
# entirely daily would flatter the company by giving every premise smart-meter
# evidence it does not have.
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
}


def _household(premise_id, property_type, build_era, insulation, bedrooms, people, heating):
    return Household(
        customer_id=premise_id,
        property_type=property_type,
        build_era=build_era,
        epc_rating="D",
        bedrooms=bedrooms,
        heating_system=heating,
        boiler_age=BoilerAge.MID,
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
        main_heating_fuel=(
            "air source heat pump"
            if household.heating_system == HeatingSystem.HEAT_PUMP_AIR
            else "mains gas"
        ),
    )


def load_weather():
    """The REAL Open-Meteo reanalysis archive (Historical Ground Truth).

    Deliberately NOT wrapped in a try/except: if the archive is missing this must
    raise, never fall back to a synthetic series. A gap measured against invented
    weather would be a number with no meaning, reported as though it had one.
    """
    return pt.load_trace_weather("C1", start=WINDOW_START, end=WINDOW_END)


def build_panel(weather, *, seed: int = 17, limit: int | None = None):
    """Generate the WORLD side once: truth traces off the real weather archive."""
    specs = PANEL[:limit] if limit else PANEL
    out = []
    for premise_id, ptype, era, insulation, bedrooms, people, heating, cadence in specs:
        household = _household(premise_id, ptype, era, insulation, bedrooms, people, heating)
        trace = pt.generate_premise_trace(
            premise_id=premise_id, household=household, weather=weather, seed=seed
        )
        commodity = "electricity" if heating == HeatingSystem.HEAT_PUMP_AIR else "gas"
        out.append((premise_id, household, trace, commodity, cadence))
    return out


def observe(panel, weather):
    """Hold the two sides together — the ONE place permitted to do so.

    Returns (observations, per-premise detail). The company's belief is computed
    from observables ONLY; the truth is read from the trace's fabric and never
    passed into the inference call.
    """
    published = [
        ti.PublishedWeatherDay(day.date, day.weather.temperature_mean_c)
        for day in weather
    ]
    observations, detail = [], []
    for premise_id, household, trace, commodity, cadence in panel:
        certificate = _certificate_for(trace, household, _LODGED.get(premise_id))
        belief = ti.infer_thermal_parameters(
            premise_id=premise_id,
            reads=_reads_from_trace(
                trace, commodity, every_n_days=cadence, start=WINDOW_START
            ),
            weather=published,
            certificate=certificate,
            as_of=AS_OF,
            property_type_hint=_EPC_PROPERTY_TYPE[household.property_type],
            main_heating_fuel=(
                "air source heat pump"
                if household.heating_system == HeatingSystem.HEAT_PUMP_AIR
                else "mains gas"
            ),
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
            )
        )
        detail.append(
            {
                "premise_id": premise_id,
                "meter_cadence_days": cadence,
                "certificate": "none" if certificate is None else str(_LODGED[premise_id]),
                "actual": actual,
                "epc": belief.prior.hlc_kw_per_k,
                "inferred": belief.hlc_kw_per_k,
                "relative_sd": belief.relative_sd,
                "basis": belief.basis.value,
                "is_actionable": belief.is_actionable,
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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--premises", type=int, default=None,
                    help="limit the panel (default: the whole panel)")
    ap.add_argument("--unit-rate", type=float, default=DEFAULT_UNIT_RATE_P_PER_KWH,
                    help="p/kWh used to price the money consequence (DIAGNOSTIC)")
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gaps into coupled_gap_ledger.json")
    ap.add_argument("--audit-wall", action="store_true",
                    help="print exactly what crossed to the company side")
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = ap.parse_args()

    weather = load_weather()
    panel = build_panel(weather, seed=args.seed, limit=args.premises)
    observations, detail = observe(panel, weather)
    result = two_level(panel, weather)

    epc = fgl.epc_vs_actual_gap(observations)
    inferred = fgl.inferred_vs_actual_gap(observations)
    money_epc = fgl.money_consequence(
        observations, unit_rate_p_per_kwh=args.unit_rate, belief="epc")
    money_inferred = fgl.money_consequence(
        observations, unit_rate_p_per_kwh=args.unit_rate, belief="inferred")

    if args.json:
        print(json.dumps({
            "epc_vs_actual_gap": epc.gap,
            "inferred_vs_actual_gap": inferred.gap,
            "inference_improvement": epc.gap - inferred.gap,
            "money_epc": {
                "misrank_rate": money_epc.misrank_rate,
                "forgone_lifetime_gbp": money_epc.forgone_lifetime_gbp,
            },
            "money_inferred": {
                "misrank_rate": money_inferred.misrank_rate,
                "forgone_lifetime_gbp": money_inferred.forgone_lifetime_gbp,
            },
            "two_level_is_red": result.is_red,
            "two_level_failed": [c.statistic for c in result.failed],
            "premises": detail,
        }, indent=2))
    else:
        print("FABRIC coupled triad — W1_11 truth / W1_12 traces / C14 belief")
        print(f"  window                    : {WINDOW_START} -> {WINDOW_END}"
              f"  ({len(weather)} days, real Open-Meteo archive)")
        print(f"  premises                  : {len(observations)}")
        print()
        print("  premise  cadence  cert        actual    EPC    inferred   sd   actionable")
        for d in detail:
            print(f"  {d['premise_id']:<8} {d['meter_cadence_days']:>4}d  "
                  f"{d['certificate']:<11} {d['actual']:.4f}  {d['epc']:.4f}  "
                  f"{d['inferred']:.4f}  {d['relative_sd']:.3f}  "
                  f"{'yes' if d['is_actionable'] else 'NO':>3}  ({d['basis']})")
        print()
        print(f"  EPC-vs-actual gap         : {epc.gap:.4f}"
              "   (1.0 = no better than the stock mean)")
        print(f"  inferred-vs-actual gap    : {inferred.gap:.4f}")
        print(f"  inference improvement     : {epc.gap - inferred.gap:+.4f}"
              "   (positive = inference beat the register)")
        print()
        print(f"  MONEY CONSEQUENCE at {args.unit_rate:.2f} p/kWh (DIAGNOSTIC, scales linearly):")
        for label, m in (("on EPC belief", money_epc), ("on inferred belief", money_inferred)):
            print(f"    {label:<20} misrank {m.misrank_rate:.3f}"
                  f"  forgone GBP {m.forgone_lifetime_gbp:,.0f}"
                  f"  {m.forgone_annual_kg_co2e:,.0f} kg CO2e/yr")
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
        )
        print()
        print(f"  ledger written: {fgl.FABRIC_WORLD_ATOM} -> gap="
              f"{written['epc_vs_actual'].gap:.4f}")
        print(f"                  {fgl.GENERATOR_WORLD_ATOM} -> gap="
              f"{written['inferred_vs_actual'].gap:.4f}")


if __name__ == "__main__":
    main()
