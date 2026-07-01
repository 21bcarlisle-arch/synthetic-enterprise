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
