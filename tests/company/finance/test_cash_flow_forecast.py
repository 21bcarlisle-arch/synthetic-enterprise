import datetime as dt
import pytest
from company.finance.cash_flow_forecast import (
    WeeklyCashFlow, CashFlowForecast, build_cash_flow_forecast
)


def _make_forecast(opening=500_000, receipts=100_000, wholesale=70_000,
                   network=10_000, policy=5_000, opex=8_000, weeks=13):
    return build_cash_flow_forecast(
        as_of=dt.date(2023, 1, 2),
        opening_cash_gbp=opening,
        weekly_receipts_gbp=receipts,
        weekly_wholesale_gbp=wholesale,
        weekly_network_gbp=network,
        weekly_policy_gbp=policy,
        weekly_opex_gbp=opex,
        weeks=weeks,
    )


def test_13_weeks_default():
    f = _make_forecast()
    assert len(f.weeks) == 13


def test_net_cash_positive():
    f = _make_forecast()
    w = f.weeks[0]
    assert w.net_cash_gbp == pytest.approx(7_000.0)


def test_closing_cash():
    f = _make_forecast(opening=500_000, receipts=100_000,
                        wholesale=70_000, network=10_000, policy=5_000, opex=8_000)
    expected_close = 500_000 + 13 * (100_000 - 70_000 - 10_000 - 5_000 - 8_000)
    assert f.closing_cash_gbp == pytest.approx(expected_close)


def test_is_solvent_throughout_true():
    f = _make_forecast()
    assert f.is_solvent_throughout is True


def test_weeks_to_cash_concern_none_when_solvent():
    f = _make_forecast()
    assert f.weeks_to_cash_concern is None


def test_cash_crisis_weeks_to_concern():
    f = _make_forecast(opening=50_000, receipts=100_000,
                        wholesale=100_000, network=15_000, policy=8_000, opex=10_000)
    assert f.is_solvent_throughout is False
    assert f.weeks_to_cash_concern is not None
    assert f.weeks_to_cash_concern <= 13


def test_minimum_weekly_balance():
    f = _make_forecast(opening=100_000, receipts=50_000,
                        wholesale=70_000, network=5_000, policy=3_000, opex=4_000)
    assert f.minimum_weekly_balance_gbp < 100_000


def test_summary_keys():
    f = _make_forecast()
    s = f.summary()
    assert 'closing_cash_gbp' in s
    assert 'is_solvent_throughout' in s
    assert 'weeks_to_cash_concern' in s
    assert 'minimum_weekly_balance_gbp' in s


def test_other_outflows_in_specific_week():
    other = [0.0] * 13
    other[3] = 200_000.0
    f = build_cash_flow_forecast(
        as_of=dt.date(2022, 10, 3),
        opening_cash_gbp=1_000_000,
        weekly_receipts_gbp=100_000,
        weekly_wholesale_gbp=70_000,
        weekly_network_gbp=10_000,
        weekly_policy_gbp=5_000,
        weekly_opex_gbp=8_000,
        other_outflows_by_week=other,
    )
    assert f.weeks[3].total_outflows_gbp == pytest.approx(70_000 + 10_000 + 5_000 + 8_000 + 200_000)
    assert f.weeks[3].net_cash_gbp < 0
