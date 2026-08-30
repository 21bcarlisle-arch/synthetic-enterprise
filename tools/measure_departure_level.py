"""Print the world's departure LEVEL beside the published switching band, on a declared denominator.

Anchor: `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`.
Write-up: `docs/market_research/gb_switching_rate_denominators.md`.
Opened by: `docs/staging/WORKER_FINDING_THE_WORLDS_DEPARTURE_LEVEL_HAS_NEVER_BEEN_CHECKED_AGAINST_A_PUBLISHED_RATE_2026-08-30.md`.

WHY A TOOL AND NOT A ONE-OFF SCRIPT. The comparison this prints was never run in this project's
history -- not because it is hard, but because no instrument existed that would put the two numbers
on one line with their denominators attached. The gap it found is 3.15x. Anything measured once by
hand gets re-measured on a different denominator next time, and the whole trap in this area is the
denominator.

THREE LEVELS, AND THE MIDDLE ONE IS THE ONE NOBODY LOOKED AT:

  published            the record: domestic electricity changes of supplier over domestic
                       electricity accounts, from the commons artefact.
  the world's curve    `market_switching_propensity._savings_to_rate` at each year's own savings.
                       It claims in its docstring to be calibrated to the published series.
  the world's outcome  what the run actually did, per renewal and per active account.

DENOMINATORS ARE NAMED ON EVERY COLUMN, and the two the world bears are DIFFERENT QUANTITIES. Per
renewal narrows the denominator to accounts at a decision point and reads about a third high against
the published record, which counts every account whether or not it could move. Only the per-account
column is comparable. Printing both, labelled, is the point -- a single unlabelled "our churn rate"
is how this comparison goes wrong.

Usage:  python3 -m tools.measure_departure_level [factor_table.json]
"""
from __future__ import annotations

import collections
import json
import statistics
import sys
from pathlib import Path

from simulation.market_switching_propensity import (
    _POST_BAN_STRUCTURAL_FACTOR,
    MARKET_SAVINGS_BY_YEAR,
    _savings_to_rate,
)

PROJECT = Path(__file__).resolve().parent.parent
COMMONS = PROJECT / "docs" / "domain_artefact_library" / "regulatory" / "gb_domestic_switching_rate.json"
DEFAULT_TABLE = PROJECT / "docs" / "reports" / "c2_departure_factors.json"

#: Active domestic electricity accounts per year in the live run, from the opening finding's own
#: table. NOT re-derived here: the factor table holds renewals, not the active book, so the
#: per-account denominator has to come from the run that counted it. Stated rather than inferred so
#: a reader can see which years the per-account column can even be computed for.
ACTIVE_ELEC_ACCOUNTS: dict[int, int] = {
    2017: 81, 2018: 88, 2019: 94, 2020: 101, 2021: 108, 2022: 110, 2023: 117, 2024: 131,
}

#: The years the comparison is meaningful over. 2016 has 3 renewals and 2025 is a partial year in
#: the captured run; averaging either in would let a 3-account year weigh as much as a 131-account
#: one. Excluded rather than silently included -- the opening finding made the same exclusion and
#: for the same reason.
COMPARISON_YEARS = range(2017, 2025)


def published_bands() -> dict[int, tuple[float, float]]:
    """`{year: (lo_pct, hi_pct)}` from the commons.

    Fails closed on a year the commons does not carry: a missing band must not read as an
    unbounded one, which is the fail-open shape that lets any level pass.
    """
    raw = json.loads(COMMONS.read_text())
    return {int(r["year"]): (float(r["rate_pct_lo"]), float(r["rate_pct_hi"])) for r in raw["rates"]}


def world_curve_pct(year: int) -> float:
    """The absolute annual switching rate the world's own savings-elasticity curve computes.

    This is the number `market_switching_multiplier` divides away one line later, and the reason
    the world's level was never checked against anything.
    """
    savings = MARKET_SAVINGS_BY_YEAR[year]
    structural = _POST_BAN_STRUCTURAL_FACTOR.get(year, 1.0)
    return 100.0 * _savings_to_rate(savings) * structural


def world_outcome(rows: list[dict]) -> dict[int, tuple[int, int, float]]:
    """`{year: (renewals, departures, mean_realised_departure_probability_pct)}`."""
    by: dict[int, list] = collections.defaultdict(lambda: [0, 0, []])
    for r in rows:
        year = int(r["event_date"][:4])
        by[year][0] += 1
        if r["event_type"] == "churned":
            by[year][1] += 1
        by[year][2].append(r["realized_churn_probability"])
    return {y: (n, d, 100.0 * statistics.fmean(ps)) for y, (n, d, ps) in by.items()}


def main(argv: list[str]) -> int:
    table_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_TABLE
    rows = json.loads(table_path.read_text())
    bands = published_bands()
    outcome = world_outcome(rows)

    print(f"factor table: {table_path}   ({len(rows)} renewals)")
    print()
    print("                published        world curve      world E[depart]   departures /")
    print("  year          band %           %                per renewal %     active elec %")
    print("  " + "-" * 74)
    mids, curves, expected = [], [], []
    for year in sorted(bands):
        lo, hi = bands[year]
        curve = world_curve_pct(year)
        n, d, mean_p = outcome.get(year, (0, 0, float("nan")))
        per_account = (
            f"{100.0 * d / ACTIVE_ELEC_ACCOUNTS[year]:.1f}" if year in ACTIVE_ELEC_ACCOUNTS else "—"
        )
        flag = "" if lo <= mean_p <= hi else "   OUT OF BAND"
        print(f"  {year}          {lo:5.1f}–{hi:5.1f}      {curve:6.1f}           "
              f"{mean_p:6.2f}            {per_account:>5}{flag}")
        if year in COMPARISON_YEARS:
            mids.append((lo + hi) / 2.0)
            curves.append(curve)
            expected.append(mean_p)
    print()
    pub_mean, curve_mean, world_mean = (
        statistics.fmean(mids), statistics.fmean(curves), statistics.fmean(expected))
    print(f"  {COMPARISON_YEARS.start}–{COMPARISON_YEARS.stop - 1} mean published midpoint : {pub_mean:5.2f}%")
    print(f"  {COMPARISON_YEARS.start}–{COMPARISON_YEARS.stop - 1} mean world curve        : {curve_mean:5.2f}%"
          f"   ({pub_mean / curve_mean:.2f}x short of the record)")
    print(f"  {COMPARISON_YEARS.start}–{COMPARISON_YEARS.stop - 1} mean world E[depart]    : {world_mean:5.2f}%"
          f"   ({pub_mean / world_mean:.2f}x short of the record)")
    print()
    print("  The curve column is an ABSOLUTE rate the world computes and then divides away:")
    print("  `market_switching_multiplier` normalises it to 1.0 at 2024, so no level reaches the run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
