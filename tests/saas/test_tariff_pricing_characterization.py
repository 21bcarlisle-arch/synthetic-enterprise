"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: saas/tariff_pricing.py — the fixed and Time-of-Use unit rates a domestic
customer is actually charged. Highest static in-degree of any remaining money
module in this codebase: the price every simulated household pays comes through
these two functions.

All inputs are fixed literals. `term_start` is passed explicitly as a string, so
there is no wall-clock read — but see the string-comparison tests below for what
that comparison does with input it does not expect.
"""
from __future__ import annotations

import datetime as dt

import pytest

from saas.tariff_pricing import (
    DEFAULT_NAKED_FRACTION,
    SIGMA_STRESSED_POST_2023,
    SIGMA_STRESSED_PRE_2023,
    TARGET_MARGIN_GBP_PER_MWH,
    TOU_OFFPEAK_MULTIPLIER,
    TOU_PEAK_MULTIPLIER,
    WACC,
    Z_SCORE,
    price_fixed_tariff,
    price_tou_tariff,
)

# A fixed, typical domestic customer: 3,100 kWh EAC on a £100/MWh forward.
EAC = 3100
FWD = 100.0


# ---------------------------------------------------------------------------
# price_fixed_tariff — the additive build-up
# ---------------------------------------------------------------------------


def test_the_six_components_are_a_plain_addition():
    rate = price_fixed_tariff(
        FWD, EAC, "2024-01-01",
        naked_fraction=0.15,
        policy_cost_per_mwh=25.0,
        network_cost_per_mwh=40.0,
        profitability_uplift_per_mwh=3.0,
    )
    # capital = Z x sigma x WACC x naked_fraction x forward = 1.645x1.5x0.10x0.15x100
    assert rate == pytest.approx(100.0 + 3.70125 + 2.0 + 25.0 + 40.0 + 3.0)


def test_the_capital_charge_is_independent_of_customer_size():
    # eac_mwh cancels out of the capital term, as the docstring states: a
    # 1,000 kWh flat and a 100,000 kWh mansion pay the same £/MWh.
    small = price_fixed_tariff(FWD, 1_000, "2024-01-01")
    large = price_fixed_tariff(FWD, 100_000, "2024-01-01")
    assert small == large


def test_the_sigma_step_at_the_start_of_2023():
    pre = price_fixed_tariff(FWD, EAC, "2022-12-31")
    post = price_fixed_tariff(FWD, EAC, "2023-01-01")
    assert pre == pytest.approx(100.0 + Z_SCORE * 0.50 * WACC * 100.0 + 2.0)
    assert post == pytest.approx(100.0 + Z_SCORE * 1.50 * WACC * 100.0 + 2.0)
    assert post - pre == pytest.approx(16.45)


def test_the_default_naked_fraction_prices_capital_on_the_whole_book():
    # SURPRISE (recorded, and flagged in the module's own docstring): the default
    # is 1.0 — capital cost priced as if NONE of the volume were hedged — while
    # the hedging mandate floors hedging at 85%. A caller that forgets the
    # argument charges 6.7x the capital component the company actually incurs:
    # £24.68/MWh instead of £3.70/MWh, on a £100/MWh forward.
    assert DEFAULT_NAKED_FRACTION == 1.0
    default = price_fixed_tariff(FWD, EAC, "2024-01-01")
    mandated = price_fixed_tariff(FWD, EAC, "2024-01-01", naked_fraction=0.15)
    assert default - FWD - TARGET_MARGIN_GBP_PER_MWH == pytest.approx(24.675)
    assert mandated - FWD - TARGET_MARGIN_GBP_PER_MWH == pytest.approx(3.70125)


def test_a_zero_eac_customer_raises_zero_division_rather_than_pricing():
    # DELIBERATELY CORRUPT INPUT: a customer whose Expected Annual Consumption is
    # zero — a real state for a new/vacant property. SURPRISE: the capital term
    # divides by eac_mwh, so this raises ZeroDivisionError instead of returning
    # the forward + margin. The pricing call is not guarded at the entry point.
    with pytest.raises(ZeroDivisionError):
        price_fixed_tariff(FWD, 0, "2024-01-01")


def test_a_negative_eac_prices_normally_because_the_size_term_cancels():
    # SURPRISE: a negative EAC is arithmetically invisible — eac_mwh cancels, so
    # a customer with -3,100 kWh EAC is priced identically to a valid one. There
    # is no validation to catch a sign error upstream.
    assert price_fixed_tariff(FWD, -EAC, "2024-01-01") == price_fixed_tariff(FWD, EAC, "2024-01-01")


def test_the_2023_sigma_step_is_a_raw_string_comparison():
    # `term_start >= "2023-01-01"` compares strings, not dates.
    assert price_fixed_tariff(FWD, EAC, "2023-1-1") == price_fixed_tariff(FWD, EAC, "2023-01-01")


def test_an_empty_or_short_term_start_silently_takes_the_lower_pre_2023_sigma():
    # DELIBERATELY CORRUPT INPUT. SURPRISE (fail-open): "" and "2023" both sort
    # BELOW "2023-01-01", so a missing or truncated term start prices the
    # customer at the pre-2023 regulatory floor — the CHEAPER capital charge —
    # with no error. Malformed input systematically under-prices risk.
    cheap = price_fixed_tariff(FWD, EAC, "2022-12-31")
    assert price_fixed_tariff(FWD, EAC, "") == cheap
    assert price_fixed_tariff(FWD, EAC, "2023") == cheap


def test_a_date_object_term_start_raises_typeerror():
    # DELIBERATELY CORRUPT INPUT: the natural thing a caller holding a real date
    # would pass. str >= date is a TypeError, so this one fails loudly.
    with pytest.raises(TypeError):
        price_fixed_tariff(FWD, EAC, dt.date(2024, 1, 1))


def test_a_negative_forward_price_produces_a_negative_capital_charge():
    # DELIBERATELY CORRUPT INPUT: GB wholesale prices really do go negative.
    # SURPRISE: the capital charge is proportional to the forward price with no
    # floor, so a -£50/MWh forward yields a NEGATIVE capital cost — the collateral
    # charge becomes a discount — and the customer is priced at -£60.34/MWh.
    rate = price_fixed_tariff(-50.0, EAC, "2024-01-01")
    assert rate == pytest.approx(-50.0 - 12.3375 + 2.0)


def test_a_naked_fraction_above_one_is_accepted_and_scales_the_charge():
    # Nothing bounds naked_fraction to [0, 1]. At 2.0 the customer is charged
    # collateral on twice the volume they consume.
    assert price_fixed_tariff(FWD, EAC, "2024-01-01", naked_fraction=2.0) == pytest.approx(
        100.0 + 49.35 + 2.0
    )


def test_a_fully_hedged_book_still_pays_the_flat_margin():
    assert price_fixed_tariff(FWD, EAC, "2024-01-01", naked_fraction=0.0) == pytest.approx(102.0)


def test_pass_through_costs_default_to_zero_so_omitting_them_silently_drops_them():
    # SURPRISE: policy and network costs default to 0.0. A caller that forgets
    # them prices a customer with no RO/CfD levy and no DUoS/TNUoS recovery at
    # all — roughly £65/MWh of real cost — and the result is a valid-looking rate
    # with no indication anything is missing.
    assert price_fixed_tariff(FWD, EAC, "2024-01-01") == pytest.approx(
        price_fixed_tariff(FWD, EAC, "2024-01-01", policy_cost_per_mwh=0.0,
                           network_cost_per_mwh=0.0)
    )


def test_the_margin_is_flat_pounds_per_mwh_not_a_percentage():
    # £2/MWh on a £100 forward is 2%; on a £600 crisis forward it is 0.33%. The
    # target margin does not scale with the cost being carried.
    calm = price_fixed_tariff(100.0, EAC, "2024-01-01", naked_fraction=0.15)
    crisis = price_fixed_tariff(600.0, EAC, "2024-01-01", naked_fraction=0.15)
    assert TARGET_MARGIN_GBP_PER_MWH == 2.00
    assert calm - 100.0 - 3.70125 == pytest.approx(2.0)
    assert crisis - 600.0 - 22.2075 == pytest.approx(2.0)


def test_the_pricing_constants_are_the_documented_values():
    assert (WACC, Z_SCORE) == (0.10, 1.645)
    assert (SIGMA_STRESSED_PRE_2023, SIGMA_STRESSED_POST_2023) == (0.50, 1.50)


# ---------------------------------------------------------------------------
# price_tou_tariff
# ---------------------------------------------------------------------------


def test_tou_splits_the_flat_rate_by_the_two_multipliers():
    flat = price_fixed_tariff(FWD, EAC, "2024-01-01", naked_fraction=0.15)
    peak, offpeak = price_tou_tariff(FWD, EAC, "2024-01-01", naked_fraction=0.15)
    assert peak == pytest.approx(flat * 1.50)
    assert offpeak == pytest.approx(flat * TOU_OFFPEAK_MULTIPLIER)
    assert TOU_OFFPEAK_MULTIPLIER == pytest.approx(0.7857142857)


def test_the_revenue_neutrality_claim_holds_exactly_at_the_thirty_seventy_split():
    # A control that DOES hold: at the stated 30/70 peak/off-peak consumption
    # split, ToU revenue equals flat revenue to floating-point precision.
    flat = price_fixed_tariff(FWD, EAC, "2024-01-01", naked_fraction=0.15)
    peak, offpeak = price_tou_tariff(FWD, EAC, "2024-01-01", naked_fraction=0.15)
    assert 0.30 * peak + 0.70 * offpeak == pytest.approx(flat)
    assert 0.30 * TOU_PEAK_MULTIPLIER + 0.70 * TOU_OFFPEAK_MULTIPLIER == pytest.approx(1.0)


def test_neutrality_is_only_at_that_one_split_and_a_peaky_customer_pays_more():
    # The neutrality is an assumption about the customer, not a property of the
    # tariff: a 50/50 customer pays 10.7% more than the flat rate.
    flat = price_fixed_tariff(FWD, EAC, "2024-01-01", naked_fraction=0.15)
    peak, offpeak = price_tou_tariff(FWD, EAC, "2024-01-01", naked_fraction=0.15)
    assert (0.50 * peak + 0.50 * offpeak) / flat == pytest.approx(1.1428571, abs=1e-6)
    assert (0.10 * peak + 0.90 * offpeak) / flat == pytest.approx(0.8571428, abs=1e-6)


def test_a_tou_customer_structurally_cannot_be_charged_policy_or_network_costs():
    # SURPRISE, and the largest money finding in this module: price_tou_tariff
    # takes no policy_cost_per_mwh, network_cost_per_mwh or
    # profitability_uplift_per_mwh, and passes none to price_fixed_tariff. Every
    # smart-meter ToU customer is therefore priced with ZERO RO/CfD levy, ZERO
    # DUoS/TNUoS recovery and no net-negative-account repricing — there is no
    # argument a caller could pass to include them. The omission is in the
    # signature, not in any caller.
    peak, offpeak = price_tou_tariff(FWD, EAC, "2024-01-01", naked_fraction=0.15)
    bare_flat = price_fixed_tariff(FWD, EAC, "2024-01-01", naked_fraction=0.15)
    with_pass_through = price_fixed_tariff(
        FWD, EAC, "2024-01-01", naked_fraction=0.15,
        policy_cost_per_mwh=25.0, network_cost_per_mwh=40.0,
    )
    assert peak == pytest.approx(bare_flat * TOU_PEAK_MULTIPLIER)
    assert peak != pytest.approx(with_pass_through * TOU_PEAK_MULTIPLIER)
    assert with_pass_through - bare_flat == pytest.approx(65.0)


def test_tou_inherits_the_zero_eac_crash():
    with pytest.raises(ZeroDivisionError):
        price_tou_tariff(FWD, 0, "2024-01-01")


def test_tou_returns_a_plain_tuple_in_peak_then_offpeak_order():
    result = price_tou_tariff(FWD, EAC, "2024-01-01")
    assert isinstance(result, tuple) and len(result) == 2
    assert result[0] > result[1]
