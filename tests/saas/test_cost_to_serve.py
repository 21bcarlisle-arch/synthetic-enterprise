from saas.cost_to_serve import (
    BAD_DEBT_RATE,
    FIXED_OVERHEAD_GBP_PER_PERIOD,
    FIXED_OVERHEAD_GBP_PER_PERIOD_GAS,
    FIXED_OVERHEAD_GBP_PER_YEAR,
    GAS_SETTLEMENT_PERIODS_PER_YEAR,
    SETTLEMENT_PERIODS_PER_YEAR,
    build_cost_to_serve,
    build_cost_to_serve_ledger_events,
    cost_to_serve_for_period,
)

CUSTOMERS = [
    {"customer_id": "C1", "segment": "resi"},
    {"customer_id": "C5", "segment": "SME"},
]


def _record(customer_id, revenue_gbp, margin_gbp, settlement_date="2020-01-01", commodity=None):
    rec = {
        "customer_id": customer_id,
        "revenue_gbp": revenue_gbp,
        "margin_gbp": margin_gbp,
        "settlement_date": settlement_date,
    }
    if commodity is not None:
        rec["commodity"] = commodity
    return rec


def test_cost_to_serve_for_period_resi():
    cost = cost_to_serve_for_period("resi", revenue_gbp=10.0)
    expected = FIXED_OVERHEAD_GBP_PER_PERIOD["resi"]
    assert cost == expected


def test_cost_to_serve_for_period_sme_is_higher_in_absolute_overhead():
    resi_cost = cost_to_serve_for_period("resi", revenue_gbp=0.0)
    sme_cost = cost_to_serve_for_period("SME", revenue_gbp=0.0)
    assert sme_cost > resi_cost


def test_empty_input_returns_zeroed_structures():
    result = build_cost_to_serve([], CUSTOMERS)
    assert result == {
        "portfolio": {
            "cost_to_serve_gbp": 0.0,
            "margin_gbp": 0.0,
            "net_margin_gbp": 0.0,
        },
        "by_customer": {},
    }


def test_aggregates_across_periods_and_customers():
    records = [
        _record("C1", revenue_gbp=10.0, margin_gbp=2.0),
        _record("C1", revenue_gbp=10.0, margin_gbp=2.0),
        _record("C5", revenue_gbp=100.0, margin_gbp=20.0),
    ]

    result = build_cost_to_serve(records, CUSTOMERS)

    c1_cost = 2 * cost_to_serve_for_period("resi", 10.0)
    c5_cost = cost_to_serve_for_period("SME", 100.0)

    assert result["by_customer"]["C1"]["cost_to_serve_gbp"] == c1_cost
    assert result["by_customer"]["C1"]["margin_gbp"] == 4.0
    assert result["by_customer"]["C1"]["net_margin_gbp"] == 4.0 - c1_cost

    assert result["by_customer"]["C5"]["cost_to_serve_gbp"] == c5_cost
    assert result["by_customer"]["C5"]["net_margin_gbp"] == 20.0 - c5_cost

    assert result["portfolio"]["cost_to_serve_gbp"] == c1_cost + c5_cost
    assert result["portfolio"]["margin_gbp"] == 24.0
    assert result["portfolio"]["net_margin_gbp"] == 24.0 - c1_cost - c5_cost


def test_unknown_customer_raises_key_error():
    records = [_record("C99", revenue_gbp=10.0, margin_gbp=2.0)]
    try:
        build_cost_to_serve(records, CUSTOMERS)
        assert False, "expected KeyError"
    except KeyError:
        pass


import pytest
from saas.cost_to_serve import (
    SETTLEMENT_PERIODS_PER_YEAR,
    FIXED_OVERHEAD_GBP_PER_YEAR,
    FIXED_OVERHEAD_GBP_PER_PERIOD,
    BAD_DEBT_RATE,
    get_bad_debt_rate,
    cost_to_serve_for_period,
)


def test_settlement_periods_per_year():
    assert SETTLEMENT_PERIODS_PER_YEAR == 17_520


def test_bad_debt_rate_resi():
    assert BAD_DEBT_RATE["resi"] == pytest.approx(0.02)


def test_bad_debt_rate_sme():
    assert BAD_DEBT_RATE["SME"] == pytest.approx(0.01)


def test_bad_debt_rate_ic():
    assert BAD_DEBT_RATE["I&C"] == pytest.approx(0.005)


def test_fixed_overhead_resi():
    assert FIXED_OVERHEAD_GBP_PER_YEAR["resi"] == pytest.approx(55.0)


def test_get_bad_debt_rate_baseline():
    assert get_bad_debt_rate(2020, "resi") == pytest.approx(0.02)


def test_get_bad_debt_rate_crisis_elevated_sme():
    rate_2022 = get_bad_debt_rate(2022, "SME")
    rate_2020 = get_bad_debt_rate(2020, "SME")
    assert rate_2022 > rate_2020


def test_get_bad_debt_rate_future_falls_back():
    assert get_bad_debt_rate(2030, "resi") == pytest.approx(0.02)


def test_cost_to_serve_zero_revenue_is_overhead_only():
    result = cost_to_serve_for_period("resi", 0.0)
    assert result == pytest.approx(FIXED_OVERHEAD_GBP_PER_PERIOD["resi"])


def test_cost_to_serve_excludes_bad_debt_component():
    """CTS reconciliation fix (NEXT_PHASE.md option B): bad debt is owned
    entirely by the emergent arrears model (ledger account 6001), not
    duplicated here — cost-to-serve is revenue-independent, fixed-overhead
    only."""
    revenue = 100.0
    result = cost_to_serve_for_period("resi", revenue)
    expected_overhead = FIXED_OVERHEAD_GBP_PER_PERIOD["resi"]
    assert result == pytest.approx(expected_overhead)
    assert result == cost_to_serve_for_period("resi", 0.0)


# ---- build_cost_to_serve_ledger_events (CTS reconciliation fix, option B) ----

def test_ledger_events_empty_input():
    assert build_cost_to_serve_ledger_events([], CUSTOMERS) == []


def test_ledger_events_aggregates_by_month():
    records = [
        _record("C1", revenue_gbp=10.0, margin_gbp=2.0, settlement_date="2020-01-01"),
        _record("C1", revenue_gbp=10.0, margin_gbp=2.0, settlement_date="2020-01-15"),
        _record("C1", revenue_gbp=10.0, margin_gbp=2.0, settlement_date="2020-02-01"),
    ]
    events = build_cost_to_serve_ledger_events(records, CUSTOMERS)
    by_month = {e["month"]: e["amount_gbp"] for e in events}
    assert set(by_month) == {"2020-01", "2020-02"}
    per_period = cost_to_serve_for_period("resi", 10.0)
    assert by_month["2020-01"] == pytest.approx(2 * per_period)
    assert by_month["2020-02"] == pytest.approx(per_period)


def test_ledger_events_sorted_by_month():
    records = [
        _record("C1", revenue_gbp=10.0, margin_gbp=2.0, settlement_date="2020-03-01"),
        _record("C1", revenue_gbp=10.0, margin_gbp=2.0, settlement_date="2020-01-01"),
    ]
    events = build_cost_to_serve_ledger_events(records, CUSTOMERS)
    assert [e["month"] for e in events] == ["2020-01", "2020-03"]


def test_ledger_events_totals_match_build_cost_to_serve_portfolio():
    records = [
        _record("C1", revenue_gbp=10.0, margin_gbp=2.0, settlement_date="2020-01-01"),
        _record("C5", revenue_gbp=100.0, margin_gbp=20.0, settlement_date="2020-02-01"),
    ]
    events = build_cost_to_serve_ledger_events(records, CUSTOMERS)
    portfolio = build_cost_to_serve(records, CUSTOMERS)["portfolio"]["cost_to_serve_gbp"]
    assert sum(e["amount_gbp"] for e in events) == pytest.approx(portfolio)


# --- coldwalk:cost_to_serve_cross_fuel_mismatch_same_household (2026-07-12) ---
# Gas settlement is daily (~365 records/yr), electricity is half-hourly
# (~17,520 records/yr) -- the SAME per-period rate applied to both cadences
# recovered only 365/17,520 (~2.1%) of a gas account's intended annual
# overhead, a confirmed 48x real-data gap (C1 elec GBP54.99/yr vs C1g gas
# GBP1.146/yr for the same household).


def test_gas_commodity_uses_gas_cadence_divisor():
    elec_cost = cost_to_serve_for_period("resi", 10.0, commodity="electricity")
    gas_cost = cost_to_serve_for_period("resi", 10.0, commodity="gas")
    assert gas_cost == pytest.approx(FIXED_OVERHEAD_GBP_PER_PERIOD_GAS["resi"])
    assert gas_cost == pytest.approx(elec_cost * (SETTLEMENT_PERIODS_PER_YEAR / GAS_SETTLEMENT_PERIODS_PER_YEAR))


def test_commodity_defaults_to_electricity_for_backward_compatibility():
    assert cost_to_serve_for_period("resi", 10.0) == cost_to_serve_for_period(
        "resi", 10.0, commodity="electricity"
    )


def test_full_year_of_gas_records_recovers_the_full_annual_overhead():
    # One record per gas day for a full year must recover ~the full annual
    # figure -- not the 2.1% the bug produced.
    records = [_record("C1", 10.0, 2.0, settlement_date=f"2020-01-{d:02d}", commodity="gas") for d in range(1, 29)]
    total = sum(cost_to_serve_for_period("resi", 10.0, commodity="gas") for _ in records)
    annual_rate_for_28_days = FIXED_OVERHEAD_GBP_PER_YEAR["resi"] * 28 / GAS_SETTLEMENT_PERIODS_PER_YEAR
    assert total == pytest.approx(annual_rate_for_28_days)


def test_build_cost_to_serve_reads_commodity_from_record():
    records = [
        _record("C1", revenue_gbp=10.0, margin_gbp=2.0, commodity="electricity"),
        _record("C1", revenue_gbp=10.0, margin_gbp=2.0, commodity="gas"),
    ]
    result = build_cost_to_serve(records, CUSTOMERS)
    expected = (
        cost_to_serve_for_period("resi", 10.0, "electricity")
        + cost_to_serve_for_period("resi", 10.0, "gas")
    )
    assert result["by_customer"]["C1"]["cost_to_serve_gbp"] == pytest.approx(expected)


def test_build_cost_to_serve_defaults_to_electricity_when_commodity_absent():
    # Old call sites / fixtures with no "commodity" key must keep behaving
    # exactly as before this fix (electricity cadence).
    records = [_record("C1", revenue_gbp=10.0, margin_gbp=2.0)]  # no commodity key
    result = build_cost_to_serve(records, CUSTOMERS)
    assert result["by_customer"]["C1"]["cost_to_serve_gbp"] == pytest.approx(
        cost_to_serve_for_period("resi", 10.0)
    )
