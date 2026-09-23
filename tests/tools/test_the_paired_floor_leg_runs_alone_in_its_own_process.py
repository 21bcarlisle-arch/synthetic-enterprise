"""The defect: the split that was supposed to cap the peak silently puts both legs back in one place.

THE DEFECT, NAMED. `tools/size_term_paired_floor` was split on 2026-09-23 so that ONE LEG runs per
process, because the undivided version peaked at 7,878 MB and was OOM-killed at 1h 26m having
written nothing. The split only buys that if the orchestrator really spawns and really holds
nothing. Every way it can stop doing so is SILENT and produces a correct-looking artefact: a
refactor that calls `_one_leg` directly again, a shard key that collides so one leg is differenced
against itself, a resume that re-runs legs already on disk. None of those change a published number
until the process dies, and then they cost the whole family.

AND THE HALF THAT IS NOT ABOUT THIS FILE AT ALL, which is the one that already happened once. The
headroom guard recognises a floor leg by a TOKEN IN ITS ARGV. When `size_term_paired_floor` was
first written it carried neither token the census knew, so it was invisible in both directions at
once -- it did not count itself against running legs and no leg launched beside it could see it --
and that invisibility is precisely what admitted the run that died. The split re-opens that hazard,
because the token that marks a process which will really grow to gigabytes moved from `--seeds` to
`--leg-only`. So the chain is controlled, not the ends: the argv `_spawn_leg` actually builds is
asserted to be an argv `running_floor_legs` actually counts. Renaming the flag in either place
alone turns this red, which is the only arrangement that could have caught the original defect.

THE CENSUS LEG IS A PARTITION CONTROL AND IS WRITTEN AS ONE. Two of its three claims are that a
process is NOT counted, and a census that counted nothing would satisfy both. So the orchestrator's
invisibility, the leg's visibility and the sibling noise-floor leg's visibility are asserted over
one population in one place, and the accepting claims carry the refusing ones.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import size_term_paired_floor as floor
from tools.run_value_cycle_ab import (
    FLOOR_RUN_PEAK_MB,
    PAIRED_FLOOR_LEG_PEAK_MB,
    running_floor_legs,
)


def _leg_payload(seed, configuration: str, net: float) -> dict:
    """A shard of the shape `run_leg_to_shard` writes, with the fields assembly reads."""
    return {
        "seed": seed,
        "configuration": configuration,
        "elapsed_s": 1.0,
        "peak_rss_mb": 4321.0,
        "realised_delta": {row: net for row in floor.DELTA_ROWS},
        "accounts_the_arm_priced": 2,
        "size_term_reached_calls": 4,
        "size_term_distinct_scales": 0 if configuration == "blind" else 3,
        "size_term_scale_range": None,
        "churn_rolls": 3,
        "churn_rolls_redrawn": 3,
        "accounts_rerolled": 3,
        "book_identity": {"billing_accounts_settled_in_window": 154},
    }


def _sharding_executor(record: list):
    """A stand-in for the CHILD PROCESS: it writes the shard the real leg would and records itself.

    It deliberately does NOT go through `_one_leg`, because the thing under test here is what the
    orchestrator does with legs, not what a leg computes -- that is the sibling file's subject.
    """
    def execute(seed, blind, report_end, leg_dir):
        record.append((seed, blind))
        leg_dir.mkdir(parents=True, exist_ok=True)
        configuration = "blind" if blind else "seeing"
        net = 100.0 if blind else 100.0 + (0 if seed is None else seed % 7) + 1.0
        floor._shard_path(leg_dir, seed, blind).write_text(
            json.dumps(_leg_payload(seed, configuration, net)), encoding="utf-8")
    return execute


def test_the_orchestrator_runs_no_leg_in_its_own_process(monkeypatch, tmp_path: Path):
    """THE POINT OF THE SPLIT. If this process runs a leg, the peak is back where it was.

    `_one_leg` is made to raise, so ANY in-process leg -- a refactor that inlines it, a fallback
    that quietly runs one when a spawn fails -- fails this loudly rather than by being 7,878 MB
    again an hour later. The default executor is exercised by not passing one.
    """
    def must_not_run(*_args, **_kwargs):
        raise AssertionError(
            "the orchestrator ran a leg in its own process; the peak is a pair's again")

    monkeypatch.setattr(floor, "_one_leg", must_not_run)
    spawned: list = []
    monkeypatch.setattr(floor, "_spawn_leg", _sharding_executor(spawned))

    report = floor.run([9001, 9002], out=tmp_path / "floor.json")

    assert len(report["seeds"]) == 2
    # Every leg went out to a process: two configurations for each of two seeds and the base.
    assert spawned == [(None, True), (None, False),
                       (9001, True), (9001, False),
                       (9002, True), (9002, False)]


def test_a_leg_already_on_disk_is_not_run_again(monkeypatch, tmp_path: Path):
    """RESUME, which is the only thing writing shards buys over holding the legs in memory.

    A family killed at its fourth leg must cost four legs to finish, not seven. Without this the
    shards are a write-only log and an OOM still costs the whole run.
    """
    monkeypatch.setattr(floor, "_one_leg", lambda *a, **k: pytest.fail("ran a leg in-process"))
    first: list = []
    monkeypatch.setattr(floor, "_spawn_leg", _sharding_executor(first))
    out = tmp_path / "floor.json"
    floor.run([9001, 9002], out=out)
    assert len(first) == 6

    second: list = []
    monkeypatch.setattr(floor, "_spawn_leg", _sharding_executor(second))
    report = floor.run([9001, 9002], out=out)
    assert second == [], "a completed family re-ran legs whose shards were already on disk"
    assert len(report["seeds"]) == 2, "the resumed family was assembled from the shards"


def test_a_dead_leg_costs_one_leg_and_leaves_the_rest_usable(monkeypatch, tmp_path: Path):
    """AN OOM MUST COST ONE LEG, NOT THE FAMILY -- the whole reason the unit is the leg.

    The seeing leg of the second seed dies. What must survive is every leg before it, so the
    re-run pays for one leg rather than five.
    """
    monkeypatch.setattr(floor, "_one_leg", lambda *a, **k: pytest.fail("ran a leg in-process"))
    done: list = []
    write = _sharding_executor(done)

    def dies_on_the_second_seeds_seeing_leg(seed, blind, report_end, leg_dir):
        if seed == 9002 and not blind:
            raise RuntimeError("OOM")
        write(seed, blind, report_end, leg_dir)

    monkeypatch.setattr(floor, "_spawn_leg", dies_on_the_second_seeds_seeing_leg)
    out = tmp_path / "floor.json"
    with pytest.raises(RuntimeError):
        floor.run([9001, 9002], out=out)

    survived = sorted(p.name for p in floor.leg_dir_for(out).glob("leg_*.json"))
    assert survived == ["leg_9001_blind.json", "leg_9001_seeing.json",
                        "leg_9002_blind.json", "leg_base_blind.json", "leg_base_seeing.json"], (
        "a dead leg took completed legs with it; the re-run pays for them again")

    # And the re-run pays for exactly the one leg that died.
    retry: list = []
    monkeypatch.setattr(floor, "_spawn_leg", _sharding_executor(retry))
    report = floor.run([9001, 9002], out=out)
    assert retry == [(9002, False)]
    assert len(report["seeds"]) == 2


def test_the_two_configurations_of_one_seed_cannot_share_a_shard(tmp_path: Path):
    """A COLLIDING KEY DIFFERENCES A LEG AGAINST ITSELF and publishes a spread of exactly zero.

    Asserted as DISTINCTNESS over the whole population rather than as one inequality, because the
    failure is two shapes collapsing to one state and a per-shape check cannot see that.
    """
    shapes = [(None, True), (None, False), (9001, True), (9001, False), (9002, True)]
    paths = [floor._shard_path(tmp_path, seed, blind) for seed, blind in shapes]
    assert len(set(paths)) == len(shapes), (
        "two legs share a shard path, so one overwrites the other and the pair built from it is a "
        "leg differenced against itself: every row exactly zero, for the flattering reason")


def test_the_spawned_leg_is_an_argv_the_headroom_census_counts(tmp_path: Path):
    """THE CHAIN, and the defect that already happened once.

    A leg the census cannot see neither counts itself against running legs nor is counted by one
    launched beside it -- the exact invisibility that admitted the OOM-killed run. So the argv this
    file BUILDS is checked against the census that has to RECOGNISE it. Asserting either end alone
    passes while they disagree, which is how the first one got through.
    """
    argv = _captured_argv(tmp_path)
    assert "--leg-only" in argv, "the spawned leg carries no --leg-only token"

    matched = [(module, flag, peak) for module, flag, peak in floor_leg_shapes()
               if flag in argv and any(module in token for token in argv)]
    assert len(matched) == 1, (
        "the census matched {} shapes against the argv this file spawns, so a running leg is "
        "priced wrongly or not at all: {}".format(len(matched), argv))
    assert matched[0][2] == PAIRED_FLOOR_LEG_PEAK_MB, (
        "a spawned leg is priced at {} MB, not the leg peak".format(matched[0][2]))


def floor_leg_shapes():
    from tools.run_value_cycle_ab import FLOOR_LEG_SHAPES
    return FLOOR_LEG_SHAPES


def _captured_argv(tmp_path: Path) -> list[str]:
    """The argv `_spawn_leg` really builds, taken at the `subprocess.run` boundary."""
    seen: dict = {}

    class _Completed:
        returncode = 0

    def fake_run(argv, **_kwargs):
        seen["argv"] = list(argv)
        return _Completed()

    import tools.size_term_paired_floor as module
    original = module.subprocess.run
    module.subprocess.run = fake_run
    try:
        with pytest.raises(RuntimeError, match="left no shard"):
            floor._pair(9001, None, None, tmp_path, floor._spawn_leg)
    finally:
        module.subprocess.run = original
    return seen["argv"]


def _fake_proc(root: Path, pid: int, argv: list[str], rss_kb: int) -> None:
    entry = root / str(pid)
    entry.mkdir(parents=True, exist_ok=True)
    (entry / "cmdline").write_bytes(("\x00".join(argv) + "\x00").encode("utf-8"))
    (entry / "status").write_text("Name:\tpython3\nPPid:\t1\nVmRSS:\t{} kB\n".format(rss_kb),
                                  encoding="utf-8")


def test_the_census_sees_a_leg_and_does_not_see_its_orchestrator(tmp_path: Path):
    """THE PARTITION, IN ONE PLACE. Two of the three claims are absences, and a census that saw
    nothing at all would satisfy both of them while pricing every real leg at zero.

    The orchestrator must NOT be counted: it spawns and holds tens of megabytes, and counting it
    would charge the guest a full leg's peak twice for the one leg actually running -- refusing
    families this machine can hold, which makes the bound unmeasurable.
    """
    _fake_proc(tmp_path, 900001,
               ["python3", "-m", "tools.size_term_paired_floor", "--leg-only", "5101",
                "--configuration", "blind"], 4_200_000)
    _fake_proc(tmp_path, 900002,
               ["python3", "-m", "tools.size_term_paired_floor", "--seeds", "5101,5102"], 48_000)
    _fake_proc(tmp_path, 900003,
               ["python3", "-m", "tools.run_value_cycle_ab", "--noise-floor-seeds", "1,2"],
               3_100_000)

    legs = {pid: peak for pid, _rss, peak in running_floor_legs(proc_root=tmp_path)}

    assert legs.get(900001) == PAIRED_FLOOR_LEG_PEAK_MB, "a running paired LEG is invisible"
    assert legs.get(900003) == FLOOR_RUN_PEAK_MB, "a running noise-floor leg is invisible"
    assert 900002 not in legs, (
        "the orchestrator was priced as a floor leg; its child is counted too, so one leg is "
        "charged to the guest twice")
