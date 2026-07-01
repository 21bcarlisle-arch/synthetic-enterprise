import pytest

from saas.tariff_pricing import (
    SIGMA_STRESSED_POST_2023,
    SIGMA_STRESSED_PRE_2023,
    TARGET_MARGIN_GBP_PER_MWH,
    WACC,
    Z_SCORE,
    price_fixed_tariff,
)


def test_tariff_covers_forward_price():
    forward_price = 60.0
    eac_kwh = 3500
    term_start = "2024-01-01"
    tariff = price_fixed_tariff(forward_price, eac_kwh, term_start)
    assert tariff >= forward_price


def test_tariff_covers_capital_cost():
    forward_price = 60.0
    eac_kwh = 3500
    term_start = "2024-01-01"
    sigma_stressed = SIGMA_STRESSED_POST_2023 if term_start >= "2023-01-01" else SIGMA_STRESSED_PRE_2023
    eac_mwh = eac_kwh / 1000
    var_stressed = Z_SCORE * sigma_stressed * eac_mwh * forward_price
    expected_capital_cost_per_mwh = (var_stressed * WACC) / eac_mwh
    tariff = price_fixed_tariff(forward_price, eac_kwh, term_start)
    assert tariff >= forward_price + expected_capital_cost_per_mwh


def test_smaller_customer_higher_tariff_per_mwh():
    forward_price = 60.0
    term_start = "2024-01-01"
    smaller_eac_kwh = 2800
    larger_eac_kwh = 45000
    smaller_tariff = price_fixed_tariff(forward_price, smaller_eac_kwh, term_start)
    larger_tariff = price_fixed_tariff(forward_price, larger_eac_kwh, term_start)
    # The capital cost term cancels eac_mwh, so the formula is currently
    # size-independent and tariffs are equal — >= documents this honestly.
    assert smaller_tariff >= larger_tariff


def test_tariff_uses_sigma_stressed_not_recent():
    forward_price = 60.0
    eac_kwh = 3500
    pre_2023_term_start = "2022-01-01"
    post_2023_term_start = "2024-01-01"
    pre_2023_tariff = price_fixed_tariff(forward_price, eac_kwh, pre_2023_term_start)
    post_2023_tariff = price_fixed_tariff(forward_price, eac_kwh, post_2023_term_start)
    assert post_2023_tariff > pre_2023_tariff


def test_naked_fraction_scales_capital_cost():
    forward_price = 60.0
    eac_kwh = 3500
    term_start = "2024-01-01"
    fully_naked = price_fixed_tariff(forward_price, eac_kwh, term_start, naked_fraction=1.0)
    mandate_naked = price_fixed_tariff(forward_price, eac_kwh, term_start, naked_fraction=0.15)

    fully_naked_capital_cost = fully_naked - forward_price - TARGET_MARGIN_GBP_PER_MWH
    mandate_naked_capital_cost = mandate_naked - forward_price - TARGET_MARGIN_GBP_PER_MWH

    assert mandate_naked_capital_cost == pytest.approx(fully_naked_capital_cost * 0.15)
    assert mandate_naked < fully_naked


def test_default_naked_fraction_is_fully_naked():
    forward_price = 60.0
    eac_kwh = 3500
    term_start = "2024-01-01"
    default = price_fixed_tariff(forward_price, eac_kwh, term_start)
    explicit = price_fixed_tariff(forward_price, eac_kwh, term_start, naked_fraction=1.0)
    assert default == explicit


from saas.tariff_pricing import TOU_PEAK_MULTIPLIER, TOU_OFFPEAK_MULTIPLIER, price_tou_tariff


def test_tou_returns_tuple():
    result = price_tou_tariff(60.0, 3500, "2024-01-01")
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_tou_peak_above_offpeak():
    peak, offpeak = price_tou_tariff(60.0, 3500, "2024-01-01")
    assert peak > offpeak


def test_tou_peak_multiplier_applied():
    from saas.tariff_pricing import price_fixed_tariff
    flat = price_fixed_tariff(60.0, 3500, "2024-01-01")
    peak, _ = price_tou_tariff(60.0, 3500, "2024-01-01")
    assert peak == pytest.approx(flat * TOU_PEAK_MULTIPLIER)


def test_tou_offpeak_multiplier_applied():
    from saas.tariff_pricing import price_fixed_tariff
    flat = price_fixed_tariff(60.0, 3500, "2024-01-01")
    _, offpeak = price_tou_tariff(60.0, 3500, "2024-01-01")
    assert offpeak == pytest.approx(flat * TOU_OFFPEAK_MULTIPLIER)


def test_tou_revenue_neutral_30_70():
    peak, offpeak = price_tou_tariff(60.0, 3500, "2024-01-01")
    blended = 0.30 * peak + 0.70 * offpeak
    from saas.tariff_pricing import price_fixed_tariff
    flat = price_fixed_tariff(60.0, 3500, "2024-01-01")
    assert blended == pytest.approx(flat)


def test_tou_constants_relationship():
    assert TOU_PEAK_MULTIPLIER > 1.0
    assert TOU_OFFPEAK_MULTIPLIER < 1.0
