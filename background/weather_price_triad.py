"""COUPLED-TRIAD runner for the W1_6 weather-physics price signal.

The third loop of the weather coupled triad (COUPLED_TRIAD: SIM adds depth ->
COMPANY copes through the wall -> HARNESS measures the belief-vs-truth GAP; the
gap is the score). This is HARNESS code: it sits OUTSIDE the epistemic wall and
is the ONLY layer permitted to hold the SIM ground truth AND the company belief
side by side (design 1.3). It lives in `background/` (like `couple_w2_10_c12`),
NOT under `company/`/`saas/`, so it may import both sides.

  1. SIM adds depth   -- sim.weather_price_chain (W1_6): one coherent weather draw
                         -> demand + renewable -> residual demand -> merit order ->
                         DERIVED price. The convex merit-order tail is the hidden
                         truth. The chain's derived price IS the published price a
                         supplier observes; how it was formed is NOT observable.
  2. COMPANY copes    -- company.pricing.weather_price_belief: fits a naive LINEAR
                         price ~ gas + temp + wind on the OBSERVED (published price,
                         public weather, gas). It cannot see residual demand or the
                         merit order, so it under-predicts the cold-and-still spike.
                         ONLY observables cross into it -- this harness hands it the
                         weather/gas/published-price arrays, never a SIM internal.
  3. HARNESS measures -- prediction_gap(truth, belief) per CELL, normalised to the
                         climatological-mean no-skill baseline. Reported per the
                         fidelity steer: the SCORE is the WORST-explained cell (the
                         cold-and-still tail), not the population average.

R15 INDEPENDENCE / NOT A TAUTOLOGY. The truth is a convex composed physics chain;
the belief is an observables-only linear regression. They are DIFFERENT machinery,
so the gap is a real form-inadequacy measurement. If the belief recovered the
truth on the tail the observables would have leaked the merit-order mechanism -- a
wall violation, not a triumph.

R12/R13. Nothing here is tuned to a target gap. The chain's constants are W1_6's
own R13-baseline fit; the belief's coefficients are whatever the observed data
produce; the gap is whatever falls out. `measured_at`/`run_git_commit` are gathered
by THIS harness for the ledger (gap_metric never calls a clock -- C-S2).
"""
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from typing import Dict, List

import numpy as np

from sim.weather_price_chain import cold_still_tail_mask, derive_price_on_record, fit_chain
from company.pricing.weather_price_belief import fit_weather_price_belief
from background.gap_metric import prediction_gap, write_gap_entry

WORLD_ATOM_ID = "W1_6_physics_price_signal"
# The nearest registered company-weather twin. C13 is the weather-normalisation
# (demand-belief) twin; THIS pair measures the PRICE-belief facet of the same
# company facing the same weather physics through the wall. A dedicated company
# price-belief C-atom is a proposed follow-on (see the map simplification); the
# ledger points at the real registered twin meanwhile.
TWIN_ATOM_ID = "C13_weather_normalisation"

# Crisis regime tag (the real UK gas-crisis years), a human-readable cell label
# only -- never a computed input to the fit (matches fidelity_emitter's convention).
_CRISIS_YEARS = ("2021", "2022")


def _cells(out: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """The scoring grid (campaign requirement 1: span the range of NEED / stress,
    score the worst cell). Boolean masks over the record:
      * cold_still_tail -- the Dunkelflaute corner where the convex merit order
        bites (the cell that stresses the physics; expected worst).
      * winter / summer -- seasonal regimes.
      * crisis / calm   -- the 2021-22 gas crisis vs the rest.
    """
    years = np.array([d[:4] for d in out["dates"]])
    winter = np.isin(out["month"], (12, 1, 2))
    summer = np.isin(out["month"], (6, 7, 8))
    crisis = np.isin(years, _CRISIS_YEARS)
    tail = cold_still_tail_mask(out)
    return {
        "cold_still_tail": tail,
        "winter": winter,
        "summer": summer,
        "crisis": crisis,
        "calm": ~crisis,
    }


def measure() -> Dict[str, object]:
    """Run the coupled loop on the real record and compute the per-cell gap.

    Returns a dict with the population gap, every cell's gap, the worst cell (the
    SCORE), the chain fit + spike diagnostics, and the fitted belief -- so a caller
    or test can quote the real numbers.
    """
    out = derive_price_on_record()
    truth = out["derived_price"]

    # -- COMPANY side: observables ONLY cross the wall. The company sees the
    #    published price (== the chain's derived output), public weather, gas. --
    belief_model = fit_weather_price_belief(
        gas_price=out["gas_price"], temp_c=out["temperature_c"],
        wind_speed_ms=out["wind_speed_ms"], published_price=truth,
    )
    belief = belief_model.predict(out["gas_price"], out["temperature_c"], out["wind_speed_ms"])

    # -- HARNESS: hold truth and belief side by side; gap per cell. --
    population = prediction_gap(truth, belief)

    cells = _cells(out)
    per_cell: Dict[str, Dict[str, float]] = {}
    for name, mask in cells.items():
        if int(mask.sum()) < 10:
            continue
        # Each cell is normalised to ITS OWN climatological-mean no-skill baseline
        # (predict this cell's mean) -- so a cell's gap says "vs a blind guess
        # calibrated to this cell", the worst-cell comparison the steer wants.
        g = prediction_gap(truth[mask], belief[mask])
        per_cell[name] = {
            "gap": g.gap, "mae_model": g.components["mae_model"],
            "mae_noskill": g.components["mae_noskill"],
            "bias_model": g.components["bias_model"], "n": int(mask.sum()),
        }

    # The SCORE = the worst-explained cell (campaign requirement 1), not the mean.
    worst_cell = max(per_cell, key=lambda c: (per_cell[c]["gap"] if per_cell[c]["gap"] is not None else -1))
    worst_gap = per_cell[worst_cell]["gap"]

    spike = cold_still_spike_summary(out)
    params = fit_chain()

    return {
        "population_gap": population,
        "per_cell": per_cell,
        "worst_cell": worst_cell,
        "worst_gap": worst_gap,
        "truth": truth,
        "belief": belief,
        "belief_model": belief_model,
        "chain_params": params,
        "spike": spike,
        "n": int(len(truth)),
    }


def cold_still_spike_summary(out: Dict[str, np.ndarray]) -> Dict[str, float]:
    """The show-the-tail numbers on the derived-price record (mechanistic spike)."""
    tail = cold_still_tail_mask(out)
    rest = ~tail
    return {
        "tail_mean_price": float(out["derived_price"][tail].mean()),
        "rest_mean_price": float(out["derived_price"][rest].mean()),
        "tail_mean_residual_mw": float(out["residual_mw"][tail].mean()),
        "rest_mean_residual_mw": float(out["residual_mw"][rest].mean()),
        "n_tail": int(tail.sum()),
    }


def build_gap_result(measurement: Dict[str, object]):
    """Shape the coupled-gap-ledger GapResult. HEADLINE gap = the WORST-cell gap
    (the score per the fidelity steer); the population gap + every cell + the
    spike diagnostics are carried in `components` so a reviewer sees the full grid
    and that the worst cell was not cherry-picked."""
    worst_cell = measurement["worst_cell"]
    per_cell = measurement["per_cell"]
    population = measurement["population_gap"]
    belief_model = measurement["belief_model"]
    params = measurement["chain_params"]
    spike = measurement["spike"]

    # Re-use the population GapResult's container but overwrite the headline gap
    # with the worst-cell score, keeping raw_gap/g0 from the worst cell for audit.
    result = prediction_gap(measurement["truth"], measurement["belief"])
    result.gap = per_cell[worst_cell]["gap"]
    result.raw_gap = per_cell[worst_cell]["mae_model"]
    result.g0 = per_cell[worst_cell]["mae_noskill"]
    result.metric = "prediction"
    result.baseline = (
        f"worst cell = {worst_cell}: company linear weather->price MAE "
        f"£{per_cell[worst_cell]['mae_model']:.2f}/MWh vs no-skill "
        f"£{per_cell[worst_cell]['mae_noskill']:.2f}/MWh"
    )
    result.components = {
        "score_definition": "worst-explained cell (campaign req 1), not the population average",
        "worst_cell": worst_cell,
        "worst_cell_gap": per_cell[worst_cell]["gap"],
        "population_gap": population.gap,
        "population_mae_model": population.components["mae_model"],
        "population_mae_noskill": population.components["mae_noskill"],
        "per_cell": per_cell,
        "belief_form": "linear: price ~ a + b_gas*gas + b_temp*temp + b_wind*wind",
        "belief_coeffs": {
            "intercept": belief_model.intercept, "b_gas": belief_model.b_gas,
            "b_temp": belief_model.b_temp, "b_wind": belief_model.b_wind,
            "r2": belief_model.r2, "n_train": belief_model.n_train,
        },
        "chain_fit": {
            "demand_r2": params.demand_r2, "wind_corr": params.wind_corr,
            "solar_corr": params.solar_corr, "n_days": params.n_days,
        },
        "cold_still_spike": spike,
        "tail_bias_mwh": per_cell.get("cold_still_tail", {}).get("bias_model"),
    }
    result.note = (
        "W1_6 weather-physics price signal: company linear weather->price belief vs "
        "the SIM's convex merit-order DERIVED price. SCORE = worst cell "
        f"({worst_cell}, gap {per_cell[worst_cell]['gap']:.3f}); the company nails "
        f"the comfortable middle (population gap {population.gap:.3f}) but "
        "under-predicts the cold-and-still spike -- a signed under-bias on the tail "
        "(belief cannot see residual demand / the convex merit order, by the wall). "
        "R12: diagnostic, not a target."
    )
    return result


def _git_head() -> str | None:
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
    spike = m["spike"]
    print("W1_6 weather-physics price-signal coupled triad")
    print(f"  aligned days             : {m['n']}")
    print(f"  chain fit                : demand R2={m['chain_params'].demand_r2:.3f}"
          f"  wind corr={m['chain_params'].wind_corr:.3f}"
          f"  solar corr={m['chain_params'].solar_corr:.3f}")
    print(f"  cold-still spike         : £{spike['tail_mean_price']:.1f}/MWh (tail) "
          f"vs £{spike['rest_mean_price']:.1f}/MWh (rest), "
          f"residual {spike['tail_mean_residual_mw']:.0f} vs {spike['rest_mean_residual_mw']:.0f} MW"
          f"  (n_tail={spike['n_tail']})")
    print(f"  population gap            : {m['population_gap'].gap:.3f}")
    print("  per-cell gap:")
    for name, c in sorted(per_cell.items(), key=lambda kv: -(kv[1]['gap'] or -1)):
        print(f"    {name:16s} gap={c['gap']:.3f}  MAE_model=£{c['mae_model']:.1f}"
              f"  bias=£{c['bias_model']:+.1f}  n={c['n']}")
    print(f"  WORST CELL (the score)   : {m['worst_cell']}  gap={m['worst_gap']:.3f}")

    if args.write_ledger:
        result = build_gap_result(m)
        measured_at = datetime.now(timezone.utc).isoformat()
        ledger = write_gap_entry(WORLD_ATOM_ID, TWIN_ATOM_ID, result,
                                 measured_at=measured_at, run_git_commit=_git_head())
        print(f"  ledger written           : {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
