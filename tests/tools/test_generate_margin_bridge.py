import json

from tools.generate_margin_bridge import compute_bridge, compute_one_bill_worked_example


def _bill(customer_id="C1", commodity_amount=50.0, non_commodity_amount=20.0,
          standing_charge=8.0, vat=3.9, total=None, segment="resi",
          catchup_adjustment=0.0):
    if total is None:
        total = commodity_amount + non_commodity_amount + standing_charge + vat + catchup_adjustment
    bill = {
        "customer_id": customer_id,
        "period_start": "2020-07-01",
        "period_end": "2020-07-31",
        "total_consumption_kwh": 350.0,
        "commodity_amount_gbp": commodity_amount,
        "non_commodity_amount_gbp": non_commodity_amount,
        "standing_charge_gbp": standing_charge,
        "vat_gbp": vat,
        "total_amount_gbp": total,
        "segment": segment,
        "commodity": "electricity",
        "billing_basis": "actual",
    }
    if catchup_adjustment:
        bill["catchup_adjustment_gbp"] = catchup_adjustment
    return bill


def _base_data(**overrides):
    data = {
        "total_revenue_gbp": 1000.0,
        "total_gross_gbp": 400.0,
        "total_capital_gbp": 10.0,
        "total_net_gbp": 90.0,
        "ledger_pnl": {
            "net_margin_gbp": 350.0,
            "wholesale_cost_gbp": 600.0,
            "gross_margin_gbp": 360.0,
            "non_commodity_cost_gbp": 200.0,
        },
        "bills": [_bill()],
    }
    data.update(overrides)
    return data


def test_bridge_fully_reconciles_with_no_unexplained_remainder():
    data = _base_data()
    bridge = compute_bridge(data)
    assert abs(bridge["unexplained_remainder_gbp"]) <= 1.0
    assert bridge["fully_explained"] is True


def test_gap_equals_ledger_minus_settlement():
    data = _base_data()
    bridge = compute_bridge(data)
    assert bridge["total_gap_gbp"] == round(
        data["ledger_pnl"]["net_margin_gbp"] - data["total_net_gbp"], 2
    )


def test_dominant_item_is_settlement_policy_network_cost():
    data = _base_data()
    bridge = compute_bridge(data)
    dominant = bridge["items"][0]
    settlement_policy_network = (
        data["total_gross_gbp"] - data["total_capital_gbp"] - data["total_net_gbp"]
    )
    assert dominant["id"] == "noncommodity_cost_no_revenue_recognition"
    assert abs(dominant["amount_gbp"] - settlement_policy_network) < 0.01


def test_held_bills_excluded_from_bridge_population():
    # A bill guaranteed to be HELD by pre_bill_validation (20% VAT on a resi
    # bill is the known trigger elsewhere in this test suite) must not be
    # counted in the comm+sc revenue-basis item.
    passing_bill = _bill(customer_id="C1")
    held_bill = _bill(customer_id="C2", commodity_amount=100.0, vat=20.0, segment="resi")
    data = _base_data(bills=[passing_bill, held_bill])
    bridge = compute_bridge(data)
    assert bridge["held_bills_excluded_from_ledger"] >= 1


def test_catchup_adjustment_residual_matches_confirmed_mechanism():
    # comm+sc = 50+8=58; wholesale=600 => implied_gross_from_components=-542.
    # Set ledger gross_margin_gbp so that (gross - implied) isolates exactly
    # the 41.0 catchup adjustment as the residual item.
    bill_with_catchup = _bill(customer_id="C3", catchup_adjustment=41.0)
    data = _base_data(
        bills=[bill_with_catchup],
        ledger_pnl={
            "net_margin_gbp": 350.0,
            "wholesale_cost_gbp": 600.0,
            "gross_margin_gbp": -501.0,
            "non_commodity_cost_gbp": 200.0,
        },
    )
    bridge = compute_bridge(data)
    residual_item = next(i for i in bridge["items"] if i["id"] == "residual")
    assert abs(residual_item["amount_gbp"] - 41.0) < 0.01
    assert residual_item["status"] == "explained"


def test_bridge_json_is_serializable():
    data = _base_data()
    bridge = compute_bridge(data)
    json.dumps(bridge)  # must not raise


# D2_three_clocks (2026-07-12, ADVISOR_STEER_TWIN_READONLY.md): the one-bill
# worked example the lane charter's L2 bar requires. bill()'s default period
# is 2020-07-01..2020-07-31, matching "2020-07" below.

def _settlement_month(revenue=50.0, wholesale=20.0, capital=1.0, net=5.0, consumption=350.0):
    return {
        "revenue_gbp": revenue, "wholesale_cost_gbp": wholesale,
        "gross_gbp": revenue - wholesale, "capital_gbp": capital, "net_gbp": net,
        "consumption_kwh": consumption,
    }


def test_one_bill_worked_example_none_when_no_years_data():
    data = _base_data()  # no "years" key at all -- older cached run predating this export
    assert compute_one_bill_worked_example(data) is None


def test_one_bill_worked_example_none_when_month_not_in_settlement_data():
    data = _base_data(years={"2020": {"per_customer_monthly": {"C1": {"2020-01": _settlement_month()}}}})
    assert compute_one_bill_worked_example(data) is None  # bill is 2020-07, only 2020-01 present


def test_one_bill_worked_example_computes_all_three_clocks():
    # _bill() defaults: commodity=50, standing_charge=8, vat=3.9 (unchanged) +
    # non_commodity=20 (explicit) -> total = 50+20+8+3.9 = 81.9.
    bill = _bill(customer_id="C1", non_commodity_amount=20.0)
    data = _base_data(
        bills=[bill],
        years={"2020": {"per_customer_monthly": {
            "C1": {"2020-07": _settlement_month(revenue=50.0, wholesale=20.0, capital=1.0, net=5.0, consumption=350.0)}
        }}},
    )
    example = compute_one_bill_worked_example(data, customer_id="C1")
    assert example is not None
    assert example["customer_id"] == "C1"
    assert example["physical_clock"]["consumption_kwh"] == 350.0
    assert example["financial_clock"]["total_amount_gbp"] == 81.9
    # ledger_net_margin = 81.9 (total) - 20 (non-commodity offset) - 20 (wholesale) - 1 (capital) = 40.9
    assert example["financial_clock"]["ledger_net_margin_gbp"] == 40.9
    assert example["regulatory_clock"]["net_margin_gbp"] == 5.0
    # gap = financial (40.9) - regulatory (5.0) = 35.9
    assert example["gap_gbp"] == 35.9
    assert "policy/network cost recovery" in example["gap_explanation"]


def test_one_bill_worked_example_agrees_within_tolerance_has_no_material_gap_language():
    bill = _bill(customer_id="C1", non_commodity_amount=20.0)
    data = _base_data(
        bills=[bill],
        years={"2020": {"per_customer_monthly": {
            "C1": {"2020-07": _settlement_month(revenue=50.0, wholesale=20.0, capital=1.0, net=40.9, consumption=350.0)}
        }}},
    )
    example = compute_one_bill_worked_example(data, customer_id="C1")
    assert abs(example["gap_gbp"]) <= 1.0
    assert "agree to within a rounding penny" in example["gap_explanation"]


def test_one_bill_worked_example_tries_preferred_customers_in_order():
    """No explicit customer_id -> tries PREFERRED_WORKED_EXAMPLE_CUSTOMERS in
    order, picking the first with real matching data (C1 has none here)."""
    bill_c2 = _bill(customer_id="C2")
    data = _base_data(
        bills=[bill_c2],
        years={"2020": {"per_customer_monthly": {
            "C2": {"2020-07": _settlement_month(net=3.0)}
        }}},
    )
    example = compute_one_bill_worked_example(data)
    assert example["customer_id"] == "C2"


def test_one_bill_worked_example_is_json_serializable():
    bill = _bill(customer_id="C1")
    data = _base_data(
        bills=[bill],
        years={"2020": {"per_customer_monthly": {"C1": {"2020-07": _settlement_month()}}}},
    )
    example = compute_one_bill_worked_example(data, customer_id="C1")
    json.dumps(example)  # must not raise
