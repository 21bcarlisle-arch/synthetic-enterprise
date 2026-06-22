"""Phase 40b: I&C gas pass-through tariff + tariff type in annual report.

C_IC3g is a 5 GWh industrial gas customer on a pass-through tariff.
Gas pass-through: NBP spot + margin locked; actual gas CCL, GGL, and
network charges billed at settlement and passed through to customer.
Net_margin = wholesale spread only (policy/network cancel).
"""
import pytest


def test_c_ic3g_customer_defined():
    """C_IC3g is in the customer list with pass-through tariff type."""
    from saas.customers import CUSTOMERS
    c = next((c for c in CUSTOMERS if c["customer_id"] == "C_IC3g"), None)
    assert c is not None
    assert c["tariff_type"] == "pass_through"
    assert c["commodity"] == "gas"
    assert c["segment"] == "I&C"
    assert c["aq_kwh"] == 5_000_000


def test_gas_pass_through_renewal_rate_lower():
    """Pass-through gas unit_rate excludes policy/network — lower than fixed equivalent."""
    from pathlib import Path
    from simulation.run_phase2b import _build_gas_renewal_schedule
    from saas.customers import CUSTOMERS
    from sim.gas_prices_history import load_nbp_history

    if not Path("sim/gas_data/nbp_sap.csv").exists():
        pytest.skip("NBP gas price data not available")

    gas_records = load_nbp_history()
    c_ic3g = next(c for c in CUSTOMERS if c["customer_id"] == "C_IC3g")

    pt_schedule = _build_gas_renewal_schedule(
        c_ic3g, gas_records, report_end="2020-12-31", tariff_type="pass_through",
    )
    fixed_schedule = _build_gas_renewal_schedule(
        c_ic3g, gas_records, report_end="2020-12-31", tariff_type="fixed",
    )

    assert len(pt_schedule) > 0
    assert len(fixed_schedule) > 0
    pt_rate = pt_schedule[0]["unit_rate_gbp_per_mwh"]
    fixed_rate = fixed_schedule[0]["unit_rate_gbp_per_mwh"]
    assert fixed_rate > pt_rate, (
        f"Fixed gas rate ({fixed_rate:.2f}) should exceed pass-through ({pt_rate:.2f})"
    )


def test_gas_pass_through_tariff_type_in_schedule():
    """Gas renewal schedule stores tariff_type in each term."""
    from pathlib import Path
    from simulation.run_phase2b import _build_gas_renewal_schedule
    from saas.customers import CUSTOMERS
    from sim.gas_prices_history import load_nbp_history

    if not Path("sim/gas_data/nbp_sap.csv").exists():
        pytest.skip("NBP gas price data not available")

    gas_records = load_nbp_history()
    c_ic3g = next(c for c in CUSTOMERS if c["customer_id"] == "C_IC3g")

    schedule = _build_gas_renewal_schedule(
        c_ic3g, gas_records, report_end="2020-12-31", tariff_type="pass_through",
    )
    assert all(t.get("tariff_type") == "pass_through" for t in schedule)


def test_gas_pass_through_revenue_higher():
    """Pass-through gas revenue includes actual policy+network costs."""
    from simulation.gas_settlement import run_gas_term

    date_str = "2020-06-01"
    price_records = [
        {"settlementDate": date_str, "systemSellPrice": 20.0}
    ]

    kwargs = dict(
        customer_id="T",
        term_start=date_str,
        term_end="2020-06-02",
        aq_kwh=5_000_000,
        unit_rate_gbp_mwh=25.0,
        hedge_fraction=0.9,
        forward_price=20.0,
        monthly_cost_of_capital_gbp=0.0,
        gas_price_records=price_records,
        segment="I&C",
    )

    fixed_recs = run_gas_term(**kwargs, pass_through=False)
    pt_recs = run_gas_term(**kwargs, pass_through=True)

    assert len(fixed_recs) == len(pt_recs) == 1
    # Pass-through has higher revenue (gas_policy + gas_network added)
    assert pt_recs[0]["revenue_gbp"] > fixed_recs[0]["revenue_gbp"]


def test_gas_pass_through_net_margin_cancels():
    """Gas pass-through net_margin = revenue - wholesale - policy - network - capital.
    Policy+network cancel so net_margin = (wholesale_rate × vol) - wholesale_cost - capital.
    """
    from simulation.gas_settlement import run_gas_term

    date_str = "2020-06-01"
    price_records = [{"settlementDate": date_str, "systemSellPrice": 20.0}]

    pt_recs = run_gas_term(
        customer_id="T",
        term_start=date_str,
        term_end="2020-06-02",
        aq_kwh=5_000_000,
        unit_rate_gbp_mwh=25.0,
        hedge_fraction=1.0,
        forward_price=20.0,
        monthly_cost_of_capital_gbp=0.0,
        gas_price_records=price_records,
        segment="I&C",
        pass_through=True,
    )
    assert len(pt_recs) == 1
    r = pt_recs[0]
    expected_net = (
        r["margin_gbp"]
        - r["gas_policy_cost_gbp"]
        - r["gas_network_cost_gbp"]
        - r.get("capital_cost_gbp", 0.0)
    )
    assert abs(r["net_margin_gbp"] - expected_net) < 1e-9


def test_annual_report_shows_tariff_type():
    """Customer P&L ranking table includes tariff type column."""
    from saas.reporting.annual_report import _section_customer_pnl_ranking

    data = {
        "per_cid_pnl": {
            "C_IC3": {"gross": 5000.0, "capital": 100.0, "net": 4900.0, "revenue": 50000.0},
            "C1": {"gross": 2000.0, "capital": 50.0, "net": 1950.0, "revenue": 20000.0},
        }
    }
    section = _section_customer_pnl_ranking(data)
    assert "Tariff" in section
    assert "pass_through" in section  # C_IC3 should show pass_through
    assert "fixed" in section  # C1 (resi) should show fixed


def test_existing_gas_customers_default_fixed():
    """Existing resi gas customers (C1g-C4g) default to fixed tariff type."""
    from saas.customers import CUSTOMERS
    resi_gas = [c for c in CUSTOMERS if c.get("commodity") == "gas" and c["customer_id"] != "C_IC3g"]
    assert len(resi_gas) > 0
    for c in resi_gas:
        assert c.get("tariff_type", "fixed") == "fixed", (
            f"{c['customer_id']} should default to fixed, got {c.get('tariff_type')}"
        )


def test_gas_pass_through_customer_in_fast_run():
    """Fast-mode sim includes C_IC3g gas settlement records."""
    import os
    os.environ["SIM_FAST_MODE"] = "1"
    try:
        from simulation.run_phase2b import main
        result = main()
    finally:
        del os.environ["SIM_FAST_MODE"]

    all_records = result.get("all_settlement_records", [])
    ic3g_records = [r for r in all_records if r.get("customer_id") == "C_IC3g"]
    assert len(ic3g_records) > 0, "C_IC3g should have gas settlement records in fast mode"
    assert all(r.get("commodity") == "gas" for r in ic3g_records)
    total_revenue = sum(r["revenue_gbp"] for r in ic3g_records)
    assert total_revenue > 100_000, (
        f"C_IC3g (5GWh gas, pass-through) revenue should exceed £100k, got £{total_revenue:,.0f}"
    )
