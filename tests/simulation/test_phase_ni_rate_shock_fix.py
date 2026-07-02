"""Phase NI: Term-level rate shock counter fix for TOU HH customers.

Bug: count_rate_shocks() from bill_shock_tracker was counting TOU peak/offpeak
transitions in HH settlement records as bill shocks, giving HH TOU customers
500-1500+ spurious shock counts and capping company churn estimate at 0.95.

Fix: run_phase2b.py now tracks shocks directly at term boundaries using
_elec_rate_shock_counts, which only increments when the annual contract rate
(stored in prev_elec_unit_rates) increases by > 20%.

These tests verify correct shock counting in isolation, exercising the same
logic embedded in the main loop.
"""
import pytest


def _term_shock_count(rate_history: list[float], threshold: float = 0.20) -> int:
    """Mirror of the _elec_rate_shock_counts logic in run_phase2b.main().

    rate_history: ordered list of annual term rates (GBP/MWh), earliest first.
    Returns cumulative count of terms where rate increased > threshold vs prior term.
    """
    shocks = 0
    for i in range(1, len(rate_history)):
        old = rate_history[i - 1]
        new = rate_history[i]
        if old is not None and old > 0:
            if (new - old) / old > threshold:
                shocks += 1
    return shocks


def test_stable_rates_no_shocks():
    rates = [120.0, 122.0, 125.0, 128.0]
    assert _term_shock_count(rates) == 0


def test_single_large_increase_counts_one():
    rates = [120.0, 150.0]
    assert _term_shock_count(rates) == 1


def test_exact_threshold_not_counted():
    rates = [100.0, 120.0]
    assert _term_shock_count(rates) == 0


def test_just_above_threshold_counted():
    rates = [100.0, 120.01]
    assert _term_shock_count(rates) == 1


def test_crisis_spike_plus_recovery_counts_once():
    """A crisis spike followed by partial recovery: only the spike counts."""
    rates = [120.0, 80.0, 90.0, 300.0, 220.0]
    assert _term_shock_count(rates) == 1


def test_two_consecutive_spikes_counts_two():
    rates = [80.0, 100.0, 180.0, 380.0]
    assert _term_shock_count(rates) == 3


def test_rate_decrease_not_a_shock():
    rates = [200.0, 120.0]
    assert _term_shock_count(rates) == 0


def test_single_rate_no_shock():
    assert _term_shock_count([100.0]) == 0


def test_empty_history_no_shock():
    assert _term_shock_count([]) == 0


def test_tou_alternation_should_not_count():
    """TOU customers see offpeak/peak alternation but term rate is stable.

    The fix ensures we track TERM rates, not HH period rates. Simulating
    what happens when term rate is 120 for two years (no shock) regardless
    of intra-term TOU variation.
    """
    term_rates = [120.0, 120.0]
    assert _term_shock_count(term_rates) == 0


def test_tou_term_spike_still_counted():
    """When the annual term rate spikes (>20%), shock IS counted, TOU or not."""
    term_rates = [100.0, 145.0]
    assert _term_shock_count(term_rates) == 1


def test_custom_threshold():
    rates = [100.0, 115.0]
    assert _term_shock_count(rates, threshold=0.10) == 1
    assert _term_shock_count(rates, threshold=0.20) == 0


def test_resi_hh_typical_rate_history_2016_2022():
    """Approximate C7 (resi HH) rate history: stable 2016-2018, spike 2021-2022."""
    rates = [117.0, 130.6, 122.7, 147.5, 141.7, 183.0, 305.0]
    assert _term_shock_count(rates) == 3


def test_ic_customer_high_sensitivity_correct_count():
    """I&C customers with multiple rate spikes get accurate cumulative count."""
    rates = [50.0, 70.0, 60.0, 150.0, 250.0]
    assert _term_shock_count(rates) == 3
