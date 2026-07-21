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
                         temperature-only HDD/CDD degree-day regression on the
                         OBSERVED (metered demand, published temperature). It cannot
                         see wind chill (CWV) or the regional dispersion, so it
                         under-explains the cold-and-windy tail. ONLY observables
                         cross into it -- this harness hands it the temperature +
                         demand arrays, never a SIM internal.
  3. HARNESS measures -- prediction_gap(truth, belief) per CELL, normalised to the
                         climatological-mean no-skill baseline. Reported per the
                         fidelity steer: the SCORE is the WORST-explained cell (the
                         cold-and-windy tail), not the population average.

BASELINE CHOICE (resolves C13 FRAME open question 1, named explicitly per that
doc's instruction). g0 = the climatological-mean no-skill baseline (predict the
average demand every period), matching the W1_6 continuous-prediction convention
and the shared `prediction_gap` machinery. The FRAME's alternative "flat national
degree-day" baseline is a per-day series `prediction_gap`'s scalar prior cannot
express; it is registered as an L2 refinement (a stronger no-skill floor that would
raise the reported gap toward 1, the honest "no book/regional discrimination yet"
reading). Named, not left implicit.

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

    Returns a dict with the population gap, every cell's gap, the worst cell (the
    SCORE), the fitted belief, and the raw truth/belief series -- so a caller or
    test can quote the real numbers.
    """
    rec = demand_truth_on_record()
    truth = rec["demand_mw"]

    # -- COMPANY side: observables ONLY cross the wall. The company sees its own
    #    confounded meter reads (== the demand outturn) and public temperature. --
    belief_model = fit_weather_normalisation_belief(
        temp_c=rec["temperature_c"], observed_demand=truth,
    )
    belief = belief_model.predict(rec["temperature_c"])

    # -- HARNESS: hold truth and belief side by side; gap per cell. --
    population = prediction_gap(truth, belief)

    cells = _cells(rec)
    per_cell: Dict[str, Dict[str, float]] = {}
    for name, mask in cells.items():
        if int(mask.sum()) < 10:
            continue
        # Each cell is normalised to ITS OWN climatological-mean no-skill baseline
        # (predict this cell's mean demand) -- so a cell's gap says "vs a blind
        # guess calibrated to this cell", the worst-cell comparison the steer wants.
        g = prediction_gap(truth[mask], belief[mask])
        per_cell[name] = {
            "gap": g.gap, "mae_model": g.components["mae_model"],
            "mae_noskill": g.components["mae_noskill"],
            "bias_model": g.components["bias_model"], "n": int(mask.sum()),
        }

    # The SCORE = the worst-explained cell (campaign requirement 1), not the mean.
    worst_cell = max(
        per_cell, key=lambda c: (per_cell[c]["gap"] if per_cell[c]["gap"] is not None else -1))
    worst_gap = per_cell[worst_cell]["gap"]

    return {
        "population_gap": population,
        "per_cell": per_cell,
        "worst_cell": worst_cell,
        "worst_gap": worst_gap,
        "truth": truth,
        "belief": belief,
        "belief_model": belief_model,
        "n": int(len(truth)),
    }


def build_gap_result(measurement: Dict[str, object]):
    """Shape the coupled-gap-ledger GapResult. HEADLINE gap = the WORST-cell gap
    (the score per the fidelity steer); the population gap + every cell are carried
    in `components` so a reviewer sees the full grid and that the worst cell was not
    cherry-picked."""
    worst_cell = measurement["worst_cell"]
    per_cell = measurement["per_cell"]
    population = measurement["population_gap"]
    belief_model = measurement["belief_model"]

    # Re-use the population GapResult's container but overwrite the headline gap
    # with the worst-cell score, keeping raw_gap/g0 from the worst cell for audit.
    result = prediction_gap(measurement["truth"], measurement["belief"])
    result.gap = per_cell[worst_cell]["gap"]
    result.raw_gap = per_cell[worst_cell]["mae_model"]
    result.g0 = per_cell[worst_cell]["mae_noskill"]
    result.metric = "prediction"
    result.baseline = (
        f"worst cell = {worst_cell}: company temperature-only degree-day "
        f"weather-normalisation MAE {per_cell[worst_cell]['mae_model']:.0f} MW vs "
        f"no-skill {per_cell[worst_cell]['mae_noskill']:.0f} MW"
    )
    result.components = {
        "score_definition": "worst-explained cell (campaign req 1), not the population average",
        "worst_cell": worst_cell,
        "worst_cell_gap": per_cell[worst_cell]["gap"],
        "population_gap": population.gap,
        "population_mae_model": population.components["mae_model"],
        "population_mae_noskill": population.components["mae_noskill"],
        "per_cell": per_cell,
        "belief_form": "temperature-only degree-day: demand ~ base + b_hdd*HDD + b_cdd*CDD",
        "belief_coeffs": {
            "base": belief_model.base, "b_hdd": belief_model.b_hdd,
            "b_cdd": belief_model.b_cdd, "r2": belief_model.r2,
            "n_train": belief_model.n_train,
        },
        "baseline_choice": (
            "g0 = climatological-mean no-skill (predict the average demand); the "
            "FRAME's flat-national-degree-day alternative is registered as an L2 "
            "refinement (a per-day series prediction_gap's scalar prior cannot hold)"
        ),
        "tail_bias_mw": per_cell.get("cold_windy_tail", {}).get("bias_model"),
    }
    result.note = (
        "W1_5 premise-demand weather-normalisation: company temperature-only "
        "degree-day belief vs the real national demand outturn (the W1_5-consistent "
        f"aggregate truth). SCORE = worst cell ({worst_cell}, gap "
        f"{per_cell[worst_cell]['gap']:.3f}); the company fits the seasonal degree-day "
        f"shape (population gap {population.gap:.3f}) but under-explains the cold-and-"
        "windy tail -- it cannot see wind chill (CWV) or the W1_5 regional-dispersion "
        "convexity, by the wall. R12: diagnostic, not a target."
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
    print("W1_5 <-> C13 weather-normalisation demand coupled triad")
    print(f"  aligned days             : {m['n']}")
    print(f"  belief fit               : demand ~ {bm.base:.0f} + {bm.b_hdd:.1f}*HDD "
          f"+ {bm.b_cdd:.1f}*CDD   R2={bm.r2:.3f}  n={bm.n_train}")
    print(f"  population gap            : {m['population_gap'].gap:.3f}")
    print("  per-cell gap:")
    for name, c in sorted(per_cell.items(), key=lambda kv: -(kv[1]['gap'] or -1)):
        print(f"    {name:16s} gap={c['gap']:.3f}  MAE_model={c['mae_model']:.0f}MW"
              f"  bias={c['bias_model']:+.0f}MW  n={c['n']}")
    print(f"  WORST CELL (the score)   : {m['worst_cell']}  gap={m['worst_gap']:.3f}")

    if args.write_ledger:
        result = build_gap_result(m)
        measured_at = datetime.now(timezone.utc).isoformat()
        ledger = write_gap_entry(WORLD_ATOM_ID, TWIN_ATOM_ID, result,
                                 measured_at=measured_at, run_git_commit=_git_head())
        print(f"  ledger written           : {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
