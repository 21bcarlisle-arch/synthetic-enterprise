"""Test B (SSP negative-lift diagnosis) -- global-fit-vs-local-refit of the
SAME structural form, per year-cell.

Diagnostic ONLY. It re-uses the landed calibration machinery
(`simulation.run_phase3b_recalibration._build_dataset` / `._fit_form`, and
`simulation.run_phase3b_regression` for the OLS baseline) purely as libraries;
it changes NO calibration constant on disk and reads NO company P&L, so it is
R13-clean (fidelity-to-reality, decided blind to company results) and R12-clean
(it measures which mechanism explains the loss, it does not tune any output
toward a benchmark).

Question it answers (from PLANNER_MINTED_ssp_negative_lift_cells_2026-07-24.md,
"Next=Test B"):
    Test A refuted the "scarcity term dormant in calm years" sub-hypothesis
    (the convex term is live 17-55% of the time EVERY year) and redirected the
    mechanism to: a SINGLE GLOBAL least-squares fit of A0/A1/A2 against a
    full-window x-distribution whose median drifted secularly (0.73 -> 0.46
    over 2016->2025). Under that redirection the prediction is:

        the calm-year negative lift is a STALE-GLOBAL-LINEAR-FIT artefact, NOT
        a scarcity-FORM defect. So if we refit A0/A1/A2 on each year's OWN
        x-distribution while HOLDING THE SCARCITY STRUCTURE FIXED (x_tight=0.70,
        p=2.0 -- the same convex kicker), the per-cell MAE in the losing calm
        cells should fall, recovering (flipping to non-negative) the lift the
        global fit gives away.

    A CONFIRM (local refit flips the calm negative-lift cells non-negative)
    points scope step 2 at a REGIME/TIME-AWARE calibration of the LINEAR terms
    (A0/A1), not a new structural form. A REFUTE (the same form refit locally
    still loses to the per-cell OLS) points at an R10 named simplification --
    the honest "the residual-demand form earns its keep only in scarcity
    regimes" close.

Fairness note on the baselines (matches background/fidelity_emitter.py exactly):
  - The ledger's per-cell OLS baseline is a SINGLE GLOBAL 3-feature OLS
    (`regr._fit_ols`) sliced per year -- we reproduce that so `global_lift`
    here reconciles against the ledger row's negative-lift table.
  - `local_lift` re-scores the SAME global OLS against the LOCALLY-refit
    scarcity model, so the ONLY thing that changes between the two lift columns
    is the scarcity model's calibration (global vs per-year) -- an apples-to-
    apples isolation of the global-fit cost. A per-year OLS `ols_local_mae`
    column is also shown as the "best achievable linear per cell" ceiling.

Reproduce:  python3 -m tools.ssp_refit_local_vs_global
"""
from __future__ import annotations

import numpy as np

from simulation import run_phase3b_recalibration as recal
from simulation import run_phase3b_regression as regr
from sim.price_engine import DISPATCHABLE_CAPACITY_MW, THERMAL_EFFICIENCY

CRISIS_YEARS = ("2021", "2022")


def _scarcity_arrays():
    """Reproduce fidelity_emitter's scarcity-model join: floor, x, ssp, year."""
    rows = recal._build_dataset()
    gas_price = np.array([r["gas_price"] for r in rows])
    demand_mw = np.array([r["demand_mw"] for r in rows])
    renewable_mw = np.array([r["renewable_mw"] for r in rows])
    ssp = np.array([r["ssp"] for r in rows])
    years = np.array([r["settlementDate"][:4] for r in rows])
    floor = gas_price / THERMAL_EFFICIENCY  # carbon_price=0, matching the landed calibration
    x = (demand_mw - renewable_mw) / DISPATCHABLE_CAPACITY_MW
    return floor, x, ssp, years


def _global_ols_per_year_mae():
    """The ledger's OLS baseline: ONE global 3-feature OLS sliced per year.
    Returns {year: mae}. Also returns per-year LOCAL OLS (best achievable
    linear in-cell) as a ceiling comparand."""
    rows = regr._build_dataset()
    years = np.array([r["settlementDate"][:4] for r in rows])
    ssp = np.array([r["ssp"] for r in rows])
    X = np.column_stack([
        np.ones(len(rows)),
        [r["gas_price"] for r in rows],
        [r["demand_mw"] for r in rows],
        [r["wind_mw"] for r in rows],
    ])
    global_fit = regr._fit_ols(rows)
    global_coeffs = np.array([
        global_fit["intercept"], global_fit["coef_gas_price"],
        global_fit["coef_demand_mw"], global_fit["coef_wind_mw"],
    ])
    global_resid = ssp - (X @ global_coeffs)

    global_by_year: dict[str, float] = {}
    local_by_year: dict[str, float] = {}
    for year in sorted(set(years)):
        mask = years == year
        global_by_year[year] = float(np.mean(np.abs(global_resid[mask])))
        # per-year (local) OLS: refit the 4 coeffs on this cell only
        coeffs, _, _, _ = np.linalg.lstsq(X[mask], ssp[mask], rcond=None)
        local_by_year[year] = float(np.mean(np.abs(ssp[mask] - X[mask] @ coeffs)))
    return global_by_year, local_by_year


def diagnose() -> dict:
    floor, x, ssp, years = _scarcity_arrays()
    x_tight = recal.SELECTED_X_TIGHT
    p = recal.SELECTED_SCARCITY_EXPONENT

    # The landed GLOBAL scarcity fit (the model on disk), scored per year.
    global_fit = recal._fit_form(floor, x, ssp, x_tight, p)
    global_pred = global_fit["predictions"]
    global_resid = ssp - global_pred

    ols_global_by_year, ols_local_by_year = _global_ols_per_year_mae()

    rows_out = []
    for year in sorted(set(years)):
        mask = years == year
        # LOCAL refit: SAME structural form, this year's data only, structure fixed.
        local = recal._fit_form(floor[mask], x[mask], ssp[mask], x_tight, p)
        model_global_mae = float(np.mean(np.abs(global_resid[mask])))
        model_local_mae = local["mae"]
        ols_mae = ols_global_by_year.get(year, float("nan"))

        rows_out.append({
            "year": year,
            "n": int(mask.sum()),
            "median_x": float(np.median(x[mask])),
            "model_global_mae": model_global_mae,
            "model_local_mae": model_local_mae,
            "ols_global_mae": ols_mae,
            "ols_local_mae": ols_local_by_year.get(year, float("nan")),
            # lift = best-naive - model  (positive = model beats naive)
            "global_lift": ols_mae - model_global_mae,
            "local_lift": ols_mae - model_local_mae,
            "a0_local": local["a0"],
            "a1_local": local["a1"],
            "a2_local": local["a2"],
        })
    return {
        "x_tight": x_tight,
        "p": p,
        "global_a0": global_fit["a0"],
        "global_a1": global_fit["a1"],
        "global_a2": global_fit["a2"],
        "per_year": rows_out,
    }


def main() -> None:
    d = diagnose()
    print(f"Structure held FIXED: x_tight={d['x_tight']}  p={d['p']}")
    print(f"Global fit (on disk): A0={d['global_a0']:.4f} A1={d['global_a1']:.4f} A2={d['global_a2']:.4f}")
    print()
    hdr = (f"{'yr':>4} {'n':>7} {'med_x':>6} {'gMAE':>7} {'lMAE':>7} "
           f"{'olsMAE':>7} {'gLift':>7} {'lLift':>7} {'flip':>5} "
           f"{'a0_loc':>7} {'a1_loc':>7}")
    print(hdr)
    n_neg_global = n_flipped = 0
    for r in d["per_year"]:
        tag = " *crisis" if r["year"] in CRISIS_YEARS else ""
        neg = r["global_lift"] < 0
        flipped = neg and r["local_lift"] >= 0
        n_neg_global += int(neg)
        n_flipped += int(flipped)
        flip = "FLIP" if flipped else ("neg" if neg else "")
        print(
            f"{r['year']:>4} {r['n']:>7} {r['median_x']:>6.3f} "
            f"{r['model_global_mae']:>7.2f} {r['model_local_mae']:>7.2f} "
            f"{r['ols_global_mae']:>7.2f} {r['global_lift']:>7.2f} "
            f"{r['local_lift']:>7.2f} {flip:>5} "
            f"{r['a0_local']:>7.3f} {r['a1_local']:>7.3f}{tag}"
        )
    print()
    print(f"global-fit negative-lift cells: {n_neg_global}")
    print(f"  ...flipped to non-negative by LOCAL refit (structure fixed): {n_flipped}")
    if n_neg_global:
        verdict = ("CONFIRM (global-fit staleness): local refit recovers the calm cells "
                   "-> scope-2 = time/regime-aware LINEAR calibration, not a new form."
                   if n_flipped >= max(1, n_neg_global - 1) else
                   "PARTIAL/REFUTE: some negative-lift cells survive a local refit "
                   "-> that residual is a FORM limit -> candidate R10 named simplification.")
        print(f"VERDICT: {verdict}")


if __name__ == "__main__":
    main()
