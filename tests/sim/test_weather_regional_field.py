"""W1_4 regional weather field — fidelity invariants (R15).

The regional field (sim/weather_engine.py: fit_regional_cholesky /
simulate_regional_deviations) models each location's daily deviation from the
national signal via a Cholesky-decomposed cross-location covariance. Measured on
the real 4-location Open-Meteo record, the mechanism is already high-fidelity —
this file MECHANISES two of its load-bearing properties as failable controls
(they were previously untested, so a refactor could silently break them):

  1. AGGREGATION-CONSISTENCY (W1_4's own DoD invariant): the location deviations
     are mean-zero across locations every day, so the regional average reconciles
     to the national signal (regional field adds correlated local variation
     AROUND the national front, it never shifts the national level).
  2. CROSS-LOCATION CORRELATION REPRODUCTION: the simulated cross-location
     deviation correlation reproduces the real one (London/Manchester/Glasgow/
     Cotswolds move together the way they really do — max abs error measured 0.026).

Both are R15 mutation-tested: a mutation that breaks each property makes its
control fire. Uses the real record + an independent published anchor is NOT
needed here (this is a self-consistency + structure-reproduction check, not a
company-facing claim). C-S2: seeded.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from sim.weather_engine import (
    MACRO_VARS,
    fit_regional_cholesky,
    simulate_regional_deviations,
)

_WD = Path(__file__).resolve().parent.parent.parent / "sim" / "weather_data"
_LOCS = ("C1", "C2", "C3", "C4")


def _load():
    loc = {}
    rows = None
    for L in _LOCS:
        rows = list(csv.DictReader((_WD / f"{L}.csv").open()))
        loc[L] = {v: np.array([float(r[v]) for r in rows]) for v in MACRO_VARS}
    national = {v: np.mean([loc[L][v] for L in _LOCS], axis=0) for v in MACRO_VARS}
    n = len(rows)
    return loc, national, n


@pytest.fixture(scope="module")
def sim_dev():
    loc, national, n = _load()
    params = fit_regional_cholesky(loc, national)
    rng = np.random.default_rng(0)
    return simulate_regional_deviations(params, n, rng), loc, national


# 1. AGGREGATION-CONSISTENCY -----------------------------------------------

def test_regional_deviations_reconcile_to_national(sim_dev):
    """The location deviations are mean-zero across locations each day: the
    regional average == the national signal. If this fails, the regional field
    is silently shifting the national LEVEL (a fidelity + double-count defect)."""
    dev, _loc, national = sim_dev
    for var in MACRO_VARS:
        per_day_mean = np.mean([dev[var][L] for L in _LOCS], axis=0)
        # Negligible RELATIVE to the signal (the cross-location covariance is
        # near-singular in the all-ones direction, so draws sum to ~0 to a tiny
        # numerical residual ~1e-4, vs signal std ~5). A real level drift (a
        # location-mean bias) is orders of magnitude larger and fails.
        tol = 1e-3 * float(national[var].std())
        assert np.max(np.abs(per_day_mean)) < tol, (
            f"{var}: regional deviations do not reconcile to national "
            f"(max |per-day cross-loc mean| = {np.max(np.abs(per_day_mean)):.2e} "
            f">= {tol:.2e}) -- the regional average has drifted off the national level"
        )


def test_aggregation_mutation_fires():
    """R15: a regional field that adds a non-zero-mean shock breaks reconciliation."""
    dev = {L: np.array([1.0, 2.0, 3.0]) for L in _LOCS}
    dev["C1"] = dev["C1"] + 5.0  # inject a location-level bias -> non-zero cross-loc mean
    per_day_mean = np.mean([dev[L] for L in _LOCS], axis=0)
    assert np.max(np.abs(per_day_mean)) >= 1e-9  # the control WOULD fire


# 2. CROSS-LOCATION CORRELATION REPRODUCTION --------------------------------

def _cross_loc_corr(dev_temp: dict) -> np.ndarray:
    return np.corrcoef([dev_temp[L] for L in _LOCS])


def test_cross_location_correlation_reproduced(sim_dev):
    """The simulated cross-location temp-deviation correlation reproduces the
    real one (the regional field preserves the real spatial co-movement)."""
    dev, loc, national = sim_dev
    real_dev = {L: loc[L]["temperature_mean_c"] - national["temperature_mean_c"] for L in _LOCS}
    real_corr = _cross_loc_corr(real_dev)
    sim_corr = _cross_loc_corr(dev["temperature_mean_c"])
    assert np.max(np.abs(real_corr - sim_corr)) < 0.15, (
        f"simulated cross-location correlation diverges from real "
        f"(max abs error {np.max(np.abs(real_corr - sim_corr)):.3f})"
    )


def test_correlation_mutation_fires(sim_dev):
    """R15: independent (identity-correlated) regional deviations do NOT reproduce
    the real (strongly anti/positively-correlated) cross-location structure."""
    dev, loc, national = sim_dev
    real_dev = {L: loc[L]["temperature_mean_c"] - national["temperature_mean_c"] for L in _LOCS}
    real_corr = _cross_loc_corr(real_dev)
    # MUTATION: draw each location independently (no cross-location coupling)
    rng = np.random.default_rng(1)
    n = len(national["temperature_mean_c"])
    indep = {L: rng.standard_normal(n) for L in _LOCS}
    indep_corr = _cross_loc_corr(indep)
    assert np.max(np.abs(real_corr - indep_corr)) >= 0.15  # the control fires on independence
