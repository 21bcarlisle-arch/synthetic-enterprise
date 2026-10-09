"""Clearing one file of a multi-file edit stranded the callers in the others, and both lanes died.

THE DEFECT, 2026-10-09. An uncommitted 10-01 edit defined `delivery_lane.held_at_dispatch` and made
`worker_tick.py` and `seat_executor.py` call it. Origin's advance touched only `delivery_lane.py`,
so the reconciler judged and cleared only that file; the callers were never asked about, stayed
live, and every worker-tick and seat-executor run died with `AttributeError` for over five hours.

THE REPAIR: before clearing, `stranded_caller_verdicts` asks whether any dirty `.py` that stays
calls a name only the cleared copy defines; if so, the whole advance is refused by name.

  * `test_a_live_caller_of_a_name_only_the_cleared_copy_defines_holds_the_advance` -- real git:
    the cleared copy is an earlier origin revision (a lossless class), the caller is a dirty file
    origin never touches; nothing is written and the refusal names the caller and the name.
  * `test_the_same_tree_without_the_live_caller_advances` -- the partition control: the guard can
    let an advance through, so the refusal above is about the caller and not about everything.
  * `test_from_import_of_the_lost_name_is_a_caller_too` -- the other binding shape.
  * `test_the_detector_reads_the_real_incident` -- the 10-01 bytes themselves, from git objects.
"""
from __future__ import annotations

import contextlib
import subprocess
from pathlib import Path

import pytest

from background import origin_reconcile as orc

_LIB = "background/lane_lib.py"
_CALLER = "background/lane_caller.py"
_ALIVE = "def kept():\n    return 1\n"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True,
                          text=True).stdout


def _repo(tmp_path: Path) -> Path:
    """Shared tree at c0; origin moves c1 (adds `extra`) then c2 (drops it). The shared tree's
    working copy of the lib is c1's bytes -- the earlier-revision class clears it losslessly."""
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    _git(tmp_path, "clone", str(origin), str(seed))
    _git(seed, "config", "user.email", "t@t")
    _git(seed, "config", "user.name", "t")
    (seed / "background").mkdir()
    (seed / _LIB).write_text(_ALIVE)
    (seed / _CALLER).write_text("from background import lane_lib\n\nlane_lib.kept()\n")
    _git(seed, "add", ".")
    _git(seed, "commit", "-m", "c0")
    _git(seed, "push", "origin", "main")
    shared = tmp_path / "shared"
    _git(tmp_path, "clone", str(origin), str(shared))
    _git(shared, "config", "user.email", "t@t")
    _git(shared, "config", "user.name", "t")
    (seed / _LIB).write_text(_ALIVE + "\ndef extra():\n    return 2\n")
    _git(seed, "commit", "-am", "c1")
    _git(seed, "push", "origin", "main")
    (shared / _LIB).write_text((seed / _LIB).read_text())
    (seed / _LIB).write_text(_ALIVE + "\nVERSION = 3\n")
    _git(seed, "commit", "-am", "c2")
    _git(seed, "push", "origin", "main")
    _git(shared, "fetch", "origin")
    return shared


def _advance(shared: Path) -> dict:
    fixture = lambda _p, paths: {p: (False, "fixture") for p in paths}  # noqa: E731
    return orc.advance_shared_tree(
        shared, stale_fn=fixture, generated_fn=fixture, orphans_fn=fixture,
        abandoned_fn=fixture, append_fn=fixture, locker=contextlib.nullcontext)


def test_a_live_caller_of_a_name_only_the_cleared_copy_defines_holds_the_advance(tmp_path):
    shared = _repo(tmp_path)
    caller = "from background import lane_lib\n\nlane_lib.extra()\n"
    (shared / _CALLER).write_text(caller)
    lib = (shared / _LIB).read_text()
    head = _git(shared, "rev-parse", "HEAD")

    result = _advance(shared)

    assert not result["advanced"]
    assert _CALLER in result["reason"] and "background.lane_lib.extra" in result["reason"]
    assert _git(shared, "rev-parse", "HEAD") == head
    assert (shared / _LIB).read_text() == lib and (shared / _CALLER).read_text() == caller


def test_the_same_tree_without_the_live_caller_advances(tmp_path):
    shared = _repo(tmp_path)

    result = _advance(shared)

    assert result["advanced"], result["reason"]
    assert "VERSION = 3" in (shared / _LIB).read_text()


def test_from_import_of_the_lost_name_is_a_caller_too(tmp_path):
    shared = _repo(tmp_path)
    (shared / _CALLER).write_text("from background.lane_lib import extra\n\nextra()\n")

    verdicts = orc.stranded_caller_verdicts(shared, [_LIB])

    assert list(verdicts) == [_LIB] and _CALLER in verdicts[_LIB]


def test_the_detector_reads_the_real_incident():
    def blob(spec: str) -> bytes:
        res = subprocess.run(["git", "cat-file", "-p", spec], capture_output=True)
        if res.returncode != 0:
            pytest.skip("the 2026-10-09 incident objects are not in this clone")
        return res.stdout

    cleared = orc._module_names(blob("07941f1b4:background/delivery_lane.py"))
    kept = orc._module_names(blob("ad0afe7b3:background/delivery_lane.py"))
    caller = blob("refs/preserved/held-at-dispatch-20261009/worker_tick")  # the 10-01 copy
    lost = cleared - kept
    assert lost == {"held_at_dispatch"}
    assert orc._references_into(caller, "background.delivery_lane") & lost == {"held_at_dispatch"}
