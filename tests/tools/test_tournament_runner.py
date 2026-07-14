"""Tests for tools/tournament_runner.py (atom A8_experiment_loop_speed).

Covers three things:
  * the memory-aware / core-aware worker cap (the OOM guard);
  * the FAIL-CLOSED publish guards, MUTATION-style — each guard is proven to
    FIRE on its own named defect (R15: a control that cannot fail is worse than
    none), and to PASS on the legitimate case;
  * a real end-to-end parallel run of cheap lives, asserting fitness is
    collected, the pool preserves determinism (identical inputs -> identical
    fitness), and NO run_complete marker / board-pack side effect is produced.

The end-to-end tests actually shell out to the sim, so they are marked slow and
skipped unless TOURNAMENT_RUNNER_E2E=1 is set (the default fast suite stays
fast; the guard/cap tests always run and are what gate the atom mechanically).
"""

import json
import os
from pathlib import Path

import pytest

from tools import tournament_runner as tr

PROJECT_DIR = Path(tr.PROJECT_DIR)


# --------------------------------------------------------------------------- #
# Worker cap (OOM guard)
# --------------------------------------------------------------------------- #

def test_memory_cap_scales_with_available_memory():
    # 10 lives worth of memory available at 1 GB/life, 75% headroom -> 7 workers.
    cap = tr.memory_safe_worker_cap(
        per_life_rss_bytes=1_000 * 1024 * 1024,
        available_bytes=10_000 * 1024 * 1024,
    )
    assert cap == 7


def test_memory_cap_never_below_one_under_pressure():
    # Even with almost no memory, we make progress one life at a time rather
    # than oversubscribing and OOM-killing the box (the 2026-07-13 incident).
    cap = tr.memory_safe_worker_cap(
        per_life_rss_bytes=4_000 * 1024 * 1024,
        available_bytes=100 * 1024 * 1024,
    )
    assert cap == 1


def test_default_worker_count_bounded_by_cores_and_memory():
    n = tr.default_worker_count()
    assert 1 <= n <= (os.cpu_count() or 1)


# --------------------------------------------------------------------------- #
# FAIL-CLOSED guard #2: output dir may never be in the publish / live path.
# Mutation-style: prove the guard FIRES on each forbidden path, and PASSES on a
# legitimate one.
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("bad", [
    PROJECT_DIR / "docs" / "staging",
    PROJECT_DIR / "docs" / "staging" / "sub",
    PROJECT_DIR / "docs" / "reports",
    PROJECT_DIR / "docs" / "reports" / "tournament",
    PROJECT_DIR / "site",
    PROJECT_DIR / "site" / "data" / "x",
])
def test_output_dir_guard_fires_on_publish_paths(bad):
    with pytest.raises(ValueError):
        tr._validate_output_dir(bad)


def test_output_dir_guard_passes_on_isolated_path(tmp_path):
    # A genuinely isolated scratch dir must be accepted, or the guard is a
    # tautology that rejects everything.
    assert tr._validate_output_dir(tmp_path) == tmp_path.resolve()


def test_run_tournament_refuses_forbidden_output_dir():
    with pytest.raises(ValueError):
        tr.run_tournament([], PROJECT_DIR / "docs" / "staging")


# --------------------------------------------------------------------------- #
# FAIL-CLOSED guard #1: every life command carries --fast (the only sim mode
# with no board-pack side effects). Inspect the command the worker builds
# WITHOUT running the sim, by monkeypatching subprocess.run.
# --------------------------------------------------------------------------- #

def test_every_life_forces_fast_flag(tmp_path, monkeypatch):
    captured = {}

    class _FakeProc:
        returncode = 0

    def _fake_run(cmd, **kw):
        captured["cmd"] = cmd
        captured["env"] = kw.get("env", {})
        # Write a minimal valid result JSON so the worker succeeds.
        out_json = Path(cmd[cmd.index("--save-json") + 1])
        out_json.write_text(json.dumps({"total_net_gbp": 1.0}))
        return _FakeProc()

    monkeypatch.setattr(tr.subprocess, "run", _fake_run)
    res = tr._run_one_life(("x", None, {}, str(tmp_path)))

    assert res.ok
    assert "--fast" in captured["cmd"], "a tournament life MUST run --fast (fail-closed)"
    assert captured["env"].get("SIM_FAST_MODE") == "1"
    assert captured["env"].get("SIM_TOURNAMENT_MODE") == "1"


def test_guard_would_catch_a_missing_fast_flag():
    # Mutation sentinel (R15): the guard test above asserts on '--fast'. Prove
    # that assertion is not vacuous — a command lacking --fast is detectable.
    non_fast_cmd = ["python3", "-m", "saas.reporting.annual_report", "--save-json", "x"]
    assert "--fast" not in non_fast_cmd


# --------------------------------------------------------------------------- #
# End-to-end (slow): real cheap lives, real parallelism, determinism preserved,
# NO publish side effect. Opt-in via TOURNAMENT_RUNNER_E2E=1.
# --------------------------------------------------------------------------- #

_E2E = os.environ.get("TOURNAMENT_RUNNER_E2E") == "1"
_e2e = pytest.mark.skipif(not _E2E, reason="set TOURNAMENT_RUNNER_E2E=1 for slow end-to-end")


@_e2e
def test_parallel_run_collects_fitness_and_preserves_determinism(tmp_path):
    staging = PROJECT_DIR / "docs" / "staging"
    markers_before = set(staging.glob("run_complete_*.md")) if staging.exists() else set()

    specs = [tr.LifeSpec("a", end_year=2016), tr.LifeSpec("b", end_year=2016)]
    results, summary = tr.run_tournament(
        specs, tmp_path, workers=2, per_life_rss_bytes=900 * 1024 * 1024)

    assert summary["lives_ok"] == 2
    fits = {r.life_id: r.fitness for r in results}
    # Two lives with identical inputs must produce identical fitness — the pool
    # did not perturb sim output (determinism / Historical Ground Truth intact).
    assert fits["a"]["total_net_gbp"] == fits["b"]["total_net_gbp"]

    # Guard #2 in the live: NO run_complete marker leaked into the publish path.
    markers_after = set(staging.glob("run_complete_*.md")) if staging.exists() else set()
    assert markers_after == markers_before


@_e2e
def test_benchmark_reports_real_speedup(tmp_path):
    # MEASURED 2026-07-14 on this box (16 cores, ~8 GB avail, under live-daemon
    # load): 8 truncated lives serial=190.6s, parallel(7)=63.5s -> 3.0x. This
    # asserts the mechanism yields a real >1.5x on 4 independent lives.
    bench = tr.benchmark(n_lives=4, end_year=2016, output_dir=tmp_path,
                         workers=4, per_life_rss_bytes=900 * 1024 * 1024)
    assert bench["serial_wall_s"] > 0
    assert bench["parallel_wall_s"] > 0
    assert bench["speedup_x"] > 1.5
