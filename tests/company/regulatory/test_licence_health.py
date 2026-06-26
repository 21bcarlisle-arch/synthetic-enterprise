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
