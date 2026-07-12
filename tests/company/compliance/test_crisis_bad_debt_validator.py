"""Tests for company/compliance/crisis_bad_debt_validator.py --
AFFORDABILITY_AS_SIM_PHYSICS.md thin start.

Two kinds of test here:
  1. Pure-function unit tests on SYNTHETIC data -- assert the validator's
     logic is correct (a real crisis step-up passes; a flat/low trajectory
     fails). These pass.
  2. A LIVE-DATA xfail test -- runs the validator against the real
     run_output_latest.json and documents that it currently FAILS. This is
     the honest measurement of the affordability gap the CFO cold-walk found
     (director-adjudicated real, coldwalk:bad_debt_implausibly_low_through_
     2021_22_crisis). It is marked xfail(strict=True): the day the
     affordability mechanism (W2_4.. cluster, M3) makes arrears actually
     emerge through the crisis, this XPASSes and strict mode turns that into
     a FAILURE, forcing this scaffolding to be revisited -- the project's
     convention for "a test that documents a currently-real gap" without
     silently rotting once the gap closes.

R12 (anti-goal-seek): nothing here may be satisfied by tuning a bad-debt
parameter toward the anchor. The xfail closes only when arrears EMERGE.
"""
import json
from pathlib import Path

import pytest

from company.compliance.crisis_bad_debt_validator import (
    CRISIS_BAD_DEBT_RATE_FLOOR,
    CRISIS_STEP_UP_MIN_RATIO,
    extract_series_from_run_output,
    validate_crisis_bad_debt,
    validate_run_output,
)

_RUN_OUTPUT = Path(__file__).resolve().parents[3] / "docs" / "reports" / "run_output_latest.json"


# --- 1. Pure-function unit tests (synthetic data) ---


def test_real_crisis_step_up_passes():
    # A trajectory that behaves like the real 2021-22 crisis: bad-debt rate
    # ~1% pre-crisis rising to ~2.5% in the crisis years -> should PASS.
    revenue = {2016: 1_000_000, 2017: 1_000_000, 2018: 1_000_000, 2019: 1_000_000,
               2021: 1_000_000, 2022: 1_000_000}
    bad_debt = {2016: 10_000, 2017: 10_000, 2018: 10_000, 2019: 10_000,   # ~1%
                2021: 25_000, 2022: 25_000}                                # ~2.5%
    result = validate_crisis_bad_debt(bad_debt, revenue)
    assert result.passed, result.summary()
    assert result.step_up_ratio >= CRISIS_STEP_UP_MIN_RATIO
    assert result.crisis_rate >= CRISIS_BAD_DEBT_RATE_FLOOR


def test_flat_low_trajectory_fails_the_floor():
    # Uniformly tiny bad debt (the behavioural-arrears-engine signature):
    # fails BOTH the floor and the step-up.
    revenue = {y: 1_000_000 for y in (2016, 2017, 2018, 2019, 2021, 2022)}
    bad_debt = {y: 50 for y in (2016, 2017, 2018, 2019, 2021, 2022)}  # 0.005%
    result = validate_crisis_bad_debt(bad_debt, revenue)
    assert not result.passed
    assert any("below anchored floor" in f for f in result.failures)


def test_in_band_but_flat_fails_the_step_up():
    # ~2.2% every year (the PnL-accrual signature): clears the floor but has
    # NO crisis spike, so it must fail the step-up assertion.
    revenue = {y: 1_000_000 for y in (2016, 2017, 2018, 2019, 2021, 2022)}
    bad_debt = {y: 22_000 for y in (2016, 2017, 2018, 2019, 2021, 2022)}
    result = validate_crisis_bad_debt(bad_debt, revenue)
    assert not result.passed
    assert any("step-up" in f for f in result.failures)
    assert not any("below anchored floor" in f for f in result.failures)


def test_zero_revenue_year_does_not_crash():
    revenue = {2016: 0, 2017: 1_000_000, 2018: 1_000_000, 2019: 1_000_000,
               2021: 1_000_000, 2022: 1_000_000}
    bad_debt = {2016: 0, 2017: 10_000, 2018: 10_000, 2019: 10_000,
                2021: 25_000, 2022: 25_000}
    result = validate_crisis_bad_debt(bad_debt, revenue)  # must not raise
    assert result.crisis_rate > 0


def test_extract_both_bases_from_run_output():
    if not _RUN_OUTPUT.exists():
        pytest.skip("no run_output_latest.json present")
    run = json.loads(_RUN_OUTPUT.read_text())
    head_bd, head_rev = extract_series_from_run_output(run, "headline")
    pnl_bd, pnl_rev = extract_series_from_run_output(run, "pnl_accrual")
    # Both bases must yield the crisis years.
    assert 2021 in head_bd and 2022 in head_bd
    assert 2021 in pnl_bd and 2022 in pnl_bd
    # The two bases are genuinely different representations (this IS the
    # separately-registered multiple-basis ambiguity).
    assert head_bd[2022] != pnl_bd[2022]


# --- 2. Live-data expected-failure: documents the currently-real gap ---


@pytest.mark.xfail(
    strict=True,
    reason=(
        "AFFORDABILITY_AS_SIM_PHYSICS.md: arrears are currently propensity-shaped, "
        "not emergent from a household budget meeting a price shock -- so the "
        "headline bad-debt trajectory shows no real 2021-22 crisis step-up. "
        "EXPECTED to fail until the W2_4.. affordability cluster (M3) is built. "
        "Do NOT satisfy this by tuning a bad-debt parameter (R12)."
    ),
)
def test_live_run_output_shows_crisis_step_up_headline():
    if not _RUN_OUTPUT.exists():
        pytest.skip("no run_output_latest.json present")
    run = json.loads(_RUN_OUTPUT.read_text())
    result = validate_run_output(run, "headline")
    assert result.passed, result.summary()
