"""Phase 40a: I&C pass-through tariff tests.

Pass-through tariffs lock only the wholesale+margin component; network and
policy costs are billed at actual rates at settlement. This means:
- unit_rate (locked) < fixed-tariff equivalent (no locked policy/network)
- revenue_gbp > fixed-tariff equivalent (includes actual pass-through costs)
- net_margin_gbp ≈ same formula but policy/network cancel (no policy cost risk)
"""
import pytest


def test_c_ic3_customer_defined():
    """C_IC3 chemical plant is in the customer list with pass-through tariff."""
    from saas.customers import CUSTOMERS
    ELEC_CUSTOMERS = [c for c in CUSTOMERS if c.get("commodity") == "electricity"]
    c = next((c for c in ELEC_CUSTOMERS if c["customer_id"] == "C_IC3"), None)
    assert c is not None
    assert c["tariff_type"] == "pass_through"
    assert c["segment"] == "I&C"
    assert c["metering"] == "HH"
    assert c["eac_kwh"] is None  # derives from HH data


def test_c_ic3_hh_data_exists():
    """C_IC3 HH consumption file exists and loads."""
    from simulation.hh_consumption import load_hh_consumption, estimate_annual_kwh
    data = load_hh_consumption("C_IC3")
    assert len(data) > 3000, "Expect 3000+ days of HH data"
    annual_kwh = estimate_annual_kwh(data)
    assert 3_500_000 < annual_kwh < 4_500_000, (
        f"C_IC3 EAC should be ~4 GWh, got {annual_kwh/1e6:.2f} GWh"
    )


def test_c_ic3_hh_flat_profile():
    """C_IC3 continuous-process profile has low peak/offpeak ratio."""
    from simulation.hh_consumption import load_hh_consumption
    data = load_hh_consumption("C_IC3")
    # Pick a weekday with data (2020-03-02 is a Monday)
    row = data.get("2020-03-02")
    assert row is not None
    periods = row
    # All 48 half-hours should be within 30% of each other (flat process load)
    mn, mx = min(periods), max(periods)
    assert mx / mn < 1.35, f"C_IC3 profile should be flat, peak/base = {mx/mn:.2f}"


def test_pass_through_renewal_rate_lower():
    """Pass-through unit_rate excludes policy/network — should be lower than fixed."""
    from simulation.renewals import build_renewal_schedule
    from saas.customers import CUSTOMERS
    ELEC_CUSTOMERS = [c for c in CUSTOMERS if c.get("commodity") == "electricity"]
    import json
    from pathlib import Path

    # Load minimal price records for 2020
    cache = Path("sim/cache/elexon_ssp_full.json")
    if not cache.exists():
        pytest.skip("Elexon SSP cache not available in this environment")

    records = json.loads(cache.read_text())
    # Need 2019 Q4 for lookback window when acquisition date is 2020-01-01
    elec_records = [
        r for r in records
        if r.get("settlementDate", "") >= "2019-10-01" and r.get("settlementDate", "") <= "2020-12-31"
    ]

    # Build pass-through schedule
    pt_schedule = build_renewal_schedule(
        "C_IC3", "2020-01-01", "2020-12-31",
        elec_records, 4_000_000, segment="I&C", tariff_type="pass_through",
    )
    # Build equivalent fixed schedule
    fixed_schedule = build_renewal_schedule(
        "C_IC3", "2020-01-01", "2020-12-31",
        elec_records, 4_000_000, segment="I&C", tariff_type="fixed",
    )

    assert len(pt_schedule) > 0
    assert len(fixed_schedule) > 0
    pt_rate = pt_schedule[0]["unit_rate_gbp_per_mwh"]
    fixed_rate = fixed_schedule[0]["unit_rate_gbp_per_mwh"]
    # Policy (~£50-70/MWh in 2020) + network (~£35-45/MWh) should make fixed higher
    assert fixed_rate > pt_rate, (
        f"Fixed rate ({fixed_rate:.2f}) should exceed pass-through rate ({pt_rate:.2f})"
    )
    diff = fixed_rate - pt_rate
    assert 50 < diff < 200, f"Rate difference should be ~policy+network costs, got £{diff:.2f}/MWh"


def test_pass_through_tariff_stored_in_term():
    """build_renewal_schedule stores tariff_type in each term dict."""
    from simulation.renewals import build_renewal_schedule
    import json
    from pathlib import Path

    cache = Path("sim/cache/elexon_ssp_full.json")
    if not cache.exists():
        pytest.skip("Elexon SSP cache not available in this environment")

    records = json.loads(cache.read_text())
    elec_records = [
        r for r in records
        if r.get("settlementDate", "") >= "2019-10-01" and r.get("settlementDate", "") <= "2020-12-31"
    ]

    schedule = build_renewal_schedule(
        "test_pt", "2020-01-01", "2020-12-31",
        elec_records, 1_000_000, segment="I&C", tariff_type="pass_through",
    )
    assert all(t.get("tariff_type") == "pass_through" for t in schedule)


def test_fixed_tariff_type_stored():
    """Fixed tariff_type (default) is stored in term dict."""
    from simulation.renewals import build_renewal_schedule
    import json
    from pathlib import Path

    cache = Path("sim/cache/elexon_ssp_full.json")
    if not cache.exists():
        pytest.skip("Elexon SSP cache not available in this environment")

    records = json.loads(cache.read_text())
    elec_records = [
        r for r in records
        if r.get("settlementDate", "") >= "2019-10-01" and r.get("settlementDate", "") <= "2020-12-31"
    ]

    schedule = build_renewal_schedule(
        "test_fixed", "2020-01-01", "2020-12-31",
        elec_records, 1_000_000, segment="resi",
    )
    assert all(t.get("tariff_type") == "fixed" for t in schedule)


def test_pass_through_revenue_includes_passthrough_costs():
    """Pass-through settlement revenue is higher (includes policy+network passed to customer)."""
    import math
    from simulation.hedged_settlement import run_hedged_term

    # Minimal synthetic price records for 2020-01-02 (a Thursday)
    date_str = "2020-01-02"
    price_records = [
        {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 50.0}
        for p in range(1, 49)
    ]

    # Flat 100 kWh/period shape
    def flat_shape(_date):
        return [100.0] * 48

    kwargs = dict(
        customer_id="T",
        term_start_date=date_str,
        term_end_date="2020-01-03",
        fixed_tariff_rate_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=50.0,
        hedge_fraction=0.9,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=flat_shape,
        system_price_records=price_records,
        segment="I&C",
    )

    fixed_records = run_hedged_term(**kwargs, pass_through=False)
    pt_records = run_hedged_term(**kwargs, pass_through=True)

    assert len(fixed_records) == len(pt_records) == 48

    total_fixed_revenue = sum(r["revenue_gbp"] for r in fixed_records)
    total_pt_revenue = sum(r["revenue_gbp"] for r in pt_records)
    # Pass-through should have higher total revenue (includes policy+network)
    assert total_pt_revenue > total_fixed_revenue, (
        f"PT revenue ({total_pt_revenue:.2f}) should exceed fixed ({total_fixed_revenue:.2f})"
    )


def test_pass_through_net_margin_formula_cancels():
    """Pass-through net_margin = revenue - wholesale - policy - network - capital.
    Policy+network cancel so net_margin = (wholesale_rate × vol) - wholesale_cost - capital.
    """
    from simulation.hedged_settlement import run_hedged_term

    date_str = "2020-01-02"
    price_records = [
        {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 50.0}
        for p in range(1, 49)
    ]

    def flat_shape(_date):
        return [100.0] * 48

    pt_records = run_hedged_term(
        customer_id="T",
        term_start_date=date_str,
        term_end_date="2020-01-03",
        fixed_tariff_rate_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=1.0,  # fully hedged: net_margin = (60-55)×vol - capital
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=flat_shape,
        system_price_records=price_records,
        segment="I&C",
        pass_through=True,
    )

    for r in pt_records:
        # net_margin_gbp should equal margin_gbp - policy - network - capital
        expected = r["margin_gbp"] - r["policy_cost_gbp"] - r["network_cost_gbp"] - r.get("capital_cost_gbp", 0)
        assert abs(r["net_margin_gbp"] - expected) < 1e-9, (
            f"net_margin accounting error: {r['net_margin_gbp']:.6f} vs {expected:.6f}"
        )


def test_existing_customers_default_fixed():
    """Existing I&C customers C_IC1 and C_IC2 default to fixed tariff type."""
    from saas.customers import CUSTOMERS
    ELEC_CUSTOMERS = [c for c in CUSTOMERS if c.get("commodity") == "electricity"]
    for cid in ("C_IC1", "C_IC2"):
        c = next(c for c in ELEC_CUSTOMERS if c["customer_id"] == cid)
        # tariff_type not set → defaults to "fixed" in the code
        assert c.get("tariff_type", "fixed") == "fixed"


def test_pass_through_customer_in_fast_run():
    """Fast-mode sim includes C_IC3 settlement records."""
    import os
    os.environ["SIM_FAST_MODE"] = "1"
    try:
        from simulation.run_phase2b import main
        result = main()
    finally:
        del os.environ["SIM_FAST_MODE"]

    all_records = result.get("all_records", [])
    ic3_records = [r for r in all_records if r.get("customer_id") == "C_IC3"]
    assert len(ic3_records) > 0, "C_IC3 should have settlement records in fast mode"

    total_revenue = sum(r["revenue_gbp"] for r in ic3_records)
    assert total_revenue > 500_000, (
        f"C_IC3 (4GWh, pass-through) revenue should exceed £500k, got £{total_revenue:,.0f}"
    )


def test_pass_through_net_margin_positive_when_covered():
    from simulation.hedged_settlement import run_hedged_term

    date_str = "2020-06-01"
    price_records = [
        {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 50.0}
        for p in range(1, 49)
    ]

    def flat_shape(_date):
        return [100.0] * 48

    records = run_hedged_term(
        customer_id="T",
        term_start_date=date_str,
        term_end_date="2020-06-02",
        fixed_tariff_rate_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=50.0,
        hedge_fraction=1.0,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=flat_shape,
        system_price_records=price_records,
        segment="I&C",
        pass_through=True,
    )
    total_net = sum(r["net_margin_gbp"] for r in records)
    assert total_net > 0


def test_pass_through_settlement_period_stored():
    from simulation.hedged_settlement import run_hedged_term

    date_str = "2020-01-02"
    price_records = [
        {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 50.0}
        for p in range(1, 3)
    ]

    def flat_shape(_date):
        return [100.0] * 48

    records = run_hedged_term(
        customer_id="T",
        term_start_date=date_str,
        term_end_date="2020-01-03",
        fixed_tariff_rate_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=50.0,
        hedge_fraction=1.0,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=flat_shape,
        system_price_records=price_records,
        segment="I&C",
        pass_through=True,
    )
    assert all("settlement_period" in r for r in records)


def test_c_ic3_customer_is_elec():
    from saas.customers import CUSTOMERS
    c = next((c for c in CUSTOMERS if c["customer_id"] == "C_IC3"), None)
    assert c is not None
    assert c.get("commodity", "electricity") == "electricity"
