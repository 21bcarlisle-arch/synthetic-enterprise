"""A day must carry everything a day can, and the registers must carry the rest exactly.

WHY THIS FILE IS MOSTLY ABOUT THE FOUR EXCEPTIONS. Folding 48 half-hours into one daily row is
arithmetic, and arithmetic is easy to check. What is not easy, and is where a fold like this
goes wrong in a way nobody notices for a month, is the handful of published figures that are
computed from the half-hour itself:

  * the worst SETTLEMENT PERIOD of each year — a min over days names the worst DAY and prints
    it under a column headed "period";
  * the peak/off-peak split — a day is neither;
  * the treasury drawdown — `_drawdown_events` walks the balance after every half-hour, and a
    trough that opens and closes inside one day is simply absent from daily closes;
  * Triad exposure — looks records up by (date, period).

Each of those is a register folded during the run. The tests below check each against the
per-period computation it replaces, on the same records, rather than against a hand-worked
answer — the point is equality with what the report did before, not plausibility.

MEASURED, on a real end-2019 run (109 customer-years): 1,909,710 records -> 45,341 (42x), peak
RSS 3,003 MB -> 486 MB (84% less), elapsed 102.5s -> 70.4s, and all five headline figures
identical to the penny.

R15 — each proven by reverting, not asserted:
  * sum `treasury_cash_balance_gbp` instead of taking the day's close ->
    `test_the_treasury_balance_is_the_days_CLOSE_not_a_sum`.
  * sum a rate field -> `test_a_rate_is_carried_not_summed`.
  * take the day's FIRST period rather than its last ->
    `test_the_day_keeps_its_last_period_so_orderings_still_work`.
  * name the worst DAY -> `test_the_worst_register_names_a_half_hour_not_a_day`.
  * record every balance, or only the daily close, in the drawdown register ->
    `test_the_drawdown_register_reproduces_the_reports_own_events`.
  * drop the segment or season bound on the Triad register ->
    `test_the_triad_register_is_bounded_to_IandC_in_the_triad_season`.
"""
from __future__ import annotations

import random

import pytest

from saas.reporting.annual_report import _drawdown_events
from simulation.settlement_daily import (
    PeriodRegisters,
    TreasuryDrawdown,
    fold_to_days,
)
from simulation.tou_periods import is_peak_period


def _period(cid="C1", day="2019-01-07", period=1, kwh=0.25, revenue=0.05, net=0.01,
            treasury=1000.0, commodity="electricity", **extra):
    rec = {
        "customer_id": cid, "settlement_date": day, "settlement_period": period,
        "commodity": commodity, "data_regime": "historical",
        "consumption_kwh": kwh, "revenue_gbp": revenue, "margin_gbp": net * 2,
        "net_margin_gbp": net, "capital_cost_gbp": 0.001, "bad_debt_gbp": 0.002,
        "unit_rate_gbp_per_mwh": 150.0, "hedge_fraction": 0.85,
        "treasury_cash_balance_gbp": treasury,
    }
    rec.update(extra)
    return rec


def _day_of(cid="C1", day="2019-01-07", n=48, **kw):
    return [_period(cid=cid, day=day, period=p, treasury=1000.0 + p, **kw)
            for p in range(1, n + 1)]


# ── the arithmetic ──────────────────────────────────────────────────────────────────────────

def test_a_days_quantities_are_the_sum_of_its_periods():
    records = _day_of()
    rows = fold_to_days(records)

    assert len(rows) == 1
    row = rows[0]
    for field in ("consumption_kwh", "revenue_gbp", "margin_gbp", "net_margin_gbp",
                  "capital_cost_gbp", "bad_debt_gbp"):
        assert row[field] == pytest.approx(sum(r[field] for r in records)), field
    assert row["settlement_periods_folded"] == 48


def test_the_treasury_balance_is_the_days_CLOSE_not_a_sum():
    """A running balance's daily value is where it ENDED. Summing it would produce a treasury
    of £48,000-odd from a day that closed at £1,048, and every downstream treasury figure —
    final balance, drawdown, the administration trigger — reads it."""
    rows = fold_to_days(_day_of())

    assert rows[0]["treasury_cash_balance_gbp"] == pytest.approx(1048.0)


def test_a_rate_is_carried_not_summed():
    """A term's unit rate is a price, not a quantity accrued 48 times a day."""
    rows = fold_to_days(_day_of())

    assert rows[0]["unit_rate_gbp_per_mwh"] == pytest.approx(150.0)
    assert rows[0]["hedge_fraction"] == pytest.approx(0.85)


def test_the_day_carries_the_rate_its_consumption_was_charged_at():
    """Defect: a reader weights the day's OPENING rate by its kWh. On a ToU day that is the 00:00
    off-peak leg, so every ToU account read 11/14 of its flat rate. The weighted rate must differ
    from the opening rate on a split day and equal it on a flat one, and a day with no kWh keeps
    its opening rate rather than dividing by zero."""
    tou = [_period(period=1, kwh=1.0, unit_rate_gbp_per_mwh=110.0),
           _period(period=34, kwh=3.0, unit_rate_gbp_per_mwh=210.0)]
    (split,) = fold_to_days(tou)
    assert split["unit_rate_gbp_per_mwh"] == 110.0
    assert split["unit_rate_weighted_gbp_per_mwh"] == pytest.approx((110.0 + 3 * 210.0) / 4)
    (flat,) = fold_to_days([_period(period=p) for p in (1, 2, 3)])
    assert flat["unit_rate_weighted_gbp_per_mwh"] == flat["unit_rate_gbp_per_mwh"] == 150.0
    (idle,) = fold_to_days([_period(period=1, kwh=0.0, unit_rate_gbp_per_mwh=110.0),
                            _period(period=34, kwh=0.0, unit_rate_gbp_per_mwh=210.0)])
    assert idle["unit_rate_weighted_gbp_per_mwh"] == 110.0


def test_the_day_keeps_its_last_period_so_orderings_still_work():
    """Two downstream sites order by `(settlement_date, settlement_period)` and one takes the
    `max` of that to find a year's closing balance. Keeping the day's LAST period makes both
    behave as they did; keeping the first would silently reorder the closing row."""
    rows = fold_to_days(_day_of())

    assert rows[0]["settlement_period"] == 48


def test_customers_commodities_and_days_are_folded_separately():
    records = (_day_of(cid="C1", day="2019-01-07")
               + _day_of(cid="C2", day="2019-01-07")
               + _day_of(cid="C1", day="2019-01-08")
               + _day_of(cid="C1", day="2019-01-07", commodity="gas"))
    rows = fold_to_days(records)

    assert len(rows) == 4
    assert {(r["customer_id"], r["commodity"], r["settlement_date"]) for r in rows} == {
        ("C1", "electricity", "2019-01-07"), ("C2", "electricity", "2019-01-07"),
        ("C1", "electricity", "2019-01-08"), ("C1", "gas", "2019-01-07"),
    }


def test_a_record_with_no_settlement_date_passes_through_untouched():
    """This function's job is to make the book smaller, not to decide what counts as settled."""
    odd = {"customer_id": "C1", "note": "no date"}
    rows = fold_to_days([odd] + _day_of())

    assert odd in rows


# ── the worst half-hour ─────────────────────────────────────────────────────────────────────

def test_the_worst_register_names_a_half_hour_not_a_day():
    """THE FIGURE THIS PROTECTS. A whole report section prints the worst half-hourly settlement
    period of each year. Once the book holds days, a `min` over it names the worst DAY and
    labels it a period — a wrong number under a right-looking heading."""
    # Day A holds the worst HALF-HOUR but is a good day overall; day B is the worst DAY and
    # its worst half-hour is mild. A day-level min picks B, and B is the wrong answer.
    day_a = _day_of(day="2019-01-07", net=0.5)
    day_a[17]["net_margin_gbp"] = -5.0
    day_b = _day_of(day="2019-01-08", net=-1.0)
    registers = PeriodRegisters()
    registers.add(day_a + day_b)

    worst = registers.worst_period_by_year["2019"]
    assert worst["settlement_period"] == 18
    assert worst["settlement_date"] == "2019-01-07"
    assert worst["net_margin_gbp"] == pytest.approx(-5.0)

    rows = {r["settlement_date"]: r["net_margin_gbp"] for r in fold_to_days(day_a + day_b)}
    assert rows["2019-01-07"] > rows["2019-01-08"], (
        "the fixture does not discriminate — the worst day already IS the day holding the "
        "worst half-hour, so a day-level min would pass this test")


def test_the_worst_register_is_per_year():
    registers = PeriodRegisters()
    registers.add(_day_of(day="2019-06-01", net=-1.0) + _day_of(day="2020-06-01", net=-9.0))

    assert registers.worst_period_by_year["2019"]["net_margin_gbp"] == pytest.approx(-1.0)
    assert registers.worst_period_by_year["2020"]["net_margin_gbp"] == pytest.approx(-9.0)


# ── the peak/off-peak split ─────────────────────────────────────────────────────────────────

def test_the_tou_register_matches_a_per_period_split_exactly():
    records = _day_of(day="2019-01-07")          # a Monday, so peak bands apply
    registers = PeriodRegisters(is_peak_period=is_peak_period)
    registers.add(records)

    peak = [r for r in records if is_peak_period(r["settlement_date"], r["settlement_period"])]
    offpeak = [r for r in records
               if not is_peak_period(r["settlement_date"], r["settlement_period"])]
    bucket = registers.tou_by_customer["C1"]

    assert bucket["total_kwh"] == pytest.approx(sum(r["consumption_kwh"] for r in records))
    assert bucket["peak_kwh"] == pytest.approx(sum(r["consumption_kwh"] for r in peak))
    assert bucket["peak_revenue_gbp"] == pytest.approx(sum(r["revenue_gbp"] for r in peak))
    assert bucket["offpeak_revenue_gbp"] == pytest.approx(sum(r["revenue_gbp"] for r in offpeak))
    assert 0 < bucket["peak_kwh"] < bucket["total_kwh"], (
        "the fixture has no peak periods in it, so this proves nothing")


def test_the_two_peak_band_definitions_still_agree():
    """The world's copy priced the revenue; the company's copy split it in the report. They are
    independent readings of a published Elexon convention (REGULATION_COMMONS_DOCTRINE) and
    they agree today. If one ever moves, `tou_stats` changes — and it should change as a red
    test here, not as a figure nobody noticed shifting."""
    from company.market.tou_periods import is_peak_period as company_is_peak

    for day in ("2019-01-07", "2019-01-12", "2019-06-19", "2022-12-25"):
        for period in range(1, 49):
            assert is_peak_period(day, period) == company_is_peak(day, period), (
                "the world and the company now disagree about {} period {}".format(day, period))


# ── the treasury path ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_the_drawdown_register_reproduces_the_reports_own_events(seed):
    """THE PROPERTY THAT MAKES THE REGISTER LOSSLESS. `_drawdown_events` state is exactly
    (peak, trough): a value strictly between them changes nothing. So keeping only the values
    that move one of the two is enough to replay it — and this asserts that against the real
    function on random walks, not against my reasoning about it."""
    rng = random.Random(seed)
    balance = 250_000.0
    records, series = [], []
    for i in range(2000):
        balance += rng.uniform(-4000, 3800)
        series.append(balance)
        records.append(_period(day="2019-%02d-%02d" % (i // 200 + 1, i % 28 + 1),
                               period=i % 48 + 1, treasury=balance))

    register = TreasuryDrawdown()
    register.add(records)

    assert _drawdown_events([p[0] for p in register.points()]) == _drawdown_events(series)
    assert len(register.points()) < len(series), (
        "the register kept every point, so it is not saving anything")


def _uncollapsed_register(records) -> list[list]:
    """The register as it was before 2026-10-06, verbatim: every new running peak and every new
    low beneath the last point, appended. The reference the collapsed one must walk identically to."""
    points, peak = [], None
    for rec in records:
        balance, day = rec.get("treasury_cash_balance_gbp"), rec.get("settlement_date")
        if balance is None or not day:
            continue
        if peak is None or balance > peak:
            points.append([balance, day[:4]])
            peak = balance
        elif balance < points[-1][0]:
            points.append([balance, day[:4]])
    return points


def _trending_walk(seed: int, n: int = 6000) -> list[dict]:
    """A treasury that mostly CLIMBS, with dips, across three years -- the shape that made the old
    register O(periods): long runs of consecutive new peaks, and runs of consecutive new lows."""
    rng = random.Random(seed)
    balance, records = 250_000.0, []
    for i in range(n):
        balance += rng.uniform(-900, 1000) if i % 400 > 40 else rng.uniform(-600, 200)
        year = 2019 + i * 3 // n
        records.append(_period(day="%d-%02d-%02d" % (year, i % 12 + 1, i % 28 + 1),
                               period=i % 48 + 1, treasury=balance))
    return records


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_the_collapsed_register_walks_to_the_same_events(seed):
    """LOSSLESS, asserted against the consumer rather than argued: the report's own by-year walk
    over the collapsed register and over the uncollapsed one gives identical events -- peaks,
    troughs, percentages, years and sequence numbers -- at five thresholds, one of which (0.0)
    makes every dip an event so a lost turning point cannot hide below the threshold."""
    from saas.reporting.annual_report import _drawdown_events_by_year

    records = _trending_walk(seed)
    register = TreasuryDrawdown()
    for start in range(0, len(records), 500):  # fed in terms, as the run feeds it
        register.add(records[start:start + 500])
    collapsed, reference = register.points(), _uncollapsed_register(records)

    event_counts = []
    for threshold in (0.0, 1e-4, 1e-3, 1e-2, 0.05):
        ours = _drawdown_events_by_year(collapsed, threshold=threshold)
        theirs = _drawdown_events_by_year(reference, threshold=threshold)
        assert ours == theirs, f"threshold {threshold}: the collapse changed the events"
        event_counts.append(sum(len(v) for v in theirs.values()))
    assert event_counts[0] > 20, "the walk has too few drawdowns for the comparison to bite"
    assert len(collapsed) < len(reference) / 2, (
        f"{len(collapsed)} of {len(reference)} points kept: the runs were not collapsed")


def test_a_rising_treasury_is_one_point_not_one_per_period():
    """The defect at its plainest: a balance that only climbs has no drawdown and needs one point.
    The old register held one per period -- 1,258,193 on the measured book."""
    register = TreasuryDrawdown()
    register.add([_period(period=p % 48 + 1, treasury=1000.0 + p) for p in range(500)])
    assert register.points() == [[1499.0, "2019"]]


def test_an_intra_day_trough_survives_the_register_and_not_the_daily_close():
    """The concrete reason the register exists: a dip that opens and closes inside one day."""
    day = _day_of(day="2019-03-04")
    for i, rec in enumerate(day):
        rec["treasury_cash_balance_gbp"] = 100_000.0 if i != 24 else 10_000.0

    register = TreasuryDrawdown()
    register.add(day)

    assert _drawdown_events([p[0] for p in register.points()]), "the intra-day trough was lost"
    daily_close = [fold_to_days(day)[0]["treasury_cash_balance_gbp"]]
    assert not _drawdown_events(daily_close), (
        "the fixture does not demonstrate the problem — the daily close sees the trough too")


# ── the Triad carve-out ─────────────────────────────────────────────────────────────────────

def test_the_triad_register_is_bounded_to_IandC_in_the_triad_season():
    """It keeps whole records, so an unbounded version is the memory problem again. Bounded two
    ways — segment and season — and both bounds are asserted."""
    registers = PeriodRegisters()
    segments = {"IC1": "I&C", "R1": "resi"}
    registers.add(_day_of(cid="IC1", day="2019-12-02"), segment_of=segments)   # kept
    registers.add(_day_of(cid="IC1", day="2019-07-02"), segment_of=segments)   # wrong season
    registers.add(_day_of(cid="R1", day="2019-12-02"), segment_of=segments)    # wrong segment

    kept = registers.triad_records
    assert kept, "the Triad register kept nothing at all"
    assert {r["customer_id"] for r in kept} == {"IC1"}
    assert {r["settlement_date"][5:7] for r in kept} == {"12"}
    assert all(r.get("settlement_period") is not None for r in kept), (
        "the register kept rows without a period, which is the one thing Triad needs")
