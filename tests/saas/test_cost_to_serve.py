from saas.cost_to_serve import (
    BAD_DEBT_RATE,
    FIXED_OVERHEAD_GBP_PER_PERIOD,
    build_cost_to_serve,
    cost_to_serve_for_period,
)

CUSTOMERS = [
    {"customer_id": "C1", "segment": "resi"},
    {"customer_id": "C5", "segment": "SME"},
]


def _record(customer_id, revenue_gbp, margin_gbp):
    return {
        "customer_id": customer_id,
        "revenue_gbp": revenue_gbp,
        "margin_gbp": margin_gbp,
    }


def test_cost_to_serve_for_period_resi():
    cost = cost_to_serve_for_period("resi", revenue_gbp=10.0)
    expected = FIXED_OVERHEAD_GBP_PER_PERIOD["resi"] + BAD_DEBT_RATE["resi"] * 10.0
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
