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
    market_departure_rate_pct,
)

PROJECT = Path(__file__).resolve().parent.parent
COMMONS = PROJECT / "docs" / "domain_artefact_library" / "regulatory" / "gb_domestic_switching_rate.json"
DEFAULT_TABLE = PROJECT / "docs" / "reports" / "c2_departure_factors.json"

#: Active domestic electricity accounts per year in the live run, from the opening finding's own
#: table. NOT re-derived here: the factor table holds renewals, not the active book, so the
#: per-account denominator has to come from the run that counted it. Stated rather than inferred so
#: a reader can see which years the per-account column can even be computed for.
#:
#: THESE ARE THE PRE-ANCHOR RUN'S COUNTS AND THE PER-ACCOUNT COLUMN IS THEREFORE INDICATIVE ONLY
#: (2026-08-30). Anchoring the level to the record roughly trebles departures, which changes the
#: book: accounts leave sooner, re-acquisition replaces them, and the active count per year is not
#: what it was. The column is kept because it is the only place the two denominators appear side by
#: side, and it is flagged rather than deleted because a per-account figure quietly recomputed on a
#: renewal denominator is exactly the confusion this tool exists to stop. The BAND is judged on the
#: `world E[depart]` column, which needs no external count.
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


def band_decimals() -> int:
    """How many decimal places the commons publishes its band endpoints to.

    DERIVED from the artefact rather than written down, so a record refined to two decimals
    tightens `inside_band` below without anyone remembering to.
    """
    raw = json.loads(COMMONS.read_text())
    return max(
        len(str(r[key]).partition(".")[2])
        for r in raw["rates"] for key in ("rate_pct_lo", "rate_pct_hi")
    )


def inside_band(value_pct: float, lo: float, hi: float) -> bool:
    """Is a measured level inside a published band, AT THE PRECISION THE BAND IS PUBLISHED TO?

    WHY THIS IS NOT A TOLERANCE BOLTED ON TO MAKE SOMETHING PASS, and the distinction matters
    because that is exactly what it would be if the number were chosen. The commons states every
    band to 0.1pp -- `13.5-14.0`, `22.5-23.0` -- because that is the precision the published switch
    counts and account totals bear. The world's level is measured from event records that round
    `realized_churn_probability` to four decimals, so a population mean carries rounding noise of
    order 0.0002pp. Aiming the level anchor at a band ENDPOINT (§6's tie-break: the high end, the
    anti-flattering choice) puts the measurement exactly on the boundary, and then a strict float
    comparison is decided by that noise: measured 2026-08-30, five of eight years landed 0.0002pp
    ABOVE their endpoint and three landed on or below it. That is a control reporting a coin flip.

    A value differing from an endpoint by 0.0002pp is EQUAL to it at every precision the record
    actually bears. So the comparison is made at the record's own precision, derived from the
    artefact. It cannot hide a real miss: the same run's 2020 sat at 23.72 against a 23.0 endpoint
    and fails here, as it should, and the pre-anchor world's 4.93% fails every year by miles.
    """
    return lo <= round(value_pct, band_decimals()) <= hi


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


def world_realised_rate_pct(table_path: Path | None = None) -> dict[int, float]:
    """`{year: mean realised departure probability %}` from a captured run.

    THE PRINCIPAL SUBJECT OF THE WHOLE COMPARISON, exposed as a table so
    `tests/architecture/test_switching_rate_commons.py` can hold it to the published band the
    same way it holds a module's year-keyed constant. It was not in that register when the
    register was written, which is why the control was green while the world sat 3.15x outside
    the band -- a control whose subject list omits its own principal subject is a control that
    stays green through exactly the defect it exists for.

    Restricted to `COMPARISON_YEARS` for the reason stated on that constant: 2016 has three
    renewals and 2025 is a partial year, and a three-account year must not carry the same weight
    as a 131-account one.
    """
    rows = json.loads((table_path or DEFAULT_TABLE).read_text())
    return {
        y: mean_p
        for y, (_n, _d, mean_p) in world_outcome(rows).items()
        if y in COMPARISON_YEARS
    }


def main(argv: list[str]) -> int:
    table_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_TABLE
    rows = json.loads(table_path.read_text())
    bands = published_bands()
    outcome = world_outcome(rows)

    print(f"factor table: {table_path}   ({len(rows)} renewals)")
    print()
    print("                published        savings curve    world rate       world E[depart]   departures /")
    print("  year          band %           %                (absolute) %     per renewal %     active elec %")
    print("  " + "-" * 96)
    mids, curves, rates, expected = [], [], [], []
    for year in sorted(bands):
        lo, hi = bands[year]
        curve = world_curve_pct(year)
        rate = market_departure_rate_pct(year)
        n, d, mean_p = outcome.get(year, (0, 0, float("nan")))
        per_account = (
            f"{100.0 * d / ACTIVE_ELEC_ACCOUNTS[year]:.1f}" if year in ACTIVE_ELEC_ACCOUNTS else "—"
        )
        flag = "" if inside_band(mean_p, lo, hi) else "   OUT OF BAND"
        print(f"  {year}          {lo:5.1f}–{hi:5.1f}      {curve:6.1f}           {rate:6.1f}           "
              f"{mean_p:6.2f}            {per_account:>5}{flag}")
        if year in COMPARISON_YEARS:
            mids.append((lo + hi) / 2.0)
            curves.append(curve)
            rates.append(rate)
            expected.append(mean_p)
    print()
    pub_mean, curve_mean, rate_mean, world_mean = (
        statistics.fmean(mids), statistics.fmean(curves),
        statistics.fmean(rates), statistics.fmean(expected))
    print(f"  {COMPARISON_YEARS.start}–{COMPARISON_YEARS.stop - 1} mean published midpoint : {pub_mean:5.2f}%")
    print(f"  {COMPARISON_YEARS.start}–{COMPARISON_YEARS.stop - 1} mean savings curve      : {curve_mean:5.2f}%"
          f"   ({pub_mean / curve_mean:.2f}x short of the record)")
    print(f"  {COMPARISON_YEARS.start}–{COMPARISON_YEARS.stop - 1} mean world rate         : {rate_mean:5.2f}%"
          f"   ({pub_mean / rate_mean:.2f}x short of the record)")
    print(f"  {COMPARISON_YEARS.start}–{COMPARISON_YEARS.stop - 1} mean world E[depart]    : {world_mean:5.2f}%"
          f"   ({pub_mean / world_mean:.2f}x short of the record)")
    print()
    print("  THE THREE COLUMNS ARE THREE DIFFERENT THINGS AND ONLY THE LAST ONE IS AN OUTCOME.")
    print("  `savings curve` is what `_savings_to_rate` computes at each year's own savings; since")
    print("  2026-08-30 it no longer sets the market level for a year the record covers, because a")
    print("  function of savings alone cannot reproduce the series (2017 and 2018 share a saving and")
    print("  differ by 6pp in the record). `world rate` is `market_departure_rate` -- the record")
    print("  itself inside the window -- and it is the quantity `market_switching_multiplier`")
    print("  normalises. `world E[depart]` is what the RUN did, and it is the only column that can")
    print("  be OUT OF BAND: the market term reaches the churn chain as a dimensionless RATIO, so")
    print("  the level it lands at is `simulation/departure_level_anchor.py`'s and not the ratio's.")
    print("  A year flagged OUT OF BAND means the anchor has gone stale against a world that moved")
    print("  under it -- re-capture and re-fit (`tools/fit_year_level_anchor.py`), never widen the")
    print("  band. See §8-§11 of docs/market_research/gb_switching_rate_denominators.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
