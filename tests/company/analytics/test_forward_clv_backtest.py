"""B11: the forward-value backtest fits only on the past, grades on the held-back years, and
puts the flat rule beside it on the same accounts."""

from __future__ import annotations

from pathlib import Path

import pytest

from company.analytics.forward_clv import (
    DEFAULT_CUT_YEAR,
    LIMITATION_DEPARTURE_CAUSE,
    AccountHistory,
    _fit_hazards,
    _month_index,
    _paired,
    backtest_run_output,
    load_book,
    regime_boundary_month,
    run_backtest,
)

REPO = Path(__file__).resolve().parents[3]
TRACKED_RUN = REPO / "docs" / "reports" / "run_output_latest.json"


def _acct(aid, segment, start, end, value):
    """`value` is a constant or a function of the month index."""
    f = value if callable(value) else (lambda m, v=value: v)
    return AccountHistory(
        aid, segment, {m: f(m) for m in range(_month_index(start), _month_index(end) + 1)}
    )


def _book():
    """Two segments, spread in margin within each, departures before and after the cut."""
    return [
        _acct("A1", "resi electricity", "2016-01", "2025-06", 10.0),
        _acct("A2", "resi electricity", "2016-01", "2025-06", 30.0),
        _acct("A3", "resi electricity", "2016-01", "2022-05", lambda m: 18.0 + (m % 3)),
        _acct("A4", "resi electricity", "2016-01", "2019-08", 20.0),  # left before the cut
        _acct("A5", "resi electricity", "2017-04", "2023-09", lambda m: 25.0 + (m % 2)),
        _acct("B1", "resi dual", "2016-01", "2025-06", lambda m: 40.0 + (m % 4)),
        _acct("B2", "resi dual", "2018-01", "2021-03", lambda m: 5.0 + (m % 5)),
        _acct("B3", "resi dual", "2016-06", "2018-02", 12.0),  # left before the cut
        _acct("N1", "resi dual", "2022-01", "2025-06", 50.0),  # joined after the cut
    ]


def test_the_forecast_reads_nothing_after_the_cut():
    """The defect: a backtest that peeks at held-back months grades its own answer.

    Rewriting every month after the cut must leave every forecast unchanged and move
    only what it is graded against.
    """
    book = _book()
    end = max(a.last_month for a in book)
    cut_end = _month_index(f"{DEFAULT_CUT_YEAR}-12")
    altered = [
        AccountHistory(
            a.account_id,
            a.segment,
            {m: (v if m <= cut_end else v * 7 - 300) for m, v in a.monthly_net_gbp.items()},
        )
        for a in book
    ]
    before, after = run_backtest(book, end), run_backtest(altered, end)
    for f0, f1 in zip(before.forecasts, after.forecasts):
        assert f0.per_customer_margin_gbp == f1.per_customer_margin_gbp
        assert f0.flat_margin_gbp == f1.flat_margin_gbp
        assert f0.per_customer_departure_p == f1.per_customer_departure_p
    assert [f.realised_margin_gbp for f in before.forecasts] != [
        f.realised_margin_gbp for f in after.forecasts
    ]


def test_a_last_month_at_the_cut_is_censored_not_a_departure():
    """The defect: counting every account still on supply at the cut as having left."""
    cut_end = _month_index("2020-12")
    on_at_cut = [_acct(f"S{i}", "resi electricity", "2016-01", "2023-01", 1.0) for i in range(3)]
    by_cy, by_seg, _ = _fit_hazards(on_at_cut, cut_end)
    assert by_seg["resi electricity"] == 0.0
    left = on_at_cut + [_acct("L", "resi electricity", "2016-01", "2018-06", 1.0)]
    _, by_seg_left, _ = _fit_hazards(left, cut_end)
    assert by_seg_left["resi electricity"] > 0.0


def test_a_trailing_contract_year_with_no_exit_is_folded_not_read_as_nil():
    cut_end = _month_index("2020-12")
    book = [
        _acct("X1", "resi dual", "2016-01", "2016-08", 1.0),  # exits in contract year 0
        _acct("X2", "resi dual", "2016-01", "2020-12", 1.0),  # censored, reaches year 4
    ]
    by_cy, _, _ = _fit_hazards(book, cut_end)
    assert list(by_cy) == [0]
    assert by_cy[0] > 0.0


def test_the_graded_population_is_the_book_on_supply_at_the_cut():
    bt = run_backtest(_book(), _month_index("2025-06"))
    assert {f.account_id for f in bt.forecasts} == {"A1", "A2", "A3", "A5", "B1", "B2"}
    assert bt.accounts_excluded == {
        "joined after the cut (no fit history)": 1,
        "left before the cut": 2,
    }
    departed = {f.account_id for f in bt.forecasts if f.departed}
    assert departed == {"A3", "A5", "B2"}


def test_both_credibility_branches_are_reachable_and_pooling_equals_flat():
    """A spread segment shrinks partway; a segment with no between-account spread pools fully,
    and then the per-customer margin IS the flat margin — said in the limitations."""
    spread = run_backtest(_book(), _month_index("2025-06"))
    weights = {f.credibility_weight for f in spread.forecasts}
    assert any(0.0 < w < 1.0 for w in weights)
    same = [_acct(f"P{i}", "resi gas", "2016-01", "2025-06", lambda m: 9.0 + (m % 6)) for i in range(4)]
    pooled = run_backtest(same, _month_index("2025-06"))
    assert pooled.shrinkage_k_by_segment["resi gas"] is None
    assert all(f.credibility_weight == 0.0 for f in pooled.forecasts)
    assert all(
        f.per_customer_margin_gbp == pytest.approx(f.flat_margin_gbp) for f in pooled.forecasts
    )
    assert any("resi gas" in lim for lim in pooled.limitations)


def test_every_verdict_of_the_paired_comparison_is_reachable():
    """The rare branches are asserted reachable before anything leans on them."""
    verdicts = {
        _paired("m", [1.0, 1.1, 0.9, 1.0], [2.0, 2.1, 1.9, 2.0]).verdict,
        _paired("m", [2.0, 2.1, 1.9, 2.0], [1.0, 1.1, 0.9, 1.0]).verdict,
        _paired("m", [1.0, 2.0, 1.0, 2.0], [2.0, 1.0, 2.0, 1.0]).verdict,
        _paired("m", [1.0], [2.0]).verdict,
    }
    assert "per-customer better" in verdicts and "flat better" in verdicts
    assert sum(v.startswith("cannot tell") for v in verdicts) == 2


def test_a_cut_with_no_held_back_months_is_refused_with_its_reason():
    with pytest.raises(ValueError, match="no held-back months"):
        run_backtest(_book(), _month_index("2025-06"), cut_year=2025)


@pytest.mark.skipif(not TRACKED_RUN.exists(), reason="no run output in this checkout")
def test_the_backtest_runs_on_a_real_book_and_carries_its_limitation():
    """Keyed to properties, not to today's verdict: the verdict is the finding, and it moves
    with the run."""
    accounts, book_end = load_book(TRACKED_RUN)
    bt = run_backtest(accounts, book_end)
    assert bt.cut_year == DEFAULT_CUT_YEAR
    assert bt.accounts_graded > 0
    assert LIMITATION_DEPARTURE_CAUSE in bt.limitations
    for comparison in (bt.margin_error, bt.departure_brier):
        assert comparison.n == bt.accounts_graded
        assert comparison.interval_95 is not None
    # What the grading counts as realised is exactly the ledger's held-back margin.
    cut_end = _month_index(f"{DEFAULT_CUT_YEAR}-12")
    graded = {f.account_id for f in bt.forecasts}
    ledger = sum(
        v for a in accounts if a.account_id in graded for m, v in a.monthly_net_gbp.items() if m > cut_end
    )
    assert bt.aggregate["realised_margin_gbp"] == pytest.approx(ledger)
    assert backtest_run_output(TRACKED_RUN).accounts_graded == bt.accounts_graded


def _reversing_pair():
    """Two accounts that swap places in 2021-22 and never leave, so every hazard is nil and a
    forecast is its monthly rate times the horizon."""
    crisis = (_month_index("2021-01"), _month_index("2022-12"))

    def path(early, during):
        return lambda m: (during if crisis[0] <= m <= crisis[1] else early) + (m % 2)

    return [
        _acct("R1", "resi electricity", "2016-01", "2025-06", path(10.0, 100.0)),
        _acct("R2", "resi electricity", "2016-01", "2025-06", path(30.0, -40.0)),
    ]


def test_the_margin_deviation_is_read_only_from_its_own_window():
    """The defect: a deviation window that still reads the crisis years tests nothing.

    Fitted through 2022, R1 sits above its segment. With the deviation taken from 2016-2020,
    R2 does, and the two forecasts still average to the flat rule's level, because only the
    deviation moved and the level is the one fitted through the cut.
    """
    book = _reversing_pair()
    end = max(a.last_month for a in book)
    shipped = {f.account_id: f for f in run_backtest(book, end, 2022).forecasts}
    early = run_backtest(book, end, 2022, margin_fit_end_year=2020)
    by_id = {f.account_id: f for f in early.forecasts}
    assert shipped["R1"].per_customer_margin_gbp > shipped["R2"].per_customer_margin_gbp
    assert by_id["R2"].per_customer_margin_gbp > by_id["R1"].per_customer_margin_gbp
    assert by_id["R1"].per_customer_margin_gbp + by_id["R2"].per_customer_margin_gbp == (
        pytest.approx(2 * by_id["R1"].flat_margin_gbp))
    assert early.margin_deviation_fit_months == ("2016-01", "2020-12")


def test_the_deviation_window_at_the_cut_is_the_rule_as_first_shipped():
    book = _book()
    end = max(a.last_month for a in book)
    default, explicit = run_backtest(book, end, 2020), run_backtest(book, end, 2020, 2020)
    assert default.forecasts == explicit.forecasts


def test_a_deviation_window_past_the_cut_is_refused_with_its_reason():
    book = _book()
    with pytest.raises(ValueError, match="after the cut"):
        run_backtest(book, max(a.last_month for a in book), 2020, margin_fit_end_year=2021)


def test_an_account_with_no_month_in_the_deviation_window_takes_its_segment():
    book = _reversing_pair() + [
        _acct("R3", "resi electricity", "2021-06", "2025-06", lambda m: 70.0 + (m % 2))]
    end = max(a.last_month for a in book)
    late = {f.account_id: f for f in run_backtest(book, end, 2022, 2020).forecasts}
    assert late["R3"].credibility_weight == 0.0
    assert late["R1"].credibility_weight > 0.0


def _gas(**at):
    """A flat wholesale record from 2016 with the named months set: `_gas(y2018_09=25.0)`."""
    series = {f"{y}-{m:02d}": 10.0 for y in range(2016, 2026) for m in range(1, 13)}
    series.update({k[1:].replace("_", "-"): v for k, v in at.items()})
    return series


def test_the_regime_boundary_is_the_first_all_time_high_on_or_after_the_anchor():
    """A high set BEFORE the anchor is the bar, not the boundary; a month that only beats the
    post-anchor months is not an all-time high; the cut never reads past itself."""
    gas = _gas(y2018_09=25.0, y2019_01=19.0, y2021_01=19.5, y2021_06=27.5)
    assert regime_boundary_month(gas, _month_index("2022-12")) == _month_index("2021-06")
    assert regime_boundary_month(gas, _month_index("2021-05")) is None
    with pytest.raises(ValueError, match="needs a record before the anchor"):
        regime_boundary_month({"2019-06": 1.0, "2020-01": 2.0}, _month_index("2022-12"))


def test_a_read_window_ends_the_month_before_the_boundary_and_both_branches_are_reachable():
    """Read at 2021-01 it is exactly the chosen 2016-2020 window; with no high by the cut it is
    exactly the rule as shipped. The two sources together are refused."""
    book = _reversing_pair()
    end = max(a.last_month for a in book)
    read = run_backtest(book, end, 2022, wholesale_gas_by_month=_gas(y2021_01=99.0))
    chosen = run_backtest(book, end, 2022, margin_fit_end_year=2020)
    assert read.forecasts == chosen.forecasts
    assert read.margin_deviation_fit_months == ("2016-01", "2020-12")
    assert "2021-01" in read.margin_deviation_window_reason
    unread = run_backtest(book, end, 2022, wholesale_gas_by_month=_gas(y2023_03=99.0))
    assert unread.forecasts == run_backtest(book, end, 2022).forecasts
    assert unread.margin_deviation_fit_months == ("2016-01", "2022-12")
    assert read.forecasts != unread.forecasts
    with pytest.raises(ValueError, match="give one"):
        run_backtest(book, end, 2022, 2020, wholesale_gas_by_month=_gas())
