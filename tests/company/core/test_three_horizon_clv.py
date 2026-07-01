"""Tests for Three-Horizon CLV Tracker (Phase EC)."""
import datetime as dt
import pytest
from company.core.three_horizon_clv import (
    H3Signal, H1Commitment, H2Actuals, H3Forecast,
    ThreeHorizonCLVTracker,
    _H3_OUTPERFORM_THRESHOLD, _H3_DETERIORATE_THRESHOLD, _H3_AT_RISK_THRESHOLD,
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


class TestH1Commitment:
    def test_contract_years(self):
        h1 = make_h1()
        assert h1.contract_years == pytest.approx(1.0, rel=0.01)

    def test_h1_clv_formula(self):
        h1 = make_h1(margin=200.0, churn=0.18, discount=0.08)
        retention = 0.82
        expected = 200.0 * retention / (1 + 0.08 - retention)
        assert h1.h1_clv_gbp == pytest.approx(expected)


class TestH3Forecast:
    def test_h3_clv(self):
        h3 = make_h3(margin=200.0, churn=0.18)
        retention = 0.82
        expected = 200.0 * retention / (1 + 0.08 - retention)
        assert h3.h3_clv_gbp == pytest.approx(expected)


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

    def test_h1_clv_fallback_negative_churn(self):
        h1 = H1Commitment(
            account_id="FX",
            committed_at=START,
            contract_start=START,
            contract_end=END,
            expected_annual_margin_gbp=200.0,
            expected_churn_rate=-0.10,
            discount_rate=0.08,
        )
        # retention = 1.10; denom = 1.08 - 1.10 = -0.02 <= 0 => fallback
        assert h1.h1_clv_gbp == pytest.approx(200.0 * h1.contract_years)

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

    def test_h3_clv_fallback_zero_denom(self):
        # churn_probability = -0.08 -> retention = 1.08; denom = 1+0.08-1.08 = 0 -> fallback
        h3 = H3Forecast(
            account_id='FX', forecast_at=MID, remaining_contract_years=2.0,
            updated_annual_margin_gbp=100.0, updated_churn_probability=-0.08, discount_rate=0.08,
        )
        assert h3.h3_clv_gbp == pytest.approx(100.0 * 2.0)

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
