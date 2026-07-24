"""Test C (SSP negative-lift diagnosis) -- does the EXTERNALLY-GROUNDED 3-era
partition actually recover the negative-lift cells, or does binning the crisis
years with their calm era-mates defeat it?

Diagnostic ONLY -- the same discipline as its two siblings
(`tools/ssp_scarcity_dwell_fraction.py` = Test A, `tools/ssp_refit_local_vs_global.py`
= Test B). It re-uses the landed calibration machinery
(`simulation.run_phase3b_recalibration._fit_form`) and the sibling tool's dataset
join purely as libraries; it changes NO calibration constant on disk and reads NO
company P&L, so it is R13-clean (fidelity-to-reality, decided blind to company
results) and R12-clean (it measures which partition a recalibration would need, it
does not tune any output toward a benchmark).

Why this test exists (the gap between grounding and build):
    Test B refit the SAME structural form PER YEAR (10 separate fits) and found
    ~half the negative-lift cells (2019/2023/2024) flip non-negative -- but a
    per-year refit is an UPPER BOUND: it is not a deployable calibration (you
    cannot fit 2025 on 2025's own future data at prediction time). The deferred
    part-(a) baseline recalibration would instead condition A0/A1 on an EXTERNALLY
    GROUNDED era partition. The market_research grounding
    (docs/market_research/ssp_dispatchable_fleet_renewables_era_boundaries_2026-07-24.md)
    established, blind to the lift table, a DUKES-fossil-capacity 3-era partition:
        Era A 2016-2018 (fossil ~50 GW, coal material)
        Era B 2019-2022 (fossil ~42-44 GW, post-major-coal-closure plateau)
        Era C 2023-2025 (fossil ~36-40 GW, coal exit completed)

    The decision-relevant question the deferred build rests on:
        Does refitting the form PER ERA (3 fits) -- the deployable structure --
        recover the same cells the per-year refit did? Or does Era B lumping the
        CALM 2019/2020 years with the CRISIS 2021/2022 years poison the calm
        cells (one pooled Era-B line cannot serve both a calm and a crisis year)?

    If the era partition recovers the cells -> the DUKES capacity eras are a sound
    calibration partition for part (a). If it does NOT (or worse, WORSENS a calm
    cell by binning it with the crisis) -> the capacity-era partition is MISALIGNED
    with the calibration need, and part (a) must key A0/A1 on a price-REGIME /
    x-distribution partition instead. Measuring this now, diagnostic-only, stops the
    deferred baseline pass building on a mis-grounded partition.

Fairness note (identical baselines to Test B, so the columns reconcile):
  - `ols_global_mae` and `global_lift` reproduce the ledger row's per-cell OLS
    baseline and negative-lift table exactly (via the sibling tool's helpers).
  - `era_lift` re-scores the SAME global OLS against the PER-ERA-refit scarcity
    model; `local_lift` (Test B) re-scores it against the PER-YEAR refit. The only
    thing changing across the three lift columns is the scarcity model's
    calibration granularity (global / per-era / per-year) -- an apples-to-apples
    isolation of what an era-partitioned recalibration can and cannot recover.
  - NOTE ON DEGREES OF FREEDOM: this refits A0/A1/A2 per era (matching Test B's
    per-year refit). The part-(a) proposal is narrower still -- A0/A1 only, holding
    A2 fixed. So the per-era A0/A1/A2 refit here is an UPPER BOUND on what an
    A0/A1-only era recalibration could achieve: any cell this fuller refit fails to
    recover, the narrower proposal fails too.

Reproduce:  python3 -m tools.ssp_refit_era_partitioned
"""
from __future__ import annotations

import numpy as np

from simulation import run_phase3b_recalibration as recal
from tools.ssp_refit_local_vs_global import (
    _scarcity_arrays,
    _global_ols_per_year_mae,
    CRISIS_YEARS,
)

# Externally-grounded DUKES fossil-capacity 3-era partition (blind to the lift
# table). Source: docs/market_research/ssp_dispatchable_fleet_renewables_era_boundaries_2026-07-24.md
ERAS: dict[str, tuple[str, ...]] = {
    "A_2016_2018": ("2016", "2017", "2018"),
    "B_2019_2022": ("2019", "2020", "2021", "2022"),
    "C_2023_2025": ("2023", "2024", "2025"),
}


def _era_of(year: str) -> str:
    for era, years in ERAS.items():
        if year in years:
            return era
    raise KeyError(f"year {year} outside the grounded era partition {list(ERAS)}")


def diagnose() -> dict:
    floor, x, ssp, years = _scarcity_arrays()
    x_tight = recal.SELECTED_X_TIGHT
    p = recal.SELECTED_SCARCITY_EXPONENT

    # Global fit on disk (the model), scored per year -> reconciles to the ledger.
    global_fit = recal._fit_form(floor, x, ssp, x_tight, p)
    global_resid = ssp - global_fit["predictions"]

    ols_global_by_year, ols_local_by_year = _global_ols_per_year_mae()

    # Fit the SAME form on each era's pooled data (structure x_tight/p held fixed).
    era_coeffs: dict[str, dict] = {}
    for era, era_years in ERAS.items():
        m = np.isin(years, era_years)
        fit = recal._fit_form(floor[m], x[m], ssp[m], x_tight, p)
        era_coeffs[era] = {"a0": fit["a0"], "a1": fit["a1"], "a2": fit["a2"], "n": int(m.sum())}

    rows_out = []
    for year in sorted(set(years)):
        m = years == year
        era = _era_of(year)
        c = era_coeffs[era]
        # Apply THIS YEAR's era coefficients (the deployable per-era calibration).
        kick = np.maximum(0.0, x[m] - x_tight) ** p
        era_pred = c["a0"] * floor[m] + c["a1"] * floor[m] * x[m] + c["a2"] * floor[m] * kick
        era_mae = float(np.mean(np.abs(ssp[m] - era_pred)))

        # Per-year (local) refit = Test B upper bound, recomputed for the same table.
        local = recal._fit_form(floor[m], x[m], ssp[m], x_tight, p)

        model_global_mae = float(np.mean(np.abs(global_resid[m])))
        ols_mae = ols_global_by_year.get(year, float("nan"))
        rows_out.append({
            "year": year,
            "era": era,
            "n": int(m.sum()),
            "median_x": float(np.median(x[m])),
            "model_global_mae": model_global_mae,
            "model_era_mae": era_mae,
            "model_local_mae": local["mae"],
            "ols_global_mae": ols_mae,
            "global_lift": ols_mae - model_global_mae,
            "era_lift": ols_mae - era_mae,
            "local_lift": ols_mae - local["mae"],
        })
    return {"x_tight": x_tight, "p": p, "era_coeffs": era_coeffs, "per_year": rows_out}


def main() -> None:
    d = diagnose()
    print(f"Structure held FIXED: x_tight={d['x_tight']}  p={d['p']}")
    print("Externally-grounded DUKES 3-era partition (blind to the lift table):")
    for era, c in d["era_coeffs"].items():
        print(f"  {era}: n={c['n']:>6}  A0={c['a0']:.3f}  A1={c['a1']:.3f}  A2={c['a2']:.3f}")
    print()
    hdr = (f"{'yr':>4} {'era':>11} {'med_x':>6} {'gMAE':>7} {'eraMAE':>7} {'lMAE':>7} "
           f"{'olsMAE':>7} {'gLift':>7} {'eraLift':>8} {'lLift':>7}  verdict")
    print(hdr)
    n_neg = n_era_flip = n_local_flip = n_era_worse = 0
    for r in d["per_year"]:
        neg = r["global_lift"] < 0
        era_flip = neg and r["era_lift"] >= 0
        local_flip = neg and r["local_lift"] >= 0
        era_worse = neg and r["era_lift"] < r["global_lift"]  # era partition HURT this cell
        n_neg += int(neg)
        n_era_flip += int(era_flip)
        n_local_flip += int(local_flip)
        n_era_worse += int(era_worse)
        tag = " *crisis" if r["year"] in CRISIS_YEARS else ""
        if era_flip:
            verdict = "ERA-FLIP"
        elif neg and era_worse:
            verdict = "era-WORSENS"
        elif neg:
            verdict = "era-neg"
        else:
            verdict = ""
        if neg and local_flip != era_flip:
            verdict += " (per-yr flips)" if local_flip else " (per-yr-neg too)"
        print(
            f"{r['year']:>4} {r['era']:>11} {r['median_x']:>6.3f} "
            f"{r['model_global_mae']:>7.2f} {r['model_era_mae']:>7.2f} "
            f"{r['model_local_mae']:>7.2f} {r['ols_global_mae']:>7.2f} "
            f"{r['global_lift']:>7.2f} {r['era_lift']:>8.2f} {r['local_lift']:>7.2f}  {verdict}{tag}"
        )
    print()
    print(f"global negative-lift cells: {n_neg}")
    print(f"  ...flipped non-negative by the DUKES-ERA refit: {n_era_flip}")
    print(f"  ...flipped non-negative by the per-YEAR refit (Test B upper bound): {n_local_flip}")
    print(f"  ...cells the ERA partition made WORSE than the global fit: {n_era_worse}")
    print()
    if n_neg:
        if n_era_flip >= n_local_flip and n_era_worse == 0:
            verdict = ("CONFIRM: the DUKES capacity-era partition is a sound calibration "
                       "partition -- it recovers the cells without harming any.")
        else:
            verdict = (
                "MISALIGNED: the DUKES fossil-capacity era partition recovers FEWER cells "
                "than a per-year refit and/or WORSENS a calm cell by binning it with its "
                "crisis era-mates (Era B 2019-22 pools calm 2019/2020 with crisis 2021/2022). "
                "-> part (a) must key A0/A1 on a price-REGIME / x-distribution partition, NOT "
                "the capacity eras. The grounding is sound; the capacity-plateau boundaries are "
                "simply not the calibration-relevant ones."
            )
        print(f"VERDICT: {verdict}")


if __name__ == "__main__":
    main()
