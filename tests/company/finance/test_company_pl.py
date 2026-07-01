import pytest
from company.finance.company_pl import CompanyPL, build_company_pl


def test_build_basic_pl():
    pl = build_company_pl(
        year=2023, revenue_gbp=5_000_000, wholesale_cost_gbp=3_000_000,
        policy_cost_gbp=400_000, network_cost_gbp=600_000,
        operating_cost_gbp=500_000
    )
    assert pl.gross_margin_gbp == pytest.approx(1_000_000.0)
    assert pl.ebitda_gbp == pytest.approx(500_000.0)


def test_gross_margin_pct():
    pl = build_company_pl(
        year=2022, revenue_gbp=10_000_000, wholesale_cost_gbp=7_500_000,
        policy_cost_gbp=500_000, network_cost_gbp=1_000_000, operating_cost_gbp=500_000
    )
    assert pl.gross_margin_pct == pytest.approx(10.0)


def test_ebitda_margin():
    pl = build_company_pl(
        year=2023, revenue_gbp=5_000_000, wholesale_cost_gbp=3_000_000,
        policy_cost_gbp=400_000, network_cost_gbp=600_000,
        operating_cost_gbp=200_000, marketing_cost_gbp=100_000
    )
    assert pl.ebitda_margin_pct == pytest.approx(14.0)


def test_bad_debt_as_pct_revenue():
    pl = build_company_pl(
        year=2022, revenue_gbp=8_000_000, wholesale_cost_gbp=5_000_000,
        policy_cost_gbp=400_000, network_cost_gbp=600_000,
        operating_cost_gbp=500_000, bad_debt_gbp=400_000
    )
    assert pl.bad_debt_as_pct_revenue == pytest.approx(5.0)


def test_is_profitable():
    pl = build_company_pl(
        year=2023, revenue_gbp=5_000_000, wholesale_cost_gbp=3_000_000,
        policy_cost_gbp=400_000, network_cost_gbp=600_000, operating_cost_gbp=500_000
    )
    assert pl.is_profitable is True


def test_loss_making():
    pl = build_company_pl(
        year=2022, revenue_gbp=5_000_000, wholesale_cost_gbp=4_000_000,
        policy_cost_gbp=700_000, network_cost_gbp=900_000,
        operating_cost_gbp=800_000, marketing_cost_gbp=200_000,
        bad_debt_gbp=500_000
    )
    assert pl.ebitda_gbp < 0
    assert pl.is_profitable is False


def test_whd_and_gsop_in_opex():
    pl = build_company_pl(
        year=2023, revenue_gbp=5_000_000, wholesale_cost_gbp=3_000_000,
        policy_cost_gbp=400_000, network_cost_gbp=600_000,
        operating_cost_gbp=400_000, whd_rebates_gbp=75_000, gsop_payments_gbp=5_000
    )
    assert pl.total_operating_cost_gbp == pytest.approx(480_000.0)


def test_pl_is_frozen():
    pl = build_company_pl(
        year=2023, revenue_gbp=5_000_000, wholesale_cost_gbp=3_000_000,
        policy_cost_gbp=400_000, network_cost_gbp=600_000, operating_cost_gbp=500_000
    )
    with pytest.raises(Exception):
        pl.year = 2024


def test_summary_keys():
    pl = build_company_pl(
        year=2023, revenue_gbp=5_000_000, wholesale_cost_gbp=3_000_000,
        policy_cost_gbp=400_000, network_cost_gbp=600_000, operating_cost_gbp=500_000
    )
    s = pl.summary()
    assert 'gross_margin_pct' in s
    assert 'ebitda_margin_pct' in s
    assert 'bad_debt_as_pct_revenue' in s
    assert 'is_profitable' in s


# --- Phase KV depth tests ---

def _pl():
    return build_company_pl(
        year=2022, revenue_gbp=5_000_000.0, wholesale_cost_gbp=3_500_000.0,
        policy_cost_gbp=200_000.0, network_cost_gbp=300_000.0,
        operating_cost_gbp=400_000.0, bad_debt_gbp=50_000.0,
    )


def test_year_stored():
    assert _pl().year == 2022


def test_revenue_stored():
    assert _pl().revenue_gbp == pytest.approx(5_000_000.0)


def test_wholesale_cost_stored():
    assert _pl().wholesale_cost_gbp == pytest.approx(3_500_000.0)


def test_policy_cost_stored():
    assert _pl().policy_cost_gbp == pytest.approx(200_000.0)


def test_network_cost_stored():
    assert _pl().network_cost_gbp == pytest.approx(300_000.0)


def test_operating_cost_stored():
    assert _pl().operating_cost_gbp == pytest.approx(400_000.0)


def test_bad_debt_stored():
    assert _pl().bad_debt_gbp == pytest.approx(50_000.0)


def test_gross_margin_gbp_formula():
    expected = 5_000_000.0 - 3_500_000.0 - 200_000.0 - 300_000.0
    assert _pl().gross_margin_gbp == pytest.approx(expected)


def test_total_opex_includes_bad_debt():
    assert _pl().total_operating_cost_gbp >= _pl().bad_debt_gbp


def test_summary_is_dict():
    s = _pl().summary()
    assert isinstance(s, dict)
    assert 'year' in s
