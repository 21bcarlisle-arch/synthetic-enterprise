"""Tests for saas/non_commodity.py -- Phase 9a/78."""

import pytest

from saas.non_commodity import (
    NON_COMMODITY_GAS_RATE_GBP_PER_MWH,
    NON_COMMODITY_RATE_GBP_PER_MWH,
    STANDING_CHARGE_GBP_PER_DAY,
    VAT_RATE,
    _SME_ELEC_MULTIPLIER,
    _SME_GAS_MULTIPLIER,
    non_commodity_rate,
    standing_charge_rate,
    vat_rate,
)


def test_elec_resi_2016():
    assert non_commodity_rate("electricity", "resi", 2016) == pytest.approx(52.0)


def test_elec_resi_2022_crisis_year():
    assert non_commodity_rate("electricity", "resi", 2022) == pytest.approx(73.0)


def test_elec_sme_2022_uses_multiplier():
    expected = 73.0 * _SME_ELEC_MULTIPLIER
    assert non_commodity_rate("electricity", "SME", 2022) == pytest.approx(expected)


def test_elec_resi_fallback_no_year():
    result = non_commodity_rate("electricity", "resi")
    assert result == pytest.approx(NON_COMMODITY_RATE_GBP_PER_MWH["resi"])


def test_elec_unknown_year_falls_back():
    result = non_commodity_rate("electricity", "resi", 2030)
    assert result == pytest.approx(NON_COMMODITY_RATE_GBP_PER_MWH["resi"])


def test_gas_resi_2021():
    assert non_commodity_rate("gas", "resi", 2021) == pytest.approx(12.0)


def test_gas_resi_2022_crisis():
    assert non_commodity_rate("gas", "resi", 2022) == pytest.approx(15.0)


def test_gas_sme_2022_uses_multiplier():
    expected = 15.0 * _SME_GAS_MULTIPLIER
    assert non_commodity_rate("gas", "SME", 2022) == pytest.approx(expected)


def test_gas_fallback_no_year():
    result = non_commodity_rate("gas", "resi")
    assert result == pytest.approx(NON_COMMODITY_GAS_RATE_GBP_PER_MWH["resi"])


def test_standing_charge_elec_resi():
    assert standing_charge_rate("electricity", "resi") == pytest.approx(0.27)


def test_standing_charge_gas_sme():
    assert standing_charge_rate("gas", "SME") == pytest.approx(0.40)


def test_standing_charge_ic_is_zero():
    """Standing-charge double-count fix (2026-07-11): I&C standing charge is
    0.0 in both real settlement engines (capacity/transportation charges are
    handled via BSC settlement, not a per-day standing charge). Before the fix
    standing_charge_rate()'s numeric default silently charged I&C the resi
    0.27/0.25 rate -- the same missing-segment-key class as the VAT bug in
    BILL_CORRECTNESS_ADDENDUM.md Defect 1."""
    assert standing_charge_rate("electricity", "I&C") == pytest.approx(0.0)
    assert standing_charge_rate("gas", "I&C") == pytest.approx(0.0)


# Every real customer segment must have an EXPLICIT standing-charge entry, not
# silently inherit the resi rate via a missing dict key -- the same invariant
# BILL_CORRECTNESS_ADDENDUM.md Defect 1 established for VAT_RATE. A future new
# business segment must add itself here explicitly, or this test catches the
# silent fallback. I&C must be zero (settlement-engine parity); resi/SME > 0.
def test_standing_charge_rate_never_silently_defaults_a_segment():
    for commodity in ("electricity", "gas"):
        assert standing_charge_rate(commodity, "I&C") == pytest.approx(0.0), (
            f"{commodity} I&C standing charge must be 0.0 (settlement engines "
            "return 0.0 for I&C); a non-zero value means I&C is missing from "
            "STANDING_CHARGE_GBP_PER_DAY and silently fell back to the resi rate"
        )
        assert STANDING_CHARGE_GBP_PER_DAY[commodity]["I&C"] == 0.0
        for segment in ("resi", "SME"):
            assert standing_charge_rate(commodity, segment) > 0.0


def test_vat_resi_is_five_pct():
    assert vat_rate("resi") == pytest.approx(0.05)


def test_vat_sme_is_twenty_pct():
    assert vat_rate("SME") == pytest.approx(0.20)


def test_vat_ic_is_twenty_pct():
    """BILL_CORRECTNESS_ADDENDUM.md Defect 1: I&C was missing from VAT_RATE,
    so vat_rate("I&C") silently fell back to the domestic 5% rate instead of
    the legally-required 20% business rate."""
    assert vat_rate("I&C") == pytest.approx(0.20)


# Every real customer segment that appears in generated data (site/data/
# customer_sample.json's live segment values, confirmed 2026-07-08) that is
# NOT domestic must be billed at the business VAT rate, not silently
# defaulted to the resi rate via a missing dict key. This is the domain
# invariant BILL_CORRECTNESS_ADDENDUM.md Defect 1 asks for: "VAT: domestic =
# 5%; business = 20%. Assert per bill." -- a future new business segment
# must add itself here explicitly, or this test catches the silent fallback.
_REAL_DOMESTIC_SEGMENTS = {"resi"}
_REAL_BUSINESS_SEGMENTS = {"SME", "I&C"}


def test_vat_rate_never_silently_defaults_a_business_segment():
    for segment in _REAL_BUSINESS_SEGMENTS:
        assert vat_rate(segment) == pytest.approx(0.20), (
            f"segment {segment!r} must be billed at the 20% business VAT "
            "rate -- got the domestic rate, meaning it's missing from "
            "VAT_RATE and silently fell back to resi's rate"
        )
    for segment in _REAL_DOMESTIC_SEGMENTS:
        assert vat_rate(segment) == pytest.approx(0.05)
