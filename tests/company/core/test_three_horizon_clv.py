"""Tests for Three-Horizon CLV Tracker (Phase EC)."""
import datetime as dt

import pytest

from company.core.three_horizon_clv import (
    _H3_AT_RISK_THRESHOLD,
    _H3_DETERIORATE_THRESHOLD,
    _H3_OUTPERFORM_THRESHOLD,
    H1Commitment,
    H2Actuals,
    H3Forecast,
    H3Signal,
    ThreeHorizonCLVTracker,
)

START = dt.date(2024, 1, 1)
END = dt.date(2025, 1, 1)
MID = dt.date(2024, 7, 1)


def make_h1(account="C1", margin=200.0, churn=0.18, discount=0.08):
    return H1Commitment(
        account_id=account,
        committed_at=START,
        contract_start=START,
        contract_end=END,
        expected_annual_margin_gbp=margin,
        expected_churn_rate=churn,
        discount_rate=discount,
    )


def make_h3(account="C1", margin=200.0, churn=0.18, date=MID, years=0.5):
    return H3Forecast(
        account_id=account,
        forecast_at=date,
        remaining_contract_years=years,
        updated_annual_margin_gbp=margin,
        updated_churn_probability=churn,
    )


@pytest.fixture
def tracker():
    return ThreeHorizonCLVTracker()


def discounted_sum(margin, churn, discount, whole_years):
    """Period-by-period value of a term, built by summation rather than by the
    module's closed form — so the assertion does not restate the implementation."""
    retention = 1.0 - churn
    return sum(
        margin * retention**t / (1 + discount) ** t for t in range(1, whole_years + 1)
    )


def h1_of_whole_years(years, margin=200.0, churn=0.18, discount=0.08):
    start = dt.date(2024, 1, 1)
    return H1Commitment(
        account_id="C1",
        committed_at=start,
        contract_start=start,
        contract_end=start + dt.timedelta(days=round(365.25 * years)),
        expected_annual_margin_gbp=margin,
        expected_churn_rate=churn,
        discount_rate=discount,
    )


class TestH1Commitment:
    def test_contract_years(self):
        h1 = make_h1()
        assert h1.contract_years == pytest.approx(1.0, rel=0.01)

    def test_h1_clv_matches_period_by_period_sum(self):
        # 4 whole years (1461 days = exactly 4 x 365.25), summed term by term —
        # an independent construction, not a restatement of the closed form.
        h1 = h1_of_whole_years(4)
        assert h1.contract_years == pytest.approx(4.0)
        assert h1.h1_clv_gbp == pytest.approx(discounted_sum(200.0, 0.18, 0.08, 4))

    def test_h1_clv_rises_strictly_with_the_term(self):
        # The defect this replaces: a 1-day and a 30-year commitment priced the same.
        values = [h1_of_whole_years(y).h1_clv_gbp for y in (1, 2, 5, 10, 30)]
        assert values == sorted(values)
        assert all(b > a for a, b in zip(values, values[1:]))

    def test_h1_clv_never_exceeds_what_the_term_can_deliver(self):
        # margin x term is the undiscounted ceiling; the perpetuity broke it 2.9x over.
        for years in (1, 2, 5, 10, 30):
            h1 = h1_of_whole_years(years)
            assert h1.h1_clv_gbp <= 200.0 * h1.contract_years

    def test_h1_clv_of_a_zero_length_contract_is_zero(self):
        start = dt.date(2024, 1, 1)
        h1 = H1Commitment(
            account_id="C1",
            committed_at=start,
            contract_start=start,
            contract_end=start,
            expected_annual_margin_gbp=200.0,
            expected_churn_rate=0.18,
            discount_rate=0.08,
        )
        assert h1.contract_years == pytest.approx(0.0)
        assert h1.h1_clv_gbp == pytest.approx(0.0)

    def test_h1_clv_of_certain_churn_is_zero(self):
        assert make_h1(churn=1.0).h1_clv_gbp == pytest.approx(0.0)

    def test_a_long_term_approaches_the_perpetuity_from_below(self):
        # The old value, now the T -> infinity limit rather than the answer for every T.
        perpetuity = 200.0 * 0.82 / (1 + 0.08 - 0.82)
        long_term = h1_of_whole_years(40).h1_clv_gbp
        assert long_term < perpetuity
        assert long_term == pytest.approx(perpetuity, rel=1e-3)


class TestH3Forecast:
    def test_h3_clv_matches_period_by_period_sum(self):
        h3 = make_h3(margin=200.0, churn=0.18, years=3)
        assert h3.h3_clv_gbp == pytest.approx(discounted_sum(200.0, 0.18, 0.08, 3))

    def test_h3_clv_rises_strictly_with_remaining_term(self):
        values = [make_h3(years=y).h3_clv_gbp for y in (0.5, 1.0, 2.0, 5.0, 10.0)]
        assert all(b > a for a, b in zip(values, values[1:]))

    def test_h3_clv_never_exceeds_what_the_remaining_term_can_deliver(self):
        for years in (0.5, 1.0, 2.0, 5.0, 10.0):
            assert make_h3(margin=200.0, years=years).h3_clv_gbp <= 200.0 * years

    def test_h3_clv_of_an_expired_contract_is_zero(self):
        assert make_h3(years=0.0).h3_clv_gbp == pytest.approx(0.0)


class TestThreeHorizonCLVTracker:
    def test_commit_h1(self, tracker):
        tracker.commit_h1(make_h1())
        assert tracker.h1("C1") is not None

    def test_record_revenue(self, tracker):
        tracker.commit_h1(make_h1())
        tracker.record_revenue("C1", START, 100.0)
        assert tracker.h2_margin("C1") == pytest.approx(100.0)

    def test_record_cost(self, tracker):
        tracker.commit_h1(make_h1())
        tracker.record_revenue("C1", START, 200.0)
        tracker.record_cost("C1", START, 80.0)
        assert tracker.h2_margin("C1") == pytest.approx(120.0)

    def test_h2_margin_as_of(self, tracker):
        tracker.commit_h1(make_h1())
        early = dt.date(2024, 3, 1)
        late = dt.date(2024, 9, 1)
        tracker.record_revenue("C1", early, 50.0)
        tracker.record_revenue("C1", late, 50.0)
        assert tracker.h2_margin("C1", as_of=dt.date(2024, 6, 1)) == pytest.approx(50.0)

    def test_h1_vs_h2_variance(self, tracker):
        tracker.commit_h1(make_h1(margin=200.0))
        # 6 months elapsed; expected = 100; actual = 150 -> variance = +50
        tracker.record_revenue("C1", MID, 200.0)
        tracker.record_cost("C1", MID, 50.0)  # actual margin = 150
        variance = tracker.h1_vs_h2_variance_gbp("C1", MID)
        assert variance is not None
        assert variance > 0  # outperforming H1 pace

    def test_latest_h3(self, tracker):
        tracker.commit_h1(make_h1())
        tracker.update_h3(make_h3(date=dt.date(2024, 3, 1)))
        tracker.update_h3(make_h3(date=MID))
        latest = tracker.latest_h3("C1")
        assert latest is not None
        assert latest.forecast_at == MID

    def test_h3_signal_on_track(self, tracker):
        h1 = make_h1(margin=200.0, churn=0.18)
        tracker.commit_h1(h1)
        tracker.update_h3(make_h3(margin=200.0, churn=0.18))
        assert tracker.h3_signal("C1") == H3Signal.ON_TRACK

    def test_h3_signal_outperforming(self, tracker):
        h1 = make_h1(margin=100.0, churn=0.40)
        tracker.commit_h1(h1)
        tracker.update_h3(make_h3(margin=300.0, churn=0.05))  # much better
        assert tracker.h3_signal("C1") == H3Signal.OUTPERFORMING

    def test_h3_signal_at_risk(self, tracker):
        h1 = make_h1(margin=200.0, churn=0.05)
        tracker.commit_h1(h1)
        tracker.update_h3(make_h3(margin=50.0, churn=0.80))  # much worse
        assert tracker.h3_signal("C1") == H3Signal.AT_RISK

    def test_at_risk_accounts(self, tracker):
        tracker.commit_h1(make_h1("C1", margin=200.0, churn=0.05))
        tracker.commit_h1(make_h1("C2", margin=200.0, churn=0.18))
        tracker.update_h3(make_h3("C1", margin=50.0, churn=0.80))  # at risk
        tracker.update_h3(make_h3("C2", margin=200.0, churn=0.18))  # on track
        assert "C1" in tracker.at_risk_accounts()
        assert "C2" not in tracker.at_risk_accounts()

    def test_clv_summary(self, tracker):
        tracker.commit_h1(make_h1())
        s = tracker.clv_summary()
        assert "3-Horizon CLV Tracker" in s

    def test_constants(self):
        assert _H3_OUTPERFORM_THRESHOLD == pytest.approx(0.10)
        assert _H3_AT_RISK_THRESHOLD == pytest.approx(-0.30)


# --- Phase JQ depth tests ---

class TestThreeHorizonCLVTrackerDepth:
    def test_outperforming_accounts(self, tracker):
        tracker.commit_h1(make_h1("C1", margin=100.0, churn=0.40))
        tracker.commit_h1(make_h1("C2", margin=200.0, churn=0.18))
        tracker.update_h3(make_h3("C1", margin=300.0, churn=0.05))  # outperforming
        tracker.update_h3(make_h3("C2", margin=200.0, churn=0.18))  # on track
        out = tracker.outperforming_accounts()
        assert "C1" in out
        assert "C2" not in out

    def test_h3_signal_deteriorating(self, tracker):
        # H1 CLV = 100 * 0.90 / (1.08 - 0.90) = 500; H3 with margin=80 gives CLV=400 → -20% → DETERIORATING
        tracker.commit_h1(make_h1("C1", margin=100.0, churn=0.10))
        tracker.update_h3(make_h3("C1", margin=80.0, churn=0.10))
        assert tracker.h3_signal("C1") == H3Signal.DETERIORATING

    def test_h3_signal_none_no_h3(self, tracker):
        tracker.commit_h1(make_h1())
        assert tracker.h3_signal("C1") is None

    def test_h3_signal_none_unknown_account(self, tracker):
        assert tracker.h3_signal("UNKNOWN") is None

    def test_latest_h3_none_unknown_account(self, tracker):
        assert tracker.latest_h3("UNKNOWN") is None

    def test_h2_margin_no_filter_all_events(self, tracker):
        tracker.commit_h1(make_h1())
        tracker.record_revenue("C1", START, 150.0)
        tracker.record_cost("C1", START, 30.0)
        assert tracker.h2_margin("C1") == pytest.approx(120.0)

    def test_h1_vs_h2_variance_none_no_h1(self, tracker):
        result = tracker.h1_vs_h2_variance_gbp("NOACCOUNT", MID)
        assert result is None

    def test_h1_clv_negative_churn_grows_and_still_tracks_the_term(self):
        # retention = 1.10 > 1 + d: the series grows rather than decays, so the
        # margin x term ceiling does NOT apply — but the term must still be priced.
        h1 = h1_of_whole_years(4, churn=-0.10)
        assert h1.h1_clv_gbp == pytest.approx(discounted_sum(200.0, -0.10, 0.08, 4))
        assert h1.h1_clv_gbp > h1_of_whole_years(2, churn=-0.10).h1_clv_gbp

    def test_deteriorate_threshold_constant(self):
        assert _H3_DETERIORATE_THRESHOLD == pytest.approx(-0.10)

    def test_at_risk_accounts_empty_when_all_on_track(self, tracker):
        tracker.commit_h1(make_h1("C1", margin=200.0, churn=0.18))
        tracker.update_h3(make_h3("C1", margin=200.0, churn=0.18))
        assert tracker.at_risk_accounts() == []


# --- Phase JX depth tests ---

class TestH2ActualsDirect:
    def test_total_revenue_sums_events(self):
        h2 = H2Actuals('A1')
        h2.record_revenue(START, 100.0)
        h2.record_revenue(MID, 80.0)
        assert h2.total_revenue_gbp() == pytest.approx(180.0)

    def test_total_cost_sums_events(self):
        h2 = H2Actuals('A1')
        h2.record_cost(START, 30.0)
        h2.record_cost(MID, 20.0)
        assert h2.total_cost_gbp() == pytest.approx(50.0)

    def test_h2_margin_gbp_direct(self):
        h2 = H2Actuals('A1')
        h2.record_revenue(START, 200.0)
        h2.record_cost(START, 75.0)
        assert h2.h2_margin_gbp() == pytest.approx(125.0)


class TestThreeHorizonCLVTrackerDepthJX:
    def test_h1_vs_h2_variance_negative_underperform(self, tracker):
        tracker.commit_h1(make_h1(margin=200.0))
        # 6 months elapsed; expected = 100; actual = 50 -> variance = -50
        tracker.record_revenue('C1', MID, 80.0)
        tracker.record_cost('C1', MID, 30.0)  # actual margin = 50
        variance = tracker.h1_vs_h2_variance_gbp('C1', MID)
        assert variance is not None
        assert variance < 0

    def test_h3_clv_unit_retention_is_margin_times_term(self):
        # churn = -0.08 -> retention = 1.08 = 1 + d, so each period is worth exactly
        # `margin` in present value and the series degenerates to margin x term.
        h3 = H3Forecast(
            account_id='FX', forecast_at=MID, remaining_contract_years=2.0,
            updated_annual_margin_gbp=100.0, updated_churn_probability=-0.08, discount_rate=0.08,
        )
        assert h3.h3_clv_gbp == pytest.approx(100.0 * 2.0)
        assert h3.h3_clv_gbp == pytest.approx(discounted_sum(100.0, -0.08, 0.08, 2))

    def test_h3_signal_just_below_outperform_threshold_is_on_track(self, tracker):
        # pct = 0.09 -> NOT > 0.10 -> ON_TRACK
        tracker.commit_h1(make_h1('C1', margin=100.0, churn=0.18))
        tracker.update_h3(make_h3('C1', margin=109.0, churn=0.18))
        assert tracker.h3_signal('C1') == H3Signal.ON_TRACK

    def test_h3_signal_boundary_exactly_at_risk_threshold_is_deteriorating(self, tracker):
        # pct = exactly -0.30 -> NOT < -0.30 -> DETERIORATING (not AT_RISK)
        tracker.commit_h1(make_h1('C1', margin=100.0, churn=0.18))
        tracker.update_h3(make_h3('C1', margin=70.0, churn=0.18))
        assert tracker.h3_signal('C1') == H3Signal.DETERIORATING

    def test_outperforming_accounts_empty_when_no_h3(self, tracker):
        tracker.commit_h1(make_h1('C1', margin=300.0, churn=0.05))
        # no H3 committed -> h3_signal returns None -> not in outperforming
        assert tracker.outperforming_accounts() == []

    def test_clv_summary_shows_account_count(self, tracker):
        tracker.commit_h1(make_h1('C1'))
        tracker.commit_h1(make_h1('C2'))
        s = tracker.clv_summary()
        assert '2 accounts' in s

    def test_h2_margin_unknown_account_returns_zero(self, tracker):
        assert tracker.h2_margin('UNKNOWN') == pytest.approx(0.0)


# --- The contract term is priced (2026-08-15 BLOCKING finding discharge) ---

class TestTheTermIsPriced:
    def test_an_expiring_contract_is_not_worth_the_same_as_a_ten_year_one(self, tracker):
        """The finding's §3 scenario: same margin, same churn, term the only difference.
        Under the perpetuity both accounts priced identically on both horizons."""
        expiring = H1Commitment(
            account_id='EXPIRING', committed_at=START, contract_start=START,
            contract_end=START + dt.timedelta(days=1),
            expected_annual_margin_gbp=100.0, expected_churn_rate=0.20, discount_rate=0.08,
        )
        long_run = H1Commitment(
            account_id='LONG', committed_at=START, contract_start=START,
            contract_end=START + dt.timedelta(days=3653),
            expected_annual_margin_gbp=100.0, expected_churn_rate=0.20, discount_rate=0.08,
        )
        tracker.commit_h1(expiring)
        tracker.commit_h1(long_run)
        tracker.update_h3(H3Forecast('EXPIRING', MID, 1 / 365.25, 100.0, 0.20))
        tracker.update_h3(H3Forecast('LONG', MID, 9.0, 100.0, 0.20))
        assert expiring.h1_clv_gbp < long_run.h1_clv_gbp / 100
        assert (
            tracker.latest_h3('EXPIRING').h3_clv_gbp
            < tracker.latest_h3('LONG').h3_clv_gbp / 100
        )

    def test_the_signal_scores_h3_over_the_same_window_h1_promised(self, tracker):
        """An unchanged belief must read ON_TRACK however much term has run off —
        the whole-term H1 value is not the baseline for a part-term H3 forecast."""
        tracker.commit_h1(h1_of_whole_years(4, margin=200.0, churn=0.18))
        tracker.update_h3(make_h3(margin=200.0, churn=0.18, years=0.25))
        assert tracker.h3_signal('C1') == H3Signal.ON_TRACK

    def test_the_signal_still_sees_a_worsened_belief_over_the_same_window(self, tracker):
        tracker.commit_h1(h1_of_whole_years(4, margin=200.0, churn=0.18))
        tracker.update_h3(make_h3(margin=60.0, churn=0.50, years=0.25))
        assert tracker.h3_signal('C1') == H3Signal.AT_RISK

    def test_clv_over_years_is_the_baseline_the_signal_uses(self):
        h1 = h1_of_whole_years(4, margin=200.0, churn=0.18)
        assert h1.clv_over_years_gbp(h1.contract_years) == pytest.approx(h1.h1_clv_gbp)
        assert h1.clv_over_years_gbp(1.0) < h1.clv_over_years_gbp(4.0)
        assert h1.clv_over_years_gbp(0.0) == pytest.approx(0.0)
