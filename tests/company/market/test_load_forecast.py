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


def test_portfolio_year_field():
    f = build_portfolio_forecast(2025, resi_accounts=10, sme_accounts=0, ic_accounts=0)
    assert f.year == 2025


def test_sme_gas_annual_mwh():
    f = build_portfolio_forecast(2023, resi_accounts=0, sme_accounts=2, ic_accounts=0)
    assert f.total_gas_mwh == pytest.approx(2 * 55000 / 1000)


def test_resi_gas_q1_steeper_than_elec_q1():
    f = build_portfolio_forecast(2023, resi_accounts=100, sme_accounts=0, ic_accounts=0)
    # Gas Q1 factor (1.55) >> elec Q1 factor (1.18)
    ratio_gas = f.quarterly_gas_mwh('q1') / f.quarterly_gas_mwh('q3')
    ratio_elec = f.quarterly_elec_mwh('q1') / f.quarterly_elec_mwh('q3')
    assert ratio_gas > ratio_elec


def test_quarterly_elec_q4_higher_than_q2():
    f = build_portfolio_forecast(2023, resi_accounts=100, sme_accounts=0, ic_accounts=0)
    assert f.quarterly_elec_mwh('q4') > f.quarterly_elec_mwh('q2')


def test_ic_no_gas_included():
    f = build_portfolio_forecast(2023, resi_accounts=0, sme_accounts=0, ic_accounts=2)
    # IC electricity: 2 × 500000 kWh / 1000 = 1000 MWh; no gas
    assert f.total_gas_mwh == 0.0
    assert f.total_elec_mwh == pytest.approx(1000.0)


def test_segment_count_full_portfolio():
    f = build_portfolio_forecast(2023, resi_accounts=10, sme_accounts=5, ic_accounts=1)
    # RESI elec, SME elec, IC elec, RESI gas, SME gas = 5 segments
    assert len(f.segments) == 5


def test_summary_has_year():
    f = build_portfolio_forecast(2024, resi_accounts=50, sme_accounts=10, ic_accounts=0)
    s = f.summary()
    assert s['year'] == 2024


def test_total_elec_combines_all_segments():
    f = build_portfolio_forecast(2023, resi_accounts=10, sme_accounts=2, ic_accounts=1)
    expected = (10 * 3100 + 2 * 25000 + 1 * 500000) / 1000
    assert f.total_elec_mwh == pytest.approx(expected)


def test_resi_gas_q1_factor_correct():
    # Q1 factor = 1.55; annual = 100 * 12000 / 1000 = 1200 MWh
    f = build_portfolio_forecast(2023, resi_accounts=100, sme_accounts=0, ic_accounts=0)
    gas_segs = [s for s in f.segments if s.segment == 'RESI' and s.commodity == 'gas']
    seg = gas_segs[0]
    assert seg.q1_mwh == pytest.approx(1200.0 * 1.55 / 4, rel=0.01)


def test_segment_count_no_ic():
    f = build_portfolio_forecast(2023, resi_accounts=10, sme_accounts=5, ic_accounts=0)
    # RESI elec, SME elec, RESI gas, SME gas = 4 segments
    assert len(f.segments) == 4
