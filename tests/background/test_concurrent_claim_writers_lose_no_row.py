"""Concurrent writers to one claims store must not lose each other's rows.

THE DEFECT (2026-10-01). The worker's dispatch claim on
`land-pb4-swap-with-value-arms-retaken-in-the-new-world`, taken at 15:17:20Z, was gone from the
store by 15:19:54Z with no release logged by anybody. The isolated executor then drew the same item
four times while the worker was still running it. Every writer here does load -> modify -> save
with no lock, so a writer that loaded before another's save writes its stale dict back over it.

Processes, not threads: the writers that collide are separate daemons.
"""
from __future__ import annotations

import multiprocessing as mp

from background import seat_work_in_hand as S

WRITERS = 8
CLAIMS_EACH = 25


def _claim_many(path: str, writer: int) -> None:
    from pathlib import Path
    for i in range(CLAIMS_EACH):
        S.claim(f"w{writer}-{i}", path=Path(path))


def _release_many(path: str, writer: int) -> None:
    from pathlib import Path
    for i in range(CLAIMS_EACH):
        S.release(f"w{writer}-{i}", path=Path(path))


def _run(target, path) -> None:
    ctx = mp.get_context("fork")
    procs = [ctx.Process(target=target, args=(str(path), w)) for w in range(WRITERS)]
    for p in procs:
        p.start()
    for p in procs:
        p.join(60)
        assert p.exitcode == 0


def test_concurrent_claims_from_separate_processes_all_survive(tmp_path):
    store = tmp_path / "claims.json"
    _run(_claim_many, store)
    assert len(S._load(store)) == WRITERS * CLAIMS_EACH


def test_a_concurrent_release_cannot_resurrect_or_drop_a_neighbour(tmp_path):
    """Half the writers release their own rows while the other half claim theirs: every claimer's
    row survives and every released row is gone. A lost update shows up as a missing claim; a
    stale save shows up as a released row coming back."""
    store = tmp_path / "claims.json"
    for w in range(0, WRITERS, 2):
        for i in range(CLAIMS_EACH):
            S.claim(f"w{w}-{i}", path=store)
    ctx = mp.get_context("fork")
    procs = [ctx.Process(target=_release_many if w % 2 == 0 else _claim_many,
                         args=(str(store), w)) for w in range(WRITERS)]
    for p in procs:
        p.start()
    for p in procs:
        p.join(60)
        assert p.exitcode == 0
    expected = {f"w{w}-{i}" for w in range(1, WRITERS, 2) for i in range(CLAIMS_EACH)}
    assert set(S._load(store)) == expected


def test_a_save_leaves_no_temporary_file_beside_the_store(tmp_path):
    """The atomic write goes through a temporary sibling; it must not be left behind for the
    worktree sweepers and the staging census to read as a second store."""
    store = tmp_path / "claims.json"
    S.claim("one", path=store)
    S.release("one", path=store)
    siblings = sorted(p.name for p in tmp_path.iterdir()
                      if p.name.startswith("claims.json") and not p.name.endswith(".lock"))
    assert siblings == ["claims.json"]
