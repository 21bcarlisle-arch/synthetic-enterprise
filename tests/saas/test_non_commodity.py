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
