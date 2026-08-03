"""W1_6b reconstructibility measurement (Board Spec 004 exit criterion 3a).

Measures, per CALM year-cell, on ORDINARY (non-tight) half-hours, whether the
merit-order reconstruction (`sim/merit_order_reconstruction.py`) beats the FROZEN
`gas_floor_alone` naive baseline on MAE. This is a DIAGNOSTIC (R12): it reports the
truth, it never tunes toward it. No constant in the engine is fit to the SSP read here.

Ordinary hour  := residual-demand fraction x = (demand - renewables)/DISPATCHABLE <=
                  X_TIGHT (0.70), matching the FRAME §3a definition.
Calm cell      := year in the calm regime (2016-2020; 2021-2022 are crisis cells).

Data join is the SAME real Historical-Ground-Truth pipeline the 2026-07-19
recalibration used (`simulation/run_phase3b_recalibration.py`), incl. the AGWS
latest-publish dedup that removes the physically-impossible revision outliers.

Reused by `tests/sim/test_merit_order_reconstruction.py`, which SKIPS if the caches
are absent (so the collected suite never depends on the 100MB+ caches being present).
"""

import json
from pathlib import Path

import numpy as np

from sim.cache_store import get_cached_prices
from sim.gas_prices_history import load_nbp_history
from sim.merit_order_reconstruction import (
    gas_floor_alone_price_gbp_per_mwh,
    is_finite_number,
    reconstruct_price_gbp_per_mwh,
)
from sim.price_engine import DISPATCHABLE_CAPACITY_MW, X_TIGHT

CACHE_DIR = Path("sim/cache")
RENEWABLE_PSR_TYPES = ("Wind Onshore", "Wind Offshore", "Solar")

CALM_YEARS = ("2016", "2017", "2018", "2019", "2020")
CALM_START = "2016-03-01"
CALM_END = "2020-12-31"


def caches_present() -> bool:
    return (CACHE_DIR / "elexon_demand_full.json").exists() and (
        CACHE_DIR / "elexon_agws_full.json"
    ).exists()


def _dedup_latest_renewable_generation(agws_records: list[dict]) -> dict[tuple[str, int], float]:
    """LATEST publishTime per (date, period, psrType), then sum the renewable types.
    Same fix as run_phase3b_recalibration._dedup_latest_renewable_generation (the naive
    summing aggregator produces >1e5 MW outliers on heavily-revised periods)."""
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
        totals[(date_str, period)] = totals.get((date_str, period), 0.0) + record["quantity"]
    return totals


def build_calm_dataset() -> list[dict]:
    """Join real SSP + gas + demand + renewables over the calm window (2016-2020)."""
    ssp_records = get_cached_prices(CALM_START, CALM_END)
    ssp_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["systemSellPrice"] for r in ssp_records
    }
    demand_records = json.loads((CACHE_DIR / "elexon_demand_full.json").read_text())
    demand_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["initialDemandOutturn"]
        for r in demand_records
    }
    agws_records = json.loads((CACHE_DIR / "elexon_agws_full.json").read_text())
    renewable_lookup = _dedup_latest_renewable_generation(agws_records)
    gas_lookup = {r["settlementDate"]: r["systemSellPrice"] for r in load_nbp_history()}

    rows = []
    for (date_str, period), ssp in ssp_lookup.items():
        if date_str[:4] not in CALM_YEARS:
            continue
        key = (date_str, period)
        if key not in demand_lookup or key not in renewable_lookup or date_str not in gas_lookup:
            continue
        rows.append({
            "date": date_str,
            "year": int(date_str[:4]),
            "gas_price": gas_lookup[date_str],
            "demand_mw": demand_lookup[key],
            "renewable_mw": renewable_lookup[key],
            "ssp": ssp,
        })
    return rows


def per_cell_reconstructibility(rows: list[dict]) -> dict[str, dict]:
    """Per calm year-cell, ORDINARY hours only: MAE of the reconstruction vs the frozen
    gas-floor baseline, and whether the reconstruction wins (exit criterion 3a)."""
    gas = np.array([r["gas_price"] for r in rows])
    dem = np.array([r["demand_mw"] for r in rows])
    ren = np.array([r["renewable_mw"] for r in rows])
    ssp = np.array([r["ssp"] for r in rows])
    yr = np.array([r["year"] for r in rows])

    residual = dem - ren
    x = residual / DISPATCHABLE_CAPACITY_MW
    ordinary = x <= X_TIGHT

    recon = np.array([
        reconstruct_price_gbp_per_mwh(g, d, rr, int(y))
        for g, d, rr, y in zip(gas, dem, ren, yr)
    ])
    floor = np.array([gas_floor_alone_price_gbp_per_mwh(g) for g in gas])

    out: dict[str, dict] = {}
    for year in sorted(set(int(v) for v in yr)):
        mask = (yr == year) & ordinary
        n = int(mask.sum())
        if n == 0:
            continue
        mae_floor = float(np.mean(np.abs(ssp[mask] - floor[mask])))
        mae_recon = float(np.mean(np.abs(ssp[mask] - recon[mask])))
        # VACUITY GUARD (R10 class fix): reject non-finite evidence BEFORE comparing.
        # `nan < nan` is False, so an unguarded `mae_recon < mae_floor` would score a
        # cell built from NaN/inf inputs as "lost" — the right answer for the WRONG
        # reason, and it would hide the fact that the cell was never measured at all.
        evidence_finite = is_finite_number(mae_floor) and is_finite_number(mae_recon)
        out[str(year)] = {
            "n_ordinary": n,
            "ssp_mean": float(ssp[mask].mean()),
            "mae_gas_floor_alone": mae_floor,
            "mae_reconstruction": mae_recon,
            "mae_lift": mae_floor - mae_recon,   # positive = reconstruction wins
            "reconstruction_wins": bool(evidence_finite and mae_recon < mae_floor),
            "evidence_finite": evidence_finite,
        }
    return out


def reconstructibility_verdict(cells: dict[str, dict]) -> dict:
    """Exit criterion 3a as a control that CAN FAIL on its own named defect (R15).

    The criterion is PER-CELL — the reconstruction must beat `gas_floor_alone` in
    EVERY calm cell — NOT on aggregate. Grading on aggregate lift would FAIL-OPEN
    against exactly the defect this atom repairs (a crisis/one-cell win hiding
    renewables-heavy-cell losses), so this returns MET only when the losing-cell set
    is empty. `losing_cells` names the shortfall for the diagnostic.

    VACUITY GUARD (R10 class fix, 2026-08-03 — this function's OWN named defect):
    the unguarded form returned **met=True on empty input**, because `losing_cells` is
    vacuously empty when there are no cells at all. A caller handed empty or malformed
    data (a silent cache-load failure, a bad join) would have read "exit criterion 3a:
    MET" with ZERO measured evidence behind it — R15 killer pattern #2. A verdict with
    no evidence is NOT MET, never MET. The same guard rejects malformed cells (missing
    keys, non-finite `mae_lift`) so a NaN can never be summed into a passing verdict."""
    if not isinstance(cells, dict) or not cells:
        return {
            "met": False, "n_cells": 0, "n_won": 0, "losing_cells": [],
            "aggregate_lift": 0.0, "vacuous": True,
            "not_met_reason": (
                "no measured cells — a verdict with zero evidence is NOT MET "
                "(R15 fail-open guard; empty/malformed input is not a pass)"
            ),
        }

    malformed = sorted(
        y for y, c in cells.items()
        if not isinstance(c, dict)
        or "reconstruction_wins" not in c
        or not is_finite_number(c.get("mae_lift"))
    )
    if malformed:
        return {
            "met": False, "n_cells": len(cells), "n_won": 0,
            "losing_cells": sorted(cells), "aggregate_lift": 0.0, "vacuous": True,
            "not_met_reason": (
                "malformed or non-finite evidence in cells "
                f"{malformed} — unmeasurable is NOT MET, never MET"
            ),
        }

    losing = sorted(y for y, c in cells.items() if not c["reconstruction_wins"])
    aggregate_lift = sum(c["mae_lift"] for c in cells.values())
    return {
        "met": len(losing) == 0,
        "n_cells": len(cells),
        "n_won": len(cells) - len(losing),
        "losing_cells": losing,
        "aggregate_lift": aggregate_lift,  # reported but NOT the pass condition (anti-fail-open)
        "vacuous": False,
        "not_met_reason": None if not losing else f"cells {losing} did not beat gas_floor_alone",
    }


def main() -> dict:
    if not caches_present():
        print("SKIP: elexon demand/agws caches absent — cannot measure on real data.")
        return {}
    rows = build_calm_dataset()
    print(f"{len(rows):,} calm-window settlement periods with full data\n")
    cells = per_cell_reconstructibility(rows)
    verdict = reconstructibility_verdict(cells)
    print(f"{'cell':>6} {'n_ord':>8} {'ssp_mean':>9} {'MAE_floor':>10} {'MAE_recon':>10} "
          f"{'lift':>7} {'wins?':>6}")
    for year, c in cells.items():
        print(f"{year:>6} {c['n_ordinary']:>8,} {c['ssp_mean']:>9.2f} "
              f"{c['mae_gas_floor_alone']:>10.2f} {c['mae_reconstruction']:>10.2f} "
              f"{c['mae_lift']:>7.2f} {'YES' if c['reconstruction_wins'] else 'no':>6}")
    print(f"\nExit criterion 3a (beat gas_floor_alone in EVERY calm cell): "
          f"{verdict['n_won']}/{verdict['n_cells']} cells won -> "
          f"{'MET' if verdict['met'] else 'NOT MET'}"
          f"{'' if verdict['met'] else '  (' + str(verdict['not_met_reason']) + ')'}")
    return cells


if __name__ == "__main__":
    main()
