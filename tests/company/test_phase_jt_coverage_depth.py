"""Phase JT: Coverage Depth Sprint XLII -- 30 tests."""
import datetime as dt
import pytest
from company.regulatory.licence_health import (
    LicenceCheckStatus, LicenceCheck, LicenceHealthReport, build_licence_health_report,
)












































def _healthy():
    return build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=2_000_000.0, treasury_gbp=800_000.0,
        weeks_cash_runway=20.0, bad_debt_ratio_pct=1.5, complaints_per_100=0.5,
    )


def test_lh_pass_count_all_healthy():
    r = _healthy()
    assert r.pass_count == 6


def test_lh_watch_count_on_cash_watch():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=2_000_000.0, treasury_gbp=800_000.0,
        weeks_cash_runway=9.0, bad_debt_ratio_pct=1.5, complaints_per_100=0.5,
    )
    assert r.watch_count >= 1


def test_lh_breach_is_not_going_concern():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=-1.0, treasury_gbp=800_000.0,
        weeks_cash_runway=20.0, bad_debt_ratio_pct=1.5, complaints_per_100=0.5,
    )
    assert not r.is_going_concern


def test_lh_get_returns_none_unknown():
    assert _healthy().get("nonexistent") is None


def test_lh_headroom_positive():
    check = LicenceCheck("n", "d", value=10.0, threshold=8.0, status=LicenceCheckStatus.PASS)
    assert check.headroom == pytest.approx(2.0)


def test_lh_headroom_negative():
    check = LicenceCheck("n", "d", value=5.0, threshold=8.0, status=LicenceCheckStatus.BREACH)
    assert check.headroom == pytest.approx(-3.0)


def test_lh_overall_watch_no_breach():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=2_000_000.0, treasury_gbp=800_000.0,
        weeks_cash_runway=9.0, bad_debt_ratio_pct=1.5, complaints_per_100=0.5,
    )
    assert r.breach_count == 0
    assert r.overall_status == LicenceCheckStatus.WATCH


def test_lh_bad_debt_exactly_5pct_is_watch():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=2_000_000.0, treasury_gbp=800_000.0,
        weeks_cash_runway=20.0, bad_debt_ratio_pct=5.0, complaints_per_100=0.5,
    )
    assert r.get("bad_debt_ratio").status == LicenceCheckStatus.WATCH


def test_lh_complaints_exactly_1_is_pass():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=2_000_000.0, treasury_gbp=800_000.0,
        weeks_cash_runway=20.0, bad_debt_ratio_pct=1.5, complaints_per_100=1.0,
    )
    assert r.get("complaints_per_100").status == LicenceCheckStatus.PASS


def test_lh_summary_as_of_iso():
    s = _healthy().summary()
    assert s["as_of"] == "2022-12-31"
