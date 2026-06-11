"""Phase 3b — wholesale price model calibration run.

Compares sim.price_engine.synthetic_price() against real Elexon SSP for two
sample years — 2019 (calm) and 2022 (gas-crisis) — across a scan of gamma
values in [1.5, 2.5], reporting error distribution and bias per gamma so the
best-fit gamma (and how well it generalises across regimes) can be assessed.

Inputs, all real (Historical Ground Truth):
  - SSP: sim/cache/elexon_ssp_full.json (pre-fetched Elexon system prices)
  - demand_mw: Elexon /demand/outturn (initialDemandOutturn)
  - renewable_generation_mw: Elexon AGWS (Wind Onshore + Wind Offshore + Solar, summed)
  - gas_price: sim/gas_data/nbp_sap.csv (NBP SAP proxy, daily)

Periods where renewable_generation_mw <= 0 are skipped (system_margin_price
requires a positive denominator) — logged as a count per year.

This is a sample-year calibration, not the full 2016-2025 run (deliverable
2 in MASTER_BACKLOG's Phase 3b spec asks for full-window calibration once
the model shape is validated). See docs/calibration/price-engine.md for the
full report and recommended next steps.

Delegation note: hand-written (orchestration-adjacent, per protocol).
"""

import statistics

from sim.cache_store import get_cached_prices
from sim.gas_prices_history import load_nbp_history
from sim.generation_demand_history import (
    aggregate_renewable_generation,
    get_demand_outturn_range,
    get_wind_solar_generation_range,
)
from sim.price_engine import gas_floor_price, system_margin_price

CALIBRATION_YEARS = ["2019", "2022"]
GAMMA_VALUES = [1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5]


def _build_year_dataset(year: str) -> tuple[list[dict], int]:
    """Returns (rows, skipped_zero_renewable_count) for one calendar year,
    where each row is {settlementDate, settlementPeriod, ssp, demand_mw,
    renewable_mw, gas_price}."""
    start, end = f"{year}-01-01", f"{year}-12-31"

    ssp_records = get_cached_prices(start, end)
    ssp_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["systemSellPrice"]
        for r in ssp_records
    }

    demand_records = get_demand_outturn_range(start, end)
    demand_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["initialDemandOutturn"]
        for r in demand_records
    }

    wind_solar_records = get_wind_solar_generation_range(start, end)
    renewable_lookup = aggregate_renewable_generation(wind_solar_records)

    gas_records = load_nbp_history()
    gas_lookup = {r["settlementDate"]: r["systemSellPrice"] for r in gas_records}

    rows = []
    skipped_zero_renewable = 0
    for key, ssp in ssp_lookup.items():
        date_str, period = key
        if key not in demand_lookup or key not in renewable_lookup:
            continue
        if date_str not in gas_lookup:
            continue
        renewable_mw = renewable_lookup[key]
        if renewable_mw <= 0:
            skipped_zero_renewable += 1
            continue
        rows.append({
            "settlementDate": date_str,
            "settlementPeriod": period,
            "ssp": ssp,
            "demand_mw": demand_lookup[key],
            "renewable_mw": renewable_mw,
            "gas_price": gas_lookup[date_str],
        })

    return rows, skipped_zero_renewable


def _calibrate_gamma(rows: list[dict], gamma: float) -> dict:
    errors = []
    actuals = []
    synthetics = []
    for row in rows:
        floor = gas_floor_price(row["gas_price"])
        synthetic = system_margin_price(floor, row["demand_mw"], row["renewable_mw"], gamma)
        errors.append(synthetic - row["ssp"])
        actuals.append(row["ssp"])
        synthetics.append(synthetic)

    mae = statistics.mean(abs(e) for e in errors)
    bias = statistics.mean(errors)
    rmse = (statistics.mean(e ** 2 for e in errors)) ** 0.5
    correlation = statistics.correlation(actuals, synthetics) if len(rows) > 1 else float("nan")

    return {"gamma": gamma, "mae": mae, "bias": bias, "rmse": rmse, "correlation": correlation}


def main():
    print("=== Phase 3b — Price Engine Calibration (sample years) ===\n")

    all_results: dict[str, list[dict]] = {}
    for year in CALIBRATION_YEARS:
        print(f"--- {year} ---")
        rows, skipped = _build_year_dataset(year)
        print(f"  {len(rows):,} settlement periods with full data "
              f"(skipped {skipped:,} zero-renewable periods)")
        actual_mean = statistics.mean(r["ssp"] for r in rows)
        print(f"  Actual SSP mean: £{actual_mean:.2f}/MWh\n")

        results = [_calibrate_gamma(rows, gamma) for gamma in GAMMA_VALUES]
        all_results[year] = results

        print(f"  {'gamma':>5} {'MAE £':>8} {'RMSE £':>8} {'bias £':>8} {'corr':>6}")
        for r in results:
            print(f"  {r['gamma']:>5.1f} {r['mae']:>8.2f} {r['rmse']:>8.2f} {r['bias']:>8.2f} {r['correlation']:>6.3f}")

        best = min(results, key=lambda r: r["mae"])
        print(f"\n  Best fit (min MAE): gamma={best['gamma']:.1f} "
              f"(MAE=£{best['mae']:.2f}, bias=£{best['bias']:.2f}, corr={best['correlation']:.3f})\n")

    return all_results


if __name__ == "__main__":
    main()
