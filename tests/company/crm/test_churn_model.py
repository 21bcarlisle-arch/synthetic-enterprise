"""Tests for company.crm.churn_model — observable-data churn estimator."""
import pytest

from company.crm.churn_model import (
    BASE_CHURN_RATE,
    BILL_STRESS_SENSITIVITY,
    BILL_STRESS_THRESHOLD_GBP,
    CRISIS_HANGOVER_BASE_UPLIFT,
    CRISIS_HANGOVER_WINDOW_PERIODS,
    GAS_BASE_CHURN_RATE,
    GAS_RATE_SENSITIVITY,
    HEDGE_SENSITIVITY_REDUCTION,
    IC_BASE_CHURN_RATE,
    IC_RATE_SENSITIVITY,
    MAX_CHURN_PROBABILITY,
    RATE_SENSITIVITY,
    TENURE_DISCOUNT_PER_YEAR,
    estimate_churn_probability,
)


def test_flat_rate_no_increase_returns_base_minus_tenure():
    """No rate change: probability = base - tenure_discount."""
    p = estimate_churn_probability(100.0, 100.0, tenure_years=2.0)
    expected = BASE_CHURN_RATE - TENURE_DISCOUNT_PER_YEAR * 2.0
    assert abs(p - expected) < 1e-9


def test_zero_tenure_flat_rate_returns_base():
    """Brand-new customer, no rate change: probability == base rate."""
    p = estimate_churn_probability(100.0, 100.0, tenure_years=0.0)
    assert abs(p - BASE_CHURN_RATE) < 1e-9


def test_rate_increase_raises_probability():
    """A 10% rate increase adds RATE_SENSITIVITY * 0.10 to base probability."""
    p = estimate_churn_probability(100.0, 110.0, tenure_years=0.0)
    expected = BASE_CHURN_RATE + RATE_SENSITIVITY * 0.10
    assert abs(p - expected) < 1e-9


def test_rate_decrease_lowers_probability():
    """A rate decrease can push probability well below base (floored at 0)."""
    p = estimate_churn_probability(110.0, 100.0, tenure_years=0.0)
    rate_change = (100.0 - 110.0) / 110.0  # ~-0.0909
    expected = max(0.0, BASE_CHURN_RATE + RATE_SENSITIVITY * rate_change)
    assert abs(p - expected) < 1e-9


def test_tenure_discount_caps_at_five_years():
    """Tenure discount stops accumulating after 5 years."""
    p_5yr = estimate_churn_probability(100.0, 100.0, tenure_years=5.0)
    p_10yr = estimate_churn_probability(100.0, 100.0, tenure_years=10.0)
    assert abs(p_5yr - p_10yr) < 1e-9


def test_crisis_rate_spike_approaches_max():
    """A massive rate spike (100% increase) should approach MAX_CHURN_PROBABILITY."""
    p = estimate_churn_probability(100.0, 200.0, tenure_years=0.0)
    # 0.10 + 0.8 * 1.0 = 0.90, well below cap
    assert p == pytest.approx(0.90)


def test_extreme_rate_spike_clamps_to_max():
    """Probability is clamped to MAX_CHURN_PROBABILITY regardless of rate spike."""
    p = estimate_churn_probability(100.0, 1000.0, tenure_years=0.0)
    assert p == MAX_CHURN_PROBABILITY


def test_probability_never_below_zero():
    """Probability is clamped at 0.0 even with rate cut + long tenure."""
    p = estimate_churn_probability(200.0, 100.0, tenure_years=5.0)
    assert p >= 0.0


def test_zero_old_rate_does_not_raise():
    """If old rate is 0 (bootstrap edge case), rate_increase_pct defaults to 0."""
    p = estimate_churn_probability(0.0, 100.0, tenure_years=0.0)
    assert p == pytest.approx(BASE_CHURN_RATE)


def test_output_is_float():
    p = estimate_churn_probability(100.0, 120.0, tenure_years=3.0)
    assert isinstance(p, float)


# ── Bill burden signal (Phase 13c) ───────────────────────────────────────────

def test_no_consumption_gives_no_bill_stress():
    """Default annual_consumption_kwh=0 means bill stress term is zero."""
    p_no_kwh = estimate_churn_probability(100.0, 100.0, tenure_years=0.0, annual_consumption_kwh=0.0)
    assert abs(p_no_kwh - BASE_CHURN_RATE) < 1e-9


def test_low_bill_below_threshold_gives_no_stress():
    """Bill below BILL_STRESS_THRESHOLD_GBP adds no stress term."""
    # £100/MWh × 2800 kWh / 1000 = £280/year << £3000 threshold
    p = estimate_churn_probability(100.0, 100.0, tenure_years=0.0, annual_consumption_kwh=2800.0)
    assert abs(p - BASE_CHURN_RATE) < 1e-9


def test_bill_exactly_at_threshold_gives_no_stress():
    """Bill exactly at threshold: max(0, 1-1) = 0, no stress added."""
    kwh = BILL_STRESS_THRESHOLD_GBP * 1000 / 100.0  # at £100/MWh, this is 30,000 kWh
    p = estimate_churn_probability(100.0, 100.0, tenure_years=0.0, annual_consumption_kwh=kwh)
    assert abs(p - BASE_CHURN_RATE) < 1e-9


def test_bill_above_threshold_adds_stress():
    """Bill above threshold raises churn probability."""
    # £100/MWh × 45,000 kWh = £4,500 bill (above £3,000)
    p_with = estimate_churn_probability(100.0, 100.0, tenure_years=0.0, annual_consumption_kwh=45000.0)
    p_without = estimate_churn_probability(100.0, 100.0, tenure_years=0.0, annual_consumption_kwh=0.0)
    assert p_with > p_without


def test_bill_stress_quantified():
    """Verify bill stress formula: SENSITIVITY × (bill/threshold - 1)."""
    # £250/MWh × 45,000 kWh / 1000 = £11,250 prev annual bill
    prev_bill = 250.0 * 45000.0 / 1000.0  # £11,250
    expected_stress = BILL_STRESS_SENSITIVITY * (prev_bill / BILL_STRESS_THRESHOLD_GBP - 1.0)
    # With flat rate (no rate increase), 5yr tenure
    p = estimate_churn_probability(250.0, 250.0, tenure_years=5.0, annual_consumption_kwh=45000.0)
    expected_p = max(0.0, min(MAX_CHURN_PROBABILITY,
        BASE_CHURN_RATE + 0.0 - TENURE_DISCOUNT_PER_YEAR * 5.0 + expected_stress))
    assert abs(p - expected_p) < 1e-9


def test_c6_scenario_falling_rate_high_consumption_detectable():
    """C6 churn failure mode: falling rate + large SME consumption → above 30% threshold.

    C6 in 2024: old_rate ~£250/MWh (crisis-era), new_rate ~£150/MWh (falling),
    45,000 kWh/year. Rate-only model returns 0. With bill burden: detectable.
    """
    p_rate_only = estimate_churn_probability(250.0, 150.0, tenure_years=8.0, annual_consumption_kwh=0.0)
    p_with_burden = estimate_churn_probability(250.0, 150.0, tenure_years=8.0, annual_consumption_kwh=45000.0)
    assert p_rate_only == 0.0, "Rate-only model should return 0 for falling rate + long tenure"
    assert p_with_burden > 0.30, f"Bill burden should push estimate above 30% threshold, got {p_with_burden:.3f}"


def test_small_resi_unaffected_by_bill_burden_in_normal_years():
    """Small resi customer (C1, 2800 kWh) at normal rates: bill stress stays zero."""
    # £60/MWh × 2800 kWh / 1000 = £168 — well below threshold
    p = estimate_churn_probability(60.0, 60.0, tenure_years=0.0, annual_consumption_kwh=2800.0)
    assert abs(p - BASE_CHURN_RATE) < 1e-9


def test_bill_stress_caps_at_max_churn_probability():
    """Extreme bill burden doesn't push probability above MAX_CHURN_PROBABILITY."""
    p = estimate_churn_probability(1000.0, 1000.0, tenure_years=0.0, annual_consumption_kwh=100000.0)
    assert p == MAX_CHURN_PROBABILITY


# ── Gas fuel tests (Phase 14b) ───────────────────────────────────────────────

def test_gas_flat_rate_returns_gas_base_minus_tenure():
    """Gas with no rate change returns GAS_BASE_CHURN_RATE minus tenure discount."""
    p = estimate_churn_probability(50.0, 50.0, tenure_years=0.0, fuel="gas")
    assert p == pytest.approx(GAS_BASE_CHURN_RATE)


def test_gas_base_rate_lower_than_electricity():
    """GAS_BASE_CHURN_RATE is lower than BASE_CHURN_RATE (stickier contracts)."""
    assert GAS_BASE_CHURN_RATE < BASE_CHURN_RATE


def test_gas_rate_sensitivity_lower_than_electricity():
    """GAS_RATE_SENSITIVITY is lower than RATE_SENSITIVITY (fewer alternatives)."""
    assert GAS_RATE_SENSITIVITY < RATE_SENSITIVITY


def test_gas_rate_increase_uses_gas_sensitivity():
    """A 50% gas rate increase uses GAS_RATE_SENSITIVITY, not RATE_SENSITIVITY."""
    p_gas = estimate_churn_probability(40.0, 60.0, tenure_years=0.0, fuel="gas")
    p_elec = estimate_churn_probability(40.0, 60.0, tenure_years=0.0, fuel="electricity")
    # Gas should be lower because sensitivity is lower
    assert p_gas < p_elec


def test_gas_estimate_quantified():
    """Gas churn estimate at +50% rate = GAS_BASE + GAS_SENSITIVITY × 0.5."""
    p = estimate_churn_probability(40.0, 60.0, tenure_years=0.0, fuel="gas")
    expected = GAS_BASE_CHURN_RATE + GAS_RATE_SENSITIVITY * 0.5
    assert p == pytest.approx(expected)


def test_gas_default_fuel_is_electricity():
    """Omitting fuel= gives same result as fuel='electricity'."""
    p_default = estimate_churn_probability(50.0, 75.0, tenure_years=1.0)
    p_explicit = estimate_churn_probability(50.0, 75.0, tenure_years=1.0, fuel="electricity")
    assert p_default == pytest.approx(p_explicit)


def test_gas_probability_never_below_zero():
    """Gas churn probability is clamped to >= 0 even for large rate decreases."""
    p = estimate_churn_probability(200.0, 50.0, tenure_years=5.0, fuel="gas")
    assert p >= 0.0


# ── Hedge fraction signal tests (Phase 15d) ──────────────────────────────────

def test_hedge_fraction_zero_matches_default():
    """hedge_fraction=0.0 gives same result as omitting the parameter."""
    p_default = estimate_churn_probability(50.0, 80.0, tenure_years=1.0)
    p_explicit = estimate_churn_probability(50.0, 80.0, tenure_years=1.0, hedge_fraction=0.0)
    assert p_default == pytest.approx(p_explicit)


def test_full_hedge_reduces_estimated_churn():
    """A fully hedged customer (hf=1.0) has lower estimated churn than unhedged at same rate increase.
    Use a moderate increase (100%) where hedge moves result below cap."""
    p_unhedged = estimate_churn_probability(50.0, 100.0, tenure_years=1.0, hedge_fraction=0.0)
    p_hedged = estimate_churn_probability(50.0, 100.0, tenure_years=1.0, hedge_fraction=1.0)
    assert p_hedged < p_unhedged


def test_hedge_sensitivity_quantified():
    """Full hedge: effective_rate_sensitivity = RATE_SENSITIVITY × (1 - HEDGE_SENSITIVITY_REDUCTION)."""
    rate_increase_pct = (100.0 - 50.0) / 50.0  # +100%
    expected_unhedged = BASE_CHURN_RATE + RATE_SENSITIVITY * rate_increase_pct - TENURE_DISCOUNT_PER_YEAR
    effective_sens = RATE_SENSITIVITY * (1.0 - 1.0 * HEDGE_SENSITIVITY_REDUCTION)
    expected_hedged = BASE_CHURN_RATE + effective_sens * rate_increase_pct - TENURE_DISCOUNT_PER_YEAR
    p_unhedged = estimate_churn_probability(50.0, 100.0, tenure_years=1.0, hedge_fraction=0.0)
    p_hedged = estimate_churn_probability(50.0, 100.0, tenure_years=1.0, hedge_fraction=1.0)
    assert p_unhedged == pytest.approx(min(MAX_CHURN_PROBABILITY, max(0.0, expected_unhedged)))
    assert p_hedged == pytest.approx(min(MAX_CHURN_PROBABILITY, max(0.0, expected_hedged)))


def test_partial_hedge_intermediate_churn():
    """A partial hedge (hf=0.5) gives a result between no-hedge and full-hedge."""
    p_none = estimate_churn_probability(50.0, 100.0, tenure_years=1.0, hedge_fraction=0.0)
    p_half = estimate_churn_probability(50.0, 100.0, tenure_years=1.0, hedge_fraction=0.5)
    p_full = estimate_churn_probability(50.0, 100.0, tenure_years=1.0, hedge_fraction=1.0)
    assert p_full < p_half < p_none


def test_hedge_does_not_reduce_below_zero():
    """Even with full hedge and rate decrease, result stays >= 0."""
    p = estimate_churn_probability(200.0, 50.0, tenure_years=5.0, hedge_fraction=1.0)
    assert p >= 0.0


def test_hedge_crisis_scenario_reduces_estimate():
    """Crisis year: 160% rate increase — no-hedge hits cap, well-hedged customer stays below cap."""
    # old=£50, new=£130 (+160%): no-hedge → capped at 0.95; hf=0.95 → stays below cap
    p = estimate_churn_probability(50.0, 130.0, tenure_years=3.0, hedge_fraction=0.95)
    p_no_hedge = estimate_churn_probability(50.0, 130.0, tenure_years=3.0, hedge_fraction=0.0)
    assert p_no_hedge == pytest.approx(MAX_CHURN_PROBABILITY)   # capped
    assert p < MAX_CHURN_PROBABILITY   # hedge keeps it below cap
    assert p < p_no_hedge   # strictly lower


# --- Phase 22a: crisis hangover uplift ---

def test_hangover_zero_no_effect():
    """hangover_periods_remaining=0 produces same result as default."""
    p_default = estimate_churn_probability(200.0, 150.0, tenure_years=2.0)
    p_zero = estimate_churn_probability(200.0, 150.0, tenure_years=2.0, hangover_periods_remaining=0)
    assert p_default == pytest.approx(p_zero)


def test_hangover_one_adds_uplift():
    """hangover_periods_remaining=1 adds CRISIS_HANGOVER_BASE_UPLIFT to churn probability.
    Use flat rate + zero tenure so base probability is not clamped, allowing exact diff check.
    """
    p_no_hangover = estimate_churn_probability(100.0, 100.0, tenure_years=0.0)
    p_hangover = estimate_churn_probability(100.0, 100.0, tenure_years=0.0, hangover_periods_remaining=1)
    assert abs(p_hangover - p_no_hangover - CRISIS_HANGOVER_BASE_UPLIFT) < 1e-9


def test_hangover_two_same_as_one():
    """Any positive hangover_periods_remaining adds exactly one CRISIS_HANGOVER_BASE_UPLIFT."""
    p_1 = estimate_churn_probability(200.0, 150.0, tenure_years=2.0, hangover_periods_remaining=1)
    p_2 = estimate_churn_probability(200.0, 150.0, tenure_years=2.0, hangover_periods_remaining=2)
    assert p_1 == pytest.approx(p_2)


def test_hangover_capped_at_max():
    """Hangover cannot push probability above MAX_CHURN_PROBABILITY."""
    p = estimate_churn_probability(100.0, 300.0, tenure_years=0.0, hangover_periods_remaining=1)
    assert p <= MAX_CHURN_PROBABILITY


def test_hangover_post_crisis_rate_fall():
    """Post-crisis scenario: rate falls, rate-change signal collapses, but hangover fires.

    This is the 2024 failure mode: rates fell from crisis peaks, rate_increase_pct is negative,
    so the model would estimate near-zero or zero churn without hangover.
    With hangover: company gets a meaningful uplift above the floor.
    """
    # old=£200 (post-crisis), new=£195 (small fall, tenure=0 so no tenure discount)
    # rate_increase_pct = -0.025 → base_only = 0.10 - 0.8*0.025 = 0.08
    p_no_hangover = estimate_churn_probability(200.0, 195.0, tenure_years=0.0)
    p_hangover = estimate_churn_probability(200.0, 195.0, tenure_years=0.0, hangover_periods_remaining=1)
    assert p_hangover > p_no_hangover
    assert abs(p_hangover - p_no_hangover - CRISIS_HANGOVER_BASE_UPLIFT) < 1e-9


def test_hangover_window_periods_constant():
    """CRISIS_HANGOVER_WINDOW_PERIODS is 2 (two renewals of elevated churn post-crisis)."""
    assert CRISIS_HANGOVER_WINDOW_PERIODS == 2


def test_hangover_uplift_constant():
    """CRISIS_HANGOVER_BASE_UPLIFT is 0.12 (12pp of extra churn during hangover)."""
    assert CRISIS_HANGOVER_BASE_UPLIFT == pytest.approx(0.12)


# --- Phase 27e: I&C churn model tests ---

def test_ic_base_churn_rate_higher_than_resi():
    """I&C base churn rate is higher than residential (broker-driven)."""
    assert IC_BASE_CHURN_RATE > BASE_CHURN_RATE


def test_ic_rate_sensitivity_higher_than_resi():
    """I&C rate sensitivity is higher than residential (price-sophisticated buyers)."""
    assert IC_RATE_SENSITIVITY > RATE_SENSITIVITY


def test_ic_churn_flat_rate_returns_base_minus_tenure():
    """No rate change at year 0: I&C returns IC_BASE_CHURN_RATE."""
    p = estimate_churn_probability(100.0, 100.0, 0.0, segment="I&C")
    assert p == pytest.approx(IC_BASE_CHURN_RATE)


def test_ic_churn_higher_than_resi_at_same_rate_increase():
    """At the same 10% rate increase, I&C churns more than residential."""
    p_resi = estimate_churn_probability(100.0, 110.0, 2.0)
    p_ic = estimate_churn_probability(100.0, 110.0, 2.0, segment="I&C")
    assert p_ic > p_resi


def test_ic_churn_capped_at_max():
    """I&C churn caps at MAX_CHURN_PROBABILITY even with extreme rate increase."""
    p = estimate_churn_probability(100.0, 500.0, 0.0, segment="I&C")
    assert p == pytest.approx(MAX_CHURN_PROBABILITY)


def test_ic_large_consumption_flat_rate_not_bill_stress_driven():
    """I&C at 4 GWh with flat rate gets base churn, not max.
    IC_BILL_STRESS_SENSITIVITY=0 means bill size does not drive churn for I&C.
    A 4 GWh site has a large bill (£216k/yr at £54/MWh) but is not financially
    stressed -- it is a professional energy buyer pricing via brokers."""
    p = estimate_churn_probability(
        54.0, 54.0, 2.0,
        annual_consumption_kwh=4_000_000,
        segment="I&C",
    )
    assert p < 0.30, f"Expected low I&C churn at flat rate, got {p:.3f}"


def test_ic_crisis_rate_spike_still_triggers_max_churn():
    """I&C churn caps at max when rate spikes 400% (crisis scenario)."""
    from company.crm.churn_model import MAX_CHURN_PROBABILITY
    p = estimate_churn_probability(
        54.0, 270.0, 2.0,
        annual_consumption_kwh=4_000_000,
        segment="I&C",
    )
    assert p == pytest.approx(MAX_CHURN_PROBABILITY)


def test_resi_segment_same_as_default():
    """segment='resi' gives same result as default (no segment param)."""
    p_default = estimate_churn_probability(100.0, 110.0, 2.0)
    p_resi = estimate_churn_probability(100.0, 110.0, 2.0, segment="resi")
    assert p_default == pytest.approx(p_resi)


# ── Phase 33: active/passive renewal split ────────────────────────────────────

def test_estimate_passive_churn_flat_rate_returns_low_base():
    from company.crm.churn_model import estimate_passive_churn_probability, PASSIVE_BASE_CHURN_RATE
    p = estimate_passive_churn_probability(100.0, 100.0, tenure_years=0.0)
    assert p == pytest.approx(PASSIVE_BASE_CHURN_RATE)


def test_estimate_passive_churn_large_increase_capped():
    from company.crm.churn_model import estimate_passive_churn_probability, PASSIVE_CHURN_CAP
    p = estimate_passive_churn_probability(100.0, 500.0, tenure_years=0.0)
    assert p == pytest.approx(PASSIVE_CHURN_CAP)


def test_estimate_passive_churn_lower_than_active_same_inputs():
    from company.crm.churn_model import estimate_passive_churn_probability
    p_active = estimate_churn_probability(100.0, 150.0, tenure_years=0.0)
    p_passive = estimate_passive_churn_probability(100.0, 150.0, tenure_years=0.0)
    assert p_passive < p_active


def test_is_active_renewal_crisis_year_always_passive():
    from company.crm.churn_model import is_active_renewal, CRISIS_PASSIVE_YEARS
    for yr in CRISIS_PASSIVE_YEARS:
        assert is_active_renewal(f"{yr}-04-01", f"C1_{yr}") is False


def test_is_active_renewal_non_crisis_probabilistic():
    from company.crm.churn_model import is_active_renewal, PASSIVE_RENEWAL_RATE
    # With a large sample, active rate should be close to PASSIVE_RENEWAL_RATE
    seeds = [f"C{i}_1" for i in range(200)]
    active_count = sum(1 for s in seeds if is_active_renewal("2020-01-01", s))
    # Should be roughly 200 * 0.35 ± noise; accept a wide band [30, 100]
    assert 30 <= active_count <= 100


def test_is_active_renewal_deterministic():
    """Same seed always gives same result."""
    from company.crm.churn_model import is_active_renewal
    r1 = is_active_renewal("2020-01-01", "C1_2")
    r2 = is_active_renewal("2020-01-01", "C1_2")
    assert r1 == r2
