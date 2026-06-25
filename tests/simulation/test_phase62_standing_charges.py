"""Phase 62: Standing charges for resi and SME electricity and gas customers."""
import pytest

def _make_price_records(date_str, spot=80.0):
    return [
        {"settlementDate": date_str, "settlementPeriod": sp, "systemSellPrice": spot}
        for sp in range(1, 49)
    ]

def _make_gas_records(date_str, spot=60.0):
    return [{"settlementDate": date_str, "systemSellPrice": spot}]

def test_elec_sc_resi_returns_positive():
    from simulation.policy_costs import get_electricity_standing_charge_per_day
    for year in range(2016, 2025):
        sc = get_electricity_standing_charge_per_day(f"{year}-06-01", "resi")
        assert sc > 0.0

def test_elec_sc_ic_is_zero():
    from simulation.policy_costs import get_electricity_standing_charge_per_day
    for year in range(2016, 2025):
        sc = get_electricity_standing_charge_per_day(f"{year}-06-01", "I&C")
        assert sc == 0.0

def test_elec_sc_sme_higher_than_resi():
    from simulation.policy_costs import get_electricity_standing_charge_per_day
    for year in range(2016, 2025):
        resi = get_electricity_standing_charge_per_day(f"{year}-06-01", "resi")
        sme = get_electricity_standing_charge_per_day(f"{year}-06-01", "SME")
        assert sme > resi

def test_elec_sc_2022_higher_than_2021():
    from simulation.policy_costs import get_electricity_standing_charge_per_day
    sc_2021 = get_electricity_standing_charge_per_day("2021-06-01", "resi")
    sc_2022 = get_electricity_standing_charge_per_day("2022-12-01", "resi")
    assert sc_2022 > sc_2021 * 1.4

def test_gas_sc_resi_returns_positive():
    from simulation.policy_costs import get_gas_standing_charge_per_day
    for year in range(2016, 2025):
        sc = get_gas_standing_charge_per_day(f"{year}-06-01", "resi")
        assert sc > 0.0

def test_gas_sc_ic_is_zero():
    from simulation.policy_costs import get_gas_standing_charge_per_day
    for year in range(2016, 2025):
        sc = get_gas_standing_charge_per_day(f"{year}-06-01", "I&C")
        assert sc == 0.0

def test_elec_sc_field_present_in_resi_record():
    from simulation.hedged_settlement import run_hedged_term
    records = run_hedged_term(
        customer_id="C1",
        term_start_date="2021-06-01",
        term_end_date="2021-06-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=lambda _: [1000.0] * 48,
        system_price_records=_make_price_records("2021-06-01"),
        segment="resi",
    )
    assert len(records) == 48
    assert "standing_charge_gbp" in records[0]
    assert records[0]["standing_charge_gbp"] > 0.0

def test_elec_sc_prorated_sums_to_daily_rate():
    from simulation.hedged_settlement import run_hedged_term
    from simulation.policy_costs import get_electricity_standing_charge_per_day
    date_str = "2021-06-01"
    records = run_hedged_term(
        customer_id="C1",
        term_start_date=date_str,
        term_end_date="2021-06-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=lambda _: [1000.0] * 48,
        system_price_records=_make_price_records(date_str),
        segment="resi",
    )
    total_sc = sum(r["standing_charge_gbp"] for r in records)
    expected = get_electricity_standing_charge_per_day(date_str, "resi")
    assert abs(total_sc - expected) < 1e-9

def test_elec_sc_zero_for_ic_in_settlement():
    from simulation.hedged_settlement import run_hedged_term
    records = run_hedged_term(
        customer_id="C_IC1",
        term_start_date="2021-06-01",
        term_end_date="2021-06-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=lambda _: [1000.0] * 48,
        system_price_records=_make_price_records("2021-06-01"),
        segment="I&C",
    )
    for r in records:
        assert r["standing_charge_gbp"] == 0.0

def test_gas_sc_field_present_in_resi_record():
    from simulation.gas_settlement import run_gas_term
    recs = run_gas_term(
        customer_id="C1g",
        term_start="2021-06-01",
        term_end="2021-06-02",
        aq_kwh=12_000,
        unit_rate_gbp_mwh=60.0,
        hedge_fraction=0.85,
        forward_price=55.0,
        monthly_cost_of_capital_gbp=0.0,
        gas_price_records=_make_gas_records("2021-06-01"),
        segment="resi",
    )
    assert len(recs) == 1
    assert "gas_standing_charge_gbp" in recs[0]
    assert recs[0]["gas_standing_charge_gbp"] > 0.0

def test_gas_sc_zero_for_ic_gas():
    from simulation.gas_settlement import run_gas_term
    recs = run_gas_term(
        customer_id="C_IC3g",
        term_start="2021-06-01",
        term_end="2021-06-02",
        aq_kwh=5_000_000,
        unit_rate_gbp_mwh=60.0,
        hedge_fraction=0.85,
        forward_price=55.0,
        monthly_cost_of_capital_gbp=0.0,
        gas_price_records=_make_gas_records("2021-06-01"),
        segment="I&C",
    )
    assert len(recs) == 1
    assert recs[0]["gas_standing_charge_gbp"] == 0.0

def test_elec_revenue_includes_sc_above_unit_rate():
    from simulation.hedged_settlement import run_hedged_term
    from simulation.policy_costs import get_electricity_standing_charge_per_day
    date_str = "2020-06-01"
    unit_rate = 80.0
    records = run_hedged_term(
        customer_id="C1",
        term_start_date=date_str,
        term_end_date="2020-06-02",
        fixed_tariff_rate_gbp_per_mwh=unit_rate,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=1.0,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=lambda _: [500.0] * 48,
        system_price_records=_make_price_records(date_str),
        segment="resi",
    )
    total_revenue = sum(r["revenue_gbp"] for r in records)
    total_mwh = sum(r["consumption_kwh"] for r in records) / 1000.0
    unit_only = unit_rate * total_mwh
    daily_sc = get_electricity_standing_charge_per_day(date_str, "resi")
    assert abs(total_revenue - (unit_only + daily_sc)) < 1e-6
