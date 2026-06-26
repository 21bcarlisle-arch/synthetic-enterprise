import pytest
from company.market.load_forecast import (
    SegmentLoadForecast, PortfolioLoadForecast, build_portfolio_forecast
)


def test_build_resi_only():
    f = build_portfolio_forecast(2023, resi_accounts=100, sme_accounts=0, ic_accounts=0)
    assert f.total_elec_mwh == pytest.approx(310.0)
    assert f.total_gas_mwh == pytest.approx(1200.0)


def test_build_with_sme():
    f = build_portfolio_forecast(2023, resi_accounts=0, sme_accounts=10, ic_accounts=0)
    assert f.total_elec_mwh == pytest.approx(250.0)


def test_ic_electricity_large():
    f = build_portfolio_forecast(2023, resi_accounts=0, sme_accounts=0, ic_accounts=1)
    assert f.total_elec_mwh == pytest.approx(500.0)


def test_no_gas_for_ic():
    f = build_portfolio_forecast(2023, resi_accounts=0, sme_accounts=0, ic_accounts=1)
    assert f.total_gas_mwh == 0.0


def test_quarterly_elec_q1_highest():
    f = build_portfolio_forecast(2023, resi_accounts=100, sme_accounts=0, ic_accounts=0)
    assert f.quarterly_elec_mwh('q1') > f.quarterly_elec_mwh('q3')


def test_quarterly_gas_q1_much_higher_than_q3():
    f = build_portfolio_forecast(2023, resi_accounts=100, sme_accounts=0, ic_accounts=0)
    assert f.quarterly_gas_mwh('q1') > f.quarterly_gas_mwh('q3') * 2


def test_summary_keys():
    f = build_portfolio_forecast(2023, resi_accounts=100, sme_accounts=5, ic_accounts=0)
    s = f.summary()
    assert 'total_elec_mwh' in s
    assert 'q1_gas_mwh' in s
    assert 'q3_elec_mwh' in s


def test_exclude_gas():
    f = build_portfolio_forecast(2023, resi_accounts=100, sme_accounts=0, ic_accounts=0, include_gas=False)
    assert f.total_gas_mwh == 0.0
    assert f.total_elec_mwh > 0.0


def test_monthly_avg_mwh():
    f = build_portfolio_forecast(2023, resi_accounts=12, sme_accounts=0, ic_accounts=0)
    elec_seg = [s for s in f.segments if s.segment == 'RESI' and s.commodity == 'electricity'][0]
    assert elec_seg.monthly_avg_mwh == pytest.approx(12 * 3.1 / 12, rel=0.01)
