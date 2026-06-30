"""Tests for Regulatory Capital Adequacy Assessment (Phase EV)."""
import datetime as dt
import pytest
from company.risk.capital_adequacy import (
    CapitalAdequacyStatus, CapitalAdequacyAssessment, CapitalAdequacyBook,
    _WIND_DOWN_RESERVE_MIN_PCT, _MARGIN_CALL_BUFFER_MIN_PCT, _EQUITY_RATIO_MIN_PCT,
)

DATE = dt.date(2024, 3, 31)


def make_assessment(
    wind_down=300_000.0, revenue=10_000_000.0,
    margin_buf=500_000.0, exposure=4_000_000.0,
    equity=2_000_000.0, rwa=15_000_000.0,
    var=1_000_000.0, date=DATE
):
    return CapitalAdequacyAssessment(
        as_of=date,
        annual_revenue_gbp=revenue,
        wind_down_reserve_gbp=wind_down,
        gross_notional_exposure_gbp=exposure,
        margin_call_buffer_gbp=margin_buf,
        total_equity_gbp=equity,
        risk_weighted_assets_gbp=rwa,
        stress_var_gbp=var,
    )


class TestCapitalAdequacyAssessment:
    def test_wind_down_reserve_pct(self):
        a = make_assessment(wind_down=200_000.0, revenue=10_000_000.0)
        assert a.wind_down_reserve_pct == pytest.approx(2.0)

    def test_margin_call_buffer_pct(self):
        a = make_assessment(margin_buf=500_000.0, exposure=5_000_000.0)
        assert a.margin_call_buffer_pct == pytest.approx(10.0)

    def test_margin_buffer_no_exposure(self):
        a = make_assessment(exposure=0.0)
        assert a.margin_call_buffer_pct == 100.0

    def test_equity_ratio_pct(self):
        a = make_assessment(equity=2_000_000.0, rwa=20_000_000.0)
        assert a.equity_ratio_pct == pytest.approx(10.0)

    def test_equity_ratio_no_rwa(self):
        a = make_assessment(rwa=0.0)
        assert a.equity_ratio_pct == 100.0

    def test_stress_test_passes_true(self):
        a = make_assessment(equity=2_000_000.0, var=1_000_000.0)
        assert a.stress_test_passes

    def test_stress_test_passes_false(self):
        a = make_assessment(equity=500_000.0, var=1_000_000.0)
        assert not a.stress_test_passes

    def test_wind_down_compliant(self):
        a = make_assessment(wind_down=200_000.0, revenue=10_000_000.0)
        assert a.wind_down_reserve_pct == 2.0 >= _WIND_DOWN_RESERVE_MIN_PCT
        assert a.wind_down_compliant

    def test_wind_down_non_compliant(self):
        a = make_assessment(wind_down=100_000.0, revenue=10_000_000.0)
        assert not a.wind_down_compliant

    def test_status_adequate(self):
        a = make_assessment(
            wind_down=300_000.0, revenue=10_000_000.0,   # 3% > 1.5%
            margin_buf=500_000.0, exposure=4_000_000.0,  # 12.5% > 10%
            equity=2_000_000.0, rwa=15_000_000.0,        # 13.3% > 10%
            var=500_000.0,                                # equity > var
        )
        assert a.status == CapitalAdequacyStatus.ADEQUATE

    def test_status_critical_all_fail(self):
        a = make_assessment(
            wind_down=0.0, revenue=10_000_000.0,         # 0% < 1.5%
            margin_buf=0.0, exposure=4_000_000.0,        # 0% < 10%
            equity=0.0, rwa=15_000_000.0,                # 0% < 10%
            var=1_000_000.0,                             # equity=0 < var
        )
        assert a.status == CapitalAdequacyStatus.CRITICAL

    def test_status_marginal(self):
        a = make_assessment(
            wind_down=100_000.0, revenue=10_000_000.0,  # 1% < 1.5% -> fail
            margin_buf=500_000.0, exposure=4_000_000.0, # OK
            equity=2_000_000.0, rwa=15_000_000.0,       # OK
            var=500_000.0,                               # OK
        )
        assert a.status == CapitalAdequacyStatus.MARGINAL

    def test_assessment_summary(self):
        a = make_assessment()
        s = a.assessment_summary()
        assert "Capital Adequacy" in s


class TestCapitalAdequacyBook:
    def test_record_and_latest(self):
        book = CapitalAdequacyBook()
        book.record(make_assessment())
        assert book.latest() is not None

    def test_latest_returns_most_recent(self):
        book = CapitalAdequacyBook()
        book.record(make_assessment(date=dt.date(2023, 12, 31)))
        book.record(make_assessment(date=dt.date(2024, 3, 31)))
        assert book.latest().as_of == dt.date(2024, 3, 31)

    def test_inadequate_assessments(self):
        book = CapitalAdequacyBook()
        book.record(make_assessment(wind_down=0, margin_buf=0, equity=0, var=1_000_000))
        book.record(make_assessment())  # adequate
        assert len(book.inadequate_assessments()) == 1

    def test_trend_deteriorating(self):
        book = CapitalAdequacyBook()
        book.record(make_assessment(equity=3_000_000.0, rwa=15_000_000.0, date=dt.date(2023, 12, 31)))
        book.record(make_assessment(equity=1_000_000.0, rwa=15_000_000.0, date=dt.date(2024, 3, 31)))
        assert book.trend_is_deteriorating()

    def test_capital_adequacy_summary(self):
        book = CapitalAdequacyBook()
        book.record(make_assessment())
        s = book.capital_adequacy_summary(DATE)
        assert "Capital Adequacy" in s
