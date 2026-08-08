"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/pricing/tariff_engine.py — the company's own forward price
estimate, built from observable spot history, and the portfolio learning
premium. Everything the company charges for a fixed-term contract starts here.

All price series are constructed deterministically from literals (no RNG is
drawn anywhere in this file, and the module draws none either) and every
delivery date is a literal. The module reads no wall clock: `delivery_date` is
always supplied, so there is no time-dependent path to work around.
"""
from __future__ import annotations

import datetime as dt
from datetime import date, timedelta

import pytest

from company.pricing.tariff_engine import (
    ADAPTIVE_LOOKBACK_MAX,
    ADAPTIVE_LOOKBACK_MIN,
    COMPANY_LOOKBACK_DAYS,
    COMPANY_RISK_PREMIUM_FRACTION,
    GAS_RISK_PREMIUM_FRACTION,
    MIN_RECORDS_FOR_ESTIMATE,
    PORTFOLIO_PREMIUM_MAX,
    PORTFOLIO_PREMIUM_MIN,
    PORTFOLIO_TARGET_MARGIN_RATE,
    TERM_LENGTH_PREMIUM_PCT_PER_YEAR,
    CompanyTariffEngine,
    _compute_adaptive_lookback,
    _compute_ewma,
    _compute_regime_premium,
    _daily_means_for_window,
    _estimate_term_structure_slope,
    compute_portfolio_premium,
)

DELIVERY = "2024-01-15"          # a WINTER delivery month
SUMMER_DELIVERY = "2024-07-15"   # an off-peak delivery month


def flat_series(delivery: str = DELIVERY, days: int = 200, price: float = 100.0):
    """One record per day for `days` days ending the day before delivery."""
    end = date.fromisoformat(delivery) - timedelta(days=1)
    return [
        {"settlementDate": (end - timedelta(days=i)).isoformat(), "systemSellPrice": price}
        for i in range(days)
    ]


def series_from(delivery: str, prices_by_offset: dict[int, float], days: int = 200,
                default: float = 100.0):
    """Series where offset 1 = the day before delivery, 2 = two days before, ..."""
    end = date.fromisoformat(delivery)
    return [
        {
            "settlementDate": (end - timedelta(days=i)).isoformat(),
            "systemSellPrice": prices_by_offset.get(i, default),
        }
        for i in range(1, days + 1)
    ]


ENGINE = CompanyTariffEngine()


def price(fuel="electricity", delivery=DELIVERY, records=None, **kw):
    kw.setdefault("seasonal", False)
    kw.setdefault("adaptive_lookback", False)
    kw.setdefault("regime_detect", False)
    return ENGINE.get_forward_price(
        fuel, delivery, flat_series(delivery) if records is None else records, **kw
    )


# ---------------------------------------------------------------------------
# _compute_ewma and _daily_means_for_window
# ---------------------------------------------------------------------------


def test_ewma_of_a_flat_series_is_that_flat_value():
    assert _compute_ewma([100.0] * 50) == pytest.approx(100.0)


def test_ewma_of_an_empty_series_is_zero_not_an_error():
    # SURPRISE (fail-open shape): no data yields a price of £0.00/MWh rather than
    # None or an exception. Callers that reach the EWMA directly get a valid-
    # looking free-energy price; `get_forward_price` is protected only by its own
    # separate MIN_RECORDS guard.
    assert _compute_ewma([]) == 0.0


def test_ewma_weights_the_last_value_most_and_the_seed_is_the_first_value():
    # A single step from 100 to 200 on the last day moves the EWMA by alpha.
    alpha = 1.0 - 0.5 ** (1.0 / 30)
    assert _compute_ewma([100.0] * 29 + [200.0]) == pytest.approx(100.0 + 100.0 * alpha)
    assert _compute_ewma([100.0]) == 100.0


def test_daily_means_average_multiple_settlement_periods_on_one_day():
    records = [
        {"settlementDate": "2024-01-01", "systemSellPrice": 80.0},
        {"settlementDate": "2024-01-01", "systemSellPrice": 120.0},
        {"settlementDate": "2024-01-02", "systemSellPrice": 50.0},
    ]
    means = _daily_means_for_window(records, date(2024, 1, 1), date(2024, 1, 2))
    assert means == [100.0, 50.0]


def test_daily_means_preserves_first_seen_order_not_chronological_order():
    # SURPRISE: `_daily_means_for_window` returns dict-insertion order — the order
    # the records happened to arrive in — while `_estimate_term_structure_slope`
    # sorts before averaging and `get_forward_price` sorts too. The one consumer
    # that does NOT sort is `_compute_adaptive_lookback`... which only takes a
    # standard deviation, so the ordering is invisible there today. Frozen
    # because feeding these means to any order-sensitive statistic would be wrong.
    records = [
        {"settlementDate": "2024-01-05", "systemSellPrice": 50.0},
        {"settlementDate": "2024-01-01", "systemSellPrice": 100.0},
    ]
    assert _daily_means_for_window(records, date(2024, 1, 1), date(2024, 1, 5)) == [50.0, 100.0]


# ---------------------------------------------------------------------------
# get_forward_price — the base path
# ---------------------------------------------------------------------------


def test_a_flat_hundred_pound_market_prices_at_the_risk_premium():
    assert price() == pytest.approx(108.0)
    assert COMPANY_RISK_PREMIUM_FRACTION == 0.08


def test_gas_takes_the_lower_gas_risk_premium_by_default():
    assert price(fuel="gas") == pytest.approx(105.0)
    assert GAS_RISK_PREMIUM_FRACTION == 0.05


def test_an_unrecognised_fuel_string_is_priced_as_electricity_without_seasonality():
    # DELIBERATELY CORRUPT INPUT. SURPRISE (the same fail-open, case-sensitive
    # fuel-matching class found in ofgem_price_cap last pass): the risk premium
    # is chosen by `if fuel == "gas" else electricity`, so "Gas", "GAS" and
    # "natural_gas" all take the ELECTRICITY premium; the seasonal block matches
    # "electricity"/"gas" exactly, so those same strings get NO seasonal
    # adjustment at all. A capitalisation slip silently reprices a winter gas
    # contract from £120.75 to £108.00/MWh — a 10.6% under-price — with no error.
    winter_gas = price(fuel="gas", seasonal=True)
    mistyped = price(fuel="Gas", seasonal=True)
    assert winter_gas == pytest.approx(120.75)
    assert mistyped == pytest.approx(108.0)
    assert price(fuel="", seasonal=True) == pytest.approx(108.0)


def test_the_point_in_time_window_excludes_the_delivery_date_itself():
    # The last usable record is the day before delivery; a record dated ON the
    # delivery date is outside the window. Removing the pre-delivery day changes
    # the answer, proving the boundary is exercised.
    records = series_from(DELIVERY, {1: 1_000.0})
    assert price(records=records) > 108.0
    with_future = records + [{"settlementDate": DELIVERY, "systemSellPrice": 99_999.0}]
    assert price(records=with_future) == pytest.approx(price(records=records))


def test_records_older_than_the_lookback_window_are_excluded():
    stale = series_from(DELIVERY, {150: 99_999.0})  # 150 days back, lookback is 120
    assert price(records=stale) == pytest.approx(108.0)


def test_too_few_records_raises_with_the_count_in_the_message():
    short = flat_series(days=29)
    with pytest.raises(ValueError, match="found 29, need at least 30"):
        price(records=short)
    assert MIN_RECORDS_FOR_ESTIMATE == 30


def test_the_minimum_records_guard_counts_ROWS_not_DAYS():
    # DELIBERATELY CORRUPT INPUT: 30 half-hourly settlement periods from a SINGLE
    # day. SURPRISE: the guard is `len(filtered) < 30` over raw records, so one
    # day of half-hourly data satisfies a check whose purpose is to refuse
    # pricing on thin history. The engine then reports a "120-day rolling
    # estimate" built from 12 hours of one day, with no signal that it did.
    one_day = [
        {"settlementDate": "2024-01-14", "systemSellPrice": 500.0} for _ in range(30)
    ]
    assert price(records=one_day) == pytest.approx(540.0)


def test_an_empty_price_history_raises_rather_than_pricing_at_zero():
    with pytest.raises(ValueError):
        price(records=[])


# ---------------------------------------------------------------------------
# Seasonality
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fuel,delivery,expected",
    [
        ("electricity", "2024-01-15", 116.64),   # winter: 100 x 1.08 x 1.08
        ("electricity", "2024-07-15", 103.68),   # summer: 100 x 0.96 x 1.08
        ("gas", "2024-01-15", 120.75),           # winter: 100 x 1.15 x 1.05
        ("gas", "2024-07-15", 96.60),            # summer: 100 x 0.92 x 1.05
    ],
)
def test_seasonal_shape_is_applied_from_the_delivery_month(fuel, delivery, expected):
    assert price(fuel=fuel, delivery=delivery, seasonal=True) == pytest.approx(expected)


def test_the_season_is_decided_by_the_contract_start_month_alone():
    # SURPRISE: a 12-month contract starting in October is priced entirely at the
    # WINTER uplift, and one starting in April entirely at the SUMMER discount,
    # even though both deliver across every season. `term_months` scales the term
    # premium but never the seasonal shape, so a full-year deal's seasonality is
    # decided by which month it happens to begin. Two identical annual contracts
    # six months apart differ by 12.5% on this factor alone.
    oct_start = price(delivery="2024-10-01", records=flat_series("2024-10-01"),
                      seasonal=True, term_months=12)
    apr_start = price(delivery="2024-04-01", records=flat_series("2024-04-01"),
                      seasonal=True, term_months=12)
    assert oct_start == pytest.approx(116.64)
    assert apr_start == pytest.approx(103.68)


def test_march_is_winter_and_april_is_summer_at_the_boundary():
    assert price(delivery="2024-03-31", records=flat_series("2024-03-31"),
                 seasonal=True) == pytest.approx(116.64)
    assert price(delivery="2024-04-01", records=flat_series("2024-04-01"),
                 seasonal=True) == pytest.approx(103.68)


# ---------------------------------------------------------------------------
# Term length and the dynamic slope
# ---------------------------------------------------------------------------


def test_the_structural_term_premium_is_two_percent_per_year_beyond_twelve_months():
    assert price(term_months=24) == pytest.approx(110.0)   # 100 x (1 + 0.08 + 0.02)
    assert price(term_months=36) == pytest.approx(112.0)
    assert TERM_LENGTH_PREMIUM_PCT_PER_YEAR == 0.02


def test_a_contract_shorter_than_a_year_gets_no_discount_only_no_premium():
    # SURPRISE: the structural term premium is floored at zero, so a 1-month deal
    # and a 12-month deal price identically. The stated rationale (longer deals
    # carry more price risk) implies the converse should be cheaper; it is not.
    assert price(term_months=1) == pytest.approx(price(term_months=12)) == pytest.approx(108.0)


def test_the_slope_is_zero_on_a_flat_market_and_needs_fifteen_days_per_window():
    assert _estimate_term_structure_slope(DELIVERY, flat_series()) == 0.0
    assert _estimate_term_structure_slope(DELIVERY, flat_series(days=40)) == 0.0  # long window short


def test_a_rising_market_produces_a_capped_contango_slope():
    # Last 30 days at £200, the prior 60 at £100: the raw annualised slope is far
    # beyond the cap, so it pins at +15%/year.
    rising = series_from(DELIVERY, {i: 200.0 for i in range(1, 31)})
    assert _estimate_term_structure_slope(DELIVERY, rising) == pytest.approx(0.15)
    # ...and a falling market pins at the asymmetric -8% floor.
    falling = series_from(DELIVERY, {i: 50.0 for i in range(1, 31)})
    assert _estimate_term_structure_slope(DELIVERY, falling) == pytest.approx(-0.08)


def test_the_slope_premium_scales_with_tenor_so_a_two_year_deal_doubles_it():
    rising = series_from(DELIVERY, {i: 200.0 for i in range(1, 31)})
    one_year = price(records=rising, term_months=12)
    two_year = price(records=rising, term_months=24)
    # base EWMA of the mixed series, then (1 + 0.08 + term + slope x tenor)
    assert two_year / one_year == pytest.approx(
        (1 + 0.08 + 0.02 + 0.15 * 2) / (1 + 0.08 + 0.15), rel=1e-9
    )


def test_a_zero_or_negative_long_ewma_disables_the_slope_silently():
    # DELIBERATELY CORRUPT INPUT: a sustained negative-price baseline (which GB
    # electricity really does produce). The slope returns 0.0 rather than
    # inverting — a guard, but a silent one: the caller cannot tell "flat market"
    # from "the slope calculation refused to run".
    negative_baseline = series_from(DELIVERY, {i: -50.0 for i in range(31, 200)})
    assert _estimate_term_structure_slope(DELIVERY, negative_baseline) == 0.0


# ---------------------------------------------------------------------------
# Regime premium
# ---------------------------------------------------------------------------


def test_the_regime_premium_is_zero_on_a_flat_market():
    assert _compute_regime_premium(DELIVERY, flat_series()) == 0.0


def test_the_long_regime_window_CONTAINS_the_short_one_damping_the_ratio():
    # SURPRISE: `_compute_regime_premium` builds long_means over
    # long_start..end_date — the SAME end date as the short window — so the
    # "baseline" includes the very period it is being compared against. The
    # sibling `_estimate_term_structure_slope` in this same module uses DISJOINT
    # windows (long_end = short_start - 1). Two functions, two conventions for
    # "short vs long". The overlap systematically understates the divergence: a
    # market that doubled for 60 days scores a ratio of 1.5, not 2.0.
    doubled = series_from(DELIVERY, {i: 200.0 for i in range(1, 61)})
    short_mean = 200.0
    long_mean = (60 * 200.0 + 120 * 100.0) / 180.0   # the short window is inside it
    assert long_mean == pytest.approx(133.333, abs=1e-3)
    expected = min(0.15, (short_mean / long_mean - 1.10) * 0.50)
    assert _compute_regime_premium(DELIVERY, doubled) == pytest.approx(expected)


def test_the_upward_premium_is_capped_at_fifteen_percent():
    spike = series_from(DELIVERY, {i: 10_000.0 for i in range(1, 61)})
    assert _compute_regime_premium(DELIVERY, spike) == pytest.approx(0.15)


def test_the_downward_discount_is_capped_at_five_percent_and_is_asymmetric():
    crash = series_from(DELIVERY, {i: 1.0 for i in range(1, 61)})
    assert _compute_regime_premium(DELIVERY, crash) == pytest.approx(-0.05)


def test_a_thin_history_disables_the_regime_premium_silently():
    assert _compute_regime_premium(DELIVERY, flat_series(days=19)) == 0.0


# ---------------------------------------------------------------------------
# Adaptive lookback
# ---------------------------------------------------------------------------


def test_a_zero_volatility_baseline_keeps_the_base_lookback():
    assert _compute_adaptive_lookback(DELIVERY, flat_series(), 120) == 120


def test_high_recent_volatility_shortens_the_lookback_to_the_floor():
    volatile = series_from(DELIVERY, {i: (500.0 if i % 2 else 50.0) for i in range(1, 31)},
                           default=100.0)
    # The prior window needs some spread of its own or the ratio is undefined.
    for r in volatile:
        d = date.fromisoformat(r["settlementDate"])
        if d <= date.fromisoformat(DELIVERY) - timedelta(days=31):
            r["systemSellPrice"] = 100.0 + (d.day % 5)
    assert _compute_adaptive_lookback(DELIVERY, volatile, 120) == ADAPTIVE_LOOKBACK_MIN


def test_a_calm_recent_window_extends_the_lookback_to_the_ceiling():
    calm_recent = series_from(DELIVERY, {}, default=100.0)
    for r in calm_recent:
        d = date.fromisoformat(r["settlementDate"])
        if d <= date.fromisoformat(DELIVERY) - timedelta(days=31):
            r["systemSellPrice"] = 100.0 + (d.day * 10)   # noisy baseline
    assert _compute_adaptive_lookback(DELIVERY, calm_recent, 120) == ADAPTIVE_LOOKBACK_MAX


def test_the_adaptive_lookback_is_bounded_both_ways():
    assert (ADAPTIVE_LOOKBACK_MIN, ADAPTIVE_LOOKBACK_MAX) == (30, 180)
    assert COMPANY_LOOKBACK_DAYS == 120


def test_adaptive_lookback_can_move_the_price_it_is_only_disabled_for_tests():
    # The default is ON in production (`ADAPTIVE_LOOKBACK_ENABLED = True`) and the
    # docstring tells callers to pass False "for deterministic tests" — recorded
    # because it means the shipped default path is the one least covered.
    volatile = series_from(DELIVERY, {i: (400.0 if i % 2 else 60.0) for i in range(1, 200)})
    on = ENGINE.get_forward_price("electricity", DELIVERY, volatile, seasonal=False,
                                  adaptive_lookback=True, regime_detect=False)
    off = ENGINE.get_forward_price("electricity", DELIVERY, volatile, seasonal=False,
                                   adaptive_lookback=False, regime_detect=False)
    assert on != pytest.approx(off)


# ---------------------------------------------------------------------------
# compute_portfolio_premium
# ---------------------------------------------------------------------------


def test_no_margin_history_means_no_adjustment():
    assert compute_portfolio_premium([]) == 0.0


def test_being_exactly_on_target_produces_no_adjustment():
    assert compute_portfolio_premium([PORTFOLIO_TARGET_MARGIN_RATE] * 4) == 0.0


def test_under_earning_lifts_the_premium_by_half_the_gap():
    # Target 8%, realised 2% → a 6-point gap → +3% surcharge.
    assert compute_portfolio_premium([0.02, 0.02, 0.02, 0.02]) == pytest.approx(0.03)


def test_over_earning_produces_a_discount_clamped_at_minus_five_percent():
    assert compute_portfolio_premium([0.14]) == pytest.approx(-0.03)
    assert compute_portfolio_premium([0.20]) == pytest.approx(PORTFOLIO_PREMIUM_MIN)
    assert compute_portfolio_premium([1.00]) == pytest.approx(PORTFOLIO_PREMIUM_MIN)


def test_a_catastrophic_loss_history_is_clamped_at_plus_fifteen_percent():
    assert compute_portfolio_premium([-5.0]) == pytest.approx(PORTFOLIO_PREMIUM_MAX)


def test_a_percentage_instead_of_a_fraction_is_silently_clamped_to_a_discount():
    # DELIBERATELY CORRUPT INPUT: margin rates handed over as PERCENTAGES (8.0)
    # rather than fractions (0.08) — the classic unit confusion at this seam.
    # SURPRISE: shortfall becomes -7.92, and the clamp turns it into the maximum
    # 5% DISCOUNT. A company hitting exactly its target margin would cut every
    # tariff by 5% and nothing would report an anomaly.
    assert compute_portfolio_premium([8.0, 8.0, 8.0, 8.0]) == pytest.approx(-0.05)


def test_the_premium_uses_an_unweighted_mean_so_one_outlier_term_dominates():
    # SURPRISE: no recency weighting and no trimming, despite
    # PORTFOLIO_PREMIUM_LOOKBACK documenting "the last N completed terms" — the
    # function never truncates the list either; it averages whatever it is given.
    assert compute_portfolio_premium([0.08, 0.08, 0.08, -1.0]) == pytest.approx(
        (0.08 - (0.08 * 3 - 1.0) / 4) * 0.5
    )


def test_the_portfolio_premium_is_never_applied_inside_get_forward_price():
    # SURPRISE: `compute_portfolio_premium` is a free function that
    # `CompanyTariffEngine.get_forward_price` never calls. The Phase 17a
    # "portfolio learning premium" only reaches a tariff if some caller
    # remembers to multiply it in; the engine's own output is unaffected.
    assert price() == pytest.approx(108.0)
    assert compute_portfolio_premium([-1.0]) == pytest.approx(PORTFOLIO_PREMIUM_MAX)


def test_the_engine_class_holds_no_state_between_calls():
    a, b = CompanyTariffEngine(), CompanyTariffEngine()
    records = flat_series()
    assert a.get_forward_price("electricity", DELIVERY, records, seasonal=False,
                               adaptive_lookback=False, regime_detect=False) == \
           b.get_forward_price("electricity", DELIVERY, records, seasonal=False,
                               adaptive_lookback=False, regime_detect=False)
    assert not vars(a)


def test_a_malformed_settlement_date_in_the_history_raises():
    # DELIBERATELY CORRUPT INPUT: one unparseable date among 200 good records
    # aborts the whole pricing call — there is no per-record guard.
    records = flat_series()
    records[5]["settlementDate"] = "15/01/2024"
    with pytest.raises(ValueError):
        price(records=records)


def test_a_missing_price_key_raises_a_keyerror_from_deep_in_the_windowing():
    records = flat_series()
    del records[5]["systemSellPrice"]
    with pytest.raises(KeyError):
        price(records=records)


def test_a_datetime_delivery_string_with_a_time_component_raises():
    # Python 3.11's fromisoformat accepts "2024-01-15T00:00:00" for date.
    # SURPRISE: it does NOT — date.fromisoformat rejects the time component here,
    # so a caller passing an ISO datetime gets a ValueError rather than the date.
    with pytest.raises(ValueError):
        price(delivery="2024-01-15T00:00:00", records=flat_series())


def test_the_documented_constants_are_the_shipped_values():
    assert (PORTFOLIO_TARGET_MARGIN_RATE, PORTFOLIO_PREMIUM_MIN, PORTFOLIO_PREMIUM_MAX) == (
        0.08, -0.05, 0.15,
    )
    assert isinstance(dt.date(2024, 1, 15), date)  # sanity: dates, not datetimes, throughout
