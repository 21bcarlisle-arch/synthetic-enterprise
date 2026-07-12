import json

from tools.generate_margin_bridge import compute_bridge


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
