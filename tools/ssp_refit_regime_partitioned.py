"""Test D (SSP negative-lift diagnosis) -- does the crisis-vs-calm price-REGIME
partition (the one Test C REDIRECTED part (a) toward) actually recover the
negative-lift cells, where the DUKES capacity-era partition did NOT?

Diagnostic ONLY -- the same discipline as its three siblings
(`tools/ssp_scarcity_dwell_fraction.py` = Test A, `tools/ssp_refit_local_vs_global.py`
= Test B, `tools/ssp_refit_era_partitioned.py` = Test C). It re-uses the landed
calibration machinery (`simulation.run_phase3b_recalibration._fit_form`) and the
sibling tools' dataset join purely as libraries; it changes NO calibration constant
on disk and reads NO company P&L, so it is R13-clean (fidelity-to-reality, decided
blind to company results) and R12-clean (it measures which partition a recalibration
would need, it does not tune any output toward a benchmark).

Why this test exists (it closes the exact gap Test C left open):
    Test C refit the SAME form PER ERA on the externally-grounded DUKES fossil-
    capacity 3-era partition (A 2016-18 / B 2019-22 / C 2023-25) and found it
    MISALIGNED: it recovered only 2 of 6 negative-lift cells and WORSENED three
    (2019/2020/2021) because Era B pools the CALM 2019/2020 years with the CRISIS
    2021/2022 years -- one pooled Era-B line takes a large scarcity kicker
    (A2=4.97) to price the crisis and that crisis-tuned line is wrong for calm
    2019/2020. Test C's conclusion: "part (a) must key A0/A1 on a price-REGIME /
    x-distribution partition, NOT the capacity eras ... the ledger already tags
    each cell's regime -- so the regime split is itself externally/structurally
    grounded, not lift-table-derived (R12-safe)."

    But Test C never MEASURED that redirected partition -- it asserted the regime
    split would work, the same untested-leap (R4) it had just criticised the
    capacity-era grounding for. This test measures it: refit the SAME form on a
    TWO-pool crisis-vs-calm regime partition (crisis = {2021, 2022}, the ledger's
    own regime tag; calm = every other year) and re-measure per-cell lift.

    The decision-relevant question the deferred part-(a) build rests on:
        Does a crisis-vs-calm regime partition recover the calm negative-lift
        cells WITHOUT the "crisis poisons its era-mate" harm the capacity eras
        showed? If YES -> the regime partition is the sound calibration key for
        part (a), de-risked and ready for a deliberate R13 pass. If some calm
        cells STILL survive -> that residual is a genuine FORM limit no partition
        can close, already bounded by the R10 named simplification part (b)
        registered -- and part (a)'s achievable scope shrinks accordingly.

Partition grounding (R12-safe -- NOT derived from the lift table):
    The crisis tag comes from the ledger's own `regime` field (gas-crisis 2021/22),
    which is a market-history fact (the 2021-22 European gas crisis), not a choice
    made to flip a lift cell. Calm = the complement. Two pools, not ten -- this is
    a DEPLOYABLE partition (a real recalibration keys A0/A1 on the observable
    regime), unlike Test B's per-year upper bound.

Fairness note (identical baselines to Tests B/C, so the columns reconcile):
  - `ols_global_mae` and `global_lift` reproduce the ledger row's per-cell OLS
    baseline and negative-lift table exactly (via the sibling tool's helpers).
  - `regime_lift` re-scores the SAME global OLS against the crisis-vs-calm-refit
    scarcity model; `era_lift`/`local_lift` (Tests C/B) re-score it against the
    per-era / per-year refits. The ONLY thing changing across the lift columns is
    the scarcity model's calibration partition -- an apples-to-apples isolation.
  - DEGREES OF FREEDOM: this refits A0/A1/A2 per regime-pool (matching Tests B/C).
    The part-(a) proposal is narrower (A0/A1 only, A2 fixed), so this is an UPPER
    BOUND: any cell this fuller refit fails to recover, the narrower proposal fails
    too.

Reproduce:  python3 -m tools.ssp_refit_regime_partitioned
"""
from __future__ import annotations

import numpy as np

from simulation import run_phase3b_recalibration as recal
from tools.ssp_refit_local_vs_global import (
    _scarcity_arrays,
    _global_ols_per_year_mae,
    CRISIS_YEARS,
)

# Crisis-vs-calm price-REGIME partition. `CRISIS_YEARS` = the ledger's own regime
# tag (the 2021-22 European gas crisis -- a market-history fact, not a lift-table
# choice). "calm" = the complement. Two deployable pools.
def _regime_of(year: str) -> str:
    return "crisis_2021_2022" if year in CRISIS_YEARS else "calm"


def diagnose() -> dict:
    floor, x, ssp, years = _scarcity_arrays()
    x_tight = recal.SELECTED_X_TIGHT
    p = recal.SELECTED_SCARCITY_EXPONENT

    # Global fit on disk (the model), scored per year -> reconciles to the ledger.
    global_fit = recal._fit_form(floor, x, ssp, x_tight, p)
    global_resid = ssp - global_fit["predictions"]

    ols_global_by_year, _ = _global_ols_per_year_mae()

    # Fit the SAME form on each regime pool (structure x_tight/p held fixed).
    regimes = sorted({_regime_of(y) for y in set(years)})
    regime_coeffs: dict[str, dict] = {}
    for regime in regimes:
        m = np.array([_regime_of(y) == regime for y in years])
        fit = recal._fit_form(floor[m], x[m], ssp[m], x_tight, p)
        regime_coeffs[regime] = {"a0": fit["a0"], "a1": fit["a1"], "a2": fit["a2"], "n": int(m.sum())}

    rows_out = []
    for year in sorted(set(years)):
        m = years == year
        regime = _regime_of(year)
        c = regime_coeffs[regime]
        # Apply THIS YEAR's regime coefficients (the deployable per-regime calibration).
        kick = np.maximum(0.0, x[m] - x_tight) ** p
        regime_pred = c["a0"] * floor[m] + c["a1"] * floor[m] * x[m] + c["a2"] * floor[m] * kick
        regime_mae = float(np.mean(np.abs(ssp[m] - regime_pred)))

        # Per-year (local) refit = Test B upper bound, recomputed for the same table.
        local = recal._fit_form(floor[m], x[m], ssp[m], x_tight, p)

        model_global_mae = float(np.mean(np.abs(global_resid[m])))
        ols_mae = ols_global_by_year.get(year, float("nan"))
        rows_out.append({
            "year": year,
            "regime": regime,
            "n": int(m.sum()),
            "median_x": float(np.median(x[m])),
            "model_global_mae": model_global_mae,
            "model_regime_mae": regime_mae,
            "model_local_mae": local["mae"],
            "ols_global_mae": ols_mae,
            "global_lift": ols_mae - model_global_mae,
            "regime_lift": ols_mae - regime_mae,
            "local_lift": ols_mae - local["mae"],
        })
    return {"x_tight": x_tight, "p": p, "regime_coeffs": regime_coeffs, "per_year": rows_out}


def main() -> None:
    d = diagnose()
    print(f"Structure held FIXED: x_tight={d['x_tight']}  p={d['p']}")
    print("Crisis-vs-calm price-REGIME partition (ledger regime tag, blind to the lift table):")
    for regime, c in d["regime_coeffs"].items():
        print(f"  {regime:>16}: n={c['n']:>6}  A0={c['a0']:.3f}  A1={c['a1']:.3f}  A2={c['a2']:.3f}")
    print()
    hdr = (f"{'yr':>4} {'regime':>16} {'med_x':>6} {'gMAE':>7} {'regMAE':>7} {'lMAE':>7} "
           f"{'olsMAE':>7} {'gLift':>7} {'regLift':>8} {'lLift':>7}  verdict")
    print(hdr)
    n_neg = n_regime_flip = n_local_flip = n_regime_worse = 0
    for r in d["per_year"]:
        neg = r["global_lift"] < 0
        regime_flip = neg and r["regime_lift"] >= 0
        local_flip = neg and r["local_lift"] >= 0
        regime_worse = neg and r["regime_lift"] < r["global_lift"]  # regime partition HURT this cell
        n_neg += int(neg)
        n_regime_flip += int(regime_flip)
        n_local_flip += int(local_flip)
        n_regime_worse += int(regime_worse)
        tag = " *crisis" if r["year"] in CRISIS_YEARS else ""
        if regime_flip:
            verdict = "REGIME-FLIP"
        elif neg and regime_worse:
            verdict = "regime-WORSENS"
        elif neg:
            verdict = "regime-neg"
        else:
            verdict = ""
        if neg and local_flip != regime_flip:
            verdict += " (per-yr flips)" if local_flip else " (per-yr-neg too)"
        print(
            f"{r['year']:>4} {r['regime']:>16} {r['median_x']:>6.3f} "
            f"{r['model_global_mae']:>7.2f} {r['model_regime_mae']:>7.2f} "
            f"{r['model_local_mae']:>7.2f} {r['ols_global_mae']:>7.2f} "
            f"{r['global_lift']:>7.2f} {r['regime_lift']:>8.2f} {r['local_lift']:>7.2f}  {verdict}{tag}"
        )
    print()
    print(f"global negative-lift cells: {n_neg}")
    print(f"  ...flipped non-negative by the crisis-vs-calm REGIME refit: {n_regime_flip}")
    print(f"  ...flipped non-negative by the per-YEAR refit (Test B upper bound): {n_local_flip}")
    print(f"  ...cells the REGIME partition made WORSE than the global fit: {n_regime_worse}")
    print()
    if n_neg:
        if n_regime_flip >= n_local_flip and n_regime_worse == 0:
            verdict = ("CONFIRM: the crisis-vs-calm regime partition is a sound calibration "
                       "partition -- it recovers the cells the DUKES eras could not, without "
                       "harming any -> part (a) keys A0/A1 on this regime split, de-risked.")
        elif n_regime_worse == 0 and n_regime_flip >= 1:
            verdict = ("PARTIAL: the regime partition recovers some cells without harming any, "
                       "but leaves a residual the R10 named simplification (part b) already "
                       "bounds -> part (a)'s achievable scope is the flipped cells only.")
        else:
            verdict = ("REFUTE: even a crisis-vs-calm regime partition fails to recover / "
                       "worsens cells -> the residual is a deeper FORM limit; part (a)'s "
                       "recalibration cannot close it, the R10 simplification (part b) is the "
                       "load-bearing close.")
        print(f"VERDICT: {verdict}")


if __name__ == "__main__":
    main()
