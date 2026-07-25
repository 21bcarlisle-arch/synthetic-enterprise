"""Tests for the run manifest/ledger + three separated scores (§3+§4).

The R15 control (mixed-basis aggregate fails loudly) is proven BOTH WAYS:
- same-basis reduce succeeds
- mixed-basis reduce raises MixedBasisError
Mutate `assert_homogeneous_basis` to `return ScoreBasis.WEIGHTED` (drop the
check) and `test_r15_mixed_basis_raises` / `test_commercial_ev_refuses_unweighted_row`
go red — the control fires on its own named defect.
"""

import json

import pytest

from background.run_manifest import (
    MixedBasisError,
    RunManifest,
    RunOutcomes,
    Score,
    ScoreBasis,
    ThreeScores,
    aggregate_scores,
    append_to_ledger,
    assert_homogeneous_basis,
    build_manifest,
    commercial_ev,
    read_ledger,
    retention_class,
    robustness,
    survival,
    three_scores,
)


# --------------------------------------------------------------------------- #
# §3 manifest                                                                 #
# --------------------------------------------------------------------------- #
def _survivor(ev, prob=None, seed=None, scenario="history-default"):
    return build_manifest(
        scenario,
        RunOutcomes(survived=True, ev_gbp=ev),
        true_probability=prob,
        population_seed=seed,
        code_sha="abcdef123456",
        curriculum_version="segmentation_curriculum_v1",
        generated_at="2026-07-25T00:00:00+00:00",
    )


def test_manifest_carries_every_ruling_field():
    m = build_manifest(
        "crisis-replay",
        RunOutcomes(survived=False, ev_gbp=-500.0, death_cause="collateral call",
                    death_date="2022-03-01", gbp_per_tco2e=41.0, worst_cell_fidelity=0.7),
        true_probability=0.15,
        population_seed=200,
        realised_cell_counts={"tenure:social_rent": 12},
        draw_population_enabled=True,
        code_sha="deadbeef0001",
        curriculum_version="segmentation_curriculum_v1",
        generated_at="2026-07-25T12:00:00+00:00",
    )
    row = m.to_row()
    for key in ("run_id", "code_sha", "curriculum_version", "world_scenario",
                "true_probability", "population_seed", "realised_cell_counts",
                "draw_population_enabled", "outcomes"):
        assert key in row
    assert row["outcomes"]["death_cause"] == "collateral call"
    assert row["true_probability"] == 0.15
    assert "crisis-replay" in row["run_id"]


def test_death_without_cause_is_rejected():
    with pytest.raises(ValueError):
        RunManifest(
            run_id="r", code_sha="s", curriculum_version="v",
            world_scenario="w", outcomes=RunOutcomes(survived=False),
        ).to_row()


def test_ledger_append_and_read_roundtrip(tmp_path):
    path = tmp_path / "run_ledger.jsonl"
    append_to_ledger(_survivor(100.0, prob=0.5), path)
    append_to_ledger(_survivor(200.0, prob=0.5), path)
    rows = read_ledger(path)
    assert len(rows) == 2
    assert all("_retention" in r for r in rows)
    # jsonl, one object per line
    assert len(path.read_text().strip().splitlines()) == 2


# --------------------------------------------------------------------------- #
# §3 retention policy                                                         #
# --------------------------------------------------------------------------- #
def test_every_death_retained_full():
    m = build_manifest("w", RunOutcomes(survived=False, death_cause="x", death_date="2022-01-01"))
    assert retention_class(m) == "full_death"


def test_fidelity_flag_retained_full():
    m = build_manifest("w", RunOutcomes(survived=True, ev_gbp=1.0, worst_cell_fidelity=0.2))
    assert retention_class(m) == "full_fidelity_flag"


def test_retention_deterministic_in_run_id():
    m = _survivor(100.0)
    assert retention_class(m) == retention_class(m)  # replay-stable, no fresh randomness


# --------------------------------------------------------------------------- #
# §4 three scores                                                             #
# --------------------------------------------------------------------------- #
def test_survival_dies_anywhere_fails_worstcase():
    rows = [
        _survivor(100.0).to_row(),
        build_manifest("w", RunOutcomes(survived=False, ev_gbp=-9.0, death_cause="c",
                                        death_date="2022-01-01")).to_row(),
    ]
    s = survival(rows)
    assert s.value == 0.0
    assert s.basis is ScoreBasis.UNWEIGHTED


def test_survival_all_live_passes():
    rows = [_survivor(100.0).to_row(), _survivor(50.0).to_row()]
    assert survival(rows).value == 1.0


def test_robustness_is_unweighted_worst_tail():
    rows = [_survivor(float(x)).to_row() for x in (1000, 900, 800, 10)]  # 10 is the bad tail
    r = robustness(rows, tail_fraction=0.25)  # worst 1 of 4
    assert r.basis is ScoreBasis.UNWEIGHTED
    assert r.value == 10.0


def test_commercial_ev_is_probability_weighted():
    rows = [
        _survivor(100.0, prob=0.9).to_row(),
        _survivor(1000.0, prob=0.1).to_row(),
    ]
    ce = commercial_ev(rows)
    assert ce.basis is ScoreBasis.WEIGHTED
    assert ce.value == pytest.approx((0.9 * 100 + 0.1 * 1000) / 1.0)


def test_commercial_ev_refuses_unweighted_row():
    # a row with no true_probability cannot silently sit in a weighted score
    rows = [_survivor(100.0, prob=0.5).to_row(), _survivor(200.0, prob=None).to_row()]
    with pytest.raises(MixedBasisError):
        commercial_ev(rows)


def test_three_scores_kept_separate():
    rows = [_survivor(100.0, prob=0.5).to_row(), _survivor(200.0, prob=0.5).to_row()]
    ts = three_scores(rows)
    assert isinstance(ts, ThreeScores)
    assert ts.commercial_ev.basis is ScoreBasis.WEIGHTED
    assert ts.robustness.basis is ScoreBasis.UNWEIGHTED
    assert ts.survival.basis is ScoreBasis.UNWEIGHTED
    # no blended scalar exists by construction
    assert not hasattr(ts, "blended")


# --------------------------------------------------------------------------- #
# R15 control — proven BOTH WAYS                                              #
# --------------------------------------------------------------------------- #
def test_r15_same_basis_reduces():
    a = Score("a", 1.0, ScoreBasis.UNWEIGHTED, 1)
    b = Score("b", 3.0, ScoreBasis.UNWEIGHTED, 1)
    out = aggregate_scores([a, b], lambda xs: sum(xs) / len(xs))
    assert out.value == 2.0
    assert out.basis is ScoreBasis.UNWEIGHTED


def test_r15_mixed_basis_raises():
    weighted = Score("ev", 5.0, ScoreBasis.WEIGHTED, 1)
    unweighted = Score("survival", 1.0, ScoreBasis.UNWEIGHTED, 1)
    with pytest.raises(MixedBasisError):
        aggregate_scores([weighted, unweighted], lambda xs: sum(xs))
    with pytest.raises(MixedBasisError):
        assert_homogeneous_basis([weighted, unweighted])


def test_r15_empty_is_failclosed():
    with pytest.raises(MixedBasisError):
        assert_homogeneous_basis([])
