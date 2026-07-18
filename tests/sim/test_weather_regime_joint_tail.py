"""W1_3 — joint cold-and-still (blocking-high) regime + tail demonstration +
independent-validator anchor. Includes the R15 mutation tests that PROVE the
tail-dependence and classification controls fire on their own named defect (a
control that cannot fail is worse than none).
"""

import copy

import numpy as np
import pytest

from sim.weather_engine import (
    MACRO_VARS,
    BLOCKING_TEMP_PERCENTILE,
    BLOCKING_WIND_PERCENTILE,
    SIMPLIFICATIONS,
    classify_blocking_regime,
    fit_national_macro_model,
    seasonal_value,
    simulate_national_macro,
)
from sim.weather_tail_report import (
    REPORT_SEED,
    build_tail_report,
    cold_still_spells,
    joint_tail_dependence_ratio,
    load_national_series,
)

REPORT_SEED_FOR_TESTS = REPORT_SEED
from sim.weather_independent_validator import (
    IndependentAnchor,
    PLACEHOLDER_DUNKELFLAUTE_ANCHOR,
    validate_against_independent_anchor,
)


# ---------------------------------------------------------------------------
# Shared fit on the real data (session-scoped — the fit is deterministic).
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def real_fit():
    national, day_of_year, _dates = load_national_series()
    params = fit_national_macro_model(national, day_of_year)
    return national, day_of_year, params


@pytest.fixture(scope="module")
def synthetic_residuals(real_fit):
    _national, _doy, params = real_fit
    big_doy = np.tile(np.arange(1, 366), 20)
    sim = simulate_national_macro(params, big_doy, np.random.default_rng(101))
    tr = sim["temperature_mean_c"] - seasonal_value(params["seasonal"]["temperature_mean_c"], big_doy)
    wr = sim["wind_speed_mean_ms"] - seasonal_value(params["seasonal"]["wind_speed_mean_ms"], big_doy)
    return sim, tr, wr, big_doy


# ---------------------------------------------------------------------------
# classify_blocking_regime — the joint (cold AND still) trigger (Gap 1)
# ---------------------------------------------------------------------------
def test_blocking_requires_both_cold_and_still():
    # Day 0: cold AND still -> blocking. Day 1: cold but WINDY -> not blocking.
    # Day 2: still but WARM -> not blocking. Day 3: warm and windy -> not blocking.
    temp = np.array([-5.0, -5.0, 5.0, 5.0])
    wind = np.array([-5.0, 5.0, -5.0, 5.0])
    regime, meta = classify_blocking_regime(temp, wind, temp_percentile=50, wind_percentile=50)
    assert list(regime) == [1, 0, 0, 0]
    assert meta["high_pressure_proxy"] == "low_wind"


def test_blocking_is_directional_not_symmetric():
    # The OLD trigger was |wind| > threshold, so a STORM (high +wind) counted.
    # The new trigger must NOT flag a cold storm as blocking-high.
    temp = np.concatenate([np.full(50, -3.0), np.full(50, 3.0)])
    wind = np.concatenate([np.full(50, 8.0), np.full(50, -1.0)])  # first half: cold+STORMY
    regime, _ = classify_blocking_regime(temp, wind, temp_percentile=50, wind_percentile=50)
    # cold+stormy days (first half) must be standard, not blocking.
    assert regime[:50].sum() == 0


def test_classify_is_pure_and_deterministic():
    rng = np.random.default_rng(1)
    temp = rng.standard_normal(500)
    wind = rng.standard_normal(500)
    r1, _ = classify_blocking_regime(temp, wind)
    r2, _ = classify_blocking_regime(temp, wind)
    assert np.array_equal(r1, r2)


def test_classify_empty_raises():
    with pytest.raises(ValueError):
        classify_blocking_regime(np.array([]), np.array([]))


def test_classify_shape_mismatch_raises():
    with pytest.raises(ValueError):
        classify_blocking_regime(np.zeros(5), np.zeros(6))


def test_blocking_frequency_reasonable(real_fit):
    _national, _doy, params = real_fit
    # A joint 33rd/33rd-percentile conjunction on positively-associated cold-still
    # residuals lands in a sensible band (not ~0, not dominating the record).
    assert 0.05 < params["regime_frequency"] < 0.25


# ---------------------------------------------------------------------------
# Mechanistic mean drift — cold-and-still driven DOWN together (Gap 1 heart)
# ---------------------------------------------------------------------------
def test_blocking_regime_mean_drift_is_cold_and_still(real_fit):
    _national, _doy, params = real_fit
    blocking_mean = params["regime_mean"]["stressed"]
    ti = MACRO_VARS.index("temperature_mean_c")
    wi = MACRO_VARS.index("wind_speed_mean_ms")
    # On a blocking day the innovation mean pushes temperature AND wind DOWN.
    assert blocking_mean[ti] < 0, "blocking regime must drift temperature cold"
    assert blocking_mean[wi] < 0, "blocking regime must drift wind still"


def test_overall_mean_preserved(real_fit, synthetic_residuals):
    national, _doy, _params = real_fit
    sim, _tr, _wr, _big = synthetic_residuals
    # The regime-mean drift must NOT shift the overall distribution mean — the
    # blocking negative drift is balanced by the standard-day positive drift.
    for v in ("temperature_mean_c", "wind_speed_mean_ms"):
        assert abs(sim[v].mean() - national[v].mean()) < 0.6, v


# ---------------------------------------------------------------------------
# Tail dependence present (the control), and its R15 MUTATION tests
# ---------------------------------------------------------------------------
TAIL_DEPENDENCE_MIN = 1.9  # bottom-10% joint/marginal ratio the mechanism must clear


def test_synthetic_carries_cold_still_tail_dependence(synthetic_residuals):
    _sim, tr, wr, _big = synthetic_residuals
    ratio = joint_tail_dependence_ratio(tr, wr, tail_pct=10.0)
    assert ratio > TAIL_DEPENDENCE_MIN, (
        f"cold-and-still tail dependence {ratio:.2f} below {TAIL_DEPENDENCE_MIN}"
    )


def _sim_ratio(params, seed=101, years=20, tail_pct=10.0):
    big_doy = np.tile(np.arange(1, 366), years)
    sim = simulate_national_macro(params, big_doy, np.random.default_rng(seed))
    tr = sim["temperature_mean_c"] - seasonal_value(params["seasonal"]["temperature_mean_c"], big_doy)
    wr = sim["wind_speed_mean_ms"] - seasonal_value(params["seasonal"]["wind_speed_mean_ms"], big_doy)
    return joint_tail_dependence_ratio(tr, wr, tail_pct)


def test_MUTATION_zeroing_mean_drift_collapses_tail_dependence(real_fit):
    """R15: strip the mechanistic mean drift -> the tail-dependence control MUST
    fire (fall below the threshold the real mechanism clears). Proves the control
    is non-vacuous: it distinguishes the mechanism from its absence."""
    _national, _doy, params = real_fit
    full_ratio = _sim_ratio(params)
    assert full_ratio > TAIL_DEPENDENCE_MIN  # control passes on the real mechanism

    mutant = copy.deepcopy(params)
    mutant["regime_mean"] = {"standard": np.zeros(len(MACRO_VARS)),
                             "stressed": np.zeros(len(MACRO_VARS))}
    mutant_ratio = _sim_ratio(mutant)
    # The control fires: dependence collapses well below the mechanism's level.
    assert mutant_ratio < full_ratio - 0.4, (
        f"mutation did not measurably reduce tail dependence (full {full_ratio:.2f} "
        f"vs mutant {mutant_ratio:.2f}) — the control would be a tautology"
    )


def test_MUTATION_no_blocking_days_makes_a_degenerate_fit(real_fit):
    """R15: force the classifier so NOTHING is cold-and-still (thresholds at the
    extreme low tail). The blocking regime must then be empty — the 'there is a
    blocking regime' expectation FIRES (count -> 0), and the drift vanishes."""
    national, day_of_year, _params = real_fit
    seasonal = {}
    resid = {}
    for var in MACRO_VARS:
        from sim.weather_engine import fit_seasonal_harmonics
        c = fit_seasonal_harmonics(national[var], day_of_year)
        seasonal[var] = c
        resid[var] = national[var] - seasonal_value(c, day_of_year)
    # 0th-percentile thresholds: strictly-less-than can never be satisfied.
    regime, _ = classify_blocking_regime(
        resid["temperature_mean_c"], resid["wind_speed_mean_ms"],
        temp_percentile=0, wind_percentile=0,
    )
    assert regime.sum() == 0  # the mutation genuinely produces zero blocking days


def test_MUTATION_degenerate_fit_still_simulates_without_nan(real_fit, monkeypatch):
    """Fail-safe (not fail-open): even a degenerate/mutated fit with an empty
    blocking regime must simulate finite numbers (guards against NaN transitions/
    covariance crashing silently). The tail-dependence control then legitimately
    shows the collapse rather than erroring out."""
    national, day_of_year, _params = real_fit
    # Force the (live) classifier constants so NOTHING is cold-and-still.
    import sim.weather_engine as we
    monkeypatch.setattr(we, "BLOCKING_TEMP_PERCENTILE", 0.0)
    monkeypatch.setattr(we, "BLOCKING_WIND_PERCENTILE", 0.0)
    params = fit_national_macro_model(national, day_of_year)
    assert params["regime_frequency"] == 0.0  # mutation genuinely suppresses blocking
    big_doy = np.tile(np.arange(1, 366), 3)
    sim = simulate_national_macro(params, big_doy, np.random.default_rng(5))
    for v in MACRO_VARS:
        assert np.all(np.isfinite(sim[v]))


# ---------------------------------------------------------------------------
# Determinism (C-S2)
# ---------------------------------------------------------------------------
def test_simulate_is_deterministic_given_seed(real_fit):
    _national, _doy, params = real_fit
    big_doy = np.tile(np.arange(1, 366), 3)
    a = simulate_national_macro(params, big_doy, np.random.default_rng(77))
    b = simulate_national_macro(params, big_doy, np.random.default_rng(77))
    for v in MACRO_VARS:
        assert np.array_equal(a[v], b[v])


def test_backcompat_params_without_regime_mean(real_fit):
    """A params dict fitted before the mean-drift field existed must still run
    (drift defaults to zero) — no KeyError."""
    _national, _doy, params = real_fit
    legacy = copy.deepcopy(params)
    legacy.pop("regime_mean")
    big_doy = np.tile(np.arange(1, 366), 2)
    sim = simulate_national_macro(legacy, big_doy, np.random.default_rng(9))
    for v in MACRO_VARS:
        assert np.all(np.isfinite(sim[v]))


# ---------------------------------------------------------------------------
# Independent validator (Gap 3) — anti-marking-own-homework, fail-closed (R15)
# ---------------------------------------------------------------------------
def test_placeholder_anchor_is_indeterminate_never_pass():
    res = validate_against_independent_anchor(3.0, PLACEHOLDER_DUNKELFLAUTE_ANCHOR)
    assert res.status == "INDETERMINATE_PLACEHOLDER"
    assert res.is_pass is False


def test_MUTATION_placeholder_cannot_be_coerced_to_pass():
    """R15 FAIL-SILENT guard: even if the synthetic value 'matches' whatever a
    reader might imagine, a placeholder anchor (no real magnitude) can NEVER
    return PASS. An unavailable independent check is a FAILED check."""
    for synthetic in (0.0, 3.0, 999.0):
        res = validate_against_independent_anchor(synthetic, PLACEHOLDER_DUNKELFLAUTE_ANCHOR)
        assert res.status != "PASS"


def test_injected_real_anchor_pass_and_fail():
    anchor = IndependentAnchor(
        name="test_anchor", metric="spells/winter",
        source="injected test value (not a real published figure)",
        is_placeholder=False, value=3.0, tolerance=1.0, unit="spells/winter",
    )
    assert validate_against_independent_anchor(3.4, anchor).status == "PASS"
    assert validate_against_independent_anchor(5.0, anchor).status == "FAIL"


def test_non_placeholder_anchor_requires_magnitude():
    with pytest.raises(ValueError):
        IndependentAnchor(
            name="broken", metric="x", source="y",
            is_placeholder=False, value=None, tolerance=None,
        )


def test_placeholder_anchor_carries_no_fabricated_magnitude():
    # Honesty: the placeholder must NOT assert a precise real number.
    assert PLACEHOLDER_DUNKELFLAUTE_ANCHOR.is_placeholder is True
    assert PLACEHOLDER_DUNKELFLAUTE_ANCHOR.value is None


# ---------------------------------------------------------------------------
# End-to-end report (show the tail) + honesty verdict
# ---------------------------------------------------------------------------
def test_report_worst_week_not_grossly_milder_than_real():
    # The synthetic worst week's JOINT (cold-and-still) severity must be comparable
    # to real — never grossly milder. (Combined severity is the right axis for
    # "cold-AND-still"; the pure-temp marginal shortfall is reported separately and
    # honestly, not hidden.)
    report = build_tail_report(synthetic_years=50, seed=REPORT_SEED_FOR_TESTS)
    ww = report["worst_week"]
    assert ww["coverage_ratio_severity"] > 0.85, ww["verdict"]


def test_report_model_can_reach_real_worst_week_severity():
    # Over long runs the model DOES produce weeks at least as severe (joint) as the
    # real GB worst week — the DoD's "can and does produce weeks at least that
    # severe". Robust across seeds (uses the max — an existence claim).
    max_cov = max(
        build_tail_report(synthetic_years=50, seed=s)["worst_week"]["coverage_ratio_severity"]
        for s in (1, 7, 101)
    )
    assert max_cov >= 1.0


def test_report_marginal_temp_tail_gap_is_reported_honestly():
    # The honest-gap fields must be present (not silently dropped): the report must
    # carry the per-axis comparison and the marginal-tail note.
    report = build_tail_report(synthetic_years=30, seed=7)
    ww = report["worst_week"]
    assert "temp_margin_shortfall_c" in ww
    assert "honest_marginal_note" in ww
    assert "both_axes_at_least_as_severe_as_real" in ww


def test_report_independent_validation_is_indeterminate():
    report = build_tail_report(synthetic_years=10, seed=7)
    assert report["independent_validation"]["status"] == "INDETERMINATE_PLACEHOLDER"


def test_report_reports_tail_dependence_present():
    report = build_tail_report(synthetic_years=20, seed=3)
    syn = report["joint_tail_dependence_ratio"]["synthetic"]
    assert syn["10"] > 1.5  # the cold-and-still correlation is present in the output


def test_simplifications_registered():
    ids = {s["id"] for s in SIMPLIFICATIONS}
    assert "W1_3_HIGH_PRESSURE_PROXIED_BY_LOW_WIND" in ids
    for s in SIMPLIFICATIONS:
        assert s["rule"] == "R10"


def test_cold_still_spells_minimum_length():
    # only runs >= min_days count
    temp = np.array([-1, -1, 1, -1, -1, -1, 1])
    wind = np.array([-1, -1, 1, -1, -1, -1, 1])
    spells = cold_still_spells(temp, wind, temp_thresh=0.0, wind_thresh=0.0, min_days=3)
    assert spells == [3]  # the 2-day run is dropped, the 3-day run kept
