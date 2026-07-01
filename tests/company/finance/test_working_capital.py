import datetime as dt
import pytest
from company.finance.working_capital import (
    CashFlowType, CashFlowDirection, CashFlowEntry, DailyCashPosition, WorkingCapitalMonitor
)


def _make_monitor(balance: float = 200_000.0) -> WorkingCapitalMonitor:
    return WorkingCapitalMonitor(balance)


def test_opening_balance():
    m = _make_monitor(200_000.0)
    assert m.current_balance() == pytest.approx(200_000.0)


def test_post_day_inflow():
    m = _make_monitor(100_000.0)
    pos = m.post_day(dt.date(2022, 3, 1), [
        (CashFlowType.CUSTOMER_COLLECTIONS, CashFlowDirection.INFLOW, 50_000.0, 'DD run'),
    ])
    assert pos.closing_balance_gbp == pytest.approx(150_000.0)
    assert m.current_balance() == pytest.approx(150_000.0)


def test_post_day_outflow():
    m = _make_monitor(200_000.0)
    pos = m.post_day(dt.date(2022, 3, 2), [
        (CashFlowType.WHOLESALE_SETTLEMENT, CashFlowDirection.OUTFLOW, 80_000.0, 'BSC R1'),
    ])
    assert pos.closing_balance_gbp == pytest.approx(120_000.0)


def test_below_minimum():
    m = _make_monitor(60_000.0)
    m.set_minimum_balance(100_000.0)
    assert m.is_below_minimum()
    assert m.headroom_gbp() == pytest.approx(-40_000.0)


def test_above_minimum():
    m = _make_monitor(200_000.0)
    assert not m.is_below_minimum()
    assert m.headroom_gbp() == pytest.approx(150_000.0)


def test_signed_amount():
    e_in = CashFlowEntry(dt.date(2022, 1, 1), CashFlowType.DSR_REVENUE,
                          CashFlowDirection.INFLOW, 5_000.0)
    e_out = CashFlowEntry(dt.date(2022, 1, 1), CashFlowType.PAYROLL,
                           CashFlowDirection.OUTFLOW, 20_000.0)
    assert e_in.signed_amount == pytest.approx(5_000.0)
    assert e_out.signed_amount == pytest.approx(-20_000.0)


def test_lowest_balance_in_period():
    m = _make_monitor(300_000.0)
    m.post_day(dt.date(2022, 6, 1), [
        (CashFlowType.NETWORK_CHARGES, CashFlowDirection.OUTFLOW, 200_000.0, 'DUoS'),
    ])
    m.post_day(dt.date(2022, 6, 2), [
        (CashFlowType.CUSTOMER_COLLECTIONS, CashFlowDirection.INFLOW, 150_000.0, 'DD'),
    ])
    low = m.lowest_balance_in_period(dt.date(2022, 6, 1), dt.date(2022, 6, 2))
    assert low == pytest.approx(100_000.0)


def test_total_inflows():
    m = _make_monitor(100_000.0)
    m.post_day(dt.date(2022, 7, 1), [
        (CashFlowType.CUSTOMER_COLLECTIONS, CashFlowDirection.INFLOW, 80_000.0, 'DD'),
        (CashFlowType.DSR_REVENUE, CashFlowDirection.INFLOW, 10_000.0, 'DSR'),
        (CashFlowType.VAT_PAYMENT, CashFlowDirection.OUTFLOW, 30_000.0, 'HMRC'),
    ])
    assert m.total_inflows_gbp(dt.date(2022, 7, 1), dt.date(2022, 7, 1)) == pytest.approx(90_000.0)


def test_cash_summary():
    m = _make_monitor(500_000.0)
    m.post_day(dt.date(2022, 8, 1), [
        (CashFlowType.REGO_PURCHASE, CashFlowDirection.OUTFLOW, 25_000.0, 'REGO'),
    ])
    s = m.cash_summary(dt.date(2022, 8, 1), dt.date(2022, 8, 1))
    assert s['days'] == 1
    assert s['current_balance_gbp'] == pytest.approx(475_000.0)
    assert 'lowest_balance_gbp' in s


def test_closing_balance_chains_across_days():
    m = _make_monitor(100_000.0)
    m.post_day(dt.date(2022, 3, 1), [
        (CashFlowType.CUSTOMER_COLLECTIONS, CashFlowDirection.INFLOW, 50_000.0, 'DD'),
    ])
    m.post_day(dt.date(2022, 3, 2), [
        (CashFlowType.WHOLESALE_SETTLEMENT, CashFlowDirection.OUTFLOW, 30_000.0, 'BSC'),
    ])
    assert m.current_balance() == pytest.approx(120_000.0)


def test_positions_in_period_filter():
    m = _make_monitor(200_000.0)
    m.post_day(dt.date(2022, 6, 1), [])
    m.post_day(dt.date(2022, 6, 2), [])
    m.post_day(dt.date(2022, 6, 3), [])
    in_period = m.positions_in_period(dt.date(2022, 6, 1), dt.date(2022, 6, 2))
    assert len(in_period) == 2


def test_lowest_balance_none_when_empty_period():
    m = _make_monitor(200_000.0)
    result = m.lowest_balance_in_period(dt.date(2022, 1, 1), dt.date(2022, 1, 31))
    assert result is None


def test_net_cash_flow_mixed():
    pos = DailyCashPosition(dt.date(2022, 6, 1), 100_000.0)
    pos.entries.append(CashFlowEntry(dt.date(2022, 6, 1), CashFlowType.CUSTOMER_COLLECTIONS,
                                     CashFlowDirection.INFLOW, 80_000.0))
    pos.entries.append(CashFlowEntry(dt.date(2022, 6, 1), CashFlowType.WHOLESALE_SETTLEMENT,
                                     CashFlowDirection.OUTFLOW, 50_000.0))
    assert pos.net_cash_flow_gbp == pytest.approx(30_000.0)


def test_total_inflows_excludes_outflows():
    pos = DailyCashPosition(dt.date(2022, 6, 1), 100_000.0)
    pos.entries.append(CashFlowEntry(dt.date(2022, 6, 1), CashFlowType.CUSTOMER_COLLECTIONS,
                                     CashFlowDirection.INFLOW, 60_000.0))
    pos.entries.append(CashFlowEntry(dt.date(2022, 6, 1), CashFlowType.NETWORK_CHARGES,
                                     CashFlowDirection.OUTFLOW, 40_000.0))
    assert pos.total_inflows_gbp == pytest.approx(60_000.0)


def test_cash_summary_headroom():
    m = _make_monitor(200_000.0)
    m.set_minimum_balance(100_000.0)
    m.post_day(dt.date(2022, 8, 1), [])
    s = m.cash_summary(dt.date(2022, 8, 1), dt.date(2022, 8, 1))
    assert s['headroom_gbp'] == pytest.approx(100_000.0)


def test_set_minimum_balance_changes_threshold():
    m = _make_monitor(80_000.0)
    m.set_minimum_balance(200_000.0)
    assert m.is_below_minimum()


def test_daily_position_total_outflows():
    pos = DailyCashPosition(dt.date(2022, 6, 1), 500_000.0)
    pos.entries.append(CashFlowEntry(dt.date(2022, 6, 1), CashFlowType.VAT_PAYMENT,
                                     CashFlowDirection.OUTFLOW, 25_000.0))
    pos.entries.append(CashFlowEntry(dt.date(2022, 6, 1), CashFlowType.PAYROLL,
                                     CashFlowDirection.OUTFLOW, 75_000.0))
    assert pos.total_outflows_gbp == pytest.approx(100_000.0)


def test_cash_summary_period_start_end_fields():
    m = _make_monitor(300_000.0)
    m.post_day(dt.date(2022, 9, 1), [])
    s = m.cash_summary(dt.date(2022, 9, 1), dt.date(2022, 9, 1))
    assert s['period_start'] == '2022-09-01'
    assert s['period_end'] == '2022-09-01'


def test_headroom_positive_when_above_minimum():
    m = _make_monitor(200_000.0)
    # default minimum is 50,000 → headroom = 150,000
    assert m.headroom_gbp() > 0
