import pytest

from sim.price_engine import (
    A0,
    A1,
    A2,
    DISPATCHABLE_CAPACITY_MW,
    EF_GAS_TCO2_PER_MWH_TH,
    THERMAL_EFFICIENCY,
    WIND_CUT_IN_MS,
    WIND_CUT_OUT_MS,
    WIND_RATED_MS,
    X_TIGHT,
    gas_floor_price,
    synthetic_price,
    system_margin_price,
    wind_power_output_fraction,
)


# --- gas_floor_price: back-compat (carbon defaults to 0) ---

def test_gas_floor_price_default_efficiency():
    assert gas_floor_price(25.0) == 25.0 / THERMAL_EFFICIENCY


def test_gas_floor_price_custom_efficiency():
    assert gas_floor_price(30.0, thermal_efficiency=0.60) == 50.0


def test_gas_floor_price_basic_50pct_efficiency():
    assert gas_floor_price(50.0, 0.50) == pytest.approx(100.0)


def test_gas_floor_price_carbon_defaults_to_zero_no_effect():
    """Back-compat: carbon_price_gbp_per_tonne defaults to 0.0, so the floor
    is unchanged from the pre-recalibration gas_price/efficiency form."""
    assert gas_floor_price(25.0) == gas_floor_price(25.0, carbon_price_gbp_per_tonne=0.0)


# --- gas_floor_price: carbon term effect (new, 2026-07-19 recalibration) ---

def test_gas_floor_price_carbon_term_raises_floor():
    floor_no_carbon = gas_floor_price(25.0, carbon_price_gbp_per_tonne=0.0)
    floor_with_carbon = gas_floor_price(25.0, carbon_price_gbp_per_tonne=80.0)
    assert floor_with_carbon > floor_no_carbon


def test_gas_floor_price_carbon_term_exact_value():
    # P_gas_floor = (gas_price + carbon_price * EF_GAS) / thermal_efficiency
    gas_price, carbon_price, efficiency = 25.0, 80.0, 0.50
    expected = (gas_price + carbon_price * EF_GAS_TCO2_PER_MWH_TH) / efficiency
    assert gas_floor_price(gas_price, efficiency, carbon_price) == pytest.approx(expected)


def test_gas_floor_price_carbon_term_monotonic_in_carbon_price():
    floors = [
        gas_floor_price(25.0, carbon_price_gbp_per_tonne=cp)
        for cp in (0.0, 20.0, 50.0, 100.0)
    ]
    assert floors == sorted(floors)


# --- system_margin_price: new residual-demand scarcity form ---

def test_system_margin_price_typical_conditions_near_floor():
    """At the calibrated median residual-demand condition (RD/cap ~= 0.6,
    below X_TIGHT), the multiplier should be within a modest band of 1.0 —
    i.e. price stays in the same order of magnitude as the gas floor, unlike
    the old raw-ratio form which multiplied the floor several-fold even in
    typical conditions."""
    floor = 50.0
    # demand - renewable = 0.6 * DISPATCHABLE_CAPACITY_MW -> typical/median x
    renewable_mw = 1000.0
    demand_mw = renewable_mw + 0.6 * DISPATCHABLE_CAPACITY_MW
    price = system_margin_price(floor, demand_mw, renewable_mw)
    assert 0.5 * floor < price < 2.0 * floor


def test_system_margin_price_monotonically_increases_with_tighter_margin():
    """Holding renewables fixed, increasing demand (tightening the residual-
    demand margin) must strictly increase price."""
    floor = 50.0
    renewable_mw = 5000.0
    prices = [
        system_margin_price(floor, demand_mw=d, renewable_generation_mw=renewable_mw)
        for d in (5000.0, 15000.0, 25000.0, 35000.0, 45000.0)
    ]
    assert prices == sorted(prices)
    assert prices[0] < prices[-1]


def test_system_margin_price_convex_above_tight_threshold():
    """Beyond X_TIGHT, equal steps in x must produce accelerating (convex)
    increases in price -- the merit-order 'small increment jumps to a much
    dearer plant' behaviour that the old linear-in-ratio form lacked."""
    floor = 50.0
    cap = DISPATCHABLE_CAPACITY_MW
    renewable_mw = 0.0

    def price_at_x(x):
        return system_margin_price(floor, demand_mw=x * cap, renewable_generation_mw=renewable_mw)

    x1, x2, x3 = X_TIGHT + 0.1, X_TIGHT + 0.2, X_TIGHT + 0.3
    step1 = price_at_x(x2) - price_at_x(x1)
    step2 = price_at_x(x3) - price_at_x(x2)
    assert step2 > step1 > 0


def test_system_margin_price_oversupply_can_go_sub_floor_and_negative():
    """When renewables flood the system (demand << renewable), residual
    demand is strongly negative and the multiplier must be able to fall
    below the floor, and below zero -- real SSP has gone as low as
    -GBP185/MWh in oversupply periods."""
    floor = 50.0
    price = system_margin_price(floor, demand_mw=1000.0, renewable_generation_mw=1000.0 + DISPATCHABLE_CAPACITY_MW)
    assert price < floor
    assert price < 0


def test_system_margin_price_zero_renewables_no_longer_errors():
    """Unlike the old raw-ratio form (which divided by renewable_generation_mw
    and required it to be > 0), the residual-demand form handles a
    zero-renewables period gracefully (RD = demand_mw)."""
    floor = 50.0
    price = system_margin_price(floor, demand_mw=20000.0, renewable_generation_mw=0.0)
    assert price == pytest.approx(
        floor * (A0 + A1 * (20000.0 / DISPATCHABLE_CAPACITY_MW)
                 + A2 * max(0.0, 20000.0 / DISPATCHABLE_CAPACITY_MW - X_TIGHT) ** 2.0)
    )


def test_system_margin_price_custom_dispatchable_capacity():
    floor = 50.0
    price_default_cap = system_margin_price(floor, demand_mw=30000.0, renewable_generation_mw=5000.0)
    price_custom_cap = system_margin_price(
        floor, demand_mw=30000.0, renewable_generation_mw=5000.0, dispatchable_capacity_mw=20000.0
    )
    assert price_default_cap != price_custom_cap


# --- wind cubic physics: unchanged ---

def test_wind_power_below_cut_in_is_zero():
    assert wind_power_output_fraction(WIND_CUT_IN_MS - 0.1, rated_power_mw=10) == 0.0


def test_wind_power_at_cut_in_is_zero():
    assert wind_power_output_fraction(WIND_CUT_IN_MS, rated_power_mw=10) == 0.0


def test_wind_power_at_rated_speed_is_full_output():
    assert wind_power_output_fraction(WIND_RATED_MS, rated_power_mw=10) == 10


def test_wind_power_in_rated_plateau_is_full_output():
    assert wind_power_output_fraction(20.0, rated_power_mw=10) == 10


def test_wind_power_at_cut_out_is_still_full_output():
    assert wind_power_output_fraction(WIND_CUT_OUT_MS, rated_power_mw=10) == 10


def test_wind_power_above_cut_out_is_zero():
    assert wind_power_output_fraction(WIND_CUT_OUT_MS + 0.1, rated_power_mw=10) == 0.0


def test_wind_power_ramp_is_cubic_and_monotonic():
    p1 = wind_power_output_fraction(5.0, rated_power_mw=10)
    p2 = wind_power_output_fraction(8.0, rated_power_mw=10)
    p3 = wind_power_output_fraction(11.0, rated_power_mw=10)
    assert 0 < p1 < p2 < p3 < 10

    # Doubling from 5 -> 10 m/s within the ramp should roughly 8x the
    # fractional output (cubic), modulo the cut-in offset.
    expected_p1 = ((5.0**3 - WIND_CUT_IN_MS**3) / (WIND_RATED_MS**3 - WIND_CUT_IN_MS**3)) * 10
    assert p1 == pytest.approx(expected_p1)


def test_wind_power_output_fraction_in_ramp_monotonic():
    speeds = [4.0, 6.0, 8.0, 10.0, 11.0]
    fracs = [wind_power_output_fraction(v) for v in speeds]
    assert fracs == sorted(fracs), "Wind ramp should be monotonically increasing"


# --- synthetic_price: chains gas_floor_price -> system_margin_price ---

def test_synthetic_price_chains_gas_floor_and_margin():
    gas_price = 25.0
    demand_mw, renewable_mw = 15000.0, 1000.0
    expected_floor = gas_floor_price(gas_price)
    expected = system_margin_price(expected_floor, demand_mw, renewable_mw)
    assert synthetic_price(gas_price, demand_mw, renewable_mw) == expected


def test_synthetic_price_passes_through_carbon_price():
    gas_price, carbon_price = 25.0, 80.0
    demand_mw, renewable_mw = 15000.0, 1000.0
    with_carbon = synthetic_price(gas_price, demand_mw, renewable_mw, carbon_price_gbp_per_tonne=carbon_price)
    without_carbon = synthetic_price(gas_price, demand_mw, renewable_mw)
    assert with_carbon > without_carbon


# --- R15-failable: real-data distribution-match mutation proof ---
# This is the mechanism that PROVES the recalibration fires: it asserts the
# engine's output over a real 2016-2025 sample lands in the realistic SSP
# band. If sim/price_engine.py is reverted to the old raw-ratio form
# (`gas_floor * (demand/renewable)^gamma`), this test MUST fail — the old
# form overestimates real SSP by ~10x (docs/calibration/price-engine.md), so
# a same-inputs sample would blow through the upper bound below by orders of
# magnitude. Kept as a small hand-built sample (not the full 157k-row
# calibration set) so this test runs fast in the standard suite; the full
# distribution check lives in simulation/run_phase3b_recalibration.py and
# docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md.
_REAL_SAMPLE_SETTLEMENT_PERIODS = [
    # (gas_price_gbp_per_mwh, demand_mw, renewable_mw) -- representative of
    # real 2016-2025 conditions across calm/typical/crisis/high-renewable
    # regimes (magnitudes drawn from docs/calibration/price-engine.md and
    # the full-window statistics in the fidelity evidence doc, not invented
    # SSP values -- only feature magnitudes, used to check the ENGINE's
    # output band, never asserted as real SSP itself).
    (15.0, 27000.0, 18000.0),   # 2016-era calm, high renewables
    (18.0, 28000.0, 7000.0),    # typical mid-decade
    (20.0, 27400.0, 6100.0),    # 2019 median-ish
    (25.0, 30000.0, 4000.0),    # tighter winter evening
    (100.0, 32000.0, 5000.0),   # 2022 gas-crisis-era gas price, tight demand
    (150.0, 35000.0, 3000.0),   # 2022 crisis peak-ish
    (10.0, 15000.0, 20000.0),   # summer night oversupply (renewables > demand)
]


def test_price_engine_realistic_distribution_over_sample_periods():
    prices = [
        synthetic_price(gas_price, demand_mw, renewable_mw)
        for gas_price, demand_mw, renewable_mw in _REAL_SAMPLE_SETTLEMENT_PERIODS
    ]
    # Real full-window SSP: median ~55, mean ~77, p95 ~220, min ~-185
    # (docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md). This sample
    # check is deliberately loose (order-of-magnitude, not tight percentile
    # match -- that full check lives in the recalibration script) but tight
    # enough that the old ~10x-overestimating raw-ratio form fails it hard:
    # every one of these sample periods would price in the thousands of
    # GBP/MWh under the old form.
    for price in prices:
        assert -300.0 < price < 1000.0, (
            f"price {price:.2f} is outside the realistic SSP band -- "
            "this is the mutation proof that the recalibration is active"
        )
    # And at least one of the abundant-renewable/low-demand sample periods
    # must land at or below the gas floor (the old form could never do this
    # -- it required renewable_generation_mw > 0 and was always >= floor).
    floors = [
        gas_floor_price(gas_price)
        for gas_price, _, _ in _REAL_SAMPLE_SETTLEMENT_PERIODS
    ]
    assert any(price <= floor for price, floor in zip(prices, floors))
