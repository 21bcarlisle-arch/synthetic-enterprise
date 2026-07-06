from saas.cost_to_serve import (
    BAD_DEBT_RATE,
    FIXED_OVERHEAD_GBP_PER_PERIOD,
    build_cost_to_serve,
    build_cost_to_serve_ledger_events,
    cost_to_serve_for_period,
)

CUSTOMERS = [
    {"customer_id": "C1", "segment": "resi"},
    {"customer_id": "C5", "segment": "SME"},
]


def _record(customer_id, revenue_gbp, margin_gbp, settlement_date="2020-01-01"):
    return {
        "customer_id": customer_id,
        "revenue_gbp": revenue_gbp,
        "margin_gbp": margin_gbp,
        "settlement_date": settlement_date,
    }


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
