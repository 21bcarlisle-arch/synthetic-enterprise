"""COUPLED-TRIAD runner for the W1_5 <-> C13 weather-normalisation demand facet.

The third loop of the weather-DEMAND coupled triad (COUPLED_TRIAD: SIM adds depth
-> COMPANY copes through the wall -> HARNESS measures the belief-vs-truth GAP; the
gap is the score). This is HARNESS code: it sits OUTSIDE the epistemic wall and is
the ONLY layer permitted to hold the SIM ground truth AND the company belief side
by side (design 1.3). It lives in `background/` (like `weather_price_triad`), NOT
under `company/`/`saas/`, so it may import both sides.

  1. SIM adds depth   -- sim.weather_demand_chain (W1_5): the real national demand
                         outturn (Elexon INDO) aligned to real published weather --
                         the W1_5-consistent aggregate demand truth (premise demand
                         reconciles TO national). It carries wind-driven heat loss,
                         working-day/daylight load, and the regional-dispersion
                         convexity of the W1_5 field -- structure NOT observable.
  2. COMPANY copes    -- company.pricing.weather_normalisation_belief (C13): fits a
                         degree-day regression on the OBSERVED (metered demand,
                         published temperature[, published wind speed]). L2 adds
                         a wind-chill (CWV) regressor -- temperature AND wind
                         speed are BOTH published weather observables, so this
                         crosses no new wall. It still cannot see the W1_5
                         regional-dispersion convexity (a named L1->L2 remainder,
                         see below), so it under-explains wherever the missing
                         regional structure bites. ONLY observables cross into
                         it -- this harness hands it temperature/wind/demand
                         arrays, never a SIM internal.
  3. HARNESS measures -- prediction_gap(truth, belief) per CELL, normalised to the
                         climatological-mean no-skill baseline. Reported per the
                         fidelity steer: the SCORE is the WORST-explained cell,
                         not the population average. This module fits BOTH the L1
                         (temperature-only) and L2 (temperature+wind-chill)
                         beliefs side by side and reports both per cell -- the
                         L2/CWV term is measured HONESTLY (R12): it may help some
                         cells and hurt others, never tuned toward a target.

BASELINE CHOICE (resolves C13 FRAME open question 1, named explicitly per that
doc's instruction). g0 = the climatological-mean no-skill baseline (predict the
average demand every period), matching the W1_6 continuous-prediction convention
and the shared `prediction_gap` machinery. The FRAME's alternative "flat national
degree-day" baseline is a per-day series `prediction_gap`'s scalar prior cannot
express; it is registered as an L2 refinement (a stronger no-skill floor that would
raise the reported gap toward 1, the honest "no book/regional discrimination yet"
reading). Named, not left implicit.

L1->L2 REMAINDER (regional-dispersion). C13's second named L1->L2 refinement
(`company.pricing.weather_normalisation_belief.book_weighted_temperature`) is
BUILT and unit-proven against synthetic truth, but NOT wired into this real-record
measurement: this harness's truth (`demand_truth_on_record`) is the national
Elexon INDO aggregate, so there is no per-book regional demand truth inside this
atom's file_scope to measure book-weighting against (a company book-weighted
belief predicting the SAME national aggregate would be measuring the wrong
target). Registered per R10/FRAME sec5 -- not silently dropped.

R15 INDEPENDENCE / NOT A TAUTOLOGY. The truth is the real Elexon demand record; the
belief is an observables-only OLS degree-day regression. They are DIFFERENT
machinery, so the gap is a real form-inadequacy measurement. If the belief
recovered the truth on the tail the observables would have leaked the W1_5
thermal/regional mechanism -- a wall violation, not a triumph.

R12/R13. Nothing here is tuned to a target gap. The demand record is W1_5's own
R13 baseline (real published Elexon INDO); the belief's coefficients are whatever
the observed data produce; the gap is whatever falls out. `measured_at`/
`run_git_commit` are gathered by THIS harness for the ledger (gap_metric never
calls a clock -- C-S2).
"""
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from typing import Dict

import numpy as np

from sim.weather_demand_chain import cold_windy_tail_mask, demand_truth_on_record
from company.pricing.weather_normalisation_belief import fit_weather_normalisation_belief
from background.gap_metric import prediction_gap, write_gap_entry

WORLD_ATOM_ID = "W1_5_premise_demand_shape"
TWIN_ATOM_ID = "C13_weather_normalisation"

_WINTER_MONTHS = (12, 1, 2)
_SUMMER_MONTHS = (6, 7, 8)


def _cells(rec: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """The scoring grid (campaign requirement 1: span the range of NEED / stress,
    score the worst cell). Boolean masks over the record:
      * cold_windy_tail -- the wind-chill corner where the temperature-only
        degree-day belief is blindest (the cell that stresses W1_5's physics;
        expected worst).
      * cold             -- the coldest quintile (deep heating load).
      * winter / summer  -- seasonal regimes.
    """
    temp = rec["temperature_c"]
    cold_thr = float(np.percentile(temp, 20.0))
    warm_thr = float(np.percentile(temp, 80.0))
    # The shoulder band: temperature near the degree-day bases (little/no HDD or
    # CDD signal), where a temperature-only model has almost nothing to work with.
    shoulder = (temp > 12.0) & (temp < 18.0)
    return {
        "cold_windy_tail": cold_windy_tail_mask(rec),
        "cold": temp <= cold_thr,
        "warm": temp >= warm_thr,
        "shoulder": shoulder,
        "winter": np.isin(rec["month"], _WINTER_MONTHS),
        "summer": np.isin(rec["month"], _SUMMER_MONTHS),
    }


def measure() -> Dict[str, object]:
    """Run the coupled loop on the real record and compute the per-cell gap.

    Fits BOTH the L1 (temperature-only) and L2 (temperature + wind-chill/CWV)
    beliefs on the SAME observed history, so the L1->L2 refinement's effect on
    the gap is measured directly, per cell, rather than asserted. The L2 belief
    is the headline ("belief"/"belief_model", the SCORE); the L1 comparison is
    carried alongside every cell (`gap_l1`, `bias_model_l1`) for an honest
    before/after report (R12: whichever way it falls).

    Returns a dict with the population gap, every cell's gap (L2 headline + L1
    comparison), the worst cell (the SCORE, by the L2 gap), both fitted belief
    models, and the raw truth/belief series -- so a caller or test can quote the
    real numbers.
    """
    rec = demand_truth_on_record()
    truth = rec["demand_mw"]
    temp = rec["temperature_c"]
    wind = rec["wind_speed_ms"]

    # -- COMPANY side: observables ONLY cross the wall. The company sees its own
    #    confounded meter reads (== the demand outturn), published temperature,
    #    and published wind speed (the SAME epistemic status as temperature). --
    belief_model_l1 = fit_weather_normalisation_belief(
        temp_c=temp, observed_demand=truth,
    )
    belief_l1 = belief_model_l1.predict(temp)

    belief_model = fit_weather_normalisation_belief(
        temp_c=temp, observed_demand=truth, wind_speed_ms=wind,
    )
    belief = belief_model.predict(temp, wind_speed_ms=wind)

    # -- HARNESS: hold truth and belief side by side; gap per cell. --
    population = prediction_gap(truth, belief)
    population_l1 = prediction_gap(truth, belief_l1)

    cells = _cells(rec)
    per_cell: Dict[str, Dict[str, float]] = {}
    for name, mask in cells.items():
        if int(mask.sum()) < 10:
            continue
        # Each cell is normalised to ITS OWN climatological-mean no-skill baseline
        # (predict this cell's mean demand) -- so a cell's gap says "vs a blind
        # guess calibrated to this cell", the worst-cell comparison the steer wants.
        g = prediction_gap(truth[mask], belief[mask])
        g_l1 = prediction_gap(truth[mask], belief_l1[mask])
        per_cell[name] = {
            "gap": g.gap, "mae_model": g.components["mae_model"],
            "mae_noskill": g.components["mae_noskill"],
            "bias_model": g.components["bias_model"], "n": int(mask.sum()),
            "gap_l1": g_l1.gap, "mae_model_l1": g_l1.components["mae_model"],
            "bias_model_l1": g_l1.components["bias_model"],
        }

    # The SCORE = the worst-explained cell (campaign requirement 1), not the mean
    # -- scored on the L2 (headline) belief.
    worst_cell = max(
        per_cell, key=lambda c: (per_cell[c]["gap"] if per_cell[c]["gap"] is not None else -1))
    worst_gap = per_cell[worst_cell]["gap"]

    return {
        "population_gap": population,
        "population_gap_l1": population_l1,
        "per_cell": per_cell,
        "worst_cell": worst_cell,
        "worst_gap": worst_gap,
        "truth": truth,
        "belief": belief,
        "belief_l1": belief_l1,
        "belief_model": belief_model,
        "belief_model_l1": belief_model_l1,
        "n": int(len(truth)),
    }


def build_gap_result(measurement: Dict[str, object]):
    """Shape the coupled-gap-ledger GapResult. HEADLINE gap = the WORST-cell gap
    of the L2 (temperature+wind-chill) belief (the score per the fidelity steer);
    the population gap, every cell, and the L1 (temperature-only) comparison are
    carried in `components` so a reviewer sees the full grid, that the worst cell
    was not cherry-picked, and exactly what the CWV term changed (R12: honest
    either way)."""
    worst_cell = measurement["worst_cell"]
    per_cell = measurement["per_cell"]
    population = measurement["population_gap"]
    population_l1 = measurement["population_gap_l1"]
    belief_model = measurement["belief_model"]
    belief_model_l1 = measurement["belief_model_l1"]

    # Re-use the population GapResult's container but overwrite the headline gap
    # with the worst-cell score, keeping raw_gap/g0 from the worst cell for audit.
    result = prediction_gap(measurement["truth"], measurement["belief"])
    result.gap = per_cell[worst_cell]["gap"]
    result.raw_gap = per_cell[worst_cell]["mae_model"]
    result.g0 = per_cell[worst_cell]["mae_noskill"]
    result.metric = "prediction"
    result.baseline = (
        f"worst cell = {worst_cell}: company temperature+wind-chill (CWV) "
        f"degree-day weather-normalisation MAE {per_cell[worst_cell]['mae_model']:.0f} "
        f"MW vs no-skill {per_cell[worst_cell]['mae_noskill']:.0f} MW"
    )
    cwv_delta = per_cell[worst_cell]["gap"] - per_cell[worst_cell]["gap_l1"]
    result.components = {
        "score_definition": "worst-explained cell (campaign req 1), not the population average",
        "worst_cell": worst_cell,
        "worst_cell_gap": per_cell[worst_cell]["gap"],
        "worst_cell_gap_l1": per_cell[worst_cell]["gap_l1"],
        "population_gap": population.gap,
        "population_gap_l1": population_l1.gap,
        "population_mae_model": population.components["mae_model"],
        "population_mae_noskill": population.components["mae_noskill"],
        "per_cell": per_cell,
        "belief_form": (
            "L2 (headline): demand ~ base + b_hdd*HDD + b_cdd*CDD + b_windchill*"
            "windchill_DD (windchill_DD = HDD * max(wind - 4m/s, 0), the CWV term); "
            "L1 (comparison, gap_l1/mae_model_l1/bias_model_l1 per cell): "
            "demand ~ base + b_hdd*HDD + b_cdd*CDD"
        ),
        "belief_coeffs": {
            "base": belief_model.base, "b_hdd": belief_model.b_hdd,
            "b_cdd": belief_model.b_cdd, "b_windchill": belief_model.b_windchill,
            "r2": belief_model.r2, "n_train": belief_model.n_train,
        },
        "belief_coeffs_l1": {
            "base": belief_model_l1.base, "b_hdd": belief_model_l1.b_hdd,
            "b_cdd": belief_model_l1.b_cdd, "r2": belief_model_l1.r2,
            "n_train": belief_model_l1.n_train,
        },
        "baseline_choice": (
            "g0 = climatological-mean no-skill (predict the average demand); the "
            "FRAME's flat-national-degree-day alternative is registered as an L2 "
            "refinement (a per-day series prediction_gap's scalar prior cannot hold)"
        ),
        "tail_bias_mw": per_cell.get("cold_windy_tail", {}).get("bias_model"),
        "tail_bias_mw_l1": per_cell.get("cold_windy_tail", {}).get("bias_model_l1"),
        "cwv_worst_cell_gap_delta": cwv_delta,
        "regional_dispersion_remainder": (
            "book_weighted_temperature (2nd named L1->L2 refinement) is BUILT and "
            "unit-proven against synthetic truth in "
            "company/pricing/weather_normalisation_belief.py, but NOT wired into "
            "this real-record measurement -- no per-book regional demand truth "
            "exists inside this atom's file_scope to measure it against (R10, "
            "FRAME sec5/6-Q3). Registered, not silently dropped."
        ),
    }
    cwv_direction = "worsened" if cwv_delta > 0 else ("improved" if cwv_delta < 0 else "left unchanged")
    result.note = (
        "W1_5 premise-demand weather-normalisation: company temperature+wind-chill "
        "(CWV, L2) belief vs the real national demand outturn (the W1_5-consistent "
        f"aggregate truth). SCORE = worst cell ({worst_cell}, L2 gap "
        f"{per_cell[worst_cell]['gap']:.3f} vs L1 (temperature-only) gap "
        f"{per_cell[worst_cell]['gap_l1']:.3f} -- the CWV term {cwv_direction} the "
        "worst cell here); population gap L2 "
        f"{population.gap:.3f} vs L1 {population_l1.gap:.3f}. Honest per R12: the "
        "CWV term is measured, not tuned -- it helps the wind-relevant cells it "
        "targets and need not fix an unrelated worst cell. Regional-dispersion "
        "(2nd L1->L2 refinement) is built+tested but not yet measurable here -- "
        "see components.regional_dispersion_remainder."
    )
    return result


def _git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gap into coupled_gap_ledger.json")
    args = ap.parse_args()

    m = measure()
    per_cell = m["per_cell"]
    bm = m["belief_model"]
    bm1 = m["belief_model_l1"]
    print("W1_5 <-> C13 weather-normalisation demand coupled triad (L2: +CWV wind-chill)")
    print(f"  aligned days              : {m['n']}")
    print(f"  L1 belief fit (temp-only) : demand ~ {bm1.base:.0f} + {bm1.b_hdd:.1f}*HDD "
          f"+ {bm1.b_cdd:.1f}*CDD   R2={bm1.r2:.3f}  n={bm1.n_train}")
    print(f"  L2 belief fit (+wind CWV) : demand ~ {bm.base:.0f} + {bm.b_hdd:.1f}*HDD "
          f"+ {bm.b_cdd:.1f}*CDD + {bm.b_windchill:.1f}*windchillDD   R2={bm.r2:.3f}  n={bm.n_train}")
    print(f"  population gap L2 / L1    : {m['population_gap'].gap:.3f} / "
          f"{m['population_gap_l1'].gap:.3f}")
    print("  per-cell gap (L2 / L1):")
    for name, c in sorted(per_cell.items(), key=lambda kv: -(kv[1]['gap'] or -1)):
        print(f"    {name:16s} gap={c['gap']:.3f} / {c['gap_l1']:.3f}"
              f"  bias={c['bias_model']:+.0f} / {c['bias_model_l1']:+.0f} MW  n={c['n']}")
    print(f"  WORST CELL (the score)    : {m['worst_cell']}  L2 gap={m['worst_gap']:.3f}"
          f"  (L1 gap={per_cell[m['worst_cell']]['gap_l1']:.3f})")

    if args.write_ledger:
        result = build_gap_result(m)
        measured_at = datetime.now(timezone.utc).isoformat()
        ledger = write_gap_entry(WORLD_ATOM_ID, TWIN_ATOM_ID, result,
                                 measured_at=measured_at, run_git_commit=_git_head())
        print(f"  ledger written           : {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
