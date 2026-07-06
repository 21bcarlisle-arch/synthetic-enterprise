"""Tests for tools/generate_invoice_data.py -- real per-invoice bill-equation
data sourced from site/state/billing_ledger.json (Phase RJ: replaces the
previous fabricated seasonal-weight invoice approximation)."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.generate_invoice_data import _real_invoice, real_invoices_for


_LEDGER_INV = dict(
    invoice_number=7,
    customer_id="C1",
    period_start="2016-01-01",
    period_end="2016-01-31",
    commodity="electricity",
    consumption_kwh=471.1,
    commodity_amount_gbp=62.69,
    non_commodity_amount_gbp=24.5,
    standing_charge_gbp=8.37,
    vat_gbp=4.78,
    total_amount_gbp=100.34,
    payment_status="paid",
)


def test_real_invoice_maps_core_fields():
    out = _real_invoice(_LEDGER_INV)
    assert out["id"] == "C1-INV7"
    assert out["date"] == "2016-01-31"
    assert out["commodity"] == "electricity"
    assert out["consumption_kwh"] == 471.1
    assert out["amount_gbp"] == 100.34


def test_real_invoice_derives_unit_rate_from_real_usage_and_charge():
    out = _real_invoice(_LEDGER_INV)
    expected = round(62.69 / 471.1 * 100, 2)
    assert out["unit_rate_p_per_kwh"] == expected


def test_real_invoice_unit_rate_none_when_no_consumption():
    inv = dict(_LEDGER_INV, consumption_kwh=0)
    out = _real_invoice(inv)
    assert out["unit_rate_p_per_kwh"] is None


def test_real_invoice_status_paid_maps_to_upper():
    out = _real_invoice(_LEDGER_INV)
    assert out["status"] == "PAID"


def test_real_invoice_status_overdue_maps_to_unpaid():
    inv = dict(_LEDGER_INV, payment_status="overdue")
    out = _real_invoice(inv)
    assert out["status"] == "UNPAID"


def test_real_invoice_status_disputed_maps_to_disputed():
    inv = dict(_LEDGER_INV, payment_status="disputed")
    out = _real_invoice(inv)
    assert out["status"] == "DISPUTED"


def test_real_invoice_carries_bill_equation_components():
    out = _real_invoice(_LEDGER_INV)
    assert out["commodity_amount_gbp"] == 62.69
    assert out["standing_charge_gbp"] == 8.37
    assert out["non_commodity_amount_gbp"] == 24.5
    assert out["vat_gbp"] == 4.78


def test_real_invoices_for_unknown_customer_returns_empty():
    assert real_invoices_for("C999", dict()) == []


def test_real_invoices_for_maps_all_invoices_in_order():
    ledger_customers = dict(C1=dict(invoices=[_LEDGER_INV, dict(_LEDGER_INV, invoice_number=8)]))
    out = real_invoices_for("C1", ledger_customers)
    assert len(out) == 2
    assert out[0]["id"] == "C1-INV7"
    assert out[1]["id"] == "C1-INV8"


def test_generate_end_to_end_uses_real_ledger_data(tmp_path, monkeypatch):
    import tools.generate_invoice_data as gid

    cust_dir = tmp_path / "customers"
    cust_dir.mkdir()
    (cust_dir / "C1.json").write_text(json.dumps(dict(account_id="C1", invoices=[])))

    ledger_path = tmp_path / "billing_ledger.json"
    ledger_path.write_text(json.dumps(dict(customers=dict(C1=dict(invoices=[_LEDGER_INV])))))

    run_json = tmp_path / "run.json"
    run_json.write_text(json.dumps(dict(per_customer_lifetime=dict(C1=dict()))))

    monkeypatch.setattr(gid, "CUSTOMERS_DIR", cust_dir)
    monkeypatch.setattr(gid, "LEDGER_PATH", ledger_path)

    count = gid.generate(str(run_json))
    assert count == 1
    updated = json.loads((cust_dir / "C1.json").read_text())
    assert len(updated["invoices"]) == 1
    assert updated["invoices"][0]["amount_gbp"] == 100.34
    assert updated["invoices"][0]["unit_rate_p_per_kwh"] is not None


def test_generate_returns_zero_when_ledger_missing(tmp_path, monkeypatch):
    import tools.generate_invoice_data as gid

    run_json = tmp_path / "run.json"
    run_json.write_text(json.dumps(dict(per_customer_lifetime=dict())))
    monkeypatch.setattr(gid, "LEDGER_PATH", tmp_path / "no_such_ledger.json")

    assert gid.generate(str(run_json)) == 0
