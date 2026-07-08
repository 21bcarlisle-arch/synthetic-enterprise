"""Tests for generate_billing_ledger.py (Phase PP)."""
import json
import random
from datetime import date, timedelta
from pathlib import Path

from tools.generate_billing_ledger import (
    generate, _stress_for_year, _payment_method, _payment_outcome, _arrears_stages,
    _bill_generation_delay_days,
)


def _bill(cid, period_end, amount, segment="ic"):
    ps = (date.fromisoformat(period_end) - timedelta(days=90)).isoformat()
    return {
        "customer_id": cid, "period_start": ps, "period_end": period_end,
        "total_consumption_kwh": 1000.0, "commodity_amount_gbp": amount * 0.8,
        "non_commodity_amount_gbp": amount * 0.1, "standing_charge_gbp": amount * 0.05,
        "vat_gbp": amount * 0.05, "total_amount_gbp": amount,
        "average_unit_rate_gbp_per_mwh": amount, "clarity_score": 0.75,
        "bill_shock_pct": None, "segment": segment, "commodity": "electricity",
    }


def _run(bills, beh=None, churned=None):
    return {"bills": bills, "per_customer_behavioral": beh or {}, "churned_billing_accounts": churned or []}


def test_stress_low_default():
    assert _stress_for_year({}, 2020) == "LOW"


def test_stress_reads_trajectory():
    beh = {"income_stress_trajectory": [{"year": 2022, "stress": "high"}]}
    assert _stress_for_year(beh, 2022) == "HIGH"
    assert _stress_for_year(beh, 2020) == "LOW"


def test_stress_none_trajectory():
    assert _stress_for_year({"income_stress_trajectory": None}, 2022) == "LOW"


def test_payment_method_ic_large_chaps():
    assert _payment_method("ic", 15000) == "chaps"


def test_payment_method_ic_small_bacs():
    assert _payment_method("ic", 5000) == "bacs"


def test_payment_method_sme_bacs():
    assert _payment_method("sme", 500) == "bacs"


def test_payment_method_resi_dd():
    assert _payment_method("resi", 120) == "direct_debit"


def test_bacs_always_success():
    outcome, _ = _payment_outcome("bacs", "HIGH", random.Random(1))
    assert outcome == "success"


def test_chaps_always_success():
    outcome, _ = _payment_outcome("chaps", "HIGH", random.Random(1))
    assert outcome == "success"


def test_dd_low_mostly_success():
    rng = random.Random(42)
    results = [_payment_outcome("direct_debit", "LOW", rng)[0] for _ in range(100)]
    assert results.count("success") > 85


def test_dd_high_some_failures():
    rng = random.Random(42)
    results = [_payment_outcome("direct_debit", "HIGH", rng)[0] for _ in range(100)]
    assert results.count("failed") > 20


def test_arrears_resolved():
    stages = _arrears_stages(200.0, date(2022, 11, 15), True)
    names = [s["stage"] for s in stages]
    assert "RESOLVED" in names and "WRITTEN_OFF" not in names


def test_arrears_written_off():
    stages = _arrears_stages(200.0, date(2022, 11, 15), False)
    names = [s["stage"] for s in stages]
    assert "WRITTEN_OFF" in names and "RESOLVED" not in names


def test_arrears_dates_ordered():
    stages = _arrears_stages(200.0, date(2022, 11, 15), True)
    assert [s["date"] for s in stages] == sorted(s["date"] for s in stages)


def test_empty_bills(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([])))
    result = generate(rj, tmp_path / "l.json")
    assert result["meta"]["invoice_count"] == 0


def test_ic_bacs_success(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8500.0, "ic")])))
    result = generate(rj, tmp_path / "l.json")
    cust = result["customers"]["C_IC1"]
    assert cust["invoice_count"] == 1
    assert cust["payments"][0]["method"] == "bacs"
    assert cust["payments"][0]["outcome"] == "success"


def test_required_invoice_fields(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8000.0)])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    for f in ("invoice_number", "customer_id", "period_start", "period_end",
              "total_amount_gbp", "issue_date", "due_date", "payment_status"):
        assert f in inv


def test_due_date_14_days(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8000.0)])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    diff = (date.fromisoformat(inv["due_date"]) - date.fromisoformat(inv["issue_date"])).days
    assert diff == 14


def test_bill_generation_delay_non_negative_and_deterministic():
    d1 = _bill_generation_delay_days("C1", "2022-03-31")
    d2 = _bill_generation_delay_days("C1", "2022-03-31")
    assert d1 == d2
    assert d1 >= 0


def test_bill_generation_delay_varies_by_period():
    delays = {
        _bill_generation_delay_days("C1", f"20{yr}-03-31") for yr in range(16, 26)
    }
    assert len(delays) > 1


def test_issue_date_carries_generation_delay(tmp_path):
    # Phase 3 item 3: issue_date is no longer always == period_end.
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8000.0)])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    expected_delay = _bill_generation_delay_days("C_IC1", "2022-03-31")
    expected_issue = (date.fromisoformat("2022-03-31") + timedelta(days=expected_delay)).isoformat()
    assert inv["issue_date"] == expected_issue
    assert inv["generation_delay_days"] == expected_delay
    assert date.fromisoformat(inv["issue_date"]) >= date.fromisoformat("2022-03-31")


def test_multiple_customers(tmp_path):
    bills = [_bill("C_IC1", "2022-03-31", 8000.0, "ic"), _bill("C1", "2022-03-31", 150.0, "resi")]
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills)))
    result = generate(rj, tmp_path / "l.json")
    assert result["meta"]["customer_count"] == 2


def test_output_file_written(tmp_path):
    bills = [_bill("C_IC1", "2022-03-31", 5000.0), _bill("C_IC1", "2022-06-30", 4800.0)]
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills)))
    out = tmp_path / "l.json"
    generate(rj, out)
    assert out.exists()
    assert json.loads(out.read_text())["meta"]["invoice_count"] == 2


def test_ic_balance_zero(tmp_path):
    bills = [_bill("C_IC1", "2022-03-31", 8000.0), _bill("C_IC1", "2022-06-30", 7500.0)]
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills)))
    result = generate(rj, tmp_path / "l.json")
    cust = result["customers"]["C_IC1"]
    assert abs(cust["total_billed_gbp"] - 15500.0) < 0.01
    assert cust["balance_gbp"] == 0.0


def test_churned_arrears_written_off(tmp_path):
    bills = [_bill("C7", "2022-10-31", 250.0, "resi")]
    beh = {"C7": {"income_stress_trajectory": [{"year": 2022, "stress": "high"}]}}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills, beh=beh, churned=["C7"])))
    result = generate(rj, tmp_path / "l.json")
    cust = result["customers"]["C7"]
    if cust["arrears_case_count"] > 0:
        assert cust["arrears_history"][0]["stages"][-1]["stage"] == "WRITTEN_OFF"


def test_stress_label_in_payment(tmp_path):
    bills = [_bill("C7", "2022-10-31", 250.0, "resi")]
    beh = {"C7": {"income_stress_trajectory": [{"year": 2022, "stress": "moderate"}]}}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills, beh=beh)))
    result = generate(rj, tmp_path / "l.json")
    assert result["customers"]["C7"]["payments"][0]["income_stress_at_time"] == "MODERATE"
