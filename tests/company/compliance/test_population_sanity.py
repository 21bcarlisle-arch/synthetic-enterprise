"""Tests for company/compliance/population_sanity.py -- DOMAIN_SENSE_AND_COMPLIANCE.md Phase 5."""
from company.compliance.population_sanity import (
    check_consumption_distribution,
    check_unit_rate_bands,
    check_estimated_read_rate,
    check_payment_channel_mix,
    run_all_population_checks,
)


def _bill(cid, period_end, kwh, gbp_per_mwh, segment="resi", commodity="electricity"):
    return {
        "customer_id": cid, "period_end": period_end, "segment": segment, "commodity": commodity,
        "total_consumption_kwh": kwh, "commodity_amount_gbp": kwh / 1000 * gbp_per_mwh,
    }


def test_consumption_distribution_clean_population_no_findings():
    # 12 months at ~200 kWh/month elec -> 2,400 kWh/yr, plausible.
    bills = [_bill("C1", f"2024-{m:02d}-28", 200.0, 150.0) for m in range(1, 13)]
    findings = check_consumption_distribution(bills)
    assert findings == []


def test_consumption_distribution_catches_sme_scale_on_resi_account():
    # 12 months at ~3000 kWh/month -> 36,000 kWh/yr, SME-scale on a resi record.
    bills = [_bill("C6", f"2024-{m:02d}-28", 3000.0, 150.0) for m in range(1, 13)]
    findings = check_consumption_distribution(bills)
    assert len(findings) == 1
    assert findings[0]["check"] == "consumption_distribution_vs_tdcv"
    assert findings[0]["customer_id"] == "C6"


def test_consumption_distribution_ignores_non_resi():
    bills = [_bill("C_IC1", f"2024-{m:02d}-28", 50000.0, 150.0, segment="I&C") for m in range(1, 13)]
    findings = check_consumption_distribution(bills)
    assert findings == []


def test_unit_rate_bands_clean_population_no_findings():
    # 2022 elec cap anchor ~305 GBP/MWh -- a rate near that is plausible.
    bills = [_bill("C1", "2022-06-30", 300.0, 300.0)]
    findings = check_unit_rate_bands(bills)
    assert findings == []


def test_unit_rate_bands_catches_order_of_magnitude_pricing_bug():
    bills = [_bill("C1", "2022-06-30", 300.0, 3000.0)]  # 10x too high
    findings = check_unit_rate_bands(bills)
    assert len(findings) == 1
    assert findings[0]["check"] == "unit_rate_vs_cap_band"


def test_estimated_read_rate_clean_within_band():
    meter_read_log = [{"status": "estimated"}] * 30 + [{"status": "actual"}] * 70
    assert check_estimated_read_rate(meter_read_log) == []


def test_estimated_read_rate_catches_all_estimated():
    meter_read_log = [{"status": "estimated"}] * 100
    findings = check_estimated_read_rate(meter_read_log)
    assert len(findings) == 1
    assert findings[0]["check"] == "estimated_read_rate_vs_industry_norms"


def test_estimated_read_rate_catches_all_actual():
    meter_read_log = [{"status": "actual"}] * 100
    findings = check_estimated_read_rate(meter_read_log)
    assert len(findings) == 1


def test_estimated_read_rate_empty_log_is_clean():
    assert check_estimated_read_rate([]) == []


def test_run_all_population_checks_concatenates_and_empty_is_clean():
    bills = [_bill("C1", f"2024-{m:02d}-28", 200.0, 150.0) for m in range(1, 13)]
    meter_read_log = [{"status": "estimated"}] * 30 + [{"status": "actual"}] * 70
    assert run_all_population_checks(bills, meter_read_log) == []


def test_run_all_population_checks_surfaces_every_class_of_finding():
    bad_consumption_bills = [_bill("C6", f"2024-{m:02d}-28", 3000.0, 150.0) for m in range(1, 13)]
    bad_rate_bills = [_bill("C1", "2022-06-30", 300.0, 3000.0)]
    findings = run_all_population_checks(
        bad_consumption_bills + bad_rate_bills, [{"status": "estimated"}] * 100
    )
    checks_found = {f["check"] for f in findings}
    assert "consumption_distribution_vs_tdcv" in checks_found
    assert "unit_rate_vs_cap_band" in checks_found
    assert "estimated_read_rate_vs_industry_norms" in checks_found


def _payment(method):
    return {"method": method}


def test_payment_channel_mix_clean_at_anchor_rate():
    # 73% DD, 27% standard credit -- within the DESNZ 72-75% anchor band.
    payments = [_payment("direct_debit")] * 73 + [_payment("standard_credit")] * 27
    assert check_payment_channel_mix(payments) == []


def test_payment_channel_mix_catches_flat_all_direct_debit():
    payments = [_payment("direct_debit")] * 100
    findings = check_payment_channel_mix(payments)
    assert len(findings) == 1
    assert findings[0]["check"] == "payment_channel_mix_vs_desnz_anchor"


def test_payment_channel_mix_catches_flat_all_standard_credit():
    payments = [_payment("standard_credit")] * 100
    findings = check_payment_channel_mix(payments)
    assert len(findings) == 1


def test_payment_channel_mix_empty_is_clean():
    assert check_payment_channel_mix([]) == []


def test_payment_channel_mix_ignores_other_methods():
    payments = [_payment("bacs")] * 50
    assert check_payment_channel_mix(payments) == []


def test_run_all_population_checks_payments_optional_backward_compatible():
    bills = [_bill("C1", f"2024-{m:02d}-28", 200.0, 150.0) for m in range(1, 13)]
    meter_read_log = [{"status": "estimated"}] * 30 + [{"status": "actual"}] * 70
    assert run_all_population_checks(bills, meter_read_log) == []


def test_run_all_population_checks_includes_payment_channel_finding():
    bills = [_bill("C1", f"2024-{m:02d}-28", 200.0, 150.0) for m in range(1, 13)]
    meter_read_log = [{"status": "estimated"}] * 30 + [{"status": "actual"}] * 70
    all_dd_payments = [_payment("direct_debit")] * 100
    findings = run_all_population_checks(bills, meter_read_log, all_dd_payments)
    checks_found = {f["check"] for f in findings}
    assert "payment_channel_mix_vs_desnz_anchor" in checks_found
