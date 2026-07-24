"""Test A (SSP negative-lift diagnosis) — scarcity-term dwell fraction per year.

Diagnostic ONLY. Pure data pass over the historical Elexon demand + wind/solar
caches; it reads NO company P&L and changes NO calibration constant, so it is
R13-clean (fidelity-to-reality, decided blind to company results) and R12-clean
(it measures a mechanism claim, it does not tune any output toward a benchmark).

Question it answers (from PLANNER_MINTED_ssp_negative_lift_cells_2026-07-24.md):
    In which year-cells is the model's convex scarcity term
        A2 * max(0, x - X_TIGHT) ** SCARCITY_EXPONENT
    actually LIVE? It is exactly zero whenever x <= X_TIGHT, where
        x = (demand_mw - renewable_generation_mw) / DISPATCHABLE_CAPACITY_MW.
    Prediction under test: near-zero dwell (x > X_TIGHT) in the calm losing
    cells (2019, 2020, 2023, 2024, 2025) and materially positive dwell in the
    crisis cells (2021, 2022). If confirmed, the scarcity term is dormant in
    calm years => the model is effectively the line A0 + A1*x there, so the
    negative lift vs the per-cell OLS baseline is a LINEAR-fit loss, not a
    scarcity-FORM loss.

Data sources (same series the model is calibrated against, joined per HH):
    sim/cache/elexon_demand_full.json  -> initialDemandOutturn (MW)
    sim/cache/elexon_agws_full.json    -> wind+solar quantity (MW), summed
                                          per (settlementDate, settlementPeriod)
Constants come from sim.price_engine so this stays a read of the live model.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict

from sim.price_engine import DISPATCHABLE_CAPACITY_MW, X_TIGHT

_CACHE = os.path.join(os.path.dirname(__file__), os.pardir, "sim", "cache")
_DEMAND = os.path.join(_CACHE, "elexon_demand_full.json")
_AGWS = os.path.join(_CACHE, "elexon_agws_full.json")


def _load(path: str) -> list[dict]:
    with open(path) as fh:
        return json.load(fh)


def dwell_fraction_by_year() -> dict[str, dict]:
    """Return {year: {n, dwell_n, dwell_fraction, median_x}} over every HH
    present in BOTH the demand and renewable series."""
    renew: dict[tuple[str, int], float] = defaultdict(float)
    for r in _load(_AGWS):
        renew[(r["settlementDate"], r["settlementPeriod"])] += r.get("quantity", 0.0) or 0.0

    demand: dict[tuple[str, int], float] = {}
    for r in _load(_DEMAND):
        v = r.get("initialDemandOutturn")
        if v is not None:
            demand[(r["settlementDate"], r["settlementPeriod"])] = float(v)

    xs_by_year: dict[str, list[float]] = defaultdict(list)
    for key, dem in demand.items():
        if key not in renew:
            continue
        x = (dem - renew[key]) / DISPATCHABLE_CAPACITY_MW
        xs_by_year[key[0][:4]].append(x)

    out: dict[str, dict] = {}
    for year in sorted(xs_by_year):
        xs = sorted(xs_by_year[year])
        n = len(xs)
        dwell_n = sum(1 for x in xs if x > X_TIGHT)
        median = xs[n // 2] if n else float("nan")
        out[year] = {
            "n": n,
            "dwell_n": dwell_n,
            "dwell_fraction": round(dwell_n / n, 6) if n else 0.0,
            "median_x": round(median, 4),
            "max_x": round(xs[-1], 4) if n else float("nan"),
        }
    return out


def main() -> None:
    table = dwell_fraction_by_year()
    print(f"X_TIGHT={X_TIGHT}  DISPATCHABLE_CAPACITY_MW={DISPATCHABLE_CAPACITY_MW}")
    print(f"{'year':>6} {'n':>8} {'dwell_n':>8} {'dwell_frac':>11} {'median_x':>9} {'max_x':>7}")
    for year, row in table.items():
        print(
            f"{year:>6} {row['n']:>8} {row['dwell_n']:>8} "
            f"{row['dwell_fraction']:>11.5f} {row['median_x']:>9.4f} {row['max_x']:>7.3f}"
        )


if __name__ == "__main__":
    main()
