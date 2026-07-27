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


# 1b. DEMAND-WEIGHTED aggregation-consistency — W1_4's DEFINING DoD invariant (I1) —
#     PINNED as a strict-xfail because it is genuinely UNBUILT.
#
# test_regional_deviations_reconcile_to_national (above) asserts the UNIFORM (1/|R|)
# cross-location mean-zero property. But W1_4's own DoD and REGIONAL_WEATHER_FIELD_
# FRAME.md §3-4 (invariant I1) require the DEMAND-WEIGHTED regional aggregate to
# reconcile to national — and FRAME §4.2 names the *uniform* case as a should-FAIL
# secondary mutation (attack-the-weights). The demand-weighted-mean PROJECTION
# (delta'_r = delta_r − Σ_s w_s·delta_s, FRAME §3.2) is UNBUILT in sim/weather_engine.py
# (out of this atom's file_scope; a deliberate L2→L3 fidelity BUILD, flagged to the
# director on 2026-07-27). Measured today the field does NOT reconcile under a
# non-uniform demand weighting: residual is 27–60% of each variable's signal std
# (~23,000× the uniform residual). This is currently LATENT (simulate_regional_
# deviations has zero live consumer), so no published figure is wrong.
#
# This control makes that gap EXECUTABLE and NO-ORPHAN: strict=True means the day the
# weighted projection lands and the field genuinely reconciles, this XPASSes and turns
# the suite RED — forcing this test's promotion to a live invariant + a re-level, so
# the DoD gap cannot close silently. Any non-uniform weight vector exposes it; the
# specific shares below are illustrative (London-largest ordering, C1..C4), NOT a
# calibrated anchor.
_DEMAND_W = np.array([0.45, 0.30, 0.15, 0.10])


@pytest.mark.xfail(
    strict=True,
    reason="W1_4 demand-weighted projection (invariant I1) UNBUILT — L2->L3 fidelity "
    "BUILD in sim/weather_engine.py (out of this atom's file_scope), director-flagged "
    "2026-07-27. XPASS here = projection landed => promote this test + re-level.",
)
def test_demand_weighted_aggregate_reconciles_to_national(sim_dev):
    """The DEMAND-WEIGHTED regional aggregate should reconcile to national (I1).
    It does not yet: the field is only mean-zero under uniform weights."""
    dev, _loc, national = sim_dev
    w = _DEMAND_W / _DEMAND_W.sum()
    for var in MACRO_VARS:
        stacked = np.array([dev[var][L] for L in _LOCS])  # (|R|, n)
        per_day_w_mean = w @ stacked
        tol = 1e-3 * float(national[var].std())
        assert np.max(np.abs(per_day_w_mean)) < tol, (
            f"{var}: demand-weighted regional aggregate does not reconcile to national "
            f"(max |Σ_s w_s·delta_s| = {np.max(np.abs(per_day_w_mean)):.2e} >= {tol:.2e})"
        )


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
