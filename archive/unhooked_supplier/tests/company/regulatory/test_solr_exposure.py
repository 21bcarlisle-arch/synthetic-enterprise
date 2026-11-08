import datetime as dt
import pytest
from company.regulatory.solr_exposure import (
    SoLREventStatus, SoLREvent, SoLRBook, get_solr_levy_gbp_per_mwh, SoLRAcquisitionPrice
)


def test_levy_2022_peak():
    assert get_solr_levy_gbp_per_mwh(2022) == pytest.approx(10.0)


def test_levy_2016_low():
    assert get_solr_levy_gbp_per_mwh(2016) == pytest.approx(0.5)


def test_record_event():
    book = SoLRBook()
    ev = book.record_event('SOLR001', 'FailedCo', dt.date(2021, 9, 1),
                            50000, 3200.0, legacy_credit_gbp=2_000_000.0)
    assert ev.status == SoLREventStatus.ANNOUNCED
    assert ev.total_annual_mwh == pytest.approx(160_000.0)


def test_levy_cost_by_year():
    book = SoLRBook()
    book.record_event('SOLR002', 'BustSupplier', dt.date(2022, 1, 1), 10000, 3000.0)
    # 10000 * 3000 = 30,000,000 kWh = 30,000 MWh * £10/MWh = £300k
    cost = book.annual_levy_cost_gbp(2022)
    assert cost == pytest.approx(300_000.0)


def test_complete_transfer():
    book = SoLRBook()
    book.record_event('SOLR003', 'GoneCo', dt.date(2022, 8, 1), 5000, 2500.0)
    book.complete_transfer('SOLR003', dt.date(2022, 8, 15), 'BigEnergy PLC')
    ev = book.get('SOLR003')
    assert ev.status == SoLREventStatus.CUSTOMERS_TRANSFERRED
    assert ev.appointed_solr == 'BigEnergy PLC'


def test_total_legacy_credit():
    book = SoLRBook()
    book.record_event('SOLR004', 'A', dt.date(2021, 6, 1), 100, 3000.0,
                       legacy_credit_gbp=500_000.0)
    book.record_event('SOLR005', 'B', dt.date(2021, 9, 1), 200, 3000.0,
                       legacy_credit_gbp=300_000.0)
    assert book.total_legacy_credit_gbp() == pytest.approx(800_000.0)


def test_acquisition_price_above_svt():
    price = SoLRAcquisitionPrice('SOLR001', 34.0, 50.0, 5.0)
    assert price.is_above_svt
    below = SoLRAcquisitionPrice('SOLR001', 28.0, 45.0, -2.0)
    assert not below.is_above_svt


def test_events_summary():
    book = SoLRBook()
    book.record_event('SOLR006', 'ZapEnergy', dt.date(2022, 11, 1), 25000, 3500.0,
                       legacy_credit_gbp=1_000_000.0)
    s = book.events_summary(2022)
    assert s['events_count'] == 1
    assert s['customers_affected'] == 25000
    assert s['levy_rate_gbp_per_mwh'] == pytest.approx(10.0)


# --- Phase KQ depth tests ---

def test_event_id_stored():
    book = SoLRBook()
    ev = book.record_event('SOLR_ID', 'TestCo', dt.date(2022, 1, 1), 1000, 3000.0)
    assert ev.event_id == 'SOLR_ID'


def test_failed_supplier_stored():
    book = SoLRBook()
    ev = book.record_event('SOLR_FS', 'GoneCo Ltd', dt.date(2022, 1, 1), 500, 3000.0)
    assert ev.failed_supplier == 'GoneCo Ltd'


def test_customer_count_stored():
    book = SoLRBook()
    ev = book.record_event('SOLR_CC', 'Bust PLC', dt.date(2021, 8, 1), 25000, 3500.0)
    assert ev.customer_count_transferred == 25000


def test_avg_kwh_stored():
    book = SoLRBook()
    ev = book.record_event('SOLR_KW', 'ElecFail', dt.date(2021, 9, 1), 10000, 2500.0)
    assert ev.avg_annual_kwh_per_customer == pytest.approx(2500.0)


def test_legacy_credit_stored():
    book = SoLRBook()
    ev = book.record_event('SOLR_LC', 'BustCo', dt.date(2021, 1, 1), 5000, 3000.0,
                            legacy_credit_gbp=1_500_000.0)
    assert ev.legacy_credit_gbp == pytest.approx(1_500_000.0)


def test_get_missing_returns_none():
    book = SoLRBook()
    assert book.get('NOT_FOUND') is None


def test_levy_2019():
    assert get_solr_levy_gbp_per_mwh(2019) == pytest.approx(1.5)


def test_annual_levy_cost_zero_empty_year():
    book = SoLRBook()
    assert book.annual_levy_cost_gbp(2099) == pytest.approx(0.0)


def test_total_legacy_credit_zero_empty():
    book = SoLRBook()
    assert book.total_legacy_credit_gbp() == pytest.approx(0.0)


def test_status_is_announced_on_record():
    book = SoLRBook()
    ev = book.record_event('SOLR_ST', 'NewFail', dt.date(2022, 6, 1), 3000, 2800.0)
    assert ev.status == SoLREventStatus.ANNOUNCED
