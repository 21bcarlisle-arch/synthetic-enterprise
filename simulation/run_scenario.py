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

import json
from datetime import date, timedelta
from pathlib import Path

from sim.scenario.bimodal_generator import SCENARIOS as ELEC_SCENARIOS, generate_scenario_prices
from sim.scenario.gas_scenario_generator import GAS_SCENARIOS, generate_gas_scenario_prices
from sim.scenario.intraday_shape import shape_day

# Real 2016-2025 daily-mean SSP reference, extracted once from the 128MB half-hourly cache
# (sim/cache/elexon_ssp_full.json) into a compact committed fixture -- see reconcile_baseline_fidelity.
REAL_SSP_DAILY_MEAN_FIXTURE = Path(__file__).resolve().parent.parent / "sim" / "scenario" / "data" / "real_ssp_daily_mean.json"

# External plausibility band for the REAL reference's daily-mean SSP LEVEL (median), anchored to
# published UK market knowledge (Ofgem/Elexon: SSP daily means sit in the tens-to-low-hundreds of
# GBP/MWh, crisis-spiking to the £100s-£1000s per DAY but with a full-history median far below that).
# Real committed fixture: median 55.59 GBP/MWh. NOT tuned to the fixture -- an EXTERNAL sanity band
# whose only job is to fire on a reference that is not real UK price LEVELS at all (see below).
MIN_REAL_SSP_DAILY_MEAN_MEDIAN = 10.0    # p/kWh mis-unit (~5.5) and returns-stored-as-levels (~0) fall below
MAX_REAL_SSP_DAILY_MEAN_MEDIAN = 500.0   # generous upside even for a crisis-heavy real window


class CorruptReferenceError(ValueError):
    """FAIL-OPEN loud (R15 killer pattern 1, INDEPENDENCE): the whole fidelity check measures
    agreement AGAINST this committed 'real' reference, so a silently corrupt / wrong-source /
    wrong-unit fixture turns the check into a tautology (agreement against a fabricated anchor).
    The fixture is in W1_2's own file_scope and editable, and the only prior guards (len>2000,
    std>0) pass a truncated or unit-wrong series -- so validate the reference's OWN declared
    integrity and its real-world plausibility before trusting it, raising loud rather than
    reconciling against a bad anchor (an unavailable/untrustworthy reference is a FAILED check)."""


def _validate_real_reference(data: dict) -> "list":
    """Integrity-check the committed real-SSP reference before it anchors the fidelity check.

    Two INDEPENDENT guards (R15 -- must fire on a corrupt reference, pass on the real one):
      (1) internal consistency: the fixture SELF-DECLARES `n_days`; cross-check it against the
          actual `daily_mean_ssp` length. Two separately-authored fields must agree -- catches
          a truncated / appended / partially-overwritten fixture (the most likely silent
          corruption of a committed data file). Independent of the values themselves.
      (2) external plausibility: the daily-mean LEVEL median must sit in a published-UK-market
          band (MIN/MAX above). Catches a reference that is not real price levels at all --
          a p/kWh unit error, returns accidentally stored where levels belong (median ~0),
          fabricated flat/near-zero data -- exactly the wrong-anchor case (1) cannot see.
    """
    if "daily_mean_ssp" not in data:
        raise CorruptReferenceError("reference fixture missing 'daily_mean_ssp' -- not a real reference")
    series = data["daily_mean_ssp"]
    if not isinstance(series, list) or len(series) == 0:
        raise CorruptReferenceError(f"'daily_mean_ssp' is empty/not a list ({type(series).__name__})")
    declared = data.get("n_days")
    if declared is None:
        # FAIL-OPEN close (R15 killer pattern 2, passes-on-MISSING, added 2026-07-28 HARDEN red-team):
        # the cross-check was `if declared is not None` -- an OPTIONAL integrity field is silently
        # SKIPPED when absent, so a corruption that truncates the series AND drops n_days evaded
        # guard (1) entirely; a truncated real head keeps its median in-band (37.56 for [:100]), so
        # guard (2) passed too and the corrupt reference anchored the whole tautology check. An intact
        # real reference self-declares its own length -- a missing n_days IS a corruption, not a licence
        # to skip the guard (the real committed fixture always carries it: n_days == len == 3501).
        raise CorruptReferenceError(
            "reference fixture missing self-declared 'n_days' -- an intact real reference declares "
            "its own length; a missing integrity field is itself corruption, not a reason to skip "
            "guard (1) (a truncation that also drops n_days would otherwise evade it and, staying "
            "in-band, guard (2) too)"
        )
    if declared != len(series):
        raise CorruptReferenceError(
            f"fixture self-declares n_days={declared} but daily_mean_ssp has {len(series)} values "
            "-- truncated/corrupt reference, not the intact real series"
        )
    import numpy as np
    v = np.asarray(series, dtype=float)
    if not np.all(np.isfinite(v)):
        raise CorruptReferenceError("reference contains non-finite daily means -- corrupt")
    median = float(np.median(v))
    if not (MIN_REAL_SSP_DAILY_MEAN_MEDIAN <= median <= MAX_REAL_SSP_DAILY_MEAN_MEDIAN):
        raise CorruptReferenceError(
            f"daily-mean SSP median {median:.2f} GBP/MWh outside the plausible UK band "
            f"[{MIN_REAL_SSP_DAILY_MEAN_MEDIAN}, {MAX_REAL_SSP_DAILY_MEAN_MEDIAN}] -- wrong unit, "
            "returns-stored-as-levels, or fabricated reference, not real price levels"
        )
    return series


def _expand_daily_to_hh(daily_records: list[dict], seed: str = "scenario") -> list[dict]:
    """Convert daily scenario price records to half-hourly format (48 periods per day).

    The historical Elexon SSP records have one row per settlement period (1-48); this expands the
    daily scenario prices into that format so the settlement lookup `elec_price_lookup[(date, period)]`
    works correctly.

    The 48 periods carry a MEAN-PRESERVING intraday SSP shape (sim.scenario.intraday_shape.shape_day):
    a diurnal profile plus a possible tightness-keyed scarcity spike and oversupply trough, so the
    forward residual settles against a within-day SSP profile — the block-hedge-vs-spiky-shape mismatch
    that bit real suppliers in 2021-22 (SPIKE_TAIL_SSP_RESIDUAL). The day's MEAN SSP is unchanged (the
    daily-generator calibration is untouched, R12/R13); only the within-day distribution is added.
    Deterministic in (day, seed): a fixed history replays byte-identical (C-S2).
    """
    hh = []
    for r in daily_records:
        periods = shape_day(r["systemSellPrice"], r["settlementDate"], seed=seed)
        for period in range(1, 49):
            hh.append({
                "settlementDate": r["settlementDate"],
                "settlementPeriod": period,
                "systemSellPrice": periods[period - 1],
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

    # data_regime provenance (W1_2 L1->L2, epistemic-wall rule .claude/rules/epistemic-wall-sim.md:
    # "every record should carry historical or synthetic"). Without this the concatenation below is
    # structurally indistinguishable real-vs-generated once built -- the exact gap the FRAME names.
    # setdefault on the historical halves so a record already tagged upstream is never overwritten;
    # explicit "synthetic" on the generated halves (which this function owns).
    for _r in historical_elec:
        _r.setdefault("data_regime", "historical")
    for _r in historical_gas:
        _r.setdefault("data_regime", "historical")

    if scenario_actual_from > year_to:
        # Historical data already covers the requested scenario range — no extension needed
        return historical_elec, historical_gas

    elec_daily = generate_scenario_prices(scenario_actual_from, year_to, scenario, seed=_seed)
    elec_hh = _expand_daily_to_hh(elec_daily, seed=_seed)
    for _r in elec_hh:
        _r["data_regime"] = "synthetic"
    extended_elec = historical_elec + elec_hh

    gas_daily = generate_gas_scenario_prices(scenario_actual_from, year_to, scenario, seed=_seed)
    if historical_gas:
        latest_gas_str = max(r["settlementDate"] for r in historical_gas)
        gas_daily = [r for r in gas_daily if r["settlementDate"] > latest_gas_str]
    for _r in gas_daily:
        _r["data_regime"] = "synthetic"
    extended_gas = historical_gas + gas_daily

    return extended_elec, extended_gas


def _daily_returns(prices) -> "list[float]":
    """First-difference returns (ΔP = P_t - P_{t-1}) of a daily price series.

    ΔP, not log/percentage returns: real UK SSP goes NEGATIVE (negative-price days) and
    through ~0, which makes log- and pct-returns undefined/explosive. First differences are
    well-defined everywhere and preserve the volatility-clustering / spike / persistence
    structure the fidelity moments measure.
    """
    import numpy as np
    v = np.asarray(prices, dtype=float)
    return np.diff(v)


def load_real_ssp_daily_returns(fixture_path: "str | Path | None" = None):
    """Return the REAL 2016-2025 daily-mean SSP first-difference return series.

    Reads the compact committed fixture (sim/scenario/data/real_ssp_daily_mean.json), a
    daily-mean aggregation of the real half-hourly Elexon SSP record -- so the 128MB
    half-hourly cache is never parsed at run/test time. Real published market data (R13:
    the real reference the baseline generator is measured AGAINST, blind to company P&L).
    """
    path = Path(fixture_path) if fixture_path is not None else REAL_SSP_DAILY_MEAN_FIXTURE
    data = json.loads(path.read_text())
    series = _validate_real_reference(data)  # R15: reject a corrupt/wrong-anchor reference LOUD
    return _daily_returns(series)


def reconcile_baseline_fidelity(
    scenario: str = "baseline_2025",
    year_from: int = 2026,
    year_to: int = 2035,
    seed: str = "baseline_fidelity",
    *,
    generated_returns=None,
    reference_returns=None,
):
    """Swing the fidelity-check blade on the ACTUAL baseline generator vs REAL history.

    check_scenario_fidelity's six R15-hardened distributional moments
    (mean/std/lag1_autocorr/tail_ratio/tail_skew/vol_clustering) had ZERO production callers
    for the whole hardening arc -- the blade was sharpened on synthetic red-team fixtures but
    never swung on the ACTUAL baseline generator's output. Per R15 an uninvoked check is a
    FAILED check (the FRAME S3 calls it a "hard gate"; a gate that gates nothing protects
    nothing). This is that caller: it generates the agree-expected baseline scenario, takes
    first-difference returns of both the generated and the real 2016-2025 SSP series, and
    reconciles them on every shared moment.

    NON-BLOCKING DIAGNOSTIC (R12/R4). Returns the FidelityVerdict; a divergence is a FINDING
    that drives diagnosis of the generator, NEVER a publish/scenario-run blocker -- the
    known hazard (a false-fire jamming the reporting pipeline) is exactly why this is
    diagnostic-only and is never wired into a gating path. Only a genuinely degenerate/missing
    reference raises (DegenerateSeriesError, FAIL-OPEN loud).

    R13 / agree-expected only: reconcile ONLY the baseline scenario against real history. The
    stress presets (dunkelflaute/low-renewables/battery-saturation) are director-authored
    curriculum that SHOULD diverge from the real record -- divergence there is the point, not
    a defect. `generated_returns`/`reference_returns` may be injected (tests) to prove the
    control both fires and passes without re-generating or re-reading the fixture.
    """
    from sim.scenario import fidelity_check as F

    if reference_returns is None:
        reference_returns = load_real_ssp_daily_returns()
    if generated_returns is None:
        gen = generate_scenario_prices(year_from, year_to, scenario, seed=seed)
        generated_returns = _daily_returns([g["systemSellPrice"] for g in gen])
    return F.check_scenario_fidelity(generated_returns, reference_returns)


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
