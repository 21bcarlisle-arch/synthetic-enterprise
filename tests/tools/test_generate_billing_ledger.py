"""Tests for generate_billing_ledger.py (Phase PP)."""
import json
import random
from datetime import date, timedelta
from pathlib import Path

import pytest

from tools.generate_billing_ledger import (
    generate, _stress_for_year, _payment_method, _payment_outcome, _arrears_stages,
    _bill_generation_delay_days,
)


def _bill(cid, period_end, amount, segment="ic"):
    ps = (date.fromisoformat(period_end) - timedelta(days=90)).isoformat()
    # VAT computed correctly by segment (5% resi, 20% otherwise) so this
    # fixture passes the Phase 3 pre-bill validation gate -- the other
    # components are reweighted proportionally so they still sum to `amount`.
    vat_rate = 0.05 if segment == "resi" else 0.20
    subtotal = amount / (1 + vat_rate)
    vat_gbp = amount - subtotal
    return {
        "customer_id": cid, "period_start": ps, "period_end": period_end,
        "total_consumption_kwh": 1000.0, "commodity_amount_gbp": subtotal * (0.8 / 0.95),
        "non_commodity_amount_gbp": subtotal * (0.1 / 0.95), "standing_charge_gbp": subtotal * (0.05 / 0.95),
        "days_in_period": 90, "standing_charge_gbp_per_day": (subtotal * (0.05 / 0.95)) / 90,
        "vat_gbp": vat_gbp, "total_amount_gbp": amount,
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


# --- days_in_period / standing_charge_gbp_per_day (2026-07-10, director page
# comment on /customers/: "Days x standing charges... explain the maths
# properly") ---

def test_invoice_exposes_days_in_period_and_daily_standing_charge_rate(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8000.0)])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    assert inv["days_in_period"] == 90
    assert inv["days_in_period"] * inv["standing_charge_gbp_per_day"] == pytest.approx(
        inv["standing_charge_gbp"], abs=0.01
    )


# BILL_CORRECTNESS_ADDENDUM.md Defect 2 (2026-07-09): meter serial,
# MPAN/MPRN, read type, opening/closing reads.

def test_defect2_meter_identity_fields_present(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8000.0)])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    for f in ("meter_serial", "mpan", "mprn", "read_type", "opening_read_kwh", "closing_read_kwh"):
        assert f in inv


def test_defect2_electricity_bill_has_mpan_not_mprn(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8000.0)])))  # commodity="electricity"
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    assert inv["mpan"] is not None
    assert len(inv["mpan"]) == 13
    assert inv["mprn"] is None


def test_defect2_gas_bill_has_mprn_not_mpan(tmp_path):
    bill = _bill("C1g", "2022-03-31", 500.0)
    bill["commodity"] = "gas"
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([bill])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C1g"]["invoices"][0]
    assert inv["mprn"] is not None
    assert len(inv["mprn"]) == 10
    assert inv["mpan"] is None


def test_defect2_mpan_stable_across_bills_for_same_account(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([
        _bill("C_IC1", "2022-03-31", 8000.0),
        _bill("C_IC1", "2022-06-30", 8000.0),
    ])))
    result = generate(rj, tmp_path / "l.json")
    invs = result["customers"]["C_IC1"]["invoices"]
    assert invs[0]["mpan"] == invs[1]["mpan"]
    assert invs[0]["meter_serial"] == invs[1]["meter_serial"]


def test_defect2_defaults_to_actual_read_without_meter_read_log(tmp_path):
    """A run predating Phase 3's meter-read simulation has no
    meter_read_log -- must fall back to "actual" at the bill's own
    consumption, not omit the fields or crash."""
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8000.0)])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    assert inv["read_type"] == "A"
    assert inv["opening_read_kwh"] == 0.0
    assert inv["closing_read_kwh"] == 1000.0  # the bill's total_consumption_kwh


def test_defect2_estimated_read_uses_estimated_consumption(tmp_path):
    bill = _bill("C_IC1", "2022-03-31", 8000.0)
    run_data = _run([bill])
    run_data["meter_read_log"] = [{
        "customer_id": "C_IC1", "period_end": "2022-03-31", "status": "estimated",
        "estimated_consumption_kwh": 850.0, "true_consumption_kwh": 1000.0,
    }]
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(run_data))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    assert inv["read_type"] == "E"
    assert inv["closing_read_kwh"] == 850.0  # estimated, not true, consumption


# D3 step 2 (docs/design/maturity_map.yaml "Estimated billing & catch-up
# rebilling cycle"): the resolving bill's catchup_* fields are carried
# straight through onto the customer-facing invoice, same passthrough
# pattern as read_type above.

def test_d3_catchup_defaults_to_not_applied(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8000.0)])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    assert inv["catchup_applied"] is False
    assert inv.get("catchup_adjustment_gbp") is None


def test_d3_credit_invoice_has_no_fabricated_payment(tmp_path):
    """A catch-up overcharge credit can make total_amount_gbp <= 0 -- no real
    DD/BACS/CHAPS collection applies to a negative amount, so no payment
    event should be recorded for it (found by reading a real instance: a
    credit bill was otherwise rendered with a "successful direct_debit
    payment" of a negative sum)."""
    bill = _bill("C1", "2022-03-31", -2.03, segment="resi")
    bill["catchup_applied"] = True
    bill["catchup_direction"] = "overcharge"
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([bill])))
    result = generate(rj, tmp_path / "l.json")
    cust = result["customers"]["C1"]
    assert cust["invoices"][0]["total_amount_gbp"] == -2.03
    assert cust["payments"] == []
    assert cust["invoices"][0]["payment_status"] == "paid"


def test_d3_catchup_fields_carried_through_to_invoice(tmp_path):
    bill = _bill("C_IC1", "2022-03-31", 8000.0)
    bill.update({
        "catchup_applied": True,
        "catchup_period_start": "2021-04-01",
        "catchup_period_end": "2022-03-31",
        "catchup_periods_covered": 12,
        "catchup_direction": "undercharge",
        "catchup_raw_delta_gbp": 120.0,
        "catchup_adjustment_gbp": 110.0,
        "catchup_written_off_gbp": 10.0,
        "catchup_back_billing_cap_applied": True,
    })
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([bill])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    assert inv["catchup_applied"] is True
    assert inv["catchup_direction"] == "undercharge"
    assert inv["catchup_periods_covered"] == 12
    assert inv["catchup_adjustment_gbp"] == 110.0
    assert inv["catchup_written_off_gbp"] == 10.0
    assert inv["catchup_back_billing_cap_applied"] is True


# BILL_CORRECTNESS_ADDENDUM.md Defect 3 (2026-07-09): register/period-
# structured bill lines (ToU-ready schema, not ToU itself).

def test_defect3_invoice_has_registers_list(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8000.0)])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    assert isinstance(inv["registers"], list)
    assert len(inv["registers"]) == 1


def test_defect3_register_totals_equal_flat_fields(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8000.0)])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    reg = inv["registers"][0]
    assert reg["register_id"] == "1"
    assert reg["label"] == "Anytime"
    assert reg["consumption_kwh"] == inv["consumption_kwh"]
    assert reg["amount_gbp"] == inv["commodity_amount_gbp"]


def test_defect2_opening_read_chains_from_previous_closing_read(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([
        _bill("C_IC1", "2022-03-31", 8000.0),
        _bill("C_IC1", "2022-06-30", 8000.0),
    ])))
    result = generate(rj, tmp_path / "l.json")
    invs = result["customers"]["C_IC1"]["invoices"]
    assert invs[0]["opening_read_kwh"] == 0.0
    assert invs[0]["closing_read_kwh"] == 1000.0
    assert invs[1]["opening_read_kwh"] == invs[0]["closing_read_kwh"]
    assert invs[1]["closing_read_kwh"] == 2000.0


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


# --- ADVISOR_STEER_BILL_ARITHMETIC.md Defect 1: displayed usage derived from
#     the already-rounded printed reads (billed_kwh == closing - opening) ---

def test_defect1_billed_usage_equals_printed_reads_delta(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run([_bill("C_IC1", "2022-03-31", 8000.0)])))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    assert inv["consumption_kwh"] == round(inv["closing_read_kwh"] - inv["opening_read_kwh"], 1)


def test_defect1_holds_by_construction_across_a_multi_bill_chain(tmp_path):
    # Every rendered bill must reconcile, and none should be held for a reads
    # mismatch when the pipeline builds them correctly.
    bills = [_bill("C_IC1", f"20{yr}-03-31", 8000.0) for yr in range(16, 26)]
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills)))
    result = generate(rj, tmp_path / "l.json")
    for inv in result["customers"]["C_IC1"]["invoices"]:
        delta = round(inv["closing_read_kwh"] - inv["opening_read_kwh"], 1)
        assert abs(inv["consumption_kwh"] - delta) <= 0.05
    assert result["meta"]["held_reads_reconciliation_count"] == 0


def test_defect1_estimated_bill_usage_reconciles_with_estimated_reads(tmp_path):
    # An estimated bill's printed usage must equal its printed (estimated)
    # reads' difference -- the previously-visible reads-vs-usage mismatch on
    # estimated bills is removed by the reads-derivation.
    bill = _bill("C_IC1", "2022-03-31", 8000.0)
    run_data = _run([bill])
    run_data["meter_read_log"] = [{
        "customer_id": "C_IC1", "period_end": "2022-03-31", "status": "estimated",
        "estimated_consumption_kwh": 850.0, "true_consumption_kwh": 1000.0,
    }]
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(run_data))
    result = generate(rj, tmp_path / "l.json")
    inv = result["customers"]["C_IC1"]["invoices"][0]
    assert inv["closing_read_kwh"] == 850.0
    assert inv["consumption_kwh"] == 850.0  # == closing - opening, not the true 1000


# --- ADVISOR_STEER_BILL_ARITHMETIC.md Defect 2: written-off invoices are
#     labelled written_off (not left overdue), so they stop double-counting
#     as outstanding against a household ledger that has already zeroed them ---

def _writeoff_scenario_result(tmp_path):
    # A churned high-stress resi account across 2020 (likely to fail a DD and
    # reach WRITTEN_OFF ~2021), plus a much later paying bill so the book's
    # reference date (max issue_date) sits AFTER those write-offs.
    bills = [_bill("C7", f"2020-{m:02d}-28", 220.0, "resi") for m in range(1, 13)]
    bills.append(_bill("C_IC1", "2024-06-30", 8000.0, "ic"))
    beh = {"C7": {"income_stress_trajectory": [{"year": 2020, "stress": "high"}]}}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills, beh=beh, churned=["C7"])))
    return generate(rj, tmp_path / "l.json")


def test_defect2_written_off_invoice_is_labelled_written_off(tmp_path):
    result = _writeoff_scenario_result(tmp_path)
    c7 = result["customers"]["C7"]
    # Deterministic under seed 42: this scenario produces at least one write-off.
    wo_invs = [i for i in c7["invoices"] if i["payment_status"] == "written_off"]
    assert wo_invs, "expected at least one written-off invoice in this scenario"
    # No written-off invoice should be left as 'overdue' (the double-count bug).
    written_off_nums = {a["invoice_number"] for a in c7["arrears_history"]
                        if any(s["stage"] == "WRITTEN_OFF" for s in a["stages"])}
    for inv in c7["invoices"]:
        if inv["invoice_number"] in written_off_nums:
            assert inv["payment_status"] == "written_off"


def test_defect2_point_in_time_writeoff_not_yet_occurred_stays_overdue(tmp_path):
    # A failing bill whose write-off date falls AFTER the book's reference
    # date must NOT be marked written_off -- it hasn't happened yet.
    bills = [_bill("C7", "2020-11-28", 220.0, "resi")]  # only bill -> book date ~2020-12
    beh = {"C7": {"income_stress_trajectory": [{"year": 2020, "stress": "high"}]}}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills, beh=beh, churned=["C7"])))
    result = generate(rj, tmp_path / "l.json")
    c7 = result["customers"]["C7"]
    # Whatever the payment outcome, no invoice can be written_off here because
    # the write-off date (~2021) is after the only issue date (~2020-11).
    assert all(i["payment_status"] != "written_off" for i in c7["invoices"])


def test_stress_label_in_payment(tmp_path):
    bills = [_bill("C7", "2022-10-31", 250.0, "resi")]
    beh = {"C7": {"income_stress_trajectory": [{"year": 2022, "stress": "moderate"}]}}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills, beh=beh)))
    result = generate(rj, tmp_path / "l.json")
    assert result["customers"]["C7"]["payments"][0]["income_stress_at_time"] == "MODERATE"
