"""Tests for generate_customers_json and generate_supplier_json (Phase PT)."""
import json
import pathlib
import tempfile

import pytest

PROJECT = pathlib.Path(__file__).resolve().parent.parent.parent


def _minimal_run(tmp_path):
    data = {
        "total_revenue_gbp": 1000.0,
        "total_gross_gbp": 400.0,
        "total_net_gbp": 100.0,
        "total_bad_debt_gbp": 10.0,
        "final_treasury_gbp": 500.0,
        "enterprise_value_gbp": 2000.0,
        "cost_to_serve_portfolio_gbp": 50.0,
        "fra_ratio_series": [],
        "years": {
            "2020": {
                "revenue_gbp": 1000.0,
                "gross_gbp": 400.0,
                "net_gbp": 100.0,
                "bad_debt_gbp": 10.0,
                "treasury_end_gbp": 500.0,
                "active_customer_ids": ["C1", "C1g"],
                "policy_cost_gbp": 50.0,
                "network_cost_gbp": 30.0,
                "segment_split": {},
                "commodity_split": {},
            }
        },
        "per_customer_lifetime": {
            "C1": {
                "commodity": "electricity",
                "segment": "resi",
                "acquisition_date": "2016-01-01",
                "revenue_gbp": 600.0,
                "gross_gbp": 250.0,
                "capital_gbp": 5.0,
                "net_gbp": 70.0,
                "cost_to_serve_gbp": 30.0,
            },
            "C1g": {
                "commodity": "gas",
                "segment": "resi",
                "acquisition_date": "2016-01-01",
                "revenue_gbp": 400.0,
                "gross_gbp": 150.0,
                "capital_gbp": 3.0,
                "net_gbp": 30.0,
                "cost_to_serve_gbp": 20.0,
            },
        },
        "bills": [
            {
                "customer_id": "C1",
                "total_consumption_kwh": 5000.0,
                "average_unit_rate_gbp_per_mwh": 120.0,
                "total_amount_gbp": 600.0,
                "commodity": "electricity",
                "segment": "resi",
            },
            {
                "customer_id": "C1g",
                "total_consumption_kwh": 10000.0,
                "average_unit_rate_gbp_per_mwh": 40.0,
                "total_amount_gbp": 400.0,
                "commodity": "gas",
                "segment": "resi",
            },
        ],
    }
    p = tmp_path / "run.json"
    p.write_text(json.dumps(data))
    return p


def test_customers_json_generated(tmp_path):
    from tools.generate_customers_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "customers.json"
    result = generate(rp, out)
    assert out.exists()
    assert result["customer_count"] == 1


def test_customers_json_dual_fuel_legs(tmp_path):
    from tools.generate_customers_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "customers.json"
    generate(rp, out)
    data = json.loads(out.read_text())
    c = data["customers"][0]
    assert c["customer_group"] == "C1"
    assert "electricity" in c["legs"]
    assert "gas" in c["legs"]
    assert c["fuels"] == ["electricity", "gas"]


def test_customers_json_combined_rollup(tmp_path):
    from tools.generate_customers_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "customers.json"
    generate(rp, out)
    data = json.loads(out.read_text())
    c = data["customers"][0]
    assert abs(c["combined"]["revenue_gbp"] - 1000.0) < 0.1
    assert abs(c["combined"]["gross_gbp"] - 400.0) < 0.1
    assert abs(c["combined"]["net_gbp"] - 100.0) < 0.1


def test_customers_json_kwh_aggregated(tmp_path):
    from tools.generate_customers_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "customers.json"
    generate(rp, out)
    data = json.loads(out.read_text())
    c = data["customers"][0]
    assert c["legs"]["electricity"]["total_kwh"] == 5000.0
    assert c["legs"]["gas"]["total_kwh"] == 10000.0
    assert c["combined"]["total_kwh"] == 15000.0


def test_customers_json_publishes_both_rates_each_named_for_what_it_is(tmp_path):
    """This used to assert one field, `avg_rate_gbp_per_mwh`, at 120.0 and 40.0.

    Those values are the COMMODITY leg -- `average_unit_rate_gbp_per_mwh` off the bill, which
    `saas/bill_generator` computes as `commodity_amount / MWh`. The fixture's own bills say so:
    electricity is 5,000 kWh at a declared 120/MWh while the bill TOTAL is £600, i.e. 120/MWh of
    energy inside £120/MWh... and gas is 10,000 kWh at 40/MWh against a £400 total. The old name
    said neither, and `tools/couple_value_based_pricing` was reading it as the price the customer
    pays -- 1.53x low across the real book. Both rates are published now and both are named.
    """
    from tools.generate_customers_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "customers.json"
    generate(rp, out)
    data = json.loads(out.read_text())
    c = data["customers"][0]
    elec, gas = c["legs"]["electricity"], c["legs"]["gas"]

    assert elec["avg_commodity_rate_gbp_per_mwh"] == 120.0
    assert gas["avg_commodity_rate_gbp_per_mwh"] == 40.0
    # £600 over 5 MWh and £400 over 10 MWh -- the whole bill, over the volume it covered.
    assert elec["avg_effective_rate_gbp_per_mwh"] == 120.0
    assert gas["avg_effective_rate_gbp_per_mwh"] == 40.0
    # Neither fixture bill carries a catch-up, so nothing is excluded and the denominator says so.
    assert elec["effective_rate_bills_excluded"] == 0
    assert gas["effective_rate_bills_excluded"] == 0
    # The ambiguous name must not survive alongside them: two names for one number is the defect.
    assert "avg_rate_gbp_per_mwh" not in elec


def test_a_catchup_bill_is_excluded_from_the_effective_rate_and_the_count_says_so(tmp_path):
    """A catch-up bill's MONEY spans up to thirteen periods and its VOLUME spans one.

    Across the real book, 959 of 11,167 bills carry one and 178 of those have a NEGATIVE GBP/MWh.
    Here the catch-up bill is deliberately absurd -- £2,000 on 1,000 kWh, a reconciliation of a
    year of under-estimates -- so that including it would visibly wreck the rate.
    """
    import json as _json

    from tools.generate_customers_json import generate
    rp = _minimal_run(tmp_path)
    data = _json.loads(rp.read_text())
    data["bills"].append({
        "customer_id": "C1", "total_consumption_kwh": 1000.0,
        "average_unit_rate_gbp_per_mwh": 120.0, "total_amount_gbp": 2000.0,
        "commodity": "electricity", "segment": "resi", "catchup_applied": True,
        "catchup_adjustment_gbp": 1880.0,
    })
    rp.write_text(_json.dumps(data))

    out = tmp_path / "customers.json"
    generate(rp, out)
    elec = _json.loads(out.read_text())["customers"][0]["legs"]["electricity"]

    assert elec["effective_rate_bills_excluded"] == 1
    assert elec["avg_effective_rate_gbp_per_mwh"] == 120.0, (
        "the catch-up bill reached the effective rate: £2,600 over 6 MWh is 433/MWh, and none of "
        "that extra money is for the volume it is being divided by"
    )
    # The commodity leg KEEPS the bill -- `commodity_amount_gbp` is for this period's volume even
    # on a catch-up row, so the two legs exclude differently and each says what it counts.
    assert elec["avg_commodity_rate_gbp_per_mwh"] == 120.0
    # TWO, not three: the fixture's other bill belongs to the GAS leg `C1g`.
    assert elec["bill_count"] == 2


def test_customers_json_has_generated_timestamp(tmp_path):
    from tools.generate_customers_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "customers.json"
    result = generate(rp, out)
    assert "generated" in result
    assert "2026" in result["generated"]


def test_customers_json_single_fuel_no_gas_leg(tmp_path):
    from tools.generate_customers_json import generate
    data = {
        "per_customer_lifetime": {
            "C5": {
                "commodity": "electricity",
                "segment": "SME",
                "acquisition_date": "2018-01-01",
                "revenue_gbp": 500.0,
                "gross_gbp": 200.0,
                "capital_gbp": 2.0,
                "net_gbp": 50.0,
                "cost_to_serve_gbp": 10.0,
            }
        },
        "bills": [],
        "total_revenue_gbp": 500.0,
        "total_gross_gbp": 200.0,
        "total_net_gbp": 50.0,
        "total_bad_debt_gbp": 0.0,
        "final_treasury_gbp": 100.0,
        "enterprise_value_gbp": 500.0,
        "cost_to_serve_portfolio_gbp": 10.0,
        "fra_ratio_series": [],
        "years": {},
    }
    rp = tmp_path / "run.json"
    rp.write_text(json.dumps(data))
    out = tmp_path / "customers.json"
    generate(rp, out)
    result = json.loads(out.read_text())
    c = result["customers"][0]
    assert c["customer_group"] == "C5"
    assert c["fuels"] == ["electricity"]
    assert "gas" not in c["legs"]


def test_supplier_json_generated(tmp_path):
    from tools.generate_supplier_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "supplier.json"
    result = generate(rp, out)
    assert out.exists()
    assert "portfolio_summary" in result


def test_supplier_json_portfolio_summary(tmp_path):
    from tools.generate_supplier_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "supplier.json"
    generate(rp, out)
    data = json.loads(out.read_text())
    ps = data["portfolio_summary"]
    assert ps["total_revenue_gbp"] == 1000.0
    assert ps["total_net_gbp"] == 100.0
    assert ps["enterprise_value_gbp"] == 2000.0


def test_supplier_json_years_summary(tmp_path):
    from tools.generate_supplier_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "supplier.json"
    generate(rp, out)
    data = json.loads(out.read_text())
    assert len(data["years"]) == 1
    yr = data["years"][0]
    assert yr["year"] == 2020
    assert yr["revenue_gbp"] == 1000.0
    assert yr["active_customers"] == 2


def test_supplier_json_simulation_window(tmp_path):
    from tools.generate_supplier_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "supplier.json"
    generate(rp, out)
    data = json.loads(out.read_text())
    assert data["simulation_window"] == "2016-2025"


def test_supplier_json_has_generated_timestamp(tmp_path):
    from tools.generate_supplier_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "supplier.json"
    result = generate(rp, out)
    assert "generated" in result
    assert "Z" in result["generated"]


def test_customers_json_live_run_loads(tmp_path):
    from tools.generate_customers_json import generate
    live_run = PROJECT / "docs" / "reports" / "run_output_latest.json"
    if not live_run.exists():
        pytest.skip("no live run")
    out = tmp_path / "customers.json"
    result = generate(live_run, out)
    assert result["customer_count"] >= 10


def test_supplier_json_live_run_loads(tmp_path):
    from tools.generate_supplier_json import generate
    live_run = PROJECT / "docs" / "reports" / "run_output_latest.json"
    if not live_run.exists():
        pytest.skip("no live run")
    out = tmp_path / "supplier.json"
    result = generate(live_run, out)
    assert len(result["years"]) >= 5
