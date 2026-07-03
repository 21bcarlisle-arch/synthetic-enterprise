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


def test_customers_json_avg_rate(tmp_path):
    from tools.generate_customers_json import generate
    rp = _minimal_run(tmp_path)
    out = tmp_path / "customers.json"
    generate(rp, out)
    data = json.loads(out.read_text())
    c = data["customers"][0]
    assert c["legs"]["electricity"]["avg_rate_gbp_per_mwh"] == 120.0
    assert c["legs"]["gas"]["avg_rate_gbp_per_mwh"] == 40.0


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
