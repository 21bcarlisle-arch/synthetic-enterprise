import pytest
from company.market.hedge_performance import (
    HedgeOutcome, HedgeDelivery, HedgePerformanceBook
)


def test_profitable_hedge():
    book = HedgePerformanceBook()
    d = book.record_delivery('T001', 'electricity', 2022, 1000.0, 80.0, 200.0)
    assert d.pnl_gbp == pytest.approx(120000.0)
    assert d.outcome == HedgeOutcome.PROFITABLE


def test_costly_hedge():
    book = HedgePerformanceBook()
    d = book.record_delivery('T002', 'electricity', 2016, 500.0, 60.0, 45.0)
    assert d.pnl_gbp == pytest.approx(-7500.0)
    assert d.outcome == HedgeOutcome.COSTLY


def test_neutral_hedge_within_5pct():
    book = HedgePerformanceBook()
    d = book.record_delivery('T003', 'gas', 2020, 1000.0, 48.0, 50.0)
    assert d.outcome == HedgeOutcome.NEUTRAL


def test_price_differential():
    book = HedgePerformanceBook()
    d = book.record_delivery('T004', 'electricity', 2022, 100.0, 100.0, 250.0)
    assert d.price_differential_gbp_per_mwh == pytest.approx(150.0)


def test_total_pnl_by_year():
    book = HedgePerformanceBook()
    book.record_delivery('T005', 'electricity', 2022, 1000.0, 80.0, 200.0)
    book.record_delivery('T006', 'electricity', 2022, 500.0, 90.0, 180.0)
    book.record_delivery('T007', 'electricity', 2021, 500.0, 70.0, 65.0)
    assert book.total_pnl_gbp(2022) == pytest.approx(120000.0 + 45000.0)
    assert book.total_pnl_gbp(2021) == pytest.approx(-2500.0)


def test_profitable_trades_list():
    book = HedgePerformanceBook()
    book.record_delivery('T008', 'electricity', 2022, 1000.0, 80.0, 200.0)
    book.record_delivery('T009', 'electricity', 2019, 500.0, 70.0, 50.0)
    assert len(book.profitable_trades()) == 1


def test_avg_effectiveness():
    book = HedgePerformanceBook()
    book.record_delivery('T010', 'electricity', 2022, 100.0, 80.0, 200.0)
    book.record_delivery('T011', 'electricity', 2022, 100.0, 100.0, 150.0)
    avg = book.avg_effectiveness_pct(2022)
    assert avg is not None
    assert avg > 0


def test_annual_summary():
    book = HedgePerformanceBook()
    book.record_delivery('T012', 'electricity', 2022, 1000.0, 80.0, 200.0)
    book.record_delivery('T013', 'electricity', 2022, 500.0, 250.0, 180.0)
    s = book.annual_summary(2022)
    assert s['trade_count'] == 2
    assert s['profitable_trades'] == 1
    assert s['costly_trades'] == 1


# --- Phase KO depth tests ---

def test_trade_id_stored():
    book = HedgePerformanceBook()
    d = book.record_delivery('T_ID', 'electricity', 2022, 100.0, 80.0, 100.0)
    assert d.trade_id == 'T_ID'


def test_commodity_stored():
    book = HedgePerformanceBook()
    d = book.record_delivery('T_C', 'gas', 2022, 100.0, 50.0, 60.0)
    assert d.commodity == 'gas'


def test_year_stored():
    book = HedgePerformanceBook()
    d = book.record_delivery('T_Y', 'electricity', 2021, 100.0, 80.0, 90.0)
    assert d.delivery_year == 2021


def test_volume_mwh_stored():
    book = HedgePerformanceBook()
    d = book.record_delivery('T_V', 'electricity', 2022, 750.0, 80.0, 100.0)
    assert d.volume_mwh == pytest.approx(750.0)


def test_pnl_negative_costly():
    book = HedgePerformanceBook()
    d = book.record_delivery('T_N', 'electricity', 2022, 500.0, 80.0, 60.0)
    assert d.pnl_gbp < 0.0


def test_total_pnl_zero_empty_year():
    book = HedgePerformanceBook()
    assert book.total_pnl_gbp(2099) == pytest.approx(0.0)


def test_avg_effectiveness_none_empty_year():
    book = HedgePerformanceBook()
    assert book.avg_effectiveness_pct(2099) is None


def test_annual_summary_empty_year():
    book = HedgePerformanceBook()
    s = book.annual_summary(2099)
    assert s['trade_count'] == 0


def test_profitable_trades_empty_book():
    book = HedgePerformanceBook()
    assert book.profitable_trades() == []


def test_contracted_price_stored():
    book = HedgePerformanceBook()
    d = book.record_delivery('T_CP', 'electricity', 2022, 100.0, 85.0, 120.0)
    assert d.contracted_price_gbp_per_mwh == pytest.approx(85.0)
