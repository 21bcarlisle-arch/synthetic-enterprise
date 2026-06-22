"""Phase 29a: Network charges (DUoS + TNUoS) for electricity customers."""

import pytest
from simulation.policy_costs import (
    get_electricity_network_cost_per_mwh,
    _NETWORK_COST_RESI_SME_BY_YEAR,
    _DUOS_IC_BY_YEAR,
)


def test_resi_network_cost_2020():
    """Resi/SME combined DUoS+TNUoS rate for 2020."""
    assert get_electricity_network_cost_per_mwh("2020-06-01", segment="resi") == pytest.approx(38.0)


def test_ic_network_cost_2020():
    """I&C DUoS-only rate for 2020 — lower because Triad TNUoS is separate."""
    assert get_electricity_network_cost_per_mwh("2020-06-01", segment="I&C") == pytest.approx(12.0)


def test_ic_rate_lower_than_resi():
    """I&C DUoS-only rate is always lower than resi combined rate."""
    for year in range(2016, 2025):
        date_str = f"{year}-06-01"
        resi = get_electricity_network_cost_per_mwh(date_str, segment="resi")
        ic = get_electricity_network_cost_per_mwh(date_str, segment="I&C")
        assert ic < resi, f"I&C {ic} should be < resi {resi} in {year}"


def test_2022_step_up():
    """2022 sees a step-up in resi rates (RIIO-ED2 transition)."""
    rate_2021 = get_electricity_network_cost_per_mwh("2021-06-01", segment="resi")
    rate_2022 = get_electricity_network_cost_per_mwh("2022-06-01", segment="resi")
    assert rate_2022 > rate_2021


def test_all_resi_years_defined():
    """All years 2016-2024 have resi/SME combined rates defined."""
    for year in range(2016, 2025):
        assert year in _NETWORK_COST_RESI_SME_BY_YEAR


def test_all_ic_years_defined():
    """All years 2016-2024 have I&C DUoS rates defined."""
    for year in range(2016, 2025):
        assert year in _DUOS_IC_BY_YEAR


def test_clamps_pre_2016():
    """Dates before 2016 clamp to the 2016 rate."""
    assert get_electricity_network_cost_per_mwh("2010-01-01", segment="resi") == pytest.approx(
        _NETWORK_COST_RESI_SME_BY_YEAR[2016]
    )


def test_clamps_post_2024():
    """Dates after 2024 clamp to the 2024 rate."""
    assert get_electricity_network_cost_per_mwh("2030-01-01", segment="resi") == pytest.approx(
        _NETWORK_COST_RESI_SME_BY_YEAR[2024]
    )


def test_default_segment_is_resi():
    """Default segment is resi — calling without segment arg gives resi rate."""
    assert get_electricity_network_cost_per_mwh("2020-06-01") == pytest.approx(
        get_electricity_network_cost_per_mwh("2020-06-01", segment="resi")
    )


def test_sme_segment_uses_resi_table():
    """SME segment uses the same combined DUoS+TNUoS table as resi."""
    assert get_electricity_network_cost_per_mwh("2022-06-01", segment="SME") == pytest.approx(
        get_electricity_network_cost_per_mwh("2022-06-01", segment="resi")
    )


def test_settlement_record_has_network_cost_field():
    """Settlement records include network_cost_gbp field (Phase 29a)."""
    from simulation.hedged_settlement import run_hedged_term

    price_records = [
        {"settlementDate": "2021-06-01", "settlementPeriod": sp, "systemSellPrice": 80.0}
        for sp in range(1, 49)
    ]

    def shape(_date):
        return [1.0] * 48

    records = run_hedged_term(
        customer_id="C1",
        term_start_date="2021-06-01",
        term_end_date="2021-06-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=shape,
        system_price_records=price_records,
        segment="resi",
    )
    assert len(records) == 48
    assert "network_cost_gbp" in records[0]
    # resi 2021: £38/MWh, 1 kWh = 0.001 MWh per period
    expected_per_period = 38.0 * (1.0 / 1000)
    assert records[0]["network_cost_gbp"] == pytest.approx(expected_per_period)


def test_ic_settlement_uses_duos_only():
    """I&C settlement records use DUoS-only rate (lower than resi)."""
    from simulation.hedged_settlement import run_hedged_term

    price_records = [
        {"settlementDate": "2021-06-01", "settlementPeriod": sp, "systemSellPrice": 80.0}
        for sp in range(1, 49)
    ]

    def shape(_date):
        return [1000.0] * 48  # 1 MWh per period

    records_ic = run_hedged_term(
        customer_id="C_IC1",
        term_start_date="2021-06-01",
        term_end_date="2021-06-02",
        fixed_tariff_rate_gbp_per_mwh=150.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=shape,
        system_price_records=price_records,
        segment="I&C",
    )
    records_resi = run_hedged_term(
        customer_id="C1",
        term_start_date="2021-06-01",
        term_end_date="2021-06-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=shape,
        system_price_records=price_records,
        segment="resi",
    )
    # I&C: £12/MWh; resi: £38/MWh for 2021
    assert records_ic[0]["network_cost_gbp"] == pytest.approx(12.0)
    assert records_resi[0]["network_cost_gbp"] == pytest.approx(38.0)
    assert records_ic[0]["network_cost_gbp"] < records_resi[0]["network_cost_gbp"]


def test_tariff_includes_network_cost():
    """price_fixed_tariff() includes network_cost_per_mwh in the returned rate."""
    from saas.tariff_pricing import price_fixed_tariff

    base = price_fixed_tariff(100.0, 3000, "2021-01-01", network_cost_per_mwh=0.0)
    with_net = price_fixed_tariff(100.0, 3000, "2021-01-01", network_cost_per_mwh=38.0)
    assert with_net == pytest.approx(base + 38.0)


def test_network_costs_section_renders_table():
    """_section_network_costs renders a markdown table with correct figures."""
    from saas.reporting.annual_report import _section_network_costs

    data = {"years": {"2021": {"network_cost_gbp": 12345.6}, "2022": {"network_cost_gbp": 18000.0}}}
    result = _section_network_costs(data)
    assert "Network Charges" in result
    assert "12,346" in result  # £12,345.6 rounds to 12,346
    assert "18,000" in result
    assert "step-up RIIO-ED2" in result  # 2022 note


def test_network_costs_section_silent_for_pre29a_data():
    """_section_network_costs returns empty string when no network_cost_gbp data."""
    from saas.reporting.annual_report import _section_network_costs
    data = {"years": {"2021": {"net_gbp": 100.0}}}
    assert _section_network_costs(data) == ""
