"""Phase 3b (redesign) — statistical regression price model.

The spec'd merit-order physics formula (sim/price_engine.py) was calibrated
against real 2019/2022 SSP and found not to fit (see
docs/calibration/price-engine.md) — that module is deferred to Regime 3.

This script implements the replacement Phase 3b deliverable: an ordinary
least-squares regression of real Elexon System Sell Price (SSP) against
gas price, national demand, and wind generation, fit on the full
2016-03-01..2025-06-07 window (the AGWS/demand data-availability window).

Inputs, all real (Historical Ground Truth):
  - SSP (target): sim/cache/elexon_ssp_full.json
  - gas_price (feature): sim/gas_prices_history.load_nbp_history() (NBP daily £/MWh)
  - demand_mw (feature): sim/cache/elexon_demand_full.json (Elexon /demand/outturn)
  - wind_mw (feature): sim/cache/elexon_agws_full.json, Wind Onshore + Wind
    Offshore only (sim.generation_demand_history.aggregate_wind_generation) —
    solar excluded per the user's "wind generation" framing.

sklearn is not installed in this environment; OLS is fit via
numpy.linalg.lstsq (closed-form normal-equation solve), with MAE and R^2
computed manually.

Delegation note: hand-written (orchestration-adjacent, schema-defining work
per the Phase 1d delegation lesson).
"""

import json
from pathlib import Path

import numpy as np

from sim.cache_store import get_cached_prices
from sim.gas_prices_history import load_nbp_history
from sim.generation_demand_history import aggregate_wind_generation

START_DATE = "2016-03-01"
END_DATE = "2025-06-07"

CACHE_DIR = Path("sim/cache")


def _build_dataset() -> list[dict]:
    ssp_records = get_cached_prices(START_DATE, END_DATE)
    ssp_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["systemSellPrice"]
        for r in ssp_records
    }

    demand_records = json.loads((CACHE_DIR / "elexon_demand_full.json").read_text())
    demand_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["initialDemandOutturn"]
        for r in demand_records
    }

    agws_records = json.loads((CACHE_DIR / "elexon_agws_full.json").read_text())
    wind_lookup = aggregate_wind_generation(agws_records)

    gas_records = load_nbp_history()
    gas_lookup = {r["settlementDate"]: r["systemSellPrice"] for r in gas_records}

    rows = []
    for key, ssp in ssp_lookup.items():
        date_str, period = key
        if key not in demand_lookup or key not in wind_lookup:
            continue
        if date_str not in gas_lookup:
            continue
        rows.append({
            "settlementDate": date_str,
            "settlementPeriod": period,
            "ssp": ssp,
            "gas_price": gas_lookup[date_str],
            "demand_mw": demand_lookup[key],
            "wind_mw": wind_lookup[key],
        })

    return rows


def _fit_ols(rows: list[dict]) -> dict:
    y = np.array([r["ssp"] for r in rows])
    X = np.column_stack([
        np.ones(len(rows)),
        [r["gas_price"] for r in rows],
        [r["demand_mw"] for r in rows],
        [r["wind_mw"] for r in rows],
    ])

    coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    predictions = X @ coeffs
    residuals = y - predictions

    mae = float(np.mean(np.abs(residuals)))
    rmse = float(np.sqrt(np.mean(residuals ** 2)))
    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot

    return {
        "n": len(rows),
        "intercept": float(coeffs[0]),
        "coef_gas_price": float(coeffs[1]),
        "coef_demand_mw": float(coeffs[2]),
        "coef_wind_mw": float(coeffs[3]),
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "actual_mean": float(np.mean(y)),
        "actual_std": float(np.std(y)),
    }


def _fit_ols_by_year(rows: list[dict]) -> dict[str, dict]:
    by_year: dict[str, list[dict]] = {}
    for row in rows:
        year = row["settlementDate"][:4]
        by_year.setdefault(year, []).append(row)
    return {year: _fit_ols(year_rows) for year, year_rows in sorted(by_year.items())}


def main():
    print("=== Phase 3b (redesign) — SSP Regression Model ===\n")

    rows = _build_dataset()
    print(f"{len(rows):,} settlement periods with full data ({START_DATE}..{END_DATE})\n")

    overall = _fit_ols(rows)
    print("--- Full-window fit ---")
    print(f"  n = {overall['n']:,}")
    print(f"  SSP: mean=£{overall['actual_mean']:.2f}/MWh, std=£{overall['actual_std']:.2f}/MWh")
    print(f"  intercept       = {overall['intercept']:.4f}")
    print(f"  coef gas_price  = {overall['coef_gas_price']:.4f}")
    print(f"  coef demand_mw  = {overall['coef_demand_mw']:.6f}")
    print(f"  coef wind_mw    = {overall['coef_wind_mw']:.6f}")
    print(f"  MAE  = £{overall['mae']:.2f}/MWh")
    print(f"  RMSE = £{overall['rmse']:.2f}/MWh")
    print(f"  R^2  = {overall['r2']:.4f}\n")

    print("--- Per-year fit (same coefficients applied year by year would differ;")
    print("    this re-fits per year to show how fit quality varies by regime) ---")
    by_year = _fit_ols_by_year(rows)
    print(f"  {'year':>6} {'n':>8} {'mean £':>8} {'MAE £':>8} {'RMSE £':>8} {'R2':>7}")
    for year, fit in by_year.items():
        print(f"  {year:>6} {fit['n']:>8,} {fit['actual_mean']:>8.2f} "
              f"{fit['mae']:>8.2f} {fit['rmse']:>8.2f} {fit['r2']:>7.4f}")

    return overall, by_year


if __name__ == "__main__":
    main()
