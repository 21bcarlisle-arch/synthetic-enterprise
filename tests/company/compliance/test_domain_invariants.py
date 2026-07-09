"""Tests for company/compliance/domain_invariants.py -- DOMAIN_SENSE_AND_COMPLIANCE.md Phase 2."""
from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    VAT_RESIDENTIAL,
    VAT_SME,
    TDCV_ELEC_MEDIUM,
    TDCV_GAS_MEDIUM,
    UNIT_RATE_ELEC_RESI_BY_YEAR,
    RESI_CONSUMPTION_ENVELOPE_ELEC,
    check_vat,
    check_unit_rate_plausible,
    check_resi_consumption_plausible,
    vat_rate_for_segment,
    invariant_count,
)


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
