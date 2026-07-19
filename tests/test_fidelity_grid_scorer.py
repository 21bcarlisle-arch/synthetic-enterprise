"""Tests for background/fidelity_grid_scorer.py -- atom G1, the fidelity
grid-scorer (Epoch-2 fidelity-evidence machinery, HARNESS-side).

Per R15 ("a control that cannot fail is worse than none"), each of the three
measures carries a MUTATION test proving it fires on its own named defect --
not just a happy-path acceptance test. Grouped by measure:

    1. best-of-family lift    -- can't be gamed by a single weak baseline.
    2. worst-q% CVaR          -- q=0 recovers MAX exactly; a flood of good
                                  cells never dilutes the tail (mutation to a
                                  plain mean-over-all-cells must change the
                                  reading); the map of ignorance is fail-open
                                  and its own omission is caught.
    3. CRN-gated ablation     -- decorative couplings surface honestly; a
                                  Delta without proven substream isolation is
                                  REJECTED, never reported as a number.
"""

import math

import pytest

from background import fidelity_grid_scorer as fgs


# ===========================================================================
# MEASURE 1 -- best-of-family lift
# ===========================================================================

def test_best_of_family_error_is_the_minimum():
    errs = {"weak_strawman": 0.90, "ols_regression": 0.20, "persistence": 0.55}
    best_id, best_err = fgs.best_of_family_error(errs)
    assert best_id == "ols_regression"
    assert best_err == pytest.approx(0.20)


def test_best_of_family_error_empty_family_raises():
    with pytest.raises(ValueError):
        fgs.best_of_family_error({})


def test_cell_lift_uses_best_of_family_not_first_or_last():
    errs = {"weak_strawman": 0.90, "ols_regression": 0.20}
    r = fgs.cell_lift("price_incidence", "A4_G2", err_model=0.15, err_by_baseline=errs)
    assert r.best_baseline_id == "ols_regression"
    assert r.err_best_naive == pytest.approx(0.20)
    assert r.lift == pytest.approx(0.20 - 0.15)


def test_R15_killer_mutation_single_weak_baseline_cannot_inflate_lift():
    """R15 mutation: a 'model' that games lift by reporting only a single
    WEAK baseline (inflating apparent lift) must never beat -- must in fact
    never exceed -- the honest best-of-family lift. best-of-family is a MIN
    over the family, so family_lift <= lift-against-any-single-member always;
    the control MUST catch (i.e. structurally prevent) the gamed reading."""
    err_model = 0.15
    weak = {"weak_strawman": 0.90}          # the gamed, cherry-picked single baseline
    family = {"weak_strawman": 0.90, "ols_regression": 0.20, "persistence": 0.55}

    gamed_lift = fgs.single_baseline_lift(err_model, err_single_baseline=0.90)
    honest = fgs.cell_lift("price_incidence", "A4_G2", err_model, family)

    assert gamed_lift == pytest.approx(0.75)          # what the gamer would report
    assert honest.lift == pytest.approx(0.05)          # the real, un-gameable value
    # The un-gameable property: best-of-family lift can NEVER exceed the lift
    # computed against any single (possibly weak) family member.
    assert honest.lift <= gamed_lift
    assert honest.best_baseline_id != "weak_strawman"


def test_naive_baseline_families_are_hash_pinned_and_versioned():
    fam = fgs.NAIVE_BASELINE_FAMILIES["weather_cascade"]
    assert len(fam) >= 2
    ids = {b.baseline_id for b in fam}
    assert "independence" in ids
    # Same content -> same hash (deterministic, reproducible).
    dup = fgs.NaiveBaseline("independence", 1,
                            "draw each variable from its own marginal, couplings off (L=1)")
    original = next(b for b in fam if b.baseline_id == "independence")
    assert dup.content_hash == original.content_hash


def test_baseline_hash_changes_if_definition_changes_without_version_bump():
    """A baseline whose DEFINITION silently drifts (without a version bump)
    produces a DIFFERENT content hash -- the mechanism that makes a moved
    baseline visible rather than a silent Goodhart move (S1.1.1)."""
    original = fgs.NaiveBaseline("flat_prior", 1, "predict the book-average band")
    weakened = fgs.NaiveBaseline("flat_prior", 1, "predict the book-average band, but softer")
    assert original.content_hash != weakened.content_hash


# ===========================================================================
# MEASURE 2 -- worst-q% CVaR generalises MAX + map of ignorance
# ===========================================================================

def test_R15_q_zero_recovers_exact_max():
    severities = [0.10, 0.95, 0.40, 0.20, 0.05]
    aggregate, k, tail = fgs.grid_cvar(severities, q=0.0)
    assert k == 1
    assert aggregate == pytest.approx(max(severities))
    assert tail == [max(severities)]


def test_R15_good_cell_flood_never_dilutes_the_tail():
    """At a FIXED tail size (q chosen so k stays constant, matching the
    real bounded archetype x regime grid), driving the REST of the grid
    ever-closer to perfect ('flooding' in good cells) must not move the CVaR
    aggregate AT ALL -- only the top-k tail cells ever enter it. A population
    MEAN, by contrast, keeps collapsing toward the flood as those cells
    improve. This is the structural reason good cells "never dilute" the bad
    tail (S1.2 CONSTRUCT_CHALLENGE sharpen)."""
    q = 0.2
    # n=10, k = ceil(0.2*10) = 2 -- the top-2 worst cells are fixed at 0.95/0.80
    # in both grids; only the OTHER 8 cells (never in the tail) are flooded
    # with better and better values.
    mixed_grid = [0.95, 0.80] + [0.50] * 8
    flooded_grid = [0.95, 0.80] + [0.01] * 8

    agg_mixed, k_mixed, tail_mixed = fgs.grid_cvar(mixed_grid, q=q)
    agg_flooded, k_flooded, tail_flooded = fgs.grid_cvar(flooded_grid, q=q)

    assert k_mixed == k_flooded == 2
    # The CVaR aggregate is IDENTICAL regardless of the flood -- the tail
    # never sees the flooded cells.
    assert agg_mixed == pytest.approx(0.875)
    assert agg_flooded == pytest.approx(0.875)
    assert agg_mixed == agg_flooded

    # The mean-over-all-cells (the forbidden mutation), in stark contrast,
    # collapses as the flood improves -- proving CVaR is doing real,
    # flood-resistant work rather than silently degenerating into a mean.
    mean_mixed = sum(mixed_grid) / len(mixed_grid)
    mean_flooded = sum(flooded_grid) / len(flooded_grid)
    assert mean_flooded < mean_mixed
    assert agg_flooded != pytest.approx(mean_flooded, abs=0.1)


def test_R15_mutation_to_plain_mean_changes_the_result():
    """Direct mutation test: swap grid_cvar's tail-mean for a population mean
    over ALL cells and confirm the reading changes -- i.e. the two are
    provably different constructs, not accidentally the same computation."""
    severities = [0.95] + [0.02] * 29   # one bad cell in a sea of good ones
    cvar_agg, _, _ = fgs.grid_cvar(severities, q=0.1)
    mean_agg = sum(severities) / len(severities)
    assert cvar_agg != pytest.approx(mean_agg)
    assert cvar_agg > mean_agg   # the tail-mean must read WORSE than the diluted mean


def test_unmeasured_cell_scores_top_severity():
    cells = [
        fgs.CellEvidence("A5_G1", measured=True, gap=0.10),
        fgs.CellEvidence("A5_G2", measured=True, gap=0.20),
        fgs.CellEvidence("A3_G3", measured=False, ignorance="missing_physics"),
    ]
    score = fgs.score_grid(cells, q=0.1)
    assert score.worst_cell == "A3_G3"
    assert score.severities["A3_G3"] >= max(0.10, 0.20)


def test_unmeasured_cell_with_no_measured_peers_uses_ignorance_floor():
    cells = [fgs.CellEvidence("A3_G3", measured=False, ignorance="untested")]
    score = fgs.score_grid(cells, q=0.1)
    assert score.severities["A3_G3"] == pytest.approx(fgs.IGNORANCE_FLOOR_NO_MEASURED)


def test_R15_killer_mutation_worst_cell_beats_mean_on_one_blind_edge():
    """The atom-A canonical mutation, re-run through this scorer: 14 near-
    perfect cells (gap~0.1) and one blind edge (gap~0.95). A MEAN reads ~0.16
    (looks great -- the bug); the worst-cell/CVaR-at-q=0 reading MUST read
    ~0.95 -- FAIL, correctly."""
    gaps = [0.1] * 14 + [0.95]
    mean_reading = sum(gaps) / len(gaps)
    worst_reading, _, _ = fgs.grid_cvar(gaps, q=0.0)
    assert mean_reading == pytest.approx(0.16, abs=0.02)
    assert worst_reading == pytest.approx(0.95)
    assert worst_reading > mean_reading


def test_R15_map_of_ignorance_completeness_guard_catches_omission():
    """R15 mutation: a coverage function that DROPS an unmeasured cell from
    the map (silent pass, exactly the hidden-blind-spot defect) MUST be
    caught by the completeness guard."""
    cells = [
        fgs.CellEvidence("A5_G1", measured=True, gap=0.10),
        fgs.CellEvidence("A3_G3", measured=False, ignorance="missing_physics"),
        fgs.CellEvidence("A3_G2", measured=False, ignorance="untested"),
    ]
    honest_map = fgs.build_map_of_ignorance(cells)
    # Honest map passes.
    fgs.assert_map_of_ignorance_complete(cells, honest_map)

    # Mutated map: silently omit one unmeasured cell (the defect).
    mutated_map = tuple(e for e in honest_map if e.cell_id != "A3_G3")
    with pytest.raises(AssertionError):
        fgs.assert_map_of_ignorance_complete(cells, mutated_map)


def test_score_grid_always_carries_map_of_ignorance_even_when_empty():
    cells = [fgs.CellEvidence("A5_G1", measured=True, gap=0.10)]
    score = fgs.score_grid(cells, q=0.1)
    assert score.map_of_ignorance == ()   # present, just empty -- never absent as a field


def test_grid_cvar_empty_input_fails_loud():
    with pytest.raises(ValueError):
        fgs.grid_cvar([])


def test_cell_evidence_rejects_measured_without_gap():
    with pytest.raises(ValueError):
        fgs.CellEvidence("A5_G1", measured=True, gap=None)


def test_cell_evidence_rejects_unmeasured_without_ignorance_kind():
    with pytest.raises(ValueError):
        fgs.CellEvidence("A3_G3", measured=False, ignorance="not_a_real_kind")


# ===========================================================================
# MEASURE 3 -- CRN-gated ablation Delta
# ===========================================================================

def test_ablation_load_bearing_when_cutting_erases_the_crisis():
    live = {"A2_G3": 0.90, "A5_G1": 0.10}
    cut = {"A2_G3": 0.20, "A5_G1": 0.10}   # cutting the coupling erases the crisis gap
    r = fgs.compute_ablation("D1_temp_wind", live, cut, crn_substream_isolated=True)
    assert r.verdict == "load_bearing"
    assert r.delta_by_cell["A2_G3"] == pytest.approx(0.70)


def test_R15_killer_mutation_A_decorative_coupling_surfaces_honestly():
    """A coupling that is wired but INERT (cutting it changes nothing) must
    be reported verdict='decorative', never silently kept as if load-bearing
    and never hidden."""
    live = {"A2_G3": 0.50, "A5_G1": 0.10}
    cut = {"A2_G3": 0.50, "A5_G1": 0.10}   # identical outcome -- the coupling does nothing
    r = fgs.compute_ablation("decorative_seam", live, cut, crn_substream_isolated=True)
    assert r.verdict == "decorative"
    assert r.delta_worst_cell == pytest.approx(0.0)


def test_R15_killer_mutation_B_ablation_without_crn_is_rejected_not_reported():
    """The CRN guard: an ablation Delta computed WITHOUT proven substream
    isolation must be REJECTED outright -- never returned as a plain number
    a caller could mistake for a valid reading (S1.3/S5 killer-mutation-B)."""
    live = {"A2_G3": 0.90, "A5_G1": 0.10}
    cut = {"A2_G3": 0.20, "A5_G1": 0.10}
    with pytest.raises(fgs.InvalidAblation):
        fgs.compute_ablation("D1_temp_wind", live, cut, crn_substream_isolated=False)


def test_ablation_fail_open_empty_outcome_sample():
    with pytest.raises(fgs.InvalidAblation):
        fgs.compute_ablation("k", {}, {"A5_G1": 0.1}, crn_substream_isolated=True)


def test_ablation_fail_open_mismatched_cell_sets():
    with pytest.raises(fgs.InvalidAblation):
        fgs.compute_ablation(
            "k", {"A5_G1": 0.1}, {"A2_G3": 0.1}, crn_substream_isolated=True
        )


def test_ablation_fail_loud_on_nan_outcome():
    with pytest.raises(fgs.InvalidAblation):
        fgs.compute_ablation(
            "k", {"A5_G1": float("nan")}, {"A5_G1": 0.1}, crn_substream_isolated=True
        )


def test_ablation_delta_worst_cell_is_max_live_minus_max_cut():
    live = {"A2_G3": 0.90, "A1_G2": 0.30}
    cut = {"A2_G3": 0.20, "A1_G2": 0.30}
    r = fgs.compute_ablation("k", live, cut, crn_substream_isolated=True)
    assert r.delta_worst_cell == pytest.approx(max(live.values()) - max(cut.values()))
