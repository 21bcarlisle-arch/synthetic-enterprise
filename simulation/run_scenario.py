"""Phase 36a: Scenario integration runner — extends historical sim with forward scenario prices.

Wraps run_phase2b.main() with:
  - Synthetic electricity prices from sim.scenario.bimodal_generator
  - Synthetic gas prices from sim.scenario.gas_scenario_generator
  - Extended REPORT_END covering the scenario period

The scenario runner produces a full run dict identical in structure to a standard Phase 2b run,
with two additional top-level keys: "scenario_name" and "scenario_year_range".

Usage:
    from simulation.run_scenario import run_forward_scenario
    result = run_forward_scenario("central_2027", year_from=2026, year_to=2029)

Or from the command line:
    python -m simulation.run_scenario --scenario central_2027 --year-from 2026 --year-to 2029
"""

from __future__ import annotations

from datetime import date, timedelta

from sim.scenario.bimodal_generator import SCENARIOS as ELEC_SCENARIOS, generate_scenario_prices
from sim.scenario.gas_scenario_generator import GAS_SCENARIOS, generate_gas_scenario_prices


def _expand_daily_to_hh(daily_records: list[dict]) -> list[dict]:
    """Convert daily price records to half-hourly format (48 periods per day).

    The historical Elexon SSP records have one row per settlement period (1-48).
    This expands daily scenario prices into that format so the settlement lookup
    `elec_price_lookup[(date, period)]` works correctly.
    """
    hh = []
    for r in daily_records:
        price = r["systemSellPrice"]
        for period in range(1, 49):
            hh.append({
                "settlementDate": r["settlementDate"],
                "settlementPeriod": period,
                "systemSellPrice": price,
            })
    return hh


def build_extended_price_feeds(
    historical_elec: list[dict],
    historical_gas: list[dict],
    scenario: str = "central_2027",
    year_from: int = 2026,
    year_to: int = 2029,
    seed: str | None = None,
) -> tuple[list[dict], list[dict]]:
    """Append synthetic scenario prices to historical records.

    Returns (extended_elec_records, extended_gas_records).

    extended_elec_records: half-hourly format (settlementDate, settlementPeriod, systemSellPrice)
    extended_gas_records:  daily format (settlementDate, systemSellPrice)

    Both are sorted by settlementDate ascending, with historical data first.
    """
    _seed = seed or f"{scenario}_{year_from}_{year_to}"

    # Find the latest historical date to avoid overlapping with scenario data
    if historical_elec:
        latest_hist_date_str = max(r["settlementDate"] for r in historical_elec)
        latest_hist_date = date.fromisoformat(latest_hist_date_str)
        scenario_actual_from = max(year_from, latest_hist_date.year + 1)
    else:
        scenario_actual_from = year_from

    if scenario_actual_from > year_to:
        # Historical data already covers the requested scenario range — no extension needed
        return historical_elec, historical_gas

    elec_daily = generate_scenario_prices(scenario_actual_from, year_to, scenario, seed=_seed)
    elec_hh = _expand_daily_to_hh(elec_daily)
    extended_elec = historical_elec + elec_hh

    gas_daily = generate_gas_scenario_prices(scenario_actual_from, year_to, scenario, seed=_seed)
    if historical_gas:
        latest_gas_str = max(r["settlementDate"] for r in historical_gas)
        gas_daily = [r for r in gas_daily if r["settlementDate"] > latest_gas_str]
    extended_gas = historical_gas + gas_daily

    return extended_elec, extended_gas


def run_forward_scenario(
    scenario: str = "central_2027",
    year_from: int = 2026,
    year_to: int = 2029,
    seed: str | None = None,
    sim_interface=None,
) -> dict:
    """Run a full 2016-year_to simulation with historical + forward scenario prices.

    scenario: named preset from sim.scenario (both electricity and gas must have matching names).
    year_from: first year of synthetic data (default 2026, just after historical window ends).
    year_to: last year of synthetic data (inclusive).
    seed: deterministic seed for scenario generators. Defaults to "{scenario}_{year_from}_{year_to}".
    sim_interface: passed through to run_phase2b.main() for risk committee / fast-mode.

    Returns the standard run_phase2b result dict, augmented with:
        "scenario_name": str
        "scenario_year_range": [year_from, year_to]
    """
    from datetime import date as _date
    import sim.cache_store as _cache
    from sim.gas_prices_history import load_nbp_history as _load_nbp
    from sim.system_prices import get_system_prices_range
    from sim.cache_store import get_cached_prices, log_cache_access
    from simulation.run_phase2b import (
        ELEC_CUSTOMERS, GAS_CUSTOMERS, EARLIEST_SSP_DATE, REPORT_START,
    )

    report_end = f"{year_to}-12-31"
    _seed = seed or f"{scenario}_{year_from}_{year_to}"

    # Load historical price feeds (same logic as run_phase2b.main)
    earliest_acq = min(
        _date.fromisoformat(c["acquisition_date"])
        for c in ELEC_CUSTOMERS + GAS_CUSTOMERS
    )
    fetch_start_natural = (earliest_acq - timedelta(days=365)).isoformat()
    fetch_start = max(fetch_start_natural, EARLIEST_SSP_DATE)

    cached = get_cached_prices(fetch_start, report_end)
    if cached is not None:
        hist_elec = cached
        log_cache_access("elexon_ssp_full.json", hit=True, phase="36a_scenario")
    else:
        from simulation.run_phase2b import REPORT_END as _REPORT_END
        hist_elec = get_system_prices_range(fetch_start, _REPORT_END)
        log_cache_access("elexon_ssp_full.json", hit=False, phase="36a_scenario")

    hist_gas = _load_nbp()

    # Extend with scenario prices
    extended_elec, extended_gas = build_extended_price_feeds(
        hist_elec, hist_gas, scenario=scenario,
        year_from=year_from, year_to=year_to, seed=_seed,
    )

    print(f"[Scenario: {scenario!r}, {year_from}-{year_to}]")
    print(f"  Electricity: {len(hist_elec):,} historical + {len(extended_elec) - len(hist_elec):,} scenario = {len(extended_elec):,} total")
    print(f"  Gas: {len(hist_gas):,} historical + {len(extended_gas) - len(hist_gas):,} scenario = {len(extended_gas):,} total")

    # Inject the extended records into run_phase2b by patching the module-level loaders.
    # This is the minimal-invasive approach — avoids refactoring main() internals.
    import simulation.run_phase2b as _runner
    _orig_get_cached = _cache.get_cached_prices
    _orig_load_nbp = None

    try:
        import sim.gas_prices_history as _gas_mod
        _orig_load_nbp = _gas_mod.load_nbp_history

        # Patch loaders to return our extended records
        _cache.get_cached_prices = lambda *a, **kw: extended_elec
        _gas_mod.load_nbp_history = lambda: extended_gas

        result = _runner.main(report_end=report_end, sim_interface=sim_interface)
    finally:
        _cache.get_cached_prices = _orig_get_cached
        if _orig_load_nbp is not None:
            _gas_mod.load_nbp_history = _orig_load_nbp

    if isinstance(result, dict):
        result["scenario_name"] = scenario
        result["scenario_year_range"] = [year_from, year_to]

    return result


if __name__ == "__main__":
    import argparse, json, sys
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Run forward scenario simulation")
    parser.add_argument("--scenario", default="central_2027", choices=list(ELEC_SCENARIOS))
    parser.add_argument("--year-from", type=int, default=2026)
    parser.add_argument("--year-to", type=int, default=2029)
    parser.add_argument("--seed", default=None)
    parser.add_argument("--output", default=None, help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    result = run_forward_scenario(
        scenario=args.scenario,
        year_from=args.year_from,
        year_to=args.year_to,
        seed=args.seed,
    )

    out_json = json.dumps(result, indent=2, default=str)
    if args.output:
        Path(args.output).write_text(out_json)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(out_json)
