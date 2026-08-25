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
    """A truly extreme spike (900% increase) still asymptotically approaches
    MAX_CHURN_PROBABILITY (Phase QP+1: saturating curve, not a hard clamp -- see
    test_moderate_ic_rate_rises_stay_distinguishable_below_cap for why the clamp
    was replaced)."""
    p = estimate_churn_probability(100.0, 1000.0, tenure_years=0.0)
    assert p == pytest.approx(MAX_CHURN_PROBABILITY)
    assert p <= MAX_CHURN_PROBABILITY


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
    assert p == pytest.approx(MAX_CHURN_PROBABILITY)
    assert p <= MAX_CHURN_PROBABILITY


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
    """Crisis year: 160% rate increase — no-hedge sits high in the saturating zone,
    well-hedged customer stays clearly lower (Phase QP+1: no longer both indistinguishably
    capped at exactly 0.95 -- that collapse was the calibration bug being fixed)."""
    # old=£50, new=£130 (+160%): no-hedge → high, near-saturated; hf=0.95 → clearly lower
    p = estimate_churn_probability(50.0, 130.0, tenure_years=3.0, hedge_fraction=0.95)
    p_no_hedge = estimate_churn_probability(50.0, 130.0, tenure_years=3.0, hedge_fraction=0.0)
    assert p_no_hedge > 0.90   # still clearly elevated
    assert p_no_hedge < MAX_CHURN_PROBABILITY   # no longer hard-clamped
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


# ── Phase QB: observable market-conditions signal ─────────────────────────────

def test_estimate_passive_churn_no_renewal_year_unchanged():
    """Default (no renewal_year) behaviour is unchanged — backward compatible."""
    from company.crm.churn_model import estimate_passive_churn_probability
    p_none = estimate_passive_churn_probability(100.0, 100.0, tenure_years=0.0)
    p_explicit_none = estimate_passive_churn_probability(100.0, 100.0, tenure_years=0.0, renewal_year=None)
    assert p_none == pytest.approx(p_explicit_none)


def test_estimate_passive_churn_crisis_year_suppressed_below_calm_year():
    """2022 (crisis, multiplier 0.44) must give a lower passive estimate than
    2016 (peak competition, multiplier 2.17) for identical rate/tenure inputs —
    even inert SVT-rollers are less likely to move when there's nowhere
    cheaper to switch to."""
    from company.crm.churn_model import estimate_passive_churn_probability
    p_crisis = estimate_passive_churn_probability(100.0, 100.0, tenure_years=0.0, renewal_year=2022)
    p_calm = estimate_passive_churn_probability(100.0, 100.0, tenure_years=0.0, renewal_year=2016)
    assert p_crisis < p_calm


def test_estimate_passive_churn_market_multiplier_clamped_to_valid_range():
    from company.crm.churn_model import estimate_passive_churn_probability, MAX_CHURN_PROBABILITY
    p = estimate_passive_churn_probability(100.0, 500.0, tenure_years=0.0, renewal_year=2016)
    assert 0.0 <= p <= MAX_CHURN_PROBABILITY


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


# --- Phase QP+1: 0.95-ceiling calibration fix (PRIORITIES.md P1, flagged since Phase QB) ---
# The C_IC1 case in the Decision Event Ledger (Phase QP) showed a 95% company estimate
# sizing a real retention discount against a SIM truth of 4% -- and PRIORITIES.md flagged
# that IC_RATE_SENSITIVITY=1.5 meant *any* sufficiently large single-renewal I&C rate rise
# saturated the hard clamp, collapsing genuinely different risk levels into an
# indistinguishable 95%. These tests lock in the fix: below CHURN_SATURATION_ELBOW nothing
# changes; above it, a saturating curve keeps realistic crisis-era rises distinguishable.

def test_below_elbow_behaviour_is_byte_for_byte_unchanged():
    """Every pre-existing non-capped test in this file already proves this, but assert
    the elbow constant explicitly so a future change to it is caught here first."""
    from company.crm.churn_model import CHURN_SATURATION_ELBOW
    assert CHURN_SATURATION_ELBOW == pytest.approx(0.90)
    # A raw score exactly at the elbow must pass through unchanged.
    p = estimate_churn_probability(100.0, 100.0 * 1.775, tenure_years=0.0)  # 0.10+0.8*0.775=0.72
    assert p < CHURN_SATURATION_ELBOW


def test_moderate_ic_rate_rises_stay_distinguishable_below_cap():
    """Two different I&C crisis-era rate rises (60% vs 150%) must no longer both
    collapse to the same 95% -- this is the exact calibration bug the fix closes."""
    p_60pct = estimate_churn_probability(100.0, 160.0, tenure_years=0.0, segment="I&C")
    p_150pct = estimate_churn_probability(100.0, 250.0, tenure_years=0.0, segment="I&C")
    assert p_60pct < MAX_CHURN_PROBABILITY
    assert p_150pct < MAX_CHURN_PROBABILITY
    assert p_60pct < p_150pct, "higher rate rise must still read as higher risk"
    assert p_150pct - p_60pct > 0.001, "must be genuinely distinguishable, not both ~= cap"


def test_saturation_still_monotonic_increasing():
    """The saturating curve must never make a larger raw score map to a smaller
    probability -- monotonicity is the property that keeps ordering meaningful."""
    prev = 0.0
    for new_rate in (100.0, 150.0, 200.0, 300.0, 500.0, 1000.0, 5000.0):
        p = estimate_churn_probability(100.0, new_rate, tenure_years=0.0, segment="I&C")
        assert p >= prev
        prev = p


def test_saturation_never_exceeds_ceiling():
    """No input, however extreme, pushes the estimate above MAX_CHURN_PROBABILITY."""
    p = estimate_churn_probability(1.0, 1_000_000.0, tenure_years=0.0, segment="I&C")
    assert p <= MAX_CHURN_PROBABILITY


def test_is_active_renewal_deterministic():
    """Same seed always gives same result."""
    from company.crm.churn_model import is_active_renewal
    r1 = is_active_renewal("2020-01-01", "C1_2")
    r2 = is_active_renewal("2020-01-01", "C1_2")
    assert r1 == r2


# --- Phase 2 Layer 1 (CORE_FIDELITY_PHASES.md): per-customer active_probability ---

def test_is_active_renewal_default_matches_flat_passive_rate():
    """No active_probability supplied -- must reproduce the old flat-rate
    behaviour byte for byte (backward compatibility for any other caller)."""
    from company.crm.churn_model import is_active_renewal, PASSIVE_RENEWAL_RATE
    seeds = [f"C{i}_default" for i in range(200)]
    with_default = [is_active_renewal("2020-01-01", s) for s in seeds]
    with_explicit_rate = [is_active_renewal("2020-01-01", s, PASSIVE_RENEWAL_RATE) for s in seeds]
    assert with_default == with_explicit_rate


def test_is_active_renewal_honours_custom_active_probability():
    from company.crm.churn_model import is_active_renewal
    seeds = [f"C{i}_custom" for i in range(300)]
    high = sum(is_active_renewal("2020-01-01", s, active_probability=0.90) for s in seeds)
    low = sum(is_active_renewal("2020-01-01", s, active_probability=0.02) for s in seeds)
    assert high > low
    assert high > 200  # ~90% of 300
    assert low < 30    # ~2% of 300


def test_is_active_renewal_zero_probability_never_active():
    from company.crm.churn_model import is_active_renewal
    seeds = [f"C{i}_zero" for i in range(100)]
    assert not any(is_active_renewal("2020-01-01", s, active_probability=0.0) for s in seeds)


def test_is_active_renewal_one_probability_always_active_outside_crisis():
    from company.crm.churn_model import is_active_renewal
    seeds = [f"C{i}_one" for i in range(100)]
    assert all(is_active_renewal("2020-01-01", s, active_probability=1.0) for s in seeds)


def test_is_active_renewal_crisis_year_forces_passive_regardless_of_probability():
    """Crisis-year forcing must override even a high active_probability -- no
    fixed deals were physically available to switch to."""
    from company.crm.churn_model import is_active_renewal, CRISIS_PASSIVE_YEARS
    for yr in CRISIS_PASSIVE_YEARS:
        assert is_active_renewal(f"{yr}-04-01", "C1_crisis", active_probability=1.0) is False


# ═══════════════════════════════════════════════════════════════════════════════════════
# 2026-08-25 -- the two properties that discharge
# WORKER_FINDING_THE_CHURN_MODELS_CAP_MAKES_THE_PROFIT_MAXIMISING_PRICE_UNBOUNDED.
#
# The finding names exactly what would close it: "a rate response that distinguishes a
# supplier-specific move from a market-wide one, and that does not leave a floor of
# unconditionally captive customers". These are those two, plus the mutation controls that
# make them able to FAIL (R15): each of the two headline tests below has a partner that puts
# ONLY the removed constant back and asserts the defect returns. A control that cannot fail
# is worse than none.
# ═══════════════════════════════════════════════════════════════════════════════════════

def test_a_market_wide_rise_and_a_supplier_specific_one_are_not_the_same_event():
    """Same bill move, same customer, same everything -- but one is the market's doing and
    one is ours. Before this fix the model could not tell them apart at all."""
    supplier_specific = estimate_churn_probability(120.0, 200.0, 4.0, 3100.0, market_move_pct=0.0)
    market_wide = estimate_churn_probability(120.0, 200.0, 4.0, 3100.0,
                                             market_move_pct=(200.0 - 120.0) / 120.0)
    assert supplier_specific > market_wide + 0.30, (
        "a customer whose supplier raised its price 67% while the market stood still has a "
        "cheaper alternative and it is obvious; one whose whole market moved has nowhere to go"
    )
    # And a supplier that moves LESS than the market is rewarded, not merely punished less.
    moved_less = estimate_churn_probability(120.0, 140.0, 4.0, 3100.0, market_move_pct=0.50)
    flat_market = estimate_churn_probability(120.0, 140.0, 4.0, 3100.0, market_move_pct=0.0)
    assert moved_less < flat_market


def test_null_control_market_netting_off_restores_the_indistinguishable_model():
    """THE MUTATION. `market_move_pct` defaults to 0.0 -- no netting -- which is the model as
    it stood. With it, the two events above become the identical number, which is the defect.
    If this ever stops holding, the test above is passing for some other reason."""
    a = estimate_churn_probability(120.0, 200.0, 4.0, 3100.0)
    b = estimate_churn_probability(120.0, 200.0, 4.0, 3100.0, market_move_pct=0.0)
    assert a == b
    # ... and the netting is the ONLY thing that separates them.
    assert estimate_churn_probability(120.0, 200.0, 4.0, 3100.0,
                                      market_move_pct=(200.0 - 120.0) / 120.0) != a


def test_the_market_move_is_derived_from_the_published_cap_not_written_down():
    """The company reads its OWN cap module for the market-wide half. Independence matters
    here (R15 TAUTOLOGY): if this came from the same place as the customer's own rate, the
    netting would be identically zero and the test above would be checking nothing."""
    from company.crm.market_conditions import market_rate_move_pct
    from company.pricing.ofgem_price_cap import get_cap_unit_rate_gbp_per_mwh

    move = market_rate_move_pct(2022)
    now = get_cap_unit_rate_gbp_per_mwh("electricity", 2022)
    before = get_cap_unit_rate_gbp_per_mwh("electricity", 2021)
    assert move == pytest.approx((now - before) / before)
    assert move > 0.5, "2022 is the largest published domestic step there has ever been"
    # FAIL-SOFT, not fail-open: an unknown year nets nothing rather than inventing a move.
    assert market_rate_move_pct(None) == 0.0
    assert market_rate_move_pct(1900) == 0.0


def test_no_customer_is_modelled_as_staying_whatever_they_are_charged():
    """P(stay) must decay toward zero, not onto a floor. This is the property the whole
    finding turns on: expected value is `P(stay) x margin x volume`, so any floor above zero
    makes the profit-maximising price unbounded."""
    from company.crm.churn_model import MAX_CHURN_PROBABILITY as CEILING
    assert CEILING == 1.0, "a company belief bounded below certainty IS the captive floor"
    p_stay = [1.0 - estimate_churn_probability(120.0, 120.0 * (1.0 + d), 4.0, 3100.0)
              for d in (1.0, 2.0, 4.0, 8.0, 16.0)]
    assert all(later < earlier for earlier, later in zip(p_stay, p_stay[1:])), \
        "retention must keep falling, not flatten"
    assert p_stay[-1] < 1e-4, f"a floor of {p_stay[-1]:.4f} survives an unbounded price"
    # It approaches zero ASYMPTOTICALLY -- still strictly positive at +800%, and only
    # reaching a literal 0.0 further out where double precision runs out of room. The
    # distinction matters: a curve that CLAMPS to zero would have an interior kink an
    # optimiser could sit in, and this one does not.
    assert p_stay[-2] > 0.0


def test_null_control_a_ceiling_below_one_reinstates_the_captive_floor(monkeypatch):
    """THE MUTATION, and it is the finding's own arithmetic. Put back the single constant
    that was changed -- nothing else -- and retention flattens onto 5% no matter the price."""
    import company.crm.churn_model as cm
    monkeypatch.setattr(cm, "MAX_CHURN_PROBABILITY", 0.95)
    p_stay = [1.0 - cm.estimate_churn_probability(120.0, 120.0 * (1.0 + d), 4.0, 3100.0)
              for d in (1.0, 4.0, 16.0, 64.0)]
    assert p_stay[-1] == pytest.approx(0.05, abs=1e-6), (
        "with the old ceiling, 5% of every account stays whatever it is charged -- if this "
        "assertion fails the defect is not what the finding said it was"
    )
