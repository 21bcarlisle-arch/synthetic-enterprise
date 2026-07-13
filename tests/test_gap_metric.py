"""Tests for background/gap_metric.py -- the WRITE side of the coupled triad
(atom A6_coupled_triad_gap_metric).

L2 acceptance (task): the metric computes correctly on a synthetic coupled pair
with known theta,b -- PERFECT belief -> gap 0, BLIND belief -> gap ~1, and a MID
case in between -- for each of the metric families the design names. Plus: the
ledger write matches the contract coupled_triad.py reads, and the module never
calls a clock (measured_at/run_git_commit passed in). Deterministic throughout.
"""

import json

import pytest

from background import gap_metric as gm
from background import coupled_triad as ct


# ===========================================================================
# (a) Classification-accuracy gap -- can't-pay vs won't-pay 2x2 (W2_7)
# ===========================================================================

# A synthetic population with a known hidden truth theta. Mixed quadrants so the
# majority-class baseline is non-degenerate (g0 > 0).
_TRUTH = [
    ("can", "will"),      # pays fine
    ("can", "will"),
    ("can", "will"),
    ("cannot", "will"),   # can't-pay, willing -> vulnerable
    ("cannot", "will"),
    ("can", "wont"),      # strategic defaulter
    ("cannot", "wont"),   # can't and won't
    ("can", "will"),
]


def test_classification_perfect_belief_gap_zero():
    perfect = list(_TRUTH)                 # b == theta
    r = gm.classification_gap(_TRUTH, perfect)
    assert r.gap == 0.0
    assert r.raw_gap == 0.0
    assert r.components["fn_ability"] == 0.0
    assert r.components["fn_willingness"] == 0.0


def test_classification_blind_belief_gap_one():
    # Blind = always predict the majority quadrant. gap must be exactly 1.0
    # (raw_gap == g0 by construction).
    counts = {}
    for t in _TRUTH:
        counts[t] = counts.get(t, 0) + 1
    majority = max(counts, key=lambda q: counts[q])
    blind = [majority] * len(_TRUTH)
    r = gm.classification_gap(_TRUTH, blind)
    assert r.gap == pytest.approx(1.0)


def test_classification_mid_case_between_zero_and_one():
    # Get 6/8 right, miss 2 -> gap strictly between 0 and 1.
    belief = list(_TRUTH)
    belief[3] = ("can", "will")     # a cannot->can miss (the harmful direction)
    belief[5] = ("can", "will")     # a willingness miss
    r = gm.classification_gap(_TRUTH, belief)
    assert r.gap is not None
    assert 0.0 < r.gap < 1.0


def test_classification_harm_asymmetry_is_8_to_1():
    # One entity. Treating a truly-cannot household as able (harmful) costs 8x
    # the mirror error. This proves the R13 8:1 curriculum weight is live.
    harm = gm.classification_gap([("cannot", "will")], [("can", "will")]).raw_gap
    loss = gm.classification_gap([("can", "will")], [("cannot", "will")]).raw_gap
    assert harm == pytest.approx(gm.HARM_RATIO_R * loss)
    assert harm == pytest.approx(8.0)


def test_classification_fn_directional_components():
    # Two cannot-pay truths, both believed able-to-pay (ability=can) -> fn_ability
    # = 1.0 (every vulnerable case treated as able, the HARM path).
    truth = [("cannot", "will"), ("cannot", "will"), ("can", "will")]
    belief = [("can", "will"), ("can", "will"), ("can", "will")]
    r = gm.classification_gap(truth, belief)
    assert r.components["fn_ability"] == pytest.approx(1.0)


# ===========================================================================
# (b) Attribution-error gap -- DD confound (W2_10)
# ===========================================================================

def test_attribution_perfect_no_confound_gap_zero():
    # Company's naive effect equals the true causal effect -> gap 0.
    r = gm.attribution_gap(delta_naive=0.20, delta_true=0.20)
    assert r.gap == 0.0


def test_attribution_wholly_confound_gap_one():
    # True causal effect is zero -> the whole naive effect is artefact -> gap 1.
    r = gm.attribution_gap(delta_naive=0.20, delta_true=0.0)
    assert r.gap == pytest.approx(1.0)


def test_attribution_mid_case_half_confound():
    r = gm.attribution_gap(delta_naive=0.20, delta_true=0.10)
    assert r.gap == pytest.approx(0.5)


def test_attribution_zero_naive_effect_is_undefined_not_crash():
    r = gm.attribution_gap(delta_naive=0.0, delta_true=0.0)
    assert r.gap == 0.0            # both zero -> defined as perfect
    r2 = gm.attribution_gap(delta_naive=0.0, delta_true=0.1)
    assert r2.gap is None         # undefined baseline, flagged not fabricated


# ===========================================================================
# (c) Belief-error gap -- TV distance, population/budget (W2_2)
# ===========================================================================

def test_belief_perfect_gap_zero():
    truth = [0.5, 0.3, 0.2]
    r = gm.belief_gap(truth, list(truth))
    assert r.gap == 0.0


def test_belief_blind_prior_gap_one():
    truth = [0.5, 0.3, 0.2]
    prior = [0.33, 0.33, 0.34]        # the national/blind prior
    # Company believes exactly the prior -> gap == 1.0 (no book-specific info).
    r = gm.belief_gap(truth, list(prior), prior=prior)
    assert r.gap == pytest.approx(1.0)


def test_belief_mid_case_between():
    truth = [0.5, 0.3, 0.2]
    prior = [0.33, 0.33, 0.34]
    belief = [0.45, 0.32, 0.23]       # closer to truth than the prior is
    r = gm.belief_gap(truth, belief, prior=prior)
    assert r.gap is not None
    assert 0.0 < r.gap < 1.0


def test_belief_raw_tv_when_no_prior():
    truth = [0.6, 0.4]
    belief = [0.4, 0.6]
    r = gm.belief_gap(truth, belief)       # no prior -> gap = raw TV
    assert r.gap == pytest.approx(0.2)     # 0.5*(0.2+0.2)


def test_belief_rejects_non_distribution():
    with pytest.raises(ValueError):
        gm.belief_gap([0.5, 0.4], [0.5, 0.5])   # truth doesn't sum to 1


# ===========================================================================
# (d) Detection-rate + false-negative-harm gap -- self-rationing (W2_8)
# ===========================================================================

def test_detection_perfect_gap_zero():
    S = {"a", "b", "c"}
    r = gm.detection_gap(truth_set=S, flagged_set=S)   # flags all
    assert r.gap == 0.0
    assert r.components["miss_rate"] == 0.0


def test_detection_flag_nobody_gap_one():
    S = {"a", "b", "c"}
    r = gm.detection_gap(truth_set=S, flagged_set=set())
    assert r.gap == pytest.approx(1.0)
    assert r.components["miss_rate"] == pytest.approx(1.0)


def test_detection_harm_weighting_beats_flat_miss():
    # Miss one of three accounts, but it's the SEVERE one. Harm-weighted gap must
    # exceed the flat miss rate (1/3): a missed severe case costs more.
    S = {"a", "b", "c"}
    harm = {"a": 8.0, "b": 1.0, "c": 1.0}
    flagged = {"b", "c"}                     # caught the two cheap ones, missed 'a'
    r = gm.detection_gap(truth_set=S, flagged_set=flagged, harm=harm)
    assert r.components["miss_rate"] == pytest.approx(1 / 3)
    assert r.gap == pytest.approx(8.0 / 10.0)     # 0.8 -- harm-weighted
    assert r.gap > r.components["miss_rate"]


def test_detection_uniform_harm_equals_miss_rate():
    S = {"a", "b", "c", "d"}
    flagged = {"a", "b"}
    r = gm.detection_gap(truth_set=S, flagged_set=flagged)   # no harm -> uniform
    assert r.gap == pytest.approx(r.components["miss_rate"])
    assert r.gap == pytest.approx(0.5)


# ===========================================================================
# Ledger write -- the contract coupled_triad.py reads
# ===========================================================================

def test_write_gap_entry_matches_reader_contract(tmp_path):
    path = tmp_path / "coupled_gap_ledger.json"
    r = gm.classification_gap(_TRUTH, list(_TRUTH))   # perfect -> gap 0.0
    ledger = gm.write_gap_entry(
        "W2_7_willingness_classification", "C9_cantpay_wontpay_classifier", r,
        measured_at="2026-07-13T00:00:00Z", run_git_commit="deadbeef",
        ledger_path=path,
    )
    # File persisted and reloadable.
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk == ledger
    entry = on_disk["W2_7_willingness_classification"]
    assert entry["twin_atom_id"] == "C9_cantpay_wontpay_classifier"
    assert entry["gap"] == 0.0
    assert entry["measured_at"] == "2026-07-13T00:00:00Z"
    assert entry["run_git_commit"] == "deadbeef"
    assert "baseline" in entry

    # The READER (coupled_triad.py) agrees a non-null numeric gap is "measured".
    reloaded = ct.load_gap_ledger(path)
    assert ct.gap_measured("W2_7_willingness_classification", reloaded) is True


def test_write_gap_entry_preserves_other_entries(tmp_path):
    path = tmp_path / "coupled_gap_ledger.json"
    path.write_text(json.dumps({"W2_8_self_rationing": {"gap": 0.5}}),
                    encoding="utf-8")
    r = gm.attribution_gap(0.2, 0.1)
    ledger = gm.write_gap_entry("W2_10_dd_attribution_confound", "C12_x", r,
                                ledger_path=path)
    assert "W2_8_self_rationing" in ledger        # untouched
    assert "W2_10_dd_attribution_confound" in ledger


def test_write_gap_entry_defaults_no_clock(tmp_path):
    # measured_at/run_git_commit default to None -- the module never calls a clock.
    path = tmp_path / "coupled_gap_ledger.json"
    r = gm.belief_gap([0.5, 0.5], [0.5, 0.5])
    ledger = gm.write_gap_entry("W2_2_population_draw", "C6_x", r, ledger_path=path)
    entry = ledger["W2_2_population_draw"]
    assert entry["measured_at"] is None
    assert entry["run_git_commit"] is None


def test_write_gap_entry_overwrites_malformed_ledger(tmp_path):
    path = tmp_path / "coupled_gap_ledger.json"
    path.write_text("{ not json", encoding="utf-8")
    r = gm.belief_gap([1.0], [1.0])
    ledger = gm.write_gap_entry("W2_2_population_draw", "C6_x", r, ledger_path=path)
    assert "W2_2_population_draw" in ledger
    assert json.loads(path.read_text(encoding="utf-8")) == ledger


# ===========================================================================
# Determinism: bootstrap CI seeded from a named substream (C-S2)
# ===========================================================================

def test_bootstrap_ci_is_deterministic_and_brackets_point():
    point1, lo1, hi1 = gm.bootstrap_gap_ci(
        gm.classification_gap, _TRUTH, list(_TRUTH),
        substream="A6_gap_metric_test", n_resamples=200)
    point2, lo2, hi2 = gm.bootstrap_gap_ci(
        gm.classification_gap, _TRUTH, list(_TRUTH),
        substream="A6_gap_metric_test", n_resamples=200)
    assert (point1, lo1, hi1) == (point2, lo2, hi2)   # reproducible (C-S2)
    assert lo1 <= point1 <= hi1


def test_bootstrap_ci_named_substreams_differ():
    # Different named substreams draw different resamples (independence).
    _, lo_a, hi_a = gm.bootstrap_gap_ci(
        gm.classification_gap, _TRUTH,
        [("can", "will")] * len(_TRUTH),               # a noisy imperfect belief
        substream="stream_A", n_resamples=200)
    _, lo_b, hi_b = gm.bootstrap_gap_ci(
        gm.classification_gap, _TRUTH,
        [("can", "will")] * len(_TRUTH),
        substream="stream_B", n_resamples=200)
    # Not asserting a specific value -- just that the seeds are genuinely distinct.
    assert gm._substream_seed("stream_A") != gm._substream_seed("stream_B")


# ===========================================================================
# Real ledger stays empty (no fabricated gaps shipped) -- mirrors gate test
# ===========================================================================

def test_real_ledger_ships_empty():
    data = json.loads(gm.GAP_LEDGER_PATH.read_text(encoding="utf-8")) \
        if gm.GAP_LEDGER_PATH.is_file() else {}
    assert data == {}
