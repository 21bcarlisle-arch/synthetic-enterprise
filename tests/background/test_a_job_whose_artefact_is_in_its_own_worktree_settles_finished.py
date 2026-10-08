"""A long job that writes a RELATIVE artefact in its own worktree must settle as finished.

THE DEFECT. `reask()` tested `Path(artefact).exists()` against the ASKER's cwd. Every long job now
runs in a worktree, so its `docs/observability/...json` lands under that worktree and the deadman,
asking from the shared tree, saw no artefact: `qep3-arms-floor` read `live` for hours after its unit
exited 0, and every brief and waiter keyed to the register believed the floor was still running.
"""
from __future__ import annotations

from background import launch_liveness as ll

ARTEFACT = "docs/observability/floor.json"


def _exited_ok(**extra):
    return lambda unit: {"ActiveState": "inactive", "Result": "success", "ExecMainStatus": "0",
                         "LoadState": "loaded", **extra}


def _worktree_with_artefact(tmp_path):
    worktree = tmp_path / "se-worktree"
    (worktree / ARTEFACT).parent.mkdir(parents=True)
    (worktree / ARTEFACT).write_text("{}", encoding="utf-8")
    asker = tmp_path / "shared-tree"
    asker.mkdir()
    return worktree, asker


def test_the_register_settles_a_job_whose_artefact_is_in_its_launch_worktree(tmp_path, monkeypatch):
    worktree, asker = _worktree_with_artefact(tmp_path)
    monkeypatch.chdir(asker)
    reg = tmp_path / "launch_records.json"
    ll.record("floor", "longjob-floor", ARTEFACT, path=reg, workdir=str(worktree))

    # The rare branch first: from the asker's cwd, with nothing saying where the job ran, the same
    # exited unit is NOT finished -- otherwise the leg below would pass with the workdir ignored.
    assert ll.reask({"unit": "longjob-floor", "artefact": ARTEFACT},
                    _exited_ok())["verdict"] != ll.FINISHED

    ll.check(path=reg, probe=_exited_ok())
    (row,) = [r for r in ll.load(reg) if r["job"] == "floor"]
    assert row["claim"] == ll.FINISHED, row
    assert str(worktree) in row["evidence"], "the evidence must name the file it actually found"


def test_a_record_without_a_workdir_falls_back_to_the_units_working_directory(tmp_path, monkeypatch):
    """Records written before `workdir` existed: systemd still holds the unit's cwd until collected."""
    worktree, asker = _worktree_with_artefact(tmp_path)
    monkeypatch.chdir(asker)
    entry = {"unit": "longjob-floor", "artefact": ARTEFACT}
    assert ll.reask(entry, _exited_ok(WorkingDirectory=str(worktree)))["verdict"] == ll.FINISHED
    assert ll.reask(entry, _exited_ok(WorkingDirectory=str(asker)))["verdict"] != ll.FINISHED


def test_a_launch_in_a_worktree_settles_finished_from_another_cwd(tmp_path, monkeypatch):
    """End to end through `launch()`: the record it writes carries the unit's cwd, and the
    re-ask from a different cwd finds the artefact the job wrote there."""
    import shutil

    from background import launch_long_job as llj
    from tests.background.test_launch_long_job import _Runner

    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(llj, "own_cgroup", lambda *a, **k: "/user.slice/launcher.service")
    worktree = tmp_path / "se-worktree"
    worktree.mkdir()
    asker = tmp_path / "shared-tree"
    asker.mkdir()
    monkeypatch.chdir(asker)
    reg = tmp_path / "records.json"
    llj.launch("floor", ["python3", "-m", "tools.nothing"], artefact=ARTEFACT,
               workdir=str(worktree), log=str(tmp_path / "job.log"), records_path=reg,
               runner=_Runner(), peak_mb=1000, residents=lambda: [], guest_total_mb=24000,
               expect_minutes=30)
    assert not (asker / ARTEFACT).parent.exists(), "the launcher made the artefact dir in the asker"
    (worktree / ARTEFACT).write_text("{}", encoding="utf-8")

    stale, lines, settled = ll.check(reg, probe=_exited_ok())
    assert stale == 1 and settled[0]["claim"] == ll.FINISHED, lines
