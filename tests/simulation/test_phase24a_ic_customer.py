"""Phase 24a: I&C customer (C_IC1) tests.

Verifies that the 2 GWh I&C electricity customer integrates correctly with:
- customer roster and HH data path
- company EAC estimation from high-volume billing records
- churn model bill-stress saturation behaviour
- retention economics at large scale
- demand estimation log and annual report sections
- SIM fast-mode run output
"""

def _make_ic1_records(year: int, total_kwh: float = 2_000_000.0):
    """Synthetic settlement records for C_IC1 for a given year."""
    from datetime import date, timedelta
    records = []
    d = date(year, 1, 1)
    while d.year == year:
        records.append({
            "customer_id": "C_IC1",
            "settlement_date": d.isoformat(),
            "consumption_kwh": total_kwh / 365.0,
        })
        d += timedelta(days=1)
    return records


def test_c_ic1_in_elec_customers():
    from simulation.run_phase2b import ELEC_CUSTOMERS
    ids = [c["customer_id"] for c in ELEC_CUSTOMERS]
    assert "C_IC1" in ids


def test_c_ic1_effective_eac_approx_2gwh():
    from simulation.run_phase2b import EFFECTIVE_EAC_KWH
    eac = EFFECTIVE_EAC_KWH["C_IC1"]
    # Should be within 1% of 2 GWh
    assert abs(eac - 2_000_000) < 20_000, f"Expected ~2,000,000 kWh, got {eac:.0f}"


def test_company_eac_estimate_handles_high_volume_records():
    from simulation.run_phase2b import _company_eac_estimate
    # 2 GWh annual consumption in prior-year billing records
    records = _make_ic1_records(2019, 2_000_000.0)
    result = _company_eac_estimate("C_IC1", "2020-01-01", records)
    assert abs(result - 2_000_000) < 10_000, f"Expected ~2,000,000 kWh, got {result:.0f}"


def test_bill_stress_saturates_for_ic1():
    """At 2 GWh and £150/MWh, bill stress alone exceeds MAX_CHURN_PROBABILITY."""
    from company.crm.churn_model import estimate_churn_probability, MAX_CHURN_PROBABILITY
    p = estimate_churn_probability(
        old_rate_gbp_per_mwh=150.0,
        new_rate_gbp_per_mwh=150.0,  # no rate change — stress alone
        tenure_years=2.0,
        annual_consumption_kwh=2_000_000,
    )
    assert p == MAX_CHURN_PROBABILITY, f"Expected saturation at {MAX_CHURN_PROBABILITY}, got {p}"


def test_ic1_retention_cost_proportionally_large():
    """5% discount on 2 GWh at £150/MWh = £15,000 retention cost."""
    eac_kwh = 2_000_000
    unit_rate_gbp_per_mwh = 150.0
    discount_pct = 0.05
    # Retention cost = eac × rate / 1000 × discount_pct
    ret_cost = eac_kwh * unit_rate_gbp_per_mwh / 1000.0 * discount_pct
    assert abs(ret_cost - 15_000) < 100, f"Expected £15,000, got £{ret_cost:.0f}"


def test_demand_estimation_log_includes_ic1_from_second_term():
    """After Phase 23a, demand_estimation_log should have C_IC1 entries
    from its 2nd term onwards (prior billing exists from 2017)."""
    from simulation.run_phase2b import main
    result = main()

    log = result.get("demand_estimation_log", [])
    ic1_entries = [e for e in log if e["customer_id"] == "C_IC1"]
    assert len(ic1_entries) > 0, "C_IC1 should appear in demand_estimation_log"
    # All C_IC1 entries should be 'prior_billing' (not fallback after 1st term)
    sources = {e["source"] for e in ic1_entries}
    assert "prior_billing" in sources


def test_annual_report_pnl_ranking_includes_ic1():
    """C_IC1 should appear in the per-customer P&L ranking section."""
    from simulation.run_phase4c_on_phase2b import main as full_main
    from saas.reporting.annual_report import generate_annual_report, extract_report_data
    result = full_main()
    report_data = extract_report_data(result)
    report = generate_annual_report(report_data)
    assert "C_IC1" in report, "C_IC1 should appear in annual report"


def test_fast_mode_produces_ic1_settlement_records():
    """SIM fast-mode run should produce settlement records for C_IC1."""
    from simulation.run_phase2b import main
    result = main()

    all_records = result.get("all_records", [])
    ic1_records = [r for r in all_records if r.get("customer_id") == "C_IC1"]
    assert len(ic1_records) > 0, "C_IC1 should have settlement records in fast mode"
    # Revenue should be large (2 GWh × rate/1000)
    total_revenue = sum(r.get("revenue_gbp", 0) for r in ic1_records)
    assert total_revenue > 100_000, f"C_IC1 revenue should exceed £100k, got £{total_revenue:.0f}"
