"""Coupled-triad tests for the W2_11 <-> D5 pair (payment belief-vs-truth,
atom H27_payment_belief_gap).

These test the GAP MEASUREMENT, not the company inference in isolation. The
central R15 concern: the gap must be a real, mutation-sensitive measurement --
it hits exactly the no-skill baseline (gap == 1) when the belief is totally
blind and exactly 0 when the belief matches truth, so a mid-range reading is a
real measurement, never a value the metric is stuck at.
"""

from __future__ import annotations

import ast
import inspect
import json

import tools.couple_w2_11_d5 as pair

from background.gap_metric import belief_gap, detection_gap, misapplication_gap, write_gap_entry
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from interface.contracts.wall_envelope import WallResponse
from simulation.payment_behaviour_source import PaymentEvent

# Small-but-real population: enough for both DD and non-DD failures to occur
# reliably (see test_non_dd_failures_occur_and_are_never_flagged) while
# keeping the suite fast.
_N = 900
_SEED = 101


# ---------------------------------------------------------------------------
# Wall: the company side of this pair reads no SIM internals (module-level,
# mirrors the AST check every other coupled-triad test file runs).
# ---------------------------------------------------------------------------

def test_company_twin_respects_wall():
    import company.billing.payment_observation_consumer as consumer_mod
    tree = ast.parse(inspect.getsource(consumer_mod))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert not a.name.startswith(("simulation", "sim")), a.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert not node.module.startswith(("simulation", "sim")), node.module


def test_consumer_never_receives_theta(monkeypatch):
    """R15 independence: every call this harness makes into
    `PaymentObservationConsumer.observe` carries a `WallResponse`, never a
    `PaymentEvent` or any of its truth-only fields (stress, dd_failure_reason,
    segment, pattern). Proves OUR usage, on top of the consumer module's own
    AST-based import-freedom test above."""
    seen = []
    original = PaymentObservationConsumer.observe

    def spy(self, response):
        seen.append(response)
        assert isinstance(response, WallResponse), type(response)
        assert not isinstance(response, PaymentEvent)
        assert not hasattr(response, "stress")
        assert not hasattr(response, "dd_failure_reason")
        assert not hasattr(response, "segment")
        payload = response.payload
        if payload is not None:
            assert not isinstance(payload, PaymentEvent)
            assert not hasattr(payload, "stress")
            assert not hasattr(payload, "segment")
        return original(self, response)

    monkeypatch.setattr(PaymentObservationConsumer, "observe", spy)
    records, consumer, ledger_book, as_of = pair.build_scenario(300, seed=11)
    assert len(seen) > 0
    assert len(records) == 300 * pair.N_PERIODS


# ---------------------------------------------------------------------------
# Non-triviality: DETECTION and BELIEF gaps must be > 0 (R12/R13 -- a ~0 gap
# here would be a leak, never a success).
# ---------------------------------------------------------------------------

def test_detection_and_belief_gaps_non_trivial():
    result = pair.measure(_N, seed=_SEED)
    det, bel, age = result["detection"], result["belief"], result["ageing"]

    assert det.gap is not None and det.gap > 0.0, det
    assert bel.gap is not None and bel.gap > 0.0, bel
    # ageing is reported honestly whatever it reads (see module note); it
    # must still be a well-formed gap, not degenerate/None.
    assert age.gap is not None

    stats = result["stats"]
    assert stats["n_true_failures"] > 0
    assert stats["n_flagged_failures"] > 0
    assert stats["n_flagged_failures"] < stats["n_true_failures"]


def test_non_dd_failures_occur_and_are_never_flagged():
    """The blind spot's own witness: this population MUST contain genuine
    non-DD failures (or the detection gap's non-triviality would be an
    accident of population shape, not the mechanism), and NONE of them may
    ever appear in the belief's flagged set -- the no-remittance blind spot
    is structural (adapter emits nothing for a failed non-DD payment), so a
    non-zero count here would mean a leak across the wall."""
    result = pair.measure(_N, seed=_SEED)
    stats = result["stats"]
    assert stats["n_true_non_dd_failures"] > 0, "population shape didn't exercise the blind spot"
    assert stats["n_flagged_non_dd_failures"] == 0


# ---------------------------------------------------------------------------
# Determinism (C-S2): same seed/population -> byte-identical gap results.
# ---------------------------------------------------------------------------

def test_deterministic():
    r1 = pair.measure(_N, seed=_SEED)
    r2 = pair.measure(_N, seed=_SEED)
    for name in ("detection", "belief", "ageing"):
        a, b = r1[name], r2[name]
        assert a.gap == b.gap, name
        assert a.raw_gap == b.raw_gap, name
        assert a.g0 == b.g0, name
        assert a.components == b.components, name
    assert r1["stats"] == r2["stats"]


def test_different_seed_changes_the_population():
    r1 = pair.measure(400, seed=1)
    r2 = pair.measure(400, seed=2)
    changed = (
        r1["stats"]["n_true_failures"] != r2["stats"]["n_true_failures"]
        or r1["detection"].gap != r2["detection"].gap
        or r1["belief"].gap != r2["belief"].gap
    )
    assert changed, "changing --seed had no observable effect on the drawn population"


# ---------------------------------------------------------------------------
# R15 mutation checks: the scorers this pairing uses must be able to FAIL
# (hit their own worst-case) as well as pass (hit 0), not sit at one number.
# ---------------------------------------------------------------------------

def test_detection_gap_hits_the_no_skill_baseline_when_belief_is_blind():
    records, _consumer, _ledger, _as_of = pair.build_scenario(_N, seed=_SEED)
    truth_set = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    blind = detection_gap(truth_set, set())
    assert blind.gap == 1.0

    result = pair.measure(_N, seed=_SEED)
    assert result["detection"].gap < blind.gap


def test_detection_gap_zero_on_perfect_flagging():
    records, _consumer, _ledger, _as_of = pair.build_scenario(400, seed=5)
    truth_set = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    perfect = detection_gap(truth_set, truth_set)
    assert perfect.gap == 0.0


def test_belief_gap_zero_when_distributions_match():
    dist = [0.7, 0.2, 0.05, 0.05]
    result = belief_gap(dist, dist)
    assert result.gap == 0.0


def test_ageing_gap_zero_when_truth_equals_belief():
    labels = ["current"] * 90 + ["30-60"] * 10
    result = misapplication_gap(labels, labels)
    assert result.gap == 0.0


# ---------------------------------------------------------------------------
# End-to-end: valid GapResults written to a TEMP ledger (never the real one).
# ---------------------------------------------------------------------------

def test_end_to_end_writes_valid_gap_entries_to_temp_ledger(tmp_path):
    result = pair.measure(_N, seed=_SEED)
    ledger_path = tmp_path / "gap.json"
    commit = "deadbeef"
    measured_at = "2026-07-18T00:00:00+00:00"

    written_keys = set()
    for name in ("detection", "belief", "ageing"):
        r = result[name]
        world_key = f"{pair.WORLD_ATOM_ID}::{name}"
        ledger = write_gap_entry(
            world_key, pair.TWIN_ATOM_ID, r,
            measured_at=measured_at, run_git_commit=commit,
            ledger_path=ledger_path,
        )
        entry = ledger[world_key]
        assert entry["twin_atom_id"] == pair.TWIN_ATOM_ID
        assert entry["metric"] == r.metric
        assert entry["measured_at"] == measured_at
        assert entry["run_git_commit"] == commit
        assert isinstance(entry["gap"], float)
        written_keys.add(world_key)

    reloaded = json.loads(ledger_path.read_text())
    assert set(reloaded.keys()) == written_keys
    assert reloaded[f"{pair.WORLD_ATOM_ID}::detection"]["gap"] > 0.0
    assert reloaded[f"{pair.WORLD_ATOM_ID}::belief"]["gap"] > 0.0


def test_gap_measured_reader_accepts_written_entries(tmp_path):
    from background.coupled_triad import gap_measured

    result = pair.measure(_N, seed=_SEED)
    ledger_path = tmp_path / "gap.json"
    for name in ("detection", "belief", "ageing"):
        world_key = f"{pair.WORLD_ATOM_ID}::{name}"
        ledger = write_gap_entry(
            world_key, pair.TWIN_ATOM_ID, result[name],
            measured_at="2026-07-18T00:00:00+00:00", run_git_commit="abc123",
            ledger_path=ledger_path,
        )
        assert gap_measured(world_key, ledger) is True


# ---------------------------------------------------------------------------
# CLI wiring (no --write-ledger here -- that path touches the real ledger and
# is exercised by the orchestrator post-merge, per the atom's own scope).
# ---------------------------------------------------------------------------

def test_cli_runs_and_prints_all_three_gaps(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["couple_w2_11_d5.py", "--customers", "300", "--seed", "3"])
    pair.main()
    out = capsys.readouterr().out
    assert "W2_11 <-> D5" in out
    assert "[detection]" in out
    assert "[belief]" in out
    assert "[ageing]" in out
    assert "allocation note:" in out
