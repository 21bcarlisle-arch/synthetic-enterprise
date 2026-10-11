"""B11: the forward-value backtest fits only on the past, grades on the held-back years, and
puts the flat rule beside it on the same accounts."""

from __future__ import annotations

from pathlib import Path

import pytest

from company.analytics.forward_clv import (
    DEFAULT_CUT_YEAR,
    HELD_BACK_OUTCOMES,
    LIMITATION_DEPARTURE_CAUSE,
    LIMITATION_NO_MOVE_REGISTER,
    LIMITATION_SWITCH_LEVEL_IS_THE_REGIME,
    AccountForecast,
    AccountHistory,
    _fit_hazards,
    _hazard_at,
    _month_index,
    _paired,
    _ranking,
    backtest_run_output,
    exit_cells,
    load_book,
    move_outs_from_run_output,
    pooled_ratio,
    regime_boundary_month,
    run_backtest,
    standardised_ratios,
)
from tools.run_output_store import as_plain_file, resolve_run_output

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


@pytest.fixture(scope="module")
def tracked_run(tmp_path_factory) -> Path:
    """The tracked run as a plain file; the committed form is gzipped (`tools.run_output_store`)
    and `company/` reads paths, so a gz-only checkout is decompressed to scratch here."""
    return as_plain_file(TRACKED_RUN, tmp_path_factory.mktemp("run"))


@pytest.mark.skipif(resolve_run_output(TRACKED_RUN) is None,
                    reason="no run output in this checkout")
def test_the_backtest_runs_on_a_real_book_and_carries_its_limitation(tracked_run):
    """Keyed to properties, not to today's verdict: the verdict is the finding, and it moves
    with the run."""
    accounts, book_end = load_book(tracked_run)
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
    assert backtest_run_output(tracked_run).accounts_graded == bt.accounts_graded


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


def _movers_book():
    """One stayer; a move and a switch on each side of the cut; a switch before a later move."""
    return [
        _acct("S1", "resi electricity", "2016-01", "2025-06", 10.0),
        _acct("M1", "resi electricity", "2016-01", "2019-03", 12.0),
        _acct("W1", "resi electricity", "2016-01", "2019-07", 11.0),
        _acct("W2", "resi electricity", "2016-01", "2018-05", 13.0),
        _acct("M2", "resi electricity", "2017-01", "2022-04", 14.0),
        _acct("W3", "resi electricity", "2017-01", "2023-02", 15.0),
    ]


_MOVE_REGISTER = {"home_move_outs": [
    {"household": "M1", "move_date": "2019-03-17", "journey_state": "content", "catchable": False},
    {"household": "W2", "move_date": "2020-02-10"},
    {"household": "M2", "move_date": "2022-05-01"},  # supply ends the day before: April
]}


def test_departures_split_by_cause_and_both_causes_are_reachable_in_both_windows():
    """The defect: a split that files every departure under one cause. W2 left by switching
    in 2018 and has a 2020 move date; only the month supply actually ended can make it a move."""
    book = _movers_book()
    bt = run_backtest(book, _month_index("2025-06"),
                      move_out_month_by_account=move_outs_from_run_output(_MOVE_REGISTER))
    assert bt.departures_by_cause == {
        "fit": {"switch": 2, "move": 1}, "held_back": {"switch": 1, "move": 1}}
    assert LIMITATION_DEPARTURE_CAUSE not in bt.limitations


def test_the_switch_hazard_censors_a_move_and_the_forecast_does_not_move():
    """A move is at risk to its date and is not a switch. Survival stays all-cause, because
    margin stops however the account leaves."""
    book = _movers_book()
    end = _month_index("2025-06")
    plain = run_backtest(book, end)
    split = run_backtest(book, end, move_out_month_by_account=move_outs_from_run_output(_MOVE_REGISTER))
    m1_year = (_month_index("2019-03") - _month_index("2016-01")) // 12
    assert split.switch_hazard_by_contract_year[m1_year] < plain.hazard_by_contract_year[m1_year]
    assert split.switch_hazard_by_contract_year == _fit_hazards(
        book, _month_index("2020-12"), frozenset({"M1", "M2"}))[0]
    assert [f.per_customer_departure_p for f in split.forecasts] == [
        f.per_customer_departure_p for f in plain.forecasts]


def test_no_register_is_none_with_its_reason_and_an_empty_one_is_zero_moves():
    """The defect: "the world has no moves" read as "nobody moved"."""
    assert move_outs_from_run_output({}) is None
    assert move_outs_from_run_output({"home_move_outs": []}) == {}
    book, end = _movers_book(), _month_index("2025-06")
    absent = run_backtest(book, end)
    assert absent.departures_by_cause is None and absent.switch_hazard_by_contract_year is None
    assert absent.error_by_outcome is None
    assert LIMITATION_NO_MOVE_REGISTER in absent.limitations
    empty = run_backtest(book, end, move_out_month_by_account={})
    assert empty.departures_by_cause["fit"]["move"] == 0
    assert empty.switch_hazard_by_contract_year == absent.hazard_by_contract_year
    assert LIMITATION_NO_MOVE_REGISTER not in empty.limitations


def test_every_held_back_outcome_is_reachable_and_each_is_graded_on_its_own_accounts():
    """The defect: a split whose mover leg is never taken grades the book as if moves were
    switches. W4 switched in 2023 with a 2024 move date: only the month supply ended decides."""
    book = _movers_book() + [_acct("W4", "resi electricity", "2016-01", "2023-08", 16.0)]
    register = {"home_move_outs": [*_MOVE_REGISTER["home_move_outs"],
                                   {"household": "W4", "move_date": "2024-03-01"}]}
    bt = run_backtest(book, _month_index("2025-06"),
                      move_out_month_by_account=move_outs_from_run_output(register))
    grades = bt.error_by_outcome
    assert grades["stayer"].accounts and grades["switcher"].accounts and grades["mover"].accounts
    assert {o: grades[o].accounts for o in HELD_BACK_OUTCOMES} == {
        "stayer": 1, "switcher": 2, "mover": 1}
    assert sum(g.accounts for g in grades.values()) == bt.accounts_graded
    f = {x.account_id: x for x in bt.forecasts}
    m2, s1 = f["M2"], f["S1"]
    assert grades["mover"].margin_error.per_customer == abs(
        m2.per_customer_margin_gbp - m2.realised_margin_gbp)
    assert grades["stayer"].ranking_against_stayers is None
    mover_rank = grades["mover"].ranking_against_stayers
    assert (mover_rank.departers, mover_rank.stayers) == (1, 1)
    assert mover_rank.verdict.startswith("cannot tell") and s1.departed is False
    assert grades["mover"].margin_bias["flat"][0] == m2.flat_margin_gbp - m2.realised_margin_gbp
    assert grades["switcher"].margin_error.interval_95 is not None


def test_the_run_output_door_passes_the_register_through(tracked_run):
    """The defect: the split built and the path from a run's report never handing it over."""
    import json
    import tempfile
    run = json.loads(tracked_run.read_text())
    accounts, _ = load_book(tracked_run)
    leaver = next(a for a in accounts if a.last_month < max(x.last_month for x in accounts))
    ym = leaver.last_month + 1
    run["home_move_outs"] = [{"household": leaver.account_id,
                              "move_date": f"{ym // 12:04d}-{ym % 12 + 1:02d}-01"}]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(run, fh)
    bt = backtest_run_output(fh.name)
    Path(fh.name).unlink()
    assert sum(w["move"] for w in bt.departures_by_cause.values()) == 1


def _fc(aid, pc, fl, departed):
    return AccountForecast(aid, "resi dual", 60, 0.0, 0.0, 0.0, 0.0, pc, fl, departed)


def test_the_ranking_is_a_hand_count_and_does_not_read_the_level():
    """The defect slice 5 shipped: a departure score inside one outcome that grades only the
    level. Adding a constant to every p must leave the AUC where it is and move only the
    calibration; ties count a half."""
    leavers = [_fc("D1", 0.6, 0.5, True), _fc("D2", 0.4, 0.5, True), _fc("D3", 0.7, 0.2, True)]
    stayers = [_fc("S1", 0.4, 0.5, False), _fc("S2", 0.3, 0.6, False)]
    r = _ranking(leavers, stayers)
    # per-customer: D1 beats both, D2 ties S1 and beats S2, D3 beats both -> 5.5 of 6.
    assert r.per_customer[0] == pytest.approx(5.5 / 6)
    # flat: D1 ties S1 and loses to S2, D2 likewise, D3 loses to both -> 1 of 6.
    assert r.flat[0] == pytest.approx(1 / 6)
    shifted = _ranking(*[[_fc(f.account_id, f.per_customer_departure_p + 0.2,
                              f.flat_departure_p + 0.2, f.departed) for f in g]
                         for g in (leavers, stayers)])
    assert shifted.per_customer[0] == pytest.approx(r.per_customer[0])
    assert shifted.difference[0] == pytest.approx(r.difference[0])


def test_every_ranking_verdict_is_reachable():
    """Both wins, a straddle, and too few to bound -- asserted over the whole partition."""
    def book(pc_gap, fl_gap, noise):
        leave = [_fc(f"D{i}", 0.5 + pc_gap + noise * (i % 3), 0.5 + fl_gap + noise * (i % 2), True)
                 for i in range(12)]
        stay = [_fc(f"S{i}", 0.5 + noise * (i % 4), 0.5 + noise * (i % 5), False) for i in range(12)]
        return leave, stay
    verdicts = {
        _ranking(*book(0.3, 0.0, 0.01)).verdict,
        _ranking(*book(0.0, 0.3, 0.01)).verdict,
        _ranking(*book(0.0, 0.0, 0.1)).verdict,
        _ranking(*[g[:1] for g in book(0.3, 0.0, 0.01)]).verdict,
    }
    assert "per-customer ranks better" in verdicts and "flat ranks better" in verdicts
    assert sum(v.startswith("cannot tell") for v in verdicts) == 2


def test_calibration_in_the_large_is_mean_p_minus_the_realised_rate():
    bt = run_backtest(_book(), _month_index("2025-06"))
    rate = sum(f.departed for f in bt.forecasts) / bt.accounts_graded
    for rule, attr in (("per_customer", "per_customer_departure_p"), ("flat", "flat_departure_p")):
        mean_p = sum(getattr(f, attr) for f in bt.forecasts) / bt.accounts_graded
        assert bt.departure_calibration[rule][0] == pytest.approx(mean_p - rate)
        assert bt.departure_calibration[rule][1] is not None
    assert bt.departure_ranking.departers + bt.departure_ranking.stayers == bt.accounts_graded


def test_a_left_truncated_hazard_window_drops_early_exits_and_keeps_tenure():
    """The defect: a recency window that still counts the early years' exits, or that restarts
    every account's tenure at the window's start."""
    cut_end = _month_index("2020-12")
    book = [
        _acct("E1", "resi dual", "2016-01", "2016-06", 1.0),  # exits before the window
        _acct("L1", "resi dual", "2016-01", "2020-06", 1.0),  # exits inside it, contract year 4
        _acct("C1", "resi dual", "2016-01", "2023-01", 1.0),
    ]
    whole, _, _ = _fit_hazards(book, cut_end)
    recent, _, _ = _fit_hazards(book, cut_end, fit_start=_month_index("2020-01"))
    assert whole[0] > 0.0
    assert list(recent) == [4] and recent[4] == pytest.approx(1 / (6 + 12))
    assert _hazard_at(recent, 0) == recent[4]
    with pytest.raises(ValueError, match="needs months at risk"):
        _fit_hazards(book[:1], cut_end, fit_start=_month_index("2020-01"))


def test_the_hazard_window_moves_only_the_departure_and_is_refused_past_the_cut():
    book = _book()
    end = _month_index("2025-06")
    default, from_start = run_backtest(book, end), run_backtest(book, end, hazard_fit_from_year=2016)
    assert default.forecasts == from_start.forecasts
    recent = run_backtest(book, end, hazard_fit_from_year=2019)
    assert recent.hazard_fit_months == ("2019-01", "2020-12")
    # The margin forecast is survival-weighted, so it moves with the hazard; its fit does not.
    assert [f.credibility_weight for f in recent.forecasts] == [
        f.credibility_weight for f in default.forecasts]
    assert [f.flat_departure_p for f in recent.forecasts] != [f.flat_departure_p for f in default.forecasts]
    with pytest.raises(ValueError, match="after the cut"):
        run_backtest(book, end, hazard_fit_from_year=2021)


def test_the_calendar_year_record_adds_up_to_the_book_and_splits_by_cause():
    book, end = _movers_book(), _month_index("2025-06")
    bt = run_backtest(book, end, move_out_month_by_account=move_outs_from_run_output(_MOVE_REGISTER))
    rows = bt.departures_by_calendar_year
    assert sum(r["months_at_risk"] for r in rows.values()) == sum(len(a.monthly_net_gbp) for a in book)
    assert sum(r["departures"] for r in rows.values()) == sum(a.last_month < end for a in book)
    assert all(r["switch"] + r["move"] == r["departures"] for r in rows.values())
    assert rows[2019] == {"months_at_risk": 12 + 3 + 7 + 12 + 12, "departures": 2, "switch": 1, "move": 1}
    assert "switch" not in run_backtest(book, end).departures_by_calendar_year[2019]


def test_the_level_split_by_cause_sums_to_the_flat_p_and_each_cause_reads_its_own_exits():
    """The defect: a cause split that re-fits the level instead of dividing it, or a move hazard
    that counts switches. In the fit window M1 moved and W1, W2 switched over 267 months at risk,
    so every account's switch incidence is exactly twice its move incidence. W4 makes the held-back
    switchers outnumber the movers, so a split that swaps the realised causes cannot pass."""
    book = _movers_book() + [_acct("W4", "resi electricity", "2016-01", "2023-08", 16.0)]
    register = {"home_move_outs": [*_MOVE_REGISTER["home_move_outs"],
                                   {"household": "W4", "move_date": "2024-03-01"}]}
    end = _month_index("2025-06")
    bt = run_backtest(book, end, move_out_month_by_account=move_outs_from_run_output(register))
    inc, cal = bt.departure_incidence_by_cause, bt.departure_calibration_by_cause
    assert inc["switch"][0] > 0.0 and inc["move"][0] > 0.0
    assert inc["switch"][0] == pytest.approx(2 * inc["move"][0])
    mean_flat_p = sum(f.flat_departure_p for f in bt.forecasts) / bt.accounts_graded
    assert inc["switch"][0] + inc["move"][0] == pytest.approx(mean_flat_p)
    grades = bt.error_by_outcome
    assert inc["switch"][1] == grades["switcher"].accounts / bt.accounts_graded
    assert inc["move"][1] == grades["mover"].accounts / bt.accounts_graded
    for cause in ("switch", "move"):
        assert cal[cause][0] == pytest.approx(inc[cause][0] - inc[cause][1])
    assert LIMITATION_SWITCH_LEVEL_IS_THE_REGIME in bt.limitations
    absent = run_backtest(book, end)
    assert absent.departure_incidence_by_cause is None
    assert absent.departure_calibration_by_cause is None
    assert LIMITATION_SWITCH_LEVEL_IS_THE_REGIME not in absent.limitations


def test_an_oldest_contract_year_fitted_on_one_calendar_year_is_named_and_both_branches_reach():
    """The defect: a per-customer level read as tenure when the oldest contract year, which
    holds for all later tenure, was fitted on the cut year alone -- the real book's shape at
    every cut. Opened in January with an exit in 2020, the fifth contract year is 2020 alone.
    Opened in July with the exit in 2019, the fifth year has none and folds into the fourth,
    which spans 2019-07..2020-06, so nothing is named."""
    end = _month_index("2025-06")

    def book(start, exit_at):
        return [
            _acct("J1", "resi dual", start, "2025-06", 10.0),
            _acct("J2", "resi dual", start, "2016-09", 10.0),
            _acct("J3", "resi dual", start, exit_at, 10.0),
            _acct("J4", "resi dual", start, "2023-02", 10.0),
        ]

    jan = run_backtest(book("2016-01", "2020-05"), end)
    named = [m for m in jan.limitations if "oldest contract year" in m]
    assert max(jan.hazard_by_contract_year) == 4
    assert len(named) == 1 and "(4) is fitted on 2020 alone" in named[0]
    july = run_backtest(book("2016-07", "2019-10"), end)
    assert max(july.hazard_by_contract_year) == 3
    assert not [m for m in july.limitations if "oldest contract year" in m]


def test_exit_cells_key_each_month_by_its_calendar_and_contract_year_and_only_exits_leave():
    """The defect: an exit counted in the wrong cell, or the book's edge (or a move) read as
    one, moves the ratio the tenure-against-calendar test reads."""
    end = _month_index("2025-06")
    book = [
        _acct("S", "resi dual", "2016-07", "2018-03", 1.0),  # exits 2018, contract year 1
        _acct("C", "resi dual", "2024-01", "2025-06", 1.0),  # on supply at the edge
        _acct("M", "resi dual", "2024-01", "2024-04", 1.0),  # moved, censored
    ]
    cells = exit_cells(book, end, censored=frozenset({"M"}))
    assert cells[(2016, 0)] == (6, 0)
    assert cells[(2017, 0)] == (6, 0) and cells[(2017, 1)] == (6, 0)
    assert cells[(2018, 1)] == (3, 1)
    assert cells[(2024, 0)] == (12 + 4, 0) and cells[(2025, 1)] == (6, 0)
    assert sum(e for _, e in cells.values()) == 1


def test_a_contract_year_ratio_is_one_when_only_the_calendar_moves_and_departs_when_tenure_does():
    """The defect: a ratio that reads 1 whatever the cells say cannot tell tenure from calendar
    time, which is the question it exists for. Both branches are asserted reachable: the
    calendar-only book reads 1 at every contract year, and doubling year 0's exits within the
    same calendar years moves year 0 above 1 with an interval that excludes it."""
    calendar_only = {(2017, 0): (1000, 20), (2017, 1): (500, 10),
                     (2018, 0): (1000, 5), (2018, 1): (2000, 10)}
    flat = standardised_ratios(calendar_only, calendar_only, "calendar_year", "contract_year")
    assert [r.key for r in flat] == [0, 1]
    assert all(abs(r.ratio - 1.0) < 1e-12 for r in flat)
    assert all(r.interval_95[0] < 1.0 < r.interval_95[1] for r in flat)

    tenure = {(2017, 0): (1000, 60), (2017, 1): (1000, 20),
              (2018, 0): (1000, 60), (2018, 1): (1000, 20)}
    first, second = standardised_ratios(tenure, tenure, "calendar_year", "contract_year")
    assert first.ratio == pytest.approx(1.5) and first.interval_95[0] > 1.0
    assert second.ratio == pytest.approx(0.5) and second.interval_95[1] < 1.0
    years = standardised_ratios(tenure, tenure, "contract_year", "calendar_year")
    assert all(abs(r.ratio - 1.0) < 1e-12 for r in years)


def test_a_subject_is_graded_only_in_years_its_reference_saw_and_pools_to_one_ratio():
    """The defect: a subject year the reference never observed given an expectation of zero (a
    ratio of infinity) or silently pooled. Such a year is left out, and that branch is taken."""
    reference = {(2018, 0): (1000, 10), (2019, 0): (1000, 20)}
    subject = {(2017, 5): (400, 9), (2018, 2): (100, 2), (2019, 3): (100, 1)}
    by_year = standardised_ratios(subject, reference, "calendar_year", "calendar_year")
    assert [r.key for r in by_year] == [2018, 2019]  # 2017 is not graded
    whole = pooled_ratio(by_year)
    assert (whole.observed, whole.expected) == (3, pytest.approx(3.0))
    assert whole.ratio == pytest.approx(1.0)
    with pytest.raises(ValueError, match="an axis must be one of"):
        standardised_ratios(subject, reference, "tenure", "calendar_year")
