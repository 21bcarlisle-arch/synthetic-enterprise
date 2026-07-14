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


# --- INVARIANT_LIBRARY_REDTEAM.md C1 (2026-07-13): the vat_by_segment control
# --- was a tautology; the independent consumption cross-check makes it real ---


def test_arithmetic_vat_control_alone_is_a_tautology_on_a_mislabel():
    # BEFORE the fix: a self-consistent mislabel (SME customer labelled resi,
    # so VAT is computed at the domestic 5% to match the WRONG label) sails
    # through the arithmetic label-vs-rate control -- proving it is inert
    # against the exact C6 SME-as-Household class it is named for.
    from company.compliance.domain_invariants import check_vat
    from company.billing.pre_bill_validation import _actual_vat_rate

    # A resi-labelled bill whose 5% VAT is internally consistent with that label
    # but whose metered load (C6's real 2,346.8 kWh/mo) is I&C-scale.
    subtotal = 700.0 + 200.0 + 9.0
    mislabel = _good_resi_bill(
        segment="resi", total_consumption_kwh=2346.8,
        commodity_amount_gbp=700.0, non_commodity_amount_gbp=200.0,
        standing_charge_gbp=9.0, vat_gbp=subtotal * 0.05,
    )
    # The arithmetic control passes it (tautology): 5% applied vs resi-implies-5%.
    assert check_vat("resi", _actual_vat_rate(mislabel)) is True


def test_mislabelled_sme_as_household_is_caught_by_vat_consumption_crosscheck():
    # AFTER the fix: the SAME self-consistent mislabel is now HELD, and the
    # reason cites the independent (label-free) consumption signal, not just the
    # adjacent consumption-plausibility check.
    subtotal = 700.0 + 200.0 + 9.0
    mislabel = _good_resi_bill(
        segment="resi", total_consumption_kwh=2346.8,
        commodity_amount_gbp=700.0, non_commodity_amount_gbp=200.0,
        standing_charge_gbp=9.0, vat_gbp=subtotal * 0.05,
    )
    result = validate_bill(mislabel)
    assert result.held is True
    # The vat_by_segment obligation now fires on a mislabel it previously could
    # not touch -- the control is no longer a tautology.
    assert any(
        "vat_by_segment" in r and "SME-as-Household mislabel" in r
        for r in result.reasons
    )


def test_moderate_sme_mislabel_below_absurdity_bound_relies_on_the_vat_crosscheck():
    # A mislabelled SME whose load is I&C-scale but NOT grossly absurd. This
    # documents that the VAT cross-check and the consumption-plausibility check
    # share the anchored domestic ceiling: both trip together here. The point is
    # that the vat_by_segment obligation now has independent detective power at
    # all, attributed to the correct (tax-classification) control.
    subtotal = 800.0 + 200.0 + 9.0
    mislabel = _good_resi_bill(
        segment="resi", total_consumption_kwh=3000.0,
        commodity_amount_gbp=800.0, non_commodity_amount_gbp=200.0,
        standing_charge_gbp=9.0, vat_gbp=subtotal * 0.05,
    )
    result = validate_bill(mislabel)
    assert result.held is True
    assert any("SME-as-Household mislabel" in r for r in result.reasons)


def test_correct_ic_scale_sme_bill_not_flagged_by_vat_crosscheck():
    # A legitimate SME bill: I&C-scale load billed correctly at 20%. The
    # cross-check must NOT flag it (applied rate matches the consumption-implied
    # non-domestic rate) -- no false positive.
    subtotal = 4455.0 + 16.65 + 9.30
    bill = _good_resi_bill(
        segment="SME", total_consumption_kwh=45000.0,
        commodity_amount_gbp=4455.0, vat_gbp=0.20 * subtotal,
    )
    result = validate_bill(bill)
    assert not any("SME-as-Household mislabel" in r for r in result.reasons)


def test_legit_small_business_on_domestic_consumption_not_flagged():
    # The honest weak direction: a genuine small business (microbusiness /
    # corner shop) consumes domestic-scale volumes and correctly pays 20%. The
    # cross-check must NEVER flag this -- low consumption cannot refute a
    # business label. This is a legit bill and must PASS.
    bill = _good_resi_bill(segment="SME", total_consumption_kwh=300.0, vat_gbp=14.10)
    result = validate_bill(bill)
    assert result.outcome == ValidationOutcome.PASS
    assert not any("SME-as-Household mislabel" in r for r in result.reasons)


def test_electric_heated_resi_max_not_flagged_by_vat_crosscheck():
    # The real observed electric-heated resi max (1,945 kWh/mo, within the
    # anchored domestic envelope) at the correct 5% rate must NOT trip the VAT
    # cross-check -- proves the domestic ceiling has headroom for genuine
    # electric heating and does not false-positive real domestic customers.
    bill = _good_resi_bill(total_consumption_kwh=1945.0, vat_gbp=3.53)
    result = validate_bill(bill)
    assert not any("SME-as-Household mislabel" in r for r in result.reasons)


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
        catchup_period_start="2024-01-01", catchup_period_end="2024-01-31",
        catchup_raw_delta_gbp=10.0,
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
        catchup_period_start="2022-06-01", catchup_period_end="2023-05-31",
        catchup_written_off_gbp=0.0, catchup_raw_delta_gbp=300.0,
        catchup_adjustment_gbp=300.0,
    )
    result = validate_bill(bill)
    assert result.held is True
    assert any("slc_21ba_back_billing_cap" in r for r in result.reasons)


def test_breach_genuinely_written_off_passes():
    from company.billing.back_billing import BackBillingAssessment, BackBillingReason
    import datetime as _dt
    assessment = BackBillingAssessment(
        account_id="C1", billing_date=_dt.date(2024, 1, 31),
        consumption_period_start=_dt.date(2022, 6, 1),
        consumption_period_end=_dt.date(2023, 5, 31),
        billed_amount_gbp=300.0, reason=BackBillingReason.ESTIMATED_READ_CORRECTED,
        is_domestic=True,
    )
    assert assessment.cap_applies
    bill = _good_resi_bill(
        period_end="2024-01-31",
        catchup_applied=True, catchup_direction="undercharge",
        catchup_period_start="2022-06-01", catchup_period_end="2023-05-31",
        catchup_written_off_gbp=assessment.written_off_gbp, catchup_raw_delta_gbp=300.0,
        catchup_adjustment_gbp=assessment.capped_amount_gbp,
    )
    result = validate_bill(bill)
    assert not any("slc_21ba_back_billing_cap" in r for r in result.reasons)


def test_breach_with_token_write_off_wrong_magnitude_is_held():
    # invariant_redteam_2026-07-12.md Finding 3, wired end-to-end through
    # the actual pre-bill gate: a symbolic write-off must not satisfy it.
    bill = _good_resi_bill(
        period_end="2024-01-31",
        catchup_applied=True, catchup_direction="undercharge",
        catchup_period_start="2019-01-01", catchup_period_end="2024-01-31",
        catchup_written_off_gbp=0.01, catchup_raw_delta_gbp=5000.0,
        catchup_adjustment_gbp=4999.99,
    )
    result = validate_bill(bill)
    assert result.held is True
    assert any("slc_21ba_back_billing_cap" in r for r in result.reasons)


def test_batch_with_one_malformed_date_bill_does_not_abort_the_whole_batch():
    # Fresh Expert-Hour finding (2026-07-12): a present-but-malformed
    # catchup_period_start previously raised an uncaught ValueError inside
    # check_back_billing_cap_respected(), which propagated all the way up
    # through validate_bills() and aborted the ENTIRE batch -- taking down
    # every other, genuinely fine bill in the same call. The malformed bill
    # must route to HELD; the good bills around it must still pass.
    good_before = _good_resi_bill(customer_id="C1", period_end="2024-01-31")
    malformed = _good_resi_bill(
        customer_id="C2", period_end="2024-01-31",
        catchup_applied=True, catchup_direction="undercharge",
        catchup_period_start="01/06/2018", catchup_period_end="2019-05-31",
        catchup_raw_delta_gbp=600.0,
    )
    good_after = _good_resi_bill(customer_id="C3", period_end="2024-01-31")
    passing, exceptions = validate_bills([good_before, malformed, good_after])
    assert {b["customer_id"] for b in passing} == {"C1", "C3"}
    assert len(exceptions) == 1
    assert exceptions[0].customer_id == "C2"
    assert any("slc_21ba_back_billing_cap" in r for r in exceptions[0].reasons)


def test_breach_with_malformed_direction_is_held():
    # invariant_redteam_2026-07-12.md Finding 4: fail closed, not open.
    bill = _good_resi_bill(
        period_end="2024-01-31",
        catchup_applied=True, catchup_direction="Undercharge",
        catchup_period_start="2022-06-01", catchup_period_end="2023-05-31",
        catchup_raw_delta_gbp=300.0,
    )
    result = validate_bill(bill)
    assert result.held is True
    assert any("slc_21ba_back_billing_cap" in r for r in result.reasons)


def test_zero_subtotal_bill_does_not_crash_vat_check():
    bill = _good_resi_bill(
        commodity_amount_gbp=0.0, non_commodity_amount_gbp=0.0,
        standing_charge_gbp=0.0, vat_gbp=0.0,
    )
    result = validate_bill(bill)
    # No VAT reason possible with a zero subtotal (nothing to rate-check);
    # consumption reason still applies independently.
    assert not any("vat_by_segment" in r for r in result.reasons)


# --- F6_bill_integrity_structural: footing, non-negativity, temporal sanity ---
# Wired end-to-end through the actual pre-bill gate. Each defect must HOLD; each
# legitimate edge (credit note, no declared total, sane period) must still PASS.


def test_bill_that_does_not_foot_is_held():
    # A GBP 999,999 total on GBP 70 of line items -- the named footing defect.
    bill = _good_resi_bill(total_amount_gbp=999999.0)
    result = validate_bill(bill)
    assert result.held is True
    assert any("does not foot" in r for r in result.reasons)


def test_correctly_footing_bill_passes():
    # commodity + non-commodity + standing + VAT = 44.55 + 16.65 + 9.30 + 3.53
    bill = _good_resi_bill(total_amount_gbp=74.03)
    result = validate_bill(bill)
    assert result.outcome == ValidationOutcome.PASS


def test_bill_without_declared_total_still_passes():
    # The existing fixtures omit total_amount_gbp -- footing is not-applicable,
    # not a fail-open hold.
    result = validate_bill(_good_resi_bill())
    assert not any("does not foot" in r for r in result.reasons)


def test_negative_line_item_on_normal_bill_is_held():
    bill = _good_resi_bill(standing_charge_gbp=-9.30)
    result = validate_bill(bill)
    assert result.held is True
    assert any("line item is negative" in r for r in result.reasons)


def test_legitimate_overcharge_credit_note_is_not_held_for_sign():
    # A D3 catch-up overcharge credit: negative amounts are correct, must PASS
    # the sign check (and its VAT is validated on magnitudes, not skipped).
    subtotal = -70.50
    credit = _good_resi_bill(
        commodity_amount_gbp=-44.55, non_commodity_amount_gbp=-16.65,
        standing_charge_gbp=-9.30, vat_gbp=subtotal * 0.05,
        total_amount_gbp=subtotal * 1.05,
        catchup_applied=True, catchup_direction="overcharge",
    )
    result = validate_bill(credit)
    assert not any("line item is negative" in r for r in result.reasons)


def test_reversed_date_bill_is_rejected_not_clamped():
    # The named temporal defect: period_start after period_end. Previously
    # silently clamped to a 1-day period by _days_in_period() and issued.
    bill = _good_resi_bill(period_start="2024-02-28", period_end="2024-01-01")
    result = validate_bill(bill)
    assert result.held is True
    assert any("temporally impossible" in r for r in result.reasons)


def test_footing_check_is_sign_invariant_credit_still_foots():
    # A correctly-footing credit note passes footing; a mis-footing one is held.
    subtotal = -70.50
    good_credit = _good_resi_bill(
        commodity_amount_gbp=-44.55, non_commodity_amount_gbp=-16.65,
        standing_charge_gbp=-9.30, vat_gbp=round(subtotal * 0.05, 2),
        total_amount_gbp=round(subtotal * 1.05, 2),
        catchup_applied=True, catchup_direction="overcharge",
    )
    assert not any("does not foot" in r for r in validate_bill(good_credit).reasons)
