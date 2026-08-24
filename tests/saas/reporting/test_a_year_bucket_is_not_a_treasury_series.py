"""A YEAR'S RECORDS ARE A SUBSEQUENCE OF THE PORTFOLIO BALANCE, NOT A SERIES OF THEIR OWN.

THE DEFECT (2026-08-24, the residual named at the end of
`docs/staging/WORKER_FINDING_THE_TREASURY_DRAWDOWN_FIGURE_IS_AN_ARTEFACT_OF_SORTING_A_BALANCE_THAT_WAS_NEVER_A_SERIES_2026-08-24.md`):

    the published count came from the accumulation-order read of `yr_records`. That is a real
    exercise of the fallback on a 10-year book, and it is the first one. It returned two
    events:

        2022   peak £1,169,284.6555   trough £1,035,944.824   11.4035%
        2023   peak £1,169,284.6953   trough £1,035,932.012   11.4046%

    those two "different years" have peaks FOUR PENCE apart and troughs £12.81 apart, on a book
    whose treasury grew £250k -> £1.75M. Two independent swings landing that close is not a
    coincidence worth entertaining.

The finding could only label the mechanism INFERRED — it needed a full-book run to settle, and
the memory headroom to take one did not exist. This file settles it a different way: it builds
the interleave the mechanism requires and shows the double-count appear, which is the same
claim without the £1.7M book. `treasury_cash_balance_gbp` is a PORTFOLIO running total stamped
record-by-record during the term loop, so between two consecutive same-year records the balance
travels through other customers' whole terms. Bucketing it by `settlement_date[:4]` therefore
breaks accumulation order for the same reason re-sorting did, just far more gently: ONE swing
shows up once in each year whose records straddle it.

WHY IT IS THE SAME CLASS, NOT A NEW ONE (R10). The opening sentence of that finding —
"meaningful in ACCUMULATION order and in no other" — was already the whole rule. `sorted()`
broke it loudly (6,747 events); the year partition broke it quietly (2 events for 1). Both are
a read of the running total in an order it never took.

THE CLASS CONTROL is `test_the_published_events_are_one_walk_and_say_so`. Every published event
carries `sequence`, its position in the one walk; the sequences across all years are therefore
0..n-1 with no repeats, and ordered by them the peaks strictly increase. A partition of the
running total — by year, by month, by segment, by anything — restarts both, so it cannot
publish through this assertion. That is what makes the fix a CLASS fix rather than one book's
answer: it is checked on the PUBLISHED dict, so any future re-introduction reds it.

MUTATIONS APPLIED, fires OBSERVED (R15), each run in a scratch worktree:
  M1  reorder the path year-by-year before the walk                       -> 3 fire
  M2  attribute an event to the year of its PEAK instead of its trough    -> 2 fire
  M3  fail-open: `_drawdown_events_by_year` returns `{}` always           -> 3 fire
  M4  drop the year tag from the register (`points()` returns balances)   -> 8 fire
  M5  the genuine pre-repair shape: one INDEPENDENT walk per year bucket  -> 3 fire, including
      `test_the_published_events_are_one_walk_and_say_so` (duplicate sequences)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from saas.reporting.annual_report import (
    DRAWDOWN_THRESHOLD_PCT,
    _drawdown_events,
    _drawdown_events_by_year,
    _treasury_path_from_book,
)
from simulation.settlement_daily import TreasuryDrawdown


def _rec(day: str, balance: float, period: int = 1) -> dict:
    return {
        "settlement_date": day,
        "settlement_period": period,
        "treasury_cash_balance_gbp": balance,
    }


def _straddling_book() -> list[dict]:
    """ONE swing, spanning a stretch of the term loop that emitted records dated in two years.

    The shape is the real one: a customer whose contract term runs across the year boundary is
    settled in one pass, so the loop emits 2022- and 2023-dated records interleaved while the
    portfolio balance makes a single peak-to-trough-to-recovery move.

    Read as one series there is exactly ONE drawdown: 1,000,000 -> 880,000 (12%) and back.
    Read as two year-buckets there are TWO, because each bucket takes its own SAMPLE of the same
    peak and the same trough — which is why the real book's two "events" had peaks four pence
    apart and troughs £12.81 apart. Those two gaps are reproduced here to the penny.
    """
    return [
        _rec("2022-11-01", 900_000.00),
        _rec("2023-01-05", 900_000.01),
        _rec("2022-11-20", 1_000_000.00),  # the peak, as 2022's records sample it
        _rec("2023-01-20", 999_999.96),    # ... and as 2023's do, four pence later
        _rec("2022-12-05", 880_012.81),    # the trough, as 2022's records sample it
        _rec("2023-02-01", 880_000.00),    # ... and as 2023's do, £12.81 lower
        _rec("2022-12-20", 1_010_000.00),  # recovery: takes out the peak, closing the drawdown
        _rec("2023-03-01", 1_020_000.00),
    ]


# ── the mechanism, demonstrated rather than inferred ────────────────────────────────────────

def test_the_year_partition_reports_one_swing_as_two_events():
    """NULL CONTROL, and the whole finding in one assertion.

    This states the PRE-REPAIR answer — what `[r['treasury_cash_balance_gbp'] for r in
    yr_records]` per year produced — and shows it is a double-count of a single swing. Without
    this the repair below is a change with no demonstrated defect behind it.
    """
    book = _straddling_book()

    per_year = {
        year: _drawdown_events([
            r["treasury_cash_balance_gbp"]
            for r in book
            if r["settlement_date"][:4] == year
        ])
        for year in ("2022", "2023")
    }

    assert len(per_year["2022"]) == 1 and len(per_year["2023"]) == 1, (
        "the fixture no longer reproduces the partition defect, so nothing below proves anything"
    )
    # The signature the finding spotted by eye on the real book: the same swing twice, its two
    # copies a few pence apart. This is the assertion that identifies the mechanism -- two
    # genuinely independent swings would not land here.
    assert per_year["2022"][0]["peak_gbp"] - per_year["2023"][0]["peak_gbp"] == pytest.approx(0.04)
    assert per_year["2022"][0]["trough_gbp"] - per_year["2023"][0]["trough_gbp"] == pytest.approx(
        12.81)
    assert per_year["2022"][0]["drawdown_pct"] == pytest.approx(0.12, abs=1e-4)
    assert per_year["2023"][0]["drawdown_pct"] == pytest.approx(0.12, abs=1e-4)


def test_one_global_walk_reports_it_once_and_dates_it_by_the_trough():
    """THE REPAIR. The same book, walked once as the portfolio series it actually is."""
    events = _drawdown_events_by_year(_treasury_path_from_book(_straddling_book()))

    assert sum(len(v) for v in events.values()) == 1, (
        f"one swing was published as {sum(len(v) for v in events.values())} events: {events}")
    assert list(events) == ["2023"], (
        "the event is dated by the year of the record at its TROUGH -- the year the treasury "
        f"was actually at its lowest -- and this says {list(events)}")
    (event,) = events["2023"]
    assert event["peak_gbp"] == pytest.approx(1_000_000.0)
    assert event["trough_gbp"] == pytest.approx(880_000.0)
    assert event["drawdown_pct"] == pytest.approx(0.12)


def test_the_run_register_and_the_retained_book_agree_on_the_straddling_swing():
    """The two paths into the same walk — the run's fold and the report's fallback — must not
    disagree, or the published count depends on which run output happens to be in hand."""
    book = _straddling_book()
    register = TreasuryDrawdown()
    register.add(book)

    assert _drawdown_events_by_year(register.points()) == _drawdown_events_by_year(
        _treasury_path_from_book(book)
    )


def test_the_register_carries_the_year_of_each_point():
    """The tag is what makes trough-attribution possible at all: strip it and the walk cannot
    date an event without re-deriving the partition it exists to avoid."""
    register = TreasuryDrawdown()
    register.add(_straddling_book())

    points = register.points()
    assert points, "the register folded nothing"
    for point in points:
        assert len(point) == 2, f"a register point lost its year tag: {point}"
        balance, year = point
        assert isinstance(balance, float)
        assert year in ("2022", "2023")


# ── the class control (R10): the shape itself is impossible after the repair ─────────────────

def test_the_published_events_are_one_walk_and_say_so():
    """THE CLASS FIX (R10). Not "this book is right" but "the shape itself is unrepresentable".

    Every published event carries `sequence`, its position in the ONE walk of the path. Two
    properties follow from there being one walk, and both are asserted here on the published
    dict rather than on a re-derivation of it:

      * the sequences across ALL years are exactly 0..n-1, no repeats — a partition restarts
        its count in every bucket, so a duplicated `sequence` IS the partition;
      * ordered by `sequence`, the peaks strictly increase — a drawdown completes only when the
        balance takes out the previous peak, and only a bucket that restarted its own peak can
        publish a later event at a lower one, which is exactly what the real 2022/2023 pair did
        (1,000,000.00 then 999,999.96).

    Asserted on a book with several genuine, well-separated drawdowns whose troughs fall in
    different years, so it is a statement about ordering rather than about an empty list.
    """
    book = [
        _rec("2022-01-01", 500_000.0),
        _rec("2023-02-01", 400_000.0),   # 20% down
        _rec("2022-06-01", 600_000.0),   # closes it, new peak
        _rec("2023-07-01", 450_000.0),   # 25% down
        _rec("2022-11-01", 700_000.0),   # closes it, new peak
        _rec("2024-12-01", 560_000.0),   # 20% down, still open at the end of the book
    ]

    events = _drawdown_events_by_year(_treasury_path_from_book(book))
    flat = [e for year in sorted(events) for e in events[year]]
    assert len(flat) == 3, f"the fixture stopped producing several drawdowns: {events}"
    assert sorted(events) == ["2023", "2024"], (
        f"the troughs no longer fall in more than one year: {sorted(events)}")

    sequences = sorted(e["sequence"] for e in flat)
    assert sequences == list(range(len(flat))), (
        f"the published events are not one walk: sequences {sequences}. A repeated sequence "
        "means some bucket restarted its own count, which is the year-partition defect in "
        "whatever form it has come back as")

    peaks = [e["peak_gbp"] for e in sorted(flat, key=lambda e: e["sequence"])]
    assert all(b > a for a, b in zip(peaks, peaks[1:])), (
        f"the published peaks are not strictly increasing in walk order: {peaks} -- a later "
        "event at a lower peak is the 2022/2023 signature this repair exists to make impossible")


def test_the_threshold_still_bites_and_is_the_published_one():
    """FAIL-OPEN guard. A walk that returned every wobble would also 'never double-count', so
    the threshold has to be shown still filtering — and to be the one the report prints."""
    shallow = [
        _rec("2022-01-01", 1_000_000.0),
        _rec("2023-01-01", 1_000_000.0 * (1 - DRAWDOWN_THRESHOLD_PCT / 2)),
        _rec("2022-02-01", 1_100_000.0),
    ]
    assert _drawdown_events_by_year(_treasury_path_from_book(shallow)) == {}

    deep = [
        _rec("2022-01-01", 1_000_000.0),
        _rec("2023-01-01", 1_000_000.0 * (1 - DRAWDOWN_THRESHOLD_PCT * 2)),
        _rec("2022-02-01", 1_100_000.0),
    ]
    assert sum(len(v) for v in _drawdown_events_by_year(
        _treasury_path_from_book(deep)).values()) == 1


def test_an_empty_or_balanceless_book_publishes_nothing_without_raising():
    """FAIL-OPEN's other face: the walk must not raise on the books it is really handed. It
    publishes nothing here because there is nothing, which is a different fact from the
    fail-open the test above guards."""
    assert _drawdown_events_by_year([]) == {}
    assert _treasury_path_from_book([{"settlement_date": "2022-01-01"}]) == []
    assert _treasury_path_from_book([{"treasury_cash_balance_gbp": 1.0}]) == []


# ── the same class control, on the PUBLISHED artefact (R11) ─────────────────────────────────
#
# `test_the_published_events_are_one_walk_and_say_so` above asserts the property on the dict
# `_drawdown_events_by_year` returns. That is the strongest form of the check and it is where
# `sequence` lives — but it is a statement about a function, and the thing this finding is
# about is a figure a reader reads. The extract that carries `sequence`
# (`docs/reports/run_output_latest.json`) is 14 MB and is not republished on the publish
# commit, so the one CURRENT published artefact is the rendered report. It renders each event
# as peak, trough and percentage, and that is enough to catch the defect's own signature: one
# swing sampled by two buckets comes out as two events whose peaks AND troughs agree to a
# rounding error, because each bucket saw the same peak and the same trough a few records
# apart. Two genuinely independent drawdowns on a book that grew £250k -> £1.75M do not.

_THRESHOLD_LINE_RE = re.compile(
    r"^- Treasury drawdown events \(>=\d+% threshold\): (?P<body>.+)$", re.MULTILINE)
_RENDERED_EVENT_RE = re.compile(
    r"£(?P<peak>-?[\d,]+\.\d\d) -> £(?P<trough>-?[\d,]+\.\d\d) \((?P<pct>-?[\d.]+)%\)")

#: Two events are the SAME SWING when their peaks and their troughs both agree to within this
#: fraction of the larger value. The real pair agreed to 3.4e-8 on the peak and 1.2e-5 on the
#: trough; 1e-3 of a >=10% drawdown is 1% of its own depth, so a pair that passes this test on
#: BOTH ends is not two swings that happened to look alike.
SAME_SWING_TOLERANCE = 1e-3

PUBLISHED_REPORT = Path(__file__).resolve().parents[3] / "docs" / "reports" / "ANNUAL_REPORT.md"


def _parse_published_drawdowns(text: str) -> tuple[int, list[tuple[float, float, float]]]:
    """(threshold lines seen, every rendered event in the whole report).

    The rendered count is checked against the number of events actually parsed out of the same
    line, so a regex that silently stops matching is a FAILURE rather than an empty result —
    R15 killer pattern 2. An empty event list is only ever reported for a report that really
    says `none` everywhere.
    """
    lines = 0
    events: list[tuple[float, float, float]] = []
    for match in _THRESHOLD_LINE_RE.finditer(text):
        lines += 1
        body = match.group("body").strip()
        if body == "none":
            continue
        count, _, rendered = body.partition(" -- ")
        parsed = [
            (
                float(m.group("peak").replace(",", "")),
                float(m.group("trough").replace(",", "")),
                float(m.group("pct")),
            )
            for m in _RENDERED_EVENT_RE.finditer(rendered)
        ]
        assert len(parsed) == int(count), (
            f"the report says {count} events on this line and this parser found "
            f"{len(parsed)} — the rendering changed and this control stopped reading it: {body[:200]}")
        events.extend(parsed)
    return lines, events


def _same_swing_pairs(
    events: list[tuple[float, float, float]],
    tolerance: float = SAME_SWING_TOLERANCE,
) -> list[tuple[tuple[float, float, float], tuple[float, float, float]]]:
    def close(a: float, b: float) -> bool:
        return abs(a - b) <= tolerance * max(abs(a), abs(b), 1.0)

    return [
        (a, b)
        for i, a in enumerate(events)
        for b in events[i + 1:]
        if close(a[0], b[0]) and close(a[1], b[1])
    ]


def test_the_published_report_never_shows_one_swing_twice():
    """R11, on the artefact a reader actually reads. This is the assertion that would have
    caught the residual: the report published at HEAD before this repair carried

        2022  £1,169,284.66 -> £1,035,944.82 (11.4%)
        2023  £1,169,284.70 -> £1,035,932.01 (11.4%)

    and nothing in the tree objected, because every control the repair had was about a
    function. `test_the_checker_fires_on_the_report_this_repair_replaced` drives those exact
    bytes through this checker and watches it refuse them.
    """
    lines, events = _parse_published_drawdowns(
        PUBLISHED_REPORT.read_text(encoding="utf-8"))

    # NOT a floor on events: a book with no drawdown at all publishes `none` on every line and
    # is a legitimate report (the end-2017 window is exactly that). The floor is on the LINES,
    # which are rendered unconditionally, so a rendering change that hides the figure from this
    # control fails here instead of passing silently.
    assert lines > 0, (
        f"no drawdown line found in {PUBLISHED_REPORT} — either the report stopped rendering "
        "the figure or this control stopped being able to see it; both are failures")

    duplicated = _same_swing_pairs(events)
    assert not duplicated, (
        f"the published report shows the same swing more than once: {duplicated}. Peaks and "
        "troughs that agree to a rounding error are one swing sampled by two buckets, which is "
        "the year-partition defect back in whatever form it has taken")


def test_the_checker_fires_on_the_report_this_repair_replaced():
    """NULL CONTROL, and not an invented one: these two lines are verbatim what
    `docs/reports/ANNUAL_REPORT.md` published before this repair reached it. A control that has
    only ever seen a clean report is a control that has never been shown to fire.
    """
    published_before = (
        "**Portfolio Health**\n"
        "\n"
        "- Treasury drawdown events (>=10% threshold): 1 -- "
        "£1,169,284.66 -> £1,035,944.82 (11.4%)\n"
        "- Treasury drawdown events (>=10% threshold): 1 -- "
        "£1,169,284.70 -> £1,035,932.01 (11.4%)\n"
    )
    lines, events = _parse_published_drawdowns(published_before)
    assert (lines, len(events)) == (2, 2)

    duplicated = _same_swing_pairs(events)
    assert len(duplicated) == 1, (
        "the checker did not refuse the pair it exists to refuse — peaks four pence apart and "
        f"troughs £12.81 apart went through: {events}")


def test_two_genuinely_distinct_swings_are_not_refused():
    """OVER-REACH guard. A checker that failed on any two events would also 'never publish one
    swing twice', and would red the first honest report with two real drawdowns in it. The pair
    here is the shape one global walk produces — a second, deeper swing off a higher peak.
    """
    distinct = (
        "- Treasury drawdown events (>=10% threshold): 2 -- "
        "£1,000,000.00 -> £880,000.00 (12.0%); £1,200,000.00 -> £1,000,000.00 (16.7%)\n"
    )
    lines, events = _parse_published_drawdowns(distinct)
    assert (lines, len(events)) == (1, 2)
    assert _same_swing_pairs(events) == []
