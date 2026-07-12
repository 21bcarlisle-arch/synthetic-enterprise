"""Tests for company/billing/pre_bill_validation.py -- DOMAIN_SENSE_AND_COMPLIANCE.md Phase 3."""
from company.billing.pre_bill_validation import (
    validate_bill,
    validate_bills,
    exception_queue_as_dicts,
    ValidationOutcome,
    check_reads_reconcile,
    validate_rendered_bill_reads,
)


def _good_resi_bill(**overrides):
    """A correct monthly resi electricity bill (~300 kWh/month, 5% VAT)."""
    bill = {
        "customer_id": "C1",
        "period_start": "2024-01-01",
        "period_end": "2024-01-31",
        "segment": "resi",
        "commodity": "electricity",
        "total_consumption_kwh": 300.0,
        "commodity_amount_gbp": 44.55,
        "non_commodity_amount_gbp": 16.65,
        "standing_charge_gbp": 9.30,
        "vat_gbp": 3.53,  # 5% of 70.50
    }
    bill.update(overrides)
    return bill


def test_correct_resi_bill_passes():
    result = validate_bill(_good_resi_bill())
    assert result.outcome == ValidationOutcome.PASS
    assert result.reasons == []
    assert result.held is False


def test_wrong_vat_rate_is_held():
    # 20% VAT applied to a resi account -- the R10 C6-defect class.
    bill = _good_resi_bill(vat_gbp=14.10)  # 20% of 70.50
    result = validate_bill(bill)
    assert result.held is True
    assert any("vat_by_segment" in r for r in result.reasons)


def test_sme_billed_at_5_percent_vat_is_held():
    bill = _good_resi_bill(segment="SME", vat_gbp=3.53)  # 5% instead of 20%
    result = validate_bill(bill)
    assert result.held is True
    assert any("vat_by_segment" in r for r in result.reasons)


def test_sme_correct_vat_passes():
    bill = _good_resi_bill(segment="SME", vat_gbp=14.10)  # 20% of 70.50
    result = validate_bill(bill)
    assert result.outcome == ValidationOutcome.PASS


def test_gross_implausible_resi_consumption_is_held():
    # Grossly implausible for any domestic account.
    bill = _good_resi_bill(total_consumption_kwh=5000.0)
    result = validate_bill(bill)
    assert result.held is True
    assert any("slc_6_7_billing_accuracy" in r for r in result.reasons)


def test_c6_real_sme_consumption_on_a_resi_account_is_held():
    # The actual R10 defect class, real figure: C6's genuine SME monthly
    # consumption is 2,346.8 kWh (BILL_CORRECTNESS_ADDENDUM.md) -- if an
    # SME account were ever mislabeled resi again, its real consumption
    # must still trip this check even though it's well below an obviously
    # absurd value.
    bill = _good_resi_bill(total_consumption_kwh=2346.8)
    result = validate_bill(bill)
    assert result.held is True
    assert any("slc_6_7_billing_accuracy" in r for r in result.reasons)


def test_real_resi_population_max_still_passes():
    # The real observed resi max in this sim's verified-correct population
    # (1,945 kWh/month) must never be flagged -- proves the bound sits
    # above genuine variation, not just below the SME-defect figure.
    bill = _good_resi_bill(total_consumption_kwh=1945.0)
    result = validate_bill(bill)
    assert not any("slc_6_7_billing_accuracy" in r for r in result.reasons)


def test_plausible_resi_consumption_passes():
    # A real domestic winter month, on the high side but plausible.
    bill = _good_resi_bill(total_consumption_kwh=450.0)
    result = validate_bill(bill)
    assert result.outcome == ValidationOutcome.PASS


def test_consumption_check_is_annualised_not_flat_monthly():
    # A short billing period (10 days) with proportionally low kWh must not
    # be flagged just because the raw monthly-style number looks small --
    # the check should annualise using the period length.
    bill = _good_resi_bill(period_start="2024-01-01", period_end="2024-01-10", total_consumption_kwh=100.0)
    result = validate_bill(bill)
    assert result.outcome == ValidationOutcome.PASS


def test_consumption_check_only_applies_to_resi():
    # An SME or I&C account isn't checked against the resi plausibility
    # envelope -- a large SME consumption figure is normal, not an anomaly.
    bill = _good_resi_bill(segment="SME", total_consumption_kwh=45000.0, vat_gbp=0.2 * (44.55 + 16.65 + 9.30 + (44.55 * (45000 / 300 - 1))))
    # Simplify: just check it's not held for the consumption reason.
    bill["commodity_amount_gbp"] = 4455.0
    bill["vat_gbp"] = 0.20 * (4455.0 + 16.65 + 9.30)
    result = validate_bill(bill)
    assert not any("slc_6_7_billing_accuracy" in r for r in result.reasons)


def test_a_bill_can_fail_multiple_checks_at_once():
    bill = _good_resi_bill(total_consumption_kwh=5000.0, vat_gbp=14.10)
    result = validate_bill(bill)
    assert result.held is True
    assert len(result.reasons) == 2


def test_validate_bills_partitions_pass_and_held():
    bills = [
        _good_resi_bill(customer_id="C1", period_end="2024-01-31"),
        _good_resi_bill(customer_id="C2", period_end="2024-01-31", vat_gbp=14.10),
    ]
    passing, exceptions = validate_bills(bills)
    assert len(passing) == 1
    assert passing[0]["customer_id"] == "C1"
    assert len(exceptions) == 1
    assert exceptions[0].customer_id == "C2"


def test_exception_queue_as_dicts_is_json_serialisable():
    import json
    bill = _good_resi_bill(vat_gbp=14.10)
    _, exceptions = validate_bills([bill])
    payload = exception_queue_as_dicts(exceptions)
    json.dumps(payload)  # must not raise
    assert payload[0]["customer_id"] == "C1"
    assert "reasons" in payload[0]


# --- ADVISOR_STEER_BILL_ARITHMETIC.md Defect 1: reads-vs-usage reconciliation ---

def test_reads_reconcile_exact_match_passes():
    # The director's actual figures: 21084.0 -> 21415.1 = 331.1 kWh.
    assert check_reads_reconcile(21084.0, 21415.1, 331.1) is True
    assert validate_rendered_bill_reads(
        {"opening_read_kwh": 21084.0, "closing_read_kwh": 21415.1, "consumption_kwh": 331.1}
    ) == []


def test_reads_vs_usage_compounding_rounding_mismatch_is_caught():
    # The exact defect the director saw: reads say 331.1 but the usage line
    # says 331.2 -- a bill that would NOT reconcile must be flagged.
    assert check_reads_reconcile(21084.0, 21415.1, 331.2) is False
    reasons = validate_rendered_bill_reads(
        {"opening_read_kwh": 21084.0, "closing_read_kwh": 21415.1, "consumption_kwh": 331.2}
    )
    assert reasons != []
    assert any("slc_6_7_billing_accuracy" in r for r in reasons)
    assert any("does not reconcile" in r for r in reasons)


def test_reads_reconcile_large_mismatch_is_caught():
    # A provenance defect (usage sourced separately from the reads) -- a big
    # divergence, not just a rounding edge, must also be held.
    assert check_reads_reconcile(1000.0, 1400.0, 350.0) is False
    assert validate_rendered_bill_reads(
        {"opening_read_kwh": 1000.0, "closing_read_kwh": 1400.0, "consumption_kwh": 350.0}
    ) != []


def test_reads_reconcile_not_applicable_when_reads_absent():
    # A bill with no meter reads (older run data) is not failed by this check.
    assert check_reads_reconcile(None, None, 300.0) is True
    assert validate_rendered_bill_reads(
        {"opening_read_kwh": None, "closing_read_kwh": None, "consumption_kwh": 300.0}
    ) == []


def test_synthetic_violating_bill_reaches_the_exception_queue():
    # End-to-end: a deliberately mismatched rendered bill must produce a
    # HELD result serialisable onto the exception queue (the R10 class gate),
    # not silently render.
    import json
    from company.billing.pre_bill_validation import BillValidationResult, ValidationOutcome as VO
    bad = {"opening_read_kwh": 5000.0, "closing_read_kwh": 5500.0, "consumption_kwh": 480.0}
    reasons = validate_rendered_bill_reads(bad)
    assert reasons, "a mismatched bill must be flagged"
    held = BillValidationResult(
        customer_id="C1", period_end="2020-07-31", outcome=VO.HELD, reasons=reasons,
    )
    assert held.held is True
    payload = exception_queue_as_dicts([held])
    json.dumps(payload)  # must not raise
    assert payload[0]["customer_id"] == "C1"
    assert any("does not reconcile" in r for r in payload[0]["reasons"])


# --- ADVISOR_STEER_BACKBILLING_GATE.md item 1(c): pre-bill back-billing cap gate ---


def test_uncapped_catchup_bill_still_passes_normally():
    bill = _good_resi_bill(
        catchup_applied=True, catchup_direction="undercharge",
        catchup_period_start="2024-01-01",
    )
    result = validate_bill(bill)
    assert not any("slc_21ba_back_billing_cap" in r for r in result.reasons)


def test_breach_silently_charged_in_full_is_held():
    # A catch-up bill whose consumption pre-dates the 12-month window but
    # was NOT written off -- the exact live gap this steer was staged to
    # catch; the pre-bill gate must HOLD it rather than let it issue.
    bill = _good_resi_bill(
        period_end="2024-01-31",
        catchup_applied=True, catchup_direction="undercharge",
        catchup_period_start="2022-06-01",
        catchup_written_off_gbp=0.0, catchup_raw_delta_gbp=300.0,
        catchup_adjustment_gbp=300.0,
    )
    result = validate_bill(bill)
    assert result.held is True
    assert any("slc_21ba_back_billing_cap" in r for r in result.reasons)


def test_breach_genuinely_written_off_passes():
    bill = _good_resi_bill(
        period_end="2024-01-31",
        catchup_applied=True, catchup_direction="undercharge",
        catchup_period_start="2022-06-01",
        catchup_written_off_gbp=100.0, catchup_raw_delta_gbp=300.0,
        catchup_adjustment_gbp=200.0,
    )
    result = validate_bill(bill)
    assert not any("slc_21ba_back_billing_cap" in r for r in result.reasons)


def test_zero_subtotal_bill_does_not_crash_vat_check():
    bill = _good_resi_bill(
        commodity_amount_gbp=0.0, non_commodity_amount_gbp=0.0,
        standing_charge_gbp=0.0, vat_gbp=0.0,
    )
    result = validate_bill(bill)
    # No VAT reason possible with a zero subtotal (nothing to rate-check);
    # consumption reason still applies independently.
    assert not any("vat_by_segment" in r for r in result.reasons)
