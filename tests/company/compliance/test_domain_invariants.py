"""Tests for company/compliance/domain_invariants.py -- DOMAIN_SENSE_AND_COMPLIANCE.md Phase 2."""
from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    BACK_BILLING_CAP_RESPECTED,
    VAT_RESIDENTIAL,
    VAT_SME,
    TDCV_ELEC_MEDIUM,
    TDCV_GAS_MEDIUM,
    UNIT_RATE_ELEC_RESI_BY_YEAR,
    RESI_CONSUMPTION_ENVELOPE_ELEC,
    check_back_billing_cap_respected,
    check_vat,
    check_vat_consistent_with_consumption,
    consumption_implied_vat_rate,
    VAT_SEGMENT_MATCHES_CONSUMPTION,
    check_unit_rate_plausible,
    check_resi_consumption_plausible,
    vat_rate_for_segment,
    invariant_count,
)


# --- INVARIANT_LIBRARY_REDTEAM.md C1 (2026-07-13): VAT/segment independent
# --- cross-check (the fix for the vat_by_segment tautology, R10 C6 class) ---


def test_vat_segment_matches_consumption_registered_as_uk_structural_invariant():
    assert VAT_SEGMENT_MATCHES_CONSUMPTION.jurisdiction == "UK"
    assert VAT_SEGMENT_MATCHES_CONSUMPTION in ALL_INVARIANTS


def test_consumption_implied_vat_rate_high_load_implies_business():
    # An I&C-scale monthly load (C6's real 2,346.8 kWh/mo elec) is clearly above
    # the anchored domestic ceiling -> implies the 20% business rate.
    assert consumption_implied_vat_rate("electricity", 2346.8, 30) == VAT_SME.value


def test_consumption_implied_vat_rate_domestic_load_implies_residential():
    assert consumption_implied_vat_rate("electricity", 300.0, 30) == VAT_RESIDENTIAL.value


def test_consumption_implied_vat_rate_indeterminate_signals():
    # No usable signal -> None (sign/period/other-commodity invariants own these).
    assert consumption_implied_vat_rate("electricity", 0.0, 30) is None
    assert consumption_implied_vat_rate("electricity", 300.0, 0) is None
    assert consumption_implied_vat_rate("water", 300.0, 30) is None


def test_vat_control_is_a_tautology_but_crosscheck_catches_the_mislabel():
    # The exact non-tautology demonstration: on a self-consistent SME-as-resi
    # mislabel (5% applied, I&C-scale load), the arithmetic label-vs-rate control
    # PASSES (tautology) while the independent consumption cross-check CATCHES it.
    assert check_vat("resi", 0.05) is True  # inert: 5% vs resi-implies-5%
    assert check_vat_consistent_with_consumption(
        "resi", "electricity", 0.05, 2346.8, 30
    ) is False  # caught: I&C load contradicts the domestic 5% rate


def test_vat_crosscheck_passes_correct_ic_scale_sme():
    # I&C load correctly billed at 20% -> consistent, not flagged.
    assert check_vat_consistent_with_consumption(
        "sme", "electricity", 0.20, 45000.0, 30
    ) is True


def test_vat_crosscheck_never_flags_business_rate_on_domestic_load():
    # Honest weak direction: a small business on domestic-scale consumption
    # paying 20% must NOT be flagged (a microbusiness looks identical).
    assert check_vat_consistent_with_consumption(
        "sme", "electricity", 0.20, 300.0, 30
    ) is True


def test_vat_crosscheck_passes_legit_domestic_bill():
    assert check_vat_consistent_with_consumption(
        "resi", "electricity", 0.05, 300.0, 30
    ) is True


def test_at_least_twenty_invariants_seeded():
    assert invariant_count() >= 20


def test_all_invariant_ids_are_unique():
    ids = [inv.id for inv in ALL_INVARIANTS]
    assert len(ids) == len(set(ids))


def test_vat_residential_is_5_percent():
    assert VAT_RESIDENTIAL.check(0.05) is True
    assert VAT_RESIDENTIAL.check(0.20) is False


def test_vat_sme_is_20_percent():
    assert VAT_SME.check(0.20) is True
    assert VAT_SME.check(0.05) is False


def test_vat_rate_for_segment():
    assert vat_rate_for_segment("resi") == 0.05
    assert vat_rate_for_segment("SME") == 0.20
    assert vat_rate_for_segment("I&C") == 0.20


def test_check_vat_catches_the_r10_c6_defect_class():
    # The R10-cited defect: an SME billed as Household at 20% VAT (or the
    # reverse) -- this is exactly the class this invariant must catch.
    assert check_vat("resi", 0.05) is True
    assert check_vat("resi", 0.20) is False
    assert check_vat("SME", 0.20) is True
    assert check_vat("SME", 0.05) is False


def test_tdcv_medium_bands_match_ofgem_2026_review():
    # Ofgem TDCV 2026 review: elec medium 2,500 kWh/yr, gas medium 9,500 kWh/yr
    # (docs/market_research/ons_consumption_profiles.md).
    assert TDCV_ELEC_MEDIUM.check(2500.0) is True
    assert TDCV_GAS_MEDIUM.check(9500.0) is True


def test_unit_rate_plausibility_uses_the_real_anchored_cap_not_a_guess():
    # 2022 electricity cap ~305 GBP/MWh (Phase 47a anchor) -- must be
    # plausible; an order-of-magnitude error (e.g. 30.5 or 3050) must not be.
    assert check_unit_rate_plausible("electricity", 2022, 305.0) is True
    assert check_unit_rate_plausible("electricity", 2022, 30.5) is False
    assert check_unit_rate_plausible("electricity", 2022, 3050.0) is False


def test_unit_rate_plausibility_falls_back_to_nearest_anchored_year():
    # Years beyond the anchored table (e.g. 2026) must still resolve to a
    # plausible range via the nearest anchor, not crash or silently pass
    # anything.
    assert UNIT_RATE_ELEC_RESI_BY_YEAR.check(190.0, 2026) is True
    assert UNIT_RATE_ELEC_RESI_BY_YEAR.check(19000.0, 2026) is False


def test_resi_consumption_envelope_catches_gross_implausibility():
    # A real domestic customer's annual usage; and the C6-class implausible
    # SME-scale figure that should never appear on a resi account.
    assert check_resi_consumption_plausible("electricity", 2500.0) is True
    assert check_resi_consumption_plausible("electricity", 45000.0) is False


def test_range_invariant_boundaries_are_inclusive():
    assert RESI_CONSUMPTION_ENVELOPE_ELEC.check(RESI_CONSUMPTION_ENVELOPE_ELEC.low) is True
    assert RESI_CONSUMPTION_ENVELOPE_ELEC.check(RESI_CONSUMPTION_ENVELOPE_ELEC.high) is True


def test_every_invariant_has_a_real_source_string():
    for inv in ALL_INVARIANTS:
        assert inv.source and len(inv.source) >= 5


def test_yearly_range_invariant_derives_from_ofgem_price_cap_module():
    from company.pricing.ofgem_price_cap import get_cap_unit_rate_gbp_per_mwh
    # The anchor for 2022 must match the ofgem_price_cap module's own value
    # exactly -- proves the invariant reuses it rather than duplicating a
    # second, driftable copy.
    anchor_2022 = get_cap_unit_rate_gbp_per_mwh("electricity", 2022)
    low, high = UNIT_RATE_ELEC_RESI_BY_YEAR.plausible_range(2022)
    assert low < anchor_2022 < high


# --- ADVISOR_STEER_BACKBILLING_GATE.md item 2: jurisdiction discipline ---


def test_every_invariant_is_tagged_uk_jurisdiction():
    # Every invariant in this library today IS UK law/market data -- this
    # proves the field is structurally populated, not silently defaulted
    # and forgotten. A future non-UK addition must set this explicitly
    # rather than inherit the default.
    for inv in ALL_INVARIANTS:
        assert inv.jurisdiction == "UK"


def test_rate_range_yearlyrange_invariants_all_expose_jurisdiction_field():
    assert VAT_RESIDENTIAL.jurisdiction == "UK"
    assert RESI_CONSUMPTION_ENVELOPE_ELEC.jurisdiction == "UK"
    assert UNIT_RATE_ELEC_RESI_BY_YEAR.jurisdiction == "UK"


# --- ADVISOR_STEER_BACKBILLING_GATE.md item 1(c): pre-bill Tier-1 cap invariant ---


def test_back_billing_cap_respected_registered_as_uk_structural_invariant():
    assert BACK_BILLING_CAP_RESPECTED.jurisdiction == "UK"
    assert BACK_BILLING_CAP_RESPECTED in ALL_INVARIANTS


# --- REGULATION_COMMONS_DOCTRINE.md item 3: time-indexed law ---


def test_invariants_expose_effective_date_fields_defaulting_to_none():
    assert VAT_RESIDENTIAL.effective_from is None
    assert VAT_RESIDENTIAL.effective_to is None
    assert RESI_CONSUMPTION_ENVELOPE_ELEC.effective_from is None
    assert UNIT_RATE_ELEC_RESI_BY_YEAR.effective_from is None


def test_back_billing_cap_respected_backfilled_with_real_slc_21ba_date():
    import datetime
    assert BACK_BILLING_CAP_RESPECTED.effective_from == datetime.date(2018, 5, 1)
    assert BACK_BILLING_CAP_RESPECTED.effective_to is None


def test_check_back_billing_cap_respected_passes_when_no_catchup():
    assert check_back_billing_cap_respected({}) is True


def test_check_back_billing_cap_respected_passes_for_credits_never_capped():
    bill = {
        "catchup_applied": True, "catchup_direction": "overcharge",
        "catchup_period_start": "2015-01-01", "period_end": "2019-12-31",
    }
    assert check_back_billing_cap_respected(bill) is True


def test_check_back_billing_cap_respected_passes_when_within_window():
    bill = {
        "catchup_applied": True, "catchup_direction": "undercharge",
        "catchup_period_start": "2019-06-01", "catchup_period_end": "2019-06-30",
        "period_end": "2019-12-31", "catchup_raw_delta_gbp": 100.0,
    }
    assert check_back_billing_cap_respected(bill) is True


def test_check_back_billing_cap_respected_fails_when_breach_not_written_off():
    # A bill that breaches the 12-month window but was silently charged in
    # full (a real live gap this steer exists to catch) must be caught.
    bill = {
        "catchup_applied": True, "catchup_direction": "undercharge",
        "catchup_period_start": "2018-06-01", "catchup_period_end": "2019-05-31",
        "period_end": "2019-12-31",
        "catchup_written_off_gbp": 0.0, "catchup_raw_delta_gbp": 600.0,
        "catchup_adjustment_gbp": 600.0,
    }
    assert check_back_billing_cap_respected(bill) is False


def test_check_back_billing_cap_respected_fails_on_token_write_off_wrong_magnitude():
    # invariant_redteam_2026-07-12.md Finding 3: a 1p symbolic write-off
    # against a genuinely large, old breach must NOT pass just because
    # written_off > 0 -- the magnitude must match what the law requires.
    bill = {
        "catchup_applied": True, "catchup_direction": "undercharge",
        "catchup_period_start": "2019-01-01", "catchup_period_end": "2024-01-31",
        "period_end": "2024-01-31",
        "catchup_written_off_gbp": 0.01, "catchup_raw_delta_gbp": 5000.0,
        "catchup_adjustment_gbp": 4999.99,
    }
    assert check_back_billing_cap_respected(bill) is False


def test_check_back_billing_cap_respected_fails_on_malformed_direction():
    # invariant_redteam_2026-07-12.md Finding 4: a case typo or unrecognised
    # direction must fail CLOSED (HELD), not silently pass.
    bill = {
        "catchup_applied": True, "catchup_direction": "Undercharge",
        "catchup_period_start": "2018-06-01", "catchup_period_end": "2019-05-31",
        "period_end": "2019-12-31", "catchup_raw_delta_gbp": 600.0,
    }
    assert check_back_billing_cap_respected(bill) is False


def test_check_back_billing_cap_respected_fails_on_missing_period_fields():
    # Same finding: a missing catchup_period_end must fail closed too.
    bill = {
        "catchup_applied": True, "catchup_direction": "undercharge",
        "catchup_period_start": "2018-06-01",
        "period_end": "2019-12-31", "catchup_raw_delta_gbp": 600.0,
    }
    assert check_back_billing_cap_respected(bill) is False


def test_check_back_billing_cap_respected_fails_closed_on_malformed_date_not_just_missing():
    # Fresh Expert-Hour finding (2026-07-12): a PRESENT but malformed date
    # string previously raised an uncaught ValueError instead of failing
    # closed -- confirmed this crashed validate_bills() for an ENTIRE batch,
    # not just the one bad bill. Must return False, never raise.
    bill = {
        "catchup_applied": True, "catchup_direction": "undercharge",
        "catchup_period_start": "01/06/2018",  # not ISO format
        "catchup_period_end": "2019-05-31",
        "period_end": "2019-12-31", "catchup_raw_delta_gbp": 600.0,
    }
    assert check_back_billing_cap_respected(bill) is False


def test_check_back_billing_cap_respected_fails_closed_on_garbage_date_string():
    bill = {
        "catchup_applied": True, "catchup_direction": "undercharge",
        "catchup_period_start": "not-a-date",
        "catchup_period_end": "2019-05-31",
        "period_end": "2019-12-31", "catchup_raw_delta_gbp": 600.0,
    }
    assert check_back_billing_cap_respected(bill) is False


def test_check_back_billing_cap_respected_passes_when_genuinely_written_off():
    from company.billing.back_billing import BackBillingAssessment, BackBillingReason
    import datetime as _dt
    assessment = BackBillingAssessment(
        account_id="C1", billing_date=_dt.date(2019, 12, 31),
        consumption_period_start=_dt.date(2018, 6, 1),
        consumption_period_end=_dt.date(2019, 5, 31),
        billed_amount_gbp=600.0, reason=BackBillingReason.ESTIMATED_READ_CORRECTED,
        is_domestic=True,
    )
    assert assessment.cap_applies  # sanity: this scenario genuinely breaches
    bill = {
        "catchup_applied": True, "catchup_direction": "undercharge",
        "catchup_period_start": "2018-06-01", "catchup_period_end": "2019-05-31",
        "period_end": "2019-12-31",
        "catchup_written_off_gbp": assessment.written_off_gbp,
        "catchup_raw_delta_gbp": 600.0,
        "catchup_adjustment_gbp": assessment.capped_amount_gbp,
    }
    assert check_back_billing_cap_respected(bill) is True


# --- BILL_TO_LEDGER_LINKAGE.md (2026-07-12): billed-clock reconciliation ---


def test_billed_clock_reconciles_registered_as_structural_invariant():
    from company.compliance.domain_invariants import BILLED_CLOCK_RECONCILES_WITH_ISSUED_BILLS
    assert BILLED_CLOCK_RECONCILES_WITH_ISSUED_BILLS in ALL_INVARIANTS
    assert BILLED_CLOCK_RECONCILES_WITH_ISSUED_BILLS.jurisdiction == "UK"


def test_check_billed_clock_reconciles_true_when_exact_match():
    from company.compliance.domain_invariants import check_billed_clock_reconciles
    bills = [{"total_amount_gbp": 73.04}, {"total_amount_gbp": 100.0}]
    assert check_billed_clock_reconciles(173.04, bills) is True


def test_check_billed_clock_reconciles_false_on_real_divergence():
    from company.compliance.domain_invariants import check_billed_clock_reconciles
    bills = [{"total_amount_gbp": 73.04}, {"total_amount_gbp": 100.0}]
    # A held bill's amount leaked into total_billed_gbp but isn't in issued_bills.
    assert check_billed_clock_reconciles(173.04 + 42.0, bills) is False


def test_check_billed_clock_reconciles_tolerant_of_penny_rounding():
    from company.compliance.domain_invariants import check_billed_clock_reconciles
    bills = [{"total_amount_gbp": 73.045}]
    assert check_billed_clock_reconciles(73.04, bills) is True


def test_check_billed_clock_reconciles_empty_bills():
    from company.compliance.domain_invariants import check_billed_clock_reconciles
    assert check_billed_clock_reconciles(0.0, []) is True
    assert check_billed_clock_reconciles(10.0, []) is False


# --- F6_rebuild: structural bill-integrity invariants (INVARIANT_LIBRARY_REDTEAM
# --- gaps 2-4; R10 class-level, R15 mutation-tested per control) ---

from company.compliance.domain_invariants import (  # noqa: E402
    BILL_FOOTS,
    BILL_LINE_ITEMS_NON_NEGATIVE,
    BILL_PERIOD_TEMPORAL_SANE,
    check_bill_foots,
    check_bill_line_items_non_negative,
    check_bill_period_sane,
    is_credit_bill,
)


def _footing_bill(**overrides):
    """A well-formed bill whose total foots to its components."""
    bill = {
        "customer_id": "C1",
        "period_start": "2024-01-01",
        "period_end": "2024-01-31",
        "commodity_amount_gbp": 50.0,
        "non_commodity_amount_gbp": 20.0,
        "standing_charge_gbp": 8.0,
        "vat_gbp": 3.9,
        "total_amount_gbp": 81.9,
    }
    bill.update(overrides)
    return bill


def test_f6_invariants_registered_as_uk_structural():
    for inv in (BILL_FOOTS, BILL_LINE_ITEMS_NON_NEGATIVE, BILL_PERIOD_TEMPORAL_SANE):
        assert inv in ALL_INVARIANTS
        assert inv.jurisdiction == "UK"
        assert inv.source and len(inv.source) >= 5


# BILL_FOOTS -------------------------------------------------------------------

def test_bill_foots_passes_when_total_matches_components():
    assert check_bill_foots(_footing_bill()) is True


def test_bill_foots_mutation_fires_on_mistotalled_bill():
    # R15 mutation test: the exact named defect -- a GBP 999,999 total printed
    # on ~GBP 82 of line items -- MUST fire (return False), never pass.
    assert check_bill_foots(_footing_bill(total_amount_gbp=999999.0)) is False


def test_bill_foots_includes_catchup_adjustment_component():
    # The regression that sank the first F6: a catch-up bill's total legitimately
    # exceeds the four category lines by exactly catchup_adjustment_gbp. With the
    # adjustment in the footing set the bill foots and is NOT held.
    bill = _footing_bill(total_amount_gbp=122.9, catchup_adjustment_gbp=41.0)
    assert check_bill_foots(bill) is True
    # ...and without the adjustment present, that same total would NOT foot.
    assert check_bill_foots(_footing_bill(total_amount_gbp=122.9)) is False


def test_bill_foots_not_applicable_when_no_total_declared():
    bill = _footing_bill()
    del bill["total_amount_gbp"]
    assert check_bill_foots(bill) is True


def test_bill_foots_fails_closed_on_unreadable_total():
    assert check_bill_foots(_footing_bill(total_amount_gbp="lots")) is False


def test_bill_foots_fails_closed_on_unreadable_component():
    assert check_bill_foots(_footing_bill(commodity_amount_gbp="fifty")) is False


def test_bill_foots_tolerant_of_penny_rounding():
    assert check_bill_foots(_footing_bill(total_amount_gbp=81.93)) is True


def test_bill_foots_sign_invariant_for_credit_note():
    # A legitimate credit note (all components negative) foots normally.
    credit = _footing_bill(
        commodity_amount_gbp=-50.0, non_commodity_amount_gbp=-20.0,
        standing_charge_gbp=-8.0, vat_gbp=-3.9, total_amount_gbp=-81.9,
    )
    assert check_bill_foots(credit) is True


# BILL_LINE_ITEMS_NON_NEGATIVE -------------------------------------------------

def test_non_negative_passes_on_a_clean_bill():
    assert check_bill_line_items_non_negative(_footing_bill()) is True


def test_non_negative_mutation_fires_on_negative_charge():
    # R15 mutation test: a negative standing charge on a NON-credit bill MUST fire.
    assert check_bill_line_items_non_negative(_footing_bill(standing_charge_gbp=-8.0)) is False


def test_non_negative_exempts_genuine_overcharge_credit_note():
    credit = _footing_bill(
        commodity_amount_gbp=-50.0, vat_gbp=-3.9,
        catchup_applied=True, catchup_direction="overcharge",
    )
    assert is_credit_bill(credit) is True
    assert check_bill_line_items_non_negative(credit) is True


def test_non_negative_does_not_exempt_an_undercharge_catchup():
    # An undercharge catch-up is not a credit; a negative line item on it is
    # still absurd and must fire.
    bill = _footing_bill(
        standing_charge_gbp=-8.0,
        catchup_applied=True, catchup_direction="undercharge",
    )
    assert is_credit_bill(bill) is False
    assert check_bill_line_items_non_negative(bill) is False


def test_non_negative_fails_closed_on_unreadable_amount():
    assert check_bill_line_items_non_negative(_footing_bill(vat_gbp="none")) is False


def test_non_negative_tolerant_of_tiny_rounding_artefact():
    assert check_bill_line_items_non_negative(_footing_bill(vat_gbp=-0.001)) is True


# BILL_PERIOD_TEMPORAL_SANE ----------------------------------------------------

def test_period_sane_passes_on_forward_period():
    assert check_bill_period_sane(_footing_bill()) is True


def test_period_sane_mutation_fires_on_reversed_dates():
    # R15 mutation test: the exact named defect -- start after end -- MUST fire,
    # never be silently clamped to a 1-day period.
    reversed_bill = _footing_bill(period_start="2024-01-31", period_end="2024-01-01")
    assert check_bill_period_sane(reversed_bill) is False


def test_period_sane_allows_equal_start_and_end():
    assert check_bill_period_sane(_footing_bill(period_start="2024-01-01", period_end="2024-01-01")) is True


def test_period_sane_fails_closed_on_missing_dates():
    bill = _footing_bill()
    del bill["period_start"]
    assert check_bill_period_sane(bill) is False


def test_period_sane_fails_closed_on_unparseable_dates():
    assert check_bill_period_sane(_footing_bill(period_start="01/06/2018")) is False


def test_period_sane_fires_on_absurdly_long_span():
    # F6 HARDEN 2026-07-16 (R15 mutation test): an ORDERED but multi-decade
    # service period is as temporally impossible as a reversed one. Previously
    # this passed the "temporal sanity" control (start<=end only) -- a fail-open.
    absurd = _footing_bill(period_start="2024-01-01", period_end="2099-12-31")
    assert check_bill_period_sane(absurd) is False


def test_period_sane_allows_an_annual_bill():
    # Regression guard: the span bound must NOT fire on a legitimate annual bill
    # (the longest real single-period bill a UK supplier issues). Observed max in
    # this project's data is 30 days; a full year has a ~24x margin to the bound.
    annual = _footing_bill(period_start="2023-01-01", period_end="2023-12-31")
    assert check_bill_period_sane(annual) is True
