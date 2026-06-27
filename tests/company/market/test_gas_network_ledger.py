import pytest
from company.market.gas_network_ledger import (
    GasTransporterZone, GasNetworkCharge, GasNetworkLedger,
)


def _charge(mprn='1000000000001', date='2022-01-31',
           mwh=10.0, aq=50000.0,
           zone=GasTransporterZone.CADENT_NW,
           nts=4.1, ldz=15.4, ggl=2.10, days=31):
    return GasNetworkCharge(
        mprn=mprn, settlement_date=date, consumption_mwh=mwh, aq_kwh=aq,
        zone=zone, nts_rate_gbp_per_mwh=nts, ldz_rate_gbp_per_mwh=ldz,
        ggl_rate_gbp_per_meter_year=ggl, days_in_period=days,
    )


def test_nts_charge_gbp():
    c = _charge(mwh=10.0, nts=4.1, ldz=0.0, ggl=0.0, days=1)
    assert abs(c.nts_charge_gbp - 41.0) < 0.001


def test_ldz_charge_gbp():
    c = _charge(mwh=10.0, nts=0.0, ldz=15.4, ggl=0.0, days=1)
    assert abs(c.ldz_charge_gbp - 154.0) < 0.001


def test_ggl_charge_gbp_daily_pro_rata():
    c = _charge(ggl=2.10 * 365, days=1)
    assert abs(c.ggl_charge_gbp - 2.10) < 0.001


def test_ggl_zero_pre_2021():
    c = _charge(date='2019-06-30', ggl=0.0, days=30)
    assert c.ggl_charge_gbp == 0.0


def test_total_charge_gbp():
    c = _charge(mwh=10.0, nts=4.1, ldz=15.4, ggl=0.0, days=31)
    assert abs(c.total_charge_gbp - (41.0 + 154.0)) < 0.01


def test_unit_cost_p_per_kwh():
    c = _charge(mwh=10.0, nts=4.1, ldz=15.4, ggl=0.0, days=1)
    assert abs(c.unit_cost_p_per_kwh - 1.95) < 0.01


def test_unit_cost_zero_consumption():
    c = _charge(mwh=0.0, nts=4.1, ldz=15.4, ggl=2.10, days=1)
    assert c.unit_cost_p_per_kwh == 0.0


def test_nts_rate_for_year():
    assert abs(GasNetworkLedger.nts_rate_for_year(2022) - 0.41) < 0.001
    assert abs(GasNetworkLedger.nts_rate_for_year(2016) - 0.30) < 0.001


def test_ldz_rate_for_year():
    assert abs(GasNetworkLedger.ldz_rate_for_year(2022) - 1.54) < 0.001
    assert abs(GasNetworkLedger.ldz_rate_for_year(2016) - 1.10) < 0.001


def test_ggl_rate_zero_pre_2021():
    for yr in range(2016, 2021):
        assert GasNetworkLedger.ggl_rate_for_year(yr) == 0.0


def test_ggl_rate_active_2021_2022():
    assert GasNetworkLedger.ggl_rate_for_year(2021) == 2.10
    assert GasNetworkLedger.ggl_rate_for_year(2022) == 2.10


def test_ggl_fell_2023():
    assert GasNetworkLedger.ggl_rate_for_year(2023) < GasNetworkLedger.ggl_rate_for_year(2022)


def test_record_and_charges_for_mprn():
    ledger = GasNetworkLedger()
    c1 = _charge(mprn='M001')
    c2 = _charge(mprn='M002')
    ledger.record_charge(c1)
    ledger.record_charge(c2)
    assert len(ledger.charges_for_mprn('M001')) == 1
    assert len(ledger.charges_for_mprn('M002')) == 1


def test_charges_for_year():
    ledger = GasNetworkLedger()
    ledger.record_charge(_charge(date='2022-01-31'))
    ledger.record_charge(_charge(date='2021-12-31'))
    assert len(ledger.charges_for_year(2022)) == 1
    assert len(ledger.charges_for_year(2021)) == 1


def test_total_nts_ldz_ggl_by_year():
    ledger = GasNetworkLedger()
    ledger.record_charge(_charge(mwh=10.0, nts=4.1, ldz=15.4, ggl=2.10, days=31, date='2022-06-30'))
    assert ledger.total_nts_gbp(2022) > 0
    assert ledger.total_ldz_gbp(2022) > ledger.total_nts_gbp(2022)
    assert ledger.total_ggl_gbp(2022) > 0


def test_annual_cost_breakdown_keys():
    ledger = GasNetworkLedger()
    ledger.record_charge(_charge(date='2022-03-31'))
    bd = ledger.annual_cost_breakdown(2022)
    for k in ('year', 'nts_gbp', 'ldz_gbp', 'ggl_gbp', 'total_gbp'):
        assert k in bd


def test_cost_trend():
    ledger = GasNetworkLedger()
    ledger.record_charge(_charge(date='2019-06-30', ggl=0.0))
    ledger.record_charge(_charge(date='2022-06-30'))
    trend = ledger.cost_trend()
    assert len(trend) == 2
    assert trend[0]['year'] == 2019
    assert trend[1]['year'] == 2022


def test_gas_network_summary_keys():
    ledger = GasNetworkLedger()
    ledger.record_charge(_charge())
    s = ledger.gas_network_summary()
    for k in ('total_charges_recorded', 'total_charged_gbp',
              'zones_covered', 'nts_rate_range',
              'ggl_active_years'):
        assert k in s


def test_ggl_active_years():
    ledger = GasNetworkLedger()
    s = ledger.gas_network_summary()
    assert 2021 in s['ggl_active_years']
    assert 2020 not in s['ggl_active_years']


def test_crisis_rates_highest():
    nts_2022 = GasNetworkLedger.nts_rate_for_year(2022)
    nts_2019 = GasNetworkLedger.nts_rate_for_year(2019)
    ldz_2022 = GasNetworkLedger.ldz_rate_for_year(2022)
    ldz_2019 = GasNetworkLedger.ldz_rate_for_year(2019)
    assert nts_2022 > nts_2019
    assert ldz_2022 > ldz_2019
