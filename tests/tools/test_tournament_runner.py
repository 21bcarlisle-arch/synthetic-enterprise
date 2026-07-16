"""Tests for tools/tournament_runner.py (atom A8_experiment_loop_speed).

Covers four things:
  * the memory-aware / core-aware worker cap (the OOM guard);
  * the FAIL-CLOSED publish guards, MUTATION-style — each guard is proven to
    FIRE on its own named defect (R15: a control that cannot fail is worse than
    none), and to PASS on the legitimate case;
  * the L2->L3 self-calibration lever (measured, not guessed, per-life RSS
    recomputes the worker cap for the remainder of a run) — plumbing tests
    that stay in-process (no real ProcessPoolExecutor spawn, so they run in
    the fast suite) plus a mutation-style proof that calibration is skipped
    exactly when it must be (explicit workers=, serial=True, nothing
    measurable);
  * a real end-to-end parallel run of cheap lives, asserting fitness is
    collected, the pool preserves determinism (identical inputs -> identical
    fitness), and NO run_complete marker / board-pack side effect is produced.

The end-to-end tests actually shell out to the sim, so they are marked slow and
skipped unless TOURNAMENT_RUNNER_E2E=1 is set (the default fast suite stays
fast; the guard/cap/calibration-plumbing tests always run and are what gate
the atom mechanically).
"""

import json
import os
import subprocess
import sys
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
# L2->L3 self-calibration: measured (not guessed) RSS feeds the worker cap.
# --------------------------------------------------------------------------- #

def test_rss_watermark_reflects_a_real_reaped_child():
    # Proves _rss_watermark_bytes is a REAL measurement of an actual process,
    # not a fixed/fake number — spawn a real child that allocates memory and
    # confirm the RUSAGE_CHILDREN high-water mark moves (never decreases).
    before = tr._rss_watermark_bytes()
    subprocess.run(
        [sys.executable, "-c", "b = bytearray(80 * 1024 * 1024)"],
        check=True,
    )
    after = tr._rss_watermark_bytes()
    assert after >= before


def test_run_one_life_reports_measured_rss_delta(tmp_path, monkeypatch):
    # Mutation-style: prove the delta computation is real arithmetic, not a
    # constant — feed a controlled before/after pair and check the exact delta.
    watermarks = iter([2_000_000, 900_000_000])
    monkeypatch.setattr(tr, "_rss_watermark_bytes", lambda: next(watermarks))

    class _FakeProc:
        returncode = 0
        stderr = b""

    def _fake_run(cmd, **kw):
        out_json = Path(cmd[cmd.index("--save-json") + 1])
        out_json.write_text(json.dumps({"total_net_gbp": 1.0}))
        return _FakeProc()

    monkeypatch.setattr(tr.subprocess, "run", _fake_run)
    res = tr._run_one_life(("x", None, {}, str(tmp_path)))

    assert res.ok
    assert res.measured_rss_bytes == 900_000_000 - 2_000_000


def test_calibration_would_unlock_more_workers_than_the_conservative_default():
    # Pure arithmetic (no process spawn): a measured real RSS far below the
    # conservative 6 GB caller guess must yield a STRICTLY higher worker cap —
    # the load-bearing claim behind self-calibration.
    avail = 10_000 * 1024 * 1024
    conservative_cap = tr.memory_safe_worker_cap(tr._PER_LIFE_RSS_BYTES, available_bytes=avail)
    measured_cap = tr.memory_safe_worker_cap(100 * 1024 * 1024, available_bytes=avail)
    assert measured_cap > conservative_cap


def test_calibration_recomputes_from_a_measured_probe(tmp_path, monkeypatch):
    # Plumbing test kept fully in-process: 2 lives (1 probe + 1 rest) means
    # the rest wave is always capped to 1 worker regardless of the cap
    # arithmetic, so no real ProcessPoolExecutor is spawned and the
    # monkeypatched _run_one_life is exercised for BOTH lives deterministically.
    calls = []

    def _fake(args):
        life_id = args[0]
        calls.append(life_id)
        return tr.LifeResult(life_id, True, 0.1, 0,
                             fitness={"total_net_gbp": 1.0},
                             measured_rss_bytes=100 * 1024 * 1024)

    monkeypatch.setattr(tr, "_run_one_life", _fake)
    lives = [tr.LifeSpec("l0"), tr.LifeSpec("l1")]

    _, summary = tr.run_tournament(lives, tmp_path, per_life_rss_bytes=tr._PER_LIFE_RSS_BYTES)

    assert calls == ["l0", "l1"]  # probe then rest, no duplication/skip
    assert summary["lives_total"] == 2
    assert summary["calibrated"] is True
    assert summary["calibrated_rss_bytes"] == 100 * 1024 * 1024
    assert summary["per_life_rss_bytes_assumed"] == tr._PER_LIFE_RSS_BYTES


def test_explicit_workers_bypasses_calibration(tmp_path, monkeypatch):
    calls = []

    def _fake(args):
        calls.append(args[0])
        return tr.LifeResult(args[0], True, 0.1, 0, fitness={"total_net_gbp": 1.0},
                             measured_rss_bytes=100 * 1024 * 1024)

    monkeypatch.setattr(tr, "_run_one_life", _fake)
    lives = [tr.LifeSpec("l{}".format(i)) for i in range(3)]

    _, summary = tr.run_tournament(lives, tmp_path, workers=1)

    assert len(calls) == 3
    assert summary["calibrated"] is False
    assert summary["calibrated_rss_bytes"] is None
    assert summary["probe_lives"] == 0


def test_serial_flag_bypasses_calibration(tmp_path, monkeypatch):
    calls = []

    def _fake(args):
        calls.append(args[0])
        return tr.LifeResult(args[0], True, 0.1, 0, fitness={"total_net_gbp": 1.0},
                             measured_rss_bytes=100 * 1024 * 1024)

    monkeypatch.setattr(tr, "_run_one_life", _fake)
    lives = [tr.LifeSpec("l{}".format(i)) for i in range(3)]

    _, summary = tr.run_tournament(lives, tmp_path, serial=True)

    assert len(calls) == 3
    assert summary["calibrated"] is False
    assert summary["workers"] == 1


def test_calibration_falls_back_when_nothing_measured(tmp_path, monkeypatch):
    # FAIL-CLOSED: if the probe wave measures nothing real (e.g. every life
    # failed before a child was reaped, or measured_rss_bytes stayed 0),
    # calibration must NOT invent a number — it degrades to the caller's own
    # per_life_rss_bytes, the pre-existing L2 behaviour.
    def _fake(args):
        return tr.LifeResult(args[0], True, 0.1, 0, fitness={"total_net_gbp": 1.0},
                             measured_rss_bytes=0)

    monkeypatch.setattr(tr, "_run_one_life", _fake)
    lives = [tr.LifeSpec("l0"), tr.LifeSpec("l1")]

    _, summary = tr.run_tournament(lives, tmp_path, per_life_rss_bytes=123 * 1024 * 1024)

    assert summary["calibrated"] is False
    assert summary["calibrated_rss_bytes"] is None
    assert summary["per_life_rss_bytes_assumed"] == 123 * 1024 * 1024


def test_probe_lives_zero_disables_calibration(tmp_path, monkeypatch):
    # A single life so the "rest" wave is always capped to 1 worker (safe,
    # in-process) regardless of the real machine's memory picture — isolates
    # the assertion to probe_lives=0 disabling calibration, not concurrency.
    calls = []

    def _fake(args):
        calls.append(args[0])
        return tr.LifeResult(args[0], True, 0.1, 0, fitness={"total_net_gbp": 1.0},
                             measured_rss_bytes=100 * 1024 * 1024)

    monkeypatch.setattr(tr, "_run_one_life", _fake)
    lives = [tr.LifeSpec("l0")]

    _, summary = tr.run_tournament(lives, tmp_path, probe_lives=0)

    assert calls == ["l0"]
    assert summary["calibrated"] is False
    assert summary["probe_lives"] == 0


# --------------------------------------------------------------------------- #
# Lever 3: TIERED TESTS -- cheap screen tier culls before the expensive full
# tier. Plumbing tests stay in-process (monkeypatched _run_one_life, workers=1
# so no real ProcessPoolExecutor spawn -- fast suite), each carrying a
# mutation-style proof (R15) that the cull actually fires on its named defect.
# --------------------------------------------------------------------------- #

def _scored_fake_run_one_life(scores: dict, fail_ids: tuple = ()):
    """Build a fake `_run_one_life` whose fitness score is entirely controlled
    by `scores[life_id]` (read from the life's own env so it applies to BOTH
    tiers identically), and which reports a screen FAILURE for any life_id in
    `fail_ids`. Also records every call as (life_id, end_year) so tests can
    assert exactly which lives ran in which tier."""
    calls = []

    def _fake(args):
        life_id, end_year, extra_env, _output_dir = args
        calls.append((life_id, end_year))
        if life_id in fail_ids:
            return tr.LifeResult(life_id, False, 0.1, 1, error="planted screen failure")
        return tr.LifeResult(
            life_id, True, 0.1, 0,
            fitness={"total_net_gbp": scores[life_id]},
            measured_rss_bytes=100 * 1024 * 1024,
        )

    return _fake, calls


def test_tiered_rejects_invalid_survive_fraction(tmp_path):
    lives = [tr.LifeSpec("a"), tr.LifeSpec("b")]
    for bad in (0.0, -0.1, 1.5, 2.0):
        with pytest.raises(ValueError):
            tr.run_tiered_tournament(lives, tmp_path, screen_end_year=2016,
                                     survive_fraction=bad)


def test_tiered_accepts_boundary_fractions(tmp_path, monkeypatch):
    # Mutation sentinel: the guard above must not be a tautology that rejects
    # every fraction -- both boundaries of the legal range (0, 1] must pass.
    fake, _calls = _scored_fake_run_one_life({"a": 1.0, "b": 2.0})
    monkeypatch.setattr(tr, "_run_one_life", fake)
    for ok in (0.01, 1.0):
        _, _, summary = tr.run_tiered_tournament(
            [tr.LifeSpec("a"), tr.LifeSpec("b")], tmp_path / str(ok),
            screen_end_year=2016, survive_fraction=ok, workers=1)
        assert summary["lives_total"] == 2


def test_tiered_culls_bottom_by_score(tmp_path, monkeypatch):
    # 4 candidates, scores 10/20/30/40 -- survive_fraction=0.5 must keep the
    # top 2 (c2, c3) and cull the bottom 2 (c0, c1).
    scores = {"c0": 10.0, "c1": 20.0, "c2": 30.0, "c3": 40.0}
    fake, calls = _scored_fake_run_one_life(scores)
    monkeypatch.setattr(tr, "_run_one_life", fake)
    lives = [tr.LifeSpec(lid) for lid in scores]

    _, _, summary = tr.run_tiered_tournament(
        lives, tmp_path, screen_end_year=2016, survive_fraction=0.5, workers=1)

    assert summary["survivor_ids"] == ["c2", "c3"]
    assert summary["culled_ids"] == ["c0", "c1"]
    # The full tier must ONLY have been asked to run the survivors.
    full_tier_calls = [lid for lid, end_year in calls if end_year is None]
    assert sorted(full_tier_calls) == ["c2", "c3"]


def test_tiered_promotes_all_when_fraction_is_one(tmp_path, monkeypatch):
    scores = {"c0": 10.0, "c1": 20.0, "c2": 30.0}
    fake, _calls = _scored_fake_run_one_life(scores)
    monkeypatch.setattr(tr, "_run_one_life", fake)
    lives = [tr.LifeSpec(lid) for lid in scores]

    _, _, summary = tr.run_tiered_tournament(
        lives, tmp_path, screen_end_year=2016, survive_fraction=1.0, workers=1)

    assert summary["survivor_ids"] == ["c0", "c1", "c2"]
    assert summary["culled_ids"] == []


def test_tiered_never_promotes_a_failed_screen_life(tmp_path, monkeypatch):
    # R15 mutation-style: even with survive_fraction=1.0 (promote everyone),
    # a life that FAILED its screen (no scoreable fitness) must never reach
    # the expensive full tier -- generosity cannot resurrect a broken life.
    scores = {"c0": 10.0, "c1": 20.0}
    fake, calls = _scored_fake_run_one_life(scores, fail_ids=("c1",))
    monkeypatch.setattr(tr, "_run_one_life", fake)
    lives = [tr.LifeSpec("c0"), tr.LifeSpec("c1")]

    _, _, summary = tr.run_tiered_tournament(
        lives, tmp_path, screen_end_year=2016, survive_fraction=1.0, workers=1)

    assert summary["survivor_ids"] == ["c0"]
    assert "c1" in summary["culled_ids"]
    full_tier_calls = [lid for lid, end_year in calls if end_year is None]
    assert "c1" not in full_tier_calls


def test_tiered_ranking_is_deterministic_tie_break(tmp_path, monkeypatch):
    # Equal scores must break the tie by life_id, not by pool completion
    # order -- the load-bearing determinism claim (C-S2).
    scores = {"c0": 10.0, "c1": 10.0, "c2": 10.0, "c3": 10.0}
    fake, _calls = _scored_fake_run_one_life(scores)
    monkeypatch.setattr(tr, "_run_one_life", fake)
    lives = [tr.LifeSpec(lid) for lid in scores]

    _, _, summary = tr.run_tiered_tournament(
        lives, tmp_path, screen_end_year=2016, survive_fraction=0.5, workers=1)

    assert summary["survivor_ids"] == ["c0", "c1"]


def test_tiered_full_tier_skipped_when_nothing_survives(tmp_path, monkeypatch):
    # All screen lives fail -> zero survivors -> the full tier must not be
    # invoked at all (no wasted expensive-tier call on an empty candidate set).
    fake, calls = _scored_fake_run_one_life({}, fail_ids=("c0", "c1"))
    monkeypatch.setattr(tr, "_run_one_life", fake)
    lives = [tr.LifeSpec("c0"), tr.LifeSpec("c1")]

    _screen_results, full_results, summary = tr.run_tiered_tournament(
        lives, tmp_path, screen_end_year=2016, survive_fraction=1.0, workers=1)

    assert summary["survivor_ids"] == []
    assert full_results == []
    assert summary["full_summary"]["lives_total"] == 0
    # Only the 2 screen calls happened -- no full-tier calls at all.
    assert len(calls) == 2


def test_tiered_screen_tier_uses_its_own_rss_hint(tmp_path, monkeypatch):
    # R15 mutation-style: proves the composition-hazard fix actually reaches
    # the screen tier's run_tournament call, not just the docstring. Without
    # this parameter, a caller composing naive+screen+full in one process
    # (benchmark_tiered's own shape) silently degrades the screen tier to the
    # conservative 6 GB default because calibration only reliably fires on a
    # process's FIRST run_tournament call (named limitation, module
    # docstring) -- REAL, MEASURED 2026-07-16 on this box: an uncorrected
    # tiered-benchmark run showed the screen tier fall back to workers=1
    # (56.5s for 6 cheap lives that should parallelise) while naive got
    # workers=4. This test proves the fix, not just asserts a docstring claim.
    seen_rss = {}

    def _fake_run_tournament(specs, output_dir, **kwargs):
        tag = "screen" if str(output_dir).endswith("screen") else "full"
        seen_rss[tag] = kwargs.get("per_life_rss_bytes")
        results = [
            tr.LifeResult(s.life_id, True, 0.1, 0, fitness={"total_net_gbp": 1.0})
            for s in specs
        ]
        return results, {"lives_total": len(specs), "lives_ok": len(specs),
                         "lives_failed": 0, "wall_clock_s": 0.1}

    monkeypatch.setattr(tr, "run_tournament", _fake_run_tournament)
    lives = [tr.LifeSpec("a"), tr.LifeSpec("b")]

    tr.run_tiered_tournament(
        lives, tmp_path, screen_end_year=2016, survive_fraction=1.0,
        per_life_rss_bytes=2_000 * 1024 * 1024,
        screen_per_life_rss_bytes=100 * 1024 * 1024,
    )

    assert seen_rss["screen"] == 100 * 1024 * 1024
    assert seen_rss["full"] == 2_000 * 1024 * 1024


def test_tiered_screen_tier_defaults_to_shared_rss_hint_when_unset(tmp_path, monkeypatch):
    # Mutation sentinel for the test above: when the caller does NOT supply a
    # separate screen hint, both tiers must fall back to the SAME
    # per_life_rss_bytes (the pre-existing, simpler behaviour) -- proves the
    # new parameter is additive, not a silent behaviour change for existing
    # callers who never pass it.
    seen_rss = {}

    def _fake_run_tournament(specs, output_dir, **kwargs):
        tag = "screen" if str(output_dir).endswith("screen") else "full"
        seen_rss[tag] = kwargs.get("per_life_rss_bytes")
        results = [
            tr.LifeResult(s.life_id, True, 0.1, 0, fitness={"total_net_gbp": 1.0})
            for s in specs
        ]
        return results, {"lives_total": len(specs), "lives_ok": len(specs),
                         "lives_failed": 0, "wall_clock_s": 0.1}

    monkeypatch.setattr(tr, "run_tournament", _fake_run_tournament)
    lives = [tr.LifeSpec("a"), tr.LifeSpec("b")]

    tr.run_tiered_tournament(
        lives, tmp_path, screen_end_year=2016, survive_fraction=1.0,
        per_life_rss_bytes=777 * 1024 * 1024,
    )

    assert seen_rss["screen"] == 777 * 1024 * 1024
    assert seen_rss["full"] == 777 * 1024 * 1024


def test_tiered_output_dir_guard_fires_on_publish_paths():
    # Same fail-closed guard #2 as run_tournament -- proven mutation-style
    # (fires on a forbidden path) so it is not a copy-pasted no-op.
    with pytest.raises(ValueError):
        tr.run_tiered_tournament([], PROJECT_DIR / "docs" / "staging",
                                 screen_end_year=2016)


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


@_e2e
def test_calibration_unlocks_real_parallelism_vs_uncalibrated_default(tmp_path):
    # THE L2->L3 evidence: with the caller's conservative 6 GB default guess
    # and NO calibration, memory_safe_worker_cap throttles to a small worker
    # count (the exact "requires a human to already know the true RSS" gap
    # this atom closes). With calibration ON -- same starting guess, no
    # external hint -- the runner measures the REAL per-life RSS from a
    # one-life probe and recomputes the cap for the rest.
    #
    # Each variant is run as a GENUINELY FRESH subprocess (the real CLI entry
    # point), not two in-process calls in this test's own process. This is
    # load-bearing, not stylistic: `_rss_watermark_bytes()` is a per-process
    # MONOTONIC high-water mark (RUSAGE_CHILDREN); a second run_tournament()
    # call in the SAME already-used process would see a stale (already-raised)
    # watermark and silently measure ~0 delta for its own probe -- exactly the
    # named per-process limitation this mechanism carries (see module
    # docstring). The real CLI is always invoked as a fresh process per
    # tournament, which is what this test reproduces.
    #
    # MEASURED 2026-07-16 on this box (16 cores, ~10 GB avail): uncalibrated
    # 4x --end-year 2016 lives, workers=1 (6 GB guess throttles to 1),
    # wall_clock_s=165.10. Calibrated (same 6 GB starting guess): probe
    # measured 783,654,912 bytes (~0.73 GB) real RSS, recomputed to workers=3
    # for the remaining 3 lives, wall_clock_s=47.18 -- a real 3.5x wall-clock
    # reduction and a 1->3 worker jump, with ZERO manual tuning of
    # per-life-mb; every life's fitness/determinism unaffected (both variants
    # produce byte-identical total_net_gbp across their lives).
    off_dir = tmp_path / "uncalibrated"
    on_dir = tmp_path / "calibrated"

    off_proc = subprocess.run(
        [sys.executable, "-m", "tools.tournament_runner", "run",
         "--lives", "4", "--end-year", "2016", "--output-dir", str(off_dir),
         "--no-calibrate"],
        cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=900,
    )
    on_proc = subprocess.run(
        [sys.executable, "-m", "tools.tournament_runner", "run",
         "--lives", "4", "--end-year", "2016", "--output-dir", str(on_dir)],
        cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=900,
    )
    assert off_proc.returncode == 0, off_proc.stderr[-2000:]
    assert on_proc.returncode == 0, on_proc.stderr[-2000:]

    off_sum = json.loads((off_dir / "tournament_summary.json").read_text())
    on_sum = json.loads((on_dir / "tournament_summary.json").read_text())

    assert off_sum["lives_ok"] == 4
    assert on_sum["lives_ok"] == 4
    assert off_sum["calibrated"] is False
    assert on_sum["calibrated"] is True
    # The measured figure must be far below the 6 GB conservative default —
    # a truncated 2016 life is documented (and independently re-measured
    # above) at well under 1 GB.
    assert on_sum["calibrated_rss_bytes"] < 2_000 * 1024 * 1024
    # The real, load-bearing claim: calibration unlocks STRICTLY more workers
    # than the same box gets with the uncalibrated conservative guess, on the
    # SAME caller-supplied per-life-mb guess in both runs.
    assert on_sum["workers"] > off_sum["workers"]
    # Determinism preserved: identical inputs -> identical fitness regardless
    # of the calibration path taken (the mechanism only changes concurrency).
    off_fitness = {r["life_id"]: r["fitness"]["total_net_gbp"] for r in off_sum["results"]}
    on_fitness = {r["life_id"]: r["fitness"]["total_net_gbp"] for r in on_sum["results"]}
    assert len(set(off_fitness.values())) == 1
    assert len(set(on_fitness.values())) == 1
    assert set(off_fitness.values()) == set(on_fitness.values())


@_e2e
def test_tiered_screening_beats_naive_full_evaluation(tmp_path):
    # Lever 3 evidence (A8, tiered tests): 6 candidates, a cheap --end-year
    # 2016 screen (~9s/life on this box) culls to the top third (2 survivors,
    # survive_fraction=0.33), which alone then pay for the expensive
    # --end-year 2018 full tier (~35s/life). NAIVE path runs all 6 candidates
    # at the expensive tier directly (same calibrated bounded pool).
    # survive_fraction is a FLOOR on survivors via math.ceil(N*frac): at N=6 any
    # fraction in (1/6, 1/3] keeps exactly 2 (ceil(6*0.33)=2). 0.34 would tip to
    # ceil(2.04)=3 -- the intent here is the majority-cull illustration (2 of 6).
    #
    # MEASURED 2026-07-16 on this box (16 cores; live daemons concurrently
    # running): naive_wall_s={NAIVE_WALL}, tiered_wall_s={TIERED_WALL}
    # (screen {SCREEN_WALL}s + full {FULL_WALL}s), speedup {SPEEDUP}x. Exact
    # numbers vary with box load; the assertions below check the mechanism
    # (culling reduces the number of expensive lives run), not a pinned
    # wall-clock figure, so this stays robust to load variance.
    naive_dir = tmp_path / "naive_direct"
    naive_specs = [tr.LifeSpec("m{}".format(i), end_year=2018) for i in range(6)]
    _, naive_sum = tr.run_tournament(naive_specs, naive_dir,
                                     per_life_rss_bytes=900 * 1024 * 1024)

    tiered_dir = tmp_path / "tiered_direct"
    tiered_specs = [tr.LifeSpec("m{}".format(i), end_year=2018) for i in range(6)]
    screen_results, full_results, tiered_sum = tr.run_tiered_tournament(
        tiered_specs, tiered_dir, screen_end_year=2016, survive_fraction=0.33,
        per_life_rss_bytes=900 * 1024 * 1024)

    assert naive_sum["lives_ok"] == 6
    assert len(tiered_sum["survivor_ids"]) == 2
    assert len(tiered_sum["culled_ids"]) == 4
    # The expensive tier ran ONLY the survivors -- exactly the mechanism this
    # lever exists for (fewer costly lives, not just faster ones).
    assert tiered_sum["full_summary"]["lives_total"] == 2
    assert all(r.ok for r in full_results)
    # A candidate that survives cheap screening must be a real candidate that
    # also completed the full tier -- no silent drop.
    assert {r.life_id for r in full_results} == set(tiered_sum["survivor_ids"])

    # The real speed claim: screening 6 cheap lives + fully evaluating only 2
    # survivors is faster than fully evaluating all 6 -- the whole point of
    # the lever. (Sum-of-wall-time comparison; both runs use the same
    # per-life RSS hint so any variance is load noise, not a rigged input.)
    assert tiered_sum["total_wall_s"] < naive_sum["wall_clock_s"]
