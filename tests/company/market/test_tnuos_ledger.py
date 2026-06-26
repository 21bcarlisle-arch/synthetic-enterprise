import pytest
from company.market.tnuos_ledger import (
    TNUoSLedger, TNUoSCharge, TriadHalfHour, TriadStatus
)


def _charge(aid="C1", year=2022, kwh=100_000.0, res_rate=1.05,
            triad_kw=50.0, triad_rate=30.0, zone="midlands"):
    return TNUoSCharge(
        account_id=aid, charge_year=year, consumption_kwh=kwh,
        residual_rate_p_per_kwh=res_rate, triad_demand_kw=triad_kw,
        triad_rate_gbp_per_kw=triad_rate, zone=zone,
    )


def _triad_hh(date="2022-11-04", sp=35, kw=500.0, status=TriadStatus.TRIAD):
    return TriadHalfHour(settlement_date=date, settlement_period=sp,
                         demand_kw=kw, status=status)


def test_residual_charge_gbp():
    c = _charge(kwh=100_000.0, res_rate=1.05)
    assert abs(c.residual_charge_gbp - 1050.0) < 0.01


def test_triad_charge_gbp():
    c = _charge(triad_kw=50.0, triad_rate=30.0)
    assert abs(c.triad_charge_gbp - 1500.0) < 0.01


def test_total_charge_gbp():
    c = _charge(kwh=100_000.0, res_rate=1.05, triad_kw=50.0, triad_rate=30.0)
    assert abs(c.total_charge_gbp - 2550.0) < 0.01


def test_residual_rate_for_year():
    rate = TNUoSLedger.residual_rate_for_year(2022)
    assert abs(rate - 1.05) < 0.001


def test_zone_factor_north_higher():
    north = TNUoSLedger.zone_factor("north")
    south = TNUoSLedger.zone_factor("south")
    assert north > south


def test_zone_factor_default():
    assert abs(TNUoSLedger.zone_factor("unknown_zone") - 1.00) < 0.001


def test_record_and_filter_by_year():
    ledger = TNUoSLedger()
    ledger.record_charge(_charge(year=2022))
    ledger.record_charge(_charge(year=2021))
    assert len(ledger.charges_for_year(2022)) == 1


def test_total_charged_gbp_by_year():
    ledger = TNUoSLedger()
    ledger.record_charge(_charge(year=2022, kwh=100_000.0, res_rate=1.05, triad_kw=0.0, triad_rate=0.0))
    ledger.record_charge(_charge(year=2021, kwh=50_000.0, res_rate=0.92, triad_kw=0.0, triad_rate=0.0))
    y2022 = ledger.total_charged_gbp(2022)
    assert abs(y2022 - 1050.0) < 0.01


def test_confirmed_triads():
    ledger = TNUoSLedger()
    ledger.record_triad_hh(_triad_hh(status=TriadStatus.TRIAD))
    ledger.record_triad_hh(_triad_hh(status=TriadStatus.NEAR_MISS))
    ledger.record_triad_hh(_triad_hh(status=TriadStatus.TRIAD))
    assert len(ledger.confirmed_triads()) == 2


def test_tnuos_summary_keys():
    ledger = TNUoSLedger()
    ledger.record_charge(_charge())
    s = ledger.tnuos_summary(2022)
    for k in ("total_accounts", "total_charged_gbp", "confirmed_triads"):
        assert k in s
