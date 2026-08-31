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
from tools.departure_population import (
    banner,
    book_banner,
    book_departure_level,
    declare,
    load_svt_decisions,
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


def band_margins(value_pct: float, lo: float, hi: float) -> tuple[float, float]:
    """`(room to the LOW edge, room to the HIGH edge)` in percentage points, SIGNED.

    Positive means the level could move that far in that direction and still be inside the band;
    negative means it is already outside by that much. So a year reading `(+0.4, +0.0)` can fall
    0.4pp before the control fires and cannot rise at all.

    WHY THE VERDICT ALONE IS NOT ENOUGH, and it is the same repair `e707b0cb7` shipped for the
    "worse than guessing" count. `inside_band` answers a threshold question, and a threshold
    crossing is not a magnitude: measured 2026-08-31, `YEAR_LEVEL_ANCHOR` is fitted to each band's
    HIGH endpoint (§6's anti-flattering tie-break), so the world sits with ZERO room above in all
    ten years. A +0.11pp move in 2024 that shifted no departures at all -- 79 either way -- exits
    the band and reads identically to one ten times larger. Printing the distance is what lets a
    reader tell those apart, and nothing else in the tree can.

    Rounded at the record's own precision, for the reason `inside_band` gives: a margin quoted to
    more decimals than the band bears would report measurement noise as headroom.
    """
    dp = band_decimals()
    value = round(value_pct, dp)
    return round(value - lo, dp), round(hi - value, dp)


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


def world_book_departure_rate_pct(
    table_path: Path | None = None,
) -> tuple[dict[int, float] | None, str | None]:
    """`({year: whole-book expected departure %}, None)`, or `(None, reason)` — BOTH ROUTES.

    THE COMPARABLE COLUMN, AND `world_realised_rate_pct` ABOVE IS NOT ONE. That function means
    `realized_churn_probability` over renewal decisions, and post-C1b the renewal roll is a
    SELECTED sub-population: the households that took a fixed deal and reached a decision point.
    The published band's denominator is every domestic electricity account. Comparing the two was
    never a like-for-like comparison, and the tell was in the artefact all along -- on the
    2026-08-31 two-route capture the renewal route has NO decisions at all in 2022, which is why
    the eight-year summary printed `nan` for that year and nothing said why.

    Kept as a SECOND function rather than a repair of the first, deliberately, and it is the same
    reasoning `reading_population` gives. `world_realised_rate_pct` is the declared subject of
    `tests/architecture/test_switching_rate_commons.py`; rewriting what a control measures inside
    the commit that repairs the measurement makes the move unattributable, and this project has
    paid for that. The two readings sit side by side, both printed, and which one the band control
    should take is a separate act on a separate day.

    NOT RESTRICTED TO `COMPARISON_YEARS`. That window exists because the renewal route had three
    decisions in 2016 and a partial 2025; on the whole book those years carry 3 and 48 accounts,
    and 2016 is small for a real reason rather than a route-selection one. The caller windows it.
    """
    path = table_path or DEFAULT_TABLE
    rows = json.loads(path.read_text())
    svt_rows, _ = load_svt_decisions(path)
    levels, refusal = book_departure_level(rows, svt_rows)
    if levels is None:
        return None, refusal
    return {y: r["expected_departure_pct"] for y, r in levels.items()
            if r["expected_departure_pct"] is not None}, None


def reading_population(table_path: Path | None = None) -> dict:
    """The population `world_realised_rate_pct` above just measured, as a declaration.

    A SECOND FUNCTION AND NOT A SECOND RETURN VALUE, deliberately: `world_realised_rate_pct` is
    the subject of `tests/architecture/test_switching_rate_commons.py` and of the band control, and
    changing its shape to carry the declaration would have rewritten a control's subject in the
    same commit that repaired what it measures. The declaration is what the READER must not be able
    to skip, and the way to hold that is a control over the pair, not a wider tuple.

    WHAT IT SAYS TODAY, MEASURED. On the committed `c2_departure_factors.json` it says *renewal
    decisions only, SVT route unreadable* -- so the band verdict that control takes is a reading
    over the households that reach a renewal roll, compared against a published rate whose
    denominator is every domestic electricity account. Those are different quantities. The control
    is green and the artefact is from a world that no longer exists; both facts belong on the
    surface rather than in a footnote.
    """
    return declare(table_path or DEFAULT_TABLE)


def main(argv: list[str]) -> int:
    table_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_TABLE
    rows = json.loads(table_path.read_text())
    bands = published_bands()
    outcome = world_outcome(rows)

    decl = declare(table_path, rows)
    print(banner(decl))
    print()
    print(f"factor table: {table_path}   ({len(rows)} renewals)")
    print()
    print("                published        savings curve    world rate       world E[depart]   departures /    room to    room to")
    print("  year          band %           %                (absolute) %     per renewal %     active elec %   LOW pp     HIGH pp")
    print("  " + "-" * 118)
    mids, curves, rates, expected = [], [], [], []
    room_below, room_above = [], []
    for year in sorted(bands):
        lo, hi = bands[year]
        curve = world_curve_pct(year)
        rate = market_departure_rate_pct(year)
        n, d, mean_p = outcome.get(year, (0, 0, float("nan")))
        per_account = (
            f"{100.0 * d / ACTIVE_ELEC_ACCOUNTS[year]:.1f}" if year in ACTIVE_ELEC_ACCOUNTS else "—"
        )
        below, above = band_margins(mean_p, lo, hi)
        flag = "" if inside_band(mean_p, lo, hi) else "   OUT OF BAND"
        print(f"  {year}          {lo:5.1f}–{hi:5.1f}      {curve:6.1f}           {rate:6.1f}           "
              f"{mean_p:6.2f}            {per_account:>5}   {below:+7.2f}   {above:+7.2f}{flag}")
        if year in COMPARISON_YEARS:
            mids.append((lo + hi) / 2.0)
            curves.append(curve)
            rates.append(rate)
            expected.append(mean_p)
            room_below.append(below)
            room_above.append(above)
    print()
    print(f"  RESOLUTION OF THIS CONTROL, {COMPARISON_YEARS.start}–{COMPARISON_YEARS.stop - 1}. Room ABOVE the level before the band is exited: "
          f"{min(room_above):+.2f} to {max(room_above):+.2f}pp.")
    print(f"  Room BELOW: {min(room_below):+.2f} to {max(room_below):+.2f}pp. A movement smaller than the room in its own "
          f"direction CANNOT be seen here,")
    print("  and one larger is reported the same whatever its size -- so read the margin, never the verdict alone. Where the")
    print("  room above is 0.00 the anchor is sitting on its band's ceiling and ANY upward move exits, however small; that is")
    print("  a property of the fit, not a finding about the world. See the finding filed 2026-08-31 on this asymmetry.")
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
    print()
    print("  AND THE `world E[depart]` COLUMN IS A MEAN OVER THE POPULATION NAMED AT THE TOP.")
    if decl["covers_svt_route"]:
        print(f"  This capture sees both routes, and the renewal route it means over carries "
              f"{decl['share_of_departures_visible']:.0%} of")
        print("  its departures. The published band's denominator is every domestic electricity")
        print("  account, not the ones that reached a renewal roll, so the two are NOT the same")
        print("  quantity and a verdict here is about the renewal route alone.")
    else:
        print("  This capture cannot see the SVT inertia route at all, so it cannot say what share")
        print("  of the book's departures it is measuring. A year flagged OUT OF BAND on this")
        print("  table is a statement about renewal decisions, and a year INSIDE it is not")
        print("  evidence the world's departure level matches the record.")
    print()
    _print_book_level(table_path, rows, bands)
    return 0


def _print_book_level(table_path: Path, rows: list[dict], bands: dict[int, tuple[float, float]]) -> None:
    """The whole-book level over both routes, which is the only column comparable to the band.

    Printed BELOW the renewal table rather than replacing it, so a reader sees the two readings
    disagree on the same screen. On the committed captures they disagree by up to 13pp and in one
    year the renewal reading does not exist at all.
    """
    svt_rows, _ = load_svt_decisions(table_path)
    levels, refusal = book_departure_level(rows, svt_rows)
    print("  " + "=" * 118)
    print(book_banner(levels, refusal))
    if levels is None:
        return
    print()
    print("                published        BOTH ROUTES       renewal route     accounts   decisions   departures   room to    room to")
    print("  year          band %           E[depart] %       only E[depart] %  (denom)    both routes  both routes LOW pp     HIGH pp")
    print("  " + "-" * 130)
    for year in sorted(levels):
        row = levels[year]
        book = row["expected_departure_pct"]
        renewal_only = row["renewal_only_expected_pct"]
        lo, hi = bands.get(year, (None, None))
        if book is None or lo is None:
            print(f"  {year}          {'—':>13}      {'—':>13}")
            continue
        below, above = band_margins(book, lo, hi)
        flag = "" if inside_band(book, lo, hi) else "   OUT OF BAND"
        ro = f"{renewal_only:.2f}" if renewal_only is not None else "— no renewals"
        print(f"  {year}          {lo:5.1f}–{hi:5.1f}      {book:6.2f}            {ro:>13}     "
              f"{row['accounts']:>5}      {row['total_decisions']:>6}      {row['total_departures']:>6}   "
              f"{below:+7.2f}   {above:+7.2f}{flag}")
    print()
    print("  READ THE DENOMINATOR BEFORE THE VERDICT. The `BOTH ROUTES` column is a mean over")
    print("  ACCOUNT-YEARS: each account's decisions in the year are combined into one annual")
    print("  departure probability. The mean over DECISIONS is NOT this number and is not")
    print("  comparable to anything -- an SVT account faces a segment decision at every boundary")
    print("  and a fixed account faces one renewal roll, so that mean reads 3.6–7.5% and would")
    print("  publish a world departing far below the record when it departs above it in 2022.")
    print()
    print("  AND THE TWO COLUMNS DISAGREE, WHICH IS THE POINT. The renewal route is the households")
    print("  that took a fixed deal and reached a decision point -- a SELECTED sub-population, not")
    print("  the book. Where the renewal column is blank the route had no decisions that year at")
    print("  all, and the renewal-only summary above prints `nan` for it. The band's denominator")
    print("  is every domestic electricity account, so only the BOTH ROUTES column is the same")
    print("  KIND of quantity as the band -- and it is an UPPER bound on it, because an account")
    print("  facing no decision in the year cannot depart and is not in the denominator. A year")
    print("  reading OUT OF BAND ABOVE therefore cannot be explained away by the bound; a year")
    print("  reading inside it might still be outside on the full book.")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
