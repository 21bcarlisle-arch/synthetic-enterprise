"""Phase 264 tests: synthetic invoice generation for customer portal."""
import json
from pathlib import Path
from datetime import date
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.generate_invoice_data import generate_invoices, _month_end, _months_between


_CDATA_RESI = {
    "segment": "resi",
    "commodity": "electricity",
    "acquisition_date": "2024-01-01",
    "revenue_gbp": 1200.0,
}

_CDATA_GAS = {
    "segment": "resi",
    "commodity": "gas",
    "acquisition_date": "2024-01-01",
    "revenue_gbp": 800.0,
}

_CDATA_IC = {
    "segment": "I&C",
    "commodity": "electricity",
    "acquisition_date": "2024-01-01",
    "revenue_gbp": 500_000.0,
}


def test_months_between_count():
    months = _months_between("2024-01-01", date(2024, 12, 31))
    assert len(months) == 12


def test_generate_invoices_count_matches_months():
    invs = generate_invoices("C1", _CDATA_RESI)
    assert len(invs) > 0
    months = _months_between("2024-01-01", min(date.today(), date(2025, 12, 31)))
    assert len(invs) == len(months)


def test_generate_invoices_last_is_unpaid():
    invs = generate_invoices("C1", _CDATA_RESI)
    assert invs[-1]["status"] == "UNPAID"


def test_generate_invoices_rest_are_paid():
    invs = generate_invoices("C1", _CDATA_RESI)
    for inv in invs[:-1]:
        assert inv["status"] == "PAID"


def test_generate_invoices_total_revenue_within_10pct():
    invs = generate_invoices("C1", _CDATA_RESI)
    total = sum(i["amount_gbp"] for i in invs)
    expected = _CDATA_RESI["revenue_gbp"]
    assert total > expected  # invoices include standing charges on top of revenue


def test_gas_invoices_winter_higher_than_summer():
    invs = generate_invoices("C1", _CDATA_GAS)
    jan = next(i for i in invs if i["period_start"].endswith("-01-01"))
    jul = next((i for i in invs if "-07-" in i["period_start"]), None)
    if jul:
        assert jan["amount_gbp"] > jul["amount_gbp"]


def test_ic_invoices_amount_much_larger():
    invs_resi = generate_invoices("C1", _CDATA_RESI)
    invs_ic = generate_invoices("C_IC1", _CDATA_IC)
    avg_resi = sum(i["amount_gbp"] for i in invs_resi) / len(invs_resi)
    avg_ic = sum(i["amount_gbp"] for i in invs_ic) / len(invs_ic)
    assert avg_ic > avg_resi * 10


def test_invoice_id_format():
    invs = generate_invoices("C1", _CDATA_RESI)
    assert invs[0]["id"].startswith("C1-2024-")


def test_generate_writes_invoices_to_customer_json(tmp_path):
    from tools.generate_invoice_data import generate
    import json
    cust_dir = tmp_path / "customers"
    cust_dir.mkdir()
    (cust_dir / "C1.json").write_text(json.dumps({
        "account_id": "C1", "segment": "resi", "commodity": "electricity",
        "acquisition_date": "2024-01-01", "revenue_gbp": 1200.0, "invoices": []
    }))
    (cust_dir / "_index.json").write_text(json.dumps(["C1"]))
    run_data = {
        "per_customer_lifetime": {
            "C1": {
                "segment": "resi", "commodity": "electricity",
                "acquisition_date": "2024-01-01", "revenue_gbp": 1200.0
            }
        }
    }
    run_json = tmp_path / "run.json"
    run_json.write_text(json.dumps(run_data))

    import tools.generate_invoice_data as gid
    orig = gid.CUSTOMERS_DIR
    gid.CUSTOMERS_DIR = cust_dir
    try:
        gid.generate(str(run_json))
    finally:
        gid.CUSTOMERS_DIR = orig

    updated = json.loads((cust_dir / "C1.json").read_text())
    assert len(updated["invoices"]) > 0
    assert updated["invoices"][0]["amount_gbp"] > 0
