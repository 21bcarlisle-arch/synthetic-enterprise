"""Epoch-2 recalibration (2026-07-19) -- fix the ~10x SSP overestimate in
sim/price_engine.py's merit-order model.

Background: the original raw-ratio form (`gas_floor * (demand/renewable)^gamma`)
overestimated real Elexon SSP by ~10x even at the lowest gamma in its spec'd
range (docs/calibration/price-engine.md). This script fits the replacement
form's constants against the full real 2016-2025 window, BLIND to company P&L
(R12/R13 -- calibrated to real SSP only; the price engine is gated off in
every production phase, so this cannot perturb current results).

The replacement form (sim/price_engine.py, see its module docstring):
  P_gas_floor = (gas_price + carbon_price * EF_GAS_TCO2_PER_MWH_TH) / thermal_efficiency
  RD = demand_mw - renewable_generation_mw
  x  = RD / DISPATCHABLE_CAPACITY_MW
  multiplier = A0 + A1*x + A2 * max(0, x - X_TIGHT) ** SCARCITY_EXPONENT
  P_HH = P_gas_floor * multiplier

carbon_price_gbp_per_tonne is held at 0.0 throughout this calibration run --
no real historical UK-ETS/EU-ETS price series is wired in yet (R10
simplification, see sim/price_engine.py docstring); the carbon term is
structurally present and unit-tested but does not participate in this fit.

A0, A1, A2 are fit by ordinary least squares (closed-form, numpy.linalg.lstsq
-- sklearn is not installed) for each (X_TIGHT, SCARCITY_EXPONENT) grid point;
the grid point minimizing MAE is selected. DISPATCHABLE_CAPACITY_MW is held
fixed at its asserted physical value (~35,000 MW, GB dispatchable fleet;
R10 simplification) rather than grid-searched, per the recalibration brief.

Data-quality finding (fixed locally in this script, not in the shared
sim/generation_demand_history.py aggregators): sim/cache/elexon_agws_full.json
contains multiple revision records per (settlementDate, settlementPeriod,
psrType) -- Elexon republishes AGWS data as it's revised, and a handful of
periods have 500+ duplicate publishes. The existing
aggregate_renewable_generation()/aggregate_wind_generation() helpers naively
SUM every record matching a key, so those few heavily-revised periods produce
a renewable_generation_mw in the hundreds of thousands or millions of MW --
physically impossible (GB's entire wind+solar fleet is under 30 GW) and a
severe leverage outlier for any least-squares fit. This script dedupes to the
LATEST publishTime per (settlementDate, settlementPeriod, psrType) before
summing, which brings the max renewable figure down to a physically sane
~28,456 MW. This is a real data-quality bug in the shared aggregator (affects
1,572 of 471,453 keys, only 3 of which have >50 duplicate publishes) -- logged
here as a finding; not fixed in generation_demand_history.py itself, which is
out of this atom's file_scope.

Inputs, all real (Historical Ground Truth):
  - SSP (target): sim/cache/elexon_ssp_full.json
  - gas_price (feature): sim/gas_prices_history.load_nbp_history() (NBP daily, GBP/MWh)
  - demand_mw (feature): sim/cache/elexon_demand_full.json (Elexon /demand/outturn)
  - renewable_mw (feature): sim/cache/elexon_agws_full.json, Wind Onshore +
    Wind Offshore + Solar (deduplicated locally, see above)

Delegation note: hand-written (calibration/schema-defining work per the
Phase 1d delegation lesson).
"""

import json
from pathlib import Path

import numpy as np

from sim.cache_store import get_cached_prices
from sim.gas_prices_history import load_nbp_history
from sim.price_engine import DISPATCHABLE_CAPACITY_MW, THERMAL_EFFICIENCY

START_DATE = "2016-03-01"
END_DATE = "2025-06-07"

CACHE_DIR = Path("sim/cache")

RENEWABLE_PSR_TYPES = ("Wind Onshore", "Wind Offshore", "Solar")

# Grid search ranges for the two nonlinear-shape constants (A0/A1/A2 are
# fit in closed form for each grid point via least squares).
X_TIGHT_GRID = np.round(np.arange(-0.2, 1.42, 0.02), 2)
SCARCITY_EXPONENT_GRID = [1.5, 2.0, 2.5, 3.0]

# The grid point actually selected for sim/price_engine.py's hardcoded
# constants (see that module's docstring for the rationale: the pure
# MAE-argmin grid point pushes X_TIGHT out to ~1.28, right at the edge of
# the observed x range, which makes the convex kicker fire on well under
# 0.1% of periods -- degenerate, effectively indistinguishable from a plain
# linear fit. X_TIGHT=0.70 is within 0.03 GBP/MWh of the argmin MAE and
# keeps the scarcity term genuinely load-bearing across the tighter ~30-40%
# of periods, matching the "convex only when unusually tight" physical
# intent rather than only the top ~1% of samples).
SELECTED_X_TIGHT = 0.70
SELECTED_SCARCITY_EXPONENT = 2.0


def _dedup_latest_renewable_generation(agws_records: list[dict]) -> dict[tuple[str, int], float]:
    """Sum AGWS quantity across Wind Onshore + Wind Offshore + Solar for
    each (settlementDate, settlementPeriod), keeping only the LATEST
    publishTime per (date, period, psrType) -- see module docstring for why
    this differs from sim.generation_demand_history.aggregate_renewable_generation."""
    latest: dict[tuple[str, int, str], dict] = {}
    for record in agws_records:
        key = (record["settlementDate"], record["settlementPeriod"], record["psrType"])
        existing = latest.get(key)
        if existing is None or record["publishTime"] > existing["publishTime"]:
            latest[key] = record

    totals: dict[tuple[str, int], float] = {}
    for (date_str, period, psr_type), record in latest.items():
        if psr_type not in RENEWABLE_PSR_TYPES:
            continue
        key = (date_str, period)
        totals[key] = totals.get(key, 0.0) + record["quantity"]
    return totals


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
    renewable_lookup = _dedup_latest_renewable_generation(agws_records)

    gas_records = load_nbp_history()
    gas_lookup = {r["settlementDate"]: r["systemSellPrice"] for r in gas_records}

    rows = []
    for key, ssp in ssp_lookup.items():
        date_str, period = key
        if key not in demand_lookup or key not in renewable_lookup:
            continue
        if date_str not in gas_lookup:
            continue
        rows.append({
            "settlementDate": date_str,
            "settlementPeriod": period,
            "ssp": ssp,
            "gas_price": gas_lookup[date_str],
            "demand_mw": demand_lookup[key],
            "renewable_mw": renewable_lookup[key],
        })

    return rows


def _fit_form(
    floor: np.ndarray, x: np.ndarray, y: np.ndarray, x_tight: float, p: float
) -> dict:
    kick = np.maximum(0.0, x - x_tight) ** p
    design = np.column_stack([floor, floor * x, floor * kick])
    coeffs, _, _, _ = np.linalg.lstsq(design, y, rcond=None)
    predictions = design @ coeffs
    residuals = y - predictions

    mae = float(np.mean(np.abs(residuals)))
    rmse = float(np.sqrt(np.mean(residuals ** 2)))
    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot

    return {
        "x_tight": x_tight,
        "p": p,
        "a0": float(coeffs[0]),
        "a1": float(coeffs[1]),
        "a2": float(coeffs[2]),
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "predictions": predictions,
    }


def _grid_search(floor: np.ndarray, x: np.ndarray, y: np.ndarray) -> list[dict]:
    results = []
    for x_tight in X_TIGHT_GRID:
        for p in SCARCITY_EXPONENT_GRID:
            fit = _fit_form(floor, x, y, float(x_tight), p)
            fit_summary = {k: v for k, v in fit.items() if k != "predictions"}
            results.append(fit_summary)
    return sorted(results, key=lambda r: r["mae"])


def _distribution_stats(values: np.ndarray) -> dict:
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "p95": float(np.percentile(values, 95)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
    }


def main():
    print("=== Epoch-2 Recalibration: sim/price_engine.py residual-demand scarcity form ===\n")

    rows = _build_dataset()
    print(f"{len(rows):,} settlement periods with full data ({START_DATE}..{END_DATE})\n")

    gas_price = np.array([r["gas_price"] for r in rows])
    demand_mw = np.array([r["demand_mw"] for r in rows])
    renewable_mw = np.array([r["renewable_mw"] for r in rows])
    ssp = np.array([r["ssp"] for r in rows])
    dates = np.array([r["settlementDate"] for r in rows])

    floor = gas_price / THERMAL_EFFICIENCY  # carbon_price = 0 throughout this calibration
    residual_demand_mw = demand_mw - renewable_mw
    x = residual_demand_mw / DISPATCHABLE_CAPACITY_MW

    print("--- Grid search (X_TIGHT x SCARCITY_EXPONENT), top 10 by MAE ---")
    grid_results = _grid_search(floor, x, ssp)
    for r in grid_results[:10]:
        print(f"  x_tight={r['x_tight']:.2f} p={r['p']:.1f} "
              f"MAE=£{r['mae']:.3f} R2={r['r2']:.4f} "
              f"a=({r['a0']:.4f},{r['a1']:.4f},{r['a2']:.4g})")

    print(f"\nArgmin-MAE grid point: x_tight={grid_results[0]['x_tight']:.2f} "
          f"p={grid_results[0]['p']:.1f} (MAE=£{grid_results[0]['mae']:.3f})")
    print("This is near the edge of the observed x range and makes the convex\n"
          "kicker fire on <0.1% of periods -- selected constants instead favour\n"
          "a moderate threshold that keeps the scarcity term genuinely active\n"
          "(see this module's SELECTED_X_TIGHT/SELECTED_SCARCITY_EXPONENT).\n")

    selected = _fit_form(floor, x, ssp, SELECTED_X_TIGHT, SELECTED_SCARCITY_EXPONENT)
    predictions = selected.pop("predictions")

    print(f"--- Selected fit: x_tight={SELECTED_X_TIGHT}, p={SELECTED_SCARCITY_EXPONENT} ---")
    print(f"  A0 = {selected['a0']:.6f}")
    print(f"  A1 = {selected['a1']:.6f}")
    print(f"  A2 = {selected['a2']:.6f}")
    print(f"  MAE  = £{selected['mae']:.3f}/MWh")
    print(f"  RMSE = £{selected['rmse']:.3f}/MWh")
    print(f"  R^2  = {selected['r2']:.4f}\n")

    actual_stats = _distribution_stats(ssp)
    pred_stats = _distribution_stats(predictions)
    print("--- Distribution match (full window) ---")
    print(f"  {'':>8} {'mean':>9} {'median':>9} {'p95':>9} {'min':>10} {'max':>10}")
    print(f"  {'actual':>8} {actual_stats['mean']:>9.2f} {actual_stats['median']:>9.2f} "
          f"{actual_stats['p95']:>9.2f} {actual_stats['min']:>10.2f} {actual_stats['max']:>10.2f}")
    print(f"  {'model':>8} {pred_stats['mean']:>9.2f} {pred_stats['median']:>9.2f} "
          f"{pred_stats['p95']:>9.2f} {pred_stats['min']:>10.2f} {pred_stats['max']:>10.2f}\n")

    naive_mae = float(np.mean(np.abs(floor - ssp)))
    naive_rmse = float(np.sqrt(np.mean((floor - ssp) ** 2)))
    ss_tot = float(np.sum((ssp - np.mean(ssp)) ** 2))
    naive_r2 = 1.0 - float(np.sum((floor - ssp) ** 2)) / ss_tot
    print("--- Lift over naive gas-floor-alone baseline ---")
    print(f"  naive (gas floor only): MAE=£{naive_mae:.3f} RMSE=£{naive_rmse:.3f} R2={naive_r2:.4f}")
    print(f"  model (recalibrated):   MAE=£{selected['mae']:.3f} RMSE=£{selected['rmse']:.3f} R2={selected['r2']:.4f}")
    print(f"  MAE reduction: £{naive_mae - selected['mae']:.3f} "
          f"({(1 - selected['mae'] / naive_mae) * 100:.1f}% better)\n")

    print("--- Per-year table (globally-fit constants applied within each year) ---")
    years = np.array([d[:4] for d in dates])
    print(f"  {'year':>6} {'n':>8} {'ssp_mean':>9} {'pred_mean':>10} {'MAE':>8} {'R2':>7}")
    per_year = {}
    for year in sorted(set(years)):
        mask = years == year
        resid = ssp[mask] - predictions[mask]
        year_mae = float(np.mean(np.abs(resid)))
        year_ss_tot = float(np.sum((ssp[mask] - ssp[mask].mean()) ** 2))
        year_r2 = 1.0 - float(np.sum(resid ** 2)) / year_ss_tot if year_ss_tot > 0 else float("nan")
        per_year[year] = {
            "n": int(mask.sum()),
            "ssp_mean": float(ssp[mask].mean()),
            "pred_mean": float(predictions[mask].mean()),
            "mae": year_mae,
            "r2": year_r2,
        }
        print(f"  {year:>6} {per_year[year]['n']:>8,} {per_year[year]['ssp_mean']:>9.2f} "
              f"{per_year[year]['pred_mean']:>10.2f} {per_year[year]['mae']:>8.2f} {per_year[year]['r2']:>7.4f}")

    frac_negative_model = float(np.mean(predictions < 0))
    frac_negative_actual = float(np.mean(ssp < 0))
    print(f"\n  Negative-price capability: model produces negative prices in "
          f"{frac_negative_model * 100:.3f}% of periods (real: {frac_negative_actual * 100:.3f}%)")

    return {
        "n": len(rows),
        "selected": selected,
        "grid_results": grid_results,
        "actual_stats": actual_stats,
        "pred_stats": pred_stats,
        "naive_mae": naive_mae,
        "naive_r2": naive_r2,
        "per_year": per_year,
        "frac_negative_model": frac_negative_model,
        "frac_negative_actual": frac_negative_actual,
    }


if __name__ == "__main__":
    main()
