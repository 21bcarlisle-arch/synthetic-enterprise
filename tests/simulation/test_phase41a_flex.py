"""Phase 41a: Flex/trading tariff for I&C customers.

A flex contract has no locked unit rate. The customer calls volumes weekly
at the day-ahead reference price (7-day rolling spot average). The supplier
earns a fixed trading desk markup (£2/MWh) per unit sold.

Key invariants:
- Gross margin = markup × consumption (predictable, markup-only)
- Capital cost = 0 (no naked exposure — hedged weekly at reference)
- Hedge fraction = 1.0 (fully covered at reference price)
- Net margin = markup × consumption − policy costs − network costs
"""
import pytest


def test_c_ic4_defined_with_flex_tariff():
    """C_IC4 is in the customer list with flex tariff type."""
    from saas.customers import CUSTOMERS
    c = next((c for c in CUSTOMERS if c["customer_id"] == "C_IC4"), None)
    assert c is not None
    assert c["tariff_type"] == "flex"
    assert c["commodity"] == "electricity"
    assert c["segment"] == "I&C"
    assert c["metering"] == "HH"


def test_c_ic4_hh_data_loads():
    """C_IC4 HH data file loads and has correct annual consumption."""
    from simulation.hh_consumption import estimate_annual_kwh, load_hh_consumption
    data = load_hh_consumption("C_IC4")
    assert len(data) > 0
    annual_kwh = estimate_annual_kwh(data)
    assert 2_500_000 < annual_kwh < 3_500_000, f"C_IC4 annual: {annual_kwh:,.0f} kWh"


def test_flex_markup_constant():
    """FLEX_MARKUP_PER_MWH is £2/MWh."""
    from simulation.renewals import FLEX_MARKUP_PER_MWH
    assert FLEX_MARKUP_PER_MWH == 2.0


def test_flex_renewal_schedule_has_no_locked_rate():
    """build_renewal_schedule for flex returns unit_rate=None (no locked rate)."""
    import json
    from pathlib import Path
    from simulation.renewals import build_renewal_schedule

    cache = Path("sim/cache/elexon_ssp_full.json")
    if not cache.exists():
        pytest.skip("Elexon SSP cache not available")

    records = json.loads(cache.read_text())
    elec = [r for r in records if "2019-10-01" <= r.get("settlementDate", "") <= "2021-12-31"]

    schedule = build_renewal_schedule(
        "C_IC4", "2020-01-01", "2021-12-31",
        elec, 3_000_000, segment="I&C", tariff_type="flex",
    )

    assert len(schedule) > 0
    for term in schedule:
        assert term["tariff_type"] == "flex"
        assert term["unit_rate_gbp_per_mwh"] is None, "Flex terms must not have a locked unit rate"
        assert "flex_markup_per_mwh" in term
        assert term["flex_markup_per_mwh"] == 2.0


def test_run_flex_term_margin_equals_markup_times_consumption():
    """Gross margin per period = flex_markup × consumption_mwh (the key invariant)."""
    from simulation.hedged_settlement import run_flex_term

    markup = 2.0
    spot = 80.0
    date_str = "2020-06-01"
    # Build enough prior records for the 7-day reference window
    from datetime import date, timedelta
    prior_records = []
    for i in range(8):
        d = (date.fromisoformat(date_str) - timedelta(days=8-i)).isoformat()
        for sp in range(1, 49):
            prior_records.append({"settlementDate": d, "settlementPeriod": sp, "systemSellPrice": spot})
    # Add the settlement day itself
    for sp in range(1, 49):
        prior_records.append({"settlementDate": date_str, "settlementPeriod": sp, "systemSellPrice": spot})

    def flat_shape(_date):
        return [1000.0] * 48  # 1 MWh per period

    records = run_flex_term(
        customer_id="T",
        term_start_date=date_str,
        term_end_date="2020-06-02",
        flex_markup_per_mwh=markup,
        consumption_shape=flat_shape,
        system_price_records=prior_records,
        segment="I&C",
    )

    assert len(records) == 48
    for r in records:
        consumption_mwh = r["consumption_kwh"] / 1000.0
        expected_margin = markup * consumption_mwh
        assert abs(r["margin_gbp"] - expected_margin) < 1e-9, (
            f"margin {r['margin_gbp']:.6f} ≠ markup×consumption {expected_margin:.6f}"
        )


def test_run_flex_term_zero_capital_cost():
    """Flex settlement has zero capital cost (no naked forward exposure)."""
    from simulation.hedged_settlement import run_flex_term
    from datetime import date, timedelta

    spot = 60.0
    date_str = "2020-06-01"
    prior = [
        {"settlementDate": (date.fromisoformat(date_str) - timedelta(days=i)).isoformat(),
         "settlementPeriod": sp, "systemSellPrice": spot}
        for i in range(1, 9) for sp in range(1, 49)
    ] + [
        {"settlementDate": date_str, "settlementPeriod": sp, "systemSellPrice": spot}
        for sp in range(1, 49)
    ]

    records = run_flex_term("T", date_str, "2020-06-02", 2.0, lambda _: [100.0] * 48, prior, "I&C")
    assert all(r["capital_cost_gbp"] == 0.0 for r in records)
    assert all(r["hedge_fraction"] == 1.0 for r in records)


def test_run_flex_term_reference_price_is_rolling_average():
    """Flex reference price is a 7-day rolling mean of daily spot (not current spot)."""
    from simulation.hedged_settlement import run_flex_term
    from datetime import date, timedelta

    # Prior 7 days: spot £50, then the settlement day spot spikes to £200
    date_str = "2020-06-08"
    prior_records = []
    for i in range(1, 9):
        d = (date.fromisoformat(date_str) - timedelta(days=i)).isoformat()
        for sp in range(1, 49):
            prior_records.append({"settlementDate": d, "settlementPeriod": sp, "systemSellPrice": 50.0})
    # Settlement day: spot spikes
    for sp in range(1, 49):
        prior_records.append({"settlementDate": date_str, "settlementPeriod": sp, "systemSellPrice": 200.0})

    records = run_flex_term("T", date_str, "2020-06-09", 2.0, lambda _: [1000.0] * 48, prior_records, "I&C")

    # Reference price should be the 7-day prior average (~£50), not the spike £200
    ref_prices = [r["flex_reference_price_gbp_per_mwh"] for r in records]
    assert all(abs(p - 50.0) < 1.0 for p in ref_prices), (
        f"Reference price should be ~50 (7-day prior avg), not {ref_prices[0]:.1f}"
    )


def test_run_flex_term_revenue_equals_ref_plus_markup():
    """Revenue per period = (ref_price + markup) × consumption."""
    from simulation.hedged_settlement import run_flex_term
    from datetime import date, timedelta

    date_str = "2020-06-08"
    spot = 60.0
    prior = [
        {"settlementDate": (date.fromisoformat(date_str) - timedelta(days=i)).isoformat(),
         "settlementPeriod": sp, "systemSellPrice": spot}
        for i in range(1, 9) for sp in range(1, 49)
    ] + [
        {"settlementDate": date_str, "settlementPeriod": sp, "systemSellPrice": spot}
        for sp in range(1, 49)
    ]

    records = run_flex_term("T", date_str, "2020-06-09", 2.0, lambda _: [500.0] * 48, prior, "I&C")

    for r in records:
        mwh = r["consumption_kwh"] / 1000.0
        expected_revenue = (r["flex_reference_price_gbp_per_mwh"] + 2.0) * mwh
        assert abs(r["revenue_gbp"] - expected_revenue) < 1e-9


def test_flex_customer_in_fast_run():
    """Fast-mode sim includes C_IC4 flex settlement records."""
    import os
    os.environ["SIM_FAST_MODE"] = "1"
    try:
        from simulation.run_phase2b import main
        result = main()
    finally:
        del os.environ["SIM_FAST_MODE"]

    all_records = result.get("all_settlement_records", [])
    flex_recs = [r for r in all_records if r.get("customer_id") == "C_IC4"]
    assert len(flex_recs) > 0, "C_IC4 should have flex settlement records"
    assert all(r.get("tariff_type") == "flex" for r in flex_recs)
    assert all(r.get("capital_cost_gbp") == 0.0 for r in flex_recs)
    assert all(r.get("hedge_fraction") == 1.0 for r in flex_recs)
    total_rev = sum(r["revenue_gbp"] for r in flex_recs)
    assert total_rev > 50_000, f"C_IC4 (3GWh flex) revenue should exceed £50k, got £{total_rev:,.0f}"
