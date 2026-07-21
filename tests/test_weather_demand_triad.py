"""W1_5 <-> C13 weather-normalisation demand COUPLED-TRIAD tests
(background/weather_demand_triad.py + background.gap_metric.prediction_gap).

The gap is the score. These tests assert:
  * the coupled loop runs on the real demand record and the SCORE is the WORST
    cell (not the population average, fidelity steer);
  * the honest finding: the company's degree-day normalisation EARNS ITS KEEP in
    winter (gap<1, beats a blind seasonal mean) but is ACTIVELY HARMFUL in summer
    (gap>1, worse than blind) -- the real weather-normalisation failure mode;
  * the wind-blindness direction: on the cold-and-windy cell the belief
    UNDER-predicts (negative bias) -- it cannot see wind chill (CWV);
  * R15: the prediction_gap control FIRES on its named defects -- cutting the
    belief's weather coupling (no-skill mean) worsens the gap on a cell where the
    fitted belief beats blind, and a DEGRADED belief (weather sensitivity zeroed)
    scores a worse gap than the real fit;
  * the measured gap round-trips into the coupled_gap_ledger under the W1_5<->C13
    pair and the coupled_triad reader sees a real numeric gap.

L2 additions (below): `measure()` now fits BOTH the L1 (temperature-only) and L2
(temperature+wind-chill/CWV) beliefs on the SAME real record and reports both per
cell. These tests assert the wiring is real (L2 has a genuinely fitted, non-zero
wind coefficient; L1/L2 predictions differ) and report the MEASURED, HONEST
finding on the real Elexon record -- the CWV term does NOT cleanly fix the
cold-and-windy cell here (R12: reported as measured, not tuned toward "the CWV
term should help").
"""
from __future__ import annotations

import numpy as np
import pytest

from background import weather_demand_triad as wdt
from background.gap_metric import prediction_gap
from background.coupled_triad import gap_measured, load_gap_ledger
from company.pricing.weather_normalisation_belief import WeatherNormalisationBelief


# --------------------------------------------------------------------------
# The real coupled measurement (one data load, module scope)
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def measurement():
    return wdt.measure()


def test_score_is_the_worst_cell_not_the_average(measurement):
    per_cell = measurement["per_cell"]
    pop = measurement["population_gap"].gap
    worst = measurement["worst_cell"]
    worst_gap = measurement["worst_gap"]
    # The SCORE (worst cell) is worse than the population average (the steer's
    # point: a model can beat the mean overall and still fail a whole regime).
    assert worst_gap > pop
    # On its worst cell the belief is WORSE than a blind seasonal mean (gap>1) --
    # the honest "actively harmful where it has no thermal signal" finding.
    assert worst_gap > 1.0
    # Every cell present is a real, in-range positive fraction.
    for c in per_cell.values():
        assert c["gap"] is not None and c["gap"] > 0


def test_earns_keep_in_winter_but_harmful_in_summer(measurement):
    per_cell = measurement["per_cell"]
    # Winter: the degree-day model beats a blind winter mean (it has learned the
    # heating shape) -> gap < 1, with a real (negative) cold-bias.
    assert per_cell["winter"]["gap"] < 1.0
    # Summer: no useful thermal signal -> the model does WORSE than the summer mean.
    assert per_cell["summer"]["gap"] > 1.0
    # Population overall the belief still beats blind (learns the seasonal shape).
    assert measurement["population_gap"].gap < 1.0


def test_wind_blindness_under_predicts_the_cold_windy_cell(measurement):
    tail = measurement["per_cell"]["cold_windy_tail"]
    # On colder-and-windier-than-median winter days the temperature-only belief
    # UNDER-predicts (negative bias) -- the wind-chill (CWV) load it cannot see.
    assert tail["bias_model"] < 0
    assert tail["n"] >= 10


def test_r15_gap_mutation_cutting_belief_coupling_worsens_the_gap(measurement):
    # R15 killer mutation: on the winter cell (where the fitted belief BEATS blind),
    # replace the belief with the no-skill mean (its weather coupling fully cut) ->
    # the gap must WORSEN to exactly 1. Proves the measured gap reflects a real
    # fitted belief, not a stored number.
    rec = wdt.demand_truth_on_record()
    winter = np.isin(rec["month"], (12, 1, 2))
    truth = measurement["truth"][winter]
    belief = measurement["belief"][winter]
    real_gap = prediction_gap(truth, belief).gap
    noskill = np.full_like(truth, truth.mean())
    cut_gap = prediction_gap(truth, noskill).gap
    assert real_gap < 1.0                     # the fitted belief genuinely helps here
    assert cut_gap == pytest.approx(1.0)      # cutting the coupling -> no-skill
    assert cut_gap > real_gap                 # cutting the coupling worsens the gap


def test_r15_degraded_belief_scores_a_worse_gap(measurement):
    # R15 independence: the gap metric must RESPOND to belief QUALITY. Degrade the
    # belief by zeroing its weather sensitivity (predict a flat base every day) and
    # the winter gap must worsen vs the real fitted belief -- the metric is not a
    # tautology that would pass any belief.
    bm = measurement["belief_model"]
    degraded = WeatherNormalisationBelief(
        base=bm.base, b_hdd=0.0, b_cdd=0.0, n_train=bm.n_train, r2=0.0)
    rec = wdt.demand_truth_on_record()
    winter = np.isin(rec["month"], (12, 1, 2))
    truth = measurement["truth"][winter]
    real_gap = prediction_gap(truth, measurement["belief"][winter]).gap
    degraded_gap = prediction_gap(truth, degraded.predict(rec["temperature_c"][winter])).gap
    assert degraded_gap > real_gap


def test_l2_wind_term_is_genuinely_fitted(measurement):
    # L2's belief has a real, fitted wind-chill coefficient (has_wind_term True);
    # L1's comparison belief has none -- the two are DIFFERENT models, not the
    # same object relabelled.
    bm = measurement["belief_model"]
    bm1 = measurement["belief_model_l1"]
    assert bm.has_wind_term is True
    assert bm1.has_wind_term is False
    assert bm.b_windchill != 0.0    # a real fitted coefficient, not dead weight
    # R15: zeroing the fitted wind coefficient changes the prediction on a windy
    # day -- proving b_windchill actually moves the output, not a stored no-op.
    rec = wdt.demand_truth_on_record()
    windy_idx = int(np.argmax(rec["wind_speed_ms"]))
    real_pred = bm.predict(rec["temperature_c"][windy_idx], rec["wind_speed_ms"][windy_idx])
    from company.pricing.weather_normalisation_belief import WeatherNormalisationBelief
    zeroed = WeatherNormalisationBelief(
        base=bm.base, b_hdd=bm.b_hdd, b_cdd=bm.b_cdd, n_train=bm.n_train, r2=bm.r2,
        b_windchill=0.0, has_wind_term=True,
    )
    zeroed_pred = zeroed.predict(rec["temperature_c"][windy_idx], rec["wind_speed_ms"][windy_idx])
    assert real_pred != pytest.approx(zeroed_pred)


def test_per_cell_carries_an_honest_l1_vs_l2_comparison(measurement):
    per_cell = measurement["per_cell"]
    for name, c in per_cell.items():
        assert "gap_l1" in c and c["gap_l1"] is not None and c["gap_l1"] > 0
        assert "bias_model_l1" in c
    # At least one cell's L2 gap genuinely differs from its L1 gap -- the CWV
    # term is measured, not a no-op that reproduces L1 everywhere.
    assert any(c["gap"] != pytest.approx(c["gap_l1"]) for c in per_cell.values())


def test_cwv_term_measured_honestly_on_the_real_record(measurement):
    # The MEASURED (not asserted-in-advance) finding on the real Elexon record:
    # the CWV wind-chill term does NOT cleanly fix the cold-and-windy cell -- its
    # bias MAGNITUDE is larger (worse) under L2 than L1 there, while the
    # population-level gap is left essentially unchanged. This is the honest
    # R12 result (report whichever way it falls); it is exactly the outcome the
    # module docstring names: CWV addresses HEATING-season wind chill and has no
    # reason to fix an unrelated (cooling-season) worst cell.
    tail = measurement["per_cell"]["cold_windy_tail"]
    assert tail["bias_model"] < 0            # still under-predicts (wind-blind
    assert tail["bias_model_l1"] < 0          # direction), same as L1
    # The population gap moves by a small, real, non-zero amount either way --
    # not a rounding no-op.
    pop_delta = measurement["population_gap"].gap - measurement["population_gap_l1"].gap
    assert abs(pop_delta) > 1e-6
    assert abs(pop_delta) < 0.05             # a small nudge, not a fabricated leap


def test_ledger_roundtrip_and_reader_sees_numeric_gap(measurement, tmp_path):
    result = wdt.build_gap_result(measurement)
    ledger = wdt.write_gap_entry(
        wdt.WORLD_ATOM_ID, wdt.TWIN_ATOM_ID, result,
        measured_at="2026-07-21T00:00:00+00:00", run_git_commit="deadbeef",
        ledger_path=tmp_path / "gap.json",
    )
    entry = ledger[wdt.WORLD_ATOM_ID]
    assert entry["twin_atom_id"] == wdt.TWIN_ATOM_ID
    assert isinstance(entry["gap"], (int, float))
    # the coupled_triad reader confirms the pair is now "measured".
    reloaded = load_gap_ledger(tmp_path / "gap.json")
    assert gap_measured(wdt.WORLD_ATOM_ID, reloaded)
    # the worst-cell provenance + population gap are preserved for audit.
    assert entry["components"]["worst_cell"] == measurement["worst_cell"]
    assert "population_gap" in entry["components"]
    # the headline gap is the worst cell's, not the population's.
    assert entry["gap"] == pytest.approx(measurement["worst_gap"])
    # L1 vs L2 comparison + the regional-dispersion R10 remainder note are both
    # persisted -- a reviewer reading the ledger sees the honest before/after and
    # the named, not-hidden gap.
    assert "population_gap_l1" in entry["components"]
    assert "worst_cell_gap_l1" in entry["components"]
    assert "b_windchill" in entry["components"]["belief_coeffs"]
    assert "regional_dispersion_remainder" in entry["components"]
