"""Phase 40c: Deemed rate for out-of-contract I&C customers.

When an I&C customer's fixed term expires and the new contract hasn't been
signed, they move to the deemed rate (day-ahead spot + 20% premium). The
company buys at spot (no forward hedge), billing at spot × 1.20.

Gross margin = spot × 0.20 × consumption per period.
No capital cost in deemed periods (no forward commitment).
"""
import pytest


def test_c_ic1_has_deemed_gap():
    """C_IC1 has deemed_gap_days set."""
    from saas.customers import CUSTOMERS
    c = next(c for c in CUSTOMERS if c["customer_id"] == "C_IC1")
    assert c.get("deemed_gap_days", 0) > 0


def test_c_ic2_has_deemed_gap():
    """C_IC2 has deemed_gap_days set."""
    from saas.customers import CUSTOMERS
    c = next(c for c in CUSTOMERS if c["customer_id"] == "C_IC2")
    assert c.get("deemed_gap_days", 0) > 0


def test_renewal_schedule_inserts_deemed_gaps():
    """build_renewal_schedule inserts deemed gap terms between fixed terms."""
    import json
    from pathlib import Path
    from simulation.renewals import build_renewal_schedule

    cache = Path("sim/cache/elexon_ssp_full.json")
    if not cache.exists():
        pytest.skip("Elexon SSP cache not available")

    records = json.loads(cache.read_text())
    elec_records = [
        r for r in records
        if r.get("settlementDate", "") >= "2016-10-01"
        and r.get("settlementDate", "") <= "2019-12-31"
    ]

    schedule = build_renewal_schedule(
        "C_IC1", "2017-01-01", "2019-06-30",
        elec_records, 2_000_000, segment="I&C",
        tariff_type="fixed", deemed_gap_days=30,
    )

    tariff_types = [t["tariff_type"] for t in schedule]
    # First term is fixed, then alternating deemed/fixed
    assert tariff_types[0] == "fixed"
    assert "deemed" in tariff_types, "Deemed gap terms should be in the schedule"
    # Deemed terms should have no locked unit_rate
    deemed_terms = [t for t in schedule if t["tariff_type"] == "deemed"]
    assert all(t["unit_rate_gbp_per_mwh"] is None for t in deemed_terms)
    assert all(t.get("deemed_premium") == 0.20 for t in deemed_terms)


def test_deemed_gap_is_correct_length():
    """Deemed gap is exactly deemed_gap_days long."""
    import json
    from datetime import date
    from pathlib import Path
    from simulation.renewals import build_renewal_schedule

    cache = Path("sim/cache/elexon_ssp_full.json")
    if not cache.exists():
        pytest.skip("Elexon SSP cache not available")

    records = json.loads(cache.read_text())
    elec_records = [
        r for r in records
        if r.get("settlementDate", "") >= "2016-10-01"
        and r.get("settlementDate", "") <= "2019-12-31"
    ]

    gap_days = 30
    schedule = build_renewal_schedule(
        "C_IC1", "2017-01-01", "2019-06-30",
        elec_records, 2_000_000, segment="I&C",
        tariff_type="fixed", deemed_gap_days=gap_days,
    )

    deemed_terms = [t for t in schedule if t["tariff_type"] == "deemed"]
    assert len(deemed_terms) > 0
    first_deemed = deemed_terms[0]
    gap_start = date.fromisoformat(first_deemed["acquisition_date"])
    gap_end = date.fromisoformat(first_deemed["term_end"])
    assert (gap_end - gap_start).days == gap_days


def test_no_gap_when_zero():
    """build_renewal_schedule with deemed_gap_days=0 produces only fixed terms."""
    import json
    from pathlib import Path
    from simulation.renewals import build_renewal_schedule

    cache = Path("sim/cache/elexon_ssp_full.json")
    if not cache.exists():
        pytest.skip("Elexon SSP cache not available")

    records = json.loads(cache.read_text())
    elec_records = [
        r for r in records
        if r.get("settlementDate", "") >= "2016-10-01"
        and r.get("settlementDate", "") <= "2018-12-31"
    ]

    schedule = build_renewal_schedule(
        "test", "2017-01-01", "2018-06-30",
        elec_records, 1_000_000, segment="I&C",
        tariff_type="fixed", deemed_gap_days=0,
    )

    assert all(t["tariff_type"] == "fixed" for t in schedule)


def test_run_deemed_term_unit_rate_is_spot_plus_premium():
    """Deemed settlement unit_rate = spot × (1 + premium) per period."""
    from simulation.hedged_settlement import run_deemed_term

    spot_price = 80.0
    premium = 0.20
    date_str = "2020-06-01"
    price_records = [
        {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": spot_price}
        for p in range(1, 49)
    ]

    def flat_shape(_date):
        return [100.0] * 48

    records = run_deemed_term(
        customer_id="T",
        term_start_date=date_str,
        term_end_date="2020-06-02",
        deemed_premium=premium,
        consumption_shape=flat_shape,
        system_price_records=price_records,
        segment="I&C",
    )

    assert len(records) == 48
    expected_rate = spot_price * (1.0 + premium)
    for r in records:
        assert abs(r["unit_rate_gbp_per_mwh"] - expected_rate) < 1e-9


def test_run_deemed_term_gross_margin():
    """Deemed gross margin = spot × premium × consumption (the 20% markup)."""
    from simulation.hedged_settlement import run_deemed_term

    spot_price = 100.0
    premium = 0.20
    date_str = "2020-06-01"
    price_records = [
        {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": spot_price}
        for p in range(1, 49)
    ]

    def flat_shape(_date):
        return [1000.0] * 48  # 1 MWh per period (convenient)

    records = run_deemed_term(
        customer_id="T",
        term_start_date=date_str,
        term_end_date="2020-06-02",
        deemed_premium=premium,
        consumption_shape=flat_shape,
        system_price_records=price_records,
        segment="I&C",
    )

    for r in records:
        consumption_mwh = r["consumption_kwh"] / 1000.0
        expected_gross = spot_price * premium * consumption_mwh
        # margin_gbp = revenue - wholesale = spot×(1+p)×mwh - spot×mwh = spot×p×mwh
        assert abs(r["margin_gbp"] - expected_gross) < 1e-9


def test_run_deemed_term_zero_capital():
    """Deemed terms have zero capital cost (no forward hedge commitment)."""
    from simulation.hedged_settlement import run_deemed_term

    date_str = "2020-06-01"
    price_records = [
        {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 50.0}
        for p in range(1, 49)
    ]

    def flat_shape(_date):
        return [100.0] * 48

    records = run_deemed_term(
        "T", date_str, "2020-06-02", 0.20,
        flat_shape, price_records, segment="I&C",
    )
    assert all(r.get("capital_cost_gbp", 0) == 0.0 for r in records)
    assert all(r.get("hedge_fraction", 0) == 0.0 for r in records)


def test_deemed_customer_in_fast_run():
    """Fast-mode sim includes deemed settlement records for C_IC1."""
    import os
    os.environ["SIM_FAST_MODE"] = "1"
    try:
        from simulation.run_phase2b import main
        result = main()
    finally:
        del os.environ["SIM_FAST_MODE"]

    all_records = result.get("all_records", [])
    deemed_recs = [
        r for r in all_records
        if r.get("customer_id") == "C_IC1" and r.get("tariff_type") == "deemed"
    ]
    assert len(deemed_recs) > 0, "C_IC1 should have deemed settlement records (30-day gap)"
    # In deemed periods, company earns 20% above spot
    for r in deemed_recs:
        assert r.get("hedge_fraction", 0.0) == 0.0
        assert r.get("capital_cost_gbp", 0.0) == 0.0


def test_run_deemed_term_customer_id_stored():
    from simulation.hedged_settlement import run_deemed_term
    date_str = "2020-06-01"
    price_records = [{"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 80.0} for p in range(1, 49)]
    records = run_deemed_term("MYTEST", date_str, "2020-06-02", 0.20, lambda _: [100.0]*48, price_records, "I&C")
    assert all(r["customer_id"] == "MYTEST" for r in records)


def test_run_deemed_term_tariff_type_is_deemed():
    from simulation.hedged_settlement import run_deemed_term
    date_str = "2020-06-01"
    price_records = [{"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 80.0} for p in range(1, 49)]
    records = run_deemed_term("T", date_str, "2020-06-02", 0.20, lambda _: [100.0]*48, price_records, "I&C")
    assert all(r.get("tariff_type") == "deemed" for r in records)


def test_run_deemed_term_48_periods_per_day():
    from simulation.hedged_settlement import run_deemed_term
    date_str = "2020-06-01"
    price_records = [{"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 80.0} for p in range(1, 49)]
    records = run_deemed_term("T", date_str, "2020-06-02", 0.20, lambda _: [100.0]*48, price_records, "I&C")
    assert len(records) == 48
