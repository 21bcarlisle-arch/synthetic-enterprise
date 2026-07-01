import datetime as dt
import pytest
from company.regulatory.licence_health import (
    LicenceCheckStatus, LicenceCheck, LicenceHealthReport, build_licence_health_report
)


def test_healthy_supplier():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=2_000_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=0.5,
    )
    assert r.overall_status == LicenceCheckStatus.PASS
    assert r.is_going_concern
    assert r.breach_count == 0


def test_negative_net_assets_breach():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=-100_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=0.5,
    )
    check = r.get('net_assets_gbp')
    assert check.status == LicenceCheckStatus.BREACH
    assert not r.is_going_concern


def test_cash_runway_watch():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=500_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=9.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=0.5,
    )
    check = r.get('cash_runway_weeks')
    assert check.status == LicenceCheckStatus.WATCH
    assert r.is_going_concern


def test_bad_debt_breach():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=500_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=6.0,
        complaints_per_100=0.5,
    )
    assert r.get('bad_debt_ratio').status == LicenceCheckStatus.BREACH


def test_complaints_watch():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=500_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=2.0,
    )
    assert r.get('complaints_per_100').status == LicenceCheckStatus.WATCH


def test_low_customer_count_watch():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=60,
        net_assets_gbp=500_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=0.5,
    )
    check = r.get('customer_count')
    assert check.status == LicenceCheckStatus.WATCH


def test_summary_keys():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=500_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=0.5,
    )
    s = r.summary()
    assert 'is_going_concern' in s
    assert 'overall_status' in s


# --- Phase KC depth tests ---

def _healthy():
    return build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=2_000_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=0.5,
    )


def test_get_unknown_returns_none():
    r = _healthy()
    assert r.get('nonexistent_check') is None


def test_headroom_positive_on_pass():
    r = _healthy()
    check = r.get('net_assets_gbp')
    assert check.headroom > 0


def test_headroom_negative_on_breach():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=-100_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=0.5,
    )
    assert r.get('net_assets_gbp').headroom < 0


def test_overall_watch_no_breach():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=2_000_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=9.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=0.5,
    )
    assert r.overall_status == LicenceCheckStatus.WATCH
    assert r.is_going_concern


def test_summary_as_of_isoformat():
    r = _healthy()
    assert r.summary()['as_of'] == '2022-12-31'


def test_bad_debt_just_above_5_pct_is_breach():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=2_000_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=5.01,
        complaints_per_100=0.5,
    )
    assert r.get('bad_debt_ratio').status == LicenceCheckStatus.BREACH


def test_bad_debt_just_above_3_pct_is_watch():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=2_000_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=3.01,
        complaints_per_100=0.5,
    )
    assert r.get('bad_debt_ratio').status == LicenceCheckStatus.WATCH


def test_complaints_just_above_1_is_watch():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=2_000_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=1.01,
    )
    assert r.get('complaints_per_100').status == LicenceCheckStatus.WATCH


def test_pass_count_6_all_healthy():
    r = _healthy()
    assert r.pass_count == 6


def test_watch_count_1_cash_runway_9_weeks():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31),
        active_customer_count=500,
        net_assets_gbp=2_000_000.0,
        treasury_gbp=800_000.0,
        weeks_cash_runway=9.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=0.5,
    )
    assert r.watch_count == 1
