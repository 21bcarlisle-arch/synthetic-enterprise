"""Phase 61: Flex tariff policy and network pass-through fix.

Bug: run_flex_term() was deducting policy+network from supplier net margin,
making C_IC4 show ~175k annual losses. In a real flex contract, policy and
network costs are passed through to the customer; supplier earns markup only.

Fix: revenue includes policy+network recovery; net = markup x consumption.
"""
from datetime import date, timedelta


def _make_records(spot=80.0, date_str="2022-01-01", markup=2.0, shape=None):
    from simulation.hedged_settlement import run_flex_term
    prior = []
    for i in range(1, 9):
        d = (date.fromisoformat(date_str) - timedelta(days=i)).isoformat()
        for sp in range(1, 49):
            prior.append({"settlementDate": d, "settlementPeriod": sp, "systemSellPrice": spot})
    for sp in range(1, 49):
        prior.append({"settlementDate": date_str, "settlementPeriod": sp, "systemSellPrice": spot})
    consumption = shape or (lambda _: [1000.0] * 48)
    return run_flex_term("C_IC4", date_str, "2022-01-02", markup, consumption, prior, "I&C")


def test_flex_net_margin_equals_markup_only():
    """Net margin = markup x consumption (policy+network do not reduce supplier margin)."""
    markup = 2.0
    records = _make_records(markup=markup)
    for r in records:
        expected = markup * (r["consumption_kwh"] / 1000.0)
        assert abs(r["net_margin_gbp"] - expected) < 1e-6


def test_flex_net_positive_in_high_policy_cost_year():
    """Net margin is positive even in 2022 when policy costs were high."""
    records = _make_records(spot=250.0, date_str="2022-08-15", markup=2.0)
    for r in records:
        assert r["net_margin_gbp"] > 0


def test_flex_revenue_includes_policy_and_network():
    """Revenue = (ref + markup) x consumption + policy_cost + network_cost."""
    records = _make_records(date_str="2022-03-01")
    for r in records:
        mwh = r["consumption_kwh"] / 1000.0
        ref = r["flex_reference_price_gbp_per_mwh"]
        expected = (ref + r["flex_markup_per_mwh"]) * mwh + r["policy_cost_gbp"] + r["network_cost_gbp"]
        assert abs(r["revenue_gbp"] - expected) < 1e-6


def test_flex_policy_cost_does_not_reduce_net():
    """Policy cost is non-zero but cancels in net (recovered from customer in revenue)."""
    records = _make_records(date_str="2021-09-01")
    for r in records:
        assert r["policy_cost_gbp"] > 0
        expected_net = r["flex_markup_per_mwh"] * (r["consumption_kwh"] / 1000.0)
        assert abs(r["net_margin_gbp"] - expected_net) < 1e-6


def test_flex_wholesale_cost_equals_ref_times_consumption():
    """Wholesale cost = ref_price x consumption (supplier hedges at reference)."""
    records = _make_records()
    for r in records:
        expected = r["flex_reference_price_gbp_per_mwh"] * (r["consumption_kwh"] / 1000.0)
        assert abs(r["wholesale_cost_gbp"] - expected) < 1e-6


def test_flex_unit_rate_reflects_full_customer_bill():
    """unit_rate_gbp_per_mwh = revenue / consumption (what customer actually pays)."""
    records = _make_records(date_str="2021-01-15")
    for r in records:
        mwh = r["consumption_kwh"] / 1000.0
        if mwh > 0:
            expected = r["revenue_gbp"] / mwh
            assert abs(r["unit_rate_gbp_per_mwh"] - expected) < 1e-6


def test_flex_margin_equals_net_plus_passthrough():
    """margin_gbp = net_margin + policy_cost + network_cost."""
    records = _make_records(date_str="2022-08-01")
    for r in records:
        expected_margin = r["net_margin_gbp"] + r["policy_cost_gbp"] + r["network_cost_gbp"]
        assert abs(r["margin_gbp"] - expected_margin) < 1e-6


def test_flex_net_stable_across_high_low_policy_years():
    """Net per MWh = markup regardless of policy year (2018 vs 2022)."""
    markup = 2.0
    recs_2018 = _make_records(spot=60.0, date_str="2018-06-01", markup=markup)
    recs_2022 = _make_records(spot=300.0, date_str="2022-07-01", markup=markup)
    for r in recs_2018 + recs_2022:
        expected = markup * (r["consumption_kwh"] / 1000.0)
        assert abs(r["net_margin_gbp"] - expected) < 1e-6
import pytest


def test_flex_commodity_is_electricity():
    records = _make_records()
    assert all(r["commodity"] == "electricity" for r in records)


def test_flex_customer_id_stored():
    from simulation.hedged_settlement import run_flex_term
    from datetime import date, timedelta
    prior = []
    for i in range(1, 9):
        d = (date.fromisoformat("2022-01-01") - timedelta(days=i)).isoformat()
        for sp in range(1, 49):
            prior.append({"settlementDate": d, "settlementPeriod": sp, "systemSellPrice": 80.0})
    for sp in range(1, 49):
        prior.append({"settlementDate": "2022-01-01", "settlementPeriod": sp, "systemSellPrice": 80.0})
    recs = run_flex_term("TESTCUST", "2022-01-01", "2022-01-02", 2.0, lambda _: [1000.0]*48, prior, "I&C")
    assert all(r["customer_id"] == "TESTCUST" for r in recs)


def test_flex_tariff_type_is_flex():
    records = _make_records()
    assert all(r["tariff_type"] == "flex" for r in records)


def test_flex_consumption_kwh_matches_shape():
    records = _make_records()
    for r in records:
        assert r["consumption_kwh"] == pytest.approx(1000.0)


# 13. Flex passthrough gross >= 0 at any spot
def test_flex_passthrough_gross_nonneg():
    from simulation.hedged_settlement import run_flex_term
    from datetime import date, timedelta
    date_str = "2022-10-01"
    prior = [{"settlementDate": (date.fromisoformat(date_str)-timedelta(days=i)).isoformat(),
              "settlementPeriod": sp, "systemSellPrice": 200.0} for i in range(1, 9) for sp in range(1, 49)]
    prior += [{"settlementDate": date_str, "settlementPeriod": sp, "systemSellPrice": 200.0} for sp in range(1, 49)]
    recs = run_flex_term("T", date_str, "2022-10-02", 2.0, lambda _: [100.0]*48, prior, "I&C")
    gross = sum(r["margin_gbp"] for r in recs)
    assert gross >= 0


# 14. Flex markup 2.0 gives deterministic margin
def test_flex_markup_determines_margin():
    from simulation.hedged_settlement import run_flex_term
    from datetime import date, timedelta
    date_str = "2022-01-01"
    prior = [{"settlementDate": (date.fromisoformat(date_str)-timedelta(days=i)).isoformat(),
              "settlementPeriod": sp, "systemSellPrice": 100.0} for i in range(1, 9) for sp in range(1, 49)]
    prior += [{"settlementDate": date_str, "settlementPeriod": sp, "systemSellPrice": 100.0} for sp in range(1, 49)]
    recs = run_flex_term("T", date_str, "2022-01-02", 2.0, lambda _: [50.0]*48, prior, "I&C")
    # Each period: 50 kWh * (1/1000) * 2.0 GBP/MWh = 0.1 GBP gross
    total_gross = sum(r["margin_gbp"] for r in recs)
    assert total_gross > 0


# 15. Flex settlement date stored in record
def test_flex_settlement_date_stored():
    from simulation.hedged_settlement import run_flex_term
    from datetime import date, timedelta
    date_str = "2022-06-01"
    prior = [{"settlementDate": (date.fromisoformat(date_str)-timedelta(days=i)).isoformat(),
              "settlementPeriod": sp, "systemSellPrice": 80.0} for i in range(1, 9) for sp in range(1, 49)]
    prior += [{"settlementDate": date_str, "settlementPeriod": sp, "systemSellPrice": 80.0} for sp in range(1, 49)]
    recs = run_flex_term("T", date_str, "2022-06-02", 2.0, lambda _: [100.0]*48, prior, "I&C")
    assert all(r["settlement_date"] == date_str for r in recs)
