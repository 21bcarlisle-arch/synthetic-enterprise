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
from pathlib import Path

import pytest

from company.compliance.crisis_bad_debt_validator import (
    CRISIS_BAD_DEBT_RATE_FLOOR,
    CRISIS_STEP_UP_MIN_RATIO,
    CRISIS_YEARS,
    extract_series_from_run_output,
    validate_crisis_bad_debt,
    validate_run_output,
)
from tools.run_output_store import load_run_output, resolve_run_output

_RUN_OUTPUT = Path(__file__).resolve().parents[3] / "docs" / "reports" / "run_output_latest.json"


def _published_run_or_skip():
    """The published run, plain or gzipped. Since 2026-10-10 only the .gz is committed, and a read of
    the plain path skipped silently in every worktree and gate extract for four days."""
    if resolve_run_output(_RUN_OUTPUT) is None:
        pytest.skip("no run_output_latest.json present, plain or gzipped")
    return load_run_output(_RUN_OUTPUT)


# --- 1. Pure-function unit tests (synthetic data) ---


def test_real_crisis_step_up_passes():
    # A trajectory that behaves like the real crisis charge: bad-debt rate
    # ~1% pre-crisis rising to ~2.5% in the crisis years -> should PASS.
    revenue = {2016: 1_000_000, 2017: 1_000_000, 2018: 1_000_000, 2019: 1_000_000,
               2022: 1_000_000, 2023: 1_000_000}
    bad_debt = {2016: 10_000, 2017: 10_000, 2018: 10_000, 2019: 10_000,   # ~1%
                2022: 25_000, 2023: 25_000}                                # ~2.5%
    result = validate_crisis_bad_debt(bad_debt, revenue)
    assert result.passed, result.summary()
    assert result.step_up_ratio >= CRISIS_STEP_UP_MIN_RATIO
    assert result.crisis_rate >= CRISIS_BAD_DEBT_RATE_FLOOR


def test_flat_low_trajectory_fails_the_floor():
    # Uniformly tiny bad debt (the behavioural-arrears-engine signature):
    # fails BOTH the floor and the step-up.
    revenue = {y: 1_000_000 for y in (2016, 2017, 2018, 2019, 2022, 2023)}
    bad_debt = {y: 50 for y in (2016, 2017, 2018, 2019, 2022, 2023)}  # 0.005%
    result = validate_crisis_bad_debt(bad_debt, revenue)
    assert not result.passed
    assert any("below anchored floor" in f for f in result.failures)


def test_in_band_but_flat_fails_the_step_up():
    # ~2.2% every year (the PnL-accrual signature): clears the floor but has
    # NO crisis spike, so it must fail the step-up assertion.
    revenue = {y: 1_000_000 for y in (2016, 2017, 2018, 2019, 2022, 2023)}
    bad_debt = {y: 22_000 for y in (2016, 2017, 2018, 2019, 2022, 2023)}
    result = validate_crisis_bad_debt(bad_debt, revenue)
    assert not result.passed
    assert any("step-up" in f for f in result.failures)
    assert not any("below anchored floor" in f for f in result.failures)


def test_zero_revenue_year_does_not_crash():
    revenue = {2016: 0, 2017: 1_000_000, 2018: 1_000_000, 2019: 1_000_000,
               2022: 1_000_000, 2023: 1_000_000}
    bad_debt = {2016: 0, 2017: 10_000, 2018: 10_000, 2019: 10_000,
                2022: 25_000, 2023: 25_000}
    result = validate_crisis_bad_debt(bad_debt, revenue)  # must not raise
    assert result.crisis_rate > 0


def test_the_published_record_passes_its_own_validator_defect_a_window_that_holds_the_real_trough():
    # Centrica's UK bad-debt charge as a share of revenue, as published (bad_debt_provisioning.md
    # 3.2): 2021 was its decade low and 2023 its high. A validator the real supplier fails cannot
    # be graded against. 2016-18 are not published on this basis, so 2019 alone is the baseline.
    real = {2019: 1.2, 2020: 2.2, 2021: 1.1, 2022: 2.1, 2023: 2.7}
    result = validate_crisis_bad_debt(real, {y: 100.0 for y in real})
    assert result.passed, result.summary()
    assert 2021 not in CRISIS_YEARS and 2023 in CRISIS_YEARS


def test_extract_both_bases_from_run_output():
    run = _published_run_or_skip()
    head_bd, head_rev = extract_series_from_run_output(run, "headline")
    pnl_bd, pnl_rev = extract_series_from_run_output(run, "pnl_accrual")
    # Both bases must yield the crisis years.
    assert all(y in head_bd and y in pnl_bd for y in CRISIS_YEARS)
    # The two bases are genuinely different representations (this IS the
    # separately-registered multiple-basis ambiguity).
    assert head_bd[2022] != pnl_bd[2022]


# --- 2. Live-data expected-failure: documents the currently-real gap ---


# THE STRICT XFAIL IS RETIRED (2026-10-11), by the convention this module states: it XPASSed. The
# published run output (a88fb2436, 2026-10-05 -- neither it nor the validator has changed since)
# shows the crisis step-up the marker said it could not, so the strict xfail had turned into a
# FAILURE on origin and refused every landing that selected it for six days. Kept as a live guard
# on the published headline. NOT ESTABLISHED HERE: that the step-up EMERGES from a household budget
# meeting the price shock rather than from a tuned propensity -- R12's condition for closing the
# gap. That question is the W2_4.. affordability cluster's and is not answered by this pass.
#
# THE STRICT XFAIL IS RE-ARMED (2026-10-14), on both bases. The a88fb2436 run above XPASSed; read
# through the store, the published run (2248e3baf, and 6ab998ad7 in the
# shared tree) FAILS on both: the crisis-years share falls (headline 0.10% against 0.15% pre-crisis;
# P&L accrual 1.76% against 2.01%) because revenue doubled in 2022 while the write-offs land in 2023.
# The pounds do rise, late: GBP 3,531 (2021) -> 5,698 (2022) -> 11,342 (2023) on the accrual basis.
# The finding: SEAT_FINDING_THE_CRISIS_BAD_DEBT_CONTROL_HAS_SKIPPED_SINCE_THE_RUN_WENT_GZIP_AND_THE_PUBLISHED_RUN_SHOWS_NO_STEP_UP_2026-10-14.
# Strict, so the day a published run steps up on a basis, that leg XPASSes, the suite reds, and
# someone revisits this. NOT ESTABLISHED: that a step-up EMERGES from a household budget meeting the
# price shock rather than a tuned propensity (R12) -- the W2_4.. affordability cluster's question.
#
# THE WINDOW MOVED TO 2022-23 (2026-10-15): the real charge stepped up then, and 2021 was Centrica's
# low. Graded before the move was made, on the committed run: P&L accrual x1.02 (2.05% against
# 2.01%), headline x0.57. Both legs still fail, as pre-registered in the finding.
#
# The two legs fail for different reasons. The headline basis is the world's WRITE-OFFS, and the
# real record's write-offs did not step up in share either: Centrica wrote off GBP 58m, 93m and 113m
# in 2021-23 while revenue roughly doubled, and the charge rose through provisions, not write-offs.
# So the headline leg is graded against an anchor that describes a different quantity; its XPASS
# would itself be a fidelity question. The P&L accrual leg is the real gap: the real charge carries
# the provision movement in the year the arrears build, and ours dips in 2022.
_REARMED = ("the published run's crisis-years bad-debt share does not step up on this basis "
            "(2026-10-15, window 2022-23): P&L accrual x1.02, headline x0.57")
_WRITE_OFFS = ("the headline basis is write-offs, and the real record's write-offs did not step up "
               "in share either (Centrica GBP 58m, 93m, 113m in 2021-23 as revenue doubled)")


@pytest.mark.xfail(strict=True, reason=_WRITE_OFFS)
def test_live_run_output_shows_crisis_step_up_headline():
    result = validate_run_output(_published_run_or_skip(), "headline")
    assert result.passed, result.summary()


@pytest.mark.xfail(strict=True, reason=_REARMED)
def test_live_run_output_shows_crisis_step_up_pnl_accrual():
    result = validate_run_output(_published_run_or_skip(), "pnl_accrual")
    assert result.passed, result.summary()


def test_the_live_legs_read_the_gzipped_run_defect_a_plain_path_read_skips_silently(tmp_path, monkeypatch):
    """Only the .gz is committed. A reader of the plain path finds nothing there and skips, and a
    skipped live leg is a green one. With the plain file absent the run must still load."""
    import gzip
    import shutil
    import sys

    src = resolve_run_output(_RUN_OUTPUT)
    if src is None:
        pytest.skip("no published run in this checkout")
    plain = tmp_path / "run_output_latest.json"
    if src.suffix == ".gz":
        shutil.copy(src, tmp_path / src.name)
    else:
        with open(src, "rb") as fin, gzip.open(tmp_path / (plain.name + ".gz"), "wb") as fout:
            shutil.copyfileobj(fin, fout)
    assert not plain.exists()
    monkeypatch.setattr(sys.modules[__name__], "_RUN_OUTPUT", plain, raising=True)
    try:
        run = _published_run_or_skip()
    except pytest.skip.Exception as skipped:
        pytest.fail(f"the live legs skip in a gz-only checkout: {skipped}")
    head_bd, _ = extract_series_from_run_output(run, "headline")
    assert 2022 in head_bd
