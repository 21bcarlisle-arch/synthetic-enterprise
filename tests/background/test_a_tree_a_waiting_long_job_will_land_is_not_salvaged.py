"""A scratch tree a waiting long job will land is live, so salvage leaves it alone.

Defect (2026-11-14, WORKER_FINDING_FORK_SALVAGE_COMMITS_A_SCRATCH_TREE_...): `fork_salvage` asked
"is a process IN this tree", found none (the chain was waiting on another pid), and committed two
scratch trees whose uncommitted work the chain was about to land.
"""
from pathlib import Path

from background import launch_liveness, seat_executor


def _rec(holds, unit="longjob-chain", claim="live"):
    return {"job": "chain", "unit": unit, "claim": claim, "holds": [str(Path(h).resolve()) for h in holds]}


def test_the_partition_both_ways(tmp_path):
    tree, other = tmp_path / "se-cp", tmp_path / "elsewhere"
    tree.mkdir()
    other.mkdir()
    held = lambda unit: unit == "longjob-chain"  # noqa: E731
    ask = lambda p, recs: seat_executor._held_by_a_live_long_job(  # noqa: E731
        p.resolve(), records=recs, unit_is_held=held)
    # The leg CAN say live, and CAN say not-live, on the same tree.
    assert ask(tree, [_rec([tree])]) and not ask(tree, [_rec([tree], unit="longjob-ended")])
    assert not ask(other, [_rec([tree])])
    assert not ask(tree, [_rec([tree], claim="finished")])
    assert not ask(tree, [])


def test_worktree_is_live_reads_the_leg(tmp_path, monkeypatch):
    tree = tmp_path / "se-cp"
    tree.mkdir()
    monkeypatch.setattr(launch_liveness, "load", lambda path=None: [_rec([tree])])
    import background.launch_long_job as llj
    monkeypatch.setattr(llj, "name_is_held", lambda unit, **_: True)
    assert seat_executor.worktree_is_live(tree)
    monkeypatch.setattr(llj, "name_is_held", lambda unit, **_: False)
    assert not seat_executor.worktree_is_live(tree)


def test_the_record_carries_holds_resolved(tmp_path):
    reg = tmp_path / "records.json"
    tree = tmp_path / "a" / ".." / "se-cp"
    entry = launch_liveness.record("chain", "longjob-chain", "/tmp/x", path=reg, holds=[tree])
    assert entry["holds"] == [str(tree.resolve())]
    assert "holds" not in launch_liveness.record("j2", "longjob-j2", "/tmp/y", path=reg)
